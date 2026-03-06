"""Tests for skill locator."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.config.agents import get_agent_config
from raise_cli.skills.locator import (
    SkillLocator,
    get_default_skill_dir,
    list_skills,
)


@pytest.fixture
def skill_dir(tmp_path: Path) -> Path:
    """Create a temporary skill directory with test skills."""
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)

    # Create rai-session-start skill
    session_start = skills / "rai-session-start"
    session_start.mkdir()
    (session_start / "SKILL.md").write_text(
        dedent("""\
        ---
        name: rai-session-start
        description: Begin a session
        metadata:
          raise.work_cycle: session
          raise.version: "3.0.0"
        ---
        # Session Start
    """)
    )

    # Create rai-story-plan skill
    feature_plan = skills / "rai-story-plan"
    feature_plan.mkdir()
    (feature_plan / "SKILL.md").write_text(
        dedent("""\
        ---
        name: rai-story-plan
        description: Plan a feature
        metadata:
          raise.work_cycle: story
          raise.version: "1.0.0"
        ---
        # Story Plan
    """)
    )

    # Create rai-debug skill (utility)
    debug = skills / "rai-debug"
    debug.mkdir()
    (debug / "SKILL.md").write_text(
        dedent("""\
        ---
        name: rai-debug
        description: Debug issues
        metadata:
          raise.work_cycle: utility
          raise.version: "1.0.0"
        ---
        # Debug
    """)
    )

    return tmp_path


class TestGetDefaultSkillDir:
    """Tests for default skill directory detection."""

    def test_default_skill_dir(self) -> None:
        """Get default skill directory path."""
        skill_dir = get_default_skill_dir()
        assert skill_dir.name == "skills"
        assert skill_dir.parent.name == ".claude"

    def test_default_skill_dir_with_project_root(self, tmp_path: Path) -> None:
        """Get skill directory relative to project root."""
        skill_dir = get_default_skill_dir(tmp_path)
        assert skill_dir == tmp_path / ".claude" / "skills"

    def test_default_skill_dir_with_ide_config(self, tmp_path: Path) -> None:
        """Get skill directory from IdeConfig."""
        config = get_agent_config("antigravity")
        skill_dir = get_default_skill_dir(tmp_path, agent_config=config)
        assert skill_dir == tmp_path / ".agent" / "skills"

    def test_default_skill_dir_with_claude_config(self, tmp_path: Path) -> None:
        """Claude config produces same path as default."""
        config = get_agent_config("claude")
        skill_dir = get_default_skill_dir(tmp_path, agent_config=config)
        assert skill_dir == tmp_path / ".claude" / "skills"


class TestSkillLocator:
    """Tests for SkillLocator class."""

    def test_init_with_path(self, skill_dir: Path) -> None:
        """Initialize locator with custom path."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        assert locator.skill_dir == skill_dir / ".claude" / "skills"

    def test_find_skill_dirs(self, skill_dir: Path) -> None:
        """Find all skill directories."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        dirs = locator.find_skill_dirs()
        assert len(dirs) == 3
        names = {d.name for d in dirs}
        assert names == {"rai-session-start", "rai-story-plan", "rai-debug"}

    def test_find_skill_dirs_empty(self, tmp_path: Path) -> None:
        """Handle empty skill directory."""
        empty_dir = tmp_path / ".claude" / "skills"
        empty_dir.mkdir(parents=True)
        locator = SkillLocator(empty_dir)
        dirs = locator.find_skill_dirs()
        assert dirs == []

    def test_find_skill_dirs_nonexistent(self, tmp_path: Path) -> None:
        """Handle nonexistent skill directory."""
        locator = SkillLocator(tmp_path / "nonexistent")
        dirs = locator.find_skill_dirs()
        assert dirs == []

    def test_load_skill(self, skill_dir: Path) -> None:
        """Load a single skill."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        skill = locator.load_skill("rai-session-start")
        assert skill is not None
        assert skill.name == "rai-session-start"
        assert skill.version == "3.0.0"

    def test_load_skill_not_found(self, skill_dir: Path) -> None:
        """Return None for nonexistent skill."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        skill = locator.load_skill("nonexistent")
        assert skill is None

    def test_load_all_skills(self, skill_dir: Path) -> None:
        """Load all skills from directory."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        skills = locator.load_all_skills()
        assert len(skills) == 3
        names = {s.name for s in skills}
        assert names == {"rai-session-start", "rai-story-plan", "rai-debug"}

    def test_load_all_skills_sorted(self, skill_dir: Path) -> None:
        """Skills are sorted by name."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        skills = locator.load_all_skills()
        names = [s.name for s in skills]
        assert names == sorted(names)

    def test_group_by_lifecycle(self, skill_dir: Path) -> None:
        """Group skills by lifecycle."""
        locator = SkillLocator(skill_dir / ".claude" / "skills")
        skills = locator.load_all_skills()
        grouped = locator.group_by_lifecycle(skills)

        assert "session" in grouped
        assert "story" in grouped
        assert "utility" in grouped
        assert len(grouped["session"]) == 1
        assert len(grouped["story"]) == 1
        assert len(grouped["utility"]) == 1
        assert grouped["session"][0].name == "rai-session-start"


class TestListSkills:
    """Tests for list_skills convenience function."""

    def test_list_skills(self, skill_dir: Path) -> None:
        """List all skills from directory."""
        skills = list_skills(skill_dir / ".claude" / "skills")
        assert len(skills) == 3

    def test_list_skills_with_project_root(self, skill_dir: Path) -> None:
        """List skills using project root."""
        skills = list_skills(project_root=skill_dir)
        assert len(skills) == 3

    def test_list_skills_with_ide_config(self, skill_dir: Path) -> None:
        """List skills using project root + ide_config resolves correct dir."""
        # Antigravity config points to .agent/skills which doesn't exist in fixture
        config = get_agent_config("antigravity")
        skills = list_skills(project_root=skill_dir, agent_config=config)
        assert len(skills) == 0  # .agent/skills/ doesn't exist in fixture
