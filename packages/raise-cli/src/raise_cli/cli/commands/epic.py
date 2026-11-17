"""CLI commands for epic operations — RAISE-19191 (D8).

``rai epic story create`` delegates to the same sync logic as
``raise_epic_story_create`` in mcp_tools_backlog, making story creation
available from the CLI without an MCP server.
"""

from __future__ import annotations

import json
from datetime import UTC
from pathlib import Path
from typing import Annotated

import typer

epic_app = typer.Typer(
    name="epic",
    help="Epic lifecycle commands.",
    no_args_is_help=True,
)

_story_app = typer.Typer(
    name="story",
    help="Story sub-commands under an epic.",
    no_args_is_help=True,
)
epic_app.add_typer(_story_app, name="story")


@epic_app.callback()
def epic_callback() -> None:
    """Epic lifecycle commands."""


def _run_epic_story_create(
    summary: str,
    project: str,
    epic_jira_key: str,
    cwd: str = "",
) -> str:
    """Sync wrapper — extracted from raise_epic_story_create._run()."""
    from datetime import datetime
    from uuid import uuid4

    from raise_cli.adapters.models import IssueSpec
    from raise_cli.adapters.resolve import resolve_pm_adapter
    from raise_cli.storage.work_items import WorkItem, WorkItemStore, slugify_local_key

    project_root = Path(cwd) if cwd else Path.cwd()
    store = WorkItemStore(project_root)

    existing = store.find_by_parent_and_summary(epic_jira_key, summary)
    if existing is not None:
        return json.dumps(
            {
                "status": "already_registered",
                "jira_key": existing.jira_key,
                "work_item_id": existing.id,
            }
        )

    try:
        pm = resolve_pm_adapter(None, project_root=project_root)
        spec = IssueSpec(summary=summary, issue_type="Story", parent=epic_jira_key)
        ref = pm.create_issue(project, spec)
        jira_key: str = ref.key
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"status": "error", "reason": str(exc)})

    pre_existing = store.get_by_jira_key(jira_key)
    if pre_existing is not None:
        return json.dumps(
            {
                "status": "already_registered",
                "jira_key": pre_existing.jira_key,
                "work_item_id": pre_existing.id,
            }
        )

    now = datetime.now(UTC).isoformat()
    local_key = slugify_local_key(store, "story", summary)
    wi = WorkItem(
        id=str(uuid4()),
        type="story",
        local_key=local_key,
        jira_key=jira_key,
        parent_jira_key=epic_jira_key,
        summary=summary,
        status="todo",
        created_at=now,
        updated_at=now,
    )
    try:
        created = store.create(wi)
    except Exception as exc:  # noqa: BLE001
        return json.dumps(
            {
                "status": "error",
                "reason": "work_items_insert_failed",
                "jira_key": jira_key,
                "reconcile": f"rai backlog get {jira_key}",
                "detail": str(exc),
            }
        )

    return json.dumps(
        {
            "status": "ok",
            "jira_key": created.jira_key,
            "work_item_id": created.id,
            "local_key": created.local_key,
        }
    )


@_story_app.command("create")
def epic_story_create_cmd(
    summary: Annotated[str, typer.Argument(help="Story summary (title).")],
    epic: Annotated[str, typer.Option("--epic", "-e", help="Parent epic Jira key.")],
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Jira project key (e.g. RAISE)."),
    ],
    cwd: Annotated[
        str,
        typer.Option(
            "--cwd", help="Working directory for work_items DB (default: cwd)."
        ),
    ] = "",
) -> None:
    """Create a Jira story and register it in work_items atomically."""
    raw = _run_epic_story_create(
        summary=summary,
        project=project,
        epic_jira_key=epic,
        cwd=cwd,
    )
    result = json.loads(raw)
    status = result.get("status", "error")
    if status in ("ok", "already_registered"):
        jira_key = result.get("jira_key", "")
        typer.echo(f"Story: {jira_key} ({status})")
    else:
        reason = result.get("reason", "unknown error")
        typer.echo(f"Error: {reason}", err=True)
        raise typer.Exit(1)
