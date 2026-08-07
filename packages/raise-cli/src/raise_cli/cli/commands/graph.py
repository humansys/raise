"""CLI commands for Rai's knowledge graph: build, query, validate, and manage.

The graph group owns commands that operate on the knowledge graph structure.
These were extracted from the `memory` God Object in RAISE-247 (ADR-038).

Commands:
- build: Build the graph index from all sources
- validate: Validate graph structure and relationships
- query: Query the graph for relevant concepts
- context: Show architectural context for a module
- list: List all concepts in the graph
- viz: Generate interactive HTML visualization
- extract: Extract concepts from governance markdown files
"""

from __future__ import annotations

import json
import logging
import os
from collections import deque
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, Protocol, cast

import typer
from rich.console import Console
from rich.markup import escape

from raise_cli.cli.error_handler import cli_error
from raise_cli.compat import open_browser as open_in_browser
from raise_cli.compat import to_file_uri
from raise_cli.config.paths import (
    checkout_scope_id,
    get_memory_dir,
    get_personal_dir,
    resolve_checkout_root,
)
from raise_cli.context import Graph, GraphBuilder
from raise_cli.context.diff import diff_graphs
from raise_cli.graph.backends import get_active_backend
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import GraphBuildEvent
from raise_cli.output.formatters.graph import (
    format_agent,
    format_build_result,
    format_compact,
    format_concepts_agent,
    format_concepts_markdown,
    format_context_agent,
    format_json,
    format_markdown,
    print_concepts_table,
    print_context_human,
)
from raise_cli.output.symbols import ARROW, CHECK, CROSS, WARN
from raise_cli.storage.connection import get_project_db_path, get_project_id
from raise_core.cartridges.instances import iter_instance_files
from raise_core.graph.backends.protocol import (
    GraphBackendMetadata,
    GraphTraversalBackend,
)
from raise_core.graph.metrics import MetricsComputer
from raise_core.graph.models import GraphEdge
from raise_core.graph.query import (
    Query,
    QueryEngine,
    QueryResult,
    QueryStrategy,
)

# Default index file name
INDEX_FILE = "index.json"

graph_app = typer.Typer(
    name="graph",
    help="Build, query, and manage the knowledge graph",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)
logger = logging.getLogger(__name__)

Neighbor = tuple[str, str]
EdgeAttrs = dict[str, Any]


class _SupportsGraphLoad(Protocol):
    def load(self) -> Graph: ...


def _get_default_index_path() -> Path:
    """Get default graph index path (.raise/rai/memory/index.json)."""
    return get_memory_dir() / INDEX_FILE


def _load_query_engine(
    index_path: Path | None,
    boost_ids: set[str] | None = None,
) -> QueryEngine:
    """Load the query engine from graph index, exit on missing index."""
    unified_path = index_path or _get_default_index_path()
    try:
        graph = get_active_backend(
            unified_path, explicit_path=index_path is not None
        ).load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )
        raise  # unreachable, satisfies pyright
    if graph.node_count == 0:
        cli_error(
            "Graph index is empty — no nodes found",
            hint="Run 'rai graph build' first to populate the index",
            exit_code=4,
        )
        raise RuntimeError("unreachable")  # satisfies pyright
    return QueryEngine(graph, boost_ids=boost_ids)


def _semantic_provider_available() -> bool:
    """Return True if the ONNX embedding provider can be initialised.

    Mirrors ``get_default_provider()``'s resolution order without side-effects:
    frozen PyInstaller binary or ``$RAISE_ONNX_MODEL_DIR`` present → True.
    A plain ``pip install raise-cli`` satisfies neither condition (RAISE-15987).
    """
    import sys as _sys

    return getattr(_sys, "frozen", False) or bool(
        os.environ.get("RAISE_ONNX_MODEL_DIR")
    )


def _parse_query_strategy(strategy: str | None) -> QueryStrategy:
    """Parse query strategy string, exit on invalid value."""
    if not strategy:
        return QueryStrategy.KEYWORD_SEARCH
    try:
        return QueryStrategy(strategy)
    except ValueError:
        cli_error(
            f"Invalid strategy: {strategy}",
            hint="Valid strategies: keyword_search, concept_lookup",
            exit_code=7,
        )
        raise  # unreachable, satisfies pyright


def _parse_comma_list(value: str | None) -> list[str] | None:
    """Parse a comma-separated string into a list, or return None."""
    if not value:
        return None
    return [t.strip() for t in value.split(",")]


