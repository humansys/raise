"""Tests for XDG directory path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.config.paths import (
    ensure_global_rai_dir,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_developer_sessions_dir,
    get_framework_dir,
    get_global_rai_dir,
    get_identity_dir,
    get_personal_dir,
    get_prefixes_path,
    get_session_dir,
)


class TestGetConfigDir:
    """Tests for get_config_dir() function."""

    def test_default_config_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.config/raise when XDG_CONFIG_HOME not set."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_config_dir()
        expected = Path.home() / ".config" / "rai"
        assert result == expected

    def test_xdg_config_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_CONFIG_HOME environment variable."""
        custom_config = "/custom/config"
        monkeypatch.setenv("XDG_CONFIG_HOME", custom_config)
        result = get_config_dir()
        expected = Path(custom_config) / "rai"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_config_dir()
        assert isinstance(result, Path)

    def test_xdg_config_home_traversal_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """XDG_CONFIG_HOME with .. components must raise ValueError (CWE-23)."""
        monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/safe/../evil")
        with pytest.raises(ValueError, match="must not contain '..' path components"):
            get_config_dir()


class TestGetCacheDir:
    """Tests for get_cache_dir() function."""

    def test_default_cache_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.cache/raise when XDG_CACHE_HOME not set."""
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        result = get_cache_dir()
        expected = Path.home() / ".cache" / "rai"
        assert result == expected

    def test_xdg_cache_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_CACHE_HOME environment variable."""
        custom_cache = "/custom/cache"
        monkeypatch.setenv("XDG_CACHE_HOME", custom_cache)
        result = get_cache_dir()
        expected = Path(custom_cache) / "rai"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        result = get_cache_dir()
        assert isinstance(result, Path)

    def test_xdg_cache_home_traversal_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """XDG_CACHE_HOME with .. components must raise ValueError (CWE-23)."""
        monkeypatch.setenv("XDG_CACHE_HOME", "/tmp/safe/../evil")
        with pytest.raises(ValueError, match="must not contain '..' path components"):
            get_cache_dir()


class TestGetDataDir:
    """Tests for get_data_dir() function."""

    def test_default_data_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return ~/.local/share/raise when XDG_DATA_HOME not set."""
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        expected = Path.home() / ".local" / "share" / "rai"
        assert result == expected

    def test_xdg_data_home_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should respect XDG_DATA_HOME environment variable."""
        custom_data = "/custom/data"
        monkeypatch.setenv("XDG_DATA_HOME", custom_data)
        result = get_data_dir()
        expected = Path(custom_data) / "rai"
        assert result == expected

    def test_returns_path_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return a Path object, not a string."""
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        assert isinstance(result, Path)

    def test_xdg_data_home_traversal_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """XDG_DATA_HOME with .. components must raise ValueError (CWE-23)."""
        monkeypatch.setenv("XDG_DATA_HOME", "/tmp/safe/../evil")
        with pytest.raises(ValueError, match="must not contain '..' path components"):
            get_data_dir()


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

    def test_rai_home_path_traversal_rejected(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """RAI_HOME with .. traversal components must raise ValueError (CWE-23)."""
        traversal = str(tmp_path / "safe" / ".." / "evil")
        monkeypatch.setenv("RAI_HOME", traversal)
        with pytest.raises(ValueError, match="must not contain '..' path components"):
            get_global_rai_dir()

    def test_rai_home_leading_traversal_rejected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RAI_HOME starting with .. must raise ValueError."""
        monkeypatch.setenv("RAI_HOME", "../../../tmp/evil")
        with pytest.raises(ValueError, match="must not contain '..' path components"):
            get_global_rai_dir()

    def test_rai_home_valid_absolute_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """RAI_HOME with a clean absolute path should work fine."""
        clean = str(tmp_path / "custom-rai")
        monkeypatch.setenv("RAI_HOME", clean)
        result = get_global_rai_dir()
        assert result == Path(clean).resolve()
        assert result.is_absolute()


