"""Built-in PipelineEventHook — persist BacklogTransitionEvent to SQLite (RAISE-15051).

Listens for ``pipeline:backlog_transition`` events (emitted by the engine on
every applied backlog transition) and writes them to the
``pipeline_backlog_events`` table (V62 migration).

The table is the source of truth for ``rai pipeline prune`` eligibility: a
terminal run is eligible only when every phase with ``outcome=applied`` has a
matching row in this table.

Fail-open contract: write failures are caught, logged, and return
``HookResult(status="ok")`` — a failed record must never block the pipeline.

Architecture: follows the same pattern as ``graph_update.py`` (direct SQLite
write in the hook, no service abstraction needed for this simple append-only
use).
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import UTC, datetime
from typing import ClassVar

from raise_cli.hooks.events import BacklogTransitionEvent, HookEvent, HookResult

logger = logging.getLogger(__name__)


class PipelineEventHook:
    """Persist ``BacklogTransitionEvent`` rows to ``pipeline_backlog_events``.

    Registered via ``rai.hooks`` entry point in pyproject.toml.

    The hook may be instantiated in two modes:
    - **Entry-point mode** (no args): resolves DB connection lazily from the
      global ``~/.rai/raise.db`` on first call.
    - **Test mode** (``conn=`` + ``project_id=``): uses the supplied
      in-memory connection directly, bypassing filesystem resolution.
    """

    events: ClassVar[list[str]] = ["pipeline:backlog_transition"]
    priority: ClassVar[int] = 0
    timeout: ClassVar[float] = 5.0

    def __init__(
        self,
        conn: sqlite3.Connection | None = None,
        project_id: str | None = None,
    ) -> None:
        self._conn = conn
        self._project_id = project_id

    def handle(self, event: HookEvent) -> HookResult:
        """Persist BacklogTransitionEvent to pipeline_backlog_events table."""
        if not isinstance(event, BacklogTransitionEvent):
            return HookResult(status="ok")
        try:
            conn, project_id = self._resolve_db()
            conn.execute(
                """INSERT INTO pipeline_backlog_events
                   (project_id, run_id, phase_id, issue_key, from_status, to_slug, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    project_id,
                    event.run_id,
                    event.phase_id,
                    event.issue_key,
                    event.from_status,
                    event.to_slug,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "PipelineEventHook: failed to persist BacklogTransitionEvent "
                "run_id=%s phase_id=%s: %s",
                getattr(event, "run_id", "?"),
                getattr(event, "phase_id", "?"),
                exc,
            )
        return HookResult(status="ok")

    def _resolve_db(self) -> tuple[sqlite3.Connection, str]:
        """Return (connection, project_id) — either injected or lazily resolved."""
        if self._conn is not None and self._project_id is not None:
            return self._conn, self._project_id

        from raise_cli.config.paths import resolve_checkout_root
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        root = resolve_checkout_root()
        conn = get_project_db(root)
        try:
            create_all(conn)
        except Exception:
            conn.close()
            raise
        project_id = get_project_id(root)
        self._conn = conn
        self._project_id = project_id
        return conn, project_id
