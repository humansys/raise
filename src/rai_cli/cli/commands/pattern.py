"""CLI commands for Rai's pattern memory: add and reinforce.

The pattern group owns commands that write to pattern memory (JSONL files).
These were extracted from the `memory` God Object in RAISE-247 (ADR-038).

Commands:
- add: Add a new learned pattern to memory
- reinforce: Reinforce a pattern with a vote signal (applied/N/A/contradicted)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from rai_cli.cli.error_handler import cli_error
from rai_cli.context.query import (
    SCORING_LOW_WILSON_THRESHOLD,
    wilson_lower_bound,
)
from rai_cli.hooks.emitter import create_emitter
from rai_cli.hooks.events import PatternAddedEvent
from rai_cli.memory import (
    MemoryScope,
    PatternInput,
    PatternSubType,
    ReinforceResult,
    append_pattern,
    get_memory_dir_for_scope,
    reinforce_pattern,
)
from rai_cli.onboarding.profile import load_developer_profile

pattern_app = typer.Typer(
    name="pattern",
    help="Manage learned patterns",
    no_args_is_help=True,
)

console = Console()


@pattern_app.command("reinforce")
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
        $ rai pattern reinforce PAT-E-183 --vote 1 --from RAISE-170
        $ rai pattern reinforce PAT-E-094 --vote -1 --from RAISE-170
        $ rai pattern reinforce PAT-E-151 --vote 0 --from RAISE-170
    """
    if vote not in (1, 0, -1):
        cli_error(
            f"Invalid vote: {vote}",
            hint="Valid values: 1 (applied), 0 (N/A), -1 (contradicted)",
            exit_code=7,
        )
        return

    vote_int = vote

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
            hint="Run 'rai pattern add' first or check --memory-dir",
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

    summary = (
        f"positives={result.positives}, "
        f"negatives={result.negatives}, "
        f"evaluations={result.evaluations}"
    )

    if result.evaluations > 0 and (result.positives + result.negatives) > 0:
        wilson = wilson_lower_bound(result.positives, result.negatives)
        wilson_str = f"wilson≈{wilson:.2f}"
        if wilson < SCORING_LOW_WILSON_THRESHOLD:
            wilson_str += " [yellow]↓ consider reviewing[/yellow]"
        summary += f", {wilson_str}"

    console.print(f"\n[green]✓[/green] {pattern_id}: {summary}\n")


@pattern_app.command("add")
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
        $ rai pattern add "HITL before commits" -c "git,workflow"

        # Add a technical pattern
        $ rai pattern add "Use capsys for stdout tests" -t technical -c "pytest,testing"

        # Add with source reference
        $ rai pattern add "BFS reuse across modules" -t architecture --from F2.3

        # Add to global scope (universal pattern)
        $ rai pattern add "Universal TDD pattern" --scope global

        # Add to personal scope (my learnings)
        $ rai pattern add "My workflow preference" --scope personal
    """
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
    if not mem_dir.exists():
        mem_dir.mkdir(parents=True, exist_ok=True)

    context_list = [c.strip() for c in context.split(",") if c.strip()]

    try:
        pattern_type = PatternSubType(sub_type)
    except ValueError:
        cli_error(
            f"Invalid pattern type: {sub_type}",
            hint="Valid types: codebase, process, architecture, technical",
            exit_code=7,
        )
        return

    input_data = PatternInput(
        content=content,
        sub_type=pattern_type,
        context=context_list,
        learned_from=learned_from,
    )

    profile = load_developer_profile()
    dev_prefix = profile.get_pattern_prefix() if profile else None

    result = append_pattern(
        mem_dir, input_data, scope=memory_scope, developer_prefix=dev_prefix
    )

    if result.success:
        emitter = create_emitter()
        emitter.emit(PatternAddedEvent(
            pattern_id=result.id or "",
            content=content,
            context=context,
        ))
        console.print(f"\n[green]✓[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Content: {content[:60]}...")
        if context_list:
            console.print(f"  Context: {', '.join(context_list)}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)
