"""Tests for skill schema models."""

from __future__ import annotations

import pytest

from raise_cli.skills.schema import (
    SkillHook,
    SkillHookCommand,
    SkillMetadata,
    SkillFrontmatter,
    Skill,
)


class TestSkillMetadata:
    """Tests for SkillMetadata model."""

    def test_minimal_metadata(self) -> None:
        """Metadata with only required fields."""
        metadata = SkillMetadata(
            work_cycle="feature",
            version="1.0.0",
        )
        assert metadata.work_cycle == "feature"
        assert metadata.version == "1.0.0"
        assert metadata.frequency is None

    def test_full_metadata(self) -> None:
        """Metadata with all fields populated."""
        metadata = SkillMetadata(
            work_cycle="session",
            frequency="per-session",
            fase="start",
            prerequisites="",
            next="session-close",
            gate="",
            adaptable=True,
            version="3.0.0",
        )
        assert metadata.work_cycle == "session"
        assert metadata.frequency == "per-session"
        assert metadata.fase == "start"
        assert metadata.next == "session-close"
        assert metadata.adaptable is True

    def test_metadata_from_raw_dict(self) -> None:
        """Parse metadata from raw YAML dict with raise. prefix."""
        raw = {
            "raise.work_cycle": "epic",
            "raise.frequency": "per-epic",
            "raise.fase": "1",
            "raise.prerequisites": "epic-start",
            "raise.next": "epic-plan",
            "raise.gate": "",
            "raise.adaptable": "true",
            "raise.version": "2.0.0",
        }
        metadata = SkillMetadata.from_raw(raw)
        assert metadata.work_cycle == "epic"
        assert metadata.frequency == "per-epic"
        assert metadata.fase == "1"
        assert metadata.prerequisites == "epic-start"
        assert metadata.next == "epic-plan"
        assert metadata.adaptable is True
        assert metadata.version == "2.0.0"


class TestSkillHook:
    """Tests for SkillHook models."""

    def test_hook_command(self) -> None:
        """Parse hook command."""
        cmd = SkillHookCommand(
            type="command",
            command='RAISE_SKILL_NAME=test "$CLAUDE_PROJECT_DIR"/.raise/scripts/log-skill-complete.sh',
        )
        assert cmd.type == "command"
        assert "RAISE_SKILL_NAME=test" in cmd.command

    def test_skill_hook(self) -> None:
        """Parse skill hook with nested commands."""
        hook = SkillHook(
            hooks=[
                SkillHookCommand(
                    type="command",
                    command="echo test",
                )
            ]
        )
        assert len(hook.hooks) == 1
        assert hook.hooks[0].command == "echo test"


class TestSkillFrontmatter:
    """Tests for SkillFrontmatter model."""

    def test_minimal_frontmatter(self) -> None:
        """Frontmatter with only required fields."""
        frontmatter = SkillFrontmatter(
            name="test-skill",
            description="A test skill",
        )
        assert frontmatter.name == "test-skill"
        assert frontmatter.description == "A test skill"
        assert frontmatter.license is None
        assert frontmatter.metadata is None
        assert frontmatter.hooks is None

    def test_full_frontmatter(self) -> None:
        """Frontmatter with all fields."""
        frontmatter = SkillFrontmatter(
            name="session-start",
            description="Begin a session",
            license="MIT",
            metadata=SkillMetadata(
                work_cycle="session",
                version="3.0.0",
            ),
            hooks={
                "Stop": [
                    SkillHook(
                        hooks=[
                            SkillHookCommand(type="command", command="echo done")
                        ]
                    )
                ]
            },
        )
        assert frontmatter.name == "session-start"
        assert frontmatter.license == "MIT"
        assert frontmatter.metadata is not None
        assert frontmatter.metadata.work_cycle == "session"
        assert "Stop" in frontmatter.hooks


class TestSkill:
    """Tests for Skill model."""

    def test_skill_with_body(self) -> None:
        """Skill with frontmatter and markdown body."""
        skill = Skill(
            frontmatter=SkillFrontmatter(
                name="test-skill",
                description="A test skill",
            ),
            body="# Test Skill\n\n## Purpose\n\nThis is a test.",
            path="/path/to/skill/SKILL.md",
        )
        assert skill.frontmatter.name == "test-skill"
        assert "# Test Skill" in skill.body
        assert skill.path == "/path/to/skill/SKILL.md"

    def test_skill_name_property(self) -> None:
        """Skill name shortcut property."""
        skill = Skill(
            frontmatter=SkillFrontmatter(
                name="feature-plan",
                description="Plan a feature",
            ),
            body="",
            path="/path/to/skill/SKILL.md",
        )
        assert skill.name == "feature-plan"

    def test_skill_version_property(self) -> None:
        """Skill version from metadata."""
        skill = Skill(
            frontmatter=SkillFrontmatter(
                name="test-skill",
                description="Test",
                metadata=SkillMetadata(
                    work_cycle="utility",
                    version="2.1.0",
                ),
            ),
            body="",
            path="/path/to/skill/SKILL.md",
        )
        assert skill.version == "2.1.0"

    def test_skill_version_none_without_metadata(self) -> None:
        """Skill version is None when no metadata."""
        skill = Skill(
            frontmatter=SkillFrontmatter(
                name="test-skill",
                description="Test",
            ),
            body="",
            path="/path/to/skill/SKILL.md",
        )
        assert skill.version is None

    def test_skill_lifecycle_property(self) -> None:
        """Skill lifecycle from metadata work_cycle."""
        skill = Skill(
            frontmatter=SkillFrontmatter(
                name="epic-design",
                description="Design an epic",
                metadata=SkillMetadata(
                    work_cycle="epic",
                    version="1.0.0",
                ),
            ),
            body="",
            path="/path/to/skill/SKILL.md",
        )
        assert skill.lifecycle == "epic"
