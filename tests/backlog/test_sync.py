"""Tests for raise_cli.backlog.sync — core sync logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from raise_cli.adapters.models import IssueSummary
from raise_cli.backlog.sync import SyncResult, sync_backlog


def _make_adapter(issues: list[IssueSummary]) -> MagicMock:
    """Create a mock adapter that returns the given issues from search()."""
    adapter = MagicMock()
    adapter.search.return_value = issues
    return adapter


class TestSyncBacklog:
    """Core sync_backlog function tests."""

    def test_sync_writes_file_with_correct_content(self, tmp_path: Path) -> None:
        """sync_backlog writes markdown with header, timestamp, and table rows."""
        issues = [
            IssueSummary(
                key="RAISE-347",
                summary="Backlog Automation",
                status="In Progress",
                issue_type="Epic",
            ),
            IssueSummary(
                key="RAISE-348",
                summary="Documentation Refresh",
                status="Backlog",
                issue_type="Epic",
            ),
            IssueSummary(
                key="RAISE-349",
                summary="Adapter Validation",
                status="Selected",
                issue_type="Epic",
            ),
        ]
        adapter = _make_adapter(issues)
        output = tmp_path / "backlog.md"

        result = sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        assert isinstance(result, SyncResult)
        assert result.adapter_name == "jira"
        assert result.epic_count == 3
        assert result.output_path == str(output)
        assert output.exists()

        content = output.read_text()
        assert "rai backlog sync" in content
        assert "jira" in content
        assert "RAISE-347" in content
        assert "Backlog Automation" in content
        assert "RAISE-349" in content
        assert "| Key |" in content

    def test_sync_empty_result_still_writes_file(self, tmp_path: Path) -> None:
        """Empty adapter result writes file with empty table + timestamp."""
        adapter = _make_adapter([])
        output = tmp_path / "backlog.md"

        result = sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        assert result.epic_count == 0
        assert output.exists()
        content = output.read_text()
        assert "rai backlog sync" in content
        assert "| Key |" in content

    def test_sync_passes_project_filter_to_search(self, tmp_path: Path) -> None:
        """Project filter is injected into the search query."""
        adapter = _make_adapter([])
        output = tmp_path / "backlog.md"

        sync_backlog(adapter, "jira", project_filter="RAISE", output_path=output)

        call_args = adapter.search.call_args
        query = call_args[0][0]
        assert "RAISE" in query

    def test_sync_result_has_timestamp(self, tmp_path: Path) -> None:
        """SyncResult includes an ISO 8601 timestamp."""
        adapter = _make_adapter([])
        output = tmp_path / "backlog.md"

        result = sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        # Timestamp should be ISO 8601-ish (contains T or -)
        assert "T" in result.timestamp or "-" in result.timestamp

    def test_sync_creates_parent_directories(self, tmp_path: Path) -> None:
        """Output path parent directories are created if missing."""
        adapter = _make_adapter([])
        output = tmp_path / "governance" / "backlog.md"

        sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        assert output.exists()

    def test_sync_escapes_pipe_in_summary(self, tmp_path: Path) -> None:
        """Pipe chars in summary/status are escaped to preserve table structure."""
        issues = [
            IssueSummary(
                key="PROJ-1",
                summary="Fix | broken pipe",
                status="In | Progress",
                issue_type="Epic",
            ),
        ]
        adapter = _make_adapter(issues)
        output = tmp_path / "backlog.md"

        sync_backlog(adapter, "test", project_filter=None, output_path=output)

        content = output.read_text()
        assert "Fix \\| broken pipe" in content
        assert "In \\| Progress" in content

    def test_atomic_write_temp_suffix_preserves_extension(self, tmp_path: Path) -> None:
        """Temp file uses .md.tmp not .tmp (suffix append, not replace)."""
        adapter = _make_adapter([])
        output = tmp_path / "backlog.md"

        sync_backlog(adapter, "test", project_filter=None, output_path=output)

        # After successful sync, temp file must be gone (renamed to target)
        assert output.exists()
        assert not Path(str(output) + ".tmp").exists()
        # The old buggy path should also not exist
        assert not (tmp_path / "backlog.tmp").exists()


class TestFilesystemDetection:
    """Filesystem adapter detection — T2."""

    def test_filesystem_adapter_raises_valueerror(self, tmp_path: Path) -> None:
        """Passing a FilesystemPMAdapter raises ValueError with clear message."""
        from raise_cli.adapters.filesystem import FilesystemPMAdapter

        adapter = FilesystemPMAdapter(project_root=tmp_path)
        output = tmp_path / "backlog.md"

        with pytest.raises(ValueError, match="source of truth"):
            sync_backlog(adapter, "filesystem", project_filter=None, output_path=output)

    def test_filesystem_adapter_does_not_write_file(self, tmp_path: Path) -> None:
        """File must not be created when filesystem adapter is rejected."""
        from raise_cli.adapters.filesystem import FilesystemPMAdapter

        adapter = FilesystemPMAdapter(project_root=tmp_path)
        output = tmp_path / "backlog.md"

        with pytest.raises(ValueError):
            sync_backlog(adapter, "filesystem", project_filter=None, output_path=output)

        assert not output.exists()


class TestAdapterErrorHandling:
    """Adapter error handling — T4: file untouched on search() failure."""

    def test_error_does_not_create_new_file(self, tmp_path: Path) -> None:
        """When search() raises, output file must not be created."""
        adapter = MagicMock()
        adapter.search.side_effect = ConnectionError("timeout")
        output = tmp_path / "backlog.md"

        with pytest.raises(RuntimeError, match="failed"):
            sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        assert not output.exists()

    def test_error_preserves_existing_file(self, tmp_path: Path) -> None:
        """When search() raises, existing file retains original content."""
        adapter = MagicMock()
        adapter.search.side_effect = ConnectionError("timeout")
        output = tmp_path / "backlog.md"
        original_content = "# Original backlog\nDo not touch."
        output.write_text(original_content)

        with pytest.raises(RuntimeError):
            sync_backlog(adapter, "jira", project_filter=None, output_path=output)

        assert output.read_text() == original_content

    def test_error_wraps_as_runtime_error(self, tmp_path: Path) -> None:
        """Adapter exceptions are wrapped in RuntimeError with adapter name."""
        adapter = MagicMock()
        adapter.search.side_effect = ValueError("bad query")
        output = tmp_path / "backlog.md"

        with pytest.raises(RuntimeError, match="jira"):
            sync_backlog(adapter, "jira", project_filter=None, output_path=output)
