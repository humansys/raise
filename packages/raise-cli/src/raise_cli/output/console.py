"""Output console with format-aware printing.

This module provides a unified output interface that respects the --format flag,
supporting human-readable (Rich), JSON, and table formats.

Example:
    >>> from raise_cli.output import get_console
    >>>
    >>> console = get_console()
    >>> console.print_message("Processing...")
    >>> console.print_success("Done!", details={"duration": "2.3s"})
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal, cast

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from raise_cli.output.symbols import CHECK, WARN

if TYPE_CHECKING:
    from collections.abc import Sequence

# Output format type
OutputFormat = Literal["human", "json", "table"]


class OutputConsole:
    """Output abstraction that respects --format flag.

    Provides consistent output formatting across human-readable, JSON,
    and table formats for CLI commands.

    Args:
        format: Output format ("human", "json", or "table").
        verbosity: Verbosity level (-1=quiet, 0=normal, 1-3=verbose).
        color: Whether to use colors in human output.

    Example:
        >>> console = OutputConsole(format="human")
        >>> console.print_message("Hello")
        Hello
        >>> console = OutputConsole(format="json")
        >>> console.print_message("Hello")
        {"message": "Hello"}
    """

    def __init__(
        self,
        format: OutputFormat = "human",
        verbosity: int = 0,
        color: bool = True,
    ) -> None:
        """Initialize OutputConsole.

        Args:
            format: Output format ("human", "json", or "table").
            verbosity: Verbosity level (-1=quiet, 0=normal, 1-3=verbose).
            color: Whether to use colors in human output.
        """
        self.format = format
        self.verbosity = verbosity
        self.color = color
        self._console = Console(force_terminal=color, no_color=not color)

    def _is_quiet(self) -> bool:
        """Check if output should be suppressed (quiet mode)."""
        return self.verbosity < 0

    def print_message(self, message: str, *, style: str | None = None) -> None:
        """Print a simple message.

        Args:
            message: The message to print.
            style: Optional Rich style for human format (e.g., "bold", "dim").

        Example:
            >>> console.print_message("Processing kata...")
            Processing kata...
        """
        if self._is_quiet():
            return

        if self.format == "json":
            self._print_json({"message": message})
        # Both human and table use plain text for messages
        elif style and self.color:
            self._console.print(f"[{style}]{message}[/]")
        else:
            self._console.print(message)

    def print_success(
        self, message: str, *, details: dict[str, Any] | None = None
    ) -> None:
        """Print a success message with optional details.

        Args:
            message: The success message.
            details: Optional key-value details to display.

        Example:
            >>> console.print_success("Kata completed", details={"duration": "2.3s"})
            ✓ Kata completed (duration: 2.3s)
        """
        if self._is_quiet():
            return

        if self.format == "json":
            output: dict[str, Any] = {"status": "success", "message": message}
            if details:
                output["details"] = details
            self._print_json(output)
        else:
            # Human and table format
            detail_str = ""
            if details:
                detail_str = (
                    " (" + ", ".join(f"{k}: {v}" for k, v in details.items()) + ")"
                )
            if self.color:
                self._console.print(f"[green]{CHECK}[/] {message}{detail_str}")
            else:
                self._console.print(f"{CHECK} {message}{detail_str}")

    def print_warning(
        self, message: str, *, details: dict[str, Any] | None = None
    ) -> None:
        """Print a warning message.

        Args:
            message: The warning message.
            details: Optional key-value details to display.

        Example:
            >>> console.print_warning("Config not found, using defaults")
            ⚠ Config not found, using defaults
        """
        if self._is_quiet():
            return

        if self.format == "json":
            output: dict[str, Any] = {"status": "warning", "message": message}
            if details:
                output["details"] = details
            self._print_json(output)
        else:
            # Human and table format
            detail_str = ""
            if details:
                detail_str = (
                    " (" + ", ".join(f"{k}: {v}" for k, v in details.items()) + ")"
                )
            if self.color:
                self._console.print(f"[yellow]{WARN}[/] {message}{detail_str}")
            else:
                self._console.print(f"{WARN} {message}{detail_str}")

    def print_data(self, data: dict[str, Any], *, title: str | None = None) -> None:
        """Print a data structure.

        Renders as:
        - Human: Rich Tree for nested, key-value list for flat
        - JSON: Raw dict
        - Table: Key-value table

        Args:
            data: Dictionary to display.
            title: Optional title for the output.

        Example:
            >>> console.print_data({"name": "discovery", "steps": 5})
        """
        if self._is_quiet():
            return

        if self.format == "json":
            self._print_json(data)
        elif self.format == "table":
            self._print_data_as_table(data, title=title)
        # Human format - use tree for nested, simple for flat
        elif self._has_nested_values(data):
            self._print_data_as_tree(data, title=title)
        else:
            self._print_data_as_kv(data, title=title)

    def print_list(
        self,
        items: Sequence[dict[str, Any]],
        *,
        columns: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        """Print a list of items.

        Renders as:
        - Human: Bullet list
        - JSON: Array
        - Table: Rich Table with columns

        Args:
            items: List of dictionaries to display.
            columns: Column names to display (default: all keys from first item).
            title: Optional title for the output.

        Example:
            >>> console.print_list([
            ...     {"id": "kata/discovery", "name": "Discovery"},
            ...     {"id": "kata/design", "name": "Design"},
            ... ])
        """
        if self._is_quiet():
            return

        if not items:
            if self.format == "json":
                self._print_json([])
            else:
                self._console.print("(no items)")
            return

        if self.format == "json":
            self._print_json(list(items))
        elif self.format == "table":
            self._print_list_as_table(items, columns=columns, title=title)
        else:
            # Human format - bullet list
            self._print_list_as_bullets(items, title=title)

    # --- Private helpers ---

    def _print_json(self, data: Any) -> None:
        """Output data as JSON to stdout."""
        print(json.dumps(data, indent=2, default=str))

    def _has_nested_values(self, data: dict[str, Any]) -> bool:
        """Check if dict has nested dict/list values."""
        return any(isinstance(v, (dict, list)) for v in data.values())

    def _print_data_as_tree(
        self, data: dict[str, Any], *, title: str | None = None
    ) -> None:
        """Render nested dict as Rich Tree."""
        tree = Tree(title or "Data")
        self._add_dict_to_tree(tree, data)
        self._console.print(tree)

    def _add_dict_to_tree(self, tree: Tree, data: dict[str, Any]) -> None:
        """Recursively add dict entries to tree."""
        for key, value in data.items():
            if isinstance(value, dict):
                branch = tree.add(f"[bold]{key}[/]")
                nested = cast("dict[str, Any]", value)
                self._add_dict_to_tree(branch, nested)
            elif isinstance(value, list):
                branch = tree.add(f"[bold]{key}[/]")
                items = cast("list[Any]", value)
                for i, item in enumerate(items):
                    if isinstance(item, dict):
                        sub = branch.add(f"[dim][{i}][/]")
                        nested_item = cast("dict[str, Any]", item)
                        self._add_dict_to_tree(sub, nested_item)
                    else:
                        branch.add(str(item))
            else:
                tree.add(f"[bold]{key}:[/] {value}")

    def _print_data_as_kv(
        self, data: dict[str, Any], *, title: str | None = None
    ) -> None:
        """Render flat dict as key-value pairs."""
        if title:
            self._console.print(f"[bold]{title}[/]")
        for key, value in data.items():
            self._console.print(f"  [bold]{key}:[/] {value}")

    def _print_data_as_table(
        self, data: dict[str, Any], *, title: str | None = None
    ) -> None:
        """Render dict as two-column table."""
        table = Table(title=title, show_header=True)
        table.add_column("Key", style="bold")
        table.add_column("Value")
        for key, value in data.items():
            table.add_row(key, str(value))
        self._console.print(table)

    def _print_list_as_bullets(
        self, items: Sequence[dict[str, Any]], *, title: str | None = None
    ) -> None:
        """Render list as bullet points."""
        if title:
            self._console.print(f"{title}:")
        for item in items:
            # Create a summary from the first 2-3 values
            values = list(item.values())[:3]
            summary = " - ".join(str(v) for v in values)
            self._console.print(f"  • {summary}")

    def _print_list_as_table(
        self,
        items: Sequence[dict[str, Any]],
        *,
        columns: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        """Render list as Rich Table."""
        # Determine columns from first item if not specified
        if columns is None:
            columns = list(items[0].keys()) if items else []

        table = Table(title=title, show_header=True)
        for col in columns:
            table.add_column(col.upper())

        for item in items:
            row = [str(item.get(col, "")) for col in columns]
            table.add_row(*row)

        self._console.print(table)


# --- Module-level singleton ---

_console: OutputConsole | None = None


def get_console() -> OutputConsole:
    """Get or create the output console singleton.

    Returns:
        The global OutputConsole instance.

    Example:
        >>> console = get_console()
        >>> console.print_message("Hello")
    """
    global _console  # noqa: PLW0603
    if _console is None:
        _console = OutputConsole()
    return _console


def set_console(console: OutputConsole | None) -> None:
    """Set the output console (for testing or reconfiguration).

    Args:
        console: Console to use, or None to reset to default.

    Example:
        >>> set_console(OutputConsole(format="json"))
        >>> # ... use console ...
        >>> set_console(None)  # Reset
    """
    global _console  # noqa: PLW0603
    _console = console


def configure_console(
    format: OutputFormat = "human",
    verbosity: int = 0,
    color: bool = True,
) -> OutputConsole:
    """Configure and return the global console.

    Creates a new OutputConsole with the given settings and sets it
    as the global singleton.

    Args:
        format: Output format ("human", "json", or "table").
        verbosity: Verbosity level (-1=quiet, 0=normal, 1-3=verbose).
        color: Whether to use colors in human output.

    Returns:
        The newly configured OutputConsole.

    Example:
        >>> console = configure_console(format="json", verbosity=1)
    """
    global _console  # noqa: PLW0603
    _console = OutputConsole(format=format, verbosity=verbosity, color=color)
    return _console


__all__ = [
    "OutputConsole",
    "OutputFormat",
    "get_console",
    "set_console",
    "configure_console",
]
