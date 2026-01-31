"""Main CLI application entry point."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

import typer
from rich.console import Console

from raise_cli import __version__

app = typer.Typer(
    name="raise",
    help="RaiSE CLI - Reliable AI Software Engineering",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""

    human = "human"
    json = "json"
    table = "table"


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"raise-cli version {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
    format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format (human, json, table)",
        ),
    ] = OutputFormat.human,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity (-v, -vv, -vvv)",
        ),
    ] = 0,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress non-error output",
        ),
    ] = False,
) -> None:
    """RaiSE CLI - Reliable AI Software Engineering governance framework.

    Global options apply to all commands and control output format and verbosity.
    """
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["format"] = format.value
    ctx.obj["verbosity"] = -1 if quiet else min(verbose, 3)
    ctx.obj["quiet"] = quiet


if __name__ == "__main__":
    app()
