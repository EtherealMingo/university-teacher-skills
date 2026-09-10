#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""teaching-ops 排期冲突检测器 —— 把「人 × 时间 × 空间」的交叉核对变成一次跑批。

不写 xlsx、不写 docx，只做两件事：
  1. 按规则逐条查冲突，输出分级问题清单（blocked / needs-review / advisory）
  2. 输出 office-layer 可吃的 spec.json，交给 xlsx_kit.py build 落盘

用法：

    PY="skills/office-layer/.venv/bin/python"
    $PY skills/teaching-ops/scripts/conflict_check.py \\
        --in 过程/排期数据.json --spec 过程/冲突spec.json \\
        --report 过程/冲突报告.md

退出码：0 = 无 blocked；2 = 存在 blocked（**不得忽略**，必须先解决再排期）；
        3 = 输入文件缺失或不是合法 JSON。

数据格式（全部字段从教师提供的真实材料来，**缺就留空，绝不替教师编**）：

{
  "term": {"name": "2025-2026-2", "start": "2026-03-02", "weeks": 18,
           "exam_weeks": [17, 18]},
  "holidays": ["2026-04-06"],
  "rooms": [{"room": "教三-201", "capacity": 60, "equipment": ["多媒体"]}],
  "rules": {"min_exam_gap_min": 30, "max_daily_invigilation": 2},
  "events": [
    {"id": "E1", "kind": "调课", "status": "active",
     "course": "数据结构", "teacher": "张明", "class": "计科2201",
     "date": "2026-03-12", "start": "08:00", "end": "09:40",
     "room": "教三-201", "students": 45,
     "origin": "原 3-11 周三 1-2 节", "approval": ""}
  ],
  "invigilation": {
    "requirements": [{"id": "I1", "course": "数据结构", "class": "计科2201",
                      "date": "2026-06-22", "start": "09:00", "end": "11:00",
                      "room": "教三-201", "need": 2}],
    "teachers": [{"name": "张明", "teaches": ["计科2201"],
                  "homeroom": ["计科2202"], "unavailable": ["2026-06-23"],
                  "max_slots": 3}],
    "assignments": [{"req_id": "I1", "teacher": "张明", "role": "主监考"}],
    "rules": {"avoid_own_class": true, "avoid_homeroom": true,
              "balance_tolerance": 1}
  }
}

status: active = 真实占用；cancelled = 原安排已取消（只留痕，不参与占用核对）。
调课 = 原时间一条 cancelled + 新时间一条 active；停课 = 原时间一条 cancelled。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date

LEVEL_ORDER = {"blocked": 0, "needs-review": 1, "advisory": 2}
LEVEL_CN = {"blocked": "阻断", "needs-review": "需人工复核", "advisory": "提示"}
HM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

# 需要「人 + 班 + 地」三要素齐全才谈得上核对的占用类事件
OCCUPY_KINDS = ("上课", "调课", "补课", "考试", "补考", "缓考", "其他")


# ------------------------------------------------------------------ 小工具
def die(msg: str, code: int = 3) -> "int":
    sys.stderr.write(msg.rstrip() + "\n")
    return code


def to_min(hm: str):
    m = HM_RE.match((hm or "").strip())
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def parse_date(s: str):
    s = (s or "").strip().replace("/", "-")
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except Exception:
        return None


def overlap(a, b) -> bool:
    """两条记录是否同日且时段相交。"""
    if a["date"] != b["date"]:
        return False
    return a["s"] < b["e"] and b["s"] < a["e"]


def week_of(term, d):
    start = parse_date(term.get("start", ""))
    if not start or not d:
        return None
    return (d - start).days // 7 + 1


class Issues:
    def __init__(self) -> None:
        self.rows = []

    def add(self, level: str, rule: str, where: str, msg: str, action: str) -> None:
        self.rows.append({
            "level": level, "rule": rule, "where": where,
            "msg": msg, "action": action,
        })

    def count(self, level: str) -> int:
        return sum(1 for r in self.rows if r["level"] == level)

    def sorted_rows(self):
        return sorted(self.rows, key=lambda r: (LEVEL_ORDER[r["level"]], r["rule"], r["where"]))


