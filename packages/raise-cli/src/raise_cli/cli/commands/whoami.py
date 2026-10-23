"""CLI command: rai whoami — verify identity and org membership."""

from __future__ import annotations

import json

import httpx
import typer
from rich.console import Console

from raise_cli.config.paths import get_global_rai_dir

console = Console()


def whoami_command() -> None:
    """Show current identity and organization."""
    creds_path = get_global_rai_dir() / "server.json"

    if not creds_path.is_file():
        console.print(
            "[red]Error:[/red] Not connected to a RaiSE server.\n"
            "Run [bold]rai connect[/bold] to authenticate."
        )
        raise typer.Exit(1)

    try:
        data = json.loads(creds_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        console.print(
            "[red]Error:[/red] Credentials file is corrupt.\n"
            "Run [bold]rai connect[/bold] to re-authenticate."
        )
        raise typer.Exit(1) from None

    server_url = data.get("server_url")
    api_key = data.get("api_key")

    if not server_url or not api_key:
        console.print(
            "[red]Error:[/red] Incomplete credentials.\n"
            "Run [bold]rai connect[/bold] to re-authenticate."
        )
        raise typer.Exit(1)

    with httpx.Client(base_url=server_url, timeout=10) as client:
        try:
            resp = client.get(
                "/api/v2/identity/me",
                headers={"Authorization": f"Bearer {api_key}"},
            )
        except httpx.HTTPError as exc:
            console.print(
                f"[red]Error:[/red] Could not reach server at {server_url}\n  {exc}"
            )
            raise typer.Exit(1) from None

    if resp.status_code in (401, 403):
        console.print(
            f"[red]Error:[/red] Authentication failed (server returned {resp.status_code}).\n"
            "Run [bold]rai connect[/bold] to re-authenticate."
        )
        raise typer.Exit(1)

    if resp.status_code != 200:
        console.print(
            f"[red]Error:[/red] Unexpected response (HTTP {resp.status_code})."
        )
        raise typer.Exit(1)

    identity = resp.json()
    console.print(f"  Name:  [bold]{identity.get('name', 'Unknown')}[/bold]")
    console.print(f"  Email: {identity.get('email', 'Unknown')}")
    console.print(f"  Org:   {identity.get('org_name', 'Unknown')}")
    console.print(f"  Role:  {identity.get('role', 'Unknown')}")
