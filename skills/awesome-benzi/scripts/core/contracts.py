"""Versioned internal contracts with explicit validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class SessionState(str, Enum):
    NEW = "NEW"
    SCANNED = "SCANNED"
    ROUTED = "ROUTED"
    PREPARED = "PREPARED"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    PLANNED = "PLANNED"
    DRAFTING = "DRAFTING"
    CONTENT_PASSED = "CONTENT_PASSED"
    FROZEN = "FROZEN"
    DOCX_STAGED = "DOCX_STAGED"
    PARITY_PASSED = "PARITY_PASSED"
    STRUCTURE_PASSED = "STRUCTURE_PASSED"
    RENDER_REVIEW_PENDING = "RENDER_REVIEW_PENDING"
    RENDER_PASSED = "RENDER_PASSED"
    DELIVERED = "DELIVERED"
    CLEANED = "CLEANED"
    BLOCKED = "BLOCKED"


@dataclass
class Versioned:
    schema_type: str
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseManifest(Versioned):
    session_id: str = ""
    request: str = ""
    material_roots: list[str] = field(default_factory=list)
    created_at: str = ""
    limits: dict[str, int] = field(default_factory=dict)

    def __init__(self, **values: Any):
        super().__init__("case-manifest", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class SourceRecord(Versioned):
    source_id: str = ""
    path: str = ""
    format: str = ""
    signature_valid: bool = True
    size: int = 0
    role: str = "unknown"
    role_confidence: float = 0.0
    role_evidence: list[str] = field(default_factory=list)
    read_status: str = "metadata-only"
    recovery: dict[str, Any] | None = None

    def __init__(self, **values: Any):
        super().__init__("source-record", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class RouteDecision(Versioned):
    program_family: str = ""
    program: str = ""
    stage: str = ""
    template_path: str | None = None
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("route-decision", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class TemplateNode(Versioned):
    node_id: str = ""
    source_anchor: str = ""
    kind: str = "paragraph"
    text: str = ""
    level: int | None = None
    confidence: float = 0.0
    locked: bool = False
    children: list[str] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("template-node", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class TemplateSchema(Versioned):
    source_path: str = ""
    source_hash: str = ""
    nodes: list[dict[str, Any]] = field(default_factory=list)
    style_directives: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def __init__(self, **values: Any):
        super().__init__("template-schema", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class FactRecord(Versioned):
    fact_id: str = ""
    field_name: str = ""
    value: Any = None
    status: str = "unknown"
    source_anchors: list[str] = field(default_factory=list)
    allowed_sections: list[str] = field(default_factory=list)
    forbidden_variants: list[str] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("fact-record", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class EvidenceCard(Versioned):
    evidence_id: str = ""
    claim: str = ""
    source: str = ""
    scope: str = ""
    locator: str = ""
    verified: bool = False
    citation_key: str = ""
    allowed_sections: list[str] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("evidence-card", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class DraftManifest(Versioned):
    revision: int = 0
    draft_path: str = ""
    map_path: str = ""
    status: str = "editing"
    section_order: list[str] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("draft-manifest", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class FrozenDraft(Versioned):
    revision: int = 0
    normalization: str = "utf8-lf-nfc-trim-trailing-v1"
    draft_sha256: str = ""
    map_sha256: str = ""
    content_report_sha256: str = ""
    frozen_at: str = ""
    status: str = "frozen"

    def __init__(self, **values: Any):
        super().__init__("frozen-draft", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class QualityIssue(Versioned):
    rule_id: str = ""
    level: str = "blocked"
    message: str = ""
    section_id: str | None = None
    block_id: str | None = None
    suggested_action: str | None = None

    def __init__(self, **values: Any):
        super().__init__("quality-issue", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class QualityReport(Versioned):
    gate: str = "blocked"
    revision: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)

    def __init__(self, **values: Any):
        super().__init__("quality-report", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


@dataclass
class DeliveryResult(Versioned):
    status: str = ""
    artifact_path: str | None = None
    source_template_path: str = ""
    source_template_hash: str = ""
    draft_sha256: str = ""
    output_hash: str | None = None
    parity_gate: dict[str, Any] = field(default_factory=dict)
    structure_gate: dict[str, Any] = field(default_factory=dict)
    render_gate: dict[str, Any] = field(default_factory=dict)

    def __init__(self, **values: Any):
        super().__init__("delivery-result", int(values.pop("schema_version", 1)))
        for name, value in values.items():
            setattr(self, name, value)


def validate_method_modules(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    modules = ledger.get("method_modules")
    if not isinstance(modules, list) or len(modules) != 10:
        return ["method_modules must contain M1 through M10"]
    expected = [f"M{index}" for index in range(1, 11)]
    actual = [item.get("module_id") for item in modules if isinstance(item, dict)]
    if actual != expected:
        errors.append("method_modules must be ordered M1 through M10")
    allowed = {"pending", "complete", "blocked", "not-required"}
    for item in modules:
        if item.get("status") not in allowed:
            errors.append(f"invalid module status for {item.get('module_id')}")
    return errors
