#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推荐信套话扫描 + 同批草稿雷同检测（本包自建，仅用标准库）。

定位：`student-recommendation` 技能阶段五「AI 味与套话清理」的机械化前置检查。
它解决的是本技能最核心的痛点——每个学生单独写、但不能套模板；挤在一起写就必然写成套话。
本脚本把「套话」和「雷同」两件事从主观感觉变成可复核的数字。

只读输入文件，不改动任何草稿。输出为 Markdown 报告（可选再走 office-layer 转 DOCX）。

用法：
    PY=vendor/office-layer/.venv/bin/python
    $PY skills/student-recommendation/scripts/cliche_scan.py \
        推荐信_李明.md 推荐信_王芳.md 推荐信_张野.md \
        --out 套话与雷同报告.md

    只查套话、不做两两比对（单人场景）：
    $PY skills/student-recommendation/scripts/cliche_scan.py 推荐信_李明.md

退出码：
    0  未命中套话黑名单，且同批草稿雷同度可接受
    1  命中套话黑名单，或某两份草稿雷同度达到 needs-review/blocked
    2  参数或读取错误

注意：本脚本只做机器可判定的部分。名字替换测试通过、雷同率为 0，也不能替代教师通读定稿。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

# ---------------------------------------------------------------- 词表

# A. 推荐信最该删的零信息量套话 -> 改法
#    判据：把学生的名字换成任意一个学生，句子仍然成立 —— 那就是没有信息量。
CLICHE_ZERO_INFO = {
    "品学兼优": "拆成两条可核验事实：哪门课多少分、哪件事上具体做了什么",
    "学习刻苦": "给出工作量：连续几周、每天几小时、完成了什么",
    "刻苦努力": "同上。努力不是证据，产出才是",
    "成绩优异": "写出课程名、分数、班级排名或百分位",
    "成绩优秀": "同上",
    "乐于助人": "写一次具体事件：什么时候、帮谁、解决了什么问题",
    "团结同学": "写一次具体协作事件：在哪个项目里承担了什么、带动了谁",
    "尊敬师长": "删掉。与学业能力无关，且高校推荐信中属礼节性填充",
    "综合素质高": "删掉。换成 2–3 项可举证的能力，每项配事例",
    "综合素质突出": "同上",
    "表现突出": "写出在哪件事上表现突出，以及突出到什么程度",
    "表现优异": "同上",
    "深受师生好评": "删掉。无主体的评价不可核验；改为「XX 课程答辩中评委询问了 3 个追问」",
    "具有良好的团队精神": "写一次分工与冲突处理的具体场景",
    "团队协作能力强": "同上",
    "责任心强": "写一次他主动承担并按时交付的任务",
    "思维活跃": "写一次他提出了什么被采纳的想法",
    "基础扎实": "写出课程与分数：如「数学分析 92、线性代数 95」",
    "学习能力强": "写一次他学新东西的具体速度：几天内掌握了什么并用于什么",
    "动手能力强": "写他做出来了什么，含规模、指标或结果",
    "积极向上": "删掉。无信息量",
    "乐观开朗": "删掉。无信息量",
    "吃苦耐劳": "写一次具体的高强度任务及其结果",
    "踏实认真": "写一次他自查、复现或纠错的具体动作",
    "具有一定的科研潜力": "写他已完成的科研动作：读了什么、复现了什么、得到什么结论",
    "有较强的创新能力": "写一项他提出的改进及其验证结果",
    "沟通能力强": "写一次他在什么场合向谁讲清了什么问题",
    "英语水平良好": "写出分数或事实：CET-6 几分、雅思几分、能否直接读英文文献",
}

# B. 通用 AI 套话与口水话（对应 LANGUAGE_MODEL.md 的 WR-STYLE-010 / WR-STYLE-011）
CLICHE_AI = {
    "值得注意的是": "WR-STYLE-010：无信息转承，删",
    "需要指出的是": "WR-STYLE-010：无信息转承，删",
    "必须看到的是": "WR-STYLE-010：删",
    "综上所述": "WR-STYLE-010：删，或改为一句具体判断",
    "总而言之": "WR-STYLE-010：删",
    "众所周知": "WR-STYLE-010：删",
    "不难发现": "WR-STYLE-010：删",
    "我们可以看到": "WR-STYLE-010：删",
    "由此可见": "WR-STYLE-010：删",
    "不言而喻": "WR-STYLE-010：删",
    "赋能": "WR-STYLE-011：营销腔，删",
    "抓手": "WR-STYLE-011：简报腔，删",
    "闭环": "WR-STYLE-011：简报腔，删",
    "底层逻辑": "WR-STYLE-011：删",
    "颗粒度": "WR-STYLE-011：删",
    "倒逼": "WR-STYLE-011：删",
    "深耕": "WR-STYLE-011：删",
    "助力": "WR-STYLE-011：改「帮助/支持」，或直接写做了什么",
    "形成合力": "WR-STYLE-011：删",
    "全面提升": "WR-STYLE-011：改写成具体能力的提升幅度",
    "下面我将": "WR-STYLE-012：聊天机器人残留，删",
    "以下是为你": "WR-STYLE-012：删",
    "希望对你有帮助": "WR-STYLE-012：删",
    "如需我继续": "WR-STYLE-012：删",
}

