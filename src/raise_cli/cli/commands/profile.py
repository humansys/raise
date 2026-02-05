"""CLI commands for developer profile management.

This module provides the `raise profile` command group for viewing
and managing the developer profile stored in ~/.rai/developer.yaml.

Example:
    $ raise profile show        # View current profile in YAML format
    $ raise profile session     # Start/record a new session
    $ raise profile session-end # End the current session
"""

from __future__ import annotations

from typing import Annotated

import typer
import yaml

from raise_cli.onboarding.profile import (
    DeveloperProfile,
    end_session,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
)

profile_app = typer.Typer(
    name="profile",
    help="View and manage developer profile",
    no_args_is_help=True,
)


@profile_app.command()
def show() -> None:
    """Display the developer profile in YAML format.

    Outputs the contents of ~/.rai/developer.yaml in human-readable YAML format.
    If no profile exists, shows a helpful message guiding the user to create one.

    Examples:
        $ raise profile show
    """
    profile = load_developer_profile()

    if profile is None:
        typer.echo(
            "No developer profile found. Run `raise init` in a project to create one."
        )
        return

    # Convert to dict and output as YAML
    data = profile.model_dump(mode="json")
    output = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    typer.echo(output.rstrip())


@profile_app.command()
def session(
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
    """Start a new session, incrementing the session counter.

    Checks for orphaned sessions (started but not closed) and warns if found.
    For first-time users, creates a new developer profile.

    Examples:
        $ raise profile session                    # Start session
        $ raise profile session --name "Alice"    # First-time setup
        $ raise profile session --project /my/proj # Start with project path
    """
    profile = load_developer_profile()

    if profile is None:
        # First-time user - need name to create profile
        if name is None:
            typer.echo(
                "No developer profile found. Provide --name for first-time setup:\n"
                "  raise profile session --name 'Your Name'"
            )
            raise typer.Exit(1)

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


@profile_app.command(name="session-end")
def session_end() -> None:
    """End the current session, clearing the active session state.

    Call this at the end of /session-close to mark the session as properly closed.
    If no session is active, this is a no-op.

    Examples:
        $ raise profile session-end
    """
    profile = load_developer_profile()

    if profile is None:
        typer.echo("No developer profile found.")
        raise typer.Exit(1)

    if profile.current_session is None:
        typer.echo("No active session to end.")
        return

    updated = end_session(profile)
    save_developer_profile(updated)

    typer.echo("Session ended.")
