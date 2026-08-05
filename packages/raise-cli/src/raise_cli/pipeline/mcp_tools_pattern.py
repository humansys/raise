"""Pattern MCP tools — raise_pattern_query, raise_pattern_add, raise_pattern_reinforce."""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from pathlib import Path

from raise_cli.memory.patterns_backend import (
    PatternsBackend,
    PatternValidationError,
    get_patterns_backend,
)
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_instance import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def raise_pattern_query(keywords: str, limit: int = 10, cwd: str = "") -> str:
    """Search RaiSE patterns by keywords.

    Searches pattern content and context tags for matching keywords.

    Args:
        keywords: Space-separated search terms (e.g., "testing singleton").
        limit: Maximum results to return (default 10).
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_pattern_query")
    if isinstance(_root, dict):
        return json.dumps(_root)
    try:
        backend = get_patterns_backend(root=_root if cwd else None)
        matches = await backend.query(keywords.split(), limit)
    except RuntimeError as exc:
        return json.dumps({"status": "error", "reason": str(exc)})
    return compact_response({"status": "ok", "results": matches})


@mcp.tool()
async def raise_pattern_add(
    content: str,
    context: str = "",
    pattern_type: str = "technical",
    from_story: str = "",
    cwd: str = "",
) -> str:
    """Add a new pattern to memory.

    Args:
        content: Pattern description text.
        context: Comma-separated context keywords.
        pattern_type: Pattern type (technical, process, architecture, approach, risk, codebase).
        from_story: Source story ID (e.g., "S1305.8").
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_pattern_add")
    if isinstance(_root, dict):
        return json.dumps(_root)
    context_tags = [t.strip() for t in context.split(",") if t.strip()]
    try:
        conn, _project_id = _get_local_conn_and_project_id(_root)
        backend = _build_local_backend(conn, _project_id, _root if cwd else None)
        result = await backend.add(
            content=content,
            context_tags=context_tags,
            pattern_type=pattern_type,
            from_story=from_story,
        )
    except PatternValidationError as exc:
        return json.dumps({"status": "rejected", "reason": exc.reason})
    except RuntimeError as exc:
        return json.dumps({"status": "error", "reason": str(exc)})
    if "error" in result:
        return json.dumps({"status": "error", "reason": result["error"]})
    try:
        from raise_cli.memory.sync import attempt_immediate_push, enqueue_push

        enqueue_push(conn, result["pattern_id"])
        attempt_immediate_push(conn, result["pattern_id"])
    except Exception:  # noqa: BLE001 — push failure must never block add
        logger.debug(
            "Pattern push failed after add (queued for retry): %s",
            result["pattern_id"],
            exc_info=True,
        )
    return compact_response({"status": "ok", **result})


def _is_local_pattern_id(pattern_id: str) -> bool:
    """Local-namespace IDs (PAT-*) are anything that isn't a server UUID."""
    try:
        uuid.UUID(pattern_id)
    except ValueError:
        return True
    return False


def _get_local_conn_and_project_id(root: Path) -> tuple[sqlite3.Connection, str]:
    """Resolve the local project DB connection + canonical project_id.

    Anchored to the caller's validated checkout root (S15457.2) — never the
    MCP server process CWD.
    """
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    project_root = resolve_checkout_root(root)
    conn = get_project_db(project_root)
    create_all(conn)
    return conn, get_project_id(project_root)


def _build_local_backend(
    conn: sqlite3.Connection, project_id: str, project_root: Path | None
) -> PatternsBackend:
    """Construct SqlitePatternsBackend from an already-resolved connection.

    Avoids opening a second connection when the caller already holds one
    via _get_local_conn_and_project_id.
    """
    from raise_cli.memory.patterns_backend import (
        SqlitePatternsBackend,
        migrate_patterns_to_sqlite,
    )

    migrate_patterns_to_sqlite(conn, project_id=project_id)
    return SqlitePatternsBackend(conn, project_id=project_id, project_root=project_root)


def _resolve_local_pattern_id(conn: sqlite3.Connection, server_uuid: str) -> str | None:
    """Look up the local pattern_id for a server UUID via original_id.

    Symmetric to _resolve_server_id (which goes pattern_id -> original_id);
    this goes the other direction, original_id -> pattern_id.
    """
    row = conn.execute(
        "SELECT pattern_id FROM patterns WHERE original_id = ?",
        (server_uuid,),
    ).fetchone()
    return row[0] if row is not None else None


@mcp.tool()
async def raise_pattern_reinforce(
    pattern_id: str,
    vote: int = 1,
    from_story: str = "",
    cwd: str = "",
) -> str:
    """Reinforce a pattern with a vote signal.

    Called at story-review to record whether a pattern was applied (1),
    not relevant (0), or contradicted (-1).

    Every id resolves to a LOCAL row and is reinforced through the local
    backend only — the v1 HTTP reinforce (410) and in-process Postgres
    reinforce (hardcoded no-op) never move the counters the Wilson scorer
    reads. Propagation to the server happens via the same v2 push
    (enqueue_push/attempt_immediate_push) that `rai pattern add` already
    uses (RAISE-11074).

    Args:
        pattern_id: Pattern ID (e.g., "PAT-E-039") or a bare server UUID.
        vote: Vote value: 1 (applied), 0 (N/A), -1 (contradicted).
        from_story: Source story ID (e.g., "S1305.8").
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_pattern_reinforce")
    if isinstance(_root, dict):
        return json.dumps(_root)
    try:
        conn, project_id = _get_local_conn_and_project_id(_root)

        if _is_local_pattern_id(pattern_id):
            local_pattern_id = pattern_id
        else:
            local_pattern_id = _resolve_local_pattern_id(conn, pattern_id)
            if local_pattern_id is None:
                from raise_cli.memory.sync import pull_patterns

                pull_patterns(conn, project_id=project_id)
                local_pattern_id = _resolve_local_pattern_id(conn, pattern_id)
            if local_pattern_id is None:
                return json.dumps(
                    {
                        "status": "error",
                        "reason": (
                            f"Pattern '{pattern_id}' not found locally or on server"
                        ),
                    }
                )

        backend = _build_local_backend(conn, project_id, _root if cwd else None)
        result = await backend.reinforce(
            pattern_id=local_pattern_id,
            vote=vote,
            from_story=from_story,
        )
        # vote=0 is a no-op (counters unchanged) — nothing to push.
        if "error" not in result and result.get("status") != "skipped":
            try:
                from raise_cli.memory.sync import attempt_immediate_push, enqueue_push

                enqueue_push(conn, local_pattern_id)
                attempt_immediate_push(conn, local_pattern_id)
            except Exception:  # noqa: BLE001 — push failure must never block reinforce
                logger.debug(
                    "Pattern push failed after reinforce (queued for retry): %s",
                    local_pattern_id,
                    exc_info=True,
                )
    except (RuntimeError, ValueError) as exc:
        return json.dumps({"status": "error", "reason": str(exc)})
    if "error" in result:
        return json.dumps({"status": "error", "reason": result["error"]})
    # result may carry its own "status" (e.g. "updated") — outer "ok" must win.
    return compact_response({**result, "status": "ok"})
