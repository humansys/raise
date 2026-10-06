"""CLI command for advisory impact analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from raise_cli.impact.rendering import render_report_human, render_report_json
from raise_cli.impact.report import ImpactReportError, build_impact_report

impact_app = typer.Typer(
    name="impact",
    help="Analyze changed files and recommend advisory validation gates",
    no_args_is_help=True,
)

console = Console()


@impact_app.callback(invoke_without_command=True)
def impact_command(
    from_ref: Annotated[
        str,
        typer.Option(
            "--from",
            help="Base Git ref for impact analysis",
        ),
    ],
    to_ref: Annotated[
        str | None,
        typer.Option(
            "--to",
            help="Head Git ref for impact analysis (default: HEAD)",
        ),
    ] = None,
    format: Annotated[
        Literal["human", "json"],
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
    project: Annotated[
        Path,
        typer.Option(
            "--project",
            "-p",
            help="Project root (default: current directory)",
        ),
    ] = Path("."),
    no_graph: Annotated[
        bool,
        typer.Option(
            "--no-graph",
            help="Disable graph enrichment (accepted for forward compatibility)",
        ),
    ] = False,
) -> None:
    """Produce an advisory impact report for a Git diff."""
    _ = no_graph
    try:
        report = build_impact_report(
            base_ref=from_ref,
            head_ref=to_ref,
            project_root=project.resolve(),
        )
    except ImpactReportError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if format == "json":
        typer.echo(render_report_json(report))
    else:
        console.print(render_report_human(report), markup=False)
