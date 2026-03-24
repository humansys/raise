"""Parser for epic scope documents.

Extracts detailed Epic and Story concepts from work/epics/*/scope.md files.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_cli.governance.parsers.backlog import normalize_status
from raise_core.graph.models import GraphNode


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


def _parse_epic_id_and_name(
    parent_dir: str, lines: list[str]
) -> tuple[str, str, int] | None:
    """Parse epic ID and name from directory name and H1 header.

    Args:
        parent_dir: Epic directory name (e.g., 'e08-backlog').
        lines: Document lines.

    Returns:
        Tuple of (epic_id, epic_name, header_line) or None if ID not found.
    """
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
        epic_name = f"Epic {epic_id}"

    return epic_id, epic_name, header_line


def _build_epic_content(
    epic_id: str,
    epic_name: str,
    frontmatter: dict[str, str | None],
    text: str,
) -> str:
    """Build epic content summary from metadata and objective.

    Args:
        epic_id: Normalized epic ID (e.g., 'E8').
        epic_name: Epic name.
        frontmatter: Extracted frontmatter metadata.
        text: Full document text for objective extraction.

    Returns:
        Content summary string, truncated to 500 chars.
    """
    content = f"Epic {epic_id}: {epic_name}"
    if frontmatter["status"]:
        content += f" ({frontmatter['status']})"

    # Extract objective (first paragraph after ## Objective)
    objective_match = re.search(
        r"##\s*Objective\s*\n+(.+?)(?=\n\n|\n##|\Z)", text, re.DOTALL
    )
    if objective_match:
        objective = objective_match.group(1).strip()
        if len(objective) > 300:
            objective = objective[:297] + "..."
        content += f". {objective}"

    return content[:500]


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
        project_root = file_path.parent.parent.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    parsed = _parse_epic_id_and_name(file_path.parent.name, lines)
    if parsed is None:
        return None
    epic_id, epic_name, header_line = parsed

    frontmatter = _extract_frontmatter(text)
    story_count = len(re.findall(r"^\|\s*F\d+\.\d+\s*\|", text, re.MULTILINE))

    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    content = _build_epic_content(epic_id, epic_name, frontmatter, text)

    return Concept(
        id=f"epic-{epic_id.lower()}",
        type=ConceptType.EPIC,
        file=relative_path,
        section=f"Epic {epic_id}: {epic_name}",
        lines=(header_line, min(header_line + 20, len(lines))),
        content=content,
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


class _StoryColumns:
    """Parsed story table columns."""

    __slots__ = ("size", "status", "sp", "description")

    def __init__(
        self,
        size: str | None,
        status: str | None,
        sp: int | None,
        description: str | None,
    ) -> None:
        self.size = size
        self.status = status
        self.sp = sp
        self.description = description


def _parse_story_columns(col3: str, col4: str, col5: str) -> _StoryColumns:
    """Parse ambiguous story table columns into structured fields.

    Story tables have varying column layouts. This function determines
    which column holds size, SP, status, and description.

    Args:
        col3: Third table column value (size or SP).
        col4: Fourth table column value (status or SP).
        col5: Fifth table column value (description, status, or empty).

    Returns:
        Parsed story column data.
    """
    size: str | None = None
    status: str | None = None
    sp: int | None = None
    description: str | None = None

    if re.match(r"^(XS|S|M|L)$", col3, re.IGNORECASE):
        size = col3.upper()
        if re.match(r"^\d+$", col4):
            sp = int(col4)
            status = normalize_status(col5) if col5 else "pending"
        else:
            status = normalize_status(col4)
            description = col5
    elif re.match(r"^\d+$", col3):
        sp = int(col3)
        status = normalize_status(col4)
        if col5 and not re.match(r"^\d+\s*min", col5):
            description = col5
    else:
        size = col3[:2].upper() if col3 else None
        status = normalize_status(col4)
        description = col5

    return _StoryColumns(size=size, status=status, sp=sp, description=description)


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

    parent_dir = file_path.parent.name
    epic_id_match = re.search(r"^e(\d+)", parent_dir, re.IGNORECASE)
    epic_id = f"E{int(epic_id_match.group(1))}" if epic_id_match else "E0"

    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    concepts: list[Concept] = []

    story_pattern = re.compile(
        r"^\|\s*(F\d+\.\d+)\s*\|"
        r"\s*\*?\*?([^|*]+?)\*?\*?\s*\|"
        r"\s*([^|]+?)\s*\|"
        r"\s*([^|]+?)\s*\|"
        r"(?:\s*([^|]*?)\s*\|)?"
    )

    for i, line in enumerate(lines, 1):
        match = story_pattern.match(line)
        if not match:
            continue

        story_id = match.group(1).strip()
        name = match.group(2).strip()
        col5 = match.group(5).strip() if match.group(5) else ""
        cols = _parse_story_columns(
            match.group(3).strip(), match.group(4).strip(), col5
        )

        content = f"{story_id}: {name}"
        if cols.status:
            content += f" ({cols.status})"
        if cols.description:
            content += f" - {cols.description}"

        concepts.append(
            Concept(
                id=f"story-{story_id.lower().replace('.', '-')}",
                type=ConceptType.STORY,
                file=relative_path,
                section=f"{story_id}: {name}",
                lines=(i, i),
                content=content[:500],
                metadata={
                    "story_id": story_id,
                    "name": name,
                    "status": cols.status or "pending",
                    "size": cols.size,
                    "sp": cols.sp,
                    "description": cols.description,
                    "epic_id": epic_id,
                },
            )
        )

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
