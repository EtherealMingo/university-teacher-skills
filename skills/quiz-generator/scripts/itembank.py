#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题库归档与复用（itembank）

把 quiz-generator 每次产出的 `题库.json` 按课程归档成可复用的课程题库：
去重（题干哈希）、检索（知识点/题型/层次）、淘汰标记（考后区分度 D<0.2 的题）、
实测难度回填（exam-pipeline 回传的逐题 P 值，用于预估校准）。

只用标准库，与 quiz_audit.py 同级运行。

用法：
  itembank.py ingest    --bank 题库 --course 概率论 --in 题库.json [--term 2025-2026-1]
  itembank.py search    --bank 题库 --course 概率论 [--kp 贝叶斯] [--type 计算题]
                        [--bloom 应用] [--status active] [--full]
  itembank.py retire    --bank 题库 --course 概率论 (--ids Q03,Q07 | --csv 淘汰题.csv)
  itembank.py calibrate --bank 题库 --course 概率论 --csv 实测难度.csv
  itembank.py stats     --bank 题库 [--course 概率论]

退出码：0 正常；1 参数/文件错误；2 有待人工处理项（ingest 发现全部重复、
calibrate/retire 有未命中题号）——与包内其它质量门脚本口径一致。
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

REQUIRED_FIELDS = ["id", "kp", "type", "bloom", "stem", "answer"]


def stem_hash(stem: str) -> str:
    """题干归一化后取哈希：去全部空白与全半角差异，判重只认这一把尺。"""
    norm = "".join(str(stem).split()).replace("（", "(").replace("）", ")") \
        .replace("，", ",").replace("。", ".").replace("：", ":")
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def bank_path(bank: str, course: str) -> Path:
    return Path(bank) / course / "itembank.json"


def load_bank(bank: str, course: str) -> dict:
    p = bank_path(bank, course)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"course": course, "schema": "itembank/v1", "questions": []}


def save_bank(bank: str, course: str, data: dict) -> Path:
    p = bank_path(bank, course)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def cmd_ingest(a) -> int:
    src = Path(a.input)
    if not src.exists():
        print(f"找不到输入文件：{src}", file=sys.stderr)
        return 1
    payload = json.loads(src.read_text(encoding="utf-8"))
    questions = payload.get("questions") if isinstance(payload, dict) else payload
    if not isinstance(questions, list) or not questions:
        print("输入里没有任何题目（需要 questions 数组）", file=sys.stderr)
        return 1

    bank = load_bank(a.bank, a.course)
    have = {q.get("stem_hash") for q in bank["questions"]}
    have_ids = {q.get("id") for q in bank["questions"]}
    added, dup, bad = [], [], []
    for q in questions:
        missing = [f for f in REQUIRED_FIELDS if q.get(f) in (None, "")]
        if missing:
            bad.append({"id": q.get("id"), "missing": missing})
            continue
        h = stem_hash(q["stem"])
        if h in have:
            dup.append(q["id"])
            continue
        if q["id"] in have_ids:
            bad.append({"id": q.get("id"), "missing": [],
                        "conflict": "题号已被库中另一道题占用（题干不同），请改题号后重入"})
            continue
        item = dict(q)
        item["stem_hash"] = h
        item["status"] = q.get("status", "active")
        item["times_used"] = q.get("times_used", 0)
        item["ingested_term"] = a.term or str(date.today())
        bank["questions"].append(item)
        have.add(h)
        have_ids.add(q["id"])
        added.append(q["id"])

    out = save_bank(a.bank, a.course, bank)
    print(json.dumps({
        "bank": str(out), "added": added, "duplicates": dup,
        "rejected": bad, "total_in_bank": len(bank["questions"]),
        "note": "重复题已按题干哈希跳过；rejected 为缺必填字段或题号撞车的题，请处理后重入"
    }, ensure_ascii=False, indent=2))
    # 全部重复或存在缺字段题 → 需要人工看一眼，给非零码但不阻断流程
    return 2 if (bad or (dup and not added)) else 0


def cmd_search(a) -> int:
    bank = load_bank(a.bank, a.course)
    hits = bank["questions"]
    if a.kp:
        hits = [q for q in hits if a.kp in str(q.get("kp", ""))]
    if a.type:
        hits = [q for q in hits if q.get("type") == a.type]
    if a.bloom:
        hits = [q for q in hits if q.get("bloom") == a.bloom]
    if a.status:
        hits = [q for q in hits if q.get("status", "active") == a.status]
    else:
        hits = [q for q in hits if q.get("status", "active") == "active"]
    preview = []
    for q in hits:
        row = {"id": q["id"], "kp": q["kp"], "type": q["type"], "bloom": q["bloom"],
               "est": q.get("est_difficulty"), "actual": q.get("actual_difficulty"),
               "times_used": q.get("times_used", 0),
               "review_status": q.get("review_status", "未审核")}
        if a.full:
            row["stem"] = q["stem"]
            row["options"] = q.get("options")
        else:
            row["stem"] = str(q["stem"])[:40]
        preview.append(row)
    print(json.dumps({"course": a.course, "hits": len(hits), "questions": preview},
                     ensure_ascii=False, indent=2))
    return 0


def _read_id_csv(path, id_col, val_col=None):
    rows = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            qid = (r.get(id_col) or "").strip()
            if qid:
                rows[qid] = (r.get(val_col) or "").strip() if val_col else ""
    return rows


