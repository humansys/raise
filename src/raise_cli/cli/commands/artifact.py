"""CLI commands for artifact validation.

Provides ``rai artifact validate`` for checking YAML artifacts
against the Pydantic type registry.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.artifacts.reader import read_artifact

artifact_app = typer.Typer(
    name="artifact",
    help="Manage skill artifacts",
    no_args_is_help=True,
)

console = Console()


def _resolve_project_root() -> Path:
    """Resolve the project root from env or cwd."""
    env_root = os.environ.get("RAI_PROJECT_ROOT")
    if env_root:
        return Path(env_root)
    return Path.cwd()


@artifact_app.command("validate")
def validate_command(
    file: Annotated[
        str | None,
        typer.Option("--file", help="Path to a single artifact file to validate"),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """Validate YAML artifacts against their Pydantic schemas.

    Reads all .yaml files from .raise/artifacts/ (or a single file with --file)
    and validates each against the type registry.

    Exit code 0 if all pass, 1 if any fail.

    Examples:
        $ rai artifact validate
        $ rai artifact validate --file .raise/artifacts/s354.1-design.yaml
        $ rai artifact validate --format json
    """
    if file:
        paths = _resolve_single_file(Path(file), format)
    else:
        paths = _resolve_all_artifacts(format)

    if paths is None:
        return  # Already handled (exit raised)

    results: list[dict[str, object]] = []
    for path in paths:
        try:
            read_artifact(path)
            results.append({"file": path.name, "passed": True, "error": None})
        except Exception as exc:  # noqa: BLE001
            results.append({"file": path.name, "passed": False, "error": str(exc)})

    failed = [r for r in results if not r["passed"]]

    if format == "json":
        typer.echo(
            json.dumps(
                {"results": results, "all_passed": len(failed) == 0},
                indent=2,
            )
        )
    else:
        for r in results:
            marker = "[green]{CHECK}[/green]" if r["passed"] else "[red]{CROSS}[/red]"
            console.print(f"  {marker} {r['file']}")
            if r["error"]:
                # Show first line of error only
                first_line = str(r["error"]).split("\n")[0]
                console.print(f"    {first_line}")
        console.print()
        if failed:
            console.print(
                f"[red bold]FAILED:[/red bold] {len(failed)} of {len(results)} artifacts invalid"
            )
        else:
            console.print(
                f"[green bold]PASSED:[/green bold] {len(results)} artifact(s) valid"
            )

    raise typer.Exit(1 if failed else 0)


def _resolve_single_file(path: Path, fmt: str) -> list[Path] | None:
    """Resolve a single file path, handling not-found."""
    if not path.exists():
        if fmt == "json":
            typer.echo(json.dumps({"error": f"File not found: {path}"}))
        else:
            console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)
    return [path]


def _resolve_all_artifacts(fmt: str) -> list[Path] | None:
    """Resolve all artifact files from .raise/artifacts/."""
    root = _resolve_project_root()
    artifacts_dir = root / ".raise" / "artifacts"

    if not artifacts_dir.is_dir():
        if fmt == "json":
            typer.echo(
                json.dumps(
                    {"results": [], "all_passed": True, "message": "No artifacts found"}
                )
            )
        else:
            console.print("No artifacts found in .raise/artifacts/")
        raise typer.Exit(0)

    paths = sorted(artifacts_dir.glob("*.yaml"))
    if not paths:
        if fmt == "json":
            typer.echo(
                json.dumps(
                    {"results": [], "all_passed": True, "message": "No artifacts found"}
                )
            )
        else:
            console.print("No artifacts found in .raise/artifacts/")
        raise typer.Exit(0)

    return paths
