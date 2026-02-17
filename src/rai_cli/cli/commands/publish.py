"""Publish CLI commands — quality gates and release workflow."""

from __future__ import annotations

import re
import subprocess  # nosec B404 - subprocess required for git operations in CLI tool
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from rai_cli.publish.check import CheckResult, run_checks
from rai_cli.publish.version import (
    BumpType,
    bump_version,
    is_pep440,
    sync_version_files,
)

publish_app = typer.Typer(help="Publish and release management commands")
console = Console()


def _find_project_paths(project: Path) -> tuple[Path, Path, Path]:
    """Find pyproject.toml, __init__.py, and CHANGELOG.md paths.

    Args:
        project: Project root directory.

    Returns:
        Tuple of (pyproject_path, init_path, changelog_path).
    """
    pyproject_path = project / "pyproject.toml"
    changelog_path = project / "CHANGELOG.md"

    # Find __init__.py with __version__ by reading pyproject.toml for package name
    init_path = project / "src" / "rai_cli" / "__init__.py"
    return pyproject_path, init_path, changelog_path


def _read_current_version(pyproject_path: Path) -> str:
    """Read current version from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml.

    Returns:
        Current version string.

    Raises:
        typer.Exit: If version cannot be read.
    """
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
    """Display check results with Rich formatting.

    Args:
        results: List of check results.

    Returns:
        True if all passed, False otherwise.
    """
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


@publish_app.command("check")
def check_command(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root path"),
    ] = Path("."),
) -> None:
    """Run all quality gates before publishing.

    Runs 10 quality checks: tests, types, lint, security, coverage,
    build, package validation, changelog, PEP 440 version, and version sync.

    Exits with code 0 if all pass, 1 if any fail.
    """
    pyproject_path, init_path, changelog_path = _find_project_paths(project)

    results = run_checks(
        project_root=project,
        pyproject_path=pyproject_path,
        init_path=init_path,
        changelog_path=changelog_path,
    )

    all_passed = _display_results(results)
    if not all_passed:
        raise typer.Exit(1)


@publish_app.command("release")
def release_command(
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
        rai publish release --bump alpha
        rai publish release --bump minor --dry-run
        rai publish release --version 2.1.0
    """
    if bump is None and version is None:
        console.print("[red]Either --bump or --version is required[/red]")
        raise typer.Exit(1)

    pyproject_path, init_path, changelog_path = _find_project_paths(project)

    # Run checks unless skipped
    if not skip_check:
        results = run_checks(
            project_root=project,
            pyproject_path=pyproject_path,
            init_path=init_path,
            changelog_path=changelog_path,
        )
        all_passed = _display_results(results)
        if not all_passed:
            console.print("\n[red]Quality gates failed. Fix issues or use --skip-check.[/red]")
            raise typer.Exit(1)
        console.print()

    # Determine new version
    current = _read_current_version(pyproject_path)

    if version:
        if not is_pep440(version):
            console.print(f"[red]'{version}' is not valid PEP 440[/red]")
            raise typer.Exit(1)
        new_version = version
    else:
        assert bump is not None  # nosec B101 - validated at line 159-161
        new_version = bump_version(current, bump)

    today = date.today().isoformat()

    # Display plan
    console.print("[bold]Release Plan[/bold]")
    console.print(f"  Current version: {current}")
    console.print(f"  New version:     {new_version}")
    console.print(f"  Date:            {today}")
    console.print()
    console.print("  Steps:")
    console.print(f"    1. Update pyproject.toml: {current} → {new_version}")
    console.print(f"    2. Update __init__.py: {current} → {new_version}")
    console.print(f"    3. Update CHANGELOG.md: [Unreleased] → [{new_version}] - {today}")
    console.print(f"    4. Commit: release: v{new_version}")
    console.print(f"    5. Tag: v{new_version}")
    console.print("    6. Push commit + tag → triggers GitHub Actions release")

    if dry_run:
        console.print("\n[yellow]Dry run — no changes made[/yellow]")
        return

    # Confirm
    console.print()
    if not typer.confirm("Proceed?"):
        console.print("[yellow]Aborted[/yellow]")
        raise typer.Exit(0)

    # Execute
    # 1-2: Bump version files
    sync_version_files(new_version, pyproject_path=pyproject_path, init_path=init_path)
    console.print("[green]✓ Version bumped[/green]")

    # 3: Update changelog
    if changelog_path.exists():
        from rai_cli.publish.changelog import promote_unreleased

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

    # 6: Push (with confirmation already given)
    subprocess.run(  # nosec B603,B607 - controlled git commands, no untrusted input
        ["git", "push", "--follow-tags"],
        cwd=project,
        check=True,
    )
    console.print("[green]✓ Pushed to origin[/green]")

    console.print(f"\n[bold green]Release v{new_version} published.[/bold green]")
    console.print("GitHub Actions will handle PyPI upload.")
