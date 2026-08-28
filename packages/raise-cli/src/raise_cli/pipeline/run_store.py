"""Pipeline run persistence — Protocol + backends.

S1962.7 / ADR-053: dual-backend store for pipeline runs. Mirrors ADR-036's
KnowledgeGraphBackend pattern — Protocol here in raise-cli (lean, no DB
deps), Postgres implementation in raise-server.

Backends:
    SqliteRunStore    — stdio transport (Claude Code local). Global
                        ~/.rai/raise.db with project_id discrimination.
    ApiRunStore       — platform mode (RAISE_SERVER_URL set). Thin HTTP
                        client to raise-server.
    PostgresRunStore  — HTTP transport (Rovo multi-tenant). Lives in
                        raise-server; see raise_server.pipeline.run_store_db.

The resolver `get_run_store()` picks the backend per transport — never per
token presence. HTTP without a valid JWT raises rather than silently
falling back to the server filesystem.
"""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Protocol, runtime_checkable


class OptimisticLockError(Exception):
    """Raised when a concurrent writer updated the run since it was last read."""


@runtime_checkable
class PipelineRunStore(Protocol):
    """Persistence contract for pipeline runs. See ADR-053."""

    async def save(self, run: dict[str, Any]) -> None:
        """Upsert a run (keyed by run['run_id'])."""
        ...

    async def load(self, run_id: str) -> dict[str, Any] | None:
        """Return the run or None if unknown."""
        ...

    async def list_runs(self) -> list[dict[str, Any]]:
        """Return all runs visible to the caller (scoping is per-impl)."""
        ...

    async def delete(self, run_id: str) -> None:
        """Remove a run. No-op if unknown."""
        ...


# Phase statuses that represent successful completion when synthesizing
# progress/current_phase. Failed/cancelled phases are terminal but must not
# make a run look complete (RAISE-15833 review item #4).
_DONE_STATUSES = frozenset({"passed", "skipped", "done"})
_FAILED_STATUSES = frozenset({"failed", "cancelled"})


def _phase_is_done(phase: Any) -> bool:
    """Return True when ``phase`` is a dict whose status counts as done."""
    return isinstance(phase, dict) and phase.get("status") in _DONE_STATUSES


