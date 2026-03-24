"""Tests for rai docs commands (publish, get, search) with mock targets."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.adapters.models import (
    AdapterHealth,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.cli.main import app

runner = CliRunner()


class _MockDocsTarget:
    """Sync docs target mock for CLI tests. Captures publish calls for assertions."""

    def __init__(self) -> None:
        self.last_publish_call: dict[str, Any] | None = None

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        self.last_publish_call = {
            "doc_type": doc_type,
            "content": content,
            "metadata": metadata,
        }
        return PublishResult(success=True, url=f"https://example.com/wiki/{doc_type}")

    def get_page(self, identifier: str) -> PageContent:
        return PageContent(
            id=identifier,
            title="Project Roadmap",
            content="## Q1 2026\n- Feature A",
            url="https://example.com/wiki/page/123",
            space_key="RAISE",
            version=3,
        )

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        if "empty" in query:
            return []
        return [
            PageSummary(
                id="123",
                title="ADR-033",
                url="https://example.com/1",
                space_key="RAISE",
            ),
            PageSummary(
                id="456",
                title="ADR-034",
                url="https://example.com/2",
                space_key="RAISE",
            ),
        ]

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="mock", healthy=True)


class _FailPublishTarget(_MockDocsTarget):
    """Target that fails on publish."""

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=False, message="Confluence auth failed")


def _patch_target(target_instance: Any):  # noqa: ANN401
    """Patch resolve_docs_target to return a specific target instance."""
    return patch(
        "raise_cli.cli.commands.docs.resolve_docs_target",
        return_value=target_instance,
    )


class TestPublish:
    def test_publish_success(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Publish resolves artifact type to governance/{type}.md and publishes."""
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "roadmap.md").write_text("# Roadmap\nQ1 stuff")
        monkeypatch.chdir(tmp_path)

        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "publish", "roadmap"])

        assert result.exit_code == 0
        assert "Published: roadmap" in result.output
        assert "https://example.com/wiki/roadmap" in result.output

    def test_publish_with_title(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--title flag overrides default page title in metadata."""
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "roadmap.md").write_text("# Roadmap")
        monkeypatch.chdir(tmp_path)

        mock_target = _MockDocsTarget()
        with _patch_target(mock_target):
            result = runner.invoke(
                app, ["docs", "publish", "roadmap", "--title", "Project Roadmap"]
            )

        assert result.exit_code == 0
        assert "Published: roadmap" in result.output
        assert mock_target.last_publish_call is not None
        assert mock_target.last_publish_call["metadata"]["title"] == "Project Roadmap"

    def test_publish_file_not_found(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Publish with nonexistent artifact type → error."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["docs", "publish", "nonexistent"])

        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_publish_failure_from_target(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Target returns failure → error message displayed."""
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "roadmap.md").write_text("# Roadmap")
        monkeypatch.chdir(tmp_path)

        with _patch_target(_FailPublishTarget()):
            result = runner.invoke(app, ["docs", "publish", "roadmap"])

        assert result.exit_code == 1
        assert "Confluence auth failed" in result.output


class TestGet:
    def test_get_page(self) -> None:
        """Get retrieves page and displays content."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "get", "123"])

        assert result.exit_code == 0
        assert "Project Roadmap" in result.output
        assert "Q1 2026" in result.output
        assert "RAISE" in result.output

    def test_get_shows_version(self) -> None:
        """Get shows version number when > 1."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "get", "123"])

        assert "Version: 3" in result.output


class TestSearch:
    def test_search_results(self) -> None:
        """Search lists matching pages."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "search", "architecture"])

        assert result.exit_code == 0
        assert "ADR-033" in result.output
        assert "ADR-034" in result.output
        assert "RAISE" in result.output

    def test_search_empty(self) -> None:
        """Search with no results shows message."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "search", "empty query"])

        assert result.exit_code == 0
        assert "No results." in result.output
