"""CLI commands for developer profile management.

This module provides the `raise profile` command group for viewing
and managing the developer profile stored in ~/.rai/developer.yaml.

Example:
    $ raise profile show    # View current profile in YAML format
    $ raise profile session # Record a new session
"""

from __future__ import annotations

from typing import Annotated

import typer
import yaml

from raise_cli.onboarding.profile import (
    DeveloperProfile,
    increment_session,
    load_developer_profile,
    save_developer_profile,
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
    """Record a new session, incrementing the session counter.

    For first-time users, creates a new developer profile.
    Use --name to provide your name when no profile exists.

    Examples:
        $ raise profile session                    # Increment session count
        $ raise profile session --name "Alice"    # First-time setup
        $ raise profile session --project /my/proj # Add project to history
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

    # Increment session
    updated = increment_session(profile, project_path=project)
    save_developer_profile(updated)

    typer.echo(
        f"Session recorded. Total sessions: {updated.sessions_total} "
        f"(last: {updated.last_session})"
    )
