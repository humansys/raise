"""CLI commands: rai scm — SCM operations via server proxy (S10724.4, S10873.4)."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.adapters.scm_adapter import RaiseServerScmAdapter
from raise_cli.adapters.sync import run_sync

console = Console()
scm_app = typer.Typer(help="SCM operations (repos, branches, PRs via server proxy).")


def _get_adapter() -> RaiseServerScmAdapter:
    """Create adapter or exit with error."""
    try:
        return RaiseServerScmAdapter()
    except ConnectionError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None


@scm_app.command("repos")
def repos_command(
    provider: Annotated[str, typer.Argument(help="Git provider (github/gitlab)")],
    search: Annotated[
        str, typer.Option("--search", "-s", help="Filter repos by name")
    ] = "",
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="Max repos to return")
    ] = 50,
) -> None:
    """List repositories from a connected git provider."""
    adapter = _get_adapter()
    repos = run_sync(adapter.list_repos(provider=provider, search=search, limit=limit))

    if not repos:
        console.print("[dim]No repositories found.[/dim]")
        return

    table = Table(title=f"{provider} repositories")
    table.add_column("Name", style="bold")
    table.add_column("Full Name")
    table.add_column("Visibility")
    table.add_column("Default Branch")

    for repo in repos:
        vis_style = "green" if repo.visibility == "public" else "dim"
        table.add_row(
            repo.name,
            repo.full_name,
            f"[{vis_style}]{repo.visibility}[/{vis_style}]",
            repo.default_branch,
        )

    console.print(table)
    console.print(f"\n[dim]{len(repos)} repos[/dim]")


@scm_app.command("branches")
def branches_command(
    provider: Annotated[str, typer.Argument(help="Git provider (github/gitlab)")],
    repo: Annotated[
        str, typer.Argument(help="Repository ID (owner/repo or project ID)")
    ],
) -> None:
    """List branches for a repository."""
    adapter = _get_adapter()
    branches = run_sync(adapter.list_branches(provider=provider, repo_id=repo))

    if not branches:
        console.print("[dim]No branches found.[/dim]")
        return

    for branch in branches:
        console.print(f"  {branch}")

    console.print(f"\n[dim]{len(branches)} branches[/dim]")


@scm_app.command("disconnect")
def disconnect_command(
    provider: Annotated[
        str, typer.Argument(help="Git provider to disconnect (github/gitlab)")
    ],
) -> None:
    """Disconnect a git provider — revoke your personal connection."""
    adapter = _get_adapter()
    result = run_sync(adapter.disconnect(provider=provider))

    if result:
        console.print(f"[green]Disconnected from {provider}.[/green]")
    else:
        console.print(f"[red]Failed to disconnect from {provider}.[/red]")
        raise typer.Exit(1)


@scm_app.command("create-pr")
def create_pr_command(
    provider: Annotated[
        str, typer.Option("--provider", "-p", help="Git provider (github/gitlab)")
    ],
    repo: Annotated[
        str,
        typer.Option(
            "--repo",
            "-r",
            help="Repository ID (owner/repo for GitHub, project ID for GitLab)",
        ),
    ],
    title: Annotated[str, typer.Option("--title", "-t", help="PR/MR title")],
    source: Annotated[str, typer.Option("--source", "-s", help="Source branch")],
    target: Annotated[str, typer.Option("--target", help="Target branch")],
    description: Annotated[
        str, typer.Option("--description", "-d", help="PR/MR description")
    ] = "",
) -> None:
    """Create a pull request / merge request via the server proxy."""
    adapter = _get_adapter()
    result = run_sync(
        adapter.create_pr(
            provider=provider,
            repo_id=repo,
            title=title,
            source_branch=source,
            target_branch=target,
            description=description,
        )
    )

    console.print("[green]PR created![/green]")
    console.print(f"  Number: [bold]#{result.number}[/bold]")
    console.print(f"  Title:  {result.title}")
    console.print(f"  URL:    [link]{result.url}[/link]")
    console.print(f"  Author: {result.author}")


@scm_app.command("get-pr")
def get_pr_command(
    provider: Annotated[
        str, typer.Option("--provider", "-p", help="Git provider (github/gitlab)")
    ],
    repo: Annotated[str, typer.Option("--repo", "-r", help="Repository ID")],
    number: Annotated[int, typer.Option("--number", "-n", help="PR/MR number")],
) -> None:
    """Get pull request / merge request details."""
    adapter = _get_adapter()
    result = run_sync(
        adapter.get_pr(
            provider=provider,
            repo_id=repo,
            pr_number=number,
        )
    )

    state_color = {"open": "green", "merged": "cyan", "closed": "red"}.get(
        result.state, "yellow"
    )
    console.print(f"  Number: [bold]#{result.number}[/bold]")
    console.print(f"  Title:  {result.title}")
    console.print(f"  State:  [{state_color}]{result.state}[/{state_color}]")
    console.print(f"  URL:    [link]{result.url}[/link]")
    console.print(f"  Branch: {result.source_branch} -> {result.target_branch}")
    console.print(f"  Author: {result.author}")
