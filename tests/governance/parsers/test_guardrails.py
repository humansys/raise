"""Tests for guardrails parser module."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.guardrails import (
    extract_guardrails,
    extract_all_guardrails,
    _parse_guardrail_table,
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
        """Extract from governance/solution/guardrails.md."""
        # Create directory structure
        gov_dir = tmp_path / "governance" / "solution"
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


class TestIntegrationWithRealGuardrails:
    """Integration tests with the actual guardrails file."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root."""
        return Path(__file__).parent.parent.parent.parent

    def test_extract_real_guardrails(self, project_root: Path) -> None:
        """Extract from actual governance/solution/guardrails.md."""
        guardrails_file = project_root / "governance" / "solution" / "guardrails.md"
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
        assert "MUST-SEC-001" in ids   # No secrets

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
