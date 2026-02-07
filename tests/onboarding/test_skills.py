"""Tests for the skills scaffolding module — copies bundled skills to project."""

from __future__ import annotations

from pathlib import Path

from raise_cli.onboarding.skills import SkillScaffoldResult, scaffold_skills


class TestScaffoldSkills:
    """Tests for scaffold_skills() function."""

    def test_copies_all_five_skills(self, tmp_path: Path) -> None:
        """Should copy all 5 onboarding skills to .claude/skills/."""
        result = scaffold_skills(tmp_path)

        skills_dir = tmp_path / ".claude" / "skills"
        assert (skills_dir / "session-start" / "SKILL.md").exists()
        assert (skills_dir / "discover-start" / "SKILL.md").exists()
        assert (skills_dir / "discover-scan" / "SKILL.md").exists()
        assert (skills_dir / "discover-validate" / "SKILL.md").exists()
        assert (skills_dir / "discover-complete" / "SKILL.md").exists()
        assert result.skills_copied == 5

    def test_skill_content_has_frontmatter(self, tmp_path: Path) -> None:
        """Copied skills should have YAML frontmatter."""
        scaffold_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "session-start" / "SKILL.md"
        content = skill_path.read_text()
        assert content.startswith("---\n")
        assert "name: session-start" in content

    def test_skill_content_matches_bundled(self, tmp_path: Path) -> None:
        """Copied skill files should match bundled originals."""
        from importlib.resources import files

        scaffold_skills(tmp_path)

        base = files("raise_cli.skills_base")
        original = (base / "session-start" / "SKILL.md").read_text()
        copied = (
            tmp_path / ".claude" / "skills" / "session-start" / "SKILL.md"
        ).read_text()
        assert copied == original

    def test_returns_skill_names(self, tmp_path: Path) -> None:
        """Should return names of copied skills."""
        result = scaffold_skills(tmp_path)

        assert "session-start" in result.skills_installed
        assert "discover-complete" in result.skills_installed
        assert len(result.skills_installed) == 5

    def test_reports_files_copied(self, tmp_path: Path) -> None:
        """Should list all copied files in result."""
        result = scaffold_skills(tmp_path)

        assert len(result.files_copied) == 5
        assert len(result.files_skipped) == 0
        assert not result.already_existed


class TestScaffoldSkillsIdempotency:
    """Tests for skills scaffolding being safe to run multiple times."""

    def test_does_not_overwrite_existing_skills(self, tmp_path: Path) -> None:
        """Should not overwrite existing skill files."""
        # First scaffold
        scaffold_skills(tmp_path)

        # Modify a skill
        skill_path = tmp_path / ".claude" / "skills" / "session-start" / "SKILL.md"
        skill_path.write_text("# Custom skill")

        # Second scaffold
        result = scaffold_skills(tmp_path)

        assert skill_path.read_text() == "# Custom skill"
        assert "session-start" in result.skills_skipped_names

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second scaffold should report already_existed=True."""
        scaffold_skills(tmp_path)
        result = scaffold_skills(tmp_path)

        assert result.already_existed
        assert len(result.files_skipped) == 5
        assert len(result.files_copied) == 0
        assert result.skills_copied == 0

    def test_copies_only_missing_skills(self, tmp_path: Path) -> None:
        """Should copy missing skills when some already exist."""
        # Create one skill manually
        skill_dir = tmp_path / ".claude" / "skills" / "session-start"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Existing")

        result = scaffold_skills(tmp_path)

        # session-start should be skipped
        assert "session-start" in result.skills_skipped_names
        # Others should be copied
        assert result.skills_copied == 4
        assert (
            tmp_path / ".claude" / "skills" / "discover-start" / "SKILL.md"
        ).exists()


class TestScaffoldSkillsPartialState:
    """Tests for scaffold when .claude/ is partially populated."""

    def test_handles_existing_claude_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/ exists but skills/ doesn't."""
        (tmp_path / ".claude").mkdir()

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == 5

    def test_handles_existing_skills_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/skills/ exists but is empty."""
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == 5


class TestSkillScaffoldResult:
    """Tests for SkillScaffoldResult model."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        result = SkillScaffoldResult()

        assert result.skills_copied == 0
        assert not result.already_existed
        assert result.files_copied == []
        assert result.files_skipped == []
        assert result.skills_installed == []
        assert result.skills_skipped_names == []
