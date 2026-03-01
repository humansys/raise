"""Tests for rai docs commands (publish, get, search) with mock targets."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rai_cli.adapters.models import (
    AdapterHealth,
    PageContent,
    PageSummary,
    PublishResult,
)
from rai_cli.cli.main import app

runner = CliRunner()


class _MockDocsTarget:
    """Sync docs target mock for CLI tests."""

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(
            success=True, url=f"https://example.com/wiki/{doc_type}"
        )

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
                id="123", title="ADR-033", url="https://example.com/1", space_key="RAISE"
            ),
            PageSummary(
                id="456", title="ADR-034", url="https://example.com/2", space_key="RAISE"
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
        "rai_cli.cli.commands.docs.resolve_docs_target",
        return_value=target_instance,
    )


class TestPublish:
    def test_publish_success(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """publish resolves artifact type to governance/{type}.md and publishes."""
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "roadmap.md").write_text("# Roadmap\nQ1 stuff")
        monkeypatch.chdir(tmp_path)

        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "publish", "roadmap"])

        assert result.exit_code == 0
        assert "Published: roadmap" in result.output
        assert "https://example.com/wiki/roadmap" in result.output

    def test_publish_with_title(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """--title flag overrides default page title."""
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "roadmap.md").write_text("# Roadmap")
        monkeypatch.chdir(tmp_path)

        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(
                app, ["docs", "publish", "roadmap", "--title", "Project Roadmap"]
            )

        assert result.exit_code == 0
        assert "Published: roadmap" in result.output

    def test_publish_file_not_found(self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """publish with nonexistent artifact type → error."""
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
        """get retrieves page and displays content."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "get", "123"])

        assert result.exit_code == 0
        assert "Project Roadmap" in result.output
        assert "Q1 2026" in result.output
        assert "RAISE" in result.output

    def test_get_shows_version(self) -> None:
        """get shows version number when > 1."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "get", "123"])

        assert "Version: 3" in result.output


class TestSearch:
    def test_search_results(self) -> None:
        """search lists matching pages."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "search", "architecture"])

        assert result.exit_code == 0
        assert "ADR-033" in result.output
        assert "ADR-034" in result.output
        assert "RAISE" in result.output

    def test_search_empty(self) -> None:
        """search with no results shows message."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "search", "empty query"])

        assert result.exit_code == 0
        assert "No results." in result.output

    def test_search_with_limit(self) -> None:
        """--limit flag is passed to target."""
        with _patch_target(_MockDocsTarget()):
            result = runner.invoke(app, ["docs", "search", "arch", "--limit", "5"])

        assert result.exit_code == 0
