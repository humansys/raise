"""CLI commands for developer profile management.

This module provides the `raise profile` command group for viewing
the developer profile stored in ~/.rai/developer.yaml.

For session management, use `raise session start/close`.

Example:
    $ raise profile show          # View current profile in YAML format
"""

from __future__ import annotations

import typer
import yaml

from rai_cli.onboarding.profile import (
    load_developer_profile,
)

profile_app = typer.Typer(
    name="profile",
    help="View developer profile",
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