# C. 夸张与无据拔高（WR-STYLE-013 / WR-STYLE-015 / WR-STYLE-016 / WR-STYLE-017）
CLICHE_HYPE = {
    "极高": "改为可核验的比较级：如「班级第 2 / 120 人」",
    "极其": "WR-STYLE-016：夸张副词，删",
    "极为": "WR-STYLE-016：删",
    "非常优秀": "WR-STYLE-017：改为对比参照",
    "最优秀": "除非能给出范围与依据（如「近五年我指导的 23 名学生中最强」），否则删",
    "无人能及": "删。不可核验",
    "天才": "删。推荐信用形容词拔高会降低可信度",
    "完美": "删。英文 perfect 同理",
    "无可挑剔": "删",
    "绝无仅有": "删",
    "首屈一指": "删，或给出比较范围与证据",
    "国际领先": "WR-STYLE-013：需限定对象/时间/样本/边界并有证据卡，否则降级为「在……方面有推进」",
    "世界一流": "WR-STYLE-013：同上",
    "填补空白": "WR-STYLE-013：同上",
    "开创性": "WR-STYLE-013：同上",
    "史无前例": "删",
}

# D. 英文推荐信的中式赞美与空泛堆砌（留学推荐信专用）
CLICHE_EN = {
    "studies hard": "中式赞美，改为具体工作量或成绩",
    "hard-working and helpful": "连续形容词堆砌，改为一次具体协作事件",
    "excellent grades": "改为 course name + score + rank",
    "willing to help others": "改为 a specific instance of helping",
    "all-round": "改为具体能力项",
    "noble character": "英文推荐信忌道德评价，删",
    "perfect": "过度赞美反而降低可信度，删",
    "genius": "删。用对比参照替代（top 5% of students I have taught）",
    "outstanding in every way": "改为具体维度",
    "diligent, hardworking and helpful": "三连形容词，改为事实",
    "very very": "口语重复，删",
}

# 零信息量句判定用的评价性形容词
EVAL_WORDS = [
    "刻苦", "努力", "勤奋", "优异", "优秀", "突出", "品学兼优", "乐于助人",
    "团结", "尊敬", "综合素质", "团队精神", "责任心", "积极", "乐观", "踏实",
    "认真", "良好", "扎实", "活跃", "上进", "热情", "细心", "任劳任怨",
    "吃苦耐劳", "虚心", "自律", "潜力",
]

# 具体性标记：出现任一，说明句子有可核验锚点。
# 只认「数字 / 书名号 / 名次 / 标准化考试」这类硬锚点 —— 不要把「人」「分」「次」这类
# 单字算进来，否则「乐于助人」「充分」会被误判为有锚点，导致零信息量句漏检。
CONCRETE = re.compile(
    r"[0-9０-９]|《|》|第[一二三四五六七八九十0-9]+名|%|"
    r"\bSCI\b|\bEI\b|\bCET\b|\bIELTS\b|\bTOEFL\b|\bGPA\b"
)
MAX_ANCHOR_LIST = 20

SENT_SPLIT = re.compile(r"[。！？；!?;\n]+")

# 同批草稿雷同度阈值
NEEDS_REVIEW = 0.10
BLOCKED = 0.20


# ---------------------------------------------------------------- 工具函数

def norm(text: str) -> str:
    """去掉空白与常见标点，用于重合度比较。"""
    return re.sub(r"[\s，。、；：？！,.;:?!”“\"'（）()《》【】\[\]—\-…·]+", "", text)


