"""Tests for rai learn CLI commands."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml
from typer.testing import CliRunner

from raise_cli.cli.error_handler import set_error_console
from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_error_console() -> Any:
    """Reset error console singleton so cli_error writes to CliRunner's stream."""
    set_error_console(None)
    yield
    set_error_console(None)


def _all_output(result: Any) -> str:
    """Get all output from CliRunner result (stdout + stderr if available)."""
    parts = [result.output or ""]
    if hasattr(result, "stderr") and result.stderr:
        parts.append(result.stderr)
    return "\n".join(parts).lower()


class TestLearnWrite:
    """Tests for rai learn write command."""

    def _valid_record_data(self) -> dict[str, object]:
        return {
            "skill": "rai-story-implement",
            "work_id": "S1136.2",
            "version": "1.0.0",
            "timestamp": "2026-04-01T10:00:00Z",
            "primed_patterns": ["PAT-E-589"],
            "tier1_queries": 3,
            "tier1_results": 5,
            "jit_queries": 1,
            "pattern_votes": {
                "PAT-E-589": {"vote": 1, "why": "Used seam pattern for config"},
            },
            "gaps": ["No pattern for CLI testing"],
            "artifacts": ["packages/raise-cli/src/raise_cli/cli/commands/learn.py"],
        }

    def test_happy_path_writes_record(self, tmp_path: Path) -> None:
        """Valid YAML file validates and writes to correct path."""
        yaml_file = tmp_path / "record.yaml"
        yaml_file.write_text(
            yaml.safe_dump(self._valid_record_data(), default_flow_style=False),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 0, f"Unexpected output: {result.output}"
        expected_path = (
            tmp_path
            / ".raise"
            / "rai"
            / "learnings"
            / "rai-story-implement"
            / "S1136.2"
            / "record.yaml"
        )
        assert expected_path.exists()
        assert "rai-story-implement" in result.output
        assert "S1136.2" in result.output

    def test_validation_error_exits_7(self, tmp_path: Path) -> None:
        """Invalid YAML (missing required field) exits with code 7."""
        bad_data = {"skill": "test"}  # missing work_id, version, timestamp
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text(
            yaml.safe_dump(bad_data, default_flow_style=False),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 7
        combined = _all_output(result)
        assert "validation" in combined or "error" in combined

    def test_missing_file_exits_1(self, tmp_path: Path) -> None:
        """Non-existent YAML file exits with code 1."""
        result = runner.invoke(
            app,
            ["learn", "write", str(tmp_path / "nope.yaml"), "--project", str(tmp_path)],
        )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "not found" in combined or "exist" in combined

    def test_malformed_yaml_exits_1(self, tmp_path: Path) -> None:
        """Malformed YAML (not valid YAML syntax) gives clear error."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("{{invalid yaml: [", encoding="utf-8")

        result = runner.invoke(
            app,
            ["learn", "write", str(yaml_file), "--project", str(tmp_path)],
        )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "yaml" in combined or "parse" in combined


def _write_record_to_disk(base: Path, skill: str, work_id: str) -> Path:
    """Helper: write a valid learning record to the conventional path."""
    record_dir = base / ".raise" / "rai" / "learnings" / skill / work_id
    record_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "skill": skill,
        "work_id": work_id,
        "version": "2.4.0",
        "timestamp": "2026-04-03T10:00:00",
        "primed_patterns": [],
        "tier1_queries": 0,
        "tier1_results": 0,
        "jit_queries": 0,
        "pattern_votes": {},
        "gaps": [],
        "artifacts": [],
    }
    record_path = record_dir / "record.yaml"
    record_path.write_text(
        yaml.safe_dump(data, default_flow_style=False),
        encoding="utf-8",
    )
    return record_path


class TestLearnPush:
    """Tests for rai learn push command."""

    def test_missing_env_vars_exits_1(self, tmp_path: Path) -> None:
        """Missing RAI_SERVER_URL exits with clear error."""
        record_path = _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")

        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(
                app,
                ["learn", "push", str(record_path), "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "rai_server_url" in combined or "not configured" in combined

    def test_push_single_record_happy_path(self, tmp_path: Path) -> None:
        """Single record push succeeds and creates .pushed marker."""
        record_path = _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")
        server_id = uuid.uuid4()

        mock_client = MagicMock()
        mock_client.push.return_value = server_id

        env = {"RAI_SERVER_URL": "http://localhost:8000", "RAI_API_KEY": "rsk_test"}
        with (
            patch.dict("os.environ", env),
            patch("raise_cli.cli.commands.learn.LearningPushClient", return_value=mock_client),
        ):
            result = runner.invoke(
                app,
                ["learn", "push", str(record_path), "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0, f"Output: {result.output}"
        assert str(server_id) in result.output or "pushed" in result.output.lower()
        # Marker should exist
        assert (record_path.parent / ".pushed").exists()

    def test_push_skips_already_pushed(self, tmp_path: Path) -> None:
        """Already-pushed record is skipped, no HTTP call made."""
        record_path = _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")
        # Write marker
        (record_path.parent / ".pushed").write_text("fake-id\n2026-04-03\n")

        mock_client = MagicMock()
        env = {"RAI_SERVER_URL": "http://localhost:8000", "RAI_API_KEY": "rsk_test"}
        with (
            patch.dict("os.environ", env),
            patch("raise_cli.cli.commands.learn.LearningPushClient", return_value=mock_client),
        ):
            result = runner.invoke(
                app,
                ["learn", "push", str(record_path), "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        combined = _all_output(result)
        assert "skip" in combined or "already" in combined
        assert mock_client.push.call_count == 0

    def test_push_all_pushes_unpushed_only(self, tmp_path: Path) -> None:
        """--all mode pushes unpushed and skips pushed."""
        # Create two records, one already pushed
        _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")
        path2 = _write_record_to_disk(tmp_path, "rai-story-plan", "S100.1")
        (path2.parent / ".pushed").write_text("existing-id\n2026-04-03\n")

        server_id = uuid.uuid4()
        mock_client = MagicMock()
        mock_client.push.return_value = server_id

        env = {"RAI_SERVER_URL": "http://localhost:8000", "RAI_API_KEY": "rsk_test"}
        with (
            patch.dict("os.environ", env),
            patch("raise_cli.cli.commands.learn.LearningPushClient", return_value=mock_client),
        ):
            result = runner.invoke(
                app,
                ["learn", "push", "--all", "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Should have pushed exactly 1 record
        assert mock_client.push.call_count == 1

    def test_push_connection_error_exits_1(self, tmp_path: Path) -> None:
        """Connection error produces clear message and no .pushed marker."""
        import httpx

        record_path = _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")

        mock_client = MagicMock()
        mock_client.server_url = "http://localhost:8000"
        mock_client.push.side_effect = httpx.ConnectError("Connection refused")

        env = {"RAI_SERVER_URL": "http://localhost:8000", "RAI_API_KEY": "rsk_test"}
        with (
            patch.dict("os.environ", env),
            patch("raise_cli.cli.commands.learn.LearningPushClient", return_value=mock_client),
        ):
            result = runner.invoke(
                app,
                ["learn", "push", str(record_path), "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        assert result.exit_code == 1
        combined = _all_output(result)
        assert "reach" in combined or "connect" in combined or "server" in combined
        # Marker must NOT be created on failure
        assert not (record_path.parent / ".pushed").exists()

    def test_push_all_continues_on_partial_failure(self, tmp_path: Path) -> None:
        """--all mode continues pushing after one record fails."""
        import httpx

        _write_record_to_disk(tmp_path, "rai-story-design", "S100.1")
        _write_record_to_disk(tmp_path, "rai-story-plan", "S100.1")

        call_count = 0

        def side_effect(*_args: object, **_kwargs: object) -> uuid.UUID:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ConnectError("Connection refused")
            return uuid.uuid4()

        mock_client = MagicMock()
        mock_client.server_url = "http://localhost:8000"
        mock_client.push.side_effect = side_effect

        env = {"RAI_SERVER_URL": "http://localhost:8000", "RAI_API_KEY": "rsk_test"}
        with (
            patch.dict("os.environ", env),
            patch("raise_cli.cli.commands.learn.LearningPushClient", return_value=mock_client),
        ):
            result = runner.invoke(
                app,
                ["learn", "push", "--all", "--project", str(tmp_path)],
                catch_exceptions=False,
            )

        # Should have attempted BOTH records (not aborted on first)
        assert mock_client.push.call_count == 2
        # Exit 1 because there was a failure
        assert result.exit_code == 1
        combined = _all_output(result)
        assert "1 pushed" in combined
        assert "1 failed" in combined
