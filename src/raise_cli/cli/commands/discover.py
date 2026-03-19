"""Discovery CLI commands for codebase scanning and graph integration.

This module provides commands to scan codebases, extract structural
information, and integrate discovered components into the unified context graph.

Supports Python, TypeScript, JavaScript, PHP, Svelte, and C#.

Example:
    $ raise discover scan src/
    $ raise discover scan . --language typescript --output json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.discovery.scanner import Language, ScanResult, scan_directory
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import DiscoverScanEvent
from raise_cli.output.formatters.discover import (
    format_analyze_result,
    format_drift_result,
    format_scan_result,
)

discover_app = typer.Typer(
    name="discover",
    help="Codebase discovery and analysis commands",
    no_args_is_help=True,
)

console = Console()


_SUPPORTED_LANGUAGES = ("python", "typescript", "javascript", "php", "svelte", "csharp")


def _validate_language(language: str | None) -> Language | None:
    """Validate and return typed language, exit on unsupported value."""
    if not language:
        return None
    if language not in _SUPPORTED_LANGUAGES:
        cli_error(
            f"Unsupported language: {language}",
            hint="Supported: python, typescript, javascript, php, svelte, csharp",
            exit_code=7,
        )
    return language  # type: ignore[return-value]


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
    lang = _validate_language(language)
    exclude_patterns = exclude if exclude else None

    result = scan_directory(
        path,
        language=lang,
        pattern=pattern,
        exclude_patterns=exclude_patterns,
    )

    emitter = create_emitter()
    emitter.emit(
        DiscoverScanEvent(
            project_path=path,
            language=lang or "auto",
            component_count=len(result.symbols),
        )
    )

    format_scan_result(result, path, output, language=lang)


def _read_scan_json(input_file: Path | None) -> str:
    """Read scan result JSON from file or stdin, exit on missing input."""
    import sys

    if input_file:
        if not input_file.exists():
            cli_error(
                f"Input file not found: {input_file}",
                hint="Run 'raise discover scan --output json' first",
                exit_code=4,
            )
        return input_file.read_text(encoding="utf-8")

    if sys.stdin.isatty():
        cli_error(
            "No input provided",
            hint="Pipe from scan: raise discover scan -o json | raise discover analyze\n"
            "Or use --input: raise discover analyze --input scan-result.json",
            exit_code=7,
        )
    return sys.stdin.read()


def _parse_scan_json(scan_json: str) -> ScanResult:
    """Parse scan result JSON string into ScanResult, exit on invalid JSON."""
    from raise_cli.discovery.scanner import Symbol

    try:
        scan_data: dict[str, Any] = json.loads(scan_json)
        scan_result = ScanResult(
            symbols=[],
            files_scanned=scan_data.get("files_scanned", 0),
            errors=scan_data.get("errors", []),
        )
        for sym_data in scan_data.get("symbols", []):
            scan_result.symbols.append(Symbol.model_validate(sym_data))
        return scan_result
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        cli_error(
            f"Invalid scan result JSON: {e}",
            hint="Input must be JSON from 'raise discover scan --output json'",
            exit_code=7,
        )
        raise  # unreachable, satisfies pyright


def _load_category_map(category_map_file: Path | None) -> dict[str, str] | None:
    """Load YAML category map from file, exit on errors."""
    if not category_map_file:
        return None
    if not category_map_file.exists():
        cli_error(
            f"Category map file not found: {category_map_file}",
            exit_code=4,
        )
    try:
        import yaml

        return yaml.safe_load(category_map_file.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except ImportError:
        cli_error(
            "PyYAML required for --category-map",
            hint="Install with: pip install pyyaml",
            exit_code=6,
        )
    except Exception as e:
        cli_error(f"Error reading category map: {e}", exit_code=7)
    return None  # unreachable, satisfies pyright


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
    from raise_cli.discovery.analyzer import analyze

    scan_json = _read_scan_json(input_file)
    scan_result = _parse_scan_json(scan_json)
    category_map = _load_category_map(category_map_file)

    result = analyze(scan_result, category_map=category_map)

    # Save analysis.json
    output_dir = Path("work/discovery")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "analysis.json"
    output_path.write_text(
        json.dumps(result.model_dump(), indent=2, default=str),
        encoding="utf-8",
    )

    format_analyze_result(result, output)

    if output != "json":
        console.print(f"\n[dim]Saved: {output_path}[/dim]")


def _drift_early_exit(status: str, message: str, output: str) -> None:
    """Print a drift early-exit message in the appropriate format and exit."""
    if output == "json":
        console.print_json(
            json.dumps(
                {
                    "status": status,
                    "warnings": [],
                    "warning_count": 0,
                    "message": message,
                }
            )
        )
    else:
        console.print(f"[yellow]{message}[/yellow]")
    raise typer.Exit(0)


def _load_drift_baseline(baseline_file: Path) -> list[Any]:
    """Load and parse baseline components from JSON file."""
    from raise_cli.discovery.drift import BaselineComponent

    try:
        baseline_data: dict[str, Any] = json.loads(
            baseline_file.read_text(encoding="utf-8")
        )
        baseline_dicts: list[dict[str, Any]] = baseline_data.get("components", [])
        return [BaselineComponent.model_validate(comp) for comp in baseline_dicts]
    except (json.JSONDecodeError, KeyError) as e:
        cli_error(f"Error reading baseline: {e}")
        return []  # unreachable


def _load_and_validate_baseline(baseline_file: Path, output: str) -> list[Any]:
    """Load baseline, validate it exists and has components, or exit early."""
    if not baseline_file.exists():
        if output == "json":
            _drift_early_exit("no_baseline", "No baseline components found", output)
        else:
            console.print(
                "[yellow]No baseline components found.[/yellow]\n"
                "[dim]Run /rai-discover to create a baseline first.[/dim]"
            )
            raise typer.Exit(0)

    baseline = _load_drift_baseline(baseline_file)

    if not baseline:
        if output == "json":
            _drift_early_exit("empty_baseline", "Baseline has no components", output)
        else:
            console.print(
                "[yellow]Baseline has no components.[/yellow]\n"
                "[dim]Run /rai-discover to add components.[/dim]"
            )
            raise typer.Exit(0)

    min_baseline_size = 10
    if len(baseline) < min_baseline_size and output == "human":
        console.print(
            f"[yellow]Note: Baseline has only {len(baseline)} component(s).[/yellow]\n"
            f"[dim]Drift detection works best with {min_baseline_size}+ components "
            "for meaningful patterns.[/dim]\n"
            "[dim]Run /rai-discover to expand the baseline.[/dim]\n"
        )

    return baseline


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
    from raise_cli.discovery.drift import DriftWarning, detect_drift

    root = project_root.resolve()
    scan_path = path.resolve() if path else root / "src"

    baseline_file = root / "work" / "discovery" / "components-validated.json"

    baseline = _load_and_validate_baseline(baseline_file, output)

    if not scan_path.exists():
        _drift_early_exit("no_source", f"Scan path not found: {scan_path}", output)

    scan_result = scan_directory(scan_path)

    warnings: list[DriftWarning] = detect_drift(
        baseline=baseline,
        scanned=scan_result.symbols,
    )

    format_drift_result(
        warnings=warnings,
        files_scanned=scan_result.files_scanned,
        symbols_checked=len(scan_result.symbols),
        output_format=output,
    )

    if warnings:
        raise typer.Exit(1)
