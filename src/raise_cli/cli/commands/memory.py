"""CLI commands for Rai's memory: query, build, and manage.

Memory is the unified knowledge base containing:
- Governance (principles, requirements, terms)
- Patterns (learned behaviors and best practices)
- Calibration (estimation data)
- Sessions (work history)
- Skills (workflow metadata)
- Work (epics, stories, decisions)

The "graph" is an implementation detail — users interact with "memory".
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import get_memory_dir, get_personal_dir
from raise_cli.context import UnifiedGraph, UnifiedGraphBuilder
from raise_cli.context.diff import GraphDiff, diff_graphs
from raise_cli.context.models import ConceptNode
from raise_cli.context.query import (
    ArchitecturalContext,
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)
from raise_cli.governance import ConceptType, GovernanceExtractor
from raise_cli.memory import (
    CalibrationInput,
    MemoryScope,
    PatternInput,
    PatternSubType,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
    get_memory_dir_for_scope,
)
from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    SessionEvent,
    WorkLifecycle,
)
from raise_cli.telemetry.writer import emit

# Memory types for filtering (when querying memory-only)
MEMORY_TYPES = ["pattern", "calibration", "session"]

# Default index file name
INDEX_FILE = "index.json"

memory_app = typer.Typer(
    name="memory",
    help="Query and manage Rai's memory",
    no_args_is_help=True,
)

console = Console()


def _get_default_memory_dir() -> Path:
    """Get default memory directory (.raise/rai/memory)."""
    return get_memory_dir()


def _get_default_index_path() -> Path:
    """Get default memory index path (.raise/rai/memory/index.json)."""
    return get_memory_dir() / INDEX_FILE


# =============================================================================
# Query Commands
# =============================================================================


@memory_app.command()
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
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
) -> None:
    """Query Rai's memory for relevant concepts.

    Searches the unified memory containing all context sources:
    - Governance (principles, requirements, terms)
    - Memory (patterns, calibration, sessions)
    - Skills (workflow metadata)
    - Work (epics, stories, decisions)

    Examples:
        # Search by keywords
        $ raise memory query "planning estimation"

        # Filter to patterns only
        $ raise memory query "testing" --types pattern,calibration

        # Lookup specific concept by ID
        $ raise memory query "PAT-001" --strategy concept_lookup

        # Output as JSON
        $ raise memory query "velocity" --format json
    """
    # Load engine
    unified_path = index_path or _get_default_index_path()
    try:
        engine = UnifiedQueryEngine.from_file(unified_path)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'raise memory build' first to create the index",
            exit_code=4,
        )

    # Parse types filter
    types_list: list[str] | None = None
    if types:
        types_list = [t.strip() for t in types.split(",")]

    # Determine strategy
    query_strategy = UnifiedQueryStrategy.KEYWORD_SEARCH  # Default
    if strategy:
        try:
            query_strategy = UnifiedQueryStrategy(strategy)
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
    unified_query = UnifiedQuery(
        query=query_str,
        strategy=query_strategy,
        max_depth=1,
        types=types_list,  # type: ignore[arg-type]
        edge_types=edge_types_list,  # type: ignore[arg-type]
        limit=limit,
    )

    console.print(f"\nQuerying memory for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(unified_query)

    # Format output
    output_text = _format_json(result) if format == "json" else _format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Results written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)


def _format_markdown(result: UnifiedQueryResult) -> str:
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
    by_type: dict[str, list[ConceptNode]] = {}
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


def _format_json(result: UnifiedQueryResult) -> str:
    """Format query result as JSON."""
    return result.to_json()


# =============================================================================
# Architectural Context Command
# =============================================================================


@memory_app.command("context")
def context_cmd(
    module_id: Annotated[
        str, typer.Argument(help="Module ID (e.g., mod-memory)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
) -> None:
    """Show full architectural context for a module.

    Returns the module's bounded context (domain), architectural layer,
    applicable guardrails (constraints), and module dependencies in a
    single structured view.

    Examples:
        # Show context for memory module
        $ raise memory context mod-memory

        # JSON output for programmatic use
        $ raise memory context mod-memory --format json
    """
    unified_path = index_path or _get_default_index_path()
    try:
        engine = UnifiedQueryEngine.from_file(unified_path)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'raise memory build' first to create the index",
            exit_code=4,
        )
        return  # cli_error exits, but this satisfies pyright

    ctx = engine.get_architectural_context(module_id)
    if ctx is None:
        cli_error(
            f"Module not found: {module_id}",
            hint="Check available modules with: raise memory query '' --types module",
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
        console.print(
            f"\n[bold]Constraints:[/bold] {len(ctx.constraints)} guardrails"
        )
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
# Generate MEMORY.md
# =============================================================================


@memory_app.command("generate")
def generate_memory(
    path: Annotated[
        Path | None,
        typer.Option(
            "--path", "-p", help="Project root (defaults to current directory)"
        ),
    ] = None,
) -> None:
    """Generate MEMORY.md for AI editors (deprecated).

    MEMORY.md generation is no longer needed — the memory graph is the
    single source of truth. Context is delivered via `raise session start
    --context` which assembles a token-optimized bundle from the graph.

    Use `raise memory build` to rebuild the graph instead.

    Examples:
        # Build the memory graph (recommended)
        $ raise memory build
    """
    console.print(
        "\n[yellow]Skipped:[/yellow] MEMORY.md generation is deprecated."
    )
    console.print(
        "  The memory graph is the single source of truth."
    )
    console.print(
        "  Context is delivered via [cyan]raise session start --context[/cyan]."
    )
    console.print(
        "  Use [cyan]raise memory build[/cyan] to rebuild the graph.\n"
    )


# =============================================================================
# Build/Index Commands
# =============================================================================


@memory_app.command()
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
    """Build memory index from all sources.

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
        $ raise memory build

        # Build without diff
        $ raise memory build --no-diff

        # Save to custom location
        $ raise memory build --output custom_index.json
    """
    default_output = _get_default_index_path()
    output_path = output or default_output

    # Load old graph for diff (before building new one)
    old_graph: UnifiedGraph | None = None
    if not no_diff and output_path.exists():
        old_graph = UnifiedGraph.load(output_path)

    # Build unified graph
    builder = UnifiedGraphBuilder()
    graph = builder.build()

    # Count nodes by type
    node_counts: dict[str, int] = {}
    for node in graph.iter_concepts():
        node_counts[node.type] = node_counts.get(node.type, 0) + 1

    # Count edges by type
    edge_counts: dict[str, int] = {}
    for edge in graph.iter_relationships():
        edge_counts[edge.type] = edge_counts.get(edge.type, 0) + 1

    # Save graph
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.save(output_path)

    # Compute and persist diff
    diff: GraphDiff | None = None
    if old_graph is not None:
        diff = diff_graphs(old_graph, graph)
        diff_path = get_personal_dir() / "last-diff.json"
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(diff.model_dump_json(indent=2))

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
    """Format and print memory build results."""
    console.print("\n[cyan]Building memory index...[/cyan]")

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


@memory_app.command()
def validate(
    index_file: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Path to index JSON file"),
    ] = None,
) -> None:
    """Validate memory index structure and relationships.

    Checks for:
    - Cycles in depends_on relationships
    - Valid relationship types
    - All edge targets exist as nodes

    Examples:
        # Validate default index
        $ raise memory validate

        # Validate specific index file
        $ raise memory validate --index custom_index.json
    """
    default_index = _get_default_index_path()
    index_path = index_file or default_index

    if not index_path.exists():
        cli_error(
            f"Index file not found: {index_path}",
            hint="Run 'raise memory build' first to create the index",
            exit_code=4,
        )

    console.print(f"\nLoading index from [cyan]{index_path}[/cyan]...")
    graph = UnifiedGraph.load(index_path)
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
            console.print(
                f"    {node_type}: expected ≥{expected}, found {actual}"
            )
    else:
        console.print("  ✓ Completeness check passed")

    console.print("\n[green]Memory index is valid.[/green]\n")


def _detect_cycles(graph: UnifiedGraph, edges: list) -> list[list[str]]:
    """Detect cycles in a set of edges using DFS."""
    # Build adjacency list from edges
    adj: dict[str, list[str]] = {}
    for edge in edges:
        adj.setdefault(edge.source, []).append(edge.target)

    cycles: list[list[str]] = []
    visited: set[str] = set()
    rec_stack: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path[:])
            elif neighbor in rec_stack:
                # Cycle detected
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        rec_stack.remove(node)

    # Get all node IDs
    node_ids = {node.id for node in graph.iter_concepts()}

    for node in node_ids:
        if node not in visited and node in adj:
            dfs(node, [])

    return cycles


@memory_app.command()
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
        $ raise memory extract

        # Extract from specific file
        $ raise memory extract governance/prd.md

        # Output as JSON
        $ raise memory extract --format json
    """
    extractor = GovernanceExtractor()

    if file_path:
        # Extract from single file
        if not file_path.exists():
            cli_error(f"File not found: {file_path}", exit_code=4)

        concepts = extractor.extract_from_file(file_path)

        if format == "json":
            # JSON output
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
            # Human-readable output
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
            # JSON output
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
            # Human-readable output
            console.print("\nExtracting concepts from governance files...")

            # Group concepts by type
            by_type: dict[ConceptType, list] = {}
            for concept in result.concepts:
                by_type.setdefault(concept.type, []).append(concept)

            # Display by file type
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


