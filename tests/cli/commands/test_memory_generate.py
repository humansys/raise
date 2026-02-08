"""Tests for `raise memory generate` command (deprecated)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


class TestMemoryGenerate:
    """Tests for deprecated `raise memory generate` command."""

    def test_generate_is_deprecated(self) -> None:
        """Should show deprecation message."""
        result = runner.invoke(
            app,
            ["memory", "generate"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        assert "deprecated" in result.output.lower()

    def test_generate_does_not_write_files(self, tmp_path: Path) -> None:
        """Should not write any MEMORY.md files."""
        result = runner.invoke(
            app,
            ["memory", "generate", "--path", str(tmp_path)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        canonical = tmp_path / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert not canonical.exists()

    def test_generate_suggests_memory_build(self) -> None:
        """Should suggest using raise memory build instead."""
        result = runner.invoke(
            app,
            ["memory", "generate"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        assert "raise memory build" in result.output

    def test_generate_suggests_session_start(self) -> None:
        """Should mention raise session start --context."""
        result = runner.invoke(
            app,
            ["memory", "generate"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        assert "raise session start --context" in result.output
