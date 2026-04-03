"""Tests for daemon PID file management."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

from rai_agent.daemon.pid import acquire_pid, is_alive, read_pid, remove, write_pid

if TYPE_CHECKING:
    from pathlib import Path


class TestWritePid:
    """Tests for write_pid()."""

    def test_writes_pid_to_file(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        write_pid(12345, pid_file)
        assert pid_file.read_text().strip() == "12345"

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        assert not pid_file.parent.exists()
        write_pid(12345, pid_file)
        assert pid_file.parent.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        write_pid(11111, pid_file)
        write_pid(22222, pid_file)
        assert pid_file.read_text().strip() == "22222"


class TestReadPid:
    """Tests for read_pid()."""

    def test_returns_pid_when_file_exists_and_alive(
        self,
        tmp_path: Path,
    ) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("12345\n")
        with patch(
            "rai_agent.daemon.pid.is_alive",
            return_value=True,
        ):
            assert read_pid(pid_file) == 12345

    def test_returns_none_when_no_file(self, tmp_path: Path) -> None:
        pid_file = tmp_path / "daemon.pid"
        assert read_pid(pid_file) is None

    def test_returns_none_and_cleans_corrupt_file(
        self,
        tmp_path: Path,
    ) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("not-a-number\n")
        assert read_pid(pid_file) is None
        assert not pid_file.exists()

    def test_returns_none_and_cleans_empty_file(
        self,
        tmp_path: Path,
    ) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("")
        assert read_pid(pid_file) is None
        assert not pid_file.exists()

    def test_returns_none_when_stale(self, tmp_path: Path) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("99999\n")
        with patch(
            "rai_agent.daemon.pid.is_alive",
            return_value=False,
        ):
            assert read_pid(pid_file) is None
        assert not pid_file.exists()

    def test_returns_pid_when_alive(self, tmp_path: Path) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("12345\n")
        with patch(
            "rai_agent.daemon.pid.is_alive",
            return_value=True,
        ):
            assert read_pid(pid_file) == 12345


class TestIsAlive:
    """Tests for is_alive()."""

    def test_returns_true_for_current_process(self) -> None:
        assert is_alive(os.getpid()) is True

    def test_returns_false_for_nonexistent_pid(self) -> None:
        # PID 4194304 is above Linux max (usually 4194304 or 32768)
        assert is_alive(4194304) is False

    @patch("os.kill", side_effect=PermissionError)
    def test_returns_true_when_permission_denied(
        self,
        _mock_kill: object,
    ) -> None:
        # Process exists but we can't signal it
        assert is_alive(1) is True

    @patch("os.kill", side_effect=ProcessLookupError)
    def test_returns_false_when_process_not_found(
        self,
        _mock_kill: object,
    ) -> None:
        assert is_alive(99999) is False


class TestAcquirePid:
    """Tests for acquire_pid()."""

    def test_acquires_when_no_file(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        result = acquire_pid(12345, pid_file)
        assert result is None  # acquired
        assert pid_file.read_text().strip() == "12345"

    def test_returns_existing_pid_when_alive(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        pid_file.parent.mkdir(parents=True)
        pid_file.write_text("99999\n")
        with patch("rai_agent.daemon.pid.is_alive", return_value=True):
            result = acquire_pid(12345, pid_file)
        assert result == 99999

    def test_acquires_after_stale_cleanup(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        pid_file.parent.mkdir(parents=True)
        pid_file.write_text("99999\n")
        with patch("rai_agent.daemon.pid.is_alive", return_value=False):
            result = acquire_pid(12345, pid_file)
        assert result is None
        assert pid_file.read_text().strip() == "12345"


class TestRemove:
    """Tests for remove()."""

    def test_removes_existing_file(self, tmp_path: Path) -> None:
        pid_file = tmp_path / "daemon.pid"
        pid_file.write_text("12345\n")
        remove(pid_file)
        assert not pid_file.exists()

    def test_no_error_when_file_missing(self, tmp_path: Path) -> None:
        pid_file = tmp_path / "daemon.pid"
        remove(pid_file)  # should not raise
