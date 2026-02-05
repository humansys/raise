"""Formatters for graph command results.

Provides format-aware output for graph build and validation results.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

# Module-level console for output
_console = Console()


def format_unified_build_result(
    output_path: Path,
    node_counts: dict[str, int],
    edge_counts: dict[str, int],
    total_nodes: int,
    total_edges: int,
) -> None:
    """Format and print unified graph build results.

    Args:
        output_path: Path where graph was saved.
        node_counts: Node counts by type.
        edge_counts: Edge counts by type.
        total_nodes: Total number of nodes.
        total_edges: Total number of edges.
    """
    _console.print("\n[cyan]Building unified context graph...[/cyan]")

    # Display node counts
    _console.print("\n[bold]Nodes by type:[/bold]")
    for node_type, count in sorted(node_counts.items()):
        _console.print(f"  {node_type}: [green]{count}[/green]")

    _console.print(f"\n[bold]Total nodes:[/bold] [green]{total_nodes}[/green]")

    # Display edge counts
    if edge_counts:
        _console.print("\n[bold]Edges by type:[/bold]")
        for edge_type, count in sorted(edge_counts.items()):
            _console.print(f"  {edge_type}: [green]{count}[/green]")

    _console.print(f"\n[bold]Total edges:[/bold] [green]{total_edges}[/green]")

    _console.print(f"\n✓ Saved to [cyan]{output_path}[/cyan]\n")


def format_governance_build_result(
    concepts_path: Path,
    output_path: Path,
    concepts_loaded: int,
    edge_counts: dict[str, int],
    total_nodes: int,
    total_edges: int,
    from_cache: bool,
) -> None:
    """Format and print governance graph build results.

    Args:
        concepts_path: Path to concepts file.
        output_path: Path where graph was saved.
        concepts_loaded: Number of concepts loaded.
        edge_counts: Edge counts by type.
        total_nodes: Total number of nodes.
        total_edges: Total number of edges.
        from_cache: Whether concepts were loaded from cache.
    """
    if from_cache:
        _console.print(f"\nLoading concepts from [cyan]{concepts_path}[/cyan]...")
    else:
        _console.print("\nNo cached concepts found. Extracting from governance files...")

    _console.print(f"  ✓ Loaded [green]{concepts_loaded}[/green] concepts")

    # Build graph
    _console.print("\nBuilding concept graph...")
    _console.print(f"  ✓ Inferred [green]{total_edges}[/green] relationships")
    for edge_type, count in edge_counts.items():
        _console.print(f"    - {edge_type}: {count}")

    # Save graph
    _console.print(f"  ✓ Saved to [cyan]{output_path}[/cyan]")
    _console.print(
        f"\nGraph: [green]{total_nodes}[/green] nodes, "
        f"[green]{total_edges}[/green] edges\n"
    )
