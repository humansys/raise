"""Session lifecycle lease integration (RAISE-15087 S3).

Bridges `rai session start/close` with the worktree lease system (ADR-094).
Session open acquires a lease; session close releases it.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from raise_cli.storage.leases import SqliteLeaseStore

_log = logging.getLogger(__name__)


def acquire_session_lease(
    store: SqliteLeaseStore,
    worktree_id: str,
    session_id: str,
) -> bool:
    """Acquire a worktree lease for the current session.

    Reaps dead-PID holders first. If a live holder already exists,
    the call is a no-op (does not raise — session open is not the place
    to hard-block).

    Returns True if a new lease was acquired.
    """
    holder = store.get_live_or_reap(worktree_id)
    if holder is not None:
        _log.info(
            "Worktree '%s' already held by session '%s' (pid %d) — skipping lease",
            worktree_id,
            holder.session_id,
            holder.pid,
        )
        return False
    store.acquire(worktree_id, session_id=session_id, pid=os.getpid())
    return True


def release_session_lease(
    store: SqliteLeaseStore,
    worktree_id: str,
    session_id: str,
) -> bool:
    """Release a worktree lease owned by session_id.

    Owner-guarded: only deletes if the lease's session_id matches.
    Returns True if a lease was actually released.
    """
    lease = store.get(worktree_id)
    if lease is None:
        return False
    if lease.session_id != session_id:
        return False
    store.release(worktree_id, session_id=session_id)
    return True


def resolve_worktree_for_session(
    project_path: Path,
    cwd: Path,
) -> str | None:
    """Resolve the worktree_id for the current CWD.

    Returns None if CWD is the main checkout (not a linked worktree)
    or if the path isn't registered in the worktree store.
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        wt_store = SqliteWorktreeStore(project_path)
        wt = wt_store.get_by_path(str(cwd))
        return wt.worktree_id
    except (WorktreeNotFoundError, Exception):  # noqa: BLE001
        return None
