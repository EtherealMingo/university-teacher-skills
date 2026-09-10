"""Visible-text parity between a frozen Markdown draft and staged DOCX."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from docx import Document

from .draft_store import parse_markdown


def normalize_visible(text: str) -> str:
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    text = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f]", "", text)
    # Tabs are the table cell separator in the canonical visible-text model and
    # must survive normalization; only spaces and non-breaking spaces collapse.
    return re.sub(r"[ \u00a0]+", " ", text).strip()


def markdown_visible_blocks(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocks, issues = parse_markdown(path.read_text(encoding="utf-8"))
    visible = [
        {
            "block_id": block["block_id"],
            "section_id": block["section_id"],
            "kind": block["kind"],
            "text": normalize_visible(block.get("text", "")),
        }
        for block in blocks
        if block.get("text")
    ]
    return visible, issues


def docx_visible_sequence(path: Path) -> list[dict[str, Any]]:
    document = Document(str(path))
    values: list[dict[str, Any]] = []
    for block in document.iter_inner_content():
        if hasattr(block, "rows"):
            rows: list[str] = []
            for row in block.rows:
                rows.append(
                    chr(9).join(
                        " ".join(normalize_visible(paragraph.text) for paragraph in cell.paragraphs)
                        for cell in row.cells
                    )
                )
            text = chr(10).join(rows)
            values.append({"kind": "table", "text": normalize_visible(text)})
            continue
        if not hasattr(block, "text"):
            continue
        value = normalize_visible(block.text)
        if value:
            values.append({"kind": "paragraph", "text": value})
    return values


def compare_frozen_to_docx(
    draft_path: Path,
    docx_path: Path,
    *,
    locked_text: set[str] | None = None,
) -> dict[str, Any]:
    expected, parse_issues = markdown_visible_blocks(draft_path)
    actual = docx_visible_sequence(docx_path)
    locked = {normalize_visible(value) for value in (locked_text or set()) if value}
    searchable = [value for value in actual if value["text"] not in locked]
    differences: list[dict[str, Any]] = []
    if parse_issues:
        differences.append(
            {
                "rule_id": "MD-SYNTAX-004",
                "level": "blocked",
                "message": "frozen Markdown could not be parsed for parity comparison",
                "parse_issues": parse_issues,
            }
        )
        return {
            "schema_type": "parity-report",
            "schema_version": 1,
            "gate": "blocked",
            "draft_path": str(draft_path),
            "docx_path": str(docx_path),
            "expected_blocks": len(expected),
            "docx_visible_blocks": len(actual),
            "issues": differences,
        }
    expected_multiset: Counter[str] = Counter()
    for block in expected:
        expected_multiset[block["text"]] += 1
        for piece in block["text"].split(chr(10)):
            piece = normalize_visible(piece)
            if piece:
                expected_multiset[piece] += 1
    available = Counter(item["text"] for item in searchable)
    cursor = 0
    for block in expected:
        target = block["text"]
        if block["kind"] == "heading" and target in locked:
            continue
        found = next(
            (
                index
                for index in range(cursor, len(searchable))
                if searchable[index]["text"] == target and available[target] > 0
            ),
            None,
        )
        if found is not None:
            available[target] -= 1
            cursor = found + 1
            continue
        pieces = [normalize_visible(piece) for piece in target.split(chr(10)) if normalize_visible(piece)]
        if len(pieces) >= 2 and all(available[piece] > 0 for piece in pieces):
            for piece in pieces:
                available[piece] -= 1
            continue
        differences.append(
            {
                "rule_id": "MD-PARITY-005",
                "level": "blocked",
                "block_id": block["block_id"],
                "section_id": block["section_id"],
                "expected": target,
                "message": "frozen Markdown block was not found unchanged in DOCX",
            }
        )
    unexpected = sorted(
        value
        for value, count in available.items()
        if count > 0
        for _ in range(count)
    )
    if unexpected:
        differences.append(
            {
                "rule_id": "MD-PARITY-005",
                "level": "blocked",
                "message": "DOCX contains visible prose not present in frozen Markdown or locked template text",
                "unexpected": unexpected[:20],
            }
        )
    return {
        "schema_type": "parity-report",
        "schema_version": 1,
        "gate": "blocked" if differences else "passed",
        "draft_path": str(draft_path),
        "docx_path": str(docx_path),
        "expected_blocks": len(expected),
        "docx_visible_blocks": len(actual),
        "issues": differences,
    }
