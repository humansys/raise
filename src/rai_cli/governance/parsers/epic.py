"""Parser for epic scope documents.

Extracts detailed Epic and Story concepts from work/epics/*/scope.md files.
"""

from __future__ import annotations

import re
from pathlib import Path

from rai_cli.adapters.models import ArtifactLocator, CoreArtifactType
from rai_cli.compat import portable_path
from rai_cli.context.models import GraphNode
from rai_cli.governance.models import Concept, ConceptType
from rai_cli.governance.parsers._convert import concept_to_node
from rai_cli.governance.parsers.backlog import normalize_status


def _extract_frontmatter(text: str) -> dict[str, str | None]:
    """Extract frontmatter metadata from epic scope document.

    Parses blockquote lines like:
    > **Status:** COMPLETE
    > **Target:** Feb 9, 2026

    Args:
        text: Full epic scope document content.

    Returns:
        Dictionary with extracted metadata (status, target, branch, etc.).
    """
    metadata: dict[str, str | None] = {
        "status": None,
        "target": None,
        "branch": None,
        "created": None,
        "completed": None,
    }

    # Pattern: > **Key:** Value or > Key: Value
    # Note: Markdown bold is **Key:** with colon inside, so pattern is :**
    frontmatter_pattern = re.compile(
        r"^>\s*\*?\*?([^:*]+?):\*?\*?\s*(.+)$", re.MULTILINE
    )

    for match in frontmatter_pattern.finditer(text):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()

        if key == "status":
            # Remove emoji and extra text after status
            status_match = re.match(r"^([A-Z]+)", value)
            if status_match:
                metadata["status"] = status_match.group(1).lower()
            else:
                metadata["status"] = normalize_status(value)
        elif key == "target":
            metadata["target"] = value
        elif key == "branch":
            metadata["branch"] = value
        elif key == "created":
            metadata["created"] = value
        elif key == "completed":
            metadata["completed"] = value

    return metadata


def extract_epic_details(
    file_path: Path, project_root: Path | None = None
) -> Concept | None:
    """Extract detailed Epic concept from epic scope document.

    Parses the epic scope document to extract full epic metadata including
    objective, status, target date, and story count.

    Args:
        file_path: Path to epic scope document (work/epics/*/scope.md).
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.parent.

    Returns:
        Epic Concept with full details if successfully parsed, None if file
        doesn't exist or can't be parsed.

    Examples:
        >>> from pathlib import Path
        >>> scope_doc = Path("work/epics/e08-backlog/scope.md")
        >>> epic = extract_epic_details(scope_doc)
        >>> epic.id
        'epic-e8'
        >>> epic.metadata["name"]
        'Work Tracking Graph'
    """
    if not file_path.exists():
        return None

    if project_root is None:
        # work/epics/e08-name/scope.md -> project root is 4 levels up
        project_root = file_path.parent.parent.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract epic ID from parent directory: e08-backlog -> E8
    parent_dir = file_path.parent.name  # e08-backlog
    epic_id_match = re.search(r"^e(\d+)", parent_dir, re.IGNORECASE)
    if not epic_id_match:
        return None

    epic_id = f"E{int(epic_id_match.group(1))}"  # E8 (normalize: e08 -> E8)

    # Extract epic name from H1: # Epic E8: Work Tracking Graph - Scope
    epic_name = None
    header_line = 1
    for i, line in enumerate(lines, 1):
        match = re.match(r"^#\s*Epic\s+E\d+[:\s]+(.+?)(?:\s*-\s*Scope)?$", line)
        if match:
            epic_name = match.group(1).strip()
            header_line = i
            break

    if not epic_name:
        # Fallback: use epic ID
        epic_name = f"Epic {epic_id}"

    # Extract frontmatter
    frontmatter = _extract_frontmatter(text)

    # Count stories in table
    story_count = len(re.findall(r"^\|\s*F\d+\.\d+\s*\|", text, re.MULTILINE))

    # Calculate relative file path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    # Extract objective (first paragraph after ## Objective)
    objective = None
    objective_match = re.search(
        r"##\s*Objective\s*\n+(.+?)(?=\n\n|\n##|\Z)", text, re.DOTALL
    )
    if objective_match:
        objective = objective_match.group(1).strip()
        # Truncate if too long
        if len(objective) > 300:
            objective = objective[:297] + "..."

    # Build content summary
    content = f"Epic {epic_id}: {epic_name}"
    if frontmatter["status"]:
        content += f" ({frontmatter['status']})"
    if objective:
        content += f". {objective}"

    return Concept(
        id=f"epic-{epic_id.lower()}",
        type=ConceptType.EPIC,
        file=relative_path,
        section=f"Epic {epic_id}: {epic_name}",
        lines=(header_line, min(header_line + 20, len(lines))),
        content=content[:500],  # Truncate to 500 chars
        metadata={
            "epic_id": epic_id,
            "name": epic_name,
            "status": frontmatter["status"] or "draft",
            "target": frontmatter["target"],
            "branch": frontmatter["branch"],
            "created": frontmatter["created"],
            "completed": frontmatter["completed"],
            "story_count": story_count,
            "scope_doc": relative_path,
        },
    )


