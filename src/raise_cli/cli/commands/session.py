"""CLI commands for session management.

This module provides the `raise session` command group for managing
working sessions — the lifecycle of a developer's focused work period.

Sessions are first-class workflow state, distinct from:
- Profile (developer identity)
- Memory (persistent knowledge)

Example:
    $ raise session start              # Start a new session
    $ raise session start --context   # Start with context bundle
    $ raise session close              # End the current session
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from raise_cli.cli.error_handler import cli_error
from raise_cli.memory.writer import validate_session_index
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    end_session,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
)
from raise_cli.session.bundle import assemble_context_bundle
from raise_cli.session.close import CloseInput, load_state_file, process_session_close
from raise_cli.session.state import load_session_state

session_app = typer.Typer(
    name="session",
    help="Manage working sessions",
    no_args_is_help=True,
)


@session_app.command()
def start(
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Your name (required for first-time setup)",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path to associate with this session",
        ),
    ] = None,
    context: Annotated[
        bool,
        typer.Option(
            "--context",
            help="Output a context bundle for AI consumption",
        ),
    ] = False,
) -> None:
    """Start a new working session.

    Increments the session counter and sets active session state.
    Checks for orphaned sessions (started but not closed) and warns if found.
    For first-time users, creates a new developer profile.

    With --context, outputs a token-optimized context bundle (~150 tokens)
    assembled from the developer profile, session state, and memory graph.

    Examples:
        $ raise session start                    # Start session
        $ raise session start --name "Alice"    # First-time setup
        $ raise session start --project /my/proj # Start with project path
        $ raise session start --project . --context  # Context bundle
    """
    profile = load_developer_profile()

    if profile is None:
        # First-time user - need name to create profile
        if name is None:
            cli_error(
                "No developer profile found",
                hint="Provide --name for first-time setup: raise session start --name 'Your Name'",
            )
            return  # cli_error raises, but this helps pyright

        # Create new profile
        profile = DeveloperProfile(name=name)
        typer.echo(f"Welcome to RaiSE, {name}! Creating your developer profile...")

    # Check for active session
    if profile.current_session is not None:
        prev = profile.current_session
        if prev.is_stale():
            typer.echo(
                f"Warning: Stale session detected (started {prev.started_at.date()}, "
                f"project: {prev.project})\n"
                "Previous session was not closed. Learnings may have been lost.\n"
                "Tip: Use /session-close before ending work."
            )
        else:
            typer.echo(
                f"Note: Session already active (project: {prev.project})\n"
                "Starting new session anyway. Previous session not closed."
            )

    # Jidoka: Validate session index if project specified
    if project is not None:
        memory_dir = Path(project) / ".raise" / "rai" / "memory"
        if memory_dir.exists():
            validation = validate_session_index(memory_dir)
            if not validation.is_valid:
                typer.echo(f"Warning: {validation.summary()}")
                typer.echo("Run `raise memory validate` to fix data quality issues.\n")

    # Increment session count
    updated = increment_session(profile, project_path=project)

    # Set active session state
    if project is not None:
        updated = start_session(updated, project)

    save_developer_profile(updated)

    if context and project is not None:
        project_path = Path(project)
        state = load_session_state(project_path)
        bundle = assemble_context_bundle(updated, state, project_path)
        typer.echo(bundle)
    else:
        typer.echo(f"Session recorded. (last: {updated.last_session})")


@session_app.command()
def close(
    summary: Annotated[
        str | None,
        typer.Option(
            "--summary",
            "-s",
            help="Session summary",
        ),
    ] = None,
    session_type: Annotated[
        str | None,
        typer.Option(
            "--type",
            "-t",
            help="Session type (feature, research, maintenance, etc.)",
        ),
    ] = None,
    pattern: Annotated[
        str | None,
        typer.Option(
            "--pattern",
            help="Pattern description to record (format: 'description')",
        ),
    ] = None,
    correction: Annotated[
        str | None,
        typer.Option(
            "--correction",
            help="Coaching correction observed",
        ),
    ] = None,
    correction_lesson: Annotated[
        str | None,
        typer.Option(
            "--correction-lesson",
            help="Lesson from the correction",
        ),
    ] = None,
    state_file: Annotated[
        str | None,
        typer.Option(
            "--state-file",
            help="YAML file with full structured session output",
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            "-p",
            help="Project path",
        ),
    ] = None,
) -> None:
    """End the current working session.

    With no flags: clears active session state (legacy behavior).
    With --summary or --state-file: performs full structured close —
    records session, patterns, corrections, and updates state.

    All writes are performed atomically by the CLI — skills should
    NOT call separate telemetry/memory commands.

    Examples:
        $ raise session close
        $ raise session close --summary "Session protocol design" --type feature
        $ raise session close --state-file /tmp/session-output.yaml --project .
    """
    profile = load_developer_profile()

    if profile is None:
        cli_error("No developer profile found")
        return  # cli_error raises, but this helps pyright

    # Determine if this is a structured close
    is_structured = summary is not None or state_file is not None

    if not is_structured:
        # Legacy behavior: just clear active session
        if profile.current_session is None:
            typer.echo("No active session to close.")
            return

        updated = end_session(profile)
        save_developer_profile(updated)
        typer.echo("Session closed.")
        return

    # Structured close: build CloseInput from flags or state file
    if state_file is not None:
        try:
            close_input = load_state_file(Path(state_file))
        except (FileNotFoundError, ValueError) as e:
            cli_error(f"Failed to load state file: {e}")
            return  # cli_error raises
    else:
        close_input = CloseInput(
            summary=summary or "",
            session_type=session_type or "feature",
        )

    # Override with CLI flags if provided alongside state file
    if pattern:
        close_input.patterns.append({"description": pattern, "type": "process"})
    if correction and correction_lesson:
        close_input.corrections.append(
            {"what": correction, "lesson": correction_lesson}
        )

    # Resolve project path
    project_path = Path(project) if project else Path.cwd()

    # Process close
    close_result = process_session_close(close_input, profile, project_path)

    # Output summary
    typer.echo(f"Session {close_result.session_id} closed.")
    if close_result.patterns_added > 0:
        typer.echo(f"  Patterns added: {close_result.patterns_added}")
    if close_result.corrections_added > 0:
        typer.echo(f"  Corrections recorded: {close_result.corrections_added}")