@memory_app.command("list")
def list_memory(
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
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
    memory_only: Annotated[
        bool,
        typer.Option(
            "--memory-only/--all",
            help="Show only memory types (pattern, calibration, session) or all",
        ),
    ] = False,
) -> None:
    """List concepts in memory.

    Shows concepts from the memory index for inspection and debugging.

    Examples:
        # Show summary table (all concepts)
        $ raise memory list

        # Show only patterns/calibrations/sessions
        $ raise memory list --memory-only

        # Export as JSON
        $ raise memory list --format json --output memory.json

        # Export as human-readable markdown
        $ raise memory list --format human --output memory.md
    """
    # Resolve index path
    unified_path = index_path or _get_default_index_path()
    if not unified_path.exists():
        cli_error(
            f"Memory index not found: {unified_path}",
            hint="Run 'raise memory build' first to create the index",
            exit_code=4,
        )

    # Load unified graph
    try:
        graph = UnifiedGraph.load(unified_path)
    except Exception as e:
        cli_error(f"Error loading memory index: {e}")

    # Filter to memory types only if requested
    if memory_only:
        concepts = [c for c in graph.iter_concepts() if c.type in MEMORY_TYPES]
    else:
        concepts = list(graph.iter_concepts())

    console.print(f"\nMemory from: [cyan]{unified_path}[/cyan]")
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
        output.write_text(output_text)
        console.print(f"✓ Memory written to [cyan]{output}[/cyan]\n")
    elif format != "table":
        console.print(output_text)


