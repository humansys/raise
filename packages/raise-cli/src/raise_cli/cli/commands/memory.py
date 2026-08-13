"""Backward-compatible aliases for commands extracted to graph, pattern, and signal groups.

All active commands have been extracted to dedicated groups (CLI restructuring):
- Graph: query, context, build, validate, extract, list, viz
- Pattern: add-pattern, reinforce
- Signal: emit-work, emit-session, emit-calibration

These aliases print deprecation warnings and delegate to the canonical commands.
They will be removed in a future release (v3.0).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

memory_app = typer.Typer(
    name="memory",
    help="Query and manage Rai's memory",
    no_args_is_help=True,
)

# =============================================================================
# Sync subcommand group (S9476.1 — CC Memory git sync)
# =============================================================================

sync_app = typer.Typer(
    name="sync",
    help="Sync Claude Code memory to/from the git-tracked personal/memory/ copy",
    no_args_is_help=True,
)
memory_app.add_typer(sync_app)


@sync_app.command("export")
def sync_export(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project root path"),
    ] = ".",
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Show what would be copied without making changes"
        ),
    ] = False,
    no_secrets_scan: Annotated[
        bool,
        typer.Option("--no-secrets-scan", help="Skip secrets scan (copies all files)"),
    ] = False,
) -> None:
    """Export Claude Code memory files to git-tracked .raise/rai/personal/memory/.

    Copies all files from ~/.claude/projects/{encoded}/memory/ to the
    git-tracked copy. Files containing API keys or secrets are skipped
    unless --no-secrets-scan is given.

    Examples:
        $ rai memory sync export
        $ rai memory sync export --dry-run
        $ rai memory sync export --no-secrets-scan
    """
    from raise_cli.memory.portability import export_memory

    console = Console()
    project_root = Path(project).resolve()
    result = export_memory(
        project_root,
        dry_run=dry_run,
        secrets_scan=not no_secrets_scan,
    )
    label = " [dim](dry run)[/dim]" if dry_run else ""
    console.print(
        f"[green]Export complete{label}:[/green] "
        f"{len(result.copied)} file(s) copied, "
        f"{len(result.skipped)} skipped "
        f"({result.elapsed_ms:.0f}ms)"
    )
    if result.skipped:
        console.print("[yellow]Skipped (secrets detected):[/yellow]")
        for path, reason in result.skipped:
            console.print(f"  - {path.name}: {reason}")


@sync_app.command("import")
def sync_import(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project root path"),
    ] = ".",
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Show what would be restored without making changes"
        ),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Force copy even if destination is newer"),
    ] = False,
) -> None:
    """Import memory files from git-tracked copy to Claude Code memory dir.

    Copies files from .raise/rai/personal/memory/ to the local CC memory dir.
    Default: LWW (last-write-wins by mtime). Use --overwrite to force.

    Examples:
        $ rai memory sync import
        $ rai memory sync import --dry-run
        $ rai memory sync import --overwrite
    """
    from raise_cli.memory.portability import import_memory

    console = Console()
    project_root = Path(project).resolve()
    result = import_memory(project_root, dry_run=dry_run, overwrite=overwrite)
    label = " [dim](dry run)[/dim]" if dry_run else ""
    console.print(
        f"[green]Import complete{label}:[/green] "
        f"{len(result.copied)} file(s) restored, "
        f"{len(result.skipped)} skipped (LWW) "
        f"({result.elapsed_ms:.0f}ms)"
    )


# =============================================================================
# Active Commands
# =============================================================================


@memory_app.command()
def hints(
    prompt: Annotated[str, typer.Argument(help="Prompt text to retrieve hints for")],
    top: Annotated[int, typer.Option("--top", "-n", help="Max hints to return")] = 5,
    project: Annotated[
        str, typer.Option("--project", "-p", help="Project root path")
    ] = ".",
) -> None:
    """Retrieve neuro-symbolic graph hints for a prompt.

    Outputs formatted markdown hints or nothing if the prompt is trivial
    or no relevant graph nodes are found.

    Examples:
        $ rai memory hints "how do I write an alembic migration"
        $ rai memory hints "alembic revision id" --top 3
    """
    from raise_cli.memory.hint_oracle import get_hints, triviality_gate

    if triviality_gate(prompt):
        return

    result = get_hints(prompt, top_k=top, project_root=Path(project).resolve())
    if result:
        console = Console()
        console.print(result)


@memory_app.command()
def migrate(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Execute the migration (default: dry-run)"),
    ] = False,
    map_epic: Annotated[
        list[str] | None,
        typer.Option(
            "--map", help="Epic→mission mapping (e.g., 'e2491:mission-primitive')"
        ),
    ] = None,
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project root path"),
    ] = ".",
) -> None:
    """Migrate flat Claude Code memory files into mission-scoped subdirectories.

    By default runs in dry-run mode. Pass --apply to execute.

    Examples:
        $ rai memory migrate                              # dry-run
        $ rai memory migrate --apply                      # execute
        $ rai memory migrate --apply --map e2491:mission-primitive
    """
    from raise_cli.config.paths import get_claude_memory_dir
    from raise_cli.memory.migrate_claude import execute_migration, plan_migration

    console = Console()
    memory_dir = get_claude_memory_dir(Path(project).resolve())

    if not memory_dir.exists():
        console.print(f"[red]Memory directory not found:[/red] {memory_dir}")
        raise typer.Exit(1)

    epic_mission_map: dict[str, str] = {}
    for entry in map_epic or []:
        if ":" not in entry:
            console.print(
                f"[red]Invalid --map format:[/red] '{entry}' (expected 'epic:mission')"
            )
            raise typer.Exit(1)
        key, _, value = entry.partition(":")
        epic_mission_map[key.strip()] = value.strip()

    plan = plan_migration(memory_dir, epic_mission_map=epic_mission_map or None)

    console.print(plan.format_summary())

    if not apply:
        console.print(
            "\n[yellow]No changes made.[/yellow] Run with --apply to execute."
        )
        return

    backup_dir = execute_migration(memory_dir, plan)

    console.print("\n[green]Migration complete.[/green]")
    console.print(f"  Backup: {backup_dir}")
    console.print("  MEMORY.md regenerated.")
    if plan.to_unassigned:
        console.print("  Review _unassigned/ and move files to missions/ as needed.")


@memory_app.command()
def ingest(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write the cartridge (default: dry-run preview)"),
    ] = False,
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project root path"),
    ] = ".",
) -> None:
    """Ingest Claude Code memory notes into the external memory cartridge.

    RAISE-13911 — the memory cartridge lives outside the repo, at
    ``$RAI_HOME/cartridges/memory/`` (default ``~/.rai/cartridges/memory/``),
    so a derived index over personal memory is structurally impossible to
    commit. Dry-run by default (reports a candidate node count, writes
    nothing). ``--apply`` scaffolds/refreshes the cartridge (idempotent)
    and re-tiers ``MEMORY.md`` to Tier-1 only.

    Examples:
        $ rai memory ingest              # dry-run: reports N candidate nodes
        $ rai memory ingest --apply      # write cartridge + re-tier MEMORY.md
    """
    from raise_cli.memory.ingest_cartridge import ingest_memory_cartridge

    console = Console()
    project_root = Path(project).resolve()

    try:
        result = ingest_memory_cartridge(project_root, apply=apply)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    for warn in result.warnings:
        console.print(f"[yellow]WARN:[/yellow] {warn}")
    for err in result.errors:
        console.print(f"[red]ERROR:[/red] {err}")

    if not apply:
        console.print(
            f"[dim](dry-run)[/dim] {result.node_count} candidate node(s) "
            f"at {result.cartridge_dir}"
        )
        console.print(
            "\n[yellow]No changes made.[/yellow] Run with --apply to execute."
        )
        return

    console.print(
        f"[green]Ingested {result.node_count} node(s)[/green] -> {result.cartridge_dir}"
    )
    console.print("  MEMORY.md regenerated (Tier-1 only).")


@memory_app.command()
def dedup(
    apply: Annotated[
        bool,
        typer.Option(
            "--apply",
            help="Collapse duplicates + create UNIQUE index (default: dry-run)",
        ),
    ] = False,
    purge: Annotated[
        bool,
        typer.Option(
            "--purge",
            help="After collapse, DELETE archived losers + VACUUM (requires --apply)",
        ),
    ] = False,
    backup: Annotated[
        bool,
        typer.Option(
            "--backup/--no-backup", help="Backup before writing (default: on)"
        ),
    ] = True,
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project root path"),
    ] = ".",
) -> None:
    """Collapse duplicate pattern rows and normalize project_id shadows.

    S14056.2/RAISE-14579 — the old dedup check (validate_pattern_add) is
    scoped by project_id and never sees the project_id='' shadow rows
    sync.py inserts, so duplicates accumulate. This groups active rows by
    (norm_pid, content_hash), picks a winner (base=1 > local authorship >
    lowest pattern_id), MAX-merges counters, and archives the rest.

    Dry-run by default (reports counts, writes nothing). ``--apply``
    executes: backs up ``~/.rai/raise.db`` (online-consistent, via
    conn.backup — ``--no-backup`` to skip), archives losers (never
    DELETEs), then re-keys any remaining ``project_id=''`` orphan row —
    one with no duplicate sibling, invisible to the collapse above — to the
    local project id (RAISE-15995), then creates the
    UNIQUE(project_id, content_hash) index. ``--purge --apply`` additionally
    DELETEs the archived losers and runs VACUUM to reclaim disk space.

    Examples:
        $ rai memory dedup                  # dry-run: reports groups/losers
        $ rai memory dedup --apply          # collapse + backup + UNIQUE index
        $ rai memory dedup --purge --apply  # + delete losers + VACUUM
    """
    from raise_cli.memory.dedup import (
        apply_collapse,
        apply_shadow_backfill,
        backup_db,
        plan_dedup,
        plan_shadow_backfill,
        purge_archived_losers,
        vacuum,
    )
    from raise_cli.storage.connection import (
        get_project_db,
        get_project_db_path,
        get_project_id,
    )
    from raise_cli.storage.schema import (
        _apply_v52,  # noqa: PLC2701  # pyright: ignore[reportPrivateUsage]
        create_all,
    )

    console = Console()

    if purge and not apply:
        console.print("[red]Error:[/red] --purge requires --apply")
        raise typer.Exit(1)

    project_root = Path(project).resolve()
    # Only call-site in this story that resolves a real DB path (AC8 boundary) —
    # the pure functions in memory/dedup.py never touch ~/.rai/raise.db.
    conn = get_project_db(project_root)
    create_all(conn)
    local_pid = get_project_id(project_root)

    plan = plan_dedup(conn, local_pid)

    console.print(f"Grupos a colapsar: {len(plan.groups)}")
    console.print(f"Filas activas: {plan.total_active}")
    console.print(f"Ganadores: {len(plan.groups)}")
    console.print(f"Perdedores a archivar: {plan.losers}")
    console.print(f"content_hash NULL (omitidas): {plan.null_hash_skipped}")
    orphan_preview = plan_shadow_backfill(conn)
    console.print(
        f"Filas project_id='' (total, antes de colapso): {len(orphan_preview)} "
        "(RAISE-15995 — se re-key tras el colapso, ver abajo)"
    )
    if plan.per_project:
        per_project_str = " | ".join(
            f"{pid}={count}" for pid, count in sorted(plan.per_project.items())
        )
        console.print(f"Por proyecto: {per_project_str}")
    if plan.groups:
        largest = max(plan.groups, key=lambda g: len(g.loser_ids))
        console.print(
            f"Grupo mayor: {len(largest.loser_ids) + 1} copias de "
            f"'{largest.content_hash}' -> ganador {largest.winner_id}"
        )

    if not apply:
        console.print(
            "\n[yellow]NADA escrito.[/yellow] Corre con --apply para ejecutar."
        )
        return

    if not (project_root / ".raise").is_dir():
        console.print(
            f"[red]Error:[/red] {project_root} no tiene .raise/ — pasa --project "
            "explicito a un proyecto RaiSE valido antes de --apply (RAISE-16219)."
        )
        raise typer.Exit(1)

    if backup:
        ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
        backup_dst = get_project_db_path(project_root).parent / f"raise.db.bak-{ts}"
        try:
            backup_db(conn, backup_dst)
        except Exception as exc:
            console.print(f"[red]Error:[/red] backup failed, aborting --apply: {exc}")
            raise typer.Exit(1) from exc
        console.print(f"Backup: {backup_dst}")

    apply_collapse(conn, plan)

    post_plan = plan_dedup(conn, local_pid)
    if post_plan.groups:
        console.print(
            f"[red]Error:[/red] {len(post_plan.groups)} grupo(s) siguen activos "
            "tras el colapso — abortando antes del índice UNIQUE."
        )
        raise typer.Exit(1)

    # RAISE-15995: re-key orphan project_id='' rows that apply_collapse never
    # touched (no duplicate sibling to form a group with). MUST run after
    # apply_collapse — see plan_shadow_backfill docstring for why the order
    # matters (winner-selection tiebreak signal).
    shadow_plan = plan_shadow_backfill(conn)
    shadow_fixed = apply_shadow_backfill(conn, shadow_plan, local_pid)

    _apply_v52(conn)
    console.print(
        f"Colapsados {len(plan.groups)} grupos | {plan.losers} filas archived=1 "
        "| ganadores normalizados"
    )
    console.print(
        f"Backfill project_id (RAISE-15995): {shadow_fixed} fila(s) huérfana(s) "
        f"re-keyed a '{local_pid}'"
    )
    console.print(
        "Aserción 0 dups activos: OK | Índice UNIQUE "
        "idx_patterns_content_hash_unique creado"
    )

    if not purge:
        console.print(
            "(perdedores recuperables: SELECT ... WHERE archived=1). "
            "Espacio NO reclamado aún."
        )
        return

    deleted = purge_archived_losers(conn, local_pid)
    vacuum(conn)
    console.print(f"Borradas {deleted} filas (dedup losers) | VACUUM ejecutado.")


# =============================================================================
# Deprecation Helpers
# =============================================================================


_stderr_console = Console(stderr=True)


def _deprecation_warning(
    old_cmd: str, new_group: str = "graph", new_cmd: str | None = None
) -> None:
    """Print deprecation warning to stderr."""
    target = new_cmd or old_cmd
    _stderr_console.print(
        f"[yellow]DEPRECATED:[/yellow] 'rai memory {old_cmd}' → "
        f"use 'rai {new_group} {target}' instead",
    )


# =============================================================================
# Backward-Compat Aliases: graph commands (extracted to graph.py during CLI restructuring)
# These wrappers will be removed in a future release (v3.0).
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
    from raise_cli.cli.commands.graph import query as graph_query

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
    from raise_cli.cli.commands.graph import context_cmd as graph_context

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
    from raise_cli.cli.commands.graph import build as graph_build

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
    from raise_cli.cli.commands.graph import validate as graph_validate

    graph_validate(index_file=index_file)


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
    from raise_cli.cli.commands.graph import list_graph

    list_graph(
        format=format, output=output, index_path=index_path, memory_only=memory_only
    )


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
    from raise_cli.cli.commands.graph import viz as graph_viz

    graph_viz(output=output, index_path=index_path, open_browser=open_browser)


# =============================================================================
# Backward-Compat Aliases: pattern commands (extracted to pattern.py during CLI restructuring)
# These wrappers will be removed in a future release (v3.0).
# =============================================================================


@memory_app.command("reinforce")
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
    """Deprecated: use 'rai pattern reinforce'."""
    _deprecation_warning("reinforce", "pattern")
    from raise_cli.cli.commands.pattern import reinforce_cmd as _reinforce

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
    from raise_cli.cli.commands.pattern import add_pattern as _add

    _add(
        content=content,
        context=context,
        sub_type=sub_type,
        learned_from=learned_from,
        scope=scope,
        memory_dir=memory_dir,
    )


# =============================================================================
# Backward-Compat Aliases: signal commands (extracted to signal.py during CLI restructuring)
# These wrappers will be removed in a future release (v3.0).
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
    from raise_cli.cli.commands.signal import emit_work as _emit_work

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
    from raise_cli.cli.commands.signal import emit_session as _emit_session

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
    from raise_cli.cli.commands.signal import emit_calibration as _emit_calibration

    _emit_calibration(
        story=story,
        size=size,
        estimated=estimated,
        actual=actual,
        session=session,
    )
