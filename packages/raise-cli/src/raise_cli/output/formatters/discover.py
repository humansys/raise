"""Formatters for discovery command results.

Provides format-aware output for scan and drift results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from raise_cli.discovery.analyzer import AnalysisResult
    from raise_cli.discovery.drift import DriftWarning
    from raise_cli.discovery.scanner import ScanResult

# Module-level console for output
_console = Console()


def format_scan_result(
    result: ScanResult,
    path: Path,
    output_format: str,
    language: str | None = None,
) -> None:
    """Format and print scan results.

    Args:
        result: Scan result containing symbols and metadata.
        path: Path that was scanned.
        output_format: Output format ("json", "summary", or "human").
        language: Language filter used (for display).
    """
    if output_format == "json":
        _format_scan_json(result)
    elif output_format == "summary":
        _format_scan_summary(result, path, language)
    else:
        _format_scan_human(result, path)


def _format_scan_json(result: ScanResult) -> None:
    """Format scan result as JSON."""
    output_data = {
        "files_scanned": result.files_scanned,
        "symbols": [s.model_dump() for s in result.symbols],
        "errors": result.errors,
    }
    _console.print_json(json.dumps(output_data))


def _format_scan_summary(
    result: ScanResult,
    path: Path,
    language: str | None,
) -> None:
    """Format scan result as summary statistics."""
    classes = sum(1 for s in result.symbols if s.kind == "class")
    functions = sum(1 for s in result.symbols if s.kind == "function")
    methods = sum(1 for s in result.symbols if s.kind == "method")
    modules = sum(1 for s in result.symbols if s.kind == "module")
    interfaces = sum(1 for s in result.symbols if s.kind == "interface")
    enums = sum(1 for s in result.symbols if s.kind == "enum")
    type_aliases = sum(1 for s in result.symbols if s.kind == "type_alias")
    constants = sum(1 for s in result.symbols if s.kind == "constant")
    traits = sum(1 for s in result.symbols if s.kind == "trait")
    components = sum(1 for s in result.symbols if s.kind == "component")

    lang_str = f" ({language})" if language else " (auto-detect)"
    _console.print(f"[bold]Scan Summary:[/bold] {path}{lang_str}")
    _console.print(f"  Files scanned: {result.files_scanned}")
    _console.print(f"  Symbols found: {len(result.symbols)}")
    _console.print(f"    - Classes: {classes}")
    _console.print(f"    - Functions: {functions}")
    _console.print(f"    - Methods: {methods}")
    if interfaces > 0:
        _console.print(f"    - Interfaces: {interfaces}")
    if enums > 0:
        _console.print(f"    - Enums: {enums}")
    if type_aliases > 0:
        _console.print(f"    - Type aliases: {type_aliases}")
    if constants > 0:
        _console.print(f"    - Constants: {constants}")
    if traits > 0:
        _console.print(f"    - Traits: {traits}")
    if components > 0:
        _console.print(f"    - Components: {components}")
    if modules > 0:
        _console.print(f"    - Modules with docstrings: {modules}")
    if result.errors:
        _console.print(f"  [yellow]Errors: {len(result.errors)}[/yellow]")


def _format_scan_human(result: ScanResult, path: Path) -> None:
    """Format scan result as human-readable table."""
    if not result.symbols:
        _console.print(f"[yellow]No symbols found in {path}[/yellow]")
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

    _console.print(table)
    _console.print(
        f"\n[dim]{result.files_scanned} files scanned, "
        f"{len(result.symbols)} symbols found[/dim]"
    )

    if result.errors:
        _console.print(f"\n[yellow]Warnings ({len(result.errors)}):[/yellow]")
        for error in result.errors[:5]:
            _console.print(f"  [dim]{error}[/dim]")
        if len(result.errors) > 5:
            _console.print(f"  [dim]... and {len(result.errors) - 5} more[/dim]")


def format_drift_result(
    warnings: list[DriftWarning],
    files_scanned: int,
    symbols_checked: int,
    output_format: str,
) -> None:
    """Format and print drift detection results.

    Args:
        warnings: List of drift warnings found.
        files_scanned: Number of files scanned.
        symbols_checked: Number of symbols checked.
        output_format: Output format ("json", "summary", or "human").
    """
    if output_format == "json":
        _format_drift_json(warnings, files_scanned, symbols_checked)
    elif output_format == "summary":
        _format_drift_summary(warnings, files_scanned, symbols_checked)
    else:
        _format_drift_human(warnings, files_scanned, symbols_checked)


def _format_drift_json(
    warnings: list[DriftWarning],
    files_scanned: int,
    symbols_checked: int,
) -> None:
    """Format drift result as JSON."""
    _console.print_json(
        json.dumps(
            {
                "status": "drift" if warnings else "clean",
                "warnings": [w.model_dump() for w in warnings],
                "warning_count": len(warnings),
                "files_scanned": files_scanned,
                "symbols_checked": symbols_checked,
            }
        )
    )


def _format_drift_summary(
    warnings: list[DriftWarning],
    files_scanned: int,
    symbols_checked: int,
) -> None:
    """Format drift result as summary statistics."""
    _console.print("[bold]Drift Detection Summary[/bold]")
    _console.print(f"  Files scanned: {files_scanned}")
    _console.print(f"  Symbols checked: {symbols_checked}")
    _console.print(f"  Warnings: {len(warnings)}")
    if warnings:
        by_severity: dict[str, int] = {}
        for w in warnings:
            by_severity[w.severity] = by_severity.get(w.severity, 0) + 1
        for sev, count in sorted(by_severity.items()):
            _console.print(f"    - {sev}: {count}")


def _format_drift_human(
    warnings: list[DriftWarning],
    files_scanned: int,
    symbols_checked: int,
) -> None:
    """Format drift result as human-readable output."""
    if not warnings:
        _console.print("[bold green]No drift detected[/bold green]")
        _console.print(
            f"[dim]Scanned {files_scanned} files, "
            f"checked {symbols_checked} symbols[/dim]"
        )
        return

    _console.print(
        f"[bold yellow]Drift detected: {len(warnings)} warning(s)[/bold yellow]\n"
    )

    for warning in warnings:
        severity_color = {
            "error": "red",
            "warning": "yellow",
            "info": "blue",
        }.get(warning.severity, "white")

        _console.print(
            f"[{severity_color}]{warning.severity.upper()}[/{severity_color}] "
            f"[bold]{warning.file}[/bold]"
        )
        _console.print(f"  {warning.issue}")
        if warning.suggestion:
            _console.print(f"  [dim]Suggestion: {warning.suggestion}[/dim]")
        _console.print()

    _console.print(
        f"[dim]Scanned {files_scanned} files, checked {symbols_checked} symbols[/dim]"
    )


def format_analyze_result(
    result: AnalysisResult,
    output_format: str,
) -> None:
    """Format and print analysis results.

    Args:
        result: Analysis result from the analyze pipeline.
        output_format: Output format ("json", "summary", or "human").
    """
    if output_format == "json":
        _format_analyze_json(result)
    elif output_format == "summary":
        _format_analyze_summary(result)
    else:
        _format_analyze_human(result)


def _format_analyze_json(result: AnalysisResult) -> None:
    """Format analysis result as JSON."""
    _console.print_json(json.dumps(result.model_dump(), default=str))


def _format_analyze_summary(result: AnalysisResult) -> None:
    """Format analysis result as summary statistics."""
    summary = result.scan_summary
    dist = result.confidence_distribution
    total = sum(dist.values())

    _console.print("[bold]Discovery Analysis Summary[/bold]")
    _console.print(f"  Files scanned: {summary.get('files_scanned', 0)}")
    _console.print(
        f"  Symbols: {summary.get('total_symbols', 0)} "
        f"({summary.get('public_symbols', 0)} public, "
        f"{summary.get('internal_symbols', 0)} internal)"
    )
    _console.print(f"  Components: {total}")
    _console.print(f"    High confidence:   {dist.get('high', 0)}")
    _console.print(f"    Medium confidence:  {dist.get('medium', 0)}")
    _console.print(f"    Low confidence:     {dist.get('low', 0)}")
    _console.print(f"  Module groups: {len(result.module_groups)}")


def _format_analyze_human(result: AnalysisResult) -> None:
    """Format analysis result as human-readable output."""
    summary = result.scan_summary
    dist = result.confidence_distribution
    total = sum(dist.values())

    _console.print("[bold]Discovery Analysis[/bold]")
    _console.print("=" * 40)
    _console.print(
        f"\nScanned: {summary.get('files_scanned', 0)} files, "
        f"{summary.get('total_symbols', 0)} symbols "
        f"({summary.get('public_symbols', 0)} public, "
        f"{summary.get('internal_symbols', 0)} internal)"
    )

    # Confidence distribution
    _console.print("\n[bold]Confidence Distribution:[/bold]")
    if total > 0:
        high = dist.get("high", 0)
        med = dist.get("medium", 0)
        low = dist.get("low", 0)
        _console.print(
            f"  [green]High   (auto-validate):[/green] {high} ({high * 100 // total}%)"
        )
        _console.print(
            f"  [yellow]Medium (batch review):[/yellow]  {med} ({med * 100 // total}%)"
        )
        _console.print(
            f"  [red]Low    (needs review):[/red]  {low} ({low * 100 // total}%)"
        )
    else:
        _console.print("  No components to analyze")

    # Category breakdown
    if result.categories:
        _console.print("\n[bold]Category Breakdown:[/bold]")
        for cat, count in sorted(result.categories.items(), key=lambda x: -x[1]):
            _console.print(f"  {cat}: {count}")

    # Module groups
    if result.module_groups:
        _console.print(f"\n[bold]Module Groups:[/bold] {len(result.module_groups)}")
        for module_path, comp_ids in sorted(result.module_groups.items()):
            _console.print(f"  {module_path}  [{len(comp_ids)} components]")
