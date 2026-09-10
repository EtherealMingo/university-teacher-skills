#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""组会轮值表生成器 —— 输出 office-layer 可吃的 spec.json

只做「排期计算 + 出 spec」，不直接写 xlsx。
落盘一律走 office-layer：

    PY="skills/office-layer/.venv/bin/python"
    $PY skills/lab-meeting/scripts/roster_plan.py --students a.txt ... --out spec.json
    $PY skills/office-layer/scripts/xlsx_kit.py build --spec spec.json --out 组会轮值表.xlsx

生成逻辑（四步，全部可解释）：
  1. 按频率（每周/双周）从开学首日铺出学期周次 → 会议槽位 slots
  2. 剔除节假日与导师冲突周：**保留行**但标【跳过/顺延】，不消耗汇报人
  3. 预答辩槽位倒排：最后 k 个槽位留给 --predefense 指定学生，一人一场
  4. 其余槽位按公平性贪心分配：优先「次数最少」，硬约束「不与上一场重复」

公平性硬约束：任何学生不得在相邻两场有效组会连续汇报。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

# 汇报类型默认轮换顺序
DEFAULT_TYPES = ["文献汇报", "进展汇报", "预答辩"]
PREDEFENSE = "预答辩"

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# ------------------------------------------------------------------ 输入
def parse_date(s: str) -> date:
    try:
        y, m, d = (int(x) for x in s.strip().replace("/", "-").split("-"))
        return date(y, m, d)
    except Exception:
        raise SystemExit(f"日期格式错误：{s!r}，应为 YYYY-MM-DD")


