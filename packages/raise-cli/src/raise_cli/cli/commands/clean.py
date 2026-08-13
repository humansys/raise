"""``rai clean`` -- detect and clean up legacy installation residues.

Architecture: Epic RAISE-16227 design S2, I2.

Follows the purge pattern: scan -> plan -> preview -> (optionally) execute.
Dry-run means ``execute_clean`` is never called.
"""

from __future__ import annotations

import difflib
import json
import logging
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.legacy.cleaner import (
    CleanAction,
    CleanResult,
    execute_clean,
    plan_clean,
)
from raise_cli.legacy.models import Residue, ScanReport
from raise_cli.legacy.scanner import scan_global, scan_project
from raise_cli.legacy.snooze import compute_set_hash, write_snooze

logger = logging.getLogger(__name__)
console = Console()


def _is_interactive() -> bool:
    """Return True when stdin is attached to a terminal.

    Extracted as a named function so tests can monkeypatch it
    (Click's CliRunner always replaces ``sys.stdin``).
    """
    return sys.stdin.isatty()

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def _render_tables(
    plan: list[CleanAction],
    project_residues: list[Residue],
    global_residues: list[Residue],
) -> None:
    """Print rich tables matching the epic S2 UX sketch."""
    owned_actions = [a for a in plan if a.residue.ownership == "owned"]
    force_actions = [a for a in plan if a.residue.ownership == "advisory"]

    # Collect all advisory residues not in the plan
    planned_paths = {(a.residue.kind, str(a.residue.path)) for a in plan}
    advisory_project = [
        r for r in project_residues
        if r.ownership == "advisory" and (r.kind, str(r.path)) not in planned_paths
    ]
    advisory_global = global_residues  # all global are advisory

    total = len(project_residues) + len(global_residues)
    console.print(f"\nLegacy install scan -- {total} residue(s) found\n")

    if owned_actions or force_actions:
        table = Table(title="ACTIONS (will be processed)")
        table.add_column("path", style="cyan")
        table.add_column("kind", style="green")
        table.add_column("action", style="yellow")
        for a in owned_actions:
            table.add_row(str(a.residue.path), a.residue.kind, a.verb)
        for a in force_actions:
            table.add_row(str(a.residue.path), a.residue.kind, f"{a.verb} (--force)")
        console.print(table)

    if advisory_project or advisory_global:
        table = Table(title="ADVISORY (manual action needed)")
        table.add_column("path", style="cyan")
        table.add_column("kind", style="green")
        table.add_column("hint", style="dim")
        for r in advisory_project:
            table.add_row(str(r.path), r.kind, r.action_hint)
        for r in advisory_global:
            table.add_row(str(r.path), r.kind, r.action_hint)
        console.print(table)


def _render_result(result: CleanResult) -> None:
    """Print execution results."""
    status_symbols = {
        "done": "[green]OK[/]",
        "skipped": "[yellow]SKIP[/]",
        "failed": "[red]FAIL[/]",
    }
    for outcome in result.outcomes:
        symbol = status_symbols[outcome.status]
        console.print(f"  {symbol} {outcome.action.residue.kind}: {outcome.detail}")
        if outcome.backup_path:
            console.print(f"       backup: {outcome.backup_path}")

    for note in result.notes:
        console.print(f"  [blue]NOTE:[/] {note}")

    for err in result.errors:
        console.print(f"  [red]ERROR:[/] {err}")


# ---------------------------------------------------------------------------
# Diff preview for --fix-config
# ---------------------------------------------------------------------------


def _print_colored_diff(diff_lines: list[str]) -> None:
    """Print unified diff lines with color: + green, - red, @@ cyan, headers bold."""
    from rich.text import Text

    for line in diff_lines:
        stripped = line.rstrip("\n")
        if line.startswith("---") or line.startswith("+++"):
            console.print(Text(stripped, style="bold"))
        elif line.startswith("@@"):
            console.print(Text(stripped, style="cyan"))
        elif line.startswith("+"):
            console.print(Text(stripped, style="green"))
        elif line.startswith("-"):
            console.print(Text(stripped, style="red"))
        else:
            console.print(Text(stripped))


