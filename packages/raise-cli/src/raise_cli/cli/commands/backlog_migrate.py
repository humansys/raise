"""``rai backlog migrate`` — import the filesystem YAML backlog into SQLite.

Mirrors the ``rai clean`` purge pattern (D1, story design.md): scan -> plan
-> preview -> (optionally) execute, dry-run as the default when stdin is
not a tty. Kept in a dedicated module (D3) — ``backlog.py`` is 3000+ lines
and under drift watch; registration there is a single import + one
``backlog_app.command("migrate")(migrate)`` line.

Story: RAISE-16624 (S16533.4)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.table import Table

from raise_cli.adapters.filesystem_models import BacklogItem
from raise_cli.backlog.migrate import (
    MigrationPlan,
    MigrationResult,
    execute_migration,
    plan_migration,
)
from raise_cli.config.paths import MANIFEST_FILE, resolve_checkout_root
from raise_cli.storage.work_items import WorkItemStore

console = Console()


def _is_interactive() -> bool:
    """Return True when stdin is attached to a terminal.

    Named function so tests can monkeypatch it (Click's CliRunner always
    replaces ``sys.stdin`` — same seam as ``cli/commands/clean.py``).
    """
    return sys.stdin.isatty()


# ---------------------------------------------------------------------------
# Error diagnostics (§4.8) — items/ malformed YAML aborts _load_all_items()
# ---------------------------------------------------------------------------


def _locate_bad_yaml(root: Path) -> str | None:
    """Best-effort diagnostic scan to name the file that broke planning.

    `_load_all_items()`'s error semantics are explicitly out of scope for
    this story (§4.8) — this does NOT feed the plan/execute contract, it
    only improves the error message when `plan_migration` propagates an
    exception raised while parsing `.raise/backlog/items/*.yaml`.
    """
    items_dir = root / ".raise" / "backlog" / "items"
    if not items_dir.is_dir():
        return None
    for yaml_path in sorted(items_dir.glob("*.yaml")):
        try:
            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            BacklogItem.model_validate(raw)
        except Exception:  # noqa: BLE001 — diagnostic best-effort, not authoritative
            return str(yaml_path)
    return None


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_plan(plan: MigrationPlan) -> None:
    """Summary header + actions table + orphan warning + db_only_rows note (§4.3)."""
    fs_count = len(plan.actions) + len(plan.orphan_keys_excluded)
    console.print(
        f"\nBacklog migration scan -- {fs_count} filesystem item(s), "
        f"{len(plan.actions)} planned action(s)\n"
    )

    if not plan.actions and not plan.orphan_keys_excluded and not plan.invalid_files:
        console.print("[green]Nothing to migrate.[/]")
        return

    if plan.actions:
        table = Table(title="ACTIONS")
        table.add_column("key", style="cyan")
        table.add_column("verb", style="yellow")
        table.add_column("fields", style="dim")
        table.add_column("claim", style="magenta")
        table.add_column("comments", justify="right")
        table.add_column("links", justify="right")
        for action in plan.actions:
            table.add_row(
                action.key,
                action.action,
                ", ".join(action.fields) or "-",
                "yes" if action.claim_project else "-",
                str(action.comments),
                str(action.links),
            )
        console.print(table)

    if plan.orphan_keys_excluded:
        console.print(
            f"\n[yellow]ORPHANS:[/] {len(plan.orphan_keys_excluded)} item(s) found "
            "outside the adapter-visible hierarchy, not included:"
        )
        for key in plan.orphan_keys_excluded:
            console.print(f"  - {key}")
        console.print("Run with [bold]--include-orphans[/] to migrate them too.")

    if plan.invalid_files:
        console.print(
            f"\n[yellow]WARNING:[/] {len(plan.invalid_files)} unparseable "
            "orphan file(s), skipped:"
        )
        for path in plan.invalid_files:
            console.print(f"  - {path}")

    if plan.db_only_rows:
        console.print(
            f"\n[blue]NOTE:[/] {plan.db_only_rows} DB row(s) have no filesystem "
            "counterpart -- rai doctor will report them."
        )


def _render_result(result: MigrationResult) -> None:
    """Print per-item outcomes + summary."""
    status_symbols = {
        "done": "[green]OK[/]",
        "skipped": "[yellow]SKIP[/]",
        "failed": "[red]FAIL[/]",
    }
    for outcome in result.outcomes:
        symbol = status_symbols[outcome.status]
        detail = f" ({outcome.detail})" if outcome.detail else ""
        console.print(
            f"  {symbol} {outcome.action.key} [{outcome.action.action}]{detail}"
        )

    done = sum(1 for o in result.outcomes if o.status == "done")
    skipped = sum(1 for o in result.outcomes if o.status == "skipped")
    failed = sum(1 for o in result.outcomes if o.status == "failed")
    console.print(
        f"\nDone: [green]{done}[/] | Skipped: [yellow]{skipped}[/] | "
        f"Failed: [red]{failed}[/]"
    )


def _json_output(
    plan: MigrationPlan, mode: str, result: MigrationResult | None = None
) -> str:
    """Serialize plan (+ result, when executed) as JSON."""
    data: dict[str, object] = {
        "plan": plan.model_dump(mode="json"),
        "mode": mode,
        "result": result.model_dump(mode="json") if result else None,
    }
    return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Manifest residue cleanup (RTEST-42)
# ---------------------------------------------------------------------------


def _detect_manifest_backlog_residue(root: Path) -> bool:
    """Return True if manifest contains the deprecated ``backlog.adapter_default`` key."""
    manifest_path = root / ".raise" / MANIFEST_FILE
    if not manifest_path.exists():
        return False
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return False
    if not isinstance(raw, dict):
        return False
    backlog = raw.get("backlog")
    return isinstance(backlog, dict) and "adapter_default" in backlog


def clean_manifest_backlog_residue(root: Path) -> str | None:
    """Remove ``backlog.adapter_default`` from manifest if present.

    Returns a human-readable summary of what was cleaned, or None if no-op.
    """
    from raise_cli.config.paths import get_raise_dir

    manifest_path = get_raise_dir(root) / MANIFEST_FILE
    if not manifest_path.exists():
        return None

    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if not isinstance(raw, dict):
        return None

    backlog = raw.get("backlog")
    if not isinstance(backlog, dict) or "adapter_default" not in backlog:
        return None

    del backlog["adapter_default"]
    if not backlog:
        del raw["backlog"]

    manifest_path.write_text(
        yaml.dump(raw, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return "removed backlog.adapter_default (deprecated in S16533.5)"


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


def migrate(  # noqa: C901 — CLI command, complexity from option handling
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show plan without executing.")
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", help="Skip [y/N] confirmation.")
    ] = False,
    include_orphans: Annotated[
        bool,
        typer.Option(
            "--include-orphans",
            help="Also migrate items found outside the adapter-visible hierarchy.",
        ),
    ] = False,
    json_output_flag: Annotated[
        bool, typer.Option("--json", help="Output JSON.")
    ] = False,
) -> None:
    """Import the filesystem YAML backlog (.raise/backlog/) into SQLite work_items.

    Idempotent (safe to re-run) and never deletes filesystem files. Without
    flags, defaults to dry-run when stdin is not a tty.
    """
    root = resolve_checkout_root()
    store = WorkItemStore(root)
    console_err = Console(stderr=True)

    has_residue = _detect_manifest_backlog_residue(root)

    effective_dry = (
        dry_run or (not _is_interactive() and not yes) or (json_output_flag and not yes)
    )

    if has_residue and not effective_dry:
        cleaned = clean_manifest_backlog_residue(root)
        if cleaned:
            console_err.print(f"[green]Cleaned manifest:[/] {cleaned}")
    elif has_residue:
        console_err.print(
            "[yellow]Note:[/] manifest has deprecated backlog.adapter_default "
            "(will be removed on next non-dry-run migrate)"
        )

    try:
        plan = plan_migration(root, store, include_orphans=include_orphans)
    except Exception as exc:
        bad_file = _locate_bad_yaml(root)
        if bad_file:
            console.print(f"[red]Error:[/] could not parse {bad_file}: {exc}")
        else:
            console.print(f"[red]Error:[/] migration planning failed: {exc}")
        raise typer.Exit(1) from exc

    if json_output_flag:
        if effective_dry:
            typer.echo(_json_output(plan, "dry-run"))
            raise typer.Exit(2 if plan.actionable else 0)
        result = execute_migration(plan, root, store) if plan.actionable else None
        typer.echo(_json_output(plan, "execute", result))
        raise typer.Exit(0 if (result is None or result.ok) else 1)

    _render_plan(plan)

    if effective_dry:
        if plan.actionable:
            console.print(
                "\n[yellow]Dry run -- nothing was changed.[/]\n"
                "Run [bold]rai backlog migrate --yes[/] to execute."
            )
        raise typer.Exit(2 if plan.actionable else 0)

    if not plan.actionable:
        raise typer.Exit(0)

    if not yes and not typer.confirm("Proceed with migration?", default=False):
        console.print("[red]Aborted.[/]")
        raise typer.Exit(1)

    result = execute_migration(plan, root, store)
    _render_result(result)
    raise typer.Exit(0 if result.ok else 1)
