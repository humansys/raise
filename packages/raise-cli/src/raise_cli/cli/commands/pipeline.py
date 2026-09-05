"""`rai pipeline` — terminal lifecycle CLI for pipeline runs (RAISE-13580, RAISE-15051, RAISE-15781).

Commands:
  start <pipeline> <issue_id>   Start a pipeline run (non-MCP entry point, RAISE-15781 R2).
  advance <run_id> --advance-token <tok>  Advance a run to the next phase (MCP fallback, RAISE-15793).
  status <run_id>               Show run info and a phase table (RAISE-15794).
  status --list                 List recent runs (RAISE-15794).
  token reissue <run_id>        Re-mint an advance token for a wedged run (triple-gated).
  cancel <run_id>               Cancel an active/paused run.
  runs [--all]                  List runs (active + recent terminal, or all).
  prune [--older-than Nd]       Prune terminal runs that have been accounted for.
  reconcile [--apply]           Mark runs stuck in 'running' (>30d) as failed (RAISE-15796).

The token reissue command is a terminal-only CLI surface — NOT an MCP tool — so
that no Task/Agent subagent can invoke it. It is triple-gated:

    (a) the caller must hold the ADR-094 worktree lease for the run — or, for
        runs anchored at the (never registered) main checkout, satisfy the
        implicit main-checkout lease (RAISE-15737),
    (b) an interactive TTY confirmation (bypassed by ``--non-interactive`` for
        agent/CI contexts — RAISE-15847), and
    (c) the run must be in a detected lockout state.

``--non-interactive`` skips gate (b) only.  Gates (a) and (c) remain in force
regardless.  Use from ``pipeline_restore`` when the advance token is lost after
a compaction event.

``cancel``, ``runs``, and ``prune`` are lower-risk read/write commands with no
TTY gate or lease requirement.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
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
from raise_cli.pipeline.run_store import (
    OptimisticLockError,
    PipelineRunStore,
    get_run_store,
)

pipeline_app = typer.Typer(
    name="pipeline",
    help="Pipeline lifecycle CLI (start + recovery).",
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


def is_lockout(run: dict[str, Any]) -> bool:
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


def holds_worktree_lease(
    run: dict[str, Any], cwd: str, *, session_override: str | None = None
) -> bool:
    """True when the calling session holds the ADR-094 lease for the run's worktree.

    When the resolved path is not a registered worktree, falls back to the
    implicit main-checkout lease (RAISE-15737, see ``_holds_implicit_main_lease``).

    Args:
        run: The pipeline run dict.
        cwd: Worktree path for lease resolution.
        session_override: Explicit session ID supplied via --session (Fix 2, §3.3).
            When provided, it is threaded through discover_agent_session_id(override=...)
            AND must match the lease's current session_id (gate a check). This
            prevents a non-holder from forging authority by passing any session ID.
    """
    import os

    from raise_cli.storage.leases import LeaseHeldError, SqliteLeaseStore, pid_alive
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
        # RAISE-15737 Gap B: the main checkout is never registered in
        # ``worktrees`` — fall back to the implicit main-checkout lease.
        return _holds_implicit_main_lease(
            run, project, session_override=session_override
        )
    # Fix 2 (RAISE-15050 §3.3): thread explicit override into discovery chain.
    session_id = discover_agent_session_id(override=session_override)
    if not session_id:
        return False
    store = SqliteLeaseStore(project)
    lease = store.get(worktree.worktree_id)
    if lease is None:
        return False
    # ``pipeline restore`` and the returned ``token reissue`` command run in
    # separate CLI processes.  Restore therefore leaves its own short-lived
    # PID in the lease.  A matching session may reclaim only that dead holder
    # under SQLite's atomic acquire; another session remains subject to the
    # normal live/expiry takeover rules.
    if lease.session_id == session_id and not pid_alive(lease.pid):
        try:
            lease = store.acquire(
                worktree.worktree_id, session_id=session_id, pid=os.getpid()
            )
        except LeaseHeldError:
            return False
    # Gate (a): lease must be held by session_id and the PID must be alive.
    # With --session: the supplied value is what session_id resolves to (via override).
    # The lease.session_id must match — this prevents an impostor from claiming
    # authority by naming any session (§3.1 S1 mitigation).
    return lease.session_id == session_id and pid_alive(lease.pid)


def _holds_implicit_main_lease(
    run: dict[str, Any], path: Path, *, session_override: str | None = None
) -> bool:
    """Implicit lease for runs anchored at the unregistered main checkout.

    RAISE-15737 Gap B: the main checkout is never registered in the
    ``worktrees`` table (ADR-094 registers only linked worktrees), so the
    strict lease gate made ``rai pipeline token reissue`` unsatisfiable for
    any run anchored there — even for a human on a TTY.

    Fallback, reached ONLY when the path is not a registered worktree:

    - the path must match the run's own anchor (``locked_worktree`` /
      ``start_cwd``) — an impostor cannot reissue a run anchored elsewhere;
    - the path must be a real main checkout: ``.git`` is a directory (a
      linked worktree has a ``.git`` gitfile instead) and ``.raise/`` exists;
    - the session identity must resolve (explicit ``--session`` override or
      ambient env discovery).

    This is intentionally weaker than a real lease (no PID liveness): the
    remaining gates — (b) interactive TTY confirmation, (c) detected lockout
    state, and the audit record on every reissue — bound the blast radius.
    Registered worktrees keep the strict real-lease requirement; this path
    never applies to them.
    """
    meta = run.get("metadata", {})
    anchored = meta.get("locked_worktree") or meta.get("start_cwd")
    if not anchored:
        return False
    if Path(anchored).resolve() != path.resolve():
        return False
    if not (path / ".git").is_dir() or not (path / ".raise").is_dir():
        return False
    session_id = discover_agent_session_id(override=session_override)
    return bool(session_id)


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
    non_interactive: Annotated[
        bool,
        typer.Option(
            "--non-interactive",
            help=(
                "Bypass TTY gate when reissuing from non-interactive context "
                "(agents, CI, RAISE-15847). "
                "Gates (a) lease and (c) lockout remain in force. "
                "Use from pipeline_restore when advance token is lost after compaction."
            ),
        ),
    ] = False,
) -> None:
    """Re-mint the per-run advance token for a wedged run (gated recovery)."""
    run = _load_run(run_id)
    if run is None:
        err_console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    # Gate (c): lockout state — refuse on runs that are not actually wedged.
    if not is_lockout(run):
        err_console.print(
            f"[red]Run {run_id} is not in a lockout state — reissue refused.[/red]"
        )
        raise typer.Exit(1)

    # Gate (a): ADR-094 worktree lease — the actor must own the worktree.
    # Fix 2 (RAISE-15050 §3.3): pass session_override so pipeline_restore's
    # recover agent can provide its current session ID explicitly.
    if not holds_worktree_lease(run, cwd, session_override=session or None):
        err_console.print(
            "[red]Reissue requires holding the ADR-094 worktree lease for "
            "this run's worktree.[/red]"
        )
        raise typer.Exit(1)

    # Gate (b): interactive TTY confirmation.
    # RAISE-15847: agents run over JSON RPC (no TTY); --non-interactive bypasses
    # the TTY check and the typer.confirm() prompt.  Gates (a) and (c) above
    # are still mandatory regardless of --non-interactive.
    if not non_interactive:
        if not _stdin_is_interactive():
            err_console.print(
                "[red]Reissue requires an interactive TTY confirmation "
                "(or --non-interactive for automated contexts).[/red]"
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
# rai pipeline advance <run_id> --advance-token <token>
# ---------------------------------------------------------------------------


@pipeline_app.command("advance")
def pipeline_advance_cmd(
    run_id: Annotated[str, typer.Argument(help="ID of the run to advance.")],
    advance_token: Annotated[
        str,
        typer.Option(
            "--advance-token",
            help="Per-run capability token from pipeline_start.",
        ),
    ],
    approve: Annotated[
        bool,
        typer.Option("--approve", help="Approve an HITL gate on the current phase."),
    ] = False,
    cwd: Annotated[
        str,
        typer.Option(
            "--cwd", help="Working directory for worktree identity resolution."
        ),
    ] = "",
    phase: Annotated[
        str,
        typer.Option(
            "--phase",
            help="Expected phase id (guards against retry-after-write-race).",
        ),
    ] = "",
) -> None:
    """Advance a pipeline run to the next phase (MCP fallback, RAISE-15793).

    Pure delegation to the async ``pipeline_advance()`` MCP tool (epic D5,
    zero engine logic in the CLI layer): token verification, lease renewal,
    artifact/gate validation, and phase transitions all live in
    ``mcp_tools_pipeline.py``. This command only parses the JSON response
    and renders status-appropriate output.

    The supplied ``advance_token`` is never echoed back.  A delegated
    composite pipeline may return a newly minted, child-scoped token; render
    that one-time value so the caller can advance the child run.
    """
    from raise_cli.pipeline.mcp_tools_pipeline import pipeline_advance

    result_json = asyncio.run(
        pipeline_advance(
            run_id,
            approve=approve,
            cwd=cwd,
            advance_token=advance_token,
            phase=phase,
        )
    )
    result: dict[str, Any] = json.loads(result_json)
    status: str = result.get("status", "")

    if status == "ok":
        current_phase = result.get("current_phase", "")
        console.print(f"[green]Run {run_id}: phase '{current_phase}' ready.[/green]")
        phase_number = result.get("phase_number")
        total_phases = result.get("total_phases")
        if phase_number is not None and total_phases is not None:
            console.print(f"Phase {phase_number}/{total_phases}")
        instruction = result.get("instruction")
        if instruction:
            console.print(f"Instruction: {instruction}")
        return

    if status == "complete":
        message = result.get("message", "Pipeline complete.")
        console.print(f"[green]Run {run_id}: {message}[/green]")
        return

    if status == "gate_pending":
        current_phase = result.get("current_phase", "")
        message = result.get(
            "message", f"Phase '{current_phase}' has a pending HITL gate."
        )
        console.print(f"[yellow]Run {run_id}: {message}[/yellow]")
        console.print("[dim]Re-run with --approve to pass the gate.[/dim]")
        return

    if status == "delegated":
        child_run_id = result.get("child_run_id", "")
        child_pipeline = result.get("child_pipeline", "")
        child_phase = result.get("child_phase", "")
        console.print(
            f"[green]Run {run_id}: delegated to child {child_run_id} "
            f"({child_pipeline}, phase={child_phase}).[/green]"
        )
        instruction = result.get("instruction")
        if instruction:
            console.print(f"Instruction: {instruction}")
        child_token = result.get("advance_token")
        if child_token:
            console.print(f"advance_token: {child_token}")
            console.print(
                "[yellow]Keep this child token private; it is required to "
                "advance the delegated pipeline.[/yellow]"
            )
        return

    if status == "authority_denied":
        reason = result.get("reason", "Authority denied.")
        err_console.print(f"[red]Run {run_id}: authority denied — {reason}[/red]")
        raise typer.Exit(1)

    # error / phase_mismatch / rejected / deterministic_failed / any other
    # non-success status — render generically and exit non-zero. Never
    # echoes advance_token (it is not part of the response payload).
    reason = (
        result.get("reason")
        or result.get("message")
        or status
        or "Unknown error advancing run."
    )
    err_console.print(f"[red]Run {run_id}: {reason}[/red]")
    raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Helpers for cancel / runs / prune
# ---------------------------------------------------------------------------

_ACTIVE_STATUSES: frozenset[str] = frozenset(
    {"started", "running", "paused", "gate_pending"}
)
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
    force: Annotated[
        bool,
        typer.Option("--force", help="Override ownership guard (RAISE-15802)."),
    ] = False,
) -> None:
    """Cancel an active or paused pipeline run.

    Only ``started``, ``paused``, or ``gate_pending`` runs can be cancelled.
    Completed, cancelled, or failed runs are rejected with exit code 1.

    Runs whose worktree lease is held by another live session are protected
    by default — use ``--force`` to override (RAISE-15802).
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
    if not force:
        from raise_cli.pipeline.mcp_tools_pipeline import is_foreign_live_run

        is_foreign, owner_desc = is_foreign_live_run(run)
        if is_foreign:
            err_console.print(
                f"[red]Run {run_id} is owned by a live foreign session: "
                f"{owner_desc}. Use --force to override.[/red]"
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
# rai pipeline status <run_id> | --list
# ---------------------------------------------------------------------------


@pipeline_app.command("status")
def pipeline_status_cmd(
    run_id: Annotated[str, typer.Argument(help="Run ID to inspect.")] = "",
    list_runs: Annotated[
        bool, typer.Option("--list", help="List recent runs instead of one.")
    ] = False,
) -> None:
    """Show run info and a phase table, or list recent runs.

    ``rai pipeline status <run_id>`` prints the run's summary fields
    (run_id, pipeline, issue, status, started_at) followed by a table of
    its phases with the current phase highlighted.

    ``rai pipeline status --list`` prints a Rich table of recent runs —
    active runs plus the last 20 terminal runs, same selection as
    ``rai pipeline runs`` — with no filtering or sorting options.
    """
    store = get_run_store()

    if list_runs:
        runs: list[dict[str, Any]] = asyncio.run(store.list_runs())
        if not runs:
            console.print("[dim]No pipeline runs found.[/dim]")
            return

        active = [r for r in runs if r.get("status") in _ACTIVE_STATUSES]
        terminal = [r for r in runs if r.get("status") in _TERMINAL_STATUSES]
        terminal = terminal[:_TERMINAL_RUNS_LIMIT]
        display = active + terminal

        table = Table(title="Pipeline Runs")
        table.add_column("run_id", style="cyan", no_wrap=True)
        table.add_column("pipeline", style="blue")
        table.add_column("issue", style="magenta")
        table.add_column("status", style="bold")
        table.add_column("started_at")

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
                (r.get("started_at") or "")[:19],
            )
        console.print(table)
        return

    if not run_id:
        console.print("[dim]Provide a run_id or use --list to see recent runs.[/dim]")
        raise typer.Exit(1)

    run = asyncio.run(store.load(run_id))
    if run is None:
        err_console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    status_val = run.get("status") or ""
    console.print(f"[cyan]run_id:[/cyan] {run.get('run_id') or run_id}")
    console.print(f"[cyan]pipeline:[/cyan] {run.get('pipeline_name') or ''}")
    console.print(f"[cyan]issue:[/cyan] {run.get('issue_id') or ''}")
    console.print(f"[cyan]status:[/cyan] {status_val}")
    console.print(f"[cyan]started_at:[/cyan] {run.get('started_at') or ''}")
    if run.get("completed_at"):
        console.print(f"[cyan]completed_at:[/cyan] {run.get('completed_at')}")

    phases: list[dict[str, Any]] = run.get("phases") or []
    current_phase_index = int(run.get("current_phase_index", 0))

    table = Table(title=f"Phases — {run_id}")
    table.add_column("#", style="dim")
    table.add_column("phase_id", style="cyan")
    table.add_column("status", style="bold")
    table.add_column("current")

    for i, phase in enumerate(phases):
        is_current = i == current_phase_index
        table.add_row(
            str(i),
            phase.get("id") or "",
            phase.get("status") or "",
            "[yellow]<-- current[/yellow]" if is_current else "",
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


# ---------------------------------------------------------------------------
# rai pipeline reconcile [--apply]
# ---------------------------------------------------------------------------

_RECONCILE_STUCK_AFTER_DAYS = 30


def _parse_started_at(started_raw: str) -> datetime | None:
    """Parse a run's started_at into a UTC-aware datetime, or None if unusable.

    Empty strings and unparseable values both return None — callers must
    treat these runs separately from genuinely stuck ones rather than
    silently dropping or including them (RAISE-15796 F5).
    """
    if not started_raw:
        return None
    try:
        started = datetime.fromisoformat(started_raw)
    except (ValueError, TypeError):
        return None
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    return started


def _classify_reconcile_candidates(
    runs: list[dict[str, Any]], *, threshold: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split ``running`` runs into (stuck, unparseable) by started_at.

    ``paused`` runs are deliberately excluded here: pausing is a
    user-initiated hold, not a stuck state (RAISE-15796). Only
    ``status == 'running'`` runs are considered at all.
    """
    stuck: list[dict[str, Any]] = []
    unparseable: list[dict[str, Any]] = []
    for r in runs:
        if r.get("status") != "running":
            continue
        started = _parse_started_at(r.get("started_at") or "")
        if started is None:
            unparseable.append(r)
        elif started < threshold:
            stuck.append(r)
    return stuck, unparseable


def _report_unparseable(unparseable: list[dict[str, Any]]) -> None:
    """Print the set-aside list of running runs with unusable started_at."""
    if not unparseable:
        return
    console.print(
        f"[yellow]{len(unparseable)} running run(s) skipped "
        "(empty/unparseable started_at):[/yellow]"
    )
    for r in unparseable:
        console.print(f"  [cyan]{r.get('run_id', '')}[/cyan]")


def _print_reconcile_dry_run(stuck: list[dict[str, Any]]) -> None:
    console.print(
        f"[yellow]Dry-run: {len(stuck)} run(s) would be reconciled "
        "(status=running, started >30d ago):[/yellow]"
    )
    for r in stuck:
        console.print(
            f"  [cyan]{r['run_id']}[/cyan]  "
            f"{r.get('pipeline_name', '')}  "
            f"{r.get('issue_id', '')}  "
            f"{(r.get('started_at') or '')[:19]}"
        )
    console.print("[dim]Re-run with --apply to execute.[/dim]")


def _apply_reconcile(
    store: PipelineRunStore, stuck: list[dict[str, Any]]
) -> tuple[int, int]:
    """Mark each stuck run failed and save it. Returns (reconciled, conflicts)."""
    reconciled = 0
    conflicts = 0
    now_iso = datetime.now(UTC).isoformat()
    for r in stuck:
        r["status"] = "failed"
        r.setdefault("metadata", {})["reconciled_at"] = now_iso
        try:
            asyncio.run(store.save(r))
            reconciled += 1
        except OptimisticLockError:
            conflicts += 1
            err_console.print(
                f"[red]Skipped {r['run_id']}: concurrent write conflict.[/red]"
            )
    return reconciled, conflicts


@pipeline_app.command("reconcile")
def pipeline_reconcile(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Apply reconciliation (default: dry-run)."),
    ] = False,
) -> None:
    """One-time reconciliation of pipeline runs stuck in 'running' (RAISE-15796).

    Scans all runs with ``status == 'running'`` whose ``started_at`` is older
    than 30 days and marks them ``failed``. This recovers runs abandoned by a
    crashed/killed agent process that never reached a terminal state.

    ``paused`` runs are deliberately excluded: pausing is a user-initiated
    hold (via ``pipeline_pause``), not a stuck state, so it carries no
    staleness signal and must not be reconciled by this scan.

    Dry-run by default — use ``--apply`` to write changes. Each reconciled
    run has ``status`` set to ``'failed'`` and ``metadata.reconciled_at``
    stamped with the reconciliation time; the write goes through the run
    store's normal ``save()``, which enforces optimistic-lock (version CAS)
    semantics — a run modified concurrently since it was loaded is skipped
    with a conflict warning rather than clobbered.

    Runs with an empty or unparseable ``started_at`` are neither reconciled
    nor silently ignored — they are reported separately so an operator can
    investigate the underlying data quality issue.
    """
    store = get_run_store()
    runs: list[dict[str, Any]] = asyncio.run(store.list_runs())
    threshold = datetime.now(UTC) - timedelta(days=_RECONCILE_STUCK_AFTER_DAYS)

    stuck, unparseable = _classify_reconcile_candidates(runs, threshold=threshold)
    _report_unparseable(unparseable)

    if not stuck:
        console.print("[dim]No stuck runs found (status=running, >30d old).[/dim]")
        return

    if not apply:
        _print_reconcile_dry_run(stuck)
        return

    reconciled, conflicts = _apply_reconcile(store, stuck)
    console.print(f"[green]Reconciled {reconciled} run(s).[/green]")
    if conflicts:
        console.print(
            f"[yellow]{conflicts} run(s) skipped due to concurrent modification.[/yellow]"
        )


# ---------------------------------------------------------------------------
# rai pipeline start <pipeline_name> <issue_id> [--size XS|S|M|L] [--cwd PATH]
# RAISE-15781 R2: non-MCP entry point for pipeline_start.
# ---------------------------------------------------------------------------


def _resolve_cwd_default() -> str:
    """Return the git toplevel for CWD, or CWD itself if not in a checkout."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return str(Path.cwd())
    top = result.stdout.strip()
    return top if result.returncode == 0 and top else str(Path.cwd())


async def _pipeline_start_async(
    pipeline_name: str, issue_id: str, cwd: str, size: str
) -> str:
    from raise_cli.pipeline.mcp_tools_pipeline import pipeline_start as _ps

    return await _ps(pipeline_name=pipeline_name, issue_id=issue_id, cwd=cwd, size=size)


pipeline_start_fn = _pipeline_start_async


@pipeline_app.command("start")
def pipeline_start_cmd(
    pipeline_name: Annotated[
        str, typer.Argument(help="Pipeline name (e.g. bugfix, story, epic).")
    ],
    issue_id: Annotated[
        str, typer.Argument(help="Issue key for traceability (e.g. RAISE-1281).")
    ],
    size: Annotated[
        str,
        typer.Option("--size", help="Work size: XS, S, M, or L."),
    ] = "",
    cwd: Annotated[
        str,
        typer.Option("--cwd", help="Worktree/checkout path (default: git toplevel)."),
    ] = "",
) -> None:
    """Start a pipeline run (non-MCP entry point, RAISE-15781 R2)."""
    effective_cwd = cwd or _resolve_cwd_default()
    raw = asyncio.run(
        pipeline_start_fn(
            pipeline_name=pipeline_name,
            issue_id=issue_id,
            cwd=effective_cwd,
            size=size,
        )
    )
    payload = json.loads(raw)
    status = payload.get("status", "")
    if status in ("error", "rejected", "deterministic_failed"):
        reason = payload.get("reason") or raw
        recovery_hint = payload.get("recovery_hint")
        err_console.print(f"[red]Pipeline start failed: {reason}[/red]")
        if recovery_hint:
            err_console.print(f"[yellow]{recovery_hint}[/yellow]")
        raise typer.Exit(1)

    run_id = payload.get("run_id", "?")
    phase = payload.get("current_phase", "?")
    console.print(f"[green]Pipeline started:[/green] run_id={run_id}, phase={phase}")
    token = payload.get("advance_token")
    if token:
        console.print(f"advance_token: {token}")
        console.print(
            "[yellow]Keep this token — required for pipeline_advance. "
            "Do NOT include it in subagent briefs.[/yellow]"
        )


# ---------------------------------------------------------------------------
# rai pipeline pause <run_id>  (RAISE-15798)
# ---------------------------------------------------------------------------


@pipeline_app.command("pause")
def pipeline_pause_cmd(
    run_id: Annotated[str, typer.Argument(help="ID of the run to pause.")],
    cwd: Annotated[
        str,
        typer.Option("--cwd", help="Worktree path (passed through to MCP tool)."),
    ] = "",
) -> None:
    """Pause an active pipeline run.

    Delegates to the async ``pipeline_pause()`` MCP tool. The run can be
    resumed by calling ``pipeline_advance`` (or ``rai pipeline advance``).
    """
    from raise_cli.pipeline.mcp_tools_pipeline import pipeline_pause

    result_json = asyncio.run(pipeline_pause(run_id, cwd=cwd))
    result: dict[str, Any] = json.loads(result_json)
    status: str = result.get("status", "")

    if status in ("error", "rejected"):
        reason = result.get("reason") or result.get("message") or "Unknown error."
        err_console.print(f"[red]Run {run_id}: {reason}[/red]")
        raise typer.Exit(1)

    current_phase = result.get("current_phase", "")
    console.print(f"[yellow]Run {run_id}: paused at phase '{current_phase}'.[/yellow]")
    message = result.get("message")
    if message:
        console.print(f"[dim]{message}[/dim]")


# ---------------------------------------------------------------------------
# rai pipeline restore <run_id>  (RAISE-15798)
# ---------------------------------------------------------------------------


@pipeline_app.command("restore")
def pipeline_restore_cmd(
    run_id: Annotated[str, typer.Argument(help="ID of the run to restore.")],
    cwd: Annotated[
        str,
        typer.Option(
            "--cwd",
            help=(
                "Worktree path. When provided, acquires the ADR-094 lease so "
                "that ``pipeline token reissue`` can verify gate (a)."
            ),
        ),
    ] = "",
) -> None:
    """Restore pipeline state after compaction or restart.

    Delegates to the async ``pipeline_restore()`` MCP tool. Returns run state
    plus context for the current phase, and (when ``--cwd`` is supplied) a
    recovery block with lease status and a reissue command if the advance
    token was lost.

    Exit code is non-zero when the tool returns ``status=error`` or
    ``status=worktree_mismatch`` (D3).
    """
    from raise_cli.pipeline.mcp_tools_pipeline import pipeline_restore

    result_json = asyncio.run(pipeline_restore(run_id, cwd=cwd))
    result: dict[str, Any] = json.loads(result_json)
    status: str = result.get("status", "")

    # D3: treat error and rejected (worktree mismatch) as failures; any run status is ok.
    if status in ("error", "rejected"):
        reason = result.get("reason") or result.get("message") or "Unknown error."
        err_console.print(f"[red]Run {run_id}: {reason}[/red]")
        raise typer.Exit(1)

    current_phase = result.get("current_phase", "")
    console.print(
        f"[green]Run {run_id}: restored "
        f"(status={status}, phase={current_phase}).[/green]"
    )
    recovery = result.get("recovery")
    if isinstance(recovery, dict):
        lease_status = recovery.get("lease_status", "")
        console.print(f"[dim]lease_status={lease_status}[/dim]")
        new_token = recovery.get("advance_token")
        if new_token:
            console.print(
                f"[green]advance_token={new_token}[/green]  "
                "[dim](do not put this in subagent briefs)[/dim]"
            )
        reissue = recovery.get("reissue_command")
        if reissue:
            console.print(f"[dim]reissue: {reissue}[/dim]")


# ---------------------------------------------------------------------------
# rai pipeline decision <run_id> --decision <approve|revise|reject>  (RAISE-15798)
# ---------------------------------------------------------------------------


@pipeline_app.command("decision")
def pipeline_decision_cmd(
    run_id: Annotated[
        str, typer.Argument(help="ID of the run to record a decision for.")
    ],
    decision: Annotated[
        str,
        typer.Option(
            "--decision",
            help="Directional HITL decision to record (approve | revise | reject).",
        ),
    ],
    phase: Annotated[
        str,
        typer.Option(
            "--phase",
            help=(
                "Phase id to attribute the decision to. "
                "Defaults to the run's current phase when omitted."
            ),
        ),
    ] = "",
    cwd: Annotated[
        str,
        typer.Option("--cwd", help="Worktree path (passed through to MCP tool)."),
    ] = "",
) -> None:
    """Persist a directional human decision into the run's journal (RAISE-15048).

    Delegates to the async ``pipeline_decision()`` MCP tool. Display-only
    governance trail — appends to ``metadata.hitl_decisions`` with
    ``source='agent'``. Has NO control effect on the pipeline (does not
    advance, pause, or cancel the run). Does not require the advance token.

    ``--decision`` is required (D4).
    """
    from raise_cli.pipeline.mcp_tools_pipeline import pipeline_decision

    result_json = asyncio.run(pipeline_decision(run_id, decision, phase=phase, cwd=cwd))
    result: dict[str, Any] = json.loads(result_json)
    status: str = result.get("status", "")

    if status in ("error", "rejected"):
        reason = result.get("reason") or result.get("message") or "Unknown error."
        err_console.print(f"[red]Run {run_id}: {reason}[/red]")
        raise typer.Exit(1)

    decisions_count = result.get("decisions_count", "?")
    resolved_phase = result.get("phase", phase or "current")
    console.print(
        f"[green]Run {run_id}: decision recorded for phase '{resolved_phase}' "
        f"({decisions_count} total).[/green]"
    )
