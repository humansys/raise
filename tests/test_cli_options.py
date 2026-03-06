"""Test CLI global options."""

from __future__ import annotations

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def test_help_flag() -> None:
    """Test --help flag shows global options in usage."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "RaiSE CLI" in result.stdout
    assert "--format" in result.stdout
    assert "--verbose" in result.stdout
    assert "--quiet" in result.stdout


def test_version_flag() -> None:
    """Test --version flag shows version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "raise-cli version" in result.stdout


def test_version_short_flag() -> None:
    """Test -V short flag shows version."""
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert "raise-cli version" in result.stdout


def test_invalid_format_rejected() -> None:
    """Test invalid format value is rejected by typer."""
    result = runner.invoke(app, ["--format", "invalid"])
    assert result.exit_code == 2  # Typer validation error
    # Check error is about format validation (error goes to stderr in runner)
    output = result.stdout + (result.stderr or "")
    assert "invalid" in output.lower() or "choice" in output.lower()
