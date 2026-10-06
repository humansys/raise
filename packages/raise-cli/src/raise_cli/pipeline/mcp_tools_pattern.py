"""Pattern MCP tools — raise_pattern_query, raise_pattern_add, raise_pattern_reinforce."""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from raise_cli.memory.patterns_backend import (
    PatternsBackend,
    PatternValidationError,
    get_patterns_backend,
    is_http_request,
    upsert_pattern,
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
    if cwd:
        _sync_query_results_locally(_root, matches)
    return compact_response({"status": "ok", "results": matches})


def _sync_query_results_locally(root: Path, matches: list[dict[str, Any]]) -> None:
    """Upsert server-sourced query results into local SQLite (RAISE-15903).

    ``raise_pattern_query`` can resolve to ``ApiPatternsBackend`` or
    ``PostgresPatternsBackend`` (ADR-075 tri-state resolver), both of which
    return raw server UUIDs with zero local footprint. ``raise_pattern_reinforce``
    only ever resolves against local SQLite via ``original_id`` (RAISE-11074 —
    reinforce never dispatches to a remote backend), so a caller reinforcing a
    server-sourced id returned by query got a silent "not found". This closes
    the gap by upserting a local shadow row (original_id set) for any
    non-local result id not already resolvable locally, using data already in
    hand from the query response — no extra network I/O, no pull_patterns()
    call, bounded by the same ``limit`` the caller already requested.

    RAISE-15903 (redesign): the server's query response now carries the
    REAL ``scope``/``project_id``/``positives``/``negatives``/``evaluations``
    for the row it already queried (see ``PatternQueryItem`` and
    ``_row_to_dict`` server-side) — the shadow row is seeded with those real
    values, not fabricated zeros.

    Mixed-version rollout window: an older server that hasn't deployed the
    widened ``PatternQueryItem`` schema yet still returns the original
    narrow 5-key shape (no ``positives``/``negatives``/``evaluations``/
    ``scope``/``project_id``). Falling back to fabricated zeros for that
    shape would re-admit the original corruption vector (a 0/0/0 shadow
    row masquerading as real state), so this case is detected via the
    absence of ``positives`` and the shadow row is skipped entirely — the
    match still comes back in the query results for the caller to see, it
    just isn't upserted locally. A subsequent reinforce on that id then
    correctly falls through to ``raise_pattern_reinforce``'s existing
    not-found path (pull_patterns retry, then a loud error) instead of
    silently reinforcing a fabricated row.

    Best-effort: under real multi-tenant HTTP transport there is no caller
    checkout to write into (``root`` would be the shared server process CWD,
    not a tenant's project — RAISE-14655 tenant-isolation concern), so this
    is skipped entirely there. Any local-write failure is swallowed — query
    results must never be blocked by enrichment.

    Callers must also skip this entirely when ``cwd`` was empty — even under
    stdio transport, an empty ``cwd`` with server credentials configured
    resolves ``root`` to the MCP *server process's* own CWD (legacy AC10
    fallback, ``_caller_context.require_caller_cwd``), not the caller's
    checkout. Writing a shadow row there would key it to the wrong project
    identity, so ``raise_pattern_query`` only invokes this when ``cwd`` is
    truthy.
    """
    if is_http_request():
        return
    try:
        conn, project_id = _get_local_conn_and_project_id(root)
        for match in matches:
            server_id = match.get("id", "")
            if not server_id or _is_local_pattern_id(server_id):
                continue
            if _resolve_local_pattern_id(conn, server_id) is not None:
                continue
            if "positives" not in match:
                # Old/undeployed server: narrow 5-key response shape carries
                # no real counters. Skip the shadow row rather than seed it
                # with fabricated zeros (the original C1 corruption vector) —
                # the match still surfaces in query results, it just can't
                # be reinforced until the server deploys the widened schema.
                continue
            upsert_pattern(
                conn,
                project_id=str(match.get("project_id") or project_id),
                content=str(match.get("content", "")),
                pattern_type=str(match.get("type", "technical")),
                context=list(match.get("context") or []),
                learned_from=str(match.get("learned_from", "")),
                scope=str(match.get("scope", "project")),
                positives=int(match.get("positives", 0)),
                negatives=int(match.get("negatives", 0)),
                evaluations=int(match.get("evaluations", 0)),
                original_id=server_id,
                on_conflict="merge_max",
            )
    except Exception:  # noqa: BLE001 — enrichment must never block query results
        logger.debug("Local sync of query results failed", exc_info=True)


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

    RAISE-15903: server-sourced query results are synced into a local
    shadow row seeded with the server's REAL counters/scope/project_id
    (see ``_sync_query_results_locally`` and the widened server query
    response) — the row is accurate from the moment it's created, so this
    function needs no hydration/detection special-casing. It simply
    resolves locally, applies the vote, and pushes.

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
