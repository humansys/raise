"""CLI command group: rai bot — bot-operator convenience commands (RAISE-15354)."""

from __future__ import annotations

import os
import subprocess
from typing import Annotated

import typer
from rich.console import Console

bot_app = typer.Typer(help="Bot operator commands for cloud-deployed Telegram bots.")
console = Console()


@bot_app.command("provision-drive")
def provision_drive_command(
    workspace_id: Annotated[
        str,
        typer.Option(
            "--workspace-id",
            help="Workspace ID for the Drive doc (used as idempotency key).",
        ),
    ],
    workspace_name: Annotated[
        str,
        typer.Option(
            "--workspace-name",
            help="Human-readable name for the Drive workspace doc.",
        ),
    ],
    fly_app: Annotated[
        str | None,
        typer.Option(
            "--fly-app",
            help="Fly.io app name. When set, writes the doc_id to CHANNEL_DEFAULT_DRIVE_DOC_ID via flyctl.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would happen without making any changes.",
        ),
    ] = False,
) -> None:
    r"""Provision a Google Drive Doc for bot workspace memory.

    Reads the default Drive OAuth token from ~/.rai/identity_map.db
    (set up via `rai auth google`), creates or reuses a workspace Doc
    in Drive (idempotent -- second run with the same workspace_id returns
    the same doc), and optionally syncs the doc_id to Fly.io as the
    CHANNEL_DEFAULT_DRIVE_DOC_ID secret.

    Examples:
    \b
    # Provision a doc and print its ID:
    rai bot provision-drive --workspace-id ws-abc --workspace-name "Rai Workspace"
    \b
    # Also sync to a Fly.io deployment:
    rai bot provision-drive --workspace-id ws-abc --workspace-name "Rai Workspace" --fly-app my-bot-app
    \b
    # Dry-run (no side effects):
    rai bot provision-drive --workspace-id ws-abc --workspace-name "Rai Workspace" --dry-run
    """
    if dry_run:
        _handle_dry_run(workspace_id, workspace_name, fly_app)
        return

    doc_id = _provision_drive_doc(workspace_id, workspace_name)

    console.print(f"[green]Drive doc provisioned:[/green] {doc_id}")

    _handle_fly_sync(doc_id, fly_app)


def _handle_dry_run(
    workspace_id: str, workspace_name: str, fly_app: str | None
) -> None:
    """Print dry-run summary without any side effects."""
    console.print(
        f"[yellow]dry-run[/yellow] Would provision Drive doc for workspace "
        f"[bold]{workspace_id}[/bold] (name: {workspace_name!r})"
    )
    if fly_app:
        console.print(
            f"[yellow]dry-run[/yellow] Would set CHANNEL_DEFAULT_DRIVE_DOC_ID "
            f"via: flyctl secrets set CHANNEL_DEFAULT_DRIVE_DOC_ID=<doc_id> --app {fly_app}"
        )


def _provision_drive_doc(workspace_id: str, workspace_name: str) -> str:
    """Read Drive token, build adapter, provision doc, return doc_id.

    Raises typer.Exit(1) on any failure.
    """
    from raise_cli.auth.google import GoogleAuthManager

    mgr = GoogleAuthManager()
    creds = mgr.get_default_drive_credentials()
    if not creds:
        console.print(
            "[red]Error:[/red] No Google Drive token found in identity_map.db.\n"
            "Run [bold]rai auth google <account_id>[/bold] to authorize first."
        )
        raise typer.Exit(1)

    drive_token, client_id, client_secret = creds
    # Inject credentials into env so GoogleDriveAdapter can use them
    os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"] = drive_token
    if client_id:
        os.environ["GOOGLE_OAUTH_CLIENT_ID"] = client_id
    if client_secret:
        os.environ["GOOGLE_OAUTH_CLIENT_SECRET"] = client_secret

    try:
        from raise_cli.adapters.google_drive_adapter import GoogleDriveAdapter

        adapter = GoogleDriveAdapter()
        doc_id = adapter.provision_workspace_doc(workspace_id, workspace_name)
    except ImportError:
        console.print(
            "[red]Error:[/red] google-auth is not installed.\n"
            "Install with: pip install 'raise-cli[gdrive]'"
        )
        raise typer.Exit(1) from None
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        console.print(f"[red]Drive provisioning failed:[/red] {exc}")
        raise typer.Exit(1) from None

    if not doc_id:
        console.print("[red]Error:[/red] Drive provisioning returned no doc_id.")
        raise typer.Exit(1)

    return doc_id


def _handle_fly_sync(doc_id: str, fly_app: str | None) -> None:
    """Write doc_id to Fly.io secret, or print the manual command if flyctl is absent."""
    if not fly_app:
        console.print(
            "\nTo sync to Fly.io, run:\n"
            f"  flyctl secrets set CHANNEL_DEFAULT_DRIVE_DOC_ID={doc_id} --app <your-app>"
        )
        return

    secret_spec = f"CHANNEL_DEFAULT_DRIVE_DOC_ID={doc_id}"
    flyctl_cmd = ["flyctl", "secrets", "set", secret_spec, "--app", fly_app]
    try:
        result = subprocess.run(
            flyctl_cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            console.print(
                f"[green]Fly secret set:[/green] CHANNEL_DEFAULT_DRIVE_DOC_ID on app {fly_app!r}"
            )
        else:
            console.print(
                f"[yellow]Warning:[/yellow] flyctl exited {result.returncode}:\n"
                f"  {result.stderr.strip()}"
            )
            _print_manual_flyctl(doc_id, fly_app)
    except FileNotFoundError:
        console.print("[yellow]flyctl not found in PATH.[/yellow]")
        _print_manual_flyctl(doc_id, fly_app)


def _print_manual_flyctl(doc_id: str, fly_app: str) -> None:
    """Print the manual flyctl command for the user to run."""
    console.print(
        "Run manually:\n"
        f"  flyctl secrets set CHANNEL_DEFAULT_DRIVE_DOC_ID={doc_id} --app {fly_app}"
    )
