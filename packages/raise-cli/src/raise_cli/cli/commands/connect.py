"""CLI command: rai connect — device authorization flow to raise-server.

Subcommands:
  rai connect [org_slug]  — server auth (existing)
  rai connect github      — git provider OAuth (S10724.2)
  rai connect gitlab      — git provider OAuth (S10724.2)
"""

from __future__ import annotations

import json
import logging
import os
import time
import webbrowser
from pathlib import Path
from typing import Annotated, Any

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console

from raise_cli.config.paths import get_global_rai_dir

console = Console()
logger = logging.getLogger(__name__)

_POLL_JITTER = 0.5
connect_app = typer.Typer(help="Connect to RaiSE server or git providers.")


def _get_server_credentials_path() -> Path:
    return get_global_rai_dir() / "server.json"


def _save_credentials(data: dict[str, object]) -> None:
    path = _get_server_credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def load_server_credentials() -> None:
    """Load RAISE_SERVER_URL/RAISE_API_KEY from ~/.rai/server.json into env.

    Only sets variables that are NOT already in the environment.
    Called from cli/main.py callback alongside load_dotenv.
    """
    path = _get_server_credentials_path()
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for env_key, json_key in (
            ("RAISE_SERVER_URL", "server_url"),
            ("RAISE_API_KEY", "api_key"),
        ):
            val = data.get(json_key)
            if val and env_key not in os.environ:
                os.environ[env_key] = val
    except (OSError, json.JSONDecodeError):
        pass


def load_cli_env(cwd: Path | None = None) -> None:
    """Load global and checkout-local dotenv files for CLI-style entrypoints."""
    effective_cwd = cwd or Path.cwd()
    load_dotenv(get_global_rai_dir() / ".env", override=False)
    load_dotenv(effective_cwd / ".env", override=True)


def _handle_approved(server: str, poll_data: dict[str, object], api_key: str) -> None:
    """Save credentials and print success on approval."""
    creds = {
        "server_url": server,
        "api_key": api_key,
        "org_id": poll_data.get("org_id"),
        "org_name": poll_data.get("org_name"),
        "member_id": poll_data.get("member_id"),
        "email": poll_data.get("email"),
        "role": poll_data.get("role"),
        "teams": poll_data.get("teams", []),
    }
    _save_credentials(creds)

    console.print()
    console.print("[green]Connected![/green]")
    console.print(f"  Organization: [bold]{creds['org_name']}[/bold]")
    console.print(f"  Email: {creds['email']}")
    console.print(f"  Role: {creds['role']}")
    console.print(f"  Credentials saved to: {_get_server_credentials_path()}")

    env_key = os.environ.get("RAISE_API_KEY")
    if env_key and env_key != api_key:
        console.print()
        console.print(
            "[yellow]Warning:[/yellow] RAISE_API_KEY is set in "
            "your shell and will shadow this credential.\n"
            "Remove it from ~/.bashrc and run "
            "`unset RAISE_API_KEY` for the new key to take effect."
        )


_ORG_PROJECTS_ENDPOINT = "/api/v2/orgs/projects"


