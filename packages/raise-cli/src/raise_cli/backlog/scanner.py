"""Scanner — extract backlog metadata from work/epics/ artifacts.

Reads scope.md and story files, extracts structured metadata from
3 formats: YAML frontmatter, blockquote headers, bold-key patterns.

Story: S1700.4 (reconcile) | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Regex patterns for non-frontmatter metadata extraction
_RE_BLOCKQUOTE_KEY = re.compile(r"^>\s*Key:\s*(RAISE-\d+)", re.MULTILINE)
_RE_BOLD_JIRA = re.compile(r"\*\*Jira:\*\*\s*(RAISE-\d+)")
_RE_BLOCKQUOTE_EPIC = re.compile(r"^>\s*Epic:\s*(RAISE-\d+)", re.MULTILINE)
_RE_TITLE_H1 = re.compile(r"^#\s+(.+?)(?:\s*—\s*Scope)?$", re.MULTILINE)
_RE_EPIC_ID_FRONTMATTER = re.compile(r"^epic_id:\s*[\"']?(E\d+)[\"']?", re.MULTILINE)
_RE_STORY_ID_FRONTMATTER = re.compile(
    r"^story_id:\s*[\"']?(S[\d.]+)[\"']?", re.MULTILINE
)


@dataclass
class ScannedItem:
    """A backlog item extracted from filesystem artifacts."""

    local_id: str  # E1700, S1700.3, RAISE-819
    title: str
    item_type: str  # epic, story
    status: str
    jira_key: str | None  # if already linked
    source_file: str  # relative path to the artifact
    parent_id: str | None = None  # epic_ref for stories


def scan_work_epics(project_root: Path) -> list[ScannedItem]:
    """Scan work/epics/ for all epics and stories with metadata."""
    work_dir = project_root / "work" / "epics"
    if not work_dir.is_dir():
        return []

    items: list[ScannedItem] = []
    for epic_dir in sorted(work_dir.iterdir()):
        if not epic_dir.is_dir():
            continue

        # Scan epic scope
        scope = epic_dir / "scope.md"
        if scope.exists():
            item = _extract_item(scope, "epic", project_root)
            if item:
                items.append(item)

        # Scan stories
        stories_dir = epic_dir / "stories"
        if stories_dir.is_dir():
            for story_file in sorted(stories_dir.glob("*scope*.md")):
                item = _extract_item(story_file, "story", project_root)
                if item:
                    items.append(item)

    return items


def _extract_item(path: Path, item_type: str, project_root: Path) -> ScannedItem | None:
    """Extract metadata from a single artifact file."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Cannot read %s: %s", path, exc)
        return None

    head = content[:2000]  # only scan first 2000 chars for metadata
    rel_path = str(path.relative_to(project_root))

    # Try YAML frontmatter first
    frontmatter = _parse_frontmatter(content)

    # Extract jira_key from multiple sources (priority order)
    jira_key = (
        frontmatter.get("jira_key")
        or _regex_first(_RE_BLOCKQUOTE_KEY, head)
        or _regex_first(_RE_BOLD_JIRA, head)
        or _jira_key_from_dirname(path)
    )

    # Extract local ID
    local_id = (
        frontmatter.get("epic_id")
        or frontmatter.get("story_id")
        or _regex_first(_RE_EPIC_ID_FRONTMATTER, head)
        or _regex_first(_RE_STORY_ID_FRONTMATTER, head)
        or _id_from_dirname(path, item_type)
    )

    if not local_id:
        logger.debug("No ID found in %s, skipping", rel_path)
        return None

    # Extract title
    title = frontmatter.get("title") or _title_from_h1(head) or local_id

    # Extract status
    status = frontmatter.get("status", "unknown")

    # Extract parent (for stories) — 3 sources
    parent_id = (
        frontmatter.get("epic_ref")
        or _regex_first(_RE_BLOCKQUOTE_EPIC, head)
        or _parent_from_dirname(path, item_type)
    )

    return ScannedItem(
        local_id=local_id,
        title=title,
        item_type=item_type,
        status=status,
        jira_key=jira_key,
        source_file=rel_path,
        parent_id=parent_id,
    )


def _parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter if present."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        raw: object = yaml.safe_load(content[3:end])
        if isinstance(raw, dict):
            return {str(k): str(v) for k, v in raw.items()}  # type: ignore[union-attr]
    except yaml.YAMLError:
        pass
    return {}


def _regex_first(pattern: re.Pattern[str], text: str) -> str | None:
    """Return first regex match group or None."""
    m = pattern.search(text)
    return m.group(1) if m else None


def _title_from_h1(text: str) -> str | None:
    """Extract title from first H1 heading."""
    m = _RE_TITLE_H1.search(text)
    if m:
        title = m.group(1).strip()
        # Remove common prefixes like "E1700: " or "RAISE-819: "
        title = re.sub(r"^(?:E\d+|S[\d.]+|RAISE-\d+)[\s:—-]+\s*", "", title)
        return title.strip() or None
    return None


def _jira_key_from_dirname(path: Path) -> str | None:
    """Extract RAISE-NNN from parent directory name."""
    epic_dir = path.parent
    if epic_dir.name == "stories":
        epic_dir = epic_dir.parent
    if epic_dir.name.startswith("RAISE-"):
        return epic_dir.name
    return None


def _id_from_dirname(path: Path, item_type: str) -> str | None:
    """Infer local ID from directory or filename."""
    if item_type == "epic":
        epic_dir = path.parent
        if epic_dir.name == "stories":
            epic_dir = epic_dir.parent
        name = epic_dir.name
        # e1700-adapter-migration-path → E1700
        m = re.match(r"e(\d+)", name)
        if m:
            return f"E{m.group(1)}"
        # RAISE-819 → RAISE-819
        if name.startswith("RAISE-"):
            return name
        # raise-153-developer-enablement → RAISE-153
        m = re.match(r"raise-(\d+)", name)
        if m:
            return f"RAISE-{m.group(1)}"
    elif item_type == "story":
        # s1700.3-scope.md → S1700.3
        m = re.match(r"s([\d.]+)", path.stem)
        if m:
            return f"S{m.group(1)}"
    return None


def _parent_from_dirname(path: Path, item_type: str) -> str | None:
    """Infer parent epic ID from directory structure for stories.

    work/epics/e1305-mcp/stories/s1305.1-scope.md → E1305
    work/epics/RAISE-819/stories/s819.1-scope.md → RAISE-819
    """
    if item_type != "story":
        return None
    # Navigate: stories/ → epic_dir
    stories_dir = path.parent
    if stories_dir.name != "stories":
        # Might be a nested subdirectory
        stories_dir = stories_dir.parent
    epic_dir = stories_dir.parent if stories_dir.name == "stories" else stories_dir
    name = epic_dir.name
    m = re.match(r"e(\d+)", name)
    if m:
        return f"E{m.group(1)}"
    if name.startswith("RAISE-"):
        return name
    # raise-153-developer-enablement → RAISE-153
    m = re.match(r"raise-(\d+)", name)
    if m:
        return f"RAISE-{m.group(1)}"
    return None
