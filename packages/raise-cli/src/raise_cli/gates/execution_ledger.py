"""Gate execution ledger — RAISE-16768.

Cross-process ledger providing at-most-once gate execution semantics and
durable outcome persistence. Before a gate subprocess starts, the caller
registers an execution. If an execution with the same (gate_id, working_dir,
scope) key already exists and is alive or completed, the existing entry is
returned instead of starting a new subprocess.

Follows the same file-locking and dead-PID-reaping pattern as worker_budget.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any
from uuid import uuid4

_logger = logging.getLogger(__name__)


class ExecutionStatus:
    """Terminal states for a ledger entry."""

    RUNNING = "running"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ExecutionOutcome:
    """Durable gate result stored in the ledger."""

    passed: bool
    message: str
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionEntry:
    """Snapshot of a ledger entry returned by queries."""

    execution_id: str
    gate_id: str
    working_dir: str
    scope: str
    pid: int
    status: str
    result: ExecutionOutcome | None


def _ledger_file() -> Path:
    override = os.environ.get("RAISE_GATE_EXECUTION_LEDGER", "").strip()
    if override:
        return Path(override)
    from raise_cli.config.paths import get_global_rai_dir

    return get_global_rai_dir() / "gate-executions.json"


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _lock_exclusive(fh: IO[str]) -> None:
    try:
        import fcntl
    except ModuleNotFoundError:
        pass
    else:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        return
    try:
        import msvcrt
    except ModuleNotFoundError:
        _logger.debug("execution_ledger: no file locking on this platform")
        return
    fh.seek(0)
    win: Any = msvcrt
    win.locking(fh.fileno(), win.LK_LOCK, 1)


def _unlock(fh: IO[str]) -> None:
    with contextlib.suppress(OSError, ModuleNotFoundError):
        try:
            import fcntl
        except ModuleNotFoundError:
            import msvcrt

            fh.seek(0)
            win: Any = msvcrt
            win.locking(fh.fileno(), win.LK_UNLCK, 1)
        else:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def _locked() -> Iterator[IO[str]]:
    path = _ledger_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(path, "a+", encoding="utf-8")  # noqa: SIM115
    try:
        _lock_exclusive(fh)
        yield fh
    finally:
        _unlock(fh)
        fh.close()


def _load(fh: IO[str]) -> dict[str, Any]:
    fh.seek(0)
    raw = fh.read()
    if not raw.strip():
        return {"executions": {}}
    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        return {"executions": {}}
    data.setdefault("executions", {})
    return data


def _save(fh: IO[str], data: dict[str, Any]) -> None:
    fh.seek(0)
    fh.truncate()
    fh.write(json.dumps(data))
    fh.flush()


def _dedup_key(gate_id: str, working_dir: str, scope: str) -> str:
    return f"{gate_id}:{working_dir}:{scope}"


def _outcome_to_dict(outcome: ExecutionOutcome) -> dict[str, Any]:
    return {
        "passed": outcome.passed,
        "message": outcome.message,
        "details": list(outcome.details),
    }


def _dict_to_outcome(d: dict[str, Any]) -> ExecutionOutcome:
    return ExecutionOutcome(
        passed=d["passed"],
        message=d["message"],
        details=tuple(d.get("details", ())),
    )


def _entry_from_dict(eid: str, d: dict[str, Any]) -> ExecutionEntry:
    result = _dict_to_outcome(d["result"]) if d.get("result") else None
    return ExecutionEntry(
        execution_id=eid,
        gate_id=d["gate_id"],
        working_dir=d["working_dir"],
        scope=d["scope"],
        pid=d["pid"],
        status=d["status"],
        result=result,
    )


def register(gate_id: str, working_dir: str, scope: str) -> str:
    """Register a gate execution. Returns the existing ID if one is active."""
    key = _dedup_key(gate_id, working_dir, scope)
    with _locked() as fh:
        data = _load(fh)
        execs: dict[str, Any] = data["executions"]

        for eid, entry in list(execs.items()):
            entry_key = _dedup_key(
                entry["gate_id"], entry["working_dir"], entry["scope"]
            )
            if entry_key != key:
                continue
            if entry["status"] == ExecutionStatus.COMPLETED:
                return eid
            if _pid_alive(int(entry["pid"])):
                return eid
            del execs[eid]

        eid = uuid4().hex
        execs[eid] = {
            "gate_id": gate_id,
            "working_dir": working_dir,
            "scope": scope,
            "pid": os.getpid(),
            "status": ExecutionStatus.RUNNING,
            "result": None,
        }
        _save(fh, data)
        return eid


def find_active(gate_id: str, working_dir: str, scope: str) -> ExecutionEntry | None:
    """Find an active (running with live PID, or completed) execution."""
    key = _dedup_key(gate_id, working_dir, scope)
    with _locked() as fh:
        data = _load(fh)
        execs: dict[str, Any] = data["executions"]
        dirty = False

        for eid, entry in list(execs.items()):
            entry_key = _dedup_key(
                entry["gate_id"], entry["working_dir"], entry["scope"]
            )
            if entry_key != key:
                continue
            if entry["status"] == ExecutionStatus.COMPLETED:
                return _entry_from_dict(eid, entry)
            if _pid_alive(int(entry["pid"])):
                return _entry_from_dict(eid, entry)
            del execs[eid]
            dirty = True

        if dirty:
            _save(fh, data)
        return None


def complete(execution_id: str, outcome: ExecutionOutcome) -> None:
    """Record the terminal outcome for a registered execution."""
    with _locked() as fh:
        data = _load(fh)
        entry = data["executions"].get(execution_id)
        if entry is None:
            return
        entry["status"] = ExecutionStatus.COMPLETED
        entry["result"] = _outcome_to_dict(outcome)
        _save(fh, data)


def get_outcome(execution_id: str) -> ExecutionOutcome | None:
    """Retrieve the outcome for a completed execution. None if still running."""
    with _locked() as fh:
        data = _load(fh)
        entry = data["executions"].get(execution_id)
        if entry is None or entry["status"] != ExecutionStatus.COMPLETED:
            return None
        return _dict_to_outcome(entry["result"])


def reap_dead() -> int:
    """Remove ledger entries held by dead PIDs. Returns count reaped."""
    with _locked() as fh:
        data = _load(fh)
        execs: dict[str, Any] = data["executions"]
        dead = [
            eid
            for eid, entry in execs.items()
            if entry["status"] == ExecutionStatus.RUNNING
            and not _pid_alive(int(entry["pid"]))
        ]
        for eid in dead:
            del execs[eid]
        if dead:
            _save(fh, data)
        return len(dead)


def clear_for_key(gate_id: str, working_dir: str, scope: str) -> None:
    """Remove all entries for a dedup key. Used after consuming a cached result."""
    key = _dedup_key(gate_id, working_dir, scope)
    with _locked() as fh:
        data = _load(fh)
        execs: dict[str, Any] = data["executions"]
        to_remove = [
            eid
            for eid, entry in execs.items()
            if _dedup_key(entry["gate_id"], entry["working_dir"], entry["scope"]) == key
        ]
        for eid in to_remove:
            del execs[eid]
        if to_remove:
            _save(fh, data)