def fetch_org_projects(server: str, api_key: str) -> list[str]:
    """Return project slugs for the connected org. Empty list on any error."""
    try:
        resp = httpx.get(
            f"{server}{_ORG_PROJECTS_ENDPOINT}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        resp.raise_for_status()
        raw: Any = resp.json()
        items: list[Any] = raw if isinstance(raw, list) else []
        return [p["slug"] for p in items if isinstance(p, dict) and p.get("slug")]
    except Exception as exc:  # noqa: BLE001
        logger.debug("fetch_org_projects failed (%s) — skipping project sync", exc)
        return []


def bootstrap_after_connect(server: str, api_key: str, *, no_bootstrap: bool) -> None:
    """Pull team knowledge after successful org connect. Fail-open.

    Sequence:
      1. Fetch org project slugs (up to 5).
      2. Pull team-scoped patterns into global DB.
      3. Pull knowledge graph per project.

    Any exception is caught, printed as a warning, and connect still succeeds.
    Skip entirely when *no_bootstrap* is True (e.g. CI environments).
    """
    if no_bootstrap:
        return
    try:
        from raise_cli.cli.commands.init import (  # noqa: PLC0415
            _pull_knowledge_sync,  # pyright: ignore[reportPrivateUsage]
        )
        from raise_cli.memory.sync import pull_patterns  # noqa: PLC0415
        from raise_cli.storage.connection import get_global_db  # noqa: PLC0415
        from raise_cli.storage.schema import create_all  # noqa: PLC0415

        slugs = fetch_org_projects(server, api_key)

        conn = get_global_db()
        create_all(conn)
        try:
            pull_patterns(conn, scope="team")
        finally:
            conn.close()

        # Dummy project path — _pull_knowledge_sync only uses it for project ID
        # derivation; we pass server_slug explicitly so path is only used as fallback.
        cwd = Path.cwd()
        for slug in slugs[:5]:
            _pull_knowledge_sync(cwd, server_slug=slug)

        console.print("[green]✓ Team knowledge synced[/green]")
    except Exception as exc:  # noqa: BLE001
        Console(stderr=True).print(
            f"[yellow]Warning:[/yellow] bootstrap skipped ({exc})"
        )


def _start_device_flow(
    client: httpx.Client, server: str, org_slug: str | None
) -> dict[str, Any]:
    body: dict[str, str] | None = {"org_slug": org_slug} if org_slug else None
    try:
        resp = client.post("/api/v2/auth/device", json=body)
        if resp.status_code == 404 and org_slug:
            console.print(
                f"[red]Organization '{org_slug}' not found on {server}[/red]\n"
                "Check the slug with your team admin."
            )
            raise typer.Exit(1)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        console.print(f"[red]Failed to start device flow:[/red] {exc}")
        raise typer.Exit(1) from None
    return resp.json()  # type: ignore[no-any-return]


def connect_command(
    org_slug: Annotated[
        str | None,
        typer.Argument(
            help="Organization slug (e.g. 'acme-eng'). "
            "Scopes the connection to this org.",
        ),
    ] = None,
    server: Annotated[
        str,
        typer.Option(
            "--server",
            "-s",
            help="Server URL (default: https://api.raise.sh)",
        ),
    ] = "https://api.raise.sh",
    no_bootstrap: Annotated[
        bool,
        typer.Option(
            "--no-bootstrap",
            help="Skip team knowledge sync after connect (e.g. for CI environments).",
        ),
    ] = False,
) -> None:
    """Connect this machine to a RaiSE server using device authorization."""
    client = httpx.Client(base_url=server, timeout=10)

    if org_slug:
        console.print(
            f"Connecting to [bold]{server}[/bold] (org: [cyan]{org_slug}[/cyan])..."
        )
    else:
        console.print(f"Connecting to [bold]{server}[/bold]...")

    data = _start_device_flow(client, server, org_slug)
    device_code: str = data["device_code"]
    user_code: str = data["user_code"]
    verification_url: str = data["verification_url"]
    expires_in: int = data.get("expires_in", 300)
    interval: int = data.get("interval", 3)

    console.print()
    console.print(f"Your device code: [bold yellow]{user_code}[/bold yellow]")
    console.print()

    opened = webbrowser.open(verification_url)
    if opened:
        console.print(
            "A browser window has been opened. Log in and approve the connection."
        )
    else:
        console.print(
            f"Open this URL in your browser:\n  [link]{verification_url}[/link]"
        )

    console.print()
    console.print("Waiting for approval...", style="dim")

    deadline = time.monotonic() + expires_in
    try:
        while time.monotonic() < deadline:
            time.sleep(interval + _POLL_JITTER)
            try:
                poll_resp = client.get(f"/api/v2/auth/device/{device_code}")
                poll_resp.raise_for_status()
            except httpx.HTTPError:
                continue

            poll_data = poll_resp.json()
            status = poll_data.get("status")

            if status == "pending":
                continue
            if status == "expired":
                console.print(
                    "[red]Device code expired.[/red] Run `rai connect` again."
                )
                raise typer.Exit(1)
            if status == "approved":
                api_key = poll_data.get("api_key")
                if not api_key:
                    console.print(
                        "[yellow]Approved but key already delivered.[/yellow]"
                    )
                    raise typer.Exit(1)
                _handle_approved(server, poll_data, api_key)
                bootstrap_after_connect(server, str(api_key), no_bootstrap=no_bootstrap)
                raise typer.Exit(0)

            console.print(f"[red]Unexpected status: {status}[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled.[/dim]")
        raise typer.Exit(130) from None

    console.print("[red]Timed out waiting for approval.[/red] Run `rai connect` again.")
    raise typer.Exit(1)


# --- Git provider device flow (S10724.2) ---


def _get_git_providers_dir() -> Path:
    return get_global_rai_dir() / "git-providers"


def _save_git_provider(provider: str, data: dict[str, object]) -> None:
    path = _get_git_providers_dir() / f"{provider}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def _get_server_url_and_key() -> tuple[str, str]:
    """Load server URL and API key from ~/.rai/server.json."""
    path = _get_server_credentials_path()
    if not path.is_file():
        console.print(
            "[red]Not connected to a RaiSE server.[/red]\n"
            "Run `rai connect` first to authenticate."
        )
        raise typer.Exit(1)
    data = json.loads(path.read_text(encoding="utf-8"))
    server_url = data.get("server_url", "")
    api_key = data.get("api_key", "")
    if not server_url or not api_key:
        console.print(
            "[red]Server credentials incomplete.[/red]\n"
            "Run `rai connect` to re-authenticate."
        )
        raise typer.Exit(1)
    return server_url, api_key


def _connect_git_provider(provider: str) -> None:  # noqa: C901
    """Run device flow for a git provider (GitHub/GitLab)."""
    server_url, api_key = _get_server_url_and_key()
    client = httpx.Client(base_url=server_url, timeout=10)

    console.print(
        f"Connecting [cyan]{provider}[/cyan] via [bold]{server_url}[/bold]..."
    )

    try:
        resp = client.post(
            f"/api/v2/git-auth/device/{provider}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            console.print(
                f"[red]Provider '{provider}' not configured on this server.[/red]"
            )
        else:
            console.print(f"[red]Failed to start device flow:[/red] {exc}")
        raise typer.Exit(1) from None
    except httpx.HTTPError as exc:
        console.print(f"[red]Failed to start device flow:[/red] {exc}")
        raise typer.Exit(1) from None

    data: dict[str, Any] = resp.json()
    device_code: str = data["device_code"]
    verification_url: str = data["verification_url"]
    user_code: str = data["user_code"]
    expires_in: int = data.get("expires_in", 300)
    interval: int = data.get("interval", 3)

    console.print()
    console.print(f"Your code: [bold yellow]{user_code}[/bold yellow]")
    console.print()

    opened = webbrowser.open(verification_url)
    if opened:
        console.print("A browser window has been opened. Authorize the application.")
    else:
        console.print(
            f"Open this URL in your browser:\n  [link]{verification_url}[/link]"
        )

    console.print()
    console.print("Waiting for authorization...", style="dim")

    deadline = time.monotonic() + expires_in
    try:
        while time.monotonic() < deadline:
            time.sleep(interval + _POLL_JITTER)
            try:
                poll_resp = client.get(
                    f"/api/v2/git-auth/device/{device_code}",
                )
                poll_resp.raise_for_status()
            except httpx.HTTPError:
                continue

            poll_data: dict[str, Any] = poll_resp.json()
            status = poll_data.get("status")

            if status == "pending":
                continue
            if status == "expired":
                console.print(
                    f"[red]Device code expired.[/red] Run `rai connect {provider}` again."
                )
                raise typer.Exit(1)
            if status == "approved":
                username = poll_data.get("username", "unknown")
                _save_git_provider(
                    provider,
                    {
                        "provider": provider,
                        "username": username,
                        "server_url": server_url,
                    },
                )
                console.print()
                console.print(f"[green]Connected to {provider}![/green]")
                console.print(f"  Username: [bold]{username}[/bold]")
                console.print(
                    f"  Credentials saved to: {_get_git_providers_dir() / f'{provider}.json'}"
                )
                raise typer.Exit(0)

            console.print(f"[red]Unexpected status: {status}[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled.[/dim]")
        raise typer.Exit(130) from None

    console.print(
        f"[red]Timed out waiting for authorization.[/red] "
        f"Run `rai connect {provider}` again."
    )
    raise typer.Exit(1)


@connect_app.command("github")
def connect_github_command() -> None:
    """Connect your GitHub account for SCM operations."""
    _connect_git_provider("github")


@connect_app.command("gitlab")
def connect_gitlab_command() -> None:
    """Connect your GitLab account for SCM operations."""
    _connect_git_provider("gitlab")
