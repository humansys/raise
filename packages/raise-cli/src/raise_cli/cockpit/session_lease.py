"""Session lifecycle lease integration (RAISE-15087 S3).

Bridges `rai session start/close` with the worktree lease system (ADR-094).
Session open acquires a lease; session close releases it.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from raise_cli.storage.leases import Lease, SqliteLeaseStore
from raise_cli.storage.worktrees import (
    SqliteWorktreeStore,
    Worktree,
    WorktreeNotFoundError,
)

_log = logging.getLogger(__name__)


def usable_worktree(lease: Lease, wt_store: SqliteWorktreeStore) -> Worktree | None:
    """Return the lease's worktree when it is a usable binding target, else None.

    Usable means: the registry row exists, its status is not ``closed`` and
    its directory exists on disk (RAISE-18504). A missing row (orphan lease)
    answers None, accepted behaviour change vs the old fail-open: the
    hook now skips it and may bind an older usable sibling lease.

    Deliberately does NOT evaluate pid liveness (that is the lease store's
    ``pid_alive`` filter; the MCP-pid caveat is RAISE-18043) nor lease expiry
    (no TTL on the read path; an expired lease with a live holder still
    binds; a policy decision belonging to the ADR). This is the seam where
    a future shared predicate extends.

    Lookup errors other than "row absent" propagate so callers fail open.
    """
    try:
        wt = wt_store.get_by_name(lease.worktree_id)
    except WorktreeNotFoundError:
        return None
    if wt.status == "closed" or not Path(wt.path).is_dir():
        return None
    return wt


def acquire_session_lease(
    store: SqliteLeaseStore,
    worktree_id: str,
    session_id: str,
) -> bool:
    """Acquire a worktree lease for the current session.

    Reaps dead-PID holders first. If a live holder already exists,
    the call is a no-op (does not raise — session open is not the place
    to hard-block).

    A same-session live holder is renewed (heartbeat + expiry, pid
    preserved) so a reopen makes this worktree the session's most recent
    one (RAISE-18504); the renew result is returned (False on a lost race).

    Returns True if a lease was acquired or renewed.
    """
    holder = store.get_live_or_reap(worktree_id)
    if holder is not None and holder.session_id == session_id:
        return store.renew(worktree_id, session_id=session_id)
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