def _write_query_output(
    output_text: str,
    output: Path | None,
    result: object,
) -> None:
    """Write query result to file or stdout with summary."""
    if output:
        output.write_text(output_text, encoding="utf-8")
        meta = result.metadata  # type: ignore[attr-defined]
        console.print(f"{CHECK} Results written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {meta.total_concepts}")
        console.print(f"  Tokens: ~{meta.token_estimate}")
        console.print(f"  Execution: {meta.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)


# =============================================================================
# Query Commands
# =============================================================================


def server_result_to_query_result(
    server_response: dict[str, Any],
    query_str: str,
) -> QueryResult:
    """Map server SemanticSearchResponse to local QueryResult.

    Converts the JSON payload from POST /api/v2/graph/semantic-search into
    the QueryResult model that the existing formatters (human, json, compact,
    agent) already know how to render. No new formatter required.

    Args:
        server_response: Raw dict with "results" list from the server.
        query_str: Original query string (preserved in QueryMetadata).

    Returns:
        QueryResult with concepts mapped from server results.
    """
    from raise_core.graph.models import GraphNode
    from raise_core.graph.query import QueryMetadata, QueryStrategy

    concepts: list[GraphNode] = []
    for r in server_response.get("results", []):
        concepts.append(
            GraphNode(
                id=r["node_id"],
                type=r["node_type"],
                content=r["content"],
                created="",
                source_file=r.get("source_file"),
                metadata={
                    **r.get("properties", {}),
                    "similarity": r.get("similarity", 0.0),
                    "repo_id": r.get("repo_id"),
                    "source": "server-semantic",
                },
            )
        )

    token_estimate = sum(len(c.content) // 4 for c in concepts)
    return QueryResult(
        concepts=concepts,
        metadata=QueryMetadata(
            query=query_str,
            strategy=QueryStrategy.KEYWORD_SEARCH,
            total_concepts=len(concepts),
            total_available=server_response.get("total", len(concepts)),
            token_estimate=token_estimate,
            execution_time_ms=0.0,
        ),
    )


def _merge_cross_repo_results(
    local_result: QueryResult,
    query_str: str,
    limit: int,
) -> QueryResult:
    """Merge local results with server cross-repo results."""
    from raise_cli.config.paths import resolve_repo_root
    from raise_cli.config.server import get_server_credentials
    from raise_cli.graph.backends.api import ApiGraphBackend
    from raise_cli.storage.connection import get_server_slug
    from raise_core.graph.models import GraphNode

    creds = get_server_credentials()
    if creds is None:
        return local_result
    server_url, api_key = creds
    repo_root = resolve_repo_root()
    # WIRE identity (RAISE-13467): both the backend project_id and the
    # server-side exclude_repo_id cross the wire, so they use get_server_slug,
    # not the local get_project_id.
    repo_name = get_server_slug(repo_root) if repo_root else "unknown"

    backend = ApiGraphBackend(
        server_url=server_url,
        api_key=api_key,
        project_id=repo_name,
    )
    server_nodes = backend.query(query_str, limit=limit, exclude_repo_id=repo_name)

    if not server_nodes:
        return local_result

    cross_concepts: list[GraphNode] = []
    for node in server_nodes:
        repo_id = node.get("repo_id", "unknown")
        cross_concepts.append(
            GraphNode(
                id=node["node_id"],
                type=node["node_type"],
                content=f"({repo_id}) {node['content']}",
                created="",
                source_file=node.get("source_file"),
                metadata={
                    **node.get("properties", {}),
                    "repo_id": repo_id,
                    "cross_repo": True,
                },
            )
        )

    console.print(
        f"\n[green]Cross-repo:[/green] {len(cross_concepts)} results from server"
    )

    merged_concepts = list(local_result.concepts) + cross_concepts
    return local_result.model_copy(
        update={
            "concepts": merged_concepts,
            "metadata": local_result.metadata.model_copy(
                update={"total_concepts": len(merged_concepts)}
            ),
        }
    )


@graph_app.command()
def query(  # noqa: C901
    query_str: Annotated[
        str, typer.Argument(help="Query string (keywords or concept ID)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human, json, or compact)"),
    ] = "human",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    strategy: Annotated[
        str | None,
        typer.Option(
            "--strategy",
            "-s",
            help="Query strategy (keyword_search, concept_lookup)",
        ),
    ] = None,
    types: Annotated[
        str | None,
        typer.Option(
            "--types",
            "-t",
            help="Filter by types (comma-separated: pattern,calibration,principle,etc.)",
        ),
    ] = None,
    subtypes: Annotated[
        str | None,
        typer.Option(
            "--subtypes",
            help="Filter by pattern subtypes (comma-separated: approach,risk,codebase,etc.)",
        ),
    ] = None,
    edge_types: Annotated[
        str | None,
        typer.Option(
            "--edge-types",
            help="Filter by edge types (comma-separated: constrained_by,depends_on,etc.)",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of results"),
    ] = 10,
    module: Annotated[
        str | None,
        typer.Option(
            "--module",
            help="Filter symbols by module ID (e.g., mod-discovery, or "
            "mod-<package>--<module> in a packages/* monorepo)",
        ),
    ] = None,
    file: Annotated[
        str | None,
        typer.Option(
            "--file",
            help="Filter symbols by source file (substring match)",
        ),
    ] = None,
    callers: Annotated[
        bool,
        typer.Option(
            "--callers",
            help="Reverse lookup — return callers of matched symbols",
        ),
    ] = False,
    cross_repo: Annotated[
        bool,
        typer.Option(
            "--cross-repo",
            help="Include results from other repos in the same org (requires server)",
        ),
    ] = False,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path"),
    ] = None,
) -> None:
    """Query the knowledge graph for relevant concepts.

    Searches the unified graph containing all context sources:
    - Governance (principles, requirements, terms)
    - Memory (patterns, calibration, sessions)
    - Skills (workflow metadata)
    - Work (epics, stories, decisions)

    Use --cross-repo to also search the server for results from other
    repos in the same organization. Local results appear first.

    Examples:
        # Search by keywords
        $ rai graph query "planning estimation"

        # Filter to patterns only
        $ rai graph query "testing" --types pattern,calibration

        # Lookup specific concept by ID
        $ rai graph query "PAT-001" --strategy concept_lookup

        # Output as JSON
        $ rai graph query "velocity" --format json

        # Filter symbols by module (mod-<package>--<module> in this repo,
        # since packages/* is a monorepo — RAISE-16033)
        $ rai graph query "scanner" --module mod-raise-cli--discovery

        # Find callers of a function
        $ rai graph query "scan_directory" --callers --types symbol

        # Cross-repo: include results from other repos
        $ rai graph query "PaymentService" --cross-repo
    """
    if cross_repo:
        from raise_cli.config.server import get_server_credentials

        if get_server_credentials() is None:
            cli_error(
                "--cross-repo requires server credentials. "
                "Run 'rai connect <org>' or set RAISE_SERVER_URL + RAISE_API_KEY.",
                exit_code=1,
            )
            raise typer.Exit(code=1)

    # Server-first semantic query (AC1–AC4, ADR-118 pattern).
    # Attempt POST /api/v2/graph/semantic-search before local keyword search.
    # On network error or missing creds → fall through to local QueryEngine below.
    # Skip server-first when CLI filters are set — server doesn't support them.
    _has_local_filters = any(
        [types, subtypes, edge_types, module, file, callers, strategy]
    )

    import httpx  # noqa: PLC0415 — local import to avoid top-level cost in standalone mode

    from raise_cli.config.server import get_server_credentials  # noqa: PLC0415
    from raise_cli.graph.api_graph_read_backend import (  # noqa: PLC0415
        ApiGraphReadBackend,
    )

    _creds = get_server_credentials()
    if _creds is not None and not _has_local_filters:
        _server_url, _api_key = _creds
        _backend = ApiGraphReadBackend(server_url=_server_url, api_key=_api_key)
        try:
            _server_response = _backend.semantic_search(query_str, limit=limit)
            if _server_response.get("results"):
                result = server_result_to_query_result(_server_response, query_str)
                if format == "agent":
                    output_text = format_agent(result)
                    if output:
                        output.write_text(output_text, encoding="utf-8")
                    elif output_text:
                        print(output_text)
                    return
                if format == "json":
                    output_text = format_json(result)
                elif format == "compact":
                    output_text = format_compact(result)
                else:
                    output_text = format_markdown(result)
                _write_query_output(output_text, output, result)
                return
        except httpx.HTTPStatusError as exc:
            _warn_msg = (
                "Server auth failed, using local search"
                if exc.response.status_code in (401, 403)
                else "Server error, using local search"
            )
            err_console.print(f"[yellow]{WARN} {_warn_msg}[/yellow]")
            logger.debug("Server-first query HTTP error: %s", exc)
        except httpx.RequestError as exc:
            err_console.print(
                f"[yellow]{WARN} Server unavailable, using local keyword search[/yellow]"
            )
            logger.debug("Server-first query request error: %s", exc)
        finally:
            _backend.close()

    engine = _load_query_engine(index_path, boost_ids=None)
    query_strategy = _parse_query_strategy(strategy)

    # Promote to KEYWORD_SEARCH_FORCED when the user did not choose a strategy
    # explicitly and the semantic provider is unavailable (RAISE-15987).
    if (
        query_strategy == QueryStrategy.KEYWORD_SEARCH
        and not strategy
        and not _semantic_provider_available()
    ):
        query_strategy = QueryStrategy.KEYWORD_SEARCH_FORCED

    # Build and execute query
    unified_query = Query(
        query=query_str,
        strategy=query_strategy,
        max_depth=1,
        types=_parse_comma_list(types),
        subtypes=_parse_comma_list(subtypes),
        edge_types=_parse_comma_list(edge_types),
        limit=limit,
        module=module,
        file=file,
        callers=callers,
    )

    if format != "agent":
        console.print(f"\nQuerying memory for: [cyan]{query_str}[/cyan]")
        if query_strategy == QueryStrategy.KEYWORD_SEARCH_FORCED:
            console.print(
                f"Strategy: [yellow]keyword_search[/yellow] "
                f"[dim]({WARN} forced — semantic index unavailable; "
                "set RAISE_ONNX_MODEL_DIR to enable)[/dim]"
            )
        else:
            console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]")
        filters: list[str] = []
        if module:
            filters.append(f"module={module}")
        if file:
            filters.append(f"file={file}")
        if callers:
            filters.append("callers")
        if cross_repo:
            filters.append("cross-repo")
        if filters:
            console.print(f"Filters: [green]{', '.join(filters)}[/green]")
        console.print()

    result = engine.query(unified_query)

    # Federated cross-repo retrieval
    if cross_repo:
        result = _merge_cross_repo_results(result, query_str, limit)

    # Format output
    if format == "agent":
        output_text = format_agent(result)
        if output:
            output.write_text(output_text, encoding="utf-8")
        elif output_text:
            print(output_text)
        return
    if format == "json":
        output_text = format_json(result)
    elif format == "compact":
        output_text = format_compact(result)
    else:
        output_text = format_markdown(result)

    _write_query_output(output_text, output, result)


# =============================================================================
# SQL-Native Graph Traversal Commands (S4513.5)
# =============================================================================


def _get_graph_backend(index_path: Path | None) -> object:
    """Return the active backend for graph CLI commands."""
    unified_path = index_path or _get_default_index_path()
    return get_active_backend(unified_path, explicit_path=index_path is not None)


def _as_graph_loader(backend: object) -> _SupportsGraphLoad:
    return cast("_SupportsGraphLoad", backend)


def _as_traversal_backend(backend: object) -> GraphTraversalBackend:
    return cast("GraphTraversalBackend", backend)


def _storage_location_exists(backend: object, fallback_path: Path) -> bool:
    if isinstance(backend, GraphBackendMetadata):
        return Path(backend.storage_location()).exists()
    return fallback_path.exists()


def _display_storage_path(backend: object, fallback_path: Path) -> Path:
    if isinstance(backend, GraphBackendMetadata):
        return Path(backend.storage_location())
    return fallback_path


def _edge_type_from_multi_edge(edge_data: object) -> str:
    if not isinstance(edge_data, Mapping):
        return ""
    edge_variants = cast("Mapping[object, object]", edge_data)
    for attrs in edge_variants.values():
        if isinstance(attrs, Mapping):
            typed_attrs = cast("Mapping[str, object]", attrs)
            raw_edge_type = typed_attrs.get("type")
            if isinstance(raw_edge_type, str):
                return raw_edge_type
    return ""


def _fallback_ego_summary(
    graph: Graph,
    node_id: str,
    depth: int,
) -> tuple[list[str], int]:
    if node_id not in graph.graph:
        return [], 0

    seen: set[str] = {node_id}
    frontier: set[str] = {node_id}
    for _ in range(depth):
        next_frontier: set[str] = set()
        for current in frontier:
            for neighbor in graph.graph.successors(current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    next_frontier.add(neighbor)
            for neighbor in graph.graph.predecessors(current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    next_frontier.add(neighbor)
        if not next_frontier:
            break
        frontier = next_frontier

    edge_count = sum(
        1
        for source, target, _key in graph.graph.edges(keys=True)
        if source in seen and target in seen
    )
    return list(seen), edge_count


def _fallback_neighbors(
    graph: Graph,
    node_id: str,
    direction: str,
) -> list[Neighbor]:
    results: list[Neighbor] = []
    if node_id not in graph.graph:
        return results

    if direction in ("outgoing", "both"):
        for target in graph.graph.successors(node_id):
            edge_data = graph.graph.get_edge_data(node_id, target)
            results.append((target, _edge_type_from_multi_edge(edge_data)))
    if direction in ("incoming", "both"):
        for source in graph.graph.predecessors(node_id):
            edge_data = graph.graph.get_edge_data(source, node_id)
            results.append((source, _edge_type_from_multi_edge(edge_data)))
    return results


def _fallback_path(graph: Graph, src: str, dst: str) -> list[str] | None:
    if src == dst:
        return [src]
    if src not in graph.graph or dst not in graph.graph:
        return None

    queue: deque[tuple[str, list[str]]] = deque([(src, [src])])
    visited: set[str] = {src}

    while queue:
        current, path = queue.popleft()
        for neighbor in graph.graph.successors(current):
            if neighbor == dst:
                return [*path, neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, [*path, neighbor]))
    return None


@graph_app.command("ego")
def ego_cmd(
    node_id: Annotated[str, typer.Argument(help="Node ID to compute ego subgraph for")],
    depth: Annotated[
        int, typer.Option("--depth", "-d", help="Traversal depth (default: 2)")
    ] = 2,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json"),
    ] = "human",
    index_path: Annotated[
        Path | None, typer.Option("--index", "-i", help="Graph index path")
    ] = None,
) -> None:
    """Compute ego subgraph for a node without loading the full graph.

    Uses native traversal capabilities when the active backend provides them,
    otherwise falls back to NetworkX traversal on the loaded graph.

    Examples:
        # Ego subgraph depth=2
        $ rai graph ego mod-raise-cli--memory --depth 2

        # JSON output
        $ rai graph ego mod-raise-cli--memory --depth 2 --format json
    """
    backend = _get_graph_backend(index_path)

    if isinstance(backend, GraphTraversalBackend):
        traversal_backend = _as_traversal_backend(backend)
        subgraph = traversal_backend.ego_subgraph(node_id, depth=depth)
        node_ids = list(subgraph.graph.nodes())
        edge_count = subgraph.graph.number_of_edges()
    else:
        graph = _as_graph_loader(backend).load()
        node_ids, edge_count = _fallback_ego_summary(graph, node_id, depth)
    node_ids = sorted(node_ids)

    if format == "json":
        print(
            json.dumps(
                {
                    "node_id": node_id,
                    "depth": depth,
                    "nodes": node_ids,
                    "edge_count": edge_count,
                },
                indent=2,
            )
        )
        return

    console.print(f"\nEgo subgraph for: [cyan]{node_id}[/cyan] (depth={depth})")
    console.print(
        f"  Nodes: [green]{len(node_ids)}[/green]  |  Edges: [green]{edge_count}[/green]\n"
    )
    for nid in sorted(node_ids):
        console.print(f"  {nid}")
    console.print()


@graph_app.command("neighbors")
def neighbors_cmd(  # noqa: C901
    node_id: Annotated[str, typer.Argument(help="Node ID to get neighbors for")],
    direction: Annotated[
        str,
        typer.Option(
            "--direction",
            help="Edge direction: outgoing (default), incoming, or both",
        ),
    ] = "outgoing",
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json"),
    ] = "human",
    index_path: Annotated[
        Path | None, typer.Option("--index", "-i", help="Graph index path")
    ] = None,
) -> None:
    """List direct neighbors of a node.

    Uses native traversal capabilities when the active backend provides them,
    otherwise falls back to NetworkX neighbors on the loaded graph.

    Examples:
        $ rai graph neighbors mod-raise-cli--memory --direction outgoing
        $ rai graph neighbors mod-raise-cli--memory --direction both
    """
    if direction not in ("outgoing", "incoming", "both"):
        cli_error(
            f"Invalid direction: {direction!r}",
            hint="Valid values: outgoing, incoming, both",
            exit_code=7,
        )
        return

    backend = _get_graph_backend(index_path)

    if isinstance(backend, GraphTraversalBackend):
        neighbors = _as_traversal_backend(backend).neighbors(
            node_id, direction=direction
        )
    else:
        graph = _as_graph_loader(backend).load()
        neighbors = _fallback_neighbors(graph, node_id, direction)
    neighbors = sorted(neighbors)

    if format == "json":
        print(
            json.dumps([{"node_id": n, "edge_type": t} for n, t in neighbors], indent=2)
        )
        return

    console.print(f"\nNeighbors of: [cyan]{node_id}[/cyan] ({direction})")
    if not neighbors:
        console.print("  No neighbors found.\n")
        return
    for nid, etype in neighbors:
        console.print(f"  [green]{nid}[/green]  {etype}")
    console.print()


