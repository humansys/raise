"""CLI command group: rai auth — provider authentication flows (RAISE-15335)."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

auth_app = typer.Typer(help="Authenticate with external providers.")
console = Console()


@auth_app.command("google")
def auth_google_command(
    account_id: Annotated[
        str,
        typer.Argument(help="Jira account ID to map this Google account to."),
    ],
    label: Annotated[
        str,
        typer.Option(
            "--label", "-l", help="Optional label for this account (e.g. 'work')."
        ),
    ] = "",
    default: Annotated[
        bool,
        typer.Option("--default", help="Mark as the default Google Drive account."),
    ] = False,
) -> None:
    """Authorize Google Drive access via InstalledAppFlow OAuth.

    Opens a browser window for Google account selection, then stores
    the refresh token in identity_map.db (ADR-112 brokered pattern).
    """
    from raise_cli.auth.google import (
        GoogleAuthManager,
        GoogleDriveConnectivityError,
        GoogleOAuthClientError,
    )

    manager = GoogleAuthManager()
    try:
        console.print("Opening browser for Google authorization...")
        record = manager.authorize(account_id, label=label, is_default=default)
    except GoogleOAuthClientError as exc:
        console.print(f"[red]OAuth client error:[/red] {exc}")
        raise typer.Exit(1) from None
    except GoogleDriveConnectivityError as exc:
        console.print(f"[red]Drive connectivity check failed:[/red] {exc}")
        raise typer.Exit(1) from None

    console.print("[green]Google Drive authorized![/green]")
    if record.email:
        console.print(f"  Email: {record.email}")
    console.print(f"  Account ID: {record.jira_account_id}")
    if record.label:
        console.print(f"  Label: {record.label}")
    if record.is_default:
        console.print("  [dim](default account)[/dim]")
