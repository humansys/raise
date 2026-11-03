"""CLI commands for schema integrity management."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from raise_cli.storage.schema_sum import SUM_FILE, verify_sum_file, write_sum_file

schema_app = typer.Typer(name="schema", help="Schema integrity tools.")
sum_app = typer.Typer(help="Manage schema.sum integrity file.")
schema_app.add_typer(sum_app, name="sum")

__all__ = ["schema_app"]

_SumPath = Annotated[Path, typer.Option("--path", "-p", help="Path to schema.sum")]


@sum_app.command("update")
def update(path: _SumPath = SUM_FILE) -> None:
    """Generate or update .raise/schema.sum with current migration hashes."""
    write_sum_file(path)
    typer.echo(f"✓ schema.sum updated → {path}")


@sum_app.command("check")
def check(path: _SumPath = SUM_FILE) -> None:
    """Verify schema.sum matches current schema.py migrations.

    Exits 0 if valid, 1 if stale, missing, or has merge conflict markers.
    """
    valid, msg = verify_sum_file(path)
    if valid:
        typer.echo(f"✓ {msg}")
    else:
        typer.echo(f"✗ {msg}", err=True)
        raise typer.Exit(1)
