"""Main CLI application entry point."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

import typer
from rich.console import Console

from raise_cli import __version__
from raise_cli.cli.commands.context import context_app
from raise_cli.cli.commands.discover import discover_app
from raise_cli.cli.commands.graph import graph_app
from raise_cli.cli.commands.init import init_command
from raise_cli.cli.commands.memory import memory_app
from raise_cli.cli.commands.telemetry import telemetry_app
from raise_cli.config import RaiseSettings

# Module-level state for error handling
_current_output_format: Literal["human", "json", "table"] = "human"


def get_output_format() -> Literal["human", "json", "table"]:
    """Get the current output format.

    Returns:
        The output format string ("human", "json", or "table").
    """
    return _current_output_format


app = typer.Typer(
    name="raise",
    help="RaiSE CLI - Reliable AI Software Engineering",
    no_args_is_help=True,
    add_completion=False,
)

# Register command groups
app.add_typer(context_app, name="context")
app.add_typer(discover_app, name="discover")
app.add_typer(graph_app, name="graph")
app.add_typer(memory_app, name="memory")
app.add_typer(telemetry_app, name="telemetry")

# Register standalone commands
app.command("init")(init_command)

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
    global _current_output_format  # noqa: PLW0603
    _current_output_format = format.value  # type: ignore[assignment]

    # Calculate verbosity from flags
    verbosity = -1 if quiet else min(verbose, 3)

    # Create settings with CLI overrides (highest priority)
    settings = RaiseSettings(
        output_format=format.value,  # type: ignore[arg-type]
        verbosity=verbosity,
    )

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings

    # Backward compatibility: keep individual values in ctx.obj
    # (Can be removed once all commands migrate to using settings)
    ctx.obj["format"] = format.value
    ctx.obj["verbosity"] = verbosity
    ctx.obj["quiet"] = quiet


if __name__ == "__main__":
    app()
