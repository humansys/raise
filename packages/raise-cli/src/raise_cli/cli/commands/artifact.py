"""CLI commands for lifecycle artifact emission (RAISE-17507).

Provides ``rai artifact emit`` as a non-MCP path for storing structured
story artifacts in the project SQLite DB. Mirrors the MCP tool
``raise_artifact_emit`` so local_git projects (or any project where MCP
tools are unavailable) can complete the story lifecycle.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from raise_cli.artifacts.models import ARTIFACT_TYPES
from raise_cli.storage.schema import create_all

_log = logging.getLogger(__name__)

artifact_app = typer.Typer(
    name="artifact",
    help="Manage story lifecycle artifacts",
    no_args_is_help=True,
)


def _get_conn_and_pid(project: Path) -> tuple[sqlite3.Connection, str]:
    """Resolve project DB connection and project_id for the given root."""
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id

    checkout = resolve_checkout_root(project)
    conn = get_project_db(checkout)
    create_all(conn)
    return conn, get_project_id(checkout)


def emit_artifact(
    artifact_type: str,
    story_id: str,
    content: str,
    session_id: str = "",
    project: Path | None = None,
) -> str:
    """Emit a structured artifact to the project SQLite store.

    Shared implementation for both the CLI command and direct call paths.
    Returns the artifact_id on success. Raises ``typer.Exit(1)`` on validation
    errors so the CLI shows a clean error message.

    The story_id MUST be the pipeline's issue_id — the same value passed to
    pipeline_start — so the close gate can find this artifact via
    ``artifact_store.exists(run["issue_id"], artifact_type)``.
    For Jira projects: the Jira key (e.g. ``RAISE-1234``).
    For local_git projects: the local key used as issue_id.
    """
    from raise_cli.artifacts.identity import normalize_to_issue_key
    from raise_cli.artifacts.store import ArtifactStore

    if artifact_type not in ARTIFACT_TYPES:
        valid = sorted(ARTIFACT_TYPES)
        typer.echo(
            f"Error: unknown artifact type '{artifact_type}'. Valid: {valid}",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        typer.echo(f"Error: invalid JSON content — {exc}", err=True)
        raise typer.Exit(code=1) from exc

    model_cls = ARTIFACT_TYPES[artifact_type]
    try:
        validated = model_cls.model_validate(parsed)
    except ValidationError as exc:
        details = [
            {"field": ".".join(str(p) for p in e["loc"]), "error": e["msg"]}
            for e in exc.errors()
        ]
        typer.echo(
            f"Error: validation failed — {json.dumps(details, indent=2)}", err=True
        )
        raise typer.Exit(code=1) from exc

    root = project or Path.cwd()
    conn, pid = _get_conn_and_pid(root)
    canonical_id = normalize_to_issue_key(story_id, root)
    store = ArtifactStore(conn, project_id=pid)
    return store.save(
        canonical_id,
        artifact_type,
        validated,
        session_id=session_id or None,
    )


@artifact_app.command("emit")
def emit_cmd(
    artifact_type: Annotated[
        str,
        typer.Argument(
            help="Artifact type: design | plan | implement | review | retro"
        ),
    ],
    story_id: Annotated[
        str,
        typer.Option(
            "--story-id",
            "-i",
            help="Story identifier — the pipeline's issue_id as passed to "
            "pipeline_start. For Jira projects: the Jira key (e.g. RAISE-1234). "
            "For local_git projects: the local key. Must match run['issue_id'].",
        ),
    ],
    content: Annotated[
        str,
        typer.Option(
            "--content",
            "-c",
            help="JSON string with artifact fields. Schema depends on artifact_type. "
            "Pipe JSON via stdin when this option is omitted.",
        ),
    ] = "",
    session_id: Annotated[
        str,
        typer.Option("--session-id", "-s", help="Session ID for traceability."),
    ] = "",
    project: Annotated[
        Path | None,
        typer.Option(
            "--project",
            "-p",
            help="Project root path. Defaults to the current directory.",
        ),
    ] = None,
) -> None:
    """Emit a structured story artifact to the project SQLite store.

    Non-MCP fallback for ``raise_artifact_emit``. Required for local_git
    projects or any context where MCP tools are unavailable (RAISE-17507).
    """
    if not content:
        import sys

        content = sys.stdin.read()

    artifact_id = emit_artifact(
        artifact_type=artifact_type,
        story_id=story_id,
        content=content,
        session_id=session_id,
        project=project,
    )
    typer.echo(f"ok artifact_id={artifact_id}")
