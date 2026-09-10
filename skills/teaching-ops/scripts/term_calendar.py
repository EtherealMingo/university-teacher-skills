#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""teaching-ops 学期时间节点倒排表 —— 用「第几周要交什么」代替脑子里的记性。

输入只要一个真实锚点：**本学期第 1 周周一**。其余日期由周次推算，
节假日由教师提供的校历导入（本工具不内置任何年份的法定节假日安排）。

    PY="vendor/office-layer/.venv/bin/python"
    $PY skills/teaching-ops/scripts/term_calendar.py \\
        --start 2026-03-02 --weeks 18 --exam-weeks 17,18 \\
        --holidays 2026-04-06,2026-05-01 \\
        --spec 过程/倒排spec.json
    $PY vendor/office-layer/scripts/xlsx_kit.py build \\
        --spec 过程/倒排spec.json --out 学期时间节点倒排表.xlsx

**重要**：默认节点是高校教学运行的通行惯例，用于提醒「别漏事」，
各校口径（提交对象、提前天数、系统名称）不同 —— 表里每行都留了
「以本校文件为准」的核对列，教师必须逐行对本校教务处通知核实后再用。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 默认节点：offset 为「第 1 周周一」起算的天数偏移，负数表示开学前
DEFAULT_NODES = [
    (-14, "教材申报与到货核对", "开学前 2 周", "教材科/教务处",
     "核对 ISBN、版次、到书数量；漏订在开学前还能补"),
    (-7, "课表与教室确认", "开学前 1 周", "教务处/开课学院",
     "核对本人课表、教室与设备；发现冲突此时还能改"),
    (0, "教学日历 / 授课计划提交", "第 1 周", "学院教学办",
     "按大纲学时分解到周；提交后修改需走变更"),
    (0, "点名册与选课名单核对", "第 1 周", "教务系统",
     "核对选课名单与实际到课学生，退补选结束前处理异常"),
    (7, "教学资料（大纲/教案）归档", "第 2 周", "学院教学办",
     "多数学校要求第 2 周前完成课程档案首轮归档"),
    (14, "补考 / 缓考安排确认", "第 3 周", "教务处考务",
     "确认补考名单、时间地点与监考；缓考学生单独通知"),
    (49, "期中教学检查材料", "第 8 周", "学院/督导",
     "教案、作业批改样本、考勤记录；按学院清单准备"),
    (105, "期末考试排期上报", "第 16 周", "教务处考务",
     "报考试科目、班级、人数、时长、考场容量与设备需求"),
    (105, "监考需求汇总与监考表报送", "第 16 周", "教务处考务",
     "汇总需求 → 排监考 → 与同事协调 → 报教务审批"),
    (112, "考试周（停课）", "第 17-18 周", "教务处考务",
     "考试周原则上不排课；补课须提前获批"),
    (126, "成绩录入截止", "考试周后 2 周内", "教务系统",
     "以本校通知的确切截止时间为准，逾期改分要另走流程"),
    (133, "试卷与教学资料归档", "学期结束后", "学院教学办",
     "试卷、成绩单、试卷分析、教学总结一并归档"),
]


