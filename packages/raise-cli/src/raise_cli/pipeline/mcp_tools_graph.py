"""Graph MCP tools — raise_graph_query, raise_graph_context."""

from __future__ import annotations

import json
from typing import Any, cast

from pydantic import ValidationError

from raise_cli.graph.query_backend import get_graph_backend
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_instance import mcp
from raise_core.graph.filters import Condition, GraphFilter


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
        backend = get_graph_backend(root=_root if cwd else None)
        if parsed_filters is not None:
            results = await backend.query(query, limit, filters=parsed_filters)
        else:
            results = await backend.query(query, limit)
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
        nodes = [{k: v for k, v in n.items() if k != "properties"} for n in nodes]

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