class TestGetIdentityDir:
    """Tests for get_identity_dir() function."""

    def test_default_identity_dir(self, tmp_path: Path) -> None:
        """Should return .raise/rai/identity/ within project root."""
        result = get_identity_dir(tmp_path)
        expected = tmp_path / ".raise" / "rai" / "identity"
        assert result == expected

    def test_identity_dir_current_directory(self) -> None:
        """Should use cwd when no project_root provided."""
        result = get_identity_dir()
        expected = Path.cwd() / ".raise" / "rai" / "identity"
        assert result == expected

    def test_returns_path_object(self, tmp_path: Path) -> None:
        """Should return a Path object, not a string."""
        result = get_identity_dir(tmp_path)
        assert isinstance(result, Path)


class TestGetFrameworkDir:
    """Tests for get_framework_dir() function."""

    def test_default_framework_dir(self, tmp_path: Path) -> None:
        """Should return .raise/rai/framework/ within project root."""
        result = get_framework_dir(tmp_path)
        expected = tmp_path / ".raise" / "rai" / "framework"
        assert result == expected

    def test_framework_dir_current_directory(self) -> None:
        """Should use cwd when no project_root provided."""
        result = get_framework_dir()
        expected = Path.cwd() / ".raise" / "rai" / "framework"
        assert result == expected

    def test_returns_path_object(self, tmp_path: Path) -> None:
        """Should return a Path object, not a string."""
        result = get_framework_dir(tmp_path)
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


class TestGetPrefixesPath:
    """Tests for get_prefixes_path() function."""

    def test_returns_prefixes_path(self, tmp_path: Path) -> None:
        """Should return .raise/rai/prefixes.yaml within project root."""
        result = get_prefixes_path(tmp_path)
        expected = tmp_path / ".raise" / "rai" / "prefixes.yaml"
        assert result == expected


class TestGetDeveloperSessionsDir:
    """Tests for get_developer_sessions_dir() function."""

    def test_returns_developer_sessions_path(self, tmp_path: Path) -> None:
        """Should return .raise/rai/personal/sessions/{prefix}/."""
        result = get_developer_sessions_dir("E", tmp_path)
        expected = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "E"
        assert result == expected

    def test_handles_multi_char_prefix(self, tmp_path: Path) -> None:
        """Should handle multi-character prefixes like 'EO'."""
        result = get_developer_sessions_dir("EO", tmp_path)
        expected = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "EO"
        assert result == expected

    def test_rejects_path_traversal_in_prefix(self, tmp_path: Path) -> None:
        """Prefix with '..' must raise ValueError."""
        with pytest.raises(ValueError, match="path traversal"):
            get_developer_sessions_dir("../evil", tmp_path)

    def test_rejects_slash_in_prefix(self, tmp_path: Path) -> None:
        """Prefix with '/' must raise ValueError."""
        with pytest.raises(ValueError, match="path traversal"):
            get_developer_sessions_dir("E/../../etc", tmp_path)


class TestGetSessionDir:
    """Tests for get_session_dir() function."""

    def test_returns_per_session_path(self, tmp_path: Path) -> None:
        """Should return .raise/rai/personal/sessions/{session_id}/."""
        result = get_session_dir("SES-177", tmp_path)
        expected = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "SES-177"
        assert result == expected

    def test_uses_cwd_when_no_project_root(self) -> None:
        """Should use cwd when no project_root provided."""
        result = get_session_dir("SES-42")
        expected = Path.cwd() / ".raise" / "rai" / "personal" / "sessions" / "SES-42"
        assert result == expected

    def test_returns_path_object(self, tmp_path: Path) -> None:
        """Should return a Path object."""
        result = get_session_dir("SES-1", tmp_path)
        assert isinstance(result, Path)

    def test_session_id_path_traversal_rejected(self, tmp_path: Path) -> None:
        """session_id with .. components must raise ValueError."""
        with pytest.raises(ValueError, match="path traversal"):
            get_session_dir("../../etc/cron.d", tmp_path)

    def test_session_id_deep_traversal_rejected(self, tmp_path: Path) -> None:
        """session_id with deep traversal must raise ValueError."""
        with pytest.raises(ValueError, match="path traversal"):
            get_session_dir("../../../../tmp/evil", tmp_path)


