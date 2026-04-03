"""CLI commands for learning record management.

Commands:
- write: Validate and write a learning record to disk
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.memory.learning import LearningRecord, write_record

learn_app = typer.Typer(
    name="learn",
    help="Manage learning records",
    no_args_is_help=True,
)

console = Console()


@learn_app.command("write")
def write(
    yaml_file: Annotated[
        Path,
        typer.Argument(help="Path to YAML file containing the learning record"),
    ],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory"),
    ] = Path("."),
) -> None:
    """Validate a learning record from YAML and write it to disk.

    Reads the YAML file, validates against the LearningRecord schema, and
    writes to .raise/rai/learnings/{skill}/{work_id}/record.yaml.

    Examples:
        $ rai learn write /tmp/record.yaml
        $ rai learn write record.yaml --project /path/to/project
    """
    if not yaml_file.exists():
        cli_error(
            f"File not found: {yaml_file}",
            hint="Check the file path and try again.",
            exit_code=1,
        )

    try:
        raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        cli_error(
            f"Failed to parse YAML: {exc}",
            hint="Check that the file contains valid YAML syntax.",
            exit_code=1,
        )

    if not isinstance(raw, dict):
        cli_error(
            "YAML file must contain a mapping (dictionary), not a scalar or list.",
            exit_code=1,
        )

    try:
        record = LearningRecord.model_validate(raw)
    except ValidationError as exc:
        fields = ", ".join(
            str(e["loc"][0]) if e.get("loc") else "unknown" for e in exc.errors()
        )
        cli_error(
            f"Validation error on field(s): {fields}",
            hint=str(exc),
            exit_code=7,
        )

    result_path = write_record(record, project.resolve())
    console.print(
        f"\n[green]✓[/green] Learning record written: "
        f"[bold]{record.skill}[/bold] / [bold]{record.work_id}[/bold]"
    )
    console.print(f"[dim]Saved to: {result_path}[/dim]\n")