def extract_stories(file_path: Path, project_root: Path | None = None) -> list[Concept]:
    """Extract Story concepts from epic scope document.

    Parses the "Stories" table to extract story metadata. Supports
    various table formats found in epic scope documents.

    Args:
        file_path: Path to epic scope document (work/epics/*/scope.md).
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.parent.parent.

    Returns:
        List of Story Concepts extracted from the table. Returns empty list
        if file doesn't exist or no stories found.

    Examples:
        >>> from pathlib import Path
        >>> scope_doc = Path("work/epics/e08-backlog/scope.md")
        >>> stories = extract_stories(scope_doc)
        >>> len(stories)
        4
        >>> features[0].metadata["story_id"]
        'F8.1'
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract epic ID from parent directory: e08-backlog -> E8
    parent_dir = file_path.parent.name
    epic_id_match = re.search(r"^e(\d+)", parent_dir, re.IGNORECASE)
    epic_id = f"E{int(epic_id_match.group(1))}" if epic_id_match else "E0"

    # Calculate relative file path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    concepts: list[Concept] = []

    # Parse story table rows
    # Pattern variants:
    # | F8.1 | Backlog Parser | S | Pending | Description |
    # | F8.1 | Backlog Parser | S | 2 | Pending | Description |
    # | F2.1 | Concept Extraction | 3 | ✅ Complete | 52 min | 3.5x |
    story_pattern = re.compile(
        r"^\|\s*(F\d+\.\d+)\s*\|"  # Story ID
        r"\s*\*?\*?([^|*]+?)\*?\*?\s*\|"  # Story name (with optional bold)
        r"\s*([^|]+?)\s*\|"  # Size or SP
        r"\s*([^|]+?)\s*\|"  # Status or SP (depends on format)
        r"(?:\s*([^|]*?)\s*\|)?"  # Optional: Description or Status or Time
    )

    for i, line in enumerate(lines, 1):
        match = story_pattern.match(line)
        if match:
            story_id = match.group(1).strip()
            name = match.group(2).strip()
            col3 = match.group(3).strip()
            col4 = match.group(4).strip()
            col5 = match.group(5).strip() if match.group(5) else ""

            # Determine column mapping based on content
            # If col3 looks like size (XS/S/M/L) or small number (1-3), it's size
            # If col4 looks like status, use col3 as size and col4 as status
            size = None
            status = None
            sp = None
            description = None

            # Check if col3 is size (XS/S/M/L)
            if re.match(r"^(XS|S|M|L)$", col3, re.IGNORECASE):
                size = col3.upper()
                # col4 could be SP or Status
                if re.match(r"^\d+$", col4):
                    sp = int(col4)
                    status = normalize_status(col5) if col5 else "pending"
                else:
                    status = normalize_status(col4)
                    description = col5
            # Check if col3 is SP (number)
            elif re.match(r"^\d+$", col3):
                sp = int(col3)
                status = normalize_status(col4)
                # col5 might be actual time or description
                if col5 and not re.match(r"^\d+\s*min", col5):
                    description = col5
            else:
                # Fallback: treat col3 as size text, col4 as status
                size = col3[:2].upper() if col3 else None
                status = normalize_status(col4)
                description = col5

            # Build content
            content = f"{story_id}: {name}"
            if status:
                content += f" ({status})"
            if description:
                content += f" - {description}"

            concept = Concept(
                id=f"story-{story_id.lower().replace('.', '-')}",
                type=ConceptType.STORY,
                file=relative_path,
                section=f"{story_id}: {name}",
                lines=(i, i),
                content=content[:500],
                metadata={
                    "story_id": story_id,
                    "name": name,
                    "status": status or "pending",
                    "size": size,
                    "sp": sp,
                    "description": description,
                    "epic_id": epic_id,
                },
            )
            concepts.append(concept)

    return concepts


class EpicScopeParser:
    """GovernanceParser wrapper for Epic scope docs (details + stories)."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match Epic scope artifact type."""
        return locator.artifact_type == CoreArtifactType.EPIC_SCOPE

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse Epic scope file into GraphNode list (epic + stories)."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        nodes: list[GraphNode] = []
        epic_detail = extract_epic_details(path, root)
        if epic_detail:
            nodes.append(concept_to_node(epic_detail))
        stories = extract_stories(path, root)
        nodes.extend(concept_to_node(s) for s in stories)
        return nodes
