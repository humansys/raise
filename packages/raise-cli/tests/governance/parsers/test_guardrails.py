"""Tests for guardrails parser module."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.guardrails import (
    _extract_prefix,
    _parse_frontmatter,
    _parse_guardrail_table,
    _strip_frontmatter,
    extract_all_guardrails,
    extract_guardrails,
)


class TestParseGuardrailTable:
    """Tests for table parsing helper."""

    def test_parse_simple_table(self) -> None:
        """Parse a simple guardrail table."""
        table = dedent("""
            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints on all code | `pyright --strict` passes | Solution Vision |
            | `SHOULD-CODE-001` | SHOULD | Google-style docstrings | Manual review | Best practices |
        """).strip()

        guardrails = _parse_guardrail_table(table, "Code Quality")

        assert len(guardrails) == 2
        assert guardrails[0]["id"] == "MUST-CODE-001"
        assert guardrails[0]["level"] == "MUST"
        assert guardrails[0]["description"] == "Type hints on all code"
        assert guardrails[0]["section"] == "Code Quality"

    def test_parse_table_with_backticks(self) -> None:
        """Handle IDs and verification with backticks."""
        table = dedent("""
            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-TEST-001` | MUST | >90% test coverage | `pytest --cov` ≥ 90% | Solution Vision |
        """).strip()

        guardrails = _parse_guardrail_table(table, "Testing")

        assert len(guardrails) == 1
        assert guardrails[0]["id"] == "MUST-TEST-001"
        assert "pytest --cov" in guardrails[0]["verification"]


class TestExtractGuardrails:
    """Tests for extracting guardrails from file."""

    def test_extract_from_guardrails_file(self, tmp_path: Path) -> None:
        """Extract guardrails from a sample file."""
        guardrails_content = dedent("""
            # Guardrails: RaiSE

            ## Guardrails Activos

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints on all code | `pyright --strict` passes | Solution Vision |
            | `MUST-CODE-002` | MUST | Ruff linting passes | `ruff check .` exits 0 | Best practices |

            ### Testing

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-TEST-001` | MUST | >90% test coverage | `pytest --cov` ≥ 90% | Solution Vision |

            ### Security

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-SEC-001` | MUST | No secrets in code | `detect-secrets` passes | Solution Vision |
        """).strip()

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(guardrails_content)

        concepts = extract_guardrails(file_path, tmp_path)

        assert len(concepts) == 4

        # Check types
        for concept in concepts:
            assert concept.type == ConceptType.GUARDRAIL

        # Check IDs
        ids = [c.metadata.get("guardrail_id") for c in concepts]
        assert "MUST-CODE-001" in ids
        assert "MUST-CODE-002" in ids
        assert "MUST-TEST-001" in ids
        assert "MUST-SEC-001" in ids

        # Check sections
        sections = [c.metadata.get("section") for c in concepts]
        assert "Code Quality" in sections
        assert "Testing" in sections
        assert "Security" in sections

    def test_extract_returns_empty_for_missing_file(self, tmp_path: Path) -> None:
        """Return empty list for missing file."""
        missing = tmp_path / "nonexistent.md"
        concepts = extract_guardrails(missing, tmp_path)
        assert concepts == []


class TestExtractAllGuardrails:
    """Tests for extracting all guardrails from standard location."""

    def test_extract_from_standard_location(self, tmp_path: Path) -> None:
        """Extract from governance/guardrails.md."""
        # Create directory structure
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir(parents=True)

        guardrails_content = dedent("""
            # Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |
        """).strip()

        (gov_dir / "guardrails.md").write_text(guardrails_content)

        concepts = extract_all_guardrails(tmp_path)

        assert len(concepts) == 1
        assert concepts[0].type == ConceptType.GUARDRAIL
        assert concepts[0].metadata.get("guardrail_id") == "MUST-CODE-001"

    def test_returns_empty_when_no_guardrails_file(self, tmp_path: Path) -> None:
        """Return empty when guardrails.md doesn't exist."""
        concepts = extract_all_guardrails(tmp_path)
        assert concepts == []


class TestParseFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_parses_constraint_scopes(self) -> None:
        """Parse constraint_scopes from YAML frontmatter."""
        content = dedent("""\
            ---
            type: guardrails
            version: "2.0.0"
            constraint_scopes:
              default: all_bounded_contexts
              overrides:
                must-arch: [bc-ontology, bc-skills]
                should-cli: [lyr-orchestration]
            ---

            # Guardrails
        """)

        fm = _parse_frontmatter(content)

        assert fm["type"] == "guardrails"
        scopes = fm["constraint_scopes"]
        assert scopes["default"] == "all_bounded_contexts"
        assert scopes["overrides"]["must-arch"] == ["bc-ontology", "bc-skills"]
        assert scopes["overrides"]["should-cli"] == ["lyr-orchestration"]

    def test_returns_empty_dict_when_no_frontmatter(self) -> None:
        """Return empty dict when content has no frontmatter."""
        content = "# Just a heading\n\nSome text.\n"

        fm = _parse_frontmatter(content)

        assert fm == {}

    def test_returns_empty_dict_for_invalid_yaml(self) -> None:
        """Return empty dict for unparseable frontmatter."""
        content = "---\n: invalid: yaml: [[\n---\n\n# Content\n"

        fm = _parse_frontmatter(content)

        assert fm == {}


class TestStripFrontmatter:
    """Tests for frontmatter stripping."""

    def test_strips_frontmatter(self) -> None:
        """Strip frontmatter and return body only."""
        content = dedent("""\
            ---
            type: guardrails
            version: "2.0.0"
            ---

            # Guardrails

            Body text here.
        """)

        body = _strip_frontmatter(content)

        assert not body.startswith("---")
        assert "# Guardrails" in body
        assert "Body text here." in body

    def test_returns_content_unchanged_when_no_frontmatter(self) -> None:
        """Return content as-is when no frontmatter present."""
        content = "# Guardrails\n\nBody text.\n"

        body = _strip_frontmatter(content)

        assert body == content


class TestExtractPrefix:
    """Tests for guardrail ID prefix extraction."""

    def test_extracts_must_code_prefix(self) -> None:
        """Extract prefix from MUST-CODE-001."""
        assert _extract_prefix("MUST-CODE-001") == "must-code"

    def test_extracts_should_cli_prefix(self) -> None:
        """Extract prefix from SHOULD-CLI-001."""
        assert _extract_prefix("SHOULD-CLI-001") == "should-cli"

    def test_extracts_must_arch_prefix(self) -> None:
        """Extract prefix from MUST-ARCH-002."""
        assert _extract_prefix("MUST-ARCH-002") == "must-arch"

    def test_extracts_should_inf_prefix(self) -> None:
        """Extract prefix from SHOULD-INF-003."""
        assert _extract_prefix("SHOULD-INF-003") == "should-inf"


class TestExtractGuardrailsWithFrontmatter:
    """Tests for scope propagation from frontmatter to guardrail metadata."""

    def test_propagates_default_scope(self, tmp_path: Path) -> None:
        """Guardrails with default scope get all_bounded_contexts."""
        content = dedent("""\
            ---
            type: guardrails
            constraint_scopes:
              default: all_bounded_contexts
              overrides:
                must-arch: [bc-ontology, bc-skills]
            ---

            ## Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |
        """)

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(content)

        concepts = extract_guardrails(file_path, tmp_path)

        assert len(concepts) == 1
        assert concepts[0].metadata["constraint_scope"] == "all_bounded_contexts"

    def test_propagates_override_scope(self, tmp_path: Path) -> None:
        """Guardrails matching an override get the specific scope list."""
        content = dedent("""\
            ---
            type: guardrails
            constraint_scopes:
              default: all_bounded_contexts
              overrides:
                must-arch: [bc-ontology, bc-skills]
            ---

            ## Guardrails

            ### Architecture

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-ARCH-001` | MUST | Engine separation | import analysis | Vision |
        """)

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(content)

        concepts = extract_guardrails(file_path, tmp_path)

        assert len(concepts) == 1
        assert concepts[0].metadata["constraint_scope"] == ["bc-ontology", "bc-skills"]

    def test_backward_compat_no_frontmatter(self, tmp_path: Path) -> None:
        """Guardrails without frontmatter still parse correctly, no constraint_scope."""
        content = dedent("""\
            # Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |
        """)

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(content)

        concepts = extract_guardrails(file_path, tmp_path)

        assert len(concepts) == 1
        # No constraint_scope when no frontmatter
        assert "constraint_scope" not in concepts[0].metadata


class TestAlwaysOnMetadata:
    """Tests for always_on metadata on MUST-level guardrails (S15.8)."""

    def test_must_guardrails_have_always_on_true(self, tmp_path: Path) -> None:
        """MUST-level guardrails should have always_on=True in metadata."""
        content = dedent("""\
            # Guardrails

            ### Code Quality

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-CODE-001` | MUST | Type hints | pyright | Vision |
            | `SHOULD-CODE-001` | SHOULD | Docstrings | review | Retro |
        """)

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(content)

        concepts = extract_guardrails(file_path, tmp_path)

        must = next(
            c for c in concepts if c.metadata["guardrail_id"] == "MUST-CODE-001"
        )
        should = next(
            c for c in concepts if c.metadata["guardrail_id"] == "SHOULD-CODE-001"
        )

        assert must.metadata.get("always_on") is True
        assert "always_on" not in should.metadata

    def test_all_must_levels_get_always_on(self, tmp_path: Path) -> None:
        """All MUST-level guardrails (SEC, TEST, ARCH) should get always_on."""
        content = dedent("""\
            # Guardrails

            ### Security

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-SEC-001` | MUST | No secrets | detect-secrets | Vision |

            ### Testing

            | ID | Level | Guardrail | Verificación | Derivado de |
            |----|-------|-----------|--------------|-------------|
            | `MUST-TEST-001` | MUST | >90% coverage | pytest | Vision |
        """)

        file_path = tmp_path / "guardrails.md"
        file_path.write_text(content)

        concepts = extract_guardrails(file_path, tmp_path)

        for concept in concepts:
            assert concept.metadata.get("always_on") is True


class TestIntegrationWithRealGuardrails:
    """Integration tests with the actual guardrails file."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root."""
        return Path(__file__).parent.parent.parent.parent.parent.parent

    def test_extract_real_guardrails(self, project_root: Path) -> None:
        """Extract from actual governance/guardrails.md."""
        guardrails_file = project_root / "governance" / "guardrails.md"
        if not guardrails_file.exists():
            pytest.skip("Guardrails file not found")

        concepts = extract_guardrails(guardrails_file, project_root)

        # Should have multiple guardrails
        assert len(concepts) >= 10  # We know there are at least 10

        # Check structure
        for concept in concepts:
            assert concept.type == ConceptType.GUARDRAIL
            assert concept.id.startswith("guardrail-")
            assert "guardrail_id" in concept.metadata
            assert "section" in concept.metadata
            assert "level" in concept.metadata

        # Check specific known guardrails
        ids = [c.metadata.get("guardrail_id") for c in concepts]
        assert "MUST-CODE-001" in ids  # Type hints
        assert "MUST-TEST-001" in ids  # Coverage
        assert "MUST-SEC-001" in ids  # No secrets

    def test_extract_all_real_guardrails(self, project_root: Path) -> None:
        """Extract all guardrails from standard location."""
        concepts = extract_all_guardrails(project_root)

        # Should match extract_guardrails result
        assert len(concepts) >= 10

        # Verify MUST vs SHOULD distribution
        must_count = sum(1 for c in concepts if c.metadata.get("level") == "MUST")
        should_count = sum(1 for c in concepts if c.metadata.get("level") == "SHOULD")
        assert must_count > 0
        assert should_count > 0