# ------------------------------------------------------------------ 事件规范化
def normalize(events, issues: Issues):
    """补齐字段、校验时间格式，返回可用于比对的记录。"""
    out = []
    for i, e in enumerate(events or [], 1):
        eid = str(e.get("id") or f"E{i}")
        where = f"事件 {eid}"
        status = (e.get("status") or "active").strip()
        if status not in ("active", "cancelled"):
            issues.add("blocked", "CHK-FIELD", where,
                       f"status 取值非法：{status!r}",
                       "改为 active（生效占用）或 cancelled（原安排已取消）")
            status = "active"
        d = parse_date(e.get("date", ""))
        s, en = to_min(e.get("start", "")), to_min(e.get("end", ""))
        if d is None or s is None or en is None:
            issues.add("blocked", "CHK-FIELD", where,
                       f"日期/起止时间缺失或格式错误：date={e.get('date')!r} "
                       f"start={e.get('start')!r} end={e.get('end')!r}",
                       "补成 YYYY-MM-DD 与 HH:MM（24 小时制）后再核对，"
                       "在此之前不得对外发布排期")
            continue
        if s >= en:
            issues.add("blocked", "CHK-TIME", where,
                       f"起止时间倒置或等长：{e.get('start')}-{e.get('end')}",
                       "核对节次对应的时间，修正后再核对")
            continue
        kind = (e.get("kind") or "上课").strip()
        rec = {
            "id": eid, "kind": kind, "status": status,
            "course": (e.get("course") or "").strip(),
            "teacher": (e.get("teacher") or "").strip(),
            "class": (e.get("class") or "").strip(),
            "room": (e.get("room") or "").strip(),
            "students": e.get("students"),
            "equipment": e.get("equipment") or [],
            "origin": (e.get("origin") or "").strip(),
            "approval": (e.get("approval") or "").strip(),
            "note": (e.get("note") or "").strip(),
            "date": d, "s": s, "e": en,
            "raw_date": e.get("date", ""), "raw_start": e.get("start", ""),
            "raw_end": e.get("end", ""),
        }
        out.append(rec)

        if status != "active":
            continue
        # 生效占用必须要素齐全，否则核对形同虚设
        missing = []
        if not rec["class"]:
            missing.append("class")
        if kind in ("上课", "调课", "补课", "其他") and not rec["teacher"]:
            missing.append("teacher")
        if kind in OCCUPY_KINDS and not rec["room"]:
            missing.append("room")
        if missing:
            issues.add("blocked", "CHK-FIELD", where,
                       f"生效占用缺字段：{'/'.join(missing)}",
                       "向教务/教师本人核实后补全，缺字段的排期无法做冲突核对")
        if kind in ("调课", "补课", "停课") and not rec["origin"]:
            issues.add("needs-review", "CHK-ORIGIN", where,
                       "调课/补课/停课未写明原上课时间与地点",
                       "补上「原 X 月 X 日 周 X 第 X 节 · 教室 X」，"
                       "这是教务审批表必填项")
        if kind in ("调课", "停课", "补课") and not rec["approval"]:
            issues.add("needs-review", "CHK-APPROVAL", where,
                       "未见教务审批状态（approval 为空）",
                       "本表只是送审材料；**未获教务批准前不得执行、不得通知学生**，"
                       "批准后把批件号/日期填进 approval")
    return out


