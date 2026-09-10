#!/usr/bin/env python3
"""Extract proposal templates into a format-neutral semantic document tree.

The extractor reads source files only. It never writes beside user materials and
uses the original formatting only as evidence for semantic classification.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from statistics import median
from typing import Any, Iterable

from .contracts import SessionState
from .errors import AwesomeBenziError, ensure_utf8_stdout
from .ledgers import integrate_method_modules, required_modules as _ledger_required_modules
from .style_profile import extract_style_profile, render_style_brief
from .session import (
    DEFAULT_BACKEND_TIMEOUT_SECONDS,
    bounded_timeout_seconds,
    cleanup_expired_sessions,
    consume_execution_budget,
    create_session,
    new_execution_budget,
    normalize_execution_budget,
    remaining_budget_seconds,
    run_bounded_process,
    transition,
)

SUPPORTED = {".doc", ".docx", ".pdf", ".md", ".txt"}
SESSION_PREFIX = "awesome-benzi-session-"
PLACEHOLDER_RE = re.compile(r"【[^】]*(?:填写|待补|请输入|在此)[^】]*】|_{3,}|^\s*(?:请填写|待填写|在此填写)\s*$")
INSTRUCTION_RE = re.compile(r"填写说明|申报说明|注意事项|不得增删|限.{0,8}字|字数.{0,8}(?:以内|不超过)|请按.{0,12}填写")
KNOWN_HEADINGS = re.compile(
    r"^(?:项目摘要|摘要|关键词|选题依据|立项依据|研究背景|国内外研究现状|研究内容|研究目标|"
    r"思路方法|研究方法|技术路线|创新之处|创新点|预期成果|研究基础|前期基础|团队介绍|"
    r"进度安排|经费预算|风险分析|社会价值|市场分析|商业模式|项目概述|可行性分析)$"
)
NUMBERED_HEADINGS = [
    (1, re.compile(r"^[一二三四五六七八九十百]+[、.]\s*\S+")),
    (2, re.compile(r"^[（(][一二三四五六七八九十百]+[）)]\s*\S+")),
    (2, re.compile(r"^\d+[、.]\s*\S+")),
    (3, re.compile(r"^\d+(?:\.\d+)+\s*\S+")),
]
STYLE_DIRECTIVE_RE = re.compile(
    r"[^。；;\n]{0,30}(?:A4|页边距|宋体|黑体|仿宋|楷体|微软雅黑|小四|四号|三号|二号|五号|"
    r"行距|首行缩进|居中|两端对齐)[^。；;\n]{0,50}"
)
SKILL_ROOT = Path(__file__).resolve().parents[2]
DOC_RECOVERY_LIMIT_SECONDS = 120
OCR_PAGE_LIMIT = 40
OCR_BATCH_SIZE = 10
OCR_BATCH_TIMEOUT_SECONDS = 45


def _is_awesome_benzi_package(path: Path) -> bool:
    skill_file = path / "SKILL.md"
    runtime_file = path / "scripts" / "runtime.py"
    if not skill_file.is_file() or not runtime_file.is_file():
        return False
    try:
        return bool(re.search(r"(?m)^name:\s*awesome-benzi\s*$", skill_file.read_text(encoding="utf-8", errors="ignore")[:2048]))
    except OSError:
        return False


def _protected_skill_owner(path: Path) -> Path | None:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(SKILL_ROOT)
        return SKILL_ROOT
    except ValueError:
        pass
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if _is_awesome_benzi_package(candidate):
            return candidate
    return None


def _assert_user_material_path(path: Path) -> Path:
    expanded = path.expanduser().absolute()
    if not expanded.exists():
        raise AwesomeBenziError(
            "E_PATH_NOT_FOUND",
            "path",
            f"path does not exist: {expanded}",
            path=str(expanded),
            recoverability="user-input",
            user_action_required=True,
            suggested_action="Provide an existing user-material path outside the Skill package.",
        )
    for candidate in (expanded, *expanded.parents):
        if not candidate.exists():
            continue
        try:
            is_reparse = os.name == "nt" and bool(candidate.lstat().st_file_attributes & 0x400)
        except (AttributeError, OSError):
            is_reparse = False
        if candidate.is_symlink() or is_reparse:
            raise AwesomeBenziError(
                "E_PATH_ESCAPE",
                "path",
                f"symbolic links and reparse points are not accepted as user materials: {candidate}",
                path=str(expanded),
                recoverability="user-input",
                user_action_required=True,
                suggested_action="Provide the real path instead of a link or reparse point.",
            )
    resolved = expanded.resolve()
    owner = _protected_skill_owner(resolved)
    if owner is not None:
        raise AwesomeBenziError(
            "E_PATH_PROTECTED",
            "path",
            f"awesome-benzi runtime package is read-only and cannot be used as proposal material: {resolved}",
            path=str(resolved),
            recoverability="user-input",
            user_action_required=True,
            suggested_action="Copy user materials outside the Skill package and retry.",
        )
    return resolved


def _check_source_signature(path: Path) -> None:
    suffix = path.suffix.lower()
    try:
        if suffix == ".docx":
            if not zipfile.is_zipfile(path):
                raise ValueError("not a ZIP-based OOXML package")
            with zipfile.ZipFile(path) as package:
                if "word/document.xml" not in package.namelist():
                    raise ValueError("missing word/document.xml")
        elif suffix == ".doc":
            if path.read_bytes()[:8] != bytes.fromhex("D0CF11E0A1B11AE1"):
                raise ValueError("not an OLE2 legacy DOC container")
        elif suffix == ".pdf":
            if path.read_bytes()[:5] != b"%PDF-":
                raise ValueError("not a PDF file")
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        raise AwesomeBenziError(
            "E_SIGNATURE_MISMATCH",
            "extract",
            f"extension does not match file signature: {path}",
            path=str(path),
            recoverability="user-input",
            user_action_required=True,
            suggested_action="Provide a valid file whose content matches its extension.",
            details={"signature_error": str(exc)},
        ) from exc


class UserActionRequired(RuntimeError):
    """Raised when a source cannot be read safely in the current environment."""


class InternalRecoveryRequired(RuntimeError):
    """Raised when the agent must continue with an internal recovery backend."""


class LegacyDocRecoveryRequired(InternalRecoveryRequired):
    """Signal that Word conversion must be retried outside a restricted session."""

    def __init__(
        self,
        path: Path,
        reason: str,
        attempts: list[dict[str, Any]] | None = None,
        execution_budget: dict[str, Any] | None = None,
    ):
        super().__init__(reason)
        self.backend_attempts = list(attempts or [])
        self.execution_budget = execution_budget
        self.action = {
            "kind": "legacy-doc-privileged-retry",
            "path": str(path),
            "instruction": "rerun document_structure.py extract in a host session allowed to launch hidden Word automation; keep every converted file in the operating-system temporary directory",
            "user_action_required": False,
        }


class VisionOcrRequired(InternalRecoveryRequired):
    """Signal that scanned pages must be transcribed with the platform vision model."""

    def __init__(
        self,
        path: Path,
        reason: str,
        attempts: list[dict[str, Any]] | None = None,
        execution_budget: dict[str, Any] | None = None,
    ):
        super().__init__(reason)
        self.backend_attempts = list(attempts or [])
        self.execution_budget = execution_budget
        self.action = {
            "kind": "platform-vision-ocr",
            "path": str(path),
            "instruction": "render every PDF page in an operating-system temporary directory, transcribe it with platform vision, preserve page order, and pass the recovered text back through recovered_source_text",
            "user_action_required": False,
        }


def _node(anchor: str, kind: str, text: str = "", confidence: float = 0.9, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source_anchor": anchor,
        "kind": kind,
        "text": text.strip(),
        "confidence": round(max(0.0, min(confidence, 1.0)), 3),
    }
    result.update(extra)
    return result


def _paragraph_kind(
    text: str,
    style_name: str = "",
    outline_level: int | None = None,
    bold_ratio: float = 0.0,
    font_size: float | None = None,
    body_size: float | None = None,
    has_numbering: bool = False,
) -> tuple[str, int | None, float]:
    clean = text.strip()
    style_lower = style_name.lower()
    if not clean:
        return "empty", None, 1.0
    if "title" in style_lower or "标题" in style_name and not re.search(r"\d", style_name):
        return "document-title", None, 0.96
    match = re.search(r"heading\s*([1-9])|标题\s*([1-9一二三])", style_lower)
    if match:
        raw = next((part for part in match.groups() if part), "1")
        mapping = {"一": 1, "二": 2, "三": 3}
        return "heading", min(mapping.get(raw, int(raw) if raw.isdigit() else 1), 3), 0.98
    if outline_level is not None:
        return "heading", min(outline_level + 1, 3), 0.98
    if KNOWN_HEADINGS.fullmatch(clean):
        return "heading", 1, 0.93
    if PLACEHOLDER_RE.search(clean):
        return "placeholder", None, 0.96
    if INSTRUCTION_RE.search(clean):
        return "instruction", None, 0.9
    if len(clean) <= 70 and not clean.endswith(("。", "；", ";", "，", ",")):
        for level, pattern in NUMBERED_HEADINGS:
            if pattern.search(clean):
                return "heading", level, 0.9
        if bold_ratio >= 0.8 and body_size and font_size and font_size >= body_size + 1.5:
            return "heading", 2, 0.78
    if has_numbering:
        return "list-item", None, 0.86
    return "paragraph", None, 0.88


def _outline_level(paragraph: Any) -> int | None:
    ppr = paragraph._p.pPr
    if ppr is None:
        return None
    outline = ppr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}outlineLvl")
    if outline is None:
        return None
    value = outline.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")
    return int(value) if value and value.isdigit() else None


def _has_numbering(paragraph: Any) -> bool:
    ppr = paragraph._p.pPr
    return bool(ppr is not None and ppr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr") is not None)


def _paragraph_features(paragraph: Any) -> dict[str, Any]:
    sizes: list[float] = []
    bold_chars = 0
    total_chars = 0
    for run in paragraph.runs:
        count = len(run.text.strip())
        total_chars += count
        if run.bold:
            bold_chars += count
        if run.font.size:
            sizes.append(float(run.font.size.pt))
    return {
        "font_size": max(sizes) if sizes else None,
        "bold_ratio": bold_chars / total_chars if total_chars else 0.0,
        "style_name": paragraph.style.name if paragraph.style else "",
        "outline_level": _outline_level(paragraph),
        "has_numbering": _has_numbering(paragraph),
    }


def _image_refs(paragraph: Any) -> list[dict[str, Any]]:
    from docx.oxml.ns import qn

    refs: list[dict[str, Any]] = []
    for blip in paragraph._p.xpath(".//a:blip"):
        rel_id = blip.get(qn("r:embed"))
        if not rel_id:
            continue
        relationship = paragraph.part.rels.get(rel_id)
        target = getattr(relationship, "target_part", None)
        refs.append({
            "image_ref": rel_id,
            "content_type": getattr(target, "content_type", None),
            "source_part": str(getattr(target, "partname", "")),
        })
    return refs


def _docx_paragraph_node(paragraph: Any, anchor: str, body_size: float | None) -> dict[str, Any]:
    features = _paragraph_features(paragraph)
    kind, level, confidence = _paragraph_kind(paragraph.text, body_size=body_size, **features)
    return _node(
        anchor,
        kind,
        paragraph.text,
        confidence,
        level=level,
        source_style=features["style_name"],
        source_font_size=features["font_size"],
        source_bold_ratio=round(features["bold_ratio"], 3),
        images=_image_refs(paragraph),
    )


def _table_node(table: Any, table_index: int, body_size: float | None) -> dict[str, Any]:
    from docx.oxml.ns import qn
    from docx.table import _Cell, _Row

    rows: list[dict[str, Any]] = []
    max_columns = 0
    for row_index, tr in enumerate(table._tbl.tr_lst):
        row = _Row(tr, table)
        cells: list[dict[str, Any]] = []
        column = 0
        for cell_index, tc in enumerate(tr.tc_lst):
            cell = _Cell(tc, row)
            grid_span_element = tc.tcPr.find(qn("w:gridSpan")) if tc.tcPr is not None else None
            span_raw = grid_span_element.get(qn("w:val")) if grid_span_element is not None else None
            grid_span = int(span_raw) if span_raw and span_raw.isdigit() else 1
            vmerge_element = tc.tcPr.find(qn("w:vMerge")) if tc.tcPr is not None else None
            if vmerge_element is None:
                vertical_merge = None
            else:
                vertical_merge = vmerge_element.get(qn("w:val")) or "continue"
            paragraphs = [
                _docx_paragraph_node(
                    paragraph,
                    f"tbl-{table_index:04d}-r{row_index:03d}-c{column:03d}-p{p_index:03d}",
                    body_size,
                )
                for p_index, paragraph in enumerate(cell.paragraphs)
            ]
            cells.append({
                "source_anchor": f"tbl-{table_index:04d}-r{row_index:03d}-c{column:03d}",
                "start_column": column,
                "grid_span": grid_span,
                "vertical_merge": vertical_merge,
                "paragraphs": paragraphs,
            })
            column += grid_span
        max_columns = max(max_columns, column)
        rows.append({"row_index": row_index, "cells": cells})
    return _node(
        f"tbl-{table_index:04d}", "table", "", 0.96,
        columns=max_columns, rows=rows,
    )


def _style_directives(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0).strip() for match in STYLE_DIRECTIVE_RE.finditer(text)))


def _normalize_preface_semantics(nodes: list[dict[str, Any]]) -> None:
    if any(node["kind"] == "document-title" for node in nodes):
        return
    preface: list[dict[str, Any]] = []
    for node in nodes:
        if node["kind"] == "table":
            break
        if node.get("text", "").strip():
            preface.append(node)
        if len(preface) >= 8:
            break
    title = next((
        node for node in preface
        if re.search(r"(?:项目|课题|基金|计划).{0,20}(?:申请书|申报书|计划书)|(?:申请书|申报书|计划书)$", node.get("text", ""))
        and len(node.get("text", "").strip()) <= 100
    ), None)
    if title is None:
        return
    title["kind"] = "document-title"
    title["level"] = None
    title["confidence"] = max(float(title.get("confidence", 0.0)), 0.94)
    for node in preface:
        if node is title:
            break
        if re.fullmatch(r"附件\s*[0-9一二三四五六七八九十]+", node.get("text", "").strip()):
            node["kind"] = "instruction"
            node["level"] = None
            node["confidence"] = max(float(node.get("confidence", 0.0)), 0.96)


def _extract_docx(path: Path) -> dict[str, Any]:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    with zipfile.ZipFile(path) as package:
        parts = package.infolist()
        if any(part.file_size > 64 * 1024 * 1024 for part in parts):
            raise ValueError("E_SIZE_LIMIT: DOCX XML/package part exceeds 64 MB")
        if sum(part.file_size for part in parts) > 1024 * 1024 * 1024:
            raise ValueError("E_SIZE_LIMIT: expanded DOCX package exceeds 1 GB")
    document = Document(str(path))
    paragraphs = [Paragraph(child, document._body) for child in document.element.body.iterchildren() if child.tag.endswith("}p")]
    candidate_sizes: list[float] = []
    for paragraph in paragraphs:
        features = _paragraph_features(paragraph)
        if features["font_size"] and len(paragraph.text.strip()) >= 20:
            candidate_sizes.append(features["font_size"])
    body_size = median(candidate_sizes) if candidate_sizes else 12.0
    nodes: list[dict[str, Any]] = []
    paragraph_index = 0
    table_index = 0
    all_text: list[str] = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            paragraph = Paragraph(child, document._body)
            paragraph_index += 1
            node = _docx_paragraph_node(paragraph, f"p-{paragraph_index:04d}", body_size)
        elif child.tag.endswith("}tbl"):
            table_index += 1
            node = _table_node(Table(child, document._body), table_index, body_size)
        else:
            continue
        nodes.append(node)
        if node.get("text"):
            all_text.append(node["text"])
        if node["kind"] == "table":
            for row in node["rows"]:
                for cell in row["cells"]:
                    all_text.extend(p["text"] for p in cell["paragraphs"] if p["text"])

    _normalize_preface_semantics(nodes)
    confidences = [n["confidence"] for n in nodes if n["kind"] != "empty"]
    title_count = sum(n["kind"] == "document-title" for n in nodes)
    heading_count = sum(n["kind"] == "heading" for n in nodes)
    structural_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    if title_count == 0 and heading_count == 0:
        structural_confidence = min(structural_confidence, 0.72)
    text = "\n".join(all_text)
    return {
        "type": "semantic-document.v1",
        "metadata": {
            "source_path": str(path.resolve()),
            "source_format": ".docx",
            "title_count": title_count,
            "heading_count": heading_count,
            "table_count": table_index,
            "image_count": sum(len(n.get("images", [])) for n in nodes)
            + sum(len(p.get("images", [])) for n in nodes if n["kind"] == "table" for r in n["rows"] for c in r["cells"] for p in c["paragraphs"]),
        },
        "nodes": nodes,
        "style_directives": _style_directives(text),
        "preserved_elements": ["text-order", "heading-hierarchy", "table-topology", "checkbox-state", "official-images"],
        "semantic_structure_confidence": round(structural_confidence, 3),
        "question_batch": [],
    }


def _text_kind(line: str, index: int) -> tuple[str, int | None, float, str]:
    stripped = line.strip()
    markdown = re.match(r"^(#{1,6})\s+(.+)$", stripped)
    if markdown:
        level = min(len(markdown.group(1)), 3)
        return ("document-title" if index == 0 and level == 1 else "heading", None if index == 0 and level == 1 else level, 0.98, markdown.group(2).strip())
    kind, level, confidence = _paragraph_kind(stripped)
    if index == 0 and kind == "paragraph" and len(stripped) <= 80:
        return "document-title", None, 0.78, stripped
    return kind, level, confidence, stripped


def _tabular_text_rows(chunk: str) -> list[list[str]] | None:
    lines = [line.rstrip() for line in chunk.splitlines() if line.strip()]
    if len(lines) < 2 or not all("\t" in line for line in lines):
        return None
    rows = [[cell.strip() for cell in line.split("\t")] for line in lines]
    width = max(len(row) for row in rows)
    return [row + [""] * (width - len(row)) for row in rows]


def _text_table_node(rows: list[list[str]], table_index: int) -> dict[str, Any]:
    semantic_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        cells: list[dict[str, Any]] = []
        for column, value in enumerate(row):
            anchor = f"tbl-{table_index:04d}-r{row_index:03d}-c{column:03d}"
            paragraph = _node(f"{anchor}-p000", "paragraph", value, 0.94, level=None, images=[])
            cells.append({
                "source_anchor": anchor,
                "start_column": column,
                "grid_span": 1,
                "vertical_merge": None,
                "paragraphs": [paragraph],
            })
        semantic_rows.append({"row_index": row_index, "cells": cells})
    return _node(f"tbl-{table_index:04d}", "table", "", 0.96, columns=max(len(row) for row in rows), rows=semantic_rows)


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith("\|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    buffer: list[str] = []
    escaped = False
    for char in stripped:
        if escaped:
            buffer.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)
    if escaped:
        buffer.append("\\")
    cells.append("".join(buffer).strip())
    return cells


def _markdown_table_rows(lines: list[str]) -> list[list[str]] | None:
    clean_lines = [line.strip() for line in lines if line.strip()]
    if len(clean_lines) < 2 or not all("|" in line for line in clean_lines):
        return None
    rows: list[list[str]] = []
    for position, line in enumerate(clean_lines):
        row = _split_table_row(line)
        rows.append(row)
        if position == 1 and not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in row):
            return None
    width = max((len(row) for row in rows), default=0)
    if width == 0:
        return None
    return [row + [""] * (width - len(row)) for row in rows]


def _semantic_text_node(text: str, index: int) -> dict[str, Any]:
    markdown = re.match(r"^(#{1,6})\s+(.+)$", text.strip())
    if markdown:
        level = min(len(markdown.group(1)), 3)
        if index == 0 and level == 1:
            return _node(f"p-{index + 1:04d}", "document-title", markdown.group(2).strip(), 0.98, level=None, images=[])
        return _node(f"p-{index + 1:04d}", "heading", markdown.group(2).strip(), 0.98, level=level, images=[])
    kind, level, confidence, clean = _text_kind(text, index)
    return _node(f"p-{index + 1:04d}", kind, clean, confidence, level=level, images=[])


def _extract_text(path: Path) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8-sig", errors="replace")
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    nodes: list[dict[str, Any]] = []
    table_count = 0
    node_index = 0
    index = 0
    is_markdown = path.suffix.lower() == ".md"
    markdown_heading_re = re.compile(r"^#{1,6}\s+\S+")
    list_item_re = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+(.+)$")
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        stripped = line.strip()
        if is_markdown and markdown_heading_re.match(stripped):
            nodes.append(_semantic_text_node(stripped, node_index))
            node_index += 1
            index += 1
            continue
        if is_markdown and stripped.startswith("|") and index + 1 < len(lines):
            table_lines: list[str] = [stripped]
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip().startswith("|"):
                table_lines.append(lines[cursor].strip())
                cursor += 1
            rows = _markdown_table_rows(table_lines)
            if rows:
                table_count += 1
                nodes.append(_text_table_node(rows, table_count))
                node_index += 1
                index = cursor
                continue
        if not is_markdown and "\t" in line and index + 1 < len(lines):
            table_lines = [line.rstrip()]
            cursor = index + 1
            while cursor < len(lines) and "\t" in lines[cursor] and lines[cursor].strip():
                table_lines.append(lines[cursor].rstrip())
                cursor += 1
            rows = _tabular_text_rows("\n".join(table_lines))
            if rows:
                table_count += 1
                nodes.append(_text_table_node(rows, table_count))
                node_index += 1
                index = cursor
                continue
        if is_markdown:
            list_match = list_item_re.match(stripped)
            if list_match:
                nodes.append(_node(f"p-{node_index + 1:04d}", "list-item", list_match.group(1).strip(), 0.88, level=None, images=[]))
                node_index += 1
                index += 1
                continue
        buffer = [stripped]
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip():
            candidate = lines[cursor].strip()
            if is_markdown and (markdown_heading_re.match(candidate) or candidate.startswith("|") or list_item_re.match(candidate)):
                break
            if not is_markdown and "\t" in candidate:
                break
            buffer.append(candidate)
            cursor += 1
        nodes.append(_semantic_text_node("\n".join(buffer), node_index))
        node_index += 1
        index = cursor
    structural_confidence = sum(n["confidence"] for n in nodes) / len(nodes) if nodes else 0.0
    if not any(n["kind"] == "heading" for n in nodes):
        structural_confidence = min(structural_confidence, 0.72)
    return {
        "type": "semantic-document.v1",
        "metadata": {"source_path": str(path.resolve()), "source_format": path.suffix.lower(), "title_count": sum(n["kind"] == "document-title" for n in nodes), "heading_count": sum(n["kind"] == "heading" for n in nodes), "table_count": table_count, "image_count": 0},
        "nodes": nodes,
        "style_directives": _style_directives(text),
        "preserved_elements": ["text-order", "heading-hierarchy", "table-topology", "checkbox-state"],
        "semantic_structure_confidence": round(structural_confidence, 3),
        "question_batch": [],
    }

def _powershell_executable() -> str | None:
    candidates = [shutil.which("powershell.exe"), shutil.which("powershell"), shutil.which("pwsh")]
    if sys.platform == "win32":
        candidates.append(str(Path(Path(sys.executable).anchor) / "Windows" / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"))
    return next((value for value in candidates if value and Path(value).exists()), None)


def _valid_docx(path: Path) -> bool:
    if not path.exists() or not zipfile.is_zipfile(path):
        return False
    with zipfile.ZipFile(path) as package:
        return "word/document.xml" in package.namelist()


def _convert_doc_with_pywin32(
    path: Path,
    target: Path,
    timeout_seconds: int | float = DEFAULT_BACKEND_TIMEOUT_SECONDS,
) -> str:
    if sys.platform != "win32" or importlib.util.find_spec("win32com") is None:
        raise RuntimeError("pywin32 is unavailable")
    worker = r"""
