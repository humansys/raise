"""Parser for Guardrails from governance documents.

Extracts guardrail rules from markdown tables in guardrails.md.
Supports sections: Code Quality, Testing, Security, Architecture,
Development Workflow, Inference Economy.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from raise_cli.governance.models import Concept, ConceptType


def _parse_guardrail_table(table_text: str, section: str) -> list[dict[str, Any]]:
    """Parse a markdown table of guardrails.

    Args:
        table_text: Markdown table text including header and separator rows.
        section: Section name (e.g., "Code Quality", "Testing").

    Returns:
        List of parsed guardrail dictionaries.

    Examples:
        >>> table = '''| ID | Level | Guardrail | Verificación |
        ... |----|-------|-----------|--------------|
        ... | `MUST-CODE-001` | MUST | Type hints | pyright |'''
        >>> results = _parse_guardrail_table(table, "Code Quality")
        >>> results[0]["id"]
        'MUST-CODE-001'
    """
    guardrails: list[dict[str, Any]] = []

    lines = table_text.strip().split("\n")
    if len(lines) < 3:  # Need header, separator, and at least one data row
        return guardrails

    # Skip header and separator
    for line in lines[2:]:
        if not line.strip() or line.strip().startswith("|-"):
            continue

        # Parse table row
        cells = [cell.strip() for cell in line.split("|")]
        # Remove empty first/last from | delimiters
        cells = [c for c in cells if c]

        if len(cells) < 4:
            continue

        # Extract ID (remove backticks)
        guardrail_id = cells[0].strip("`").strip()
        if not guardrail_id:
            continue

        # Extract other fields
        level = cells[1].strip() if len(cells) > 1 else ""
        description = cells[2].strip() if len(cells) > 2 else ""
        verification = cells[3].strip("`").strip() if len(cells) > 3 else ""
        derived_from = cells[4].strip() if len(cells) > 4 else ""

        guardrails.append(
            {
                "id": guardrail_id,
                "level": level,
                "description": description,
                "verification": verification,
                "derived_from": derived_from,
                "section": section,
            }
        )

    return guardrails


def _find_section_tables(content: str) -> list[tuple[str, str]]:
    """Find all section headers and their associated tables.

    Args:
        content: Full markdown file content.

    Returns:
        List of (section_name, table_text) tuples.

    Examples:
        >>> content = '''### Code Quality
        ... | ID | Level |
        ... |----|-------|
        ... | X | Y |'''
        >>> sections = _find_section_tables(content)
        >>> sections[0][0]
        'Code Quality'
    """
    sections: list[tuple[str, str]] = []

    # Pattern to match section headers (### Section Name)
    section_pattern = re.compile(r"^###\s+(.+?)$", re.MULTILINE)

    # Find all sections
    matches = list(section_pattern.finditer(content))

    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()

        # Find end of section (next ### or end of content)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        section_content = content[start:end]

        # Find table in section (starts with | ID or similar)
        table_match = re.search(
            r"(\|[^\n]+\|\n\|[-|\s]+\|\n(?:\|[^\n]+\|\n?)+)",
            section_content,
            re.MULTILINE,
        )

        if table_match:
            sections.append((section_name, table_match.group(1)))

    return sections


def extract_guardrails(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract guardrails from a guardrails markdown file.

    Parses tables in sections like Code Quality, Testing, Security.
    Each table row becomes a Concept with type GUARDRAIL.

    Args:
        file_path: Path to guardrails markdown file.
        project_root: Project root for relative path calculation.

    Returns:
        List of Concept objects representing guardrails.

    Examples:
        >>> from pathlib import Path
        >>> guardrails = extract_guardrails(Path("governance/guardrails.md"))
        >>> len(guardrails) > 0
        True
        >>> guardrails[0].type
        <ConceptType.GUARDRAIL: 'guardrail'>
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent  # governance/ -> root

    content = file_path.read_text(encoding="utf-8")
    concepts: list[Concept] = []

    # Find all section tables
    section_tables = _find_section_tables(content)

    # Calculate relative path
    try:
        relative_path = str(file_path.relative_to(project_root))
    except ValueError:
        relative_path = file_path.name

    # Track line numbers for each section
    lines = content.split("\n")

    for section_name, table_text in section_tables:
        # Find line number of section header
        section_line = 1
        for i, line in enumerate(lines, 1):
            if f"### {section_name}" in line:
                section_line = i
                break

        # Parse guardrails from table
        parsed = _parse_guardrail_table(table_text, section_name)

        for guardrail in parsed:
            guardrail_id = guardrail["id"]
            level = guardrail["level"]
            description = guardrail["description"]

            # Build content string
            content_str = f"[{level}] {description}"
            if guardrail["verification"]:
                content_str += f" — Verify: {guardrail['verification']}"

            # Truncate if needed
            if len(content_str) > 500:
                content_str = content_str[:500] + "..."

            concept = Concept(
                id=f"guardrail-{guardrail_id.lower()}",
                type=ConceptType.GUARDRAIL,
                file=relative_path,
                section=f"{section_name}: {guardrail_id}",
                lines=(section_line, section_line + 10),  # Approximate
                content=content_str,
                metadata={
                    "guardrail_id": guardrail_id,
                    "level": level,
                    "section": section_name,
                    "description": description,
                    "verification": guardrail["verification"],
                    "derived_from": guardrail["derived_from"],
                },
            )
            concepts.append(concept)

    return concepts


def extract_all_guardrails(project_root: Path | None = None) -> list[Concept]:
    """Extract all guardrails from standard location.

    Looks for governance/guardrails.md.

    Args:
        project_root: Project root directory.

    Returns:
        List of all extracted guardrail Concepts.

    Examples:
        >>> from pathlib import Path
        >>> guardrails = extract_all_guardrails(Path("."))
        >>> len(guardrails) >= 10
        True
    """
    if project_root is None:
        project_root = Path.cwd()

    guardrails_file = project_root / "governance" / "guardrails.md"

    if guardrails_file.exists():
        return extract_guardrails(guardrails_file, project_root)

    return []
