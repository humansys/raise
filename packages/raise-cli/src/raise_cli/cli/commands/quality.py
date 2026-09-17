"""CLI commands: rai quality — Reliability/Quality lens (RAISE-11187).

``rai quality defect-rate`` parses the commit stream and reports defect/rework
rates. The integration branch defaults to ``.raise/manifest.yaml``
``branches.development`` (org-calibrated), not a hardcoded ``main``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.quality.classifier import defect_rate, parse_commits, resolve_branch
from raise_cli.quality.enrichment import adapter_field_lookup, enrich_commits
from raise_cli.quality.models import (
    CommitRecord,
    DefectRateReport,
    EnrichedDefectReport,
    FieldGroupReport,
    GroupBy,
    WindowMetrics,
)

console = Console()
quality_app = typer.Typer(help="Reliability/Quality lens over the commit stream.")

_VALID_DIMENSIONS: set[GroupBy] = {"origin", "type"}


def _parse_by(raw: str | None) -> list[GroupBy]:
    """Parse the ``--by origin,type`` flag into validated dimensions."""
    if not raw:
        return []
    dims: list[GroupBy] = []
    for token in raw.split(","):
        name = token.strip().lower()
        if not name:
            continue
        if name not in _VALID_DIMENSIONS:
            raise typer.BadParameter(
                f"unknown --by dimension '{name}' (valid: origin, type)"
            )
        dim: GroupBy = "origin" if name == "origin" else "type"
        if dim not in dims:
            dims.append(dim)
    return dims


@quality_app.command("defect-rate")
def defect_rate_command(
    since: Annotated[
        int,
        typer.Option("--since", help="Look back this many days"),
    ] = 90,
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            help="Integration branch (default: manifest branches.development)",
        ),
    ] = None,
    format: Annotated[
        Literal["human", "json"],
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
    by: Annotated[
        str | None,
        typer.Option(
            "--by",
            help=(
                "Group by Jira bug taxonomy: 'origin', 'type', or "
                "'origin,type' (adds the Origin×Type cross). Looks up each "
                "RAISE ticket via the backlog adapter — network-bound."
            ),
        ),
    ] = None,
    adapter: Annotated[
        str | None,
        typer.Option("--adapter", "-a", help="Backlog adapter for --by lookup"),
    ] = None,
    project: Annotated[
        Path,
        typer.Option(
            "--project", "-p", help="Project root (default: current directory)"
        ),
    ] = Path("."),
) -> None:
    """Report defect/rework rates from the commit stream.

    With ``--by``, each fix/bug commit's RAISE ticket is joined to its Jira bug
    taxonomy (Origin, Bug Type) via the backlog adapter, and the defect rate is
    grouped by that taxonomy. Tickets that are not Bug-type or lack the field
    are counted as 'uncategorized' (coverage is reported).
    """
    repo_path = project.resolve()
    resolved_branch, warning = resolve_branch(repo_path, branch)
    if warning and format == "human":
        console.print(f"[yellow]warning:[/yellow] {warning}")

    commits = parse_commits(repo_path, since=since, branch=resolved_branch)

    dimensions = _parse_by(by)
    if dimensions:
        _run_enriched(
            commits,
            branch=resolved_branch,
            since=since,
            dimensions=dimensions,
            adapter=adapter,
            output=format,
        )
        return

    report = defect_rate(commits, branch=resolved_branch, since_days=since)
    if format == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        _render_human(report)


def _run_enriched(
    commits: list[CommitRecord],
    *,
    branch: str,
    since: int,
    dimensions: list[GroupBy],
    adapter: str | None,
    output: Literal["human", "json"],
) -> None:
    """Resolve the backlog adapter, enrich the stream, and render the report."""
    from raise_cli.adapters.resolve import resolve_pm_adapter

    pm = resolve_pm_adapter(adapter)
    lookup = adapter_field_lookup(pm)
    report = enrich_commits(
        commits,
        lookup,
        branch=branch,
        since_days=since,
        by=dimensions,
    )
    if output == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        _render_enriched(report)


def _render_human(report: DefectRateReport) -> None:
    o = report.overall
    console.print(
        f"\n[bold]Commit-stream defect/rework[/bold]  "
        f"branch=[cyan]{report.branch}[/cyan]  window={report.since_days}d"
    )
    if o.total == 0:
        console.print("[dim]No commits in range — near-empty signal.[/dim]\n")
        return

    console.print(
        f"  total={o.total}  "
        f"fix={o.fix_count} ({o.fix_rate * 100:.1f}%)  "
        f"bug={o.bug_count} ({o.bug_rate * 100:.1f}%)"
    )
    console.print(
        f"  rework_in_process={o.rework_count} ({o.rework_rate * 100:.1f}%)  "
        f"escaped(candidate)={o.escaped_count} ({o.escaped_rate * 100:.1f}%)"
    )

    if report.windows:
        table = Table(title="By window")
        table.add_column("Window")
        table.add_column("Total", justify="right")
        table.add_column("Fix%", justify="right")
        table.add_column("Bug%", justify="right")
        table.add_column("Rework%", justify="right")
        table.add_column("Escaped%", justify="right")
        for w in report.windows:
            _add_window_row(table, w)
        console.print(table)
    console.print(
        "[dim]Heuristic: 'escaped' = fix/bug with no in-process "
        "review/CI/gate marker — a candidate, not a confirmed escape.[/dim]\n"
    )


def _add_window_row(table: Table, w: WindowMetrics) -> None:
    table.add_row(
        w.label,
        str(w.total),
        f"{w.fix_rate * 100:.1f}",
        f"{w.bug_rate * 100:.1f}",
        f"{w.rework_rate * 100:.1f}",
        f"{w.escaped_rate * 100:.1f}",
    )


def _render_enriched(report: EnrichedDefectReport) -> None:
    console.print(
        f"\n[bold]Defect rate by Jira taxonomy[/bold]  "
        f"branch=[cyan]{report.branch}[/cyan]  window={report.since_days}d"
    )
    if report.total_fix_bug == 0:
        console.print("[dim]No fix/bug commits in range — near-empty signal.[/dim]\n")
        return
    console.print(f"  fix/bug commits={report.total_fix_bug}")

    if report.by_origin is not None:
        _render_group(report.by_origin, "Origin (cf[13269])")
    if report.by_type is not None:
        _render_group(report.by_type, "Bug Type (cf[13267])")
    if report.cross:
        _render_cross(report)
    console.print(
        "[dim]Only Bug-type tickets carry these fields; non-Bug / missing "
        "→ 'uncategorized'. Lookup via backlog adapter.[/dim]\n"
    )


def _render_group(group: FieldGroupReport, title: str) -> None:
    uncategorized = group.total_fix_bug - group.categorized
    table = Table(title=f"{title}  (coverage {group.coverage * 100:.1f}%)")
    table.add_column("Value")
    table.add_column("fix/bug", justify="right")
    table.add_column("% of fix/bug", justify="right")
    for bucket in group.buckets:
        share = bucket.fix_bug_count / group.total_fix_bug * 100
        table.add_row(bucket.value, str(bucket.fix_bug_count), f"{share:.1f}")
    if uncategorized:
        share = uncategorized / group.total_fix_bug * 100
        table.add_row("uncategorized", str(uncategorized), f"{share:.1f}")
    console.print(table)


def _render_cross(report: EnrichedDefectReport) -> None:
    table = Table(title="Origin × Bug Type")
    table.add_column("Origin")
    table.add_column("Bug Type")
    table.add_column("fix/bug", justify="right")
    for cell in report.cross:
        table.add_row(cell.origin, cell.type, str(cell.fix_bug_count))
    console.print(table)
