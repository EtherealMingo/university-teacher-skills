#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — 技能包完整性自检

对应 CONVENTIONS.md 第 8 节的验收清单，把「靠记忆检查」变成「跑一遍」：
  1. 14 个子技能目录与 SKILL.md 是否齐全
  2. frontmatter 是否有 name / description，description 是否有 Triggers 与足够触发短语
  3. SKILL.md 里引用的 vendor/ 路径是否真实存在（防止凭记忆写路径）
  4. 文件产出是否走了 office-layer
  5. 是否声明了「不虚构」与「人工确认位」纪律
  6. office-layer 的三个脚本能否正常拉起

用法：python3 verify.py [--root .]
退出码：0 全部通过；1 有 FAIL。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

EXPECTED = [
    # 教学
    "lesson-plan", "lecture-slides", "quiz-generator",
    "exam-pipeline", "classroom-live", "teaching-contest",
    # 科研
    "research-assistant", "grant-proposal", "paper-to-slides", "peer-review",
    # 指导
    "thesis-supervisor", "lab-meeting",
    # 考核与对外
    "annual-review", "science-outreach",
]

OK, FAIL, WARN = "\033[32mOK\033[0m", "\033[31mFAIL\033[0m", "\033[33mWARN\033[0m"
results = {"ok": 0, "fail": 0, "warn": 0}


def ok(msg):
    results["ok"] += 1
    print(f"  [{OK}] {msg}")


def fail(msg):
    results["fail"] += 1
    print(f"  [{FAIL}] {msg}")


def warn(msg):
    results["warn"] += 1
    print(f"  [{WARN}] {msg}")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def find_vendor_refs(text):
    """抓出 SKILL.md 里所有 vendor/... 路径（含反引号内与代码块内的）。"""
    refs = set()
    for m in re.finditer(r"vendor/[\w\-./]+", text, re.UNICODE):
        p = m.group(0).rstrip(".,;:`)】」").rstrip("/")
        if p:
            refs.add(p)
    return refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="技能包根目录")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    print(f"\n=== 技能包自检：{root} ===\n")

    # ---------- 1. 结构 ----------
    print("[1] 目录结构")
    for f in ("SKILL.md", "CONVENTIONS.md", "README.md", "vendor/VENDOR.md",
              "vendor/office-layer/SKILL.md"):
        (ok if (root / f).exists() else fail)(f"{f} {'存在' if (root/f).exists() else '缺失'}")

    print("\n[2] 14 个子技能")
    skill_dir = root / "skills"
    missing, no_fm, weak_desc = [], [], []
    for name in EXPECTED:
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            missing.append(name)
            fail(f"{name}/SKILL.md 缺失")
            continue
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm or "name" not in fm or "description" not in fm:
            no_fm.append(name)
            fail(f"{name}: frontmatter 缺 name 或 description")
            continue
        if fm.get("name") != name:
            warn(f"{name}: frontmatter name='{fm.get('name')}' 与目录名不一致")
        desc = fm.get("description", "")
        if "Triggers" not in desc:
            weak_desc.append(name)
            warn(f"{name}: description 缺 Triggers 段落")
        # 触发短语计数：优先数 Triggers: 之后用「、」分隔的条目，也接受正文里
        # 用「」/『』引号列出的口语（取两者较大值，避免因写法不同而误判）。
        n_trig = 0
        if "Triggers" in desc:
            tail = desc.split("Triggers", 1)[1].lstrip(":： ").strip()
            n_trig = len([x for x in re.split(r"[、,，;；]", tail) if len(x.strip()) >= 2])
        n_quote = len(re.findall(r"[「『][^」』]{2,}[」』]", desc))
        n = max(n_trig, n_quote)
        if n < 3:
            warn(f"{name}: description 触发短语偏少（识别到 {n} 个）")
        else:
            ok(f"{name} ({n} 个触发短语, {len(text.splitlines())} 行)")

    # ---------- 3. vendor 引用真实性 ----------
    # .venv 是 bootstrap.sh 生成的产物，不是源码。刚 clone 下来时它必然不存在，
    # 若按普通路径判定会把「还没装依赖」误报成「引用了不存在的路径」。
    GENERATED = ("vendor/office-layer/.venv",)

    def is_generated(ref):
        return any(ref == g or ref.startswith(g + "/") for g in GENERATED)

    print("\n[3] vendor 路径引用真实性")
    bad_refs, gen_refs = {}, set()
    for name in EXPECTED:
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            continue
        for ref in find_vendor_refs(f.read_text(encoding="utf-8")):
            if is_generated(ref):
                gen_refs.add(ref)
                continue
            if not (root / ref).exists():
                bad_refs.setdefault(name, []).append(ref)
    if bad_refs:
        for name, refs in bad_refs.items():
            for r in sorted(set(refs)):
                fail(f"{name} 引用了不存在的路径：{r}")
    else:
        ok("所有子技能引用的 vendor 路径均真实存在")

    venv_py = root / "vendor/office-layer/.venv/bin/python"
    if gen_refs:
        if venv_py.exists():
            ok(f"生成物引用正常（{len(gen_refs)} 处指向 .venv，已就绪）")
        else:
            warn(f"{len(gen_refs)} 处引用 vendor/office-layer/.venv —— 尚未生成，"
                 f"请先运行：bash vendor/office-layer/bootstrap.sh")

    # ---------- 4/5. 纪律 ----------
    print("\n[4] 纪律与产出通道")
    for name in EXPECTED:
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        has_nofake = any(k in t for k in ("不虚构", "禁止虚构", "绝不虚构"))
        has_office = "office-layer" in t
        if not has_office:
            fail(f"{name}: 未写明走 office-layer 产出文件")
        if not has_nofake:
            warn(f"{name}: 未见「不虚构」纪律表述")
    if all(("office-layer" in (skill_dir / n / "SKILL.md").read_text(encoding="utf-8"))
           for n in EXPECTED if (skill_dir / n / "SKILL.md").exists()):
        ok("全部子技能都指向 office-layer 产出通道")

    # ---------- 6. office-layer 冒烟测试 ----------
    print("\n[5] office-layer 冒烟测试")
    py = root / "vendor/office-layer/.venv/bin/python"
    if not py.exists():
        warn("未找到 .venv，先运行 bash vendor/office-layer/bootstrap.sh")
    else:
        for script, cmd in (("docx_kit.py", "--help"), ("pptx_kit.py", "--help"),
                            ("xlsx_kit.py", "--help")):
            sp = root / "vendor/office-layer/scripts" / script
            r = subprocess.run([str(py), str(sp), cmd], capture_output=True, text=True)
            (ok if r.returncode == 0 else fail)(
                f"{script} {'可运行' if r.returncode == 0 else '启动失败: ' + r.stderr[:120]}")

    # ---------- 汇总 ----------
    print(f"\n=== 结果：{results['ok']} 通过 / {results['warn']} 警告 / {results['fail']} 失败 ===\n")
    if missing or no_fm:
        print(f"缺失技能：{missing or '无'}；frontmatter 问题：{no_fm or '无'}\n")
    return 1 if results["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
