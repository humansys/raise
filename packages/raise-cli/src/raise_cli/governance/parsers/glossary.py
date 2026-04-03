"""Parser for Glossary terms from framework documents.

Extracts term definitions from markdown glossary files.
Supports version tags, translations, and deprecated markers.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.compat import portable_path
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.parsers._convert import concept_to_node
from raise_core.graph.models import GraphNode

# Sections that contain term definitions (extract from these)
DEFINITION_SECTIONS = {
    "Términos Core de RaiSE",
    "Ontología Agentic AI",
    "Artefactos del Flujo de Trabajo",
    "Conceptos de Preventa/Proyectos",
}

# Sections to skip (tables, references, changelog)
SKIP_SECTIONS = {
    "Mapeo Español-Inglés",
    "Anti-Términos",
    "Changelog",
    "Jerarquías de Referencia",
    "Métricas de Calidad AI",
    "Formato de Referencia a Principios",
}


def _parse_term_header(header: str) -> tuple[str | None, str | None, str | None]:
    """Parse a term header line.

    Extracts term name, optional translation, and optional version/status.

    Args:
        header: Header line like "### Agent (Agente)" or "### Kata [v2.3: ...]"

    Returns:
        Tuple of (name, translation, version) where any can be None.

    Examples:
        >>> _parse_term_header("### Agent (Agente)")
        ('Agent', 'Agente', None)
        >>> _parse_term_header("### Kata [v2.3: Work Cycles]")
        ('Kata', None, 'v2.3: Work Cycles')
        >>> _parse_term_header("### Gate Engine ⚠️ **DEPRECATED v2.6**")
        ('Gate Engine', None, 'DEPRECATED v2.6')
    """
    if not header.startswith("###"):
        return None, None, None

    # Remove ### prefix and strip
    text = header[3:].strip()

    name: str | None = None
    translation: str | None = None
    version: str | None = None

    # Check for DEPRECATED marker (with or without emoji)
    deprecated_match = re.search(r"\*\*DEPRECATED\s+(v[\d.]+)\*\*", text)
    if deprecated_match:
        version = f"DEPRECATED {deprecated_match.group(1)}"
        # Remove deprecated marker from text
        text = text[: deprecated_match.start()].strip()
        # Remove emoji if present
        text = text.replace("⚠️", "").strip()

    # Check for **[ACTUALIZADO vX.X]** or **[NUEVO vX.X]** pattern
    update_match = re.search(r"\*\*\[(ACTUALIZADO|NUEVO)\s+(v[\d.]+)\]\*\*", text)
    if update_match and not version:
        version = update_match.group(2)  # Just the version number
        text = text[: update_match.start()].strip()

    # Check for [vX.X: description] version tag
    version_match = re.search(r"\[(v[\d.]+[^\]]*)\]", text)
    if version_match and not version:  # Don't override DEPRECATED or ACTUALIZADO
        version = version_match.group(1)
        text = text[: version_match.start()].strip()

    # Check for (Translation) pattern
    trans_match = re.search(r"\(([^)]+)\)$", text)
    if trans_match:
        translation = trans_match.group(1)
        text = text[: trans_match.start()].strip()

    name = text if text else None

    return name, translation, version


def _extract_term_content(content: str) -> tuple[str, str | None]:
    """Extract definition and version tag from term content.

    Args:
        content: Content text after the term header.

    Returns:
        Tuple of (definition, version_tag) where version_tag may be None.

    Examples:
        >>> definition, version = _extract_term_content("**[NUEVO v2.0]** Discipline...")
        >>> version
        'v2.0'
    """
    version_tag: str | None = None

    # Check for **[NUEVO vX.X]** at start
    bold_match = re.match(r"\*\*\[NUEVO\s+(v[\d.]+)\]\*\*\s*", content)
    if bold_match:
        version_tag = bold_match.group(1)
        content = content[bold_match.end() :]

    # Check for [NUEVO vX.X] at start (without bold)
    if not version_tag:
        plain_match = re.match(r"\[NUEVO\s+(v[\d.]+)\]\s*", content)
        if plain_match:
            version_tag = plain_match.group(1)
            content = content[plain_match.end() :]

    # Clean up content - take first paragraph or up to 500 chars
    definition = content.strip()

    return definition, version_tag


def _find_terms_in_section(
    content: str,
    section_start: int,
    section_end: int,
    lines: list[str],  # noqa: ARG001 -- API signature consistency with other parsers
) -> list[tuple[int, str, str]]:
    """Find all term definitions within a section.

    Args:
        content: Full file content.
        section_start: Character offset where section starts.
        section_end: Character offset where section ends.
        lines: List of lines in the file.

    Returns:
        List of (line_number, term_header, term_content) tuples.
    """
    section_text = content[section_start:section_end]
    terms: list[tuple[int, str, str]] = []

    # Find all ### headers in section
    term_pattern = re.compile(r"^###\s+.+$", re.MULTILINE)
    matches = list(term_pattern.finditer(section_text))

    for i, match in enumerate(matches):
        header = match.group(0)

        # Find content (until next ### or end of section)
        content_start = match.end()
        content_end = (
            matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        )
        term_content = section_text[content_start:content_end].strip()

        # Calculate line number
        # Count newlines from start of section to match
        line_offset = section_text[: match.start()].count("\n")
        # Count newlines from start of file to section
        section_line = content[:section_start].count("\n") + 1
        term_line = section_line + line_offset

        terms.append((term_line, header, term_content))

    return terms


def extract_glossary_terms(
    file_path: Path, project_root: Path | None = None
) -> list[Concept]:
    """Extract glossary terms from a glossary markdown file.

    Parses term definitions from sections like "Términos Core de RaiSE".
    Each term becomes a Concept with type TERM.

    Args:
        file_path: Path to glossary markdown file.
        project_root: Project root for relative path calculation.

    Returns:
        List of Concept objects representing glossary terms.

    Examples:
        >>> from pathlib import Path
        >>> terms = extract_glossary_terms(Path("framework/reference/glossary.md"))
        >>> len(terms) > 0
        True
        >>> terms[0].type
        <ConceptType.TERM: 'term'>
    """
    if not file_path.exists():
        return []

    if project_root is None:
        project_root = file_path.parent.parent.parent  # framework/reference/ -> root

    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    concepts: list[Concept] = []

    # Calculate relative path
    try:
        relative_path = portable_path(file_path, project_root)
    except ValueError:
        relative_path = file_path.name

    # Find ## section boundaries
    section_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    section_matches = list(section_pattern.finditer(content))

    for i, match in enumerate(section_matches):
        section_name = match.group(1).strip()

        # Skip non-definition sections
        if section_name in SKIP_SECTIONS:
            continue

        # Only process definition sections (or any section not explicitly skipped)
        # This allows for flexibility if new sections are added
        section_start = match.end()
        section_end = (
            section_matches[i + 1].start()
            if i + 1 < len(section_matches)
            else len(content)
        )

        # Find terms in this section
        terms = _find_terms_in_section(content, section_start, section_end, lines)

        for term_line, header, term_content in terms:
            name, translation, header_version = _parse_term_header(header)

            if not name:
                continue

            # Extract definition and check for version tag in content
            definition, content_version = _extract_term_content(term_content)

            # Use header version if present, else content version
            version = header_version or content_version

            # Generate ID from name (lowercase, hyphenated)
            term_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

            # Truncate definition if needed
            if len(definition) > 500:
                definition = definition[:500] + "..."

            concept = Concept(
                id=f"term-{term_id}",
                type=ConceptType.TERM,
                file=relative_path,
                section=f"{section_name}: {name}",
                lines=(term_line, term_line + 10),  # Approximate end
                content=definition,
                metadata={
                    "name": name,
                    "translation": translation,
                    "version": version,
                    "section": section_name,
                },
            )
            concepts.append(concept)

    return concepts


def extract_all_terms(project_root: Path | None = None) -> list[Concept]:
    """Extract all glossary terms from standard location.

    Looks for framework/reference/glossary.md.

    Args:
        project_root: Project root directory.

    Returns:
        List of all extracted term Concepts.

    Examples:
        >>> from pathlib import Path
        >>> terms = extract_all_terms(Path("."))
        >>> len(terms) >= 30
        True
    """
    if project_root is None:
        project_root = Path.cwd()

    glossary_file = project_root / "framework" / "reference" / "glossary.md"

    if glossary_file.exists():
        return extract_glossary_terms(glossary_file, project_root)

    return []


class GlossaryParser:
    """GovernanceParser wrapper for glossary terms."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        """Match Glossary artifact type."""
        return locator.artifact_type == CoreArtifactType.GLOSSARY

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse Glossary file into GraphNode list."""
        root = Path(locator.metadata["project_root"])
        path = root / locator.path
        concepts = extract_glossary_terms(path, root)
        return [concept_to_node(c) for c in concepts]
