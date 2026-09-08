"""Best-effort git worktree lock for active pipelines (S8170.6, ADR-094).

`git worktree lock` only protects against concurrent cleanup
(worktree remove/prune) — not edits nor ref operations (research F2).
It complements the session lease as defense in depth. Lock and unlock
never fail the pipeline flow: any git error degrades to a log warning.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_GIT_TIMEOUT = 10

DEFAULT_STALE_AFTER_HOURS = 24.0


def _git(args: list[str], cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=_GIT_TIMEOUT,
    )


def _is_linked_worktree(cwd: str) -> bool:
    """True when cwd lives in a linked worktree (not the main checkout)."""
    git_dir = _git(["rev-parse", "--git-dir"], cwd)
    common_dir = _git(["rev-parse", "--git-common-dir"], cwd)
    if git_dir.returncode != 0 or common_dir.returncode != 0:
        return False
    resolved_git = Path(cwd, git_dir.stdout.strip()).resolve()
    resolved_common = Path(cwd, common_dir.stdout.strip()).resolve()
    return resolved_git != resolved_common


def _resolve_toplevel(cwd: str) -> str | None:
    """Resolve cwd's git toplevel path, or None on any git failure."""
    toplevel = _git(["rev-parse", "--show-toplevel"], cwd)
    if toplevel.returncode != 0:
        return None
    return toplevel.stdout.strip()


def lock_worktree(cwd: str, run_id: str) -> str | None:
    """Lock the worktree containing cwd. Returns the locked path or None.

    None means: empty cwd, main checkout, not a git repo, or git failed —
    all non-fatal by design (AC5).
    """
    if not cwd:
        return None
    try:
        if not _is_linked_worktree(cwd):
            return None
        path = _resolve_toplevel(cwd)
        if not path:
            return None
        result = _git(["worktree", "lock", "--reason", f"pipeline {run_id}", path], cwd)
        if result.returncode != 0:
            _log.warning(
                "git worktree lock failed for %s: %s", path, result.stderr.strip()
            )
            return None
        return path
    except Exception:  # noqa: BLE001 — best-effort by design
        _log.warning("worktree lock skipped", exc_info=True)
        return None


def unlock_worktree(path: str | None) -> bool:
    """Unlock a previously locked worktree. Best-effort, returns success."""
    if not path:
        return False
    try:
        result = _git(["worktree", "unlock", path], path)
        if result.returncode != 0:
            _log.warning(
                "git worktree unlock failed for %s: %s", path, result.stderr.strip()
            )
            return False
        return True
    except Exception:  # noqa: BLE001 — best-effort by design
        _log.warning("worktree unlock skipped", exc_info=True)
        return False


def reap_orphan_worktree_locks(
    cwd: str,
    runs: list[dict[str, Any]],
    *,
    lease_is_dead: bool = False,
    stale_after_hours: float = DEFAULT_STALE_AFTER_HOURS,
    now: datetime | None = None,
) -> list[str]:
    """Best-effort reap of orphaned `git worktree lock`s targeting cwd's worktree.

    Never touches a `paused` run — pause is intentional, not abandonment.
    Only `status == "started"` runs whose `metadata.locked_worktree` resolves
    to cwd's git toplevel are candidates. Reaped when either:
      - `lease_is_dead` is True (caller already proved the prior lease
        holder's PID is dead via lease_enforcement), or
      - (fallback) the run predates any lease-derived confirmation and has
        been `started` longer than `stale_after_hours`.

    Q1 (ar.md, RAISE-11089): the staleness fallback is a deliberate, narrow
    tradeoff — it is the only path that can reap without a proven-dead PID.
    It is kept (not dropped) as a backstop for runs whose worktree has no
    surviving lease row at all (pre-lease-tracking runs, or a GC'd lease),
    per analysis.md. It is deliberately *not* a general override of a live
    lease: a foreign, live lease holder can never reach this function in
    the first place (lease_enforcement.enforce() rejects pipeline_start
    outright before any reap call — see mcp_tools_pipeline.py), and the
    caller wires this reaper *after* the dedup early-return (R1, ar.md), so
    a session resuming its own matching (issue, pipeline) run never reaches
    reap either. A worktree has exactly one lease row, so any *other*
    `started` run sharing this cwd's `locked_worktree` that isn't caught by
    dedup implies its original session is no longer the lease holder —
    the remaining exposure is intentionally accepted, not an oversight.

    Returns the run_ids whose lock was released (best-effort — degrades to
    a log warning on git failure, matching `unlock_worktree`'s contract).
    """
    if not cwd:
        return []
    try:
        toplevel = _resolve_toplevel(cwd)
    except Exception:  # noqa: BLE001 — best-effort by design
        _log.warning("orphan lock reap skipped (toplevel resolution)", exc_info=True)
        return []
    if not toplevel:
        return []

    moment = now or datetime.now(UTC)
    reaped: list[str] = []
    for run in runs:
        locked = _matching_locked_worktree(run, toplevel)
        if locked is None:
            continue
        if not _is_orphan(
            run,
            lease_is_dead=lease_is_dead,
            stale_after_hours=stale_after_hours,
            moment=moment,
        ):
            continue
        if unlock_worktree(locked):
            reaped.append(run.get("run_id", ""))

    return reaped


def _matching_locked_worktree(run: dict[str, Any], toplevel: str) -> str | None:
    """Return run's locked_worktree path when it matches toplevel, else None."""
    if run.get("status") not in ("started", "running"):
        return None
    locked = (run.get("metadata") or {}).get("locked_worktree")
    return locked if locked == toplevel else None


def _is_orphan(
    run: dict[str, Any],
    *,
    lease_is_dead: bool,
    stale_after_hours: float,
    moment: datetime,
) -> bool:
    """True when the run's lock should be reaped (lease-dead or stale fallback)."""
    if lease_is_dead:
        return True
    started_at = run.get("started_at")
    started = _parse_started_at(started_at) if started_at else None
    if started is None:
        return False
    return (moment - started) > timedelta(hours=stale_after_hours)


def _parse_started_at(value: str) -> datetime | None:
    try:
        started = datetime.fromisoformat(value)
    except ValueError:
        return None
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    return started