class TestEnsureGlobalRaiDir:
    """Tests for ensure_global_rai_dir() function."""

    def test_creates_directory_if_not_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should create ~/.rai directory if it doesn't exist."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("RAI_HOME", str(fake_home / ".rai"))

        result = ensure_global_rai_dir()

        assert result.exists()
        assert result.is_dir()

    def test_creates_empty_patterns_jsonl(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should create empty patterns.jsonl file."""
        fake_rai = tmp_path / ".rai"
        monkeypatch.setenv("RAI_HOME", str(fake_rai))

        ensure_global_rai_dir()

        patterns_file = fake_rai / "patterns.jsonl"
        assert patterns_file.exists()
        assert patterns_file.read_text(encoding="utf-8") == ""

    def test_creates_empty_calibration_jsonl(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should create empty calibration.jsonl file."""
        fake_rai = tmp_path / ".rai"
        monkeypatch.setenv("RAI_HOME", str(fake_rai))

        ensure_global_rai_dir()

        calibration_file = fake_rai / "calibration.jsonl"
        assert calibration_file.exists()
        assert calibration_file.read_text(encoding="utf-8") == ""

    def test_does_not_overwrite_existing_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should not overwrite existing patterns/calibration files."""
        fake_rai = tmp_path / ".rai"
        fake_rai.mkdir(parents=True)
        patterns_file = fake_rai / "patterns.jsonl"
        patterns_file.write_text('{"id": "PAT-001"}\n')
        monkeypatch.setenv("RAI_HOME", str(fake_rai))

        ensure_global_rai_dir()

        # File should still have original content
        assert patterns_file.read_text(encoding="utf-8") == '{"id": "PAT-001"}\n'

    def test_returns_path_to_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should return Path to the global rai directory."""
        fake_rai = tmp_path / ".rai"
        monkeypatch.setenv("RAI_HOME", str(fake_rai))

        result = ensure_global_rai_dir()

        assert result == fake_rai
        assert isinstance(result, Path)


class TestGetClaudeMemoryPath:
    """Tests for get_claude_memory_path() function."""

    def test_transforms_path_correctly(self) -> None:
        """Should replace / with - and prepend - for Claude Code convention."""
        from raise_cli.config.paths import get_claude_memory_path

        project_root = Path("/home/user/Code/my-project")
        result = get_claude_memory_path(project_root)

        expected = (
            Path.home()
            / ".claude"
            / "projects"
            / "-home-user-Code-my-project"
            / "memory"
            / "MEMORY.md"
        )
        assert result == expected

    def test_handles_root_path(self) -> None:
        """Should handle simple root-level paths."""
        from raise_cli.config.paths import get_claude_memory_path

        project_root = Path("/myproject")
        result = get_claude_memory_path(project_root)

        expected = (
            Path.home() / ".claude" / "projects" / "-myproject" / "memory" / "MEMORY.md"
        )
        assert result == expected

    def test_returns_path_object(self) -> None:
        """Should return a Path object."""
        from raise_cli.config.paths import get_claude_memory_path

        result = get_claude_memory_path(Path("/some/project"))
        assert isinstance(result, Path)

    def test_ends_with_memory_md(self) -> None:
        """Should always end with memory/MEMORY.md."""
        from raise_cli.config.paths import get_claude_memory_path

        result = get_claude_memory_path(Path("/any/path"))
        assert result.name == "MEMORY.md"
        assert result.parent.name == "memory"

    def test_handles_windows_backslashes(self) -> None:
        """Should normalize Windows backslashes to dashes."""
        from raise_cli.config.paths import get_claude_memory_path

        # Simulate a Windows-style path string
        project_root = Path("/C:/Users/emilio/Code/my-project")
        result = get_claude_memory_path(project_root)

        # The encoded part should use dashes, no backslashes or colons
        encoded_part = result.parent.parent.name
        assert "\\" not in encoded_part
        assert ":" not in encoded_part

    def test_handles_windows_drive_letter(self) -> None:
        """Should strip drive letter colon for Windows paths."""
        from raise_cli.config.paths import get_claude_memory_path

        # On Linux, we can't create a real Windows Path, but we can
        # test the string manipulation by passing a path-like string.
        # The function converts to str first, so this tests the logic.
        result = get_claude_memory_path(Path("/C:/Users/dev/project"))

        encoded_part = result.parent.parent.name
        # Should not contain colon from drive letter
        assert ":" not in encoded_part
        assert "-C" in encoded_part or "-c" in encoded_part.lower()
