"""Manifest CLI command group — validate and manage .raise/manifest.yaml."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console

from raise_cli.onboarding.manifest_validate import (
    KNOWN_PROJECT_KEY_PATHS,
    validate_manifest_project_keys,
)

manifest_app = typer.Typer(
    name="manifest",
    help="Manage .raise/manifest.yaml",
    no_args_is_help=True,
)

console = Console()


@manifest_app.command("validate")
def validate_command(
    project: Annotated[
        Path,
        typer.Option(
            "--project", "-p", help="Project root (default: current directory)"
        ),
    ] = Path("."),
) -> None:
    """Validate project.* keys in .raise/manifest.yaml against ADR-071 known set.

    Exits 0 when the manifest is valid or absent.
    Exits 1 when unknown project.* keys are found or the manifest cannot be parsed.
    """
    project = project.resolve()
    manifest_path = project / ".raise" / "manifest.yaml"

    if not manifest_path.exists():
        console.print(
            "[dim]No .raise/manifest.yaml found - no project.* keys to validate[/dim]"
        )
        raise typer.Exit(0)

    unknown, total, parse_error = validate_manifest_project_keys(project)

    if parse_error is not None:
        console.print(
            f"[red]FAIL[/red] Cannot parse .raise/manifest.yaml: {parse_error}"
        )
        raise typer.Exit(1)

    if not unknown:
        if total == 0:
            console.print(
                "[green]OK[/green] Manifest valid (no project.* keys to validate)"
            )
        else:
            console.print(
                f"[green]OK[/green] Manifest valid"
                f" ({total} project.* key{'s' if total != 1 else ''} validated)"
            )
        raise typer.Exit(0)

    console.print(f"[red]FAIL[/red] Unknown project.* keys ({len(unknown)}):")
    for path in sorted(unknown):
        console.print(f"  {path}")
    hint = ", ".join(
        sorted(
            KNOWN_PROJECT_KEY_PATHS
            - {
                "name",
                "project_type",
                "language",
                "test_command",
                "lint_command",
                "type_check_command",
                "format_command",
                "code_file_count",
                "detected_at",
                "apps",
            }
        )
    )
    console.print(f"  [dim]Valid ADR-071 keys: {hint}[/dim]")
    raise typer.Exit(1)


@manifest_app.command("env")
def env_command(
    project: Annotated[
        Path,
        typer.Option(
            "--project", "-p", help="Project root (default: current directory)"
        ),
    ] = Path("."),
) -> None:
    """Output project.* section of .raise/manifest.yaml as JSON for shell consumption.

    Exits 0 always. Outputs '{}' when manifest is absent or unparseable.
    Parse warnings go to stderr to avoid contaminating shell variable captures.

    Usage in skills (ADR-074 D2):
        _CFG=$(rai manifest env)
    """
    manifest_path = project.resolve() / ".raise" / "manifest.yaml"
    if not manifest_path.exists():
        print("{}")
        raise typer.Exit(0)
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        # RAISE-14653: expose 'branches' (root-level) alongside 'project' so that
        # skill bash blocks can read branches.development without falling back to 'main'.
        section = {
            **(data.get("project", {}) or {}),
            "branches": data.get("branches", {}) or {},
        }
        print(json.dumps(section))
    except Exception as e:  # noqa: BLE001
        typer.echo(f"⚠ manifest parse failed: {e}", err=True)
        print("{}")
    raise typer.Exit(0)
