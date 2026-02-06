"""CLI commands for session management.

This module provides the `raise session` command group for managing
working sessions — the lifecycle of a developer's focused work period.

Sessions are first-class workflow state, distinct from:
- Profile (developer identity)
- Memory (persistent knowledge)

Example:
    $ raise session start              # Start a new session
    $ raise session close              # End the current session
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from raise_cli.cli.error_handler import cli_error
from raise_cli.memory.writer import validate_session_index
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    end_session,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
)

session_app = typer.Typer(
    name="session",
    help="Manage working sessions",
    no_args_is_help=True,
)


@session_app.command()
def start(
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Your name (required for first-time setup)",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path to associate with this session",
        ),
    ] = None,
) -> None:
    """Start a new working session.

    Increments the session counter and sets active session state.
    Checks for orphaned sessions (started but not closed) and warns if found.
    For first-time users, creates a new developer profile.

    Examples:
        $ raise session start                    # Start session
        $ raise session start --name "Alice"    # First-time setup
        $ raise session start --project /my/proj # Start with project path
    """
    profile = load_developer_profile()

    if profile is None:
        # First-time user - need name to create profile
        if name is None:
            cli_error(
                "No developer profile found",
                hint="Provide --name for first-time setup: raise session start --name 'Your Name'",
            )
            return  # cli_error raises, but this helps pyright

        # Create new profile
        profile = DeveloperProfile(name=name)
        typer.echo(f"Welcome to RaiSE, {name}! Creating your developer profile...")

    # Check for active session
    if profile.current_session is not None:
        prev = profile.current_session
        if prev.is_stale():
            typer.echo(
                f"Warning: Stale session detected (started {prev.started_at.date()}, "
                f"project: {prev.project})\n"
                "Previous session was not closed. Learnings may have been lost.\n"
                "Tip: Use /session-close before ending work."
            )
        else:
            typer.echo(
                f"Note: Session already active (project: {prev.project})\n"
                "Starting new session anyway. Previous session not closed."
            )

    # Jidoka: Validate session index if project specified
    if project is not None:
        memory_dir = Path(project) / ".raise" / "rai" / "memory"
        if memory_dir.exists():
            validation = validate_session_index(memory_dir)
            if not validation.is_valid:
                typer.echo(f"Warning: {validation.summary()}")
                typer.echo("Run `raise memory validate` to fix data quality issues.\n")

    # Increment session count
    updated = increment_session(profile, project_path=project)

    # Set active session state
    if project is not None:
        updated = start_session(updated, project)

    save_developer_profile(updated)

    typer.echo(
        f"Session recorded. Total sessions: {updated.sessions_total} "
        f"(last: {updated.last_session})"
    )


@session_app.command()
def close() -> None:
    """End the current working session.

    Clears the active session state. Call this at the end of /session-close
    to mark the session as properly closed.

    If no session is active, this is a no-op.

    Examples:
        $ raise session close
    """
    profile = load_developer_profile()

    if profile is None:
        cli_error("No developer profile found")
        return  # cli_error raises, but this helps pyright

    if profile.current_session is None:
        typer.echo("No active session to close.")
        return

    updated = end_session(profile)
    save_developer_profile(updated)

    typer.echo("Session closed.")
