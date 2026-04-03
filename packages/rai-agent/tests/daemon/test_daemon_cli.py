"""Tests for daemon CLI subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rai_agent.daemon.cli import app

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


class TestDaemonStart:
    """Tests for `rai daemon start`."""

    def test_starts_daemon_and_acquires_pid(
        self,
        tmp_path: Path,
    ) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        log_file = tmp_path / ".rai" / "daemon.log"
        mock_process = MagicMock()
        mock_process.pid = 12345

        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.cli._log_path", return_value=log_file),
            patch(
                "subprocess.Popen",
                return_value=mock_process,
            ) as mock_popen,
            patch(
                "rai_agent.daemon.pid.acquire_pid",
                return_value=None,
            ) as mock_acquire,
            patch("dotenv.load_dotenv"),
        ):
            result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert "12345" in result.output
        mock_acquire.assert_called_once_with(12345, pid_file)
        mock_popen.assert_called_once()

    def test_warns_when_already_running(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        log_file = tmp_path / ".rai" / "daemon.log"
        mock_process = MagicMock()
        mock_process.pid = 99
        mock_process.terminate = MagicMock()

        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.cli._log_path", return_value=log_file),
            patch("subprocess.Popen", return_value=mock_process),
            patch(
                "rai_agent.daemon.pid.acquire_pid",
                return_value=12345,
            ),
            patch("dotenv.load_dotenv"),
        ):
            result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert "already running" in result.output.lower()
        mock_process.terminate.assert_called_once()

    def test_unsets_claudecode_env(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        log_file = tmp_path / ".rai" / "daemon.log"
        mock_process = MagicMock()
        mock_process.pid = 99

        captured_env: dict[str, str] = {}

        def _capture_popen(
            *args: object,
            **kwargs: object,
        ) -> MagicMock:
            env = kwargs.get("env", {})
            assert isinstance(env, dict)
            captured_env.update(env)
            return mock_process

        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.cli._log_path", return_value=log_file),
            patch("subprocess.Popen", side_effect=_capture_popen),
            patch("rai_agent.daemon.pid.acquire_pid", return_value=None),
            patch("dotenv.load_dotenv"),
            patch.dict("os.environ", {"CLAUDECODE": "1"}, clear=False),
        ):
            result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert "CLAUDECODE" not in captured_env

    def test_propagates_config_host_port(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        log_file = tmp_path / ".rai" / "daemon.log"
        mock_process = MagicMock()
        mock_process.pid = 99

        captured_args: list[str] = []

        def _capture_popen(
            args: list[str],
            **_kwargs: object,
        ) -> MagicMock:
            captured_args.extend(args)
            return mock_process

        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.cli._log_path", return_value=log_file),
            patch("subprocess.Popen", side_effect=_capture_popen),
            patch("rai_agent.daemon.pid.acquire_pid", return_value=None),
            patch("dotenv.load_dotenv"),
        ):
            result = runner.invoke(
                app,
                ["start", "--host", "0.0.0.0", "--port", "9000"],
            )

        assert result.exit_code == 0
        assert "--host" in captured_args
        assert "0.0.0.0" in captured_args
        assert "--port" in captured_args
        assert "9000" in captured_args


class TestDaemonStop:
    """Tests for `rai daemon stop`."""

    def test_stops_running_daemon(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.pid.read_pid", return_value=12345),
            patch("os.kill") as mock_kill,
            patch(
                "rai_agent.daemon.cli._wait_for_exit",
                return_value=True,
            ),
            patch("rai_agent.daemon.pid.remove") as mock_remove,
        ):
            result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "stopped" in result.output.lower()
        mock_kill.assert_called_once()
        mock_remove.assert_called_once_with(pid_file)

    def test_handles_process_died_between_read_and_kill(
        self,
        tmp_path: Path,
    ) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.pid.read_pid", return_value=12345),
            patch(
                "os.kill",
                side_effect=ProcessLookupError,
            ),
            patch("rai_agent.daemon.pid.remove") as mock_remove,
        ):
            result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "already exited" in result.output.lower()
        mock_remove.assert_called_once_with(pid_file)

    def test_warns_when_not_running(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.pid.read_pid", return_value=None),
        ):
            result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        assert "no daemon running" in result.output.lower()


class TestDaemonRestart:
    """Tests for `rai daemon restart`."""

    def test_restart_stops_then_starts(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        log_file = tmp_path / ".rai" / "daemon.log"
        mock_process = MagicMock()
        mock_process.pid = 99

        call_order: list[str] = []

        def _track_kill(*_args: object) -> None:
            call_order.append("kill")

        def _track_popen(
            *_args: object,
            **_kwargs: object,
        ) -> MagicMock:
            call_order.append("popen")
            return mock_process

        # stop() reads PID 12345 (running), start() acquires new PID
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.cli._log_path", return_value=log_file),
            patch(
                "rai_agent.daemon.pid.read_pid",
                return_value=12345,
            ),
            patch("os.kill", side_effect=_track_kill),
            patch(
                "rai_agent.daemon.cli._wait_for_exit",
                return_value=True,
            ),
            patch("rai_agent.daemon.pid.remove"),
            patch("subprocess.Popen", side_effect=_track_popen),
            patch("rai_agent.daemon.pid.acquire_pid", return_value=None),
            patch("dotenv.load_dotenv"),
        ):
            result = runner.invoke(app, ["restart"])

        assert result.exit_code == 0
        assert call_order == ["kill", "popen"]


class TestDaemonStatus:
    """Tests for `rai daemon status`."""

    def test_shows_running(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.pid.read_pid", return_value=12345),
        ):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "running" in result.output.lower()
        assert "12345" in result.output

    def test_shows_not_running(self, tmp_path: Path) -> None:
        pid_file = tmp_path / ".rai" / "daemon.pid"
        with (
            patch("rai_agent.daemon.cli._pid_path", return_value=pid_file),
            patch("rai_agent.daemon.pid.read_pid", return_value=None),
        ):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "not running" in result.output.lower()


class TestDaemonRun:
    """Tests for `rai daemon run`."""

    def test_calls_main_directly(self) -> None:
        with patch("rai_agent.daemon.cli._run_foreground") as mock_run:
            result = runner.invoke(app, ["run"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
