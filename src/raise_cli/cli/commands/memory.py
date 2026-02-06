"""CLI commands for Rai's memory: query, build, and manage.

Memory is the unified knowledge base containing:
- Governance (principles, requirements, terms)
- Patterns (learned behaviors and best practices)
- Calibration (estimation data)
- Sessions (work history)
- Skills (workflow metadata)
- Work (epics, features, decisions)

The "graph" is an implementation detail — users interact with "memory".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import get_memory_dir
from raise_cli.context import UnifiedGraph, UnifiedGraphBuilder
from raise_cli.context.models import ConceptNode
from raise_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)
from raise_cli.governance import ConceptType, GovernanceExtractor
from raise_cli.memory import (
    CalibrationInput,
    PatternInput,
    PatternSubType,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
)

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
    - Work (epics, features, decisions)

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

    # Build and execute query
    unified_query = UnifiedQuery(
        query=query_str,
        strategy=query_strategy,
        max_depth=1,
        types=types_list,  # type: ignore[arg-type]
        limit=limit,
    )

    console.print(f"\nQuerying memory for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(unified_query)

    # Format output
    output_text = (
        _format_json(result) if format == "json" else _format_markdown(result)
    )

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
# Build/Index Commands
# =============================================================================


@memory_app.command()
def build(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save index JSON"),
    ] = None,
) -> None:
    """Build memory index from all sources.

    Merges all context sources into a single queryable index:
    - Governance documents (constitution, PRD, vision)
    - Memory (patterns, calibration, sessions)
    - Work tracking (epics, features)
    - Skills (SKILL.md metadata)
    - Components (from discovery)

    Examples:
        # Build index to default location
        $ raise memory build

        # Save to custom location
        $ raise memory build --output custom_index.json
    """
    default_output = _get_default_index_path()
    output_path = output or default_output

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

    # Format output
    _format_build_result(
        output_path=output_path,
        node_counts=node_counts,
        edge_counts=edge_counts,
        total_nodes=graph.node_count,
        total_edges=graph.edge_count,
    )


def _format_build_result(
    output_path: Path,
    node_counts: dict[str, int],
    edge_counts: dict[str, int],
    total_nodes: int,
    total_edges: int,
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
    - governance/projects/*/prd.md (requirements)
    - governance/solution/vision.md (outcomes)
    - framework/reference/constitution.md (principles)

    Examples:
        # Extract from all governance files
        $ raise memory extract

        # Extract from specific file
        $ raise memory extract governance/projects/raise-cli/prd.md

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
        typer.Option("--from", "-f", help="Feature/session where learned"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Add a new pattern to memory.

    Examples:
        # Add a process pattern
        $ raise memory add-pattern "HITL before commits" -c "git,workflow"

        # Add a technical pattern
        $ raise memory add-pattern "Use capsys for stdout tests" -t technical -c "pytest,testing"

        # Add with source reference
        $ raise memory add-pattern "BFS reuse across modules" -t architecture --from F2.3
    """
    mem_dir = memory_dir or _get_default_memory_dir()
    if not mem_dir.exists():
        cli_error(f"Memory directory not found: {mem_dir}", exit_code=4)

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

    input_data = PatternInput(
        content=content,
        sub_type=pattern_type,
        context=context_list,
        learned_from=learned_from,
    )

    result = append_pattern(mem_dir, input_data)

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
    feature: Annotated[str, typer.Argument(help="Feature ID (e.g., F3.5)")],
    name: Annotated[
        str,
        typer.Option("--name", help="Feature name (required)"),
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
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Add calibration data for a completed feature.

    Examples:
        # Basic calibration
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20

        # With estimate for velocity calculation
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60

        # Full details
        $ raise memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60 --sp 2 -n "Hook-assisted"
    """
    mem_dir = memory_dir or _get_default_memory_dir()
    if not mem_dir.exists():
        cli_error(f"Memory directory not found: {mem_dir}", exit_code=4)

    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    if size.upper() not in valid_sizes:
        cli_error(
            f"Invalid size: {size}",
            hint=f"Valid sizes: {', '.join(valid_sizes)}",
            exit_code=7,
        )

    input_data = CalibrationInput(
        feature=feature,
        name=name,
        size=size.upper(),
        sp=sp,
        estimated_min=estimated,
        actual_min=actual,
        kata_cycle=kata,
        notes=notes,
    )

    result = append_calibration(mem_dir, input_data)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Feature: {feature} ({name})")
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
        typer.Option("--type", "-t", help="Session type (feature, research, etc.)"),
    ] = "feature",
    log_path: Annotated[
        str | None,
        typer.Option("--log", "-l", help="Path to session log file"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Add a session record to memory.

    Examples:
        # Basic session
        $ raise memory add-session "F3.5 Skills Integration"

        # With outcomes
        $ raise memory add-session "F3.5 Skills Integration" -o "Writer API,Hooks setup,CLI commands"

        # Full details
        $ raise memory add-session "F3.5 Skills Integration" -t feature -o "Writer API,Hooks" -l "dev/sessions/2026-02-02-f3.5.md"
    """
    mem_dir = memory_dir or _get_default_memory_dir()
    if not mem_dir.exists():
        cli_error(f"Memory directory not found: {mem_dir}", exit_code=4)

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
