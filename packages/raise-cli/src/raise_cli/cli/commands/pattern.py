"""CLI commands for Rai's pattern memory: add, reinforce, promote, query.

Commands:
- add: Add a new learned pattern to memory (SQLite)
- reinforce: Reinforce a pattern with a vote signal
- promote: Change a pattern from personal scope to project scope
- query: Search patterns by keywords (delegates to PatternsBackend.query)
"""

from __future__ import annotations

import logging
from datetime import UTC
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markup import escape

from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import resolve_checkout_root
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
from raise_cli.memory.patterns_backend import PatternValidationError
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

MIN_EVALUATIONS: int = 10
WILSON_THRESHOLD: float = 0.7

console = Console()
logger = logging.getLogger(__name__)


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
    scope: Annotated[  # noqa: ARG001
        str,
        typer.Option(
            "--scope", "-s", help="Memory scope (ignored — SQLite resolves internally)"
        ),
    ] = "project",
    memory_dir: Annotated[  # noqa: ARG001
        Path | None,
        typer.Option(
            "--memory-dir",
            "-m",
            help="Memory directory path (ignored — SQLite resolves internally)",
        ),
    ] = None,
) -> None:
    """Reinforce a pattern with a vote signal.

    Called at story-review to record whether a pattern was applied (1),
    not relevant (0), or contradicted (-1) during implementation.

    Examples:
        $ rai pattern reinforce PAT-001 --vote 1 --from S101
        $ rai pattern reinforce PAT-002 --vote -1 --from S101
    """
    if vote not in (1, 0, -1):
        cli_error(
            f"Invalid vote: {vote}",
            hint="Valid values: 1 (applied), 0 (N/A), -1 (contradicted)",
            exit_code=7,
        )
        return

    try:
        result: ReinforceResult = reinforce_pattern(
            Path("unused"), pattern_id, vote=vote, story_id=story_id
        )
    except KeyError:
        cli_error(
            f"Pattern '{pattern_id}' not found",
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
            help="Pattern type (codebase, process, architecture, technical, approach, risk)",
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
        $ rai pattern add "HITL before commits" -c "git,workflow"
        $ rai pattern add "Use capsys for stdout tests" -t technical -c "pytest,testing"
        $ rai pattern add "BFS reuse across modules" -t architecture --from F2.3
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

    context_list = [c.strip() for c in context.split(",") if c.strip()]

    try:
        pattern_type = PatternSubType(sub_type)
    except ValueError:
        cli_error(
            f"Invalid pattern type: {sub_type}",
            hint="Valid types: codebase, process, architecture, technical, approach, risk",
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

    try:
        result = append_pattern(
            mem_dir, input_data, scope=memory_scope, developer_prefix=dev_prefix
        )
    except PatternValidationError as exc:
        cli_error(f"Pattern rejected: {exc.reason}", hint="Adjust content and retry")
        return

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
        console.print()
    else:
        cli_error(result.message)


@pattern_app.command("query")
def query_cmd(
    keywords: Annotated[
        str,
        typer.Argument(help='Space-separated search terms (e.g., "testing singleton")'),
    ],
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum results to return"),
    ] = 10,
) -> None:
    """Search patterns by keywords.

    Searches pattern content and context tags for matching keywords.
    Delegates to the same PatternsBackend the raise_pattern_query MCP
    tool uses — one query path, two entrypoints (RAISE-15994).

    Examples:
        $ rai pattern query "testing singleton"
        $ rai pattern query "pydantic validation" --limit 5
    """
    import asyncio

    from raise_cli.memory.patterns_backend import get_patterns_backend

    backend = get_patterns_backend()
    results = asyncio.run(backend.query(keywords.split(), limit))

    if not results:
        console.print("\nNo patterns found.\n")
        return

    console.print(f"\nFound {len(results)} pattern(s):\n")
    for r in results:
        content_preview = escape(str(r["content"])[:80])
        console.print(f"  [cyan]{r['id']}[/cyan]  {content_preview}")
        context = r.get("context")
        if context:
            context_str = escape(", ".join(context))
            console.print(f"    Context: {context_str}")
    console.print()


@pattern_app.command("promote")
def promote_pattern(
    pattern_id: Annotated[
        str, typer.Argument(help="Pattern ID to promote (e.g., PAT-E-123)")
    ],
    to: Annotated[
        str,
        typer.Option(
            "--to", "-t", help="Target scope: project (local) or team (server)"
        ),
    ] = "project",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Bypass the evidence gate (explicit team approval)",
        ),
    ] = False,
) -> None:
    """Promote a pattern to a broader scope.

    personal → project: local scope change only.
    personal/project → team: pushes to raise-server for the whole team.

    Examples:
        $ rai pattern promote PAT-E-123
        $ rai pattern promote PAT-E-123 --to team
    """
    from raise_cli.storage.connection import get_project_db
    from raise_cli.storage.schema import create_all

    if to not in ("project", "team"):
        cli_error(
            f"Invalid target scope: {to}",
            hint="Valid targets: project, team",
            exit_code=7,
        )
        return

    conn = get_project_db(resolve_checkout_root())
    create_all(conn)

    row = conn.execute(
        "SELECT scope, content, positives, negatives, evaluations FROM patterns WHERE pattern_id = ?",
        (pattern_id,),
    ).fetchone()

    if row is None:
        cli_error(
            f"Pattern '{pattern_id}' not found",
            hint="Check the pattern ID with 'rai graph query'",
            exit_code=4,
        )
        return

    current_scope, content = row[0], row[1]
    positives: int = row[2] or 0
    negatives: int = row[3] or 0
    evaluations: int = row[4] or 0

    valid_promotions = {
        "project": ["personal"],
        "team": ["personal", "project"],
    }

    if current_scope not in valid_promotions[to]:
        cli_error(
            f"Pattern '{pattern_id}' is already in '{current_scope}' scope — cannot promote to '{to}'",
            hint=f"Valid source scopes for --to {to}: {', '.join(valid_promotions[to])}",
            exit_code=4,
        )
        return

    # Wilson evidence gate — applies only to --to team promotions (AC1, AC5, AC6, AC7)
    if to == "team":
        if evaluations < MIN_EVALUATIONS:
            wilson = 0.0
        else:
            wilson = wilson_lower_bound(positives, negatives)

        if (evaluations < MIN_EVALUATIONS or wilson < WILSON_THRESHOLD) and not force:
            console.print(
                f"[yellow]WARNING:[/yellow] Pattern {pattern_id} has insufficient evidence "
                f"(evaluations={evaluations}, wilson={wilson:.2f}). "
                f"Need >= {MIN_EVALUATIONS} evaluations and wilson >= {WILSON_THRESHOLD}."
            )
            console.print("  Re-run with --force to promote anyway.")
            raise typer.Exit(0)

    target_scope = to if to != "team" else "team"
    conn.execute(
        "UPDATE patterns SET scope = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') "
        "WHERE pattern_id = ?",
        (target_scope, pattern_id),
    )
    conn.commit()

    emitter = create_emitter()
    emitter.emit(
        PatternAddedEvent(
            pattern_id=pattern_id,
            content=str(content),
            context="",
        )
    )

    if to == "team":
        try:
            import getpass
            from datetime import datetime

            from raise_cli.memory.sync import attempt_immediate_push, enqueue_push

            enqueue_push(conn, pattern_id)
            pushed = attempt_immediate_push(conn, pattern_id)

            # Stamp promotion metadata on the local patterns row (AC4)
            conn.execute(
                "UPDATE patterns SET promoted_at = ?, promoted_by = ? WHERE pattern_id = ?",
                (
                    datetime.now(UTC).isoformat(),
                    getpass.getuser(),
                    pattern_id,
                ),
            )
            conn.commit()

            if pushed:
                console.print(
                    f"\n[green]{CHECK}[/green] Promoted {pattern_id} to team (synced to server)"
                )
            else:
                console.print(
                    f"\n[green]{CHECK}[/green] Promoted {pattern_id} to team (queued for sync)"
                )
        except Exception:  # noqa: BLE001
            console.print(
                f"\n[green]{CHECK}[/green] Promoted {pattern_id} to team (queued for sync)"
            )
    else:
        console.print(
            f"\n[green]{CHECK}[/green] Promoted {pattern_id} to project scope"
        )

    console.print(f"  Content: {str(content)[:60]}")
    console.print()


