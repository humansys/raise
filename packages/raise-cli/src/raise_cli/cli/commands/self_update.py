"""CLI command: rai self-update — update rai + rai-mcp-pipeline (RAISE-15632)."""

from __future__ import annotations

import shutil
import sys
from importlib.metadata import version
from pathlib import Path

import httpx
import typer
from rich.console import Console

from raise_cli.compat import IS_FROZEN
from raise_cli.self_update.manifest import (
    MANIFEST_URL,
    VersionManifest,
    fetch_manifest,
    is_newer,
)
from raise_cli.self_update.updater import (
    ChecksumMismatchError,
    UnsupportedPlatformError,
    detect_platform_tag,
    update_binaries,
)

console = Console()


def apply_update(manifest: VersionManifest) -> int:
    """Download, verify, and swap to the release described by `manifest`.

    Caller (self_update_command, or the session-open interactive prompt —
    RAISE-15715) already knows `manifest.version` is newer than what's
    installed. Returns 0 on success, 1 on any handled failure — never
    raises `typer.Exit` so it stays usable outside a typer command.
    """
    try:
        platform_tag = detect_platform_tag()
    except UnsupportedPlatformError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        return 1

    platform_artifact = manifest.platforms.get(platform_tag)
    if platform_artifact is None:
        console.print(
            f"[red]Error:[/red] No release published for platform '{platform_tag}'."
        )
        return 1

    rai_install_dir = Path(sys.executable).parent
    mcp_path = shutil.which("rai-mcp-pipeline")
    if mcp_path is None:
        console.print("[red]Error:[/red] rai-mcp-pipeline not found on PATH.")
        return 1
    mcp_install_dir = Path(mcp_path).parent

    console.print(f"Latest version:  {manifest.version}")

    with console.status(
        f"Downloading and verifying rai + rai-mcp-pipeline ({platform_tag})..."
    ):
        try:
            pending_script = update_binaries(
                platform_artifact=platform_artifact,
                rai_install_dir=rai_install_dir,
                mcp_install_dir=mcp_install_dir,
            )
        except ChecksumMismatchError as exc:
            console.print(f"[red]Error:[/red] {exc}\nNo binaries were changed.")
            return 1
        except httpx.HTTPError as exc:
            console.print(
                f"[red]Error:[/red] Download failed: {exc}\nNo binaries were changed."
            )
            return 1

    if pending_script is not None:
        console.print(
            f"[green]✓[/green] Downloaded and verified {manifest.version}. "
            "Swap will finish after rai exits."
        )
    else:
        console.print(
            f"[green]✓[/green] Updated rai and rai-mcp-pipeline to {manifest.version}."
        )
    return 0


def self_update_command() -> None:
    """Update rai and rai-mcp-pipeline to the latest release."""
    if not IS_FROZEN:
        console.print(
            "self-update is only available for standalone binary installs.\n"
            "You're running rai from a Python environment — update with:\n"
            "  pip install --upgrade raise-cli"
        )
        raise typer.Exit(0)

    current_version = version("raise-cli")

    try:
        manifest = fetch_manifest(MANIFEST_URL)
    except httpx.HTTPError as exc:
        console.print(f"[red]Error:[/red] Could not reach {MANIFEST_URL}\n  {exc}")
        raise typer.Exit(1) from None

    if not is_newer(remote=manifest.version, local=current_version):
        console.print(f"Already up to date ({current_version}).")
        raise typer.Exit(0)

    console.print(f"Current version: {current_version}")
    raise typer.Exit(apply_update(manifest))
