"""Tests for skill name checker."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.skills.name_checker import (
    NameCheckResult,
    check_name,
)


class TestNameCheckResult:
    """Tests for NameCheckResult model."""

    def test_is_valid_when_no_errors(self) -> None:
        """A result with only warnings/suggestions is valid."""
        result = NameCheckResult(
            name="session-validate",
            valid_pattern=True,
            no_skill_conflict=True,
            no_cli_conflict=True,
            known_lifecycle=True,
            suggestions=["Consider adding after rai-session-start"],
        )
        assert result.is_valid is True

    def test_is_valid_when_pattern_invalid(self) -> None:
        """Invalid pattern makes result invalid."""
        result = NameCheckResult(
            name="badname",
            valid_pattern=False,
            no_skill_conflict=True,
            no_cli_conflict=True,
            known_lifecycle=True,
        )
        assert result.is_valid is False

    def test_is_valid_when_skill_conflict(self) -> None:
        """Skill conflict makes result invalid."""
        result = NameCheckResult(
            name="rai-session-start",
            valid_pattern=True,
            no_skill_conflict=False,
            no_cli_conflict=True,
            known_lifecycle=True,
            conflicting_skill="rai-session-start",
        )
        assert result.is_valid is False

    def test_is_valid_when_cli_conflict(self) -> None:
        """CLI command conflict makes result invalid."""
        result = NameCheckResult(
            name="memory-build",
            valid_pattern=True,
            no_skill_conflict=True,
            no_cli_conflict=False,
            known_lifecycle=True,
            conflicting_command="memory build",
        )
        assert result.is_valid is False


class TestCheckName:
    """Tests for check_name function."""

    def test_valid_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A valid name passes all checks."""
        # Create empty skill dir
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = check_name("story-validate")

        assert result.is_valid
        assert result.valid_pattern
        assert result.no_skill_conflict
        assert result.no_cli_conflict
        assert result.known_lifecycle

    def test_invalid_pattern_no_hyphen(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Name without hyphen is invalid."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = check_name("badname")

        assert not result.is_valid
        assert not result.valid_pattern

    def test_invalid_pattern_uppercase(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Name with uppercase is invalid."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = check_name("Session-Start")

        assert not result.is_valid
        assert not result.valid_pattern

    def test_conflict_with_existing_skill(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Name that conflicts with existing skill is invalid."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)

        # Create existing skill
        existing = skills / "rai-session-start"
        existing.mkdir()
        (existing / "SKILL.md").write_text("""\
---
name: rai-session-start
description: Test
metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---
# Test
""")

        monkeypatch.chdir(tmp_path)
        result = check_name("rai-session-start")

        assert not result.is_valid
        assert not result.no_skill_conflict
        assert result.conflicting_skill == "rai-session-start"

    def test_conflict_with_cli_command(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Name that conflicts with CLI command is invalid."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        # PAT-132: CLI commands are reserved
        result = check_name("memory-build")

        assert not result.is_valid
        assert not result.no_cli_conflict
        assert "memory" in result.conflicting_command.lower()

    def test_unknown_lifecycle(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unknown lifecycle domain is noted but valid."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = check_name("custom-action")

        # Unknown lifecycle is a warning, not error
        assert result.is_valid
        assert not result.known_lifecycle

    def test_known_lifecycles(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Known lifecycles are recognized."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        known = ["session", "epic", "story", "discover", "skill"]
        for lifecycle in known:
            result = check_name(f"{lifecycle}-test")
            assert result.known_lifecycle, f"{lifecycle} should be known"

    def test_suggestions_for_positioning(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Suggestions include positioning hints for known lifecycles."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)

        # Create related skills
        for name in ["rai-session-start", "rai-session-close"]:
            skill_dir = skills / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"""\
---
name: {name}
description: Test
metadata:
  raise.work_cycle: session
  raise.version: "1.0.0"
---
# Test
""")

        monkeypatch.chdir(tmp_path)
        result = check_name("session-validate")

        assert result.is_valid
        # Should suggest positioning relative to existing session skills
        assert len(result.suggestions) > 0
