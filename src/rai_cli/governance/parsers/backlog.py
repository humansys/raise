"""Parser for project backlog files.

Extracts Project and Epic concepts from governance/backlog.md.
"""

from __future__ import annotations

import re
from pathlib import Path

from rai_cli.adapters.models import ArtifactLocator, CoreArtifactType
from rai_cli.compat import portable_path
from rai_cli.governance.models import Concept, ConceptType
from rai_cli.governance.parsers._convert import concept_to_node
from rai_core.graph.models import GraphNode


def normalize_status(raw: str) -> str:
    """Normalize epic status to standard values.

    Converts various status representations (emoji, text) to lowercase
    standard values compatible with WorkStatus enum.

    Args:
        raw: Raw status string from backlog table.

    Returns:
        Normalized status: 'complete', 'draft', 'deferred', 'in_progress', or 'pending'.

    Examples:
        >>> normalize_status("✅ Complete")
        'complete'
        >>> normalize_status("📋 DRAFT")
        'draft'
        >>> normalize_status("Deferred")
        'deferred'
        >>> normalize_status("→ Replaced by E9")
        'deferred'
    """
    raw_lower = raw.lower().strip()
    if "complete" in raw_lower or "✅" in raw:
        return "complete"
    if "draft" in raw_lower or "📋" in raw:
        return "draft"
    if "deferred" in raw_lower or "replaced" in raw_lower or "→" in raw:
        return "deferred"
    if "progress" in raw_lower:
        return "in_progress"
    if "planning" in raw_lower:
        return "planning"
    return "pending"


def _extract_current_focus(text: str) -> str | None:
    """Extract current epic focus from backlog content.

    Looks for patterns like:
    - **F&F Scope (Feb 9):** E8 → E7 → E9
    - Epic: E8

    Args:
        text: Full backlog file content.

    Returns:
        Epic ID (e.g., 'E8') if found, None otherwise.
    """
    # Try F&F Scope pattern first
    match = re.search(r"\*\*F&F Scope[^:]*:\*\*\s*(E\d+)", text)
    if match:
        return match.group(1)

    # Try explicit Epic: pattern
    match = re.search(r"^Epic:\s*(E\d+)", text, re.MULTILINE)
    if match:
        return match.group(1)

    # Try "P0 (next)" pattern in table
    match = re.search(
        r"\|\s*(E\d+)\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*P0\s*\(next\)", text
    )
    if match:
        return match.group(1)

    return None


