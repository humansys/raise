"""CLI commands for concept graph operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.context import UnifiedGraph, UnifiedGraphBuilder
from raise_cli.governance import ConceptType, GovernanceExtractor
from raise_cli.output.formatters.graph import format_unified_build_result

graph_app = typer.Typer(
    name="graph",
    help="Concept graph operations (extract, build, query)",
    no_args_is_help=True,
)

console = Console()


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
    - governance/projects/*/prd.md (requirements)
    - governance/solution/vision.md (outcomes)
    - framework/reference/constitution.md (principles)

    Examples:
        # Extract from all governance files
        $ raise graph extract

        # Extract from specific file
        $ raise graph extract governance/projects/raise-cli/prd.md

        # Output as JSON
        $ raise graph extract --format json
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


@graph_app.command()
def build(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save graph JSON"),
    ] = None,
) -> None:
    """Build unified context graph from all sources.

    Merges all context sources into a single queryable graph:
    - Governance documents (constitution, PRD, vision)
    - Memory (patterns, calibration, sessions)
    - Work tracking (epics, features)
    - Skills (SKILL.md metadata)
    - Components (from discovery)

    Examples:
        # Build graph to default location
        $ raise graph build

        # Save to custom location
        $ raise graph build --output my_graph.json
    """
    default_output = Path(".raise/graph/unified.json")
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
    format_unified_build_result(
        output_path=output_path,
        node_counts=node_counts,
        edge_counts=edge_counts,
        total_nodes=graph.node_count,
        total_edges=graph.edge_count,
    )


@graph_app.command()
def validate(
    graph_file: Annotated[
        Path | None,
        typer.Option("--graph", "-g", help="Path to graph JSON file"),
    ] = None,
) -> None:
    """Validate graph structure and relationships.

    Checks for:
    - Cycles in depends_on relationships
    - Valid relationship types
    - All edge targets exist as nodes

    Examples:
        # Validate default graph
        $ raise graph validate

        # Validate specific graph file
        $ raise graph validate --graph my_graph.json
    """
    default_graph = Path(".raise/graph/unified.json")
    graph_path = graph_file or default_graph

    if not graph_path.exists():
        cli_error(
            f"Graph file not found: {graph_path}",
            hint="Run 'raise graph build' first to create a graph",
            exit_code=4,
        )

    console.print(f"\nLoading graph from [cyan]{graph_path}[/cyan]...")
    graph = UnifiedGraph.load(graph_path)
    console.print(
        f"  ✓ Loaded graph with {graph.node_count} nodes, {graph.edge_count} edges"
    )

    console.print("\nValidating graph...")

    # Build node set for validation
    node_ids = {node.id for node in graph.iter_concepts()}

    # Check 1: All edge targets exist as nodes
    valid_edges = True
    edges_list = list(graph.iter_relationships())
    for edge in edges_list:
        if edge.source not in node_ids:
            console.print(
                f"  [red]✗[/red] Invalid edge: source '{edge.source}' not in graph"
            )
            valid_edges = False
        if edge.target not in node_ids:
            console.print(
                f"  [red]✗[/red] Invalid edge: target '{edge.target}' not in graph"
            )
            valid_edges = False

    if valid_edges:
        console.print("  ✓ All relationships valid")

    # Check 2: Detect cycles in depends_on relationships
    depends_edges = [e for e in edges_list if e.type == "depends_on"]
    if depends_edges:
        cycles = _detect_cycles_unified(graph, depends_edges)
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

    console.print("\n[green]Graph is valid.[/green]\n")


def _detect_cycles_unified(
    graph: UnifiedGraph, edges: list
) -> list[list[str]]:
    """Detect cycles in a set of edges using DFS.

    Args:
        graph: Unified graph.
        edges: List of ConceptEdge to check for cycles.

    Returns:
        List of cycles (each cycle is a list of node IDs).
    """
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
