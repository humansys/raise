"""CLI commands for developer profile management.

This module provides the `rai profile` command for viewing
the developer profile stored in ~/.rai/developer.yaml.

For session management, use `rai session start/close`.

Example:
    $ rai profile              # View current profile in YAML format
    $ rai profile show         # Same (backward-compat subcommand)
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
    invoke_without_command=True,
)


@profile_app.callback(invoke_without_command=True)
def profile_callback(ctx: typer.Context) -> None:
    """View developer profile. Runs 'show' when called without subcommand."""
    if ctx.invoked_subcommand is None:
        show()


@profile_app.command()
def show() -> None:
    """Display the developer profile in YAML format.

    Outputs the contents of ~/.rai/developer.yaml in human-readable YAML format.
    If no profile exists, shows a helpful message guiding the user to create one.

    Examples:
        $ rai profile
        $ rai profile show
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
