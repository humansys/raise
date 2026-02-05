"""CLI commands for MVC context queries."""

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
from raise_cli.governance.query import ContextQuery, ContextQueryEngine, QueryStrategy
from raise_cli.governance.query.formatters import format_json, format_markdown

context_app = typer.Typer(
    name="context",
    help="Query concept graph for Minimum Viable Context (MVC)",
    no_args_is_help=True,
)

console = Console()

# Default unified graph path
UNIFIED_GRAPH_PATH = Path(".raise/graph/unified.json")


def format_unified_markdown(result: UnifiedQueryResult) -> str:
    """Format UnifiedQueryResult as markdown for human consumption.

    Args:
        result: Unified query result to format.

    Returns:
        Formatted markdown string.
    """
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


def format_unified_json(result: UnifiedQueryResult) -> str:
    """Format UnifiedQueryResult as JSON.

    Args:
        result: Unified query result to format.

    Returns:
        JSON string representation.
    """
    return result.to_json()


@context_app.command()
def query(
    query_str: Annotated[
        str, typer.Argument(help="Query string (concept ID or keywords)")
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
            help="Query strategy (concept_lookup, keyword_search, relationship_traversal, related_concepts)",
        ),
    ] = None,
    max_depth: Annotated[
        int,
        typer.Option("--max-depth", "-d", help="Maximum graph traversal depth (0-5)"),
    ] = 1,
    edge_types: Annotated[
        str | None,
        typer.Option(
            "--edge-types",
            "-e",
            help="Edge types to follow (comma-separated: governed_by,implements)",
        ),
    ] = None,
    concept_type: Annotated[
        str | None,
        typer.Option(
            "--type", "-t", help="Filter by concept type (requirement, principle, etc.)"
        ),
    ] = None,
    unified: Annotated[
        bool,
        typer.Option(
            "--unified",
            "-u",
            help="Query unified context graph (includes memory, work, skills)",
        ),
    ] = False,
    types: Annotated[
        str | None,
        typer.Option(
            "--types",
            help="Filter by node types for unified query (comma-separated: pattern,calibration,skill)",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of results (unified only)"),
    ] = 10,
) -> None:
    """Query concept graph for Minimum Viable Context.

    Retrieves relevant concepts from the concept graph based on the query,
    reducing token usage by >90% vs loading full files.

    Use --unified to query the unified context graph which includes:
    - Patterns (learned from sessions)
    - Calibration (velocity data)
    - Skills (workflow metadata)
    - Governance (principles, requirements)
    - Work (epics, features)

    Examples:
        # Query governance graph by concept ID
        $ raise context query "req-rf-05"

        # Query unified graph for planning context
        $ raise context query "planning estimation" --unified

        # Filter unified by types
        $ raise context query "pattern" --unified --types pattern,calibration

        # Keyword search in requirements only
        $ raise context query "validation" --type requirement

        # Output as JSON
        $ raise context query "req-rf-05" --format json
    """
    if unified:
        _query_unified(
            query_str=query_str,
            format=format,
            output=output,
            strategy=strategy,
            max_depth=max_depth,
            types=types,
            limit=limit,
            concept_type=concept_type,
        )
    else:
        _query_governance(
            query_str=query_str,
            format=format,
            output=output,
            strategy=strategy,
            max_depth=max_depth,
            edge_types=edge_types,
            concept_type=concept_type,
        )


def _query_unified(
    query_str: str,
    format: str,
    output: Path | None,
    strategy: str | None,
    max_depth: int,
    types: str | None,
    limit: int,
    concept_type: str | None = None,
) -> None:
    """Execute query against unified context graph."""
    # Load engine
    try:
        engine = UnifiedQueryEngine.from_file(UNIFIED_GRAPH_PATH)
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'raise graph build --unified' first to create the graph",
            exit_code=4,
        )

    # Parse types filter (--types takes precedence, --type as fallback)
    types_list: list[str] | None = None
    if types:
        types_list = [t.strip() for t in types.split(",")]
    elif concept_type:
        types_list = [concept_type]

    # Determine strategy
    query_strategy = UnifiedQueryStrategy.KEYWORD_SEARCH  # Default
    if strategy:
        try:
            query_strategy = UnifiedQueryStrategy(strategy)
        except ValueError:
            cli_error(
                f"Invalid strategy: {strategy}",
                hint="Valid strategies for unified: keyword_search, concept_lookup",
                exit_code=7,
            )

    # Build query
    unified_query = UnifiedQuery(
        query=query_str,
        strategy=query_strategy,
        max_depth=max_depth,
        types=types_list,  # type: ignore[arg-type]
        limit=limit,
    )

    # Execute query
    console.print(f"\nQuerying unified context graph for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(unified_query)

    # Format output
    if format == "json":
        output_text = format_unified_json(result)
    else:
        output_text = format_unified_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ Context written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)


def _query_governance(
    query_str: str,
    format: str,
    output: Path | None,
    strategy: str | None,
    max_depth: int,
    edge_types: str | None,
    concept_type: str | None,
) -> None:
    """Execute query against governance concept graph."""
    # Load graph
    try:
        engine = ContextQueryEngine.from_cache()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'raise graph build' first to create the graph",
            exit_code=4,
        )

    # Build query
    filters: dict[str, list[str] | str] = {}

    if edge_types:
        filters["edge_types"] = [et.strip() for et in edge_types.split(",")]

    if concept_type:
        filters["type"] = concept_type

    # Determine strategy
    query_strategy = QueryStrategy.CONCEPT_LOOKUP  # Default
    if strategy:
        try:
            query_strategy = QueryStrategy(strategy)
        except ValueError:
            cli_error(
                f"Invalid strategy: {strategy}",
                hint="Valid strategies: concept_lookup, keyword_search, relationship_traversal, related_concepts",
                exit_code=7,
            )

    mvc_query = ContextQuery(
        query=query_str,
        strategy=query_strategy,
        max_depth=max_depth,
        filters=filters,
    )

    # Execute query
    console.print(f"\nQuerying concept graph for: [cyan]{query_str}[/cyan]")
    console.print(f"Strategy: [yellow]{query_strategy.value}[/yellow]\n")

    result = engine.query(mvc_query)

    # Format output
    output_text = format_json(result) if format == "json" else format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ MVC written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)
