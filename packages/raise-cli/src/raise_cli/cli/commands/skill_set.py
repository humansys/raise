"""CLI commands for skill set management.

Provides ``rai skill set create|list|diff`` for observable skill set
operations. These commands are the foundation for ``/rai-skillset-manage``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.output.symbols import CHECK, CROSS
from raise_cli.skills.skillsets import (
    create_skill_set,
    diff_skill_set,
    list_skill_sets,
)

skill_set_app = typer.Typer(
    name="set",
    help="Manage skill sets",
    no_args_is_help=True,
)

console = Console()


@skill_set_app.command("create")
def create_command(
    name: Annotated[
        str,
        typer.Argument(help="Skill set name (e.g., 'my-team')."),
    ],
    empty: Annotated[
        bool,
        typer.Option("--empty", help="Create empty set (no builtins copied)."),
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """Create a new skill set from builtins.

    Copies all builtin skills to .raise/skills/<name>/ as a starting
    base for customization. Use --empty for a blank set.
    """
    project_root = Path.cwd()
    result = create_skill_set(name, project_root, empty=empty)

    if format == "json":
        print(result.model_dump_json(indent=2))
    elif result.created:
        console.print(
            f"[green]{CHECK}[/green] Skill set '{name}' created at {result.path}"
        )
        console.print(f"  {result.skill_count} skills copied from builtins")
        console.print("\n  Next: customize skills, then deploy with:")
        console.print(f"  [bold]rai init --skill-set {name}[/bold]")
    else:
        console.print(f"[red]{CROSS}[/red] {result.error}")
        raise typer.Exit(code=1)


@skill_set_app.command("list")
def list_command(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """List all skill sets in .raise/skills/."""
    project_root = Path.cwd()
    sets = list_skill_sets(project_root)

    if format == "json":
        print(json.dumps([s.model_dump() for s in sets], indent=2))
        return

    if not sets:
        console.print("No skill sets found in .raise/skills/")
        console.print("  Create one with: [bold]rai skill set create <name>[/bold]")
        return

    table = Table(title="Skill Sets")
    table.add_column("Name", style="bold")
    table.add_column("Skills", justify="right")
    table.add_column("Path")

    for s in sets:
        table.add_row(s.name, str(s.skill_count), s.path)

    console.print(table)


@skill_set_app.command("diff")
def diff_command(
    name: Annotated[
        str,
        typer.Argument(help="Skill set name to compare against builtins."),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """Compare a skill set against builtins.

    Shows which skills are added, modified, or unchanged relative
    to the builtin skill set.
    """
    project_root = Path.cwd()
    diff = diff_skill_set(name, project_root)

    if diff is None:
        console.print(f"[red]{CROSS}[/red] Skill set '{name}' not found")
        raise typer.Exit(code=1)

    if format == "json":
        print(diff.model_dump_json(indent=2))
        return

    console.print(f"[bold]Skill set:[/bold] {name}\n")

    if diff.added:
        console.print(f"[green]Added ({len(diff.added)}):[/green]")
        for s in diff.added:
            console.print(f"  + {s}")

    if diff.modified:
        console.print(f"[yellow]Modified ({len(diff.modified)}):[/yellow]")
        for s in diff.modified:
            console.print(f"  ~ {s}")

    if diff.unchanged:
        console.print(f"[dim]Unchanged ({len(diff.unchanged)}):[/dim]")
        for s in diff.unchanged:
            console.print(f"  = {s}")

    total = len(diff.added) + len(diff.modified) + len(diff.unchanged)
    added, modified = len(diff.added), len(diff.modified)
    console.print(
        f"\n[bold]Total:[/bold] {total} skills ({added} added, {modified} modified)"
    )
