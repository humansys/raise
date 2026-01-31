"""Error presentation with Rich formatting.

This module provides error display for raise-cli, supporting both
human-friendly Rich output and JSON format for scripting.

Example:
    >>> from raise_cli.exceptions import KataNotFoundError
    >>> from raise_cli.cli.error_handler import handle_error
    >>>
    >>> error = KataNotFoundError("Kata 'foo' not found", hint="Check .raise/katas/")
    >>> exit_code = handle_error(error, format="human")
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Literal

from rich.console import Console
from rich.panel import Panel

if TYPE_CHECKING:
    from raise_cli.exceptions import RaiseError

# Stderr console for error output
_error_console: Console | None = None


def get_error_console() -> Console:
    """Get or create the stderr console singleton.

    Returns:
        Rich Console configured for stderr output.
    """
    global _error_console  # noqa: PLW0603
    if _error_console is None:
        _error_console = Console(stderr=True)
    return _error_console


def set_error_console(console: Console | None) -> None:
    """Set the error console (for testing).

    Args:
        console: Console to use, or None to reset to default.
    """
    global _error_console  # noqa: PLW0603
    _error_console = console


def handle_error(
    error: RaiseError,
    *,
    output_format: Literal["human", "json", "table"] = "human",
) -> int:
    """Format and display error, return exit code.

    Args:
        error: The RaiseError to display.
        output_format: Output format (human uses Rich, json outputs JSON).

    Returns:
        The error's exit_code for use with sys.exit().
    """
    if output_format == "json":
        _handle_error_json(error)
    else:
        _handle_error_human(error)

    return error.exit_code


def _handle_error_human(error: RaiseError) -> None:
    """Display error with Rich formatting.

    Args:
        error: The RaiseError to display.
    """
    console = get_error_console()

    # Main error panel
    console.print(
        Panel(
            f"[bold red]{error.message}[/]",
            title=f"[red]Error {error.error_code}[/]",
            border_style="red",
        )
    )

    # Details section
    if error.details:
        console.print("\n[dim]Details:[/]")
        for key, value in error.details.items():
            console.print(f"  [dim]\u2022[/] {key}: {value}")

    # Hint section
    if error.hint:
        console.print(f"\n[cyan]Hint:[/] {error.hint}")


def _handle_error_json(error: RaiseError) -> None:
    """Output error as JSON to stderr.

    Args:
        error: The RaiseError to display.
    """
    output = json.dumps(error.to_dict(), indent=2)
    print(output, file=sys.stderr)


__all__ = [
    "handle_error",
    "get_error_console",
    "set_error_console",
]
