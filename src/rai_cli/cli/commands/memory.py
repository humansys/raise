"""CLI commands for Rai's memory: calibration and session storage.

Memory commands own the persistent knowledge that lives in JSONL files:
- Calibration (estimation data)
- Sessions (work history)

Graph-structure commands have been extracted to the `graph` group (RAISE-247).
Pattern commands have been extracted to the `pattern` group (RAISE-247).
Signal/telemetry commands have been extracted to the `signal` group (RAISE-247).
Backward-compatible aliases remain here and will be removed in a future release.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from rai_cli.cli.error_handler import cli_error
from rai_cli.config.paths import get_personal_dir
from rai_cli.memory import (
    CalibrationInput,
    MemoryScope,
    SessionInput,
    append_calibration,
    append_session,
    get_memory_dir_for_scope,
)

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


def _deprecation_warning(old_cmd: str, new_group: str = "graph", new_cmd: str | None = None) -> None:
    """Print deprecation warning to stderr."""
    target = new_cmd or old_cmd
    _stderr_console.print(
        f"[yellow]DEPRECATED:[/yellow] 'rai memory {old_cmd}' → "
        f"use 'rai {new_group} {target}' instead",
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
    """Deprecated: use 'rai pattern reinforce'."""
    _deprecation_warning("reinforce", "pattern")
    from rai_cli.cli.commands.pattern import reinforce_cmd as _reinforce

    _reinforce(
        pattern_id=pattern_id,
        vote=vote,
        story_id=story_id,
        scope=scope,
        memory_dir=memory_dir,
    )


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
    """Deprecated: use 'rai pattern add'."""
    _deprecation_warning("add-pattern", "pattern", new_cmd="add")
    from rai_cli.cli.commands.pattern import add_pattern as _add

    _add(
        content=content,
        context=context,
        sub_type=sub_type,
        learned_from=learned_from,
        scope=scope,
        memory_dir=memory_dir,
    )


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
# Backward-Compat Aliases: signal commands (extracted to signal.py in RAISE-247)
# These wrappers will be removed in a future release (RAISE-247/S9).
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
    """Deprecated: use 'rai signal emit-work'."""
    _deprecation_warning("emit-work", "signal")
    from rai_cli.cli.commands.signal import emit_work as _emit_work

    _emit_work(
        work_type=work_type,
        work_id=work_id,
        event_type=event_type,
        phase=phase,
        blocker=blocker,
        session=session,
    )


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
    """Deprecated: use 'rai signal emit-session'."""
    _deprecation_warning("emit-session", "signal")
    from rai_cli.cli.commands.signal import emit_session as _emit_session

    _emit_session(
        session_type=session_type,
        outcome=outcome,
        duration=duration,
        stories=stories,
        session=session,
    )


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
    """Deprecated: use 'rai signal emit-calibration'."""
    _deprecation_warning("emit-calibration", "signal")
    from rai_cli.cli.commands.signal import emit_calibration as _emit_calibration

    _emit_calibration(
        story=story,
        size=size,
        estimated=estimated,
        actual=actual,
        session=session,
    )
