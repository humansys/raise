"""Release CLI commands — release management, quality gates, and release workflow.

Provides commands for:
- Listing releases from the memory graph
- Running pre-publish quality checks
- Orchestrating full releases (bump, changelog, commit, tag, push)

The check and publish commands were absorbed from the `publish` group (RAISE-247/S5).
"""

from __future__ import annotations

import re
import subprocess  # nosec B404 - subprocess required for git operations in CLI tool
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.graph.backends import get_active_backend
from raise_cli.publish.check import CheckResult, run_checks
from raise_cli.publish.version import (
    BumpType,
    bump_version,
    is_pep440,
    sync_version_files,
)

release_app = typer.Typer(help="Release management commands")
console = Console()

# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"


# =============================================================================
# Helpers (moved from publish.py)
# =============================================================================


def _find_project_paths(project: Path) -> tuple[Path, Path]:
    """Find pyproject.toml and CHANGELOG.md paths."""
    pyproject_path = project / "pyproject.toml"
    changelog_path = project / "CHANGELOG.md"
    return pyproject_path, changelog_path


def _read_current_version(pyproject_path: Path) -> str:
    """Read current version from pyproject.toml."""
    if not pyproject_path.exists():
        console.print("[red]pyproject.toml not found[/red]")
        raise typer.Exit(1)
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]*)"', content)
    if not match:
        console.print("[red]Could not find version in pyproject.toml[/red]")
        raise typer.Exit(1)
    return match.group(1)


def _display_results(results: list[CheckResult]) -> bool:
    """Display check results with Rich formatting."""
    console.print()
    console.print("[bold]Pre-publish Quality Check[/bold]")
    console.print("─" * 40)

    passed_count = 0
    for r in results:
        icon = "[green]✓[/green]" if r.passed else "[red]✗[/red]"
        console.print(f"  {icon} {r.gate}: {r.message}")
        if r.passed:
            passed_count += 1

    total = len(results)
    console.print()
    if passed_count == total:
        console.print(f"[green]All {total} checks passed[/green]")
    else:
        console.print(
            f"[red]{passed_count}/{total} checks passed, "
            f"{total - passed_count} FAILED[/red]"
        )

    return passed_count == total


# =============================================================================
# Commands
# =============================================================================


