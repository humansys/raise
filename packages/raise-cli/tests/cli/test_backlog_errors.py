"""RAISE-553: backlog commands must show clean error messages, not raw tracebacks.

Tests that each unprotected command catches adapter exceptions and outputs
"[red]Error:[/red] {msg}" with exit code 1.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _mock_adapter(side_effect: Exception) -> MagicMock:
    adapter = MagicMock()
    adapter.create_issue.side_effect = side_effect
    adapter.transition_issue.side_effect = side_effect
    adapter.update_issue.side_effect = side_effect
    adapter.link_issues.side_effect = side_effect
    adapter.add_comment.side_effect = side_effect
    adapter.search.side_effect = side_effect
    adapter.batch_transition.side_effect = side_effect
    return adapter


_ERROR = RuntimeError("MCP bridge connection failed")
_PATCH = "raise_cli.cli.commands.backlog.resolve_adapter"


class TestBacklogErrorHandling:
    """RAISE-553: all backlog commands must catch adapter errors cleanly."""

    @patch(_PATCH)
    def test_create_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(
            app, ["backlog", "create", "Test summary", "-p", "RAISE"]
        )
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_transition_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(app, ["backlog", "transition", "RAISE-1", "done"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_update_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(
            app, ["backlog", "update", "RAISE-1", "--summary", "New title"]
        )
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_link_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(app, ["backlog", "link", "RAISE-1", "RAISE-2", "blocks"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_comment_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(
            app, ["backlog", "comment", "RAISE-1", "Some comment text"]
        )
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_search_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(app, ["backlog", "search", "RAISE-1"])
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output

    @patch(_PATCH)
    def test_batch_transition_shows_clean_error(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = _mock_adapter(_ERROR)
        result = runner.invoke(
            app, ["backlog", "batch-transition", "RAISE-1,RAISE-2", "done"]
        )
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Traceback" not in result.output
