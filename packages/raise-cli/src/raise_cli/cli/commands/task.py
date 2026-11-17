"""CLI commands for task operations — RAISE-19189 (D6).

``rai task complete`` delegates to ``build_task_complete_report`` — the same
service used by the ``raise_task_complete`` MCP tool — making the inner task
loop available from the CLI without an MCP server.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

task_app = typer.Typer(
    name="task",
    help="Task lifecycle commands (inner loop: complete).",
    no_args_is_help=True,
)

console = Console()


@task_app.callback()
def task_callback() -> None:
    """Task lifecycle commands (inner loop: complete)."""


@task_app.command("complete")
def task_complete_cmd(
    work_id: Annotated[
        str, typer.Argument(help="Story/bugfix identifier, e.g. S8370.1.")
    ],
    branch: Annotated[
        str,
        typer.Option("--branch", "-b", help="Expected current git branch."),
    ],
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Full commit message."),
    ],
    files: Annotated[
        str,
        typer.Option(
            "--files",
            help="Space-separated paths to stage. Empty = git add -u.",
        ),
    ] = "",
    gate_scope: Annotated[
        str,
        typer.Option(
            "--gate-scope", help="Scope path for gate-tests (empty = full suite)."
        ),
    ] = "",
    cwd: Annotated[
        str,
        typer.Option(
            "--cwd", help="Working directory for git operations (default: cwd)."
        ),
    ] = "",
) -> None:
    """Complete a task: run gates, assert branch, stage, commit, emit signal."""
    from raise_cli.task.complete_service import build_task_complete_report

    project_path = Path(cwd) if cwd else Path.cwd()
    report = build_task_complete_report(
        project_path=project_path,
        cwd=project_path,
        work_id=work_id,
        task_name=message,
        expected_branch=branch,
        commit_message=message,
        gate_scope=gate_scope,
        files=files,
    )

    status = report.status
    for step in (
        report.gates,
        report.branch,
        report.stage,
        report.commit,
        report.signal,
    ):
        icon = {
            "ok": "[green]✓[/green]",
            "warn": "[yellow]⚠[/yellow]",
            "blocked": "[red]✗[/red]",
        }.get(step.status, "?")
        console.print(f"{icon} {step.name}: {step.status}")
        if step.data:
            console.print(f"  {step.data}")

    if status != "ok":
        gates_data = report.gates.data or {}
        blocking = gates_data.get("blocking_gate", "")
        remediation = gates_data.get("remediation", "")
        if blocking:
            typer.echo(f"Blocking gate: {blocking}", err=True)
        if remediation:
            typer.echo(f"Remediation: {remediation}", err=True)
        raise typer.Exit(1)
