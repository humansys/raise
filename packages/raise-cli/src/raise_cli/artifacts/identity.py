"""Resolve the local identity used to persist lifecycle artifacts."""

from __future__ import annotations

import re
from pathlib import Path

_STORY_ID_RE = re.compile(r"^story_id:\s*[\"']?(S[\d.]+)[\"']?", re.MULTILINE)
_JIRA_KEY_RE = re.compile(
    r"^jira_key:\s*[\"']?([A-Z][A-Z0-9_]*-\d+)[\"']?", re.MULTILINE
)


def resolve_artifact_identity(identifier: str, project_root: Path) -> str:
    """Return the local artifact key for an issue identifier when known.

    Story files remain the source of truth for legacy ``S123.4`` identifiers.
    The work-item registry covers newly created items that have no story file
    yet. Unknown identifiers intentionally pass through unchanged.
    """
    if not identifier:
        return identifier

    story_id = _story_id_for_jira_key(identifier, project_root)
    if story_id:
        return story_id

    try:
        from raise_cli.storage.work_items import WorkItemStore

        work_item = WorkItemStore(project_root).get_by_jira_key(identifier)
    except Exception:  # noqa: BLE001 - identity lookup must not block a gate
        return identifier

    return work_item.local_key if work_item else identifier


def _story_id_for_jira_key(jira_key: str, project_root: Path) -> str | None:
    """Find a persisted story ID whose frontmatter is linked to ``jira_key``."""
    stories_dir = project_root / "work" / "epics"
    if not stories_dir.is_dir():
        return None

    for story_file in stories_dir.glob("*/stories/*-story.md"):
        try:
            content = story_file.read_text(encoding="utf-8")
        except OSError:
            continue
        jira_match = _JIRA_KEY_RE.search(content)
        if not jira_match or jira_match.group(1).upper() != jira_key.upper():
            continue
        story_match = _STORY_ID_RE.search(content)
        if story_match:
            return story_match.group(1)
    return None
