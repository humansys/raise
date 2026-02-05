"""CLI commands for context queries.

Queries the unified context graph which includes all sources:
- Governance (principles, requirements, terms)
- Memory (patterns, calibration, sessions)
- Skills (workflow metadata)
- Work (epics, features, decisions)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.context.models import ConceptNode
from raise_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)

context_app = typer.Typer(
    name="context",
    help="Query the unified context graph",
    no_args_is_help=True,
)

console = Console()

# Unified graph path
UNIFIED_GRAPH_PATH = Path(".raise/graph/unified.json")


def _format_markdown(result: UnifiedQueryResult) -> str:
    """Format query result as markdown for human consumption."""
    lines: list[str] = []

    # Header
    lines.append("# Unified Context Results")
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


@context_app.command()
def query(
    query_str: Annotated[
        str, typer.Argument(help="Query string (keywords or concept ID)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (markdown or json)"),
    ] = "markdown",
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
            help="Filter by node types (comma-separated: pattern,calibration,skill,principle,requirement,epic,feature)",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of results"),
    ] = 10,
) -> None:
    """Query the unified context graph.

    The unified graph includes all context sources:
    - Governance (principles, requirements, terms)
    - Memory (patterns, calibration, sessions)
    - Skills (workflow metadata)
    - Work (epics, features, decisions)

    Examples:
        # Search by keywords
        $ raise context query "planning estimation"

        # Filter by types
        $ raise context query "pattern" --types pattern,calibration

        # Lookup specific concept by ID
        $ raise context query "PAT-001" --strategy concept_lookup

        # Output as JSON
        $ raise context query "velocity" --format json
    """
    # Load engine
    try:
        engine = UnifiedQueryEngine.from_file(UNIFIED_GRAPH_PATH)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'raise graph build' first to create the graph",
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

    console.print(f"\nQuerying unified context graph for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(unified_query)

    # Format output
    output_text = _format_json(result) if format == "json" else _format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Context written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)
