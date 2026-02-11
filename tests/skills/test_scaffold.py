"""Tests for skill scaffolding."""

from __future__ import annotations

from pathlib import Path

import pytest

from rai_cli.skills.scaffold import scaffold_skill


class TestScaffoldSkill:
    """Tests for scaffold_skill function."""

    def test_scaffold_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold creates skill directory."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("feature-test")

        assert result.created
        assert (skills / "feature-test").is_dir()
        assert (skills / "feature-test" / "SKILL.md").exists()

    def test_scaffold_with_lifecycle(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold uses specified lifecycle."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("session-test", lifecycle="session")

        assert result.created
        content = (skills / "session-test" / "SKILL.md").read_text()
        assert "raise.work_cycle: session" in content

    def test_scaffold_with_prerequisites(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold uses specified prerequisites."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("feature-test", after="story-start")

        assert result.created
        content = (skills / "feature-test" / "SKILL.md").read_text()
        assert "story-start" in content

    def test_scaffold_with_next(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold uses specified next skill."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("feature-test", before="story-close")

        assert result.created
        content = (skills / "feature-test" / "SKILL.md").read_text()
        assert "story-close" in content

    def test_scaffold_infers_lifecycle_from_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold infers lifecycle from skill name domain."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("session-validate")

        assert result.created
        content = (skills / "session-validate" / "SKILL.md").read_text()
        assert "raise.work_cycle: session" in content

    def test_scaffold_defaults_to_utility(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold defaults to utility lifecycle for unknown domains."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("custom-action")

        assert result.created
        content = (skills / "custom-action" / "SKILL.md").read_text()
        assert "raise.work_cycle: utility" in content

    def test_scaffold_fails_if_exists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold fails if skill already exists."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        existing = skills / "existing-skill"
        existing.mkdir()
        (existing / "SKILL.md").write_text("existing")
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("existing-skill")

        assert not result.created
        assert "exists" in result.error.lower()

    def test_scaffold_returns_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold returns path to created skill."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("test-skill")

        assert result.created
        assert result.path is not None
        assert "test-skill" in str(result.path)

    def test_scaffold_creates_valid_skill(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffolded skill passes validation."""
        from rai_cli.skills.validator import validate_skill_file

        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        scaffold_skill("feature-test")

        result = validate_skill_file(skills / "feature-test" / "SKILL.md")
        assert result.is_valid, f"Validation errors: {result.errors}"

    def test_scaffold_no_skill_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scaffold creates skill dir if it doesn't exist."""
        monkeypatch.chdir(tmp_path)

        result = scaffold_skill("test-skill")

        assert result.created
        assert (tmp_path / ".claude" / "skills" / "test-skill" / "SKILL.md").exists()
