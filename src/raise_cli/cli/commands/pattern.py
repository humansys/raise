"""CLI commands for Rai's pattern memory: add, reinforce, promote.

The pattern group owns commands that write to pattern memory (JSONL files).
These were extracted from the `memory` God Object (see ADR-038).

Commands:
- add: Add a new learned pattern to memory
- reinforce: Reinforce a pattern with a vote signal (applied/N/A/contradicted)
- promote: Move a pattern from personal scope to project scope
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.error_handler import cli_error
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import PatternAddedEvent
from raise_cli.memory import (
    MemoryScope,
    PatternInput,
    PatternSubType,
    ReinforceResult,
    append_pattern,
    get_memory_dir_for_scope,
    reinforce_pattern,
)
from raise_cli.onboarding.profile import load_developer_profile
from raise_cli.output.symbols import CHECK
from raise_core.graph.query import (
    SCORING_LOW_WILSON_THRESHOLD,
    wilson_lower_bound,
)

pattern_app = typer.Typer(
    name="pattern",
    help="Manage learned patterns",
    no_args_is_help=True,
)

console = Console()

_PATTERNS_FILE = "patterns.jsonl"


@pattern_app.command("reinforce")
def reinforce_cmd(
    pattern_id: Annotated[
        str, typer.Argument(help="Pattern ID to reinforce (e.g., PAT-E-183)")
    ],
    vote: Annotated[
        int,
        typer.Option(
            "--vote",
            "-v",
            help="Vote: 1 (applied), 0 (N/A — not counted), -1 (contradicted)",
        ),
    ],
    story_id: Annotated[
        str | None,
        typer.Option("--from", "-f", help="Story ID for traceability (e.g., S101)"),
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
    """Reinforce a pattern with a vote signal.

    Called at story-review to record whether a pattern was applied (1),
    not relevant (0), or contradicted (-1) during implementation.
    Vote 0 (N/A) does not modify evaluations count.

    Examples:
        $ rai pattern reinforce PAT-001 --vote 1 --from S101
        $ rai pattern reinforce PAT-002 --vote -1 --from S101
        $ rai pattern reinforce PAT-003 --vote 0 --from S101
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

    mem_dir = (memory_dir or get_memory_dir_for_scope(memory_scope)).resolve()
    patterns_file = mem_dir / _PATTERNS_FILE

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
        console.print(f"\n[green]{CHECK}[/green] {pattern_id}: N/A (not counted)\n")
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

    console.print(f"\n[green]{CHECK}[/green] {pattern_id}: {summary}\n")


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
        # Add a process pattern (default: personal scope)
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

    mem_dir = (memory_dir or get_memory_dir_for_scope(memory_scope)).resolve()
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
        emitter.emit(
            PatternAddedEvent(
                pattern_id=result.id or "",
                content=content,
                context=context,
            )
        )
        console.print(f"\n[green]{CHECK}[/green] {result.message}")
        console.print(f"  ID: [cyan]{result.id}[/cyan]")
        console.print(f"  Content: {content[:60]}...")
        if context_list:
            console.print(f"  Context: {', '.join(context_list)}")
        console.print("\n[dim]Index will rebuild on next query.[/dim]\n")
    else:
        cli_error(result.message)


@pattern_app.command("promote")
def promote_pattern(
    pattern_id: Annotated[
        str, typer.Argument(help="Pattern ID to promote (e.g., PAT-E-123)")
    ],
    memory_dir: Annotated[
        Path | None,
        typer.Option(
            "--memory-dir",
            "-m",
            help="Memory directory path (overrides default)",
        ),
    ] = None,
) -> None:
    """Promote a pattern from personal scope to project scope.

    Moves the pattern entry from personal patterns.jsonl to project patterns.jsonl.
    The pattern ID is preserved.

    Examples:
        $ rai pattern promote PAT-E-123
    """
    personal_dir = (
        memory_dir or get_memory_dir_for_scope(MemoryScope.PERSONAL)
    ).resolve()
    personal_file = personal_dir / _PATTERNS_FILE

    if not personal_file.exists():
        cli_error(
            f"Personal patterns file not found: {personal_file}",
            hint="No personal patterns to promote. Add patterns first with 'rai pattern add'.",
            exit_code=4,
        )
        return

    # Read all personal patterns and find the target
    lines = personal_file.read_text(encoding="utf-8").strip().splitlines()
    target: dict[str, object] | None = None
    remaining: list[str] = []

    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("id") == pattern_id:
            target = entry
        else:
            remaining.append(line)

    if target is None:
        cli_error(
            f"Pattern '{pattern_id}' not found in personal patterns",
            hint="Check the pattern ID. Only personal-scope patterns can be promoted.",
            exit_code=4,
        )
        return

    # Append to project patterns
    project_dir = get_memory_dir_for_scope(MemoryScope.PROJECT)
    project_dir.mkdir(parents=True, exist_ok=True)
    project_file = project_dir / _PATTERNS_FILE
    with project_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(target)) + "\n")

    # Rewrite personal file without the promoted pattern (atomic: temp + rename)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=personal_file.parent, suffix=".tmp")
    try:
        with open(tmp_fd, "w", encoding="utf-8") as tmp_f:
            for line in remaining:
                tmp_f.write(line + "\n")
        Path(tmp_path).replace(personal_file)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise

    # Emit hook
    content_str = str(target.get("content", ""))
    emitter = create_emitter()
    emitter.emit(
        PatternAddedEvent(
            pattern_id=pattern_id,
            content=content_str,
            context=str(target.get("context", "")),
        )
    )

    console.print(f"\n[green]{CHECK}[/green] Promoted {pattern_id} to project scope")
    console.print(f"  Content: {content_str[:60]}")
    console.print()
