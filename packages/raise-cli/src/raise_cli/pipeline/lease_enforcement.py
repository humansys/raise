"""Worktree lease enforcement for pipeline MCP tools (S8170.3, ADR-094).

Single entry point `enforce()` called by pipeline_start (acquire) and
pipeline_advance (renew). Fail-open by design: an unresolvable session_id
or an internal error degrades to a warning — a false rejection is worse
than a protection gap.
"""

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.storage.leases import Lease, LeaseHeldError, SqliteLeaseStore, pid_alive
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

_log = logging.getLogger(__name__)

EnforcementStatus = Literal["allowed", "rejected", "warning"]


@dataclass
class EnforcementDecision:
    """Outcome of a lease check for one tool invocation."""

    status: EnforcementStatus
    holder: Lease | None = None
    recovery_hint: str = ""
    warning: str = ""
    worktree_id: str = ""
    prior_holder_dead: bool = False

    def to_payload(self) -> dict[str, Any]:
        """Rejection payload for the MCP tool response."""
        payload: dict[str, Any] = {
            "status": "rejected",
            "reason": "worktree_leased",
            "recovery_hint": self.recovery_hint,
        }
        if self.holder is not None:
            payload["holder"] = {
                "session_id": self.holder.session_id,
                "pid": self.holder.pid,
                "heartbeat_at": self.holder.heartbeat_at,
            }
        return payload


def _hint(holder: Lease) -> str:
    expires = holder.expires_at
    with contextlib.suppress(ValueError):
        expires = datetime.fromisoformat(holder.expires_at).strftime("%H:%M UTC")
    return (
        f"El worktree '{holder.worktree_id}' está en uso por la sesión "
        f"'{holder.session_id}' (pid {holder.pid}). Si esa sesión murió, "
        f"el lease expira a las {expires} y el takeover es automático "
        f"cuando el PID ya no exista."
    )


def enforce(cwd: str, *, renew: bool = False) -> EnforcementDecision:
    """Check (and acquire/renew) the worktree lease for the calling session.

    Args:
        cwd: Working directory of the calling session.
        renew: True for pipeline_advance (holder heartbeat), False for
            pipeline_start (acquire).
    """
    try:
        return _enforce(cwd, renew=renew)
    except LeaseHeldError as exc:
        return EnforcementDecision(
            status="rejected", holder=exc.holder, recovery_hint=_hint(exc.holder)
        )
    except Exception:  # noqa: BLE001 — fail-open by design (ADR-094)
        _log.warning("lease enforcement failed, proceeding open", exc_info=True)
        return EnforcementDecision(
            status="warning",
            warning="Lease enforcement no disponible (error interno) — procediendo sin verificación.",
        )


def _enforce(cwd: str, *, renew: bool) -> EnforcementDecision:
    if not cwd:
        return EnforcementDecision(status="allowed")

    project = Path(cwd)
    try:
        worktree = SqliteWorktreeStore(project).get_by_path(cwd)
    except WorktreeNotFoundError:
        return EnforcementDecision(status="allowed")

    session_id = discover_agent_session_id()
    if not session_id:
        return EnforcementDecision(
            status="warning",
            worktree_id=worktree.worktree_id,
            warning=(
                f"Worktree '{worktree.worktree_id}' registrado pero el session_id "
                "no es resoluble — enforcement de lease omitido."
            ),
        )

    import os  # noqa: PLC0415

    store = SqliteLeaseStore(project)
    if renew and store.renew(worktree.worktree_id, session_id=session_id):
        return EnforcementDecision(status="allowed", worktree_id=worktree.worktree_id)

    # Peek the prior lease row before acquire() overwrites it — this is the
    # same liveness verdict (expired AND not pid_alive) that already gates
    # session-lease takeover in production, surfaced here so callers (e.g.
    # pipeline_start's orphan lock reaper, RAISE-11089) can reuse it instead
    # of re-implementing PID liveness checks.
    prior = store.get(worktree.worktree_id)

    # For pipeline_advance (renew=True): if the current holder's PID is dead
    # the pipeline cannot be owned by a live session — release the stale lease
    # so acquire() can proceed without raising LeaseHeldError. TTL is NOT
    # required to have elapsed: a dead PID is sufficient proof the session is
    # gone (RAISE-14878). pipeline_start (renew=False) keeps the stricter
    # expired-AND-dead check via _takeover_allowed.
    if renew and prior is not None and not pid_alive(prior.pid):
        store.release(prior.worktree_id, session_id=prior.session_id)

    prior_dead = (
        prior is not None
        and prior.session_id != session_id
        and SqliteLeaseStore._takeover_allowed(  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
            prior, datetime.now(UTC)
        )
    )

    # acquire covers both start and a renew where we never held the lease:
    # it succeeds on a free worktree, renews idempotently for the holder,
    # and raises LeaseHeldError when another live session owns it.
    store.acquire(worktree.worktree_id, session_id=session_id, pid=os.getpid())
    return EnforcementDecision(
        status="allowed",
        worktree_id=worktree.worktree_id,
        prior_holder_dead=prior_dead,
    )
