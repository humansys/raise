"""Main CLI application entry point."""

from __future__ import annotations

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


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"raise-cli version {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
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
) -> None:
    """RaiSE CLI - Reliable AI Software Engineering governance framework."""
    pass


if __name__ == "__main__":
    app()
