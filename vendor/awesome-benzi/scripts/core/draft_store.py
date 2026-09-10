"""The only writable prose store: restricted Markdown, mapping and freeze."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .contracts import DraftManifest, FrozenDraft
from .errors import AwesomeBenziError
from .paths import assert_session_path, sha256

HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+(.+)$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*$")
PLACEHOLDER_RE = re.compile(r"【待补：[^】]{1,100}】")
FORBIDDEN_RE = re.compile(r"<(?:script|iframe|object|embed|link)\b|!\[[^\]]*\]\([^)]*\)|\[[^\]]+\]\(\s*(?:javascript|file|data):", re.I)
MANAGEMENT_RE = re.compile(r"(?:^|[。；;!?])(?:帮我|请帮我|按(?:用户|申请人)(?:要求|需求)|根据(?:用户|申请人)(?:要求|需求)|用户希望我|申请人希望我)")
CHINESE_NUMERALS = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十")
INTERNAL_HEADING_PREFIX = re.compile(
    r"^\s*(?:[（(]?[一二三四五六七八九十0-9]+[）).、]|第[一二三四五六七八九十0-9]+)"
)


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith(chr(92)+"|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    buffer: list[str] = []
    escaped = False
    for char in stripped:
        if escaped:
            buffer.append(char)
            escaped = False
        elif char == chr(92):
            escaped = True
        elif char == "|":
            cells.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)
    if escaped:
        buffer.append(chr(92))
    cells.append("".join(buffer).strip())
    return cells


def _json_write(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def normalize_markdown(text: str) -> str:
    # Strip a stray UTF-8 BOM so a BOM-prefixed draft never leaks a literal
    # "#\ufeff" title or blank first block into Markdown or the DOCX.
    text = text.lstrip("\ufeff")
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def _markdown_for_value(value: Any, level: int = 3) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return normalize_markdown(value).rstrip("\n").splitlines()
    if isinstance(value, list):
        lines: list[str] = []
        top = 0
        child = 0
        for item in value:
            if isinstance(item, dict):
                kind = str(item.get("type") or item.get("kind") or "paragraph")
                if kind in {"heading", "subheading", "sub-subheading"}:
                    depth = int(item.get("depth") or (2 if kind == "sub-subheading" else 1))
                    text = str(item.get("text") or item.get("content") or "").strip()
                    if depth <= 1:
                        top += 1
                        child = 0
                        prefix = f"（{CHINESE_NUMERALS[top - 1]}）" if top <= len(CHINESE_NUMERALS) else f"（{top}）"
                        markdown_level = 3
                    else:
                        if top == 0:
                            top = 1
                        child += 1
                        prefix = f"{top}.{child}"
                        markdown_level = 4
                    if text and not INTERNAL_HEADING_PREFIX.match(text):
                        text = f"{prefix}{text}"
                    lines.append(f"{'#' * markdown_level} {text}")
                else:
                    lines.extend(_markdown_for_value(item, level))
            else:
                lines.append(f"- {item}")
        return lines
    if isinstance(value, dict):
        if "blocks" in value:
            return _markdown_for_value(value["blocks"], level)
        kind = str(value.get("type") or value.get("kind") or "paragraph")
        text = str(value.get("text") or value.get("content") or "")
        if kind in {"heading", "subheading", "sub-subheading"}:
            requested = int(value.get("level") or (4 if int(value.get("depth") or 1) > 1 else level))
            return [f"{'#' * max(3, min(4, requested))} {text}"]
        if kind == "list":
            return [f"- {item}" for item in value.get("items", [])]
        if kind == "table":
            rows = value.get("rows", [])
            if not rows:
                return []
            width = max(len(row) for row in rows)
            padded = [list(row) + [""] * (width - len(row)) for row in rows]
            lines = ["| " + " | ".join(map(str, padded[0])) + " |"]
            lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
            lines.extend("| " + " | ".join(map(str, row)) + " |" for row in padded[1:])
            return lines
        return text.splitlines() if text else []
    return [str(value)]


def content_to_markdown(
    content: dict[str, Any] | None,
    structure: dict[str, Any] | None = None,
    new_text: str | None = None,
) -> str:
    content = content or {}
    lines: list[str] = []
    nodes = (structure or {}).get("nodes", [])
    title = next(
        (
            str(node.get("text", "")).strip()
            for node in nodes
            if node.get("kind") in {"title", "document-title"} and node.get("text")
        ),
        "",
    )
    if title:
        lines.extend([f"# {title}", ""])

    sections = content.get("sections")
    if isinstance(sections, dict):
        for heading, value in sections.items():
            lines.extend([f"## {heading}", ""])
            lines.extend(_markdown_for_value(value))
            lines.append("")

    replacements = content.get("replacements")
    if isinstance(replacements, dict):
        heading_by_placeholder: dict[str, str] = {}
        current_heading = "正文"
        for node in nodes:
            if node.get("kind") == "heading" and node.get("text"):
                current_heading = str(node["text"]).strip()
            if node.get("text"):
                heading_by_placeholder[str(node["text"])] = current_heading
        for source, replacement in replacements.items():
            heading = heading_by_placeholder.get(str(source), "正文")
            if f"## {heading}" not in lines:
                lines.extend([f"## {heading}", ""])
            lines.extend(_markdown_for_value(replacement))
            lines.append("")

    blocks = content.get("blocks")
    if blocks:
        if not any(line.startswith("## ") for line in lines):
            lines.extend(["## 正文", ""])
        lines.extend(_markdown_for_value(blocks))
        lines.append("")

    prose = (new_text or "").strip()
    if prose and prose not in "\n".join(lines):
        if not any(line.startswith("## ") for line in lines):
            lines.extend(["## 正文", ""])
        lines.extend(prose.splitlines())
        lines.append("")

    if not lines:
        visible = [
            str(node.get("text", "")).strip()
            for node in nodes
            if node.get("kind") in {"paragraph", "list-item"} and str(node.get("text", "")).strip()
        ]
        lines = ["## 正文", "", *(visible or ["【待补：正文】"]), ""]
    return normalize_markdown("\n".join(lines))


def structure_to_markdown(structure: dict[str, Any], new_text: str | None = None) -> str:
    """Serialize the complete post-injection semantic tree into canonical prose Markdown."""
    lines: list[str] = []
    visible_text: list[str] = []
    heading_levels = [
        int(node.get("level") or 1)
        for node in structure.get("nodes", [])
        if node.get("kind") == "heading"
    ]
    minimum_heading_level = min(heading_levels, default=1)
    for node in structure.get("nodes", []):
        kind = str(node.get("kind", ""))
        text = str(node.get("text", "")).strip()
        if kind == "document-title" and text:
            lines.extend([f"# {text}", ""])
            visible_text.append(text)
        elif kind == "heading" and text:
            level = max(2, min(4, int(node.get("level") or minimum_heading_level) - minimum_heading_level + 2))
            lines.extend([f"{'#' * level} {text}", ""])
            visible_text.append(text)
        elif kind == "internal-heading" and text:
            level = 3 if int(node.get("internal_depth") or node.get("level") or 1) <= 1 else 4
            lines.extend([f"{'#' * level} {text}", ""])
            visible_text.append(text)
        elif kind == "list-item" and text:
            lines.append(f"- {text}")
            visible_text.append(text)
        elif kind == "table":
            rows = []
            for row in node.get("rows", []):
                values = [
                    " ".join(
                        str(part.get("text", "")).strip()
                        for part in cell.get("paragraphs", [])
                        if str(part.get("text", "")).strip()
                    )
                    for cell in row.get("cells", [])
                ]
                rows.append(values)
            if rows:
                width = max(len(row) for row in rows)
                padded = [row + [""] * (width - len(row)) for row in rows]
                lines.append("| " + " | ".join(padded[0]) + " |")
                lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
                lines.extend("| " + " | ".join(row) + " |" for row in padded[1:])
                lines.append("")
                visible_text.extend(value for row in padded for value in row if value)
        elif kind == "placeholder":
            label = re.sub(r"[【】_\s]", "", text)
            label = re.sub(r"^(?:请|在此)?(?:填写|输入|待补)[:：]?", "", label) or "正文"
            placeholder = f"【待补：{label[:100]}】"
            lines.extend([placeholder, ""])
            visible_text.append(placeholder)
        elif kind not in {"empty", "instruction", "image"} and text:
            lines.extend([text, ""])
            visible_text.append(text)
    prose = (new_text or "").strip()
    if prose and prose not in "\n".join(visible_text):
        if not any(line.startswith("## ") for line in lines):
            lines.extend(["## 正文", ""])
        lines.extend([prose, ""])
    if not lines:
        lines = ["## 正文", "", "【待补：正文】", ""]
    return normalize_markdown("\n".join(lines))


def parse_markdown(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    normalized = normalize_markdown(text)
    issues: list[dict[str, Any]] = []
    if FORBIDDEN_RE.search(normalized):
        issues.append({"rule_id": "MD-SYNTAX-004", "level": "blocked", "message": "forbidden executable or embedded Markdown content"})
    if MANAGEMENT_RE.search(normalized):
        issues.append({"rule_id": "QG-CONTENT-007", "level": "blocked", "message": "task-management language leaked into prose"})
    blocks: list[dict[str, Any]] = []
    lines = normalized.splitlines()
    index = 0
    section_id = "section-000"
    heading_count = {1: 0, 2: 0, 3: 0, 4: 0}
    title_count = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title_count += level == 1
            heading_count[level] += 1
            if level == 2:
                section_id = f"section-{heading_count[2]:03d}"
            blocks.append({"kind": "heading", "level": level, "text": heading.group(2).strip(), "section_id": section_id})
            index += 1
            continue
        if line.lstrip().startswith("|") and index + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[index + 1]):
            rows: list[list[str]] = []
            rows.append(_split_table_row(line))
            index += 2
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                rows.append(_split_table_row(lines[index]))
                index += 1
            width = max((len(row) for row in rows), default=0)
            rows = [row + [""] * (width - len(row)) for row in rows]
            blocks.append({"kind": "table", "rows": rows, "text": chr(10).join(chr(9).join(row) for row in rows), "section_id": section_id})
            continue
        list_match = LIST_RE.match(line)
        if list_match:
            items: list[str] = []
            depths: list[int] = []
            list_types: list[str] = []
            while index < len(lines):
                match = LIST_RE.match(lines[index])
                if not match:
                    break
                raw = lines[index]
                indent = len(raw) - len(raw.lstrip(" "))
                ordered = bool(re.match(r"^[ 	]*[0-9]+[.)]", raw))
                items.append(match.group(1).strip())
                depths.append(1 if indent < 2 else 2)
                list_types.append("ordered" if ordered else "unordered")
                index += 1
            blocks.append({
                "kind": "list", "items": items, "depths": depths, "list_types": list_types,
                "text": chr(10).join(items), "section_id": section_id,
            })
            continue
        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not HEADING_RE.match(lines[index]) and not LIST_RE.match(lines[index]):
            if lines[index].lstrip().startswith("|") and index + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[index + 1]):
                break
            paragraph_lines.append(lines[index].strip())
            index += 1
        blocks.append({"kind": "paragraph", "text": chr(10).join(paragraph_lines), "section_id": section_id})

    for position, heading in enumerate(blocks):
        if heading.get("kind") != "heading":
            continue
        level = int(heading.get("level") or 1)
        has_body = False
        for candidate in blocks[position + 1:]:
            candidate_level = int(candidate.get("level") or 1) if candidate.get("kind") == "heading" else level + 1
            if candidate.get("kind") == "heading" and candidate_level <= level:
                break
            if candidate.get("kind") == "heading":
                has_body = True
                break
            if candidate.get("text", "").strip() or (candidate.get("kind") == "list" and candidate.get("items")):
                has_body = True
                break
        if not has_body:
            issues.append({
                "rule_id": "QG-CONTENT-002",
                "level": "blocked",
                "message": f"heading has no body before the next same-level heading: {heading.get('text')}",
                "block_id": heading.get("text"),
            })
    if title_count > 1:
        issues.append({"rule_id": "MD-SYNTAX-002", "level": "blocked", "message": "draft may contain at most one level-one title"})
    if not any(block["kind"] == "heading" and block["level"] == 2 for block in blocks):
        issues.append({"rule_id": "QG-CONTENT-002", "level": "blocked", "message": "draft has no template section"})
    for position, block in enumerate(blocks):
        block["ordinal"] = position
        seed = f"{block['section_id']}|{block['kind']}|{position}|{block.get('text', '')}"
        block["block_id"] = f"B-{hashlib.sha1(seed.encode('utf-8')).hexdigest()[:12]}"
    return blocks, issues


def create_draft(
    session: Path,
    markdown: str,
    source_anchors: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    session = session.resolve()
    draft_dir = assert_session_path(session / "draft", session)
    draft_dir.mkdir(exist_ok=True)
    normalized = normalize_markdown(markdown)
    blocks, issues = parse_markdown(normalized)
    if any(item["level"] == "blocked" for item in issues):
        raise AwesomeBenziError("E_DRAFT_PARSE", "draft", "draft Markdown is invalid", details={"issues": issues})
    draft_path = draft_dir / "draft.md"
    map_path = draft_dir / "draft-map.json"
    draft_path.write_text(normalized, encoding="utf-8", newline="\n")
    mapping = {
        "schema_type": "draft-map",
        "schema_version": 1,
        "revision": 1,
        "blocks": [
            {
                "block_id": block["block_id"],
                "section_id": block["section_id"],
                "kind": block["kind"],
                "ordinal": block["ordinal"],
                "source_anchors": (source_anchors or {}).get(block["block_id"], []),
                "generated": True,
            }
            for block in blocks
        ],
    }
    _json_write(map_path, mapping)
    manifest = DraftManifest(
        revision=1,
        draft_path=str(draft_path),
        map_path=str(map_path),
        status="editing",
        section_order=list(dict.fromkeys(block["section_id"] for block in blocks if block["section_id"] != "section-000")),
    ).to_dict()
    _json_write(draft_dir / "draft-manifest.json", manifest)
    for obsolete in ("frozen-draft.json", "content-quality.json"):
        (draft_dir / obsolete).unlink(missing_ok=True)
    return manifest


def revise_draft(session: Path, markdown: str) -> dict[str, Any]:
    draft_dir = assert_session_path(session / "draft", session)
    manifest_path = draft_dir / "draft-manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = create_draft(session, markdown)
    result["revision"] = int(previous["revision"]) + 1
    mapping_path = Path(result["map_path"])
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    mapping["revision"] = result["revision"]
    _json_write(mapping_path, mapping)
    _json_write(manifest_path, result)
    return result


def freeze_draft(session: Path, content_report: dict[str, Any]) -> dict[str, Any]:
    draft_dir = assert_session_path(session / "draft", session)
    manifest = json.loads((draft_dir / "draft-manifest.json").read_text(encoding="utf-8"))
    draft_path = Path(manifest["draft_path"])
    map_path = Path(manifest["map_path"])
    normalized = normalize_markdown(draft_path.read_text(encoding="utf-8"))
    blocks, issues = parse_markdown(normalized)
    mapping = json.loads(map_path.read_text(encoding="utf-8"))
    mapped_blocks = mapping.get("blocks", [])
    expected_signature = [
        (block["block_id"], block["section_id"], block["kind"], block["ordinal"])
        for block in blocks
    ]
    mapped_signature = [
        (block.get("block_id"), block.get("section_id"), block.get("kind"), block.get("ordinal"))
        for block in mapped_blocks
        if isinstance(block, dict)
    ]
    if (
        issues
        or expected_signature != mapped_signature
        or int(mapping.get("revision", -1)) != int(manifest["revision"])
    ):
        raise AwesomeBenziError(
            "E_DRAFT_MAP_MISMATCH",
            "freeze",
            "draft map count, type, order, identity or revision does not match Markdown",
            recoverability="internal-invariant",
            details={"issues": issues, "expected": expected_signature, "actual": mapped_signature},
        )
    if content_report.get("gate") == "blocked":
        raise AwesomeBenziError(
            "E_CONTENT_GATE_BLOCKED",
            "content",
            "content gate blocked freezing",
            recoverability="retryable",
            details={"issues": content_report.get("issues", [])},
        )
    draft_path.write_text(normalized, encoding="utf-8", newline=chr(10))
    report_path = draft_dir / "content-quality.json"
    _json_write(report_path, content_report)
    frozen = FrozenDraft(
        revision=int(manifest["revision"]),
        draft_sha256=sha256(draft_path),
        map_sha256=sha256(map_path),
        content_report_sha256=sha256(report_path),
        frozen_at=datetime.now(timezone.utc).isoformat(),
    ).to_dict()
    frozen.update({"draft_path": str(draft_path), "map_path": str(map_path), "content_report_path": str(report_path)})
    _json_write(draft_dir / "frozen-draft.json", frozen)
    manifest["status"] = "frozen"
    _json_write(draft_dir / "draft-manifest.json", manifest)
    return frozen
def verify_frozen(frozen_or_path: dict[str, Any] | Path) -> dict[str, Any]:
    frozen = json.loads(frozen_or_path.read_text(encoding="utf-8")) if isinstance(frozen_or_path, Path) else frozen_or_path
    checks = {
        "draft_sha256": sha256(Path(frozen["draft_path"])),
        "map_sha256": sha256(Path(frozen["map_path"])),
        "content_report_sha256": sha256(Path(frozen["content_report_path"])),
    }
    if any(checks[key] != frozen[key] for key in checks):
        raise AwesomeBenziError(
            "E_DRAFT_CHANGED_AFTER_FREEZE",
            "freeze",
            "draft, map or content report changed after freeze",
            recoverability="internal-retry",
            details={"actual": checks},
        )
    return frozen
