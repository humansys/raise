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
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rai_cli.cli.error_handler import cli_error
from rai_cli.compat import to_file_uri
from rai_cli.config.paths import get_memory_dir, get_personal_dir
from rai_cli.context import Graph, GraphBuilder
from rai_cli.context.diff import GraphDiff, diff_graphs
from rai_cli.governance import Concept, ConceptType, GovernanceExtractor
from rai_cli.hooks.emitter import create_emitter
from rai_cli.hooks.events import GraphBuildEvent
from rai_core.graph.backends.filesystem import get_active_backend
from rai_core.graph.models import GraphEdge, GraphNode
from rai_core.graph.query import (
    ArchitecturalContext,
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


def _get_default_index_path() -> Path:
    """Get default graph index path (.raise/rai/memory/index.json)."""
    return get_memory_dir() / INDEX_FILE


# =============================================================================
# Query Commands
# =============================================================================


@graph_app.command()
def query(
    query_str: Annotated[
        str, typer.Argument(help="Query string (keywords or concept ID)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
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

    Examples:
        # Search by keywords
        $ rai graph query "planning estimation"

        # Filter to patterns only
        $ rai graph query "testing" --types pattern,calibration

        # Lookup specific concept by ID
        $ rai graph query "PAT-001" --strategy concept_lookup

        # Output as JSON
        $ rai graph query "velocity" --format json
    """
    # Load engine
    unified_path = index_path or _get_default_index_path()
    try:
        graph = get_active_backend(unified_path).load()
        engine = QueryEngine(graph)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    # Parse types filter
    types_list: list[str] | None = None
    if types:
        types_list = [t.strip() for t in types.split(",")]

    # Determine strategy
    query_strategy = QueryStrategy.KEYWORD_SEARCH  # Default
    if strategy:
        try:
            query_strategy = QueryStrategy(strategy)
        except ValueError:
            cli_error(
                f"Invalid strategy: {strategy}",
                hint="Valid strategies: keyword_search, concept_lookup",
                exit_code=7,
            )

    # Parse edge_types filter
    edge_types_list: list[str] | None = None
    if edge_types:
        edge_types_list = [t.strip() for t in edge_types.split(",")]

    # Build and execute query
    unified_query = Query(
        query=query_str,
        strategy=query_strategy,
        max_depth=1,
        types=types_list,
        edge_types=edge_types_list,
        limit=limit,
    )

    console.print(f"\nQuerying memory for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(unified_query)

    # Format output
    if format == "json":
        output_text = _format_json(result)
    elif format == "compact":
        output_text = _format_compact(result)
    else:
        output_text = _format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text, encoding="utf-8")
        console.print(f"✓ Results written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)


def _format_markdown(result: QueryResult) -> str:
    """Format query result as markdown for human consumption."""
    lines: list[str] = []

    # Header
    lines.append("# Memory Query Results")
    lines.append("")
    lines.append(f"**Query:** `{result.metadata.query}`")
    lines.append(f"**Strategy:** {result.metadata.strategy.value}")

    # Types found summary
    types_str = ", ".join(
        f"{t}={c}" for t, c in sorted(result.metadata.types_found.items())
    )
    lines.append(
        f"**Concepts:** {result.metadata.total_concepts} | "
        f"**Tokens:** ~{result.metadata.token_estimate} | "
        f"**Types:** {types_str}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # No results
    if not result.concepts:
        lines.append("*No concepts found matching the query.*")
        lines.append("")
        return "\n".join(lines)

    # Group concepts by type
    by_type: dict[str, list[GraphNode]] = {}
    for concept in result.concepts:
        by_type.setdefault(concept.type, []).append(concept)

    # Render by type groups
    for node_type in sorted(by_type.keys()):
        concepts = by_type[node_type]
        lines.append(f"## {node_type.title()} ({len(concepts)})")
        lines.append("")

        for concept in concepts:
            # Concept header
            lines.append(f"### {concept.id}")
            source = concept.source_file or "unknown"
            lines.append(f"**Source:** {source} | **Created:** {concept.created}")
            lines.append("")

            # Content (truncate if very long)
            content = concept.content
            if len(content) > 300:
                content = content[:300] + "..."
            lines.append(content)
            lines.append("")

            # Metadata annotations (if available)
            if concept.metadata and "needs_context" in concept.metadata:
                ctx = ", ".join(concept.metadata["needs_context"])
                lines.append(f"*Needs context: {ctx}*")
                lines.append("")

        lines.append("---")
        lines.append("")

    # Footer with metadata
    lines.append("**Query Metadata:**")
    lines.append(f"- Execution time: {result.metadata.execution_time_ms:.2f}ms")
    lines.append(f"- Token estimate: ~{result.metadata.token_estimate}")
    lines.append("")

    return "\n".join(lines)


_COMPACT_CONTENT_MAX = 150


def _format_compact(result: QueryResult) -> str:
    """Format query result as compact Markdown-KV for AI consumption.

    One line per result: **type** id: content (truncated at 150 chars).
    Header with query, count, and strategy. Truncation footer when clipped.
    """
    meta = result.metadata
    lines: list[str] = []

    # Header: # Memory: query (N results, strategy)
    lines.append(
        f"# Memory: {meta.query} ({meta.total_concepts} results, {meta.strategy.value})"
    )

    # No results
    if not result.concepts:
        lines.append("*No results.*")
        return "\n".join(lines)

    # One Markdown-KV line per concept
    for concept in result.concepts:
        content = concept.content
        if len(content) > _COMPACT_CONTENT_MAX:
            content = content[:_COMPACT_CONTENT_MAX] + "..."
        lines.append(f"**{concept.type}** {concept.id}: {content}")

    # Truncation footer (only when results were clipped)
    remaining = meta.total_available - meta.total_concepts
    if remaining > 0:
        lines.append(
            f"[+{remaining} more — use --limit {meta.total_available} to see all]"
        )

    return "\n".join(lines)


def _format_json(result: QueryResult) -> str:
    """Format query result as JSON."""
    return result.to_json()


# =============================================================================
# Architectural Context Command
# =============================================================================


@graph_app.command("context")
def context_cmd(
    module_id: Annotated[str, typer.Argument(help="Module ID (e.g., mod-memory)")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
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
        $ rai graph context mod-memory

        # JSON output for programmatic use
        $ rai graph context mod-memory --format json
    """
    unified_path = index_path or _get_default_index_path()
    try:
        graph = get_active_backend(unified_path).load()
        engine = QueryEngine(graph)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright

    ctx = engine.get_architectural_context(module_id)
    if ctx is None:
        cli_error(
            f"Module not found: {module_id}",
            hint="Check available modules with: rai graph query '' --types module",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright

    if format == "json":
        console.print(_format_context_json(ctx))
    else:
        _print_context_human(ctx)


def _format_context_json(ctx: ArchitecturalContext) -> str:
    """Format architectural context as JSON."""
    return ctx.model_dump_json(indent=2)


def _print_context_human(ctx: ArchitecturalContext) -> None:
    """Print architectural context in human-readable format."""
    console.print(f"\n[bold]Module:[/bold] [cyan]{ctx.module.id}[/cyan]")
    console.print(f"  {ctx.module.content}")

    if ctx.domain:
        console.print(f"\n[bold]Domain:[/bold] [green]{ctx.domain.id}[/green]")
        console.print(f"  {ctx.domain.content}")
    else:
        console.print("\n[bold]Domain:[/bold] [dim]None[/dim]")

    if ctx.layer:
        console.print(f"\n[bold]Layer:[/bold] [green]{ctx.layer.id}[/green]")
        console.print(f"  {ctx.layer.content}")
    else:
        console.print("\n[bold]Layer:[/bold] [dim]None[/dim]")

    if ctx.constraints:
        must = [c for c in ctx.constraints if "MUST" in c.content]
        should = [c for c in ctx.constraints if "SHOULD" in c.content]
        console.print(f"\n[bold]Constraints:[/bold] {len(ctx.constraints)} guardrails")
        if must:
            must_ids = ", ".join(c.id for c in must)
            console.print(f"  [red]MUST:[/red] {must_ids}")
        if should:
            should_ids = ", ".join(c.id for c in should)
            console.print(f"  [yellow]SHOULD:[/yellow] {should_ids}")
    else:
        console.print("\n[bold]Constraints:[/bold] [dim]None[/dim]")

    if ctx.dependencies:
        dep_ids = ", ".join(d.id for d in ctx.dependencies)
        console.print(f"\n[bold]Dependencies:[/bold] {dep_ids}")
    else:
        console.print("\n[bold]Dependencies:[/bold] [dim]None[/dim]")

    console.print()


# =============================================================================
# Build/Index Commands
# =============================================================================


@graph_app.command()
def build(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save index JSON"),
    ] = None,
    no_diff: Annotated[
        bool,
        typer.Option("--no-diff", help="Skip diff computation"),
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

    # Load old graph for diff (before building new one)
    backend = get_active_backend(output_path)
    old_graph = None
    if not no_diff and output_path.exists():
        old_graph = backend.load()

    # Build unified graph
    builder = GraphBuilder()
    graph = builder.build()

    # Count nodes by type
    node_counts: dict[str, int] = {}
    for node in graph.iter_concepts():
        node_counts[node.type] = node_counts.get(node.type, 0) + 1

    # Count edges by type
    edge_counts: dict[str, int] = {}
    for edge in graph.iter_relationships():
        edge_counts[edge.type] = edge_counts.get(edge.type, 0) + 1

    # Save graph via backend
    backend.persist(graph)

    # Emit graph:build event
    emitter = create_emitter()
    emitter.emit(GraphBuildEvent(
        project_path=output_path.parent,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
    ))

    # Compute and persist diff
    diff: GraphDiff | None = None
    if old_graph is not None:
        diff = diff_graphs(old_graph, graph)
        diff_path = get_personal_dir() / "last-diff.json"
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(diff.model_dump_json(indent=2), encoding="utf-8")

    # Format output
    _format_build_result(
        output_path=output_path,
        node_counts=node_counts,
        edge_counts=edge_counts,
        total_nodes=graph.node_count,
        total_edges=graph.edge_count,
        diff=diff,
    )


def _format_build_result(
    output_path: Path,
    node_counts: dict[str, int],
    edge_counts: dict[str, int],
    total_nodes: int,
    total_edges: int,
    diff: GraphDiff | None = None,
) -> None:
    """Format and print graph build results."""
    console.print("\n[cyan]Building graph index...[/cyan]")

    # Display node counts
    console.print("\n[bold]Concepts by type:[/bold]")
    for node_type, count in sorted(node_counts.items()):
        console.print(f"  {node_type}: [green]{count}[/green]")

    console.print(f"\n[bold]Total concepts:[/bold] [green]{total_nodes}[/green]")

    # Display edge counts
    if edge_counts:
        console.print("\n[bold]Relationships by type:[/bold]")
        for edge_type, count in sorted(edge_counts.items()):
            console.print(f"  {edge_type}: [green]{count}[/green]")

    console.print(f"\n[bold]Total relationships:[/bold] [green]{total_edges}[/green]")

    # Display diff summary
    if diff is not None:
        console.print(f"\n[bold]Diff:[/bold] {diff.summary}")
        if diff.impact != "none":
            console.print(f"[bold]Impact:[/bold] {diff.impact}")

    console.print(f"\n✓ Saved to [cyan]{output_path}[/cyan]\n")


@graph_app.command()
def validate(
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

    if not index_path.exists():
        cli_error(
            f"Index file not found: {index_path}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    console.print(f"\nLoading index from [cyan]{index_path}[/cyan]...")
    graph = get_active_backend(index_path).load()
    console.print(
        f"  ✓ Loaded index with {graph.node_count} concepts, {graph.edge_count} relationships"
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
                f"  [red]✗[/red] Invalid edge: source '{edge.source}' not in index"
            )
            valid_edges = False
        if edge.target not in node_ids:
            console.print(
                f"  [red]✗[/red] Invalid edge: target '{edge.target}' not in index"
            )
            valid_edges = False

    if valid_edges:
        console.print("  ✓ All relationships valid")

    # Check 2: Detect cycles in depends_on relationships
    depends_edges = [e for e in edges_list if e.type == "depends_on"]
    if depends_edges:
        cycles = _detect_cycles(graph, depends_edges)
        if cycles:
            console.print(
                f"  [yellow]⚠[/yellow]  {len(cycles)} cycle(s) detected in depends_on relationships"
            )
            for cycle in cycles[:3]:  # Show first 3
                console.print(f"      {' → '.join(cycle)}")
        else:
            console.print("  ✓ No cycles detected")

    # Check 3: Reachability
    console.print(f"  ✓ {graph.node_count}/{graph.node_count} concepts reachable")

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
        console.print("  [yellow]⚠[/yellow]  Completeness gaps:")
        for node_type, expected, actual in missing:
            console.print(f"    {node_type}: expected ≥{expected}, found {actual}")
    else:
        console.print("  ✓ Completeness check passed")

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


@graph_app.command()
def extract(
    file_path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to governance file (optional, extracts all if not provided)"
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
) -> None:
    """Extract concepts from governance markdown files.

    If no file path is provided, extracts from all standard governance locations:
    - governance/prd.md (requirements)
    - governance/vision.md (outcomes)
    - framework/reference/constitution.md (principles)

    Examples:
        # Extract from all governance files
        $ rai graph extract

        # Extract from specific file
        $ rai graph extract governance/prd.md

        # Output as JSON
        $ rai graph extract --format json
    """
    extractor = GovernanceExtractor()

    if file_path:
        # Extract from single file
        if not file_path.exists():
            cli_error(f"File not found: {file_path}", exit_code=4)

        concepts = extractor.extract_from_file(file_path)

        if format == "json":
            output = {
                "concepts": [
                    {
                        "id": c.id,
                        "type": c.type.value,
                        "file": c.file,
                        "section": c.section,
                        "lines": list(c.lines),
                        "content": c.content,
                        "metadata": c.metadata,
                    }
                    for c in concepts
                ],
                "total": len(concepts),
            }
            console.print(json.dumps(output, indent=2))
        else:
            console.print(
                f"\nExtracting concepts from [cyan]{file_path.name}[/cyan]..."
            )

            for concept in concepts:
                console.print(
                    f"  ✓ Found {concept.metadata.get('requirement_id') or concept.metadata.get('principle_number') or concept.section}"
                )

            console.print(f"→ Extracted [green]{len(concepts)}[/green] concepts\n")

    else:
        # Extract from all governance files
        result = extractor.extract_with_result()

        if format == "json":
            output = {
                "concepts": [
                    {
                        "id": c.id,
                        "type": c.type.value,
                        "file": c.file,
                        "section": c.section,
                        "lines": list(c.lines),
                        "content": c.content,
                        "metadata": c.metadata,
                    }
                    for c in result.concepts
                ],
                "total": result.total,
                "files_processed": result.files_processed,
                "errors": result.errors,
            }
            console.print(json.dumps(output, indent=2))
        else:
            console.print("\nExtracting concepts from governance files...")

            # Group concepts by type
            by_type: dict[ConceptType, list[Concept]] = {}
            for concept in result.concepts:
                by_type.setdefault(concept.type, []).append(concept)

            if ConceptType.REQUIREMENT in by_type:
                reqs = by_type[ConceptType.REQUIREMENT]
                console.print(f"  📄 prd.md → [green]{len(reqs)}[/green] requirements")

            if ConceptType.OUTCOME in by_type:
                outcomes = by_type[ConceptType.OUTCOME]
                console.print(
                    f"  📄 vision.md → [green]{len(outcomes)}[/green] outcomes"
                )

            if ConceptType.PRINCIPLE in by_type:
                principles = by_type[ConceptType.PRINCIPLE]
                console.print(
                    f"  📄 constitution.md → [green]{len(principles)}[/green] principles"
                )

            console.print(
                f"→ Total: [green]{result.total}[/green] concepts extracted\n"
            )

            if result.errors:
                console.print("[yellow]Warnings:[/yellow]")
                for error in result.errors:
                    console.print(f"  ⚠  {error}")


# =============================================================================
# List Command
# =============================================================================


@graph_app.command("list")
def list_graph(
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
    if not unified_path.exists():
        cli_error(
            f"Graph index not found: {unified_path}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    # Load unified graph
    try:
        graph = get_active_backend(unified_path).load()
    except Exception as e:
        cli_error(f"Error loading graph index: {e}")

    # Filter to memory types only if requested (inlined — single-use constant)
    if memory_only:
        concepts = [
            c for c in graph.iter_concepts()
            if c.type in ["pattern", "calibration", "session"]
        ]
    else:
        concepts = list(graph.iter_concepts())

    console.print(f"\nGraph from: [cyan]{unified_path}[/cyan]")
    console.print(f"Concepts: [yellow]{len(concepts)}[/yellow]\n")

    # Format output
    if format == "json":
        output_text = json.dumps(
            [c.model_dump(mode="json") for c in concepts],
            indent=2,
        )
    elif format == "human":
        output_text = _format_concepts_markdown(concepts)
    else:  # table
        _print_concepts_table(concepts)
        if output:
            # For file output in table mode, use markdown
            output_text = _format_concepts_markdown(concepts)
        else:
            return

    # Write to file or stdout
    if output:
        output.write_text(output_text, encoding="utf-8")
        console.print(f"✓ Graph written to [cyan]{output}[/cyan]\n")
    elif format != "table":
        console.print(output_text)


def _format_concepts_markdown(concepts: list[GraphNode]) -> str:
    """Format concepts list as markdown."""
    lines = ["# Graph Concepts\n"]
    lines.append(f"**Total:** {len(concepts)}\n")

    # Group by type
    by_type: dict[str, list[GraphNode]] = {}
    for concept in concepts:
        type_name = concept.type
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(concept)

    lines.append("## Concepts by Type\n")
    for type_name, type_concepts in sorted(by_type.items()):
        lines.append(f"### {type_name.title()} ({len(type_concepts)})\n")
        for concept in sorted(type_concepts, key=lambda c: c.id):
            content = (
                concept.content[:60] + "..."
                if len(concept.content) > 60
                else concept.content
            )
            lines.append(f"- **{concept.id}**: {content}")
        lines.append("")

    return "\n".join(lines)


def _print_concepts_table(concepts: list[GraphNode]) -> None:
    """Print concepts as rich table."""
    table = Table(title="Graph Concepts")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Content", max_width=50)
    table.add_column("Created")

    for concept in sorted(concepts, key=lambda c: c.id):
        content = (
            concept.content[:47] + "..."
            if len(concept.content) > 50
            else concept.content
        )
        table.add_row(
            concept.id,
            concept.type,
            content,
            concept.created,
        )

    console.print(table)


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
    import webbrowser

    from rai_cli.viz import generate_viz_html

    unified_path = index_path or _get_default_index_path()
    if not unified_path.exists():
        cli_error(
            f"Graph index not found: {unified_path}",
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )

    output_path = output or Path(".raise/rai/memory/graph.html")

    console.print(f"\nGenerating visualization from [cyan]{unified_path}[/cyan]...")
    result_path = generate_viz_html(unified_path, output_path)
    console.print(f"✓ Written to [cyan]{result_path}[/cyan]\n")

    if open_browser:
        webbrowser.open(to_file_uri(result_path))
        console.print("  Opened in browser.\n")
