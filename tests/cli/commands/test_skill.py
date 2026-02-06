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
