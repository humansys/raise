"""CLI commands for telemetry signals.

This module provides CLI commands to emit telemetry signals as specified
in ADR-018. These commands are designed to be called by AI agents or
humans to record signals to .raise/rai/telemetry/signals.jsonl.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    SessionEvent,
    WorkLifecycle,
)
from raise_cli.telemetry.writer import emit

telemetry_app = typer.Typer(
    name="telemetry",
    help="Emit telemetry signals for local learning",
    no_args_is_help=True,
)

console = Console()


@telemetry_app.command("emit-session")
def emit_session(
    session_type: Annotated[
        str,
        typer.Option(
            "--type", "-t", help="Session type (e.g., feature, research, maintenance)"
        ),
    ] = "feature",
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
    features: Annotated[
        str,
        typer.Option("--features", "-f", help="Features worked on (comma-separated)"),
    ] = "",
) -> None:
    """Emit a session event to telemetry.

    Records a session completion signal for local learning and insights.
    Called at the end of /session-close to capture session metadata.

    Examples:
        # Basic session complete
        $ raise telemetry emit-session --type feature --outcome success

        # With duration and features
        $ raise telemetry emit-session -t feature -o success -d 45 -f F9.1,F9.2,F9.3

        # Research session
        $ raise telemetry emit-session --type research --outcome partial --duration 90
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

    # Parse features
    features_list = [f.strip() for f in features.split(",") if f.strip()]

    # Create event
    event = SessionEvent(
        timestamp=datetime.now(UTC),
        session_type=session_type,
        outcome=outcome,  # type: ignore[arg-type]
        duration_min=duration,
        features=features_list,
    )

    # Emit signal
    result = emit(event)

    if result.success:
        console.print("\n[green]✓[/green] Session event recorded")
        console.print(f"  Type: {session_type}")
        console.print(f"  Outcome: {outcome}")
        console.print(f"  Duration: {duration} min")
        if features_list:
            console.print(f"  Features: {', '.join(features_list)}")
        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit session event")


@telemetry_app.command("emit-calibration")
def emit_calibration(
    feature: Annotated[
        str,
        typer.Argument(help="Feature ID (e.g., F9.4)"),
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
) -> None:
    """Emit a calibration event to telemetry.

    Records estimate vs actual for velocity tracking and pattern detection.
    Called at the end of /feature-review to capture calibration data.

    Velocity is calculated automatically: estimated / actual.
    - velocity > 1.0 means faster than estimated
    - velocity < 1.0 means slower than estimated

    Examples:
        # Feature completed faster than estimated
        $ raise telemetry emit-calibration F9.4 --size S --estimated 30 --actual 15

        # Feature took longer
        $ raise telemetry emit-calibration F9.4 -s M -e 60 -a 90

        # Short form
        $ raise telemetry emit-calibration F9.4 -s S -e 30 -a 15
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
        feature_id=feature,
        feature_size=size_upper,
        estimated_min=estimated,
        actual_min=actual,
        velocity=velocity,
    )

    # Emit signal
    result = emit(event)

    if result.success:
        console.print("\n[green]✓[/green] Calibration event recorded")
        console.print(f"  Feature: {feature}")
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


@telemetry_app.command("emit-work")
def emit_work(
    work_type: Annotated[
        str,
        typer.Argument(help="Work type (epic, feature)"),
    ],
    work_id: Annotated[
        str,
        typer.Argument(help="Work ID (e.g., E9, F9.4)"),
    ],
    event_type: Annotated[
        str,
        typer.Option(
            "--event", "-e", help="Event type (start, complete, blocked, unblocked, abandoned)"
        ),
    ] = "start",
    phase: Annotated[
        str,
        typer.Option("--phase", "-p", help="Phase (design, plan, implement, review)"),
    ] = "design",
    blocker: Annotated[
        str,
        typer.Option("--blocker", "-b", help="Blocker description (for blocked events)"),
    ] = "",
) -> None:
    """Emit a work lifecycle event for Lean flow analysis.

    Tracks work items (epics, features) through normalized phases to enable:
    - Lead time: total time from start to complete
    - Wait time: gaps between phases
    - WIP: work started but not completed
    - Bottlenecks: which phase takes longest
    - Cross-level analysis: compare epic vs feature flow

    Phases (normalized across all work types):
    - design: Scope definition and specification
    - plan: Task/feature decomposition and sequencing
    - implement: Active development work
    - review: Retrospective and learnings

    Examples:
        # Epic lifecycle
        $ raise telemetry emit-work epic E9 --event start --phase design
        $ raise telemetry emit-work epic E9 -e complete -p design
        $ raise telemetry emit-work epic E9 -e start -p plan

        # Feature lifecycle
        $ raise telemetry emit-work feature F9.4 --event start --phase design
        $ raise telemetry emit-work feature F9.4 -e complete -p implement
        $ raise telemetry emit-work feature F9.4 -e start -p review

        # Work blocked
        $ raise telemetry emit-work feature F9.4 -e blocked -p plan -b "unclear requirements"

        # Work unblocked
        $ raise telemetry emit-work feature F9.4 -e unblocked -p plan
    """
    # Validate work type
    valid_work_types: list[Literal["epic", "feature"]] = ["epic", "feature"]
    work_type_lower = work_type.lower()
    if work_type_lower not in valid_work_types:
        cli_error(
            f"Invalid work type: {work_type}",
            hint=f"Valid types: {', '.join(valid_work_types)}",
            exit_code=7,
        )

    # Validate event type
    valid_events: list[Literal["start", "complete", "blocked", "unblocked", "abandoned"]] = [
        "start",
        "complete",
        "blocked",
        "unblocked",
        "abandoned",
    ]
    if event_type not in valid_events:
        cli_error(
            f"Invalid event: {event_type}",
            hint=f"Valid events: {', '.join(valid_events)}",
            exit_code=7,
        )

    # Validate phase
    valid_phases: list[Literal["design", "plan", "implement", "review"]] = [
        "design",
        "plan",
        "implement",
        "review",
    ]
    if phase not in valid_phases:
        cli_error(
            f"Invalid phase: {phase}",
            hint=f"Valid phases: {', '.join(valid_phases)}",
            exit_code=7,
        )

    # Blocker is required for blocked events
    blocker_value = blocker if blocker else None
    if event_type == "blocked" and not blocker_value:
        console.print("[yellow]Warning:[/yellow] No blocker description provided for blocked event")

    # Create event
    lifecycle_event = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type_lower,  # type: ignore[arg-type]
        work_id=work_id,
        event=event_type,  # type: ignore[arg-type]
        phase=phase,  # type: ignore[arg-type]
        blocker=blocker_value,
    )

    # Emit signal
    result = emit(lifecycle_event)

    if result.success:
        # Format label based on work type
        label = f"{work_type_lower.capitalize()} {work_id}"

        # Format output based on event type
        if event_type == "start":
            console.print(f"\n[green]▶[/green] {label} → {phase} started")
        elif event_type == "complete":
            console.print(f"\n[green]✓[/green] {label} → {phase} complete")
        elif event_type == "blocked":
            console.print(f"\n[red]⏸[/red] {label} → {phase} blocked")
            if blocker_value:
                console.print(f"  Blocker: {blocker_value}")
        elif event_type == "unblocked":
            console.print(f"\n[green]▶[/green] {label} → {phase} unblocked")
        elif event_type == "abandoned":
            console.print(f"\n[yellow]✗[/yellow] {label} → {phase} abandoned")

        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        cli_error(result.error or "Failed to emit work lifecycle event")
