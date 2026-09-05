"""CatalogSource Protocol and LocalCatalogSource implementation."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from raise_cli.session.catalog.models import (
    CatalogFilter,
    RuntimeSessionRecord,
    SessionState,
)
from raise_cli.session.catalog.scope import ProjectScope, WorktreeScope

logger = logging.getLogger(__name__)

SOURCE_ID_LOCAL = "local"


@dataclass(frozen=True)
class SourceResult:
    """Return value from ``CatalogSource.query()``."""

    source_id: str
    records: list[RuntimeSessionRecord] = field(default_factory=list)
    error: str | None = None


@runtime_checkable
class CatalogSource(Protocol):
    """Protocol for session catalog backends."""

    source_id: str

    def query(self, filters: CatalogFilter, *, timeout_s: float = 5.0) -> SourceResult:
        """Query sessions matching *filters*."""
        ...


class LocalCatalogSource:
    """Reads runtime_sessions from the local SQLite database."""

    source_id: str = SOURCE_ID_LOCAL

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def query(self, filters: CatalogFilter, *, timeout_s: float = 5.0) -> SourceResult:
        """Query the local runtime_sessions table."""
        try:
            return self._query(filters)
        except Exception as exc:  # noqa: BLE001 — fail-open: log and surface error field
            logger.warning("LocalCatalogSource.query failed: %s", exc)
            return SourceResult(source_id=self.source_id, error=str(exc))

    def _query(self, filters: CatalogFilter) -> SourceResult:
        conn = sqlite3.connect(self._db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        try:
            sql, params = self._build_query(filters)
            rows = conn.execute(sql, params).fetchall()
        finally:
            conn.close()

        records = [self._row_to_record(r) for r in rows]
        return SourceResult(source_id=self.source_id, records=records)

    def _build_query(self, filters: CatalogFilter) -> tuple[str, list[object]]:
        conditions: list[str] = []
        params: list[object] = []

        scope = filters.scope
        if isinstance(scope, WorktreeScope):
            conditions.append("project_id = ?")
            params.append(scope.project_id)
            conditions.append("worktree_id = ?")
            params.append(scope.worktree_id)
        elif isinstance(scope, ProjectScope):
            conditions.append("project_id = ?")
            params.append(scope.project_id)
        # HostScope: no filter — all sessions on this host

        if filters.states:
            placeholders = ",".join("?" * len(filters.states))
            conditions.append(f"state IN ({placeholders})")
            params.extend(s.value for s in filters.states)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        limit = f"LIMIT {filters.limit}" if filters.limit is not None else ""
        sql = f"SELECT * FROM runtime_sessions {where} ORDER BY created_at DESC {limit}"  # noqa: S608 # nosec B608 — conditions/limit are literals; values use ? params
        return sql, params

    def _row_to_record(self, row: sqlite3.Row) -> RuntimeSessionRecord:
        def _parse_dt(val: str | None) -> datetime:
            if not val:
                return datetime.now(tz=UTC)
            try:
                return datetime.fromisoformat(val).replace(tzinfo=UTC)
            except ValueError:
                return datetime.now(tz=UTC)

        return RuntimeSessionRecord(
            session_id=row["session_id"],
            project_id=row["project_id"],
            worktree_id=row["worktree_id"] or "",
            alias=row["alias"],
            harness=row["harness"],
            state=SessionState(row["state"]),
            governance_session_id=row["governance_session_id"],
            created_at=_parse_dt(row["created_at"]),
            updated_at=_parse_dt(row["updated_at"]),
        )