def _resolve_rel(action: CleanAction, root: Path) -> str | None:
    """Resolve the relative config path for a fix-config action."""
    if action.residue.kind == "stale-mcp-command":
        return ".mcp.json"
    try:
        return str(action.residue.path.relative_to(root))
    except ValueError:
        console.print(f"  [yellow]warning:[/] {action.residue.path} outside project root")
        return None


def _render_fix_config_diffs(plan: list[CleanAction], root: Path) -> None:
    """Print unified diffs for fix-config actions.

    Deduplicates by resolved path.  Per-file try/except: render failure
    prints a warning line, never aborts.
    """
    from raise_cli.worktree.provision import render_runtime_config

    seen: set[Path] = set()
    for action in plan:
        if action.verb != "fix-config":
            continue
        config_path = action.residue.path
        resolved = config_path.resolve() if config_path.exists() else config_path
        if resolved in seen:
            continue
        seen.add(resolved)

        rel = _resolve_rel(action, root)
        if rel is None:
            continue

        try:
            current = config_path.read_text(encoding="utf-8") if config_path.is_file() else ""
        except OSError:
            current = ""

        try:
            proposed = render_runtime_config(root, rel)
        except Exception as exc:  # noqa: BLE001
            console.print(f"  [yellow]warning:[/] could not render {rel}: {exc}")
            continue

        if current == proposed:
            console.print(f"  {rel}: already up to date")
            continue

        diff_lines = list(difflib.unified_diff(
            current.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        ))
        _print_colored_diff(diff_lines)


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def _json_output(
    report: ScanReport,
    global_residues: list[Residue],
    plan: list[CleanAction],
    mode: str,
    set_hash: str,
    result: CleanResult | None = None,
) -> str:
    """Serialize full state as JSON."""
    data: dict[str, object] = {
        "report": report.model_dump(mode="json"),
        "global": [r.model_dump(mode="json") for r in global_residues],
        "plan": [a.model_dump(mode="json") for a in plan],
        "mode": mode,
        "set_hash": set_hash,
        "result": result.model_dump(mode="json") if result else None,
    }
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _do_execute(
    plan: list[CleanAction],
    root: Path,
    report: ScanReport,
    *,
    ignore_tracked: bool = False,
) -> CleanResult:
    """Execute the plan and add contextual notes."""
    result = execute_clean(plan, project_root=root, ignore_tracked=ignore_tracked)

    has_dep_removal = any(a.verb in ("remove-line", "remove-entry") for a in plan)
    has_uvlock_residue = any(r.kind == "uvlock-entry" for r in report.residues)
    if has_dep_removal and has_uvlock_residue:
        result.notes.append("run `uv lock` to regenerate the lockfile")

    return result


def _validate_flags(force: bool, yes: bool) -> None:
    """Check flag combinations; raise ``typer.Exit(1)`` on conflict."""
    if force and yes:
        console.print(
            "[red]Error:[/] cannot combine --force with --yes; "
            "--force requires explicit confirmation."
        )
        raise typer.Exit(1)

    if force and not _is_interactive():
        console.print("[red]Error:[/] --force requires a tty for interactive confirmation.")
        raise typer.Exit(1)


def _handle_json_mode(
    effective_dry: bool,
    report: ScanReport,
    global_residues: list[Residue],
    plan: list[CleanAction],
    set_hash: str,
    project_set_hash: str,
    root: Path,
    *,
    ignore_tracked: bool = False,
) -> None:
    """Handle --json output and exit."""
    mode = "dry-run" if effective_dry else "execute"
    if effective_dry:
        output = _json_output(report, global_residues, plan, mode, set_hash)
        write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
        typer.echo(output)
        raise typer.Exit(2 if plan else 0)

    result_obj: CleanResult | None = None
    if plan:
        result_obj = _do_execute(plan, root, report, ignore_tracked=ignore_tracked)
    output = _json_output(report, global_residues, plan, mode, set_hash, result_obj)
    write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
    typer.echo(output)
    exit_code = 1 if result_obj and not result_obj.ok else 0
    raise typer.Exit(exit_code)


