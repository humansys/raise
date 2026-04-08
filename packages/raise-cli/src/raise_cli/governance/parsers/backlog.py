"""Parser for project backlog files.

Extracts Project and Epic concepts from governance/backlog.md.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_core.graph.models import GraphNode


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

    # Count epics in table (both E{N} and [RAISE-XXX](url) formats)
    epic_count = len(
        re.findall(
            r"^\|\s*(?:E\d+|\[[A-Z]+-\d+\])\s*(?:\([^)]+\)\s*)?\|", text, re.MULTILINE
        )
    )

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


def _should_yield_to_scope_parser(epic_id: str, project_root: Path) -> bool:
    """Check if this epic has a scope doc and should be parsed there instead.

    The scope doc is the authoritative source (richer data); the backlog
    row is only an index entry. Without this check, both BacklogParser
    and EpicScopeParser produce the same node ID, causing duplicate
    warnings in ``rai graph build``.

    Only applies to local epic IDs (E{N}), never to Jira keys (RAISE-275).

    Args:
        epic_id: Epic identifier (e.g., 'E8', 'RAISE-275').
        project_root: Project root directory.

    Returns:
        True if a scope doc exists for this epic and extraction should be skipped.
    """
    e_match = re.match(r"^E0*(\d+)$", epic_id, re.IGNORECASE)
    if not e_match:
        return False

    canon = int(e_match.group(1))  # E08 -> 8, E1 -> 1
    return any(
        (m := re.search(r"^e0*(\d+)", d.name, re.IGNORECASE))
        and int(m.group(1)) == canon
        for d in project_root.glob("work/epics/e*")
        if (d / "scope.md").exists()
    )


def _build_epic_concept(
    match: re.Match[str],
    line_num: int,
    relative_path: str,
    project_name: str,
) -> Concept:
    """Build an Epic Concept from a regex match on a backlog table row.

    Args:
        match: Regex match with groups for epic ID, name, status, scope doc, priority.
        line_num: Line number of the match in the file.
        relative_path: Relative path to the backlog file.
        project_name: Project name for metadata.

    Returns:
        Epic Concept.
    """
    epic_id = (match.group(1) or match.group(2)).strip()
    name = match.group(3).strip()
    raw_status = match.group(4).strip()
    scope_doc: str | None = match.group(5).strip()
    priority: str | None = match.group(6).strip()

    # Clean up scope doc (remove backticks)
    scope_doc = scope_doc.strip("`").strip() if scope_doc else None
    if scope_doc in {"—", "-", ""}:
        scope_doc = None

    # Clean up priority
    priority = priority.strip("*").strip() if priority else None
    if priority in {"—", "-", ""}:
        priority = None

    status = normalize_status(raw_status)
    content = f"{name} - {raw_status.strip()}"

    return Concept(
        id=f"epic-{epic_id.lower()}",
        type=ConceptType.EPIC,
        file=relative_path,
        section=f"{epic_id}: {name}",
        lines=(line_num, line_num),
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

    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    concepts: list[Concept] = []

    epic_pattern = re.compile(
        r"^\|\s*"
        r"(?:\[([A-Z]+-\d+)\]\([^)]+\)|(E\d+))"
        r"\s*\|"
        r"\s*\*?\*?([^|*]+?)\*?\*?\s*\|"
        r"\s*([^|]+?)\s*\|"
        r"\s*([^|]*?)\s*\|"
        r"\s*([^|]*?)\s*\|"
    )

    for i, line in enumerate(lines, 1):
        match = epic_pattern.match(line)
        if not match:
            continue

        epic_id = (match.group(1) or match.group(2)).strip()
        if _should_yield_to_scope_parser(epic_id, project_root):
            continue

        concepts.append(_build_epic_concept(match, i, relative_path, project_name))

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
