#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task_gate.py — 会议纪要 / 通知 / 工作计划文书的交付前自检（本包自建，仅标准库）

做三件事：
  1. 任务可执行化检查：所有「任务分工 / 工作计划 / 待办」类表格，每行必须齐
     动词+对象、责任人、截止时间、验收方式；缺项进 blocked。
  2. 决议纯度检查：出现在「决议 / 决定 / 议定事项」小节里的行，不得含模糊表态词
     （建议、可以考虑、酌情、争取、尽量、待定…）——「讨论过」不许写成「已决定」。
  3. AI 味与套话扫描：按 awesome-benzi LANGUAGE_MODEL 口径，扫出公文套话、口水话、
     营销腔、聊天机器人残留、空泛判断句。

用法：
  PY="skills/office-layer/.venv/bin/python"
  $PY skills/meeting-notices/scripts/task_gate.py --in 教研会纪要.md --out 纪要自检报告.md
  $PY skills/meeting-notices/scripts/task_gate.py --in 通知.md          # 只打印，不落盘

退出码：0 = 通过（可能带 needs-review）；2 = 有 blocked 项，不得交付。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 词表
# 一、公文套话：无动作句子，删掉或改成「谁做什么」
CLICHES = {
    "领导关怀式开头": ["在校领导", "在学院领导的正确领导", "在上级部门的大力支持", "在各位领导的关怀"],
    "空喊重视": ["高度重视", "高度关注", "充分认识", "提高政治站位", "统一思想", "凝聚共识"],
    "空喊落实": ["狠抓落实", "抓好落实", "扎实推进", "大力推进", "全力推进", "切实把", "切实抓好",
                 "认真做好", "认真抓好", "落到实处"],
    "营销腔": ["赋能", "抓手", "闭环管理", "底层逻辑", "颗粒度", "倒逼", "深耕", "助力",
               "形成合力", "全面提升", "提质增效"],
    "无信息转承": ["值得注意的是", "需要指出的是", "必须看到的是", "综上所述", "总而言之",
                   "众所周知", "不难发现", "我们可以看到", "由此可见", "不言而喻"],
    "空泛判断": ["具有重要价值", "具有重要意义", "奠定坚实基础", "提供有力支撑", "意义重大"],
    "成效无据": ["取得显著成效", "效果显著", "成效明显", "反响热烈", "广受好评"],
    "聊天机器人残留": ["下面我将", "以下是为你", "希望这对你有帮助", "如需我继续", "作为 AI",
                       "好的，", "当然，"],
    "口水话": ["我们觉得", "大家都知道", "说白了", "搞定", "很厉害", "非常牛", "一大堆",
               "太棒了", "超级", "居然", "竟然"],
}

# 二、模糊表态词：出现在「决议」小节即判 blocked
VAGUE = ["建议", "可以考虑", "研究一下", "研究研究", "酌情", "看情况", "争取", "尽量",
         "下一步再说", "后续再议", "待定", "视情况", "大概", "可能", "初步考虑"]

# 三、任务表判定
TASK_HEADER_HINTS = ["责任人", "负责", "承办"]
TASK_TEXT_HINTS = ["任务", "事项", "工作", "举措"]
DUE_HEADER_HINTS = ["截止", "完成时间", "时间节点", "期限", "deadline"]
CHECK_HEADER_HINTS = ["验收", "衡量标准", "交付物", "完成标志"]
DECISION_SECTION_HINTS = ["决议", "决定", "议定", "形成的事项", "结论"]
PLACEHOLDER_RE = re.compile(r"【待[^】]*】")
DATE_RE = re.compile(r"(20\d{2}[-/年]\d{1,2}[-/月]\d{1,2}|\d{1,2}月\d{1,2}日|第\d+周)")
EMPTY_CELL = {"", "-", "—", "/", "无", "待定", "TBD", "tbd", "?"}
# 不是「人」的责任人写法：出现即视为未落实到人
VAGUE_OWNER = ["相关老师", "相关人员", "有关人员", "相关同志", "有关方面", "各相关部门",
               "大家", "各位老师", "全体老师", "相关责任人"]
MINUTES_HINTS = ["纪要", "记录"]


def parse_tables(text: str):
    """返回 [{'start': 行号, 'header': [列名], 'rows': [[单元格]], 'section': 所属标题}]"""
    tables, cur, section = [], [], ""
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#"):
            section = s.lstrip("# ").strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):      # 分隔行
                continue
            cur.append((i, cells))
        else:
            if cur:
                tables.append({"start": cur[0][0], "header": cur[0][1],
                               "rows": [c for _, c in cur[1:]], "section": section})
                cur = []
    if cur:
        tables.append({"start": cur[0][0], "header": cur[0][1],
                       "rows": [c for _, c in cur[1:]], "section": section})
    return tables


def col_index(header, hints):
    for idx, name in enumerate(header):
        if any(h in name for h in hints):
            return idx
    return None


