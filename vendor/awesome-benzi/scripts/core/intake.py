#!/usr/bin/env python3
"""Read-only intake and routing for awesome-benzi.

The command prints one JSON object to stdout and never writes beside user files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from .errors import AwesomeBenziError, ensure_utf8_stdout
from .paths import assert_user_path
from .session import new_execution_budget, normalize_execution_budget

SUPPORTED = {".doc", ".docx", ".pdf", ".xlsx", ".xlsm", ".pptx", ".md", ".txt"}
REBUILDABLE_DOCX = {".doc", ".docx", ".pdf", ".md", ".txt"}
NATIVE_FORMATS = {".xlsx", ".xlsm", ".pptx"}
TEMPLATE_FORMATS = REBUILDABLE_DOCX | NATIVE_FORMATS
TEXT_TYPES = {".md", ".txt"}
MAX_SAMPLE_CHARACTERS = 12_000
MAX_SCAN_WORKERS = 4
MAX_FILES = 500
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_DEPTH = 12
MAX_XML_PART_BYTES = 64 * 1024 * 1024
IGNORED_DIRS = {
    ".git", ".agents", ".codex", ".idea", ".vscode", ".venv", "venv",
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "tmp", "temp", "qa", "dist", "build", "output", "outputs", "expected",
}
IGNORED_SUFFIXES = {".tmp", ".bak", ".lock", ".pyc", ".pyo"}
PREVIOUS_OUTPUT = re.compile(r"(?:完成稿|生成稿|修改稿|润色稿|最终稿)(?:[-_ ]?\d+)?$", re.I)
STYLE_DIRECTIVE_RE = re.compile(
    r"[^。；;\n]{0,30}(?:A4|页边距|宋体|黑体|仿宋|楷体|微软雅黑|小四|四号|三号|二号|五号|"
    r"行距|首行缩进|居中|两端对齐)[^。；;\n]{0,50}"
)
FACT_PLACEHOLDER_RE = re.compile(r"【\s*待补\s*[：:]?\s*([^】]{1,80})】")

ROLE_PATTERNS = {
    "official-notice": re.compile(r"通知|公告|申报指南|参赛指南|申报工作|截止时间|申报条件|参赛对象|赛道设置"),
    "official-rules": re.compile(r"评审规则|评分标准|评分细则|竞赛章程|管理办法|资格审查|匿名要求|评审指标"),
    "application-template": re.compile(r"填写说明|请填写|申报书|申请书|申报表|申请表|课题论证活页|表格不得增删|项目名称.{0,20}(负责人|申请人)"),
    "facts-evidence": re.compile(r"事实|证据|调研记录|访谈记录|实验记录|测试记录|原始数据|合同|订单|发票|专利号|团队分工|已完成|尚未完成"),
    "references": re.compile(r"参考文献|文献综述|研究述评|bibliography|references|DOI|CSSCI|SSCI", re.I),
    "style-sample": re.compile(r"写作样稿|语言样本|语气样本|个人文风|voice sample|style sample", re.I),
    "user-draft": re.compile(r"选题依据|研究内容|研究目标|思路方法|技术路线|创新之处|预期成果|研究基础|项目摘要"),
}
NAME_PATTERNS = {
    "official-notice": re.compile(r"通知|公告|指南|申报要求|赛事要求"),
    "official-rules": re.compile(r"规则|章程|评分|评审|管理办法"),
    "application-template": re.compile(r"模板|空表|申报书|申请书|申报表|申请表|活页|附件\s*\d+", re.I),
    "facts-evidence": re.compile(r"事实|证据|调研|访谈|实验|测试|数据|成果|财务|合同|专利"),
    "references": re.compile(r"参考文献|文献|bibliography|references", re.I),
    "style-sample": re.compile(r"样稿|文风|写作样本|voice|style", re.I),
    "user-draft": re.compile(r"草稿|初稿|修改稿|正文|大纲|论证"),
}

PROGRAMS = [
    ("natural-science-grant", "国家自然科学基金", re.compile(r"NSFC|国自然|国家自然科学基金|自然科学基金|青年科学基金|面上项目", re.I)),
    ("social-science-grant", "社会科学基金", re.compile(r"国社科|国家社会科学基金|社会科学基金|哲学社会科学|人文社科|社科基金", re.I)),
    ("challenge-cup", "挑战杯", re.compile(r"挑战杯|创青春|课外学术科技作品", re.I)),
    ("student-innovation", "大学生创新创业训练计划", re.compile(r"大创|国创|大学生创新创业训练|创新训练|创业训练|创业实践", re.I)),
    ("innovation-competition", "中国国际大学生创新大赛", re.compile(r"中国国际大学生创新大赛|互联网\+|互联网加|创新创业大赛", re.I)),
]

STAGES = [
    ("section-revision", re.compile(r"只(?:修改|润色|改写)|仅(?:修改|润色|改写)|单节|本节")),
    ("full-revision", re.compile(r"全文|全稿|完整.*(?:润色|修改|修订|改写)|润色|完善|修订|改写")),
    ("review", re.compile(r"审稿|评审|诊断|模拟评审")),
    ("defense", re.compile(r"答辩|路演|PPT", re.I)),
    ("topic", re.compile(r"选题|题目|方向")),
    ("outline", re.compile(r"大纲|框架|结构")),
    ("full-draft", re.compile(r"起草|初稿|第一版|完成申报|填完整|撰写|写作|写一份|写完")),
]


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _is_awesome_benzi_package(path: Path) -> bool:
    skill_file = path / "SKILL.md"
    runtime_file = path / "scripts" / "runtime.py"
    if not skill_file.is_file() or not runtime_file.is_file():
        return False
    try:
        head = skill_file.read_text(encoding="utf-8", errors="ignore")[:2048]
    except OSError:
        return False
    return bool(re.search(r"(?m)^name:\s*awesome-benzi\s*$", head))


def _protected_skill_owner(path: Path, active_skill_root: Path, cache: dict[Path, Path | None] | None = None) -> Path | None:
    resolved = path.expanduser().resolve()
    active_skill_root = active_skill_root.resolve()
    if _inside(resolved, active_skill_root):
        return active_skill_root
    current = resolved if resolved.is_dir() else resolved.parent
    if cache is not None and current in cache:
        return cache[current]
    visited: list[Path] = []
    owner: Path | None = None
    for candidate in (current, *current.parents):
        if cache is not None and candidate in cache:
            owner = cache[candidate]
            break
        visited.append(candidate)
        if _is_awesome_benzi_package(candidate):
            owner = candidate
            break
    if cache is not None:
        for candidate in visited:
            cache[candidate] = owner
    return owner


def discover(raw_paths: list[str], skill_root: Path) -> tuple[list[Path], list[str], Path]:
    requested = raw_paths or [str(Path.cwd())]
    files: list[Path] = []
    errors: list[str] = []
    workspace = Path(requested[0]).expanduser().resolve()
    owner_cache: dict[Path, Path | None] = {}
    if workspace.is_file():
        workspace = workspace.parent

    for raw in requested:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            errors.append(f"not found: {path}")
            continue
        owner = _protected_skill_owner(path, skill_root, owner_cache)
        if owner is not None:
            errors.append(f"protected awesome-benzi package is not a user-material path: {path}")
            continue
        if path.is_file():
            if path.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"E_SIZE_LIMIT: file exceeds 100 MB: {path}")
            else:
                files.append(path)
            continue
        for item in path.rglob("*"):
            if not item.is_file() or item.is_symlink():
                continue
            resolved = item.resolve()
            if _protected_skill_owner(resolved, skill_root, owner_cache) is not None:
                continue
            relative = item.relative_to(path)
            if len(relative.parts) > MAX_DEPTH + 1:
                errors.append(f"E_DEPTH_LIMIT: directory depth exceeds {MAX_DEPTH}: {item}")
                continue
            if any(part.startswith(".") or part.lower() in IGNORED_DIRS for part in relative.parts[:-1]):
                continue
            if item.name.startswith((".", "~$")) or item.suffix.lower() in IGNORED_SUFFIXES:
                continue
            if PREVIOUS_OUTPUT.search(item.stem):
                continue
            if item.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"E_SIZE_LIMIT: file exceeds 100 MB: {item}")
                continue
            files.append(resolved)
            if len(files) > MAX_FILES:
                errors.append(f"E_FILE_LIMIT: discovered more than {MAX_FILES} files")
                break
    ordered = sorted(set(files), key=lambda value: str(value).lower())[:MAX_FILES]
    total = 0
    retained: list[Path] = []
    for candidate in ordered:
        size = candidate.stat().st_size
        if total + size > MAX_TOTAL_BYTES:
            errors.append("E_SIZE_LIMIT: discovered files exceed 1 GB in total")
            break
        retained.append(candidate)
        total += size
    return retained, errors, workspace


def _ooxml_text(path: Path) -> str:
    prefixes = {
        ".docx": ("word/document.xml", "word/header", "word/footer"),
        ".pptx": ("ppt/slides/slide",),
        ".xlsx": ("xl/sharedStrings.xml", "xl/worksheets/sheet"),
        ".xlsm": ("xl/sharedStrings.xml", "xl/worksheets/sheet"),
    }[path.suffix.lower()]
    parts: list[str] = []
    characters = 0
    with zipfile.ZipFile(path) as package:
        for name in package.namelist():
            if name.endswith(".xml") and any(name.startswith(prefix) for prefix in prefixes):
                info = package.getinfo(name)
                if info.file_size > MAX_XML_PART_BYTES:
                    raise ValueError(f"E_SIZE_LIMIT: OOXML part exceeds 64 MB: {name}")
                if info.compress_size and info.file_size / info.compress_size > 200:
                    raise ValueError(f"E_SIZE_LIMIT: suspicious OOXML compression ratio: {name}")
                try:
                    with package.open(name) as handle:
                        for _, node in ET.iterparse(handle, events=("end",)):
                            if node.tag.rsplit("}", 1)[-1] in {"t", "v"} and (node.text or "").strip():
                                value = (node.text or "").strip()
                                parts.append(value)
                                characters += len(value)
                                if characters >= MAX_SAMPLE_CHARACTERS:
                                    return "\n".join(parts)[:MAX_SAMPLE_CHARACTERS]
                            node.clear()
                except ET.ParseError:
                    continue
    return "\n".join(parts)


def _pdf_text_and_form(path: Path) -> tuple[str, bool, list[str]]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", False, ["pypdf unavailable; classified from filename only"]
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            return "", False, ["encrypted PDF"]
        if len(reader.pages) > 500:
            raise ValueError("E_SIZE_LIMIT: PDF exceeds 500 pages")
        text = "\n".join((page.extract_text() or "") for page in islice(reader.pages, 2))[:MAX_SAMPLE_CHARACTERS]
        return text, bool(reader.get_fields()), []
    except Exception as exc:
        return "", False, [f"PDF extraction failed: {exc}"]


def _signature_check(path: Path, suffix: str) -> tuple[bool, str | None]:
    try:
        if suffix in {".docx", ".pptx", ".xlsx", ".xlsm"}:
            if not zipfile.is_zipfile(path):
                return False, "not a ZIP-based OOXML package"
            with zipfile.ZipFile(path) as package:
                names = package.namelist()
            required = {
                ".docx": "word/document.xml",
                ".pptx": "ppt/presentation.xml",
                ".xlsx": "xl/workbook.xml",
                ".xlsm": "xl/workbook.xml",
            }[suffix]
            if required not in names:
                return False, f"missing {required}"
        elif suffix == ".pdf":
            if path.read_bytes()[:5] != b"%PDF-":
                return False, "not a PDF file"
        elif suffix == ".doc":
            if path.read_bytes()[:8] != bytes.fromhex("D0CF11E0A1B11AE1"):
                return False, "not an OLE2 legacy DOC container"
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        return False, str(exc)
    return True, None


def extract(path: Path) -> tuple[str, dict]:
    suffix = path.suffix.lower()
    if suffix in TEXT_TYPES:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            return handle.read(MAX_SAMPLE_CHARACTERS), {"sampled": True}
    if suffix == ".doc":
        magic = path.read_bytes()[:8]
        return "", {
            "legacy_doc": True,
            "ole_container": magic == bytes.fromhex("D0CF11E0A1B11AE1"),
            "input_recovery": {
                "kind": "legacy-doc-conversion",
                "required": True,
                "user_action_required": False,
                "preferred_backends": ["word-com", "libreoffice-headless"],
            },
        }
    if suffix in {".docx", ".pptx", ".xlsx", ".xlsm"}:
        if not zipfile.is_zipfile(path):
            raise ValueError("invalid OOXML package")
        return _ooxml_text(path), {"sampled": True}
    if suffix == ".pdf":
        text, fillable, review = _pdf_text_and_form(path)
        characters = len(re.sub(r"\s+", "", text))
        details = {"fillable_pdf": fillable, "review": review, "extracted_characters": characters, "sampled_pages": 2}
        if characters < 100:
            details["input_recovery"] = {
                "kind": "scanned-pdf-ocr",
                "required": True,
                "user_action_required": False,
                "preferred_backends": ["local-ocr", "platform-vision"],
            }
        return text, details
    raise ValueError(f"unsupported extension: {suffix}")


def classify(name: str, text: str, suffix: str) -> tuple[str, float, list[str]]:
    best = ("unknown", 0.2, [])
    for role, content_pattern in ROLE_PATTERNS.items():
        content_hits = list(content_pattern.finditer(text[:100_000]))
        name_hits = list(NAME_PATTERNS[role].finditer(name))
        if not content_hits and not name_hits:
            continue
        score = 0.25 + min(len(content_hits), 5) * 0.11 + min(len(name_hits), 2) * 0.17
        evidence = [match.group(0)[:40] for match in content_hits[:3]] + [f"filename:{match.group(0)}" for match in name_hits[:2]]
        if role == "application-template" and suffix in TEMPLATE_FORMATS and name_hits:
            score = max(score, 0.84)
        if role == "application-template" and re.search(r"_{3,}|【?待填写|请在.{0,12}填写", text):
            score += 0.15
        if score > best[1]:
            best = role, min(round(score, 2), 0.99), evidence
    return best


def _program(text: str) -> tuple[str, str, float]:
    for family, label, pattern in PROGRAMS:
        if pattern.search(text):
            return family, label, 0.94
    return "unknown", "待确认项目", 0.35


def _stage(prompt: str) -> str:
    for stage, pattern in STAGES:
        if pattern.search(prompt):
            return stage
    return "intake"


def _word_automation_available() -> bool:
    if shutil.which("soffice") or shutil.which("libreoffice"):
        return True
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Word.Application\CLSID"):
            return True
    except OSError:
        return False


def _style_directives(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0).strip() for match in STYLE_DIRECTIVE_RE.finditer(text)))


def _style_directive_conflicts(directives: list[str]) -> dict[str, list[str]]:
    text = "\n".join(directives)
    margins = {
        match.group(1)
        for match in re.finditer(r"(?:四边|上下左右)?页边距[^\d]{0,8}(\d+(?:\.\d+)?)\s*(?:厘米|cm)", text, re.I)
    }
    body_profiles: set[str] = set()
    for size_first, pattern in (
        (False, r"正文[^。；;\n]{0,35}(宋体|仿宋(?:_GB2312)?|楷体|微软雅黑)[^。；;\n]{0,20}(小四|四号|五号|小五)"),
        (True, r"正文[^。；;\n]{0,35}(小四|四号|五号|小五)[^。；;\n]{0,20}(宋体|仿宋(?:_GB2312)?|楷体|微软雅黑)"),
    ):
        for match in re.finditer(pattern, text):
            first, second = match.groups()
            body_profiles.add(f"{second}/{first}" if size_first else f"{first}/{second}")
    conflicts: dict[str, list[str]] = {}
    if len(margins) > 1:
        conflicts["page-margin"] = sorted(margins)
    if len(body_profiles) > 1:
        conflicts["body-font"] = sorted(body_profiles)
    return conflicts


def _semantic_confidence(record: dict) -> float:
    suffix = record["extension"]
    text = record.get("content_excerpt", "")
    if suffix == ".doc":
        return 0.8
    if suffix == ".pdf":
        characters = record.get("format_details", {}).get("extracted_characters", 0)
        return 0.78 if characters >= 100 else 0.76
    if suffix in {".docx", ".md", ".txt"}:
        has_heading = bool(re.search(r"(?:^|\n)(?:#{1,3}\s+|[一二三四五六七八九十]+[、.]|（[一二三四五六七八九十]+）|选题依据|研究内容|项目摘要)", text))
        return 0.9 if has_heading else 0.76 if len(text.strip()) >= 100 else 0.55
    return 0.95


def _template_strategy(record: dict) -> tuple[str, str | None]:
    suffix = record["extension"]
    if suffix == ".doc":
        return "semantic-docx-rebuild", None
    if suffix == ".pdf":
        return "semantic-docx-rebuild", None
    if suffix in {".docx", ".md", ".txt"}:
        return "semantic-docx-rebuild", None
    if suffix in NATIVE_FORMATS:
        return "unsupported-format", "PPTX, XLSX and XLSM are outside the DOCX proposal workflow"
    return "blocked", "unsupported template format"


def scan(
    paths: list[str],
    prompt: str,
    explicit_template: str | None = None,
    budget_seconds: int | float = 30,
) -> dict:
    started = time.perf_counter()
    scan_deadline = started + max(1.0, float(budget_seconds))
    execution_budget = new_execution_budget(budget_seconds)
    from .template_schema import detect_runtime_capabilities

    capabilities = detect_runtime_capabilities()
    skill_root = Path(__file__).resolve().parents[2]
    files, errors, workspace = discover(paths, skill_root)
    discovery_finished = time.perf_counter()
    explicit = None
    if explicit_template:
        try:
            explicit = assert_user_path(Path(explicit_template), skill_root)
        except AwesomeBenziError as exc:
            errors.append(f"{exc.code}: {exc.message}")
        if explicit is not None and explicit not in files:
            files.append(explicit)

    blockers: list[dict] = []

    def inspect(path: Path) -> tuple[dict, str, dict | None]:
        suffix = path.suffix.lower()
        source_id = "src-" + hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()[:12]
        record = {
            "schema_type": "source-record", "schema_version": 1,
            "source_id": source_id,
            "path": str(path), "name": path.name, "extension": suffix,
            "mime": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "size": path.stat().st_size, "supported": suffix in SUPPORTED,
            "signature_valid": True, "signature_error": None,
        }
        if time.perf_counter() >= scan_deadline:
            record.update(
                {
                    "semantic_role": "unknown",
                    "role_confidence": 0.0,
                    "read_status": "budget-exhausted",
                    "read_error": "E_TIMEOUT: scan budget exhausted",
                }
            )
            return record, "", None
        if suffix not in SUPPORTED:
            record.update({"semantic_role": "unknown", "role_confidence": 0.0, "read_status": "ignored-unsupported"})
            return record, "", None
        signature_valid, signature_error = _signature_check(path, suffix)
        if not signature_valid:
            record.update({"signature_valid": False, "signature_error": signature_error, "semantic_role": "unknown", "role_confidence": 0.0, "read_status": "signature-mismatch", "read_error": f"E_SIGNATURE_MISMATCH: {signature_error}"})
            errors.append(f"E_SIGNATURE_MISMATCH: {path}: {signature_error}")
            blocker = None
            if explicit and path.resolve() == explicit:
                blocker = {"class": "A", "kind": "signature-mismatch", "error_code": "E_SIGNATURE_MISMATCH", "path": str(path), "message": signature_error}
            return record, "", blocker
        try:
            text, details = extract(path)
            role, confidence, evidence = classify(path.name, text, suffix)
            if explicit and path.resolve() == explicit:
                role, confidence, evidence = "application-template", 1.0, ["explicit-template-path"]
            elif path.name.lower() in prompt.lower() or str(path).lower() in prompt.lower():
                if re.search(r"模板|申请书|申报书|表格", prompt):
                    role, confidence, evidence = "application-template", 0.99, ["template-named-in-prompt"]
            style_directives = _style_directives(text)
            record.update({
                "semantic_role": role, "role_confidence": confidence,
                "role_evidence": evidence, "content_excerpt": text[:5000],
                "read_status": (
                    "recoverable-input"
                    if details.get("input_recovery", {}).get("required")
                    else "read" if text.strip() else "metadata-only"
                ),
                "format_details": details,
                "style_directives": style_directives,
            })
            record["semantic_structure_confidence"] = _semantic_confidence(record)
            return record, text, None
        except Exception as exc:
            record.update({"semantic_role": "unknown", "role_confidence": 0.0, "read_status": "unreadable", "read_error": str(exc)})
            blocker = None
            if explicit and path.resolve() == explicit:
                blocker = {"class": "A", "kind": "unreadable-key-file", "path": str(path), "message": str(exc)}
            return record, "", blocker

    max_workers = max(1, min(MAX_SCAN_WORKERS, len(files))) if len(files) >= 8 else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        inspected = list(executor.map(inspect, files))
    records = [item[0] for item in inspected]
    full_text_by_path = {item[0]["path"]: item[1] for item in inspected}
    blockers.extend(item[2] for item in inspected if item[2] is not None)
    sampling_finished = time.perf_counter()
    if sampling_finished > scan_deadline:
        errors.append(f"E_TIMEOUT: scan exceeded {round(float(budget_seconds), 2)} seconds")

    templates = sorted(
        [item for item in records if item.get("semantic_role") == "application-template"],
        key=lambda item: (item.get("role_confidence", 0), item["extension"] != ".pdf", item["path"]),
        reverse=True,
    )
    primary = templates[0] if templates else None
    if len(templates) > 1 and templates[0]["role_confidence"] - templates[1]["role_confidence"] <= 0.05 and not explicit:
        blockers.append({"class": "A", "kind": "multiple-primary-templates", "candidates": [templates[0]["path"], templates[1]["path"]], "message": "choose the main template"})
        primary = None
    if primary:
        status, reason = _template_strategy(primary)
        primary["output_strategy"] = status
        if status == "blocked":
            blockers.append({"class": "A", "kind": "template-blocked", "path": primary["path"], "message": reason})
        elif status == "unsupported-format":
            blockers.append(
                {
                    "class": "A",
                    "kind": "unsupported-format",
                    "error_code": "E_UNSUPPORTED_FORMAT",
                    "path": primary["path"],
                    "message": reason,
                }
            )
        elif (
            primary.get("semantic_structure_confidence", 0.0) < 0.75
            and not primary.get("format_details", {}).get("input_recovery", {}).get("required")
        ):
            blockers.append({"class": "A", "kind": "low-semantic-structure-confidence", "path": primary["path"], "message": "provide a clearer template or confirm the heading structure"})
    else:
        blockers.append({"class": "A", "kind": "missing-template", "message": "provide the official native editable template"})

    evidence_chunks = [prompt]
    evidence_sources: list[str] = []
    for item in records:
        if item.get("semantic_role") in {"official-notice", "official-rules", "application-template", "user-draft"}:
            evidence_chunks.append(item.get("name", ""))
            evidence_chunks.append(item.get("content_excerpt", ""))
            evidence_sources.append(item["path"])
    prompt_family, prompt_program, prompt_confidence = _program(prompt)
    if prompt_confidence >= 0.9:
        family, program, confidence = prompt_family, prompt_program, prompt_confidence
    else:
        family, program, confidence = _program("\n".join(evidence_chunks))
    stage = _stage(prompt)
    output_strategy = primary.get("output_strategy") if primary else None
    output_format = "docx" if primary and primary["extension"] in REBUILDABLE_DOCX else None
    style_records = ([primary] if primary else []) + [
        item for item in records
        if item is not primary and item.get("semantic_role") in {"official-notice", "official-rules"}
    ]
    style_directives = list(dict.fromkeys(
        directive
        for item in style_records
        for directive in item.get("style_directives", [])
    ))
    directive_conflicts = _style_directive_conflicts(style_directives)
    if directive_conflicts:
        blockers.append({
            "class": "A", "kind": "conflicting-style-directives",
            "message": "confirm which explicit formatting requirement controls the rebuilt document",
            "conflicts": directive_conflicts,
        })
    required_facts: list[dict] = []
    if primary:
        template_text = full_text_by_path.get(primary["path"], "")
        names = list(dict.fromkeys(match.group(1).strip() for match in FACT_PLACEHOLDER_RE.finditer(template_text)))
        required_facts = [
            {"class": "B", "kind": "required-fact", "name": name, "message": f"provide {name}, or keep the marked placeholder"}
            for name in names
        ]
    recovery_actions = [
        {
            **item["format_details"]["input_recovery"],
            "path": item["path"],
            "semantic_role": item.get("semantic_role", "unknown"),
        }
        for item in records
        if item.get("format_details", {}).get("input_recovery", {}).get("required")
    ]
    full_extraction_candidates = [
        item["path"]
        for item in records
        if item.get("supported") and item.get("semantic_role") in {
            "official-notice", "official-rules", "application-template", "user-draft",
            "facts-evidence", "references", "style-sample",
        }
    ]
    route = {
        "schema_type": "route", "schema_version": 2,
        "type": "route.v2", "program_family": family, "program": program,
        "stage": stage, "workflow_id": family, "template_path": primary["path"] if primary else None,
        "source_template_path": primary["path"] if primary else None,
        "source_format": primary["extension"].lstrip(".") if primary else None,
        "output_strategy": output_strategy,
        "output_format": output_format,
        "semantic_structure_confidence": primary.get("semantic_structure_confidence") if primary else None,
        "style_directives": style_directives,
        "preserved_elements": ["text-order", "heading-hierarchy", "table-topology", "checkbox-state", "official-images"] if primary and primary["extension"] in REBUILDABLE_DOCX else [],
        "input_recovery_actions": recovery_actions,
        "full_extraction_candidates": full_extraction_candidates,
        "confidence": confidence, "sources": evidence_sources,
        "delivery_preflight": {
            "gate": "passed",
            "render_review_available": bool(capabilities["render_gate"]["available"]),
            "missing": capabilities["render_gate"]["missing"],
            "warnings": (
                []
                if capabilities["render_gate"]["available"]
                else [
                    "LibreOffice 或 Poppler 不可用：交付时将跳过机械渲染与逐页视觉复核，仅执行一致性与结构检查。"
                ]
            ),
            "suggested_action": (
                None
                if capabilities["render_gate"]["available"]
                else "Optional: install LibreOffice and Poppler to enable page-level render review."
            ),
        },
    }
    question_batch = {
        "schema_type": "question-batch", "schema_version": 1,
        "type": "question-batch.v1", "needed": bool(blockers or required_facts),
        "groups": {"A_route_or_template_blockers": blockers, "B_required_facts": required_facts, "C_preferences": []},
        "ask_once": True,
    }
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    execution_budget = normalize_execution_budget(execution_budget, budget_seconds)
    execution_budget["consumed_ms"] = round(min(execution_budget["limit_ms"], elapsed_ms), 2)
    execution_budget["remaining_ms"] = round(
        max(0.0, execution_budget["limit_ms"] - execution_budget["consumed_ms"]),
        2,
    )
    return {
        "schema_type": "session", "schema_version": 5,
        "type": "session.v5", "workspace": str(workspace), "prompt": prompt,
        "intake": {
            "schema_type": "intake", "schema_version": 2,
            "type": "intake.v2", "files": records,
            "primary_template": primary["path"] if primary else None,
            "template_candidates": [item["path"] for item in templates],
            "errors": errors, "internal_recovery_actions": recovery_actions,
        },
        "route": route, "question_batch": question_batch,
        "case-manifest": {
            "workspace": str(workspace),
            "files": len(records),
            "primary_template": primary["path"] if primary else None,
            "budget_seconds": float(budget_seconds),
        },
        "source-records": records,
        "route-decision": route,
        "capabilities": capabilities,
        "execution_budget": execution_budget,
        "backend_attempts": [],
        "recovery_checkpoints": [],
        "performance": {
            "discovery_ms": round((discovery_finished - started) * 1000, 2),
            "sampling_ms": round((sampling_finished - discovery_finished) * 1000, 2),
            "total_ms": elapsed_ms,
            "discovered_files": len(files), "sampled_files": sum(item.get("supported", False) for item in records),
            "full_extractions": 0, "max_workers": max_workers,
        },
        "side_effect_contract": {
            "writes_to_material_directory": False,
            "allowed_delivery_additions": 1,
            "skill_package_mutable": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scan_parser = sub.add_parser("scan", help="scan and route without writing files")
    scan_parser.add_argument("--path", action="append", default=[])
    scan_parser.add_argument("--prompt", default="")
    scan_parser.add_argument("--template")
    scan_parser.add_argument("--budget-seconds", type=float, default=30)
    args = parser.parse_args(argv)
    result = scan(args.path, args.prompt, args.template, args.budget_seconds)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    blocked = bool(result["intake"]["errors"]) or result["route"].get("output_strategy") in {
        "blocked",
        "unsupported-format",
    }
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
