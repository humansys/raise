"""Parser for roadmap files.

Extracts Release concepts from governance/roadmap.md.
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


def extract_releases(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract Release concepts from roadmap.md Releases table.

    Parses the "Releases" table to extract release metadata including
    ID, name, target date, status, and associated epics.

    Args:
        file_path: Path to roadmap.md file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.

    Returns:
        List of Release Concepts extracted from the table. Returns empty list
        if file doesn't exist or no releases found.
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return []

    lines = text.split("\n")

    # Calculate relative file path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    concepts: list[Concept] = []

    # Parse release table rows
    # Pattern: | REL-V2.0 | V2.0 Open Core | 2026-02-15 | In Progress | E18 |
    release_pattern = re.compile(
        r"^\|\s*(REL-[^\s|]+)\s*\|"  # Release ID
        r"\s*([^|]+?)\s*\|"  # Release name
        r"\s*([^|]+?)\s*\|"  # Target date
        r"\s*([^|]+?)\s*\|"  # Status
        r"\s*([^|]*?)\s*\|"  # Epics (optional)
    )

    for i, line in enumerate(lines, 1):
        match = release_pattern.match(line)
        if match:
            release_id = match.group(1).strip()
            name = match.group(2).strip()
            target = match.group(3).strip()
            raw_status = match.group(4).strip()
            raw_epics = match.group(5).strip()

            # Normalize status
            status = normalize_status(raw_status)

            # Parse epics list
            epics: list[str] = []
            if raw_epics:
                epics = [e.strip() for e in raw_epics.split(",") if e.strip()]

            # Build content summary
            content = f"{name} — {raw_status}. Target: {target}"

            concept = Concept(
                id=f"rel-{release_id.removeprefix('REL-').lower()}",
                type=ConceptType.RELEASE,
                file=relative_path,
                section=f"{release_id}: {name}",
                lines=(i, i),
                content=content,
                metadata={
                    "release_id": release_id,
                    "name": name,
                    "target": target,
                    "status": status,
                    "epics": epics,
                },
            )
            concepts.append(concept)

    return concepts


class RoadmapParser:
    """GovernanceParser wrapper for Roadmap releases."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match Roadmap artifact type."""
        return locator.artifact_type == CoreArtifactType.ROADMAP

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse Roadmap file into GraphNode list."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        concepts = extract_releases(path, root)
        return [concept_to_node(c) for c in concepts]