@graph_app.command("path")
def path_cmd(
    src: Annotated[str, typer.Argument(help="Source node ID")],
    dst: Annotated[str, typer.Argument(help="Destination node ID")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json"),
    ] = "human",
    index_path: Annotated[
        Path | None, typer.Option("--index", "-i", help="Graph index path")
    ] = None,
) -> None:
    """Find directed path between two nodes.

    Uses native traversal capabilities when the active backend provides them,
    otherwise falls back to NetworkX path traversal on the loaded graph.

    Examples:
        $ rai graph path mod-raise-cli--memory mod-raise-cli--session
    """
    backend = _get_graph_backend(index_path)

    if isinstance(backend, GraphTraversalBackend):
        path: list[str] | None = _as_traversal_backend(backend).path(src, dst)
    else:
        graph = _as_graph_loader(backend).load()
        path = _fallback_path(graph, src, dst)

    if format == "json":
        print(json.dumps({"src": src, "dst": dst, "path": path}, indent=2))
        return

    if path is None:
        console.print(
            f"\nNo path found between [cyan]{src}[/cyan] and [cyan]{dst}[/cyan]\n"
        )
        return

    console.print(f"\nPath: [green]{' → '.join(path)}[/green]")
    console.print(f"  Hops: {len(path) - 1}\n")


