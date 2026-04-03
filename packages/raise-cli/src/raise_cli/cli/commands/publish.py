"""Backward-compatible aliases for commands moved to the release group.

All active commands have been moved to the `release` group (CLI restructuring):
- publish check → release check
- publish release → release publish

These aliases print deprecation warnings and delegate to the canonical commands.
They will be removed in a future release (v3.0).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.publish.version import BumpType

publish_app = typer.Typer(help="Publish and release management commands")

_stderr_console = Console(stderr=True)


def _deprecation_warning(old_cmd: str, new_cmd: str) -> None:
    """Print deprecation warning to stderr."""
    _stderr_console.print(
        f"[yellow]DEPRECATED:[/yellow] 'rai {old_cmd}' → use 'rai {new_cmd}' instead",
    )


@publish_app.command("check")
def check_shim(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """Deprecated: use 'rai release check'."""
    _deprecation_warning("publish check", "release check")
    from raise_cli.cli.commands.release import check_command

    check_command(project=project)


@publish_app.command("release")
def release_shim(
    bump: Annotated[
        BumpType | None,
        typer.Option("--bump", "-b", help="Version bump type"),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option("--version", "-v", help="Explicit version (overrides --bump)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would happen without executing"),
    ] = False,
    skip_check: Annotated[
        bool,
        typer.Option("--skip-check", help="Skip quality gates (dangerous)"),
    ] = False,
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """Deprecated: use 'rai release publish'."""
    _deprecation_warning("publish release", "release publish")
    from raise_cli.cli.commands.release import publish_command

    publish_command(
        bump=bump,
        version=version,
        dry_run=dry_run,
        skip_check=skip_check,
        project=project,
    )
