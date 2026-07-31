"""SQLite-backed worktree registry for E4325 parallel-worktrees-skill."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import ensure_schema


class WorktreeNotFoundError(Exception):
    """Raised when a worktree lookup finds no matching row."""


class WorktreeDuplicateError(Exception):
    """Raised on register() when the name already exists and update=False."""


@dataclass
class Worktree:
    """Row representation of a registered git worktree."""

    worktree_id: str
    project_id: str
    path: str
    branch: str
    merge_target: str
    stories: list[str]
    status: str
    last_session_id: str | None
    created_at: str
    mission_id: str = ""
    workitem_id: str = ""  # ADR-130 D2 (RAISE-14643/S4)
    agent_id: str = ""  # agent session ID at registration (RAISE-15003)
    harness: str = ""  # agent runtime identifier (RAISE-15003)
    parent_session_id: str = ""  # parent session for sub-agent chains (RAISE-15003)


def _row_to_worktree(row: object) -> Worktree:
    return Worktree(
        worktree_id=row["worktree_id"],  # type: ignore[index]
        project_id=row["project_id"],  # type: ignore[index]
        path=row["path"],  # type: ignore[index]
        branch=row["branch"],  # type: ignore[index]
        merge_target=row["merge_target"],  # type: ignore[index]
        stories=json.loads(row["stories_json"]),  # type: ignore[index]
        status=row["status"],  # type: ignore[index]
        last_session_id=row["last_session_id"],  # type: ignore[index]
        created_at=row["created_at"],  # type: ignore[index]
        mission_id=row["mission_id"],  # type: ignore[index]
        workitem_id=row["workitem_id"],  # type: ignore[index]
        agent_id=row["agent_id"] or "",  # type: ignore[index]
        harness=row["harness"] or "",  # type: ignore[index]
        parent_session_id=row["parent_session_id"] or "",  # type: ignore[index]
    )


class SqliteWorktreeStore:
    """SQLite-backed worktree registry (V25 schema). CRUD over worktrees table.

    Pattern: SqliteMissionStore — thin wrapper, no git logic.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        # RAISE-15605: once-per-process, so constructing a store for a READ
        # does not issue migration backfill WRITEs on the shared DB.
        ensure_schema(self._conn)

    def register(
        self,
        name: str,
        path: str,
        branch: str,
        merge_target: str,
        stories: list[str] | None = None,
        *,
        mission_id: str = "",
        workitem_id: str = "",
        agent_id: str = "",
        harness: str = "",
        parent_session_id: str = "",
        update: bool = False,
    ) -> Worktree:
        """Insert a new worktree row.

        Raises WorktreeDuplicateError if the name already exists and update=False.
        With update=True performs a non-destructive upsert (preserves status and
        last_session_id). Attribution fields (agent_id, harness, parent_session_id)
        are best-effort: empty strings are acceptable defaults.
        """
        resolved_path = str(Path(path).resolve())
        existing = self._conn.execute(
            "SELECT * FROM worktrees WHERE worktree_id = ? AND project_id = ?",
            (name, self._project_id),
        ).fetchone()

        if existing is not None and not update:
            raise WorktreeDuplicateError(
                f"Worktree '{name}' already registered. Use --update to modify."
            )

        now = datetime.now(UTC).isoformat()
        stories_json = json.dumps(stories or [])

        # Transactional (RAISE-15605): on failure the context manager rolls back
        # and releases the shared WAL write lock instead of holding it open for
        # the life of the process.
        with self._conn:
            if existing is None:
                self._conn.execute(
                    """
                    INSERT INTO worktrees
                        (worktree_id, project_id, path, branch, merge_target,
                         stories_json, status, created_at, mission_id, workitem_id,
                         agent_id, harness, parent_session_id)
                    VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        self._project_id,
                        resolved_path,
                        branch,
                        merge_target,
                        stories_json,
                        now,
                        mission_id,
                        workitem_id,
                        agent_id,
                        harness,
                        parent_session_id,
                    ),
                )
            else:
                self._conn.execute(
                    """
                    UPDATE worktrees
                    SET path = ?, branch = ?, merge_target = ?, stories_json = ?,
                        mission_id = ?, workitem_id = ?,
                        agent_id = ?, harness = ?, parent_session_id = ?
                    WHERE worktree_id = ? AND project_id = ?
                    """,
                    (
                        resolved_path,
                        branch,
                        merge_target,
                        stories_json,
                        mission_id,
                        workitem_id,
                        agent_id,
                        harness,
                        parent_session_id,
                        name,
                        self._project_id,
                    ),
                )

        return self.get_by_name(name)

    def get_by_name(self, name: str) -> Worktree:
        """Return worktree by ID. Raises WorktreeNotFoundError if absent."""
        row = self._conn.execute(
            "SELECT * FROM worktrees WHERE worktree_id = ? AND project_id = ?",
            (name, self._project_id),
        ).fetchone()
        if row is None:
            raise WorktreeNotFoundError(f"Worktree '{name}' not found.")
        return _row_to_worktree(row)

    def get_by_path(self, path: str) -> Worktree:
        """Return worktree by filesystem path (resolved). Raises WorktreeNotFoundError if absent."""
        resolved = str(Path(path).resolve())
        row = self._conn.execute(
            "SELECT * FROM worktrees WHERE path = ? AND project_id = ?",
            (resolved, self._project_id),
        ).fetchone()
        if row is None:
            raise WorktreeNotFoundError(
                f"No worktree registered at {path}. Run `rai worktree register` first."
            )
        return _row_to_worktree(row)

    def complete(self, name: str) -> Worktree:
        """Set status='closed' for the named worktree. Raises WorktreeNotFoundError if absent."""
        self.get_by_name(name)  # raises if not found
        with self._conn:  # RAISE-15605: roll back, do not strand the write lock
            self._conn.execute(
                "UPDATE worktrees SET status = 'closed' "
                "WHERE worktree_id = ? AND project_id = ?",
                (name, self._project_id),
            )
        return self.get_by_name(name)

    def set_last_session(self, name: str, session_id: str) -> None:
        """Record the session that last ran in this worktree. Raises WorktreeNotFoundError if absent."""
        self.get_by_name(name)  # raises if not found
        with self._conn:  # RAISE-15605: roll back, do not strand the write lock
            self._conn.execute(
                "UPDATE worktrees SET last_session_id = ? "
                "WHERE worktree_id = ? AND project_id = ?",
                (session_id, name, self._project_id),
            )

    def list_worktrees(self, *, include_closed: bool = False) -> list[Worktree]:
        """Return project worktrees ordered by creation date descending."""
        if include_closed:
            rows = self._conn.execute(
                "SELECT * FROM worktrees WHERE project_id = ? ORDER BY created_at DESC",
                (self._project_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM worktrees WHERE project_id = ? AND status = 'open' ORDER BY created_at DESC",
                (self._project_id,),
            ).fetchall()
        return [_row_to_worktree(r) for r in rows]
