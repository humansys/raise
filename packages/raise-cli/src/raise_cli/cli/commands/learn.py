"""CLI commands for learning record management.

Commands:
- write: Validate and write a learning record to disk
- push: Push learning records to raise-server
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Annotated

import httpx
import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.memory.learning import LearningRecord, write_record
from raise_cli.memory.push import LearningPushClient, is_pushed, write_push_marker

logger = logging.getLogger(__name__)

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


def _get_server_config() -> tuple[str, str]:
    """Read server URL and API key from environment.

    Returns:
        (server_url, api_key) tuple.

    Raises:
        SystemExit: If either env var is missing.
    """
    server_url = os.environ.get("RAI_SERVER_URL", "").strip()
    api_key = os.environ.get("RAI_API_KEY", "").strip()
    if not server_url or not api_key:
        cli_error(
            "Server not configured. Set RAI_SERVER_URL and RAI_API_KEY.",
            hint="Example: export RAI_SERVER_URL=http://localhost:8000",
            exit_code=1,
        )
    return server_url, api_key


_HTTP_ERROR_MESSAGES: dict[int, str] = {
    401: "Authentication failed. Check RAI_API_KEY.",
    403: "Server requires 'team' plan. Check license.",
}


def _format_http_error(exc: httpx.HTTPStatusError) -> str:
    status = exc.response.status_code
    if status in _HTTP_ERROR_MESSAGES:
        return _HTTP_ERROR_MESSAGES[status]
    if status == 422:
        return f"Server rejected: {exc.response.text}"
    return f"Server error ({status}): {exc.response.text}"


def _try_push(client: LearningPushClient, record: LearningRecord, label: str) -> uuid.UUID | None:
    """Attempt the HTTP push. Returns server_id or None on failure."""
    try:
        return client.push(record)
    except httpx.ConnectError:
        console.print(f"[red]✗[/red] Cannot reach server at {client.server_url}: [dim]{label}[/dim]")
    except httpx.TimeoutException:
        console.print(f"[red]✗[/red] Request timed out: [dim]{label}[/dim]")
    except httpx.HTTPStatusError as exc:
        console.print(f"[red]✗[/red] {_format_http_error(exc)}")
    except Exception:
        logger.exception("Unexpected error pushing %s", label)
        console.print(f"[red]✗[/red] Unexpected error: [dim]{label}[/dim]")
    return None


def _push_single(
    client: LearningPushClient,
    record_path: Path,
) -> str | None:
    """Push a single record file.

    Returns:
        "pushed" on success, "skipped" if already pushed, None on failure.
        Never calls cli_error — callers decide whether to exit or continue.
    """
    record_dir = record_path.parent
    label = f"{record_dir.parent.name}/{record_dir.name}"

    if is_pushed(record_dir):
        console.print(f"[yellow]⏭[/yellow] Already pushed: [dim]{label}[/dim]")
        return "skipped"

    raw = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        console.print(f"[red]✗[/red] Invalid record: {record_path}")
        return None

    try:
        record = LearningRecord.model_validate(raw)
    except ValidationError as exc:
        console.print(f"[red]✗[/red] Validation error: {exc}")
        return None

    server_id = _try_push(client, record, label)
    if server_id is None:
        return None

    write_push_marker(record_dir, server_id)
    console.print(
        f"[green]✓[/green] Pushed: "
        f"[bold]{record.skill}[/bold] / [bold]{record.work_id}[/bold] "
        f"[dim](id: {server_id})[/dim]"
    )
    return "pushed"


def _push_all(client: LearningPushClient, project: Path) -> None:
    """Push all unpushed learning records under project root."""
    learnings_dir = project.resolve() / ".raise" / "rai" / "learnings"
    if not learnings_dir.exists():
        console.print("[dim]No learning records found.[/dim]")
        return

    records = sorted(learnings_dir.glob("*/*/record.yaml"))
    if not records:
        console.print("[dim]No learning records found.[/dim]")
        return

    pushed = 0
    skipped = 0
    failed = 0
    for record_file in records:
        result = _push_single(client, record_file)
        if result == "pushed":
            pushed += 1
        elif result == "skipped":
            skipped += 1
        else:
            failed += 1

    console.print(
        f"\n[bold]Summary:[/bold] {pushed} pushed, {skipped} skipped, {failed} failed"
    )
    if failed:
        raise typer.Exit(code=1)


@learn_app.command("push")
def push(
    path: Annotated[
        Path | None,
        typer.Argument(help="Path to a specific record.yaml to push"),
    ] = None,
    all_records: Annotated[
        bool,
        typer.Option("--all", help="Push all unpushed records"),
    ] = False,
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory"),
    ] = Path("."),
) -> None:
    """Push learning records to raise-server.

    Sends learning records as agent events to the raise-server endpoint.
    Records are validated locally before push. Already-pushed records
    are skipped (idempotent).

    Examples:
        $ rai learn push .raise/rai/learnings/rai-story-design/S100.1/record.yaml
        $ rai learn push --all
    """
    if not path and not all_records:
        cli_error(
            "Provide a record path or use --all to push all unpushed records.",
            exit_code=1,
        )

    server_url, api_key = _get_server_config()
    client = LearningPushClient(server_url, api_key)

    try:
        if path:
            if not path.exists():
                cli_error(f"File not found: {path}", exit_code=1)
            result = _push_single(client, path)
            if result is None:
                raise typer.Exit(code=1)
        else:
            _push_all(client, project)
    finally:
        client.close()
