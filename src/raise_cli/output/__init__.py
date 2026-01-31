"""Output formatting module for raise-cli.

Provides format-aware output (human, JSON, table) for CLI commands.

Example:
    >>> from raise_cli.output import get_console
    >>>
    >>> console = get_console()
    >>> console.print_success("Done!", details={"duration": "2.3s"})
"""

from __future__ import annotations

from raise_cli.output.console import (
    OutputConsole,
    OutputFormat,
    configure_console,
    get_console,
    set_console,
)

__all__ = [
    "OutputConsole",
    "OutputFormat",
    "get_console",
    "set_console",
    "configure_console",
]
