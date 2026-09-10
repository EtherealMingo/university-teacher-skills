"""Mechanical DOCX rendering and render-review validation."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from PIL import Image

from .errors import AwesomeBenziError
from .paths import sha256
from .session import (
    bounded_timeout_seconds,
    consume_execution_budget,
    run_bounded_process,
)


def find_libreoffice() -> str | None:
    for name in ("soffice", "libreoffice"):
        executable = shutil.which(name)
        if executable:
            return executable
    windows_candidates = (
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    )
    return next((str(path) for path in windows_candidates if path.exists()), None)


def find_pdftoppm() -> str | None:
    configured = os.environ.get("POPPLER_PATH")
    if configured:
        candidate = Path(configured) / "pdftoppm.exe" if os.name == "nt" else Path(configured) / "pdftoppm"
        if candidate.exists():
            return str(candidate)
    found = shutil.which("pdftoppm")
    if found:
        return found
    if os.name == "nt":
        for candidate in (
            Path("C:/Program Files/poppler/Library/bin/pdftoppm.exe"),
            Path("C:/Program Files (x86)/poppler/Library/bin/pdftoppm.exe"),
            Path("C:/poppler/Library/bin/pdftoppm.exe"),
        ):
            if candidate.exists():
                return str(candidate)
    return None


def render_capabilities() -> dict[str, Any]:
    libreoffice = find_libreoffice()
    pdftoppm = find_pdftoppm()
    return {
        "libreoffice": {"available": bool(libreoffice), "path": libreoffice},
        "pdftoppm": {"available": bool(pdftoppm), "path": pdftoppm},
        # Rendering is an optional review enhancement, never a delivery blocker.
        "render_gate": {
            "available": bool(libreoffice and pdftoppm),
            "missing": [
                name
                for name, value in (("libreoffice", libreoffice), ("pdftoppm", pdftoppm))
                if not value
            ],
        },
    }


def _attempt(
    attempts: list[dict[str, Any]] | None,
    *,
    backend: str,
    status: str,
    elapsed_seconds: float,
    error_code: str | None = None,
    budget: dict[str, Any] | None = None,
) -> None:
    if attempts is not None:
        ended_epoch = time.time()
        attempts.append(
            {
                "backend": backend,
                "stage": "render",
                "status": status,
                "started_at_epoch": round(ended_epoch - elapsed_seconds, 3),
                "ended_at_epoch": round(ended_epoch, 3),
                "elapsed_ms": round(elapsed_seconds * 1000, 2),
                "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
                "error_code": error_code,
            }
        )


def render_docx(
    docx_path: Path,
    qa_dir: Path,
    timeout_seconds: int = 60,
    budget: dict[str, Any] | None = None,
    attempts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    libreoffice = find_libreoffice()
    pdftoppm = find_pdftoppm()
    if not libreoffice or not pdftoppm:
        raise AwesomeBenziError(
            "E_RENDERER_UNAVAILABLE",
            "render",
            "LibreOffice and pdftoppm are unavailable; render review cannot run",
            recoverability="environment",
            suggested_action="Install or expose LibreOffice and Poppler to enable page-level render review.",
            details={"libreoffice": libreoffice, "pdftoppm": pdftoppm},
        )
    qa_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = qa_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    for stale in pages_dir.glob("page-*.png"):
        stale.unlink(missing_ok=True)
    pdf_path = qa_dir / f"{docx_path.stem}.pdf"
    pdf_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="awesome-benzi-lo-profile-") as raw_profile:
        profile = Path(raw_profile).resolve().as_uri()
        backend = "libreoffice-render"
        started = time.perf_counter()
        try:
            conversion = run_bounded_process(
                [
                    libreoffice,
                    f"-env:UserInstallation={profile}",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(qa_dir),
                    str(docx_path),
                ],
                timeout_seconds=bounded_timeout_seconds(
                    budget,
                    timeout_seconds,
                    stage="render",
                    backend=backend,
                ),
                stage="render",
                backend=backend,
            )
        except AwesomeBenziError as exc:
            elapsed = time.perf_counter() - started
            consume_execution_budget(budget, elapsed) if budget is not None else None
            _attempt(attempts, backend=backend, status="timeout", elapsed_seconds=elapsed, error_code=exc.code, budget=budget)
            exc.details.update(
                {
                    "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
                    "backend_attempts": list(attempts or []),
                }
            )
            raise
        elapsed = time.perf_counter() - started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        _attempt(
            attempts,
            backend=backend,
            status="succeeded" if conversion.returncode == 0 else "failed",
            elapsed_seconds=elapsed,
            error_code=None if conversion.returncode == 0 else "E_RENDER_FAILED",
            budget=budget,
        )
    if conversion.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise AwesomeBenziError(
            "E_RENDER_FAILED",
            "render",
            "LibreOffice could not render the staged DOCX",
            recoverability="environment",
            details={"returncode": conversion.returncode, "stderr": conversion.stderr[-2000:]},
        )
    prefix = pages_dir / "page"
    backend = "pdftoppm-raster"
    started = time.perf_counter()
    try:
        raster = run_bounded_process(
            [pdftoppm, "-png", "-r", "144", str(pdf_path), str(prefix)],
            timeout_seconds=bounded_timeout_seconds(
                budget,
                timeout_seconds,
                stage="render",
                backend=backend,
            ),
            stage="render",
            backend=backend,
        )
    except AwesomeBenziError as exc:
        elapsed = time.perf_counter() - started
        consume_execution_budget(budget, elapsed) if budget is not None else None
        _attempt(attempts, backend=backend, status="timeout", elapsed_seconds=elapsed, error_code=exc.code, budget=budget)
        exc.details.update(
            {
                "remaining_budget_ms": budget.get("remaining_ms") if budget is not None else None,
                "backend_attempts": list(attempts or []),
            }
        )
        raise
    elapsed = time.perf_counter() - started
    consume_execution_budget(budget, elapsed) if budget is not None else None
    _attempt(
        attempts,
        backend=backend,
        status="succeeded" if raster.returncode == 0 else "failed",
        elapsed_seconds=elapsed,
        error_code=None if raster.returncode == 0 else "E_RENDER_FAILED",
        budget=budget,
    )
    pages = sorted(pages_dir.glob("page-*.png"))
    if raster.returncode != 0 or not pages:
        raise AwesomeBenziError(
            "E_RENDER_FAILED",
            "render",
            "PDF pages could not be rasterized",
            recoverability="environment",
            details={"returncode": raster.returncode, "stderr": raster.stderr[-2000:]},
        )
    page_records: list[dict[str, Any]] = []
    for index, page in enumerate(pages, start=1):
        try:
            with Image.open(page) as image:
                image.verify()
            with Image.open(page) as image:
                width, height = image.size
        except Exception as exc:
            raise AwesomeBenziError("E_RENDER_FAILED", "render", f"rendered page is unreadable: {page}", details={"error": str(exc)}) from exc
        if width < 500 or height < 500:
            raise AwesomeBenziError("E_RENDER_FAILED", "render", f"rendered page dimensions are implausible: {page}")
        page_records.append({"page": index, "path": str(page), "width": width, "height": height, "sha256": sha256(page)})
    report = {
        "schema_type": "render-report",
        "schema_version": 1,
        "gate": "awaiting-visual-review",
        "docx_path": str(docx_path),
        "docx_sha256": sha256(docx_path),
        "pdf_path": str(pdf_path),
        "page_count": len(page_records),
        "pages": page_records,
    }
    (qa_dir / "render.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def validate_render_review(
    review: dict[str, Any],
    render_report: dict[str, Any],
    session_id: str,
    expected_draft_sha256: str | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    required_checks = {
        "cropping",
        "overlap",
        "missing_glyphs",
        "font_substitution",
        "broken_tables",
        "blank_pages",
        "header_footer_drift",
    }
    if review.get("schema_type") != "render-review" or int(review.get("schema_version", 0)) != 1:
        issues.append({"rule_id": "QG-RENDER-005", "message": "invalid render-review schema"})
    if review.get("session_id") != session_id:
        issues.append({"rule_id": "QG-RENDER-005", "message": "render review session mismatch"})
    if review.get("staged_docx_sha256") != render_report.get("docx_sha256"):
        issues.append({"rule_id": "QG-RENDER-005", "message": "render review DOCX hash mismatch"})
    try:
        review_page_count = int(review.get("page_count", -1))
        report_page_count = int(render_report.get("page_count", 0))
    except (TypeError, ValueError):
        issues.append({"rule_id": "QG-RENDER-005", "message": "render review page count must be an integer"})
    else:
        if review_page_count != report_page_count:
            issues.append({"rule_id": "QG-RENDER-005", "message": "render review page count mismatch"})
    if expected_draft_sha256 is not None and review.get("draft_sha256") != expected_draft_sha256:
        issues.append({"rule_id": "QG-RENDER-005", "message": "render review frozen draft hash mismatch"})
    expected_pages = set(range(1, int(render_report.get("page_count", 0)) + 1))
    reviewed_pages = set()
    for page in review.get("reviewed_pages", []) if isinstance(review.get("reviewed_pages"), list) else []:
        try:
            reviewed_pages.add(int(page))
        except (TypeError, ValueError):
            pass
    if reviewed_pages != expected_pages:
        issues.append(
            {
                "rule_id": "QG-RENDER-003",
                "message": "every rendered page must be reviewed exactly once",
                "expected_pages": sorted(expected_pages),
                "reviewed_pages": sorted(reviewed_pages),
            }
        )
    checks = review.get("checks", {})
    if not isinstance(checks, dict) or set(checks) != required_checks or any(
        checks.get(name) != "passed" for name in required_checks
    ):
        issues.append(
            {
                "rule_id": "QG-RENDER-004",
                "message": "render review must record a passed status for every visual defect class",
                "required_checks": sorted(required_checks),
                "actual_checks": checks,
            }
        )
    visual_issues = review.get("issues", [])
    if review.get("gate") != "passed" or visual_issues:
        issues.append({"rule_id": "QG-RENDER-004", "message": "visual review did not pass", "visual_issues": visual_issues})
    return {
        "schema_type": "render-review-validation",
        "schema_version": 1,
        "gate": "blocked" if issues else "passed",
        "issues": issues,
        "reviewed_pages": sorted(reviewed_pages),
    }
