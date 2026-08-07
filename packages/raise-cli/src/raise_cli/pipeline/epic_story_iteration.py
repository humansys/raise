"""Shared proof helpers for epic story-iteration completion."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, cast

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


_JIRA_KEY_RE = re.compile(r"[A-Z][A-Z0-9]*-\d+")
_FRONTMATTER_JIRA_KEY_RE = re.compile(
    r"^jira_key\s*:\s*([A-Z][A-Z0-9]*-\d+)\s*$", re.IGNORECASE
)


def _frontmatter_jira_key(lines: list[str]) -> str | None:
    """Extract `jira_key: RAISE-N` from a leading YAML frontmatter block.

    RAISE-15960 C1: 31 live-corpus scope.md files (e.g.
    e-kc2-cartridge-server-runtime) declare their epic key this way, using
    an underscore rather than the "Jira Key" wording the rest of this module
    scans for. Only scans between the opening and closing `---` fences so a
    key mentioned later in the document body is never mistaken for
    frontmatter.
    """
    if not lines or lines[0].strip() != "---":
        return None
    for fm_line in lines[1:]:
        if fm_line.strip() == "---":
            break
        match = _FRONTMATTER_JIRA_KEY_RE.match(fm_line.strip())
        if match:
            return match.group(1)
    return None


def _heading_epic_jira_key(lines: list[str]) -> str | None:
    """Extract the key from a `## Jira` heading followed by an `Epic:` line.

    RAISE-15960 C1: 93 live-corpus scope.md files (e.g.
    RAISE-10617-gate-test-tech-debt, e8395-*) declare the epic's key this
    way rather than via the literal "Jira Key" wording.
    """
    for idx, raw_line in enumerate(lines):
        heading = raw_line.strip().lower()
        if heading not in ("## jira", "# jira"):
            continue
        for lookahead in lines[idx + 1 : idx + 5]:
            candidate = lookahead.strip()
            if not candidate.lower().startswith("epic:"):
                continue
            match = _JIRA_KEY_RE.search(candidate)
            if match:
                return match.group(0)
    return None


def _epic_jira_key(scope_file: Path) -> str | None:
    """Extract the epic's own declared Jira key from scope.md content.

    Skips markdown table rows: a `Jira Key` column header on the *child
    stories* table is not the epic's own key and must not be treated as
    one (RAISE-15960). Supports inline (`**Jira Key:** RAISE-X`,
    `- **Jira Key**: RAISE-X`), heading-style (`## Jira Key` followed by
    the bare key a couple of lines down), YAML frontmatter
    (`jira_key: RAISE-X`), and `## Jira` heading + `Epic: RAISE-X` line
    declarations (RAISE-15960 C1).
    """
    lines = scope_file.read_text(encoding="utf-8").splitlines()

    frontmatter_key = _frontmatter_jira_key(lines)
    if frontmatter_key:
        return frontmatter_key

    heading_epic_key = _heading_epic_jira_key(lines)
    if heading_epic_key:
        return heading_epic_key

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if line.startswith("|") or "jira key" not in line.lower():
            continue

        match = _JIRA_KEY_RE.search(line)
        if match:
            return match.group(0)

        for lookahead in lines[idx + 1 : idx + 4]:
            candidate = lookahead.strip()
            if not candidate:
                continue
            match = _JIRA_KEY_RE.search(candidate)
            if match:
                return match.group(0)

    return None


def find_epic_scope_file(search_root: Path, issue_id: str) -> Path | None:
    """Resolve the epic scope path from an epic issue key or local epic ID."""
    issue_num = re.sub(r"[^0-9]", "", issue_id)
    if not issue_num:
        return None

    epics_root = search_root / "work" / "epics"
    if not epics_root.is_dir():
        return None

    matches = sorted(epics_root.glob(f"e{issue_num}-*/scope.md"))
    if matches:
        return matches[0]

    # RAISE-15960: the numeric-prefix glob misses for epic directories with
    # no numeric segment (e.g. `e-fleet-governance`) or whose numeric prefix
    # is a local epic ID rather than the Jira issue number. Fall back to
    # scanning scope.md content for a declared Jira Key matching issue_id.
    issue_key = issue_id.strip().upper()
    for scope_file in sorted(epics_root.glob("*/scope.md")):
        if _epic_jira_key(scope_file) == issue_key:
            return scope_file
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
        raw_jira = (
            cols[jira_idx] if jira_idx is not None and jira_idx < len(cols) else None
        )
        # Accept only real issue keys, not placeholders such as "—", "-",
        # "N/A", or free-form text like "not-created-yet".
        jira_key = (
            raw_jira
            if raw_jira and re.match(r"[A-Z][A-Z0-9]*-\d+$", raw_jira)
            else None
        )
        rows.append((story_id, status, jira_key))

    return rows


def is_story_run_complete(run: dict[str, object]) -> bool:
    """Return True when a story run is demonstrably complete.

    RAISE-15833: some run-store serializations expose the terminal state via
    ``current_phase``/``progress`` rather than a top-level ``status`` field.
    Accept any of those signals so standalone story runs reconcile correctly.
    """
    status = run.get("status")
    if status in (
        RunStatus.COMPLETED,
        "complete",
        "completed",
    ):
        return True
    # Failed/cancelled runs are terminal but not complete, regardless of what
    # derived fields might say (RAISE-15833 review item #4).
    if status in ("failed", "cancelled"):
        return False

    phases = run.get("phases", [])
    phase_list = cast("list[dict[str, str]]", phases)
    if phase_list and any(
        p.get("status") in ("failed", "cancelled") for p in phase_list
    ):
        return False

    if run.get("current_phase") == "complete":
        return True

    progress = run.get("progress", "")
    if isinstance(progress, str):
        # Generic X/X check: works for 5-phase stories, 8-phase enterprise
        # stories, and any future pipeline length (RAISE-15833 review item #1).
        parts = progress.split("/")
        if (
            len(parts) == 2
            and parts[0].isdigit()
            and parts[1].isdigit()
            and int(parts[0]) > 0
            and parts[0] == parts[1]
        ):
            return True
    return False


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
        and is_story_run_complete(run)
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
