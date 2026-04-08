"""Tests for rai backlog get and get-comments commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.adapters.models import Comment, IssueDetail
from raise_cli.cli.main import app

runner = CliRunner()


def _make_detail(**overrides: object) -> IssueDetail:
    """Create an IssueDetail with sensible defaults."""
    defaults: dict[str, object] = {
        "key": "RAISE-100",
        "url": "https://jira.example.com/browse/RAISE-100",
        "summary": "Test issue summary",
        "description": "Detailed description here.",
        "status": "In Progress",
        "issue_type": "Task",
        "parent_key": None,
        "labels": [],
        "assignee": "dev@example.com",
        "priority": "Medium",
        "created": "2026-03-01T10:00:00Z",
        "updated": "2026-03-01T12:00:00Z",
    }
    defaults.update(overrides)
    return IssueDetail(**defaults)  # type: ignore[arg-type]


def _make_comment(**overrides: object) -> Comment:
    """Create a Comment with sensible defaults."""
    defaults: dict[str, object] = {
        "id": "10001",
        "body": "This is a comment.",
        "author": "dev@example.com",
        "created": "2026-03-01T11:00:00Z",
    }
    defaults.update(overrides)
    return Comment(**defaults)  # type: ignore[arg-type]


class TestBacklogGet:
    """Tests for `rai backlog get KEY`."""

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_displays_key_status_type(self, mock_resolve: MagicMock) -> None:
        """Get shows key, status, and issue type on first line."""
        adapter = MagicMock()
        adapter.get_issue.return_value = _make_detail()
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-100"])

        assert result.exit_code == 0
        assert "RAISE-100" in result.output
        assert "In Progress" in result.output
        assert "Task" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_displays_summary(self, mock_resolve: MagicMock) -> None:
        """Get shows issue summary."""
        adapter = MagicMock()
        adapter.get_issue.return_value = _make_detail()
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-100"])

        assert "Test issue summary" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_displays_assignee(self, mock_resolve: MagicMock) -> None:
        """Get shows assignee when present."""
        adapter = MagicMock()
        adapter.get_issue.return_value = _make_detail(assignee="alice@example.com")
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-100"])

        assert "alice@example.com" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_omits_empty_fields(self, mock_resolve: MagicMock) -> None:
        """Get omits assignee/labels/parent/priority when empty."""
        adapter = MagicMock()
        adapter.get_issue.return_value = _make_detail(
            assignee=None,
            labels=[],
            parent_key=None,
            priority=None,
        )
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-100"])

        assert "Assignee" not in result.output
        assert "Labels" not in result.output
        assert "Parent" not in result.output
        assert "Priority" not in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_displays_description(self, mock_resolve: MagicMock) -> None:
        """Get shows description text."""
        adapter = MagicMock()
        adapter.get_issue.return_value = _make_detail(description="A detailed desc.")
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-100"])

        assert "A detailed desc." in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_error_exits_nonzero(self, mock_resolve: MagicMock) -> None:
        """Get with non-existent key shows error and exits non-zero."""
        adapter = MagicMock()
        adapter.get_issue.side_effect = Exception("Issue not found")
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get", "RAISE-99999"])

        assert result.exit_code != 0
        assert "Error" in result.output


class TestBacklogGetComments:
    """Tests for `rai backlog get-comments KEY`."""

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_comments_displays_author_and_body(
        self, mock_resolve: MagicMock
    ) -> None:
        """get-comments shows author and comment body."""
        adapter = MagicMock()
        adapter.get_comments.return_value = [
            _make_comment(author="alice@example.com", body="First comment"),
        ]
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get-comments", "RAISE-100"])

        assert result.exit_code == 0
        assert "alice@example.com" in result.output
        assert "First comment" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_comments_shows_timestamp(self, mock_resolve: MagicMock) -> None:
        """get-comments includes timestamp."""
        adapter = MagicMock()
        adapter.get_comments.return_value = [
            _make_comment(created="2026-03-01T11:00:00Z"),
        ]
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get-comments", "RAISE-100"])

        assert "2026-03-01" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_comments_no_comments(self, mock_resolve: MagicMock) -> None:
        """get-comments with no comments shows message."""
        adapter = MagicMock()
        adapter.get_comments.return_value = []
        mock_resolve.return_value = adapter

        result = runner.invoke(app, ["backlog", "get-comments", "RAISE-100"])

        assert result.exit_code == 0
        assert "No comments" in result.output

    @patch("raise_cli.cli.commands.backlog.resolve_adapter")
    def test_get_comments_limit_flag(self, mock_resolve: MagicMock) -> None:
        """get-comments passes --limit to adapter."""
        adapter = MagicMock()
        adapter.get_comments.return_value = []
        mock_resolve.return_value = adapter

        runner.invoke(app, ["backlog", "get-comments", "RAISE-100", "--limit", "5"])

        adapter.get_comments.assert_called_once_with("RAISE-100", limit=5)