def load_students(args) -> list[str]:
    names: list[str] = []
    if args.students:
        names += [n.strip() for n in args.students.replace("，", ",").split(",")]
    if args.students_file:
        with open(args.students_file, encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if line:
                    names.append(line)
    # 去重保序
    seen, out = set(), []
    for n in names:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def load_dates(val: str | None) -> set[date]:
    if not val:
        return set()
    return {parse_date(x) for x in val.replace("，", ",").split(",") if x.strip()}


# ------------------------------------------------------------------ 排期
def build_slots(start: date, weeks: int, frequency: str) -> list[dict]:
    """铺出学期会议槽位。weeks=学期周次总数。"""
    step = 7 if frequency == "weekly" else 14
    slots, d, wk = [], start, 1
    while wk <= weeks:
        slots.append({"week": wk, "date": d})
        d += timedelta(days=step)
        wk += 1 if frequency == "weekly" else 2
    return slots


def assign(slots, students, holidays, blocked, types, per_meeting, predefense):
    """贪心分配，返回行记录。"""
    # 1) 标记跳过
    for s in slots:
        if s["date"] in holidays:
            s["skip"] = "【节假日跳过】"
        elif s["date"] in blocked:
            s["skip"] = "【导师时间冲突，顺延】"
        else:
            s["skip"] = None
    active = [s for s in slots if not s["skip"]]

    # 2) 预答辩槽位倒排
    reserved: dict[int, str] = {}
    if predefense:
        k = min(len(predefense), len(active))
        if k:
            tail = active[-k:]
            for slot, name in zip(tail, predefense):
                reserved[id(slot)] = name

    # 3) 类型轮换（在非预答辩槽位上循环）
    non_pre = [t for t in types if t != PREDEFENSE] or ["文献汇报", "进展汇报"]
    free_active = [s for s in active if id(s) not in reserved]
    for i, s in enumerate(free_active):
        s["type"] = non_pre[i % len(non_pre)]
    for s in active:
        if id(s) in reserved:
            s["type"] = PREDEFENSE

    # 4) 公平性贪心
    count = {n: 0 for n in students}
    disc_count = {n: 0 for n in students}
    prev_speakers: set[str] = set()
    fallback_note: list[str] = []

    for i, s in enumerate(active):
        if id(s) in reserved:
            speakers = [reserved[id(s)]]
            pool = [n for n in students if n not in speakers]
            if not pool:
                pool = speakers
            # 预答辩场次点评人取「点评次数最少」且在预答辩名单外者
            discussant = min(pool, key=lambda n: (disc_count[n], n))
        else:
            pool = [n for n in students if n not in prev_speakers]
            if len(pool) < per_meeting:
                # 硬约束无法满足（人太少），放宽并记录，绝不静默造假
                fallback_note.append(
                    f"第{s['week']}周：学生数不足以规避连续汇报，已放宽该约束"
                )
                pool = list(students)
            speakers = sorted(
                pool, key=lambda n: (count[n], n)
            )[:per_meeting]
            rest = [n for n in students if n not in speakers]
            discussant = min(rest or students, key=lambda n: (disc_count[n], n))

        for n in speakers:
            count[n] += 1
        disc_count[discussant] += 1
        s["speakers"] = speakers
        s["discussant"] = discussant
        prev_speakers = set(speakers)

    return active, count, disc_count, fallback_note


# ------------------------------------------------------------------ 出表
def make_rows(slots, per_meeting):
    rows = []
    for s in slots:
        if s["skip"]:
            rows.append([
                f"第{s['week']}周", s["date"].isoformat(), "—", "—",
                "", "—", s["skip"],
            ])
            continue
        for idx, sp in enumerate(s["speakers"]):
            rows.append([
                f"第{s['week']}周",
                s["date"].isoformat(),
                sp,
                s["type"],
                "【待补：汇报主题】",
                s["discussant"],
                "【待补：备注】" if idx else "",
            ])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(prog="roster_plan", description="组会轮值表 → xlsx_kit spec")
    ap.add_argument("--students", help="学生名单，逗号分隔（中文逗号也可）")
    ap.add_argument("--students-file", help="学生名单文件，一行一名，# 后为注释")
    ap.add_argument("--start", required=True, help="开学首个组会日期 YYYY-MM-DD")
    ap.add_argument("--weeks", type=int, default=18, help="学期周次总数，默认 18")
    ap.add_argument("--frequency", choices=["weekly", "biweekly"], default="weekly")
    ap.add_argument("--per-meeting", type=int, default=1, help="每场汇报人数，默认 1")
    ap.add_argument("--types", default=",".join(DEFAULT_TYPES), help="汇报类型轮换顺序")
    ap.add_argument("--holidays", default="", help="节假日日期，逗号分隔")
    ap.add_argument("--blocked", default="", help="导师冲突日期，逗号分隔")
    ap.add_argument("--predefense", default="", help="需预答辩的学生，逗号分隔（排在期末）")
    ap.add_argument("--out", required=True, help="输出 spec.json 路径")
    args = ap.parse_args()

    students = load_students(args)
    if not students:
        sys.stderr.write(
            "错误：未提供学生名单（--students 或 --students-file）。\n"
            "本工具不虚构学生姓名 —— 请先给名单。\n"
        )
        return 2

    start = parse_date(args.start)
    holidays = load_dates(args.holidays)
    blocked = load_dates(args.blocked)
    types = [t.strip() for t in args.types.replace("，", ",").split(",") if t.strip()]
    predefense = [n.strip() for n in args.predefense.replace("，", ",").split(",") if n.strip()]
    predefense = [n for n in predefense if n in students]

    slots = build_slots(start, args.weeks, args.frequency)
    active, count, disc_count, notes = assign(
        slots, students, holidays, blocked, types, args.per_meeting, predefense
    )

    rows = make_rows(slots, args.per_meeting)

    stat_rows = [
        [n, count[n], disc_count[n],
         "✔ 均衡" if max(count.values()) - count[n] <= 1 else "⚠ 次数偏少"]
        for n in students
    ]

    spec = {
        "sheets": [
            {
                "name": "组会轮值表",
                "header": ["周次", "日期", "汇报人", "汇报类型", "主题", "点评人", "备注"],
                "rows": rows,
                "freeze": True,
                "widths": [10, 13, 12, 12, 30, 10, 22],
            },
            {
                "name": "公平性统计",
                "header": ["姓名", "汇报次数", "点评次数", "均衡检查"],
                "rows": stat_rows,
                "widths": [14, 12, 12, 14],
                "chart": {
                    "type": "bar",
                    "title": "各生汇报次数",
                    "value_col": 2,
                    "height": 9,
                    "width": 16,
                },
            },
        ]
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    report = {
        "out": args.out,
        "学期槽位": len(slots),
        "有效组会": len(active),
        "跳过": len(slots) - len(active),
        "汇报次数": count,
        "点评次数": disc_count,
        "公平性告警": notes,
        "提示": "主题与备注为占位，请教师与学生补全",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
