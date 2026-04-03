"""Tests for glossary parser module."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.glossary import (
    _extract_term_content,
    _parse_term_header,
    extract_all_terms,
    extract_glossary_terms,
)


class TestParseTermHeader:
    """Tests for term header parsing helper."""

    def test_parse_simple_term(self) -> None:
        """Parse a simple term header."""
        header = "### Agent (Agente)"
        name, translation, version = _parse_term_header(header)

        assert name == "Agent"
        assert translation == "Agente"
        assert version is None

    def test_parse_term_without_translation(self) -> None:
        """Parse term without translation in parentheses."""
        header = "### Jidoka"
        name, translation, version = _parse_term_header(header)

        assert name == "Jidoka"
        assert translation is None
        assert version is None

    def test_parse_term_with_version_tag(self) -> None:
        """Parse term with [NUEVO vX.X] tag."""
        header = "### Context Engineering"
        # Version tag is in the content, not header
        name, translation, version = _parse_term_header(header)

        assert name == "Context Engineering"
        assert translation is None
        assert version is None

    def test_parse_term_with_inline_version(self) -> None:
        """Parse term with version in header."""
        header = "### Kata [v2.3: Work Cycles + Jidoka Inline]"
        name, translation, version = _parse_term_header(header)

        assert name == "Kata"
        assert translation is None
        assert version == "v2.3: Work Cycles + Jidoka Inline"

    def test_parse_deprecated_term(self) -> None:
        """Parse deprecated term with warning symbol."""
        header = "### Gate Engine ⚠️ **DEPRECATED v2.6**"
        name, translation, version = _parse_term_header(header)

        assert name == "Gate Engine"
        assert translation is None
        # Deprecated marker captured
        assert version == "DEPRECATED v2.6"

    def test_parse_term_with_actualizado_tag(self) -> None:
        """Parse term with **[ACTUALIZADO vX.X]** tag."""
        header = "### MVC (Minimum Viable Context) **[ACTUALIZADO v2.6]**"
        name, translation, version = _parse_term_header(header)

        assert name == "MVC"
        assert translation == "Minimum Viable Context"
        assert version == "v2.6"


class TestExtractTermContent:
    """Tests for term content extraction."""

    def test_extract_simple_definition(self) -> None:
        """Extract a simple prose definition."""
        content = dedent("""
            Sistema de IA que ejecuta tareas de desarrollo de software.

            > **Principio relacionado:** Los agentes son ejecutores.
        """).strip()

        definition, version_tag = _extract_term_content(content)

        assert "Sistema de IA" in definition
        assert version_tag is None

    def test_extract_definition_with_version_tag(self) -> None:
        """Extract definition with **[NUEVO vX.X]** tag."""
        content = dedent("""
            **[NUEVO v2.0]** Disciplina de diseñar el ambiente informacional.

            > Acuñado por Andrej Karpathy (2025).
        """).strip()

        definition, version_tag = _extract_term_content(content)

        assert "Disciplina de diseñar" in definition
        assert version_tag == "v2.0"

    def test_extract_definition_with_alternate_version_tag(self) -> None:
        """Extract definition with [NUEVO vX.X] tag (no bold)."""
        content = dedent("""
            [NUEVO v2.3] Primera capa del modelo ontológico RaiSE.
        """).strip()

        definition, version_tag = _extract_term_content(content)

        assert "Primera capa" in definition
        assert version_tag == "v2.3"


class TestExtractGlossaryTerms:
    """Tests for extracting terms from file."""

    def test_extract_from_glossary_file(self, tmp_path: Path) -> None:
        """Extract terms from a sample glossary file."""
        glossary_content = dedent("""\
            # RaiSE Glossary
            ## Vocabulario Canónico

            ---

            ## Términos Core de RaiSE

            ### Agent (Agente)
            Sistema de IA que ejecuta tareas de desarrollo de software.

            > **Principio relacionado:** Los agentes son ejecutores.

            ### Context Engineering
            **[NUEVO v2.0]** Disciplina de diseñar el ambiente informacional.

            ## Changelog

            ### v2.0.0
            - Added Context Engineering
        """)

        file_path = tmp_path / "glossary.md"
        file_path.write_text(glossary_content)

        concepts = extract_glossary_terms(file_path, tmp_path)

        assert len(concepts) == 2

        # Check types
        for concept in concepts:
            assert concept.type == ConceptType.TERM

        # Check specific terms
        names = [c.metadata.get("name") for c in concepts]
        assert "Agent" in names
        assert "Context Engineering" in names

        # Check version tag extraction
        ce_concept = next(
            c for c in concepts if c.metadata.get("name") == "Context Engineering"
        )
        assert ce_concept.metadata.get("version") == "v2.0"

    def test_skip_non_definition_sections(self, tmp_path: Path) -> None:
        """Skip sections that are not definitions."""
        glossary_content = dedent("""\
            # RaiSE Glossary

            ## Términos Core de RaiSE

            ### Agent (Agente)
            Sistema de IA.

            ## Mapeo Español-Inglés

            | Español | Inglés |
            |---------|--------|
            | Agente | Agent |

            ## Changelog

            ### v2.0.0
            - Added Agent
        """)

        file_path = tmp_path / "glossary.md"
        file_path.write_text(glossary_content)

        concepts = extract_glossary_terms(file_path, tmp_path)

        # Only Agent should be extracted (not table rows or changelog)
        assert len(concepts) == 1
        assert concepts[0].metadata.get("name") == "Agent"

    def test_extract_returns_empty_for_missing_file(self, tmp_path: Path) -> None:
        """Return empty list for missing file."""
        missing = tmp_path / "nonexistent.md"
        concepts = extract_glossary_terms(missing, tmp_path)
        assert concepts == []


class TestExtractAllTerms:
    """Tests for extracting all terms from standard location."""

    def test_extract_from_standard_location(self, tmp_path: Path) -> None:
        """Extract from framework/reference/glossary.md."""
        # Create directory structure
        ref_dir = tmp_path / "framework" / "reference"
        ref_dir.mkdir(parents=True)

        glossary_content = dedent("""\
            # Glossary

            ## Términos Core de RaiSE

            ### Kata
            Proceso estructurado.
        """)

        (ref_dir / "glossary.md").write_text(glossary_content)

        concepts = extract_all_terms(tmp_path)

        assert len(concepts) == 1
        assert concepts[0].type == ConceptType.TERM
        assert concepts[0].metadata.get("name") == "Kata"

    def test_returns_empty_when_no_glossary_file(self, tmp_path: Path) -> None:
        """Return empty when glossary.md doesn't exist."""
        concepts = extract_all_terms(tmp_path)
        assert concepts == []


