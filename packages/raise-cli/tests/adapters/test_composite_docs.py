"""Tests for CompositeDocTarget.

S1051.7 (RAISE-1051)
"""

from __future__ import annotations

from unittest.mock import MagicMock

from raise_cli.adapters.composite_docs import CompositeDocTarget
from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.adapters.protocols import DocumentationTarget


def _mock_target(name: str = "mock", can_publish: bool = True) -> MagicMock:
    """Create a mock DocumentationTarget."""
    target = MagicMock()
    target.can_publish.return_value = can_publish
    target.publish.return_value = PublishResult(success=True, url=f"https://{name}", message=name)
    target.health.return_value = AdapterHealth(name=name, healthy=True)
    target.search.return_value = [PageSummary(id="1", title="R", url="", space_key="")]
    target.get_page.return_value = PageContent(
        id="1", title="P", content="c", url="", space_key="", version=1
    )
    return target


class TestCompositeDocTarget:
    """CompositeDocTarget delegates to multiple targets."""

    def test_satisfies_documentation_target(self) -> None:
        composite = CompositeDocTarget([_mock_target()])
        assert isinstance(composite, DocumentationTarget)

    def test_publish_delegates_to_all_targets(self) -> None:
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        composite = CompositeDocTarget([t1, t2])

        composite.publish("adr", "content", {"title": "ADR"})

        t1.publish.assert_called_once_with("adr", "content", {"title": "ADR"})
        t2.publish.assert_called_once_with("adr", "content", {"title": "ADR"})

    def test_publish_returns_last_successful_result(self) -> None:
        """Last success = remote URL (preferred over local path)."""
        t1 = _mock_target("fs")  # first = filesystem
        t2 = _mock_target("confluence")  # last = remote
        composite = CompositeDocTarget([t1, t2])

        result = composite.publish("adr", "content", {"title": "ADR"})

        assert result.url == "https://confluence"

    def test_publish_skips_targets_that_cant_publish(self) -> None:
        t1 = _mock_target("fs", can_publish=True)
        t2 = _mock_target("confluence", can_publish=False)
        composite = CompositeDocTarget([t1, t2])

        composite.publish("adr", "content", {"title": "ADR"})

        t1.publish.assert_called_once()
        t2.publish.assert_not_called()

    def test_publish_returns_failure_when_no_target_accepts(self) -> None:
        t1 = _mock_target("fs", can_publish=False)
        composite = CompositeDocTarget([t1])

        result = composite.publish("unknown", "content", {"title": "X"})

        assert result.success is False

    def test_can_publish_true_if_any_target_accepts(self) -> None:
        t1 = _mock_target("fs", can_publish=False)
        t2 = _mock_target("confluence", can_publish=True)
        composite = CompositeDocTarget([t1, t2])

        assert composite.can_publish("adr", {}) is True

    def test_can_publish_false_if_no_target_accepts(self) -> None:
        t1 = _mock_target("fs", can_publish=False)
        composite = CompositeDocTarget([t1])

        assert composite.can_publish("adr", {}) is False

    def test_get_page_delegates_to_remote(self) -> None:
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        composite = CompositeDocTarget([t1, t2])

        composite.get_page("123")

        t2.get_page.assert_called_once_with("123")
        t1.get_page.assert_not_called()

    def test_search_delegates_to_remote(self) -> None:
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        composite = CompositeDocTarget([t1, t2])

        composite.search("query", limit=5)

        t2.search.assert_called_once_with("query", limit=5)
        t1.search.assert_not_called()

    def test_health_delegates_to_remote(self) -> None:
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        composite = CompositeDocTarget([t1, t2])

        h = composite.health()

        assert h.name == "confluence"
        t2.health.assert_called_once()

    # ── Reliability scenarios ────────────────────────────────────────────

    def test_fs_ok_confluence_fails_returns_success_with_warning(self) -> None:
        """Filesystem succeeds, Confluence fails → success + sync pending."""
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        t2.publish.return_value = PublishResult(
            success=False, message="Confluence unreachable"
        )
        composite = CompositeDocTarget([t1, t2])

        result = composite.publish("adr", "content", {"title": "ADR"})

        assert result.success is True
        assert "sync pending" in result.message

    def test_fs_ok_confluence_exception_returns_success_with_warning(self) -> None:
        """Filesystem succeeds, Confluence throws → success + sync pending."""
        t1 = _mock_target("fs")
        t2 = _mock_target("confluence")
        t2.publish.side_effect = ConnectionError("Network down")
        composite = CompositeDocTarget([t1, t2])

        result = composite.publish("adr", "content", {"title": "ADR"})

        assert result.success is True
        assert "sync pending" in result.message

    def test_both_fail_returns_failure(self) -> None:
        t1 = _mock_target("fs")
        t1.publish.return_value = PublishResult(success=False, message="disk full")
        t2 = _mock_target("confluence")
        t2.publish.return_value = PublishResult(success=False, message="unreachable")
        composite = CompositeDocTarget([t1, t2])

        result = composite.publish("adr", "content", {"title": "ADR"})

        assert result.success is False