import sys
import pythoncom
import win32com.client
source, destination = sys.argv[1], sys.argv[2]
pythoncom.CoInitialize()
word = None
document = None
try:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    word.AutomationSecurity = 3
    document = word.Documents.Open(source, ReadOnly=True, AddToRecentFiles=False)
    document.SaveAs2(destination, FileFormat=16)
    document.Close(False)
    document = None
finally:
    if document is not None:
        document.Close(False)
    if word is not None:
        word.Quit()
    pythoncom.CoUninitialize()
"""
    completed = run_bounded_process(
        [sys.executable, "-B", "-c", worker, str(path), str(target)],
        timeout_seconds=timeout_seconds,
        stage="recovery",
        backend="word-com-pywin32",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Word COM conversion failed: {completed.stderr[-500:]}")
    if not _valid_docx(target):
        raise RuntimeError("Word COM did not produce a valid DOCX")
    return "word-com-pywin32"


def _convert_doc_with_word_powershell(
    path: Path,
    target: Path,
    timeout_seconds: int | float = DEFAULT_BACKEND_TIMEOUT_SECONDS,
) -> str:
    executable = _powershell_executable()
    if sys.platform != "win32" or executable is None:
        raise RuntimeError("PowerShell Word automation is unavailable")
    script = target.parent / "convert-doc.ps1"
    script.write_text(
        """param([string]$InputPath, [string]$OutputPath)