def check(text: str):
    blocked, review, advisory = [], [], []

    # ---- 1. 任务表
    seen_task_table = False
    for tb in parse_tables(text):
        hdr = tb["header"]
        if not any(h in "".join(hdr) for h in TASK_HEADER_HINTS):
            continue
        seen_task_table = True
        pi = col_index(hdr, TASK_HEADER_HINTS)
        di = col_index(hdr, DUE_HEADER_HINTS)
        ci = col_index(hdr, CHECK_HEADER_HINTS)
        ti = col_index(hdr, TASK_TEXT_HINTS)
        if di is None:
            blocked.append(f"第 {tb['start']} 行的任务表**没有「截止时间」列** —— "
                           f"没有截止时间的任务等于没有任务，必须补列。")
        if ci is None:
            review.append(f"第 {tb['start']} 行的任务表没有「验收方式/衡量标准」列，"
                          f"建议补上，否则无法判断做没做。")
        for n, row in enumerate(tb["rows"], 1):
            label = (row[ti].strip() if (ti is not None and ti < len(row)) else
                     (row[0] if row else "?"))
            owner = row[pi].strip() if (pi is not None and pi < len(row)) else ""
            if pi is not None and (not owner or owner in EMPTY_CELL
                                   or PLACEHOLDER_RE.search(owner)):
                blocked.append(f"任务表第 {n} 行「{label}」："
                               f"**责任人缺失或为占位**，必须填到人（姓名或岗位），不得写「相关老师」。")
            elif owner in VAGUE_OWNER or any(v in owner for v in VAGUE_OWNER):
                blocked.append(f"任务表第 {n} 行责任人写的是「{owner}」—— 这不是人，"
                               f"任务落不到具体人身上就没人做，请改到姓名或明确岗位。")
            if di is not None:
                due = row[di].strip() if di < len(row) else ""
                if not due or due in EMPTY_CELL:
                    blocked.append(f"任务表第 {n} 行「{label}」：**截止时间空缺**。")
                elif not DATE_RE.search(due) and not PLACEHOLDER_RE.search(due):
                    review.append(f"任务表第 {n} 行截止时间「{due}」不是可核对日期"
                                  f"（应写 2025-11-20 或「11月20日」或「第12周」）。")
            first = row[ti].strip() if (ti is not None and ti < len(row)) else ""
            if first and len(first) <= 6 and not re.search(r"[做完成提交整理组织落实拟定修订汇总]",
                                                           first):
                advisory.append(f"任务表第 {n} 行事项「{first}」看不出动作，"
                                f"建议写成「动词+对象」，如「提交修订版培养方案」。")
    if not seen_task_table and PLACEHOLDER_RE.search(text) is None and \
            ("纪要" in text[:400] or "工作计划" in text[:400]):
        review.append("全文未发现「责任人」列的任务表 —— 纪要/通知的落地全靠这张表，"
                      "如本次确实无任务可跳过，否则请补。")

    # ---- 2. 决议纯度
    lines, in_decision = text.splitlines(), False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            in_decision = any(h in s for h in DECISION_SECTION_HINTS)
            continue
        if in_decision and s:
            for v in VAGUE:
                if v in s:
                    blocked.append(f"第 {i} 行在「决议」小节里出现模糊表态词「{v}」："
                                   f"「{s[:40]}」。讨论意见不得写成决议 —— "
                                   f"要么改成明确动作与责任人，要么移到「讨论情况」小节并标「待定」。")
                    break

    # ---- 3. 套话扫描
    for i, line in enumerate(text.splitlines(), 1):
        for cat, words in CLICHES.items():
            for w in words:
                if w in line:
                    advisory.append(f"第 {i} 行命中【{cat}】「{w}」：{line.strip()[:40]}")

    # ---- 4. 人工确认位
    body = text[:600]
    if any(h in body for h in MINUTES_HINTS) and "待" not in text and "确认" not in text:
        review.append("**没有找到参会人/主持人确认位** —— 纪要须经确认后定稿，"
                      "请在文末加「参会人签字：____」「【待主持人确认：定稿】」。")

    return blocked, review, advisory


def render(src: Path, blocked, review, advisory) -> str:
    out = [f"# 交付前自检报告：{src.name}", ""]
    out.append(f"- 阻断项 blocked：**{len(blocked)}**")
    out.append(f"- 需复核 needs-review：**{len(review)}**")
    out.append(f"- 提示 advisory：**{len(advisory)}**")
    out.append("")
    for title, items in (("一、阻断项（必须改完才能交付）", blocked),
                         ("二、需人工复核", review),
                         ("三、提示（套话等，逐条判断）", advisory)):
        out.append(f"## {title}")
        out.append("")
        if not items:
            out.append("- 无")
        else:
            for it in items:
                out.append(f"- [ ] {it}")
        out.append("")
    out.append("> 本报告由 `task_gate.py` 生成，只做机械检查。"
               "**事实是否真实、决议是否属实、责任人与时间是否可行，仍须主持人和参会人确认。**")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="纪要/通知/计划文书交付前自检（任务可执行化 + 决议纯度 + AI 味）")
    ap.add_argument("--in", dest="src", required=True, help="待检 Markdown 草稿")
    ap.add_argument("--out", dest="out", help="自检报告输出路径（.md）；不给则只打印")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"找不到文件：{src}", file=sys.stderr)
        return 2
    text = src.read_text(encoding="utf-8")
    blocked, review, advisory = check(text)
    report = render(src, blocked, review, advisory)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"自检报告已写入：{args.out}")
    print(f"blocked={len(blocked)} needs-review={len(review)} advisory={len(advisory)}")
    for it in blocked[:10]:
        print(f"  [blocked] {it}")
    print("结论：" + ("有阻断项，不得交付。" if blocked else "无阻断项，可进入人工确认。"))
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
