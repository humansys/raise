"""CLI commands for governance artifact sync (S5708.2 — ADR-076).

Commands:
- sync: One-shot scan + push governance artifacts to raise-server
- sync --watch: Polling loop that auto-pushes on change detection
- hook install: Install git post-commit hook for auto-sync
"""

import logging
import stat
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.governance.sync import (
    scan_governance_artifacts,
    sync_to_server,
)
from raise_cli.output.symbols import ARROW, CHECK, CROSS

logger = logging.getLogger(__name__)

governance_app = typer.Typer(
    name="governance",
    help="Governance artifact sync",
    no_args_is_help=True,
)

hook_app = typer.Typer(
    name="hook",
    help="Git hook management for governance sync",
    no_args_is_help=True,
)
governance_app.add_typer(hook_app, name="hook")

console = Console()

_POST_COMMIT_HOOK_BODY = """\
#!/bin/sh
# RaiSE governance auto-sync (S5708.2)
# Triggers governance sync to raise-server on commit.
rai governance sync --quiet 2>/dev/null || true
"""


@governance_app.command("sync")
def sync(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory"),
    ] = Path("."),
    watch: Annotated[
        bool,
        typer.Option("--watch", "-w", help="Poll for changes and auto-sync"),
    ] = False,
    interval: Annotated[
        int,
        typer.Option(
            "--interval", "-i", help="Poll interval in seconds (0 to disable)"
        ),
    ] = 300,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress output (for hook usage)"),
    ] = False,
) -> None:
    """Sync governance artifacts to raise-server.

    Scans the governance directory, computes content hashes, and POSTs
    to /api/v2/governance/reconcile.

    Examples:
        $ rai governance sync
        $ rai governance sync --watch --interval 60
        $ rai governance sync --quiet
    """
    project = project.resolve()

    if watch:
        if interval <= 0:
            if not quiet:
                console.print("[yellow]Watch disabled (interval=0)[/yellow]")
            return
        _watch_loop(project, interval, quiet)
    else:
        _sync_once(project, quiet)


def _sync_once(project_root: Path, quiet: bool) -> None:
    """Execute a single sync cycle."""
    try:
        result = sync_to_server(project_root)
        if result is None:
            if not quiet:
                console.print(
                    f"[yellow]{CROSS}[/yellow] Sync skipped "
                    "(server not configured or no artifacts)"
                )
            return
        if not quiet:
            new = result.get("new", 0)
            changed = result.get("changed", 0)
            deleted = result.get("deleted", 0)
            skipped = result.get("skipped", 0)
            console.print(
                f"[green]{CHECK}[/green] Governance sync complete "
                f"{ARROW} new: {new}, changed: {changed}, "
                f"deleted: {deleted}, skipped: {skipped}"
            )
    except Exception as exc:
        if not quiet:
            console.print(f"[red]{CROSS}[/red] Sync failed: {exc}")
        logger.error("Governance sync failed", exc_info=True)


def _watch_loop(project_root: Path, interval: int, quiet: bool) -> None:
    """Poll for governance changes and sync periodically."""
    if not quiet:
        console.print(
            f"Governance sync watch started (interval: {interval}s). Ctrl+C to stop."
        )

    last_hashes: dict[str, str] = {}

    try:
        while True:
            artifacts = scan_governance_artifacts(project_root)
            current_hashes = {a.path: a.content_hash for a in artifacts}

            if current_hashes != last_hashes:
                if last_hashes and not quiet:
                    console.print(
                        f"[dim]{time.strftime('%H:%M:%S')}[/dim] "
                        f"Changes detected {ARROW} syncing..."
                    )
                _sync_once(project_root, quiet)
                last_hashes = current_hashes
            elif not quiet:
                console.print(
                    f"[dim]{time.strftime('%H:%M:%S')}[/dim] "
                    f"No changes ({len(artifacts)} artifacts)"
                )

            time.sleep(interval)
    except KeyboardInterrupt:
        if not quiet:
            console.print("\nStopped.")


@hook_app.command("install")
def hook_install(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory"),
    ] = Path("."),
) -> None:
    """Install a git post-commit hook that auto-syncs governance on commit.

    Appends to existing hook if one exists. Creates new hook file otherwise.

    Examples:
        $ rai governance hook install
    """
    project = project.resolve()
    git_dir = project / ".git"
    if not git_dir.is_dir():
        console.print(f"[red]{CROSS}[/red] Not a git repository: {project}")
        raise typer.Exit(1)

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook_file = hooks_dir / "post-commit"

    marker = "# RaiSE governance auto-sync"

    if hook_file.exists():
        existing = hook_file.read_text(encoding="utf-8")
        if marker in existing:
            console.print(
                f"[yellow]{CROSS}[/yellow] Hook already installed in {hook_file}"
            )
            return
        hook_file.write_text(
            existing.rstrip() + "\n\n" + _POST_COMMIT_HOOK_BODY,
            encoding="utf-8",
        )
    else:
        hook_file.write_text(_POST_COMMIT_HOOK_BODY, encoding="utf-8")

    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    console.print(f"[green]{CHECK}[/green] Installed post-commit hook: {hook_file}")
