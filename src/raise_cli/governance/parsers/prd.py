"""Parser for PRD (Product Requirements Document) files.

Extracts requirements in RF-XX format from PRD markdown files.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_core.graph.models import GraphNode


def extract_requirements(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract RF-XX requirements from PRD markdown file.

    Parses PRD markdown files looking for requirement sections with the
    format "### RF-XX: Title" and extracts the requirement content along
    with metadata.

    Args:
        file_path: Path to PRD markdown file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.

    Returns:
        List of Concept objects representing requirements.

    Examples:
        >>> from pathlib import Path
        >>> prd = Path("governance/prd.md")
        >>> requirements = extract_requirements(prd)
        >>> len(requirements)
        8
        >>> requirements[0].id
        'req-rf-01'
        >>> requirements[0].metadata["requirement_id"]
        'RF-01'
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    concepts: list[Concept] = []

    for i, line in enumerate(lines, 1):
        # Match requirement sections: ### RF-05: Title
        match = re.match(r"^### (RF-\d+):\s*(.+)$", line)

        if match:
            req_id = match.group(1)  # "RF-05"
            title = match.group(2).strip()  # "Golden Context Generation"

            # Extract section content until next ### heading
            content_lines: list[str] = []
            j = i
            while j < len(lines) and not lines[j].startswith("###"):
                content_lines.append(lines[j])
                j += 1

            # Truncate to first ~20 lines or 500 chars
            content = "\n".join(content_lines[:20])
            if len(content) > 500:
                content = content[:500] + "..."

            # Generate ID from requirement ID
            concept_id = f"req-{req_id.lower()}"

            # Calculate relative file path
            try:
                relative_path = portable_path(file_path, project_root)
            except ValueError:
                # If file_path not relative to project_root, use file name
                relative_path = file_path.name

            concept = Concept(
                id=concept_id,
                type=ConceptType.REQUIREMENT,
                file=relative_path,
                section=f"{req_id}: {title}",
                lines=(i, min(i + len(content_lines[:20]), len(lines))),
                content=content.strip(),
                metadata={"requirement_id": req_id, "title": title},
            )
            concepts.append(concept)

    return concepts


class PrdParser:
    """GovernanceParser wrapper for PRD requirements."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match PRD artifact type."""
        return locator.artifact_type == CoreArtifactType.PRD

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse PRD file into GraphNode list."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        concepts = extract_requirements(path, root)
        return [concept_to_node(c) for c in concepts]
