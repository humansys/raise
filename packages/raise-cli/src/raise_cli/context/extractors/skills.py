"""Skill metadata extraction from SKILL.md frontmatter.

This module extracts skill metadata from YAML frontmatter in SKILL.md files
and converts them to GraphNode for the unified context graph.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from raise_core.graph.models import GraphNode

# Regex to match YAML frontmatter between --- markers
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def extract_skill_metadata(skill_path: Path) -> GraphNode | None:
    """Extract metadata from SKILL.md YAML frontmatter.

    Args:
        skill_path: Path to SKILL.md file.

    Returns:
        GraphNode for the skill, or None if parsing fails or file doesn't exist.

    Examples:
        >>> node = extract_skill_metadata(Path(".claude/skills/rai-story-plan/SKILL.md"))
        >>> node.id if node else None
        '/rai-story-plan'
    """
    if not skill_path.exists():
        return None

    try:
        content = skill_path.read_text(encoding="utf-8")
    except OSError:
        return None

    # Extract YAML frontmatter
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    # Cast to typed dict for pyright
    fm: dict[str, Any] = cast("dict[str, Any]", frontmatter)

    # Name is required
    name_value = fm.get("name")
    if not name_value:
        return None
    name: str = str(name_value)

    # Extract fields
    desc_value = fm.get("description", "")
    description: str = ""
    if isinstance(desc_value, str):
        # Clean up multiline YAML strings
        description = " ".join(desc_value.split())

    meta_value = fm.get("metadata", {})
    metadata_section: dict[str, Any] = {}
    if isinstance(meta_value, dict):
        metadata_section = cast("dict[str, Any]", meta_value)

    # Get file modification time for created timestamp
    try:
        mtime = skill_path.stat().st_mtime
        created = datetime.fromtimestamp(mtime, tz=UTC).isoformat()
    except OSError:
        created = datetime.now(tz=UTC).isoformat()

    return GraphNode(
        id=f"/{name}",
        type="skill",
        content=description,
        source_file=str(skill_path),
        created=created,
        metadata=metadata_section,
    )


def extract_all_skills(skills_dir: Path) -> list[GraphNode]:
    """Extract metadata from all skills in a directory.

    Searches for SKILL.md files in subdirectories of the given path.

    Args:
        skills_dir: Path to skills directory (e.g., .claude/skills/).

    Returns:
        List of GraphNode for each valid skill found.

    Examples:
        >>> nodes = extract_all_skills(Path(".claude/skills"))
        >>> len(nodes) > 0
        True
    """
    if not skills_dir.exists():
        return []

    nodes: list[GraphNode] = []

    for skill_md in skills_dir.glob("*/SKILL.md"):
        node = extract_skill_metadata(skill_md)
        if node is not None:
            nodes.append(node)

    return nodes
