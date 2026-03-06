"""Integration tests for configuration cascade precedence.

Tests the 5-level configuration cascade:
1. CLI arguments (constructor)
2. Environment variables
3. Project pyproject.toml
4. User config (~/.config/rai/config.toml)
5. Defaults
"""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.config.settings import RaiSettings


class TestConfigurationCascade:
    """Tests for complete configuration cascade precedence."""

    def test_defaults_when_no_overrides(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Level 5: Defaults should be used when nothing else is set."""
        # Clear all possible override sources
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)
        monkeypatch.chdir(tmp_path)  # No pyproject.toml
        monkeypatch.setenv("HOME", str(tmp_path))  # No user config

        settings = RaiSettings()
        assert settings.output_format == "human"
        assert settings.verbosity == 0
        assert settings.color is True

    def test_user_config_overrides_defaults(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Level 4: User config should override defaults."""
        # Set up user config
        config_dir = tmp_path / ".config" / "rai"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text("""
[rai]
output_format = "json"
verbosity = 2
color = false
""")

        # Point to our test user config
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)
        monkeypatch.chdir(tmp_path)  # No pyproject.toml

        settings = RaiSettings()
        assert settings.output_format == "json"
        assert settings.verbosity == 2
        assert settings.color is False

    def test_project_config_overrides_user_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Level 3: Project pyproject.toml should override user config."""
        # Set up user config
        config_dir = tmp_path / ".config" / "rai"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text("""
[rai]
output_format = "json"
verbosity = 1
""")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

        # Set up project config (should win)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text("""
[tool.rai]
output_format = "table"
verbosity = 3
""")

        monkeypatch.chdir(project_dir)
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)

        settings = RaiSettings()
        assert settings.output_format == "table"
        assert settings.verbosity == 3

    def test_env_vars_override_project_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Level 2: Environment variables should override project config."""
        # Set up project config
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.rai]
output_format = "table"
verbosity = 2
color = true
""")

        monkeypatch.chdir(tmp_path)

        # Set env vars (should win)
        monkeypatch.setenv("RAI_OUTPUT_FORMAT", "json")
        monkeypatch.setenv("RAI_VERBOSITY", "1")
        monkeypatch.setenv("RAI_COLOR", "false")

        settings = RaiSettings()
        assert settings.output_format == "json"
        assert settings.verbosity == 1
        assert settings.color is False

    def test_cli_args_override_env_vars(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Level 1: CLI arguments should override environment variables."""
        # Set up env vars
        monkeypatch.setenv("RAI_OUTPUT_FORMAT", "json")
        monkeypatch.setenv("RAI_VERBOSITY", "2")

        # Constructor args should win
        settings = RaiSettings(output_format="table", verbosity=3)
        assert settings.output_format == "table"
        assert settings.verbosity == 3

    def test_full_cascade_all_levels(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test complete cascade with all 5 levels configured."""
        # Level 5: Defaults (color=True, interactive=False)

        # Level 4: User config
        config_dir = tmp_path / ".config" / "rai"
        config_dir.mkdir(parents=True)
        (config_dir / "config.toml").write_text("""
[rai]
output_format = "json"
verbosity = 1
color = false
interactive = true
""")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

        # Level 3: Project config (should override user for output_format)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text("""
[tool.rai]
output_format = "table"
""")
        monkeypatch.chdir(project_dir)

        # Level 2: Env var (should override project for verbosity)
        monkeypatch.setenv("RAI_VERBOSITY", "2")

        # Level 1: CLI arg (should override everything for color)
        settings = RaiSettings(color=True)

        # Verify cascade:
        assert settings.color is True  # From CLI (level 1)
        assert settings.verbosity == 2  # From env var (level 2)
        assert settings.output_format == "table"  # From project config (level 3)
        assert settings.interactive is True  # From user config (level 4)
        # (No field uses default in this test since all are overridden)


class TestConfigurationEdgeCases:
    """Tests for edge cases and error handling."""

    def test_malformed_pyproject_toml_graceful_degradation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should gracefully handle malformed pyproject.toml."""
        # Create invalid TOML
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("this is not valid toml [[[")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)

        # Should fall back to defaults without crashing
        settings = RaiSettings()
        assert settings.output_format == "human"

    def test_malformed_user_config_graceful_degradation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should gracefully handle malformed user config."""
        config_dir = tmp_path / ".config" / "rai"
        config_dir.mkdir(parents=True)
        (config_dir / "config.toml").write_text("invalid toml content {{{")

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)

        # Should fall back to defaults without crashing
        settings = RaiSettings()
        assert settings.output_format == "human"

    def test_missing_config_files_no_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should not error when config files don't exist."""
        monkeypatch.chdir(tmp_path)  # No pyproject.toml
        monkeypatch.setenv("HOME", str(tmp_path))  # No user config
        monkeypatch.delenv("RAI_OUTPUT_FORMAT", raising=False)

        settings = RaiSettings()
        assert settings.output_format == "human"

    def test_partial_config_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should handle config files with only some fields set."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.rai]
output_format = "json"
# verbosity intentionally not set
""")

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("RAI_VERBOSITY", raising=False)

        settings = RaiSettings()
        assert settings.output_format == "json"  # From config
        assert settings.verbosity == 0  # From default


class TestPathConfiguration:
    """Tests for Path field configuration."""

    def test_path_fields_from_toml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Path fields should be loaded correctly from TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.rai]
raise_dir = ".custom-raise"
governance_dir = "gov"
work_dir = "work-dir"
""")

        monkeypatch.chdir(tmp_path)
        settings = RaiSettings()

        assert settings.raise_dir == Path(".custom-raise")
        assert settings.governance_dir == Path("gov")
        assert settings.work_dir == Path("work-dir")