# ------------------------------------------------------------------ 占用核对
def check_occupancy(recs, term, holidays, rooms, issues: Issues, rules=None):
    rules = rules or {}
    active = [r for r in recs if r["status"] == "active"]

    # 1) 人 × 时间
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            a, b = active[i], active[j]
            if a["teacher"] and a["teacher"] == b["teacher"] and overlap(a, b):
                issues.add("blocked", "CHK-TEACHER", f"教师 {a['teacher']}",
                           f"{a['raw_date']} {a['raw_start']}-{a['raw_end']} "
                           f"同一时段被排了两次：{a['id']}（{a['course']}）与 "
                           f"{b['id']}（{b['course']}）",
                           "二者只能留一个；改时间或在调课申请里说明取舍")
            # 2) 班级 × 时间
            if a["class"] and a["class"] == b["class"] and overlap(a, b):
                issues.add("blocked", "CHK-CLASS", f"班级 {a['class']}",
                           f"{a['raw_date']} {a['raw_start']}-{a['raw_end']} "
                           f"同一时段被排了两次：{a['id']}（{a['course']}）与 "
                           f"{b['id']}（{b['course']}）",
                           "学生无法同时上两门课；调整其中一场")
            # 3) 空间 × 时间
            if a["room"] and a["room"] == b["room"] and overlap(a, b):
                issues.add("blocked", "CHK-ROOM", f"教室 {a['room']}",
                           f"{a['raw_date']} {a['raw_start']}-{a['raw_end']} "
                           f"被 {a['teacher'] or '?'}（{a['id']}）与 "
                           f"{b['teacher'] or '?'}（{b['id']}）同时占用",
                           "换教室或换时段；换教室后要同步教室借用登记")

    # 4) 节假日 / 校历
    hol = set()
    for h in holidays or []:
        d = parse_date(h)
        if d:
            hol.add(d)
    for r in active:
        if r["date"] in hol:
            issues.add("blocked", "CHK-HOLIDAY", f"事件 {r['id']}",
                       f"{r['raw_date']} 落在已提供的节假日/校历特殊日",
                       "法定节假日不排课不考试；补课改期，"
                       "并核对该日是否为调休上班日（以本校校历为准）")
        wk = week_of(term, r["date"])
        weeks = term.get("weeks")
        if wk is not None and weeks:
            if wk < 1 or wk > int(weeks):
                issues.add("needs-review", "CHK-TERM", f"事件 {r['id']}",
                           f"{r['raw_date']} 换算为第 {wk} 周，超出学期周次 1-{weeks}",
                           "核对开学首日与校历；跨学期的课要单独说明")
            exam_weeks = term.get("exam_weeks") or []
            if exam_weeks and r["kind"] in ("上课", "调课", "补课") and wk in [int(x) for x in exam_weeks]:
                issues.add("needs-review", "CHK-EXAMWEEK", f"事件 {r['id']}",
                           f"第 {wk} 周属于考试周，但排了 {r['kind']}（{r['course']}）",
                           "考试周原则上停课；若确需补课，先确认教务是否允许在考试周补课")

    # 5) 同一班级同一天连考：考试之间的间隔不得小于本校规定
    min_gap = rules.get("min_exam_gap_min", 0)
    if min_gap:
        exams = [r for r in active if r["kind"] in ("考试", "补考", "缓考")]
        for i in range(len(exams)):
            for j in range(i + 1, len(exams)):
                a, b = exams[i], exams[j]
                if a["class"] and a["class"] == b["class"] and a["date"] == b["date"] \
                        and not overlap(a, b):
                    first, second = (a, b) if a["s"] < b["s"] else (b, a)
                    gap = second["s"] - first["e"]
                    if gap < min_gap:
                        issues.add("needs-review", "CHK-CLASS-GAP", f"班级 {a['class']}",
                                   f"{a['raw_date']} 同一班级连考两场，间隔仅 {gap} 分钟"
                                   f"（{first['id']} 至 {second['id']}），低于本校要求的 "
                                   f"{min_gap} 分钟",
                                   "调整其中一场的时间；连考间隔以本校考务规定为准，"
                                   "确认无误后再保留")

    # 6) 教室容量与登记状态
    reg = {}
    for r in rooms or []:
        name = (r.get("room") or "").strip()
        if name:
            reg[name] = r
    for r in active:
        if not r["room"]:
            continue
        info = reg.get(r["room"])
        if info is None:
            issues.add("needs-review", "CHK-ROOM-REG", f"事件 {r['id']}",
                       f"教室 {r['room']} 不在提供的教室资源清单里",
                       "确认教室编号写法（如「教三-201」与「3 号教学楼 201」），"
                       "或补登记该教室的容量与设备")
            continue
        cap = info.get("capacity")
        stu = r["students"]
        if isinstance(cap, int) and isinstance(stu, int) and stu > cap:
            issues.add("needs-review", "CHK-CAPACITY", f"事件 {r['id']}",
                       f"{r['class']} {stu} 人 > 教室 {r['room']} 容量 {cap} 人",
                       "换大教室，或按实际到课人数核实；超容不得作为最终安排上报")
        eq_need = r.get("equipment")
        if isinstance(eq_need, list) and eq_need:
            have = set(info.get("equipment") or [])
            lack = [x for x in eq_need if x not in have]
            if lack:
                issues.add("needs-review", "CHK-EQUIP", f"事件 {r['id']}",
                           f"教室 {r['room']} 缺所需设备：{'、'.join(lack)}",
                           "换教室或申请临时设备，并在排期表备注")
    return active


