"""CLI commands for memory queries and writes."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.memory import (
    CalibrationInput,
    MemoryCache,
    MemoryGraph,
    MemoryQuery,
    MemoryQueryResult,
    PatternInput,
    PatternSubType,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
)

memory_app = typer.Typer(
    name="memory",
    help="Query Rai's memory graph for relevant concepts",
    no_args_is_help=True,
)

console = Console()


def _get_default_memory_dir() -> Path:
    """Get default memory directory (.rai/memory)."""
    return Path(".rai/memory")


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
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Query memory graph for relevant concepts.

    Searches Rai's memory (patterns, calibrations, sessions) using
    keyword matching, BFS traversal, and recency weighting.

    Examples:
        # Simple keyword search
        $ raise memory query "testing patterns"

        # Limit results
        $ raise memory query "velocity" --max-results 5

        # Disable traversal expansion
        $ raise memory query "singleton" --no-expand

        # Output as JSON
        $ raise memory query "calibration" --format json

        # Save to file
        $ raise memory query "architecture" --output context.md
    """
    # Resolve memory directory
    mem_dir = memory_dir or _get_default_memory_dir()
    if not mem_dir.exists():
        console.print(f"[red]Error:[/red] Memory directory not found: {mem_dir}")
        console.print("\nEnsure .rai/memory/ exists with JSONL files.")
        raise typer.Exit(1)

    # Load graph via cache
    try:
        cache = MemoryCache(mem_dir)
        graph = cache.get_graph()
    except Exception as e:
        console.print(f"[red]Error loading memory graph:[/red] {e}")
        raise typer.Exit(1) from None

    # Create query engine and search
    engine = MemoryQuery(graph)
    result = engine.search(
        query=query_str,
        max_results=min(max(1, max_results), 50),
        expand_traversal=expand,
        max_depth=min(max(1, max_depth), 3),
    )

    console.print(f"\nSearching memory for: [cyan]{query_str}[/cyan]")
    console.print(f"Found: [yellow]{len(result.concepts)}[/yellow] concepts")
    console.print(f"Query time: {result.query_time_ms:.2f}ms\n")

    # Format output
    if format == "json":
        output_text = result.model_dump_json(indent=2)
    else:
        output_text = _format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Results written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {len(result.concepts)}")
        console.print(f"  Tokens: ~{result.token_estimate}\n")
    else:
        console.print(output_text)


@memory_app.command()
def dump(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (markdown, json, or table)"),
    ] = "table",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Dump full memory graph for inspection.

    Shows all concepts and relationships in the memory graph,
    useful for debugging and verification.

    Examples:
        # Show summary table
        $ raise memory dump

        # Export as JSON
        $ raise memory dump --format json --output graph.json

        # Export as Markdown
        $ raise memory dump --format markdown --output memory.md
    """
    # Resolve memory directory
    mem_dir = memory_dir or _get_default_memory_dir()
    if not mem_dir.exists():
        console.print(f"[red]Error:[/red] Memory directory not found: {mem_dir}")
        console.print("\nEnsure .rai/memory/ exists with JSONL files.")
        raise typer.Exit(1)

    # Load graph via cache
    try:
        cache = MemoryCache(mem_dir)
        graph = cache.get_graph()
    except Exception as e:
        console.print(f"[red]Error loading memory graph:[/red] {e}")
        raise typer.Exit(1) from None

    console.print(f"\nMemory Graph: [cyan]{mem_dir}[/cyan]")
    console.print(f"Nodes: [yellow]{len(graph.nodes)}[/yellow]")
    console.print(f"Edges: [yellow]{len(graph.edges)}[/yellow]\n")

    # Format output
    if format == "json":
        output_text = graph.to_json()
    elif format == "markdown":
        output_text = _format_graph_markdown(graph)
    else:  # table
        _print_graph_table(graph)
        if output:
            # For file output in table mode, use markdown
            output_text = _format_graph_markdown(graph)
        else:
            return

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Graph written to [cyan]{output}[/cyan]\n")
    elif format != "table":
        console.print(output_text)


def _format_markdown(result: MemoryQueryResult) -> str:
    """Format query result as markdown."""

    lines = ["# Memory Query Results\n"]
    lines.append(f"**Concepts:** {len(result.concepts)}")
    lines.append(f"**Tokens:** ~{result.token_estimate}")
    lines.append(f"**Query time:** {result.query_time_ms:.2f}ms\n")

    if result.concepts:
        lines.append("## Concepts\n")
        for concept in result.concepts:
            lines.append(f"### {concept.id} ({concept.type.value})")
            lines.append(f"\n{concept.content}\n")
            if concept.context:
                lines.append(f"**Context:** {', '.join(concept.context)}")
            lines.append(f"**Created:** {concept.created}\n")

    if result.relationships:
        lines.append("## Relationships\n")
        for rel in result.relationships:
            lines.append(f"- {rel.source} --[{rel.type.value}]--> {rel.target}")

    return "\n".join(lines)


def _format_graph_markdown(graph: MemoryGraph) -> str:
    """Format full graph as markdown."""

    lines = ["# Memory Graph\n"]
    lines.append(f"**Nodes:** {len(graph.nodes)}")
    lines.append(f"**Edges:** {len(graph.edges)}\n")

    # Group by type
    by_type: dict[str, list[str]] = {}
    for concept in graph.nodes.values():
        type_name = concept.type.value
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(concept.id)

    lines.append("## Concepts by Type\n")
    for type_name, ids in sorted(by_type.items()):
        lines.append(f"### {type_name.title()} ({len(ids)})\n")
        for concept_id in sorted(ids):
            concept = graph.nodes[concept_id]
            lines.append(f"- **{concept_id}**: {concept.content[:60]}...")
        lines.append("")

    if graph.edges:
        lines.append("## Relationships\n")
        for edge in graph.edges:
            lines.append(f"- {edge.source} --[{edge.type.value}]--> {edge.target}")

    return "\n".join(lines)


def _print_graph_table(graph: MemoryGraph) -> None:
    """Print graph as rich table."""

    # Concepts table
    table = Table(title="Memory Concepts")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Content", max_width=50)
    table.add_column("Created")

    for concept in sorted(graph.nodes.values(), key=lambda c: c.id):
        content = (
            concept.content[:47] + "..."
            if len(concept.content) > 50
            else concept.content
        )
        table.add_row(
            concept.id,
            concept.type.value,
            content,
            str(concept.created),
        )

    console.print(table)

    # Edges summary
    if graph.edges:
        console.print(f"\n[dim]Relationships: {len(graph.edges)} edges[/dim]")


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
        console.print(f"[red]Error:[/red] Memory directory not found: {mem_dir}")
        raise typer.Exit(1)

    # Parse context
    context_list = [c.strip() for c in context.split(",") if c.strip()]

    # Parse sub_type
    try:
        pattern_type = PatternSubType(sub_type)
    except ValueError:
        console.print(f"[red]Error:[/red] Invalid pattern type: {sub_type}")
        console.print("Valid types: codebase, process, architecture, technical")
        raise typer.Exit(1) from None

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
        console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


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
        console.print(f"[red]Error:[/red] Memory directory not found: {mem_dir}")
        raise typer.Exit(1)

    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    if size.upper() not in valid_sizes:
        console.print(f"[red]Error:[/red] Invalid size: {size}")
        console.print(f"Valid sizes: {', '.join(valid_sizes)}")
        raise typer.Exit(1)

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
        console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


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
        console.print(f"[red]Error:[/red] Memory directory not found: {mem_dir}")
        raise typer.Exit(1)

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
        console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)
