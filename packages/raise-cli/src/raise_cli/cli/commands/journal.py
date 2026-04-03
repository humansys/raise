"""CLI commands for session journal — incremental memory persistence.

Provides `rai session journal add` and `rai session journal show` for
persisting and retrieving session context across compaction events.

Example:
    $ rai session journal add "Use JSONL for persistence" --type decision
    $ rai session journal show --last 5
    $ rai session journal show --compact
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import get_personal_dir
from raise_cli.onboarding.profile import load_developer_profile
from raise_cli.schemas.journal import JournalEntryType
from raise_cli.session.journal import (
    append_journal_entry,
    format_journal_compact,
    read_journal,
)

journal_app = typer.Typer(
    name="journal",
    help="Incremental session memory (decisions, insights, tasks)",
    no_args_is_help=True,
)


def _resolve_session_dir(project: str | None) -> Path:
    """Resolve the current session directory from the developer profile.

    Args:
        project: Project path override.

    Returns:
        Path to the per-session directory.

    Raises:
        typer.Exit: If no active session found.
    """
    profile = load_developer_profile()
    if profile is None:
        cli_error("No developer profile found")
        raise typer.Exit(1)  # unreachable, cli_error raises

    project_path = Path(project).resolve() if project else Path.cwd().resolve()

    # Find active session for this project
    for active in profile.active_sessions:
        if active.project and Path(active.project).resolve() == project_path:
            session_id = active.session_id
            return get_personal_dir(project_path) / "sessions" / session_id

    cli_error(
        "No active session for this project",
        hint="Start a session first: rai session start --project .",
    )
    raise typer.Exit(1)  # unreachable


@journal_app.command()
def add(
    content: Annotated[
        str,
        typer.Argument(help="Content to persist"),
    ],
    entry_type: Annotated[
        JournalEntryType,
        typer.Option(
            "--type",
            "-t",
            help="Entry type (decision, insight, task_done, note)",
        ),
    ] = JournalEntryType.NOTE,
    tags: Annotated[
        str | None,
        typer.Option(
            "--tags",
            help="Comma-separated tags (e.g., 'arch,spike')",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
) -> None:
    """Add a journal entry to the current session.

    Examples:
        $ rai session journal add "Use JSONL for journal" --type decision
        $ rai session journal add "T1 complete" --type task_done
        $ rai session journal add "Compaction loses rationale" --type insight --tags "compaction,memory"
    """
    session_dir = _resolve_session_dir(project)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    result = append_journal_entry(
        session_dir=session_dir,
        entry_type=entry_type,
        content=content,
        tags=tag_list,
    )

    typer.echo(f"{result.id}: {entry_type.value} recorded")


@journal_app.command()
def show(
    last: Annotated[
        int | None,
        typer.Option(
            "--last",
            "-n",
            help="Show only the last N entries",
        ),
    ] = None,
    compact: Annotated[
        bool,
        typer.Option(
            "--compact",
            help="Output compact format for context injection",
        ),
    ] = False,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
) -> None:
    """Show journal entries for the current session.

    With --compact, outputs a token-efficient format suitable for
    post-compaction context injection via hooks.

    Examples:
        $ rai session journal show
        $ rai session journal show --last 5
        $ rai session journal show --compact
    """
    session_dir = _resolve_session_dir(project)
    entries = read_journal(session_dir, last_n=last)

    if compact:
        typer.echo(format_journal_compact(entries))
    else:
        if not entries:
            typer.echo("No journal entries.")
            return
        for entry in entries:
            tag_suffix = f" [{', '.join(entry.tags)}]" if entry.tags else ""
            typer.echo(
                f"[{entry.id}] {entry.entry_type.value}: {entry.content}{tag_suffix}"
            )
