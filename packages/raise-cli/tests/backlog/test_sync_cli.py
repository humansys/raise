"""Tests for `rai backlog sync` CLI subcommand — T3."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.backlog.sync import SyncResult
from raise_cli.cli.commands.backlog import backlog_app

runner = CliRunner()


def _mock_sync_result(tmp_path: Path) -> SyncResult:
    return SyncResult(
        adapter_name="jira",
        epic_count=3,
        timestamp="2026-03-03T14:30:00+00:00",
        output_path=str(tmp_path / "governance" / "backlog.md"),
    )


class TestSyncCommand:
    """CLI sync subcommand tests."""

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    @patch("raise_cli.cli.commands.backlog.sync_backlog")
    def test_sync_success_output(
        self, mock_sync: MagicMock, mock_resolve: MagicMock, tmp_path: Path
    ) -> None:
        """Successful sync prints epic count and adapter name."""
        mock_resolve.return_value = MagicMock()
        mock_sync.return_value = _mock_sync_result(tmp_path)

        result = runner.invoke(backlog_app, ["sync"])

        assert result.exit_code == 0
        assert "3" in result.output
        assert "jira" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    @patch("raise_cli.cli.commands.backlog.sync_backlog")
    def test_sync_with_project_filter(
        self, mock_sync: MagicMock, mock_resolve: MagicMock, tmp_path: Path
    ) -> None:
        """Project filter is passed through to sync_backlog."""
        mock_resolve.return_value = MagicMock()
        mock_sync.return_value = _mock_sync_result(tmp_path)

        runner.invoke(backlog_app, ["sync", "-p", "RAISE"])

        call_kwargs = mock_sync.call_args
        assert call_kwargs[1].get("project_filter") == "RAISE" or (
            len(call_kwargs[0]) > 2 and call_kwargs[0][2] == "RAISE"
        )

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    @patch("raise_cli.cli.commands.backlog.sync_backlog")
    def test_sync_filesystem_noop(
        self, mock_sync: MagicMock, mock_resolve: MagicMock
    ) -> None:
        """Filesystem adapter produces no-op message, exit code 0."""
        mock_resolve.return_value = MagicMock()
        mock_sync.side_effect = ValueError(
            "Filesystem adapter is source of truth — nothing to sync."
        )

        result = runner.invoke(backlog_app, ["sync"])

        assert result.exit_code == 0
        assert "source of truth" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    @patch("raise_cli.cli.commands.backlog.sync_backlog")
    def test_sync_adapter_error(
        self, mock_sync: MagicMock, mock_resolve: MagicMock
    ) -> None:
        """Adapter failure produces error message, exit code 1."""
        mock_resolve.return_value = MagicMock()
        mock_sync.side_effect = RuntimeError(
            "Adapter 'jira' failed: connection timeout"
        )

        result = runner.invoke(backlog_app, ["sync"])

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()
