"""Formatters for graph CLI command output.

Moved from cli/commands/graph.py (S370.5a) to consolidate formatting
logic in the output/formatters/ layer.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from raise_cli.context.diff import GraphDiff
from raise_core.graph.models import GraphNode
from raise_core.graph.query import ArchitecturalContext, QueryResult

console = Console()


# =============================================================================
# Query result formatters
# =============================================================================


def format_markdown(result: QueryResult) -> str:
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


def format_compact(result: QueryResult) -> str:
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


def sanitize_pipe(value: str) -> str:
    """Replace pipe characters in value to preserve agent format field boundaries."""
    return value.replace("|", "¦")


def format_agent(result: QueryResult) -> str:
    """Format query result as pipe-delimited lines for agent consumption.

    One line per concept: type|id|content (no truncation, no markdown).
    Empty string when no results. Pipes in content replaced with ¦.
    """
    if not result.concepts:
        return ""
    lines: list[str] = []
    for concept in result.concepts:
        lines.append(f"{concept.type}|{concept.id}|{sanitize_pipe(concept.content)}")
    return "\n".join(lines)


def format_json(result: QueryResult) -> str:
    """Format query result as JSON."""
    return result.to_json()


# =============================================================================
# Architectural context formatters
# =============================================================================


def format_context_agent(ctx: ArchitecturalContext) -> str:
    """Format architectural context as pipe-delimited lines for agent consumption."""
    lines: list[str] = []
    lines.append(f"module|{ctx.module.id}|{sanitize_pipe(ctx.module.content)}")

    if ctx.domain:
        lines.append(f"domain|{ctx.domain.id}|{sanitize_pipe(ctx.domain.content)}")

    if ctx.layer:
        lines.append(f"layer|{ctx.layer.id}|{sanitize_pipe(ctx.layer.content)}")

    if ctx.constraints:
        # Classify by ID convention (more robust than content string matching)
        must = [c for c in ctx.constraints if "-must-" in c.id]
        should = [c for c in ctx.constraints if "-should-" in c.id]
        if must:
            lines.append(f"must|{','.join(c.id for c in must)}")
        if should:
            lines.append(f"should|{','.join(c.id for c in should)}")

    if ctx.dependencies:
        lines.append(f"dependencies|{','.join(d.id for d in ctx.dependencies)}")

    return "\n".join(lines)


def format_context_json(ctx: ArchitecturalContext) -> str:
    """Format architectural context as JSON."""
    return ctx.model_dump_json(indent=2)


def print_context_human(ctx: ArchitecturalContext) -> None:
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
# Build result formatter
# =============================================================================


def format_build_result(
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


# =============================================================================
# Concept list formatters
# =============================================================================


def format_concepts_agent(concepts: list[GraphNode]) -> str:
    """Format concepts as type|count summary for agent consumption."""
    if not concepts:
        return ""
    by_type: dict[str, int] = {}
    for c in concepts:
        by_type[c.type] = by_type.get(c.type, 0) + 1
    return "\n".join(
        f"{t}|{n}" for t, n in sorted(by_type.items(), key=lambda x: -x[1])
    )


def format_concepts_markdown(concepts: list[GraphNode]) -> str:
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


def print_concepts_table(concepts: list[GraphNode]) -> None:
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
