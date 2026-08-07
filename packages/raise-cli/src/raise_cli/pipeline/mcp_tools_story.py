"""Composite story bookend MCP tools — S7884.3 (E7884 K1, ADR-093/ADR-024).

raise_story_open / raise_story_close_full absorb the deterministic
sequence of the rai-story-start / rai-story-close skills; the skills
become thin presenters. Telemetry is emitted server-side as a handler
side-effect (K3 pattern) — never an LLM turn.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from pathlib import Path
from typing import Any

from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only


def _emit_work_signal(
    work_id: str, event: str, phase: str, cwd: str | None = None
) -> None:
    """Server-side lifecycle signal — best-effort, never raises (K3).

    Delegates to the shared helper (S7884.6) so story bookend signals
    carry the same correlation fields as engine transitions.

    ``cwd`` is the caller's checkout (RAISE-15986). This handler runs in
    the MCP server process, so without it both the git correlation fields
    and the checkout-scoped hooks downstream resolve against the server's
    directory instead of the agent's worktree.
    """
    from raise_cli.telemetry.emit_work import emit_work_lifecycle

    emit_work_lifecycle("story", work_id, event, phase, cwd=cwd)


def _emit_story_cost_summary(
    project_path: Path, session_id: str, *, story_id: str | None = None
) -> None:
    """Delegate to session.py helper — thin wrapper to keep mcp_tools_story import-cycle-safe.

    Lazy import avoids mcp_tools_story ↔ session.py cycle (T6 refactor phase).
    """
    from raise_cli.cli.commands.session import (
        _emit_story_cost_summary as _session_emit,  # noqa: PLC2701  # pyright: ignore[reportPrivateUsage]
    )

    _session_emit(project_path, session_id, story_id=story_id)


async def _story_open_impl(
    story_id: str,
    slug: str,
    epic_dir: str,
    story_content: str,
    scope_content: str,
    jira_key: str = "",
    cwd: str = "",
    commit_message: str = "",
) -> str:
    _root = _caller_context.require_caller_cwd(cwd, "raise_story_open")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from raise_cli.story.open_service import build_story_open_report

        project = _root
        report = build_story_open_report(
            project_path=project,
            cwd=project,
            story_id=story_id,
            slug=slug,
            jira_key=jira_key,
            epic_dir=epic_dir,
            story_content=story_content,
            scope_content=scope_content,
            commit_message=commit_message,
        )
        if report.status != "blocked":
            with suppress(Exception):
                _emit_work_signal(story_id, "start", "init", cwd=str(project))
        payload: dict[str, Any] = report.model_dump()
        return compact_response(payload)

    return await asyncio.to_thread(_run)


async def _story_close_full_impl(
    story_id: str,
    slug: str,
    epic_dir: str,
    merge_summary: str,
    jira_key: str = "",
    cwd: str = "",
) -> str:
    _root = _caller_context.require_caller_cwd(cwd, "raise_story_close_full")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from raise_cli.story.close_service import build_story_close_report

        project = _root
        report = build_story_close_report(
            project_path=project,
            cwd=project,
            story_id=story_id,
            slug=slug,
            jira_key=jira_key,
            epic_dir=epic_dir,
            merge_summary=merge_summary,
        )
        if report.status != "blocked":
            with suppress(Exception):
                _emit_work_signal(story_id, "complete", "close", cwd=str(project))
            with suppress(Exception):
                _emit_story_cost_summary(
                    project, "", story_id=story_id
                )  # "" → resolved via discover_agent_session_id() inside helper
        payload: dict[str, Any] = report.model_dump()
        return compact_response(payload)

    return await asyncio.to_thread(_run)


@local_only
async def raise_story_open(
    story_id: str,
    slug: str,
    epic_dir: str,
    story_content: str,
    scope_content: str,
    jira_key: str = "",
    cwd: str = "",
    commit_message: str = "",
) -> str:
    """Composite story open: epic check, branch, docs, commit, transition, bind.

    One call replaces the deterministic sequence of the rai-story-start
    skill. Statuses are ok|warn|blocked — blocked requires a human
    decision (the tool never auto-resolves); steps after a block are
    skipped.

    Args:
        story_id: Story identifier (e.g., "S7884.3").
        slug: Branch slug (e.g., "story-bookends-mcp").
        epic_dir: Epic directory under work/epics/ (empty = standalone).
        story_content: Markdown for the story doc (LLM judgment).
        scope_content: Markdown for the scope doc (LLM judgment).
        jira_key: Backlog issue key (empty skips transition + bind).
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
        commit_message: Override for the scope commit message.
    """
    return await _story_open_impl(
        story_id=story_id,
        slug=slug,
        epic_dir=epic_dir,
        story_content=story_content,
        scope_content=scope_content,
        jira_key=jira_key,
        cwd=cwd,
        commit_message=commit_message,
    )


@local_only
async def raise_story_close_full(
    story_id: str,
    slug: str,
    epic_dir: str,
    merge_summary: str,
    jira_key: str = "",
    cwd: str = "",
) -> str:
    """Composite story close: retro gate, hygiene, merge, cleanup, Done.

    One call replaces the deterministic close sequence of the
    rai-story-close skill. Merge target resolves worktree DB → epic
    branch → dev. Conflicts abort + block; a missing retro blocks.
    AR review and epic-scope updates stay with the skill (judgment).

    Args:
        story_id: Story identifier (e.g., "S7884.3").
        slug: Branch slug used at open.
        epic_dir: Epic directory under work/epics/.
        merge_summary: One-line summary for the merge commit body.
        jira_key: Backlog issue key (empty skips Done transition).
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
    """
    return await _story_close_full_impl(
        story_id=story_id,
        slug=slug,
        epic_dir=epic_dir,
        merge_summary=merge_summary,
        jira_key=jira_key,
        cwd=cwd,
    )
