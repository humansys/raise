"""Tests for the raise init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import BranchConfig, load_manifest, save_manifest
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
        assert "next" in output_lower or "/rai-session-start" in result.output

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
        content = guardrails_path.read_text(encoding="utf-8")

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
        content = guardrails_path.read_text(encoding="utf-8")
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

    def test_detect_claude_md_contains_raise_content(
        self, python_project: Path, mock_home: Path
    ) -> None:
        """Generated CLAUDE.md contains RaiSE content (init creates .raise/)."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(python_project), "--detect", "--name", "my-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        claude_md_path = python_project / "CLAUDE.md"
        content = claude_md_path.read_text(encoding="utf-8")

        # After init, .raise/ exists so CLAUDE.md is generated from .raise/ sources
        assert "Generated from .raise/ canonical source" in content
        assert "## Rai Identity" in content
        assert "## Process Rules" in content

    def test_detect_greenfield_generates_claude_md(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect on greenfield generates CLAUDE.md from .raise/ sources."""
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
        content = claude_md_path.read_text(encoding="utf-8")
        # After init, .raise/ exists so CLAUDE.md is generated from .raise/ sources
        assert "Generated from .raise/ canonical source" in content


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
        assert (identity_dir / "core.yaml").exists()
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
        assert "BASE-001" in patterns.read_text(encoding="utf-8")

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
        assert "version:" in methodology.read_text(encoding="utf-8")

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
        core_path = greenfield_project / ".raise" / "rai" / "identity" / "core.yaml"
        core_path.write_text("values: []")

        # Second init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert core_path.read_text(encoding="utf-8") == "values: []"

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
        canonical = greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.exists()
        content = canonical.read_text(encoding="utf-8")
        assert "# Rai Memory" in content
        assert "RaiSE Framework Process" in content

    def test_init_generates_claude_md_for_raise_project(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init (without --detect) generates CLAUDE.md with Rai sections when .raise/ exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0

        # After init, .raise/ exists (created by bootstrap), so CLAUDE.md should be generated
        claude_md = greenfield_project / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md should be generated for RaiSE projects"
        content = claude_md.read_text(encoding="utf-8")

        # Should have the generated header comment
        assert "Generated from .raise/ canonical source" in content
        # Should have Rai-specific sections
        assert "## Rai Identity" in content
        assert "## Process Rules" in content
        assert "## CLI Quick Reference" in content
        assert "## File Operations" in content
        assert "## Post-Compaction Context Restoration" in content

    def test_init_creates_personal_dir_with_gitkeep(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should create .raise/rai/personal/.gitkeep for developer workspace."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        personal_dir = greenfield_project / ".raise" / "rai" / "personal"
        assert personal_dir.is_dir()
        gitkeep = personal_dir / ".gitkeep"
        assert gitkeep.exists(), (
            ".raise/rai/personal/.gitkeep should be created by init"
        )


class TestInitMemoryMdBranches:
    """Tests for MEMORY.md branch substitution during init."""

    def test_init_memory_md_no_placeholder_leak(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Generated MEMORY.md must not contain raw {development_branch} placeholder."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        canonical = greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        content = canonical.read_text(encoding="utf-8")
        assert "{development_branch}" not in content

    def test_init_memory_md_uses_default_main_branch(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Default init produces MEMORY.md with 'main' as development branch."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        canonical = greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        content = canonical.read_text(encoding="utf-8")
        assert "main (development)" in content

    def test_init_memory_md_no_hardcoded_v2(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Generated MEMORY.md must not contain hardcoded 'v2' as branch name."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        canonical = greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        content = canonical.read_text(encoding="utf-8")
        assert "v2 (development)" not in content
        assert "branch (v2)" not in content


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
        assert (skills_dir / "rai-session-start" / "SKILL.md").exists()
        assert (skills_dir / "rai-discover" / "SKILL.md").exists()

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
            greenfield_project / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        )
        skill_path.write_text("# Custom skill")

        # Second init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert skill_path.read_text(encoding="utf-8") == "# Custom skill"

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


class TestInitGovernanceScaffolding:
    """Tests for governance scaffolding integration in raise init."""

    def test_init_creates_governance_directory(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should scaffold governance/ with template files."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        gov_dir = greenfield_project / "governance"
        assert gov_dir.is_dir()
        assert (gov_dir / "prd.md").exists()
        assert (gov_dir / "vision.md").exists()
        assert (gov_dir / "guardrails.md").exists()
        assert (gov_dir / "backlog.md").exists()
        assert (gov_dir / "architecture" / "system-context.md").exists()
        assert (gov_dir / "architecture" / "system-design.md").exists()

    def test_init_renders_project_name_in_templates(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init should render project name in governance templates."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--name", "my-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        prd = (greenfield_project / "governance" / "prd.md").read_text(encoding="utf-8")
        assert "# PRD: my-api" in prd
        assert "{project_name}" not in prd

    def test_init_does_not_overwrite_existing_governance(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Re-running init should not overwrite existing governance files."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # First init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        # Modify a governance file
        prd_path = greenfield_project / "governance" / "prd.md"
        prd_path.write_text("# My Custom PRD\n")

        # Second init
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert prd_path.read_text(encoding="utf-8") == "# My Custom PRD\n"

    def test_shu_output_includes_governance_info(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Shu users should see governance scaffolding in output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "governance" in result.output.lower()


class TestInitSkillRecommendation:
    """Tests for skill recommendation in init output."""

    def test_greenfield_recommends_project_create(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Greenfield project should recommend /project-create."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "/rai-project-create" in result.output

    def test_brownfield_recommends_project_onboard(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """Brownfield project should recommend /project-onboard."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "/rai-project-onboard" in result.output


class TestInitIdeFlag:
    """Tests for --ide flag (multi-IDE scaffolding)."""

    def test_default_produces_claude_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Default rai init (no --ide) produces .claude/ structure."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Claude structure
        assert (
            greenfield_project / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()
        assert not (greenfield_project / ".agent").exists()

    def test_explicit_claude_identical_to_default(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--ide claude produces same structure as default."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--ide", "claude"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (
            greenfield_project / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()
        assert not (greenfield_project / ".agent").exists()

    def test_antigravity_produces_agent_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--ide antigravity produces .agent/ structure."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--ide", "antigravity"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Antigravity skills structure
        assert (
            greenfield_project / ".agent" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()
        # Workflows directory created by scaffold_workflows
        assert (greenfield_project / ".agent" / "workflows").is_dir()
        # No Claude structure
        assert not (greenfield_project / ".claude").exists()
        assert not (greenfield_project / "CLAUDE.md").exists()

    def test_antigravity_no_claude_memory_copy(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--ide antigravity does NOT write Claude Code MEMORY.md copy."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with (
            patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home),
            patch("raise_cli.config.paths.get_claude_memory_path") as mock_claude_mem,
        ):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--ide", "antigravity"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Canonical MEMORY.md still exists
        canonical = greenfield_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.exists()
        # get_claude_memory_path should NOT have been called for antigravity
        mock_claude_mem.assert_not_called()

    def test_antigravity_with_detect(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """--ide antigravity --detect writes to .agent/rules/raise.md not CLAUDE.md."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                [
                    "init",
                    "--path",
                    str(brownfield_project),
                    "--ide",
                    "antigravity",
                    "--detect",
                ],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Instructions file at Antigravity path
        assert (brownfield_project / ".agent" / "rules" / "raise.md").exists()
        # NOT at Claude path
        assert not (brownfield_project / "CLAUDE.md").exists()

    def test_canonical_memory_exists_for_both_ides(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Canonical MEMORY.md in .raise/rai/memory/ exists regardless of IDE."""
        mock_home.mkdir(parents=True, exist_ok=True)

        for ide in ("claude", "antigravity"):
            project = greenfield_project / ide
            project.mkdir()
            with patch(
                "raise_cli.onboarding.profile.get_rai_home", return_value=mock_home
            ):
                result = runner.invoke(
                    app,
                    ["init", "--path", str(project), "--ide", ide],
                    catch_exceptions=False,
                )
            assert result.exit_code == 0
            canonical = project / ".raise" / "rai" / "memory" / "MEMORY.md"
            assert canonical.exists(), f"Canonical MEMORY.md missing for --ide {ide}"


class TestInitAgentFlag:
    """Tests for new --agent flag (replaces --ide)."""

    def test_agent_cursor_produces_cursor_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent cursor scaffolds to .cursor/skills/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "cursor"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (
            greenfield_project / ".cursor" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()
        assert not (greenfield_project / ".claude").exists()

    def test_agent_windsurf_produces_windsurf_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent windsurf scaffolds to .windsurf/skills/ and .windsurf/workflows/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "windsurf"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (greenfield_project / ".windsurf" / "skills").exists()
        assert (greenfield_project / ".windsurf" / "workflows").exists()

    def test_multi_agent_produces_both_structures(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent claude --agent cursor scaffolds to both locations."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                [
                    "init",
                    "--path",
                    str(greenfield_project),
                    "--agent",
                    "claude",
                    "--agent",
                    "cursor",
                ],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (
            greenfield_project / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()
        assert (
            greenfield_project / ".cursor" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()

    def test_multi_agent_manifest_stores_all_types(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Manifest agents.types contains all specified agents."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app,
                [
                    "init",
                    "--path",
                    str(greenfield_project),
                    "--agent",
                    "claude",
                    "--agent",
                    "cursor",
                ],
                catch_exceptions=False,
            )

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert "claude" in manifest.agents.types
        assert "cursor" in manifest.agents.types

    def test_agent_takes_priority_over_ide(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent takes priority over --ide when both provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                [
                    "init",
                    "--path",
                    str(greenfield_project),
                    "--agent",
                    "cursor",
                    "--ide",
                    "antigravity",
                ],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (greenfield_project / ".cursor" / "skills").exists()
        assert not (greenfield_project / ".agent").exists()

    def test_unknown_agent_warns_and_falls_back(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Unknown agent type produces warning, falls back to claude."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "nonexistent"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert "Warning" in result.output or "warning" in result.output.lower()
        # Falls back to claude
        assert (greenfield_project / ".claude" / "skills").exists()

    def test_agent_roo_produces_roo_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent roo scaffolds to .roo/skills/."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "roo"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (
            greenfield_project / ".roo" / "skills" / "rai-session-start" / "SKILL.md"
        ).exists()

    def test_agent_roo_detect_generates_instructions(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent roo --detect generates .roo/rules/raise.md instructions."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                [
                    "init",
                    "--path",
                    str(greenfield_project),
                    "--agent",
                    "roo",
                    "--detect",
                ],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (greenfield_project / ".roo" / "rules" / "raise.md").exists()

    def test_agent_roo_no_claude_structure(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent roo does NOT scaffold .claude/ structure."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "roo"],
                catch_exceptions=False,
            )

        assert not (greenfield_project / ".claude").exists()

    def test_agent_cursor_ide_type_consistent(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent cursor writes ide.type: cursor (consistent with agents.types)."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "cursor"],
                catch_exceptions=False,
            )

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.agents.types == ["cursor"]
        assert manifest.ide.type == "cursor"

    def test_agent_windsurf_ide_type_consistent(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--agent windsurf writes ide.type: windsurf (consistent with agents.types)."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--agent", "windsurf"],
                catch_exceptions=False,
            )

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.agents.types == ["windsurf"]
        assert manifest.ide.type == "windsurf"

    def test_default_agent_ide_type_is_claude(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Default init (no --agent) writes ide.type: claude."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            runner.invoke(
                app,
                ["init", "--path", str(greenfield_project)],
                catch_exceptions=False,
            )

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.ide.type == "claude"


class TestInitDetectAgents:
    """Tests for --detect auto-detection of agents."""

    def test_detect_finds_claude_marker(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect picks up CLAUDE.md as claude marker."""
        mock_home.mkdir(parents=True, exist_ok=True)
        (greenfield_project / "CLAUDE.md").write_text("# Claude")

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert "claude" in manifest.agents.types

    def test_detect_generates_agents_md(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect generates AGENTS.md at project root."""
        mock_home.mkdir(parents=True, exist_ok=True)
        (greenfield_project / "CLAUDE.md").write_text("# Claude")

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (greenfield_project / "AGENTS.md").exists()

    def test_detect_no_markers_defaults_to_claude(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect with no markers found defaults to claude."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert (greenfield_project / ".claude" / "skills").exists()

    def test_detect_finds_roo_marker(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """--detect picks up .roo/ directory as roo marker."""
        mock_home.mkdir(parents=True, exist_ok=True)
        (greenfield_project / ".roo").mkdir()

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--detect"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert "roo" in manifest.agents.types


class TestInitPreservesExistingManifest:
    """Regression tests for RAISE-376: rai init must preserve existing manifest config."""

    def test_preserves_branches_development(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Rai init preserves existing branches.development value."""
        from raise_cli.onboarding.manifest import (
            AgentsManifest,
            ProjectInfo,
            ProjectManifest,
        )

        existing = ProjectManifest(
            project=ProjectInfo(name="test", project_type="brownfield"),
            agents=AgentsManifest(types=["claude"]),
            branches=BranchConfig(development="dev", main="main"),
        )
        save_manifest(existing, greenfield_project)

        mock_home.mkdir(parents=True, exist_ok=True)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.branches.development == "dev"

    def test_preserves_tier_config(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Rai init preserves existing tier value."""
        from raise_cli.onboarding.manifest import (
            AgentsManifest,
            ProjectInfo,
            ProjectManifest,
            TierConfig,
        )

        existing = ProjectManifest(
            project=ProjectInfo(name="test", project_type="brownfield"),
            agents=AgentsManifest(types=["claude"]),
            tier=TierConfig(level="enterprise"),
        )
        save_manifest(existing, greenfield_project)

        mock_home.mkdir(parents=True, exist_ok=True)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.tier is not None
        assert manifest.tier.level == "enterprise"
