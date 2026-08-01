"""Shared proof helpers for epic story-iteration completion."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from raise_cli.pipeline.terminal_status import is_terminal_status
from raise_core.workflow.models import RunStatus

if TYPE_CHECKING:
    from raise_cli.pipeline.run_store import PipelineRunStore


def _is_story_terminal(status: str) -> bool:
    """Treat done/complete/closed/cancelled/archived story statuses as terminal.

    Delegates to the shared ``terminal_status.is_terminal_status`` helper
    (S14559.1 T1) so ``ChildEpicsCompleteGate`` reuses the same token set
    instead of cloning it. The ``archived`` token added there is a no-op for
    real story statuses (stories don't carry an Archived status in
    practice), so this is a zero-behavior-change delegation for the epic
    path.
    """
    return is_terminal_status(status)


def find_epic_scope_file(search_root: Path, issue_id: str) -> Path | None:
    """Resolve the epic scope path from an epic issue key or local epic ID."""
    import re

    issue_num = re.sub(r"[^0-9]", "", issue_id)
    if not issue_num:
        return None

    epics_root = search_root / "work" / "epics"
    if not epics_root.is_dir():
        return None

    matches = sorted(epics_root.glob(f"e{issue_num}-*/scope.md"))
    if matches:
        return matches[0]
    return None


def _story_status_column(cols: list[str]) -> int | None:
    """Resolve the status column index from a stories table header row."""
    lowered = [col.lower() for col in cols]
    return next(
        (idx for idx, col in enumerate(lowered) if col in {"status", "estado"}),
        None,
    )


def _is_epic_story_row(story_id: str) -> bool:
    """Accept markdown table rows that look like story IDs."""
    if story_id.lower() == "id" or set(story_id) == {"-"}:
        return False
    return "." in story_id and any(ch.isdigit() for ch in story_id)


def _story_jira_column(cols: list[str]) -> int | None:
    """Resolve the Jira Key column index from a stories table header row."""
    lowered = [col.lower() for col in cols]
    return next(
        (
            idx
            for idx, col in enumerate(lowered)
            if "jira" in col or "clave" in col or col == "key"
        ),
        None,
    )


def parse_epic_story_rows(scope_file: Path) -> list[tuple[str, str, str | None]]:
    """Parse the epic scope stories table into (story_id, status, jira_key) rows."""
    rows: list[tuple[str, str, str | None]] = []
    status_idx: int | None = None
    jira_idx: int | None = None
    for raw_line in scope_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            status_idx = None  # reset at table boundary
            jira_idx = None
            continue

        cols = [col.strip() for col in line.strip("|").split("|")]
        if len(cols) < 2:
            continue

        story_id = cols[0]
        if not _is_epic_story_row(story_id):
            # Any non-story row may be a header — look for status/Jira columns
            new_status_idx = _story_status_column(cols)
            if new_status_idx is not None:
                status_idx = new_status_idx
            new_jira_idx = _story_jira_column(cols)
            if new_jira_idx is not None:
                jira_idx = new_jira_idx
            continue

        # Story data row — only count when we know the status column
        if status_idx is None or status_idx >= len(cols):
            continue

        status = cols[status_idx]
        jira_key = (
            cols[jira_idx] if jira_idx is not None and jira_idx < len(cols) else None
        )
        rows.append((story_id, status, jira_key or None))

    return rows


async def _terminal_story_jira_keys(run_store: PipelineRunStore) -> set[str]:
    """Return Jira Keys with a completed `story`-pipeline run in history.

    RAISE-11622: a story that ran via a standalone `pipeline_start` call
    (not nested under the epic's own run) never gets its epic scope.md
    Status column hand-edited. `pipeline_runs` history is authoritative and
    independent of that nesting, so it is consulted as a fallback source.
    """
    runs = await run_store.list_runs()
    return {
        run["issue_id"]
        for run in runs
        if run.get("pipeline_name") == "story"
        and run.get("status")
        in (
            RunStatus.COMPLETED,
            "complete",
        )  # engine writes "complete"; enum value is "completed"
        and run.get("issue_id")
    }


async def pending_epic_stories(
    search_root: Path,
    issue_id: str,
    run_store: PipelineRunStore | None = None,
) -> tuple[list[str], str | None]:
    """Return pending story IDs from the epic scope, or a blocking reason.

    A story row is treated as terminal when EITHER its scope.md Status text
    is terminal (fast path, no I/O) OR a completed `story`-pipeline run
    exists in `pipeline_runs` history for the row's Jira Key (RAISE-11622).
    The latter check only runs when the fast path leaves pending rows with a
    resolvable Jira Key, keeping the common case (scope.md already current)
    free of the extra lookup.
    """
    scope_file = find_epic_scope_file(search_root, issue_id)
    if scope_file is None:
        return [], "epic scope document not found"

    rows = parse_epic_story_rows(scope_file)
    if not rows:
        return [], "epic scope does not declare child stories"

    pending = [
        story_id for story_id, status, _ in rows if not _is_story_terminal(status)
    ]
    if not pending:
        return [], None

    jira_by_story = {story_id: jira_key for story_id, _, jira_key in rows}
    if any(jira_by_story.get(story_id) for story_id in pending):
        if run_store is None:
            from raise_cli.pipeline.run_store import get_run_store

            run_store = get_run_store()
        completed_keys = await _terminal_story_jira_keys(run_store)
        pending = [
            story_id
            for story_id in pending
            if jira_by_story.get(story_id) not in completed_keys
        ]

    return pending, None
