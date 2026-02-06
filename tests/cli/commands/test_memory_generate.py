"""Tests for `raise memory generate` command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.bootstrap import bootstrap_rai_base

runner = CliRunner()


@pytest.fixture()
def bootstrapped_project(tmp_path: Path) -> Path:
    """Create a project with bootstrap already run (has methodology + patterns)."""
    project = tmp_path / "my-project"
    project.mkdir()
    # Bootstrap creates methodology.yaml and patterns.jsonl
    bootstrap_rai_base(project)
    return project


class TestMemoryGenerate:
    """Tests for `raise memory generate` command."""

    def test_generates_canonical_memory_md(
        self, bootstrapped_project: Path
    ) -> None:
        """Should write MEMORY.md to .raise/rai/memory/."""
        result = runner.invoke(
            app,
            ["memory", "generate", "--path", str(bootstrapped_project)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        canonical = bootstrapped_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.exists()
        content = canonical.read_text()
        assert "# Rai Memory" in content
        assert "RaiSE Framework Process" in content

    def test_generates_claude_code_memory_md(
        self, bootstrapped_project: Path, tmp_path: Path
    ) -> None:
        """Should write MEMORY.md to Claude Code projects dir."""
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        with patch("raise_cli.config.paths.Path.home", return_value=fake_home):
            result = runner.invoke(
                app,
                ["memory", "generate", "--path", str(bootstrapped_project)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Check Claude Code path was created
        encoded = str(bootstrapped_project).replace("/", "-")
        claude_path = fake_home / ".claude" / "projects" / encoded / "memory" / "MEMORY.md"
        assert claude_path.exists()
        content = claude_path.read_text()
        assert "# Rai Memory" in content

    def test_output_includes_success_message(
        self, bootstrapped_project: Path, tmp_path: Path
    ) -> None:
        """Should print success message with paths."""
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()

        with patch("raise_cli.config.paths.Path.home", return_value=fake_home):
            result = runner.invoke(
                app,
                ["memory", "generate", "--path", str(bootstrapped_project)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert "MEMORY.md" in result.output

    def test_uses_project_name_from_dir(
        self, bootstrapped_project: Path
    ) -> None:
        """Should use directory name as project name."""
        result = runner.invoke(
            app,
            ["memory", "generate", "--path", str(bootstrapped_project)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        canonical = bootstrapped_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        content = canonical.read_text()
        assert "my-project" in content

    def test_includes_patterns_from_project(
        self, bootstrapped_project: Path
    ) -> None:
        """Should include base patterns in generated MEMORY.md."""
        result = runner.invoke(
            app,
            ["memory", "generate", "--path", str(bootstrapped_project)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        canonical = bootstrapped_project / ".raise" / "rai" / "memory" / "MEMORY.md"
        content = canonical.read_text()
        assert "BASE-" in content

    def test_graceful_when_no_methodology(self, tmp_path: Path) -> None:
        """Should still work when methodology.yaml is missing."""
        project = tmp_path / "bare-project"
        project.mkdir()
        # Create minimal .raise dir but no methodology
        (project / ".raise").mkdir()

        result = runner.invoke(
            app,
            ["memory", "generate", "--path", str(project)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        canonical = project / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.exists()