def _confirm_and_execute(
    force: bool,
    yes: bool,
    plan: list[CleanAction],
    report: ScanReport,
    root: Path,
    set_hash: str,
    project_set_hash: str,
    *,
    ignore_tracked: bool = False,
) -> None:
    """Prompt for confirmation, execute, and exit."""
    # Show diff preview before prompt when fix-config actions present
    fix_config_actions = [a for a in plan if a.verb == "fix-config"]
    if fix_config_actions and ignore_tracked:
        _render_fix_config_diffs(fix_config_actions, root)

    if force:
        answer = typer.prompt("Type 'yes' to confirm destructive cleanup")
        if answer != "yes":
            console.print("[red]Aborted.[/]")
            write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
            raise typer.Exit(1)
    elif not yes:
        if not typer.confirm("Proceed with cleanup?", default=False):
            console.print("[red]Aborted.[/]")
            write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
            raise typer.Exit(1)

    if not plan:
        console.print("\n[green]Nothing to do.[/]")
        write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
        raise typer.Exit(0)

    result = _do_execute(plan, root, report, ignore_tracked=ignore_tracked)
    _render_result(result)
    write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)

    raise typer.Exit(0 if result.ok else 1)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


def clean_command(
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show plan without executing.")] = False,
    yes: Annotated[bool, typer.Option("--yes", help="Skip [y/N] confirmation.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Include advisory residues (requires typing 'yes').")] = False,
    fix_config: Annotated[bool, typer.Option("--fix-config", help="Process only fix-config actions.")] = False,
    json_output_flag: Annotated[bool, typer.Option("--json", help="Output JSON.")] = False,
) -> None:
    """Detect and clean up legacy installation residues.

    Scans the current project for leftovers from per-project raise-cli
    installations and migrates to the binary-global layout.

    Without flags, defaults to dry-run when stdin is not a tty.
    """
    root = Path.cwd()
    _validate_flags(force, yes)

    # C1 fix: --json always requires --yes to execute.  Without it,
    # JSON mode is forced to dry-run (cannot prompt interactively).
    effective_dry = (
        dry_run
        or (not _is_interactive() and not yes)
        or (json_output_flag and not yes)
    )

    report = scan_project(root)
    global_residues = scan_global()

    plan = plan_clean(report, force=force)
    if fix_config:
        plan = [a for a in plan if a.verb == "fix-config"]

    all_residues = list(report.residues) + global_residues
    set_hash = compute_set_hash(all_residues)
    project_set_hash = compute_set_hash(list(report.residues))

    if json_output_flag:
        _handle_json_mode(
            effective_dry, report, global_residues, plan, set_hash,
            project_set_hash, root,
            ignore_tracked=fix_config,
        )

    _render_tables(plan, report.residues, global_residues)

    if effective_dry:
        # Show diff preview in dry-run when fix-config
        fix_config_plan = [a for a in plan if a.verb == "fix-config"]
        if fix_config and fix_config_plan:
            _render_fix_config_diffs(fix_config_plan, root)

        if plan:
            console.print("\n[yellow]Dry run -- nothing was changed.[/]")
            console.print("Run [bold]rai clean[/] to process owned residues.")
            if not force:
                console.print(
                    "Run [bold]rai clean --force[/] to process ALL residues "
                    "(including advisory)."
                )
        else:
            console.print("\n[green]No actionable residues found.[/]")
        write_snooze(root, set_hash=set_hash, project_set_hash=project_set_hash)
        raise typer.Exit(2 if plan else 0)

    _confirm_and_execute(
        force, yes, plan, report, root, set_hash, project_set_hash,
        ignore_tracked=fix_config,
    )
