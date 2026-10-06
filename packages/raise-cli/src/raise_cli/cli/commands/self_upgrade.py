"""CLI command: rai self-upgrade — package + project in one command (RAISE-15662).

Orchestrates two commands that already exist, in the order that matters:
package (`self-update`'s apply_update) before project (`upgrade`'s
upgrade_command). Neither layer's internal contract is modified here.
"""

from __future__ import annotations

from importlib.metadata import version as _pkg_version
from typing import Annotated

import httpx
import typer
from rich.console import Console

from raise_cli.cli.commands.init import upgrade_command
from raise_cli.cli.commands.self_update import IS_FROZEN, apply_update
from raise_cli.self_update.manifest import MANIFEST_URL, fetch_manifest, is_newer

console = Console()

_RELEASES_BASE = "https://github.com/humansys/raise/releases/download"


def _versioned_manifest_url(target_version: str) -> str:
    """Build the version.json URL for a specific tagged release (not 'latest')."""
    return f"{_RELEASES_BASE}/v{target_version}/version.json"


def _package_layer(*, requested_version: str | None, dry_run: bool) -> bool:
    """Update the frozen binary package layer. Returns True if it changed.

    Mirrors self_update_command()'s own IS_FROZEN / already-up-to-date checks
    so pip installs and no-op upgrades behave identically here and there.
    """
    if not IS_FROZEN:
        console.print(
            "self-upgrade's package layer is only available for standalone "
            "binary installs.\nYou're running rai from a Python environment — "
            "update the package with:\n  pip install --upgrade raise-cli"
        )
        return False

    current_version = _pkg_version("raise-cli")
    manifest_url = (
        MANIFEST_URL
        if requested_version is None
        else _versioned_manifest_url(requested_version)
    )

    try:
        manifest = fetch_manifest(manifest_url)
    except httpx.HTTPStatusError as exc:
        if requested_version is not None and exc.response.status_code == 404:
            console.print(
                f"[red]Error:[/red] version {requested_version} does not exist "
                f"in the release registry ({manifest_url})."
            )
            raise typer.Exit(1) from None
        console.print(f"[red]Error:[/red] Could not reach {manifest_url}\n  {exc}")
        raise typer.Exit(1) from None
    except httpx.HTTPError as exc:
        console.print(f"[red]Error:[/red] Could not reach {manifest_url}\n  {exc}")
        raise typer.Exit(1) from None

    nothing_to_do = (
        manifest.version == current_version
        if requested_version is not None
        else not is_newer(remote=manifest.version, local=current_version)
    )
    if nothing_to_do:
        console.print(f"Package already up to date ({current_version}).")
        return False

    if dry_run:
        console.print(
            f"[package] {current_version} -> {manifest.version} available "
            "(dry-run, nothing downloaded)."
        )
        return False

    console.print(f"Current version: {current_version}")
    exit_code = apply_update(manifest)
    if exit_code != 0:
        raise typer.Exit(exit_code)
    return True


def self_upgrade_command(
    version: Annotated[
        str | None,
        typer.Option(
            "--version",
            help="Specific version to upgrade to (default: latest published).",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview package + project changes without writing anything.",
        ),
    ] = False,
) -> None:
    """Update the rai package and the project in one command, in the right order.

    Calls the package layer (self-update's apply_update) before the project
    layer (upgrade's upgrade_command) — reversing the order would sync the
    project against a stale package. Prints a restart notice only when the
    package actually changed: the MCP server keeps the previous binary in
    memory even after `rai --version` reports the new one.
    """
    package_changed = _package_layer(requested_version=version, dry_run=dry_run)

    upgrade_command(dry_run=dry_run)

    if package_changed:
        console.print(
            "\n[yellow]⚠[/yellow]  Restart your agent session — the MCP server "
            "keeps the previous binary in memory even though rai --version now "
            "reports the new one."
        )
