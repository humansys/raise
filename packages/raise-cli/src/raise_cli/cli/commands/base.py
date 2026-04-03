"""Backward-compatible alias for the info command.

The `base show` command has been moved to `rai info` (CLI restructuring).

This alias prints a deprecation warning and delegates to the canonical command.
It will be removed in a future release (v3.0).
"""

from __future__ import annotations

import typer
from rich.console import Console

base_app = typer.Typer(
    name="base",
    help="View base Rai package info",
    no_args_is_help=True,
)

_stderr_console = Console(stderr=True)


@base_app.command()
def show() -> None:
    """Deprecated: use 'rai info'."""
    _stderr_console.print(
        "[yellow]DEPRECATED:[/yellow] 'rai base show' → use 'rai info' instead",
    )
    from raise_cli.cli.commands.info import info_command

    info_command()
