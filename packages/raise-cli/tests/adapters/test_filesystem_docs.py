"""Tests for FilesystemDocsTarget.

S1051.7 (RAISE-1051), S1040.4 (RAISE-1040)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.adapters.filesystem_docs import (
    FilesystemDocsTarget,
    FrontmatterValidationError,
)
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
            {
                "title": "S1051.7 Design",
                "path": "work/epics/e1051/stories/s1051.7-design.md",
            },
        )
        assert result.success is True
        written = (tmp_path / "work/epics/e1051/stories/s1051.7-design.md").read_text()
        assert "# Design" in written

    def test_publish_creates_parent_dirs(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        target.publish(
            "x", "content", {"title": "T", "path": "deep/nested/dir/file.md"}
        )
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


# ── S1040.4: Frontmatter Validation ─────────────────────────────────────


class TestFrontmatterValidation:
    """Frontmatter validation in FilesystemDocsTarget.publish()."""

    def _meta(self, path: str = "doc.md") -> dict[str, str]:
        return {"path": path}

    def test_publish_valid_frontmatter_passes(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: My Doc\nstatus: draft\n---\n# Body\n"
        result = target.publish("generic", content, self._meta())
        assert result.success is True
        assert (tmp_path / "doc.md").read_text() == content

    def test_publish_no_frontmatter_passes(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "# Just a heading\n\nNo frontmatter here."
        result = target.publish("generic", content, self._meta())
        assert result.success is True
        assert (tmp_path / "doc.md").read_text() == content

    def test_publish_unparseable_yaml_raises(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\n: bad: yaml: [unclosed\n---\n"
        with pytest.raises(FrontmatterValidationError, match="Unparseable YAML"):
            target.publish("generic", content, self._meta())
        assert not (tmp_path / "doc.md").exists()

    def test_publish_missing_required_fields_raises(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: Only Title\n---\n"
        with pytest.raises(
            FrontmatterValidationError, match="Missing required"
        ) as exc_info:
            target.publish("generic", content, self._meta())
        assert "status" in exc_info.value.missing_fields

    def test_publish_epic_level_requires_epic_id(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: Epic Doc\nstatus: active\n---\n"
        with pytest.raises(FrontmatterValidationError) as exc_info:
            target.publish("epic-design", content, self._meta())
        assert "epic_id" in exc_info.value.missing_fields

    def test_publish_epic_with_epic_id_passes(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: Epic Doc\nstatus: active\nepic_id: E1040\n---\n"
        result = target.publish("epic-design", content, self._meta())
        assert result.success is True

    def test_publish_story_level_requires_story_id_and_epic_id(
        self, tmp_path: Path
    ) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: Story Doc\nstatus: draft\n---\n"
        with pytest.raises(FrontmatterValidationError) as exc_info:
            target.publish("story-design", content, self._meta())
        assert "story_id" in exc_info.value.missing_fields
        assert "epic_id" in exc_info.value.missing_fields

    def test_publish_story_with_story_id_infers_level(self, tmp_path: Path) -> None:
        """story_id in frontmatter triggers story-level validation."""
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\ntitle: Doc\nstatus: draft\nstory_id: S1040.4\n---\n"
        with pytest.raises(FrontmatterValidationError) as exc_info:
            target.publish("generic", content, self._meta())
        assert "epic_id" in exc_info.value.missing_fields

    def test_publish_non_mapping_frontmatter_raises(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\n- item1\n- item2\n---\n"
        with pytest.raises(FrontmatterValidationError, match="mapping"):
            target.publish("generic", content, self._meta())

    def test_publish_empty_frontmatter_passes(self, tmp_path: Path) -> None:
        target = FilesystemDocsTarget(project_root=tmp_path)
        content = "---\n---\n# Body\n"
        result = target.publish("generic", content, self._meta())
        assert result.success is True
