"""Tests for skill metadata extraction from SKILL.md files."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from raise_cli.context.extractors.skills import (
    extract_all_skills,
    extract_skill_metadata,
)


class TestExtractSkillMetadata:
    """Tests for extract_skill_metadata function."""

    def test_extracts_basic_frontmatter(self, tmp_path: Path) -> None:
        """Should extract name, description from YAML frontmatter."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            name: story-plan
            description: Plan implementation tasks
            ---
            # Feature Plan
            Body content here.
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is not None
        assert node.id == "/story-plan"
        assert node.type == "skill"
        assert node.content == "Plan implementation tasks"
        assert node.source_file == str(skill_md)

    def test_extracts_metadata_fields(self, tmp_path: Path) -> None:
        """Should extract raise.* metadata fields."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            name: test-skill
            description: Test skill description
            metadata:
              raise.prerequisites: other-skill
              raise.next: next-skill
              raise.work_cycle: story
            ---
            # Test
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is not None
        assert node.metadata["raise.prerequisites"] == "other-skill"
        assert node.metadata["raise.next"] == "next-skill"
        assert node.metadata["raise.work_cycle"] == "story"

    def test_handles_multiline_description(self, tmp_path: Path) -> None:
        """Should handle YAML multiline description."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            name: multi-line
            description: >
              This is a multiline
              description that spans
              multiple lines.
            ---
            # Multi
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is not None
        assert "multiline" in node.content
        assert "multiple lines" in node.content

    def test_returns_none_for_missing_frontmatter(self, tmp_path: Path) -> None:
        """Should return None if no YAML frontmatter."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("# No Frontmatter\nJust content.")

        node = extract_skill_metadata(skill_md)

        assert node is None

    def test_returns_none_for_missing_name(self, tmp_path: Path) -> None:
        """Should return None if name field is missing."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            description: No name field
            ---
            # Test
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is None

    def test_returns_none_for_nonexistent_file(self, tmp_path: Path) -> None:
        """Should return None if file doesn't exist."""
        skill_md = tmp_path / "nonexistent.md"

        node = extract_skill_metadata(skill_md)

        assert node is None

    def test_handles_empty_metadata(self, tmp_path: Path) -> None:
        """Should handle skill with no metadata section."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            name: simple-skill
            description: Simple skill
            ---
            # Simple
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is not None
        assert node.metadata == {}

    def test_sets_created_timestamp(self, tmp_path: Path) -> None:
        """Should set created field from file or current time."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            dedent("""\
            ---
            name: timestamped
            description: Has timestamp
            ---
            # Test
        """)
        )

        node = extract_skill_metadata(skill_md)

        assert node is not None
        assert node.created is not None
        assert len(node.created) > 0  # ISO format string


class TestExtractAllSkills:
    """Tests for extract_all_skills function."""

    def test_extracts_from_directory(self, tmp_path: Path) -> None:
        """Should extract all SKILL.md files from skills directory."""
        # Create skill directories
        (tmp_path / "skill-a").mkdir()
        (tmp_path / "skill-a" / "SKILL.md").write_text(
            dedent("""\
            ---
            name: skill-a
            description: Skill A
            ---
            # A
        """)
        )

        (tmp_path / "skill-b").mkdir()
        (tmp_path / "skill-b" / "SKILL.md").write_text(
            dedent("""\
            ---
            name: skill-b
            description: Skill B
            ---
            # B
        """)
        )

        nodes = extract_all_skills(tmp_path)

        assert len(nodes) == 2
        ids = {n.id for n in nodes}
        assert "/skill-a" in ids
        assert "/skill-b" in ids

    def test_skips_invalid_skills(self, tmp_path: Path) -> None:
        """Should skip skills with invalid frontmatter."""
        (tmp_path / "valid").mkdir()
        (tmp_path / "valid" / "SKILL.md").write_text(
            dedent("""\
            ---
            name: valid
            description: Valid skill
            ---
            # Valid
        """)
        )

        (tmp_path / "invalid").mkdir()
        (tmp_path / "invalid" / "SKILL.md").write_text("No frontmatter")

        nodes = extract_all_skills(tmp_path)

        assert len(nodes) == 1
        assert nodes[0].id == "/valid"

    def test_returns_empty_for_nonexistent_directory(self, tmp_path: Path) -> None:
        """Should return empty list if directory doesn't exist."""
        nodes = extract_all_skills(tmp_path / "nonexistent")

        assert nodes == []

    def test_returns_empty_for_empty_directory(self, tmp_path: Path) -> None:
        """Should return empty list if no skill subdirectories."""
        nodes = extract_all_skills(tmp_path)

        assert nodes == []