# ------------------------------------------------------------------ 监考核对
def check_invigilation(inv, active, issues: Issues, rules_top=None):
    if not inv:
        return None
    rules_top = rules_top or {}
    reqs = inv.get("requirements") or []
    teachers = {t.get("name"): t for t in (inv.get("teachers") or []) if t.get("name")}
    assigns = inv.get("assignments") or []
    rules = inv.get("rules") or {}
    avoid_own = rules.get("avoid_own_class", True)
    avoid_home = rules.get("avoid_homeroom", True)
    tol = rules.get("balance_tolerance", 1)

    req_by_id = {str(r.get("id")): r for r in reqs}
    norm_req = {}
    for i, r in enumerate(reqs, 1):
        rid = str(r.get("id") or f"I{i}")
        d = parse_date(r.get("date", ""))
        s, e = to_min(r.get("start", "")), to_min(r.get("end", ""))
        if d is None or s is None or e is None:
            issues.add("blocked", "INV-FIELD", f"监考需求 {rid}",
                       f"考试时间缺失或格式错误：date={r.get('date')!r} "
                       f"start={r.get('start')!r} end={r.get('end')!r}",
                       "补全考试时间后才能排监考")
            continue
        need = r.get("need")
        if not isinstance(need, int) or need < 1:
            issues.add("needs-review", "INV-NEED", f"监考需求 {rid}",
                       f"需监考人数未给定（need={need!r}）",
                       "向教务/开课学院确认每个考场的监考人数要求，"
                       "多数学校按考生人数分档（如 30 人以下 1 人、以上 2 人），"
                       "**以本校规定为准**")
            need = 0
        norm_req[rid] = {
            "id": rid, "course": (r.get("course") or "").strip(),
            "class": (r.get("class") or "").strip(),
            "room": (r.get("room") or "").strip(),
            "date": d, "s": s, "e": e,
            "raw_date": r.get("date", ""), "raw_start": r.get("start", ""),
            "raw_end": r.get("end", ""), "need": need,
        }

    # 教师名单与占用时段（含本人任课）
    busy = {}
    for r in active:
        if r["teacher"]:
            busy.setdefault(r["teacher"], []).append(r)

    picked = {}
    for a in assigns:
        rid = str(a.get("req_id") or a.get("rid") or "")
        who = (a.get("teacher") or "").strip()
        if rid not in norm_req:
            issues.add("blocked", "INV-ORPHAN", f"监考分配 {rid or '?'}",
                       f"分配指向不存在的监考需求：{rid!r}",
                       "核对需求编号；不得保留无法对应到考场的人员安排")
            continue
        if who not in teachers:
            issues.add("needs-review", "INV-UNKNOWN", f"监考需求 {rid}",
                       f"分配名单里的「{who}」不在教师名单中",
                       "确认姓名写法是否与人事/教务名单一致")
        picked.setdefault(rid, [])
        if who in picked[rid]:
            issues.add("blocked", "INV-DUP", f"监考需求 {rid}",
                       f"同一人被重复排进同一考场：{who}",
                       "删掉重复项，并核对是否有多余的行未清理")
            continue
        picked[rid].append(who)

        req = norm_req[rid]
        tinfo = teachers.get(who, {})
        # 不可用日期
        unavail = {parse_date(x) for x in (tinfo.get("unavailable") or [])}
        if req["date"] in unavail:
            issues.add("blocked", "INV-UNAVAIL", f"教师 {who}",
                       f"{req['raw_date']} 已登记不可用（请假/出差），仍被排了 {rid}",
                       "换人；确认请假已批准后从名单中剔除")
        # 与本人上课/其他监考时间冲突
        for b in busy.get(who, []):
            if overlap(req, b):
                issues.add("blocked", "INV-TEACH-BUSY", f"教师 {who}",
                           f"{req['raw_date']} {req['raw_start']}-{req['raw_end']} "
                           f"该时段本人在 {b['id']}（{b['course']}）有课",
                           "换人；**不得让教师同时上课与监考**")
        # 本人授课班级
        if avoid_own and req["class"] and req["class"] in (tinfo.get("teaches") or []):
            issues.add("needs-review", "INV-OWN-CLASS", f"教师 {who}",
                       f"被排到本人授课班级 {req['class']} 的 {req['course']} 监考",
                       "按本校规定处理：多数学校要求回避（任课教师不监考本班），"
                       "如本校无此规定请在此处注明「已核对本校规定，允许」")
        if avoid_home and req["class"] and req["class"] in (tinfo.get("homeroom") or []):
            issues.add("needs-review", "INV-HOMEROOM", f"教师 {who}",
                       f"被排到本人担任班主任的班级 {req['class']} 监考",
                       "确认本校是否要求班主任回避")

    # 同一时段一人两岗 + 上限
    # 同一时段一人两岗（同一需求内重复已在上方按 INV-DUP 报过）
    flat = []
    for rid, names in picked.items():
        for n in names:
            flat.append((rid, n))
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            (r1, n1), (r2, n2) = flat[i], flat[j]
            if r1 == r2 or n1 != n2:
                continue
            if overlap(norm_req[r1], norm_req[r2]):
                issues.add("blocked", "INV-CLASH", f"教师 {n1}",
                           f"{norm_req[r1]['raw_date']} "
                           f"{norm_req[r1]['raw_start']}-{norm_req[r1]['raw_end']} "
                           f"同一时段被排了两场监考：{r1} 与 {r2}",
                           "换人；一人同一时段只能一个考场")

    # 缺口：未提供 assignments 视为「还没排班」，不当作缺人报警
    planned = "assignments" in inv
    for rid, req in norm_req.items():
        got = len(picked.get(rid, []))
        if req["need"] and got < req["need"]:
            if not planned:
                issues.add("needs-review", "INV-TODO", f"监考需求 {rid}",
                           f"{req['course']} {req['raw_date']} {req['room']} "
                           f"需 {req['need']} 人，尚未排班",
                           "先跑 invigilation_plan.py 生成安排，再回来复检；"
                           "**排班不得由模型凭印象指派同事**")
            else:
                issues.add("blocked", "INV-GAP", f"监考需求 {rid}",
                           f"{req['course']} {req['raw_date']} {req['room']} "
                           f"需 {req['need']} 人，已排 {got} 人，缺 {req['need'] - got} 人",
                           "补排；**不要用凑数的人填坑**，宁可上报缺口由教务协调")

    # 均衡
    counts = {}
    for t in teachers:
        counts[t] = sum(1 for _, n in flat if n == t)

    # 单日监考场次上限（连监）
    max_daily = rules_top.get("max_daily_invigilation", 0)
    if max_daily:
        per_day = {}
        for rid, name in flat:
            per_day.setdefault((name, norm_req[rid]["raw_date"]), set()).add(rid)
        for (name, day), rids in sorted(per_day.items()):
            if len(rids) > max_daily:
                issues.add("needs-review", "INV-DAILY", f"教师 {name}",
                           f"{day} 一天被排了 {len(rids)} 场监考（{'、'.join(sorted(rids))}），"
                           f"超过本校上限 {max_daily} 场",
                           "调开其中一场；连续监考影响状态，"
                           "各校单日上限不同，以本校考务规定为准")

    for t, info in teachers.items():
        cap = info.get("max_slots")
        if isinstance(cap, int) and counts.get(t, 0) > cap:
            issues.add("needs-review", "INV-OVERLOAD", f"教师 {t}",
                       f"已排 {counts[t]} 场，超过本人上限 {cap} 场",
                       "与本人确认；孕期、临近退休、行政岗等常有减免，以本校规定为准")
    if counts:
        vals = [v for v in counts.values() if v]
        if len(vals) >= 2 and (max(vals) - min(vals)) > int(tol):
            most = max(counts, key=lambda k: counts[k])
            least = min(counts, key=lambda k: counts[k])
            issues.add("advisory", "INV-BALANCE", "监考均衡",
                       f"监考次数差 {max(vals) - min(vals)} 场，超过容差 {tol}"
                       f"（最多 {most} {counts[most]} 场，"
                       f"最少 {least} {counts[least]} 场）",
                       "按「次数最少优先」重排，或与教研室说明为何不均")

    return {"reqs": norm_req, "teachers": teachers, "picked": picked,
            "counts": counts, "rules": rules}


