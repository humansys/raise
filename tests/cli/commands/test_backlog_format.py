"""Tests for --format agent in rai backlog commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.adapters.models import IssueRef, IssueSummary
from raise_cli.cli.main import app

runner = CliRunner()


def _mock_adapter() -> MagicMock:
    """Create a mock ProjectManagementAdapter."""
    adapter = MagicMock()
    return adapter


class TestBacklogSearchFormat:
    """Tests for rai backlog search --format."""

    def test_search_agent_format_pipe_delimited(self) -> None:
        """Agent format produces key|status|summary lines."""
        adapter = _mock_adapter()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-1", summary="First issue", status="Done", issue_type="Task"
            ),
            IssueSummary(
                key="RAISE-2",
                summary="Second issue",
                status="In Progress",
                issue_type="Story",
            ),
        ]
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "search", "project=RAISE", "--format", "agent"]
            )
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert lines[0] == "RAISE-1|Done|First issue"
        assert lines[1] == "RAISE-2|In Progress|Second issue"

    def test_search_agent_format_empty(self) -> None:
        """Agent format with no results produces empty output."""
        adapter = _mock_adapter()
        adapter.search.return_value = []
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "search", "project=RAISE", "--format", "agent"]
            )
        assert result.exit_code == 0
        assert result.output.strip() == ""

    def test_search_human_format_unchanged(self) -> None:
        """Human format (default) produces same output as before."""
        adapter = _mock_adapter()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-1", summary="First issue", status="Done", issue_type="Task"
            ),
        ]
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(app, ["backlog", "search", "project=RAISE"])
        assert result.exit_code == 0
        # Original format uses padded status, not pipe-delimited
        assert "|" not in result.output
        assert "RAISE-1" in result.output
        assert "Done" in result.output

    def test_search_agent_no_truncation(self) -> None:
        """Agent format does not truncate long summaries."""
        long_summary = "A" * 200
        adapter = _mock_adapter()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-1", summary=long_summary, status="Done", issue_type="Task"
            ),
        ]
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "search", "project=RAISE", "--format", "agent"]
            )
        assert result.exit_code == 0
        assert long_summary in result.output


class TestBacklogCreateFormat:
    """Tests for rai backlog create --format."""

    def test_create_agent_format_bare_key(self) -> None:
        """Agent format returns only the created key."""
        adapter = _mock_adapter()
        adapter.create_issue.return_value = IssueRef(key="RAISE-99")
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app,
                ["backlog", "create", "Test issue", "-p", "RAISE", "--format", "agent"],
            )
        assert result.exit_code == 0
        assert result.output.strip() == "RAISE-99"

    def test_create_human_format_unchanged(self) -> None:
        """Human format (default) produces 'Created: KEY'."""
        adapter = _mock_adapter()
        adapter.create_issue.return_value = IssueRef(key="RAISE-99")
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "create", "Test issue", "-p", "RAISE"]
            )
        assert result.exit_code == 0
        assert "Created: RAISE-99" in result.output


class TestBacklogFormatValidation:
    """Tests for format option validation (QR-3)."""

    def test_search_invalid_format_rejected(self) -> None:
        """Invalid format value exits with error."""
        adapter = _mock_adapter()
        adapter.search.return_value = []
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "search", "project=RAISE", "--format", "banana"]
            )
        assert result.exit_code == 1
        assert "Invalid format" in result.output

    def test_create_invalid_format_rejected(self) -> None:
        """Invalid format value exits with error."""
        adapter = _mock_adapter()
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "create", "Test", "-p", "RAISE", "--format", "json"]
            )
        assert result.exit_code == 1
        assert "Invalid format" in result.output


class TestBacklogPipeSanitization:
    """Tests for pipe character sanitization in agent format (QR-1)."""

    def test_search_pipe_in_summary_sanitized(self) -> None:
        """Pipe in summary is replaced to preserve field boundaries."""
        adapter = _mock_adapter()
        adapter.search.return_value = [
            IssueSummary(
                key="RAISE-1",
                summary="Fix auth | retry logic",
                status="Done",
                issue_type="Task",
            ),
        ]
        with patch(
            "raise_cli.cli.commands.backlog.resolve_adapter", return_value=adapter
        ):
            result = runner.invoke(
                app, ["backlog", "search", "project=RAISE", "--format", "agent"]
            )
        assert result.exit_code == 0
        line = result.output.strip()
        # Exactly 3 fields when split on pipe
        parts = line.split("|")
        assert len(parts) == 3
        assert parts[0] == "RAISE-1"
        assert parts[1] == "Done"
        assert "auth" in parts[2]
