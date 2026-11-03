"""Graph MCP tools — raise_graph_query, raise_graph_context."""

from __future__ import annotations

import asyncio
import contextvars
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from raise_cli.graph.query_backend import get_graph_backend
from raise_cli.output.formatters.backlog_node import is_backlog_node, render_t0
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_instance import mcp
from raise_core.graph.filters import Condition, GraphFilter


def _timeout_response(message: str) -> str:
    """Build a timeout JSON response, with an init hint on win32."""
    resp: dict[str, Any] = {"status": "ok", "timeout": True, "results": []}
    if sys.platform == "win32":
        resp["message"] = message
    return json.dumps(resp)


def _graph_query_sync(
    root: Path | None,
    query: str,
    limit: int,
    parsed_filters: GraphFilter | None,
) -> dict[str, Any]:
    """Run graph query in a thread-local event loop for use from run_in_executor.

    asyncio.run() creates a new event loop in the calling thread, which is
    safe because run_in_executor threads have no running event loop (RAISE-18876).
    """
    backend = get_graph_backend(root=root)
    if parsed_filters is not None:
        return asyncio.run(backend.query(query, limit, filters=parsed_filters))
    return asyncio.run(backend.query(query, limit))


def _strip_verbose_fields(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Non-verbose path: T0-render backlog content, then drop 'properties' (R6).

    For backlog nodes (D3.8, RAISE-16449), 'content' becomes the T0 line
    before 'properties' is dropped, so description/comments never leak.
    Non-backlog nodes and backlog nodes lacking key/summary are untouched.
    """
    for node in nodes:
        properties = node.get("properties")
        if is_backlog_node(node.get("node_type", ""), properties):
            node["content"] = render_t0(cast("Mapping[str, Any]", properties))
    return [{k: v for k, v in n.items() if k != "properties"} for n in nodes]


@mcp.tool()
async def raise_graph_query(
    query: str,
    limit: int = 5,
    verbose: bool = False,
    filters: list[dict[str, Any]] | None = None,
    cwd: str = "",
) -> str:
    """Search the RaiSE knowledge graph for relevant nodes.

    Args:
        query: Search terms (e.g., "pipeline persistence", "testing patterns").
        limit: Maximum results to return (default 5).
        verbose: When False (default), strips 'properties' from each node (R6).
            Pass True to receive full node data including heavy frontmatter.
            Auto-set to True when filters are present.
        filters: Optional list of filter conditions. Each dict has keys:
            field (str), op (one of: eq, neq, in, nin, lt, lte, gt, gte,
            contains, exists, startswith), value (str | int | list | None).
            Multiple conditions are AND-combined.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_graph_query")
    if isinstance(_root, dict):
        return json.dumps(_root)

    parsed_filters: GraphFilter | None = None
    if filters:
        try:
            parsed_filters = GraphFilter(
                conditions=[Condition.model_validate(f) for f in filters]
            )
        except (ValidationError, TypeError) as exc:
            return json.dumps({"status": "error", "reason": f"Invalid filter: {exc}"})
        verbose = True

    try:
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(
            None,
            contextvars.copy_context().run,
            lambda: _graph_query_sync(
                _root if cwd else None, query, limit, parsed_filters
            ),
        )
        try:
            results = await asyncio.wait_for(asyncio.shield(fut), timeout=110.0)
        except TimeoutError:
            return _timeout_response(
                "The knowledge engine is still initializing. This may take up to 3 min on first startup — retry then."
            )
    except (RuntimeError, TypeError) as exc:
        return json.dumps({"status": "error", "reason": str(exc)})

    # Normalize: FilesystemBackend returns {results:[...], total, query, limit};
    # mocks and ApiBackend may return a list directly.
    if isinstance(results, list):
        nodes: list[dict[str, Any]] = cast("list[dict[str, Any]]", results)
        total: int | None = None
    else:
        if results.get("status") == "error":
            return json.dumps(results)
        nodes = cast("list[dict[str, Any]]", results.get("results", []))
        total = results.get("total")

    if not verbose:
        nodes = _strip_verbose_fields(nodes)

    payload: dict[str, Any] = {"status": "ok", "results": nodes}
    if total is not None:
        payload["total"] = total
    return compact_response(payload)


@mcp.tool()
async def raise_graph_context(module_id: str, cwd: str = "") -> str:
    """Get context for a specific module from the knowledge graph.

    Args:
        module_id: Module identifier (e.g., "mod-pipeline", "mod-memory").
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_graph_context")
    if isinstance(_root, dict):
        return json.dumps(_root)
    try:
        backend = get_graph_backend(root=_root if cwd else None)
        result = await backend.context(module_id)
    except RuntimeError as exc:
        return json.dumps({"status": "error", "reason": str(exc)})
    return compact_response({"status": "ok", "result": result})
