"""CLI commands for concept graph operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.governance import ConceptType, GovernanceExtractor
from raise_cli.governance.graph import ConceptGraph
from raise_cli.governance.graph.builder import GraphBuilder

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
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            raise typer.Exit(1)

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
    concepts: Annotated[
        Path | None,
        typer.Option("--concepts", "-c", help="Path to concepts JSON file"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save graph JSON"),
    ] = None,
    unified: Annotated[
        bool,
        typer.Option(
            "--unified", "-u", help="Build unified context graph (merges all sources)"
        ),
    ] = False,
) -> None:
    """Build concept graph from extracted concepts.

    Loads concepts (from file or extraction), infers relationships, and
    saves the resulting graph.

    With --unified flag, builds a unified context graph that merges:
    - Governance documents (constitution, PRD, vision)
    - Memory (patterns, calibration, sessions)
    - Work tracking (epics, features)
    - Skills (SKILL.md metadata)

    Examples:
        # Build graph from default location
        $ raise graph build

        # Build from custom concepts file
        $ raise graph build --concepts my_concepts.json

        # Save to custom location
        $ raise graph build --output my_graph.json

        # Build unified context graph
        $ raise graph build --unified
    """
    if unified:
        _build_unified_graph(output)
        return
    # Default paths
    default_concepts = Path(".raise/cache/concepts.json")
    default_output = Path(".raise/cache/graph.json")

    concepts_path = concepts or default_concepts
    output_path = output or default_output

    # Load concepts
    if concepts_path.exists():
        console.print(f"\nLoading concepts from [cyan]{concepts_path}[/cyan]...")
        with concepts_path.open() as f:
            data = json.load(f)
            concept_data = data.get("concepts", [])

        # Reconstruct Concept objects
        from raise_cli.governance.models import Concept

        loaded_concepts = [
            Concept(
                id=c["id"],
                type=ConceptType(c["type"]),
                file=c["file"],
                section=c["section"],
                lines=tuple(c["lines"]),
                content=c["content"],
                metadata=c.get("metadata", {}),
            )
            for c in concept_data
        ]
    else:
        # Extract fresh
        console.print("\nNo cached concepts found. Extracting from governance files...")
        extractor = GovernanceExtractor()
        result = extractor.extract_with_result()
        loaded_concepts = result.concepts

        # Save concepts for future use
        concepts_path.parent.mkdir(parents=True, exist_ok=True)
        concepts_output = {
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
                for c in loaded_concepts
            ],
            "total": len(loaded_concepts),
        }
        with concepts_path.open("w") as f:
            json.dump(concepts_output, f, indent=2)

    console.print(f"  ✓ Loaded [green]{len(loaded_concepts)}[/green] concepts")

    # Build graph
    console.print("\nBuilding concept graph...")
    builder = GraphBuilder()
    graph = builder.build(loaded_concepts)

    # Display statistics
    stats = graph.metadata.get("stats", {})
    edge_counts = stats.get("edges_by_type", {})

    console.print(f"  ✓ Inferred [green]{len(graph.edges)}[/green] relationships")
    for edge_type, count in edge_counts.items():
        console.print(f"    - {edge_type}: {count}")

    # Save graph
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        f.write(graph.to_json())

    console.print(f"  ✓ Saved to [cyan]{output_path}[/cyan]")
    console.print(
        f"\nGraph: [green]{len(graph.nodes)}[/green] nodes, [green]{len(graph.edges)}[/green] edges\n"
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
    default_graph = Path(".raise/cache/graph.json")
    graph_path = graph_file or default_graph

    if not graph_path.exists():
        console.print(f"[red]Error:[/red] Graph file not found: {graph_path}")
        console.print("\nRun [cyan]raise graph build[/cyan] first to create a graph.")
        raise typer.Exit(1)

    console.print(f"\nLoading graph from [cyan]{graph_path}[/cyan]...")
    with graph_path.open() as f:
        json_str = f.read()

    graph = ConceptGraph.from_json(json_str)
    console.print(
        f"  ✓ Loaded graph with {len(graph.nodes)} nodes, {len(graph.edges)} edges"
    )

    console.print("\nValidating graph...")

    # Check 1: All edge targets exist as nodes
    valid_edges = True
    for edge in graph.edges:
        if edge.source not in graph.nodes:
            console.print(
                f"  [red]✗[/red] Invalid edge: source '{edge.source}' not in graph"
            )
            valid_edges = False
        if edge.target not in graph.nodes:
            console.print(
                f"  [red]✗[/red] Invalid edge: target '{edge.target}' not in graph"
            )
            valid_edges = False

    if valid_edges:
        console.print("  ✓ All relationships valid")

    # Check 2: Detect cycles in depends_on relationships
    depends_edges = [e for e in graph.edges if e.type == "depends_on"]
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
    console.print(f"  ✓ {len(graph.nodes)}/{len(graph.nodes)} concepts reachable")

    console.print("\n[green]Graph is valid.[/green]\n")


def _detect_cycles(graph: ConceptGraph, edges: list) -> list[list[str]]:
    """Detect cycles in a set of edges using DFS.

    Args:
        graph: Concept graph.
        edges: List of edges to check for cycles.

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

    for node in graph.nodes:
        if node not in visited and node in adj:
            dfs(node, [])

    return cycles


def _build_unified_graph(output: Path | None) -> None:
    """Build unified context graph from all sources.

    Args:
        output: Optional custom output path.
    """
    from raise_cli.context import UnifiedGraphBuilder

    default_output = Path(".raise/graph/unified.json")
    output_path = output or default_output

    console.print("\n[cyan]Building unified context graph...[/cyan]")

    # Build unified graph
    builder = UnifiedGraphBuilder()
    graph = builder.build()

    # Count nodes by type
    node_counts: dict[str, int] = {}
    for node in graph.iter_concepts():
        node_type = node.type
        node_counts[node_type] = node_counts.get(node_type, 0) + 1

    # Count edges by type
    edge_counts: dict[str, int] = {}
    for edge in graph.iter_relationships():
        edge_type = edge.type
        edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

    # Display node counts
    console.print("\n[bold]Nodes by type:[/bold]")
    for node_type, count in sorted(node_counts.items()):
        console.print(f"  {node_type}: [green]{count}[/green]")

    console.print(f"\n[bold]Total nodes:[/bold] [green]{graph.node_count}[/green]")

    # Display edge counts
    if edge_counts:
        console.print("\n[bold]Edges by type:[/bold]")
        for edge_type, count in sorted(edge_counts.items()):
            console.print(f"  {edge_type}: [green]{count}[/green]")

    console.print(f"\n[bold]Total edges:[/bold] [green]{graph.edge_count}[/green]")

    # Save graph
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.save(output_path)

    console.print(f"\n✓ Saved to [cyan]{output_path}[/cyan]\n")
