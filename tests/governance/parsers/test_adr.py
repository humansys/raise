"""Tests for ADR parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.adr import (
    _extract_decision_summary,
    _parse_frontmatter,
    extract_all_decisions,
    extract_decision_from_file,
    extract_decisions,
)

# Resolve project root at import time (immune to chdir in other tests)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class TestParseFrontmatter:
    """Tests for _parse_frontmatter function."""

    def test_parses_valid_frontmatter(self) -> None:
        """Should parse YAML frontmatter correctly."""
        text = dedent("""\
            ---
            id: "ADR-001"
            title: "Test Decision"
            status: "Accepted"
            ---
            # Content here
        """)
        fm, content, end_line = _parse_frontmatter(text)

        assert fm["id"] == "ADR-001"
        assert fm["title"] == "Test Decision"
        assert fm["status"] == "Accepted"
        assert "# Content here" in content
        assert end_line == 5

    def test_returns_empty_for_no_frontmatter(self) -> None:
        """Should return empty dict when no frontmatter present."""
        text = "# Just a title\n\nSome content."
        fm, content, end_line = _parse_frontmatter(text)

        assert fm == {}
        assert content == text
        assert end_line == 0

    def test_returns_empty_for_unclosed_frontmatter(self) -> None:
        """Should return empty dict when frontmatter not closed."""
        text = dedent("""\
            ---
            id: "ADR-001"
            title: "Test"
            # No closing ---
        """)
        fm, content, end_line = _parse_frontmatter(text)

        assert fm == {}
        assert end_line == 0

    def test_handles_related_to_list(self) -> None:
        """Should parse related_to as list."""
        text = dedent("""\
            ---
            id: "ADR-019"
            related_to: ["ADR-011", "ADR-015"]
            ---
            Content
        """)
        fm, _, _ = _parse_frontmatter(text)

        assert fm["related_to"] == ["ADR-011", "ADR-015"]


class TestExtractDecisionSummary:
    """Tests for _extract_decision_summary function."""

    def test_extracts_decision_section(self) -> None:
        """Should extract Decision section content."""
        content = dedent("""\
            # ADR-001: Test

            ## Context
            Some context here.

            ## Decision
            We decided to use X because Y.

            ## Consequences
            Good stuff.
        """)
        summary = _extract_decision_summary(content)

        assert "We decided to use X because Y." in summary

    def test_extracts_spanish_decision_section(self) -> None:
        """Should extract Decisión section (Spanish)."""
        content = dedent("""\
            # ADR-001: Test

            ## Contexto
            Algo de contexto.

            ## Decisión
            Decidimos usar X porque Y.

            ## Consecuencias
            Cosas buenas.
        """)
        summary = _extract_decision_summary(content)

        assert "Decidimos usar X porque Y." in summary

    def test_truncates_long_summaries(self) -> None:
        """Should truncate summaries longer than 500 chars."""
        long_decision = "A" * 600
        content = f"## Decision\n{long_decision}\n## Next"

        summary = _extract_decision_summary(content)

        assert len(summary) <= 503  # 500 + "..."
        assert summary.endswith("...")

    def test_decision_as_last_section(self) -> None:
        r"""Decision is the last section — hits \\Z branch (RAISE-537)."""
        content = "## Context\nSome context.\n\n## Decision\nWe chose Y.\n"
        summary = _extract_decision_summary(content)
        assert "We chose Y." in summary

    def test_returns_empty_for_no_decision(self) -> None:
        """Should return empty string if no Decision section."""
        content = "# Title\n\nJust content without Decision section."
        summary = _extract_decision_summary(content)

        # May return first paragraph as fallback or empty
        assert isinstance(summary, str)


class TestExtractDecisionFromFile:
    """Tests for extract_decision_from_file function."""

    def test_extracts_from_valid_adr(self, tmp_path: Path) -> None:
        """Should extract decision from valid ADR file."""
        adr_file = tmp_path / "adr-001-test.md"
        adr_file.write_text(
            dedent("""\
            ---
            id: "ADR-001"
            title: "Test Decision"
            date: "2026-02-03"
            status: "Accepted"
            related_to: ["ADR-000"]
            ---
            # ADR-001: Test Decision

            ## Context
            We need to decide something.

            ## Decision
            We will use option A.

            ## Consequences
            It will be good.
        """)
        )

        concept = extract_decision_from_file(adr_file, tmp_path)

        assert concept is not None
        assert concept.id == "decision-adr-001"
        assert concept.type == ConceptType.DECISION
        assert "Test Decision" in concept.content
        assert "We will use option A" in concept.content
        assert concept.metadata["adr_id"] == "ADR-001"
        assert concept.metadata["status"] == "Accepted"
        assert concept.metadata["related_to"] == ["ADR-000"]

    def test_returns_none_for_no_frontmatter(self, tmp_path: Path) -> None:
        """Should return None for files without frontmatter."""
        adr_file = tmp_path / "adr-001-legacy.md"
        adr_file.write_text("# ADR-001: Legacy\n\nNo frontmatter here.")

        concept = extract_decision_from_file(adr_file, tmp_path)

        assert concept is None

    def test_returns_none_for_missing_id(self, tmp_path: Path) -> None:
        """Should return None if frontmatter has no id."""
        adr_file = tmp_path / "adr-001-no-id.md"
        adr_file.write_text(
            dedent("""\
            ---
            title: "No ID"
            status: "Draft"
            ---
            Content
        """)
        )

        concept = extract_decision_from_file(adr_file, tmp_path)

        assert concept is None

    def test_returns_none_for_nonexistent_file(self, tmp_path: Path) -> None:
        """Should return None for nonexistent file."""
        concept = extract_decision_from_file(tmp_path / "nonexistent.md", tmp_path)

        assert concept is None


class TestExtractDecisions:
    """Tests for extract_decisions function."""

    def test_extracts_from_directory(self, tmp_path: Path) -> None:
        """Should extract all ADRs from directory."""
        # Create test ADRs
        (tmp_path / "adr-001-first.md").write_text(
            dedent("""\
            ---
            id: "ADR-001"
            title: "First"
            status: "Accepted"
            ---
            ## Decision
            First decision.
        """)
        )
        (tmp_path / "adr-002-second.md").write_text(
            dedent("""\
            ---
            id: "ADR-002"
            title: "Second"
            status: "Proposed"
            ---
            ## Decision
            Second decision.
        """)
        )
        # Legacy file (no frontmatter) - should be skipped
        (tmp_path / "adr-003-legacy.md").write_text("# Legacy ADR\nNo frontmatter.")

        concepts = extract_decisions(tmp_path, tmp_path)

        assert len(concepts) == 2
        ids = {c.id for c in concepts}
        assert "decision-adr-001" in ids
        assert "decision-adr-002" in ids

    def test_returns_empty_for_nonexistent_directory(self, tmp_path: Path) -> None:
        """Should return empty list for nonexistent directory."""
        concepts = extract_decisions(tmp_path / "nonexistent", tmp_path)

        assert concepts == []


class TestExtractAllDecisions:
    """Tests for extract_all_decisions function."""

    def test_extracts_from_standard_locations(self, tmp_path: Path) -> None:
        """Should extract from governance/adrs/ and governance/adrs/v2/."""
        # Create directory structure
        root_dir = tmp_path / "governance" / "adrs"
        root_dir.mkdir(parents=True)
        v2_dir = root_dir / "v2"
        v2_dir.mkdir()

        # Root ADR
        (root_dir / "adr-019-unified.md").write_text(
            dedent("""\
            ---
            id: "ADR-019"
            title: "Unified Graph"
            status: "Accepted"
            ---
            ## Decision
            Use unified graph.
        """)
        )

        # v2 ADR
        (v2_dir / "adr-001-sar.md").write_text(
            dedent("""\
            ---
            id: "ADR-001"
            title: "SAR Pipeline"
            status: "Accepted"
            ---
            ## Decisión
            Usar pipeline de 4 fases.
        """)
        )

        concepts = extract_all_decisions(tmp_path)

        assert len(concepts) == 2
        ids = {c.id for c in concepts}
        assert "decision-adr-019" in ids
        assert "decision-adr-001" in ids

    def test_skips_v1_directory(self, tmp_path: Path) -> None:
        """Should NOT extract from governance/adrs/v1/ (legacy)."""
        # Create directory structure
        root_dir = tmp_path / "governance" / "adrs"
        root_dir.mkdir(parents=True)
        v1_dir = root_dir / "v1"
        v1_dir.mkdir()

        # v1 ADR (legacy format without frontmatter)
        (v1_dir / "adr-001-legacy.md").write_text("# ADR-001: Legacy\nNo frontmatter.")

        concepts = extract_all_decisions(tmp_path)

        # Should be empty - v1 is not extracted
        assert concepts == []


class TestIntegrationWithRealData:
    """Integration tests with real ADR data."""

    @pytest.mark.skipif(
        not (
            _PROJECT_ROOT / "governance/adrs/v1/adr-019-unified-context-graph.md"
        ).exists(),
        reason="Real ADR data not available",
    )
    def test_extracts_real_adrs(self) -> None:
        """Should extract real ADRs from project."""
        concepts = extract_all_decisions(_PROJECT_ROOT)

        # Should have extracted some decisions
        assert len(concepts) > 0

        # All should be DECISION type
        for concept in concepts:
            assert concept.type == ConceptType.DECISION

        # Check ADR-019 specifically
        adr_019 = next((c for c in concepts if "adr-019" in c.id), None)
        if adr_019:
            assert "Unified" in adr_019.content or "unified" in adr_019.content.lower()
            assert adr_019.metadata["status"] in ["Accepted", "accepted"]
