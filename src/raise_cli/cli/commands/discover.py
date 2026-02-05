"""Discovery CLI commands for codebase scanning and graph integration.

This module provides commands to scan codebases, extract structural
information, and integrate discovered components into the unified context graph.

Supports Python, TypeScript, and JavaScript.

Example:
    $ raise discover scan src/
    $ raise discover scan . --language typescript --output json
    $ raise discover build --input work/discovery/components-validated.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.discovery.scanner import Language, scan_directory
from raise_cli.output.formatters.discover import format_drift_result, format_scan_result

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
            cli_error(
                f"Unsupported language: {language}",
                hint="Supported: python, typescript, javascript",
                exit_code=7,
            )
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

    format_scan_result(result, path, output, language=lang)


@discover_app.command("build")
def build_command(
    input_file: Annotated[
        Path | None,
        typer.Option(
            "--input",
            "-i",
            help="Path to validated components JSON (default: work/discovery/components-validated.json)",
        ),
    ] = None,
    project_root: Annotated[
        Path,
        typer.Option(
            "--project-root",
            "-r",
            help="Project root directory (default: current directory)",
        ),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output format: human, json, or summary",
        ),
    ] = "human",
) -> None:
    """Build unified graph with discovered components.

    Reads validated components from JSON and integrates them into the unified
    context graph. Components become queryable via `raise context query`.

    The graph is rebuilt from all sources (governance, memory, work, skills,
    and components) and saved to `.raise/graph/unified.json`.

    Examples:
        # Build with default input file
        raise discover build

        # Build with custom input
        raise discover build --input my-components.json

        # Build and show JSON output
        raise discover build --output json
    """
    root = project_root.resolve()

    # Resolve input file path
    if input_file is None:
        input_path = root / "work" / "discovery" / "components-validated.json"
    else:
        input_path = input_file.resolve()

    # Check input file exists
    if not input_path.exists():
        cli_error(
            f"Components file not found: {input_path}",
            hint="Run /discover-complete to generate validated components",
            exit_code=4,
        )

    # Load components to validate and count
    try:
        data: dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))
        components: list[dict[str, Any]] = data.get("components", [])
        component_count = len(components)
    except (json.JSONDecodeError, KeyError) as e:
        cli_error(f"Invalid JSON in {input_path}: {e}")

    if component_count == 0:
        cli_error(
            "No components found in input file",
            hint="Run /discover-validate to validate components first",
        )

    # Build unified graph (includes components automatically)
    from raise_cli.context.builder import UnifiedGraphBuilder

    builder = UnifiedGraphBuilder(project_root=root)
    graph = builder.build()

    # Save graph
    graph_dir = root / ".raise" / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    graph_path = graph_dir / "unified.json"
    graph.save(graph_path)

    # Count component nodes in graph
    component_nodes = [n for n in graph.iter_concepts() if n.type == "component"]
    components_in_graph = len(component_nodes)

    if output == "json":
        output_data = {
            "status": "success",
            "input_file": str(input_path),
            "graph_file": str(graph_path),
            "components_loaded": component_count,
            "components_in_graph": components_in_graph,
            "total_nodes": graph.node_count,
            "total_edges": graph.edge_count,
        }
        console.print_json(json.dumps(output_data))

    elif output == "summary":
        console.print("[bold]Graph Build Summary[/bold]")
        console.print(f"  Components loaded: {components_in_graph}")
        console.print(f"  Total nodes: {graph.node_count}")
        console.print(f"  Total edges: {graph.edge_count}")

    else:
        # Human-readable output
        console.print("[bold green]Graph built successfully[/bold green]\n")
        console.print(f"[bold]Input:[/bold] {input_path}")
        console.print(f"[bold]Output:[/bold] {graph_path}\n")

        # Component summary
        console.print(f"[bold]Components:[/bold] {components_in_graph} loaded")

        # Show by category if available
        categories: dict[str, int] = {}
        for comp in component_nodes:
            category = comp.metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        if categories:
            console.print("\n[bold]By Category:[/bold]")
            for cat, count in sorted(categories.items()):
                console.print(f"  {cat}: {count}")

        # Graph totals
        console.print("\n[bold]Graph Totals:[/bold]")
        console.print(f"  Nodes: {graph.node_count}")
        console.print(f"  Edges: {graph.edge_count}")

        # Sample components
        if component_nodes:
            console.print("\n[bold]Sample Components:[/bold]")
            for comp in component_nodes[:3]:
                name = comp.metadata.get("name", comp.id)
                kind = comp.metadata.get("kind", "")
                console.print(f"  [cyan]{name}[/cyan] ({kind}) — {comp.content[:60]}...")

        # Next steps
        console.print("\n[dim]Query components:[/dim]")
        console.print('  [dim]raise context query --type component "keyword"[/dim]')
        console.print("  [dim]raise context query --unified --type component[/dim]")


@discover_app.command("drift")
def drift_command(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Directory to scan for drift (default: src/)",
        ),
    ] = None,
    project_root: Annotated[
        Path,
        typer.Option(
            "--project-root",
            "-r",
            help="Project root directory (default: current directory)",
        ),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output format: human, json, or summary",
        ),
    ] = "human",
) -> None:
    """Check for architectural drift against baseline components.

    Compares scanned code against the validated component baseline to
    identify potential architectural drift (files in wrong locations,
    naming convention violations, missing documentation).

    Exit codes:
        0 - No drift detected
        1 - Drift warnings found

    Examples:
        # Check entire project
        raise discover drift

        # Check specific directory
        raise discover drift src/new_module/

        # Output as JSON
        raise discover drift --output json
    """
    from raise_cli.discovery.drift import BaselineComponent, DriftWarning, detect_drift

    root = project_root.resolve()
    scan_path = path.resolve() if path else root / "src"

    # Load baseline components
    baseline_file = root / "work" / "discovery" / "components-validated.json"

    if not baseline_file.exists():
        if output == "json":
            console.print_json(
                json.dumps({
                    "status": "no_baseline",
                    "warnings": [],
                    "warning_count": 0,
                    "message": "No baseline components found",
                })
            )
        else:
            console.print(
                "[yellow]No baseline components found.[/yellow]\n"
                "[dim]Run /discover-complete to create a baseline first.[/dim]"
            )
        raise typer.Exit(0)

    # Load baseline
    try:
        baseline_data: dict[str, Any] = json.loads(
            baseline_file.read_text(encoding="utf-8")
        )
        baseline_dicts: list[dict[str, Any]] = baseline_data.get("components", [])
        baseline: list[BaselineComponent] = [
            BaselineComponent.model_validate(comp) for comp in baseline_dicts
        ]
    except (json.JSONDecodeError, KeyError) as e:
        cli_error(f"Error reading baseline: {e}")

    if not baseline:
        if output == "json":
            console.print_json(
                json.dumps({
                    "status": "empty_baseline",
                    "warnings": [],
                    "warning_count": 0,
                    "message": "Baseline has no components",
                })
            )
        else:
            console.print(
                "[yellow]Baseline has no components.[/yellow]\n"
                "[dim]Run /discover-validate to add components.[/dim]"
            )
        raise typer.Exit(0)

    # Warn if baseline is too small for meaningful drift detection
    min_baseline_size = 10
    if len(baseline) < min_baseline_size and output == "human":
        console.print(
            f"[yellow]Note: Baseline has only {len(baseline)} component(s).[/yellow]\n"
            f"[dim]Drift detection works best with {min_baseline_size}+ components "
            "for meaningful patterns.[/dim]\n"
            "[dim]Run /discover-scan and /discover-validate to expand the baseline.[/dim]\n"
        )

    # Scan for new symbols
    if not scan_path.exists():
        if output == "json":
            console.print_json(
                json.dumps({
                    "status": "no_source",
                    "warnings": [],
                    "warning_count": 0,
                    "message": f"Scan path not found: {scan_path}",
                })
            )
        else:
            console.print(f"[yellow]Scan path not found: {scan_path}[/yellow]")
        raise typer.Exit(0)

    scan_result = scan_directory(scan_path)

    # Detect drift
    warnings: list[DriftWarning] = detect_drift(
        baseline=baseline,
        scanned=scan_result.symbols,
    )

    # Output results
    format_drift_result(
        warnings=warnings,
        files_scanned=scan_result.files_scanned,
        symbols_checked=len(scan_result.symbols),
        output_format=output,
    )

    # Exit with 1 if warnings found
    if warnings:
        raise typer.Exit(1)
