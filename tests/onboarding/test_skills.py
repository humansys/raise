"""Tests for the skills scaffolding module — copies bundled skills to project."""

from __future__ import annotations

from pathlib import Path

from rai_cli.config.agents import get_agent_config
from rai_cli.onboarding.skills import SkillScaffoldResult, scaffold_skills
from rai_cli.skills_base import DISTRIBUTABLE_SKILLS

TOTAL_SKILLS = len(DISTRIBUTABLE_SKILLS)

# Skills that include reference subdirectories (more than just SKILL.md)
SKILLS_WITH_REFERENCES = {"rai-epic-plan", "rai-research", "rai-story-design"}


class TestScaffoldSkills:
    """Tests for scaffold_skills() function."""

    def test_copies_all_skills(self, tmp_path: Path) -> None:
        """Should copy all distributable skills to .claude/skills/."""
        result = scaffold_skills(tmp_path)

        skills_dir = tmp_path / ".claude" / "skills"
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (skills_dir / skill_name / "SKILL.md").exists(), (
                f"Missing: {skill_name}"
            )
        assert result.skills_copied == TOTAL_SKILLS

    def test_copies_reference_files(self, tmp_path: Path) -> None:
        """Skills with reference subdirectories should have them copied."""
        scaffold_skills(tmp_path)

        skills_dir = tmp_path / ".claude" / "skills"
        assert (
            skills_dir / "rai-epic-plan" / "_references" / "sequencing-strategies.md"
        ).exists()
        assert (
            skills_dir / "rai-research" / "references" / "research-prompt-template.md"
        ).exists()
        assert (
            skills_dir / "rai-story-design" / "references" / "tech-design-story-v2.md"
        ).exists()

    def test_skill_content_has_frontmatter(self, tmp_path: Path) -> None:
        """Copied skills should have YAML frontmatter."""
        scaffold_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert content.startswith("---\n") or content.startswith("#")

    def test_skill_content_matches_bundled(self, tmp_path: Path) -> None:
        """Copied skill files should match bundled originals."""
        from importlib.resources import files

        scaffold_skills(tmp_path)

        base = files("rai_cli.skills_base")
        original = (base / "rai-session-start" / "SKILL.md").read_text(encoding="utf-8")
        copied = (
            tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert copied == original

    def test_returns_skill_names(self, tmp_path: Path) -> None:
        """Should return names of copied skills."""
        result = scaffold_skills(tmp_path)

        assert "rai-session-start" in result.skills_installed
        assert "rai-discover-document" in result.skills_installed
        assert "rai-story-implement" in result.skills_installed
        assert "rai-epic-design" in result.skills_installed
        assert "rai-debug" in result.skills_installed
        assert len(result.skills_installed) == TOTAL_SKILLS

    def test_reports_files_copied(self, tmp_path: Path) -> None:
        """Should list all copied files in result."""
        result = scaffold_skills(tmp_path)

        # 17 skills × 1 SKILL.md + 3 reference files = 20 files
        expected_files = TOTAL_SKILLS + len(SKILLS_WITH_REFERENCES)
        assert len(result.files_copied) == expected_files
        assert len(result.files_skipped) == 0
        assert not result.already_existed


class TestScaffoldSkillsIdempotency:
    """Tests for skills scaffolding being safe to run multiple times."""

    def test_does_not_overwrite_existing_skills(self, tmp_path: Path) -> None:
        """Should not overwrite existing skill files."""
        # First scaffold
        scaffold_skills(tmp_path)

        # Modify a skill
        skill_path = tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        skill_path.write_text("# Custom skill")

        # Second scaffold
        result = scaffold_skills(tmp_path)

        assert skill_path.read_text(encoding="utf-8") == "# Custom skill"
        assert "rai-session-start" in result.skills_skipped_names

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second scaffold should report already_existed=True."""
        scaffold_skills(tmp_path)
        result = scaffold_skills(tmp_path)

        assert result.already_existed
        assert len(result.files_skipped) == TOTAL_SKILLS
        assert len(result.files_copied) == 0
        assert result.skills_copied == 0

    def test_copies_only_missing_skills(self, tmp_path: Path) -> None:
        """Should copy missing skills when some already exist."""
        # Create one skill manually
        skill_dir = tmp_path / ".claude" / "skills" / "rai-session-start"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Existing")

        result = scaffold_skills(tmp_path)

        # session-start should be skipped
        assert "rai-session-start" in result.skills_skipped_names
        # Others should be copied
        assert result.skills_copied == TOTAL_SKILLS - 1
        assert (
            tmp_path / ".claude" / "skills" / "rai-discover-start" / "SKILL.md"
        ).exists()
        assert (
            tmp_path / ".claude" / "skills" / "rai-story-implement" / "SKILL.md"
        ).exists()


class TestScaffoldSkillsIdeConfig:
    """Tests for scaffold_skills() with IDE configuration."""

    def test_scaffold_to_antigravity_dir(self, tmp_path: Path) -> None:
        """Should scaffold skills to .agent/skills/ with antigravity config."""
        config = get_agent_config("antigravity")
        result = scaffold_skills(tmp_path, agent_config=config)

        agent_skills = tmp_path / ".agent" / "skills"
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (agent_skills / skill_name / "SKILL.md").exists(), (
                f"Missing: {skill_name}"
            )
        assert result.skills_copied == TOTAL_SKILLS
        # .claude/skills/ should NOT exist
        assert not (tmp_path / ".claude" / "skills").exists()

    def test_scaffold_default_is_claude(self, tmp_path: Path) -> None:
        """Default scaffold (no ide_config) still goes to .claude/skills/."""
        result = scaffold_skills(tmp_path)

        assert (tmp_path / ".claude" / "skills").exists()
        assert result.skills_copied == TOTAL_SKILLS


class TestScaffoldSkillsPartialState:
    """Tests for scaffold when .claude/ is partially populated."""

    def test_handles_existing_claude_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/ exists but skills/ doesn't."""
        (tmp_path / ".claude").mkdir()

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == TOTAL_SKILLS

    def test_handles_existing_skills_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/skills/ exists but is empty."""
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == TOTAL_SKILLS


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
