"""Tests for RaiSettings configuration."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from raise_cli.config.settings import RaiSettings


class TestRaiSettingsDefaults:
    """Tests for default values in RaiSettings."""

    def test_output_format_default(self) -> None:
        """Should default to 'human' output format."""
        settings = RaiSettings()
        assert settings.output_format == "human"

    def test_color_default(self) -> None:
        """Should default to color enabled."""
        settings = RaiSettings()
        assert settings.color is True

    def test_verbosity_default(self) -> None:
        """Should default to normal verbosity (0)."""
        settings = RaiSettings()
        assert settings.verbosity == 0

    def test_raise_dir_default(self) -> None:
        """Should default to '.raise' directory."""
        settings = RaiSettings()
        assert settings.raise_dir == Path(".raise")

    def test_governance_dir_default(self) -> None:
        """Should default to 'governance' directory."""
        settings = RaiSettings()
        assert settings.governance_dir == Path("governance")

    def test_work_dir_default(self) -> None:
        """Should default to 'work' directory."""
        settings = RaiSettings()
        assert settings.work_dir == Path("work")

    def test_ast_grep_path_default(self) -> None:
        """Should default to None (auto-detect)."""
        settings = RaiSettings()
        assert settings.ast_grep_path is None

    def test_ripgrep_path_default(self) -> None:
        """Should default to None (auto-detect)."""
        settings = RaiSettings()
        assert settings.ripgrep_path is None

    def test_interactive_default(self) -> None:
        """Should default to non-interactive."""
        settings = RaiSettings()
        assert settings.interactive is False


class TestRaiSettingsConstructorOverride:
    """Tests for overriding settings via constructor (CLI args)."""

    def test_override_output_format(self) -> None:
        """Should allow overriding output_format via constructor."""
        settings = RaiSettings(output_format="json")
        assert settings.output_format == "json"

    def test_override_verbosity(self) -> None:
        """Should allow overriding verbosity via constructor."""
        settings = RaiSettings(verbosity=2)
        assert settings.verbosity == 2

    def test_override_color(self) -> None:
        """Should allow disabling color via constructor."""
        settings = RaiSettings(color=False)
        assert settings.color is False

    def test_override_multiple_fields(self) -> None:
        """Should allow overriding multiple fields at once."""
        settings = RaiSettings(
            output_format="table",
            verbosity=-1,
            color=False,
            interactive=True,
        )
        assert settings.output_format == "table"
        assert settings.verbosity == -1
        assert settings.color is False
        assert settings.interactive is True


class TestRaiSettingsValidation:
    """Tests for field validation in RaiSettings."""

    def test_invalid_output_format(self) -> None:
        """Should reject invalid output format."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSettings(output_format="xml")  # type: ignore[arg-type]
        assert "output_format" in str(exc_info.value)

    def test_verbosity_too_low(self) -> None:
        """Should reject verbosity below -1."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSettings(verbosity=-2)
        assert "verbosity" in str(exc_info.value)

    def test_verbosity_too_high(self) -> None:
        """Should reject verbosity above 3."""
        with pytest.raises(ValidationError) as exc_info:
            RaiSettings(verbosity=4)
        assert "verbosity" in str(exc_info.value)

    def test_verbosity_boundaries_valid(self) -> None:
        """Should accept verbosity at boundaries (-1 and 3)."""
        settings_quiet = RaiSettings(verbosity=-1)
        settings_max = RaiSettings(verbosity=3)
        assert settings_quiet.verbosity == -1
        assert settings_max.verbosity == 3


class TestRaiSettingsEnvironmentVariables:
    """Tests for environment variable overrides."""

    def test_env_var_output_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should read output_format from RAI_OUTPUT_FORMAT env var."""
        monkeypatch.setenv("RAI_OUTPUT_FORMAT", "json")
        settings = RaiSettings()
        assert settings.output_format == "json"

    def test_env_var_verbosity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should read verbosity from RAI_VERBOSITY env var."""
        monkeypatch.setenv("RAI_VERBOSITY", "2")
        settings = RaiSettings()
        assert settings.verbosity == 2

    def test_env_var_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should read color from RAI_COLOR env var."""
        monkeypatch.setenv("RAI_COLOR", "false")
        settings = RaiSettings()
        assert settings.color is False

    def test_constructor_overrides_env_var(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Constructor args should override environment variables."""
        monkeypatch.setenv("RAI_OUTPUT_FORMAT", "json")
        settings = RaiSettings(output_format="table")
        assert settings.output_format == "table"


class TestRaiSettingsTypes:
    """Tests for field types."""

    def test_output_format_is_literal(self) -> None:
        """output_format should be Literal type."""
        settings = RaiSettings(output_format="human")
        assert settings.output_format in ("human", "json", "table")

    def test_paths_are_path_objects(self) -> None:
        """Path fields should be Path objects, not strings."""
        settings = RaiSettings()
        assert isinstance(settings.raise_dir, Path)
        assert isinstance(settings.governance_dir, Path)
        assert isinstance(settings.work_dir, Path)

    def test_path_field_accepts_string(self) -> None:
        """Path fields should accept string input and convert to Path."""
        settings = RaiSettings(raise_dir="/custom/raise")  # type: ignore[arg-type]
        assert settings.raise_dir == Path("/custom/raise")
        assert isinstance(settings.raise_dir, Path)
