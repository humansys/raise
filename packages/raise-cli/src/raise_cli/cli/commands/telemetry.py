"""CLI commands for querying telemetry data from raise-server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import httpx
import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from raise_cli.telemetry.cost_report import (
        CostReport,
        EpicRow,
        ReportComparison,
        StoryAttribution,
        TrendReport,
        WeeklyRow,
    )
    from raise_cli.telemetry.defect_attribution import AttributionRecord
    from raise_cli.telemetry.szz import IntroducerResult, SzzAttributor

telemetry_app = typer.Typer(
    name="telemetry",
    help="Query telemetry data from raise-server",
    no_args_is_help=True,
)

console = Console()

_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=2.0)

# S6456.4 — cost trend constants (from epic scope.md)
_BASELINE_USD: float = 36.0  # current average cost per story
_TARGET_USD: float = 18.0  # mission objective [0]


def _get_client() -> httpx.Client | None:
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is None:
        return None
    server_url, api_key = creds
    return httpx.Client(
        base_url=server_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=_TIMEOUT,
    )


@telemetry_app.command("tokens")
def list_tokens(
    story: Annotated[
        str | None,
        typer.Option("--story", "-s", help="Filter by story ID (e.g. S3044.4)"),
    ] = None,
    phase: Annotated[
        str | None,
        typer.Option("--phase", "-p", help="Filter by phase (e.g. implement)"),
    ] = None,
    since: Annotated[
        str | None,
        typer.Option(
            "--since", help="ISO 8601 datetime — return records after this time"
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Max records to return", min=1, max=100),
    ] = 20,
    offset: Annotated[
        int,
        typer.Option("--offset", help="Pagination offset", min=0),
    ] = 0,
) -> None:
    """List token usage events from raise-server.

    Requires RAISE_SERVER_URL and RAISE_API_KEY environment variables.

    Examples:
        $ rai telemetry tokens
        $ rai telemetry tokens --story S3044.4
        $ rai telemetry tokens --phase implement --limit 10
    """
    client = _get_client()
    if client is None:
        console.print(
            "[yellow]⚠[/yellow] RAISE_SERVER_URL or RAISE_API_KEY not set — "
            "cannot query telemetry."
        )
        raise typer.Exit(1)

    params: dict[str, str | int] = {"limit": limit, "offset": offset}
    if story is not None:
        params["story"] = story
    if phase is not None:
        params["phase"] = phase
    if since is not None:
        params["since"] = since

    try:
        with client:
            response = client.get("/api/telemetry/tokens", params=params)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        console.print(f"[red]Error:[/red] server returned {exc.response.status_code}")
        raise typer.Exit(1) from exc
    except httpx.TransportError as exc:
        console.print(f"[red]Error:[/red] could not reach server — {exc}")
        raise typer.Exit(1) from exc

    data = response.json()
    events = data.get("events", [])
    total = data.get("total", 0)

    if not events:
        console.print("[dim]No token usage events found.[/dim]")
        return

    table = Table(title=f"Token Usage ({len(events)} of {total})")
    table.add_column("Story", style="cyan")
    table.add_column("Phase", style="magenta")
    table.add_column("Output Tokens", justify="right", style="green")
    table.add_column("Recorded At", style="dim")

    for ev in events:
        table.add_row(
            ev.get("story_id") or "—",
            ev.get("phase") or "—",
            str(ev.get("output_tokens") or "—"),
            (ev.get("recorded_at") or "")[:19],
        )

    console.print(table)


@telemetry_app.command("backfill")
def backfill_tokens(
    repo: Annotated[
        str | None,
        typer.Option("--repo", "-r", help="Filter by repo slug (e.g. raise-commons)"),
    ] = None,
    since: Annotated[
        str | None,
        typer.Option(
            "--since", help="Only sessions on or after this date (YYYY-MM-DD)"
        ),
    ] = None,
    emit: Annotated[
        bool,
        typer.Option(
            "--emit",
            help="Actually send events to raise-server (default: preview only)",
        ),
    ] = False,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Max sessions to process", min=1, max=10000),
    ] = 5000,
) -> None:
    """Backfill token usage from CC JSONL conversation history.

    Scans ~/.claude/projects/ for JSONL files, extracts full token
    usage (input, output, cache_read, cache_write, model), and optionally
    emits token_usage_daily events to raise-server.

    Run without --emit first to preview what would be sent.

    Examples:
        $ rai telemetry backfill
        $ rai telemetry backfill --repo raise-commons --since 2026-01-01
        $ rai telemetry backfill --repo raise-commons --emit
    """
    from raise_cli.telemetry.backfill import scan_cc_sessions

    console.print("[dim]Scanning ~/.claude/projects/ for CC sessions...[/dim]")
    entries = scan_cc_sessions(repo_filter=repo, since=since)

    if not entries:
        console.print("[yellow]No sessions found.[/yellow]")
        raise typer.Exit(0)

    entries = entries[:limit]

    # Aggregate stats for preview
    repos: dict[str, int] = {}
    dates: list[str] = []
    total_output = 0
    total_cache_read = 0
    total_cache_write = 0
    total_input = 0
    with_cache = 0

    for e in entries:
        repos[e.repo_slug] = repos.get(e.repo_slug, 0) + 1
        dates.append(e.date)
        total_output += e.totals.output_tokens
        total_cache_read += e.totals.cache_read
        total_cache_write += e.totals.cache_write
        total_input += e.totals.input_tokens
        if e.totals.cache_read > 0 or e.totals.cache_write > 0:
            with_cache += 1

    date_range = f"{min(dates)} → {max(dates)}" if dates else "—"

    summary = Table(title="Backfill Preview")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", justify="right")
    summary.add_row("Sessions found", str(len(entries)))
    summary.add_row("Date range", date_range)
    summary.add_row("Sessions with cache data", f"{with_cache}/{len(entries)}")
    summary.add_row("Total output tokens", f"{total_output:,}")
    summary.add_row("Total cache read", f"{total_cache_read:,}")
    summary.add_row("Total cache write", f"{total_cache_write:,}")
    summary.add_row("Total input tokens", f"{total_input:,}")
    console.print(summary)

    repo_table = Table(title="By Repository")
    repo_table.add_column("Repo", style="cyan")
    repo_table.add_column("Sessions", justify="right")
    for rname, count in sorted(repos.items(), key=lambda x: -x[1]):
        repo_table.add_row(rname, str(count))
    console.print(repo_table)

    if not emit:
        console.print(
            "\n[dim]Preview only. Add [bold]--emit[/bold] to send events to raise-server.[/dim]"
        )
        return

    client = _get_client()
    if client is None:
        console.print(
            "[yellow]⚠[/yellow] RAISE_SERVER_URL or RAISE_API_KEY not set — "
            "cannot emit events."
        )
        raise typer.Exit(1)

    from raise_cli.telemetry.session_tokens import build_token_usage_daily_event

    sent = 0
    errors = 0
    with client:
        for entry in entries:
            event = build_token_usage_daily_event(
                entry.totals,
                session_id=entry.session_id,
                date=entry.date,
                repo_slug=entry.repo_slug,
            )
            try:
                resp = client.post(
                    "/api/v1/agent/events",
                    json=event.model_dump(),
                )
                if resp.status_code in (200, 201, 409):
                    sent += 1
                else:
                    errors += 1
            except Exception:  # noqa: BLE001
                errors += 1

    console.print(f"\n[green]✓[/green] Sent {sent} events ({errors} errors)")


def _emit_events(
    client: httpx.Client,
    events: list[object],
) -> tuple[int, int, int]:
    """POST events to server, returning (sent, dupes, errors)."""
    sent = 0
    dupes = 0
    errors = 0
    with client:
        for event in events:
            try:
                resp = client.post(
                    "/api/v1/agent/events",
                    json=event.model_dump(),  # type: ignore[union-attr]
                )
                if resp.status_code in (200, 201):
                    sent += 1
                elif resp.status_code == 409:
                    dupes += 1
                else:
                    errors += 1
            except Exception:  # noqa: BLE001
                errors += 1
    return sent, dupes, errors


@telemetry_app.command("replay")
def replay_command(
    repo: Annotated[
        str | None,
        typer.Option("--repo", "-r", help="Filter by repo slug (e.g. raise-commons)"),
    ] = None,
    since: Annotated[
        str | None,
        typer.Option(
            "--since", help="Only sessions on or after this date (YYYY-MM-DD)"
        ),
    ] = None,
    emit: Annotated[
        bool,
        typer.Option(
            "--emit",
            help="Actually send events to raise-server (default: preview only)",
        ),
    ] = False,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Max sessions to process", min=1, max=10000),
    ] = 5000,
) -> None:
    """Replay enriched per-skill telemetry from CC session history.

    Scans ~/.claude/projects/ for JSONL files, runs scan_single_session()
    on each, and emits one token_usage_daily event per skill per session.
    Idempotent: re-running produces 0 new events (server dedup via event_id).

    Examples:
        $ rai telemetry replay
        $ rai telemetry replay --repo raise-commons --since 2026-06-01
        $ rai telemetry replay --emit
    """
    from pathlib import Path

    from raise_cli.telemetry.backfill import scan_cc_sessions
    from raise_cli.telemetry.cost_report import scan_single_session
    from raise_cli.telemetry.session_tokens import build_replay_events

    console.print("[dim]Scanning ~/.claude/projects/ for CC sessions...[/dim]")
    entries = scan_cc_sessions(repo_filter=repo, since=since)

    if not entries:
        console.print("[yellow]No sessions found.[/yellow]")
        raise typer.Exit(0)

    entries = entries[:limit]

    all_events = []
    unique_skills: set[str] = set()
    unique_categories: set[str] = set()

    for entry in entries:
        report = scan_single_session(Path(entry.jsonl_path))
        if not report.skills:
            continue
        events = build_replay_events(
            report,
            session_id=entry.session_id,
            date=entry.date,
            repo_slug=entry.repo_slug,
        )
        all_events.extend(events)
        for s in report.skills:
            unique_skills.add(s.skill)
            unique_categories.add(s.category)

    summary = Table(title="Replay Preview")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", justify="right")
    summary.add_row("Sessions scanned", str(len(entries)))
    summary.add_row("Events to emit", str(len(all_events)))
    summary.add_row("Unique skills", str(len(unique_skills)))
    summary.add_row("Unique categories", str(len(unique_categories)))
    console.print(summary)

    if not emit:
        console.print(
            "\n[dim]Preview only. Add [bold]--emit[/bold] to send events to raise-server.[/dim]"
        )
        return

    client = _get_client()
    if client is None:
        console.print(
            "[yellow]⚠[/yellow] RAISE_SERVER_URL or RAISE_API_KEY not set — "
            "cannot emit events."
        )
        raise typer.Exit(1)

    sent, dupes, errors = _emit_events(client, all_events)
    console.print(f"\n[green]✓[/green] Sent {sent} new, {dupes} dupes, {errors} errors")


@telemetry_app.command("backfill-report")
def backfill_report(
    since: Annotated[
        str | None,
        typer.Option("--since", help="Start date YYYY-MM-DD"),
    ] = None,
    until: Annotated[
        str | None,
        typer.Option("--until", help="End date YYYY-MM-DD (exclusive)"),
    ] = None,
    repo: Annotated[
        str | None,
        typer.Option("--repo", "-r", help="Filter by repo slug"),
    ] = None,
    emit: Annotated[
        bool,
        typer.Option(
            "--emit",
            help="Send enriched report to raise-server (default: preview only)",
        ),
    ] = False,
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human | json"),
    ] = "human",
) -> None:
    """Enriched cost report backfill — phases, skills, rubber-stamp baseline.

    Runs the full cost_report scanner over CC JSONL history and optionally
    sends the enriched snapshot to raise-server as a token_usage_daily event.

    Examples:
        $ rai telemetry backfill-report --since 2026-06-01
        $ rai telemetry backfill-report --since 2026-06-01 --emit
        $ rai telemetry backfill-report --since 2026-06-01 -f json
    """
    import json as json_mod

    from raise_cli.telemetry.backfill import build_enriched_report

    console.print("[dim]Building enriched cost report from CC sessions...[/dim]")
    payload = build_enriched_report(repo_filter=repo, since=since, until=until)

    if output_format == "json":
        print(json_mod.dumps(payload, indent=2, default=str))
        return

    summary = Table(title="Enriched Backfill Report")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", justify="right")
    summary.add_row("Total cost USD", f"${payload['total_cost_usd']:,.2f}")
    summary.add_row("Stories completed", str(payload["stories_completed"]))
    summary.add_row(
        "Cost/story",
        f"${payload['cost_per_story']:,.2f}" if payload["cost_per_story"] else "—",
    )
    summary.add_row("Models", str(len(payload["models"])))
    summary.add_row("Skills tracked", str(len(payload["skills"])))
    summary.add_row("Phases tracked", str(len(payload["phases"])))
    summary.add_row("HITL approvals", str(payload["approvals_total"]))
    summary.add_row("Approvals with edits", str(payload["approvals_with_edits"]))
    rate = payload["rubber_stamp_rate"]
    summary.add_row("Rubber-stamp rate", f"{rate:.1%}" if rate is not None else "—")
    console.print(summary)

    if payload["phases"]:
        pt = Table(title="Costo por fase")
        pt.add_column("Fase", style="cyan")
        pt.add_column("Msgs", justify="right")
        pt.add_column("USD", justify="right", style="green")
        for p in payload["phases"]:
            pt.add_row(p["phase"], str(p["messages"]), f"${p['cost_usd']:,.2f}")
        console.print(pt)

    if payload["categories"]:
        ct = Table(title="Categorías lean")
        ct.add_column("Categoría", style="cyan")
        ct.add_column("USD", justify="right", style="green")
        for name, usd in sorted(payload["categories"].items(), key=lambda kv: -kv[1]):
            ct.add_row(name, f"${usd:,.2f}")
        console.print(ct)

    if not emit:
        console.print(
            "\n[dim]Preview only. Add [bold]--emit[/bold] to send to raise-server.[/dim]"
        )
        return

    client = _get_client()
    if client is None:
        console.print("[yellow]⚠[/yellow] RAISE_SERVER_URL or RAISE_API_KEY not set.")
        raise typer.Exit(1)

    from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

    event_id = make_event_id(
        event_type="token_usage_daily",
        work_item_ref="cost_report_snapshot",
        iso_timestamp=since or "all",
        source_id=repo or "all",
    )
    event = AgentEventCreate(
        event_type="token_usage_daily",
        payload=payload,
        work_item_ref="cost_report_snapshot",
        event_id=event_id,
    )

    try:
        with client:
            resp = client.post("/api/v1/agent/events", json=event.model_dump())
        if resp.status_code in (200, 201, 409):
            console.print("[green]✓[/green] Enriched report sent to raise-server")
        else:
            console.print(
                f"[red]Error:[/red] server returned {resp.status_code}: {resp.text}"
            )
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


def _build_signals_query(
    type_: str | None,
    source: str | None,
    limit: int,
    since: str | None,
    *,
    project_id: str | None = None,
) -> tuple[str, list[object]]:
    """Build parameterized SELECT for signals table."""
    clauses: list[str] = []
    params: list[object] = []
    if project_id is not None:
        clauses.append("project_id = ?")
        params.append(project_id)
    if type_:
        clauses.append("type = ?")
        params.append(type_)
    if source:
        clauses.append("source = ?")
        params.append(source)
    if since:
        clauses.append("timestamp >= ?")
        params.append(since)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT timestamp, type, source, session_id, output_tokens FROM signals{where} ORDER BY id DESC LIMIT ?"  # noqa: S608  # nosec B608
    params.append(limit)
    return sql, params


@telemetry_app.command("query")
def query_signals(
    db: Annotated[
        str | None,
        typer.Option("--db", help="Path to raise.db (default: project DB)"),
    ] = None,
    type_: Annotated[
        str | None,
        typer.Option("--type", "-t", help="Filter by signal type"),
    ] = None,
    source: Annotated[
        str | None,
        typer.Option("--source", "-s", help="Filter by source (e.g. claude_code)"),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Max rows", min=1, max=500),
    ] = 20,
    since: Annotated[
        str | None,
        typer.Option(
            "--since", help="ISO 8601 datetime — only signals after this time"
        ),
    ] = None,
    all_projects: Annotated[
        bool,
        typer.Option(
            "--all-projects",
            help="Show signals from all projects instead of only the current project",
        ),
    ] = False,
) -> None:
    """Query local SQLite signals table.

    Reads the project raise.db directly (no server required).

    Examples:
        $ rai telemetry query
        $ rai telemetry query --type work_lifecycle --limit 5
        $ rai telemetry query --source claude_code
        $ rai telemetry query --since 2026-05-04T00:00:00Z
    """
    import sqlite3
    from pathlib import Path

    if db:
        db_path = Path(db)
        if not db_path.exists():
            console.print(f"[red]Error:[/red] DB not found: {db_path}")
            raise typer.Exit(1)
        conn = sqlite3.connect(str(db_path))
    else:
        from raise_cli.storage.connection import get_project_db

        try:
            conn = get_project_db(Path.cwd())
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error:[/red] Could not open project DB — {exc}")
            raise typer.Exit(1) from exc

    from raise_cli.storage.connection import get_project_id
    from raise_cli.storage.schema import create_all

    create_all(conn)

    sql, params = _build_signals_query(
        type_,
        source,
        limit,
        since,
        project_id=None if all_projects else get_project_id(Path.cwd()),
    )
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        console.print("[dim](no signals found)[/dim]")
        return

    table = Table(title=f"Signals (showing {len(rows)})")
    table.add_column("Timestamp", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Source", style="magenta")
    table.add_column("Session", style="dim")
    table.add_column("Tokens", style="green", justify="right")

    for row in rows:
        table.add_row(
            (row[0] or "")[:19],
            row[1] or "—",
            row[2] or "—",
            (row[3] or "")[:16],
            str(row[4]) if row[4] is not None else "—",
        )

    console.print(table)


@telemetry_app.command("attribute")
def attribute_command(
    input_file: Annotated[
        str,
        typer.Option("--input", "-i", help="Path to CC sessions baseline JSON"),
    ],
    output: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Write attributed JSON to this path"),
    ] = None,
    report: Annotated[
        bool,
        typer.Option("--report", "-r", help="Print attribution report table"),
    ] = False,
    db: Annotated[
        str | None,
        typer.Option("--db", help="Path to raise.db for session_records lookup"),
    ] = None,
    repo: Annotated[
        str | None,
        typer.Option("--repo", help="Git repo path for temporal heuristic"),
    ] = None,
) -> None:
    """Attribute CC sessions to epics using cascading heuristics.

    Processes sessions without epic assignment and infers the epic
    from branch names, session_records, or temporal git correlation.

    Examples:
        $ rai telemetry attribute --input cc-sessions-baseline.json --report
        $ rai telemetry attribute -i baseline.json -o attributed.json
    """
    import json
    from pathlib import Path

    from raise_cli.telemetry.attribution import (
        attribute_sessions,
        attribution_report,
    )

    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[red]Error:[/red] File not found: {input_path}")
        raise typer.Exit(1)

    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    sessions = data.get("sessions", data) if isinstance(data, dict) else data

    from raise_cli.storage.connection import get_project_db_path

    db_path = Path(db) if db else get_project_db_path()
    repo_path = Path(repo) if repo else Path.cwd()

    results = attribute_sessions(
        sessions,
        db_path=db_path if db_path.exists() else None,
        repo_path=repo_path if repo_path.exists() else None,
    )

    if output:
        out_data = [
            {
                "cc_session_id": r.cc_session_id,
                "epic_id": r.epic_id,
                "method": r.method,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "output_tokens": r.output_tokens,
            }
            for r in results
        ]
        out_path = Path(output)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        console.print(f"[green]✓[/green] Written to {out_path}")

    if report or not output:
        rep = attribution_report(results)
        table = Table(title=f"Attribution Report ({rep['total_sessions']} sessions)")
        table.add_column("Method", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Tokens", justify="right", style="green")

        for method in ("branch_parse", "session_record", "temporal", "unresolved"):
            count = rep["by_method"].get(method, 0)
            tokens = rep["tokens_by_method"].get(method, 0)
            token_str = (
                f"{tokens / 1_000_000:.1f}M" if tokens >= 1_000_000 else f"{tokens:,}"
            )
            table.add_row(method, str(count), token_str)

        console.print(table)
        console.print(
            f"\n[bold]Attribution rate:[/bold] {rep['attribution_rate']}% "
            f"({rep['attributed']}/{rep['total_sessions']})"
        )


def _emit_cost_kpi_signal(
    emit_kpi: bool,
    base_dir: Path,
    db_path: Path | None,
    since: str | None,
    until: str | None,
    since_dt: datetime | None,
    until_dt: datetime | None,
) -> None:
    """Build story attribution and emit a cost_kpi lifecycle signal (best-effort)."""
    if not emit_kpi:
        return
    from contextlib import suppress

    from raise_cli.telemetry.cost_report import CostReport, build_story_attribution
    from raise_cli.telemetry.emit_work import emit_cost_kpi

    attrs = build_story_attribution(
        base_dir, db_path=db_path, since=since_dt, until=until_dt
    )
    report = CostReport(story_attributions=attrs)
    with suppress(Exception):
        emit_cost_kpi(
            avg_cost=report.avg_cost_per_story,
            median_cost=report.median_cost_per_story,
            p95_cost=report.p95_cost_per_story,
            stories_count=len([a for a in attrs if not a.overhead]),
            since=since,
            until=until,
        )


def _print_story_reports(
    base_dir: Path,
    db_path: Path | None,
    since_dt: datetime | None,
    until_dt: datetime | None,
    by_story: bool,
    by_week: bool,
    by_epic: bool,
    by_trend: bool,
) -> None:
    """Build story attributions and dispatch to requested report printers."""
    from raise_cli.telemetry.cost_report import (
        build_epic_report,
        build_story_attribution,
        build_trend_report,
        build_weekly_report,
    )

    attributions = build_story_attribution(
        base_dir,
        db_path=db_path,
        since=since_dt,
        until=until_dt,
    )
    if by_story:
        _print_story_table(attributions)
    if by_week:
        _print_weekly_table(build_weekly_report(attributions))
    if by_epic:
        _print_epic_table(build_epic_report(attributions))
    if by_trend:
        _print_trend(build_trend_report(attributions))


@telemetry_app.command("cost")
def cost_command(
    since: Annotated[
        str | None,
        typer.Option("--since", help="Start date YYYY-MM-DD (local midnight)"),
    ] = None,
    until: Annotated[
        str | None,
        typer.Option("--until", help="End date YYYY-MM-DD (exclusive, local midnight)"),
    ] = None,
    by_skill: Annotated[
        bool,
        typer.Option("--by-skill", help="Show per-skill attribution table"),
    ] = False,
    by_category: Annotated[
        bool,
        typer.Option("--by-category", help="Show lean category rollup"),
    ] = False,
    by_phase: Annotated[
        bool,
        typer.Option("--by-phase", help="Show cost per pipeline phase"),
    ] = False,
    by_task: Annotated[
        bool,
        typer.Option(
            "--by-task", help="Show per-task breakdown (raise_task_complete boundaries)"
        ),
    ] = False,
    by_story: Annotated[
        bool,
        typer.Option(
            "--by-story", help="Show per-story attributable cost (via SQLite signals)"
        ),
    ] = False,
    by_week: Annotated[
        bool,
        typer.Option("--by-week", help="Show cost grouped by ISO week"),
    ] = False,
    by_epic: Annotated[
        bool,
        typer.Option("--by-epic", help="Show cost grouped by inferred epic"),
    ] = False,
    by_trend: Annotated[
        bool,
        typer.Option(
            "--trend",
            help="Show 8-week trend + sparkline (offline; see also: telemetry trend)",
        ),
    ] = False,
    db: Annotated[
        str | None,
        typer.Option(
            "--db", help="Path to raise.db (default: auto-detect)", hidden=True
        ),
    ] = None,
    baseline: Annotated[
        str | None,
        typer.Option("--baseline", help="Baseline JSON to compare against"),
    ] = None,
    compare: Annotated[
        bool,
        typer.Option("--compare", help="Print deltas vs --baseline"),
    ] = False,
    save_baseline_path: Annotated[
        str | None,
        typer.Option("--save-baseline", help="Persist this report as baseline JSON"),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human | json"),
    ] = "human",
    projects_dir: Annotated[
        str | None,
        typer.Option(
            "--projects-dir",
            help="CC projects directory (default: ~/.claude/projects)",
            hidden=True,
        ),
    ] = None,
    emit_kpi: Annotated[
        bool,
        typer.Option(
            "--emit-kpi",
            help="Emit cost_kpi signal to SQLite/server after computing story attribution stats",
        ),
    ] = False,
) -> None:
    """API-equivalent cost report over local CC session logs (offline, read-only)."""
    from datetime import datetime
    from pathlib import Path

    from raise_cli.telemetry import cost_report as cr

    def _parse_date(value: str | None) -> datetime | None:
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value).astimezone()
        except ValueError as exc:
            console.print(f"[red]Invalid date: {value}[/red]")
            raise typer.Exit(1) from exc

    base_dir = (
        Path(projects_dir) if projects_dir else Path.home() / ".claude" / "projects"
    )
    report = cr.build_report(
        projects_dir=base_dir, since=_parse_date(since), until=_parse_date(until)
    )

    if save_baseline_path:
        cr.save_baseline(report, Path(save_baseline_path))
        console.print(f"Baseline saved: {save_baseline_path}")

    if compare:
        if not baseline:
            console.print("[red]--compare requires --baseline[/red]")
            raise typer.Exit(1)
        comparison = cr.compare_reports(cr.load_baseline(Path(baseline)), report)
        _print_comparison(comparison)
        return

    if output_format == "json":
        from raise_cli.telemetry.cost_report import build_story_attribution

        db_path_resolved = Path(db) if db else None
        attributions = build_story_attribution(
            base_dir,
            db_path=db_path_resolved,
            since=_parse_date(since),
            until=_parse_date(until),
        )
        report = report.model_copy(update={"story_attributions": attributions})
        _emit_cost_kpi_signal(
            emit_kpi=emit_kpi,
            base_dir=base_dir,
            db_path=db_path_resolved,
            since=since,
            until=until,
            since_dt=_parse_date(since),
            until_dt=_parse_date(until),
        )
        print(report.model_dump_json(indent=2))
        return

    _emit_cost_kpi_signal(
        emit_kpi=emit_kpi,
        base_dir=base_dir,
        db_path=Path(db) if db else None,
        since=since,
        until=until,
        since_dt=_parse_date(since),
        until_dt=_parse_date(until),
    )

    _print_cost_report(
        report,
        by_skill=by_skill,
        by_category=by_category,
        by_phase=by_phase,
        by_task=by_task,
    )

    if by_story or by_week or by_epic or by_trend:
        db_path = Path(db) if db else None
        _print_story_reports(
            base_dir=base_dir,
            db_path=db_path,
            since_dt=_parse_date(since),
            until_dt=_parse_date(until),
            by_story=by_story,
            by_week=by_week,
            by_epic=by_epic,
            by_trend=by_trend,
        )


@telemetry_app.command("snapshot")
def snapshot_command(
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human | json"),
    ] = "human",
    project: Annotated[
        str | None,
        typer.Option("--project", "-p", help="Project path (default: CWD)"),
    ] = None,
) -> None:
    """In-progress cost + quality snapshot of the active local session.

    Scans the most recent CC JSONL for this project (no session close
    required) and reports accumulated cost + trajectory-quality signals.
    `--format json` emits a single object for the fleet dispatcher (S8741.4).
    """
    import json as _json
    from pathlib import Path

    from raise_cli.telemetry.cost_report import scan_single_session
    from raise_cli.telemetry.session_tokens import find_current_session_jsonl

    project_path = Path(project) if project else Path.cwd()
    jsonl = find_current_session_jsonl(project_path)

    if jsonl is None:
        if output_format == "json":
            print(
                _json.dumps(
                    {
                        "session_id": None,
                        "total_cost_usd": 0.0,
                        "tool_fail_ratio": None,
                        "edit_revert_files": 0,
                        "session_duration_minutes": None,
                        "max_gate_fail_streak": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                    }
                )
            )
        else:
            console.print(
                "[yellow]No active session found[/yellow] "
                "(no CC JSONL for this project)"
            )
        return

    report = scan_single_session(jsonl)
    session_id = report.session_id or jsonl.stem
    input_tokens = sum(m.input_tokens for m in report.models)
    output_tokens = sum(m.output_tokens for m in report.models)

    if output_format == "json":
        print(
            _json.dumps(
                {
                    "session_id": session_id,
                    "total_cost_usd": report.total_cost_usd,
                    "tool_fail_ratio": report.tool_fail_ratio,
                    "edit_revert_files": report.edit_revert_files,
                    "session_duration_minutes": report.session_duration_minutes,
                    "max_gate_fail_streak": report.max_gate_fail_streak,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                }
            )
        )
        return

    console.print(f"Session [cyan]{session_id}[/cyan]  (in progress)")
    console.print(
        f"Cost: [green]${report.total_cost_usd:,.2f}[/green]   "
        f"Tokens: {input_tokens:,} in / {output_tokens:,} out"
    )
    _print_quality_signals(report)


def _resolve_run(run_id: str | None) -> dict[str, Any]:
    """Find a pipeline run by ID or return the first active/complete run."""
    import asyncio

    from raise_cli.pipeline.run_store import get_run_store

    async def _find() -> dict[str, Any] | None:
        store = get_run_store()
        if run_id:
            return await store.load(run_id)
        runs = await store.list_runs()
        for r in runs:
            if r.get("status") in ("started", "complete"):
                return r
        return None

    run = asyncio.run(_find())
    if run is None:
        console.print("[yellow]No active pipeline run found.[/yellow]")
        raise typer.Exit(1)
    return run


def _resolve_phase(
    phases: list[dict[str, Any]], phase_name: str | None
) -> dict[str, Any]:
    """Find a phase by name or return the last completed phase."""
    if phase_name:
        for p in phases:
            if p["id"] == phase_name:
                return p
        console.print(f"[red]Phase '{phase_name}' not found in run.[/red]")
        raise typer.Exit(1)

    for p in reversed(phases):
        if p.get("status") == "done":
            return p
    console.print("[yellow]No completed phase found.[/yellow]")
    raise typer.Exit(1)


@telemetry_app.command("phase-report")
def phase_report_command(
    run_id: Annotated[
        str | None,
        typer.Option("--run", "-r", help="Pipeline run ID (default: active run)"),
    ] = None,
    phase_name: Annotated[
        str | None,
        typer.Option("--phase", "-p", help="Phase name (default: last completed)"),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human | json"),
    ] = "human",
    project: Annotated[
        str | None,
        typer.Option("--project", help="Project path (default: CWD)"),
    ] = None,
) -> None:
    """Show telemetry report for a single pipeline phase.

    Computes cost + quality signals for one recently completed phase
    using the AgentTelemetryAdapter (ADR-062). Useful for debugging
    and validating phase-level observability.

    Examples:
        $ rai telemetry phase-report
        $ rai telemetry phase-report --phase implement
        $ rai telemetry phase-report --run abc123 --format json
    """
    import json as _json
    from datetime import datetime as dt
    from pathlib import Path

    from raise_cli.telemetry.phase_report import (
        format_phase_summary,
        phase_finish_report,
    )

    project_path = Path(project) if project else Path.cwd()
    run = _resolve_run(run_id)

    phases: list[dict[str, Any]] = run.get("phases") or run.get("pipeline", {}).get(
        "phases", []
    )  # type: ignore[assignment]
    if not phases:
        console.print("[yellow]No phases in run.[/yellow]")
        raise typer.Exit(1)

    target = _resolve_phase(phases, phase_name)

    started_at = (
        dt.fromisoformat(target["started_at"]) if target.get("started_at") else None
    )
    completed_at = (
        dt.fromisoformat(target["completed_at"]) if target.get("completed_at") else None
    )

    report = phase_finish_report(
        project_path,
        phase=target["id"],
        pipeline_name=str(run.get("pipeline_name", "unknown")),
        run_id=str(run.get("id", "")),
        started_at=started_at,
        completed_at=completed_at,
        issue=str(run.get("issue_id")) if run.get("issue_id") else None,
    )

    if output_format == "json":
        print(_json.dumps(report.model_dump(), indent=2, default=str))
        return

    from rich.markup import escape

    console.print(
        f"\n[bold]Phase Report:[/bold] {escape(format_phase_summary(report))}"
    )
    if report.by_model:
        model_table = Table(title="Por modelo")
        model_table.add_column("Modelo", style="cyan")
        model_table.add_column("Calls", justify="right")
        model_table.add_column("Input", justify="right")
        model_table.add_column("Output", justify="right")
        model_table.add_column("USD", justify="right", style="green")
        for m in report.by_model:
            model_table.add_row(
                m.model,
                str(m.calls),
                f"{m.input_tokens:,}",
                f"{m.output_tokens:,}",
                f"${m.cost_usd:.2f}",
            )
        console.print(model_table)
    console.print(f"[dim]boundary: {report.boundary_source}[/dim]")


def _dominant_model(models: dict[str, float]) -> str:
    """Return the model with >50% cost share, or 'mixed' / 'N/A'."""
    total = sum(models.values())
    if total == 0:
        return "N/A"
    for model, cost in sorted(models.items(), key=lambda kv: -kv[1]):
        if cost / total > 0.50:
            return model
    return "mixed"


def _print_skill_table(report: CostReport) -> None:
    """Render per-skill attribution table."""
    st = Table(title="Atribución por skill")
    st.add_column("Skill", style="cyan")
    st.add_column("Runs", justify="right")
    st.add_column("Msgs", justify="right")
    st.add_column("Msgs/run", justify="right")
    st.add_column("USD", justify="right", style="green")
    st.add_column("USD/run", justify="right")
    st.add_column("Categoría")
    st.add_column("Modelo", style="dim")
    for s in report.skills:
        runs = s.runs or 1
        st.add_row(
            s.skill,
            str(s.runs),
            str(s.messages),
            f"{s.messages / runs:.1f}",
            f"${s.cost_usd:,.2f}",
            f"${s.cost_usd / runs:,.2f}",
            s.category,
            _dominant_model(s.models),
        )
    console.print(st)


def _print_task_section(report: CostReport) -> None:
    """Render per-task breakdown table and msgs/task headline (omitted when no tasks)."""
    if report.tasks:
        tt = Table(title="Por tarea (raise_task_complete boundaries)")
        tt.add_column("Tarea", style="cyan")
        tt.add_column("Work ID", style="dim")
        tt.add_column("Msgs", justify="right")
        tt.add_column("USD", justify="right", style="green")
        for t in report.tasks:
            tt.add_row(t.task, t.work_id, str(t.messages), f"${t.cost_usd:,.4f}")
        console.print(tt)

    if report.setup_overhead_msgs:
        console.print(
            f"[dim]setup overhead:[/dim] {report.setup_overhead_msgs} msgs"
            f" (${report.setup_overhead_cost_usd:,.4f}, once/story — excluded from msgs/task)"
        )

    if report.msgs_per_task is not None:
        glyph = (
            "[green]ok[/green]"
            if report.msgs_per_task <= _MSGS_PER_TASK_TARGET
            else "[red]>[/red]"
        )
        console.print(
            f"[bold]msgs/task:[/bold] {report.msgs_per_task:.1f} {glyph}"
            f" (target ≤{_MSGS_PER_TASK_TARGET:.0f}, marginal boundary-to-boundary)"
        )


def _print_quality_signals(report: CostReport) -> None:
    parts: list[str] = []
    if report.tool_fail_ratio is not None:
        parts.append(f"tool_fail {report.tool_fail_ratio:.1%}")
    if report.edit_revert_files > 0:
        parts.append(f"edit_reverts {report.edit_revert_files} files")
    if report.session_duration_minutes is not None:
        parts.append(f"duration {report.session_duration_minutes:.0f}min")
    if report.max_gate_fail_streak > 0:
        parts.append(f"gate_streak {report.max_gate_fail_streak}")
    if parts:
        console.print(f"[bold]Quality:[/bold] {' | '.join(parts)}")


_MSGS_PER_TASK_TARGET = 2.0


def _sparkline(values: list[float]) -> str:
    """Map a list of floats to Unicode block sparkline characters.

    Delegates to cost_report.build_sparkline for consistency.
    Exported here so tests can import from telemetry module.
    S9463.5/T6.
    """
    from raise_cli.telemetry.cost_report import build_sparkline

    return build_sparkline(values)


def _print_weekly_table(rows: list[WeeklyRow]) -> None:
    """Render ISO-week cost table. S9463.5/T4 — AC5."""
    if not rows:
        console.print("[dim]Sin datos de costo por semana.[/dim]")
        return
    t = Table(title="Costo por semana ISO")
    t.add_column("Semana", style="cyan")
    t.add_column("Stories", justify="right")
    t.add_column("USD", justify="right", style="green")
    t.add_column("$/story", justify="right")
    for r in rows:
        t.add_row(
            r.iso_week,
            str(r.n_stories),
            f"${r.total_usd:,.2f}",
            f"${r.avg_usd:,.2f}",
        )
    console.print(t)


def _print_epic_table(rows: list[EpicRow]) -> None:
    """Render epic cost table. S9463.5/T5 — AC6."""
    if not rows:
        console.print("[dim]Sin datos de costo por épica.[/dim]")
        return
    t = Table(title="Costo por épica")
    t.add_column("Épica", style="cyan")
    t.add_column("Stories", justify="right")
    t.add_column("USD Total", justify="right", style="green")
    t.add_column("USD prom", justify="right")
    for r in rows:
        t.add_row(
            r.epic,
            str(r.n_stories),
            f"${r.total_usd:,.2f}",
            f"${r.avg_usd:,.2f}",
        )
    console.print(t)


def _print_trend(report: TrendReport) -> None:
    """Render 8-week trend summary. S9463.5/T6 — AC7."""
    t = Table(title="Tendencia de costo (8 semanas ISO)")
    t.add_column("Semana", style="cyan")
    t.add_column("USD", justify="right", style="green")
    for week, cost in zip(report.weeks, report.costs, strict=True):
        t.add_row(week, f"${cost:,.2f}")
    console.print(t)
    # Recompute sparkline from costs (report.sparkline pre-computed at build time)
    console.print(f"Sparkline: {_sparkline(report.costs)}")
    if report.prior_week is not None and report.delta_pct is not None:
        sign = "+" if report.delta_pct >= 0 else ""
        console.print(
            f"{report.current_week} ${report.current_usd:,.2f} vs "
            f"{report.prior_week} ${report.prior_usd:,.2f}  "
            f"(Δ {sign}{report.delta_pct:.1f}%)"
        )


def _print_story_table(attributions: list[StoryAttribution]) -> None:
    """Render per-story cost attribution table.

    S9463.5/T2: overhead entries (overhead=True) are rendered dimmed at the bottom;
    the summary line counts and totals only real story entries.
    """
    st = Table(title="Costo por story (atribuible)")
    st.add_column("Story", style="cyan")
    st.add_column("Session", style="dim")
    st.add_column("USD attr", justify="right", style="green")
    st.add_column("Cobertura")
    for a in attributions:
        cost_str = f"${a.cost_usd:,.2f}" if a.cost_usd is not None else "N/A"
        if a.overhead:
            cov_str = "[dim](overhead)[/dim]"
        else:
            cov_str = "✓ atribuido" if a.jsonl_found else "sin JSONL"
        session_short = (
            a.session_id[:12] + "..." if len(a.session_id) > 12 else a.session_id
        )
        st.add_row(a.work_id, session_short, cost_str, cov_str)
    console.print(st)
    real_attrs = [a for a in attributions if not a.overhead]
    n_found = sum(1 for a in real_attrs if a.jsonl_found)
    total = sum(a.cost_usd for a in real_attrs if a.cost_usd is not None)
    console.print(
        f"{n_found}/{len(real_attrs)} stories con costo atribuible"
        f" | Atribuido: ${total:,.2f}"
    )


def _print_cost_report(
    report: CostReport,
    *,
    by_skill: bool,
    by_category: bool,
    by_phase: bool = False,
    by_task: bool = False,
) -> None:
    table = Table(title="Costo API-equivalente por modelo")
    table.add_column("Modelo", style="cyan")
    table.add_column("Calls", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cache W", justify="right")
    table.add_column("Cache R", justify="right")
    table.add_column("USD", justify="right", style="green")
    for m in report.models:
        table.add_row(
            m.model,
            f"{m.calls:,}",
            f"{m.input_tokens:,}",
            f"{m.output_tokens:,}",
            f"{m.cache_write:,}",
            f"{m.cache_read:,}",
            f"${m.cost_usd:,.2f}",
        )
    console.print(table)
    headline = f"[bold]TOTAL ${report.total_cost_usd:,.2f}[/bold]"
    headline += f"  |  stories cerradas: {report.stories_completed}"
    if report.cost_per_story is not None:
        headline += f"  |  $/story: ${report.cost_per_story:,.2f}"
    console.print(headline)

    if by_skill and report.skills:
        _print_skill_table(report)

    if by_category and report.categories:
        ct = Table(title="Rollup lean")
        ct.add_column("Categoría", style="cyan")
        ct.add_column("USD", justify="right", style="green")
        for name, usd in sorted(report.categories.items(), key=lambda kv: -kv[1]):
            ct.add_row(name, f"${usd:,.2f}")
        console.print(ct)

    if by_phase and report.phases:
        pt = Table(title="Costo por fase de pipeline")
        pt.add_column("Fase", style="cyan")
        pt.add_column("Msgs", justify="right")
        pt.add_column("USD", justify="right", style="green")
        pt.add_column("% total", justify="right")
        for p in report.phases:
            pct = (
                (p.cost_usd / report.total_cost_usd * 100)
                if report.total_cost_usd
                else 0
            )
            pt.add_row(p.phase, str(p.messages), f"${p.cost_usd:,.2f}", f"{pct:.1f}%")
        console.print(pt)

    if by_task:
        _print_task_section(report)

    if report.approvals_total > 0:
        rate_str = (
            f"{report.rubber_stamp_rate:.1%}"
            if report.rubber_stamp_rate is not None
            else "n/a"
        )
        console.print(
            f"[bold]HITL:[/bold] {report.approvals_total} aprobaciones, "
            f"{report.approvals_with_edits} con edición post-approve "
            f"(rubber-stamp rate: {rate_str})"
        )

    _print_quality_signals(report)


def _print_comparison(comparison: ReportComparison) -> None:
    def _fmt(delta_pct: float | None) -> str:
        return f"{delta_pct:+.1f}%" if delta_pct is not None else "n/a"

    table = Table(title="Comparación vs baseline")
    table.add_column("Métrica", style="cyan")
    table.add_column("Antes", justify="right")
    table.add_column("Después", justify="right")
    table.add_column("Δ", justify="right", style="green")
    table.add_row(
        "total",
        f"${comparison.total.before:,.2f}",
        f"${comparison.total.after:,.2f}",
        _fmt(comparison.total.pct),
    )
    for d in comparison.categories:
        table.add_row(d.name, f"${d.before:,.2f}", f"${d.after:,.2f}", _fmt(d.pct))
    console.print(table)

    skills = Table(title="Skills (USD)")
    skills.add_column("Skill", style="cyan")
    skills.add_column("Antes", justify="right")
    skills.add_column("Después", justify="right")
    skills.add_column("Δ", justify="right", style="green")
    for d in comparison.skills:
        skills.add_row(d.name, f"${d.before:,.2f}", f"${d.after:,.2f}", _fmt(d.pct))
    console.print(skills)


def _print_szz_table(results: list[IntroducerResult]) -> None:
    """Render SZZ introducer report table (parallel to _print_story_table)."""
    if not results:
        console.print("[dim]0 introducers — net-new code[/dim]")
        return

    table = Table(title=f"SZZ Introducer Report ({len(results)} introducer(s))")
    table.add_column("fix_commit", style="cyan")
    table.add_column("introducer", style="magenta")
    table.add_column("authoring_condition", style="dim")
    table.add_column("conf", justify="right")

    for r in results:
        conf_str = f"{r.confidence:.2f}"
        if r.confidence < 0.5:
            conf_str += " low"
        table.add_row(
            r.fix_commit[:8],
            r.introducer_commit[:8],
            r.authoring_condition,
            conf_str,
        )
    console.print(table)


def _szz_run_single(
    attributor: SzzAttributor, fix_commit: str, repo_path: Path
) -> list[IntroducerResult]:
    """Run SZZ attribution for one fix commit; raises typer.Exit(1) on error."""
    try:
        return attributor.attribute_introducer(
            fix_commit=fix_commit, repo_path=repo_path
        )
    except Exception as exc:  # noqa: BLE001
        console.print(
            f"[red]Error:[/red] fix commit '{fix_commit}' not found in repo — {exc}"
        )
        raise typer.Exit(1) from exc


def _szz_run_batch(
    attributor: SzzAttributor, input_file: str, repo_path: Path
) -> list[IntroducerResult]:
    """Run SZZ attribution over a JSON batch file; skips unfound commits."""
    import json as _json
    from pathlib import Path

    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[red]Error:[/red] input file not found: {input_path}")
        raise typer.Exit(1)
    with input_path.open(encoding="utf-8") as f:
        pairs = _json.load(f)
    results: list[IntroducerResult] = []
    for pair in pairs:
        fc = pair.get("fix_commit", "")
        if not fc:
            continue
        try:
            results.extend(
                attributor.attribute_introducer(fix_commit=fc, repo_path=repo_path)
            )
        except Exception:  # noqa: BLE001
            console.print(f"[yellow]Warning:[/yellow] skipping {fc} — not found")
    return results


@telemetry_app.command("szz")
def szz_command(
    fix_commit: Annotated[
        str | None,
        typer.Option("--fix-commit", help="SHA of the fix commit to attribute"),
    ] = None,
    input_file: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="JSON file with [{bug_key, fix_commit}] pairs for batch mode",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output", "-o", help="Write IntroducerResult[] JSON to this path"
        ),
    ] = None,
    repo: Annotated[
        str,
        typer.Option("--repo", "-r", help="Git repo path (default: current directory)"),
    ] = ".",
    report: Annotated[
        bool,
        typer.Option("--report", help="Print introducer report table"),
    ] = False,
) -> None:
    """Identify introducer commits for one or more fix commits (SZZ algorithm).

    Given a fix commit, runs git-blame over the modified lines to find the
    commit(s) that introduced the bug. Resolves the authoring condition
    (ai_session_unresolved vs human_or_pre_trailer) from the Claude-Session:
    trailer on each introducer commit.

    Examples:
        $ rai telemetry szz --fix-commit abc1234 --repo . --report
        $ rai telemetry szz --input fixes.json --output introducers.json
    """
    import json as _json
    from pathlib import Path

    from raise_cli.telemetry.szz import SzzAttributor

    repo_path = Path(repo)
    if not repo_path.exists():
        console.print(f"[red]Error:[/red] repo path not found: {repo_path}")
        raise typer.Exit(1)

    attributor = SzzAttributor()

    if fix_commit and not input_file:
        all_results = _szz_run_single(attributor, fix_commit, repo_path)
    elif input_file:
        all_results = _szz_run_batch(attributor, input_file, repo_path)
    else:
        console.print("[red]Error:[/red] provide --fix-commit or --input")
        raise typer.Exit(1)

    if not all_results:
        console.print("[dim]0 introducers — net-new code[/dim]")
        return

    if output:
        out_data = [r.model_dump() for r in all_results]
        out_path = Path(output)
        with out_path.open("w", encoding="utf-8") as f:
            _json.dump(out_data, f, indent=2)
        console.print(f"[green]✓[/green] Written to {out_path}")

    if report or not output:
        _print_szz_table(all_results)


@telemetry_app.command("trend")
def trend(
    stories: Annotated[
        str,
        typer.Option(
            "--stories",
            "-s",
            help="Comma-separated Jira keys (e.g. RAISE-8742,RAISE-8762)",
        ),
    ],
) -> None:
    """Show cost trend for stories vs $36 baseline. Exit 0 if all ≤$18.

    Calls GET /api/telemetry/story-cost?story=KEY for each key and renders
    a table with cost_usd, delta% vs baseline ($36), and ≤$18 mission flag.

    Exit code: 0 = all stories ≤$18 (mission objective [0] met),
               1 = any story exceeds $18 or server not configured.

    Examples:
        $ rai telemetry trend --stories RAISE-8742
        $ rai telemetry trend --stories RAISE-8742,RAISE-8762
    """
    client = _get_client()
    if client is None:
        console.print(
            "[yellow]⚠[/yellow] RAISE_SERVER_URL or RAISE_API_KEY not set — "
            "cannot query telemetry."
        )
        raise typer.Exit(1)

    keys = [k.strip() for k in stories.split(",") if k.strip()]
    rows: list[tuple[str, float | None]] = []
    any_over_target = False

    with client:
        for key in keys:
            try:
                resp = client.get("/api/telemetry/story-cost", params={"story": key})
                if resp.status_code == 404:
                    rows.append((key, None))
                    any_over_target = (
                        True  # missing data = mission objective not confirmed
                    )
                    continue
                resp.raise_for_status()
                data = resp.json()
                cost = float(data["total_cost_usd"])
                rows.append((key, cost))
                if cost > _TARGET_USD:
                    any_over_target = True
            except httpx.HTTPStatusError:
                rows.append((key, None))
                any_over_target = True

    table = Table(title=f"Cost Trend vs ${_BASELINE_USD:.0f} Baseline")
    table.add_column("Story", style="cyan")
    table.add_column("cost_usd", justify="right", style="green")
    table.add_column("vs_baseline", justify="right")
    table.add_column("delta%", justify="right")
    table.add_column(f"≤${_TARGET_USD:.0f}?", justify="center")

    for key, cost in rows:
        if cost is None:
            table.add_row(key, "—", f"${_BASELINE_USD:.0f}", "—", "—")
        else:
            delta_pct = (cost - _BASELINE_USD) / _BASELINE_USD * 100
            passes = cost <= _TARGET_USD
            flag = "[green]✓[/green]" if passes else "[red]✗[/red]"
            table.add_row(
                key,
                f"${cost:.2f}",
                f"${_BASELINE_USD:.0f}",
                f"{delta_pct:+.0f}%",
                flag,
            )

    console.print(table)
    raise typer.Exit(1 if any_over_target else 0)


def _print_attribution_table(
    records: list[AttributionRecord],
) -> None:
    """Render defect attribution report table (parallel to _print_szz_table)."""
    if not records:
        console.print("[dim]0 attribution records[/dim]")
        return

    table = Table(title=f"Defect Attribution ({len(records)} record(s))")
    table.add_column("fix_commit", style="cyan")
    table.add_column("introducer", style="magenta")
    table.add_column("authoring_condition", style="dim")
    table.add_column("reason", style="dim")
    table.add_column("conf", justify="right")
    table.add_column("bug_key", style="green")

    for r in records:
        conf_str = f"{r.confidence:.2f}"
        if r.confidence < 0.5:
            conf_str += " low"
        table.add_row(
            r.fix_commit[:8],
            r.introducer_commit[:8],
            r.authoring_condition,
            r.resolution_reason[:30],
            conf_str,
            r.bug_key or "—",
        )
    console.print(table)

    # Summary breakdown
    from collections import Counter

    counts = Counter(r.authoring_condition for r in records)
    summary = Table(title="Breakdown by authoring_condition")
    summary.add_column("condition", style="cyan")
    summary.add_column("count", justify="right")
    summary.add_column("%", justify="right")
    total = len(records)
    # RAISE-11898: 'ai_unknown' reemplaza el falso 'human' para commits sin
    # trailer (repo 100%-IA). 'human' se mantiene por si hubiera evidencia
    # positiva de autoría humana (no instrumentada hoy).
    for condition in ("interactive", "batch_agent", "ai_unknown", "human", "unknown"):
        count = counts.get(condition, 0)
        pct = f"{count / total * 100:.0f}%" if total else "—"
        summary.add_row(condition, str(count), pct)
    console.print(summary)


def _attribution_dataset_mode(project_root: Path) -> None:
    """Print all persisted attribution records (--dataset mode)."""
    from raise_cli.telemetry.defect_attribution import get_attribution_dataset

    records = get_attribution_dataset(project_root=project_root)
    if not records:
        console.print("[dim]No attribution records in DB.[/dim]")
        return
    _print_attribution_table(records)


def _attribution_run_mode(
    *,
    fix_commit: str | None,
    input_file: str | None,
    repo: str,
    persist: bool,
    report: bool,
) -> None:
    """Run SZZ → resolve → optionally persist attribution records."""
    from pathlib import Path

    from raise_cli.telemetry.defect_attribution import (
        persist_attribution,
        resolve_authoring_condition,
    )
    from raise_cli.telemetry.szz import SzzAttributor

    repo_path = Path(repo)
    if not repo_path.exists():
        console.print(f"[red]Error:[/red] repo path not found: {repo_path}")
        raise typer.Exit(1)

    attributor = SzzAttributor()

    if fix_commit and not input_file:
        all_results = _szz_run_single(attributor, fix_commit, repo_path)
    elif input_file:
        all_results = _szz_run_batch(attributor, input_file, repo_path)
    else:
        console.print("[red]Error:[/red] provide --fix-commit, --input, or --dataset")
        raise typer.Exit(1)

    if not all_results:
        console.print("[dim]0 introducers — net-new code[/dim]")
        return

    attribution_records = [
        resolve_authoring_condition(r, repo_path=repo_path) for r in all_results
    ]

    if persist:
        count = persist_attribution(attribution_records, repo_path)
        console.print(f"[green]✓[/green] Persisted {count} attribution record(s)")

    if report or not persist:
        _print_attribution_table(attribution_records)


@telemetry_app.command("attribute-defect")
def attribute_defect_command(
    fix_commit: Annotated[
        str | None,
        typer.Option("--fix-commit", help="SHA of the fix commit to attribute"),
    ] = None,
    input_file: Annotated[
        str | None,
        typer.Option(
            "--input",
            "-i",
            help="JSON file with [{fix_commit}] or IntroducerResult[] for batch mode",
        ),
    ] = None,
    repo: Annotated[
        str,
        typer.Option("--repo", "-r", help="Git repo path (default: current directory)"),
    ] = ".",
    persist: Annotated[
        bool,
        typer.Option("--persist", help="Persist records to project SQLite DB"),
    ] = False,
    report: Annotated[
        bool,
        typer.Option("--report", help="Print attribution report table"),
    ] = False,
    dataset: Annotated[
        bool,
        typer.Option(
            "--dataset", help="Query and display all persisted attribution records"
        ),
    ] = False,
) -> None:
    """Resolve authoring condition for bug introducer commits.

    Takes fix commits, runs SZZ to find introducers, resolves each introducer's
    authoring_condition (interactive | batch_agent | ai_unknown | unknown) via CC
    JSONL log lookup, and optionally persists AttributionRecords to project SQLite.
    Nota (RAISE-11898): commits sin trailer → 'ai_unknown' (IA pre-instrumentación),
    no 'human' — raise-commons es 100%-IA.

    Examples:
        $ rai telemetry attribute-defect --fix-commit abc1234 --repo . --report
        $ rai telemetry attribute-defect --input fixes.json --persist --report
        $ rai telemetry attribute-defect --dataset --report
    """
    from pathlib import Path

    if dataset:
        _attribution_dataset_mode(Path(repo))
        return

    _attribution_run_mode(
        fix_commit=fix_commit,
        input_file=input_file,
        repo=repo,
        persist=persist,
        report=report,
    )
