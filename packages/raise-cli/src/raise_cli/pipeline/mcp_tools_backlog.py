"""Backlog MCP tools — raise_backlog_context, raise_backlog_transition, raise_backlog_create, raise_backlog_update, raise_epic_story_create.

RAISE-2816: Tools are async and use asyncio.to_thread() for blocking adapter
calls so the FastMCP event loop stays responsive. Adapter resolution uses
the domain-level resolve_pm_adapter() which raises AdapterResolutionError
instead of calling sys.exit().
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC
from pathlib import Path
from typing import Any, cast

from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only
from raise_cli.pipeline._mcp_instance import mcp


def _write_outcome_response(ref: Any) -> dict[str, Any]:
    """Build the MCP JSON response for a write based on ``IssueRef.remote_synced``.

    Mirrors ``cli/commands/backlog.py::_report_write_outcome`` (RAISE-12598):
    a caller trusting a bare ``{"status": "ok"}`` cannot tell a landed write
    from one the composite adapter silently queued locally (RAISE-11745).

    - ``True`` or ``None`` (older/unrelated adapters that don't set the
      field) — unchanged ``status: "ok"``.
    - ``False`` with a remote configured (reason != "no_remotes") — the
      false-positive-success failure mode: ``status: "queued"`` with the
      reason, so a caller that only checks for ``"ok"`` sees a different
      value instead of a false positive.
    - ``False`` with no remote configured (reason == "no_remotes") — pure
      local/offline project; queueing is expected, not a failure: still
      ``status: "ok"`` with an informational ``queued`` note.
    """
    remote_synced = getattr(ref, "remote_synced", None)
    if remote_synced is not False:
        return {"status": "ok", "key": ref.key}
    reason = ref.metadata.get("remote_sync_reason", "unknown")
    if reason == "no_remotes":
        return {
            "status": "ok",
            "key": ref.key,
            "note": "queued locally; no remote configured",
        }
    return {
        "status": "queued",
        "key": ref.key,
        "reason": reason,
        "message": (
            f"{ref.key}: queued locally; NOT yet on remote (reason: {reason}) — "
            "run 'rai backlog pending-ops list --dead' or verify manually."
        ),
    }


def _get_adapter(adapter_name: str | None, cwd: str = "") -> Any:
    """Resolve PM adapter via domain resolver."""
    from raise_cli.adapters.resolve import resolve_pm_adapter

    project_root = Path(cwd).resolve() if cwd else None
    resolver = cast("Any", resolve_pm_adapter)
    return resolver(adapter_name, project_root=project_root)


def _resolve_adapter(adapter_name: str | None, cwd: str) -> Any:
    """Resolve adapter with cwd override while preserving legacy monkeypatch shape."""
    if cwd:
        return _get_adapter(adapter_name, cwd)
    return _get_adapter(adapter_name)


def _resolve_issue_type_alias(issue_type: str, adapter: str | None, cwd: str) -> str:
    """Resolve localized issue-type alias (e.g. Historia → Story) via backlog config."""
    try:
        from raise_cli.adapters.backlog_config import load_backlog_config
        from raise_cli.cli.commands._resolve import get_effective_adapter_name

        project_root = Path(cwd).resolve() if cwd else Path.cwd()
        config = load_backlog_config(project_root, get_effective_adapter_name(adapter))
        return config.issue_type_aliases.get(issue_type, issue_type)
    except (FileNotFoundError, KeyError, Exception):  # noqa: BLE001
        return issue_type


@mcp.tool()
async def raise_backlog_context(
    issue_key: str, adapter: str = "jira", cwd: str = ""
) -> str:
    """Get issue details from the backlog for context.

    Args:
        issue_key: Issue key (e.g., "RAISE-1310").
        adapter: Backlog adapter to use (default "jira").
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_backlog_context")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        try:
            pm = _resolve_adapter(adapter or None, cwd)
            detail = pm.get_issue(issue_key)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        content = (
            f"{detail.key}  {detail.status}  {detail.issue_type}\n{detail.summary}"
        )
        if detail.description:
            content += f"\n\n{detail.description}"
        return json.dumps({"status": "ok", "key": issue_key, "content": content})

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_backlog_transition(
    issue_key: str, status: str, adapter: str = "jira", cwd: str = ""
) -> str:
    """Transition a backlog issue to a new status.

    Args:
        issue_key: Issue key (e.g., "RAISE-1438").
        status: Target status (e.g., "In Progress", "Done").
        adapter: Backlog adapter to use (default "jira").
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_backlog_transition")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        try:
            pm = _resolve_adapter(adapter or None, cwd)
            ref = pm.transition_issue(issue_key, status)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        return compact_response(_write_outcome_response(ref))

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_backlog_create(
    summary: str,
    project: str,
    issue_type: str = "Story",
    description: str = "",
    labels: str = "",
    parent: str = "",
    adapter: str = "jira",
    cwd: str = "",
) -> str:
    """Create a new backlog issue.

    Args:
        summary: Issue title.
        project: Project key (e.g., "RAISE").
        issue_type: Issue type (default "Story").
        description: Issue description in markdown.
        labels: Comma-separated labels.
        parent: Parent issue key (for sub-tasks or epic children).
        adapter: Backlog adapter to use (default "jira").
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_backlog_create")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from raise_cli.adapters.models import IssueSpec

        try:
            pm = _resolve_adapter(adapter or None, cwd)
            resolved_type = _resolve_issue_type_alias(issue_type, adapter or None, cwd)
            spec = IssueSpec(
                summary=summary,
                issue_type=resolved_type,
                description=description,
                labels=labels.split(",") if labels else [],
                parent=parent or None,
            )
            ref = pm.create_issue(project, spec)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        return compact_response({"status": "ok", "key": ref.key})

    return await asyncio.to_thread(_run)