def _format_concepts_markdown(concepts: list[ConceptNode]) -> str:
    """Format concepts list as markdown."""

    lines = ["# Memory Concepts\n"]
    lines.append(f"**Total:** {len(concepts)}\n")

    # Group by type
    by_type: dict[str, list[ConceptNode]] = {}
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


def _print_concepts_table(concepts: list[ConceptNode]) -> None:
    """Print concepts as rich table."""

    table = Table(title="Memory Concepts")
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


@memory_app.command("viz")
def viz(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output HTML file path"),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open in browser after generating"),
    ] = True,
) -> None:
    """Generate interactive HTML visualization of the memory graph.

    Creates a self-contained HTML file with a D3.js force-directed graph.
    Nodes are color-coded by type, filterable, zoomable, and searchable.

    Examples:
        # Generate and open in browser
        $ raise memory viz

        # Generate to specific path
        $ raise memory viz --output graph.html

        # Generate without opening
        $ raise memory viz --no-open
    """
    import webbrowser

    from raise_cli.viz import generate_viz_html

    unified_path = index_path or _get_default_index_path()
    if not unified_path.exists():
        cli_error(
            f"Memory index not found: {unified_path}",
            hint="Run 'raise memory build' first to create the index",
            exit_code=4,
        )

    output_path = output or Path(".raise/rai/memory/graph.html")

    console.print(f"\nGenerating visualization from [cyan]{unified_path}[/cyan]...")
    result_path = generate_viz_html(unified_path, output_path)
    console.print(f"✓ Written to [cyan]{result_path}[/cyan]\n")

    if open_browser:
        webbrowser.open(f"file://{result_path.resolve()}")
        console.print("  Opened in browser.\n")