$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $document = $word.Documents.Open($InputPath, $false, $true)
    $document.SaveAs2($OutputPath, 16)
    $document.Close($false)
    $document = $null
}
finally {
    if ($null -ne $document) { $document.Close($false) }
    if ($null -ne $word) { $word.Quit() }
}
""",
        encoding="utf-8",
    )
    completed = run_bounded_process(
        [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script), str(path), str(target)],
        timeout_seconds=timeout_seconds,
        stage="recovery",
        backend="word-com-powershell",
        text=False,
    )
    if completed.returncode != 0 or not _valid_docx(target):
        message = completed.stderr.decode(errors="replace")[-500:] if isinstance(completed.stderr, bytes) else str(completed.stderr)[-500:]
        raise RuntimeError(f"PowerShell Word conversion failed: {message}")
    return "word-com-powershell"


def _libreoffice_executable() -> str | None:
    candidates = [shutil.which("soffice"), shutil.which("libreoffice")]
    if sys.platform == "win32":
        candidates.extend([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ])
    return next((value for value in candidates if value and Path(value).exists()), None)


def _convert_doc_with_libreoffice(
    path: Path,
    target: Path,
    timeout_seconds: int | float = DEFAULT_BACKEND_TIMEOUT_SECONDS,
) -> str:
    executable = _libreoffice_executable()
    if executable is None:
        raise RuntimeError("LibreOffice is unavailable")
    completed = run_bounded_process(
        [executable, "--headless", "--convert-to", "docx", "--outdir", str(target.parent), str(path)],
        timeout_seconds=timeout_seconds,
        stage="recovery",
        backend="libreoffice-doc-conversion",
        text=False,
    )
    generated = target.parent / f"{path.stem}.docx"
    if generated.exists() and generated != target:
        generated.replace(target)
    if completed.returncode != 0 or not _valid_docx(target):
        raise RuntimeError("LibreOffice did not produce a valid DOCX")
    return "libreoffice-headless"


def _legacy_doc_to_docx(
    path: Path,
    target: Path,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    circuit_breakers: set[str] | None = None,
) -> str:
    errors: list[str] = []
    recovery_started = time.perf_counter()
    breakers = circuit_breakers if circuit_breakers is not None else set()
    converters = (
        ("word-com-pywin32", _convert_doc_with_pywin32),
        ("word-com-powershell", _convert_doc_with_word_powershell),
        ("libreoffice-doc-conversion", _convert_doc_with_libreoffice),
    )
    for backend, converter in converters:
        if backend in breakers:
            errors.append(f"{backend}: circuit open after an earlier timeout")
            continue
        elapsed_total = time.perf_counter() - recovery_started
        if elapsed_total >= DOC_RECOVERY_LIMIT_SECONDS:
            break
        timeout = bounded_timeout_seconds(
            budget,
            min(DEFAULT_BACKEND_TIMEOUT_SECONDS, DOC_RECOVERY_LIMIT_SECONDS - elapsed_total),
            stage="recovery",
            backend=backend,
        )
        started = time.perf_counter()
        try:
            parameters = inspect.signature(converter).parameters
            result = (
                converter(path, target, timeout_seconds=timeout)
                if "timeout_seconds" in parameters
                else converter(path, target)
            )
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            if attempts is not None:
                ended_epoch = time.time()
                attempts.append(
                    {
                        "backend": backend,
                        "stage": "recovery",
                        "path": str(path),
                        "status": "succeeded",
                        "started_at_epoch": round(ended_epoch - elapsed, 3),
                        "ended_at_epoch": round(ended_epoch, 3),
                        "elapsed_ms": round(elapsed * 1000, 2),
                        "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
                        "error_code": None,
                    }
                )
            return result
        except Exception as exc:
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            error_code = exc.code if isinstance(exc, AwesomeBenziError) else "E_DOC_RECOVERY_FAILED"
            if isinstance(exc, AwesomeBenziError) and exc.code == "E_TIMEOUT":
                breakers.add(backend)
            errors.append(f"{backend}: {exc}")
            if attempts is not None:
                ended_epoch = time.time()
                attempts.append(
                    {
                        "backend": backend,
                        "stage": "recovery",
                        "path": str(path),
                        "status": "timeout" if error_code == "E_TIMEOUT" else "failed",
                        "started_at_epoch": round(ended_epoch - elapsed, 3),
                        "ended_at_epoch": round(ended_epoch, 3),
                        "elapsed_ms": round(elapsed * 1000, 2),
                        "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
                        "error_code": error_code,
                    }
                )
            if target.exists():
                target.unlink()
    raise LegacyDocRecoveryRequired(
        path,
        "automatic legacy DOC recovery exhausted its local backends: " + " | ".join(errors),
        attempts,
        normalize_execution_budget(budget) if budget is not None else None,
    )


def _invoke_legacy_recovery(
    path: Path,
    target: Path,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    circuit_breakers: set[str] | None = None,
) -> str:
    parameters = inspect.signature(_legacy_doc_to_docx).parameters
    if "budget" not in parameters:
        return _legacy_doc_to_docx(path, target)
    return _legacy_doc_to_docx(
        path,
        target,
        budget=budget,
        attempts=attempts,
        circuit_breakers=circuit_breakers,
    )


def _record_backend_attempt(
    attempts: list[dict[str, Any]] | None,
    *,
    backend: str,
    stage: str,
    path: Path,
    status: str,
    elapsed_seconds: float,
    error_code: str | None = None,
    batch: str | None = None,
    budget: dict[str, Any] | None = None,
) -> None:
    if attempts is None:
        return
    ended_epoch = time.time()
    attempts.append(
        {
            "backend": backend,
            "stage": stage,
            "path": str(path),
            "status": status,
            "started_at_epoch": round(ended_epoch - elapsed_seconds, 3),
            "ended_at_epoch": round(ended_epoch, 3),
            "elapsed_ms": round(elapsed_seconds * 1000, 2),
            "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
            "error_code": error_code,
            "batch": batch,
        }
    )


def _render_pdf_pages(
    path: Path,
    output_dir: Path,
    page_count: int,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
) -> list[Path]:
    from .render import find_pdftoppm

    executable = find_pdftoppm()
    if executable is None:
        raise RuntimeError("pdftoppm is unavailable")
    pages: list[Path] = []
    for start_page in range(1, page_count + 1, OCR_BATCH_SIZE):
        end_page = min(page_count, start_page + OCR_BATCH_SIZE - 1)
        prefix = output_dir / f"ocr-{start_page:04d}"
        backend = "pdftoppm-ocr-render"
        started = time.perf_counter()
        try:
            completed = run_bounded_process(
                [
                    executable,
                    "-f",
                    str(start_page),
                    "-l",
                    str(end_page),
                    "-png",
                    "-r",
                    "180",
                    str(path),
                    str(prefix),
                ],
                timeout_seconds=bounded_timeout_seconds(
                    budget,
                    OCR_BATCH_TIMEOUT_SECONDS,
                    stage="ocr",
                    backend=backend,
                ),
                stage="ocr",
                backend=backend,
            )
        except AwesomeBenziError as exc:
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            _record_backend_attempt(
                attempts,
                backend=backend,
                stage="ocr",
                path=path,
                status="timeout",
                elapsed_seconds=elapsed,
                error_code=exc.code,
                batch=f"{start_page}-{end_page}",
                budget=budget,
            )
            raise
        elapsed = time.perf_counter() - started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        status = "succeeded" if completed.returncode == 0 else "failed"
        _record_backend_attempt(
            attempts,
            backend=backend,
            stage="ocr",
            path=path,
            status=status,
            elapsed_seconds=elapsed,
            error_code=None if status == "succeeded" else "E_OCR_FAILED",
            batch=f"{start_page}-{end_page}",
            budget=budget,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"PDF page rendering failed: {completed.stderr[-500:]}")
        pages.extend(sorted(output_dir.glob(f"{prefix.name}-*.png")))
    if len(pages) != page_count:
        raise RuntimeError(f"PDF page rendering produced {len(pages)} pages; expected {page_count}")
    return pages


def _tesseract_executable() -> str | None:
    candidates = [shutil.which("tesseract")]
    if sys.platform == "win32":
        candidates.extend([r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"])
    return next((value for value in candidates if value and Path(value).exists()), None)


def detect_runtime_capabilities() -> dict[str, Any]:
    from .render import render_capabilities

    renderers = render_capabilities()
    powershell = _powershell_executable()
    tesseract = _tesseract_executable()
    pywin32 = sys.platform == "win32" and importlib.util.find_spec("win32com") is not None
    return {
        "schema_type": "runtime-capabilities",
        "schema_version": 1,
        "word_com_pywin32": {
            "available": bool(pywin32),
            "status": "available" if pywin32 else "unavailable",
        },
        "word_com_powershell": {
            "available": bool(sys.platform == "win32" and powershell),
            "path": powershell,
            "status": "probe-on-use" if sys.platform == "win32" and powershell else "unavailable",
        },
        "libreoffice": renderers["libreoffice"],
        "pdftoppm": renderers["pdftoppm"],
        "tesseract": {"available": bool(tesseract), "path": tesseract},
        "windows_ocr": {
            "available": bool(sys.platform == "win32" and powershell),
            "status": "probe-on-use" if sys.platform == "win32" and powershell else "unavailable",
        },
        "platform_vision": {
            "available": None,
            "status": "agent-mediated",
        },
        "render_gate": renderers["render_gate"],
    }


def _ocr_images_with_tesseract(
    images: list[Path],
    source_path: Path | None = None,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
) -> str:
    executable = _tesseract_executable()
    if executable is None:
        raise RuntimeError("Tesseract is unavailable")
    probe_backend = "tesseract-language-probe"
    probe_started = time.perf_counter()
    try:
        language_probe = run_bounded_process(
            [executable, "--list-langs"],
            timeout_seconds=bounded_timeout_seconds(
                budget,
                10,
                stage="ocr",
                backend=probe_backend,
            ),
            stage="ocr",
            backend=probe_backend,
        )
    except AwesomeBenziError as exc:
        elapsed = time.perf_counter() - probe_started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        _record_backend_attempt(
            attempts,
            backend=probe_backend,
            stage="ocr",
            path=source_path or images[0],
            status="timeout",
            elapsed_seconds=elapsed,
            error_code=exc.code,
            batch="language-probe",
            budget=budget,
        )
        raise
    elapsed = time.perf_counter() - probe_started
    consume_execution_budget(budget, elapsed) if budget is not None else None
    _record_backend_attempt(
        attempts,
        backend=probe_backend,
        stage="ocr",
        path=source_path or images[0],
        status="succeeded" if language_probe.returncode == 0 else "failed",
        elapsed_seconds=elapsed,
        error_code=None if language_probe.returncode == 0 else "E_OCR_FAILED",
        batch="language-probe",
        budget=budget,
    )
    if language_probe.returncode != 0:
        raise RuntimeError("Tesseract language probe failed")
    languages = language_probe.stdout.splitlines()
    available = {item.strip() for item in languages if item.strip() and "available languages" not in item}
    selected = "+".join(language for language in ("chi_sim", "eng") if language in available)
    if not selected:
        raise RuntimeError("Tesseract has no Chinese or English language data")
    pages: list[str] = []
    for batch_index, start in enumerate(range(0, len(images), OCR_BATCH_SIZE), start=1):
        batch = images[start:start + OCR_BATCH_SIZE]
        list_path = batch[0].parent / f"tesseract-batch-{batch_index:03d}.txt"
        list_path.write_text("\n".join(str(image) for image in batch), encoding="utf-8")
        backend = "tesseract"
        started = time.perf_counter()
        try:
            result = run_bounded_process(
                [executable, str(list_path), "stdout", "-l", selected, "--psm", "6"],
                timeout_seconds=bounded_timeout_seconds(
                    budget,
                    OCR_BATCH_TIMEOUT_SECONDS,
                    stage="ocr",
                    backend=backend,
                ),
                stage="ocr",
                backend=backend,
            )
        except AwesomeBenziError as exc:
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            _record_backend_attempt(
                attempts,
                backend=backend,
                stage="ocr",
                path=source_path or batch[0],
                status="timeout",
                elapsed_seconds=elapsed,
                error_code=exc.code,
                batch=f"{start + 1}-{start + len(batch)}",
                budget=budget,
            )
            raise
        elapsed = time.perf_counter() - started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        _record_backend_attempt(
            attempts,
            backend=backend,
            stage="ocr",
            path=source_path or batch[0],
            status="succeeded" if result.returncode == 0 else "failed",
            elapsed_seconds=elapsed,
            error_code=None if result.returncode == 0 else "E_OCR_FAILED",
            batch=f"{start + 1}-{start + len(batch)}",
            budget=budget,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Tesseract failed on pages {start + 1}-{start + len(batch)}")
        pages.append(result.stdout.strip())
    return "\n\n".join(pages)


def _ocr_images_with_windows(
    images: list[Path],
    work_dir: Path,
    source_path: Path | None = None,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
) -> str:
    executable = _powershell_executable()
    if sys.platform != "win32" or executable is None:
        raise RuntimeError("Windows OCR is unavailable")
    script = work_dir / "windows-ocr.ps1"
    script.write_text(
        """param([string]$ImageListPath, [string]$OutputPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.FileAccessMode, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
function Await-Result($Operation, [Type]$ResultType) {
    $method = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
        Select-Object -First 1
    $task = $method.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($null -eq $engine) { throw 'No Windows OCR language is available' }
$builder = New-Object System.Text.StringBuilder
foreach ($imagePath in [System.IO.File]::ReadAllLines($ImageListPath)) {
    $file = Await-Result ([Windows.Storage.StorageFile]::GetFileFromPathAsync($imagePath)) ([Windows.Storage.StorageFile])
    $stream = Await-Result ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await-Result ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await-Result ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result = Await-Result ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    foreach ($line in $result.Lines) {
        [void]$builder.AppendLine($line.Text)
    }
    [void]$builder.AppendLine()
    $bitmap.Dispose()
    $stream.Dispose()
}
[System.IO.File]::WriteAllText($OutputPath, $builder.ToString(), (New-Object System.Text.UTF8Encoding($false)))
""",
        encoding="utf-8",
    )
    pages: list[str] = []
    for batch_index, start in enumerate(range(0, len(images), OCR_BATCH_SIZE), start=1):
        batch = images[start:start + OCR_BATCH_SIZE]
        image_list = work_dir / f"windows-ocr-images-{batch_index:03d}.txt"
        image_list.write_text("\n".join(str(path) for path in batch), encoding="utf-8")
        output = work_dir / f"windows-ocr-output-{batch_index:03d}.txt"
        backend = "windows-ocr"
        started = time.perf_counter()
        try:
            completed = run_bounded_process(
                [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script), str(image_list), str(output)],
                timeout_seconds=bounded_timeout_seconds(
                    budget,
                    OCR_BATCH_TIMEOUT_SECONDS,
                    stage="ocr",
                    backend=backend,
                ),
                stage="ocr",
                backend=backend,
                text=False,
            )
        except AwesomeBenziError as exc:
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            _record_backend_attempt(
                attempts,
                backend=backend,
                stage="ocr",
                path=source_path or batch[0],
                status="timeout",
                elapsed_seconds=elapsed,
                error_code=exc.code,
                batch=f"{start + 1}-{start + len(batch)}",
                budget=budget,
            )
            raise
        elapsed = time.perf_counter() - started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        success = completed.returncode == 0 and output.exists()
        _record_backend_attempt(
            attempts,
            backend=backend,
            stage="ocr",
            path=source_path or batch[0],
            status="succeeded" if success else "failed",
            elapsed_seconds=elapsed,
            error_code=None if success else "E_OCR_FAILED",
            batch=f"{start + 1}-{start + len(batch)}",
            budget=budget,
        )
        if not success:
            message = completed.stderr.decode(errors="replace")[-500:] if isinstance(completed.stderr, bytes) else str(completed.stderr)[-500:]
            raise RuntimeError(f"Windows OCR failed: {message}")
        pages.append(output.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(pages)


def _normalize_ocr_text(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = re.sub(r"(?<=[\u3400-\u9fff])[ \t]+(?=[\u3400-\u9fff])", "", raw_line)
        line = re.sub(r"[ \t]+([，。；、！？）】])", r"\1", line)
        line = re.sub(r"([（【])[ \t]+", r"\1", line)
        heading_candidate = re.sub(r"^[、，。．·•\s]+", "", line)
        if KNOWN_HEADINGS.fullmatch(heading_candidate):
            line = heading_candidate
        lines.append(line.strip())
    return "\n".join(lines).strip()


def _ocr_scanned_pdf(
    path: Path,
    page_count: int | None = None,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    circuit_breakers: set[str] | None = None,
) -> tuple[str, str, int]:
    errors: list[str] = []
    breakers = circuit_breakers if circuit_breakers is not None else set()
    if page_count is None:
        try:
            from pypdf import PdfReader

            page_count = len(PdfReader(str(path)).pages)
        except Exception as exc:
            raise VisionOcrRequired(
                path,
                f"could not determine scanned PDF page count: {exc}",
                attempts,
                normalize_execution_budget(budget) if budget is not None else None,
            ) from exc
    if page_count > OCR_PAGE_LIMIT:
        raise VisionOcrRequired(
            path,
            f"scanned PDF has {page_count} pages; local OCR is capped at {OCR_PAGE_LIMIT} pages and must use platform vision or a narrowed input",
            attempts,
            normalize_execution_budget(budget) if budget is not None else None,
        )
    with tempfile.TemporaryDirectory(prefix="awesome-benzi-ocr-") as raw:
        work_dir = Path(raw)
        try:
            images = _render_pdf_pages(path, work_dir, page_count, budget, attempts)
        except Exception as exc:
            raise VisionOcrRequired(
                path,
                f"local PDF rendering for OCR failed: {exc}",
                attempts,
                normalize_execution_budget(budget) if budget is not None else None,
            ) from exc
        recognizers = (
            ("tesseract", lambda: _ocr_images_with_tesseract(images, path, budget, attempts)),
            ("windows-ocr", lambda: _ocr_images_with_windows(images, work_dir, path, budget, attempts)),
        )
        for backend, recognizer in recognizers:
            if backend in breakers:
                errors.append(f"{backend}: circuit open after an earlier timeout")
                continue
            try:
                text = _normalize_ocr_text(recognizer())
                if len(re.sub(r"\s+", "", text)) >= 30:
                    return text, backend, len(images)
                errors.append(f"{backend}: OCR returned too little text")
            except Exception as exc:
                if isinstance(exc, AwesomeBenziError) and exc.code == "E_TIMEOUT":
                    breakers.add(backend)
                errors.append(f"{backend}: {exc}")
    raise VisionOcrRequired(
        path,
        "local OCR backends were unavailable or inconclusive: " + " | ".join(errors),
        attempts,
        normalize_execution_budget(budget) if budget is not None else None,
    )


def _pdf_text_nodes(text: str, confidence_cap: float = 0.82) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    paragraph_index = 0
    for page_index, page_text in enumerate(re.split(r"\f|\n\s*---\s*PAGE\s*---\s*\n", text, flags=re.I)):
        for line in (item.strip() for item in page_text.splitlines() if item.strip()):
            kind, level, confidence, clean = _text_kind(line, paragraph_index)
            paragraph_index += 1
            nodes.append(_node(f"pdf-p{page_index + 1:03d}-{paragraph_index:04d}", kind, clean, min(confidence, confidence_cap), level=level, images=[]))
    return nodes


def _extract_pdf(
    path: Path,
    recovered_text: str | None = None,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    circuit_breakers: set[str] | None = None,
) -> dict[str, Any]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise InternalRecoveryRequired("pdfplumber is required for PDF semantic extraction") from exc

    native_nodes: list[dict[str, Any]] = []
    all_text: list[str] = []
    image_nodes: list[dict[str, Any]] = []
    table_count = 0
    paragraph_index = 0
    with pdfplumber.open(str(path)) as pdf:
        page_count = len(pdf.pages)
        if page_count > 500:
            raise ValueError("E_SIZE_LIMIT: PDF exceeds 500 pages")
        if recovered_text is None and page_count > OCR_PAGE_LIMIT:
            sample_text = "\n".join(
                (pdf.pages[index].extract_text(layout=True) or "")
                for index in range(min(2, page_count))
            )
            if len(re.sub(r"\s+", "", sample_text)) < 100:
                raise VisionOcrRequired(
                    path,
                    f"scanned PDF has {page_count} pages; local OCR is capped at {OCR_PAGE_LIMIT} pages",
                )
        last_tick = time.perf_counter()
        for page_index, page in enumerate(pdf.pages):
            if budget is not None and remaining_budget_seconds(budget) <= 0:
                raise AwesomeBenziError(
                    "E_TIMEOUT",
                    "extract",
                    "execution budget was exhausted while parsing PDF pages",
                    path=str(path),
                    recoverability="environment",
                    details={"page": page_index + 1, "page_count": page_count},
                )
            page_text = page.extract_text(layout=True) or ""
            all_text.append(page_text)
            for line in (item.strip() for item in page_text.splitlines() if item.strip()):
                kind, level, confidence, clean = _text_kind(line, paragraph_index)
                paragraph_index += 1
                native_nodes.append(_node(
                    f"pdf-p{page_index + 1:03d}-{paragraph_index:04d}", kind, clean,
                    min(confidence, 0.82), level=level, images=[],
                ))
            for table in page.extract_tables() or []:
                table_count += 1
                rows = []
                columns = max((len(row or []) for row in table), default=0)
                for row_index, raw_row in enumerate(table):
                    cells = []
                    for column, value in enumerate(raw_row or []):
                        text_value = (value or "").strip()
                        paragraph = _node(f"pdf-t{table_count:03d}-r{row_index:03d}-c{column:03d}-p000", "paragraph", text_value, 0.72, level=None, images=[])
                        cells.append({"source_anchor": f"pdf-t{table_count:03d}-r{row_index:03d}-c{column:03d}", "start_column": column, "grid_span": 1, "vertical_merge": None, "paragraphs": [paragraph]})
                    rows.append({"row_index": row_index, "cells": cells})
                native_nodes.append(_node(f"pdf-t{table_count:03d}", "table", "", 0.7, columns=columns, rows=rows))
            page_area = max(float(page.width) * float(page.height), 1.0)
            for image_index, image in enumerate(page.images or []):
                width = max(float(image.get("x1", 0)) - float(image.get("x0", 0)), 0.0)
                height = max(float(image.get("bottom", 0)) - float(image.get("top", 0)), 0.0)
                if width * height / page_area >= 0.7:
                    continue
                image_nodes.append(_node(
                    f"pdf-img-{page_index + 1:03d}-{image_index:03d}", "image", "", 0.68,
                    images=[{"image_ref": f"pdf:{page_index}:{image_index}", "bbox": [image.get("x0"), image.get("top"), image.get("x1"), image.get("bottom")]}],
                ))
            if budget is not None:
                current_tick = time.perf_counter()
                consume_execution_budget(budget, current_tick - last_tick)
                last_tick = current_tick
    native_text = "\n".join(all_text)
    if len(re.sub(r"\s+", "", native_text)) >= 100:
        text = native_text
        nodes = native_nodes + image_nodes
        recovery = {"status": "native-text", "backend": None, "pages": page_count}
    else:
        if recovered_text is not None and len(re.sub(r"\s+", "", recovered_text)) >= 30:
            text, backend, pages = recovered_text, "platform-vision", page_count
        else:
            text, backend, pages = _ocr_scanned_pdf(
                path,
                page_count,
                budget,
                attempts,
                circuit_breakers,
            )
        nodes = _pdf_text_nodes(text, 0.86) + image_nodes
        table_count = 0
        recovery = {"status": "recovered", "backend": backend, "pages": pages}
    confidences = [n["confidence"] for n in nodes if n["kind"] not in {"empty", "image"}]
    structural_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    if not any(n["kind"] in {"document-title", "heading"} for n in nodes):
        structural_confidence = min(structural_confidence, 0.76 if recovery["status"] == "recovered" else 0.72)
    return {
        "type": "semantic-document.v1",
        "metadata": {
            "source_path": str(path.resolve()), "source_format": ".pdf",
            "title_count": sum(n["kind"] == "document-title" for n in nodes),
            "heading_count": sum(n["kind"] == "heading" for n in nodes),
            "table_count": table_count, "image_count": len(image_nodes),
            "input_recovery": recovery,
        },
        "nodes": nodes,
        "style_directives": _style_directives(text),
        "preserved_elements": ["text-order", "heading-hierarchy", "table-topology", "checkbox-state", "official-images"],
        "semantic_structure_confidence": round(structural_confidence, 3),
        "question_batch": [],
    }


def extract_structure(
    path: Path,
    recovered_text: str | None = None,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    circuit_breakers: set[str] | None = None,
) -> dict[str, Any]:
    path = _assert_user_material_path(path)
    if not path.is_file():
        raise AwesomeBenziError(
            "E_PATH_NOT_FOUND",
            "extract",
            f"template path is not a file: {path}",
            path=str(path),
            recoverability="user-input",
            user_action_required=True,
        )
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise AwesomeBenziError(
            "E_UNSUPPORTED_FORMAT",
            "extract",
            f"unsupported semantic rebuild source: {suffix}",
            path=str(path),
            recoverability="user-input",
            user_action_required=True,
            suggested_action="Convert the file to DOC, DOCX, PDF, Markdown or plain text outside the Skill package.",
        )
    _check_source_signature(path)
    if suffix == ".docx":
        result = _extract_docx(path)
    elif suffix in {".md", ".txt"}:
        result = _extract_text(path)
    elif suffix == ".pdf":
        result = _extract_pdf(path, recovered_text, budget, attempts, circuit_breakers)
    else:
        with tempfile.TemporaryDirectory(prefix="awesome-benzi-doc-") as raw:
            converted = Path(raw) / f"{path.stem}.docx"
            backend = _invoke_legacy_recovery(path, converted, budget, attempts, circuit_breakers)
            result = _extract_docx(converted)
            result["metadata"]["source_path"] = str(path)
            result["metadata"]["source_format"] = ".doc"
            result["metadata"]["input_recovery"] = {"status": "recovered", "backend": backend}
    result.setdefault("schema_type", "semantic-document")
    result.setdefault("schema_version", 1)
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _semantic_text(structure: dict[str, Any]) -> str:
    values: list[str] = []
    for node in structure.get("nodes", []):
        if node.get("kind") == "table":
            for row in node.get("rows", []):
                for cell in row.get("cells", []):
                    values.extend(part.get("text", "") for part in cell.get("paragraphs", []))
        else:
            values.append(node.get("text", ""))
    return "\n".join(value.strip() for value in values if value and value.strip())


def _cleanup_stale_sessions(max_age_seconds: int = 86_400) -> int:
    return cleanup_expired_sessions(max_age_seconds)


CRITICAL_SECTION_RULES = (
    ("core-problem", re.compile(r"选题|立项|背景|项目概述"), "核心问题、研究对象与适用边界"),
    ("research-scope", re.compile(r"研究内容|研究目标|任务"), "研究对象、地域、时间范围和核心任务"),
    ("method-data", re.compile(r"研究方法|思路方法|技术路线|实验设计"), "材料或数据来源、样本范围、方法和具体操作"),
    ("foundation-team", re.compile(r"研究基础|前期基础|团队|条件"), "已有成果、团队分工和可用资源"),
    ("expected-results", re.compile(r"预期成果|成果形式|应用价值"), "成果类型、数量边界、使用对象和形成路径"),
    ("feasibility", re.compile(r"可行性|进度|风险|实施"), "实施周期、关键条件和风险控制"),
)

SECTION_ARGUMENT_TASKS = (
    (re.compile(r"选题|立项|背景|依据|现状|综述"), ["界定问题与边界", "综合证据与分歧", "推导研究缺口与切口"]),
    (re.compile(r"研究内容|研究目标|主要任务"), ["说明总体框架", "分解子问题", "建立任务关系", "落实研究路径"]),
    (re.compile(r"研究方法|思路方法|技术路线|实验设计"), ["说明选择理由", "界定材料与样本", "落实操作与分析", "安排验证与输出"]),
    (re.compile(r"创新"), ["对应既有边界", "说明实现载体", "检验不可替代性"]),
    (re.compile(r"预期成果|成果形式|应用价值"), ["对应研究任务", "界定成果内容", "说明使用对象与条件"]),
    (re.compile(r"研究基础|前期基础|团队|条件"), ["筛选相关积累", "对应任务能力", "说明资源与分工"]),
    (re.compile(r"可行性|进度|风险|实施"), ["核实实施条件", "安排阶段任务", "识别风险与控制"]),
)
SHORT_SECTION = re.compile(r"摘要|关键词|基本信息|申请人信息|经费|预算|签字|承诺|推荐意见")
DESIGN_INSTRUCTION = re.compile(r"不要|不能|避免|需要|应当|必须|只(?:用|做|保留|写)|采用|使用|增加|补充|删除|修改|强调|突出|围绕|聚焦|保持")


def _section_has_body(nodes: list[dict[str, Any]], heading_index: int) -> bool:
    heading = nodes[heading_index]
    current_level = int(heading.get("level") or 1)
    for node in nodes[heading_index + 1:]:
        if node.get("kind") == "heading":
            if int(node.get("level") or 1) <= current_level:
                break
            return True
        if node.get("kind") == "table":
            if any(part.get("text", "").strip() for row in node.get("rows", []) for cell in row.get("cells", []) for part in cell.get("paragraphs", [])):
                return True
            continue
        text = node.get("text", "").strip()
        if text and node.get("kind") not in {"empty", "placeholder", "instruction"} and not PLACEHOLDER_RE.search(text):
            return True
    return False


def _initial_writing_ledger(structure: dict[str, Any], support_text: str, prompt: str) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = structure.get("nodes", [])
    # The task prompt controls the work but is not project evidence. Mixing it
    # into this context can both hide genuine fact gaps and leak user wording
    # into the proposal body.
    context = f"{_semantic_text(structure)}\n{support_text}"
    sections: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    seen_gap_kinds: set[str] = set()
    for index, node in enumerate(nodes):
        if node.get("kind") != "heading":
            continue
        heading = node.get("text", "").strip()
        source_present = _section_has_body(nodes, index)
        argument_tasks = next((list(tasks) for pattern, tasks in SECTION_ARGUMENT_TASKS if pattern.search(heading)), [])
        exempt_from_internal_structure = bool(SHORT_SECTION.search(heading))
        section = {
            "section_id": node.get("source_anchor", f"section-{index:04d}"),
            "heading": heading,
            "argument_task": f"完成“{heading}”栏目规定的实质论证",
            "argument_tasks": argument_tasks,
            "word_budget": None,
            "facts": [], "evidence": [], "methods": [], "missing_items": [],
            "argument_tree": {
                "central_thesis": "", "subproblems": [], "facts": [], "evidence": [],
                "mechanisms": [], "methods": [], "boundary": "", "conclusion": "", "units": [],
            },
            "exempt_from_internal_structure": exempt_from_internal_structure,
            "requires_internal_structure": False,
            "modified": False,
            "status": "source-present" if source_present else "pending",
        }
        for kind, pattern, request in CRITICAL_SECTION_RULES:
            if not pattern.search(heading) or kind in seen_gap_kinds:
                continue
            contextual_support = len(re.sub(r"\s+", "", context)) >= 120 and bool(pattern.search(context))
            if not source_present and not contextual_support:
                gap = {
                    "class": "B", "kind": "content-critical-fact", "gap_id": kind,
                    "section_id": section["section_id"], "name": request,
                    "message": f"请一次性补充{request}；未提供部分将在成稿中以红色占位标明。",
                }
                gaps.append(gap)
                section["missing_items"].append(kind)
                seen_gap_kinds.add(kind)
        sections.append(section)

    for match in re.finditer(r"【\s*待补\s*[：:]\s*([^】]{1,100})】", _semantic_text(structure)):
        label = match.group(1).strip()
        if not any(keyword in label for keyword in ("对象", "范围", "时间", "样本", "数据", "方法", "成果", "团队", "基础", "资源", "项目名称")):
            continue
        gap_id = f"placeholder-{hashlib.sha1(label.encode('utf-8')).hexdigest()[:10]}"
        if gap_id in seen_gap_kinds:
            continue
        gaps.append({
            "class": "B", "kind": "content-critical-fact", "gap_id": gap_id,
            "section_id": None, "name": label,
            "message": f"请一次性补充{label}；未提供时保留红色占位。",
        })
        seen_gap_kinds.add(gap_id)

    section_headings = [str(item.get("heading", "")) for item in sections]
    required_module_ids = {
        int(module_id[1:])
        for module_id in _ledger_required_modules(prompt, section_headings)
    }
    required_modules = required_module_ids or set(range(1, 11))
    ledger = {
        "schema_type": "writing-ledger", "schema_version": 1,
        "type": "writing-ledger.v1",
        "sections": sections,
        "modules": [
            {"module": index, "required": index in required_modules, "status": "pending" if index in required_modules else "not-required"}
            for index in range(1, 11)
        ],
        "instruction_translation": {
            "required": bool(DESIGN_INSTRUCTION.search(prompt)),
            "status": "pending" if DESIGN_INSTRUCTION.search(prompt) else "not-required",
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest() if prompt else None,
            "decisions": [],
        },
        "review": {"status": "pending", "dimensions": {}},
        "m10_targeted_revision_count": 0,
        "m10_affected_modules": [],
        "gaps": gaps,
        "display_to_user": False,
    }
    question_batch = {
        "schema_type": "question-batch", "schema_version": 1,
        "type": "question-batch.v1", "needed": bool(gaps), "ask_once": True,
        "groups": {"A_route_or_template_blockers": [], "B_required_facts": gaps, "C_preferences": []},
        "answer_template": {item["gap_id"]: "" for item in gaps},
    }
    return integrate_method_modules(ledger, prompt), question_batch


def prepare_session(
    template: Path,
    support_paths: list[Path] | None = None,
    prompt: str = "",
    recovered_text: str | None = None,
    budget_seconds: int | float = 300,
) -> dict[str, Any]:
    started = time.perf_counter()
    _cleanup_stale_sessions()
    template = _assert_user_material_path(template)
    if not template.exists() or not template.is_file():
        raise FileNotFoundError(template)
    if template.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("E_SIZE_LIMIT: template exceeds 100 MB")
    budget = new_execution_budget(budget_seconds)
    capabilities = detect_runtime_capabilities()
    backend_attempts: list[dict[str, Any]] = []
    recovery_checkpoints: list[dict[str, Any]] = []
    circuit_breakers: set[str] = set()
    session_dir = create_session(prompt, budget_seconds=budget_seconds)
    transition(session_dir, SessionState.SCANNED)
    semantic_source = template
    conversions = 0
    ocr_recoveries = 0
    support_results: list[dict[str, Any]] = []
    try:
        template_hash = _sha256(template)
        if template.suffix.lower() == ".doc":
            semantic_source = session_dir / "source" / "recovered-template.docx"
            backend = _invoke_legacy_recovery(
                template,
                semantic_source,
                budget,
                backend_attempts,
                circuit_breakers,
            )
            conversions += 1
            structure = _extract_docx(semantic_source)
            structure["metadata"].update({
                "source_path": str(template), "source_format": ".doc",
                "input_recovery": {"status": "recovered", "backend": backend},
            })
        else:
            structure = extract_structure(
                template,
                recovered_text,
                budget,
                backend_attempts,
                circuit_breakers,
            )
            backend = structure.get("metadata", {}).get("input_recovery", {}).get("backend")
        structure.setdefault("schema_type", "semantic-document")
        structure.setdefault("schema_version", 1)
        primary_cache = session_dir / "source" / f"{template_hash}.semantic.json"
        primary_cache.write_text(json.dumps(structure, ensure_ascii=False), encoding="utf-8")
        recovery_checkpoints.append(
            {
                "path": str(template),
                "fingerprint": template_hash,
                "status": "recovered" if backend else "extracted",
                "backend": backend,
                "cache_path": str(primary_cache),
            }
        )
        transition(session_dir, SessionState.ROUTED)
        if structure.get("metadata", {}).get("input_recovery", {}).get("status") == "recovered" and template.suffix.lower() == ".pdf":
            ocr_recoveries += 1

        support_texts: list[str] = []
        style_texts: list[str] = []
        support_material_issues: list[dict[str, Any]] = []
        if len(support_paths or []) + 1 > 500:
            raise ValueError("E_FILE_LIMIT: prepared session exceeds 500 input files")
        total_input_bytes = template.stat().st_size
        for raw_path in support_paths or []:
            try:
                path = _assert_user_material_path(raw_path)
            except AwesomeBenziError as exc:
                support_results.append({"path": str(raw_path), "status": exc.code == "E_PATH_NOT_FOUND" and "not-found" or "blocked", "error_code": exc.code, "error": str(exc)})
                support_material_issues.append({"class": "D", "kind": "support-material-unavailable", "path": str(raw_path), "error_code": exc.code, "message": str(exc)})
                continue
            if path == template:
                continue
            if path.suffix.lower() not in SUPPORTED:
                support_results.append({"path": str(path), "status": "unsupported", "error_code": "E_UNSUPPORTED_FORMAT", "error": f"unsupported support format: {path.suffix}"})
                support_material_issues.append({"class": "D", "kind": "unsupported-support-format", "path": str(path), "error_code": "E_UNSUPPORTED_FORMAT", "message": f"unsupported support format: {path.suffix}; convert to DOC/DOCX/PDF/MD/TXT or remove it from the support list"})
                continue
            support_size = path.stat().st_size
            if support_size > 100 * 1024 * 1024:
                support_results.append({"path": str(path), "status": "blocked", "error": "E_SIZE_LIMIT: support file exceeds 100 MB"})
                continue
            if total_input_bytes + support_size > 1024 * 1024 * 1024:
                raise ValueError("E_SIZE_LIMIT: prepared-session inputs exceed 1 GB")
            total_input_bytes += support_size
            try:
                fingerprint = _sha256(path)
                cache_path = session_dir / "source" / f"{fingerprint}.semantic.json"
                if cache_path.is_file():
                    support_structure = json.loads(cache_path.read_text(encoding="utf-8"))
                    checkpoint_status = "cached"
                else:
                    support_structure = extract_structure(
                        path,
                        budget=budget,
                        attempts=backend_attempts,
                        circuit_breakers=circuit_breakers,
                    )
                    cache_path.write_text(json.dumps(support_structure, ensure_ascii=False), encoding="utf-8")
                    checkpoint_status = "extracted"
                text = _semantic_text(support_structure)
                combined_name = f"{path.name} {text[:300]}"
                if re.search(r"写作样稿|语言样本|语气样本|个人文风|文风|voice sample|style sample|样稿", combined_name, re.I):
                    style_texts.append(text)
                    support_results.append({"path": str(path), "status": "style-sample", "characters": len(text)})
                else:
                    support_texts.append(text)
                    support_results.append({"path": str(path), "status": checkpoint_status, "characters": len(text)})
                recovery_checkpoints.append(
                    {
                        "path": str(path),
                        "fingerprint": fingerprint,
                        "status": checkpoint_status,
                        "backend": support_structure.get("metadata", {}).get("input_recovery", {}).get("backend"),
                        "cache_path": str(cache_path),
                    }
                )
                if support_structure.get("metadata", {}).get("input_recovery", {}).get("status") == "recovered":
                    if path.suffix.lower() == ".doc":
                        conversions += 1
                    elif path.suffix.lower() == ".pdf":
                        ocr_recoveries += 1
            except Exception as exc:
                support_results.append({"path": str(path), "status": "unreadable", "error": str(exc)})
                recovery_checkpoints.append(
                    {
                        "path": str(path),
                        "fingerprint": _sha256(path),
                        "status": "failed",
                        "backend": None,
                        "error_code": exc.code if isinstance(exc, AwesomeBenziError) else "E_EXTRACT_FAILED",
                    }
                )
                if isinstance(exc, AwesomeBenziError) and exc.code == "E_TIMEOUT":
                    break

        ledger, question_batch = _initial_writing_ledger(structure, "\n".join(support_texts), prompt)
        if support_material_issues:
            question_batch["groups"]["D_support_material_issues"] = support_material_issues
            question_batch["needed"] = True
        style_profile = extract_style_profile(style_texts, prompt, [str(item.get("heading", "")) for item in ledger.get("sections", [])])
        style_brief = render_style_brief(style_profile)
        ledger["style_brief"] = style_brief
        schema_dir = session_dir / "schema"
        structure_path = schema_dir / "template-schema.json"
        ledger_path = schema_dir / "writing-ledger.json"
        structure_path.write_text(json.dumps(structure, ensure_ascii=False), encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
        (schema_dir / "style-profile.json").write_text(
            json.dumps(style_profile, ensure_ascii=False), encoding="utf-8",
        )
        (schema_dir / "fact-ledger.json").write_text(
            json.dumps({"schema_type": "fact-ledger", "schema_version": 1, "facts": []}, ensure_ascii=False),
            encoding="utf-8",
        )
        (schema_dir / "evidence-ledger.json").write_text(
            json.dumps({"schema_type": "evidence-ledger", "schema_version": 1, "evidence": []}, ensure_ascii=False),
            encoding="utf-8",
        )
        (schema_dir / "writing-plan.json").write_text(
            json.dumps(
                {
                    "schema_type": "writing-plan",
                    "schema_version": 1,
                    "sections": ledger.get("sections", []),
                    "method_modules": ledger.get("method_modules", []),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        budget = normalize_execution_budget(budget, budget_seconds)
        budget["consumed_ms"] = round(min(budget["limit_ms"], max(budget["consumed_ms"], elapsed_ms)), 2)
        budget["remaining_ms"] = round(max(0.0, budget["limit_ms"] - budget["consumed_ms"]), 2)
        manifest = {
            "schema_type": "prepared-session", "schema_version": 1,
            "type": "prepared-session.v1", "session_dir": str(session_dir),
            "source_template_path": str(template), "source_format": template.suffix.lower(),
            "source_hash": template_hash, "semantic_source_path": str(semantic_source),
            "semantic_structure_path": str(structure_path), "writing_ledger_path": str(ledger_path),
            "question_batch": question_batch, "support_results": support_results,
            "task_prompt": prompt,
            "capabilities": capabilities,
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
            "execution_budget": budget,
            "backend_attempts": backend_attempts,
            "recovery_checkpoints": recovery_checkpoints,
            "reasoning_plan": ledger.get("reasoning_plan"),
            "verification_summary": ledger.get("verification_summary"),
            "style_profile": style_profile,
            "style_brief": style_brief,
            "style_sample_count": len(style_texts),
            "extraction_stats": {
                "primary_semantic_extractions": 1,
                "support_semantic_extractions": sum(item["status"] in {"extracted", "cached"} for item in support_results),
                "legacy_doc_conversions": conversions, "pdf_ocr_recoveries": ocr_recoveries,
            },
            "performance": {"prepare_ms": elapsed_ms},
        }
        manifest_path = session_dir / "manifest.json"
        manifest["manifest_path"] = str(manifest_path)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        transition(
            session_dir,
            SessionState.PREPARED,
            prepared_manifest_path=str(manifest_path),
            execution_budget=budget,
            capabilities=capabilities,
        )
        return manifest
    except Exception:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise


def main(argv: Iterable[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    extract_parser = sub.add_parser("extract")
    extract_parser.add_argument("--template", required=True)
    extract_parser.add_argument("--recovered-text", help="UTF-8 OCR text created in an operating-system temporary directory")
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--template", required=True)
    prepare_parser.add_argument("--support", action="append", default=[])
    prepare_parser.add_argument("--prompt", default="")
    prepare_parser.add_argument("--recovered-text", help="UTF-8 OCR text created in an operating-system temporary directory")
    prepare_parser.add_argument("--budget-seconds", type=float, default=300)
    args = parser.parse_args(argv)
    try:
        recovered_text = Path(args.recovered_text).read_text(encoding="utf-8-sig") if args.recovered_text else None
        if args.command == "prepare":
            result = prepare_session(
                Path(args.template),
                [Path(item) for item in args.support],
                args.prompt,
                recovered_text,
                args.budget_seconds,
            )
        else:
            result = extract_structure(Path(args.template), recovered_text)
        code = 0
    except VisionOcrRequired as exc:
        result = {
            "type": "internal-input-recovery.v1", "status": "requires-internal-vision-ocr",
            "error": str(exc), "action": exc.action, "question_batch": [],
            "backend_attempts": exc.backend_attempts,
            "execution_budget": exc.execution_budget,
        }
        code = 0
    except InternalRecoveryRequired as exc:
        result = {
            "type": "internal-input-recovery.v1", "status": "requires-internal-document-recovery",
            "error": str(exc), "action": getattr(exc, "action", None),
            "user_action_required": False, "question_batch": [],
            "backend_attempts": getattr(exc, "backend_attempts", []),
            "execution_budget": getattr(exc, "execution_budget", None),
        }
        code = 0
    except AwesomeBenziError as exc:
        result = {**exc.to_dict(), "status": "blocked", "question_batch": []}
        code = exc.exit_code
    except Exception as exc:
        result = {"type": "semantic-document-error", "status": "blocked", "error": str(exc), "question_batch": [{"class": "A", "kind": "unreadable-template", "message": str(exc)}]}
        code = 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
