"""Fact/evidence ledgers and the integrated ten-module execution ledger."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from .contracts import validate_method_modules

MODULE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("M1", re.compile(r"选题|立项|背景|依据|现状|价值")),
    ("M2", re.compile(r"研究内容|研究目标|重点|难点")),
    ("M3", re.compile(r"方法|思路|技术路线|可行性")),
    ("M4", re.compile(r"创新")),
    ("M5", re.compile(r"成果|效益|产出")),
    ("M6", re.compile(r"基础|团队|条件")),
    ("M7", re.compile(r"摘要|关键词")),
]

MODULE_ARTIFACT_DEFAULTS: dict[str, dict[str, Any]] = {
    "M1": {"problem_chain": {}, "literature_diagnostics": [], "academic_value": "", "application_value": ""},
    "M2": {"content_graph": {}, "task_dependencies": [], "key_points": [], "difficulties": []},
    "M3": {"method_map": [], "technical_route": [], "feasibility": {}},
    "M4": {"innovation_map": [], "gap_links": [], "non_substitutability_checks": []},
    "M5": {"outcome_map": [], "audiences": [], "application_paths": []},
    "M6": {"foundation_map": [], "team_assignments": [], "resource_evidence": []},
    "M7": {"abstract_coverage": {}, "keywords": [], "keyword_overlap_checks": []},
    "M8": {"logical_diagnostics": [], "overall_logic_assessment": {}},
    "M9": {"language_revision_log": [], "unchanged_pass_records": []},
    "M10": {"review": {"dimensions": {}, "strengths": [], "issues": [], "revision_route": []}},
}
MECHANICAL_TASK = re.compile(r"扫描|识别格式|格式检查|只读检查|抽取|提取结构|转换格式")
SUBSTANTIVE_SECTION = re.compile(r"依据|背景|现状|内容|目标|方法|路线|创新|成果|基础|团队|摘要|可行性|风险")


def reasoning_mode(prompt: str, sections: list[dict[str, Any]]) -> str:
    substantive = [
        section
        for section in sections
        if SUBSTANTIVE_SECTION.search(str(section.get("heading", "")))
    ]
    section_task = bool(re.search(r"只(?:修改|润色|改写)|仅(?:修改|润色|改写)|单节|本节", prompt))
    writing_task = bool(re.search(r"撰写|起草|完成|润色|改写|修订|全文|全稿|申请书|申报书", prompt))
    if MECHANICAL_TASK.search(prompt) and not writing_task:
        return "mechanical"
    if section_task or 1 <= len(substantive) <= 3:
        return "standard"
    return "deep"


def _module_rank(heading: str) -> int:
    for module_id, pattern in MODULE_PATTERNS:
        if pattern.search(heading):
            return int(module_id[1:])
    return 99


def initialize_reasoning_plan(prompt: str, sections: list[dict[str, Any]]) -> dict[str, Any]:
    mode = reasoning_mode(prompt, sections)
    ordered = [
        (
            str(section.get("section_id", f"section-{index + 1:04d}")),
            str(section.get("heading", "")),
            _module_rank(str(section.get("heading", ""))),
        )
        for index, section in enumerate(sections)
    ]
    planned_sections: list[dict[str, Any]] = []
    for index, section in enumerate(sections):
        section_id, heading, rank = ordered[index]
        prior_candidates = [
            candidate_id
            for candidate_id, _, candidate_rank in ordered[:index]
            if candidate_rank < rank
        ]
        dependencies = prior_candidates[-1:] if prior_candidates else []
        planned_sections.append(
            {
                "section_id": section_id,
                "heading": heading,
                "dependencies": dependencies,
                "central_proposition": "",
                "subquestions": [],
                "claims": [],
                "evidence_ids": [],
                "unknowns": list(section.get("missing_items", [])),
                "method": "",
                "boundary": "",
                "expected_conclusion": "",
                "word_budget": section.get("word_budget"),
                "verification_questions": [],
                "status": "planned" if mode != "mechanical" else "not-required",
            }
        )
    return {
        "schema_type": "reasoning-plan",
        "schema_version": 1,
        "protocol": "evidence-plan-generate-verify",
        "mode": mode,
        "sections": planned_sections,
        "verification_policy": {
            "independent_from_draft": True,
            "max_questions_per_section": 3,
            "max_questions_total": 20,
            "high_risk_claims_only": True,
        },
        "stop_conditions": {
            "max_revision_rounds": 1,
            "stop_when_no_blocked_or_review_issues": True,
            "stop_when_no_new_evidence": True,
            "stop_when_issues_do_not_improve": True,
        },
        "stores_free_form_reasoning": False,
    }


def initialize_verification_summary() -> dict[str, Any]:
    return {
        "schema_type": "verification-summary",
        "schema_version": 1,
        "status": "pending",
        "total_questions": 0,
        "verified": 0,
        "unsupported": 0,
        "unknown": 0,
        "revision_rounds": 0,
        "early_stop_reason": None,
    }


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def validate_reasoning_protocol(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    plan = ledger.get("reasoning_plan")
    if plan is None:
        return []
    issues: list[dict[str, Any]] = []
    if plan.get("schema_type") != "reasoning-plan" or _safe_int(plan.get("schema_version", 0)) != 1:
        issues.append({"kind": "invalid-reasoning-plan", "message": "reasoning plan must use reasoning-plan.v1"})
        return issues
    if plan.get("mode") not in {"mechanical", "standard", "deep"}:
        issues.append({"kind": "invalid-reasoning-mode", "message": "reasoning mode must be mechanical, standard, or deep"})
    sections = [item for item in plan.get("sections", []) if isinstance(item, dict)]
    section_ids = [str(item.get("section_id", "")) for item in sections]
    if not all(section_ids) or len(section_ids) != len(set(section_ids)):
        issues.append({"kind": "invalid-reasoning-sections", "message": "reasoning section IDs must be non-empty and unique"})
    graph = {
        str(item.get("section_id", "")): [str(value) for value in item.get("dependencies", [])]
        for item in sections
    }
    unknown_dependencies = sorted(
        {
            dependency
            for dependencies in graph.values()
            for dependency in dependencies
            if dependency not in graph
        }
    )
    if unknown_dependencies:
        issues.append(
            {
                "kind": "unknown-reasoning-dependency",
                "message": "reasoning dependencies must reference an existing section",
                "dependencies": unknown_dependencies,
            }
        )
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        for dependency in graph.get(node, []):
            if dependency in graph and not visit(dependency):
                return False
        visiting.remove(node)
        visited.add(node)
        return True

    if any(not visit(node) for node in graph):
        issues.append({"kind": "cyclic-reasoning-plan", "message": "reasoning section dependencies must be acyclic"})
    total_questions = 0
    for section in sections:
        questions = section.get("verification_questions", [])
        if not isinstance(questions, list):
            issues.append(
                {
                    "kind": "invalid-verification-questions",
                    "message": "verification_questions must be an array",
                    "section": section.get("section_id"),
                }
            )
            continue
        total_questions += len(questions)
        if len(questions) > 3:
            issues.append(
                {
                    "kind": "section-verification-limit",
                    "message": "a section may contain at most three independent verification questions",
                    "section": section.get("section_id"),
                    "count": len(questions),
                }
            )
        for claim in section.get("claims", []):
            if not isinstance(claim, dict):
                issues.append(
                    {
                        "kind": "invalid-reasoning-claim",
                        "message": "reasoning claims must be structured objects",
                        "section": section.get("section_id"),
                    }
                )
                continue
            if claim.get("status") == "asserted" and not claim.get("evidence_ids") and not claim.get("unknown"):
                issues.append(
                    {
                        "kind": "unsupported-reasoning-claim",
                        "message": "an asserted claim must cite evidence or be marked unknown",
                        "section": section.get("section_id"),
                        "claim_id": claim.get("claim_id"),
                    }
                )
    if total_questions > 20:
        issues.append(
            {
                "kind": "verification-question-limit",
                "message": "the full reasoning plan may contain at most twenty verification questions",
                "count": total_questions,
            }
        )
    stop = plan.get("stop_conditions", {})
    if _safe_int(stop.get("max_revision_rounds", 1), 1) > 1:
        issues.append({"kind": "reasoning-revision-limit", "message": "the reasoning protocol permits at most one revision round"})
    summary = ledger.get("verification_summary")
    if isinstance(summary, dict):
        if _safe_int(summary.get("revision_rounds", 0), 0) > 1:
            issues.append({"kind": "verification-revision-limit", "message": "verification triggered more than one revision round"})
        if _safe_int(summary.get("total_questions", total_questions), total_questions) > 20:
            issues.append({"kind": "verification-summary-limit", "message": "verification summary exceeds the twenty-question limit"})
    return issues


def required_modules(prompt: str, headings: list[str]) -> set[str]:
    section_task = bool(re.search(r"只(?:修改|润色|改写)|仅(?:修改|润色|改写)|单节|本节", prompt))
    if not section_task:
        return {f"M{index}" for index in range(1, 11)}
    combined = f"{prompt}\n{' '.join(headings)}"
    selected = {module for module, pattern in MODULE_PATTERNS if pattern.search(combined)}
    if not selected:
        selected = {"M1"}
    return selected | {"M8", "M9", "M10"}


def initialize_method_modules(prompt: str, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    headings = [str(section.get("heading", "")) for section in sections]
    required = required_modules(prompt, headings)
    records: list[dict[str, Any]] = []
    for index in range(1, 11):
        module_id = f"M{index}"
        section_ids = [
            str(section.get("section_id"))
            for section in sections
            if any(module_id == candidate and pattern.search(str(section.get("heading", ""))) for candidate, pattern in MODULE_PATTERNS)
        ]
        records.append(
            {
                "schema_type": "method-module",
                "schema_version": 1,
                "module_id": module_id,
                "required": module_id in required,
                "status": "pending" if module_id in required else "not-required",
                "section_ids": section_ids,
                "input_revision": 0,
                "diagnostic_issue_ids": [],
                "decision_ids": [],
                "unresolved_gap_ids": [],
                "completed_revision": None,
                **deepcopy(MODULE_ARTIFACT_DEFAULTS[module_id]),
            }
        )
    return records


def integrate_method_modules(ledger: dict[str, Any], prompt: str = "") -> dict[str, Any]:
    result = deepcopy(ledger)
    result.setdefault("schema_type", "writing-ledger")
    result.setdefault("schema_version", 1)
    if "method_modules" not in result:
        result["method_modules"] = initialize_method_modules(prompt, result.get("sections", []))
    result.setdefault("reasoning_plan", initialize_reasoning_plan(prompt, result.get("sections", [])))
    result.setdefault("verification_summary", initialize_verification_summary())
    result["structured_reasoning_only"] = True
    result["display_to_user"] = False
    errors = validate_method_modules(result)
    if errors:
        raise ValueError("; ".join(errors))
    return result


def complete_modules(
    ledger: dict[str, Any],
    completed: list[str | int],
    revision: int,
    diagnostics: dict[str, list[str]] | None = None,
    module_results: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = deepcopy(ledger)
    normalized = {f"M{value}" if str(value).isdigit() else str(value) for value in completed}
    for item in result.get("method_modules", []):
        supplied_result = (module_results or {}).get(item["module_id"], {})
        if isinstance(supplied_result, dict):
            for field_name in MODULE_ARTIFACT_DEFAULTS[item["module_id"]]:
                if field_name in supplied_result:
                    item[field_name] = deepcopy(supplied_result[field_name])
        if item["module_id"] in normalized:
            item["status"] = "complete"
            item["input_revision"] = revision
            item["completed_revision"] = revision
            item["diagnostic_issue_ids"] = list((diagnostics or {}).get(item["module_id"], []))
    if "modules" in result:
        for item in result.get("modules", []):
            if not isinstance(item, dict):
                continue
            module = _safe_int(item.get("module"), 0)
            module_id = f"M{module}" if 1 <= module <= 10 else None
            if module_id and module_id in normalized:
                item["status"] = "complete"
                item["input_revision"] = revision
                item["completed_revision"] = revision
            elif item.get("required") is False:
                item["status"] = "not-required"
    return result
