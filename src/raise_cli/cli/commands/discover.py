"""Discovery CLI commands for codebase scanning.

This module provides commands to scan codebases and extract structural
information for the unified context graph.

Supports Python, TypeScript, and JavaScript.

Example:
    $ raise discover scan src/
    $ raise discover scan . --language typescript --output json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.discovery.scanner import Language, scan_directory

discover_app = typer.Typer(
    name="discover",
    help="Codebase discovery and analysis commands",
    no_args_is_help=True,
)

console = Console()


@discover_app.command("scan")
def scan_command(
    path: Annotated[
        Path,
        typer.Argument(
            help="Directory to scan for source files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = Path("."),
    language: Annotated[
        str | None,
        typer.Option(
            "--language",
            "-l",
            help="Language to scan: python, typescript, javascript (auto-detect if not set)",
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output format: human, json, or summary",
        ),
    ] = "human",
    pattern: Annotated[
        str | None,
        typer.Option(
            "--pattern",
            "-p",
            help="Glob pattern for files (default: language-specific)",
        ),
    ] = None,
    exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--exclude",
            "-e",
            help="Patterns to exclude (can be repeated)",
        ),
    ] = None,
) -> None:
    """Scan a directory and extract code symbols.

    Extracts classes, functions, methods, interfaces, and module docstrings
    from source files. Supports Python, TypeScript, and JavaScript.

    Output can be human-readable table, JSON, or summary statistics.

    Examples:
        # Scan current directory (auto-detect languages)
        raise discover scan

        # Scan Python files only
        raise discover scan src/ --language python

        # Scan TypeScript project
        raise discover scan ./app --language typescript --output json

        # Auto-detect but exclude tests
        raise discover scan . --exclude "**/test_*" --exclude "**/__tests__/**"
    """
    # Validate language if provided
    lang: Language | None = None
    if language:
        if language not in ("python", "typescript", "javascript"):
            console.print(
                f"[red]Error: Unsupported language '{language}'. "
                "Supported: python, typescript, javascript[/red]"
            )
            raise typer.Exit(1)
        lang = language  # type: ignore[assignment]

    # Set default excludes if none provided
    exclude_patterns = (
        exclude
        if exclude
        else [
            "**/__pycache__/**",
            "**/.venv/**",
            "**/venv/**",
            "**/node_modules/**",
            "**/dist/**",
            "**/build/**",
            "**/.git/**",
        ]
    )

    result = scan_directory(
        path,
        language=lang,
        pattern=pattern,
        exclude_patterns=exclude_patterns,
    )

    if output == "json":
        # JSON output for programmatic use
        output_data = {
            "files_scanned": result.files_scanned,
            "symbols": [s.model_dump() for s in result.symbols],
            "errors": result.errors,
        }
        console.print_json(json.dumps(output_data))

    elif output == "summary":
        # Summary statistics only
        classes = sum(1 for s in result.symbols if s.kind == "class")
        functions = sum(1 for s in result.symbols if s.kind == "function")
        methods = sum(1 for s in result.symbols if s.kind == "method")
        modules = sum(1 for s in result.symbols if s.kind == "module")
        interfaces = sum(1 for s in result.symbols if s.kind == "interface")

        lang_str = f" ({lang})" if lang else " (auto-detect)"
        console.print(f"[bold]Scan Summary:[/bold] {path}{lang_str}")
        console.print(f"  Files scanned: {result.files_scanned}")
        console.print(f"  Symbols found: {len(result.symbols)}")
        console.print(f"    - Classes: {classes}")
        console.print(f"    - Functions: {functions}")
        console.print(f"    - Methods: {methods}")
        if interfaces > 0:
            console.print(f"    - Interfaces: {interfaces}")
        if modules > 0:
            console.print(f"    - Modules with docstrings: {modules}")
        if result.errors:
            console.print(f"  [yellow]Errors: {len(result.errors)}[/yellow]")

    else:
        # Human-readable table output
        if not result.symbols:
            console.print(f"[yellow]No symbols found in {path}[/yellow]")
            return

        table = Table(title=f"Symbols in {path}")
        table.add_column("Kind", style="cyan", width=10)
        table.add_column("Name", style="green")
        table.add_column("File", style="dim")
        table.add_column("Line", justify="right", style="dim")

        # Group by file for readability
        symbols_by_file: dict[str, list[tuple[str, str, int]]] = {}
        for s in result.symbols:
            if s.file not in symbols_by_file:
                symbols_by_file[s.file] = []
            display_name = f"  {s.name}" if s.parent else s.name
            symbols_by_file[s.file].append((s.kind, display_name, s.line))

        for file_path, symbols in sorted(symbols_by_file.items()):
            for kind, name, line in sorted(symbols, key=lambda x: x[2]):
                table.add_row(kind, name, file_path, str(line))

        console.print(table)
        console.print(
            f"\n[dim]{result.files_scanned} files scanned, "
            f"{len(result.symbols)} symbols found[/dim]"
        )

        if result.errors:
            console.print(f"\n[yellow]Warnings ({len(result.errors)}):[/yellow]")
            for error in result.errors[:5]:  # Show first 5 errors
                console.print(f"  [dim]{error}[/dim]")
            if len(result.errors) > 5:
                console.print(f"  [dim]... and {len(result.errors) - 5} more[/dim]")
