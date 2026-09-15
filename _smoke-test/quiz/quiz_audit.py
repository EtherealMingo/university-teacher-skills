#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quiz_audit.py — 出题质量门自检（仅标准库）
用法: python3 quiz_audit.py 题库.json [识记:20,理解:30,应用:30,分析:20] [知识点清单.txt]
"""
import json, re, sys, collections

def norm(s):
    return re.sub(r"[\s，。、；：？！,.;:?!（）()【】\[\]「」\"'']+", "", str(s or ""))

def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python3 quiz_audit.py 题库.json [识记:20,理解:30,...] [知识点清单.txt]")
    qs = json.load(open(sys.argv[1], encoding="utf-8"))["questions"]
    target = {}
    if len(sys.argv) > 2 and sys.argv[2].strip():
        for kv in sys.argv[2].split(","):
            if ":" in kv:
                k, v = kv.split(":", 1)
                target[k.strip()] = float(v)
    n = len(qs)
    if not n:
        sys.exit("题库为空")
    print(f"题量 {n} 题｜总分 {sum(float(q.get('score') or 0) for q in qs):g} 分")

    for field, label in (("type", "题型"), ("bloom", "认知层次"), ("answer", "答案位置"), ("kp", "知识点")):
        cnt = collections.Counter(str(q.get(field) or "(空)") for q in qs)
        print(f"\n[{label}] {len(cnt)} 类")
        for k, v in cnt.most_common():
            pct = v * 100.0 / n
            line = f"  {k}: {v} 题 ({pct:.0f}%)"
            if field == "bloom" and k in target:
                d = pct - target[k]
                line += f"｜目标 {target[k]:.0f}%｜偏差 {d:+.0f}pp {'OK' if abs(d) <= 5 else '<<超差'}"
            print(line)

    seen, seen12, flagged = {}, {}, []
    for q in qs:
        stem = norm(q.get("stem"))
        if not stem:
            flagged.append((q.get("id"), "题干为空"))
            continue
        if stem in seen:
            flagged.append((q.get("id"), f"题干与 {seen[stem]} 完全重复"))
        else:
            seen[stem] = q.get("id")
        p12 = stem[:12]
        if p12 in seen12:
            flagged.append((q.get("id"), f"题干前 12 字与 {seen12[p12]} 雷同"))
        else:
            seen12[p12] = q.get("id")

    for q in qs:
        opts, ans = q.get("options") or {}, q.get("answer")
        if not isinstance(opts, dict) or ans not in opts or len(opts) < 3:
            continue
        lens = {k: len(str(v)) for k, v in opts.items()}
        others = [v for k, v in lens.items() if k != ans]
        avg = sum(others) / len(others)
        if avg > 0 and lens[ans] > avg * 1.4:
            flagged.append((q.get("id"),
                f"正确项长度 {lens[ans]} 字，为干扰项均值 {avg:.1f} 的 {lens[ans]/avg:.1f} 倍，答案可能被长度泄露"))
        if any("以上都对" in str(v) or "以上都不对" in str(v) for v in opts.values()):
            flagged.append((q.get("id"), "使用了「以上都对/都不对」凑数选项"))

    if len(sys.argv) > 3:
        plan = [l.strip() for l in open(sys.argv[3], encoding="utf-8") if l.strip() and not l.startswith("#")]
        tested = {norm(q.get("kp")) for q in qs}
        miss = [p for p in plan if norm(p) not in tested]
        cov = (len(plan) - len(miss)) * 100.0 / len(plan)
        print(f"\n[知识点覆盖] 计划 {len(plan)} 个｜已覆盖 {len(plan)-len(miss)} 个｜覆盖率 {cov:.0f}%")
        for m in miss:
            print(f"  未覆盖: {m}")

    print(f"\n[问题清单] {len(flagged)} 条")
    for qid, msg in flagged:
        print(f"  {qid}: {msg}")
    print("\n结论: " + ("通过（0 条问题）" if not flagged else "未通过，逐条修正后重跑"))

main()
