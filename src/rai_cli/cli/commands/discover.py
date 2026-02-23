"""Discovery CLI commands for codebase scanning and graph integration.

This module provides commands to scan codebases, extract structural
information, and integrate discovered components into the unified context graph.

Supports Python, TypeScript, JavaScript, PHP, Svelte, and C#.

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

from rai_cli.cli.error_handler import cli_error
from rai_cli.discovery.scanner import Language, ScanResult, scan_directory
from rai_cli.output.formatters.discover import (
    format_analyze_result,
    format_build_result,
    format_drift_result,
    format_scan_result,
)

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
            help="Language to scan: python, typescript, javascript, php, svelte, csharp (auto-detect if not set)",
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
    from source files. Supports Python, TypeScript, JavaScript, PHP, Svelte, and C#.

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
        if language not in ("python", "typescript", "javascript", "php", "svelte", "csharp"):
            cli_error(
                f"Unsupported language: {language}",
                hint="Supported: python, typescript, javascript, php, svelte, csharp",
                exit_code=7,
            )
        lang = language  # type: ignore[assignment]

    # Pass user excludes or None to use DEFAULT_EXCLUDE_PATTERNS from scanner
    exclude_patterns = exclude if exclude else None

    result = scan_directory(
        path,
        language=lang,
        pattern=pattern,
        exclude_patterns=exclude_patterns,
    )

    format_scan_result(result, path, output, language=lang)


@discover_app.command("analyze")
def analyze_command(
    input_file: Annotated[
        Path | None,
        typer.Option(
            "--input",
            "-i",
            help="Path to scan result JSON (reads stdin if not provided)",
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
    category_map_file: Annotated[
        Path | None,
        typer.Option(
            "--category-map",
            "-c",
            help="YAML file with custom path-to-category mappings",
        ),
    ] = None,
) -> None:
    """Analyze scan results with confidence scoring and module grouping.

    Takes raw scan output (from `raise discover scan --output json`) and
    produces an analysis with confidence scores, auto-categorization,
    hierarchical folding, and module grouping for parallel AI synthesis.

    All analysis is deterministic — no AI inference required.

    Examples:
        # Analyze from file
        raise discover analyze --input scan-result.json

        # Pipe from scan
        raise discover scan src/ -l python -o json | raise discover analyze

        # JSON output
        raise discover analyze --input scan-result.json --output json

        # Summary only
        raise discover analyze --input scan-result.json --output summary
    """
    import sys

    from rai_cli.discovery.analyzer import analyze

    # Load scan result JSON
    scan_json: str = ""
    if input_file:
        if not input_file.exists():
            cli_error(
                f"Input file not found: {input_file}",
                hint="Run 'raise discover scan --output json' first",
                exit_code=4,
            )
        scan_json = input_file.read_text(encoding="utf-8")
    else:
        # Read from stdin
        if sys.stdin.isatty():
            cli_error(
                "No input provided",
                hint="Pipe from scan: raise discover scan -o json | raise discover analyze\n"
                "Or use --input: raise discover analyze --input scan-result.json",
                exit_code=7,
            )
        scan_json = sys.stdin.read()

    # Parse scan result
    scan_result = ScanResult(symbols=[], files_scanned=0, errors=[])
    try:
        scan_data: dict[str, Any] = json.loads(scan_json)
        scan_result = ScanResult(
            symbols=[],
            files_scanned=scan_data.get("files_scanned", 0),
            errors=scan_data.get("errors", []),
        )
        # Parse symbols from JSON
        from rai_cli.discovery.scanner import Symbol

        for sym_data in scan_data.get("symbols", []):
            scan_result.symbols.append(Symbol.model_validate(sym_data))
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        cli_error(
            f"Invalid scan result JSON: {e}",
            hint="Input must be JSON from 'raise discover scan --output json'",
            exit_code=7,
        )

    # Load custom category map if provided
    category_map: dict[str, str] | None = None
    if category_map_file:
        if not category_map_file.exists():
            cli_error(
                f"Category map file not found: {category_map_file}",
                exit_code=4,
            )
        try:
            import yaml

            category_map = yaml.safe_load(category_map_file.read_text(encoding="utf-8"))
        except ImportError:
            cli_error(
                "PyYAML required for --category-map",
                hint="Install with: pip install pyyaml",
                exit_code=6,
            )
        except Exception as e:
            cli_error(f"Error reading category map: {e}", exit_code=7)

    # Run analysis
    result = analyze(scan_result, category_map=category_map)

    # Save analysis.json
    output_dir = Path("work/discovery")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "analysis.json"
    output_path.write_text(
        json.dumps(result.model_dump(), indent=2, default=str),
        encoding="utf-8",
    )

    # Format and print
    format_analyze_result(result, output)

    if output != "json":
        console.print(f"\n[dim]Saved: {output_path}[/dim]")


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
            hint="Run /rai-discover-validate to generate validated components",
            exit_code=4,
        )

    # Load components to validate and count
    component_count = 0
    try:
        data: dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))
        components: list[dict[str, Any]] = data.get("components", [])
        component_count = len(components)
    except (json.JSONDecodeError, KeyError) as e:
        cli_error(f"Invalid JSON in {input_path}: {e}")

    if component_count == 0:
        cli_error(
            "No components found in input file",
            hint="Run /rai-discover-validate to validate components first",
        )

    # Build unified graph (includes components automatically)
    from rai_cli.context.builder import UnifiedGraphBuilder

    builder = UnifiedGraphBuilder(project_root=root)
    graph = builder.build()

    # Save graph via backend
    from rai_cli.graph.filesystem_backend import get_active_backend

    graph_path = root / ".raise" / "graph" / "unified.json"
    backend = get_active_backend()
    backend.persist(graph, graph_path)

    # Count component nodes in graph
    component_nodes = [n for n in graph.iter_concepts() if n.type == "component"]
    components_in_graph = len(component_nodes)

    # Build categories dict
    categories: dict[str, int] = {}
    for comp in component_nodes:
        category = comp.metadata.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1

    # Build sample components list
    sample_components = [
        (
            comp.metadata.get("name", comp.id),
            comp.metadata.get("kind", ""),
            comp.content[:60],
        )
        for comp in component_nodes[:3]
    ]

    format_build_result(
        input_path=input_path,
        graph_path=graph_path,
        component_count=component_count,
        components_in_graph=components_in_graph,
        node_count=graph.node_count,
        edge_count=graph.edge_count,
        categories=categories,
        sample_components=sample_components,
        output_format=output,
    )


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
    from rai_cli.discovery.drift import BaselineComponent, DriftWarning, detect_drift

    root = project_root.resolve()
    scan_path = path.resolve() if path else root / "src"

    # Load baseline components
    baseline_file = root / "work" / "discovery" / "components-validated.json"

    if not baseline_file.exists():
        if output == "json":
            console.print_json(
                json.dumps(
                    {
                        "status": "no_baseline",
                        "warnings": [],
                        "warning_count": 0,
                        "message": "No baseline components found",
                    }
                )
            )
        else:
            console.print(
                "[yellow]No baseline components found.[/yellow]\n"
                "[dim]Run /rai-discover-validate to create a baseline first.[/dim]"
            )
        raise typer.Exit(0)

    # Load baseline
    baseline: list[BaselineComponent] = []
    try:
        baseline_data: dict[str, Any] = json.loads(
            baseline_file.read_text(encoding="utf-8")
        )
        baseline_dicts: list[dict[str, Any]] = baseline_data.get("components", [])
        baseline = [BaselineComponent.model_validate(comp) for comp in baseline_dicts]
    except (json.JSONDecodeError, KeyError) as e:
        cli_error(f"Error reading baseline: {e}")

    if not baseline:
        if output == "json":
            console.print_json(
                json.dumps(
                    {
                        "status": "empty_baseline",
                        "warnings": [],
                        "warning_count": 0,
                        "message": "Baseline has no components",
                    }
                )
            )
        else:
            console.print(
                "[yellow]Baseline has no components.[/yellow]\n"
                "[dim]Run /rai-discover-validate to add components.[/dim]"
            )
        raise typer.Exit(0)

    # Warn if baseline is too small for meaningful drift detection
    min_baseline_size = 10
    if len(baseline) < min_baseline_size and output == "human":
        console.print(
            f"[yellow]Note: Baseline has only {len(baseline)} component(s).[/yellow]\n"
            f"[dim]Drift detection works best with {min_baseline_size}+ components "
            "for meaningful patterns.[/dim]\n"
            "[dim]Run /rai-discover-scan and /rai-discover-validate to expand the baseline.[/dim]\n"
        )

    # Scan for new symbols
    if not scan_path.exists():
        if output == "json":
            console.print_json(
                json.dumps(
                    {
                        "status": "no_source",
                        "warnings": [],
                        "warning_count": 0,
                        "message": f"Scan path not found: {scan_path}",
                    }
                )
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
