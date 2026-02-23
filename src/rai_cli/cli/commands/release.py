"""Release CLI commands.

Provides commands for inspecting releases from the memory graph.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rai_cli.cli.error_handler import cli_error
from rai_cli.graph.filesystem_backend import get_active_backend

release_app = typer.Typer(help="Release management commands")
console = Console()

# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"


@release_app.command("list")
def list_releases(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """List releases from the memory graph.

    Shows all release nodes with their status, target date, and associated epics.

    Examples:
        $ rai release list
        $ rai release list --project /path/to/project
    """
    graph_path = project / GRAPH_REL_PATH
    if not graph_path.exists():
        cli_error(
            f"Memory index not found: {graph_path}",
            hint="Run 'rai memory build' first to create the index",
            exit_code=4,
        )

    try:
        graph = get_active_backend(graph_path).load()
    except Exception as e:
        cli_error(f"Error loading memory index: {e}")

    # Find all release nodes
    releases = [n for n in graph.iter_concepts() if n.type == "release"]

    if not releases:
        console.print("\nNo release nodes found in graph.")
        return

    # Find epics linked to each release via part_of edges
    release_epics: dict[str, list[str]] = {}
    for node in graph.iter_concepts():
        if node.type == "epic":
            neighbors = graph.get_neighbors(node.id, depth=1, edge_types=["part_of"])
            for neighbor in neighbors:
                if neighbor.type == "release":
                    release_epics.setdefault(neighbor.id, []).append(
                        node.id.replace("epic-", "").upper()
                    )

    # Build table
    table = Table(title="Releases")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status", style="yellow")
    table.add_column("Target", style="green")
    table.add_column("Epics", style="dim")

    for rel in sorted(releases, key=lambda r: r.metadata.get("target", "")):
        release_id = rel.metadata.get("release_id", rel.id)
        name = rel.metadata.get("name", "")
        status = rel.metadata.get("status", "")
        target = rel.metadata.get("target", "")
        epics = ", ".join(sorted(release_epics.get(rel.id, [])))

        table.add_row(release_id, name, status, target, epics)

    console.print()
    console.print(table)
