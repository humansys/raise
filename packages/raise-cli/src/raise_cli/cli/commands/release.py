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
from rich.markup import escape
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.git.branch_guard import assert_head_branch
from raise_cli.graph.backends import get_active_backend
from raise_cli.output.symbols import ARROW, CHECK, WARN
from raise_cli.publish.check import CheckResult, run_checks
from raise_cli.publish.version import (
    BumpType,
    bump_version,
    is_pep440,
    parse_version,
    sync_core_dependency_pin,
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
    """Find pyproject.toml and CHANGELOG.md paths.

    If project is a workspace root (has [tool.uv.workspace] in pyproject.toml),
    auto-detect the publishable package at packages/raise-cli/.
    """
    pyproject_path = project / "pyproject.toml"

    # Auto-detect monorepo: if pyproject.toml has workspace config, look for raise-cli
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        if "[tool.uv.workspace]" in content:
            cli_pkg = project / "packages" / "raise-cli"
            if cli_pkg.exists():
                project = cli_pkg
                pyproject_path = project / "pyproject.toml"

    changelog_path = project / "CHANGELOG.md"
    return pyproject_path, changelog_path


def _find_core_paths(pyproject_path: Path) -> tuple[Path, Path] | None:
    """Find raise-core paths when release runs from the monorepo workspace."""
    if pyproject_path.parent.name != "raise-cli":
        return None

    packages_dir = pyproject_path.parent.parent
    core_dir = packages_dir / "raise-core"
    core_pyproject = core_dir / "pyproject.toml"
    core_init = core_dir / "src" / "raise_core" / "__init__.py"
    if core_pyproject.exists() and core_init.exists():
        return core_pyproject, core_init
    return None


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
        console.print(f"  {icon} {escape(r.gate)}: {escape(r.message)}")
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

    try:
        graph = get_active_backend(graph_path, project_root=project).load()
    except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
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

    Runs 10 quality checks: tests (with coverage diagnostic), types, lint,
    security, build, package validation, changelog, changelog severity
    (RAISE-15661), PEP 440 version, and version sync. Coverage is reported
    but not a blocking gate.

    Exits with code 0 if all pass, 1 if any fail.

    Examples:
        $ rai release check
        $ rai release check --project /path/to/project
    """
    pyproject_path, changelog_path = _find_project_paths(project)
    # Use the resolved project root (may differ from input in monorepos)
    resolved_root = pyproject_path.parent

    results = run_checks(
        project_root=resolved_root,
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


def _is_prerelease(version: str) -> bool:
    """Return True for PEP 440 prerelease versions."""
    return parse_version(version).is_prerelease


def _display_release_plan(
    current: str,
    new_version: str,
    today: str,
    *,
    co_release_core: bool = False,
) -> None:
    """Print the release plan summary."""
    console.print("[bold]Release Plan[/bold]")
    console.print(f"  Current version: {current}")
    console.print(f"  New version:     {new_version}")
    console.print(f"  Date:            {today}")
    console.print()
    console.print("  Steps:")
    package_scope = "raise-cli + raise-core" if co_release_core else "package"
    console.print(
        f"    1. Update version files ({package_scope}): {current} {ARROW} {new_version}"
    )
    console.print(
        f"    2. Update CHANGELOG.md: [Unreleased] → [{new_version}] - {today}"
    )
    console.print("    3. Regenerate uv.lock")
    console.print(f"    4. Commit: release: v{new_version}")
    console.print(f"    5. Tag: v{new_version}")
    publish_target = (
        "GitLab alpha registry"
        if _is_prerelease(new_version)
        else "stable release workflow"
    )
    console.print(f"    6. Push commit + tag {ARROW} triggers {publish_target}")


def _execute_release(
    new_version: str,
    today: str,
    pyproject_path: Path,
    init_path: Path,
    changelog_path: Path,
    extra_version_files: list[tuple[Path, Path]] | None = None,
) -> None:
    """Execute version bump, changelog update, commit, tag, and push.

    All paths must be relative to the repo root (or absolute). Git commands
    run from CWD (repo root) — no cwd override — so paths resolve correctly
    in both flat and monorepo layouts (RAISE-1599).

    Captures the branch before touching anything and re-asserts it after the
    commit lands (RAISE-11103) — this path previously had no branch guard at
    all, so a concurrent checkout in another session could land the release
    commit on the wrong branch undetected.
    """
    # 0: Capture the branch guard before any mutation
    guard_proc = subprocess.run(  # nosec B603,B607 - controlled git command
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    )
    guard_branch = guard_proc.stdout.strip()

    # 1-2: Bump version files
    sync_version_files(new_version, pyproject_path=pyproject_path)
    if extra_version_files:
        # Co-releasing raise-core: pin the raise-core dependency in raise-cli to the
        # exact new version so resolvers cannot install a stale alpha (RAISE-11614).
        sync_core_dependency_pin(pyproject_path, new_version)
    for extra_pyproject, _extra_init in extra_version_files or []:
        sync_version_files(
            new_version,
            pyproject_path=extra_pyproject,
        )
    console.print(f"[green]{CHECK} Version bumped[/green]")

    # 3: Update changelog
    if changelog_path.exists():
        from raise_cli.publish.changelog import promote_unreleased

        content = changelog_path.read_text(encoding="utf-8")
        try:
            content = promote_unreleased(content, new_version, today)
            changelog_path.write_text(content, encoding="utf-8")
            console.print(f"[green]{CHECK} Changelog updated[/green]")
        except ValueError:
            console.print(f"[yellow]{WARN} No unreleased entries to promote[/yellow]")

    # 4: Regenerate lockfile — workspace root is 2 levels above packages/raise-cli/
    uv_lock_path = pyproject_path.parents[2] / "uv.lock"
    subprocess.run(  # nosec B603,B607 - controlled uv command, no untrusted input
        ["uv", "lock"],
        check=True,
    )
    console.print(f"[green]{CHECK} uv.lock regenerated[/green]")

    # 5: Commit
    staged_paths = [
        str(pyproject_path),
        str(init_path),
        str(changelog_path),
        str(uv_lock_path),
    ]
    for extra_pyproject, extra_init in extra_version_files or []:
        staged_paths.extend([str(extra_pyproject), str(extra_init)])

    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "add", *staged_paths],
        check=True,
    )
    from raise_cli.telemetry.trailer import resolve_session_id, with_session_trailer

    release_message = with_session_trailer(
        f"release: v{new_version}", resolve_session_id()
    )
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "commit", "-m", release_message],
        check=True,
    )
    console.print(f"[green]{CHECK} Committed: release: v{new_version}[/green]")

    # Post-commit branch-drift guard (RAISE-11103, closes the TOCTOU window)
    branch_ok, current_branch = assert_head_branch(Path.cwd(), guard_branch)
    if not branch_ok:
        cli_error(
            f"Branch drift detected during release: started on '{guard_branch}', "
            f"now on '{current_branch}'. The release commit landed but tag/push "
            "were aborted — verify repository state manually before retrying.",
            hint="A concurrent checkout or branch switch occurred mid-release.",
            exit_code=6,
        )

    # 5: Tag
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "tag", f"v{new_version}"],
        check=True,
    )
    console.print(f"[green]{CHECK} Tagged: v{new_version}[/green]")

    # 6: Push
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "push", "--follow-tags"],
        check=True,
    )
    console.print(f"[green]{CHECK} Pushed to origin[/green]")

    console.print(f"\n[bold green]Release v{new_version} published.[/bold green]")
    console.print(
        "GitHub Actions will publish stable releases to PyPI (alphas go to GitLab only)."
    )


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
    resolved_root = pyproject_path.parent
    init_path = resolved_root / "src" / "raise_cli" / "__init__.py"
    extra_version_files: list[tuple[Path, Path]] = []
    core_paths = _find_core_paths(pyproject_path)
    if core_paths is not None:
        extra_version_files.append(core_paths)

    if not skip_check:
        results = run_checks(
            project_root=resolved_root,
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

    _display_release_plan(
        current,
        new_version,
        today,
        co_release_core=bool(extra_version_files),
    )

    if dry_run:
        console.print("\n[yellow]Dry run — no changes made[/yellow]")
        return

    console.print()
    if not typer.confirm("Proceed?"):
        console.print("[yellow]Aborted[/yellow]")
        raise typer.Exit(0)

    _execute_release(
        new_version,
        today,
        pyproject_path,
        init_path,
        changelog_path,
        extra_version_files=extra_version_files,
    )
