"""Tests for XDG directory path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.config.paths import (
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_global_rai_dir,
    get_personal_dir,
)


class TestGetConfigDir:
    """Tests for get_config_dir() function."""

    def test_default_config_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.config/raise when XDG_CONFIG_HOME not set."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_config_dir()
        expected = Path.home() / ".config" / "raise"
        assert result == expected

    def test_xdg_config_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_CONFIG_HOME environment variable."""
        custom_config = "/custom/config"
        monkeypatch.setenv("XDG_CONFIG_HOME", custom_config)
        result = get_config_dir()
        expected = Path(custom_config) / "raise"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_config_dir()
        assert isinstance(result, Path)


class TestGetCacheDir:
    """Tests for get_cache_dir() function."""

    def test_default_cache_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.cache/raise when XDG_CACHE_HOME not set."""
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        result = get_cache_dir()
        expected = Path.home() / ".cache" / "raise"
        assert result == expected

    def test_xdg_cache_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_CACHE_HOME environment variable."""
        custom_cache = "/custom/cache"
        monkeypatch.setenv("XDG_CACHE_HOME", custom_cache)
        result = get_cache_dir()
        expected = Path(custom_cache) / "raise"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        result = get_cache_dir()
        assert isinstance(result, Path)


class TestGetDataDir:
    """Tests for get_data_dir() function."""

    def test_default_data_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.local/share/raise when XDG_DATA_HOME not set."""
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        expected = Path.home() / ".local" / "share" / "raise"
        assert result == expected

    def test_xdg_data_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_DATA_HOME environment variable."""
        custom_data = "/custom/data"
        monkeypatch.setenv("XDG_DATA_HOME", custom_data)
        result = get_data_dir()
        expected = Path(custom_data) / "raise"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        assert isinstance(result, Path)


class TestGetGlobalRaiDir:
    """Tests for get_global_rai_dir() function."""

    def test_default_global_rai_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.rai by default."""
        # Ensure no override is set
        monkeypatch.delenv("RAI_HOME", raising=False)
        result = get_global_rai_dir()
        expected = Path.home() / ".rai"
        assert result == expected

    def test_rai_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect RAI_HOME environment variable."""
        custom_rai = "/custom/rai"
        monkeypatch.setenv("RAI_HOME", custom_rai)
        result = get_global_rai_dir()
        expected = Path(custom_rai)
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("RAI_HOME", raising=False)
        result = get_global_rai_dir()
        assert isinstance(result, Path)


class TestGetPersonalDir:
    """Tests for get_personal_dir() function."""

    def test_default_personal_dir(self, tmp_path: Path) -> None:
        """Should return .raise/rai/personal/ within project root."""
        result = get_personal_dir(tmp_path)
        expected = tmp_path / ".raise" / "rai" / "personal"
        assert result == expected

    def test_personal_dir_current_directory(self) -> None:
        """Should use cwd when no project_root provided."""
        result = get_personal_dir()
        expected = Path.cwd() / ".raise" / "rai" / "personal"
        assert result == expected

    def test_returns_path_object(self, tmp_path: Path) -> None:
        """Should return a Path object, not a string."""
        result = get_personal_dir(tmp_path)
        assert isinstance(result, Path)
