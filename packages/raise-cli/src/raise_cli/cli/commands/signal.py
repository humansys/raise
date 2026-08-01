"""CLI commands for Rai's telemetry signals: work lifecycle, sessions, calibration.

The signal group owns commands that emit telemetry events to JSONL files.
These were extracted from the `memory` God Object in RAISE-247 (ADR-038).

Commands:
- emit-work: Emit a work lifecycle event (epic/story phases)
- emit-session: Emit a session completion event
- emit-calibration: Emit an estimation calibration event
- backfill: Replay historical pipeline runs as work events (S2.6)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal, get_args

import typer
from rich.console import Console

from raise_cli._agent_session import discover_agent_runtime, discover_agent_session_id
from raise_cli.cli.error_handler import cli_error
from raise_cli.output.symbols import ARROW, CHECK, CROSS, PAUSE, PLAY
from raise_cli.session import resolve_session_id_optional
from raise_cli.telemetry.emitter import UnifiedEmitter, emit
from raise_cli.telemetry.phase_map import normalize_phase
from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    SessionEvent,
    WorkLifecycle,
)
from raise_cli.work_events.backfill import BackfillStats, scan_runs

logger = logging.getLogger(__name__)

signal_app = typer.Typer(
    name="signal",
    help="Emit lifecycle and telemetry signals",
    no_args_is_help=True,
)

console = Console()


def _resolve_agent_session(flag_value: str | None) -> str | None:
    """Resolve agent session_id for emit-* events.

    Precedence: explicit --cc-session-id flag > runtime priority chain.
    """
    if flag_value:
        return flag_value
    return discover_agent_session_id()


def _validate_work_inputs(
    event_type: str,
    phase: str | None,
    work_type_lower: str,
) -> str:
    """Validate event type and normalized phase. Returns normalized phase (or 'init').

    work_type is open — any string is accepted.
    phase is validated after normalization via PHASE_MAP.
    """
    valid_events: list[
        Literal["start", "complete", "blocked", "unblocked", "abandoned", "ar-skip"]
    ] = ["start", "complete", "blocked", "unblocked", "abandoned", "ar-skip"]
    if event_type not in valid_events:
        cli_error(
            f"Invalid event: {event_type}",
            hint=f"Valid events: {', '.join(valid_events)}",
            exit_code=7,
        )

    raw_phase = phase or "init"
    normalized = normalize_phase(work_type_lower, raw_phase)

    # Derived from the WorkLifecycle.phase Literal — single source of truth
    # (RAISE-8347: hardcoded copies drift when the schema gains phases).
    valid_phases: tuple[str, ...] = get_args(
        WorkLifecycle.model_fields["phase"].annotation
    )
    if normalized not in valid_phases:
        cli_error(
            f"Invalid phase: {phase}",
            hint=f"Valid phases: {', '.join(valid_phases)}",
            exit_code=7,
        )

    return normalized


def _resolve_branch(explicit: str | None) -> str | None:
    """Return the git branch name, preferring an explicit value."""
    if explicit:
        return explicit
    try:
        import subprocess

        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        branch = result.stdout.strip()
        return branch or None
    except Exception:  # noqa: BLE001
        return None


def _resolve_commit(explicit: str | None) -> str | None:
    """Return the git HEAD commit hash, preferring an explicit value."""
    if explicit:
        return explicit
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit = result.stdout.strip()
        return commit or None
    except Exception:  # noqa: BLE001
        return None


def _dispatch_work_hook(
    work_type_lower: str,
    work_id: str,
    event_type: str,
    phase: str,
    mission_id: str | None = None,
    task: str | None = None,
    branch: str | None = None,
) -> None:
    """Bridge: fire WorkLifecycleEvent to hook system (non-fatal)."""
    try:
        from raise_cli.hooks.emitter import create_emitter
        from raise_cli.hooks.events import WorkLifecycleEvent

        emitter = create_emitter()
        emitter.emit(
            WorkLifecycleEvent(
                work_type=work_type_lower,
                work_id=work_id,
                event=event_type,
                phase=phase,
                mission_id=mission_id or "",
                task=task or "",
                branch=branch or "",
            )
        )
    except Exception:  # noqa: BLE001
        logger.warning("Hook dispatch failed for work:lifecycle event")


def _print_work_result(
    work_type_lower: str,
    work_id: str,
    event_type: str,
    phase: str | None,
    blocker_value: str | None,
    result_path: Path | str | None,
) -> None:
    """Print formatted output for a successful work lifecycle event."""
    label = f"{work_type_lower.capitalize()} {work_id}"
    phase_prefix = f"{phase} " if phase else ""

    if event_type == "start":
        console.print(f"\n[green]{PLAY}[/green] {label} {ARROW} {phase_prefix}started")
    elif event_type == "complete":
        console.print(
            f"\n[green]{CHECK}[/green] {label} {ARROW} {phase_prefix}complete"
        )
    elif event_type == "blocked":
        console.print(f"\n[red]{PAUSE}[/red] {label} {ARROW} {phase_prefix}blocked")
        if blocker_value:
            console.print(f"  Blocker: {blocker_value}")
    elif event_type == "unblocked":
        console.print(
            f"\n[green]{PLAY}[/green] {label} {ARROW} {phase_prefix}unblocked"
        )
    elif event_type == "abandoned":
        console.print(
            f"\n[yellow]{CROSS}[/yellow] {label} {ARROW} {phase_prefix}abandoned"
        )

    console.print(f"\n[dim]Saved to: {result_path}[/dim]\n")


@signal_app.command("emit-work")
def emit_work(
    work_type: Annotated[
        str,
        typer.Argument(help="Work type (epic, story)"),
    ],
    work_id: Annotated[
        str,
        typer.Argument(help="Work ID (e.g., E9, F9.4)"),
    ],
    event_type: Annotated[
        str,
        typer.Option(
            "--event",
            "-e",
            help="Event type (start, complete, blocked, unblocked, abandoned)",
        ),
    ] = "start",
    phase: Annotated[
        str | None,
        typer.Option("--phase", "-p", help="Phase (design, plan, implement, review)"),
    ] = None,
    blocker: Annotated[
        str,
        typer.Option(
            "--blocker", "-b", help="Blocker description (for blocked events)"
        ),
    ] = "",
    session: Annotated[
        str | None,
        typer.Option(
            "--session",
            help="Session ID (e.g., SES-177). Falls back to RAI_SESSION_ID env var.",
        ),
    ] = None,
    task: Annotated[
        str | None,
        typer.Option(
            "--task",
            "-t",
            help="Task identity within a phase (e.g., 'Task 1: add schema fields')",
        ),
    ] = None,
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            help="Git branch name. Auto-resolved from git when not provided.",
        ),
    ] = None,
    commit: Annotated[
        str | None,
        typer.Option(
            "--commit",
            help="Git HEAD commit hash. Auto-resolved from git when not provided.",
        ),
    ] = None,
    cc_session_id: Annotated[
        str | None,
        typer.Option(
            "--session-id",
            "--cc-session-id",
            help=(
                "Agent session UUID. Falls back to runtime discovery chain "
                "(RAISE_AGENT_SESSION_ID > RAISE_CC_SESSION_ID > CC port)."
            ),
        ),
    ] = None,
    output_tokens: Annotated[
        int | None,
        typer.Option(
            "--output-tokens",
            help="LLM output token count for this phase. Emits a token_usage event.",
            min=0,
        ),
    ] = None,
) -> None:
    """Emit a work lifecycle event for Lean flow analysis.

    Tracks work items (epics, stories) through normalized phases to enable:
    - Lead time: total time from start to complete
    - Wait time: gaps between phases
    - WIP: work started but not completed
    - Bottlenecks: which phase takes longest
    - Cross-level analysis: compare epic vs story flow

    Phases (normalized across all work types):
    - design: Scope definition and specification
    - plan: Task/story decomposition and sequencing
    - implement: Active development work
    - review: Retrospective and learnings

    Examples:
        # Epic lifecycle
        $ rai signal emit-work epic E9 --event start --phase design
        $ rai signal emit-work epic E9 -e complete -p design
        $ rai signal emit-work epic E9 -e start -p plan

        # Story lifecycle
        $ rai signal emit-work story S9.4 --event start --phase design
        $ rai signal emit-work story S9.4 -e complete -p implement
        $ rai signal emit-work story S9.4 -e start -p review

        # Work blocked
        $ rai signal emit-work story S9.4 -e blocked -p plan -b "unclear requirements"

        # Work unblocked
        $ rai signal emit-work story S9.4 -e unblocked -p plan
    """
    work_type_lower = work_type.lower()
    schema_phase = _validate_work_inputs(event_type, phase, work_type_lower)

    blocker_value = blocker if blocker else None
    if event_type == "blocked" and not blocker_value:
        console.print(
            "[yellow]Warning:[/yellow] No blocker description provided for blocked event"
        )

    resolved_branch = _resolve_branch(branch)
    resolved_commit = _resolve_commit(commit)

    lifecycle_event = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type_lower,
        work_id=work_id,
        event=event_type,  # type: ignore[arg-type]
        phase=schema_phase,  # type: ignore[arg-type]
        blocker=blocker_value,
        task=task,
        branch=resolved_branch,
        commit=resolved_commit,
        agent_session_id=_resolve_agent_session(cc_session_id),
        source=discover_agent_runtime(),
        mission_id=None,
    )

    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    result = emit(lifecycle_event, session_id=session_id)

    if result.success:
        _dispatch_work_hook(
            work_type_lower,
            work_id,
            event_type,
            schema_phase,
            mission_id=lifecycle_event.mission_id,
            task=lifecycle_event.task,
            branch=lifecycle_event.branch,
        )
        _print_work_result(
            work_type_lower, work_id, event_type, phase, blocker_value, result.path
        )
        if output_tokens is not None:
            _emit_token_usage(
                work_id=work_id,
                phase=schema_phase,
                output_tokens=output_tokens,
                session_id=session_id,
                agent_session_id=lifecycle_event.agent_session_id,
            )
    else:
        cli_error(result.error or "Failed to emit work lifecycle event")


@signal_app.command("query")
def query_signal(
    work_type: Annotated[str, typer.Argument(help="Work type (story, epic)")],
    work_id: Annotated[str, typer.Argument(help="Work ID (e.g., S3008.5)")],
    event: Annotated[
        str | None,
        typer.Option("--event", help="Filter by event type (e.g. complete)"),
    ] = None,
    phase: Annotated[
        str | None,
        typer.Option("--phase", help="Filter by phase (e.g. implement)"),
    ] = None,
    session_id: Annotated[
        str | None,
        typer.Option("--session-id", help="Filter by agent_session_id in payload"),
    ] = None,
    latest: Annotated[
        bool,
        typer.Option("--latest", help="Return only the most recent match"),
    ] = False,
    fields: Annotated[
        str | None,
        typer.Option("--fields", help="Comma-separated payload fields to output"),
    ] = None,
) -> None:
    r"""Query signals from SQLite — returns key=value lines, exit 1 if no match.

    Examples:
        $ rai signal query story S3008.5 --event complete --phase implement \
              --session-id $RAISE_CC_SESSION_ID --latest --fields commit,timestamp
    """
    import json
    import sys

    from raise_cli.storage.connection import get_project_db
    from raise_cli.storage.schema import create_all

    try:
        conn = get_project_db(Path.cwd())
        try:
            create_all(conn)

            conditions = [
                "json_extract(payload, '$.work_type') = ?",
                "json_extract(payload, '$.work_id') = ?",
            ]
            params: list[str] = [work_type.lower(), work_id]

            if event:
                conditions.append("json_extract(payload, '$.event') = ?")
                params.append(event)
            if phase:
                conditions.append("json_extract(payload, '$.phase') = ?")
                params.append(phase)
            if session_id:
                conditions.append("json_extract(payload, '$.agent_session_id') = ?")
                params.append(session_id)

            where = " AND ".join(conditions)
            order = " ORDER BY id DESC"
            limit = " LIMIT 1" if latest else ""
            rows = conn.execute(
                f"SELECT payload FROM signals WHERE {where}{order}{limit}",  # noqa: S608  # nosec B608
                params,
            ).fetchall()
        finally:
            conn.close()
    except Exception:  # noqa: BLE001
        sys.exit(1)

    if not rows:
        sys.exit(1)

    requested = [f.strip() for f in fields.split(",")] if fields else None
    for row in rows:
        payload = json.loads(row["payload"])
        for key, value in payload.items():
            if requested is None or key in requested:
                console.print(f"{key}={value}", highlight=False)


@signal_app.command("emit-session")
def emit_session(
    session_type: Annotated[
        str,
        typer.Option(
            "--type", "-t", help="Session type (e.g., story, research, maintenance)"
        ),
    ] = "story",
    outcome: Annotated[
        str,
        typer.Option(
            "--outcome",
            "-o",
            help="Session outcome (success, partial, abandoned)",
        ),
    ] = "success",
    duration: Annotated[
        int,
        typer.Option("--duration", "-d", help="Session duration in minutes"),
    ] = 0,
    stories: Annotated[
        str,
        typer.Option("--stories", "-f", help="Stories worked on (comma-separated)"),
    ] = "",
    session: Annotated[
        str | None,
        typer.Option(
            "--session",
            help="Session ID (e.g., SES-177). Falls back to RAI_SESSION_ID env var.",
        ),
    ] = None,
    cc_session_id: Annotated[
        str | None,
        typer.Option(
            "--session-id",
            "--cc-session-id",
            help=(
                "Agent session UUID. Falls back to runtime discovery chain "
                "(RAISE_AGENT_SESSION_ID > RAISE_CC_SESSION_ID > CC port)."
            ),
        ),
    ] = None,
) -> None:
    """Emit a session event to telemetry.

    Records a session completion signal for local learning and insights.
    Called at the end of /rai-session-close to capture session metadata.

    Examples:
        # Basic session complete
        $ rai signal emit-session --type story --outcome success

        # With duration and stories
        $ rai signal emit-session -t story -o success -d 45 -f S9.1,S9.2,S9.3

        # Research session
        $ rai signal emit-session --type research --outcome partial --duration 90
    """
    # Validate outcome
    valid_outcomes: list[Literal["success", "partial", "abandoned"]] = [
        "success",
        "partial",
        "abandoned",
    ]
    if outcome not in valid_outcomes:
        cli_error(
            f"Invalid outcome: {outcome}",
            hint=f"Valid outcomes: {', '.join(valid_outcomes)}",
            exit_code=7,
        )

    # Parse stories
    stories_list = [f.strip() for f in stories.split(",") if f.strip()]

    # Create event
    event = SessionEvent(
        timestamp=datetime.now(UTC),
        session_type=session_type,
        outcome=outcome,  # type: ignore[arg-type]
        duration_min=duration,
        stories=stories_list,
        agent_session_id=_resolve_agent_session(cc_session_id),
        source=discover_agent_runtime(),
    )

    # Resolve optional session ID
    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    # Emit signal
    result = emit(event, session_id=session_id)

    if result.success:
        console.print(f"\n[green]{CHECK}[/green] Session event recorded")
        console.print(f"  Type: {session_type}")
        console.print(f"  Outcome: {outcome}")
        console.print(f"  Duration: {duration} min")
        if stories_list:
            console.print(f"  Stories: {', '.join(stories_list)}")
        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit session event")


@signal_app.command("emit-calibration")
def emit_calibration(
    story: Annotated[
        str,
        typer.Argument(help="Story ID (e.g., S9.4)"),
    ],
    size: Annotated[
        str,
        typer.Option("--size", "-s", help="T-shirt size (XS, S, M, L)"),
    ] = "S",
    estimated: Annotated[
        int,
        typer.Option("--estimated", "-e", help="Estimated duration in minutes"),
    ] = 0,
    actual: Annotated[
        int,
        typer.Option("--actual", "-a", help="Actual duration in minutes"),
    ] = 0,
    session: Annotated[
        str | None,
        typer.Option(
            "--session",
            help="Session ID (e.g., SES-177). Falls back to RAI_SESSION_ID env var.",
        ),
    ] = None,
    cc_session_id: Annotated[
        str | None,
        typer.Option(
            "--session-id",
            "--cc-session-id",
            help=(
                "Agent session UUID. Falls back to runtime discovery chain "
                "(RAISE_AGENT_SESSION_ID > RAISE_CC_SESSION_ID > CC port)."
            ),
        ),
    ] = None,
) -> None:
    """Emit a calibration event to telemetry.

    Records estimate vs actual for velocity tracking and pattern detection.
    Called at the end of /rai-story-review to capture calibration data.

    Velocity is calculated automatically: estimated / actual.
    - velocity > 1.0 means faster than estimated
    - velocity < 1.0 means slower than estimated

    Examples:
        # Story completed faster than estimated
        $ rai signal emit-calibration S9.4 --size S --estimated 30 --actual 15

        # Story took longer
        $ rai signal emit-calibration S9.4 -s M -e 60 -a 90

        # Short form
        $ rai signal emit-calibration S9.4 -s S -e 30 -a 15
    """
    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    size_upper = size.upper()
    if size_upper not in valid_sizes:
        cli_error(
            f"Invalid size: {size}",
            hint=f"Valid sizes: {', '.join(valid_sizes)}",
            exit_code=7,
        )

    # Validate durations
    if estimated <= 0:
        cli_error("Estimated duration must be > 0", exit_code=7)
    if actual <= 0:
        cli_error("Actual duration must be > 0", exit_code=7)

    # Calculate velocity
    velocity = round(estimated / actual, 2)

    # Create event
    event = CalibrationEvent(
        timestamp=datetime.now(UTC),
        story_id=story,
        story_size=size_upper,
        estimated_min=estimated,
        actual_min=actual,
        velocity=velocity,
        agent_session_id=_resolve_agent_session(cc_session_id),
        source=discover_agent_runtime(),
    )

    # Resolve optional session ID
    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    # Emit signal
    result = emit(event, session_id=session_id)

    if result.success:
        console.print(f"\n[green]{CHECK}[/green] Calibration event recorded")
        console.print(f"  Story: {story}")
        console.print(f"  Size: {size_upper}")
        console.print(f"  Estimated: {estimated} min")
        console.print(f"  Actual: {actual} min")
        console.print(f"  Velocity: {velocity}x", end="")
        if velocity > 1.0:
            console.print(" [green](faster than estimated)[/green]")
        elif velocity < 1.0:
            console.print(" [yellow](slower than estimated)[/yellow]")
        else:
            console.print(" (on target)")
        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit calibration event")


# ---------------------------------------------------------------------------
# S2.6 — backfill historical pipeline runs
# ---------------------------------------------------------------------------


_DEFAULT_LIMIT = 10
_EMITTER_FACTORY_ENV = "_RAI_TEST_EMITTER_FACTORY"


def _make_emitter(project_root: Path) -> UnifiedEmitter:
    """Build the emitter used by backfill. Test hook-point kept simple."""
    return UnifiedEmitter(project_root=project_root)


def _emit_token_usage(
    *,
    work_id: str,
    phase: str | None,
    output_tokens: int,
    session_id: str | None,
    agent_session_id: str | None,  # noqa: ARG001
) -> None:
    """Emit a token_usage signal via emit() — SQLite always, server if configured."""
    from raise_cli.telemetry.schemas import TokenUsage

    signal = TokenUsage(
        timestamp=datetime.now(UTC),
        story_id=work_id,
        phase=phase,
        output_tokens=output_tokens,
        source="claude_code",
    )
    emitter = UnifiedEmitter(project_root=Path.cwd())
    emitter.emit(signal, session_id=session_id)


def _print_dry_run(stats: BackfillStats, preview_count: int) -> None:
    console.print(
        f"Scanned {stats.scanned} runs. {stats.eligible} eligible phase events."
    )
    if stats.skipped:
        console.print(
            f"[yellow]⚠ skipped (corrupt or invalid): {stats.skipped}[/yellow]"
        )
    if stats.skipped_no_ref:
        console.print(
            f"[yellow]⚠ skipped (missing/invalid issue_id): {stats.skipped_no_ref}[/yellow]"
        )
    console.print(f"[dim]dry-run: would emit {preview_count} events.[/dim]")


def _print_summary(stats: BackfillStats, *, hinted_all: bool) -> None:
    console.print(
        f"[green]✓[/green] emitted: {stats.emitted}  "
        f"queued: {stats.queued}  "
        f"already_present: {stats.already_present}  "
        f"skipped: {stats.skipped}  "
        f"skipped_no_ref: {stats.skipped_no_ref}"
    )
    if hinted_all:
        console.print(
            "[dim]Run with --all to replay the full corpus "
            f"(~{stats.eligible} events).[/dim]"
        )


@signal_app.command("backfill")
def backfill(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Scan + report counts without emitting."),
    ] = False,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            help="Max events to emit (ignored when --all is set).",
            min=1,
        ),
    ] = _DEFAULT_LIMIT,
    all_: Annotated[
        bool,
        typer.Option("--all", help="Emit every eligible event, ignoring --limit."),
    ] = False,
    runs_dir: Annotated[
        Path | None,
        typer.Option(
            "--runs-dir",
            help="Override the default .rai-state/pipeline/runs directory.",
        ),
    ] = None,
    project_root: Annotated[
        Path | None,
        typer.Option(
            "--project-root",
            help="Project root for the retry queue (default: cwd).",
        ),
    ] = None,
) -> None:
    """Replay historical pipeline runs as pipeline_phase_completed events.

    Reads `.rai-state/pipeline/runs/*.json`, builds one AgentEventCreate per
    completed phase with a valid issue_id, and emits via ServerEmitHook. The
    event_id is deterministic, so re-runs are idempotent — the server dedups
    (S2.6 AC1) and the CLI counts duplicates as `already_present`.

    Default `--limit 10` protects dev servers from accidental floods; run
    with `--all` to replay the full corpus.
    """
    root = project_root or Path.cwd()
    target_runs = runs_dir or (root / ".rai-state" / "pipeline" / "runs")

    stats = BackfillStats()
    events = scan_runs(target_runs, stats=stats)

    if dry_run:
        preview = len(events) if all_ else min(limit, len(events))
        _print_dry_run(stats, preview)
        return

    if not all_:
        events = events[:limit]

    if not events:
        console.print(
            f"Scanned {stats.scanned} runs. {stats.eligible} eligible phase events."
        )
        console.print("Nothing to emit.")
        return

    hook = _make_emitter(root)
    for event in events:
        outcome = hook.post_direct(event)
        if outcome == "emitted":
            stats.emitted += 1
        elif outcome == "already_present":
            stats.already_present += 1
        elif outcome == "queued":
            stats.queued += 1
        # "dropped" is intentionally silent — same as a no-op emitter.

    _print_summary(stats, hinted_all=not all_ and stats.eligible > limit)
