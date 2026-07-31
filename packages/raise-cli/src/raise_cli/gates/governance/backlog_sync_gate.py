"""BacklogSyncGate — HITL pause when story/epic issues are missing from Jira.

Extracts story IDs from the epic scope.md and verifies each has a
corresponding issue in Jira (child of the epic). Fails with actionable
detail when issues are missing — the dev decides whether to create them
or skip.

Runs at:
  - before:story:start  (single story check)
  - before:epic:close   (all stories check)

Escape hatch: RAISE_BACKLOG_SYNC_SKIP=<reason> bypasses with logged warning.

Architecture: RAISE-10613.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from raise_cli.adapters.models.pm import IssueSummary
from raise_cli.gates.models import GateContext, GateResult

if TYPE_CHECKING:
    from raise_cli.storage.work_items import WorkItem

_log = logging.getLogger(__name__)
_SKIP_ENV = "RAISE_BACKLOG_SYNC_SKIP"
_STORY_RE = re.compile(r"story/s(\d+)\.(\d+)/")
# New-style branches: story/raise-14644/ or story/RAISE-14644/ (RAISE-14644 S5)
_BRANCH_JIRA_RE = re.compile(r"story/([a-zA-Z]+)-(\d+)/")
_SCOPE_STORY_RE = re.compile(r"\|\s*S(\d+\.\d+)\s*\|")
_JIRA_STORY_RE = re.compile(r"\bS(\d+\.\d+)\b")
_JIRA_KEY_FRONTMATTER_RE = re.compile(r'^jira_key:\s*"?(RAISE-\d+)"?\s*$', re.MULTILINE)


def _git_branch(working_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def _find_epic_scope(working_dir: Path, epic_num: str) -> Path | None:
    """Find scope.md for an epic by its number prefix."""
    for candidate in (working_dir / "work" / "epics").iterdir():
        if candidate.is_dir() and candidate.name.startswith(f"e{epic_num}"):
            scope = candidate / "scope.md"
            if scope.is_file():
                return scope
    return None


def _extract_story_ids_from_scope(scope_path: Path) -> list[str]:
    """Parse story IDs from the scope.md table (e.g. S10332.1)."""
    content = scope_path.read_text(encoding="utf-8")
    return _SCOPE_STORY_RE.findall(content)


def _get_jira_children_full(epic_key: str) -> list[IssueSummary]:
    """Query Jira for full child issue records of an epic.

    Returns the full ``IssueSummary`` (key + summary + ...) so callers can
    match structurally on ``.key`` instead of scraping issue titles.
    """
    try:
        from raise_cli.adapters.resolve import resolve_pm_adapter

        adapter = resolve_pm_adapter(None)
        return adapter.search(
            f"project = RAISE AND parent = {epic_key}",
            limit=100,
        )
    except Exception:  # noqa: BLE001
        _log.debug("Failed to query Jira for epic children", exc_info=True)
        return []


def _get_jira_children(epic_key: str) -> list[str]:
    """Query Jira for child issue summaries of an epic."""
    return [issue.summary for issue in _get_jira_children_full(epic_key)]


def _read_story_jira_key(working_dir: Path, epic_num: str, story_id: str) -> str | None:
    """Parse the persisted ``jira_key`` from the story's own story.md frontmatter.

    Locates ``work/epics/{epic-dir}/stories/s{story_id lower}-story.md``
    (directory-matching mirrors ``_find_epic_scope``) and extracts a
    ``jira_key: "RAISE-XXXX"`` (or unquoted) frontmatter line. Returns None
    when the epics dir, the story.md, or the field itself is absent — the
    caller falls back to the legacy summary-substring heuristic in that case
    (RAISE-14588).
    """
    epics_dir = working_dir / "work" / "epics"
    if not epics_dir.is_dir():
        return None
    for candidate in epics_dir.iterdir():
        if candidate.is_dir() and candidate.name.startswith(f"e{epic_num}"):
            story_file = candidate / "stories" / f"{story_id.lower()}-story.md"
            if story_file.is_file():
                content = story_file.read_text(encoding="utf-8")
                match = _JIRA_KEY_FRONTMATTER_RE.search(content)
                return match.group(1) if match else None
    return None


def _extract_story_ids_from_jira(children_summaries: list[str]) -> set[str]:
    """Extract story IDs from Jira child summaries (e.g. S10332.4)."""
    story_ids: set[str] = set()
    for summary in children_summaries:
        match = _JIRA_STORY_RE.search(summary)
        if match:
            story_ids.add(match.group(1))
    return story_ids


def _get_epic_key(working_dir: Path, epic_num: str) -> str | None:
    """Resolve the Jira key for an epic from scope.md frontmatter."""
    scope = _find_epic_scope(working_dir, epic_num)
    if not scope:
        return None
    content = scope.read_text(encoding="utf-8")
    jira_match = re.search(r"\*\*Jira:\*\*\s*(RAISE-\d+)", content)
    if jira_match:
        return jira_match.group(1)
    key_match = re.search(r"RAISE-(\d+)", content)
    return f"RAISE-{key_match.group(1)}" if key_match else None


def _extract_jira_key_from_branch(branch: str) -> str | None:
    """Extract Jira key from new-style branches: story/raise-14644/ → 'RAISE-14644'."""
    m = _BRANCH_JIRA_RE.search(branch)
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    return None


def _get_work_item_stories(working_dir: Path, parent_jira_key: str) -> list[WorkItem]:
    """Query work_items for story-type items under parent_jira_key.

    Returns [] on any error (graceful degradation for old DBs without work_items).
    """
    try:
        from raise_cli.storage.work_items import WorkItemStore

        return [
            item
            for item in WorkItemStore(working_dir).list_all(type="story")
            if item.parent_jira_key == parent_jira_key
        ]
    except Exception:  # noqa: BLE001
        _log.debug(
            "work_items query failed — falling back to legacy path", exc_info=True
        )
        return []


def _verify_story_in_work_items(
    gate_id: str, working_dir: Path, jira_key: str
) -> GateResult | None:
    """Check story is in work_items. Returns None when check is unavailable (fallthrough)."""
    try:
        from raise_cli.storage.work_items import WorkItemStore

        item = WorkItemStore(working_dir).get_by_jira_key(jira_key)
    except Exception:  # noqa: BLE001
        _log.debug("work_items check unavailable for %s — falling through", jira_key)
        return None
    if item is not None:
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"Story {jira_key} verified in work_items registry",
        )
    return GateResult(
        passed=False,
        gate_id=gate_id,
        message=f"Story {jira_key} not found in work_items registry",
        details=(
            f"Sync story: rai backlog get {jira_key}",
            f"Escape: {_SKIP_ENV}=<reason> rai gate check {gate_id}",
        ),
    )


class BacklogSyncGate:
    """HITL gate — pauses when work items lack Jira issues."""

    gate_id: ClassVar[str] = "gate-backlog-sync"
    description: ClassVar[str] = (
        "Work items have corresponding issues in backlog tracker"
    )
    workflow_point: ClassVar[str] = "before:story:implement"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check that stories in scope have Jira issues."""
        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Backlog sync skipped: {skip_reason}",
            )

        branch = _git_branch(context.working_dir)

        # work_items primary path: story/raise-{N}/ branches (RAISE-14644 S5)
        branch_jira_key = _extract_jira_key_from_branch(branch)
        if branch_jira_key:
            result = _verify_story_in_work_items(
                self.gate_id, context.working_dir, branch_jira_key
            )
            if result is not None:
                return result
        # end work_items path

        story_m = _STORY_RE.search(branch)
        if not story_m:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No story context detected — backlog sync not applicable",
            )

        epic_num = story_m.group(1)
        story_id = f"S{epic_num}.{story_m.group(2)}"

        epic_key = _get_epic_key(context.working_dir, epic_num)
        if not epic_key:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"No epic key found for E{epic_num} — cannot verify backlog",
            )

        story_jira_key = _read_story_jira_key(context.working_dir, epic_num, story_id)

        if story_jira_key:
            # Precise structural match: the story's own persisted Jira key
            # must appear among the epic's children — independent of how
            # the child issue's title/summary is worded (RAISE-14588).
            children = _get_jira_children_full(epic_key)
            if not children:
                return GateResult(
                    passed=False,
                    gate_id=self.gate_id,
                    message=f"No child issues found in Jira for {epic_key} — story {story_id} has no Jira issue",
                    details=(
                        f'Create the issue: rai backlog create "{story_id} — <title>" -p RAISE -t Story --parent {epic_key}',
                        f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
                    ),
                )
            story_found = any(issue.key == story_jira_key for issue in children)
        else:
            # No persisted key (older story, or story.md absent) — fall back
            # to the legacy summary-substring heuristic for backward compat.
            children_summaries = _get_jira_children(epic_key)
            if not children_summaries:
                return GateResult(
                    passed=False,
                    gate_id=self.gate_id,
                    message=f"No child issues found in Jira for {epic_key} — story {story_id} has no Jira issue",
                    details=(
                        f'Create the issue: rai backlog create "{story_id} — <title>" -p RAISE -t Story --parent {epic_key}',
                        f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
                    ),
                )
            story_found = any(story_id in s for s in children_summaries)

        if story_found:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{story_id} has a corresponding issue in {epic_key}",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=f"Story {story_id} has no Jira issue under {epic_key}",
            details=(
                f'Create the issue: rai backlog create "{story_id} — <title>" -p RAISE -t Story --parent {epic_key}',
                f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
            ),
        )


