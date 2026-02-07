"""Tests for the raise init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import load_manifest
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    ExperienceLevel,
    save_developer_profile,
)

runner = CliRunner()


@pytest.fixture
def mock_home(tmp_path: Path) -> Path:
    """Provide a temporary home directory for tests."""
    return tmp_path / "home"


@pytest.fixture
def greenfield_project(tmp_path: Path) -> Path:
    """Create an empty greenfield project directory."""
    project = tmp_path / "greenfield-project"
    project.mkdir()
    return project


@pytest.fixture
def brownfield_project(tmp_path: Path) -> Path:
    """Create a brownfield project with code files."""
    project = tmp_path / "brownfield-project"
    project.mkdir()
    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')")
    (src / "utils.py").write_text("def helper(): pass")
    (project / "app.py").write_text("from src import main")
    return project


class TestInitCommand:
    """Tests for raise init command."""

    def test_init_creates_manifest(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init creates .raise/manifest.yaml."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None

    def test_init_greenfield_detection(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init detects greenfield project correctly."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "greenfield" in result.output.lower()

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.project_type == ProjectType.GREENFIELD

    def test_init_brownfield_detection(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """Init detects brownfield project correctly."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "brownfield" in result.output.lower()

        manifest = load_manifest(brownfield_project)
        assert manifest is not None
        assert manifest.project.project_type == ProjectType.BROWNFIELD
        assert manifest.project.code_file_count == 3

    def test_init_creates_new_profile(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init creates new developer profile if none exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Check profile was created
        profile_path = mock_home / "developer.yaml"
        assert profile_path.exists()

    def test_init_loads_existing_profile(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init loads existing developer profile."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create existing profile
        existing_profile = DeveloperProfile(
            name="Test User",
            experience_level=ExperienceLevel.RI,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(existing_profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Should welcome back existing user
        assert (
            "test user" in result.output.lower()
            or "welcome back" in result.output.lower()
        )


class TestInitOutputAdaptation:
    """Tests for experience-level adaptive output."""

    def test_shu_output_is_verbose(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Shu users get verbose, educational output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Shu output should include welcome and next steps
        output_lower = result.output.lower()
        assert "welcome" in output_lower or "rai" in output_lower
        assert "next" in output_lower or "/session-start" in result.output

    def test_ri_output_is_concise(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Ri users get concise output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create Ri-level profile
        ri_profile = DeveloperProfile(
            name="Expert",
            experience_level=ExperienceLevel.RI,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(ri_profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Ri output should be shorter (less verbose)
        # Check that it doesn't have the full welcome text
        output_lines = [line for line in result.output.split("\n") if line.strip()]
        # Ri output should be more concise
        assert len(output_lines) < 15  # Reasonable limit for concise output


class TestInitIdempotency:
    """Tests for init being safe to run multiple times."""

    def test_init_updates_existing_manifest(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """Running init again updates the manifest."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            # First init
            result1 = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )
            assert result1.exit_code == 0

            # Add more files
            (brownfield_project / "new_module.py").write_text("# new")

            # Second init
            result2 = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )
            assert result2.exit_code == 0

        manifest = load_manifest(brownfield_project)
        assert manifest is not None
        assert manifest.project.code_file_count == 4  # 3 original + 1 new


class TestInitWithCustomName:
    """Tests for --name option."""

    def test_init_with_custom_name(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init uses custom name when provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--name", "my-custom-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.name == "my-custom-api"

    def test_init_defaults_to_directory_name(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init uses directory name when --name not provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.name == "greenfield-project"


class TestInitWithDetect:
    """Tests for --detect option (convention detection and guardrails generation)."""

    @pytest.fixture
    def python_project(self, tmp_path: Path) -> Path:
        """Create a Python project with detectable conventions."""
        project = tmp_path / "python-project"
        project.mkdir()
        src = project / "src" / "mypackage"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text('"""Package init."""\n')

        # Files with consistent style for HIGH confidence detection
        for i in range(15):
            content = f'''"""Module {i}."""


def function_{i}(value: str) -> str:
    """Process value."""
    return value.upper()


class Handler{i}:
    """Handler class."""

    def handle(self) -> None:
        """Handle request."""
        pass
'''
            (src / f"module_{i}.py").write_text(content)

        # Tests directory
        tests = project / "tests"
        tests.mkdir()
        (tests / "__init__.py").write_text("")
        (tests / "test_main.py").write_text("def test_example(): pass\n")

        return project

    def test_detect_generates_guardrails_file(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """--detect generates governance/guardrails.md."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        guardrails_path = python_project / "governance" / "guardrails.md"
        assert guardrails_path.exists(), f"Expected {guardrails_path} to exist"

    def test_detect_guardrails_contain_conventions(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """Generated guardrails reflect detected conventions."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        guardrails_path = python_project / "governance" / "guardrails.md"
        content = guardrails_path.read_text()

        # Should contain style guardrails
        assert "Code Style" in content
        # Should contain naming guardrails
        assert "Naming" in content
        # Should have structure (src layout detected)
        assert "src/" in content

    def test_detect_outputs_summary(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """--detect outputs detection summary to console."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        output_lower = result.output.lower()
        # Should mention convention detection
        assert "convention" in output_lower or "guardrail" in output_lower

    def test_detect_greenfield_skips_guardrails(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect on greenfield doesn't create guardrails (nothing to detect)."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        guardrails_path = (
            greenfield_project / "governance" / "solution" / "guardrails.md"
        )
        # Greenfield has no code to analyze - guardrails not generated
        assert not guardrails_path.exists()
        # But CLAUDE.md is still created
        claude_md_path = greenfield_project / "CLAUDE.md"
        assert claude_md_path.exists()

    def test_detect_includes_project_name_in_guardrails(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """Generated guardrails include project name."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect", "--name", "my-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        guardrails_path = python_project / "governance" / "guardrails.md"
        content = guardrails_path.read_text()
        assert "my-api" in content

    def test_detect_generates_claude_md(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """--detect generates CLAUDE.md for brownfield projects."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        claude_md_path = python_project / "CLAUDE.md"
        assert claude_md_path.exists(), f"Expected {claude_md_path} to exist"

    def test_detect_claude_md_contains_conventions(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """Generated CLAUDE.md contains convention summary."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect", "--name", "my-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        claude_md_path = python_project / "CLAUDE.md"
        content = claude_md_path.read_text()

        # Should contain project name
        assert "my-api" in content
        # Should contain conventions summary
        assert "Conventions" in content or "convention" in content.lower()
        # Should reference guardrails
        assert "guardrails" in content.lower()

    def test_detect_greenfield_generates_claude_md(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect on greenfield generates minimal CLAUDE.md."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        claude_md_path = greenfield_project / "CLAUDE.md"
        assert claude_md_path.exists()
        content = claude_md_path.read_text()
        assert "greenfield" in content.lower()


class TestInitBootstrap:
    """Tests for bootstrap integration in raise init."""

    def test_init_creates_identity_files(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should copy base identity files to .raise/rai/identity/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        identity_dir = greenfield_project / ".raise" / "rai" / "identity"
        assert (identity_dir / "core.md").exists()
        assert (identity_dir / "perspective.md").exists()

    def test_init_creates_patterns_file(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should copy base patterns to .raise/rai/memory/patterns.jsonl."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        patterns = greenfield_project / ".raise" / "rai" / "memory" / "patterns.jsonl"
        assert patterns.exists()
        assert "BASE-001" in patterns.read_text()

    def test_init_creates_methodology_file(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should copy methodology.yaml to .raise/rai/framework/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        methodology = (
            greenfield_project / ".raise" / "rai" / "framework" / "methodology.yaml"
        )
        assert methodology.exists()
        assert "version:" in methodology.read_text()

    def test_init_does_not_overwrite_existing_identity(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Re-running init should not overwrite existing identity files."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # First init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        # Modify identity
        core_path = greenfield_project / ".raise" / "rai" / "identity" / "core.md"
        core_path.write_text("# Custom identity")

        # Second init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert core_path.read_text() == "# Custom identity"

    def test_shu_output_includes_bootstrap_info(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Shu users should see bootstrap details in output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        output_lower = result.output.lower()
        assert "identity" in output_lower or "rai" in output_lower

    def test_init_generates_canonical_memory_md(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should generate MEMORY.md to canonical location."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        canonical = (
            greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        )
        assert canonical.exists()
        content = canonical.read_text()
        assert "# Rai Memory" in content
        assert "RaiSE Framework Process" in content


class TestInitSkillScaffolding:
    """Tests for skill scaffolding integration in raise init."""

    def test_init_creates_skill_files(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should scaffold onboarding skills to .claude/skills/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        skills_dir = greenfield_project / ".claude" / "skills"
        assert (skills_dir / "session-start" / "SKILL.md").exists()
        assert (skills_dir / "discover-start" / "SKILL.md").exists()
        assert (skills_dir / "discover-scan" / "SKILL.md").exists()
        assert (skills_dir / "discover-validate" / "SKILL.md").exists()
        assert (skills_dir / "discover-complete" / "SKILL.md").exists()

    def test_init_does_not_overwrite_existing_skills(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Re-running init should not overwrite existing skill files."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # First init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        # Modify a skill
        skill_path = (
            greenfield_project / ".claude" / "skills" / "session-start" / "SKILL.md"
        )
        skill_path.write_text("# Custom skill")

        # Second init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert skill_path.read_text() == "# Custom skill"

    def test_shu_output_includes_skills_info(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Shu users should see skills scaffolding in output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "skills" in result.output.lower()
