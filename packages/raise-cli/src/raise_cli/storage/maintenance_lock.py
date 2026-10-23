"""SQLite-backed maintenance lock for global DB consolidation (S8371.3, ADR-104).

Guards `consolidate_all()` against concurrent pipeline runs: consolidation
acquires a named lock on the global DB before its first write; pipeline tools
consult the lock and degrade gracefully if consolidation is active.

Pattern mirrors `SqliteLeaseStore` (BEGIN IMMEDIATE + PID-alive takeover) but
operates on the global DB (`~/.rai/raise.db`) with a `name` TEXT PRIMARY KEY
instead of `(worktree_id, project_id)`. Duplication accepted per design DR1 —
different PKs, different semantics; extracting a shared base would couple
without value until a third lock store appears.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from raise_cli.storage.leases import pid_alive

DEFAULT_TTL_SECONDS = 300


@dataclass
class MaintenanceLock:
    """Row representation of a maintenance lock in the global DB."""

    name: str
    pid: int
    acquired_at: str
    expires_at: str


class MaintenanceLockHeldError(Exception):
    """Raised when acquire() finds a live lock owned by another process."""

    def __init__(self, holder: MaintenanceLock) -> None:
        self.holder = holder
        super().__init__(
            f"Maintenance lock '{holder.name}' is held by PID {holder.pid} "
            f"(expires {holder.expires_at})"
        )


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _row_to_lock(row: object) -> MaintenanceLock:
    return MaintenanceLock(
        name=row["name"],  # type: ignore[index]
        pid=row["pid"],  # type: ignore[index]
        acquired_at=row["acquired_at"],  # type: ignore[index]
        expires_at=row["expires_at"],  # type: ignore[index]
    )


class MaintenanceLockStore:
    """SQLite-backed maintenance lock registry (V43 schema).

    Takes an open sqlite3.Connection (expected to be the global DB).
    Uses BEGIN IMMEDIATE so concurrent acquires see a consistent winner.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def acquire(
        self,
        name: str,
        *,
        pid: int,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> bool:
        """Acquire (or renew) a named maintenance lock.

        Returns True when the lock is taken by this call.
        Raises MaintenanceLockHeldError when another live PID holds the lock.
        Same PID re-acquiring its own lock is an idempotent renewal.
        """
        now = _now()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                "SELECT * FROM maintenance_locks WHERE name = ?",
                (name,),
            ).fetchone()
            if row is not None:
                current = _row_to_lock(row)
                # Same PID — idempotent renewal allowed
                if current.pid != pid and not self._takeover_allowed(current, now):
                    raise MaintenanceLockHeldError(current)

            lock = MaintenanceLock(
                name=name,
                pid=pid,
                acquired_at=_iso(now),
                expires_at=_iso(now + timedelta(seconds=ttl_seconds)),
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO maintenance_locks VALUES (?, ?, ?, ?)",
                (lock.name, lock.pid, lock.acquired_at, lock.expires_at),
            )
            self._conn.commit()
        except BaseException:
            self._conn.rollback()
            raise
        return True

    def release(self, name: str, *, pid: int) -> None:
        """Remove the lock. No-op unless the caller's PID matches the holder."""
        self._conn.execute(
            "DELETE FROM maintenance_locks WHERE name = ? AND pid = ?",
            (name, pid),
        )
        self._conn.commit()

    def get(self, name: str) -> MaintenanceLock | None:
        """Return the current lock, or None when the lock is free."""
        row = self._conn.execute(
            "SELECT * FROM maintenance_locks WHERE name = ?",
            (name,),
        ).fetchone()
        return _row_to_lock(row) if row is not None else None

    def is_expired_and_dead(self, lock: MaintenanceLock) -> bool:
        """True only when the lock is both past its TTL and the holder PID is dead."""
        now = _now()
        expired = datetime.fromisoformat(lock.expires_at) <= now
        return expired and not pid_alive(lock.pid)

    @staticmethod
    def _takeover_allowed(current: MaintenanceLock, now: datetime) -> bool:
        expired = datetime.fromisoformat(current.expires_at) <= now
        return expired and not pid_alive(current.pid)