def _resolve_epic_context(
    branch: str, working_dir: Path
) -> tuple[str | None, str | None]:
    """Return (epic_key, epic_num) from branch name.

    For old-style branches (story/s{N}.{M}/): reads scope.md.
    For new-style branches (story/raise-{N}/): looks up parent via work_items.
    Returns (None, None) when no epic context can be determined.
    """
    story_m = _STORY_RE.search(branch)
    if story_m:
        epic_num = story_m.group(1)
        return _get_epic_key(working_dir, epic_num), epic_num

    branch_jira_key = _extract_jira_key_from_branch(branch)
    if branch_jira_key:
        try:
            from raise_cli.storage.work_items import WorkItemStore

            item = WorkItemStore(working_dir).get_by_jira_key(branch_jira_key)
            if item:
                return item.parent_jira_key, None
        except Exception:  # noqa: BLE001
            _log.debug("work_items lookup failed for %s", branch_jira_key)
    return None, None


def _check_work_items_status_consistency(
    gate_id: str, working_dir: Path, epic_key: str
) -> GateResult | None:
    """Check all work_items stories under epic_key have status='done'.

    Returns a GateResult (pass or fail) when work_items has data, None to
    signal fallback / skip (empty registry → uncertain, don't block).
    Only called when context.workflow_point == 'before:epic:close'.
    """
    registry_stories = _get_work_item_stories(working_dir, epic_key)
    if not registry_stories:
        return None
    open_stories = [wi for wi in registry_stories if wi.status.lower() != "done"]
    if not open_stories:
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"All {len(registry_stories)} stories verified — all Done under {epic_key}",
        )
    count = len(open_stories)
    noun = "story" if count == 1 else "stories"
    details: list[str] = [
        f"{wi.jira_key} is {wi.status} — transition to Done before closing epic"
        for wi in open_stories
        if wi.jira_key
    ]
    details.append(f"Escape: {_SKIP_ENV}=<reason> rai gate check {gate_id}")
    return GateResult(
        passed=False,
        gate_id=gate_id,
        message=f"{count} open {noun} under {epic_key}",
        details=tuple(details),
    )


