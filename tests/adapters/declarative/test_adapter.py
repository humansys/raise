"""Tests for DeclarativeMcpAdapter (PM + Docs protocols).

Mocks at McpBridge.call() level. Uses asyncio.run() (no pytest-asyncio).
AC refs: s337.2-story.md scenarios 1-7, s337.4-story.md scenarios 1-5.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest
import yaml

from raise_cli.adapters.declarative.adapter import DeclarativeMcpAdapter
from raise_cli.adapters.declarative.schema import DeclarativeAdapterConfig
from raise_cli.adapters.mcp_bridge import McpToolResult
from raise_cli.adapters.models import (
    AdapterHealth,
    IssueRef,
    IssueSpec,
    PageContent,
    PageSummary,
    PublishResult,
)

VALID_YAML = """\
adapter:
  name: test-pm
  protocol: pm
  description: "Test PM adapter"

server:
  command: echo
  args: [test]

methods:
  create_issue:
    tool: test_create_issue
    args:
      title: "{{ issue.summary }}"
      body: "{{ issue.description }}"
      repo: "{{ project_key }}"
    response:
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url | default('') }}"

  get_issue:
    tool: test_get_issue
    args:
      issue_number: "{{ key }}"
    response:
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url | default('') }}"
        summary: "{{ data.title }}"
        description: "{{ data.body | default('') }}"
        status: "{{ data.state }}"
        issue_type: "{{ data.type | default('Task') }}"

  update_issue:
    tool: test_update_issue
    args:
      issue_number: "{{ key }}"
    response:
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url | default('') }}"

  transition_issue:
    tool: test_transition
    args:
      issue_number: "{{ key }}"
      state: "{{ status }}"
    response:
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url | default('') }}"

  search:
    tool: test_search_issues
    args:
      query: "{{ query }}"
      per_page: "{{ limit }}"
    response:
      items_path: data.items
      fields:
        key: "{{ item.number | str }}"
        summary: "{{ item.title }}"
        status: "{{ item.state }}"
        issue_type: "{{ item.type | default('Task') }}"

  add_comment:
    tool: test_add_comment
    args:
      issue_number: "{{ key }}"
      body: "{{ body }}"
    response:
      fields:
        id: "{{ data.id | str }}"
        url: "{{ data.html_url | default('') }}"

  get_comments:
    tool: test_get_comments
    args:
      issue_number: "{{ key }}"
      per_page: "{{ limit }}"
    response:
      items_path: data
      fields:
        id: "{{ item.id | str }}"
        body: "{{ item.body }}"
        author: "{{ item.user }}"
        created: "{{ item.created_at }}"

  link_to_parent: null
  link_issues: null
