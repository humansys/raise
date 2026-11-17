"""CLI command: rai self-update — update rai + rai-mcp-pipeline (RAISE-15632).

RAISE-19635 (S19413.2): adds --channel, --version, --show-channel, --dry-run flags
and update_channel persistence in developer.yaml.
RAISE-19636 (S19413.3): safe downgrade flow — backup DB → schema rollback → verify → swap.
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import httpx
import typer
from packaging.version import Version
from rich.console import Console

from raise_cli.compat import IS_FROZEN, IS_WINDOWS
from raise_cli.core.manifest import (
    VALID_CHANNELS,
    VersionManifest,
    fetch_channel_manifest,
    fetch_manifest,
)
from raise_cli.developer_profile.persistence import save_developer_profile
from raise_cli.developer_profile.profile import load_developer_profile
from raise_cli.self_update.updater import (
    ChecksumMismatchError,
    UnsupportedPlatformError,
    backup_database,
    detect_platform_tag,
    restore_database,
    update_binaries,
)
from raise_cli.storage.connection import get_project_db_path

console = Console()

_RELEASES_BASE = "https://github.com/humansys/raise/releases/download"


def _versioned_manifest_url(target_version: str) -> str:
    """Build the version.json URL for a specific tagged release."""
    return f"{_RELEASES_BASE}/v{target_version}/version.json"


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
    mcp_path_obj = Path(mcp_path)
    if IS_WINDOWS:
        mcp_install_dir = mcp_path_obj.parent
    else:
        if not mcp_path_obj.is_symlink():
            console.print(
                "[red]Error:[/red] rai-mcp-pipeline is not installed as a symlink. "
                "Reinstall with the current install.sh before using self-update:\n"
                "  curl -fsSL https://github.com/humansys/raise/releases/latest/download/install.sh | bash"
            )
            return 1
        mcp_install_dir = mcp_path_obj.resolve().parent

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
            "To complete the update, run this command in a new terminal:\n"
            f'  cmd /c "{pending_script}"'
        )
    else:
        # After atomic_replace_dir the running process uses the new binary on disk.
        # console.print() would trigger a lazy import of rich._unicode_data via
        # PyInstaller using the old binary's offsets → zlib.error -3 (RAISE-17247).
        print(f"✓ Updated rai and rai-mcp-pipeline to {manifest.version}.")
    return 0


def apply_downgrade(
    manifest: VersionManifest,
    current_version: str,
    resolved_channel: str,
    *,
    dry_run: bool = False,
) -> int:
    """Backup DB, roll back schema, verify, then swap binaries — RAISE-19636.

    Returns 0 on success, 1 on any handled failure. Never raises typer.Exit.

    Args:
        manifest: Target version manifest (must include schema_revision).
        current_version: Currently installed version string.
        resolved_channel: Effective release channel (for display only).
        dry_run: When True, print intent and exit without touching any file.
    """
    if dry_run:
        console.print(
            f"downgrade: {current_version} → {manifest.version} ({resolved_channel}) "
            "[dry-run, nothing modified]."
        )
        return 0

    schema_revision = manifest.schema_revision
    if schema_revision is None:
        console.print(
            f"[red]Error:[/red] Cannot safely downgrade: "
            f"version {manifest.version} has no schema_revision in its manifest. "
            "Manual downgrade required."
        )
        return 1

    db_path = get_project_db_path()
    backup_path_preview = db_path.parent / f"{db_path.name}.bak-{current_version}"

    console.print(
        f"[yellow]Downgrade:[/yellow] {current_version} → {manifest.version} ({resolved_channel}).\n"
        f"Database will be backed up to: {backup_path_preview}\n"
        f"Schema will roll back to revision: {schema_revision}"
    )
    # RAISE-19413 QR R1: bare input() raises EOFError on non-interactive stdin
    # (CI, piped invocation, scripted session) — mirror the isatty guard
    # already used in cli/commands/init.py rather than let a safety-critical
    # confirmation crash with a raw traceback. Non-interactive always declines.
    if sys.stdin.isatty():
        answer = input("Continue? [y/N] ").strip().lower()
    else:
        console.print(
            "[yellow]Non-interactive session — downgrade requires an explicit "
            "y/N confirmation. Aborting.[/yellow]"
        )
        answer = "n"
    if answer != "y":
        console.print("Downgrade aborted.")
        return 1

    try:
        backup_path = backup_database(db_path, current_version)
    except OSError as exc:
        console.print(f"[red]Error:[/red] Backup failed — downgrade aborted: {exc}")
        return 1

    try:
        from raise_cli.storage.schema import _rollback_schema  # noqa: PLC0415,I001  # pyright: ignore[reportPrivateUsage]

        with sqlite3.connect(str(db_path)) as conn:
            _rollback_schema(conn, schema_revision)
    except Exception as exc:  # noqa: BLE001
        console.print(
            f"[red]Error:[/red] Schema rollback failed: {exc}\nRestoring backup..."
        )
        try:
            restore_database(backup_path, db_path)
            console.print("[green]✓[/green] Database restored from backup.")
        except OSError as restore_exc:
            console.print(
                f"[bold red]CRITICAL:[/bold red] Restore failed: {restore_exc}\n"
                f"Restore manually: cp {backup_path} {db_path}"
            )
        return 1

    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute("SELECT version_num FROM alembic_version").fetchall()

    if rows != [(schema_revision,)]:
        console.print(
            f"[red]Error:[/red] Schema verification failed: "
            f"expected {schema_revision!r}, got {rows}. Restoring backup..."
        )
        try:
            restore_database(backup_path, db_path)
            console.print("[green]✓[/green] Database restored from backup.")
        except OSError as restore_exc:
            console.print(
                f"[bold red]CRITICAL:[/bold red] Restore failed: {restore_exc}\n"
                f"Restore manually: cp {backup_path} {db_path}"
            )
        return 1

    return apply_update(manifest)


def self_update_command(  # noqa: C901
    channel: Annotated[
        str | None,
        typer.Option(
            "--channel",
            help="Release channel to use (stable|rc|alpha). Overrides the stored channel and persists it to developer.yaml.",
        ),
    ] = None,
    version_arg: Annotated[
        str | None,
        typer.Option(
            "--version",
            help="Install a specific version (e.g. 3.1.8). Does not change the stored channel.",
            show_default=False,
        ),
    ] = None,
    show_channel: Annotated[
        bool,
        typer.Option(
            "--show-channel",
            help="Print the current stored release channel and exit.",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would happen without downloading or installing anything.",
        ),
    ] = False,
) -> None:
    """Update rai and rai-mcp-pipeline to the latest release.

    With --channel, overrides the release channel for this run and persists it
    to ~/.rai/developer.yaml. Without flags, uses the stored channel (default: stable).
    """
    if not IS_FROZEN:
        console.print(
            "self-update is only available for standalone binary installs.\n"
            "You're running rai from a Python environment — update with:\n"
            "  pip install --upgrade raise-cli"
        )
        raise typer.Exit(0)

    # Load profile once — used for channel resolution and persistence.
    profile = load_developer_profile()

    # --show-channel: print current channel and exit without network.
    if show_channel:
        stored = profile.update_channel if profile is not None else "stable"
        console.print(stored)
        raise typer.Exit(0)

    # Resolve effective channel (--channel > stored > "stable").
    if channel is not None:
        if channel not in VALID_CHANNELS:
            console.print(
                f"[red]Error:[/red] Invalid channel {channel!r}. "
                f"Valid values: {', '.join(sorted(VALID_CHANNELS))}."
            )
            raise typer.Exit(1)
        resolved_channel = channel
    else:
        resolved_channel = profile.update_channel if profile is not None else "stable"
        # Guard against typos already in developer.yaml — fail-open to stable.
        if resolved_channel not in VALID_CHANNELS:
            resolved_channel = "stable"

    current_version = version("raise-cli")

    # Resolve the target manifest.
    try:
        if version_arg is not None:
            manifest = fetch_manifest(_versioned_manifest_url(version_arg))
        else:
            manifest = fetch_channel_manifest(resolved_channel)
    except httpx.HTTPStatusError as exc:
        if version_arg is not None and exc.response.status_code == 404:
            console.print(
                f"[red]Error:[/red] Version {version_arg!r} not found in releases."
            )
        else:
            console.print(
                f"[red]Error:[/red] Could not reach manifest for channel {resolved_channel!r}\n  {exc}"
            )
        raise typer.Exit(1) from None
    except httpx.HTTPError as exc:
        console.print(
            f"[red]Error:[/red] Network error fetching manifest for channel {resolved_channel!r}\n  {exc}"
        )
        raise typer.Exit(1) from None
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from None

    target_version = manifest.version

    # Persist channel preference BEFORE the version comparison so that the
    # user's intent is recorded even when the downgrade is blocked (DD3).
    if channel is not None and profile is not None:
        updated_profile = profile.model_copy(update={"update_channel": channel})
        save_developer_profile(updated_profile)

    # Sync logic: == no-op; > upgrade; < downgrade (blocked in this story).
    local_v = Version(current_version)
    target_v = Version(target_version)

    if target_v == local_v:
        console.print(f"Already up to date ({current_version}).")
        raise typer.Exit(0)

    if target_v < local_v:
        raise typer.Exit(
            apply_downgrade(
                manifest, current_version, resolved_channel, dry_run=dry_run
            )
        )

    # Upgrade path.
    if dry_run:
        console.print(
            f"upgrade: {current_version} → {target_version} ({resolved_channel}) "
            "[dry-run, nothing downloaded]."
        )
        raise typer.Exit(0)

    console.print(f"Current version: {current_version}")
    raise typer.Exit(apply_update(manifest))
