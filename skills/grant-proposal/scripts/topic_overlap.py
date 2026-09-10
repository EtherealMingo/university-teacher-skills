#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topic_overlap — 选题重叠度检查（自建）

对给定选题与「已立项/已发表」语料做三维度重叠分析：
  1. 用词重叠   —— 中文按字符二元组 + 英文按词，计算加权 Jaccard
  2. 方法重叠   —— 命中方法类关键词的交集比
  3. 场景重叠   —— 命中应用场景类关键词的交集比

给出「撞车风险」分级。**结论不构成查新报告**，仅供选题阶段自检。

用法：
  python topic_overlap.py --topic "..." --corpus 清单.xlsx --out 报告.md
  python topic_overlap.py --topic "..." --corpus 清单.txt  --out 报告.md
  python topic_overlap.py --topic "..."                       # 无语料，仅做选题自检
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ------------------------------------------------------------------ 关键词表
METHODS = [
    "深度学习", "机器学习", "强化学习", "迁移学习", "联邦学习", "多模态", "图神经网络",
    "卷积神经网络", "循环神经网络", "transformer", "注意力机制", "大语言模型", "知识图谱",
    "因果推断", "贝叶斯", "随机森林", "支持向量机", "聚类", "回归分析", "结构方程",
    "扎根理论", "案例研究", "问卷调查", "访谈", "实验研究", "准实验", "元分析",
    "仿真", "数值模拟", "有限元", "优化算法", "遗传算法", "粒子群", "数字孪生",
    "deep learning", "machine learning", "neural network", "llm", "gnn",
]
DOMAINS = [
    "城市交通", "轨道交通", "客流预测", "智慧城市", "自动驾驶", "新能源", "储能",
    "碳中和", "碳排放", "环境治理", "水资源", "大气污染", "土壤修复",
    "医学影像", "临床", "公共卫生", "流行病", "护理", "药物",
    "教育", "教学", "课程", "学习行为", "在线教育", "教育评价", "教师发展",
    "乡村振兴", "基层治理", "社会保障", "老龄化", "就业", "收入分配",
    "供应链", "金融风险", "企业管理", "创新创业", "产业升级", "数字经济",
    "材料", "器件", "芯片", "半导体", "生物医学工程", "机器人",
]
STOP = set("的 了 与 和 及 或 在 对 基于 研究 分析 方法 一种 及其 应用 技术 系统 设计 实现 探讨".split())


def tokens(text: str):
    """中文取字符二元组，英文/数字取词。返回带权重的集合。"""
    text = (text or "").lower()
    out = set()
    # 英文词
    for w in re.findall(r"[a-z][a-z0-9\-]{2,}", text):
        if w not in STOP:
            out.add(w)
    # 中文二元组
    han = re.sub(r"[^\u4e00-\u9fff]", "", text)
    for i in range(len(han) - 1):
        bg = han[i:i + 2]
        if bg not in STOP:
            out.add(bg)
    return out


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def kw_hit(text: str, table):
    t = (text or "").lower()
    return {k for k in table if k.lower() in t}


def grade(score: float) -> str:
    if score >= 0.55:
        return "高（疑似撞车，建议换角度或明确差异化）"
    if score >= 0.35:
        return "中（部分重合，需在创新点上做切割）"
    if score >= 0.18:
        return "低（有交集，属正常同领域）"
    return "极低"


def load_corpus(path: Path):
    """支持 .xlsx（取第一列含标题的列）与 .txt/.md（每行一条）。"""
    items = []
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("读取 xlsx 需要 openpyxl")
        wb = openpyxl.load_workbook(str(path), data_only=True)
        ws = wb[wb.sheetnames[0]]
        for row in ws.iter_rows(values_only=True):
            if not row:
                continue
            # 取该行最长的文本单元格作为题名
            cells = [str(c).strip() for c in row if isinstance(c, str) and len(str(c).strip()) > 4]
            if cells:
                items.append(max(cells, key=len))
    else:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line)
    return items


def analyze(topic: str, corpus_path=None):
    tt = tokens(topic)
    tm, td = kw_hit(topic, METHODS), kw_hit(topic, DOMAINS)

    rows = []
    if corpus_path:
        for title in load_corpus(Path(corpus_path)):
            ct = tokens(title)
            cm, cd = kw_hit(title, METHODS), kw_hit(title, DOMAINS)
            w_j, m_j, d_j = jaccard(tt, ct), jaccard(tm, cm), jaccard(td, cd)
            # 方法/场景权重更高：同方法同场景才是真撞车
            score = 0.4 * w_j + 0.35 * m_j + 0.25 * d_j
            rows.append({"题名": title, "综合分": round(score, 3),
                         "用词": round(w_j, 3), "方法": round(m_j, 3),
                         "场景": round(d_j, 3), "风险": grade(score),
                         "共有方法": sorted(tm & cm), "共有场景": sorted(td & cd)})
        rows.sort(key=lambda r: r["综合分"], reverse=True)

    return {"topic": topic, "tokens": len(tt),
            "methods_found": sorted(tm), "domains_found": sorted(td),
            "corpus_size": len(rows),
            "top": rows[:15],
            "max_score": rows[0]["综合分"] if rows else None}


def to_markdown(res) -> str:
    L = [f"# 选题重叠度检查报告", "",
         f"**选题**：{res['topic']}", ""]
    L += [f"- 识别到的**方法**关键词：{'、'.join(res['methods_found']) or '（无）'}",
          f"- 识别到的**场景**关键词：{'、'.join(res['domains_found']) or '（无）'}",
          f"- 语料条数：{res['corpus_size']}", ""]
    if res["corpus_size"]:
        L += ["## 高风险条目", "",
              "| 排名 | 题名 | 综合分 | 用词 | 方法 | 场景 | 风险 |",
              "|---|---|---|---|---|---|---|"]
        for i, r in enumerate(res["top"], 1):
            t = r["题名"][:48].replace("|", "/")
            L.append(f"| {i} | {t} | {r['综合分']} | {r['用词']} | {r['方法']} | {r['场景']} | {r['风险']} |")
        L += ["", "## 共有要素", ""]
        for i, r in enumerate(res["top"][:5], 1):
            if r["共有方法"] or r["共有场景"]:
                L.append(f"{i}. **{r['题名'][:40]}** — 共有方法：{'、'.join(r['共有方法']) or '无'}；"
                         f"共有场景：{'、'.join(r['共有场景']) or '无'}")
    else:
        L += ["> ⚠️ **未提供语料**，本次仅做选题自检，未与任何已立项/已发表题目比对。",
              "> 结论不能替代正式查新。", ""]
    L += ["", "---", "",
          "> **免责**：本报告为选题阶段自检，**不构成科技查新报告**。",
          "> 正式申报请以具备资质的查新机构出具的报告为准。"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(prog="topic_overlap", description="选题重叠度检查")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--corpus", help="已立项/已发表清单（.xlsx 或 .txt/.md，每行一条）")
    ap.add_argument("--out", help="输出 Markdown 报告路径；缺省打印 JSON")
    args = ap.parse_args()

    res = analyze(args.topic, args.corpus)
    if args.out:
        Path(args.out).write_text(to_markdown(res), encoding="utf-8")
        print(json.dumps({"out": args.out, "corpus_size": res["corpus_size"],
                          "max_score": res["max_score"],
                          "top1": res["top"][0]["题名"][:40] if res["top"] else None},
                         ensure_ascii=False, indent=2))
        if not args.corpus:
            print("警告：未提供语料，报告已标注「不能替代查新」", file=sys.stderr)
    else:
        print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
