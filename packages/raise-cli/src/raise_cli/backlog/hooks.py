"""Backlog side-effect hooks — extracted from story/open_service.py (S15033).

Stage 2 of the ownership-flip enforcement initiative (RAISE-15027).
The canonical location for hooks that modify backlog state as a side-effect
of pipeline engine actions. Skills delegate here; they do NOT transition
backlog state directly when the engine is running.

S15036 adds:
- ``apply_transition`` — shared single-issue transition core
- ``TransitionLogEntry`` / ``log_transition`` / ``get_transition_log`` /
  ``clear_transition_log`` — in-memory audit log (Phase 1; durable persistence post-3.1.0)
- ``_pipeline_run_active`` — guard for CLI batch ops (imported by batch-transition command)
"""

from __future__ import annotations

import logging
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

_log = logging.getLogger(__name__)
_TRANSITION_TIMEOUT_S = 30


# ── TransitionLogEntry + in-memory log (S15036 AC2) ──────────────────


class TransitionLogEntry(BaseModel):
    """Audit record for a single engine-initiated backlog transition."""

    timestamp: str
    jira_key: str
    target_status: str
    outcome: Literal["ok", "fail"]
    error_detail: str | None = None


_transition_log: list[TransitionLogEntry] = []


def log_transition(entry: TransitionLogEntry) -> None:
    """Append *entry* to the in-memory transition log."""
    _transition_log.append(entry)


def get_transition_log() -> list[TransitionLogEntry]:
    """Return a copy of the current in-memory transition log."""
    return list(_transition_log)


def clear_transition_log() -> None:
    """Empty the in-memory transition log (use between pipeline runs / tests)."""
    _transition_log.clear()


# ── apply_transition (S15036 AC1) ────────────────────────────────────


def apply_transition(project: Path, jira_key: str, status: str) -> str | None:
    """Transition a single backlog item and log the attempt.

    Calls ``rai backlog transition {jira_key} {status}`` via subprocess.
    Appends a :class:`TransitionLogEntry` on every call (ok or fail).
    Returns ``None`` on success, or an error string on failure.
    """
    timestamp = datetime.now(UTC).isoformat()
    try:
        proc = subprocess.run(
            ["rai", "backlog", "transition", jira_key, status],
            capture_output=True,
            text=True,
            timeout=_TRANSITION_TIMEOUT_S,
            check=False,
            cwd=project,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log_transition(
            TransitionLogEntry(
                timestamp=timestamp,
                jira_key=jira_key,
                target_status=status,
                outcome="fail",
                error_detail=str(exc),
            )
        )
        return f"transition failed: {exc}"
    if proc.returncode != 0:
        error_detail = proc.stderr.strip() or proc.stdout.strip() or None
        log_transition(
            TransitionLogEntry(
                timestamp=timestamp,
                jira_key=jira_key,
                target_status=status,
                outcome="fail",
                error_detail=error_detail,
            )
        )
        return "transition failed: " + (error_detail or "(no output)")
    log_transition(
        TransitionLogEntry(
            timestamp=timestamp,
            jira_key=jira_key,
            target_status=status,
            outcome="ok",
        )
    )
    return None


# ── pipeline_run_active (S15036 AC4) ─────────────────────────────────


def pipeline_run_active() -> bool:
    """Return True when any pipeline run with an active status exists.

    Used by the CLI ``batch-transition`` command as an engine-ownership guard.
    Returns False (fail-open) when the store is unavailable or raises any
    exception — preserving the RAISE-10966 invariant that CLI flows are
    never blocked by guard errors.
    """
    try:
        from raise_cli.adapters.sync import run_sync
        from raise_cli.pipeline.run_store import get_run_store
        from raise_core.workflow.status_sets import ACTIVE_RUN_STATUSES

        store = get_run_store()
        # RAISE-15201: _run_sync is safe from both sync (CLI) and async
        # (MCP server) callers — bare asyncio.run() raised RuntimeError under
        # an active loop, which fail-open silently swallowed, defeating the guard.
        runs: list[dict[str, object]] = run_sync(store.list_runs())
        return any(str(r.get("status", "")) in ACTIVE_RUN_STATUSES for r in runs)
    except Exception:  # noqa: BLE001 — fail-open per RAISE-10966
        _log.debug("pipeline_run_active: store unavailable — fail-open", exc_info=True)
        return False


def assign_fix_version(project: Path, jira_key: str, version: str) -> str | None:
    """Assign ``fixVersion`` via the ``rai backlog update`` JSON escape hatch.

    Uses the existing ``-F 'fixVersions=[...]'`` path (system field), so no
    new CLI surface is introduced. Returns an error message on failure or
    ``None`` on success (RAISE-10966).

    Extracted from ``raise_cli.story.open_service._assign_fix_version``
    (RAISE-15033) so the engine can own fixVersion assignment and skills
    can delegate without duplicating the logic.
    """
    payload = f'fixVersions=[{{"name": "{version}"}}]'
    try:
        proc = subprocess.run(
            ["rai", "backlog", "update", jira_key, "-F", payload],
            capture_output=True,
            text=True,
            timeout=_TRANSITION_TIMEOUT_S,
            check=False,
            cwd=project,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"fixVersion assign failed: {exc}"
    if proc.returncode != 0:
        return "fixVersion assign failed: " + (
            proc.stderr.strip() or proc.stdout.strip()
        )
    return None
