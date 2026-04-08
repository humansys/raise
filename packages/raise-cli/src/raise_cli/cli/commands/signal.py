"""CLI commands for Rai's telemetry signals: work lifecycle, sessions, calibration.

The signal group owns commands that emit telemetry events to JSONL files.
These were extracted from the `memory` God Object in RAISE-247 (ADR-038).

Commands:
- emit-work: Emit a work lifecycle event (epic/story phases)
- emit-session: Emit a session completion event
- emit-calibration: Emit an estimation calibration event
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.session.resolver import resolve_session_id_optional
from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    SessionEvent,
    WorkLifecycle,
)
from raise_cli.telemetry.writer import emit

logger = logging.getLogger(__name__)

signal_app = typer.Typer(
    name="signal",
    help="Emit lifecycle and telemetry signals",
    no_args_is_help=True,
)

console = Console()


def _validate_work_inputs(
    work_type: str,
    event_type: str,
    phase: str | None,
) -> str:
    """Validate work type, event type, and phase. Returns lowercased work_type."""
    valid_work_types: list[Literal["epic", "story"]] = ["epic", "story"]
    work_type_lower = work_type.lower()
    if work_type_lower not in valid_work_types:
        cli_error(
            f"Invalid work type: {work_type}",
            hint=f"Valid types: {', '.join(valid_work_types)}",
            exit_code=7,
        )

    valid_events: list[
        Literal["start", "complete", "blocked", "unblocked", "abandoned"]
    ] = ["start", "complete", "blocked", "unblocked", "abandoned"]
    if event_type not in valid_events:
        cli_error(
            f"Invalid event: {event_type}",
            hint=f"Valid events: {', '.join(valid_events)}",
            exit_code=7,
        )

    if phase is not None:
        valid_phases: list[
            Literal["init", "design", "plan", "implement", "review", "close"]
        ] = ["init", "design", "plan", "implement", "review", "close"]
        if phase not in valid_phases:
            cli_error(
                f"Invalid phase: {phase}",
                hint=f"Valid phases: {', '.join(valid_phases)}",
                exit_code=7,
            )

    return work_type_lower


def _dispatch_work_hook(
    work_type_lower: str,
    work_id: str,
    event_type: str,
    phase: str,
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
        console.print(f"\n[green]▶[/green] {label} → {phase_prefix}started")
    elif event_type == "complete":
        console.print(f"\n[green]✓[/green] {label} → {phase_prefix}complete")
    elif event_type == "blocked":
        console.print(f"\n[red]⏸[/red] {label} → {phase_prefix}blocked")
        if blocker_value:
            console.print(f"  Blocker: {blocker_value}")
    elif event_type == "unblocked":
        console.print(f"\n[green]▶[/green] {label} → {phase_prefix}unblocked")
    elif event_type == "abandoned":
        console.print(f"\n[yellow]✗[/yellow] {label} → {phase_prefix}abandoned")

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
    work_type_lower = _validate_work_inputs(work_type, event_type, phase)

    blocker_value = blocker if blocker else None
    if event_type == "blocked" and not blocker_value:
        console.print(
            "[yellow]Warning:[/yellow] No blocker description provided for blocked event"
        )

    # Use "init" as neutral phase for telemetry when not specified
    schema_phase = phase or "init"

    lifecycle_event = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type_lower,  # type: ignore[arg-type]
        work_id=work_id,
        event=event_type,  # type: ignore[arg-type]
        phase=schema_phase,  # type: ignore[arg-type]
        blocker=blocker_value,
    )

    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    result = emit(lifecycle_event, session_id=session_id)

    if result.success:
        _dispatch_work_hook(work_type_lower, work_id, event_type, schema_phase)
        _print_work_result(
            work_type_lower, work_id, event_type, phase, blocker_value, result.path
        )
    else:
        cli_error(result.error or "Failed to emit work lifecycle event")


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
    )

    # Resolve optional session ID
    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    # Emit signal
    result = emit(event, session_id=session_id)

    if result.success:
        console.print("\n[green]✓[/green] Session event recorded")
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
    )

    # Resolve optional session ID
    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    # Emit signal
    result = emit(event, session_id=session_id)

    if result.success:
        console.print("\n[green]✓[/green] Calibration event recorded")
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
