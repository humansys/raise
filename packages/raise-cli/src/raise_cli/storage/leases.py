"""SQLite-backed worktree session leases (S8170.2, ADR-094).

Enforces the one-session-per-worktree invariant: a session acquires a
lease before operating a worktree; a second session is rejected with the
holder's identity. Takeover requires an expired lease AND a dead PID —
a live process always keeps its worktree even if its heartbeat lagged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all

DEFAULT_TTL_SECONDS = 1800


@dataclass
class Lease:
    """Row representation of a worktree session lease."""

    worktree_id: str
    project_id: str
    session_id: str
    pid: int
    acquired_at: str
    heartbeat_at: str
    expires_at: str


class LeaseHeldError(Exception):
    """Raised when acquire() finds a live lease owned by another session."""

    def __init__(self, holder: Lease) -> None:
        self.holder = holder
        super().__init__(
            f"Worktree '{holder.worktree_id}' is leased by session "
            f"'{holder.session_id}' (pid {holder.pid}, "
            f"last heartbeat {holder.heartbeat_at})"
        )


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _pid_alive_win32(pid: int) -> bool:
    # os.kill(pid, 0) on Windows == GenerateConsoleCtrlEvent(CTRL_C_EVENT, pid),
    # which broadcasts SIGINT to the console — not a liveness probe. Use
    # OpenProcess + GetExitCodeProcess (STILL_ACTIVE=259) instead.
    import ctypes
    import ctypes.wintypes

    process_query_limited_information = 0x1000
    still_active = 259

    handle = ctypes.windll.kernel32.OpenProcess(  # type: ignore[attr-defined]
        process_query_limited_information, False, pid
    )
    if not handle:
        return False
    try:
        exit_code = ctypes.wintypes.DWORD()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(  # type: ignore[attr-defined]
            handle, ctypes.byref(exit_code)
        )
        return bool(ok) and exit_code.value == still_active
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)  # type: ignore[attr-defined]


def pid_alive(pid: int) -> bool:
    """True when *pid* belongs to a live process (EPERM counts as alive)."""
    if os.name == "nt":
        return _pid_alive_win32(pid)  # pyright: ignore[reportUnreachable]
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _row_to_lease(row: object) -> Lease:
    return Lease(
        worktree_id=row["worktree_id"],  # type: ignore[index]
        project_id=row["project_id"],  # type: ignore[index]
        session_id=row["session_id"],  # type: ignore[index]
        pid=row["pid"],  # type: ignore[index]
        acquired_at=row["acquired_at"],  # type: ignore[index]
        heartbeat_at=row["heartbeat_at"],  # type: ignore[index]
        expires_at=row["expires_at"],  # type: ignore[index]
    )


class SqliteLeaseStore:
    """SQLite-backed lease registry (V39 schema).

    Pattern: SqliteWorktreeStore — thin wrapper, no git logic.
    Writes serialize through BEGIN IMMEDIATE so concurrent acquires
    see a consistent winner (busy_timeout retries the loser).
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        create_all(self._conn)

    def acquire(
        self,
        worktree_id: str,
        *,
        session_id: str,
        pid: int,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> Lease:
        """Acquire (or renew) the lease for a worktree.

        Raises LeaseHeldError when another session holds a lease that is
        either unexpired or backed by a live PID.
        """
        now = _now()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                "SELECT * FROM worktree_leases "
                "WHERE worktree_id = ? AND project_id = ?",
                (worktree_id, self._project_id),
            ).fetchone()
            if row is not None:
                current = _row_to_lease(row)
                if current.session_id != session_id and not self._takeover_allowed(
                    current, now
                ):
                    raise LeaseHeldError(current)

            lease = Lease(
                worktree_id=worktree_id,
                project_id=self._project_id,
                session_id=session_id,
                pid=pid,
                acquired_at=_iso(now),
                heartbeat_at=_iso(now),
                expires_at=_iso(now + timedelta(seconds=ttl_seconds)),
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO worktree_leases VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    lease.worktree_id,
                    lease.project_id,
                    lease.session_id,
                    lease.pid,
                    lease.acquired_at,
                    lease.heartbeat_at,
                    lease.expires_at,
                ),
            )
            self._conn.commit()
        except BaseException:
            self._conn.rollback()
            raise
        return lease

    def renew(
        self,
        worktree_id: str,
        *,
        session_id: str,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> bool:
        """Refresh heartbeat and expiry. Returns False unless caller holds the lease."""
        now = _now()
        cursor = self._conn.execute(
            "UPDATE worktree_leases SET heartbeat_at = ?, expires_at = ? "
            "WHERE worktree_id = ? AND project_id = ? AND session_id = ?",
            (
                _iso(now),
                _iso(now + timedelta(seconds=ttl_seconds)),
                worktree_id,
                self._project_id,
                session_id,
            ),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def release(self, worktree_id: str, *, session_id: str) -> None:
        """Remove the lease. No-op unless caller holds it."""
        self._conn.execute(
            "DELETE FROM worktree_leases "
            "WHERE worktree_id = ? AND project_id = ? AND session_id = ?",
            (worktree_id, self._project_id, session_id),
        )
        self._conn.commit()

    def get(self, worktree_id: str) -> Lease | None:
        """Return the current lease, or None when the worktree is free."""
        row = self._conn.execute(
            "SELECT * FROM worktree_leases WHERE worktree_id = ? AND project_id = ?",
            (worktree_id, self._project_id),
        ).fetchone()
        return _row_to_lease(row) if row is not None else None

    def get_live_or_reap(self, worktree_id: str) -> Lease | None:
        """Return live holder or atomically reap a dead-PID lease.

        Unlike ``get()``, this checks PID liveness and deletes the lease
        in-place when the holder process is dead — regardless of TTL.
        The delete is owner-guarded (session_id + pid) so a concurrent
        new acquirer is never accidentally reaped.

        RAISE-16785: cascade-deletes the matching ``active_sessions``
        pointer so zombie session rows cannot accumulate.
        """
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            lease = self.get(worktree_id)
            if lease is None:
                self._conn.commit()
                return None
            if pid_alive(lease.pid):
                self._conn.commit()
                return lease
            self._conn.execute(
                "DELETE FROM worktree_leases "
                "WHERE worktree_id = ? AND project_id = ? "
                "AND session_id = ? AND pid = ?",
                (
                    lease.worktree_id,
                    lease.project_id,
                    lease.session_id,
                    lease.pid,
                ),
            )
            self._conn.execute(
                "DELETE FROM active_sessions WHERE worktree_id = ? AND project_id = ?",
                (worktree_id, self._project_id),
            )
            self._conn.commit()
            return None
        except BaseException:
            self._conn.rollback()
            raise

    def list_live_or_reap(self) -> dict[str, Lease]:
        """Return all live leases for this project, reaping dead holders.

        Returns a dict keyed by worktree_id containing only leases whose
        holder PID is still alive.  Dead-PID leases are deleted in place.
        """
        rows = self._conn.execute(
            "SELECT * FROM worktree_leases WHERE project_id = ?",
            (self._project_id,),
        ).fetchall()
        live: dict[str, Lease] = {}
        dead_keys: list[tuple[str, str, str, int]] = []
        for row in rows:
            lease = _row_to_lease(row)
            if pid_alive(lease.pid):
                live[lease.worktree_id] = lease
            else:
                dead_keys.append(
                    (
                        lease.worktree_id,
                        lease.project_id,
                        lease.session_id,
                        lease.pid,
                    )
                )
        if dead_keys:
            for key in dead_keys:
                self._conn.execute(
                    "DELETE FROM worktree_leases "
                    "WHERE worktree_id = ? AND project_id = ? "
                    "AND session_id = ? AND pid = ?",
                    key,
                )
                # RAISE-16785: cascade-delete orphaned session pointers
                self._conn.execute(
                    "DELETE FROM active_sessions "
                    "WHERE worktree_id = ? AND project_id = ?",
                    (key[0], key[1]),
                )
            self._conn.commit()
        return live

    def release_if_heartbeat_matches(
        self, worktree_id: str, *, session_id: str, observed_heartbeat_at: str
    ) -> bool:
        """Release lease only when heartbeat_at matches the observed value (ABA guard).

        Provides compare-and-delete semantics for the cockpit force-release flow
        (RAISE-15050 §3.6 Sol R2): the TUI snapshots the lease's heartbeat_at at
        display time and passes it here. If the holder renewed the lease between
        display and user confirmation, heartbeat_at will have changed and this
        delete silently returns False — preventing an accidental force-release on
        a session that just proved liveness.

        Args:
            worktree_id: Target worktree identifier.
            session_id: The session currently holding the lease (from displayed state).
            observed_heartbeat_at: The heartbeat_at value read when the TUI built
                the confirmation prompt. Used as the compare condition.

        Returns:
            True when the lease was found and deleted; False when the condition
            didn't match (ABA race detected or wrong session).
        """
        cursor = self._conn.execute(
            "DELETE FROM worktree_leases "
            "WHERE worktree_id = ? AND project_id = ? "
            "AND session_id = ? AND heartbeat_at = ?",
            (worktree_id, self._project_id, session_id, observed_heartbeat_at),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _takeover_allowed(current: Lease, now: datetime) -> bool:
        expired = datetime.fromisoformat(current.expires_at) <= now
        return expired and not pid_alive(current.pid)