def _check_work_items_epic_drift(
    gate_id: str, working_dir: Path, epic_key: str
) -> GateResult | None:
    """Check drift between work_items registry and Jira for the epic.

    Returns a GateResult (pass or fail) when work_items has data, None to
    signal fallback to the scope.md regex path.
    """
    registry_stories = _get_work_item_stories(working_dir, epic_key)
    if not registry_stories:
        return None

    registry_keys = {wi.jira_key for wi in registry_stories if wi.jira_key}
    jira_keys = {issue.key for issue in _get_jira_children_full(epic_key)}
    missing_jira = sorted(registry_keys - jira_keys)
    missing_registry = sorted(jira_keys - registry_keys)

    if not missing_jira and not missing_registry:
        return GateResult(
            passed=True,
            gate_id=gate_id,
            message=f"All {len(registry_keys)} stories verified — no drift between work_items and {epic_key}",
        )

    details: list[str] = [
        *[
            f'Missing in Jira: {k} — rai backlog create "{k}" -p RAISE -t Story --parent {epic_key}'
            for k in missing_jira
        ],
        *[
            f"Missing in registry: {k} — sync to local work_items"
            for k in missing_registry
        ],
        f"Escape: {_SKIP_ENV}=<reason> rai gate check {gate_id}",
    ]
    summary_parts: list[str] = []
    if missing_jira:
        summary_parts.append(f"{len(missing_jira)} missing from Jira")
    if missing_registry:
        summary_parts.append(f"{len(missing_registry)} missing from registry")
    return GateResult(
        passed=False,
        gate_id=gate_id,
        message=f"Story drift under {epic_key}: {', '.join(summary_parts)}",
        details=tuple(details),
    )


