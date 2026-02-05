"""CLI commands for memory queries and writes.

Memory queries now use the UnifiedGraph (ADR-019) with type filters,
rather than a separate MemoryGraph. This consolidation provides:
- Single source of truth for all context
- Cross-domain queries (patterns + skills + governance)
- Simpler cache invalidation
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptNode
from raise_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryResult,
)
from raise_cli.cli.error_handler import cli_error
from raise_cli.memory import (
    CalibrationInput,
    PatternInput,
    PatternSubType,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
)

# Memory types for filtering unified graph
MEMORY_TYPES = ["pattern", "calibration", "session"]

memory_app = typer.Typer(
    name="memory",
    help="Query Rai's memory graph for relevant concepts",
    no_args_is_help=True,
)

console = Console()


def _get_default_memory_dir() -> Path:
    """Get default memory directory (.rai/memory)."""
    return Path(".rai/memory")


def _get_default_graph_path() -> Path:
    """Get default unified graph path (.raise/graph/unified.json)."""
    return Path(".raise/graph/unified.json")


@memory_app.command()
def query(
    query_str: Annotated[str, typer.Argument(help="Search query (keywords)")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (markdown or json)"),
    ] = "markdown",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    max_results: Annotated[
        int,
        typer.Option("--max-results", "-n", help="Maximum number of results (1-50)"),
    ] = 10,
    expand: Annotated[
        bool,
        typer.Option("--expand/--no-expand", help="Expand results via BFS traversal"),
    ] = True,
    max_depth: Annotated[
        int,
        typer.Option("--max-depth", "-d", help="Maximum traversal depth (1-3)"),
    ] = 2,
    graph_path: Annotated[
        Path | None,
        typer.Option("--graph", "-g", help="Unified graph path"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir",
            "-m",
            help="[DEPRECATED] Use --graph instead",
            hidden=True,
        ),
    ] = None,
) -> None:
    """Query memory for relevant concepts.

    Searches Rai's memory (patterns, calibrations, sessions) using
    keyword matching and relevance scoring. Uses the unified graph
    with memory type filters.

    Examples:
        # Simple keyword search
        $ raise memory query "testing patterns"

        # Limit results
        $ raise memory query "velocity" --max-results 5

        # Output as JSON
        $ raise memory query "calibration" --format json

        # Save to file
        $ raise memory query "architecture" --output context.md
    """
    # Handle deprecated option
    if memory_dir is not None:
        warnings.warn(
            "--memory-dir is deprecated, use --graph instead",
            DeprecationWarning,
            stacklevel=2,
        )

    # Resolve graph path
    unified_path = graph_path or _get_default_graph_path()
    if not unified_path.exists():
        cli_error(
            f"Unified graph not found: {unified_path}",
            hint="Run 'raise graph build --unified' to create the graph first",
            exit_code=4,
        )

    # Load unified graph and create query engine
    try:
        engine = UnifiedQueryEngine.from_file(unified_path)
    except Exception as e:
        cli_error(f"Error loading unified graph: {e}")

    # Query with memory type filter
    unified_query = UnifiedQuery(
        query=query_str,
        types=MEMORY_TYPES,  # type: ignore[arg-type]
        limit=min(max(1, max_results), 50),
        max_depth=min(max(1, max_depth), 3) if expand else 0,
    )
    result = engine.query(unified_query)

    console.print(f"\nSearching memory for: [cyan]{query_str}[/cyan]")
    console.print(f"Found: [yellow]{len(result.concepts)}[/yellow] concepts")
    console.print(f"Query time: {result.metadata.execution_time_ms:.2f}ms\n")

    # Format output
    if format == "json":
        output_text = result.model_dump_json(indent=2)
    else:
        output_text = _format_unified_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Results written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {len(result.concepts)}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}\n")
    else:
        console.print(output_text)


@memory_app.command("list")
def list_memory(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (markdown, json, or table)"),
    ] = "table",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    graph_path: Annotated[
        Path | None,
        typer.Option("--graph", "-g", help="Unified graph path"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir",
            "-m",
            help="[DEPRECATED] Use --graph instead",
            hidden=True,
        ),
    ] = None,
) -> None:
    """List all memory concepts.

    Shows all memory concepts (patterns, calibrations, sessions)
    from the unified graph for inspection and debugging.

    Examples:
        # Show summary table
        $ raise memory list

        # Export as JSON
        $ raise memory list --format json --output memory.json

        # Export as Markdown
        $ raise memory list --format markdown --output memory.md
    """
    # Handle deprecated option
    if memory_dir is not None:
        warnings.warn(
            "--memory-dir is deprecated, use --graph instead",
            DeprecationWarning,
            stacklevel=2,
        )

    # Resolve graph path
    unified_path = graph_path or _get_default_graph_path()
    if not unified_path.exists():
        cli_error(
            f"Unified graph not found: {unified_path}",
            hint="Run 'raise graph build --unified' to create the graph first",
            exit_code=4,
        )

    # Load unified graph
    try:
        graph = UnifiedGraph.load(unified_path)
    except Exception as e:
        cli_error(f"Error loading unified graph: {e}")

    # Filter to memory types only
    memory_concepts = [
        c for c in graph.iter_concepts() if c.type in MEMORY_TYPES
    ]

    console.print(f"\nMemory Concepts from: [cyan]{unified_path}[/cyan]")
    console.print(f"Concepts: [yellow]{len(memory_concepts)}[/yellow]\n")

    # Format output
    if format == "json":
        import json

        output_text = json.dumps(
            [c.model_dump(mode="json") for c in memory_concepts],
            indent=2,
        )
    elif format == "markdown":
        output_text = _format_concepts_markdown(memory_concepts)
    else:  # table
        _print_concepts_table(memory_concepts)
        if output:
            # For file output in table mode, use markdown
            output_text = _format_concepts_markdown(memory_concepts)
        else:
            return

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Memory dump written to [cyan]{output}[/cyan]\n")
    elif format != "table":
        console.print(output_text)


def _format_unified_markdown(result: UnifiedQueryResult) -> str:
    """Format unified query result as markdown."""

    lines = ["# Memory Query Results\n"]
    lines.append(f"**Concepts:** {len(result.concepts)}")
    lines.append(f"**Tokens:** ~{result.metadata.token_estimate}")
    lines.append(f"**Query time:** {result.metadata.execution_time_ms:.2f}ms\n")

    if result.concepts:
        lines.append("## Concepts\n")
        for concept in result.concepts:
            lines.append(f"### {concept.id} ({concept.type})")
            lines.append(f"\n{concept.content}\n")
            if concept.source_file:
                lines.append(f"**Source:** {concept.source_file}")
            lines.append(f"**Created:** {concept.created}\n")

    return "\n".join(lines)


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


# --- Append Commands ---


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
            "--type", "-t", help="Pattern type (codebase, process, architecture, technical)"
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
        console.print("\n[dim]Graph will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@memory_app.command("add-calibration")
def add_calibration_cmd(
    feature: Annotated[str, typer.Argument(help="Feature ID (e.g., F3.5)")],
    name: Annotated[str, typer.Argument(help="Feature name")],
    size: Annotated[str, typer.Argument(help="T-shirt size (XS, S, M, L, XL)")],
    actual: Annotated[int, typer.Argument(help="Actual minutes")],
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
        $ raise memory add-calibration F3.5 "Skills Integration" XS 20

        # With estimate for velocity calculation
        $ raise memory add-calibration F3.5 "Skills Integration" XS 20 -e 60

        # Full details
        $ raise memory add-calibration F3.5 "Skills Integration" XS 20 -e 60 --sp 2 -n "Hook-assisted workflow"
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
        console.print("\n[dim]Graph will rebuild on next query.[/dim]\n")
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
        console.print("\n[dim]Graph will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)