def _phase_is_failed(phase: Any) -> bool:
    """Return True when ``phase`` failed or was cancelled."""
    return isinstance(phase, dict) and phase.get("status") in _FAILED_STATUSES


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite3.Row from pipeline_runs into a run dict."""
    d = dict(row)
    d["phases"] = json.loads(d["phases"])
    d["metadata"] = json.loads(d.get("metadata") or "{}") or {}
    # RAISE-15833: match ApiRunStore serialization by exposing derived fields
    # that the engine uses to decide whether a run is complete.
    phases = d.get("phases", [])
    if isinstance(phases, dict):
        # Engine/legacy shape: {phase_id: PhaseExecution(...)}
        phase_items = list(phases.items())
        total = len(phase_items)
        done = sum(1 for _, p in phase_items if _phase_is_done(p))
        failed = next(
            (phase_id for phase_id, p in phase_items if _phase_is_failed(p)), None
        )
        current_phase: str | None = None
        for phase_id, p in phase_items:
            if isinstance(p, dict) and p.get("status") not in (
                *_DONE_STATUSES,
                *_FAILED_STATUSES,
            ):
                current_phase = phase_id
                break
        if failed is not None:
            d["current_phase"] = failed
        elif total > 0 and done == total:
            d["current_phase"] = "complete"
        else:
            d["current_phase"] = current_phase or ""
    elif isinstance(phases, list):
        # ApiRunStore / server-side shape: [{"id": ..., "status": ...}, ...]
        total = len(phases)
        done = sum(1 for p in phases if _phase_is_done(p))
        failed_phase = next((p for p in phases if _phase_is_failed(p)), None)
        current_idx = d.get("current_phase_index", 0)
        if failed_phase is not None:
            d["current_phase"] = (
                failed_phase.get("id", "") if isinstance(failed_phase, dict) else ""
            )
        elif current_idx >= total > 0:
            d["current_phase"] = "complete"
        elif total > 0:
            current = phases[current_idx]
            d["current_phase"] = (
                current.get("id", "") if isinstance(current, dict) else ""
            )
        else:
            d["current_phase"] = ""
    else:
        total = 0
        done = 0
        d["current_phase"] = ""
    d["progress"] = f"{done}/{total}" if total else "0/0"
    return d


class SqliteRunStore:
    """SQLite-backed pipeline run persistence with WAL concurrency.

    Stdio-transport backend since E2780. WAL mode serializes
    concurrent writes from multiple mcp_server.py processes natively.
    """

    def __init__(self, conn: sqlite3.Connection, project_id: str = "") -> None:
        self._conn = conn
        self._pid = project_id

    async def save(self, run: dict[str, Any], sync_state: str | None = None) -> None:
        """Upsert a run with optimistic locking via version column.

        New runs (no ``version`` key) are inserted at version 1.
        Existing runs must carry the ``version`` read from ``load()``; the
        update succeeds only if the DB row still has that version.  On
        conflict ``OptimisticLockError`` is raised.

        Args:
            run:        Run dict to upsert.
            sync_state: When provided (e.g. ``'pending'``), the sync_state column
                        is written in the **same** INSERT/UPDATE + single commit.
                        This is the S8371.2 F1 fix — a single atomic transaction
                        replaces the previous two-commit sequence of save() then
                        mark_pending().  Only valid on V42+ DBs; silently omitted
                        when the sync_state column is absent.
        """
        version = run.get("version")
        params = (
            self._pid,
            run["run_id"],
            run["pipeline_name"],
            run.get("issue_id") or "",
            run.get("current_phase_index", 0),
            run.get("status", "running"),
            json.dumps(run.get("phases", [])),
            run.get("started_at", ""),
            run.get("completed_at"),
            json.dumps(run.get("metadata", {})),
            run.get("paused_at_phase"),
        )

        # Only include sync_state in the SQL when the column exists (V42+ guard)
        # and a value was requested, to keep the query backward-compatible with V41.
        include_sync = sync_state is not None and self._has_sync_state_column()

        if version is None:
            if include_sync:
                self._conn.execute(
                    """INSERT INTO pipeline_runs
                       (project_id, run_id, pipeline_name, issue_id, current_phase_index,
                        status, phases, started_at, completed_at, metadata,
                        paused_at_phase, version, sync_state)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                       ON CONFLICT(run_id) DO UPDATE SET
                         current_phase_index=excluded.current_phase_index,
                         status=excluded.status,
                         phases=excluded.phases,
                         started_at=excluded.started_at,
                         completed_at=excluded.completed_at,
                         metadata=excluded.metadata,
                         paused_at_phase=excluded.paused_at_phase,
                         version=version+1,
                         sync_state=excluded.sync_state""",
                    (*params, sync_state),
                )
            else:
                self._conn.execute(
                    """INSERT INTO pipeline_runs
                       (project_id, run_id, pipeline_name, issue_id, current_phase_index,
                        status, phases, started_at, completed_at, metadata,
                        paused_at_phase, version)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                       ON CONFLICT(run_id) DO UPDATE SET
                         current_phase_index=excluded.current_phase_index,
                         status=excluded.status,
                         phases=excluded.phases,
                         started_at=excluded.started_at,
                         completed_at=excluded.completed_at,
                         metadata=excluded.metadata,
                         paused_at_phase=excluded.paused_at_phase,
                         version=version+1""",
                    params,
                )
        else:
            if include_sync:
                cur = self._conn.execute(
                    """UPDATE pipeline_runs SET
                         current_phase_index=?, status=?, phases=?,
                         started_at=?, completed_at=?, metadata=?,
                         paused_at_phase=?, version=version+1, sync_state=?
                       WHERE project_id=? AND run_id=? AND version=?""",
                    (
                        run.get("current_phase_index", 0),
                        run.get("status", "running"),
                        json.dumps(run.get("phases", [])),
                        run.get("started_at", ""),
                        run.get("completed_at"),
                        json.dumps(run.get("metadata", {})),
                        run.get("paused_at_phase"),
                        sync_state,
                        self._pid,
                        run["run_id"],
                        version,
                    ),
                )
            else:
                cur = self._conn.execute(
                    """UPDATE pipeline_runs SET
                         current_phase_index=?, status=?, phases=?,
                         started_at=?, completed_at=?, metadata=?,
                         paused_at_phase=?, version=version+1
                       WHERE project_id=? AND run_id=? AND version=?""",
                    (
                        run.get("current_phase_index", 0),
                        run.get("status", "running"),
                        json.dumps(run.get("phases", [])),
                        run.get("started_at", ""),
                        run.get("completed_at"),
                        json.dumps(run.get("metadata", {})),
                        run.get("paused_at_phase"),
                        self._pid,
                        run["run_id"],
                        version,
                    ),
                )
            if cur.rowcount == 0:
                raise OptimisticLockError(
                    f"run {run['run_id']} was modified by another writer "
                    f"(expected version {version})"
                )
        self._conn.commit()

    async def load(self, run_id: str) -> dict[str, Any] | None:
        """Return the run or None if unknown."""
        row = self._conn.execute(
            "SELECT * FROM pipeline_runs WHERE project_id = ? AND run_id = ?",
            (self._pid, run_id),
        ).fetchone()
        if row is None:
            return None
        return _row_to_dict(row)

    async def list_runs(self) -> list[dict[str, Any]]:
        """Return all runs for this project, newest first."""
        rows = self._conn.execute(
            "SELECT * FROM pipeline_runs WHERE project_id = ? ORDER BY started_at DESC",
            (self._pid,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    async def delete(self, run_id: str) -> None:
        """Remove a run. No-op if unknown."""
        self._conn.execute(
            "DELETE FROM pipeline_runs WHERE project_id = ? AND run_id = ?",
            (self._pid, run_id),
        )
        self._conn.commit()

    def local_db(self) -> tuple[sqlite3.Connection, str]:
        """Return (connection, project_id) for direct DB queries (e.g. prune).

        Intended for same-process callers (CLI commands) that need to query
        the local store directly.  Accessing ``_conn`` / ``_pid`` across a
        module boundary triggers pyright ``reportPrivateUsage`` — this method
        provides a typed, public seam.
        """
        return self._conn, self._pid

    # ------------------------------------------------------------------
    # S8371.2 sync_state helpers (V42+ only; fail-safe on V41 DBs)
    # ------------------------------------------------------------------

    def _has_sync_state_column(self) -> bool:
        """Return True when the pipeline_runs table has the sync_state column."""
        cols = {
            r[1]
            for r in self._conn.execute("PRAGMA table_info(pipeline_runs)").fetchall()
        }
        return "sync_state" in cols

    def mark_pending(self, run_id: str) -> None:
        """Mark a run as pending re-sync to the primary.

        No-op on V41 DBs (sync_state column absent) — fail-safe degradation.
        """
        if not self._has_sync_state_column():
            return
        self._conn.execute(
            "UPDATE pipeline_runs SET sync_state='pending'"
            " WHERE project_id=? AND run_id=?",
            (self._pid, run_id),
        )
        self._conn.commit()

    def mark_synced(self, run_id: str) -> None:
        """Clear sync_state after a successful push to the primary.

        No-op on V41 DBs — fail-safe degradation.
        """
        if not self._has_sync_state_column():
            return
        self._conn.execute(
            "UPDATE pipeline_runs SET sync_state=NULL WHERE project_id=? AND run_id=?",
            (self._pid, run_id),
        )
        self._conn.commit()

    def mark_pending_delete(self, run_id: str) -> None:
        """Mark a run for deferred delete on the primary.

        No-op on V41 DBs — fail-safe degradation.
        """
        if not self._has_sync_state_column():
            return
        self._conn.execute(
            "UPDATE pipeline_runs SET sync_state='pending_delete'"
            " WHERE project_id=? AND run_id=?",
            (self._pid, run_id),
        )
        self._conn.commit()

    def list_pending(self) -> list[dict[str, Any]]:
        """Return pending runs in FIFO order (started_at ASC, rowid ASC).

        Returns an empty list on V41 DBs — fail-safe degradation.
        """
        if not self._has_sync_state_column():
            return []
        rows = self._conn.execute(
            "SELECT * FROM pipeline_runs"
            " WHERE project_id=? AND sync_state IS NOT NULL"
            " ORDER BY started_at ASC, rowid ASC",
            (self._pid,),
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            d = _row_to_dict(row)
            # Preserve sync_state so the flush can dispatch pending_delete
            d["sync_state"] = row["sync_state"]
            result.append(d)
        return result

    def purge_local(self, run_id: str) -> None:
        """Physically delete a local row after the server has confirmed the delete.

        No-op if the run_id does not exist locally.
        """
        self._conn.execute(
            "DELETE FROM pipeline_runs WHERE project_id=? AND run_id=?",
            (self._pid, run_id),
        )
        self._conn.commit()


# ---------------------------------------------------------------------------
# Transport-based resolver — tri-state (ADR-075 / S4835.1)
# ---------------------------------------------------------------------------
#
# Priority:
#   1. RAISE_SERVER_URL set → ApiRunStore (thin HTTP client to raise-server)
#   2. RAISE_MCP_TRANSPORT=http → PostgresRunStore (server-side in-process,
#      backward compat for mcp_mount until server-side refactor)
#   3. Neither → SqliteRunStore (local offline)


def _is_http_request() -> bool:
    """True if the current MCP invocation is over HTTP transport (server-side)."""
    return os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http"


def get_run_store() -> PipelineRunStore:
    """Resolve the right store for the current context.

    Tri-state resolver (ADR-075):
    - RAISE_SERVER_URL set → ApiRunStore (thin HTTP client).
    - RAISE_MCP_TRANSPORT=http → PostgresRunStore (server in-process).
    - Neither → SqliteRunStore (local offline, WAL).
    """
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is not None:
        from raise_cli.pipeline.api_run_store import ApiRunStore
        from raise_cli.pipeline.resilient_run_store import ResilientRunStore

        server_url, api_key = creds
        primary = ApiRunStore(server_url=server_url, api_key=api_key)
        fallback = _local_sqlite_store()
        return ResilientRunStore(primary, fallback)

    if _is_http_request():
        from mcp.server.auth.middleware.auth_context import get_access_token
        from raise_server.mcp_mount import get_mcp_session_factory
        from raise_server.pipeline.run_store_db import PostgresRunStore

        token: Any = get_access_token()
        if token is None:
            raise RuntimeError(
                "pipeline tool invoked via HTTP without valid JWT — "
                "no filesystem fallback allowed on server",
            )
        return PostgresRunStore(
            get_mcp_session_factory(),
            org_id=token.org_id,
            member_id=token.member_id,
        )

    return _local_sqlite_store()


def _local_sqlite_store() -> SqliteRunStore:
    """Resolve the local SQLite store (global ~/.rai/raise.db).

    Used by the stdio branch and as the circuit-breaker fallback in server mode.
    D7: same resolution as the historic stdio inline block.
    """
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    root = resolve_checkout_root()
    conn = get_project_db(root)
    create_all(conn)
    return SqliteRunStore(conn, project_id=get_project_id(root))
