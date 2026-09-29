"""Cockpit domain types — V2 SessionState enum and classification."""

from __future__ import annotations

from enum import StrEnum

STALE_THRESHOLD_HOURS: float = 2.0

_BLOCKED_PHASES = frozenset({"error", "blocked"})
_TERMINAL_PHASES = frozenset({"completed", "done", "closed"})


class SessionState(StrEnum):
    """Unified display state for a cockpit session entry."""

    WORKING = "working"
    PAUSED = "paused"
    BLOCKED = "blocked"
    DONE = "done"
    ERROR = "error"
    IDLE = "idle"


def classify_session_state(
    *,
    worktree_status: str,
    lease_alive: bool,
    heartbeat_age_hours: float | None,
    pipeline_phase: str | None,
    paused: bool = False,
) -> SessionState:
    """Map worktree + lease + pipeline inputs to a single display state.

    ``paused`` is explicit user intent (RAISE-16708, D-S3.3) — when the
    lease is alive and paused is set, it outranks every derived state
    (BLOCKED, stale-heartbeat PAUSED, WORKING). Defaults to False so all
    existing callers are unaffected.

    Pure function — no I/O.
    """
    if worktree_status == "closed":
        return SessionState.DONE

    if lease_alive:
        if paused:
            return SessionState.PAUSED
        if pipeline_phase in _BLOCKED_PHASES:
            return SessionState.BLOCKED
        if (
            heartbeat_age_hours is not None
            and heartbeat_age_hours > STALE_THRESHOLD_HOURS
        ):
            return SessionState.PAUSED
        return SessionState.WORKING

    if pipeline_phase in _TERMINAL_PHASES:
        return SessionState.DONE

    # No lease, pipeline_phase == "none" → never had a session, just registered
    if pipeline_phase == "none":
        return SessionState.IDLE

    # No lease, pipeline_phase is None → had a session but orphaned
    if pipeline_phase is None:
        if worktree_status == "closed":
            return SessionState.DONE
        return SessionState.ERROR

    # No lease but active pipeline phase → error (orphaned mid-work)
    return SessionState.ERROR
