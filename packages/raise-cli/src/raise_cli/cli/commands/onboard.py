"""CLI command: rai onboard — unified developer onboarding orchestrator.

Two paths:
  1. OIT web-first: --from-oit-token oit_xxx
     Exchange token → save ~/.rai/server.json → rai init (if slug) → bootstrap
  2. Local-first OSS: (no token)
     Detect server.json + .raise/manifest.yaml → fill gaps → bootstrap if server
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import httpx
import typer
from rich.console import Console

from raise_cli.cli.commands.connect import (
    _get_server_credentials_path,  # pyright: ignore[reportPrivateUsage]
    _save_credentials,  # pyright: ignore[reportPrivateUsage]
    bootstrap_after_connect,
)

console = Console()
_DEFAULT_SERVER = "https://api.raise.sh"
_OIT_EXCHANGE_PATH = "/api/v2/auth/oit/exchange"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _stdin_is_tty() -> bool:
    """Return True when stdin is an interactive terminal."""
    return sys.stdin.isatty()


def _manifest_exists() -> bool:
    """Return True when .raise/manifest.yaml exists in the current directory."""
    return (Path.cwd() / ".raise" / "manifest.yaml").exists()


def _load_server_credentials() -> dict[str, str] | None:
    """Load credentials from ~/.rai/server.json. Return None if not present."""
    path = _get_server_credentials_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        server_url = str(data.get("server_url", "")).strip()
        api_key = str(data.get("api_key", "")).strip()
        if server_url and api_key:
            return {"server_url": server_url, "api_key": api_key}
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _exchange_oit(server: str, token: str) -> dict[str, object]:
    """POST /api/v2/auth/oit/exchange. Raises typer.Exit on failure."""
    url = f"{server.rstrip('/')}{_OIT_EXCHANGE_PATH}"
    try:
        resp = httpx.post(url, json={"token": token}, timeout=30)
    except httpx.RequestError as exc:
        console.print(f"[red]Network error during OIT exchange:[/red] {exc}")
        raise typer.Exit(1) from None

    if resp.status_code == 410:
        console.print(
            "[red]Token expired or already used.[/red]\n"
            "Request a new magic link from [bold]raise.sh/onboard[/bold]"
        )
        raise typer.Exit(1)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        console.print(f"[red]OIT exchange failed ({resp.status_code}):[/red] {exc}")
        raise typer.Exit(1) from None

    return resp.json()  # type: ignore[no-any-return]


def _check_credential_overwrite(force: bool) -> None:
    """If ~/.rai/server.json exists, warn and prompt (or error in non-TTY).

    Raises typer.Exit(1) when user declines or is in non-TTY without --force.
    """
    creds_path = _get_server_credentials_path()
    if not creds_path.exists():
        return

    if force:
        return

    if not _stdin_is_tty():
        console.print(
            "[red]Existing credentials found in ~/.rai/server.json.[/red]\n"
            "Cannot overwrite in non-interactive mode.\n"
            "Use [bold]--force[/bold] to overwrite, or run [bold]rai connect[/bold] "
            "to update credentials interactively."
        )
        raise typer.Exit(1)

    # TTY: interactive confirm
    try:
        existing = json.loads(creds_path.read_text(encoding="utf-8"))
        org_name = existing.get("org_name", creds_path)
    except (OSError, json.JSONDecodeError):
        org_name = str(creds_path)

    confirmed = typer.confirm(
        f"Overwrite existing credentials for '{org_name}'?",
        default=False,
    )
    if not confirmed:
        console.print("[dim]Aborted — existing credentials kept.[/dim]")
        raise typer.Exit(1)


def _run_oit_path(token: str, server: str, no_bootstrap: bool, force: bool) -> None:
    """Execute the web-first OIT onboarding path."""
    _check_credential_overwrite(force)

    console.print(f"Exchanging OIT token with [bold]{server}[/bold]...")
    payload = _exchange_oit(server, token)

    api_key = str(payload.get("api_key", ""))
    server_url = str(payload.get("server_url", server))
    org_id = str(payload.get("org_id", ""))
    org_name = str(payload.get("org_name", ""))
    project_slug: str | None = payload.get("project_slug")  # type: ignore[assignment]
    if project_slug is not None:
        project_slug = str(project_slug)

    creds: dict[str, object] = {
        "server_url": server_url,
        "api_key": api_key,
        "org_id": org_id,
        "org_name": org_name,
    }
    _save_credentials(creds)
    console.print(f"[green]✓ Connected to {org_name}[/green]")

    # Run rai init if a project was scoped and not already initialized
    if project_slug and not _manifest_exists():
        console.print(f"[dim]Initializing project '{project_slug}'...[/dim]")
        result = subprocess.run(  # noqa: S603
            ["rai", "init", "--slug", project_slug],  # noqa: S607
            check=False,
        )
        if result.returncode != 0:
            console.print(
                "[yellow]Warning:[/yellow] rai init returned non-zero. "
                "You can run [bold]rai init[/bold] manually to fix."
            )

    bootstrap_after_connect(server_url, api_key, no_bootstrap=no_bootstrap)

    console.print()
    console.print(
        "[green]✓ Setup complete![/green]\n"
        "Run [bold]/rai-session-start[/bold] in your AI editor to begin working."
    )


def _run_local_path(no_bootstrap: bool) -> None:
    """Execute the local-first OSS onboarding path."""
    existing_creds = _load_server_credentials()

    if existing_creds is None:
        console.print(
            "[dim]No server configured — continuing in local (OSS) mode.[/dim]"
        )
    else:
        console.print(f"[dim]Server configured: {existing_creds['server_url']}[/dim]")

    if not _manifest_exists():
        console.print("[dim]Initializing project...[/dim]")
        result = subprocess.run(  # noqa: S603
            ["rai", "init"],  # noqa: S607
            check=False,
        )
        if result.returncode != 0:
            console.print(
                "[red]rai init failed.[/red] "
                "Run [bold]rai init[/bold] manually to diagnose."
            )
            raise typer.Exit(1)
    else:
        console.print("[dim]Project already initialized — skipping init.[/dim]")

    if existing_creds is not None:
        bootstrap_after_connect(
            existing_creds["server_url"],
            existing_creds["api_key"],
            no_bootstrap=no_bootstrap,
        )

    console.print()
    console.print(
        "[green]✓ Setup complete![/green]\n"
        "Run [bold]/rai-session-start[/bold] in your AI editor to begin working."
    )


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


def onboard_command(
    from_oit_token: Annotated[
        str | None,
        typer.Option(
            "--from-oit-token",
            help=(
                "One-time invitation token (oit_xxx) from raise.sh/onboard. "
                "Exchanges token for credentials, runs init if scoped, then bootstraps."
            ),
            metavar="TOKEN",
        ),
    ] = None,
    server: Annotated[
        str,
        typer.Option(
            "--server",
            "-s",
            help="RaiSE server URL (default: https://api.raise.sh)",
        ),
    ] = _DEFAULT_SERVER,
    no_bootstrap: Annotated[
        bool,
        typer.Option(
            "--no-bootstrap",
            help="Skip team knowledge sync after connect (useful in CI).",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help=(
                "Overwrite existing credentials without prompting. "
                "Required in non-TTY when --from-oit-token is used and "
                "~/.rai/server.json already exists."
            ),
        ),
    ] = False,
) -> None:
    r"""Unified developer onboarding — sets up RaiSE from zero to working session.

    Two modes:

    \b
    OIT (invitation) path — pass --from-oit-token:
      1. Exchange OIT for credentials
      2. Save ~/.rai/server.json
      3. Run rai init (if project scoped in token)
      4. Sync team knowledge

    \b
    Local-first (OSS) path — no token:
      1. Detect existing credentials / project
      2. Run rai init if not initialized
      3. Sync team knowledge (if server configured)
    """
    if from_oit_token:
        _run_oit_path(from_oit_token, server, no_bootstrap, force)
    else:
        _run_local_path(no_bootstrap)
