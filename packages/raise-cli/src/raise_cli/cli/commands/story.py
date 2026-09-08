"""Composite story bookend commands — S7884.3 (ADR-084 CLI fallback).

``rai story open`` / ``rai story close`` return the same JSON schema as
the raise_story_open / raise_story_close_full MCP tools, so agents
without MCP get identical data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

story_app = typer.Typer(
    name="story",
    help="Composite story bookends (open/close) — MCP tool fallback.",
    no_args_is_help=True,
)

_ICONS = {"ok": "✓", "warn": "⚠", "blocked": "✗"}


def _print_human(report_status: str, checks: list[object]) -> None:
    from rich.console import Console

    console = Console()
    for check in checks:
        name = getattr(check, "name", "?")
        status = getattr(check, "status", "?")
        data = getattr(check, "data", {})
        console.print(f"{_ICONS.get(status, '?')} {name}: {status}")
        if status != "ok":
            console.print(f"  {data}")
    console.print(f"\n[bold]Estado: {report_status}[/bold]")


@story_app.command("open")
def story_open(
    story_id: Annotated[str, typer.Option("--story-id", help="e.g. S7884.3")],
    slug: Annotated[str, typer.Option("--slug", help="Branch slug")],
    epic_dir: Annotated[
        str,
        typer.Option("--epic-dir", help="Epic dir under work/epics/ ('' standalone)"),
    ] = "",
    jira_key: Annotated[str, typer.Option("--jira-key")] = "",
    story_file: Annotated[
        str, typer.Option("--story-file", help="Path to story.md content")
    ] = "",
    scope_file: Annotated[
        str, typer.Option("--scope-file", help="Path to scope.md content")
    ] = "",
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="human | json")
    ] = "human",
) -> None:
    """Composite story open: branch + docs + scope commit + transition + bind.

    CLI fallback for the raise_story_open MCP tool (ADR-084) — same schema.
    """
    from raise_cli.work_item.open_service import build_story_open_report

    project_path = Path(project).resolve()
    story_content = (
        Path(story_file).read_text(encoding="utf-8") if story_file else f"# {story_id}"
    )
    scope_content = (
        Path(scope_file).read_text(encoding="utf-8") if scope_file else "## In Scope"
    )
    report = build_story_open_report(
        project_path=project_path,
        cwd=project_path,
        story_id=story_id,
        slug=slug,
        jira_key=jira_key,
        epic_dir=epic_dir,
        story_content=story_content,
        scope_content=scope_content,
    )
    if output_format == "json":
        print(report.model_dump_json())
        return
    _print_human(
        report.status,
        [
            report.epic,
            report.worktree,
            report.branch,
            report.docs,
            report.commit,
            report.backlog,
            report.bind,
        ],
    )


@story_app.command("sync-dev-branch")
def story_sync_dev_branch(
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    dev_branch: Annotated[
        str,
        typer.Option("--dev-branch", help="Override; defaults to manifest/env"),
    ] = "",
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="human | json")
    ] = "human",
) -> None:
    """Fetch + ff-only merge the dev branch onto HEAD — skipped inside a worktree.

    RAISE-15825, Regla 2: once a worktree exists, nothing auto-touches its
    HEAD — regardless of what its ``merge_target`` is, registered or not.
    This command consults the same worktree-detection path the story-open
    service uses (registered binding, or a physical linked-worktree
    fallback) and skips the sync entirely whenever inside one. Outside any
    worktree it fetches + ff-only merges against the global dev branch —
    unchanged, still correct. Replaces the raw ``git fetch``/``git merge
    --ff-only`` bash that used to run unconditionally as Step 1 of the
    rai-story-start skill.
    """
    from raise_cli.project_config import resolve_dev_branch
    from raise_cli.work_item.open_service import (
        detect_worktree,
        sync_dev_branch,
    )

    project_path = Path(project).resolve()
    branch = dev_branch or resolve_dev_branch(project_path)
    worktree = detect_worktree(project_path, project_path)
    result = sync_dev_branch(
        project_path, branch, in_worktree=bool(worktree.data.get("in_worktree"))
    )
    if output_format == "json":
        print(result.model_dump_json())
    else:
        _print_human(result.status, [worktree, result])
    if result.status == "blocked":
        raise typer.Exit(code=1)


@story_app.command("close")
def story_close(
    story_id: Annotated[str, typer.Option("--story-id", help="e.g. S7884.3")] = "",
    slug: Annotated[str, typer.Option("--slug")] = "",
    epic_dir: Annotated[str, typer.Option("--epic-dir")] = "",
    jira_key: Annotated[str, typer.Option("--jira-key")] = "",
    merge_summary: Annotated[str, typer.Option("--summary")] = "",
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    output_format: Annotated[str, typer.Option("--format", "-f")] = "human",
) -> None:
    """[DEPRECATED] CLI fallback for story close — ADR-143 B2.

    This command is deprecated (ADR-143 B2, RAISE-15351). It bypasses the pipeline
    engine and emits no lifecycle signals, creating an observability gap (ADR-084).

    Use the pipeline engine instead:
        rai pipeline start story --issue-id <JIRA-KEY>
    """
    _ = story_id, slug, epic_dir, jira_key, merge_summary, project, output_format
    typer.echo(
        "rai story close is deprecated (ADR-143 B2, RAISE-15351).\n"
        "Use the pipeline engine instead:\n"
        "  rai pipeline start story --issue-id <JIRA-KEY>",
        err=True,
    )
    raise typer.Exit(code=1)
