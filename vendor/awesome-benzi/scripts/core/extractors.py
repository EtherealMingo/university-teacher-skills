"""Extractor registry façade over format-specific deterministic backends."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import template_schema

SUPPORTED = {".doc", ".docx", ".pdf", ".md", ".txt"}


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: dict[str, Callable[[Path, str | None], dict[str, Any]]] = {}

    def register(self, suffix: str, extractor: Callable[[Path, str | None], dict[str, Any]]) -> None:
        self._extractors[suffix.lower()] = extractor

    def probe(self, path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()
        return {"supported": suffix in self._extractors, "format": suffix.lstrip("."), "extractor": suffix}

    def extract(self, path: Path, recovered_text: str | None = None) -> dict[str, Any]:
        suffix = path.suffix.lower()
        if suffix not in self._extractors:
            raise ValueError(f"unsupported format: {suffix}")
        return self._extractors[suffix](path, recovered_text)


registry = ExtractorRegistry()
for _suffix in SUPPORTED:
    registry.register(_suffix, template_schema.extract_structure)

extract_structure = template_schema.extract_structure
legacy_doc_to_docx = template_schema._legacy_doc_to_docx
ocr_scanned_pdf = template_schema._ocr_scanned_pdf