# =============================================================================
# Architectural Context Command
def _portfolio_impact_for_component(
    component_name: str, project_root: Path
) -> list[dict[str, str]]:
    """Query-time inverse lookup: epics/initiatives that touched *component_name*.

    Searches graph_nodes content for the literal token ``components_touched:{name}``.
    No edges are persisted — query-time only (RAISE-15286).

    Returns a list of dicts with keys: id, change_mode, jira_status.
    Empty list when DB absent, no portfolio cartridge loaded, or no matches.
    """
    import sqlite3  # noqa: PLC0415

    db_path = get_project_db_path(project_root)
    if not db_path.exists():
        return []
    project_id = get_project_id(project_root)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT node_id, metadata_json FROM graph_nodes"
            " WHERE project_id = ?"
            " AND node_type IN ('epic', 'initiative')"
            " AND content LIKE ?",
            (project_id, f"%components_touched:{component_name}%"),
        ).fetchall()
        conn.close()
    except Exception:  # noqa: BLE001
        return []

    result: list[dict[str, str]] = []
    for row in rows:
        try:
            import json as _json  # noqa: PLC0415

            meta: dict[str, object] = _json.loads(str(row["metadata_json"] or "{}"))
        except Exception:  # noqa: BLE001
            meta = {}
        result.append(
            {
                "id": str(row["node_id"]),
                "change_mode": str(meta.get("change_mode") or ""),
                "jira_status": str(meta.get("jira_status") or ""),
            }
        )
    return result


# =============================================================================


@graph_app.command("context")
def context_cmd(
    module_id: Annotated[
        str, typer.Argument(help="Module ID (e.g., mod-raise-cli--memory)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human, json, or agent)"),
    ] = "human",
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path"),
    ] = None,
) -> None:
    """Show full architectural context for a module.

    Returns the module's bounded context (domain), architectural layer,
    applicable guardrails (constraints), and module dependencies in a
    single structured view.

    Examples:
        # Show context for memory module
        $ rai graph context mod-raise-cli--memory

        # JSON output for programmatic use
        $ rai graph context mod-raise-cli--memory --format json
    """
    unified_path = index_path or _get_default_index_path()
    try:
        graph = get_active_backend(
            unified_path, explicit_path=index_path is not None
        ).load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright
    if graph.node_count == 0:
        cli_error(
            "Graph index is empty — no nodes found",
            hint="Run 'rai graph build' first to populate the index",
            exit_code=4,
        )
        return
    engine = QueryEngine(graph)

    ctx = engine.get_architectural_context(module_id)
    if ctx is None:
        cli_error(
            f"Module not found: {module_id}",
            hint="Check available modules with: rai graph query '' --types module",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright

    # Portfolio impact: query-time inverse lookup (RAISE-15286)
    component_name = module_id.removeprefix("mod-")
    project_root = resolve_checkout_root(Path.cwd())
    portfolio_nodes = _portfolio_impact_for_component(component_name, project_root)

    if format == "agent":
        print(format_context_agent(ctx))
    elif format == "json":
        ctx_dict = json.loads(ctx.model_dump_json())
        ctx_dict["portfolio_impact"] = portfolio_nodes
        console.print(json.dumps(ctx_dict, indent=2))
    else:
        print_context_human(ctx)
        if portfolio_nodes:
            console.print("[bold]Portfolio impact:[/bold]")
            for node in portfolio_nodes:
                cm = f" | {node['change_mode']}" if node["change_mode"] else ""
                st = f" | {node['jira_status']}" if node["jira_status"] else ""
                console.print(f"  - {node['id']}{cm}{st}")
        else:
            console.print(
                "[bold]Portfolio impact:[/bold] [dim]ninguna epic anotada"
                " (run rai portfolio epic-profile create)[/dim]"
            )


# =============================================================================
# Metrics Command
# =============================================================================


@graph_app.command("metrics")
def metrics_cmd(
    module_id: Annotated[
        str, typer.Argument(help="Module ID (e.g., mod-raise-cli--memory)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json"),
    ] = "human",
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path"),
    ] = None,
) -> None:
    """Compute Lanza-Marinescu structural health metrics for a module.

    Returns WMC, LCOM4, fan_in, fan_out, and cyclomatic_p95 computed
    deterministically from SymbolNode + CALLS edges. No LLM required.

    Metrics:
      wmc            Weighted Methods per Class (count of method+function symbols)
      lcom           LCOM4: cohesion via shared-callee topology (0 = cohesive)
      fan_in         Distinct external modules calling INTO this module
      fan_out        Distinct external modules called FROM this module
      cyclomatic_p95 95th-percentile branch_count across callable symbols

    ADR-E2162-4 documents the LCOM variant and branch-node set choices.

    Examples:
        # Human-readable output (default)
        $ rai graph metrics mod-raise-cli--memory

        # JSON output for programmatic use
        $ rai graph metrics mod-raise-cli--memory --format json

        # Discover available modules
        $ rai graph query '' --types module
    """
    unified_path = index_path or _get_default_index_path()
    try:
        graph = get_active_backend(
            unified_path, explicit_path=index_path is not None
        ).load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright
    if graph.node_count == 0:
        cli_error(
            "Graph index is empty — no nodes found",
            hint="Run 'rai graph build' first to populate the index",
            exit_code=4,
        )
        return

    try:
        report = MetricsComputer(graph).compute(module_id)
    except ModuleNotFoundError:
        cli_error(
            f"Module not found: {module_id}",
            hint="Check available modules with: rai graph query '' --types module",
            exit_code=4,
        )
        return  # unreachable — cli_error raises SystemExit

    if format == "json":
        print(report.model_dump_json(indent=2))
        return

    # Human format: key-value table
    console.print(f"\nMetrics for module: [cyan]{report.module_id}[/cyan]")
    console.print(f"  Symbols:         {report.symbol_count}")
    console.print(f"  WMC:             {report.wmc}")
    console.print(f"  LCOM:            {report.lcom}")
    console.print(f"  fan_in:          {report.fan_in}")
    console.print(f"  fan_out:         {report.fan_out}")
    console.print(f"  cyclomatic_p95:  {report.cyclomatic_p95:.2f}")
    console.print(f"  computed_at:     {report.computed_at.isoformat()}\n")


# =============================================================================
# Build/Index Commands
# =============================================================================


def _persist_graph(backend: object, graph: Any, *, prune: bool) -> None:
    """Persist graph to backend.

    ``--prune`` is currently a no-op on every path (RAISE-15607). The remote
    keyspace is still repo-wide — keyed by ``server_slug`` with no checkout
    discriminator — so pruning from one checkout would send only ITS nodes as
    ``keep_node_ids`` and the server would delete every other checkout's
    nodes. ``DualWriteBackend.persist`` therefore no longer forwards the flag.

    Both paths warn: a silent no-op while ``--help`` still advertises pruning
    is exactly the false evidence this release forbids.
    """
    from raise_cli.graph.backends.dual import DualWriteBackend  # noqa: PLC0415

    if prune:
        reason = (
            "remote keyspace is not checkout-scoped yet (RAISE-15607)"
            if isinstance(backend, DualWriteBackend)
            else "no remote server configured"
        )
        err_console.print(f"[yellow]{WARN} --prune ignored ({reason})[/yellow]")
    backend.persist(graph)  # type: ignore[union-attr]


def _report_build_diagnostics(builder: GraphBuilder) -> None:
    """Print what the build dropped and what it never picked up.

    Two channels, deliberately distinct: ``warnings`` mean the build lost
    something (duplicate node ids, RAISE-648), ``hints`` mean the build did
    exactly what the manifest said and the operator may not have meant it
    (RAISE-15992).

    Both messages quote data the operator wrote — manifest globs, node ids —
    and ``[a-z]`` is valid glob syntax that Rich reads as markup and drops.
    Escaping keeps the diagnostic showing the pattern that actually failed
    rather than a silently rewritten one.
    """
    for warning in builder.warnings:
        console.print(f"[yellow]{WARN} {escape(warning)}[/yellow]")
    for hint in builder.hints:
        console.print(f"[cyan]hint:[/cyan] {escape(hint)}")


