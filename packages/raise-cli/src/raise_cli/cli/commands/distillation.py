"""CLI commands for distillation run management: list, show, stats."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

distillation_app = typer.Typer(
    name="distillation", help="Post-session distillation run management."
)
_console = Console()


@distillation_app.command("list")
def list_cmd(
    since: Annotated[
        str | None, typer.Option("--since", help="Filter by date (YYYY-MM-DD)")
    ] = None,
    runtime: Annotated[
        str | None, typer.Option("--runtime", help="Filter by runtime")
    ] = None,
) -> None:
    """List distillation runs."""
    from raise_cli.distillation.storage import list_runs
    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()
    runs = list_runs(conn, since=since, runtime=runtime)

    if not runs:
        _console.print("[yellow]No distillation runs found.[/yellow]")
        return

    table = Table(title="Distillation Runs")
    table.add_column("Session ID", style="cyan")
    table.add_column("Date")
    table.add_column("Runtime", style="dim")
    table.add_column("Turns", justify="right")
    table.add_column("D", justify="right", style="green")
    table.add_column("C", justify="right", style="red")
    table.add_column("P", justify="right", style="blue")
    table.add_column("B", justify="right", style="yellow")

    for run in runs:
        table.add_row(
            run.session_id[:30],
            run.date,
            run.runtime,
            str(run.turns_total),
            str(run.decisions_count),
            str(run.corrections_count),
            str(run.patterns_count),
            str(run.blockers_count),
        )

    _console.print(table)
    _console.print("[dim]D=decisions C=corrections P=patterns B=blockers[/dim]")


@distillation_app.command("show")
def show_cmd(
    session_id: Annotated[str, typer.Argument(help="Session ID to show")],
) -> None:
    """Show details of a single distillation run."""
    from raise_cli.distillation.storage import get_run
    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()
    run = get_run(conn, session_id)

    if run is None:
        _console.print(f"[red]Run not found: {session_id}[/red]")
        raise typer.Exit(1)

    _console.print(f"[bold]Session:[/bold] {run.session_id}")
    _console.print(f"[bold]Date:[/bold] {run.date}")
    _console.print(f"[bold]Project:[/bold] {run.project or '—'}")
    _console.print(f"[bold]Runtime:[/bold] {run.runtime}")
    _console.print(f"[bold]Turns:[/bold] {run.turns_total}")
    _console.print(f"[bold]Decisions:[/bold] {run.decisions_count}")
    _console.print(f"[bold]Corrections:[/bold] {run.corrections_count}")
    _console.print(f"[bold]Patterns:[/bold] {run.patterns_count}")
    _console.print(f"[bold]Blockers:[/bold] {run.blockers_count}")
    _console.print(f"[bold]Tool uses:[/bold] {run.tool_use_count}")
    _console.print(f"[bold]Journal:[/bold] {run.journal_path or '—'}")
    _console.print(f"[bold]Created:[/bold] {run.created_at}")


@distillation_app.command("stats")
def stats_cmd(
    since: Annotated[
        str | None, typer.Option("--since", help="Filter by date (YYYY-MM-DD)")
    ] = None,
) -> None:
    """Aggregate distillation stats by period."""
    from raise_cli.distillation.storage import stats
    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()
    result = stats(conn, since=since)

    period = f"since {since}" if since else "all time"
    _console.print(f"[bold]Distillation Stats ({period})[/bold]")
    _console.print(f"  Runs:        {result['total_runs']}")
    _console.print(f"  Turns:       {result['total_turns']}")
    _console.print(f"  Decisions:   {result['total_decisions']}")
    _console.print(f"  Corrections: {result['total_corrections']}")
    _console.print(f"  Patterns:    {result['total_patterns']}")
    _console.print(f"  Blockers:    {result['total_blockers']}")
    _console.print(f"  Tool uses:   {result['total_tool_use']}")


@distillation_app.command("score")
def score_cmd(
    session_id: Annotated[str, typer.Argument(help="Session ID to score")],
) -> None:
    """Show the Jidoka (gate-honoring) score for a session."""
    from raise_cli.distillation.storage import jidoka_score
    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()
    s = jidoka_score(conn, session_id)

    if s.no_failures and s.bypass_flags == 0 and s.omissions == 0:
        _console.print(
            f"[green]Session {session_id}: no gate failures recorded.[/green]"
        )
        _console.print("[dim](Either all gates passed or no gates were invoked.)[/dim]")
        return

    score_str = f"{s.score:.2f}" if s.score is not None else "N/A"
    color = (
        "green"
        if (s.score or 0) >= 0.8
        else "yellow"
        if (s.score or 0) >= 0.5
        else "red"
    )

    _console.print(
        f"[bold]Jidoka Score:[/bold] [{color}]{score_str}[/{color}]"
        + (
            f" ({s.honored}/{s.total_failures} gate failures honored)"
            if s.total_failures
            else ""
        )
    )
    _console.print(
        f"  Gate failures:  {s.total_failures} ({s.honored} honored, {s.total_failures - s.honored} evaded)"
    )
    _console.print(f"  Bypass flags:   {s.bypass_flags}")
    _console.print(f"  Omissions:      {s.omissions}")


@distillation_app.command("patterns")
def patterns_cmd(
    cluster: Annotated[
        bool, typer.Option("--cluster", help="Scan journals and propose new patterns")
    ] = False,
    min_sessions: Annotated[
        int,
        typer.Option(
            "--min-sessions", help="Minimum sessions for a cluster to qualify"
        ),
    ] = 2,
    accept: Annotated[
        int | None, typer.Option("--accept", help="Accept a proposed pattern by ID")
    ] = None,
    reject: Annotated[
        int | None, typer.Option("--reject", help="Reject a proposed pattern by ID")
    ] = None,
) -> None:
    """Show and manage proposed cross-session patterns."""
    import asyncio

    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()

    if accept is not None:
        row = conn.execute(
            "SELECT id, cluster_theme FROM proposed_patterns WHERE id = ?", (accept,)
        ).fetchone()
        if row is None:
            _console.print(f"[red]No proposed pattern with id={accept}[/red]")
            raise typer.Exit(1)
        from raise_cli.memory.patterns_backend import get_patterns_backend

        backend = get_patterns_backend()
        result = asyncio.run(
            backend.add(
                content=row["cluster_theme"],
                context_tags=["distillation", "cross-session"],
                pattern_type="process",
                from_story="distillation-clustering",
            )
        )
        pat_id = result.get("pattern_id", "") if isinstance(result, dict) else ""  # type: ignore[union-attr]
        conn.execute(
            "UPDATE proposed_patterns SET status='accepted', pattern_id=?, reviewed_at=datetime('now') WHERE id=?",
            (pat_id, accept),
        )
        conn.commit()
        _console.print(f"[green]Accepted: {row['cluster_theme'][:80]}[/green]")
        return

    if reject is not None:
        n = conn.execute(
            "UPDATE proposed_patterns SET status='rejected', reviewed_at=datetime('now') WHERE id=?",
            (reject,),
        ).rowcount
        conn.commit()
        if n == 0:
            _console.print(f"[red]No proposed pattern with id={reject}[/red]")
            raise typer.Exit(1)
        _console.print(f"[yellow]Rejected proposal {reject}[/yellow]")
        return

    if cluster:
        from raise_cli.distillation.clustering import propose_from_journals

        found = propose_from_journals(conn, min_sessions=min_sessions)
        _console.print(f"[dim]Clustering done — {len(found)} cluster(s) found.[/dim]")

    rows = conn.execute(
        "SELECT id, cluster_theme, correction_count, sample_keys FROM proposed_patterns "
        "WHERE status='pending' ORDER BY correction_count DESC, id"
    ).fetchall()

    if not rows:
        _console.print(
            "[dim]No pending proposed patterns. Run with --cluster to scan journals.[/dim]"
        )
        return

    table = Table(title="Proposed Patterns (pending)")
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Sessions", justify="right")
    table.add_column("Theme")
    for row in rows:
        table.add_row(
            str(row["id"]), str(row["correction_count"]), row["cluster_theme"][:100]
        )
    _console.print(table)
    _console.print(
        "[dim]Use --accept <id> or --reject <id> to action a proposal.[/dim]"
    )


def _enrich_query(
    conn: object,
    session_id: str | None,
    since: str | None,
    min_corrections: int,
    limit: int | None,
) -> list[tuple[str, str, str]]:  # type: ignore[type-arg]
    """Return (session_id, project, date) rows for sessions with empty journal_md."""
    query = (
        "SELECT session_id, project, date FROM distillation_runs WHERE journal_md = ''"
    )
    params: list[str | int] = []
    if session_id:
        query += " AND session_id LIKE ?"
        params.append(f"{session_id}%")
    if since:
        query += " AND date >= ?"
        params.append(since)
    if min_corrections:
        query += " AND corrections_count >= ?"
        params.append(min_corrections)
    query += " ORDER BY date DESC, corrections_count DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    return conn.execute(query, params).fetchall()  # type: ignore[union-attr]


def _enrich_one(sid: str, project: str, sid_to_path: dict[str, Path]) -> bool:
    """Run full LLM distillation on one session. Returns True on success."""
    import asyncio

    from raise_cli.distillation.agent import distill

    jsonl: Path | None = sid_to_path.get(sid)
    if jsonl is None:
        return False
    asyncio.run(distill(jsonl, project=project or "", use_llm=True))
    return True


@distillation_app.command("enrich")
def enrich_cmd(
    since: Annotated[
        str | None,
        typer.Option("--since", help="Enrich sessions with date >= DATE (YYYY-MM-DD)"),
    ] = None,
    session_id: Annotated[
        str | None,
        typer.Option("--session", help="Enrich a single session by ID (prefix ok)"),
    ] = None,
    min_corrections: Annotated[
        int,
        typer.Option(
            "--min-corrections", help="Only enrich sessions with >= N corrections"
        ),
    ] = 0,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Max sessions to enrich"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="List targets without running distillation"),
    ] = False,
) -> None:
    """Run full LLM distillation on historical sessions to populate journal_md.

    Uses the LLM classifier (Haiku → DeepSeek → subprocess fallback chain) for
    every turn — no keyword filter, 100% turn coverage.

    Sessions are selected from distillation_runs where journal_md is empty.
    """
    from raise_cli.distillation.backfill import enumerate_jsonls
    from raise_cli.storage.connection import get_global_db

    conn = get_global_db()
    rows = _enrich_query(conn, session_id, since, min_corrections, limit)
    if not rows:
        _console.print("[yellow]No sessions found matching criteria.[/yellow]")
        return

    _console.print(f"[bold]Enrich targets:[/bold] {len(rows)} session(s)")
    if dry_run:
        for r in rows:
            _console.print(f"  {r[0][:8]}  {r[2]}  project={r[1] or '—'}")
        return

    sid_to_path: dict[str, Path] = {p.stem: p for p in enumerate_jsonls()}
    ok = 0
    failed = 0
    for i, (sid, project, date) in enumerate(rows, 1):
        label = f"  [{i}/{len(rows)}] {sid[:8]} ({date})"
        if sid not in sid_to_path:
            _console.print(f"{label} [yellow]JSONL not found[/yellow]")
            failed += 1
            continue
        _console.print(f"{label} …", end="")
        try:
            _enrich_one(sid, project, sid_to_path)
            _console.print(" [green]✓[/green]")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            _console.print(f" [red]✗ {exc}[/red]")
            failed += 1

    _console.print(f"\n[bold]Done:[/bold] {ok} enriched, {failed} failed")


@distillation_app.command("backfill")
def backfill_cmd(
    since: Annotated[
        str | None,
        typer.Option(
            "--since", help="Only process JSONLs modified since DATE (YYYY-MM-DD)"
        ),
    ] = None,
    limit: Annotated[
        int | None, typer.Option("--limit", help="Process at most N sessions")
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Count sessions WITHOUT writing to DB")
    ] = False,
) -> None:
    """Backfill historical session JSONLs into distillation_runs using heuristic classifier."""
    from raise_cli.distillation.backfill import (
        backfill_session,
        enumerate_jsonls,
        generate_report,
    )
    from raise_cli.storage.connection import get_global_db

    paths = enumerate_jsonls(since=since, limit=limit)
    if not paths:
        _console.print("[yellow]No JSONLs found.[/yellow]")
        return

    mode = "[yellow]DRY RUN[/yellow]" if dry_run else "[green]writing to DB[/green]"
    _console.print(f"Backfill: {len(paths)} sessions — {mode}")

    conn = get_global_db()
    results: list[tuple] = []  # type: ignore[type-arg]
    skipped = 0
    for i, path in enumerate(paths, 1):
        counts = backfill_session(conn, path, dry_run=dry_run)
        if counts is None:
            skipped += 1
            continue
        results.append((path, counts))
        if i % 50 == 0 or i == len(paths):
            _console.print(f"  [{i}/{len(paths)}] processed ({skipped} skipped)")

    report = generate_report(results, dry_run=dry_run)
    _console.print(report)
    _console.print(f"\n[dim]Skipped (empty/malformed): {skipped}[/dim]")
