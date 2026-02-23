"""CLI commands for Rai's memory: patterns, calibration, sessions, and telemetry.

Memory commands own the persistent knowledge that lives in JSONL files:
- Patterns (learned behaviors and best practices)
- Calibration (estimation data)
- Sessions (work history)

Graph-structure commands (build, validate, query, context, list, viz, extract)
have been extracted to the `graph` group (RAISE-247, ADR-038).
Backward-compatible aliases remain here and will be removed in a future release.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from rai_cli.cli.error_handler import cli_error
from rai_cli.config.paths import get_personal_dir
from rai_cli.context.query import (
    SCORING_LOW_WILSON_THRESHOLD,
    wilson_lower_bound,
)
from rai_cli.memory import (
    CalibrationInput,
    MemoryScope,
    PatternInput,
    PatternSubType,
    ReinforceResult,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
    get_memory_dir_for_scope,
    reinforce_pattern,
)
from rai_cli.onboarding.profile import load_developer_profile
from rai_cli.session.resolver import resolve_session_id_optional
from rai_cli.telemetry.schemas import (
    CalibrationEvent,
    SessionEvent,
    WorkLifecycle,
)
from rai_cli.telemetry.writer import emit

memory_app = typer.Typer(
    name="memory",
    help="Query and manage Rai's memory",
    no_args_is_help=True,
)

console = Console()


# =============================================================================
# Deprecation Helpers
# =============================================================================


_stderr_console = Console(stderr=True)


def _deprecation_warning(old_cmd: str, new_group: str = "graph") -> None:
    """Print deprecation warning to stderr."""
    _stderr_console.print(
        f"[yellow]DEPRECATED:[/yellow] 'rai memory {old_cmd}' → "
        f"use 'rai {new_group} {old_cmd}' instead",
    )


# =============================================================================
# Backward-Compat Aliases: graph commands (extracted to graph.py in RAISE-247)
# These wrappers will be removed in a future release (RAISE-247/S9).
# =============================================================================


@memory_app.command()
def query(
    query_str: Annotated[
        str, typer.Argument(help="Query string (keywords or concept ID)")
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    strategy: Annotated[
        str | None,
        typer.Option(
            "--strategy",
            "-s",
            help="Query strategy (keyword_search, concept_lookup)",
        ),
    ] = None,
    types: Annotated[
        str | None,
        typer.Option(
            "--types",
            "-t",
            help="Filter by types (comma-separated: pattern,calibration,principle,etc.)",
        ),
    ] = None,
    edge_types: Annotated[
        str | None,
        typer.Option(
            "--edge-types",
            help="Filter by edge types (comma-separated: constrained_by,depends_on,etc.)",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of results"),
    ] = 10,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
) -> None:
    """Deprecated: use 'rai graph query'."""
    _deprecation_warning("query")
    from rai_cli.cli.commands.graph import query as graph_query

    graph_query(
        query_str=query_str,
        format=format,
        output=output,
        strategy=strategy,
        types=types,
        edge_types=edge_types,
        limit=limit,
        index_path=index_path,
    )


@memory_app.command("context")
def context_cmd(
    module_id: Annotated[str, typer.Argument(help="Module ID (e.g., mod-memory)")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
) -> None:
    """Deprecated: use 'rai graph context'."""
    _deprecation_warning("context")
    from rai_cli.cli.commands.graph import context_cmd as graph_context

    graph_context(module_id=module_id, format=format, index_path=index_path)


@memory_app.command()
def build(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to save index JSON"),
    ] = None,
    no_diff: Annotated[
        bool,
        typer.Option("--no-diff", help="Skip diff computation"),
    ] = False,
) -> None:
    """Deprecated: use 'rai graph build'."""
    _deprecation_warning("build")
    from rai_cli.cli.commands.graph import build as graph_build

    graph_build(output=output, no_diff=no_diff)


@memory_app.command()
def validate(
    index_file: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Path to index JSON file"),
    ] = None,
) -> None:
    """Deprecated: use 'rai graph validate'."""
    _deprecation_warning("validate")
    from rai_cli.cli.commands.graph import validate as graph_validate

    graph_validate(index_file=index_file)


@memory_app.command()
def extract(
    file_path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to governance file (optional, extracts all if not provided)"
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
) -> None:
    """Deprecated: use 'rai graph extract'."""
    _deprecation_warning("extract")
    from rai_cli.cli.commands.graph import extract as graph_extract

    graph_extract(file_path=file_path, format=format)


@memory_app.command("list")
def list_memory(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human, json, or table)"),
    ] = "table",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (default: stdout)"),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
    memory_only: Annotated[
        bool,
        typer.Option(
            "--memory-only/--all",
            help="Show only memory types (pattern, calibration, session) or all",
        ),
    ] = False,
) -> None:
    """Deprecated: use 'rai graph list'."""
    _deprecation_warning("list")
    from rai_cli.cli.commands.graph import list_graph

    list_graph(format=format, output=output, index_path=index_path, memory_only=memory_only)


@memory_app.command("viz")
def viz(
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output HTML file path"),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Memory index path"),
    ] = None,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open in browser after generating"),
    ] = True,
) -> None:
    """Deprecated: use 'rai graph viz'."""
    _deprecation_warning("viz")
    from rai_cli.cli.commands.graph import viz as graph_viz

    graph_viz(output=output, index_path=index_path, open_browser=open_browser)


# =============================================================================
# Generate MEMORY.md (deprecated, kept for compat)
# =============================================================================


@memory_app.command("generate")
def generate_memory(
    path: Annotated[
        Path | None,
        typer.Option(
            "--path", "-p", help="Project root (defaults to current directory)"
        ),
    ] = None,
) -> None:
    """Generate MEMORY.md for AI editors (deprecated).

    MEMORY.md generation is no longer needed — the memory graph is the
    single source of truth. Context is delivered via `raise session start
    --context` which assembles a token-optimized bundle from the graph.

    Use `rai graph build` to rebuild the graph instead.

    Examples:
        # Build the memory graph (recommended)
        $ rai graph build
    """
    console.print("\n[yellow]Skipped:[/yellow] MEMORY.md generation is deprecated.")
    console.print("  The memory graph is the single source of truth.")
    console.print(
        "  Context is delivered via [cyan]raise session start --context[/cyan]."
    )
    console.print("  Use [cyan]rai graph build[/cyan] to rebuild the graph.\n")


# =============================================================================
# Append Commands (Add to memory)
# =============================================================================


@memory_app.command("reinforce")
def reinforce_cmd(
    pattern_id: Annotated[str, typer.Argument(help="Pattern ID to reinforce (e.g., PAT-E-183)")],
    vote: Annotated[
        int,
        typer.Option("--vote", "-v", help="Vote: 1 (applied), 0 (N/A — not counted), -1 (contradicted)"),
    ],
    story_id: Annotated[
        str | None,
        typer.Option("--from", "-f", help="Story ID for traceability (e.g., RAISE-170)"),
    ] = None,
    scope: Annotated[
        str,
        typer.Option("--scope", "-s", help="Memory scope (global, project, personal)"),
    ] = "project",
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path (overrides scope)"),
    ] = None,
) -> None:
    """Reinforce a pattern with a vote signal.

    Called at story-review to record whether a pattern was applied (1),
    not relevant (0), or contradicted (-1) during implementation.
    Vote 0 (N/A) does not modify evaluations count.

    Examples:
        $ rai memory reinforce PAT-E-183 --vote 1 --from RAISE-170
        $ rai memory reinforce PAT-E-094 --vote -1 --from RAISE-170
        $ rai memory reinforce PAT-E-151 --vote 0 --from RAISE-170
    """
    # Validate vote value
    if vote not in (1, 0, -1):
        cli_error(
            f"Invalid vote: {vote}",
            hint="Valid values: 1 (applied), 0 (N/A), -1 (contradicted)",
            exit_code=7,
        )
        return

    vote_int = vote

    # Resolve patterns file
    try:
        memory_scope = MemoryScope(scope)
    except ValueError:
        cli_error(
            f"Invalid scope: {scope}",
            hint="Valid scopes: global, project, personal",
            exit_code=7,
        )
        return

    mem_dir = memory_dir or get_memory_dir_for_scope(memory_scope)
    patterns_file = mem_dir / "patterns.jsonl"

    if not patterns_file.exists():
        cli_error(
            f"Patterns file not found: {patterns_file}",
            hint="Run 'rai memory add-pattern' first or check --memory-dir",
            exit_code=4,
        )
        return

    try:
        result: ReinforceResult = reinforce_pattern(
            patterns_file, pattern_id, vote=vote_int, story_id=story_id
        )
    except KeyError:
        cli_error(
            f"Pattern '{pattern_id}' not found in {patterns_file}",
            hint="Check the pattern ID with 'rai graph query'",
            exit_code=4,
        )
        return

    if not result.was_updated:
        console.print(f"\n[green]✓[/green] {pattern_id}: N/A (not counted)\n")
        return

    # Build summary line
    summary = (
        f"positives={result.positives}, "
        f"negatives={result.negatives}, "
        f"evaluations={result.evaluations}"
    )

    # Compute Wilson score for display
    if result.evaluations > 0 and (result.positives + result.negatives) > 0:
        wilson = wilson_lower_bound(result.positives, result.negatives)
        wilson_str = f"wilson≈{wilson:.2f}"
        if wilson < SCORING_LOW_WILSON_THRESHOLD:
            wilson_str += " [yellow]↓ consider reviewing[/yellow]"
        summary += f", {wilson_str}"

    console.print(f"\n[green]✓[/green] {pattern_id}: {summary}\n")


@memory_app.command("add-pattern")
def add_pattern(
    content: Annotated[str, typer.Argument(help="Pattern description")],
    context: Annotated[
        str,
        typer.Option("--context", "-c", help="Context keywords (comma-separated)"),
    ] = "",
    sub_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Pattern type (codebase, process, architecture, technical)",
        ),
    ] = "process",
    learned_from: Annotated[
        str | None,
        typer.Option("--from", "-f", help="Story/session where learned"),
    ] = None,
    scope: Annotated[
        str,
        typer.Option("--scope", "-s", help="Memory scope (global, project, personal)"),
    ] = "project",
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir", "-m", help="Memory directory path (overrides scope)"
        ),
    ] = None,
) -> None:
    """Add a new pattern to memory.

    Examples:
        # Add a process pattern (default: project scope)
        $ raise memory add-pattern "HITL before commits" -c "git,workflow"

        # Add a technical pattern
        $ raise memory add-pattern "Use capsys for stdout tests" -t technical -c "pytest,testing"

        # Add with source reference
        $ raise memory add-pattern "BFS reuse across modules" -t architecture --from F2.3

        # Add to global scope (universal pattern)
        $ raise memory add-pattern "Universal TDD pattern" --scope global

        # Add to personal scope (my learnings)
        $ raise memory add-pattern "My workflow preference" --scope personal
    """
    # Parse scope
    try:
        memory_scope = MemoryScope(scope)
    except ValueError:
        cli_error(
            f"Invalid scope: {scope}",
            hint="Valid scopes: global, project, personal",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    # Determine directory (explicit dir overrides scope)
    mem_dir = memory_dir or get_memory_dir_for_scope(memory_scope)
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Parse context
    context_list = [c.strip() for c in context.split(",") if c.strip()]

    # Parse sub_type
    try:
        pattern_type = PatternSubType(sub_type)
    except ValueError:
        cli_error(
            f"Invalid pattern type: {sub_type}",
            hint="Valid types: codebase, process, architecture, technical",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    input_data = PatternInput(
        content=content,
        sub_type=pattern_type,
        context=context_list,
        learned_from=learned_from,
    )

    # Load developer prefix for multi-dev safety
    profile = load_developer_profile()
    dev_prefix = profile.get_pattern_prefix() if profile else None

    result = append_pattern(
        mem_dir, input_data, scope=memory_scope, developer_prefix=dev_prefix
    )

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Content: {content[:60]}...")
        if context_list:
            console.print(f"  Context: {', '.join(context_list)}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@memory_app.command("add-calibration")
def add_calibration_cmd(
    story: Annotated[str, typer.Argument(help="Story ID (e.g., F3.5)")],
    name: Annotated[
        str,
        typer.Option("--name", help="Story name (required)"),
    ],
    size: Annotated[
        str,
        typer.Option("--size", "-s", help="T-shirt size: XS, S, M, L, XL (required)"),
    ],
    actual: Annotated[
        int,
        typer.Option("--actual", "-a", help="Actual minutes spent (required)"),
    ],
    estimated: Annotated[
        int | None,
        typer.Option("--estimated", "-e", help="Estimated minutes"),
    ] = None,
    sp: Annotated[
        int | None,
        typer.Option("--sp", help="Story points"),
    ] = None,
    kata: Annotated[
        bool,
        typer.Option("--kata/--no-kata", help="Kata cycle followed (default: yes)"),
    ] = True,
    notes: Annotated[
        str | None,
        typer.Option("--notes", "-n", help="Additional notes"),
    ] = None,
    scope: Annotated[
        str,
        typer.Option("--scope", help="Memory scope (global, project, personal)"),
    ] = "personal",
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir", "-m", help="Memory directory path (overrides scope)"
        ),
    ] = None,
) -> None:
    """Add calibration data for a completed story.

    Examples:
        # Basic calibration (default: personal scope)
        $ rai memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20

        # With estimate for velocity calculation
        $ rai memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60

        # Full details
        $ rai memory add-calibration F3.5 --name "Skills Integration" -s XS -a 20 -e 60 --sp 2 -n "Hook-assisted"

        # Add to project scope (shared)
        $ rai memory add-calibration F3.5 --name "Skills" -s XS -a 20 --scope project
    """
    # Parse scope
    try:
        memory_scope = MemoryScope(scope)
    except ValueError:
        cli_error(
            f"Invalid scope: {scope}",
            hint="Valid scopes: global, project, personal",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    # Determine directory (explicit dir overrides scope)
    mem_dir = memory_dir or get_memory_dir_for_scope(memory_scope)
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL"]
    if size.upper() not in valid_sizes:
        cli_error(
            f"Invalid size: {size}",
            hint=f"Valid sizes: {', '.join(valid_sizes)}",
            exit_code=7,
        )
        return  # cli_error exits, but this satisfies pyright

    input_data = CalibrationInput(
        story=story,
        name=name,
        size=size.upper(),
        sp=sp,
        estimated_min=estimated,
        actual_min=actual,
        kata_cycle=kata,
        notes=notes,
    )

    result = append_calibration(mem_dir, input_data, scope=memory_scope)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Story: {story} ({name})")
        console.print(f"  Size: {size.upper()}, Actual: {actual}min")
        if estimated:
            ratio = round(estimated / actual, 1)
            console.print(f"  Velocity: {ratio}x (estimated {estimated}min)")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@memory_app.command("add-session")
def add_session_cmd(
    topic: Annotated[str, typer.Argument(help="Session topic")],
    outcomes: Annotated[
        str,
        typer.Option("--outcomes", "-o", help="Session outcomes (comma-separated)"),
    ] = "",
    session_type: Annotated[
        str,
        typer.Option("--type", "-t", help="Session type (story, research, etc.)"),
    ] = "story",
    log_path: Annotated[
        str | None,
        typer.Option("--log", "-l", help="Path to session log file"),
    ] = None,
    memory_dir: Annotated[
        Path | None,
        typer.Option("--memory-dir", "-m", help="Memory directory path"),
    ] = None,
) -> None:
    """Add a session record to memory (personal scope).

    Sessions are developer-specific and always written to personal directory.

    Examples:
        # Basic session
        $ raise memory add-session "F3.5 Skills Integration"

        # With outcomes
        $ raise memory add-session "F3.5 Skills Integration" -o "Writer API,Hooks setup,CLI commands"

        # Full details
        $ raise memory add-session "F3.5 Skills Integration" -t story -o "Writer API,Hooks" -l "dev/sessions/2026-02-02-f3.5.md"
    """
    # Sessions always go to personal directory (developer-specific)
    mem_dir = memory_dir or get_personal_dir()
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Parse outcomes
    outcomes_list = [o.strip() for o in outcomes.split(",") if o.strip()]

    input_data = SessionInput(
        topic=topic,
        session_type=session_type,
        outcomes=outcomes_list,
        log_path=log_path,
    )

    result = append_session(mem_dir, input_data)

    if result.success:
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Topic: {topic}")
        console.print(f"  Type: {session_type}")
        if outcomes_list:
            console.print(f"  Outcomes: {', '.join(outcomes_list[:3])}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


# =============================================================================
# Emit Commands (Telemetry signals)
# =============================================================================


@memory_app.command("emit-work")
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
        str,
        typer.Option("--phase", "-p", help="Phase (design, plan, implement, review)"),
    ] = "design",
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
        $ raise memory emit-work epic E9 --event start --phase design
        $ raise memory emit-work epic E9 -e complete -p design
        $ raise memory emit-work epic E9 -e start -p plan

        # Story lifecycle
        $ raise memory emit-work story F9.4 --event start --phase design
        $ raise memory emit-work story F9.4 -e complete -p implement
        $ raise memory emit-work story F9.4 -e start -p review

        # Work blocked
        $ raise memory emit-work story F9.4 -e blocked -p plan -b "unclear requirements"

        # Work unblocked
        $ raise memory emit-work story F9.4 -e unblocked -p plan
    """
    # Validate work type
    valid_work_types: list[Literal["epic", "story"]] = ["epic", "story"]
    work_type_lower = work_type.lower()
    if work_type_lower not in valid_work_types:
        cli_error(
            f"Invalid work type: {work_type}",
            hint=f"Valid types: {', '.join(valid_work_types)}",
            exit_code=7,
        )

    # Validate event type
    valid_events: list[
        Literal["start", "complete", "blocked", "unblocked", "abandoned"]
    ] = [
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
    valid_phases: list[
        Literal["init", "design", "plan", "implement", "review", "close"]
    ] = [
        "init",
        "design",
        "plan",
        "implement",
        "review",
        "close",
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
        console.print(
            "[yellow]Warning:[/yellow] No blocker description provided for blocked event"
        )

    # Create event
    lifecycle_event = WorkLifecycle(
        timestamp=datetime.now(UTC),
        work_type=work_type_lower,  # type: ignore[arg-type]
        work_id=work_id,
        event=event_type,  # type: ignore[arg-type]
        phase=phase,  # type: ignore[arg-type]
        blocker=blocker_value,
    )

    # Resolve optional session ID
    import os

    session_id = resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))

    # Emit signal
    result = emit(lifecycle_event, session_id=session_id)

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


@memory_app.command("emit-session")
def emit_session_event(
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
        $ raise memory emit-session --type story --outcome success

        # With duration and stories
        $ raise memory emit-session -t story -o success -d 45 -f F9.1,F9.2,F9.3

        # Research session
        $ raise memory emit-session --type research --outcome partial --duration 90
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


@memory_app.command("emit-calibration")
def emit_calibration_event(
    story: Annotated[
        str,
        typer.Argument(help="Story ID (e.g., F9.4)"),
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
        $ raise memory emit-calibration F9.4 --size S --estimated 30 --actual 15

        # Story took longer
        $ raise memory emit-calibration F9.4 -s M -e 60 -a 90

        # Short form
        $ raise memory emit-calibration F9.4 -s S -e 30 -a 15
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
