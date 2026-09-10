#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""teaching-ops 监考表排班器 —— 生成「需求 × 教师」的监考安排，并自报缺口。

设计原则（对应 SKILL.md 的冲突检测表）：
  · 硬约束（违反即不排，绝不静默将就）：
      同一人同一时段只能一个考场 / 不可用日期不排 / 本人该时段有课不排
  · 软约束（违反则人工复核，不阻断）：
      回避本人授课班级（可关）、回避本人任班主任班级、单人不超上限
  · 公平：按「已排场次最少」优先，同次数按姓名排序 —— 结果确定、可复现
  · 排不满就报缺口（blocked），**不用凑数的人填坑**

只输出 spec.json / 核对 JSON，落盘一律交 office-layer：

    PY="skills/office-layer/.venv/bin/python"
    $PY skills/teaching-ops/scripts/invigilation_plan.py \\
        --in 过程/排期数据.json --spec 过程/监考spec.json \\
        --out-check 过程/监考核对.json
    $PY skills/office-layer/scripts/xlsx_kit.py build \\
        --spec 过程/监考spec.json --out 监考表.xlsx
    $PY skills/teaching-ops/scripts/conflict_check.py \\
        --in 过程/监考核对.json --report 过程/监考核对报告.md

退出码：0 = 排满（仍需人工复核）；2 = 有缺口或硬约束导致排不满；3 = 输入不可用。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date


def die(msg: str, code: int = 3) -> int:
    sys.stderr.write(msg.rstrip() + "\n")
    return code


def to_min(hm):
    try:
        h, m = (hm or "").strip().split(":")
        h, m = int(h), int(m)
    except Exception:
        return None
    if not (0 <= h <= 23 and 0 <= m <= 59):
        return None
    return h * 60 + m


def parse_date(s):
    s = (s or "").strip().replace("/", "-")
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except Exception:
        return None


def overlap(a, b) -> bool:
    return a["date"] == b["date"] and a["s"] < b["e"] and b["s"] < a["e"]