def parse_date(s: str):
    s = (s or "").strip().replace("/", "-")
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(prog="term_calendar",
                                 description="学期时间节点倒排表 → xlsx_kit spec")
    ap.add_argument("--start", required=True, help="本学期第 1 周周一，YYYY-MM-DD")
    ap.add_argument("--weeks", type=int, default=18, help="学期总周次，默认 18")
    ap.add_argument("--exam-weeks", default="17,18", help="考试周，逗号分隔；留空表示无")
    ap.add_argument("--holidays", default="", help="节假日/停课日，逗号分隔（以本校校历为准）")
    ap.add_argument("--nodes", help="覆盖默认节点：JSON 文件，[{\"offset\":天数,\"task\":\"…\",…}]")
    ap.add_argument("--spec", required=True, help="输出 xlsx_kit 规格 JSON")
    args = ap.parse_args()

    start = parse_date(args.start)
    if start is None:
        sys.stderr.write(f"开学首日格式错误：{args.start!r}，应为 YYYY-MM-DD\n")
        return 3
    if start.weekday() != 0:
        sys.stderr.write(
            f"提示：{start.isoformat()} 是{WEEKDAY_CN[start.weekday()]}，不是周一。\n"
            f"本工具按「第 1 周周一」推算，若贵校第 1 周从其他日期起算，请改传该周周一。\n"
        )
    hol = {}
    for x in (args.holidays or "").replace("，", ",").split(","):
        d = parse_date(x)
        if d:
            hol[d] = True
    exam_weeks = []
    for x in (args.exam_weeks or "").replace("，", ",").split(","):
        x = x.strip()
        if x.isdigit():
            exam_weeks.append(int(x))

    nodes = DEFAULT_NODES
    if args.nodes:
        try:
            with open(args.nodes, encoding="utf-8") as f:
                nodes = json.load(f)
        except Exception as e:
            sys.stderr.write(f"节点文件读取失败：{e}\n")
            return 3

    # ---- 倒排表：锚点日期 = 第 1 周周一 + offset
    node_rows = []
    for n in nodes:
        if isinstance(n, dict):
            off = int(n["offset"])
            task = n.get("task", "【待补：任务】")
            node = n.get("node", "")
            owner = n.get("owner", "【待补：负责部门】")
            why = n.get("why", "")
        else:  # 内置节点为 (offset, task, node, owner, why) 五元组
            off, task, node, owner, why = n
        d = start + timedelta(days=off)
        wk = off // 7 + 1
        node_rows.append([
            task,
            d.isoformat(),
            f"第 {wk} 周" if off >= 0 else f"开学前 {-off // 7} 周",
            WEEKDAY_CN[d.weekday()],
            node,
            owner,
            why,
            "【待教师确认：本校确切时间与提交系统】",
            hol.get(d, False) and "该日已在节假日清单中" or "",
        ])

    # ---- 周次日历
    week_rows = []
    for w in range(1, args.weeks + 1):
        mon = start + timedelta(days=(w - 1) * 7)
        sun = mon + timedelta(days=6)
        tag = []
        if w in exam_weeks:
            tag.append("考试周")
        hit = [ (mon + timedelta(days=i)).isoformat() for i in range(7)
                if (mon + timedelta(days=i)) in hol ]
        if hit:
            tag.append("含节假日 " + "、".join(hit))
        week_rows.append([
            f"第 {w} 周", f"{mon.isoformat()} ~ {sun.isoformat()}",
            "；".join(tag) or "正常教学周",
            "【待补：本周关键节点】",
        ])

    spec = {"sheets": [
        {
            "name": "时间节点倒排表",
            "header": ["任务", "锚点日期", "周次", "星期", "节点说明",
                       "负责部门/提交对象", "为什么不能漏", "校历核对位", "备注"],
            "rows": node_rows,
            "widths": [22, 12, 10, 8, 14, 18, 34, 26, 22],
        },
        {
            "name": "周次日历",
            "header": ["周次", "起止日期", "周次标记", "教师填本周节点"],
            "rows": week_rows,
            "widths": [10, 26, 30, 30],
        },
        {
            "name": "口径与免责",
            "header": ["项目", "内容"],
            "rows": [
                ["开学首日（第 1 周周一）", start.isoformat()],
                ["学期总周次", args.weeks],
                ["考试周", "、".join(f"第 {w} 周" for w in exam_weeks) or "【待补：本校考试周】"],
                ["节假日来源", "由教师提供的校历数据；本工具**不内置任何年份的法定节假日安排**"],
                ["节点依据", "高校教学运行通行惯例，用于防漏；"
                             "**各校提交对象、提前天数与系统名称不同，以本校教务处通知为准**"],
                ["下一步", "1) 把每行「校历核对位」逐条对本校教务处通知核实 "
                            "2) 把确切截止日期填回锚点日期列 3) 删除无效行并补充本校特有节点"],
            ],
            "widths": [26, 76],
        },
    ]}

    with open(args.spec, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "开学首日": start.isoformat(),
        "学期周次": args.weeks,
        "考试周": exam_weeks,
        "节点数": len(node_rows),
        "节假日数": len(hol),
        "spec": args.spec,
        "提示": "默认节点为通行惯例，日期需逐行换成本校教务通知的确切时间后再用。",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