def _run_work_items_epic_checks(
    gate_id: str,
    working_dir: Path,
    epic_key: str,
    run_status_check: bool,
) -> GateResult | None:
    """Run drift then (optionally) status check against work_items.

    Returns a GateResult when work_items has data, None to fall through to
    the scope.md regex path. ``run_status_check`` is True only when the gate
    is invoked at its own workflow_point (before:epic:close).
    """
    drift_result = _check_work_items_epic_drift(gate_id, working_dir, epic_key)
    if drift_result is None:
        return None
    if not drift_result.passed:
        return drift_result  # drift failed — skip status check
    if run_status_check:
        status_result = _check_work_items_status_consistency(
            gate_id, working_dir, epic_key
        )
        if status_result is not None:
            return status_result
    return drift_result


class EpicBacklogSyncGate:
    """HITL gate — at epic close, verifies ALL stories have Jira issues."""

    gate_id: ClassVar[str] = "gate-epic-backlog-sync"
    description: ClassVar[str] = (
        "All epic stories have corresponding issues in backlog tracker"
    )
    workflow_point: ClassVar[str] = "before:epic:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check all stories in scope.md have Jira issues."""
        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Backlog sync skipped: {skip_reason}",
            )

        branch = _git_branch(context.working_dir)
        epic_key, epic_num = _resolve_epic_context(branch, context.working_dir)
        if not epic_key:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No story/epic context detected — not applicable",
            )

        # work_items primary path (RAISE-14644 S5 + RAISE-14645 S6)
        work_items_result = _run_work_items_epic_checks(
            self.gate_id,
            context.working_dir,
            epic_key,
            run_status_check=(context.workflow_point == self.workflow_point),
        )
        if work_items_result is not None:
            return work_items_result
        # fallback to scope.md regex

        if epic_num is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"No scope.md fallback available for {epic_key} — skipping",
            )

        scope = _find_epic_scope(context.working_dir, epic_num)
        if not scope:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"No scope.md found for E{epic_num}",
            )

        local_stories = _extract_story_ids_from_scope(scope)
        if not local_stories:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No stories found in scope.md",
            )

        children_summaries = _get_jira_children(epic_key)
        jira_story_ids = _extract_story_ids_from_jira(children_summaries)
        local_story_ids = set(local_stories)
        missing = sorted(local_story_ids - jira_story_ids)
        extra = sorted(jira_story_ids - local_story_ids)

        if not missing and not extra:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"All {len(local_stories)} stories in scope.md have Jira issues under {epic_key}",
            )

        details = [
            *[
                f'Missing in Jira: S{s} — rai backlog create "S{s} — <title>" -p RAISE -t Story --parent {epic_key}'
                for s in missing
            ],
            *[
                f"Extra in Jira: S{s} — remove or reconcile the stale child issue under {epic_key}"
                for s in extra
            ],
            f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
        ]
        summary_parts: list[str] = []
        if missing:
            summary_parts.append(f"{len(missing)} missing")
        if extra:
            summary_parts.append(f"{len(extra)} extra")

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=(
                f"Story parity mismatch under {epic_key}: " + ", ".join(summary_parts)
            ),
            details=tuple(details),
        )
