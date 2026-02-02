"""CLI commands for memory queries."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.memory import MemoryCache, MemoryGraph, MemoryQuery, MemoryQueryResult

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
