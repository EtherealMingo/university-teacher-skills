#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — 技能包完整性自检

对应 CONVENTIONS.md 第 8 节的验收清单，把「靠记忆检查」变成「跑一遍」：
  1. 22 个主技能 + 26 个底座技能的目录与 SKILL.md 是否齐全
  2. frontmatter 是否有 name / description，description 是否有 Triggers 与足够触发短语
  3. SKILL.md 里引用的 skills/ 底座路径是否真实存在（防止凭记忆写路径）
  4. 文件产出是否走了 office-layer（主技能）
  5. 是否声明了「不虚构」与「人工确认位」纪律（主技能）
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

# 22 个面向教师场景的主技能（总控路由的对象）
EXPECTED_MAIN = [
    # 教学
    "lesson-plan", "lecture-slides", "quiz-generator",
    "exam-pipeline", "classroom-live", "teaching-contest",
    # 科研
    "research-assistant", "grant-proposal", "paper-to-slides", "peer-review",
    # 指导（含学生工作）
    "thesis-supervisor", "lab-meeting", "student-competition",
    "student-affairs", "internship-practice",
    # 行政事务
    "admin-reporting", "meeting-notices", "teaching-ops",
    "academic-correspondence", "student-recommendation",
    # 考核与对外
    "annual-review", "science-outreach",
]