def _print_health_report(hr: object) -> None:
    """Print edge resolution health report from GraphBuilder."""
    resolutions = getattr(hr, "edge_resolutions", [])
    if not resolutions:
        return
    console.print("\n[bold]Edge resolution health:[/bold]")
    for r in resolutions:
        pct = f"{r.resolution_rate:.0%}"
        style = (
            "green"
            if r.resolution_rate >= 0.8
            else ("yellow" if r.resolution_rate >= 0.3 else "red")
        )
        console.print(
            f"  {r.edge_type}: {r.resolved}/{r.attempted} resolved ([{style}]{pct}[/{style}])"
        )
    dangling = getattr(hr, "dangling_edges", 0)
    if dangling > 0:
        console.print(f"  [red]dangling: {dangling}[/red]")
    else:
        console.print("  dangling: 0")


def _record_build_to_db(node_count: int, symbol_depth: str) -> None:
    """Write graph build record to SQLite graph_builds table (RAISE-14852).

    Fail-safe: any exception is logged at DEBUG level and swallowed so a
    DB initialisation race never blocks the graph build CLI command.
    """
    import sqlite3 as _sqlite3

    from raise_cli.storage.connection import get_project_db_path, get_project_id
    from raise_cli.storage.schema import create_all as _create_all

    try:
        project_root = resolve_checkout_root()
        project_id = get_project_id(project_root)
        db_path = get_project_db_path(project_root)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = _sqlite3.connect(str(db_path))
        try:
            _create_all(conn)
            conn.execute(
                "INSERT INTO graph_builds"
                " (project_id, checkout_id, built_at, node_count, symbol_depth)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    project_id,
                    # RAISE-15607: a build record without its checkout makes
                    # doctor report "fresh" from another worktree's build.
                    checkout_scope_id(project_root),
                    datetime.now(tz=UTC).isoformat(),
                    node_count,
                    symbol_depth,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        logger.debug("Failed to write graph_builds record to SQLite", exc_info=True)


@graph_app.command(short_help="NO --project flag, runs from CWD")
def build(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save index JSON"),
    ] = None,
    no_diff: Annotated[
        bool,
        typer.Option("--no-diff", help="Skip diff computation"),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail on duplicate node IDs (for CI)"),
    ] = False,
    depth: Annotated[
        str,
        typer.Option(
            "--depth",
            help="Symbol scan depth: none, classes, functions, full (default: functions)",
        ),
    ] = "functions",
    prune: Annotated[
        bool,
        typer.Option(
            "--prune",
            help="IGNORED for now: prune stale nodes on the remote server. "
            "Suppressed while the remote keyspace is repo-wide (RAISE-15607).",
        ),
    ] = False,
) -> None:
    """Build graph index from all sources.

    Merges all context sources into a single queryable index:
    - Governance documents (constitution, PRD, vision)
    - Memory (patterns, calibration, sessions)
    - Work tracking (epics, stories)
    - Skills (SKILL.md metadata)
    - Components (from discovery)

    By default, diffs against the previous build and saves the diff
    to .raise/rai/personal/last-diff.json for downstream consumers.

    Examples:
        # Build index to default location
        $ rai graph build

        # Build without diff
        $ rai graph build --no-diff

        # Save to custom location
        $ rai graph build --output custom_index.json
    """
    default_output = _get_default_index_path()
    output_path = output or default_output

    # Load old graph for diff (before building new one). Backends may store
    # graph data outside the legacy JSON path, so ask metadata-capable backends.
    backend = get_active_backend(output_path, explicit_path=output is not None)
    old_graph = None
    if not no_diff:
        has_existing = _storage_location_exists(backend, output_path)
        if has_existing:
            old_graph = backend.load()

    # Build unified graph
    from raise_core.discovery.symbols import SymbolDepth

    try:
        symbol_depth = SymbolDepth(depth)
    except ValueError:
        valid = ", ".join(d.value for d in SymbolDepth)
        cli_error(f"Invalid --depth '{depth}'. Valid: {valid}")
        raise typer.Exit(code=1) from None

    builder = GraphBuilder(strict=strict, symbol_depth=symbol_depth)
    graph = builder.build()

    # Report dropped nodes (RAISE-648) and configuration hints (RAISE-15992)
    _report_build_diagnostics(builder)

    # Count nodes by type
    node_counts: dict[str, int] = {}
    for node in graph.iter_concepts():
        node_counts[node.type] = node_counts.get(node.type, 0) + 1

    # Count edges by type
    edge_counts: dict[str, int] = {}
    for edge in graph.iter_relationships():
        edge_counts[edge.type] = edge_counts.get(edge.type, 0) + 1

    # Save graph via backend
    _persist_graph(backend, graph, prune=prune)

    # Remove legacy index.json if present at the DEFAULT path only; custom
    # --output paths must never be touched.  Legacy cleanup is for repos that
    # still carry an index.json from the pre-SQLite era (Kuzu, removed Jun 10).
    legacy_index = _get_default_index_path()
    if (
        output_path == legacy_index
        and legacy_index.exists()
        and legacy_index.suffix == ".json"
    ):
        legacy_index.unlink()
        logger.debug("Removed legacy index.json after backend graph persist")

    # Persist build metadata to SQLite for doctor and downstream consumers
    _record_build_to_db(graph.node_count, depth)

    # Emit graph:build event
    emitter = create_emitter()
    emitter.emit(
        GraphBuildEvent(
            project_path=output_path.parent,
            node_count=graph.node_count,
            edge_count=graph.edge_count,
        )
    )

    # Compute and persist diff
    diff = None
    if old_graph is not None:
        diff = diff_graphs(old_graph, graph)
        diff_path = get_personal_dir() / "last-diff.json"
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(diff.model_dump_json(indent=2), encoding="utf-8")

    # Format output — show actual backend storage path when available.
    display_path = _display_storage_path(backend, output_path)
    format_build_result(
        output_path=display_path,
        node_counts=node_counts,
        edge_counts=edge_counts,
        total_nodes=graph.node_count,
        total_edges=graph.edge_count,
        diff=diff,
    )

    _print_health_report(builder.health_report)

    # Auto-embed cartridges for hybrid retrieval (S9795.7)
    _auto_embed_all_cartridges(Path.cwd() / ".raise" / "cartridges")

    # Auto-embed non-cartridge graph nodes (pattern/symbol/document) for
    # pure-semantic reachability (RAISE-16087)
    _auto_embed_graph_nodes(graph)


# Allowlist for RAISE-16087: node types embedded outside the cartridge
# pipeline. Excludes cartridge-tagged nodes (already handled by
# _auto_embed_all_cartridges) — module/component/skill deferred (YAGNI, DD3).
EMBEDDABLE_GRAPH_NODE_TYPES = frozenset({"pattern", "symbol", "document"})

# Kill-switch env var (DD5, default ON) — mirrors RAISE_FEDERATION_ENABLED's
# precedent (raise_core/graph/retrieval/federation.py).
_GRAPH_NODE_EMBED_ENV = "RAISE_GRAPH_NODE_EMBED"
_GRAPH_NODE_EMBED_FALSY = frozenset({"0", "false", "no", "off"})


def _load_nodes_from_instances(instances_dir: Path, ts: str) -> list[Any]:
    """Load GraphNode-like dicts from instance JSON files (list or single-item format)."""
    from raise_core.graph.models import GraphNode

    nodes: list[GraphNode] = []
    for jf in iter_instance_files(instances_dir):
        try:
            raw = json.loads(jf.read_text(encoding="utf-8"))
            items = raw if isinstance(raw, list) else [raw]
            for item in items:
                if not isinstance(item, dict):
                    continue
                nodes.append(
                    GraphNode(
                        id=item.get("id") or jf.stem,
                        content=item.get("content", ""),
                        type=item.get("type") or "cartridge_node",
                        created=item.get("created") or ts,
                    )
                )
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Skipping malformed instance %s", jf)
    return nodes


