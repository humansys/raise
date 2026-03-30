"""Tests for FilesystemDocsTarget.

S1051.7 (RAISE-1051)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.adapters.filesystem_docs import FilesystemDocsTarget
from raise_cli.adapters.protocols import DocumentationTarget


# ── T1: FilesystemDocsTarget ─────────────────────────────────────────────


class TestFilesystemDocsTarget:
    """FilesystemDocsTarget writes markdown to local paths."""

    def test_satisfies_documentation_target(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        assert isinstance(target, DocumentationTarget)

    def test_publish_writes_file(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        result = target.publish(
            "story-design",
            "# Design\n\nContent here.",
            {"title": "S1051.7 Design", "path": "work/epics/e1051/stories/s1051.7-design.md"},
        )
        assert result.success is True
        written = (tmp_path / "work/epics/e1051/stories/s1051.7-design.md").read_text()
        assert "# Design" in written

    def test_publish_creates_parent_dirs(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        target.publish("x", "content", {"title": "T", "path": "deep/nested/dir/file.md"})
        assert (tmp_path / "deep/nested/dir/file.md").exists()

    def test_can_publish_true_with_path(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        assert target.can_publish("any", {"path": "some/path.md"}) is True

    def test_can_publish_false_without_path(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        assert target.can_publish("any", {}) is False

    def test_health_returns_healthy(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        h = target.health()
        assert h.healthy is True
        assert h.name == "filesystem-docs"

    def test_search_returns_empty(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        assert target.search("anything") == []

    def test_get_page_raises(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        with pytest.raises(NotImplementedError):
            target.get_page("123")
