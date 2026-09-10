#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成果条目去重合并 → 生成 xlsx_kit 可用的 spec.json
用法: python dedup_merge.py --in raw.json --out spec.json [--year 2024]
raw.json: {"items":[{type,name,role,date,source,code,level,index,evidence,student}, ...]}
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata
from pathlib import Path

SHEET = "科研成果"
RULES = [
    (("教改项目", "教研项目", "教学研究论文", "教改论文", "教学成果奖", "一流课程",
      "课程建设", "教材建设", "教学竞赛", "专业建设", "实验教学", "教改"), "教学研究"),
    (("指导学生获奖", "指导竞赛", "学科竞赛", "大创指导", "创新创业训练", "班主任",
      "学业导师", "研究生指导", "学位论文指导", "指导学生"), "人才培养"),
    (("横向课题", "技术服务", "技术咨询", "成果转化", "社会培训", "学会任职",
      "评审专家", "科普讲座", "社会兼职", "对口支援"), "社会服务"),
    (("荣誉表彰", "人才称号", "先进个人", "优秀教师", "师德标兵", "荣誉"), "荣誉表彰"),
    (("继续教育", "进修", "访学", "培训学时", "企业实践"), "继续教育"),
    (("期刊论文", "会议论文", "论文", "著作", "专著", "译著", "教材", "发明专利",
      "实用新型", "软件著作权", "软著", "专利", "标准", "科研项目", "纵向项目",
      "研究报告"), "科研成果"),
]
# 长键优先，避免「教材建设」被「教材」抢先命中
FLAT = sorted(((k, s) for keys, s in RULES for k in keys), key=lambda kv: -len(kv[0]))
LBL = {
    "科研成果": (("date", "时间"), ("source", "刊物/来源"), ("code", "编号/收录号"),
                 ("level", "级别"), ("evidence", "支撑材料")),
    "教学研究": (("date", "时间"), ("source", "来源单位"), ("code", "项目编号"),
                 ("level", "级别"), ("evidence", "支撑材料")),
    "人才培养": (("date", "时间"), ("source", "竞赛/奖项来源"), ("level", "获奖等级"),
                 ("student", "学生姓名"), ("evidence", "支撑材料")),
    "社会服务": (("date", "时间"), ("source", "委托单位"), ("level", "工作量/到账金额"),
                 ("evidence", "证明材料")),
    "荣誉表彰": (("date", "时间"), ("source", "授予单位"), ("level", "级别"),
                 ("evidence", "证明材料")),
    "继续教育": (("date", "时间"), ("source", "主办单位"), ("level", "学时/学分"),
                 ("evidence", "证明材料")),
}
HEADERS = {
    "科研成果": ["序号", "成果名称", "成果形式", "本人排名", "时间", "刊物/项目来源",
                 "编号/收录号", "级别", "支撑材料", "待核实"],
    "教学研究": ["序号", "项目/成果名称", "类别", "项目编号", "时间", "级别",
                 "本人角色", "支撑材料", "待核实"],
    "人才培养": ["序号", "学生姓名", "获奖/竞赛名称", "等级", "时间", "本人角色",
                 "支撑材料", "待核实"],
    "社会服务": ["序号", "事项", "类型", "时间", "成效/工作量", "证明材料", "待核实"],
    "荣誉表彰": ["序号", "荣誉名称", "授予单位", "时间", "级别", "证明材料", "待核实"],
    "继续教育": ["序号", "项目", "形式", "时间", "学时/学分", "证明材料", "待核实"],
}
CORE = ("role", "date", "source", "code", "level", "index", "evidence", "student")
CN_FIELD = {"role": "本人排名", "date": "时间", "source": "来源", "code": "编号",
            "level": "级别/等级", "index": "收录号", "evidence": "支撑材料", "student": "学生姓名"}
PUNCT = re.compile(r"[\s\u3000\-—_·、,，.。:：;；()（）《》\[\]【】\"'“”‘’/\\|]+")


def route(t: str) -> str:
    tt = PUNCT.sub("", t or "")
    for k, sheet in FLAT:
        if k and (k in tt):
            return sheet
    return "科研成果"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return PUNCT.sub("", s)


def year(s: str) -> str:
    m = re.search(r"(19|20)\d{2}", str(s or ""))
    return m.group(0) if m else ""


def keys_for(it: dict) -> list:
    """返回该条目的**候选匹配键**（按优先级）。

    同一条成果在不同材料里写法常不一致：成果登记表带收录号，学院汇总表不带；
    简历里写「期刊论文」，系统导出写「论文」。若只认单一键（尤其「有编号就只按
    编号匹配」），这两条永远合不到一起——而隔年重复填报正是本脚本要治的病。
    因此同时登记「编号键」与「名称键」，任一命中即视为同一条。
    """
    sheet = route(it["type"])
    ks = []
    if it.get("code"):
        ks.append(("code", norm(it["code"])))
    if sheet == "人才培养":
        ks.append(("stu", norm(it.get("student", "")) + "|" + norm(it["name"]),
                   year(it.get("date"))))
    elif sheet in ("荣誉表彰", "继续教育"):
        ks.append(("honor", norm(it["name"]), norm(it.get("level", "")), year(it.get("date"))))
    else:
        ks.append(("name", norm(it["name"]), year(it.get("date"))))
    return ks