def sentences(text: str):
    """返回 (行号, 句子) 列表，过滤过短片段与 Markdown 标记行。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        s = s.lstrip("-*+ ").strip()
        for piece in SENT_SPLIT.split(s):
            piece = piece.strip()
            if len(norm(piece)) >= 6:
                out.append((i, piece))
    return out


def ngrams(s: str, n: int = 12):
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def containment(a: set, b: set) -> float:
    """A 被 B 覆盖的比例（取较小集合为分母）。"""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


# ---------------------------------------------------------------- 各检查项

def scan_phrases(text: str):
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for table, kind in ((CLICHE_ZERO_INFO, "零信息量套话"),
                            (CLICHE_AI, "AI 套话"),
                            (CLICHE_HYPE, "夸张拔高"),
                            (CLICHE_EN, "中式英文赞美")):
            for phrase, advice in table.items():
                if phrase.lower() in low:
                    hits.append({"line": i, "kind": kind, "phrase": phrase,
                                 "advice": advice, "context": line.strip()[:60]})
    if "！" in text or "!" in text:
        for i, line in enumerate(text.splitlines(), 1):
            if "！" in line or "!" in line:
                hits.append({"line": i, "kind": "严肃性", "phrase": "感叹号",
                             "advice": "WR-STYLE-015：推荐信不用感叹号",
                             "context": line.strip()[:60]})
    return hits


def scan_zero_info(text: str):
    """零信息量句：≥2 个评价词且无任何可核验锚点。"""
    out = []
    for ln, s in sentences(text):
        n_eval = sum(1 for w in EVAL_WORDS if w in s)
        if n_eval >= 2 and not CONCRETE.search(s):
            out.append({"line": ln, "sentence": s,
                        "eval_words": [w for w in EVAL_WORDS if w in s]})
    return out


def scan_no_anchor(text: str):
    """名字替换测试候选：无数字、无具体标记的句子。"""
    return [{"line": ln, "sentence": s}
            for ln, s in sentences(text)
            if not CONCRETE.search(s) and len(norm(s)) >= 12]


def compare(files):
    pairs = []
    for (pa, ta), (pb, tb) in combinations(files, 2):
        sa = {norm(s) for _, s in sentences(ta)}
        sb = {norm(s) for _, s in sentences(tb)}
        dup = sorted(sa & sb, key=len, reverse=True)
        ga, gb = ngrams(norm(ta)), ngrams(norm(tb))
        rate = containment(ga, gb)

        if rate >= BLOCKED:
            level = "blocked"
        elif rate >= NEEDS_REVIEW:
            level = "needs-review"
        else:
            level = "ok"

        shared = sorted(ga & gb, key=len, reverse=True)[:8]
        pairs.append({
            "a": pa.name, "b": pb.name,
            "overlap": round(rate, 4), "level": level,
            "dup_sentences": dup[:8],
            "shared_phrases": shared,
        })
    return pairs


# ---------------------------------------------------------------- 报告

def build_report(files, results):
    L = []
    L.append("# 推荐信套话与雷同检测报告")
    L.append("")
    L.append("> 本报告由 `skills/student-recommendation/scripts/cliche_scan.py` 生成，")
    L.append("> 只做机器可判定的部分。**通过不等于合格** —— 事实核验与推荐强度定级必须由教师完成。")
    L.append("")

    total_hits = sum(len(r["phrases"]) for _, r in results)
    worst = max([p["overlap"] for p in results[0][1]["pairs"]] or [0.0]) if results else 0.0

    L.append("## 一、总览")
    L.append("")
    L.append("| 草稿 | 句数 | 套话命中 | 零信息量句 | 无锚点句 |")
    L.append("|---|---|---|---|---|")
    for path, r in results:
        L.append(f"| {path.name} | {r['n_sent']} | {len(r['phrases'])} | "
                 f"{len(r['zero_info'])} | {len(r['no_anchor'])} |")
    L.append("")

    pairs = results[0][1]["pairs"] if results else []
    if pairs:
        L.append("## 二、同批草稿雷同度")
        L.append("")
        L.append(f"判读：< {NEEDS_REVIEW:.2f} 可接受｜"
                 f"{NEEDS_REVIEW:.2f}–{BLOCKED:.2f} 需改写｜≥ {BLOCKED:.2f} 必须重写。")
        L.append("")
        L.append("| 草稿 A | 草稿 B | 重合率 | 判定 |")
        L.append("|---|---|---|---|")
        for p in pairs:
            L.append(f"| {p['a']} | {p['b']} | {p['overlap']:.3f} | {p['level']} |")
        L.append("")
        for p in pairs:
            if p["level"] == "ok":
                continue
            L.append(f"### {p['a']} ↔ {p['b']}（{p['level']}）")
            L.append("")
            if p["shared_phrases"]:
                L.append("高频重合片段（12 字窗口，按长度排序）：")
                L.append("")
                for g in p["shared_phrases"]:
                    L.append(f"- `{g}`")
                L.append("")
            if p["dup_sentences"]:
                L.append("完全相同的句子：")
                L.append("")
                for s in p["dup_sentences"]:
                    L.append(f"- {s}")
                L.append("")
            L.append("处理：对每一处重合，换成该生**自己的事例**；"
                     "同一优点在不同信里必须用不同事例表达，见 SKILL.md「区分度设计」。")
            L.append("")

    L.append("## 三、逐份明细")
    L.append("")
    for path, r in results:
        L.append(f"### {path.name}")
        L.append("")
        if r["phrases"]:
            L.append("#### 套话命中（必须逐条改写或删除）")
            L.append("")
            L.append("| 行 | 类型 | 命中 | 建议 |")
            L.append("|---|---|---|---|")
            for h in r["phrases"]:
                L.append(f"| {h['line']} | {h['kind']} | {h['phrase']} | {h['advice']} |")
            L.append("")
        else:
            L.append("套话命中：无。")
            L.append("")

        if r["zero_info"]:
            L.append("#### 疑似零信息量句（≥2 个评价词且无可核验锚点）")
            L.append("")
            for z in r["zero_info"]:
                L.append(f"- **第 {z['line']} 行**：{z['sentence']}")
                L.append(f"  - 命中评价词：{'、'.join(z['eval_words'])}")
                L.append("  - 处理：删掉整句，或改写为「具体事例 + 数字」。"
                         "无法改写说明这条素材还没采集到 —— 留 `【待补：具体事例】`，不要用形容词填。")
            L.append("")

        if r["no_anchor"]:
            L.append("#### 名字替换测试候选（无数字、无具体标记，请逐句自问）")
            L.append("")
            L.append("> 把句中学生的名字换成任意一个学生，如果句子仍然成立，这句话就没有信息量。")
            L.append("")
            for n in r["no_anchor"][:MAX_ANCHOR_LIST]:
                L.append(f"- 第 {n['line']} 行：{n['sentence']}")
            if len(r["no_anchor"]) > MAX_ANCHOR_LIST:
                L.append(f"- …… 另有 {len(r['no_anchor']) - MAX_ANCHOR_LIST} 句，见草稿原文")
            L.append("")
        L.append("")

    L.append("## 四、下一步（人工，不可省）")
    L.append("")
    L.append("1. 逐条处理上面的套话命中与零信息量句；改写不了的一律留 `【待补：具体事例】`。")
    L.append("2. 同批草稿按雷同度表逐对改写，确保核心事例不重复。")
    L.append("3. 教师通读定稿，逐句确认事实性陈述属实（见 SKILL.md 阶段六）。")
    L.append("")

    return "\n".join(L), {"files": len(files), "cliche_hits": total_hits,
                          "max_overlap": worst}


def main():
    ap = argparse.ArgumentParser(
        prog="cliche_scan",
        description="推荐信套话扫描 + 同批草稿雷同检测（只读，不改动草稿）")
    ap.add_argument("drafts", nargs="+", help="一份或多份草稿（.md/.txt），多份时做两两雷同比对")
    ap.add_argument("--out", default="套话与雷同报告.md", help="报告输出路径")
    ap.add_argument("--quiet", action="store_true", help="不打印 stdout 摘要")
    args = ap.parse_args()

    files = []
    for p in args.drafts:
        path = Path(p)
        if not path.is_file():
            print(f"E_INPUT: 找不到文件 {path}", file=sys.stderr)
            return 2
        files.append((path, path.read_text(encoding="utf-8")))

    results = []
    for path, text in files:
        results.append((path, {
            "phrases": scan_phrases(text),
            "zero_info": scan_zero_info(text),
            "no_anchor": scan_no_anchor(text),
            "n_sent": len(sentences(text)),
            "pairs": [],
        }))
    pairs = compare(files)
    for _, r in results:
        r["pairs"] = pairs

    report, summary = build_report(files, results)
    Path(args.out).write_text(report, encoding="utf-8")

    if not args.quiet:
        print(f"草稿数 {summary['files']}｜套话命中 {summary['cliche_hits']} 处｜"
              f"最高雷同度 {summary['max_overlap']:.3f}")
        print(f"报告：{args.out}")

    flags = summary["cliche_hits"] > 0 or summary["max_overlap"] >= NEEDS_REVIEW
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
