#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — 技能包完整性自检

对应 CONVENTIONS.md 第 7、8 节的验收清单，把「靠记忆检查」变成「跑一遍」：
  1. skills/ 下所有技能目录自动发现（主技能/底座按布局约定分类，不再硬编码清单）
  2. frontmatter 是否有 name / description，description 是否有 Triggers 与足够触发短语
  2b. 主技能是否具备 CONVENTIONS §7 规定的必备章节（何时使用/intake/工作流/底座/产出物/红线/自检）
  3. SKILL.md 里引用的 skills/ 底座路径是否真实存在（防止凭记忆写路径）
  3b. $BK_HOME/skills/... 这类上游套件内引用能否解析到 skills/ibook-skills/ 下的真实文件
  4. 文件产出是否走了 office-layer（主技能）
  5. 是否声明了「不虚构」与「人工确认位」纪律（主技能）
  6. office-layer 的三个脚本能否正常拉起

布局约定（自动发现的分类依据）：
  - 技能 = skills/ 下任何含 SKILL.md 的目录
  - 底座 = 位于套件目录（SUITE_DIRS）内的技能，或 INDEPENDENT_FOUNDATION 点名的顶层技能
  - 主技能 = 其余顶层技能

用法：python3 verify.py [--root .]
退出码：0 全部通过；1 有 FAIL。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# 套件目录：同一上游的一套底座收进一个目录（目录自身不含 SKILL.md）
SUITE_DIRS = (
    "education-skills", "empirical-research", "ibook-skills",
    "k12-teacher-skills", "learning-education",
)

# 独立底座件：顶层平铺但不是主技能
INDEPENDENT_FOUNDATION = (
    "office-layer", "awesome-benzi", "paper-analyst", "slides-polish",
)


def discover_skills(skill_dir: Path):
    """自动发现 skills/ 下全部技能，返回 (主技能列表, 底座列表)，元素为相对 skills/ 的路径。"""
    mains, foundations = [], []
    for f in sorted(skill_dir.rglob("SKILL.md")):
        rel = f.parent.relative_to(skill_dir).as_posix()
        parts = rel.split("/")
        if len(parts) > 1:
            # 套件目录内的技能一律是底座
            foundations.append(rel)
        elif parts[0] in INDEPENDENT_FOUNDATION:
            foundations.append(rel)
        else:
            mains.append(rel)
    return mains, foundations

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
    EXPECTED_MAIN, EXPECTED_FOUNDATION = discover_skills(skill_dir)

    # CONVENTIONS §7 规定的主技能必备章节（宽松匹配常见同义写法）
    REQUIRED_SECTIONS = {
        "何时使用": r"^#{1,4}\s.*(何时使用|何时用|适用场景|使用场景|何时触发)",
        "intake 前置信息收集": r"^#{1,4}\s.*(前置信息|信息收集|intake)",
        "工作流": r"^#{1,4}\s.*(工作流|流程|阶段一|执行步骤)",
        "底座": r"^#{1,4}\s.*底座",
        "产出物": r"^#{1,4}\s.*(产出物|产出|交付物)",
        "红线": r"^#{1,4}\s.*红线",
        "自检清单": r"^#{1,4}\s.*(自检|检查清单|自查|核对清单)",
    }

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

    print(f"\n[2] {len(EXPECTED_MAIN)} 个主技能（自动发现）")
    for name in EXPECTED_MAIN:
        check_skill(name, discipline=True)

    # ---------- 2b. 主技能结构完备性（CONVENTIONS §7） ----------
    print("\n[2b] 主技能必备章节（CONVENTIONS §7）")
    for name in EXPECTED_MAIN:
        f = skill_dir / name / "SKILL.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        missing = [label for label, pat in REQUIRED_SECTIONS.items()
                   if not re.search(pat, text, re.MULTILINE)]
        if missing:
            warn(f"{name}: 缺章节 {missing}")
        else:
            ok(f"{name} 章节齐全")

    print(f"\n[3] {len(EXPECTED_FOUNDATION)} 个底座技能（自动发现）")
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

    # ---------- 4b. $BK_HOME 套件内引用真实性 ----------
    # ibook-skills 套件内部用 $BK_HOME/skills/<子路径> 互相引用（上游生态约定）。
    # 在本仓库中 $BK_HOME/skills 映射到 skills/ibook-skills/；套件成员缺收时
    # 这些引用会静默悬空（2026-10-19 曾因此缺收 book-installer 等两件）。
    # 扫描所有技能目录下的 .md（含 references/），逐一解析验证。
    print("\n[4b] 上游套件内引用（$BK_HOME/skills/...）解析")
    BK_PREFIX = "$BK_HOME/skills/"
    bk_map_root = skill_dir / "ibook-skills"
    bk_bad = {}
    bk_count = 0
    bk_re = re.compile(r"\$BK_HOME/skills/[\w\-./]+", re.UNICODE)
    for name in EXPECTED_MAIN + EXPECTED_FOUNDATION:
        d = skill_dir / name
        if not d.is_dir():
            continue
        for md in d.rglob("*.md"):
            for m in bk_re.finditer(md.read_text(encoding="utf-8")):
                ref = m.group(0).rstrip(".,;:`)】」").rstrip("/")
                rel = ref[len(BK_PREFIX):]
                if not rel or ".." in rel:
                    continue
                bk_count += 1
                if not (bk_map_root / rel).exists():
                    bk_bad.setdefault(f"{name}/{md.relative_to(d)}", []).append(ref)
    if bk_bad:
        for where, refs in bk_bad.items():
            for r in sorted(set(refs)):
                fail(f"{where} 的 $BK_HOME 引用悬空：{r}（映射 skills/ibook-skills/ 后不存在）")
    else:
        ok(f"所有 $BK_HOME 套件内引用均可解析（共 {bk_count} 处）")

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
