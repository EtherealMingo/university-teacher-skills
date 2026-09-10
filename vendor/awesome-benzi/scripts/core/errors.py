"""Typed runtime errors and CLI exit-code policy."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AwesomeBenziError(Exception):
    code: str
    stage: str
    message: str
    path: str | None = None
    field_name: str | None = None
    recoverability: str = "fatal"
    user_action_required: bool = False
    suggested_action: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)

    @property
    def exit_code(self) -> int:
        if self.recoverability == "environment":
            return 3
        if self.recoverability == "internal-invariant":
            return 4
        return 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "awesome-benzi-error",
            "schema_version": 1,
            "code": self.code,
            "stage": self.stage,
            "message": self.message,
            "path": self.path,
            "field": self.field_name,
            "recoverability": self.recoverability,
            "user_action_required": self.user_action_required,
            "suggested_action": self.suggested_action,
            "details": self.details,
        }


def ensure_utf8_stdout() -> None:
    """Force UTF-8 on stdout so JSON output never hits the console code page.

    On Chinese Windows the default stdout encoding is GBK and characters such
    as a UTF-8 BOM or rare glyphs make json.dump crash with UnicodeEncodeError.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass


def path_error(code: str, path: Path, message: str) -> AwesomeBenziError:
    return AwesomeBenziError(
        code=code,
        stage="path",
        message=message,
        path=str(path),
        recoverability="user-input",
        user_action_required=True,
        suggested_action="Provide an existing user-material path outside the Skill package.",
    )


def cli_error_result(exc: Exception, stage: str = "runtime") -> tuple[dict[str, Any], int]:
    if isinstance(exc, AwesomeBenziError):
        return exc.to_dict(), exc.exit_code
    wrapped = AwesomeBenziError(
        code="E_INTERNAL",
        stage=stage,
        message=str(exc),
        recoverability="internal-invariant",
        suggested_action="Inspect stderr diagnostics and the failing stage.",
    )
    return wrapped.to_dict(), wrapped.exit_code