def _build_update_fields(
    summary: str,
    labels: str,
    priority: str,
    assignee: str,
    custom_fields: str,
) -> dict[str, Any] | str:
    """Build field dict from MCP params. Returns error JSON string on failure."""
    fields: dict[str, Any] = {}
    if summary:
        fields["summary"] = summary
    if labels:
        fields["labels"] = labels.split(",")
    if priority:
        fields["priority"] = priority
    if assignee:
        fields["assignee"] = assignee
    if custom_fields:
        try:
            parsed = json.loads(custom_fields)
            if isinstance(parsed, dict):
                fields.update(parsed)
        except json.JSONDecodeError as exc:
            return json.dumps(
                {"status": "error", "reason": f"Invalid custom_fields JSON: {exc}"}
            )
    if not fields:
        return json.dumps(
            {"status": "error", "reason": "No fields to update — all parameters empty"}
        )
    return fields


@local_only
async def raise_epic_story_create(
    summary: str,
    project: str,
    epic_jira_key: str,
    cwd: str = "",
) -> str:
    """Create a Jira story AND register it in work_items atomically (RAISE-14647 / S8).

    Returns JSON:
      {status: ok, jira_key, work_item_id, local_key} — both created.
      {status: already_registered, jira_key, work_item_id} — idempotent re-run.
      {status: error, reason, jira_key?, reconcile?} — failure with context.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_epic_story_create")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from datetime import datetime
        from uuid import uuid4

        from raise_cli.adapters.models import IssueSpec
        from raise_cli.storage.work_items import (
            WorkItem,
            WorkItemStore,
            slugify_local_key,
        )

        project_root = _root
        store = WorkItemStore(project_root)

        # AC4 — idempotency pre-check: avoid duplicate Jira call if already registered
        existing = store.find_by_parent_and_summary(epic_jira_key, summary)
        if existing is not None:
            return compact_response(
                {
                    "status": "already_registered",
                    "jira_key": existing.jira_key,
                    "work_item_id": existing.id,
                }
            )

        # AC2 — Jira create; failure prevents any INSERT
        try:
            pm = _resolve_adapter(None, cwd)
            spec = IssueSpec(
                summary=summary,
                issue_type="Story",
                parent=epic_jira_key,
            )
            ref = pm.create_issue(project, spec)
            jira_key: str = ref.key
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})

        # AC5 — post-Jira idempotency: jira_key may have been pre-seeded
        pre_existing = store.get_by_jira_key(jira_key)
        if pre_existing is not None:
            return compact_response(
                {
                    "status": "already_registered",
                    "jira_key": pre_existing.jira_key,
                    "work_item_id": pre_existing.id,
                }
            )

        # AC1 — INSERT into work_items
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
            # AC3 — partial failure: Jira created, INSERT failed
            return json.dumps(
                {
                    "status": "error",
                    "reason": "work_items_insert_failed",
                    "jira_key": jira_key,
                    "reconcile": f"rai backlog get {jira_key}",
                    "detail": str(exc),
                }
            )

        return compact_response(
            {
                "status": "ok",
                "jira_key": created.jira_key,
                "work_item_id": created.id,
                "local_key": created.local_key,
            }
        )

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_backlog_update(
    issue_key: str,
    summary: str = "",
    labels: str = "",
    priority: str = "",
    assignee: str = "",
    custom_fields: str = "",
    adapter: str = "jira",
    cwd: str = "",
) -> str:
    """Update fields on a backlog issue.

    Args:
        issue_key: Issue key (e.g., "RAISE-123").
        summary: New summary/title. Empty string = no change.
        labels: Comma-separated labels. Empty string = no change.
        priority: Priority name (e.g., "High"). Empty string = no change.
        assignee: Assignee identifier (email or account ID). Empty string = no change.
        custom_fields: JSON object of custom field updates (e.g., '{"customfield_13267": "Value"}').
                       Empty string = no custom fields.
        adapter: Backlog adapter to use (default "jira").
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_backlog_update")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        result = _build_update_fields(
            summary, labels, priority, assignee, custom_fields
        )
        if isinstance(result, str):
            return result
        try:
            pm = _resolve_adapter(adapter or None, cwd)
            ref = pm.update_issue(issue_key, result)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        return compact_response(_write_outcome_response(ref))

    return await asyncio.to_thread(_run)
