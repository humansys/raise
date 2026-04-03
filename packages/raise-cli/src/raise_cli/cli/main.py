"""Main CLI application entry point."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

import typer
from dotenv import load_dotenv
from rich.console import Console

from raise_cli import __version__
from raise_cli.cli.commands.adapters import adapters_app
from raise_cli.cli.commands.artifact import artifact_app
from raise_cli.cli.commands.backlog import backlog_app
from raise_cli.cli.commands.base import base_app
from raise_cli.cli.commands.discover import discover_app
from raise_cli.cli.commands.docs import docs_app
from raise_cli.cli.commands.doctor import doctor_app
from raise_cli.cli.commands.gate import gate_app
from raise_cli.cli.commands.graph import graph_app
from raise_cli.cli.commands.info import info_command
from raise_cli.cli.commands.learn import learn_app
from raise_cli.cli.commands.init import init_command
from raise_cli.cli.commands.mcp import mcp_app
from raise_cli.cli.commands.memory import memory_app
from raise_cli.cli.commands.pattern import pattern_app
from raise_cli.cli.commands.profile import profile_app
from raise_cli.cli.commands.publish import publish_app
from raise_cli.cli.commands.release import release_app
from raise_cli.cli.commands.session import session_app
from raise_cli.cli.commands.signal import signal_app
from raise_cli.cli.commands.skill import skill_app
from raise_cli.cli.extensions import discover_cli_extensions
from raise_cli.config import RaiSettings

# Module-level state for error handling
_current_output_format: Literal["human", "json", "table"] = "human"


def get_output_format() -> Literal["human", "json", "table"]:
    """Get the current output format.

    Returns:
        The output format string ("human", "json", or "table").
    """
    return _current_output_format


app = typer.Typer(
    name="rai",
    help="RaiSE CLI - Reliable AI Software Engineering",
    no_args_is_help=True,
    add_completion=False,
)

# Register command groups
app.add_typer(adapters_app, name="adapter")
app.add_typer(artifact_app, name="artifact")
app.add_typer(backlog_app, name="backlog")
app.add_typer(base_app, name="base")
app.add_typer(discover_app, name="discover")
app.add_typer(docs_app, name="docs")
app.add_typer(doctor_app, name="doctor")
app.add_typer(gate_app, name="gate")
app.add_typer(graph_app, name="graph")
app.add_typer(learn_app, name="learn")
app.add_typer(mcp_app, name="mcp")
app.add_typer(memory_app, name="memory")
app.add_typer(pattern_app, name="pattern")
app.add_typer(profile_app, name="profile")
app.add_typer(publish_app, name="publish")
app.add_typer(release_app, name="release")
app.add_typer(session_app, name="session")
app.add_typer(signal_app, name="signal")
app.add_typer(skill_app, name="skill")

# Register standalone commands
app.command("info")(info_command)
app.command("init")(init_command)

# Register CLI extensions from external packages
discover_cli_extensions(app)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""

    human = "human"
    json = "json"
    table = "table"


def version_callback(value: bool) -> None:  # noqa: ARG001
    """Print version and exit."""
    if value:
        console.print(f"raise-cli version {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[  # noqa: ARG001
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
    load_dotenv(override=False)

    global _current_output_format  # noqa: PLW0603
    _current_output_format = format.value  # type: ignore[assignment]

    # Calculate verbosity from flags
    verbosity = -1 if quiet else min(verbose, 3)

    # Create settings with CLI overrides (highest priority)
    settings = RaiSettings(
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
