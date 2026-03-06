"""Tests for Constitution parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.constitution import extract_principles

# Note: sanitize_id tests are in tests/core/test_text.py


@pytest.fixture
def tmp_constitution_file(tmp_path: Path) -> Path:
    """Create a temporary Constitution file for testing.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary Constitution file.
    """
    constitution_content = dedent(
        """
        # RaiSE Constitution

        ## Core Principles

        ### §1. Humans Define, Machines Execute
        Specifications are the source of truth.
        Code is the expression of specifications.

        ### §2. Governance as Code
        Standards are versioned in Git.
        What's not in the repository doesn't exist.

        ### §10. Observable Workflow
        Every decision must be traceable and auditable.
        """
    )

    constitution_file = tmp_path / "framework" / "reference" / "constitution.md"
    constitution_file.parent.mkdir(parents=True, exist_ok=True)
    constitution_file.write_text(constitution_content)

    return constitution_file


class TestExtractPrinciples:
    """Tests for extract_principles function."""

    def test_extract_from_valid_constitution(self, tmp_constitution_file: Path) -> None:
        """Should extract all principles from valid Constitution file."""
        principles = extract_principles(
            tmp_constitution_file, tmp_constitution_file.parent.parent.parent
        )

        assert len(principles) == 3
        assert all(p.type == ConceptType.PRINCIPLE for p in principles)

    def test_principle_ids(self, tmp_constitution_file: Path) -> None:
        """Should generate correct IDs from principle names."""
        principles = extract_principles(tmp_constitution_file)

        ids = [p.id for p in principles]
        assert "principle-humans-define-machines-execute" in ids
        assert "principle-governance-as-code" in ids
        assert "principle-observable-workflow" in ids

    def test_principle_metadata(self, tmp_constitution_file: Path) -> None:
        """Should extract principle number and name to metadata."""
        principles = extract_principles(tmp_constitution_file)

        principle = next(
            p for p in principles if p.id == "principle-governance-as-code"
        )
        assert principle.metadata["principle_number"] == "2"
        assert principle.metadata["principle_name"] == "Governance as Code"

    def test_principle_sections(self, tmp_constitution_file: Path) -> None:
        """Should extract correct section headers."""
        principles = extract_principles(tmp_constitution_file)

        principle = next(
            p for p in principles if p.id == "principle-governance-as-code"
        )
        assert principle.section == "§2. Governance as Code"

    def test_principle_content(self, tmp_constitution_file: Path) -> None:
        """Should extract section content."""
        principles = extract_principles(tmp_constitution_file)

        principle = next(
            p for p in principles if p.id == "principle-governance-as-code"
        )
        assert "versioned in Git" in principle.content
        assert "repository" in principle.content

    def test_relative_file_path(self, tmp_constitution_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_constitution_file.parent.parent.parent
        principles = extract_principles(tmp_constitution_file, project_root)

        principle = principles[0]
        assert principle.file == "framework/reference/constitution.md"

    def test_empty_file(self, tmp_path: Path) -> None:
        """Should return empty list for empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        principles = extract_principles(empty_file)
        assert principles == []

    def test_missing_file(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        principles = extract_principles(missing_file)
        assert principles == []

    def test_no_principles(self, tmp_path: Path) -> None:
        """Should return empty list for file with no principles."""
        no_principles_file = tmp_path / "no_principles.md"
        no_principles_file.write_text(
            dedent(
                """
                # Document

                This document has no §N principles.

                ### Just a heading
                Not a principle.
                """
            )
        )

        principles = extract_principles(no_principles_file)
        assert principles == []

    def test_content_truncation_by_lines(self, tmp_path: Path) -> None:
        """Should truncate content to ~30 lines."""
        long_content = "\n".join([f"Line {i}" for i in range(50)])
        constitution_file = tmp_path / "long.md"
        constitution_file.write_text(f"### §1. Long Principle\n{long_content}")

        principles = extract_principles(constitution_file)
        principle = principles[0]

        # Content should be truncated
        assert "Line 0" in principle.content
        assert "Line 29" in principle.content
        # But not include line 40+
        lines_in_content = principle.content.count("\n")
        assert lines_in_content <= 31  # 30 lines + header line

    def test_content_truncation_by_chars(self, tmp_path: Path) -> None:
        """Should truncate content to 500 chars with ellipsis."""
        long_line = "x" * 600
        constitution_file = tmp_path / "long_line.md"
        constitution_file.write_text(f"### §1. Long Line\n{long_line}")

        principles = extract_principles(constitution_file)
        principle = principles[0]

        assert len(principle.content) <= 504  # 500 + "..."
        assert principle.content.endswith("...")

    def test_always_on_for_core_principles(self, tmp_path: Path) -> None:
        """§1, §3, §7 should have always_on=True in metadata (S15.8)."""
        content = dedent("""\
            # Constitution

            ### §1. Humans Define, Machines Execute
            Specs are source of truth.

            ### §2. Governance as Code
            Standards versioned in Git.

            ### §3. Platform Agnosticism
            Works where Git works.

            ### §7. Lean Software Development
            Eliminate waste, Jidoka.

            ### §8. Observable Workflow
            Every decision traceable.
        """)

        file_path = tmp_path / "constitution.md"
        file_path.write_text(content)

        principles = extract_principles(file_path, tmp_path)

        always_on_nums = {"1", "3", "7"}
        for p in principles:
            num = p.metadata["principle_number"]
            if num in always_on_nums:
                assert p.metadata.get("always_on") is True, (
                    f"§{num} should be always_on"
                )
            else:
                assert "always_on" not in p.metadata, f"§{num} should NOT be always_on"

    def test_integration_with_real_constitution(self) -> None:
        """Should extract principles from real raise-cli Constitution."""
        constitution_path = Path("framework/reference/constitution.md")

        if not constitution_path.exists():
            pytest.skip("Real Constitution file not found")

        principles = extract_principles(constitution_path)

        # Should extract multiple principles
        assert len(principles) >= 8

        # Should have proper structure
        for principle in principles:
            assert principle.id.startswith("principle-")
            assert principle.type == ConceptType.PRINCIPLE
            assert principle.metadata["principle_number"].isdigit()
            assert len(principle.metadata["principle_name"]) > 0
            assert len(principle.content) > 0
