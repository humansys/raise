"""Built-in GraphAutoUpdateHook — rebuild graph on work close.

Listens to work:lifecycle events and triggers a full graph rebuild when
a story or epic closes. Platform-agnostic: any agent calling
``rai signal emit-work`` triggers this hook.

Architecture: ADR-085 (Graph Auto-Update Trigger Strategy)
"""

from __future__ import annotations

import logging
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from raise_cli.config.paths import checkout_scope_id, resolve_checkout_root
from raise_cli.hooks.events import HookEvent, HookResult, WorkLifecycleEvent

logger = logging.getLogger(__name__)

DEBOUNCE_SECONDS = 60.0


class GraphAutoUpdateHook:
    """Rebuild the knowledge graph when a story or epic closes.

    Subscribes to ``work:lifecycle`` and filters for ``event=complete``
    + ``phase=close``. Runs a full ``GraphBuilder.build()`` with error
    isolation — failures log a warning and never block work close.

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = ["work:lifecycle"]
    priority: ClassVar[int] = -10
    timeout: ClassVar[float] = 60.0

    def handle(self, event: HookEvent) -> HookResult:
        """Rebuild graph if this is a work-close event."""
        if not isinstance(event, WorkLifecycleEvent):
            return HookResult(status="ok")
        if event.event != "complete" or event.phase != "close":
            return HookResult(status="ok")

        # RAISE-13319 F5: key the rebuilt graph under the ACTIVE checkout, not
        # resolve_repo_root() (the MAIN checkout). get_active_backend keys
        # graph_nodes by get_project_id(root) — a LOCAL key that must match
        # the checkout `rai graph query` reads from, else the graph splits
        # across two project_ids. resolve_checkout_root() never returns None
        # (falls back to cwd), so guard on RaiSE-project presence instead.
        root = resolve_checkout_root()
        if not (root / ".raise").is_dir():
            return HookResult(
                status="ok", message="No RaiSE project — skipped graph rebuild"
            )

        if _is_recent(root):
            return HookResult(
                status="ok",
                message="Debounce — recent build exists, skipped",
            )

        try:
            return _rebuild(root)
        except Exception as exc:  # noqa: BLE001
            msg = f"{type(exc).__name__}: {exc}"
            logger.warning("Graph auto-update failed: %s", msg)
            return HookResult(status="error", message=msg)


def _is_recent(root: Path) -> bool:
    """Check if THIS checkout's most recent build is within DEBOUNCE_SECONDS.

    RAISE-15607: debouncing by project_id alone let a build in worktree A
    suppress the rebuild in worktree B — B's partition would stay empty or
    stale while the hook reported a recent build. The scope must be the
    checkout, exactly like the graph rows themselves.
    """
    from raise_cli.storage.connection import get_project_db_path, get_project_id

    try:
        project_id = get_project_id(root)
        db_path = get_project_db_path(root)
        if not db_path.is_file():
            return False
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT built_at FROM graph_builds"
                " WHERE project_id = ? AND checkout_id = ?"
                " ORDER BY built_at DESC LIMIT 1",
                (project_id, checkout_scope_id(root)),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return False
        built_at = datetime.fromisoformat(row[0])
        age = time.time() - built_at.timestamp()
        return age < DEBOUNCE_SECONDS
    except Exception:  # noqa: BLE001 — debounce must not crash the hook
        return False


def _rebuild(root: Path) -> HookResult:
    """Execute full graph rebuild and persist results."""
    from raise_cli.context.builder import GraphBuilder
    from raise_cli.graph.backends import get_active_backend
    from raise_cli.storage.connection import get_project_db_path, get_project_id
    from raise_cli.storage.schema import create_all as _create_all
    from raise_core.discovery.symbols import SymbolDepth

    builder = GraphBuilder(project_root=root, symbol_depth=SymbolDepth.FUNCTIONS)
    graph = builder.build()

    index_path = root / ".raise" / "rai" / "memory" / "index.json"
    backend = get_active_backend(index_path, project_root=root)
    backend.persist(graph)

    # Write build record to SQLite (RAISE-14852)
    try:
        project_id = get_project_id(root)
        db_path = get_project_db_path(root)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        try:
            _create_all(conn)
            conn.execute(
                "INSERT INTO graph_builds"
                " (project_id, checkout_id, built_at, node_count, symbol_depth)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    project_id,
                    checkout_scope_id(root),  # RAISE-15607 — scope the record
                    datetime.now(tz=UTC).isoformat(),
                    graph.node_count,
                    "functions",
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001 — metadata write must not block the rebuild
        logger.warning("Failed to persist graph_builds record", exc_info=True)

    logger.info(
        "Graph auto-updated: %d nodes (%s)",
        graph.node_count,
        root.name,
    )
    return HookResult(
        status="ok",
        message=f"Graph rebuilt — {graph.node_count} nodes",
    )
