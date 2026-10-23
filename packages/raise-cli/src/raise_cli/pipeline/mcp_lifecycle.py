"""MCP server lifecycle instrumentation (RAISE-15784).

Provides fail-open helpers that record startup/shutdown/crash/heartbeat events
to the global SQLite store so stranded pipeline runs become diagnosable.

Public surface:
    record_event         — sync, fail-open, writes one row to mcp_server_events
    start_heartbeat_task — schedules a repeating heartbeat coroutine
    prune_old_events     — removes stale rows older than N days, fail-open
    prune_heartbeats     — removes heartbeat rows older than N days, fail-open
    build_lifecycle_cm   — async CM that wires start/stop + heartbeat together
    install_sigterm_handler — registers SIGTERM handler that records 'crash'
    wire_mcp_lifecycle   — wires lifespan + SIGTERM into a FastMCP instance
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sqlite3
import sys
import types
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

from raise_cli.storage.connection import get_global_db
from raise_cli.storage.schema import ensure_schema

logger = logging.getLogger(__name__)

_PRUNE_BATCH = 5000


def _import_critical_modules() -> None:
    """Import modules that trigger Windows Defender scans on first load.

    Called from _prewarm_critical_modules() in a background thread so the
    Defender scan (30-200s) does not block the asyncio event loop (RAISE-18876).
    """
    import importlib

    for module_name in ("networkx", "raise_core.graph.query"):
        importlib.import_module(module_name)


def _prewarm_critical_modules() -> None:
    """Trigger first-import of heavy modules in a background thread. Fail-open."""
    try:
        _import_critical_modules()
        logger.debug("prewarm: critical modules imported successfully")
    except Exception:  # noqa: BLE001
        logger.debug("prewarm: import failed (non-fatal)", exc_info=True)


def record_event(
    event: str,
    *,
    pid: int,
    server_root: str,
    version: str,
    transport: str,
    session_id: str,
) -> None:
    """Record an MCP server lifecycle event. Sync, fail-open.

    Writes one row to ``mcp_server_events`` in ``~/.rai/raise.db``.
    All errors are caught and logged at DEBUG level — this function must
    never cause the server to exit or surface an error to a caller.
    """
    try:
        conn: sqlite3.Connection = get_global_db()
        ensure_schema(conn)
        conn.execute(
            """
            INSERT INTO mcp_server_events
                (event, pid, server_root, version, transport, session_id, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            """,
            (event, pid, server_root, version, transport, session_id),
        )
        conn.commit()
    except Exception:  # noqa: BLE001
        logger.debug("record_event(%r): suppressed error", event, exc_info=True)


async def heartbeat_loop(
    *,
    interval: int,
    pid: int,
    server_root: str,
    version: str,
    transport: str,
    session_id: str,
) -> None:
    """Async loop that emits heartbeat events every ``interval`` seconds."""
    while True:
        await asyncio.sleep(interval)
        record_event(
            "heartbeat",
            pid=pid,
            server_root=server_root,
            version=version,
            transport=transport,
            session_id=session_id,
        )


def start_heartbeat_task(
    *,
    interval: int = 60,
    pid: int,
    server_root: str,
    version: str,
    transport: str,
    session_id: str,
) -> asyncio.Task[None]:
    """Schedule a heartbeat coroutine on the running event loop.

    Returns the created Task so the caller can cancel it on shutdown.
    The default ``interval`` is 60 seconds.
    """
    return asyncio.create_task(
        heartbeat_loop(
            interval=interval,
            pid=pid,
            server_root=server_root,
            version=version,
            transport=transport,
            session_id=session_id,
        ),
        name="mcp-lifecycle-heartbeat",
    )


def prune_old_events(*, days: int = 30) -> None:
    """Delete ``mcp_server_events`` rows older than ``days`` days. Sync, fail-open."""
    try:
        conn: sqlite3.Connection = get_global_db()
        ensure_schema(conn)
        conn.execute(
            "DELETE FROM mcp_server_events WHERE recorded_at < datetime('now', ?)",
            (f"-{days} days",),
        )
        conn.commit()
    except Exception:  # noqa: BLE001
        logger.debug("prune_old_events: suppressed error", exc_info=True)


def prune_heartbeats(*, days: int = 7) -> None:
    """Delete ``heartbeat`` rows older than ``days`` days. Sync, fail-open.

    RAISE-18989: one heartbeat per minute per server accumulates without
    bound. start/stop/crash rows are the diagnostic record and are kept.
    Deletes in batches, committing each, so a first run over a large backlog
    never holds the write lock long enough to starve sibling servers. The
    cutoff uses the same ISO-Z format as ``recorded_at``.
    """
    try:
        conn: sqlite3.Connection = get_global_db()
        ensure_schema(conn)
        while True:
            cur = conn.execute(
                "DELETE FROM mcp_server_events WHERE rowid IN ("
                " SELECT rowid FROM mcp_server_events"
                " WHERE event = 'heartbeat'"
                " AND recorded_at < strftime('%Y-%m-%dT%H:%M:%SZ', 'now', ?)"
                " LIMIT ?)",
                (f"-{days} days", _PRUNE_BATCH),
            )
            conn.commit()
            if cur.rowcount < _PRUNE_BATCH:
                break
    except Exception:  # noqa: BLE001
        logger.debug("prune_heartbeats: suppressed error", exc_info=True)


@asynccontextmanager
async def build_lifecycle_cm(
    *,
    server_root: str,
    version: str,
    transport: str,
    session_id: str,
) -> AsyncGenerator[None, None]:
    """Async context manager that instruments MCP server lifecycle.

    On entry: records ``start`` event, prunes stale heartbeats (RAISE-18989),
    schedules heartbeat task.
    On exit (normal or exception): cancels heartbeat, records ``stop`` event.

    Prefer ``wire_mcp_lifecycle()`` for one-call setup from ``mcp_server.py``.
    """
    pid = os.getpid()
    record_event(
        "start",
        pid=pid,
        server_root=server_root,
        version=version,
        transport=transport,
        session_id=session_id,
    )
    prune_heartbeats()
    task = start_heartbeat_task(
        interval=60,
        pid=pid,
        server_root=server_root,
        version=version,
        transport=transport,
        session_id=session_id,
    )
    if sys.platform == "win32":
        asyncio.create_task(
            asyncio.to_thread(_prewarm_critical_modules),
            name="mcp-prewarm-win32",
        )
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        record_event(
            "stop",
            pid=pid,
            server_root=server_root,
            version=version,
            transport=transport,
            session_id=session_id,
        )


def install_sigterm_handler(
    *,
    pid: int,
    server_root: str,
    version: str,
    transport: str,
    session_id: str,
) -> None:
    """Register a SIGTERM handler that records a 'crash' event before terminating.

    After recording the event the default SIGTERM disposition is restored and
    the signal is re-sent so the process terminates normally.
    """

    def _handler(signum: int, frame: types.FrameType | None) -> None:  # noqa: ARG001
        record_event(
            "crash",
            pid=pid,
            server_root=server_root,
            version=version,
            transport=transport,
            session_id=session_id,
        )
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.kill(pid, signal.SIGTERM)

    signal.signal(signal.SIGTERM, _handler)


def wire_mcp_lifecycle(
    mcp_instance: Any,
    *,
    server_root: str = "",
    transport: str = "stdio",
    version: str | None = None,
    session_id: str | None = None,
) -> None:
    """Wire lifecycle instrumentation into a FastMCP instance.

    Injects ``build_lifecycle_cm`` as the MCP lifespan handler (D2) and
    installs a SIGTERM handler that records 'crash' before terminating (D4).

    ``version`` defaults to the installed ``raise-cli`` package version.
    ``session_id`` defaults to ``RAI_SESSION_ID`` env var (or "").

    Must be called before ``mcp_instance.run()``.
    """
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.server import lifespan_wrapper

    if version is None:
        try:
            from importlib.metadata import version as _pkg_version

            version = _pkg_version("raise-cli")
        except Exception:  # noqa: BLE001
            version = ""
    if session_id is None:
        session_id = os.environ.get("RAI_SESSION_ID", "")

    pid = os.getpid()
    _version = version
    _session_id = session_id

    def _lifecycle(_app: FastMCP[None]) -> AbstractAsyncContextManager[None]:  # pyright: ignore[reportMissingTypeArgument]
        return build_lifecycle_cm(
            server_root=server_root,
            version=_version,
            transport=transport,
            session_id=_session_id,
        )

    mcp_instance._mcp_server.lifespan = lifespan_wrapper(mcp_instance, _lifecycle)  # pyright: ignore[reportPrivateUsage]
    install_sigterm_handler(
        pid=pid,
        server_root=server_root,
        version=_version,
        transport=transport,
        session_id=_session_id,
    )