# ------------------------------------------------------------------ 出表
def cross_sheet(active, inv_out):
    rows = []
    for dim, key, label in (("人", "teacher", "教师"), ("班", "class", "班级"),
                            ("地", "room", "教室")):
        groups = {}
        for r in active:
            if r[key]:
                groups.setdefault(r[key], []).append(r)
        for name, recs in sorted(groups.items()):
            clash = 0
            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    if overlap(recs[i], recs[j]):
                        clash += 1
            rows.append([
                dim, f"{label}：{name}", len(recs), clash,
                "、".join(sorted({x["id"] for x in recs})),
                "✔ 无交叉" if clash == 0 else f"✘ {clash} 处交叉，见冲突清单",
            ])
    if inv_out:
        for name, cnt in sorted(inv_out["counts"].items()):
            tinfo = inv_out["teachers"].get(name, {})
            cap = tinfo.get("max_slots")
            rows.append([
                "监考", f"教师：{name}", cnt, "",
                "、".join(sorted(rid for rid, names in inv_out["picked"].items()
                                 if name in names)) or "—",
                ("✔ 在上限内" if not isinstance(cap, int) or cnt <= cap
                 else f"✘ 超过上限 {cap}"),
            ])
    return rows


def build_spec(recs, active, issues: Issues, inv_out, term) -> dict:
    sheets = []

    sheets.append({
        "name": "事件总表",
        "header": ["编号", "类型", "状态", "课程", "教师", "班级", "日期",
                   "起", "止", "教室", "人数", "原安排", "审批状态", "备注"],
        "rows": [[
            r["id"], r["kind"],
            "生效" if r["status"] == "active" else "已取消（留痕）",
            r["course"], r["teacher"] or "【待补：教师】",
            r["class"] or "【待补：班级】",
            r["raw_date"], r["raw_start"], r["raw_end"],
            r["room"] or "【待补：教室】",
            r["students"] if r["students"] is not None else "【待补：人数】",
            r["origin"] or "—",
            r["approval"] or "【待补：教务审批状态】",
            r["note"],
        ] for r in recs],
        "widths": [8, 8, 14, 16, 10, 12, 12, 7, 7, 12, 8, 22, 18, 14],
    })

    sheets.append({
        "name": "冲突清单",
        "header": ["级别", "规则ID", "位置", "问题", "建议动作"],
        "rows": [[LEVEL_CN[r["level"]], r["rule"], r["where"], r["msg"], r["action"]]
                 for r in issues.sorted_rows()] or
                [["—", "—", "—", "本次核对未发现冲突", "仍请人工复核节假日与校历后签字确认"]],
        "widths": [12, 16, 20, 52, 52],
    })

    sheets.append({
        "name": "人时地交叉核对",
        "header": ["维度", "对象", "涉及场次", "交叉数", "涉及编号", "结论"],
        "rows": cross_sheet(active, inv_out),
        "widths": [8, 22, 10, 10, 30, 30],
    })

    if inv_out:
        reqs, picked = inv_out["reqs"], inv_out["picked"]
        sheets.append({
            "name": "监考需求汇总",
            "header": ["需求编号", "考试科目", "班级", "日期", "起", "止",
                       "考场", "需监考人数", "已排人数", "缺口"],
            "rows": [[
                rid, r["course"] or "【待补：科目】", r["class"] or "【待补：班级】",
                r["raw_date"], r["raw_start"], r["raw_end"],
                r["room"] or "【待补：考场】", r["need"] or "【待补：人数】",
                len(picked.get(rid, [])),
                max(0, (r["need"] or 0) - len(picked.get(rid, []))) or "0",
            ] for rid, r in sorted(reqs.items())],
            "widths": [10, 18, 12, 12, 7, 7, 12, 12, 10, 8],
        })
        sheets.append({
            "name": "监考安排表",
            "header": ["序号", "考试科目", "日期", "起", "止", "考场",
                       "监考教师", "角色", "备注"],
            "rows": [
                [i, reqs[rid]["course"] or "【待补：科目】", reqs[rid]["raw_date"],
                 reqs[rid]["raw_start"], reqs[rid]["raw_end"],
                 reqs[rid]["room"] or "【待补：考场】", name, role,
                 "【待教师确认：已与本人协调】" if idx == 0 else ""]
                for i, (rid, name, role, idx) in enumerate(
                    [(rid, n, ("主监考" if k == 0 else "监考"), k)
                     for rid in sorted(reqs)
                     for k, n in enumerate(picked.get(rid, []))], 1)
            ],
            "widths": [6, 18, 12, 7, 7, 12, 12, 10, 24],
        })
        sheets.append({
            "name": "监考均衡统计",
            "header": ["教师", "已排场次", "上限", "任课班级", "不可用日期", "结论"],
            "rows": [[
                t, inv_out["counts"].get(t, 0),
                inv_out["teachers"].get(t, {}).get("max_slots", "—"),
                "、".join(inv_out["teachers"].get(t, {}).get("teaches") or []) or "—",
                "、".join(inv_out["teachers"].get(t, {}).get("unavailable") or []) or "—",
                "✔ 均衡" if inv_out["counts"].get(t, 0) else "⚠ 本次未安排",
            ] for t in sorted(inv_out["teachers"])],
            "widths": [12, 10, 8, 24, 24, 14],
        })

    term_rows = [
        ["学期", term.get("name") or "【待补：学期】"],
        ["开学首日", term.get("start") or "【待补：开学首日】"],
        ["学期周次", term.get("weeks") or "【待补：学期总周次】"],
        ["考试周", "、".join(str(x) for x in (term.get("exam_weeks") or [])) or "【待补：考试周】"],
        ["阻断项", issues.count("blocked")],
        ["需人工复核", issues.count("needs-review")],
        ["提示项", issues.count("advisory")],
        ["总体判定", "存在阻断，不得执行/上报，先解决冲突清单里的阻断项"
                     if issues.count("blocked") else
                     "无阻断；需人工复核项请逐条确认后再送教务审批"],
        ["免责说明", "本表依据教师/教务提供的课表、教室、名单数据生成；"
                     "各校教务规定不同，最终以本校教务文件与教务审核结论为准"],
    ]
    sheets.append({
        "name": "核对结论",
        "header": ["项目", "内容"],
        "rows": term_rows,
        "widths": [14, 60],
    })
    return {"sheets": sheets}


