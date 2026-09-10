"""Path protection and atomic delivery."""

from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import tempfile
from pathlib import Path

from .errors import AwesomeBenziError, path_error


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_skill_package(path: Path) -> bool:
    skill = path / "SKILL.md"
    runtime = path / "scripts" / "runtime.py"
    if not skill.is_file() or not runtime.is_file():
        return False
    try:
        return "name: awesome-benzi" in skill.read_text(encoding="utf-8", errors="ignore")[:4096]
    except OSError:
        return False


def protected_owner(path: Path, active_skill_root: Path) -> Path | None:
    resolved = path.expanduser().resolve()
    if is_inside(resolved, active_skill_root):
        return active_skill_root.resolve()
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if is_skill_package(candidate):
            return candidate.resolve()
    return None


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name != "nt":
        return False
    try:
        return bool(path.lstat().st_file_attributes & 0x400)
    except (AttributeError, OSError):
        return False


def assert_user_path(path: Path, skill_root: Path, *, must_exist: bool = True) -> Path:
    expanded = path.expanduser()
    if must_exist and not expanded.exists():
        raise path_error("E_PATH_NOT_FOUND", expanded, f"path does not exist: {expanded}")
    current = expanded.absolute()
    for candidate in (current, *current.parents):
        if candidate.exists() and _is_reparse_point(candidate):
            raise path_error("E_PATH_ESCAPE", current, f"symbolic link or reparse point is not allowed: {candidate}")
    resolved = current.resolve()
    if protected_owner(resolved, skill_root) is not None:
        raise path_error("E_PATH_PROTECTED", resolved, f"awesome-benzi package path is protected: {resolved}")
    return resolved


def assert_session_path(path: Path, session_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not is_inside(resolved, session_root):
        raise AwesomeBenziError(
            "E_PATH_ESCAPE",
            "session",
            f"session path escapes its root: {resolved}",
            path=str(resolved),
            recoverability="internal-invariant",
        )
    return resolved


def safe_output_path(output_dir: Path, stem: str, requested_name: str | None, skill_root: Path) -> Path:
    directory = assert_user_path(output_dir, skill_root)
    if not directory.is_dir():
        raise path_error("E_PATH_NOT_FOUND", directory, "output directory must already exist")
    name = requested_name or f"{stem}-完成稿.docx"
    if Path(name).name != name or not name.lower().endswith(".docx"):
        raise path_error("E_PATH_ESCAPE", directory / name, "output name must be one DOCX filename")
    candidate = directory / name
    if not candidate.exists():
        return candidate
    base = Path(name).stem
    for index in range(2, 10000):
        candidate = directory / f"{base}-{index}.docx"
        if not candidate.exists():
            return candidate
    raise AwesomeBenziError("E_OUTPUT_EXISTS", "delivery", "no stable output suffix is available")


def atomic_commit(source: Path, destination: Path) -> str:
    source = source.resolve()
    destination = destination.resolve()
    source_hash = sha256(source)
    try:
        os.replace(source, destination)
    except OSError:
        hidden = destination.with_name(f".{destination.name}.{secrets.token_hex(8)}.tmp")
        try:
            shutil.copy2(source, hidden)
            try:
                with hidden.open("r+b") as handle:
                    os.fsync(handle.fileno())
            except (OSError, ValueError):
                pass
            if sha256(hidden) != source_hash:
                raise AwesomeBenziError("E_ATOMIC_COMMIT_FAILED", "delivery", "cross-volume copy hash mismatch")
            os.replace(hidden, destination)
        finally:
            if hidden.exists():
                hidden.unlink()
    if sha256(destination) != source_hash:
        destination.unlink(missing_ok=True)
        raise AwesomeBenziError("E_ATOMIC_COMMIT_FAILED", "delivery", "delivered file hash mismatch")
    return source_hash