def cmd_retire(a) -> int:
    bank = load_bank(a.bank, a.course)
    ids = set(a.ids.split(",")) if a.ids else set(_read_id_csv(a.csv, "question_id", None))
    if not ids:
        print("没有给出任何要淘汰的题号", file=sys.stderr)
        return 1
    have = {q["id"] for q in bank["questions"]}
    miss = sorted(ids - have)
    n = 0
    for q in bank["questions"]:
        if q["id"] in ids and q.get("status") != "retired":
            q["status"] = "retired"
            q["retire_reason"] = a.reason
            n += 1
    save_bank(a.bank, a.course, bank)
    print(json.dumps({"retired": n, "not_found": miss,
                      "note": "淘汰题保留在库中不再被 search 默认检出；not_found 需人工核对题号"},
                     ensure_ascii=False, indent=2))
    return 2 if miss else 0


def cmd_calibrate(a) -> int:
    bank = load_bank(a.bank, a.course)
    actual = _read_id_csv(a.csv, "question_id", "actual_p")
    if not actual:
        print("CSV 里没有可用数据（需要 question_id,actual_p 两列）", file=sys.stderr)
        return 1
    have = {q["id"]: q for q in bank["questions"]}
    miss, rows = [], []
    for qid, p in actual.items():
        q = have.get(qid)
        if q is None:
            miss.append(qid)
            continue
        try:
            q["actual_difficulty"] = float(p)
        except ValueError:
            miss.append(qid)
            continue
        q["times_used"] = int(q.get("times_used", 0)) + 1
        est = q.get("est_difficulty")
        rows.append({"id": qid, "est": est, "actual": q["actual_difficulty"],
                     "delta": round(q["actual_difficulty"] - est, 3)
                     if isinstance(est, (int, float)) else None})
    save_bank(a.bank, a.course, bank)
    deltas = [r["delta"] for r in rows if r["delta"] is not None]
    print(json.dumps({"calibrated": len(rows), "not_found": miss, "detail": rows,
                      "mean_delta": round(sum(deltas) / len(deltas), 3) if deltas else None,
                      "note": "mean_delta > 0 说明整体估偏难；写进出题自检报告的「预估校准」小节"},
                     ensure_ascii=False, indent=2))
    return 2 if miss else 0


def cmd_stats(a) -> int:
    if a.course and not bank_path(a.bank, a.course).exists():
        print(f"课程 {a.course} 还没有归档（{bank_path(a.bank, a.course)} 不存在）", file=sys.stderr)
        return 1
    courses = [a.course] if a.course else sorted(
        p.parent.name for p in Path(a.bank).glob("*/itembank.json"))
    if not courses:
        print(f"题库目录 {a.bank} 下还没有任何课程归档", file=sys.stderr)
        return 1
    out = {}
    for c in courses:
        bank = load_bank(a.bank, c)
        qs = bank["questions"]
        act = [q for q in qs if q.get("status", "active") == "active"]
        by_kp = {}
        for q in act:
            by_kp[q.get("kp", "?")] = by_kp.get(q.get("kp", "?"), 0) + 1
        cal = [q for q in qs if isinstance(q.get("actual_difficulty"), (int, float))]
        out[c] = {"total": len(qs), "active": len(act), "retired": len(qs) - len(act),
                  "by_type": {t: sum(1 for q in act if q.get("type") == t)
                              for t in sorted({q.get("type") for q in act})},
                  "kp_top": sorted(by_kp.items(), key=lambda x: -x[1])[:5],
                  "calibrated": len(cal)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(prog="itembank", description="题库归档与复用（按课程）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--bank", required=True, help="题库根目录，如 题库")
        p.add_argument("--course", required=True, help="课程名（归档单元）")

    p = sub.add_parser("ingest", help="把 quiz-generator 的题库.json 归档进课程题库")
    common(p); p.add_argument("--in", dest="input", required=True)
    p.add_argument("--term", default="", help="学期标记，如 2025-2026-1")
    p.set_defaults(fn=cmd_ingest)

    p = sub.add_parser("search", help="按知识点/题型/层次检索可复用题")
    common(p); p.add_argument("--kp"); p.add_argument("--type"); p.add_argument("--bloom")
    p.add_argument("--status", default="active"); p.add_argument("--full", action="store_true")
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser("retire", help="标记淘汰题（考后 D<0.2 的题不再复用）")
    common(p); p.add_argument("--ids"); p.add_argument("--csv")
    p.add_argument("--reason", default="考后区分度 D<0.2，按 exam-pipeline 回传淘汰")
    p.set_defaults(fn=cmd_retire)

    p = sub.add_parser("calibrate", help="回填考后实测难度 P（CSV: question_id,actual_p）")
    common(p); p.add_argument("--csv", required=True)
    p.set_defaults(fn=cmd_calibrate)

    p = sub.add_parser("stats", help="题库总览（可省略 --course 看全部课程）")
    p.add_argument("--bank", required=True); p.add_argument("--course")
    p.set_defaults(fn=cmd_stats)

    a = ap.parse_args()
    if getattr(a, "cmd", None) in ("retire",) and not (a.ids or a.csv):
        print("retire 需要 --ids 或 --csv 之一", file=sys.stderr)
        sys.exit(1)
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
