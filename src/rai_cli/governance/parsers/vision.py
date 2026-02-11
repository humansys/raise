"""Parser for Vision documents.

Extracts outcomes from Vision markdown tables.
"""

from __future__ import annotations

import re
from pathlib import Path

from rai_cli.core.text import sanitize_id
from rai_cli.governance.models import Concept, ConceptType


def extract_outcomes(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract outcomes from Vision markdown tables.

    Parses Vision markdown files looking for tables with bold outcome names
    in the first column and descriptions in the second column.

    Args:
        file_path: Path to Vision markdown file.
        project_root: Project root for relative path calculation.
            If None, uses file_path.parent.parent.

    Returns:
        List of Concept objects representing outcomes.

    Examples:
        >>> from pathlib import Path
        >>> vision = Path("governance/vision.md")
        >>> outcomes = extract_outcomes(vision)
        >>> len(outcomes)
        7
        >>> outcomes[0].type
        <ConceptType.OUTCOME: 'outcome'>
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent

    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    concepts: list[Concept] = []

    in_outcomes_table = False

    for i, line in enumerate(lines, 1):
        # Detect outcomes table header (only if not already in table)
        if (
            not in_outcomes_table
            and "| **" in line
            and ("outcome" in line.lower() or "context" in line.lower())
        ):
            in_outcomes_table = True
            continue

        if in_outcomes_table:
            # Parse table row: | **Outcome Name** | Description |
            match = re.match(r"\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|", line)

            if match:
                outcome_name = match.group(1).strip()
                description = match.group(2).strip()

                # Generate ID from name
                outcome_id = sanitize_id(outcome_name)

                # Calculate relative file path
                try:
                    relative_path = str(file_path.relative_to(project_root))
                except ValueError:
                    relative_path = file_path.name

                concept = Concept(
                    id=f"outcome-{outcome_id}",
                    type=ConceptType.OUTCOME,
                    file=relative_path,
                    section=outcome_name,
                    lines=(i, i),
                    content=description,
                    metadata={"outcome_name": outcome_name},
                )
                concepts.append(concept)

            # End of table: empty line or separator
            if line.strip() == "" or (line.startswith("|") and "---" in line):
                continue
            # Non-table line: exit table mode
            elif not line.startswith("|"):
                in_outcomes_table = False

    return concepts