"""


def _run(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    return asyncio.run(coro)


def _make_adapter(mock_bridge: AsyncMock) -> DeclarativeMcpAdapter:
    """Create adapter from YAML config with injected mock bridge."""
    data = yaml.safe_load(VALID_YAML)
    config = DeclarativeAdapterConfig(**data)
    adapter = DeclarativeMcpAdapter(config)
    adapter._bridge = mock_bridge  # type: ignore[assignment]
    return adapter


def _mock_bridge(**tool_responses: dict[str, Any]) -> AsyncMock:
    """Create a mock McpBridge that returns configured responses per tool name."""
    bridge = AsyncMock()

    async def mock_call(tool_name: str, arguments: dict[str, Any]) -> McpToolResult:
        data = tool_responses.get(tool_name, {})
        return McpToolResult(text="", data=data)

    bridge.call = AsyncMock(side_effect=mock_call)
    bridge.health = AsyncMock(
        return_value=AdapterHealth(name="test", healthy=True, message="OK")
    )
    bridge.aclose = AsyncMock()
    return bridge


# --- AC Scenario 1: create_issue dispatch ---


class TestCreateIssue:
    def test_dispatches_to_configured_tool(self) -> None:
        bridge = _mock_bridge(
            test_create_issue={"number": 42, "html_url": "https://github.com/issues/42"}
        )
        adapter = _make_adapter(bridge)

        result = _run(
            adapter.create_issue(
                "PROJ", IssueSpec(summary="Bug", description="Details")
            )
        )

        bridge.call.assert_called_once_with(
            "test_create_issue",
            {"title": "Bug", "body": "Details", "repo": "PROJ"},
        )
        assert isinstance(result, IssueRef)
        assert result.key == "42"
        assert result.url == "https://github.com/issues/42"

    def test_missing_optional_fields_use_defaults(self) -> None:
        bridge = _mock_bridge(test_create_issue={"number": 1})
        adapter = _make_adapter(bridge)

        result = _run(adapter.create_issue("PROJ", IssueSpec(summary="Test")))
        assert result.key == "1"
        assert result.url == ""


# --- get_issue, update_issue, transition_issue ---


class TestGetIssue:
    def test_returns_issue_detail(self) -> None:
        bridge = _mock_bridge(
            test_get_issue={
                "number": 42,
                "html_url": "https://...",
                "title": "Bug",
                "body": "Details",
                "state": "open",
                "type": "Bug",
            }
        )
        adapter = _make_adapter(bridge)

        result = _run(adapter.get_issue("42"))
        assert result.key == "42"
        assert result.summary == "Bug"
        assert result.status == "open"
        assert result.issue_type == "Bug"


class TestUpdateIssue:
    def test_returns_issue_ref(self) -> None:
        bridge = _mock_bridge(
            test_update_issue={"number": 42, "html_url": "https://..."}
        )
        adapter = _make_adapter(bridge)

        result = _run(adapter.update_issue("42", {"title": "Updated"}))
        assert isinstance(result, IssueRef)
        assert result.key == "42"


class TestTransitionIssue:
    def test_passes_status_as_arg(self) -> None:
        bridge = _mock_bridge(test_transition={"number": 42})
        adapter = _make_adapter(bridge)

        result = _run(adapter.transition_issue("42", "closed"))
        bridge.call.assert_called_once_with(
            "test_transition",
            {"issue_number": "42", "state": "closed"},
        )
        assert result.key == "42"


# --- AC Scenario 3: null method ---


class TestNullMethod:
    def test_null_method_raises(self) -> None:
        bridge = _mock_bridge()
        adapter = _make_adapter(bridge)

        with pytest.raises(NotImplementedError, match="link_to_parent"):
            _run(adapter.link_to_parent("A-1", "A-2"))

    def test_another_null_method_raises(self) -> None:
        bridge = _mock_bridge()
        adapter = _make_adapter(bridge)

        with pytest.raises(NotImplementedError, match="link_issues"):
            _run(adapter.link_issues("A-1", "A-2", "Blocks"))


# --- AC Scenario 4: undeclared method ---


class TestUndeclaredMethod:
    def test_undeclared_method_raises(self) -> None:
        data = yaml.safe_load(VALID_YAML)
        data["methods"] = {}
        config = DeclarativeAdapterConfig(**data)
        adapter = DeclarativeMcpAdapter(config)

        with pytest.raises(NotImplementedError, match="create_issue"):
            _run(adapter.create_issue("PROJ", IssueSpec(summary="Test")))


# --- AC Scenario 2: search with list response ---


class TestSearch:
    def test_returns_list_of_summaries(self) -> None:
        bridge = _mock_bridge(
            test_search_issues={
                "data": {
                    "items": [
                        {"number": 1, "title": "Bug", "state": "open", "type": "Bug"},
                        {
                            "number": 2,
                            "title": "Feature",
                            "state": "closed",
                            "type": "Story",
                        },
                    ]
                }
            }
        )
        adapter = _make_adapter(bridge)

        result = _run(adapter.search("is:issue", limit=10))
        assert len(result) == 2
        assert result[0].key == "1"
        assert result[0].summary == "Bug"
        assert result[0].status == "open"
        assert result[1].key == "2"

    def test_empty_search_results(self) -> None:
        bridge = _mock_bridge(test_search_issues={"data": {"items": []}})
        adapter = _make_adapter(bridge)

        result = _run(adapter.search("nothing", limit=10))
        assert result == []


# --- AC Scenario 5: batch_transition auto-loop ---


class TestBatchTransition:
    def test_auto_loops_over_transition(self) -> None:
        bridge = _mock_bridge(test_transition={"number": 0})
        adapter = _make_adapter(bridge)

        result = _run(adapter.batch_transition(["A-1", "A-2"], "closed"))
        assert len(result.succeeded) == 2
        assert result.failed == []
        assert bridge.call.call_count == 2

    def test_captures_failures(self) -> None:
        bridge = AsyncMock()
        call_count = 0

        async def fail_second(tool: str, args: dict[str, Any]) -> McpToolResult:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("Connection lost")
            return McpToolResult(text="", data={"number": 1})

        bridge.call = AsyncMock(side_effect=fail_second)
        adapter = _make_adapter(bridge)

        result = _run(adapter.batch_transition(["A-1", "A-2"], "closed"))
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.failed[0].key == "A-2"


# --- AC Scenario 6: health ---


class TestHealth:
    def test_delegates_to_bridge(self) -> None:
        bridge = _mock_bridge()
        adapter = _make_adapter(bridge)

        result = _run(adapter.health())
        assert isinstance(result, AdapterHealth)
        assert result.name == "test-pm"


# --- AC Scenario 7: aclose ---


class TestAclose:
    def test_delegates_to_bridge(self) -> None:
        bridge = _mock_bridge()
        adapter = _make_adapter(bridge)

        _run(adapter.aclose())
        bridge.aclose.assert_called_once()


# --- Comments ---


class TestComments:
    def test_add_comment(self) -> None:
        bridge = _mock_bridge(test_add_comment={"id": 99, "html_url": "https://..."})
        adapter = _make_adapter(bridge)

        result = _run(adapter.add_comment("42", "Great work!"))
        assert result.id == "99"

    def test_get_comments(self) -> None:
        bridge = _mock_bridge(
            test_get_comments={
                "data": [
                    {
                        "id": 1,
                        "body": "Hello",
                        "user": "alice",
                        "created_at": "2026-01-01",
                    },
                    {
                        "id": 2,
                        "body": "World",
                        "user": "bob",
                        "created_at": "2026-01-02",
                    },
                ]
            }
        )
        adapter = _make_adapter(bridge)

        result = _run(adapter.get_comments("42", limit=10))
        assert len(result) == 2
        assert result[0].body == "Hello"
        assert result[0].author == "alice"


# --- Docs protocol tests (S337.4) ---

DOCS_YAML = """\
adapter:
  name: test-wiki
  protocol: docs
  description: "Test docs adapter"

