#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""述职报告字数门（沿用 awesome-benzi QG-LENGTH-001/002 口径）
统计：每个汉字计 1 字；连续西文单词或数字串计 1 字；标点、空白不计；
      【待补：…】占位不计入字数（占位不是内容）。
通过条件：不低于下限，且不超过上限（默认下限×1.1）；不通过退出码 2。
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

HAN = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z0-9]+(?:[.\-][A-Za-z0-9]+)*")
PLACEHOLDER = re.compile(r"【[^】]*】")
HEAD = re.compile(r"^\s{0,3}#{1,6}\s*", re.M)


def count(text: str) -> int:
    t = PLACEHOLDER.sub("", text)
    return len(HAN.findall(t)) + len(WORD.findall(t))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--min", type=int, required=True, help="全文下限")
    ap.add_argument("--max", type=int, help="全文上限，缺省为下限×1.1")
    ap.add_argument("--sections", help='各栏目下限，如 "教学工作=400,科研工作=400"')
    a = ap.parse_args()
    md = Path(a.src).read_text(encoding="utf-8")
    hi = a.max or int(a.min * 1.1)

    blocks, cur = [], {"title": "（前置）", "buf": []}
    for line in md.splitlines():
        if re.match(r"^\s{0,3}#{1,6}\s", line):
            blocks.append(cur)
            cur = {"title": HEAD.sub("", line).strip(), "buf": []}
        else:
            cur["buf"].append(line)
    blocks.append(cur)

    total, issues = count(md), []
    per = {b["title"]: count("\n".join(b["buf"])) for b in blocks if b["title"] != "（前置）"}
    if total < a.min:
        issues.append({"level": "blocked", "rule": "QG-LENGTH-002",
                       "msg": f"全文 {total} 字，低于下限 {a.min}"})
    elif total > hi:
        issues.append({"level": "blocked", "rule": "QG-LENGTH-002",
                       "msg": f"全文 {total} 字，超过上限 {hi}（下限的 110%）"})
    if a.sections:
        for pair in a.sections.split(","):
            name, _, lim = pair.partition("=")
            name, lim = name.strip(), int(lim)
            hit = next((v for k, v in per.items() if name in k), None)
            if hit is None:
                issues.append({"level": "blocked", "rule": "QG-CONTENT-002",
                               "msg": f"缺栏目「{name}」"})
            elif hit < lim:
                issues.append({"level": "blocked", "rule": "QG-LENGTH-002",
                               "msg": f"栏目「{name}」{hit} 字，低于下限 {lim}"})
    print(json.dumps({"全文": total, "下限": a.min, "上限": hi, "分栏目": per,
                      "issues": issues, "result": "blocked" if issues else "passed"},
                     ensure_ascii=False, indent=2))
    return 2 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