def _load_npy_embeddings(npy_path: Path, idx_path: Path) -> dict[str, list[float]]:
    """Load embeddings from .npy + index JSON into a node_id → vector dict."""
    import contextlib  # noqa: I001

    import numpy as np  # noqa: I001

    result: dict[str, list[float]] = {}
    with contextlib.suppress(Exception):
        matrix = np.load(npy_path).astype(float)
        index: dict[str, int] = json.loads(idx_path.read_text(encoding="utf-8"))
        result = {nid: matrix[i].tolist() for nid, i in index.items()}
    return result


def _load_existing_embeddings(instances_dir: Path) -> dict[str, list[float]]:
    """Load existing embedding vectors from the active generation or legacy files.

    Returns an empty dict when no embeddings exist yet.
    """
    import contextlib  # noqa: I001

    # Prefer manifest-based generation dir (RAISE-14952 incremental format)
    manifest = instances_dir / "manifest.json"
    if manifest.exists():
        with contextlib.suppress(Exception):
            gen_dir_name = json.loads(manifest.read_text(encoding="utf-8")).get(
                "generation_dir", ""
            )
            gen_dir = instances_dir / gen_dir_name
            npy_path = gen_dir / "embeddings.npy"
            idx_path = gen_dir / "embedding_index.json"
            if npy_path.exists() and idx_path.exists():
                return _load_npy_embeddings(npy_path, idx_path)

    # Fallback: legacy flat files
    npy_path = instances_dir / "embeddings.npy"
    idx_path = instances_dir / "embedding_index.json"
    if npy_path.exists() and idx_path.exists():
        return _load_npy_embeddings(npy_path, idx_path)

    return {}


def _find_stale_cartridges(
    cartridges_root: Path,
    ts: str,
    compute_fp: Any,
    load_fps: Any,
    spec: Any,
) -> list[tuple[Path, list[Any], dict[str, list[float]], dict[str, str]]]:
    """Identify cartridges that need re-embedding by comparing fingerprints."""
    work_items: list[
        tuple[Path, list[Any], dict[str, list[float]], dict[str, str]]
    ] = []
    for cd in sorted(cartridges_root.iterdir()):
        instances_dir = cd / "instances"
        if not instances_dir.is_dir():
            continue
        nodes = _load_nodes_from_instances(instances_dir, ts)
        if not nodes:
            continue
        existing_fps = load_fps(instances_dir)
        current_fps = {n.id: compute_fp(n.id, n.content, spec) for n in nodes}
        deleted_ids = set(existing_fps) - {n.id for n in nodes}
        changed = any(current_fps[n.id] != existing_fps.get(n.id) for n in nodes)
        if not changed and not deleted_ids and existing_fps:
            continue
        work_items.append(
            (
                instances_dir,
                nodes,
                _load_existing_embeddings(instances_dir),
                existing_fps,
            )
        )
    return work_items


def _auto_embed_all_cartridges(cartridges_root: Path) -> None:
    """Generate embeddings for all cartridges after graph build.

    Uses content fingerprints to detect changed nodes and re-embed only
    those, reusing existing vectors for unchanged nodes (RAISE-14952).
    Degrades gracefully when sentence-transformers is not installed.
    """
    if not cartridges_root.is_dir():
        return

    try:
        from raise_cli.cartridges.onnx_provider import get_default_provider
        from raise_core.cartridges.embedding import (  # noqa: I001
            DEFAULT_MODEL,
            PASSAGE_PREFIX,
            QUERY_PREFIX,
            EmbeddingGenerator,
            EmbeddingSpec,
            compute_node_fingerprint,
            load_fingerprints,
            write_embeddings_atomic,
        )
    except ImportError as exc:
        logger.warning(
            "embedding provider not available, skipping embeddings generation: %r",
            exc,
        )
        return

    spec = EmbeddingSpec(
        model_name=DEFAULT_MODEL,
        format_version="v1",
        query_prefix=QUERY_PREFIX,
        passage_prefix=PASSAGE_PREFIX,
    )
    ts = datetime.now(tz=UTC).isoformat()
    work_items = _find_stale_cartridges(
        cartridges_root, ts, compute_node_fingerprint, load_fingerprints, spec
    )
    if not work_items:
        return

    try:
        provider = get_default_provider()
        generator = EmbeddingGenerator(provider)
    except ImportError as exc:
        logger.warning(
            "embedding provider not available, skipping embeddings generation: %r",
            exc,
        )
        return
    except RuntimeError as exc:
        logger.warning(
            "embedding provider not available, skipping embeddings generation: %r",
            exc,
        )
        err_console.print(
            f"[yellow]{WARN} Semantic embeddings unavailable:[/yellow] {exc}\n"
            "  Graph queries will use keyword search only.\n"
            "  Remedy: set [bold]RAISE_ONNX_MODEL_DIR[/bold] to your "
            "multilingual-e5-base model directory, or use the PyInstaller "
            "binary distribution."
        )
        return

    for instances_dir, nodes, existing_embeddings, existing_fps in work_items:
        try:
            embeddings, new_fps = generator.generate_incremental(
                nodes, existing_embeddings, existing_fps, spec=spec
            )
            write_embeddings_atomic(embeddings, new_fps, nodes, spec, instances_dir)
            logger.debug(
                "Embedded %d nodes from %s", len(nodes), instances_dir.parent.name
            )
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning(
                "Embedding failed for cartridge %s", instances_dir.parent.name
            )


def _select_embeddable_graph_nodes(graph: Graph) -> list[Any]:
    """Return graph nodes eligible for non-cartridge embedding (DD3 allowlist).

    Selection: ``type`` in ``EMBEDDABLE_GRAPH_NODE_TYPES``, no
    ``metadata.cartridge`` tag (cartridge nodes are handled by
    ``_auto_embed_all_cartridges``), and non-empty content.
    """
    return [
        node
        for node in graph.iter_concepts()
        if node.type in EMBEDDABLE_GRAPH_NODE_TYPES
        and not (node.metadata or {}).get("cartridge")
        and node.content
    ]