server:
  command: echo
  args: [test]

methods:
  can_publish:
    tool: wiki_can_publish
    args:
      doc_type: "{{ doc_type }}"
    response:
      fields:
        result: "{{ data.allowed }}"

  publish:
    tool: wiki_publish
    args:
      doc_type: "{{ doc_type }}"
      content: "{{ content }}"
      title: "{{ metadata.title | default('Untitled') }}"
    response:
      fields:
        success: "{{ data.ok }}"
        url: "{{ data.url | default('') }}"
        message: "{{ data.message | default('') }}"

  get_page:
    tool: wiki_get_page
    args:
      page_id: "{{ identifier }}"
    response:
      fields:
        id: "{{ data.id | str }}"
        title: "{{ data.title }}"
        content: "{{ data.body }}"
        url: "{{ data.url | default('') }}"

  search:
    tool: wiki_search
    args:
      query: "{{ query }}"
      limit: "{{ limit }}"
    response:
      items_path: data.results
      fields:
        id: "{{ item.id | str }}"
        title: "{{ item.title }}"
        url: "{{ item.url | default('') }}"

  get_page_children: null
"""


def _make_docs_adapter(mock_bridge: AsyncMock) -> DeclarativeMcpAdapter:
    """Create docs adapter from YAML config with injected mock bridge."""
    data = yaml.safe_load(DOCS_YAML)
    config = DeclarativeAdapterConfig(**data)
    adapter = DeclarativeMcpAdapter(config)
    adapter._bridge = mock_bridge  # type: ignore[assignment]
    return adapter


class TestCanPublish:
    def test_returns_true(self) -> None:
        bridge = _mock_bridge(wiki_can_publish={"allowed": True})
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.can_publish("page", {"title": "Test"}))
        assert result is True
        bridge.call.assert_called_once_with(
            "wiki_can_publish",
            {"doc_type": "page"},
        )

    def test_returns_false(self) -> None:
        bridge = _mock_bridge(wiki_can_publish={"allowed": False})
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.can_publish("restricted", {}))
        assert result is False


class TestPublish:
    def test_returns_publish_result(self) -> None:
        bridge = _mock_bridge(
            wiki_publish={
                "ok": True,
                "url": "https://wiki.example.com/page/1",
                "message": "Created",
            }
        )
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.publish("page", "# Hello", {"title": "My Page"}))
        assert isinstance(result, PublishResult)
        assert result.success is True
        assert result.url == "https://wiki.example.com/page/1"
        bridge.call.assert_called_once_with(
            "wiki_publish",
            {"doc_type": "page", "content": "# Hello", "title": "My Page"},
        )

    def test_default_fields(self) -> None:
        bridge = _mock_bridge(wiki_publish={"ok": False})
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.publish("page", "content", {}))
        assert result.success is False
        assert result.url == ""


class TestGetPage:
    def test_returns_page_content(self) -> None:
        bridge = _mock_bridge(
            wiki_get_page={
                "id": 42,
                "title": "Design Doc",
                "body": "# Design",
                "url": "https://wiki.example.com/42",
            }
        )
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.get_page("42"))
        assert isinstance(result, PageContent)
        assert result.id == "42"
        assert result.title == "Design Doc"
        assert result.content == "# Design"
        assert result.url == "https://wiki.example.com/42"


class TestDocsSearch:
    def test_returns_page_summaries(self) -> None:
        bridge = _mock_bridge(
            wiki_search={
                "data": {
                    "results": [
                        {"id": 1, "title": "Page A", "url": "https://wiki/1"},
                        {"id": 2, "title": "Page B", "url": "https://wiki/2"},
                    ]
                }
            }
        )
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.search("design", limit=10))
        assert len(result) == 2
        assert isinstance(result[0], PageSummary)
        assert result[0].id == "1"
        assert result[0].title == "Page A"

    def test_empty_results(self) -> None:
        bridge = _mock_bridge(wiki_search={"data": {"results": []}})
        adapter = _make_docs_adapter(bridge)

        result = _run(adapter.search("nothing", limit=5))
        assert result == []


class TestDocsUnmappedMethod:
    def test_unmapped_docs_method_raises(self) -> None:
        data = yaml.safe_load(DOCS_YAML)
        data["methods"] = {}
        config = DeclarativeAdapterConfig(**data)
        adapter = DeclarativeMcpAdapter(config)

        with pytest.raises(NotImplementedError, match="get_page"):
            _run(adapter.get_page("42"))


# --- Protocol compliance (S337.4 T2) ---


class TestProtocolCompliance:
    def test_satisfies_async_pm_protocol(self) -> None:
        from raise_cli.adapters.protocols import AsyncProjectManagementAdapter

        bridge = _mock_bridge()
        adapter = _make_adapter(bridge)
        assert isinstance(adapter, AsyncProjectManagementAdapter)

    def test_satisfies_async_docs_protocol(self) -> None:
        from raise_cli.adapters.protocols import AsyncDocumentationTarget

        bridge = _mock_bridge()
        adapter = _make_docs_adapter(bridge)
        assert isinstance(adapter, AsyncDocumentationTarget)


class TestIsErrorPropagation:
    """RAISE-472: DeclarativeMcpAdapter must raise McpBridgeError when result.is_error=True."""

    def test_get_issue_raises_on_is_error(self) -> None:
        from raise_cli.mcp.bridge import McpBridgeError

        bridge = _mock_bridge()
        bridge.call = AsyncMock(
            return_value=McpToolResult(
                is_error=True, error_message="Jira client not available"
            )
        )
        adapter = _make_adapter(bridge)

        with pytest.raises(McpBridgeError, match="Jira client not available"):
            asyncio.run(adapter.get_issue("RAISE-144"))

    def test_search_raises_on_is_error(self) -> None:
        from raise_cli.mcp.bridge import McpBridgeError

        bridge = _mock_bridge()
        bridge.call = AsyncMock(
            return_value=McpToolResult(is_error=True, error_message="Invalid JQL")
        )
        adapter = _make_adapter(bridge)

        with pytest.raises(McpBridgeError, match="Invalid JQL"):
            asyncio.run(adapter.search('project = "RAISE"'))
