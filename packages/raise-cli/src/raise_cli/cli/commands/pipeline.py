"""`rai pipeline` — terminal lifecycle CLI for pipeline runs (RAISE-13580, RAISE-15051).

Commands:
  token reissue <run_id>        Re-mint an advance token for a wedged run (triple-gated).
  cancel <run_id>               Cancel an active/paused run.
  runs [--all]                  List runs (active + recent terminal, or all).
  prune [--older-than Nd]       Prune terminal runs that have been accounted for.

The token reissue command is a terminal-only CLI surface — NOT an MCP tool — so
that no Task/Agent subagent can invoke it. It is triple-gated:

    (a) the caller must hold the ADR-094 worktree lease for the run,
    (b) an interactive TTY confirmation, and
    (c) the run must be in a detected lockout state.

``cancel``, ``runs``, and ``prune`` are lower-risk read/write commands with no
TTY gate or lease requirement.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import secrets
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.pipeline.run_store import get_run_store

pipeline_app = typer.Typer(
    name="pipeline",
    help="Pipeline run recovery (terminal-only; not an MCP tool).",
    no_args_is_help=True,
)
token_app = typer.Typer(
    name="token",
    help="Advance-token recovery for wedged runs.",
    no_args_is_help=True,
)
pipeline_app.add_typer(token_app, name="token")

console = Console()
err_console = Console(stderr=True)

# Dedicated audit channel — every token reissue is recorded here from day one.
_audit = logging.getLogger("raise.audit")


def _stdin_is_interactive() -> bool:
    """True when stdin is a real TTY (patchable seam for tests)."""
    return sys.stdin.isatty()


def _load_run(run_id: str) -> dict[str, Any] | None:
    from raise_cli.pipeline.run_store import get_run_store

    return asyncio.run(get_run_store().load(run_id))


def _save_run(run: dict[str, Any]) -> None:
    from raise_cli.pipeline.run_store import get_run_store

    asyncio.run(get_run_store().save(run))


def _is_lockout(run: dict[str, Any]) -> bool:
    """Detect a run wedged by a lost advance token.

    Lockout ≙ token-bearing (has ``advance_token_hash``) AND still advanceable
    (not cancelled, not past its last phase). Legacy/untokened runs advance
    without a token, so they are never in lockout and need no recovery.
    """
    meta = run.get("metadata", {})
    if not meta.get("advance_token_hash"):
        return False
    if run.get("status") == "cancelled":
        return False
    phases = run.get("phases", [])
    return int(run.get("current_phase_index", 0)) < len(phases)


def _holds_worktree_lease(
    run: dict[str, Any], cwd: str, *, session_override: str | None = None
) -> bool:
    """True when the calling session holds the ADR-094 lease for the run's worktree.

    Args:
        run: The pipeline run dict.
        cwd: Worktree path for lease resolution.
        session_override: Explicit session ID supplied via --session (Fix 2, §3.3).
            When provided, it is threaded through discover_agent_session_id(override=...)
            AND must match the lease's current session_id (gate a check). This
            prevents a non-holder from forging authority by passing any session ID.
    """
    from raise_cli.storage.leases import SqliteLeaseStore, pid_alive
    from raise_cli.storage.worktrees import (
        SqliteWorktreeStore,
        WorktreeNotFoundError,
    )

    meta = run.get("metadata", {})
    path = cwd or meta.get("locked_worktree") or meta.get("start_cwd")
    if not path:
        return False
    project = Path(path)
    try:
        worktree = SqliteWorktreeStore(project).get_by_path(str(project))
    except WorktreeNotFoundError:
        return False
    # Fix 2 (RAISE-15050 §3.3): thread explicit override into discovery chain.
    session_id = discover_agent_session_id(override=session_override)
    if not session_id:
        return False
    lease = SqliteLeaseStore(project).get(worktree.worktree_id)
    if lease is None:
        return False
    # Gate (a): lease must be held by session_id and the PID must be alive.
    # With --session: the supplied value is what session_id resolves to (via override).
    # The lease.session_id must match — this prevents an impostor from claiming
    # authority by naming any session (§3.1 S1 mitigation).
    return lease.session_id == session_id and pid_alive(lease.pid)


@token_app.command("reissue")
def token_reissue(
    run_id: Annotated[
        str, typer.Argument(help="Run ID whose advance token to re-mint.")
    ],
    cwd: Annotated[
        str,
        typer.Option("--cwd", help="Worktree path for lease resolution."),
    ] = "",
    session: Annotated[
        str,
        typer.Option(
            "--session",
            help=(
                "Explicit session ID for gate (a) verification (Fix 2, RAISE-15050 §3.3). "
                "Threads into discover_agent_session_id(override=...). "
                "The supplied value MUST equal lease.session_id — this is not a bypass."
            ),
        ),
    ] = "",
) -> None:
    """Re-mint the per-run advance token for a wedged run (gated recovery)."""
    run = _load_run(run_id)
    if run is None:
        err_console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    # Gate (c): lockout state — refuse on runs that are not actually wedged.
    if not _is_lockout(run):
        err_console.print(
            f"[red]Run {run_id} is not in a lockout state — reissue refused.[/red]"
        )
        raise typer.Exit(1)

    # Gate (a): ADR-094 worktree lease — the actor must own the worktree.
    # Fix 2 (RAISE-15050 §3.3): pass session_override so pipeline_restore's
    # recover agent can provide its current session ID explicitly.
    if not _holds_worktree_lease(run, cwd, session_override=session or None):
        err_console.print(
            "[red]Reissue requires holding the ADR-094 worktree lease for "
            "this run's worktree.[/red]"
        )
        raise typer.Exit(1)

    # Gate (b): interactive TTY confirmation — never non-interactive/scripted.
    if not _stdin_is_interactive():
        err_console.print(
            "[red]Reissue requires an interactive TTY confirmation.[/red]"
        )
        raise typer.Exit(1)
    if not typer.confirm(
        f"Re-mint the advance token for run {run_id}? "
        "This invalidates the current token"
    ):
        err_console.print("[yellow]Reissue aborted — no changes made.[/yellow]")
        raise typer.Exit(1)

    # Re-mint. Only the SHA-256 is persisted; the plaintext is shown once.
    new_token = secrets.token_urlsafe(16)
    run.setdefault("metadata", {})["advance_token_hash"] = hashlib.sha256(
        new_token.encode()
    ).hexdigest()
    _save_run(run)

    # Audited event from day one — who reissued which run.
    _audit.warning(
        "pipeline.advance_token.reissued run_id=%s session_id=%s issue=%s",
        run_id,
        discover_agent_session_id() or "unknown",
        run.get("issue_id", "unknown"),
    )

    console.print(f"[green]Re-minted advance token for run {run_id}.[/green]")
    console.print(f"advance_token: {new_token}")
    console.print(
        "[yellow]Present this on pipeline_advance. Do NOT include it in "
        "subagent briefs.[/yellow]"
    )


# ---------------------------------------------------------------------------
# Helpers for cancel / runs / prune
# ---------------------------------------------------------------------------

_ACTIVE_STATUSES: frozenset[str] = frozenset({"started", "paused", "gate_pending"})
_TERMINAL_STATUSES: frozenset[str] = frozenset({"completed", "cancelled", "failed"})


def _has_backlog_event(
    conn: sqlite3.Connection,
    project_id: str,
    run_id: str,
    phase_id: str,
    issue_key: str,
) -> bool:
    """Return True when a matching BacklogTransitionEvent row exists in the DB."""
    row = conn.execute(
        "SELECT 1 FROM pipeline_backlog_events"
        " WHERE project_id = ? AND run_id = ? AND phase_id = ? AND issue_key = ?"
        " LIMIT 1",
        (project_id, run_id, phase_id, issue_key),
    ).fetchone()
    return row is not None


def _parse_duration(s: str) -> timedelta:
    """Parse a simple duration string like ``30d`` or ``7d`` into a timedelta.

    Only days are supported for now (e.g. ``30d``).  Unrecognised formats
    fall back to 30 days.
    """
    m = re.fullmatch(r"(\d+)d", s.strip())
    if m:
        return timedelta(days=int(m.group(1)))
    import click

    click.echo(
        f"Warning: unrecognised duration format '{s}' — defaulting to 30d. Use e.g. '7d'.",
        err=True,
    )
    return timedelta(days=30)


def _phase_has_applied_transition(phase: dict[str, Any]) -> tuple[bool, str]:
    """Return (True, issue_key) when a phase has outcome='applied' in backlog_transition.

    Returns (False, '') otherwise.
    """
    bt: dict[str, Any] | None = phase.get("backlog_transition")
    if not bt:
        return False, ""
    if bt.get("outcome") != "applied":
        return False, ""
    issue_key: str = bt.get("issue_key") or ""
    return True, issue_key


def _is_prune_eligible(
    run: dict[str, Any],
    *,
    threshold: datetime,
    force: bool,
    conn: sqlite3.Connection | None,
    project_id: str,
) -> bool:
    """Return True when a run is eligible for pruning.

    Eligibility criteria:
    1. Status is terminal (completed / cancelled / failed).
    2. ``started_at`` is older than ``threshold``.
    3. Without ``--force``: every phase with outcome='applied' must have a
       matching row in ``pipeline_backlog_events``.
    """
    if run.get("status") not in _TERMINAL_STATUSES:
        return False
    started_raw: str = run.get("started_at") or ""
    try:
        started = datetime.fromisoformat(started_raw)
    except (ValueError, TypeError):
        return False
    # Normalise to UTC for comparison (started_at may be offset-aware).
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    if started >= threshold:
        return False
    if force:
        return True
    # Event-record check: every applied phase needs a DB record.
    if conn is None:
        return True  # Non-local backend — skip event check.
    phases: list[dict[str, Any]] = run.get("phases") or []
    for phase in phases:
        phase_id: str = phase.get("id") or ""
        has_applied, issue_key = _phase_has_applied_transition(phase)
        if has_applied and not _has_backlog_event(
            conn, project_id, run["run_id"], phase_id, issue_key
        ):
            return False
    return True


# ---------------------------------------------------------------------------
# rai pipeline cancel <run_id>
# ---------------------------------------------------------------------------


@pipeline_app.command("cancel")
def pipeline_cancel(
    run_id: Annotated[str, typer.Argument(help="ID of the run to cancel.")],
) -> None:
    """Cancel an active or paused pipeline run.

    Only ``started``, ``paused``, or ``gate_pending`` runs can be cancelled.
    Completed, cancelled, or failed runs are rejected with exit code 1.
    """
    store = get_run_store()
    run = asyncio.run(store.load(run_id))
    if run is None:
        err_console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)
    status: str = run.get("status", "")
    if status not in _ACTIVE_STATUSES:
        err_console.print(
            f"[red]Run {run_id} is not active (status={status!r}) — cancel refused.[/red]"
        )
        raise typer.Exit(1)
    run["status"] = "cancelled"
    asyncio.run(store.save(run))
    console.print(f"[green]Run {run_id} cancelled.[/green]")


# ---------------------------------------------------------------------------
# rai pipeline runs [--all]
# ---------------------------------------------------------------------------

_TERMINAL_RUNS_LIMIT = 20


@pipeline_app.command("runs")
def pipeline_runs(
    all_runs: Annotated[
        bool,
        typer.Option("--all", help="Show all runs instead of only recent ones."),
    ] = False,
) -> None:
    """List pipeline runs.

    Without ``--all``: all active runs plus the last 20 terminal runs,
    ordered by ``started_at`` descending.

    With ``--all``: every run in the store, no limit.
    """
    store = get_run_store()
    runs: list[dict[str, Any]] = asyncio.run(store.list_runs())
    if not runs:
        console.print("[dim]No pipeline runs found.[/dim]")
        return

    if not all_runs:
        active = [r for r in runs if r.get("status") in _ACTIVE_STATUSES]
        terminal = [r for r in runs if r.get("status") in _TERMINAL_STATUSES]
        # list_runs() already returns newest-first; cap terminal at limit.
        terminal = terminal[:_TERMINAL_RUNS_LIMIT]
        display = active + terminal
    else:
        display = runs

    table = Table(title="Pipeline Runs")
    table.add_column("run_id", style="cyan", no_wrap=True)
    table.add_column("pipeline", style="blue")
    table.add_column("issue_id", style="magenta")
    table.add_column("status", style="bold")
    table.add_column("started_at")
    table.add_column("paused_at_phase")

    for r in display:
        status_val: str = r.get("status") or ""
        style = (
            "green"
            if status_val == "completed"
            else ("red" if status_val in ("cancelled", "failed") else "yellow")
        )
        table.add_row(
            r.get("run_id") or "",
            r.get("pipeline_name") or "",
            r.get("issue_id") or "",
            f"[{style}]{status_val}[/{style}]",
            (r.get("started_at") or "")[:19],  # ISO date without microseconds
            r.get("paused_at_phase") or "",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# rai pipeline prune [--older-than 30d] [--yes] [--force]
# ---------------------------------------------------------------------------


@pipeline_app.command("prune")
def pipeline_prune(
    older_than: Annotated[
        str,
        typer.Option(
            "--older-than",
            help="Prune runs whose started_at is older than this duration (default 30d).",
        ),
    ] = "30d",
    yes: Annotated[
        bool,
        typer.Option("--yes", help="Execute the prune (default is dry-run)."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Skip BacklogTransitionEvent eligibility check (age + terminal only).",
        ),
    ] = False,
) -> None:
    """Prune terminal pipeline runs that have been accounted for.

    Dry-run by default — use ``--yes`` to execute deletion.

    Eligibility (without ``--force``):
    - Run is in a terminal state (completed / cancelled / failed).
    - ``started_at`` is older than ``--older-than`` threshold.
    - Every phase with an applied backlog transition has a matching record
      in ``pipeline_backlog_events`` (confirming the transition was observed).

    Use ``--force`` to skip the event-record check and prune by age alone.
    """
    delta = _parse_duration(older_than)
    threshold = datetime.now(UTC) - delta

    store = get_run_store()
    runs: list[dict[str, Any]] = asyncio.run(store.list_runs())

    # Resolve local SQLite connection + project_id for event-record queries.
    # Non-local backends (ApiRunStore, PostgresRunStore) are out of scope for
    # prune — the event check is skipped for those (same as --force for non-local).
    from raise_cli.pipeline.run_store import SqliteRunStore

    conn: sqlite3.Connection | None = None
    project_id = ""
    if isinstance(store, SqliteRunStore):
        conn, project_id = store.local_db()

    eligible: list[dict[str, Any]] = [
        r
        for r in runs
        if _is_prune_eligible(
            r,
            threshold=threshold,
            force=force,
            conn=conn,
            project_id=project_id,
        )
    ]

    if not eligible:
        console.print(
            f"[dim]No eligible runs found older than {older_than}.[/dim]"
            if not yes
            else f"[dim]Nothing to prune (older-than {older_than}).[/dim]"
        )
        return

    if not yes:
        console.print(
            f"[yellow]Dry-run: {len(eligible)} run(s) would be pruned "
            f"(older than {older_than}):[/yellow]"
        )
        for r in eligible:
            console.print(
                f"  [cyan]{r['run_id']}[/cyan]  "
                f"{r.get('pipeline_name', '')}  "
                f"{r.get('status', '')}  "
                f"{(r.get('started_at') or '')[:10]}"
            )
        console.print("[dim]Re-run with --yes to execute.[/dim]")
        return

    deleted = 0
    for r in eligible:
        asyncio.run(store.delete(r["run_id"]))
        deleted += 1
    console.print(f"[green]Pruned {deleted} run(s).[/green]")
