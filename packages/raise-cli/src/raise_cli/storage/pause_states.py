"""SQLite-backed cockpit pause states (RAISE-16708, D-S3.1/D-S3.2).

An explicit, liveness-independent flag: pause is user intent, not a
derived process state. Deliberately kept separate from ``worktree_leases``
(SqliteLeaseStore) — lease rows are reaped when the holder PID dies and
clobbered by ``INSERT OR REPLACE`` on re-acquire, both of which would erase
a pause flag stored there, defeating "pause persists across cockpit
restart".
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class SqlitePauseStore:
    """SQLite-backed pause-state registry (V76 schema).

    Pattern: SqliteLeaseStore — thin wrapper, project-scoped, ``create_all``
    on init. Pause is a distinct concern from lease liveness (Simple First).
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        create_all(self._conn)

    def toggle(self, worktree_id: str) -> bool:
        """Flip the paused flag for *worktree_id* and return the new value."""
        new_value = not self.is_paused(worktree_id)
        self._conn.execute(
            "INSERT OR REPLACE INTO worktree_pause_states "
            "(project_id, worktree_id, paused, updated_at) VALUES (?, ?, ?, ?)",
            (self._project_id, worktree_id, int(new_value), _now_iso()),
        )
        self._conn.commit()
        return new_value

    def is_paused(self, worktree_id: str) -> bool:
        """Return whether *worktree_id* is currently paused (default False)."""
        row = self._conn.execute(
            "SELECT paused FROM worktree_pause_states "
            "WHERE project_id = ? AND worktree_id = ?",
            (self._project_id, worktree_id),
        ).fetchone()
        return bool(row[0]) if row is not None else False

    def clear(self, worktree_id: str) -> None:
        """Delete the pause row for *worktree_id* outright (idempotent).

        Distinct from toggling to unpaused: a future worktree re-created
        under the same slug should not inherit a dead ``paused=0`` row nor
        any pause intent (RAISE-16709 D-S4.6).
        """
        self._conn.execute(
            "DELETE FROM worktree_pause_states "
            "WHERE project_id = ? AND worktree_id = ?",
            (self._project_id, worktree_id),
        )
        self._conn.commit()

    def list_paused(self) -> set[str]:
        """Return the set of worktree ids currently marked paused."""
        rows = self._conn.execute(
            "SELECT worktree_id FROM worktree_pause_states "
            "WHERE project_id = ? AND paused = 1",
            (self._project_id,),
        ).fetchall()
        return {row[0] for row in rows}