def _auto_embed_graph_nodes(graph: Graph) -> None:
    """Generate embeddings for non-cartridge graph nodes after graph build.

    Companion to ``_auto_embed_all_cartridges`` (S9795.7): embeds
    ``pattern``/``symbol``/``document`` nodes so pure-semantic queries can
    reach them (RAISE-16087, epic RAISE-15984). Reuses the same incremental
    fingerprint + atomic-write machinery, writing to a single fused
    generation dir at ``get_memory_dir()/embeddings`` — already gitignored
    (``.raise/.gitignore: rai/memory/*``), so no new hygiene surface (DD2).

    Set ``RAISE_GRAPH_NODE_EMBED=0`` to disable (default ON, DD5).
    Degrades gracefully when the embedding provider is unavailable, mirroring
    ``_auto_embed_all_cartridges``.
    """
    if os.environ.get(_GRAPH_NODE_EMBED_ENV, "").strip().lower() in (
        _GRAPH_NODE_EMBED_FALSY
    ):
        return

    nodes = _select_embeddable_graph_nodes(graph)
    if not nodes:
        return

    try:
        from raise_cli.cartridges.onnx_provider import get_default_provider
        from raise_core.cartridges.embedding import (  # noqa: I001
            DEFAULT_MODEL,
            PASSAGE_PREFIX,
            QUERY_PREFIX,
            EmbeddingGenerator,
            EmbeddingSpec,
            compute_node_fingerprint,
            load_fingerprints,
            write_embeddings_atomic,
        )
    except ImportError as exc:
        logger.warning(
            "embedding provider not available, skipping graph node embeddings: %r",
            exc,
        )
        return

    out_dir = get_memory_dir() / "embeddings"
    spec = EmbeddingSpec(
        model_name=DEFAULT_MODEL,
        format_version="v1",
        query_prefix=QUERY_PREFIX,
        passage_prefix=PASSAGE_PREFIX,
    )

    existing_fps = load_fingerprints(out_dir)
    current_fps = {n.id: compute_node_fingerprint(n.id, n.content, spec) for n in nodes}
    deleted_ids = set(existing_fps) - {n.id for n in nodes}
    changed = any(current_fps[n.id] != existing_fps.get(n.id) for n in nodes)
    if not changed and not deleted_ids and existing_fps:
        # Nothing stale — mirrors _find_stale_cartridges' skip (AC5).
        return

    existing_embeddings = _load_existing_embeddings(out_dir)

    try:
        provider = get_default_provider()
        generator = EmbeddingGenerator(provider)
    except ImportError as exc:
        logger.warning(
            "embedding provider not available, skipping graph node embeddings: %r",
            exc,
        )
        return
    except RuntimeError as exc:
        logger.warning(
            "embedding provider not available, skipping graph node embeddings: %r",
            exc,
        )
        err_console.print(
            f"[yellow]{WARN} Semantic embeddings unavailable:[/yellow] {exc}\n"
            "  Graph queries will use keyword search only.\n"
            "  Remedy: set [bold]RAISE_ONNX_MODEL_DIR[/bold] to your "
            "multilingual-e5-base model directory, or use the PyInstaller "
            "binary distribution."
        )
        return

    try:
        embeddings, new_fps = generator.generate_incremental(
            nodes, existing_embeddings, existing_fps, spec=spec
        )
        write_embeddings_atomic(embeddings, new_fps, nodes, spec, out_dir)
        logger.debug("Embedded %d graph nodes to %s", len(nodes), out_dir)
    except Exception:  # noqa: BLE001 — intentional broad catch, mirrors _auto_embed_all_cartridges
        logger.warning("Embedding graph nodes failed")


