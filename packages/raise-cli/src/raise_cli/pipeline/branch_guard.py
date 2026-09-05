"""Branch-operation guard against live foreign sessions (S8170.7, ADR-094).

Before the engine checks out, merges, or removes a branch, this guard
resolves branch → worktree → lease → liveness and blocks the operation
when the branch belongs to a worktree whose lease is held by another
live session — the cross-session merge/delete gap neither git nor SOTA
tooling covers (research F2, incident RAISE-8108).

Fail-open by design: internal errors or RAISE_BRANCH_GUARD=warn degrade
to a warning instead of blocking.
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from raise_cli.pipeline.worktree import parse_porcelain
from raise_cli.storage.leases import Lease, SqliteLeaseStore, pid_alive
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

_log = logging.getLogger(__name__)

GuardStatus = Literal["allowed", "blocked", "warning"]

_GIT_TIMEOUT = 10


@dataclass
class GuardDecision:
    """Outcome of a branch-operation check."""

    status: GuardStatus
    message: str = ""
    holder: Lease | None = None
    worktree_path: str = ""


def _warn_mode() -> bool:
    return os.environ.get("RAISE_BRANCH_GUARD", "block").lower() == "warn"


def lease_is_live(lease: Lease) -> bool:
    """Return True if the lease is not expired or its owner process is still alive."""
    expired = datetime.fromisoformat(lease.expires_at) <= datetime.now(UTC)
    return not expired or pid_alive(lease.pid)


def guard_branch_operation(
    operation: str, branch: str, cwd: str, *, session_id: str | None = None
) -> GuardDecision:
    """Check whether *operation* on *branch* is safe for the calling session.

    Args:
        operation: Human label for messages (e.g. "remove", "merge").
        branch: Target branch name (without refs/heads/ prefix).
        cwd: Directory inside the repository to query worktrees from.
        session_id: Calling session; resolved from env when None.
    """
    try:
        return _guard(operation, branch, cwd, session_id)
    except Exception:  # noqa: BLE001 — fail-open by design (ADR-094)
        _log.warning("branch guard failed open", exc_info=True)
        return GuardDecision(
            status="warning",
            message=(
                f"Branch guard no disponible para {operation} de '{branch}' "
                "(error interno) — procediendo sin verificación."
            ),
        )


def _guard(
    operation: str, branch: str, cwd: str, session_id: str | None
) -> GuardDecision:
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=_GIT_TIMEOUT,
    )
    if result.returncode != 0:
        return GuardDecision(status="allowed")

    worktree = next(
        (w for w in parse_porcelain(result.stdout) if w.branch == branch), None
    )
    if worktree is None:
        return GuardDecision(status="allowed")

    wt_path = str(worktree.path)
    try:
        registered = SqliteWorktreeStore(Path(wt_path)).get_by_path(wt_path)
    except WorktreeNotFoundError:
        # Unregistered worktree — no lease to consult; git's own
        # checked-out-branch protections still apply (D2).
        return GuardDecision(status="allowed", worktree_path=wt_path)

    lease = SqliteLeaseStore(Path(wt_path)).get(registered.worktree_id)
    if lease is None or not lease_is_live(lease):
        return GuardDecision(status="allowed", worktree_path=wt_path)

    if session_id is None:
        from raise_cli._agent_session import discover_agent_session_id

        session_id = discover_agent_session_id()
    if session_id and lease.session_id == session_id:
        return GuardDecision(status="allowed", worktree_path=wt_path)

    message = (
        f"Operación '{operation}' sobre la rama '{branch}' bloqueada: "
        f"pertenece al worktree '{registered.worktree_id}' ({wt_path}) con "
        f"lease vivo de la sesión '{lease.session_id}' (pid {lease.pid}, "
        f"heartbeat {lease.heartbeat_at}). Si esa sesión murió, el lease "
        f"expira a las {lease.expires_at}."
    )
    if _warn_mode():
        return GuardDecision(
            status="warning", message=message, holder=lease, worktree_path=wt_path
        )
    return GuardDecision(
        status="blocked", message=message, holder=lease, worktree_path=wt_path
    )