# =============================================================================
# Append Commands (Add to memory)
# =============================================================================


@memory_app.command("add-pattern")
def add_pattern(
    content: Annotated[str, typer.Argument(help="Pattern description")],
    context: Annotated[
        str,
        typer.Option("--context", "-c", help="Context keywords (comma-separated)"),
    ] = "",
    sub_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Pattern type (codebase, process, architecture, technical)",
        ),
    ] = "process",
    learned_from: Annotated[
        str | None,
        typer.Option("--from", "-f", help="Story/session where learned"),
    ] = None,
    scope: Annotated[
        str,
        typer.Option("--scope", "-s", help="Memory scope (global, project, personal)"),
    ] = "project",
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir", "-m", help="Memory directory path (overrides scope)"
        ),
    ] = None,
) -> None:
    """Add a new pattern to memory.

    Examples:
        # Add a process pattern (default: project scope)
        $ raise memory add-pattern "HITL before commits" -c "git,workflow"

        # Add a technical pattern
        $ raise memory add-pattern "Use capsys for stdout tests" -t technical -c "pytest,testing"

        # Add with source reference
        $ raise memory add-pattern "BFS reuse across modules" -t architecture --from F2.3

        # Add to global scope (universal pattern)
        $ raise memory add-pattern "Universal TDD pattern" --scope global

        # Add to personal scope (my learnings)
        $ raise memory add-pattern "My workflow preference" --scope personal
    """
    # Parse scope
    try:
        memory_scope = MemoryScope(scope)
    except ValueError:
        cli_error(
            f"Invalid scope: {scope}",
            hint="Valid scopes: global, project, personal",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    # Determine directory (explicit dir overrides scope)
    mem_dir = memory_dir or get_memory_dir_for_scope(memory_scope)
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Parse context
    context_list = [c.strip() for c in context.split(",") if c.strip()]

    # Parse sub_type
    try:
        pattern_type = PatternSubType(sub_type)
    except ValueError:
        cli_error(
            f"Invalid pattern type: {sub_type}",
            hint="Valid types: codebase, process, architecture, technical",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    input_data = PatternInput(
        content=content,
        sub_type=pattern_type,
        context=context_list,
        learned_from=learned_from,
    )

    result = append_pattern(mem_dir, input_data, scope=memory_scope)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Content: {content[:60]}...")
        if context_list:
            console.print(f"  Context: {', '.join(context_list)}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@memory_app.command("add-calibration")
def add_calibration_cmd(
    story: Annotated[str, typer.Argument(help="Story ID (e.g., F3.5)")],
    name: Annotated[
        str,
        typer.Option("--name", help="Story name (required)"),
    ],
    size: Annotated[
        str,
        typer.Option("--size", "-s", help="T-shirt size: XS, S, M, L, XL (required)"),
    ],
    actual: Annotated[
        int,
        typer.Option("--actual", "-a", help="Actual minutes spent (required)"),
    ],
    estimated: Annotated[
        int | None,
        typer.Option("--estimated", "-e", help="Estimated minutes"),
    ] = None,
    sp: Annotated[
        int | None,
        typer.Option("--sp", help="Story points"),
    ] = None,
    kata: Annotated[
        bool,
        typer.Option("--kata/--no-kata", help="Kata cycle followed (default: yes)"),
    ] = True,
    notes: Annotated[
        str | None,
        typer.Option("--notes", "-n", help="Additional notes"),
    ] = None,
    scope: Annotated[
        str,
        typer.Option("--scope", help="Memory scope (global, project, personal)"),
    ] = "project",
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir", "-m", help="Memory directory path (overrides scope)"
        ),
    ] = None,
) -> None:
    """Add calibration data for a completed story.

    Examples:
        # Basic calibration (default: project scope)
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20

        # With estimate for velocity calculation
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60

        # Full details
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60 --sp 2 -n "Hook-assisted"

        # Add to personal scope
        $ raise memory add-calibration F3.5 --name "Skills" -s XS -a 20 --scope personal
    """
    # Parse scope
    try:
        memory_scope = MemoryScope(scope)
    except ValueError:
        cli_error(
            f"Invalid scope: {scope}",
            hint="Valid scopes: global, project, personal",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    # Determine directory (explicit dir overrides scope)
    mem_dir = memory_dir or get_memory_dir_for_scope(memory_scope)
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    if size.upper() not in valid_sizes:
        cli_error(
            f"Invalid size: {size}",
            hint=f"Valid sizes: {', '.join(valid_sizes)}",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    input_data = CalibrationInput(
        story=story,
        name=name,
        size=size.upper(),
        sp=sp,
        estimated_min=estimated,
        actual_min=actual,
        kata_cycle=kata,
        notes=notes,
    )

    result = append_calibration(mem_dir, input_data, scope=memory_scope)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Story: {story} ({name})")
        console.print(f"  Size: {size.upper()}, Actual: {actual}min")
        if estimated:
            ratio = round(estimated / actual, 1)
            console.print(f"  Velocity: {ratio}x (estimated {estimated}min)")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@memory_app.command("add-session")
def add_session_cmd(
    topic: Annotated[str, typer.Argument(help="Session topic")],
    outcomes: Annotated[
        str,
        typer.Option("--outcomes", "-o", help="Session outcomes (comma-separated)"),
    ] = "",
    session_type: Annotated[
        str,
        typer.Option("--type", "-t", help="Session type (story, research, etc.)"),
    ] = "story",
    log_path: Annotated[
        str | None,
        typer.Option("--log", "-l", help="Path to session log file"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Add a session record to memory (personal scope).

    Sessions are developer-specific and always written to personal directory.

    Examples:
        # Basic session
        $ raise memory add-session "F3.5 Skills Integration"

        # With outcomes
        $ raise memory add-session "F3.5 Skills Integration" -o "Writer API,Hooks setup,CLI commands"

        # Full details
        $ raise memory add-session "F3.5 Skills Integration" -t story -o "Writer API,Hooks" -l "dev/sessions/2026-02-02-f3.5.md"
    """
    # Sessions always go to personal directory (developer-specific)
    mem_dir = memory_dir or get_personal_dir()
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Parse outcomes
    outcomes_list = [o.strip() for o in outcomes.split(",") if o.strip()]

    input_data = SessionInput(
        topic=topic,
        session_type=session_type,
        outcomes=outcomes_list,
        log_path=log_path,
    )

    result = append_session(mem_dir, input_data)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Topic: {topic}")
        console.print(f"  Type: {session_type}")
        if outcomes_list:
            console.print(f"  Outcomes: {', '.join(outcomes_list[:3])}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


# =============================================================================
# Emit Commands (Telemetry signals)
# =============================================================================


@memory_app.command("emit-work")
def emit_work(
    work_type: Annotated[
        str,
        typer.Argument(help="Work type (epic, story)"),
    ],
    work_id: Annotated[
        str,
        typer.Argument(help="Work ID (e.g., E9, F9.4)"),
    ],
    event_type: Annotated[
        str,
        typer.Option(
            "--event",
            "-e",
            help="Event type (start, complete, blocked, unblocked, abandoned)",
        ),
    ] = "start",
    phase: Annotated[
        str,
        typer.Option("--phase", "-p", help="Phase (design, plan, implement, review)"),
    ] = "design",
    blocker: Annotated[
        str,
        typer.Option(
            "--blocker", "-b", help="Blocker description (for blocked events)"
        ),
    ] = "",
) -> None:
    """Emit a work lifecycle event for Lean flow analysis.

    Tracks work items (epics, stories) through normalized phases to enable:
    - Lead time: total time from start to complete
    - Wait time: gaps between phases
    - WIP: work started but not completed
    - Bottlenecks: which phase takes longest
    - Cross-level analysis: compare epic vs story flow

    Phases (normalized across all work types):
    - design: Scope definition and specification
    - plan: Task/story decomposition and sequencing
    - implement: Active development work
    - review: Retrospective and learnings

    Examples:
        # Epic lifecycle
        $ raise memory emit-work epic E9 --event start --phase design
        $ raise memory emit-work epic E9 -e complete -p design
        $ raise memory emit-work epic E9 -e start -p plan

        # Story lifecycle
        $ raise memory emit-work story F9.4 --event start --phase design
        $ raise memory emit-work story F9.4 -e complete -p implement
        $ raise memory emit-work story F9.4 -e start -p review

        # Work blocked
        $ raise memory emit-work story F9.4 -e blocked -p plan -b "unclear requirements"

        # Work unblocked
        $ raise memory emit-work story F9.4 -e unblocked -p plan
    """
    # Validate work type
    valid_work_types: list[Literal["epic", "story"]] = ["epic", "story"]
    work_type_lower = work_type.lower()
    if work_type_lower not in valid_work_types:
        cli_error(
            f"Invalid work type: {work_type}",
            hint=f"Valid types: {', '.join(valid_work_types)}",
            exit_code=7,
        )

    # Validate event type
    valid_events: list[
        Literal["start", "complete", "blocked", "unblocked", "abandoned"]
    ] = [
        "start",
        "complete",
        "blocked",
        "unblocked",
        "abandoned",
    ]
    if event_type not in valid_events:
        cli_error(
            f"Invalid event: {event_type}",
            hint=f"Valid events: {', '.join(valid_events)}",
            exit_code=7,
        )

    # Validate phase
    valid_phases: list[Literal["init", "design", "plan", "implement", "review", "close"]] = [
        "init",
        "design",
        "plan",
        "implement",
        "review",
        "close",
    ]
    if phase not in valid_phases:
        cli_error(
            f"Invalid phase: {phase}",
            hint=f"Valid phases: {', '.join(valid_phases)}",
            exit_code=7,
        )

    # Blocker is required for blocked events
    blocker_value = blocker if blocker else None
    if event_type == "blocked" and not blocker_value:
        console.print(
            "[yellow]Warning:[/yellow] No blocker description provided for blocked event"
        )

    # Create event
    lifecycle_event = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type_lower,  # type: ignore[arg-type]
        work_id=work_id,
        event=event_type,  # type: ignore[arg-type]
        phase=phase,  # type: ignore[arg-type]
        blocker=blocker_value,
    )

    # Emit signal
    result = emit(lifecycle_event)

    if result.success:
        # Format label based on work type
        label = f"{work_type_lower.capitalize()} {work_id}"

        # Format output based on event type
        if event_type == "start":
            console.print(f"\n[green]▶[/green] {label} → {phase} started")
        elif event_type == "complete":
            console.print(f"\n[green]✓[/green] {label} → {phase} complete")
        elif event_type == "blocked":
            console.print(f"\n[red]⏸[/red] {label} → {phase} blocked")
            if blocker_value:
                console.print(f"  Blocker: {blocker_value}")
        elif event_type == "unblocked":
            console.print(f"\n[green]▶[/green] {label} → {phase} unblocked")
        elif event_type == "abandoned":
            console.print(f"\n[yellow]✗[/yellow] {label} → {phase} abandoned")

        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit work lifecycle event")


@memory_app.command("emit-session")
def emit_session_event(
    session_type: Annotated[
        str,
        typer.Option(
            "--type", "-t", help="Session type (e.g., story, research, maintenance)"
        ),
    ] = "story",
    outcome: Annotated[
        str,
        typer.Option(
            "--outcome",
            "-o",
            help="Session outcome (success, partial, abandoned)",
        ),
    ] = "success",
    duration: Annotated[
        int,
        typer.Option("--duration", "-d", help="Session duration in minutes"),
    ] = 0,
    stories: Annotated[
        str,
        typer.Option("--stories", "-f", help="Stories worked on (comma-separated)"),
    ] = "",
) -> None:
    """Emit a session event to telemetry.

    Records a session completion signal for local learning and insights.
    Called at the end of /session-close to capture session metadata.

    Examples:
        # Basic session complete
        $ raise memory emit-session --type story --outcome success

        # With duration and stories
        $ raise memory emit-session -t story -o success -d 45 -f F9.1,F9.2,F9.3

        # Research session
        $ raise memory emit-session --type research --outcome partial --duration 90
    """
    # Validate outcome
    valid_outcomes: list[Literal["success", "partial", "abandoned"]] = [
        "success",
        "partial",
        "abandoned",
    ]
    if outcome not in valid_outcomes:
        cli_error(
            f"Invalid outcome: {outcome}",
            hint=f"Valid outcomes: {', '.join(valid_outcomes)}",
            exit_code=7,
        )

    # Parse stories
    stories_list = [f.strip() for f in stories.split(",") if f.strip()]

    # Create event
    event = SessionEvent(
        timestamp=datetime.now(UTC),
        session_type=session_type,
        outcome=outcome,  # type: ignore[arg-type]
        duration_min=duration,
        stories=stories_list,
    )

    # Emit signal
    result = emit(event)

    if result.success:
        console.print("\n[green]✓[/green] Session event recorded")
        console.print(f"  Type: {session_type}")
        console.print(f"  Outcome: {outcome}")
        console.print(f"  Duration: {duration} min")
        if stories_list:
            console.print(f"  Stories: {', '.join(stories_list)}")
        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit session event")


@memory_app.command("emit-calibration")
def emit_calibration_event(
    story: Annotated[
        str,
        typer.Argument(help="Story ID (e.g., F9.4)"),
    ],
    size: Annotated[
        str,
        typer.Option("--size", "-s", help="T-shirt size (XS, S, M, L)"),
    ] = "S",
    estimated: Annotated[
        int,
        typer.Option("--estimated", "-e", help="Estimated duration in minutes"),
    ] = 0,
    actual: Annotated[
        int,
        typer.Option("--actual", "-a", help="Actual duration in minutes"),
    ] = 0,
) -> None:
    """Emit a calibration event to telemetry.

    Records estimate vs actual for velocity tracking and pattern detection.
    Called at the end of /story-review to capture calibration data.

    Velocity is calculated automatically: estimated / actual.
    - velocity > 1.0 means faster than estimated
    - velocity < 1.0 means slower than estimated

    Examples:
        # Story completed faster than estimated
        $ raise memory emit-calibration F9.4 --size S --estimated 30 --actual 15

        # Story took longer
        $ raise memory emit-calibration F9.4 -s M -e 60 -a 90

        # Short form
        $ raise memory emit-calibration F9.4 -s S -e 30 -a 15
    """
    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    size_upper = size.upper()
    if size_upper not in valid_sizes:
        cli_error(
            f"Invalid size: {size}",
            hint=f"Valid sizes: {', '.join(valid_sizes)}",
            exit_code=7,
        )

    # Validate durations
    if estimated <= 0:
        cli_error("Estimated duration must be > 0", exit_code=7)
    if actual <= 0:
        cli_error("Actual duration must be > 0", exit_code=7)

    # Calculate velocity
    velocity = round(estimated / actual, 2)

    # Create event
    event = CalibrationEvent(
        timestamp=datetime.now(UTC),
        story_id=story,
        story_size=size_upper,
        estimated_min=estimated,
        actual_min=actual,
        velocity=velocity,
    )

    # Emit signal
    result = emit(event)

    if result.success:
        console.print("\n[green]✓[/green] Calibration event recorded")
        console.print(f"  Story: {story}")
        console.print(f"  Size: {size_upper}")
        console.print(f"  Estimated: {estimated} min")
        console.print(f"  Actual: {actual} min")
        console.print(f"  Velocity: {velocity}x", end="")
        if velocity > 1.0:
            console.print(" [green](faster than estimated)[/green]")
        elif velocity < 1.0:
            console.print(" [yellow](slower than estimated)[/yellow]")
        else:
            console.print(" (on target)")
        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit calibration event")
