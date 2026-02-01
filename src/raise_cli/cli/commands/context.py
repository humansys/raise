"""CLI commands for MVC context queries."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.governance.query import ContextQuery, ContextQueryEngine, QueryStrategy
from raise_cli.governance.query.formatters import format_json, format_markdown

context_app = typer.Typer(
    name="context",
    help="Query concept graph for Minimum Viable Context (MVC)",
    no_args_is_help=True,
)

console = Console()


@context_app.command()
def query(
    query_str: Annotated[str, typer.Argument(help="Query string (concept ID or keywords)")],
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
        typer.Option("--strategy", "-s", help="Query strategy (concept_lookup, keyword_search, relationship_traversal, related_concepts)"),
    ] = None,
    max_depth: Annotated[
        int,
        typer.Option("--max-depth", "-d", help="Maximum graph traversal depth (0-5)"),
    ] = 1,
    edge_types: Annotated[
        str | None,
        typer.Option("--edge-types", "-e", help="Edge types to follow (comma-separated: governed_by,implements)"),
    ] = None,
    concept_type: Annotated[
        str | None,
        typer.Option("--type", "-t", help="Filter by concept type (requirement, principle, outcome)"),
    ] = None,
) -> None:
    """Query concept graph for Minimum Viable Context.

    Retrieves relevant governance concepts from the concept graph based
    on the query, reducing token usage by >90% vs loading full files.

    Examples:
        # Query by concept ID
        $ raise context query "req-rf-05"

        # Keyword search in requirements only
        $ raise context query "validation" --type requirement

        # Traverse relationships
        $ raise context query "req-rf-05" --strategy relationship_traversal --edge-types governed_by

        # Save to file
        $ raise context query "req-rf-05" --output context.md

        # Output as JSON
        $ raise context query "req-rf-05" --format json
    """
    # Load graph
    try:
        engine = ContextQueryEngine.from_cache()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\nRun [cyan]raise graph build[/cyan] first to create the graph.")
        raise typer.Exit(1)

    # Build query
    filters = {}

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
            console.print(f"[red]Error:[/red] Invalid strategy: {strategy}")
            console.print("Valid strategies: concept_lookup, keyword_search, relationship_traversal, related_concepts")
            raise typer.Exit(1)

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
    if format == "json":
        output_text = format_json(result)
    else:
        output_text = format_markdown(result)

    # Write to file or stdout
    if output:
        output.write_text(output_text)
        console.print(f"✓ MVC written to [cyan]{output}[/cyan]")
        console.print(f"  Concepts: {result.metadata.total_concepts}")
        console.print(f"  Tokens: ~{result.metadata.token_estimate}")
        console.print(f"  Execution: {result.metadata.execution_time_ms:.2f}ms\n")
    else:
        console.print(output_text)