def key(it: dict) -> tuple:
    """保留旧接口：返回主键（候选键中优先级最高者）。"""
    return keys_for(it)[0]



def merge(a: dict, b: dict) -> tuple:
    """返回 (合并条目, 冲突列表)"""
    out, conflicts = dict(a), []
    for k, v in b.items():
        if k == "type":
            continue
        old = out.get(k)
        if not old and v:
            out[k] = v
        elif old and v and norm(str(old)) != norm(str(v)) and k in CORE:
            conflicts.append(f"{CN_FIELD.get(k, k)}：「{old}」 vs 「{v}」")
    return out, conflicts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--year")
    a = ap.parse_args()
    raw = json.loads(Path(a.src).read_text(encoding="utf-8"))
    items = raw.get("items", raw if isinstance(raw, list) else [])

    order, store, cf_map, dup_log, canon = [], {}, {}, [], {}
    for it in items:
        it = {k: ("" if v is None else str(v).strip()) for k, v in it.items()}
        if a.year and year(it.get("date")) and year(it["date"]) != a.year:
            it["_out_of_year"] = "1"          # 非本考核年度：单独标注，不静默丢弃
        ks = keys_for(it)
        # 任一候选键命中即视为同一条。命中后把其余候选键也登记为别名，
        # 这样「先录无编号、后录有编号」与相反的录入顺序都能正确合并。
        hit = next((k for k in ks if k in store), None)
        if hit is not None:
            ck = canon.get(hit, hit)          # 别名的规范键
            srcs = store[ck].setdefault("_sources", [])
            srcs.append(it.get("_source", "?"))
            store[ck], cf = merge(store[ck], it)
            cf_map[ck].extend(cf)
            for k in ks:
                store.setdefault(k, store[ck])
                canon.setdefault(k, ck)
            dup_log.append({"key": list(ck), "名称": it.get("name"), "合并来源": srcs})
        else:
            ck = ks[0]
            store[ck] = it
            cf_map[ck] = []
            store[ck]["_sources"] = [it.get("_source", "?")]
            for k in ks:
                canon.setdefault(k, ck)
                store.setdefault(k, store[ck])
            order.append(ck)

    sheets, pending, seq = {}, [], {}
    for k in order:
        it = store[k]
        sheet = route(it["type"])
        n = seq[sheet] = seq.get(sheet, 0) + 1
        miss = []
        for f, label in LBL[sheet]:
            if not it.get(f):
                miss.append(label)
        if cf_map[k]:
            miss.append("字段冲突：" + "；".join(cf_map[k]))
        if it.get("_out_of_year"):
            miss.append(f"时间不在{a.year}年度内，请确认是否计入本期")
        mark = "是" if miss else ""
        if miss:
            pending.append([len(pending) + 1, sheet, it["name"], "、".join(miss),
                            it.get("evidence") or "【待补：支撑材料】"])
        if sheet == "科研成果":
            row = [n, it["name"], it["type"], it.get("role") or "【待补：本人排名】",
                   it.get("date") or "【待补：时间】", it.get("source") or "【待补：来源】",
                   it.get("code") or "【待补：编号/收录号】", it.get("level") or "【待补：级别】",
                   it.get("evidence") or "【待补：支撑材料】", mark]
        elif sheet == "教学研究":
            row = [n, it["name"], it["type"], it.get("code") or "【待补：项目编号】",
                   it.get("date") or "【待补：时间】", it.get("level") or "【待补：级别】",
                   it.get("role") or "【待补：本人角色】",
                   it.get("evidence") or "【待补：支撑材料】", mark]
        elif sheet == "人才培养":
            row = [n, it.get("student") or "【待补：学生姓名（含个人信息，请教师本人填写）】",
                   it["name"], it.get("level") or "【待补：获奖等级】",
                   it.get("date") or "【待补：时间】",
                   it.get("role") or "【待补：本人角色】",
                   it.get("evidence") or "【待补：支撑材料】", mark]
        elif sheet == "社会服务":
            row = [n, it["name"], it["type"], it.get("date") or "【待补：时间】",
                   it.get("level") or "【待补：工作量/到账金额】",
                   it.get("evidence") or "【待补：证明材料】", mark]
        elif sheet == "荣誉表彰":
            row = [n, it["name"], it.get("source") or "【待补：授予单位】",
                   it.get("date") or "【待补：时间】", it.get("level") or "【待补：级别】",
                   it.get("evidence") or "【待补：证明材料】", mark]
        else:
            row = [n, it["name"], it.get("type"), it.get("date") or "【待补：时间】",
                   it.get("level") or "【待补：学时/学分】",
                   it.get("evidence") or "【待补：证明材料】", mark]
        sheets.setdefault(sheet, []).append(row)

    spec_sheets = [{"name": s, "header": HEADERS[s], "rows": rows, "freeze": True}
                   for s, rows in sheets.items()]
    spec_sheets.append({"name": "待核实清单",
                        "header": ["序号", "所属栏目", "成果/事项", "缺口", "需要教师提供"],
                        "rows": pending or [["", "", "", "无", "无"]], "freeze": True})
    Path(a.out).write_text(json.dumps({"sheets": spec_sheets}, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    print(json.dumps({"条目总数": len(items), "合并后": len(order),
                      "重复合并": len(dup_log), "待核实": len(pending),
                      "分栏": {s: len(r) for s, r in sheets.items()},
                      "duplicates": dup_log}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
