"""Parser for Constitution documents.

Extracts principles in §N format from Constitution markdown files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.core.text import sanitize_id
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_core.graph.models import GraphNode


def extract_principles(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract §N principles from Constitution markdown file.

    Parses Constitution markdown files looking for principle sections with the
    format "### §N. Title" and extracts the principle content along with metadata.

    Args:
        file_path: Path to Constitution markdown file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.

    Returns:
        List of Concept objects representing principles.

    Examples:
        >>> from pathlib import Path
        >>> constitution = Path("framework/reference/constitution.md")
        >>> principles = extract_principles(constitution)
        >>> len(principles)
        8
        >>> principles[0].type
        <ConceptType.PRINCIPLE: 'principle'>
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    concepts: list[Concept] = []

    for i, line in enumerate(lines, 1):
        # Match principle headers: ### §2. Governance as Code
        match = re.match(r"^### §(\d+)\.\s*(.+)$", line)

        if match:
            principle_num = match.group(1)  # "2"
            principle_name = match.group(2).strip()  # "Governance as Code"

            # Extract section content until next ### heading
            content_lines: list[str] = []
            j = i
            while j < len(lines) and not (lines[j].startswith("###") and j > i):
                content_lines.append(lines[j])
                j += 1

            # Truncate to first ~30 lines or 500 chars
            content = "\n".join(content_lines[:30])
            if len(content) > 500:
                content = content[:500] + "..."

            # Generate ID from principle name
            principle_id = sanitize_id(principle_name)

            # Calculate relative file path
            try:
                relative_path = portable_path(file_path, project_root)
            except ValueError:
                relative_path = file_path.name

            metadata: dict[str, Any] = {
                "principle_number": principle_num,
                "principle_name": principle_name,
            }

            # Tag core principles as always_on (S15.8)
            if principle_num in {"1", "3", "7"}:
                metadata["always_on"] = True

            concept = Concept(
                id=f"principle-{principle_id}",
                type=ConceptType.PRINCIPLE,
                file=relative_path,
                section=f"§{principle_num}. {principle_name}",
                lines=(i, min(i + len(content_lines[:30]), len(lines))),
                content=content.strip(),
                metadata=metadata,
            )
            concepts.append(concept)

    return concepts


class ConstitutionParser:
    """GovernanceParser wrapper for Constitution principles."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match Constitution artifact type."""
        return locator.artifact_type == CoreArtifactType.CONSTITUTION

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse Constitution file into GraphNode list."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        concepts = extract_principles(path, root)
        return [concept_to_node(c) for c in concepts]
