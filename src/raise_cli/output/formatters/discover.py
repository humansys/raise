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

    lang_str = f" ({language})" if language else " (auto-detect)"
    _console.print(f"[bold]Scan Summary:[/bold] {path}{lang_str}")
    _console.print(f"  Files scanned: {result.files_scanned}")
    _console.print(f"  Symbols found: {len(result.symbols)}")
    _console.print(f"    - Classes: {classes}")
    _console.print(f"    - Functions: {functions}")
    _console.print(f"    - Methods: {methods}")
    if interfaces > 0:
        _console.print(f"    - Interfaces: {interfaces}")
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


def format_build_result(
    input_path: Path,
    graph_path: Path,
    component_count: int,
    components_in_graph: int,
    node_count: int,
    edge_count: int,
    categories: dict[str, int],
    sample_components: list[tuple[str, str, str]],
    output_format: str,
) -> None:
    """Format and print discover build results.

    Args:
        input_path: Path to the input components file.
        graph_path: Path to the output graph file.
        component_count: Number of components loaded from input.
        components_in_graph: Number of component nodes in graph.
        node_count: Total nodes in graph.
        edge_count: Total edges in graph.
        categories: Component counts by category.
        sample_components: List of (name, kind, content_preview) tuples.
        output_format: Output format ("json", "summary", or "human").
    """
    if output_format == "json":
        _format_build_json(
            input_path,
            graph_path,
            component_count,
            components_in_graph,
            node_count,
            edge_count,
        )
    elif output_format == "summary":
        _format_build_summary(components_in_graph, node_count, edge_count)
    else:
        _format_build_human(
            input_path,
            graph_path,
            components_in_graph,
            node_count,
            edge_count,
            categories,
            sample_components,
        )


def _format_build_json(
    input_path: Path,
    graph_path: Path,
    component_count: int,
    components_in_graph: int,
    node_count: int,
    edge_count: int,
) -> None:
    """Format build result as JSON."""
    output_data = {
        "status": "success",
        "input_file": str(input_path),
        "graph_file": str(graph_path),
        "components_loaded": component_count,
        "components_in_graph": components_in_graph,
        "total_nodes": node_count,
        "total_edges": edge_count,
    }
    _console.print_json(json.dumps(output_data))


def _format_build_summary(
    components_in_graph: int,
    node_count: int,
    edge_count: int,
) -> None:
    """Format build result as summary statistics."""
    _console.print("[bold]Graph Build Summary[/bold]")
    _console.print(f"  Components loaded: {components_in_graph}")
    _console.print(f"  Total nodes: {node_count}")
    _console.print(f"  Total edges: {edge_count}")


def _format_build_human(
    input_path: Path,
    graph_path: Path,
    components_in_graph: int,
    node_count: int,
    edge_count: int,
    categories: dict[str, int],
    sample_components: list[tuple[str, str, str]],
) -> None:
    """Format build result as human-readable output."""
    _console.print("[bold green]Graph built successfully[/bold green]\n")
    _console.print(f"[bold]Input:[/bold] {input_path}")
    _console.print(f"[bold]Output:[/bold] {graph_path}\n")

    # Component summary
    _console.print(f"[bold]Components:[/bold] {components_in_graph} loaded")

    # Show by category if available
    if categories:
        _console.print("\n[bold]By Category:[/bold]")
        for cat, count in sorted(categories.items()):
            _console.print(f"  {cat}: {count}")

    # Graph totals
    _console.print("\n[bold]Graph Totals:[/bold]")
    _console.print(f"  Nodes: {node_count}")
    _console.print(f"  Edges: {edge_count}")

    # Sample components
    if sample_components:
        _console.print("\n[bold]Sample Components:[/bold]")
        for name, kind, content in sample_components[:3]:
            _console.print(f"  [cyan]{name}[/cyan] ({kind}) — {content}...")

    # Next steps
    _console.print("\n[dim]Query components:[/dim]")
    _console.print('  [dim]raise context query "keyword" --types component[/dim]')
