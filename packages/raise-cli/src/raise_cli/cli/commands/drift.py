"""Drift CLI group — rai drift check <module_path>."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.discovery.check import (
    DriftCheckConfig,
    DriftCheckReport,
    run_drift_check,
)
from raise_cli.discovery.corpus import HotspotRanking, scan_corpus
from raise_cli.discovery.metric import (
    DriftBaselineRecord,
    MetricStore,
    take_baseline,
    take_report,
)
from raise_cli.discovery.thresholds import calibrate_thresholds

drift_app = typer.Typer(
    name="drift",
    help="Drift health checks for codebase modules.",
    no_args_is_help=True,
)


# Stub forces Typer to treat drift_app as a group (single-command apps bypass routing).
@drift_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # type: ignore[reportUnusedFunction]
    pass  # pragma: no cover


console = Console()

_STATUS_STYLE = {
    "ok": "green",
    "warn": "yellow",
    "alert": "red",
    "unavailable": "dim",
}


@drift_app.command("check")
def check_command(
    module_path: Annotated[
        Path,
        typer.Argument(
            help="Module directory or file to analyse (repo-root-relative).",
            exists=True,
            file_okay=True,
            dir_okay=True,
            resolve_path=False,
        ),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json"),
    ] = "human",
) -> None:
    """Run full drift health check on a module.

    Composes structural metrics (I2), temporal slope (I3), clone detection (I4),
    and SAST (I5) into a single report. No LLM required. Budget: <5s warm.

    Examples:
        rai drift check packages/raise-cli/src/raise_cli/discovery/

        rai drift check packages/raise-cli/src/raise_cli/discovery/ --format json
    """
    try:
        report: DriftCheckReport = run_drift_check(module_path, DriftCheckConfig())
    except FileNotFoundError as exc:
        cli_error(
            str(exc),
            hint="Run 'rai graph build' first to create the index",
            exit_code=4,
        )
        return  # unreachable — cli_error raises SystemExit

    if format == "json":
        print(report.model_dump_json(indent=2))
        return

    _print_human(report)


@drift_app.command("scan-corpus")
def scan_corpus_command(
    manifest_path: Annotated[
        Path,
        typer.Argument(
            help="Path to corpus manifest YAML (schema_version='1').",
            exists=False,  # validated manually to return a consistent exit code
            dir_okay=False,
            resolve_path=False,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Write HotspotRanking JSON to this path (default: stdout).",
        ),
    ] = None,
    top_n: Annotated[
        int,
        typer.Option("--top-n", help="Retain only the N highest-scoring modules."),
    ] = 20,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Calibrate thresholds from the healthy subset, print them, and exit (no scan).",
        ),
    ] = False,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human (default) or json.",
        ),
    ] = "human",
) -> None:
    """Rank modules in a corpus by drift signal violations.

    Loads a YAML corpus manifest declaring target modules and a healthy-ref
    subset, self-hosts thresholds from the healthy subset (Pass 1 per DR-003 §9),
    scores every target, and emits a HotspotRanking (schema_version="1").

    Examples:
        rai drift scan-corpus work/epics/e2161-drift-detection-infra/corpus.yaml

        rai drift scan-corpus corpus.yaml -o .raise/drift/pass1/hotspots.json --top-n 20

        rai drift scan-corpus corpus.yaml --dry-run
    """
    if not manifest_path.exists():
        cli_error(
            f"Manifest not found: {manifest_path}",
            hint="Provide a path to a corpus YAML manifest",
            exit_code=2,
        )
        return  # unreachable

    if dry_run:
        _run_dry_run(manifest_path)
        return

    try:
        ranking = scan_corpus(manifest_path, top_n=top_n)
    except FileNotFoundError as exc:
        cli_error(
            str(exc), hint="Fix the manifest path or remove the entry", exit_code=2
        )
        return  # unreachable
    except ValueError as exc:
        cli_error(str(exc), hint="Check the manifest schema_version", exit_code=2)
        return  # unreachable

    payload = ranking.model_dump_json(indent=2)

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output} ({len(ranking.entries)} entries)")
        return

    if format == "json":
        print(payload)
        return

    _print_ranking_human(ranking)


def _run_dry_run(manifest_path: Path) -> None:
    """Load manifest, calibrate, print thresholds. No scan."""
    from raise_cli.discovery.corpus import _load_manifest  # type: ignore[attr-defined]

    try:
        manifest = _load_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as exc:
        cli_error(str(exc), hint="Check manifest path/schema", exit_code=2)
        return  # unreachable

    cfg, report = calibrate_thresholds(
        manifest.healthy_refs, repo_root=manifest_path.parent
    )

    table = Table(
        title="Calibrated thresholds (dry run)", show_header=True, header_style="bold"
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    for key, value in sorted(report.thresholds.items()):
        table.add_row(key, f"{value}")
    if not report.thresholds:
        table.add_row("(none)", "(no healthy modules contributed)")
    console.print(table)
    console.print(
        f"healthy_n={report.healthy_n}  quantile={report.quantile}  "
        f"excluded={report.excluded or '[]'}"
    )
    # cfg is already embedded in report.thresholds; avoid duplicate output.
    _ = cfg


def _print_ranking_human(ranking: HotspotRanking) -> None:
    table = Table(
        title=f"Pass 1 hotspots — top {len(ranking.entries)} "
        f"(healthy_n={ranking.healthy_n}, q={ranking.quantile})",
        show_header=True,
        header_style="bold",
    )
    table.add_column("#", justify="right")
    table.add_column("Module", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("WARN signals")

    for i, entry in enumerate(ranking.entries, start=1):
        warns = ", ".join(s.name for s in entry.signals if s.status == "warn") or "—"
        score_style = (
            "red"
            if entry.violation_score >= 3
            else "yellow"
            if entry.violation_score > 0
            else "green"
        )
        table.add_row(
            str(i),
            entry.module_id,
            f"[{score_style}]{entry.violation_score}[/{score_style}]",
            warns,
        )

    console.print(table)


def _print_human(report: DriftCheckReport) -> None:
    table = Table(
        title=f"Module: {report.module_id}", show_header=True, header_style="bold"
    )
    table.add_column("Signal", style="bold")
    table.add_column("Status")
    table.add_column("Detail")

    for sig in report.signals:
        style = _STATUS_STYLE.get(sig.status, "")
        table.add_row(sig.name, f"[{style}]{sig.status.upper()}[/{style}]", sig.detail)

    console.print(table)
    console.print(f"Duration: {report.duration_s:.1f}s")


# ---------------------------------------------------------------------------
# Metric commands (S2100.3) — baseline, report, dashboard
# ---------------------------------------------------------------------------

_DEFAULT_STORE = Path(".raise/rai/memory/drift-metric.jsonl")


@drift_app.command("baseline")
def baseline_command(
    store: Annotated[
        Path,
        typer.Option("--store", help="Path to JSONL metric store."),
    ] = _DEFAULT_STORE,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json."),
    ] = "human",
) -> None:
    """Scan all modules and store a drift baseline with P75/P90 thresholds.

    Examples:
        rai drift baseline

        rai drift baseline --format json
    """
    rec = take_baseline(store)

    if format == "json":
        print(rec.model_dump_json(indent=2))
        return

    console.print(
        f"[green]✓ Baseline taken[/green] — {rec.taken_at.strftime('%Y-%m-%dT%H:%M:%S%z')}"
    )
    console.print(f"  Modules scanned: {rec.module_count}")
    console.print(
        f"  P75  WMC={rec.p75.wmc:.0f}  LCOM={rec.p75.lcom:.0f}  fan_out={rec.p75.fan_out:.0f}"
    )
    console.print(
        f"  P90  WMC={rec.p90.wmc:.0f}  LCOM={rec.p90.lcom:.0f}  fan_out={rec.p90.fan_out:.0f}"
    )
    console.print(f"  Stored: {store}")


@drift_app.command("report")
def report_command(
    store: Annotated[
        Path,
        typer.Option("--store", help="Path to JSONL metric store."),
    ] = _DEFAULT_STORE,
    story: Annotated[
        str | None,
        typer.Option("--story", help="Story ID for traceability (e.g. S2100.3)."),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json."),
    ] = "human",
) -> None:
    """Append a drift delta snapshot, comparing current state to the latest baseline.

    Examples:
        rai drift report --story S2100.3

        rai drift report --format json
    """
    try:
        rec = take_report(store, story_id=story)
    except ValueError as exc:
        cli_error(str(exc), hint="Run 'rai drift baseline' first", exit_code=1)
        return  # unreachable

    if format == "json":
        print(rec.model_dump_json(indent=2))
        return

    label = f"story={story}" if story else "no story tag"
    console.print(
        f"[green]✓ Report appended[/green] — {rec.taken_at.strftime('%Y-%m-%dT%H:%M:%S%z')} ({label})"
    )
    hotspots = [m for m in rec.modules if m.violation_score >= 3]
    if hotspots:
        console.print("  [yellow]High-violation modules (≥3 warns):[/yellow]")
        for m in hotspots:
            delta = f" (+{m.delta_wmc})" if m.delta_wmc and m.delta_wmc > 0 else ""
            console.print(
                f"    {m.module_id}  WMC={m.wmc}{delta}  score={m.violation_score}"
            )
    else:
        console.print("  All modules within baseline.")


@drift_app.command("dashboard")
def dashboard_command(
    store: Annotated[
        Path,
        typer.Option("--store", help="Path to JSONL metric store."),
    ] = _DEFAULT_STORE,
) -> None:
    """Display a drift dashboard comparing current metrics to the baseline.

    Examples:
        rai drift dashboard
    """
    records = MetricStore.load(store)
    baseline = MetricStore.latest_baseline(records)
    if baseline is None:
        cli_error(
            f"No baseline found in {store}",
            hint="Run 'rai drift baseline' first",
            exit_code=1,
        )
        return  # unreachable

    reports = [r for r in records if not isinstance(r, DriftBaselineRecord)]
    last_report = reports[-1] if reports else None
    last_story = getattr(last_report, "story_id", None) if last_report else None

    title = f"Drift Dashboard — baseline {baseline.taken_at.strftime('%Y-%m-%d')}"
    if last_story:
        title += f" · last report {last_story}"

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Module", style="bold")
    table.add_column("WMC", justify="right")
    table.add_column("ΔWMC", justify="right")
    table.add_column("LCOM", justify="right")
    table.add_column("Δfan_out", justify="right")
    table.add_column("Score", justify="right")

    source = last_report.modules if last_report else baseline.modules
    for m in source:
        delta_wmc = (
            f"+{m.delta_wmc}"
            if m.delta_wmc and m.delta_wmc > 0
            else (str(m.delta_wmc) if m.delta_wmc is not None else "—")
        )
        delta_fout = (
            f"+{m.delta_fan_out}"
            if m.delta_fan_out and m.delta_fan_out > 0
            else (str(m.delta_fan_out) if m.delta_fan_out is not None else "—")
        )
        score_style = (
            "red"
            if m.violation_score >= 3
            else "yellow"
            if m.violation_score > 0
            else "green"
        )
        table.add_row(
            m.module_id,
            str(m.wmc),
            delta_wmc,
            str(m.lcom),
            delta_fout,
            f"[{score_style}]{m.violation_score}[/{score_style}]",
        )

    console.print(table)
    console.print(
        f"P90 thresholds: WMC={baseline.p90.wmc:.0f}  LCOM={baseline.p90.lcom:.0f}  fan_out={baseline.p90.fan_out:.0f}"
    )
