"""Temporary session lifecycle and transition validation."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from .contracts import SessionState
from .errors import AwesomeBenziError
from .paths import assert_session_path

SESSION_PREFIX = "awesome-benzi-session-"
DEFAULT_EXECUTION_BUDGET_SECONDS = 300
DEFAULT_BACKEND_TIMEOUT_SECONDS = 45
DEFAULT_SESSION_LOCK_LEASE_SECONDS = 300
MAX_CAPTURE_BYTES = 1024 * 1024

TRANSITIONS: dict[SessionState, set[SessionState]] = {
    SessionState.NEW: {SessionState.SCANNED, SessionState.BLOCKED},
    SessionState.SCANNED: {SessionState.ROUTED, SessionState.BLOCKED},
    SessionState.ROUTED: {SessionState.PREPARED, SessionState.BLOCKED},
    SessionState.PREPARED: {SessionState.WAITING_FOR_USER, SessionState.PLANNED, SessionState.BLOCKED},
    SessionState.WAITING_FOR_USER: {SessionState.PLANNED, SessionState.BLOCKED},
    SessionState.PLANNED: {SessionState.DRAFTING, SessionState.BLOCKED},
    SessionState.DRAFTING: {SessionState.CONTENT_PASSED, SessionState.BLOCKED},
    SessionState.CONTENT_PASSED: {SessionState.FROZEN, SessionState.DRAFTING, SessionState.BLOCKED},
    SessionState.FROZEN: {SessionState.DOCX_STAGED, SessionState.DRAFTING, SessionState.BLOCKED},
    SessionState.DOCX_STAGED: {SessionState.PARITY_PASSED, SessionState.DRAFTING, SessionState.BLOCKED},
    SessionState.PARITY_PASSED: {SessionState.STRUCTURE_PASSED, SessionState.FROZEN, SessionState.BLOCKED},
    SessionState.STRUCTURE_PASSED: {SessionState.RENDER_REVIEW_PENDING, SessionState.DELIVERED, SessionState.FROZEN, SessionState.BLOCKED},
    SessionState.RENDER_REVIEW_PENDING: {SessionState.RENDER_PASSED, SessionState.FROZEN, SessionState.BLOCKED},
    SessionState.RENDER_PASSED: {SessionState.DELIVERED, SessionState.BLOCKED},
    SessionState.DELIVERED: {SessionState.CLEANED},
    SessionState.BLOCKED: {SessionState.CLEANED},
    SessionState.CLEANED: set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_execution_budget(limit_seconds: int | float = DEFAULT_EXECUTION_BUDGET_SECONDS) -> dict[str, Any]:
    limit = max(1.0, float(limit_seconds))
    return {
        "schema_type": "execution-budget",
        "schema_version": 1,
        "limit_ms": round(limit * 1000, 2),
        "consumed_ms": 0.0,
        "remaining_ms": round(limit * 1000, 2),
    }


def normalize_execution_budget(
    value: dict[str, Any] | None,
    default_seconds: int | float = DEFAULT_EXECUTION_BUDGET_SECONDS,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        return new_execution_budget(default_seconds)
    limit_ms = max(1000.0, float(value.get("limit_ms", float(default_seconds) * 1000)))
    consumed_ms = max(0.0, min(float(value.get("consumed_ms", 0.0)), limit_ms))
    return {
        "schema_type": "execution-budget",
        "schema_version": 1,
        "limit_ms": round(limit_ms, 2),
        "consumed_ms": round(consumed_ms, 2),
        "remaining_ms": round(max(0.0, limit_ms - consumed_ms), 2),
    }


def consume_execution_budget(
    budget: dict[str, Any],
    elapsed_seconds: int | float,
) -> dict[str, Any]:
    normalized = normalize_execution_budget(budget)
    normalized["consumed_ms"] = round(
        min(normalized["limit_ms"], normalized["consumed_ms"] + max(0.0, float(elapsed_seconds)) * 1000),
        2,
    )
    normalized["remaining_ms"] = round(max(0.0, normalized["limit_ms"] - normalized["consumed_ms"]), 2)
    budget.clear()
    budget.update(normalized)
    return budget


def remaining_budget_seconds(budget: dict[str, Any] | None) -> float:
    normalized = normalize_execution_budget(budget)
    return max(0.0, float(normalized["remaining_ms"]) / 1000.0)


def bounded_timeout_seconds(
    budget: dict[str, Any] | None,
    requested_seconds: int | float,
    *,
    stage: str,
    backend: str,
) -> float:
    remaining = remaining_budget_seconds(budget)
    if remaining <= 0:
        raise AwesomeBenziError(
            "E_TIMEOUT",
            stage,
            f"execution budget was exhausted before starting {backend}",
            recoverability="environment",
            suggested_action="Resume with a larger --budget-seconds value or use the indicated fallback.",
            details={"backend": backend, "remaining_ms": 0},
        )
    return max(0.1, min(float(requested_seconds), remaining))


def _read_tail(handle: Any, limit: int = MAX_CAPTURE_BYTES) -> bytes:
    handle.flush()
    size = handle.seek(0, os.SEEK_END)
    handle.seek(max(0, size - limit), os.SEEK_SET)
    return handle.read(limit)


def _terminate_process_tree(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            pass
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                process.kill()
        except OSError:
            process.kill()
    try:
        process.wait(timeout=2)
    except subprocess.SubprocessError:
        process.kill()
        try:
            process.wait(timeout=2)
        except subprocess.SubprocessError:
            pass


def run_bounded_process(
    command: Iterable[str],
    *,
    timeout_seconds: int | float,
    stage: str,
    backend: str,
    text: bool = True,
    encoding: str = "utf-8",
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[Any]:
    args = [str(item) for item in command]
    creationflags = 0
    popen_options: dict[str, Any] = {}
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    else:
        popen_options["start_new_session"] = True
    started = time.perf_counter()
    with tempfile.TemporaryFile() as stdout_handle, tempfile.TemporaryFile() as stderr_handle:
        process = subprocess.Popen(
            args,
            cwd=str(cwd) if cwd else None,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=creationflags,
            **popen_options,
        )
        try:
            process.wait(timeout=max(0.1, float(timeout_seconds)))
        except subprocess.TimeoutExpired as exc:
            _terminate_process_tree(process)
            raise AwesomeBenziError(
                "E_TIMEOUT",
                stage,
                f"{backend} exceeded its {round(float(timeout_seconds), 2)} second limit",
                recoverability="environment",
                suggested_action="Use the next available backend or provide recovered text.",
                details={
                    "backend": backend,
                    "timeout_seconds": round(float(timeout_seconds), 2),
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            ) from exc
        except BaseException:
            _terminate_process_tree(process)
            raise
        stdout = _read_tail(stdout_handle)
        stderr = _read_tail(stderr_handle)
    if text:
        return subprocess.CompletedProcess(
            args,
            process.returncode,
            stdout.decode(encoding, errors="replace"),
            stderr.decode(encoding, errors="replace"),
        )
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def create_session(
    request: str = "",
    root: Path | None = None,
    budget_seconds: int | float = DEFAULT_EXECUTION_BUDGET_SECONDS,
) -> Path:
    parent = root or Path(tempfile.gettempdir())
    session = parent / f"{SESSION_PREFIX}{secrets.token_urlsafe(18)}"
    session.mkdir(mode=0o700, parents=False, exist_ok=False)
    for name in ("source", "schema", "draft", "build", "qa", "qa/pages"):
        (session / name).mkdir(mode=0o700)
    manifest = {
        "schema_type": "session",
        "schema_version": 1,
        "session_id": session.name.removeprefix(SESSION_PREFIX),
        "request": request,
        "state": SessionState.NEW.value,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "root": str(session),
        "execution_budget": new_execution_budget(budget_seconds),
    }
    write_manifest(session, manifest)
    return session


def manifest_path(session: Path) -> Path:
    return session / "session.json"


def read_manifest(session_or_manifest: Path) -> dict[str, Any]:
    raw = session_or_manifest.expanduser().resolve()
    path = raw if raw.is_file() else manifest_path(raw)
    data = json.loads(path.read_text(encoding="utf-8"))
    root = Path(data["root"]).resolve()
    assert_session_path(path, root)
    if root.name != f"{SESSION_PREFIX}{data['session_id']}":
        raise AwesomeBenziError("E_SESSION_CORRUPT", "session", "session identity mismatch", recoverability="internal-invariant")
    return data


def write_manifest(session: Path, data: dict[str, Any]) -> None:
    session = session.resolve()
    data["root"] = str(session)
    data["updated_at"] = utc_now()
    path = assert_session_path(manifest_path(session), session)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def _reclaim_stale_lock(lock: Path) -> bool:
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
        pid = int(data.get("pid", -1))
        lease_expires_epoch = float(data.get("lease_expires_epoch", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False
    if _pid_is_alive(pid) or time.time() <= lease_expires_epoch:
        return False
    try:
        lock.unlink()
        return True
    except OSError:
        return False


@contextmanager
def session_lock(
    session: Path,
    lease_seconds: int | float = DEFAULT_SESSION_LOCK_LEASE_SECONDS,
) -> Iterator[Path]:
    """Hold an exclusive, process-scoped lock with token-checked heartbeat.

    The lock file is refreshed by a daemon thread so a legitimate operation
    longer than the lease is never reclaimed. Only the token owner may delete
    the lock at the end, which prevents an expired first holder from removing
    a newer holder's lock.
    """
    session = session.expanduser().resolve()
    lock = assert_session_path(session / ".lock", session)
    descriptor: int | None = None
    heartbeat_thread = None
    token = secrets.token_hex(16)
    heartbeat_stop = threading.Event()
    lease = max(1.0, float(lease_seconds))

    def write_payload() -> None:
        nonlocal descriptor
        if descriptor is None:
            return
        payload = json.dumps(
            {
                "pid": os.getpid(),
                "token": token,
                "created_at": utc_now(),
                "heartbeat_at": utc_now(),
                "lease_expires_epoch": time.time() + lease,
            }
        ).encode("utf-8")
        os.lseek(descriptor, 0, os.SEEK_SET)
        os.write(descriptor, payload)
        os.ftruncate(descriptor, len(payload))
        os.fsync(descriptor)

    def heartbeat() -> None:
        while not heartbeat_stop.wait(max(1.0, lease / 3.0)):
            try:
                write_payload()
            except OSError:
                return

    try:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if not _reclaim_stale_lock(lock):
                raise
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        write_payload()
        heartbeat_thread = threading.Thread(target=heartbeat, name=f"benzi-lock-{session.name}", daemon=True)
        heartbeat_thread.start()
        yield lock
    except FileExistsError as exc:
        raise AwesomeBenziError(
            "E_SESSION_LOCKED",
            "session",
            "the session is already being processed",
            path=str(session),
            recoverability="retryable",
        ) from exc
    finally:
        heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=2.0)
        if descriptor is not None:
            os.close(descriptor)
            descriptor = None
        try:
            payload = json.loads(lock.read_text(encoding="utf-8"))
            if payload.get("pid") == os.getpid() and payload.get("token") == token:
                lock.unlink(missing_ok=True)
        except (OSError, ValueError, json.JSONDecodeError):
            pass
def transition(session: Path, target: SessionState, **updates: Any) -> dict[str, Any]:
    data = read_manifest(session)
    current = SessionState(data["state"])
    if target not in TRANSITIONS[current]:
        raise AwesomeBenziError(
            "E_INVALID_STATE_TRANSITION",
            "session",
            f"invalid transition {current.value} -> {target.value}",
            recoverability="internal-invariant",
        )
    data.update(updates)
    data["state"] = target.value
    write_manifest(session, data)
    return data


def cleanup_session(session: Path) -> None:
    resolved = session.expanduser().resolve()
    if not resolved.name.startswith(SESSION_PREFIX):
        raise AwesomeBenziError("E_PATH_PROTECTED", "cleanup", f"refusing to clean non-session path: {resolved}")
    data = read_manifest(resolved)
    if Path(data["root"]).resolve() != resolved:
        raise AwesomeBenziError("E_SESSION_CORRUPT", "cleanup", "session manifest root mismatch", recoverability="internal-invariant")
    shutil.rmtree(resolved, ignore_errors=False)


def cleanup_expired_sessions(max_age_seconds: int = 86_400, root: Path | None = None) -> int:
    parent = (root or Path(tempfile.gettempdir())).resolve()
    now = time.time()
    removed = 0
    for candidate in parent.glob(f"{SESSION_PREFIX}*"):
        try:
            if candidate.is_dir() and now - candidate.stat().st_mtime > max_age_seconds:
                lock = candidate / ".lock"
                if lock.exists() and not _reclaim_stale_lock(lock):
                    continue
                cleanup_session(candidate)
                removed += 1
        except (OSError, AwesomeBenziError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return removed
