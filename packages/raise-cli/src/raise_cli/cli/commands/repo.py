"""CLI commands: rai repo — manage repositories on RaiSE server."""

from __future__ import annotations

import subprocess
from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

from raise_cli.config.server import get_server_credentials
from raise_cli.core.text import slugify as _slugify

console = Console()

repo_app = typer.Typer(
    name="repo",
    help="Manage repositories on RaiSE server.",
    no_args_is_help=True,
)


@repo_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]
    pass


def _server_config() -> tuple[str, str] | None:
    return get_server_credentials()


def _detect_git_remote() -> str:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _require_config() -> tuple[str, str]:
    cfg = _server_config()
    if not cfg:
        console.print(
            "[red]Not connected to a RaiSE server.[/red] "
            "Run [bold]rai connect[/bold] first."
        )
        raise typer.Exit(1)
    return cfg


@repo_app.command("register")
def register_command(
    name: Annotated[str, typer.Argument(help="Repository name")],
    url: Annotated[str, typer.Option("--url", "-u", help="Git remote URL")] = "",
    slug: Annotated[str, typer.Option("--slug", "-s", help="Slug override")] = "",
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
    allow_org_mismatch: Annotated[
        bool,
        typer.Option(
            "--allow-org-mismatch",
            help="Write even if the project is bound to a different org (RAISE-9823)",
        ),
    ] = False,
) -> None:
    """Register a repository on the RaiSE server."""
    from pathlib import Path

    from raise_cli.cli.commands._server_write import confirm_server_write
    from raise_cli.config.org_binding import bind_org
    from raise_cli.config.repo_binding import bind_repo

    project_root = Path.cwd()
    target = confirm_server_write(
        "repository registration",
        yes=yes,
        project_root=project_root,
        allow_org_mismatch=allow_org_mismatch,
    )
    server_url, api_key = target.server_url, target.api_key

    if not url:
        url = _detect_git_remote()
    if not slug:
        slug = _slugify(name)

    resp = httpx.post(
        f"{server_url}/api/v2/repositories",
        json={"name": name, "slug": slug, "git_remote_url": url},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )

    resolved = False
    if resp.status_code == 409:
        get_resp = httpx.get(
            f"{server_url}/api/v2/repositories",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        data = None
        if get_resp.status_code == 200:
            data = next((r for r in get_resp.json() if r.get("slug") == slug), None)
        if data is None:
            console.print(
                f"[red]Repository with slug '{slug}' already exists "
                f"but could not be resolved.[/red]"
            )
            raise typer.Exit(1)
        resolved = True
    elif resp.status_code == 403:
        console.print(
            "[red]Permission denied.[/red] "
            "Only org admins can register repositories. "
            "Contact your admin or use an admin API key."
        )
        raise typer.Exit(1)
    elif resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            detail = resp.text
        console.print(f"[red]Error ({resp.status_code}):[/red] {detail}")
        raise typer.Exit(1)
    else:
        data = resp.json()

    if target.org_id:
        bind_org(project_root, target.org_name, target.org_id)
    bind_repo(
        project_root, repo_id=str(data.get("id", "")), slug=str(data.get("slug", slug))
    )
    org_label = target.org_name or target.server_url
    status = "already registered — resolved" if resolved else "registered"
    console.print(f"[green]✓ Repository {status}[/green] in org '{org_label}'")
    console.print(f"  Name: {data.get('name', name)}")
    console.print(f"  Slug: {data.get('slug', slug)}")
    console.print(f"  URL:  {data.get('git_remote_url', url)}")


@repo_app.command("list")
def list_command() -> None:
    """List repositories registered on the RaiSE server."""
    server_url, api_key = _require_config()

    resp = httpx.get(
        f"{server_url}/api/v2/repositories",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            detail = resp.text
        console.print(f"[red]Error ({resp.status_code}):[/red] {detail}")
        raise typer.Exit(1)
    repos: list[dict[str, str]] = resp.json()

    if not repos:
        console.print("No repositories registered.")
        return

    table = Table(title="Repositories")
    table.add_column("Name", style="bold")
    table.add_column("Slug")
    table.add_column("Git Remote URL", style="dim")
    for r in repos:
        table.add_row(r.get("name", ""), r.get("slug", ""), r.get("git_remote_url", ""))
    console.print(table)