def build_report(recs, active, issues: Issues, inv_out, term, data_path) -> str:
    L = []
    L.append("# 排期冲突核对报告\n")
    L.append(f"> 数据来源：`{data_path}`；学期：{term.get('name') or '【待补：学期】'}；"
             f"开学首日：{term.get('start') or '【待补：开学首日】'}。\n")
    L.append("> 结论由脚本按固定规则算出，可复核；**冲突一律显式列出，不做静默通过**。\n")

    n_b, n_r, n_a = (issues.count("blocked"), issues.count("needs-review"),
                     issues.count("advisory"))
    L.append("\n## 一、总结论\n")
    if n_b:
        L.append(f"**存在 {n_b} 项阻断问题** —— 在解决之前，本排期不得执行、"
                 f"不得通知学生、不得上报教务。\n")
    else:
        L.append("**无阻断问题** —— 但仍需教师逐条确认「需人工复核」项，"
                 "并经教务审批后方可执行。\n")
    L.append(f"\n统计：阻断 {n_b} · 需人工复核 {n_r} · 提示 {n_a}；"
             f"参与核对的有效场次 {len(active)}。\n")

    L.append("\n## 二、冲突清单\n")
    L.append("| 级别 | 规则 | 位置 | 问题 | 建议动作 |\n|---|---|---|---|---|\n")
    for r in issues.sorted_rows():
        L.append(f"| {LEVEL_CN[r['level']]} | {r['rule']} | {r['where']} | "
                 f"{r['msg']} | {r['action']} |\n")

    L.append("\n## 三、人 × 时间 × 空间交叉核对\n")
    L.append("| 维度 | 对象 | 场次 | 交叉数 | 结论 |\n|---|---|---|---|---|\n")
    for row in cross_sheet(active, inv_out):
        L.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[5]} |\n")

    if inv_out:
        L.append("\n## 四、监考\n")
        L.append("| 需求 | 科目 | 日期 | 时段 | 考场 | 需 | 已排 | 缺口 |\n"
                 "|---|---|---|---|---|---|---|---|\n")
        for rid, r in sorted(inv_out["reqs"].items()):
            got = len(inv_out["picked"].get(rid, []))
            L.append(f"| {rid} | {r['course']} | {r['raw_date']} | "
                     f"{r['raw_start']}-{r['raw_end']} | {r['room']} | {r['need']} | "
                     f"{got} | {max(0, (r['need'] or 0) - got)} |\n")
        L.append("\n### 教师监考场次\n")
        for t in sorted(inv_out["teachers"]):
            L.append(f"- {t}：{inv_out['counts'].get(t, 0)} 场\n")

    L.append("\n## 五、必须由人做的事（本脚本不做）\n")
    L.append("1. 调课/停课/补课**必须报教务审批**；本报告只是送审材料。\n")
    L.append("2. 监考安排涉及同事，须**事先与本人协调**，不得擅自指派。\n")
    L.append("3. 节假日、校历、考试周、教室容量与设备、监考人数定额"
             "**以本校教务文件为准**，本报告只做交叉核对，不替代教务审核。\n")
    L.append("4. 学生名单等个人信息只在本机处理，交付后请删除过程文件。\n")
    return "".join(L)


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(prog="conflict_check",
                                 description="teaching-ops 排期冲突检测（人×时间×空间）")
    ap.add_argument("--in", dest="src", required=True, help="排期数据 JSON")
    ap.add_argument("--spec", help="输出 xlsx_kit 规格 JSON")
    ap.add_argument("--report", help="输出 Markdown 报告")
    args = ap.parse_args()

    try:
        with open(args.src, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return die(f"找不到输入文件：{args.src}")
    except json.JSONDecodeError as e:
        return die(f"输入不是合法 JSON：{args.src}\n{e}")

    term = data.get("term") or {}
    rules = data.get("rules") or {}
    issues = Issues()
    recs = normalize(data.get("events"), issues)
    active = check_occupancy(recs, term, data.get("holidays"), data.get("rooms"),
                             issues, rules)
    inv_out = check_invigilation(data.get("invigilation"), active, issues, rules)

    if len(recs) == 0 and not inv_out:
        issues.add("needs-review", "CHK-EMPTY", "输入数据",
                   "events 与 invigilation 均为空，没有可核对的内容",
                   "先按 intake 清单收集真实课表/教室/名单；"
                   "**本工具不会替教师编造任何一条排期**")

    if args.spec:
        with open(args.spec, "w", encoding="utf-8") as f:
            json.dump(build_spec(recs, active, issues, inv_out, term), f,
                      ensure_ascii=False, indent=2)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(build_report(recs, active, issues, inv_out, term, args.src))

    summary = {
        "输入": args.src,
        "有效场次": len(active),
        "阻断": issues.count("blocked"),
        "需人工复核": issues.count("needs-review"),
        "提示": issues.count("advisory"),
        "spec": args.spec, "报告": args.report,
        "总体判定": "存在阻断，不得执行/上报" if issues.count("blocked")
                    else "无阻断，请人工复核后送教务审批",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if issues.count("blocked") else 0


if __name__ == "__main__":
    sys.exit(main())