def main() -> int:
    ap = argparse.ArgumentParser(prog="invigilation_plan",
                                 description="监考需求 → 排班 → xlsx_kit spec")
    ap.add_argument("--in", dest="src", required=True, help="排期数据 JSON")
    ap.add_argument("--spec", required=True, help="输出 xlsx_kit 规格 JSON")
    ap.add_argument("--out-check", help="输出带 assignments 的核对 JSON（供 conflict_check 复检）")
    ap.add_argument("--allow-own-class", action="store_true",
                    help="本校无「任课教师回避本班监考」规定时加上此开关")
    ap.add_argument("--max-slots", type=int, help="覆盖名单里的单人监考上限")
    args = ap.parse_args()

    try:
        with open(args.src, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return die(f"找不到输入文件：{args.src}")
    except json.JSONDecodeError as e:
        return die(f"输入不是合法 JSON：{args.src}\n{e}")

    inv = data.get("invigilation") or {}
    reqs_raw = inv.get("requirements") or []
    teachers_raw = inv.get("teachers") or []
    rules = inv.get("rules") or {}
    if not reqs_raw:
        return die("监考需求为空（invigilation.requirements）——\n"
                   "本工具不虚构考试科目/时间/考场，请先汇总真实需求。", 2)
    if not teachers_raw:
        return die("教师名单为空（invigilation.teachers）——\n"
                   "本工具不虚构教师姓名，请先提供本单位可参加监考的教师名单。", 2)

    avoid_own = not args.allow_own_class and rules.get("avoid_own_class", True)
    avoid_home = rules.get("avoid_homeroom", True)

    # ---- 需求
    reqs = []
    for i, r in enumerate(reqs_raw, 1):
        rid = str(r.get("id") or f"I{i}")
        d, s, e = parse_date(r.get("date", "")), to_min(r.get("start", "")), to_min(r.get("end", ""))
        need = r.get("need")
        if d is None or s is None or e is None:
            return die(f"监考需求 {rid} 的考试时间缺失或格式错误："
                       f"date={r.get('date')!r} start={r.get('start')!r} end={r.get('end')!r}")
        if not isinstance(need, int) or need < 1:
            return die(f"监考需求 {rid} 未给定需监考人数（need）——\n"
                       f"监考人数定额各校不同，请查本校教务文件后填入，本工具不猜。")
        reqs.append({
            "id": rid, "course": (r.get("course") or "").strip(),
            "class": (r.get("class") or "").strip(),
            "room": (r.get("room") or "").strip(),
            "date": d, "s": s, "e": e, "need": need,
            "raw_date": r.get("date", ""), "raw_start": r.get("start", ""),
            "raw_end": r.get("end", ""),
        })
    reqs.sort(key=lambda r: (r["date"], r["s"], r["id"]))

    # ---- 教师
    teachers = {}
    for t in teachers_raw:
        name = (t.get("name") or "").strip()
        if not name:
            continue
        cap = args.max_slots if args.max_slots is not None else t.get("max_slots")
        teachers[name] = {
            "name": name,
            "teaches": [x for x in (t.get("teaches") or []) if x],
            "homeroom": [x for x in (t.get("homeroom") or []) if x],
            "unavailable": {parse_date(x) for x in (t.get("unavailable") or []) if parse_date(x)},
            "max_slots": cap if isinstance(cap, int) else None,
            "note": (t.get("note") or "").strip(),
            "count": 0,
        }
    if not teachers:
        return die("教师名单里没有有效姓名。", 2)

    # ---- 本人已有课时（用于「不排本人有课时段」）
    busy = {}
    for r in (data.get("events") or []):
        if (r.get("status") or "active") != "active":
            continue
        name = (r.get("teacher") or "").strip()
        d, s, e = parse_date(r.get("date", "")), to_min(r.get("start", "")), to_min(r.get("end", ""))
        if name in teachers and d and s is not None and e is not None:
            busy.setdefault(name, []).append(
                {"date": d, "s": s, "e": e,
                 "what": f"{r.get('course') or '课程'}({r.get('id') or '?'})"})

    # ---- 预置安排（如教务已定的人），计入次数与占用
    picked = {r["id"]: [] for r in reqs}
    for a in (inv.get("assignments") or []):
        rid = str(a.get("req_id") or a.get("rid") or "")
        who = (a.get("teacher") or "").strip()
        if rid in picked and who in teachers and who not in picked[rid]:
            picked[rid].append(who)
            teachers[who]["count"] += 1

    # ---- 贪心排班
    why = []  # 每个人的落选原因，便于出「缺口说明」
    for req in reqs:
        while len(picked[req["id"]]) < req["need"]:
            cands = []
            for name, t in teachers.items():
                if name in picked[req["id"]]:
                    continue
                if t["max_slots"] is not None and t["count"] >= t["max_slots"]:
                    why.append((req["id"], name, "已达本人监考上限"))
                    continue
                if req["date"] in t["unavailable"]:
                    why.append((req["id"], name, "该日已登记不可用（请假/出差）"))
                    continue
                if any(overlap(req, b) for b in busy.get(name, [])):
                    why.append((req["id"], name, "该时段本人有课"))
                    continue
                if any(overlap(req, r2) for r2 in reqs
                       if name in picked.get(r2["id"], []) and r2["id"] != req["id"]):
                    why.append((req["id"], name, "该时段已排其他考场"))
                    continue
                if avoid_own and req["class"] and req["class"] in t["teaches"]:
                    why.append((req["id"], name, "本人授课班级（按规定回避）"))
                    continue
                if avoid_home and req["class"] and req["class"] in t["homeroom"]:
                    why.append((req["id"], name, "本人班主任班级"))
                    continue
                cands.append(name)
            if not cands:
                break
            pick = sorted(cands, key=lambda n: (teachers[n]["count"], n))[0]
            picked[req["id"]].append(pick)
            teachers[pick]["count"] += 1

    gaps = []
    for req in reqs:
        got = len(picked[req["id"]])
        if got < req["need"]:
            gaps.append({
                "需求": req["id"], "科目": req["course"], "日期": req["raw_date"],
                "时段": f"{req['raw_start']}-{req['raw_end']}", "考场": req["room"],
                "需要": req["need"], "已排": got, "缺": req["need"] - got,
            })

    # ---- 出表
    assign_rows, seq = [], 0
    for req in reqs:
        for k, name in enumerate(picked[req["id"]]):
            seq += 1
            assign_rows.append([
                seq, req["course"] or "【待补：科目】", req["raw_date"],
                req["raw_start"], req["raw_end"],
                req["room"] or "【待补：考场】", name,
                "主监考" if k == 0 else "监考",
                f"【待教师确认：{req['raw_date']} 是否可监考】",
            ])
    for req in reqs:
        for k in range(len(picked[req["id"]]), req["need"]):
            seq += 1
            assign_rows.append([
                seq, req["course"] or "【待补：科目】", req["raw_date"],
                req["raw_start"], req["raw_end"],
                req["room"] or "【待补：考场】",
                "【待补：需教务协调监考】",
                "主监考" if k == 0 else "监考",
                "本工具不虚构人名，缺口须由教务/教研室协调",
            ])

    counts = {n: t["count"] for n, t in teachers.items()}
    vals = [v for v in counts.values() if v]
    spread = (max(vals) - min(vals)) if len(vals) >= 2 else 0
    tol = rules.get("balance_tolerance", 1)

    stat_rows = [[
        n, t["count"], t["max_slots"] if t["max_slots"] is not None else "—",
        "、".join(t["teaches"]) or "—",
        "、".join(sorted(d.isoformat() for d in t["unavailable"])) or "—",
        ("✔ 均衡" if vals and abs(t["count"] - sum(vals) / len(vals)) <= 1 else "⚠ 偏高")
        if t["count"] else "⚠ 本次未安排",
        t["note"] or "",
    ] for n, t in sorted(teachers.items())]

    spec = {"sheets": [
        {
            "name": "监考需求汇总",
            "header": ["需求编号", "考试科目", "班级", "日期", "起", "止",
                       "考场", "需监考人数", "已排", "缺口"],
            "rows": [[r["id"], r["course"] or "【待补：科目】",
                      r["class"] or "【待补：班级】", r["raw_date"], r["raw_start"],
                      r["raw_end"], r["room"] or "【待补：考场】", r["need"],
                      len(picked[r["id"]]), r["need"] - len(picked[r["id"]])]
                     for r in reqs],
            "widths": [10, 18, 12, 12, 7, 7, 12, 12, 8, 8],
        },
        {
            "name": "监考安排表",
            "header": ["序号", "考试科目", "日期", "起", "止", "考场",
                       "监考教师", "角色", "备注"],
            "rows": assign_rows,
            "widths": [6, 18, 12, 7, 7, 12, 20, 10, 34],
        },
        {
            "name": "均衡与可用性统计",
            "header": ["教师", "已排场次", "上限", "任课班级", "不可用日期", "均衡", "备注"],
            "rows": stat_rows,
            "widths": [12, 10, 8, 22, 22, 12, 20],
            "chart": {"type": "bar", "title": "各教师监考场次", "value_col": 2,
                      "height": 9, "width": 16},
        },
        {
            "name": "缺口与说明",
            "header": ["项目", "内容"],
            "rows": (
                [["缺口数", len(gaps)],
                 ["总体判定",
                  "存在排不满的考场，须由教务/教研室协调补人；安排表里的"
                  "「【待补：需教务协调监考】」即缺口位置"] if gaps else
                  ["总体判定", "全部考场已排满；仍需逐人与本人确认时间后再定稿"],
                 ["回避规则",
                  ("已启用：任课教师不监考本人授课班级" if avoid_own
                   else "已关闭任课班级回避 —— 仅在确认本校无此规定时使用") +
                  ("；班主任回避已启用" if avoid_home else "")],
                 ["数据来源", "依据教师提供的考试需求与教师名单；各校监考定额、"
                              "回避、减免规定不同，**以本校教务文件为准**"],
                 ["下一步", "1) 逐人征求同意 2) 报教务审批 3) 审批后按" 
                            "「监考须知」发通知 4) 考前核对考场与试卷份数"]]
                + ([] if not gaps else [["缺口明细", ""]] +
                   [[f"{g['需求']} {g['科目']} {g['日期']} {g['时段']} {g['考场']}",
                     f"需 {g['需要']} 人，已排 {g['已排']} 人，缺 {g['缺']} 人"]
                    for g in gaps])
            ),
            "widths": [16, 70],
        },
    ]}

    with open(args.spec, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    if args.out_check:
        out = dict(data)
        inv2 = dict(inv)
        inv2["assignments"] = [
            {"req_id": r["id"], "teacher": n,
             "role": "主监考" if k == 0 else "监考"}
            for r in reqs for k, n in enumerate(picked[r["id"]])
        ]
        out["invigilation"] = inv2
        with open(args.out_check, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    # 落选原因汇总（只保留有信息的）
    reason_stat = {}
    for rid, name, r in why:
        reason_stat.setdefault(r, set()).add(name)

    summary = {
        "需求数": len(reqs), "教师数": len(teachers),
        "已排人次": sum(counts.values()),
        "监考次数": counts,
        "最多/最少": [max(vals), min(vals)] if vals else [0, 0],
        "均衡差": spread,
        "均衡容差": tol,
        "缺口": gaps,
        "排不满原因分布": {k: sorted(v) for k, v in sorted(reason_stat.items())},
        "spec": args.spec, "核对数据": args.out_check,
        "提示": "安排表只是草稿：涉及同事，须逐人协调并报教务审批；"
                "审批后再发通知。",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
