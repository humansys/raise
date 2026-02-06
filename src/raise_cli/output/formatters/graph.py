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
