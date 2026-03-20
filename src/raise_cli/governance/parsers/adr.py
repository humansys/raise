"""Parser for Architecture Decision Records (ADRs).

Extracts decisions from ADR markdown files with YAML frontmatter.
Supports ADRs in governance/adrs/ (root and v2 subdirectory).
Legacy v1 ADRs without frontmatter are skipped.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_core.graph.models import GraphNode


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, int]:
    r"""Parse YAML frontmatter from markdown text.

    Args:
        text: Full markdown text content.

    Returns:
        Tuple of (frontmatter dict, remaining content, frontmatter end line).
        Returns empty dict if no frontmatter found.

    Examples:
        >>> text = "---\nid: ADR-001\n---\n# Title"
        >>> fm, content, end_line = _parse_frontmatter(text)
        >>> fm["id"]
        'ADR-001'
    """
    if not text.startswith("---"):
        return {}, text, 0

    # Find closing ---
    lines = text.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, text, 0

    # Parse YAML
    frontmatter_text = "\n".join(lines[1:end_idx])
    try:
        loaded = yaml.safe_load(frontmatter_text)
        frontmatter: dict[str, Any] = cast("dict[str, Any]", loaded) if loaded else {}
    except yaml.YAMLError:
        return {}, text, 0

    remaining = "\n".join(lines[end_idx + 1 :])
    return frontmatter, remaining, end_idx + 1


def _extract_decision_summary(content: str) -> str:
    r"""Extract the Decision section content as summary.

    Args:
        content: Markdown content after frontmatter.

    Returns:
        Decision section content, truncated to ~500 chars.

    Examples:
        >>> content = "## Context\nSome context.\n## Decision\nWe decided X."
        >>> _extract_decision_summary(content)
        'We decided X.'
    """
    # Look for ## Decision or ## Decisión section
    match = re.search(
        r"^##\s+(?:Decision|Decisión)\s*\n(.*?)(?=(?:^##\s|\Z))",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    if match:
        decision_text = match.group(1).strip()
        # Truncate if too long
        if len(decision_text) > 500:
            decision_text = decision_text[:500] + "..."
        return decision_text

    # Fallback: use first paragraph after title
    lines = content.strip().split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            # Skip title, get next non-empty content
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip() and not lines[j].startswith("#"):
                    return lines[j].strip()[:500]

    return ""


def extract_decisions(
    directory: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract ADR decisions from a directory.

    Parses ADR files with YAML frontmatter containing id, title, status, date.
    Files without frontmatter are skipped (legacy v1 format).

    Args:
        directory: Directory containing ADR markdown files.
        project_root: Project root for relative path calculation.

    Returns:
        List of Concept objects representing decisions.

    Examples:
        >>> from pathlib import Path
        >>> decisions = extract_decisions(Path("governance/adrs"))
        >>> len(decisions) > 0
        True
        >>> decisions[0].type
        <ConceptType.DECISION: 'decision'>
    """
    if not directory.exists():
        return []

    if project_root is None:
        project_root = directory.parent

    concepts: list[Concept] = []

    # Process ADR files in directory
    for adr_file in sorted(directory.glob("adr-*.md")):
        concept = extract_decision_from_file(adr_file, project_root)
        if concept:
            concepts.append(concept)

    return concepts


def extract_decision_from_file(
    file_path: Path, project_root: Path | None = None
) -> Concept | None:
    """Extract a single ADR decision from a file.

    Args:
        file_path: Path to ADR markdown file.
        project_root: Project root for relative path calculation.

    Returns:
        Concept object if valid ADR with frontmatter, None otherwise.

    Examples:
        >>> from pathlib import Path
        >>> decision = extract_decision_from_file(Path("governance/adrs/adr-019.md"))
        >>> decision.id if decision else None
        'ADR-019'
    """
    if not file_path.exists():
        return None

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    frontmatter, content, _ = _parse_frontmatter(text)

    # Skip files without frontmatter (legacy format)
    if not frontmatter:
        return None

    # Required fields
    adr_id = frontmatter.get("id")
    if not adr_id:
        return None

    title = frontmatter.get("title", "")
    status = frontmatter.get("status", "unknown")
    date = frontmatter.get("date", "")
    related_to = frontmatter.get("related_to", [])

    # Extract decision summary
    decision_summary = _extract_decision_summary(content)

    # Build content string
    content_str = f"{title}"
    if decision_summary:
        content_str = f"{title} — {decision_summary}"

    # Truncate if needed
    if len(content_str) > 500:
        content_str = content_str[:500] + "..."

    # Calculate relative path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    # Count lines for line range
    total_lines = len(text.split("\n"))

    return Concept(
        id=f"decision-{adr_id.lower()}",
        type=ConceptType.DECISION,
        file=relative_path,
        section=f"{adr_id}: {title}",
        lines=(1, total_lines),
        content=content_str,
        metadata={
            "adr_id": adr_id,
            "title": title,
            "status": status,
            "date": str(date) if date else "",
            "related_to": related_to if isinstance(related_to, list) else [],
        },
    )


def extract_all_decisions(project_root: Path | None = None) -> list[Concept]:
    """Extract all ADR decisions from standard locations.

    Searches governance/adrs/ (root) and governance/adrs/v2/ for ADRs.
    Skips governance/adrs/v1/ (legacy format without frontmatter).

    Args:
        project_root: Project root directory.

    Returns:
        List of all extracted decision Concepts.

    Examples:
        >>> from pathlib import Path
        >>> decisions = extract_all_decisions(Path("."))
        >>> len(decisions) >= 20
        True
    """
    if project_root is None:
        project_root = Path.cwd()

    concepts: list[Concept] = []

    # Root level ADRs (current series)
    root_decisions = project_root / "governance" / "adrs"
    if root_decisions.exists():
        concepts.extend(extract_decisions(root_decisions, project_root))

    # v2 subdirectory ADRs
    v2_decisions = project_root / "governance" / "adrs" / "v2"
    if v2_decisions.exists():
        concepts.extend(extract_decisions(v2_decisions, project_root))

    # Note: v1 is intentionally skipped (legacy format without frontmatter)

    return concepts


class AdrParser:
    """GovernanceParser wrapper for ADR decisions. Per-file parsing."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match ADR artifact type."""
        return locator.artifact_type == CoreArtifactType.ADR

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse single ADR file pointed to by locator."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        concept = extract_decision_from_file(path, root)
        return [concept_to_node(concept)] if concept else []