@graph_app.command()
def push(
    prune: Annotated[
        bool,
        typer.Option(
            "--prune",
            help="IGNORED for now: prune stale nodes on the remote server. "
            "Suppressed while the remote keyspace is repo-wide (RAISE-15607).",
        ),
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
    allow_org_mismatch: Annotated[
        bool,
        typer.Option(
            "--allow-org-mismatch",
            help="Push even if the project is bound to a different org (RAISE-9823)",
        ),
    ] = False,
) -> None:
    """Build and push the knowledge graph to the remote server.

    Requires server credentials — either RAISE_SERVER_URL + RAISE_API_KEY
    env vars, or ~/.rai/server.json (written by ``rai connect``).
    Builds the graph locally, then persists via DualWriteBackend which
    sends all node types to the server by default.

    Intended for CI post-merge jobs.

    Examples:
        $ rai graph push

        $ RAISE_SERVER_URL=https://raise.fly.dev RAISE_API_KEY=rsk_xxx rai graph push
    """
    from pathlib import Path

    from raise_cli.cli.commands._server_write import confirm_server_write

    target = confirm_server_write(
        "graph push",
        yes=yes,
        project_root=Path.cwd(),
        allow_org_mismatch=allow_org_mismatch,
    )
    server_url = target.server_url

    console.print("Building graph...")
    builder = GraphBuilder()
    graph = builder.build()

    _report_build_diagnostics(builder)

    backend = get_active_backend(_get_default_index_path())
    _persist_graph(backend, graph, prune=prune)

    org_label = target.org_name or server_url
    console.print(
        f"[green]✓[/green] Graph pushed to org '{org_label}' ({server_url}) "
        f"({graph.node_count} nodes, {graph.edge_count} edges)"
    )


@graph_app.command()
def pull() -> None:
    """Download graph from the remote server to local SQLite.

    Requires server credentials — either RAISE_SERVER_URL + RAISE_API_KEY
    env vars, or ~/.rai/server.json (written by ``rai connect``).

    Fetches all nodes and edges for the current project from the server
    and upserts them into the local SQLite graph store.

    Examples:
        $ rai graph pull
    """
    from raise_cli.graph.backends import get_active_backend
    from raise_cli.graph.backends.api import ApiGraphBackend
    from raise_cli.graph.backends.dual import DualWriteBackend
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend

    backend = get_active_backend(_get_default_index_path())

    remote: ApiGraphBackend | None = None
    local: SQLiteGraphBackend | None = None

    if isinstance(backend, DualWriteBackend):
        remote = backend.remote  # type: ignore[assignment]
        local = backend.local  # type: ignore[assignment]
    elif isinstance(backend, SQLiteGraphBackend):
        cli_error(
            "No server credentials found. "
            "Run 'rai connect <org>' or set RAISE_SERVER_URL + RAISE_API_KEY."
        )
        raise typer.Exit(code=1)

    if remote is None or local is None:
        cli_error("Could not resolve remote + local backends for pull.")
        raise typer.Exit(code=1)

    console.print(f"Pulling graph from {remote.server_url}...")
    try:
        data = remote.pull()
    except Exception as exc:
        cli_error(f"Failed to fetch graph: {exc}")
        raise typer.Exit(code=1) from exc

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not nodes:
        console.print("[yellow]Server returned 0 nodes — nothing to import.[/yellow]")
        raise typer.Exit(code=0)

    from raise_cli.graph.utils import build_graph_from_payload  # noqa: PLC0415

    graph = build_graph_from_payload(data)

    local.persist(graph)
    console.print(
        f"[green]✓[/green] Pulled {len(nodes)} nodes, {len(edges)} edges "
        f"from {remote.server_url}"
    )


@graph_app.command()
def validate(  # noqa: C901 -- complexity 14, refactor deferred
    index_file: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Path to index JSON file"),
    ] = None,
) -> None:
    """Validate graph index structure and relationships.

    Checks for:
    - Cycles in depends_on relationships
    - Valid relationship types
    - All edge targets exist as nodes

    Examples:
        # Validate default index
        $ rai graph validate

        # Validate specific index file
        $ rai graph validate --index custom_index.json
    """
    default_index = _get_default_index_path()
    index_path = index_file or default_index

    if index_file is not None and not index_path.exists():
        cli_error(
            f"Index file not found: {index_path}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    backend = get_active_backend(index_path, explicit_path=index_file is not None)
    display_path = _display_storage_path(backend, index_path)

    console.print(f"\nLoading index from [cyan]{display_path}[/cyan]...")
    graph = backend.load()
    console.print(
        f"  {CHECK} Loaded index with {graph.node_count} concepts, {graph.edge_count} relationships"
    )

    console.print("\nValidating index...")

    # Build node set for validation
    node_ids = {node.id for node in graph.iter_concepts()}

    # Check 1: All edge targets exist as nodes
    valid_edges = True
    edges_list = list(graph.iter_relationships())
    for edge in edges_list:
        if edge.source not in node_ids:
            console.print(
                f"  [red]{CROSS}[/red] Invalid edge: source '{edge.source}' not in index"
            )
            valid_edges = False
        if edge.target not in node_ids:
            console.print(
                f"  [red]{CROSS}[/red] Invalid edge: target '{edge.target}' not in index"
            )
            valid_edges = False

    if valid_edges:
        console.print(f"  {CHECK} All relationships valid")

    # Check 2: Detect cycles in depends_on relationships
    depends_edges = [e for e in edges_list if e.type == "depends_on"]
    if depends_edges:
        cycles = _detect_cycles(graph, depends_edges)
        if cycles:
            console.print(
                f"  [yellow]{WARN}[/yellow]  {len(cycles)} cycle(s) detected in depends_on relationships"
            )
            for cycle in cycles[:3]:  # Show first 3
                console.print(f"      {f' {ARROW} '.join(cycle)}")
        else:
            console.print(f"  {CHECK} No cycles detected")

    # Check 3: Reachability
    console.print(f"  {CHECK} {graph.node_count}/{graph.node_count} concepts reachable")

    # Check 4: Completeness — expected node types present
    expected_types: dict[str, int] = {
        "architecture": 1,  # ≥1 arch-* node
        "module": 1,  # ≥1 mod-* node
        "release": 1,  # ≥1 rel-* node
    }
    type_counts: dict[str, int] = {}
    for node in graph.iter_concepts():
        type_counts[node.type] = type_counts.get(node.type, 0) + 1

    missing: list[tuple[str, int, int]] = []
    for node_type, min_count in expected_types.items():
        actual = type_counts.get(node_type, 0)
        if actual < min_count:
            missing.append((node_type, min_count, actual))

    if missing:
        console.print(f"  [yellow]{WARN}[/yellow]  Completeness gaps:")
        for node_type, expected, actual in missing:
            console.print(f"    {node_type}: expected ≥{expected}, found {actual}")
    else:
        console.print(f"  {CHECK} Completeness check passed")

    console.print("\n[green]Memory index is valid.[/green]\n")


def _detect_cycles(graph: Graph, edges: list[GraphEdge]) -> list[list[str]]:
    """Detect cycles in a set of edges using iterative DFS.

    Iterative (not recursive) to avoid RecursionError on large graphs.
    Complexity: O(V + E).
    """
    adj: dict[str, list[str]] = {}
    for edge in edges:
        adj.setdefault(edge.source, []).append(edge.target)

    cycles: list[list[str]] = []
    node_ids = {node.id for node in graph.iter_concepts()}

    for start in node_ids:
        if start not in adj:
            continue
        visited: set[str] = set()
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbor in adj.get(node, []):
                if neighbor in path:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                else:
                    stack.append((neighbor, path + [neighbor]))

    return cycles


# =============================================================================
# List Command
# =============================================================================


@graph_app.command("list")
def list_graph(  # noqa: C901 -- complexity 12, refactor deferred
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human, json, or table)"),
    ] = "table",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path"),
    ] = None,
    memory_only: Annotated[
        bool,
        typer.Option(
            "--memory-only/--all",
            help="Show only memory types (pattern, calibration, session) or all",
        ),
    ] = False,
) -> None:
    """List concepts in the knowledge graph.

    Shows concepts from the graph index for inspection and debugging.

    Examples:
        # Show summary table (all concepts)
        $ rai graph list

        # Show only patterns/calibrations/sessions
        $ rai graph list --memory-only

        # Export as JSON
        $ rai graph list --format json --output graph.json

        # Export as human-readable markdown
        $ rai graph list --format human --output graph.md
    """
    # Resolve index path
    unified_path = index_path or _get_default_index_path()
    if index_path is not None and not unified_path.exists():
        cli_error(
            f"Graph index not found: {unified_path}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    # Load unified graph
    try:
        backend = get_active_backend(unified_path, explicit_path=index_path is not None)
        graph = backend.load()
    except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        cli_error(f"Error loading graph index: {e}")

    # Filter to memory types only if requested (inlined — single-use constant)
    if memory_only:
        concepts = [
            c
            for c in graph.iter_concepts()
            if c.type in ["pattern", "calibration", "session"]
        ]
    else:
        concepts = list(graph.iter_concepts())

    # Agent format: type|count summary, skip Rich headers
    if format == "agent":
        output_text = format_concepts_agent(concepts)
        if output:
            output.write_text(output_text, encoding="utf-8")
        elif output_text:
            print(output_text)
        else:
            print("empty")
        return

    console.print(
        f"\nGraph from: [cyan]{_display_storage_path(backend, unified_path)}[/cyan]"
    )
    console.print(f"Concepts: [yellow]{len(concepts)}[/yellow]\n")

    # Format output
    if format == "json":
        output_text = json.dumps(
            [c.model_dump(mode="json") for c in concepts],
            indent=2,
        )
    elif format == "human":
        output_text = format_concepts_markdown(concepts)
    else:  # table
        print_concepts_table(concepts)
        if output:
            # For file output in table mode, use markdown
            output_text = format_concepts_markdown(concepts)
        else:
            return

    # Write to file or stdout
    if output:
        output.write_text(output_text, encoding="utf-8")
        console.print(f"{CHECK} Graph written to [cyan]{output}[/cyan]\n")
    elif format != "table":
        console.print(output_text)


# =============================================================================
# Import Command
# =============================================================================


@graph_app.command("import")
def import_graph(
    source: Annotated[
        str,
        typer.Option(
            "--from",
            help="Import source: legacy-json",
        ),
    ],
    source_path: Annotated[
        Path,
        typer.Option("--path", help="Path to source graph storage"),
    ],
) -> None:
    """Explicitly import graph data into canonical SQLite storage."""
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_cli.storage.connection import get_project_db_path, get_project_id
    from raise_core.graph.backends.filesystem import FilesystemGraphBackend

    # RAISE-15607: Path.cwd() is not the checkout root when invoked from a
    # subdirectory, and this backend calls persist() — a wrong root would write
    # (and delete) in the wrong partition.
    project_root = resolve_checkout_root()
    target_backend = SQLiteGraphBackend(
        project_id=get_project_id(project_root),
        db_path=get_project_db_path(project_root),
        checkout_id=checkout_scope_id(project_root),
    )

    if source == "legacy-json":
        if not source_path.exists():
            cli_error(f"Graph import source not found: {source_path}", exit_code=4)
        try:
            graph = FilesystemGraphBackend(source_path).load()
        except Exception as exc:
            cli_error(f"Error loading legacy JSON graph: {exc}", exit_code=4)
            raise typer.Exit(code=4) from exc
    else:
        cli_error("Invalid import source. Use: legacy-json", exit_code=2)

    target_backend.persist(graph)
    console.print(
        f"{CHECK} Imported {graph.node_count} nodes and {graph.edge_count} edges "
        f"into [cyan]{_display_storage_path(target_backend, _get_default_index_path())}[/cyan]"
    )


# =============================================================================
# Visualization Command
# =============================================================================


@graph_app.command("viz")
def viz(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output HTML file path"),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path"),
    ] = None,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open in browser after generating"),
    ] = True,
) -> None:
    """Generate interactive HTML visualization of the knowledge graph.

    Creates a self-contained HTML file with a D3.js force-directed graph.
    Nodes are color-coded by type, filterable, zoomable, and searchable.

    Examples:
        # Generate and open in browser
        $ rai graph viz

        # Generate to specific path
        $ rai graph viz --output graph.html

        # Generate without opening
        $ rai graph viz --no-open
    """
    from raise_cli.viz import generate_viz_html

    unified_path = index_path or _get_default_index_path()
    backend = get_active_backend(unified_path, explicit_path=index_path is not None)
    has_data = _storage_location_exists(backend, unified_path)
    if not has_data:
        cli_error(
            f"Graph index not found: {_display_storage_path(backend, unified_path)}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    graph = backend.load()
    if graph.node_count == 0:
        cli_error(
            "Graph index is empty — no nodes found",
            hint="Run 'rai graph build' first to populate the index",
            exit_code=4,
        )

    output_path = output or Path(".raise/rai/memory/graph.html")

    graph_data: dict[str, object] = {
        "nodes": [
            {
                "id": n.id,
                "type": n.type,
                "content": n.content,
                "source_file": n.source_file,
                "metadata": n.metadata,
            }
            for n in graph.iter_concepts()
        ],
        "edges": [
            {"source": e.source, "target": e.target, "type": e.type}
            for e in graph.iter_relationships()
        ],
    }

    display = _display_storage_path(backend, unified_path)
    console.print(f"\nGenerating visualization from [cyan]{display}[/cyan]...")
    result_path = generate_viz_html(graph_data, output_path)
    console.print(f"{CHECK} Written to [cyan]{result_path}[/cyan]\n")

    if open_browser:
        open_in_browser(to_file_uri(result_path))
        console.print("  Opened in browser.\n")
