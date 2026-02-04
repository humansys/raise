"""CLI commands for telemetry signals.

This module provides CLI commands to emit telemetry signals as specified
in ADR-018. These commands are designed to be called by AI agents or
humans to record signals to .rai/telemetry/signals.jsonl.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

import typer
from rich.console import Console

from raise_cli.telemetry.schemas import (
    CalibrationEvent,
    FeatureLifecycle,
    SessionEvent,
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
        console.print(f"[red]Error:[/red] Invalid outcome: {outcome}")
        console.print(f"Valid outcomes: {', '.join(valid_outcomes)}")
        raise typer.Exit(1)

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
        console.print(f"[red]Error:[/red] {result.error}")
        raise typer.Exit(1)


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
        console.print(f"[red]Error:[/red] Invalid size: {size}")
        console.print(f"Valid sizes: {', '.join(valid_sizes)}")
        raise typer.Exit(1)

    # Validate durations
    if estimated <= 0:
        console.print("[red]Error:[/red] Estimated duration must be > 0")
        raise typer.Exit(1)
    if actual <= 0:
        console.print("[red]Error:[/red] Actual duration must be > 0")
        raise typer.Exit(1)

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
        console.print(f"[red]Error:[/red] {result.error}")
        raise typer.Exit(1)


@telemetry_app.command("emit-feature")
def emit_feature(
    feature: Annotated[
        str,
        typer.Argument(help="Feature ID (e.g., F9.4)"),
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
    """Emit a feature lifecycle event for Lean flow analysis.

    Tracks feature progression through phases to enable:
    - Lead time: total time from start to complete
    - Wait time: gaps between phases
    - WIP: features started but not completed
    - Bottlenecks: which phase takes longest

    Call at the start and end of each phase (design, plan, implement, review).

    Examples:
        # Starting design phase
        $ raise telemetry emit-feature F9.4 --event start --phase design

        # Completing design, starting plan
        $ raise telemetry emit-feature F9.4 -e complete -p design
        $ raise telemetry emit-feature F9.4 -e start -p plan

        # Feature blocked
        $ raise telemetry emit-feature F9.4 -e blocked -p plan -b "unclear requirements"

        # Feature unblocked
        $ raise telemetry emit-feature F9.4 -e unblocked -p plan

        # Feature complete (after review)
        $ raise telemetry emit-feature F9.4 -e complete -p review
    """
    # Validate event type
    valid_events: list[Literal["start", "complete", "blocked", "unblocked", "abandoned"]] = [
        "start",
        "complete",
        "blocked",
        "unblocked",
        "abandoned",
    ]
    if event_type not in valid_events:
        console.print(f"[red]Error:[/red] Invalid event: {event_type}")
        console.print(f"Valid events: {', '.join(valid_events)}")
        raise typer.Exit(1)

    # Validate phase
    valid_phases: list[Literal["design", "plan", "implement", "review"]] = [
        "design",
        "plan",
        "implement",
        "review",
    ]
    if phase not in valid_phases:
        console.print(f"[red]Error:[/red] Invalid phase: {phase}")
        console.print(f"Valid phases: {', '.join(valid_phases)}")
        raise typer.Exit(1)

    # Blocker is required for blocked events
    blocker_value = blocker if blocker else None
    if event_type == "blocked" and not blocker_value:
        console.print("[yellow]Warning:[/yellow] No blocker description provided for blocked event")

    # Create event
    lifecycle_event = FeatureLifecycle(
        timestamp=datetime.now(UTC),
        feature=feature,
        event=event_type,  # type: ignore[arg-type]
        phase=phase,  # type: ignore[arg-type]
        blocker=blocker_value,
    )

    # Emit signal
    result = emit(lifecycle_event)

    if result.success:
        # Format output based on event type
        if event_type == "start":
            console.print(f"\n[green]▶[/green] Feature {feature} → {phase} started")
        elif event_type == "complete":
            console.print(f"\n[green]✓[/green] Feature {feature} → {phase} complete")
        elif event_type == "blocked":
            console.print(f"\n[red]⏸[/red] Feature {feature} → {phase} blocked")
            if blocker_value:
                console.print(f"  Blocker: {blocker_value}")
        elif event_type == "unblocked":
            console.print(f"\n[green]▶[/green] Feature {feature} → {phase} unblocked")
        elif event_type == "abandoned":
            console.print(f"\n[yellow]✗[/yellow] Feature {feature} → {phase} abandoned")

        console.print(f"\n[dim]Saved to: {result.path}[/dim]\n")
    else:
        console.print(f"[red]Error:[/red] {result.error}")
        raise typer.Exit(1)
