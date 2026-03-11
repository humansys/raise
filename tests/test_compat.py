"""Tests for raise_cli.compat — cross-platform compatibility layer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from raise_cli.compat import (
    file_lock,
    file_unlock,
    portable_path,
    secure_permissions,
    to_file_uri,
)


class TestPortablePath:
    """Test portable_path returns forward-slash strings."""

    def test_simple_relative(self, tmp_path: Path) -> None:
        child = tmp_path / "src" / "foo" / "bar.py"
        child.parent.mkdir(parents=True)
        child.touch()
        result = portable_path(child, tmp_path)
        assert result == "src/foo/bar.py"

    def test_single_component(self, tmp_path: Path) -> None:
        child = tmp_path / "file.txt"
        child.touch()
        result = portable_path(child, tmp_path)
        assert result == "file.txt"

    def test_no_backslashes(self, tmp_path: Path) -> None:
        child = tmp_path / "a" / "b" / "c.py"
        child.parent.mkdir(parents=True)
        child.touch()
        result = portable_path(child, tmp_path)
        assert "\\" not in result


class TestToFileUri:
    """Test to_file_uri produces valid file:// URIs."""

    def test_produces_file_scheme(self, tmp_path: Path) -> None:
        f = tmp_path / "test.html"
        f.touch()
        uri = to_file_uri(f)
        assert uri.startswith("file:///")

    def test_no_backslashes_in_uri(self, tmp_path: Path) -> None:
        f = tmp_path / "sub" / "test.html"
        f.parent.mkdir()
        f.touch()
        uri = to_file_uri(f)
        assert "\\" not in uri


class TestSecurePermissions:
    """Test secure_permissions sets restrictive mode on Unix."""

    def test_sets_600_on_unix(self, tmp_path: Path) -> None:
        f = tmp_path / "secret.dat"
        f.write_bytes(b"secret")
        f.chmod(0o644)
        with patch("raise_cli.compat.IS_WINDOWS", False):
            secure_permissions(f)
        assert f.stat().st_mode & 0o777 == 0o600

    def test_noop_on_windows(self, tmp_path: Path) -> None:
        f = tmp_path / "secret.dat"
        f.write_bytes(b"secret")
        original_mode = f.stat().st_mode
        with patch("raise_cli.compat.IS_WINDOWS", True):
            secure_permissions(f)
        # Should not raise, mode unchanged conceptually
        assert f.stat().st_mode == original_mode


class TestFileLock:
    """Test file_lock/file_unlock work without crashing."""

    def test_lock_unlock_cycle(self, tmp_path: Path) -> None:
        f = tmp_path / "lockable.txt"
        f.touch()
        with open(f, "a") as fh:
            file_lock(fh)
            fh.write("data\n")
            file_unlock(fh)
        assert f.read_text(encoding="utf-8") == "data\n"

    def test_lock_is_reentrant_after_unlock(self, tmp_path: Path) -> None:
        f = tmp_path / "lockable.txt"
        f.touch()
        with open(f, "a") as fh:
            file_lock(fh)
            file_unlock(fh)
            file_lock(fh)
            file_unlock(fh)
