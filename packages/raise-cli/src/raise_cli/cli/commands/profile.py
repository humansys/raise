"""CLI commands for developer profile management.

This module provides the `rai profile` command for viewing, exporting,
and importing the developer profile stored in ~/.rai/developer.yaml.

For session management, use `rai session start/close`.

Example:
    $ rai profile              # View current profile in YAML format
    $ rai profile show         # Same (backward-compat subcommand)
    $ rai profile export       # Export portable bundle to stdout
    $ rai profile import bundle.yaml  # Import from bundle
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import yaml

from raise_cli.onboarding.profile import (
    load_developer_profile,
    save_developer_profile,
)
from raise_cli.onboarding.profile_portability import (
    export_profile,
    import_profile,
    parse_bundle,
    serialize_bundle,
)

profile_app = typer.Typer(
    name="profile",
    help="View and manage developer profile",
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


@profile_app.command("export")
def export_cmd(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write bundle to file instead of stdout"),
    ] = None,
) -> None:
    """Export developer profile as a portable YAML bundle.

    Strips machine-local state (active sessions, projects) and adds
    export metadata. Output goes to stdout by default (pipeable).

    Examples:
        $ rai profile export
        $ rai profile export --output ~/profile-bundle.yaml
    """
    profile = load_developer_profile()
    if profile is None:
        typer.echo("No developer profile found. Nothing to export.", err=True)
        raise typer.Exit(1)

    bundle = export_profile(profile)
    yaml_str = serialize_bundle(bundle)

    if output is not None:
        output.write_text(yaml_str, encoding="utf-8")
        typer.echo(f"Profile exported to {output}")
    else:
        typer.echo(yaml_str.rstrip())


@profile_app.command("import")
def import_cmd(
    path: Annotated[Path, typer.Argument(help="Path to profile bundle YAML")],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Overwrite existing profile without confirmation"
        ),
    ] = False,
) -> None:
    """Import developer profile from a portable YAML bundle.

    Restores identity on a new machine. Machine-local state (active sessions,
    projects) is cleared regardless of bundle content.

    Examples:
        $ rai profile import ~/profile-bundle.yaml
        $ rai profile import ~/profile-bundle.yaml --force
    """
    if not path.exists():
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    try:
        bundle = parse_bundle(content)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)  # noqa: B904

    # Check for existing profile
    existing = load_developer_profile()
    if existing is not None and not force:
        confirm = typer.confirm(
            f"Profile for '{existing.name}' already exists. Overwrite?"
        )
        if not confirm:
            typer.echo("Import cancelled.")
            raise typer.Exit(0)

    profile = import_profile(bundle)
    save_developer_profile(profile)
    typer.echo(
        f"Profile imported from {bundle.meta.source_machine} "
        f"(exported {bundle.meta.exported_at:%Y-%m-%d})."
    )