@release_app.command("list")
def list_releases(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """List releases from the memory graph.

    Shows all release nodes with their status, target date, and associated epics.

    Examples:
        $ rai release list
        $ rai release list --project /path/to/project
    """
    graph_path = project / GRAPH_REL_PATH
    if not graph_path.exists():
        cli_error(
            f"Memory index not found: {graph_path}",
            hint="Run 'rai memory build' first to create the index",
            exit_code=4,
        )

    try:
        graph = get_active_backend(graph_path).load()
    except Exception as e:
        cli_error(f"Error loading memory index: {e}")

    # Find all release nodes
    releases = [n for n in graph.iter_concepts() if n.type == "release"]

    if not releases:
        console.print("\nNo release nodes found in graph.")
        return

    # Find epics linked to each release via part_of edges
    release_epics: dict[str, list[str]] = {}
    for node in graph.iter_concepts():
        if node.type == "epic":
            neighbors = graph.get_neighbors(node.id, depth=1, edge_types=["part_of"])
            for neighbor in neighbors:
                if neighbor.type == "release":
                    release_epics.setdefault(neighbor.id, []).append(
                        node.id.replace("epic-", "").upper()
                    )

    # Build table
    table = Table(title="Releases")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status", style="yellow")
    table.add_column("Target", style="green")
    table.add_column("Epics", style="dim")

    for rel in sorted(releases, key=lambda r: r.metadata.get("target", "")):
        release_id = rel.metadata.get("release_id", rel.id)
        name = rel.metadata.get("name", "")
        status = rel.metadata.get("status", "")
        target = rel.metadata.get("target", "")
        epics = ", ".join(sorted(release_epics.get(rel.id, [])))

        table.add_row(release_id, name, status, target, epics)

    console.print()
    console.print(table)


@release_app.command("check")
def check_command(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """Run all quality gates before publishing.

    Runs 9 quality checks: tests (with coverage diagnostic), types, lint,
    security, build, package validation, changelog, PEP 440 version, and
    version sync. Coverage is reported but not a blocking gate.

    Exits with code 0 if all pass, 1 if any fail.

    Examples:
        $ rai release check
        $ rai release check --project /path/to/project
    """
    pyproject_path, changelog_path = _find_project_paths(project)

    results = run_checks(
        project_root=project,
        pyproject_path=pyproject_path,
        changelog_path=changelog_path,
    )

    all_passed = _display_results(results)
    if not all_passed:
        raise typer.Exit(1)


def _resolve_new_version(
    current: str, bump: BumpType | None, version: str | None
) -> str:
    """Determine new version from bump type or explicit version string."""
    if version:
        if not is_pep440(version):
            console.print(f"[red]'{version}' is not valid PEP 440[/red]")
            raise typer.Exit(1)
        return version
    assert bump is not None  # noqa: S101 -- validated by caller
    return bump_version(current, bump)


def _display_release_plan(current: str, new_version: str, today: str) -> None:
    """Print the release plan summary."""
    console.print("[bold]Release Plan[/bold]")
    console.print(f"  Current version: {current}")
    console.print(f"  New version:     {new_version}")
    console.print(f"  Date:            {today}")
    console.print()
    console.print("  Steps:")
    console.print(f"    1. Update pyproject.toml: {current} → {new_version}")
    console.print(f"    2. Update __init__.py: {current} → {new_version}")
    console.print(
        f"    3. Update CHANGELOG.md: [Unreleased] → [{new_version}] - {today}"
    )
    console.print(f"    4. Commit: release: v{new_version}")
    console.print(f"    5. Tag: v{new_version}")
    console.print("    6. Push commit + tag → triggers GitHub Actions release")


def _execute_release(
    new_version: str,
    today: str,
    pyproject_path: Path,
    init_path: Path,
    changelog_path: Path,
    project: Path,
) -> None:
    """Execute version bump, changelog update, commit, tag, and push."""
    # 1-2: Bump version files
    sync_version_files(new_version, pyproject_path=pyproject_path, init_path=init_path)
    console.print("[green]✓ Version bumped[/green]")

    # 3: Update changelog
    if changelog_path.exists():
        from raise_cli.publish.changelog import promote_unreleased

        content = changelog_path.read_text(encoding="utf-8")
        try:
            content = promote_unreleased(content, new_version, today)
            changelog_path.write_text(content, encoding="utf-8")
            console.print("[green]✓ Changelog updated[/green]")
        except ValueError:
            console.print("[yellow]⚠ No unreleased entries to promote[/yellow]")

    # 4: Commit
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "add", str(pyproject_path), str(init_path), str(changelog_path)],
        cwd=project,
        check=True,
    )
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "commit", "-m", f"release: v{new_version}"],
        cwd=project,
        check=True,
    )
    console.print(f"[green]✓ Committed: release: v{new_version}[/green]")

    # 5: Tag
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "tag", f"v{new_version}"],
        cwd=project,
        check=True,
    )
    console.print(f"[green]✓ Tagged: v{new_version}[/green]")

    # 6: Push
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "push", "--follow-tags"],
        cwd=project,
        check=True,
    )
    console.print("[green]✓ Pushed to origin[/green]")

    console.print(f"\n[bold green]Release v{new_version} published.[/bold green]")
    console.print("GitHub Actions will handle PyPI upload.")


@release_app.command("publish")
def publish_command(
    bump: Annotated[
        BumpType | None,
        typer.Option("--bump", "-b", help="Version bump type"),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option("--version", "-v", help="Explicit version (overrides --bump)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would happen without executing"),
    ] = False,
    skip_check: Annotated[
        bool,
        typer.Option("--skip-check", help="Skip quality gates (dangerous)"),
    ] = False,
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """Orchestrate a full release: check, bump, changelog, commit, tag, push.

    Either --bump or --version is required.

    Examples:
        rai release publish --bump alpha
        rai release publish --bump minor --dry-run
        rai release publish --version 2.1.0
    """
    if bump is None and version is None:
        console.print("[red]Either --bump or --version is required[/red]")
        raise typer.Exit(1)

    pyproject_path, changelog_path = _find_project_paths(project)
    init_path = project / "src" / "raise_cli" / "__init__.py"

    if not skip_check:
        results = run_checks(
            project_root=project,
            pyproject_path=pyproject_path,
            changelog_path=changelog_path,
        )
        all_passed = _display_results(results)
        if not all_passed:
            console.print(
                "\n[red]Quality gates failed. Fix issues or use --skip-check.[/red]"
            )
            raise typer.Exit(1)
        console.print()

    current = _read_current_version(pyproject_path)
    new_version = _resolve_new_version(current, bump, version)
    today = date.today().isoformat()

    _display_release_plan(current, new_version, today)

    if dry_run:
        console.print("\n[yellow]Dry run — no changes made[/yellow]")
        return

    console.print()
    if not typer.confirm("Proceed?"):
        console.print("[yellow]Aborted[/yellow]")
        raise typer.Exit(0)

    _execute_release(
        new_version, today, pyproject_path, init_path, changelog_path, project
    )