class TestIntegrationWithRealGlossary:
    """Integration tests with the actual glossary file."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root."""
        return Path(__file__).parent.parent.parent.parent.parent.parent

    def test_extract_real_glossary(self, project_root: Path) -> None:
        """Extract from actual framework/reference/glossary.md."""
        glossary_file = project_root / "framework" / "reference" / "glossary.md"
        if not glossary_file.exists():
            pytest.skip("Glossary file not found")

        concepts = extract_glossary_terms(glossary_file, project_root)

        # Should have many terms
        assert len(concepts) >= 30  # We know there are ~50 terms

        # Check structure
        for concept in concepts:
            assert concept.type == ConceptType.TERM
            assert concept.id.startswith("term-")
            assert "name" in concept.metadata
            assert concept.content  # Non-empty definition

        # Check specific known terms
        names = [c.metadata.get("name") for c in concepts]
        assert "Agent" in names
        assert "Kata" in names
        assert "Jidoka" in names
        assert "Constitution" in names
        assert (
            "MVC" in names
        )  # Translation "(Minimum Viable Context)" captured separately

    def test_extract_all_real_terms(self, project_root: Path) -> None:
        """Extract all terms from standard location."""
        concepts = extract_all_terms(project_root)

        # Should match extract_glossary_terms result
        assert len(concepts) >= 30

        # Verify we captured version tags where present
        versioned = [c for c in concepts if c.metadata.get("version")]
        assert len(versioned) > 0  # Some terms have version tags

    def test_deprecated_terms_captured(self, project_root: Path) -> None:
        """Verify deprecated terms are captured with status."""
        concepts = extract_all_terms(project_root)

        # Find deprecated terms (like Gate Engine, Kata Engine)
        deprecated = [
            c for c in concepts if "DEPRECATED" in (c.metadata.get("version") or "")
        ]
        assert len(deprecated) >= 1  # At least Gate Engine is deprecated
