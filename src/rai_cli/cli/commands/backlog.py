"""CLI commands for backlog management and external provider integration.

This module provides the `rai backlog` command group for managing project backlogs
and integrating with external providers (JIRA, GitLab, etc.).

Example:
    $ rai backlog auth --provider jira    # Authenticate with JIRA
"""

from __future__ import annotations

import os

import typer
from rich.console import Console

backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog and external provider integrations",
    no_args_is_help=True,
)

console = Console()


@backlog_app.command()
def auth(
    provider: str = typer.Option(
        ...,
        "--provider",
        "-p",
        help="External provider to authenticate with (e.g., 'jira')",
    ),
) -> None:
    """Authenticate with an external backlog provider.

    Initiates OAuth 2.0 flow to authenticate with the specified provider.
    Credentials are stored securely in ~/.rai/credentials.json with encryption.

    Supported providers:
        - jira: Atlassian JIRA Cloud

    Environment variables (optional):
        - JIRA_CLIENT_ID: Custom OAuth client ID
        - JIRA_CLIENT_SECRET: Custom OAuth client secret

    Examples:
        $ rai backlog auth --provider jira
        $ JIRA_CLIENT_ID=xxx JIRA_CLIENT_SECRET=yyy rai backlog auth --provider jira
    """
    # Validate provider
    if provider.lower() not in ["jira"]:
        console.print(
            f"[red]Error:[/red] Provider '{provider}' is not supported.\n"
            f"Supported providers: jira",
            style="red",
        )
        raise typer.Exit(code=1)

    # Import provider modules
    try:
        from rai_cli.config.paths import get_credentials_path
        from rai_providers.jira.oauth import (
            OAuthError,
            authenticate,
            get_current_user,
        )
    except ImportError as e:
        console.print(
            f"[red]Error:[/red] Failed to load provider modules: {e}",
            style="red",
        )
        raise typer.Exit(code=1) from e

    # Get credentials path
    credentials_path = get_credentials_path()

    # Get OAuth credentials from environment or use defaults
    if provider.lower() == "jira":
        client_id = os.getenv("JIRA_CLIENT_ID", "")
        client_secret = os.getenv("JIRA_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            console.print(
                "[yellow]Warning:[/yellow] Using demo OAuth credentials.\n"
                "For production use, set JIRA_CLIENT_ID and JIRA_CLIENT_SECRET environment variables.",
                style="yellow",
            )
            # Demo credentials (replace with actual demo app credentials)
            client_id = os.getenv("JIRA_CLIENT_ID", "demo-client-id")
            client_secret = os.getenv("JIRA_CLIENT_SECRET", "demo-client-secret")

        # Run OAuth flow
        try:
            console.print(
                f"[bold]Authenticating with {provider.upper()}...[/bold]"
            )

            token = authenticate(
                client_id=client_id,
                client_secret=client_secret,
                credentials_path=credentials_path,
            )

            # Get user info to display confirmation
            user_info = get_current_user(token["access_token"])
            email = user_info.get("emailAddress", "Unknown")

            console.print(
                f"\n[green]✓ Authenticated as {email}[/green]",
                style="bold green",
            )
            console.print(
                f"Credentials stored securely in: {credentials_path}",
                style="dim",
            )

        except OAuthError as e:
            console.print(
                f"\n[red]OAuth Error:[/red] {e}",
                style="red",
            )
            raise typer.Exit(code=1) from e

        except Exception as e:
            # Handle network errors and other unexpected errors
            console.print(
                f"\n[red]Error:[/red] {e}",
                style="red",
            )
            raise typer.Exit(code=1) from e
