"""Tests for raise skill CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app


@pytest.fixture
def skill_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary project with skills."""
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)

    # Create session-start skill
    session_start = skills / "session-start"
    session_start.mkdir()
    (session_start / "SKILL.md").write_text(dedent("""\
        ---
        name: session-start
        description: Begin a session by loading memory
        metadata:
          raise.work_cycle: session
          raise.version: "3.0.0"
        ---
        # Session Start
    """))

    # Create feature-plan skill
    feature_plan = skills / "feature-plan"
    feature_plan.mkdir()
    (feature_plan / "SKILL.md").write_text(dedent("""\
        ---
        name: feature-plan
        description: Plan a feature implementation
        metadata:
          raise.work_cycle: feature
          raise.version: "1.0.0"
        ---
        # Feature Plan
    """))

    # Create debug skill
    debug = skills / "debug"
    debug.mkdir()
    (debug / "SKILL.md").write_text(dedent("""\
        ---
        name: debug
        description: Debug issues systematically
        metadata:
          raise.work_cycle: utility
          raise.version: "1.0.0"
        ---
        # Debug
    """))

    monkeypatch.chdir(tmp_path)
    return tmp_path


runner = CliRunner()


class TestSkillList:
    """Tests for raise skill list command."""

    def test_list_skills_human(self, skill_project: Path) -> None:
        """List skills in human-readable format."""
        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0
        assert "session-start" in result.stdout
        assert "feature-plan" in result.stdout
        assert "debug" in result.stdout

    def test_list_skills_json(self, skill_project: Path) -> None:
        """List skills in JSON format."""
        result = runner.invoke(app, ["skill", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "skills" in data
        assert len(data["skills"]) == 3
        names = {s["name"] for s in data["skills"]}
        assert names == {"session-start", "feature-plan", "debug"}

    def test_list_skills_json_structure(self, skill_project: Path) -> None:
        """Verify JSON output structure."""
        result = runner.invoke(app, ["skill", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)

        # Check skill structure
        skill = next(s for s in data["skills"] if s["name"] == "session-start")
        assert skill["version"] == "3.0.0"
        assert skill["lifecycle"] == "session"
        assert "description" in skill
        assert "path" in skill

    def test_list_skills_grouped_by_lifecycle(self, skill_project: Path) -> None:
        """Human output groups skills by lifecycle."""
        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0
        # Check that lifecycle headers appear
        assert "session" in result.stdout.lower()
        assert "feature" in result.stdout.lower()
        assert "utility" in result.stdout.lower()

    def test_list_skills_empty_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Handle empty skill directory gracefully."""
        empty_skills = tmp_path / ".claude" / "skills"
        empty_skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0
        assert "No skills found" in result.stdout or "0" in result.stdout

    def test_list_skills_no_skill_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Handle missing skill directory gracefully."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "list"])
        assert result.exit_code == 0
        assert "No skills found" in result.stdout or "0" in result.stdout


@pytest.fixture
def valid_skill_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary project with valid skills (including required sections)."""
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)

    # Create valid session-start skill
    session_start = skills / "session-start"
    session_start.mkdir()
    (session_start / "SKILL.md").write_text(dedent("""\
        ---
        name: session-start
        description: Begin a session by loading memory
        metadata:
          raise.work_cycle: session
          raise.version: "3.0.0"
        ---
        # Session Start

        ## Purpose

        Load context and propose work.

        ## Context

        When to use this skill.

        ## Steps (1)

        Do the thing.

        ## Output

        What this produces.
    """))

    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestSkillValidate:
    """Tests for raise skill validate command."""

    def test_validate_all_skills(self, valid_skill_project: Path) -> None:
        """Validate all skills in skill directory."""
        result = runner.invoke(app, ["skill", "validate"])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_validate_specific_file(self, valid_skill_project: Path) -> None:
        """Validate a specific skill file."""
        skill_path = valid_skill_project / ".claude" / "skills" / "session-start" / "SKILL.md"
        result = runner.invoke(app, ["skill", "validate", str(skill_path)])
        assert result.exit_code == 0
        # Check for success indicators (path may be wrapped by Rich)
        assert "valid" in result.stdout.lower() or "passed" in result.stdout.lower()

    def test_validate_specific_dir(self, valid_skill_project: Path) -> None:
        """Validate a skill directory (looks for SKILL.md)."""
        skill_dir = valid_skill_project / ".claude" / "skills" / "session-start"
        result = runner.invoke(app, ["skill", "validate", str(skill_dir)])
        assert result.exit_code == 0

    def test_validate_invalid_skill(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Invalid skill returns exit code 1."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)

        # Create invalid skill (missing metadata)
        bad_skill = skills / "bad-skill"
        bad_skill.mkdir()
        (bad_skill / "SKILL.md").write_text(dedent("""\
            ---
            name: bad-skill
            description: Missing metadata
            ---
            # Bad Skill

            No sections.
        """))

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["skill", "validate"])
        assert result.exit_code == 1
        assert "error" in result.stdout.lower() or "✗" in result.stdout

    def test_validate_json_output(self, valid_skill_project: Path) -> None:
        """Validate with JSON output format."""
        result = runner.invoke(app, ["skill", "validate", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "results" in data
        assert "all_valid" in data
        assert data["all_valid"] is True

    def test_validate_nonexistent_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Handle nonexistent path."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["skill", "validate", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_validate_shows_warnings(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Warnings are displayed (e.g., naming convention)."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)

        # Create skill with bad naming (missing hyphen)
        bad_name = skills / "badname"
        bad_name.mkdir()
        (bad_name / "SKILL.md").write_text(dedent("""\
            ---
            name: badname
            description: Skill with bad name
            metadata:
              raise.work_cycle: utility
              raise.version: "1.0.0"
            ---
            # Badname

            ## Purpose

            Test.

            ## Context

            Test.

            ## Steps (1)

            Test.

            ## Output

            Test.
        """))

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["skill", "validate"])
        # Valid but with warnings
        assert result.exit_code == 0
        assert "warning" in result.stdout.lower() or "⚠" in result.stdout


class TestSkillCheckName:
    """Tests for raise skill check-name command."""

    def test_check_name_valid(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Valid name returns exit code 0."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "check-name", "feature-validate"])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_check_name_invalid_pattern(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Invalid pattern returns exit code 1."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "check-name", "badname"])
        assert result.exit_code == 1
        assert "pattern" in result.stdout.lower()

    def test_check_name_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """JSON output format works."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "check-name", "session-test", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "session-test"
        assert data["valid"] is True
        assert "checks" in data

    def test_check_name_skill_conflict(self, valid_skill_project: Path) -> None:
        """Conflicts with existing skill."""
        result = runner.invoke(app, ["skill", "check-name", "session-start"])
        assert result.exit_code == 1
        assert "conflict" in result.stdout.lower()

    def test_check_name_cli_conflict(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Conflicts with CLI command."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "check-name", "memory-build"])
        assert result.exit_code == 1
        assert "cli" in result.stdout.lower() or "command" in result.stdout.lower()

    def test_check_name_shows_suggestions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Shows suggestions for valid names."""
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["skill", "check-name", "custom-action"])
        # Should show suggestion about unknown lifecycle
        assert result.exit_code == 0
        assert "lifecycle" in result.stdout.lower()