# 26 个底座技能（自 vendor/ 迁入并中文化；2026-09-10 起按上游套件嵌套为 5 个目录，
# 4 个独立件保持平铺）。相对 skills/ 的路径。
EXPECTED_FOUNDATION = [
    # 自建文件产出层
    "office-layer",
    # 申报书写作引擎
    "awesome-benzi",
    # 论文拆解与课件视觉
    "paper-analyst", "slides-polish",
    # 实证研究（empirical-research）
    "empirical-research/econ-audit", "empirical-research/data-dictionary",
    "empirical-research/lit-review",
    # 智能教材工具链（ibook-skills）
    "ibook-skills/question-writing", "ibook-skills/learning-graph-generator",
    "ibook-skills/glossary-generator",
    "ibook-skills/faq-generator", "ibook-skills/course-description-analyzer",
    # K-12 教学法（Anthropic，k12-teacher-skills）
    "k12-teacher-skills/k12-lesson-plan-creation",
    "k12-teacher-skills/k12-lesson-differentiation",
    "k12-teacher-skills/k12-lesson-prep",
    "k12-teacher-skills/k12-check-for-understanding",
    # 教育方法库（education-skills，台湾课纲，已译简体）
    "education-skills/edu-teaching-design", "education-skills/edu-learning-analytics",
    "education-skills/edu-rural-education",
    "education-skills/edu-research-methods", "education-skills/edu-math-tech-education",
    "education-skills/edu-ai-tools", "education-skills/edu-ict-integration",
    # 学习方法（learning-education）
    "learning-education/study-skill", "learning-education/thinking-toolkit",
    "learning-education/learning-paths",
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


def find_skill_refs(text):
    """抓出 SKILL.md 里所有 skills/... 路径（含反引号内与代码块内的）。"""
    refs = set()
    # 排除 URL（github.com/.../skills/tree/...）与 $BK_HOME/skills/... 这类上游生态路径：
    # 仅匹配前面不是 字母/数字/._/- 的 skills/ 前缀
    for m in re.finditer(r"(?<![\w./\-])skills/[\w\-./]+", text, re.UNICODE):
        p = m.group(0).rstrip(".,;:`)】」").rstrip("/")
        if p and ".." not in p:
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
    for f in ("SKILL.md", "CONVENTIONS.md", "README.md", "THIRD_PARTY_NOTICES.md",
              "skills/office-layer/SKILL.md"):
        (ok if (root / f).exists() else fail)(f"{f} {'存在' if (root/f).exists() else '缺失'}")

    skill_dir = root / "skills"

    def check_skill(name, discipline):
        # name 是相对 skills/ 的路径（底座可能在套件子目录里，
        # 如 "ibook-skills/question-writing"）；frontmatter 的 name 与目录本名比较
        base = name.split("/")[-1]
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            fail(f"{name}/SKILL.md 缺失")
            return False
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm or "name" not in fm or "description" not in fm:
            fail(f"{name}: frontmatter 缺 name 或 description")
            return False
        if fm.get("name") != base:
            warn(f"{name}: frontmatter name='{fm.get('name')}' 与目录名不一致")
        desc = fm.get("description", "")
        if "Triggers" not in desc:
            warn(f"{name}: description 缺 Triggers 段落")
        # 触发短语计数：优先数 Triggers: 之后用「、」分隔的条目，也接受正文里
        # 用「」/『』/“”引号列出的口语（取两者较大值，避免因写法不同而误判）。
        n_trig = 0
        if "Triggers" in desc:
            tail = desc.split("Triggers", 1)[1].lstrip(":： ").strip()
            n_trig = len([x for x in re.split(r"[、,，;；。]", tail) if len(x.strip()) >= 2])
        n_quote = len(re.findall(r"[「『“][^」』”]{2,}[」』”]", desc))
        n = max(n_trig, n_quote)
        if n < 3:
            warn(f"{name}: description 触发短语偏少（识别到 {n} 个）")
        else:
            ok(f"{name} ({n} 个触发短语, {len(text.splitlines())} 行)")
        if discipline:
            # 接受同义表述：有的技能写「不虚构」，有的写「绝不编造」「不得捏造」，语义等价
            has_nofake = any(k in text for k in (
                "不虚构", "禁止虚构", "绝不虚构", "不得虚构",
                "编造", "捏造", "伪造", "杜撰"))
            if "office-layer" not in text:
                fail(f"{name}: 未写明走 office-layer 产出文件")
            if not has_nofake:
                warn(f"{name}: 未见「不虚构 / 不编造」纪律表述")
        return True

    print("\n[2] 22 个主技能")
    for name in EXPECTED_MAIN:
        check_skill(name, discipline=True)

    print("\n[3] 26 个底座技能")
    for name in EXPECTED_FOUNDATION:
        check_skill(name, discipline=False)

    # ---------- 4. 底座路径引用真实性 ----------
    # .venv 是 bootstrap.sh 生成的产物，不是源码。刚 clone 下来时它必然不存在，
    # 若按普通路径判定会把「还没装依赖」误报成「引用了不存在的路径」。
    GENERATED = ("skills/office-layer/.venv",)

    def is_generated(ref):
        return any(ref == g or ref.startswith(g + "/") for g in GENERATED)

    print("\n[4] 底座路径（skills/）引用真实性")
    bad_refs, gen_refs = {}, set()
    for name in EXPECTED_MAIN + EXPECTED_FOUNDATION:
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            continue
        for ref in find_skill_refs(f.read_text(encoding="utf-8")):
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
        ok("所有技能引用的 skills/ 底座路径均真实存在")

    venv_py = root / "skills/office-layer/.venv/bin/python"
    if gen_refs:
        if venv_py.exists():
            ok(f"生成物引用正常（{len(gen_refs)} 处指向 .venv，已就绪）")
        else:
            warn(f"{len(gen_refs)} 处引用 skills/office-layer/.venv —— 尚未生成，"
                 f"请先运行：bash skills/office-layer/bootstrap.sh")

    # ---------- 5. office-layer 冒烟测试 ----------
    print("\n[5] office-layer 冒烟测试")
    if not venv_py.exists():
        warn("未找到 .venv，先运行 bash skills/office-layer/bootstrap.sh")
    else:
        for script in ("docx_kit.py", "pptx_kit.py", "xlsx_kit.py"):
            sp = root / "skills/office-layer/scripts" / script
            r = subprocess.run([str(venv_py), str(sp), "--help"],
                               capture_output=True, text=True)
            (ok if r.returncode == 0 else fail)(
                f"{script} {'可运行' if r.returncode == 0 else '启动失败: ' + r.stderr[:120]}")

    # ---------- 汇总 ----------
    print(f"\n=== 结果：{results['ok']} 通过 / {results['warn']} 警告 / {results['fail']} 失败 ===\n")
    return 1 if results["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