def _extract_target_date(text: str) -> str | None:
    """Extract target date from backlog content.

    Looks for patterns like:
    - **F&F Scope (Feb 9):**
    - Target: 2026-02-09

    Args:
        text: Full backlog file content.

    Returns:
        Date string if found, None otherwise.
    """
    # Try F&F Scope with date
    match = re.search(r"\*\*F&F Scope\s*\(([^)]+)\)", text)
    if match:
        return match.group(1)

    # Try explicit Target: pattern
    match = re.search(r"Target:\s*(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)

    return None


def extract_project(
    file_path: Path, project_root: Path | None = None
) -> Concept | None:
    """Extract Project concept from backlog.md file.

    Parses the backlog file header to extract project metadata including
    name, status, current focus, and target date.

    Args:
        file_path: Path to backlog.md file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.

    Returns:
        Project Concept if successfully parsed, None if file doesn't exist
        or can't be parsed.

    Examples:
        >>> from pathlib import Path
        >>> backlog = Path("governance/backlog.md")
        >>> project = extract_project(backlog)
        >>> project.id
        'project-raise-cli'
        >>> project.metadata["current_epic"]
        'E8'
    """
    if not file_path.exists():
        return None

    if project_root is None:
        # governance/backlog.md -> project root is 2 levels up
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract project name from H1: # Backlog: {name}
    project_name = None
    header_line = 1
    for i, line in enumerate(lines, 1):
        match = re.match(r"^# Backlog:\s*(.+)$", line)
        if match:
            project_name = match.group(1).strip()
            header_line = i
            break

    # Fallback: extract from path
    if not project_name:
        project_name = file_path.parent.name

    # Extract metadata
    current_epic = _extract_current_focus(text)
    target_date = _extract_target_date(text)

    # Count epics in table
    epic_count = len(re.findall(r"^\|\s*E\d+\s*\|", text, re.MULTILINE))

    # Calculate relative file path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    # Extract frontmatter for status
    status = "active"
    status_match = re.search(r">\s*\*\*Status\*\*:\s*(\w+)", text)
    if status_match:
        status = status_match.group(1).lower()

    # Build content summary
    content = f"Project backlog for {project_name}"
    if current_epic:
        content += f". Current focus: {current_epic}"
    if target_date:
        content += f". Target: {target_date}"

    return Concept(
        id=f"project-{project_name}",
        type=ConceptType.PROJECT,
        file=relative_path,
        section=f"Backlog: {project_name}",
        lines=(header_line, min(header_line + 10, len(lines))),
        content=content,
        metadata={
            "name": project_name,
            "status": status,
            "current_epic": current_epic,
            "target_date": target_date,
            "epic_count": epic_count,
        },
    )


def extract_epics(file_path: Path, project_root: Path | None = None) -> list[Concept]:
    """Extract Epic concepts from backlog.md Epics Overview table.

    Parses the "Epics Overview" table to extract epic metadata. This extracts
    the epic index only - full epic details come from epic scope docs (F8.2).

    Args:
        file_path: Path to backlog.md file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.parent.parent.

    Returns:
        List of Epic Concepts extracted from the table. Returns empty list
        if file doesn't exist or no epics found.

    Examples:
        >>> from pathlib import Path
        >>> backlog = Path("governance/backlog.md")
        >>> epics = extract_epics(backlog)
        >>> len(epics)
        9
        >>> epics[0].metadata["epic_id"]
        'E1'
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract project name from H1: # Backlog: {name}
    project_name = file_path.parent.name  # Fallback
    for line in lines:
        h1_match = re.match(r"^# Backlog:\s*(.+)$", line)
        if h1_match:
            project_name = h1_match.group(1).strip()
            break

    # Calculate relative file path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    concepts: list[Concept] = []

    # Parse epic table rows
    # Pattern: | E1 | **Name** or Name | Status | `scope.md` or — | Priority |
    epic_pattern = re.compile(
        r"^\|\s*(E\d+)\s*\|"  # Epic ID
        r"\s*\*?\*?([^|*]+?)\*?\*?\s*\|"  # Epic name (with optional bold)
        r"\s*([^|]+?)\s*\|"  # Status
        r"\s*([^|]*?)\s*\|"  # Scope doc (optional)
        r"\s*([^|]*?)\s*\|"  # Priority (optional)
    )

    for i, line in enumerate(lines, 1):
        match = epic_pattern.match(line)
        if match:
            epic_id = match.group(1).strip()
            name = match.group(2).strip()
            raw_status = match.group(3).strip()
            scope_doc = match.group(4).strip()
            priority = match.group(5).strip()

            # Clean up scope doc (remove backticks)
            scope_doc = scope_doc.strip("`").strip()
            if scope_doc == "—" or scope_doc == "-" or not scope_doc:
                scope_doc = None

            # Clean up priority
            priority = priority.strip("*").strip()
            if priority == "—" or priority == "-" or not priority:
                priority = None

            # Normalize status
            status = normalize_status(raw_status)

            # Build content
            content = f"{name} - {raw_status.strip()}"

            concept = Concept(
                id=f"epic-{epic_id.lower()}",
                type=ConceptType.EPIC,
                file=relative_path,
                section=f"{epic_id}: {name}",
                lines=(i, i),
                content=content,
                metadata={
                    "epic_id": epic_id,
                    "name": name,
                    "status": status,
                    "scope_doc": scope_doc,
                    "priority": priority,
                    "project_id": project_name,
                },
            )
            concepts.append(concept)

    return concepts


class BacklogParser:
    """GovernanceParser wrapper for Backlog (project + epics)."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match Backlog artifact type."""
        return locator.artifact_type == CoreArtifactType.BACKLOG

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse Backlog file into GraphNode list (project + epics)."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        nodes: list[GraphNode] = []
        project = extract_project(path, root)
        if project:
            nodes.append(concept_to_node(project))
        epics = extract_epics(path, root)
        nodes.extend(concept_to_node(e) for e in epics)
        return nodes
