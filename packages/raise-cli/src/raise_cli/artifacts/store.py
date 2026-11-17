"""SQLite-backed artifact persistence.

Stores structured story lifecycle artifacts produced by MCP tools.
Each artifact is uniquely identified by (project_id, story_id, artifact_type),
plus review_type for review artifacts.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from raise_cli.artifacts.models import ARTIFACT_TYPES, ArtifactBase


class ArtifactStore:
    """Read/write structured artifacts in the project SQLite DB."""

    def __init__(self, conn: sqlite3.Connection, project_id: str = "") -> None:
        self._conn = conn
        self._pid = project_id

    def save(
        self,
        story_id: str,
        artifact_type: str,
        content: ArtifactBase,
        *,
        session_id: str | None = None,
        work_item_id: str | None = None,
    ) -> str:
        """Persist an artifact, returning its ID. Upserts on its natural key."""
        now = datetime.now(UTC).isoformat()
        content_json = content.model_dump_json()
        review_type = (
            str(getattr(content, "review_type", ""))
            if artifact_type == "review"
            else ""
        )
        if artifact_type == "review" and not review_type:
            raise ValueError("review artifacts require review_type")

        existing = self._conn.execute(
            """SELECT artifact_id FROM artifacts
               WHERE project_id = ? AND story_id = ? AND artifact_type = ?
                 AND review_type = ?""",
            (self._pid, story_id, artifact_type, review_type),
        ).fetchone()

        # Transactional (RAISE-15605): commit on clean exit, ROLLBACK on
        # exception. Without it a failed write leaves the implicit BEGIN --
        # and the shared ~/.rai/raise.db WAL write lock -- open forever.
        with self._conn:
            if existing:
                artifact_id: str = existing["artifact_id"]
                self._conn.execute(
                    """UPDATE artifacts SET
                         content_json = ?, schema_version = ?, session_id = ?,
                         work_item_id = ?, review_type = ?, updated_at = ?
                       WHERE project_id = ? AND artifact_id = ?""",
                    (
                        content_json,
                        content.schema_version,
                        session_id,
                        work_item_id,
                        review_type,
                        now,
                        self._pid,
                        artifact_id,
                    ),
                )
            else:
                artifact_id = f"ART-{self._pid}:{story_id}:{artifact_type}"
                if review_type:
                    artifact_id = f"{artifact_id}:{review_type}"
                self._conn.execute(
                    """INSERT INTO artifacts
                       (project_id, artifact_id, story_id, artifact_type, schema_version,
                        session_id, work_item_id, content_json, review_type,
                        created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self._pid,
                        artifact_id,
                        story_id,
                        artifact_type,
                        content.schema_version,
                        session_id,
                        work_item_id,
                        content_json,
                        review_type,
                        now,
                        now,
                    ),
                )

        return artifact_id

    def get(
        self,
        story_id: str,
        artifact_type: str,
        *,
        review_type: str | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve one artifact by its complete natural identity."""
        if artifact_type == "review" and review_type is None:
            raise ValueError("review_type is required when querying a review")

        query = (
            "SELECT * FROM artifacts "
            "WHERE project_id = ? AND story_id = ? AND artifact_type = ?"
        )
        params: list[str] = [self._pid, story_id, artifact_type]
        if artifact_type == "review":
            query += " AND review_type = ?"
            params.append(review_type or "")
        row = self._conn.execute(query, params).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def list(
        self,
        story_id: str,
        *,
        artifact_type: str | None = None,
        review_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List artifacts, optionally filtered by type and review phase."""
        query = "SELECT * FROM artifacts WHERE project_id = ? AND story_id = ?"
        params: list[str] = [self._pid, story_id]
        if artifact_type is not None:
            query += " AND artifact_type = ?"
            params.append(artifact_type)
        if review_type is not None:
            query += " AND review_type = ?"
            params.append(review_type)
        query += " ORDER BY created_at"
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def exists(
        self,
        story_id: str,
        artifact_type: str,
        *,
        review_type: str | None = None,
    ) -> bool:
        """Check whether an artifact exists for the requested identity."""
        query = (
            "SELECT 1 FROM artifacts "
            "WHERE project_id = ? AND story_id = ? AND artifact_type = ?"
        )
        params: list[str] = [self._pid, story_id, artifact_type]
        if artifact_type == "review" and review_type is not None:
            query += " AND review_type = ?"
            params.append(review_type)
        row = self._conn.execute(query, params).fetchone()
        return row is not None

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a DB row to a dict with parsed content."""
        d = dict(row)
        raw_content = json.loads(d["content_json"])
        model_cls = ARTIFACT_TYPES.get(d["artifact_type"])
        if model_cls:
            d["content"] = model_cls.model_validate(raw_content).model_dump()
        else:
            d["content"] = raw_content
        return d