@pattern_app.command("prune")
def prune_cmd(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="List candidates without archiving"),
    ] = False,
    age_days: Annotated[
        int,
        typer.Option("--age", help="Minimum age in days (default: 60)"),
    ] = 60,
) -> None:
    """Archive stale patterns with 0 evaluations older than --age days.

    Foundational patterns (base=1) are never archived.

    Examples:
        $ rai pattern prune --dry-run
        $ rai pattern prune
        $ rai pattern prune --age 90
    """
    from raise_cli.memory.patterns_backend import prune_stale_patterns
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all as ensure_schema

    project_root = resolve_checkout_root()
    conn = get_project_db(project_root)
    ensure_schema(conn)
    pid = get_project_id(project_root)

    result = prune_stale_patterns(
        conn, project_id=pid, age_days=age_days, dry_run=dry_run
    )

    if dry_run:
        if result.candidates:
            console.print(
                f"\nDry run — {result.archived_count} patterns eligible for archival:"
            )
            for c in result.candidates[:20]:
                console.print(
                    f'  {c.pattern_id}  (created {c.created_at})  "{c.content[:50]}..."'
                )
            if len(result.candidates) > 20:
                console.print(f"  ... and {len(result.candidates) - 20} more")
        else:
            console.print("\nNo patterns eligible for archival.")
        console.print(
            f"\n  {result.archived_count} would be archived"
            f"\n  Foundational excluded: {result.excluded_foundational}"
            f"\n  With evaluations excluded: {result.excluded_with_evals}"
            f"\n  Run without --dry-run to apply.\n"
        )
    else:
        if result.archived_count:
            console.print(
                f"\n[green]{CHECK}[/green] Archived {result.archived_count} patterns "
                f"(0 evals, > {age_days} days old)"
            )
        else:
            console.print("\nNo patterns eligible for archival.")
        console.print(
            f"  Excluded: {result.excluded_foundational} foundational (base=1), "
            f"{result.excluded_with_evals} with evaluations"
            f"\n  Remaining active: {result.total_active}\n"
        )


@pattern_app.command("sync")
def sync_cmd(
    status: Annotated[
        bool,
        typer.Option("--status", "-s", help="Show sync status only"),
    ] = False,
) -> None:
    """Sync patterns with raise-server (pull + drain outbox)."""
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all as ensure_schema

    console = Console()
    project = resolve_checkout_root()
    conn = get_project_db(project)
    ensure_schema(conn)

    from raise_cli.memory.sync import drain_outbox, pull_patterns, sync_status

    if status:
        info = sync_status(conn)
        console.print(f"Server configured: {info['server_configured']}")
        console.print(
            f"Outbox: {info['pending']} pending, {info['failed']} failed, {info['synced']} synced"
        )
        console.print(f"Last push: {info['last_push'] or 'never'}")
        console.print(f"Last pull: {info['last_pull'] or 'never'}")
        return

    pid = get_project_id(project)
    pull_result = pull_patterns(conn, project_id=pid)
    drain_result = drain_outbox(conn, project_id=pid)

    console.print(
        f"Pulled: {pull_result['pulled']} ({pull_result['new']} new, {pull_result['updated']} updated)"
    )
    console.print(
        f"Pushed: {drain_result['pushed']} from outbox ({drain_result['failed']} failed)"
    )
