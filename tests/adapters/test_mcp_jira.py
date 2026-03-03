"""Tests for McpJiraAdapter — Jira adapter via MCP bridge.

Mocks at McpBridge.call() level. Does NOT require mcp-atlassian installed.
Uses asyncio.run() for async tests (no pytest-asyncio dependency).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from rai_cli.adapters.mcp_bridge import McpBridgeError, McpToolResult
from rai_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)

# --- Helpers ---


def _run(coro: Any) -> Any:
    """Run async test coroutine synchronously."""
    return asyncio.run(coro)


def _ok(data: dict[str, Any]) -> McpToolResult:
    """Create a successful McpToolResult with JSON data."""
    return McpToolResult(text=json.dumps(data), data=data)


# Sample jira.yaml content for tests
JIRA_YAML = """\
projects:
  RAISE:
    name: RAISE
    category: Development

workflow:
  states:
    - name: Backlog
      id: 11
    - name: Selected for Development
      id: 21
    - name: In Progress
      id: 31
    - name: Done
      id: 41

  lifecycle_mapping:
    story_start: 31
    story_close: 41

  status_mapping:
    backlog: 11
    selected: 21
    in-progress: 31
    done: 41

team:
  - name: Emilio Osorio
    identifier: emilio@humansys.ai
    role: lead-dev
"""

JIRA_YAML_NO_STATUS_MAPPING = """\
projects:
  RAISE:
    name: RAISE

workflow:
  states:
    - name: Backlog
      id: 11
"""


# =============================================================================
# McpJiraAdapter.__init__ + config
# =============================================================================


class TestMcpJiraAdapterInit:
    def test_init_reads_jira_yaml(self, tmp_path: Path) -> None:
        """__init__ reads jira.yaml and validates status_mapping."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "jira.yaml").write_text(JIRA_YAML)

        from rai_cli.adapters.mcp_jira import McpJiraAdapter

        adapter = McpJiraAdapter(project_root=tmp_path)
        assert adapter._status_mapping == {
            "backlog": 11,
            "selected": 21,
            "in-progress": 31,
            "done": 41,
        }

    def test_init_raises_on_missing_status_mapping(self, tmp_path: Path) -> None:
        """__init__ raises ValueError when status_mapping is missing."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "jira.yaml").write_text(JIRA_YAML_NO_STATUS_MAPPING)

        from rai_cli.adapters.mcp_jira import McpJiraAdapter

        with pytest.raises(ValueError, match="status_mapping"):
            McpJiraAdapter(project_root=tmp_path)

    def test_init_raises_on_missing_jira_yaml(self, tmp_path: Path) -> None:
        """__init__ raises FileNotFoundError when jira.yaml doesn't exist."""
        from rai_cli.adapters.mcp_jira import McpJiraAdapter

        with pytest.raises(FileNotFoundError):
            McpJiraAdapter(project_root=tmp_path)


# =============================================================================
# _resolve_transition_id
# =============================================================================


class TestResolveTransitionId:
    def test_resolve_known_status(self, tmp_path: Path) -> None:
        """_resolve_transition_id returns correct ID for known status."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "jira.yaml").write_text(JIRA_YAML)

        from rai_cli.adapters.mcp_jira import McpJiraAdapter

        adapter = McpJiraAdapter(project_root=tmp_path)
        assert adapter._resolve_transition_id("done") == "41"
        assert adapter._resolve_transition_id("in-progress") == "31"

    def test_resolve_unknown_status_raises(self, tmp_path: Path) -> None:
        """_resolve_transition_id raises ValueError with available statuses."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "jira.yaml").write_text(JIRA_YAML)

        from rai_cli.adapters.mcp_jira import McpJiraAdapter

        adapter = McpJiraAdapter(project_root=tmp_path)
        with pytest.raises(ValueError, match="invalid") as exc_info:
            adapter._resolve_transition_id("invalid")
        # Error message should list available statuses
        assert "backlog" in str(exc_info.value)
        assert "done" in str(exc_info.value)


# =============================================================================
# Protocol method tests — mock McpBridge.call()
# =============================================================================


def _make_adapter(tmp_path: Path) -> Any:
    """Create McpJiraAdapter with valid config and mocked bridge."""
    (tmp_path / ".raise").mkdir(exist_ok=True)
    (tmp_path / ".raise" / "jira.yaml").write_text(JIRA_YAML)

    from rai_cli.adapters.mcp_jira import McpJiraAdapter

    adapter = McpJiraAdapter(project_root=tmp_path)
    adapter._bridge = AsyncMock()
    return adapter


class TestTransitionIssue:
    def test_transition_calls_bridge_with_correct_args(self, tmp_path: Path) -> None:
        """transition_issue resolves status and calls jira_transition_issue."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {"key": "RAISE-301", "fields": {"status": {"name": "Done"}}}
        )

        async def run() -> IssueRef:
            return await adapter.transition_issue("RAISE-301", "done")

        result = _run(run())
        adapter._bridge.call.assert_called_once_with(
            "jira_transition_issue",
            {"issue_key": "RAISE-301", "transition_id": "41"},
        )
        assert result.key == "RAISE-301"


class TestCreateIssue:
    def test_create_maps_issue_spec_fields(self, tmp_path: Path) -> None:
        """create_issue maps IssueSpec fields to jira_create_issue args."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "key": "RAISE-400",
                "self": "https://humansys.atlassian.net/rest/api/2/issue/10400",
            }
        )

        spec = IssueSpec(
            summary="New feature",
            description="Description here",
            issue_type="Story",
            labels=["frontend"],
            metadata={"priority": {"name": "High"}},
        )

        async def run() -> IssueRef:
            return await adapter.create_issue("RAISE", spec)

        result = _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_create_issue"
        args = call_args[0][1]
        assert args["project_key"] == "RAISE"
        assert args["summary"] == "New feature"
        assert args["issue_type"] == "Story"
        assert args["description"] == "Description here"
        assert result.key == "RAISE-400"


class TestGetIssue:
    def test_get_issue_parses_into_issue_detail(self, tmp_path: Path) -> None:
        """get_issue parses McpToolResult.data into IssueDetail (sooperset format)."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "key": "RAISE-301",
                "summary": "Test story",
                "description": "Some desc",
                "status": {
                    "name": "In Progress",
                    "category": "In Progress",
                    "color": "blue",
                },
                "issue_type": {"name": "Story"},
                "parent": {"key": "RAISE-275"},
                "labels": ["backend"],
                "assignee": {"display_name": "Emilio", "name": "Emilio", "email": None},
                "priority": {"name": "High"},
                "created": "2026-02-28T10:00:00.000+0000",
                "updated": "2026-02-28T12:00:00.000+0000",
                "url": "https://humansys.atlassian.net/rest/api/2/issue/10301",
            }
        )

        async def run() -> IssueDetail:
            return await adapter.get_issue("RAISE-301")

        result = _run(run())
        assert result.key == "RAISE-301"
        assert result.summary == "Test story"
        assert result.status == "In Progress"
        assert result.issue_type == "Story"
        assert result.parent_key == "RAISE-275"
        assert result.labels == ["backend"]
        assert result.assignee == "Emilio"
        assert result.priority == "High"


class TestUpdateIssue:
    def test_update_calls_bridge_with_fields(self, tmp_path: Path) -> None:
        """update_issue passes fields as JSON string to jira_update_issue."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok({"key": "RAISE-301"})

        async def run() -> IssueRef:
            return await adapter.update_issue(
                "RAISE-301", {"summary": "Updated title", "labels": ["urgent"]}
            )

        result = _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_update_issue"
        args = call_args[0][1]
        assert args["issue_key"] == "RAISE-301"
        assert result.key == "RAISE-301"


class TestSearch:
    def test_search_passes_jql_and_limit(self, tmp_path: Path) -> None:
        """search passes JQL and limit to jira_search."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "issues": [
                    {
                        "key": "RAISE-1",
                        "summary": "First",
                        "status": {"name": "Done", "category": "Done"},
                        "issue_type": {"name": "Story"},
                        "parent": None,
                    },
                    {
                        "key": "RAISE-2",
                        "summary": "Second",
                        "status": {"name": "In Progress", "category": "In Progress"},
                        "issue_type": {"name": "Bug"},
                        "parent": {"key": "RAISE-144"},
                    },
                ]
            }
        )

        async def run() -> list[IssueSummary]:
            return await adapter.search('project = "RAISE"', limit=5)

        result = _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_search"
        args = call_args[0][1]
        assert args["jql"] == 'project = "RAISE"'
        assert args["limit"] == 5
        assert len(result) == 2
        assert result[0].key == "RAISE-1"
        assert result[0].status == "Done"
        assert result[1].parent_key == "RAISE-144"


class TestGetComments:
    def test_get_comments_passes_limit_as_comment_limit(self, tmp_path: Path) -> None:
        """get_comments passes limit as comment_limit to jira_get_issue (AR-S3-5)."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "key": "RAISE-301",
                "comments": [
                    {
                        "id": "10001",
                        "body": "First comment",
                        "author": {"display_name": "Emilio", "name": "Emilio"},
                        "created": "2026-02-28T10:00:00.000+0000",
                    },
                    {
                        "id": "10002",
                        "body": "Second comment",
                        "author": {"display_name": "Aquiles", "name": "Aquiles"},
                        "created": "2026-02-28T11:00:00.000+0000",
                    },
                ],
            }
        )

        async def run() -> list[Comment]:
            return await adapter.get_comments("RAISE-301", limit=5)

        result = _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_get_issue"
        args = call_args[0][1]
        assert args["comment_limit"] == 5
        assert len(result) == 2
        assert result[0].id == "10001"
        assert result[0].author == "Emilio"


class TestLinkToParent:
    def test_link_to_parent_uses_update_issue(self, tmp_path: Path) -> None:
        """link_to_parent uses jira_update_issue with parent field (AR-S3-2)."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok({"key": "RAISE-301"})

        async def run() -> None:
            await adapter.link_to_parent("RAISE-301", "RAISE-275")

        _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_update_issue"
        args = call_args[0][1]
        assert args["issue_key"] == "RAISE-301"
        assert '"parent"' in args["additional_fields"] or "parent" in args.get(
            "additional_fields", ""
        )


class TestLinkIssues:
    def test_link_issues_calls_create_issue_link(self, tmp_path: Path) -> None:
        """link_issues calls jira_create_issue_link."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok({"status": "ok"})

        async def run() -> None:
            await adapter.link_issues("RAISE-301", "RAISE-302", "Blocks")

        _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_create_issue_link"
        args = call_args[0][1]
        assert args["inward_issue_key"] == "RAISE-301"
        assert args["outward_issue_key"] == "RAISE-302"
        assert args["link_type"] == "Blocks"


class TestAddComment:
    def test_add_comment_calls_jira_add_comment(self, tmp_path: Path) -> None:
        """add_comment calls jira_add_comment and returns CommentRef."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "id": "10099",
                "self": "https://humansys.atlassian.net/rest/api/2/issue/10301/comment/10099",
            }
        )

        async def run() -> CommentRef:
            return await adapter.add_comment("RAISE-301", "Test comment")

        result = _run(run())
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "jira_add_comment"
        args = call_args[0][1]
        assert args["issue_key"] == "RAISE-301"
        assert args["body"] == "Test comment"
        assert result.id == "10099"


class TestBatchTransition:
    def test_batch_transition_loops_sequentially(self, tmp_path: Path) -> None:
        """batch_transition loops N calls sequentially."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {"key": "RAISE-1", "fields": {"status": {"name": "Done"}}}
        )

        async def run() -> BatchResult:
            return await adapter.batch_transition(
                ["RAISE-1", "RAISE-2", "RAISE-3"], "done"
            )

        result = _run(run())
        assert adapter._bridge.call.call_count == 3
        assert len(result.succeeded) == 3

    def test_batch_transition_captures_failures(self, tmp_path: Path) -> None:
        """batch_transition captures individual failures without stopping."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.side_effect = [
            _ok({"key": "RAISE-1", "fields": {"status": {"name": "Done"}}}),
            McpBridgeError("Connection lost"),
            _ok({"key": "RAISE-3", "fields": {"status": {"name": "Done"}}}),
        ]

        async def run() -> BatchResult:
            return await adapter.batch_transition(
                ["RAISE-1", "RAISE-2", "RAISE-3"], "done"
            )

        result = _run(run())
        assert len(result.succeeded) == 2
        assert len(result.failed) == 1
        assert result.failed[0].key == "RAISE-2"


class TestHealth:
    def test_health_returns_adapter_health(self, tmp_path: Path) -> None:
        """health returns AdapterHealth from JQL probe."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "total": 42,
                "issues": [],
            }
        )

        async def run() -> AdapterHealth:
            return await adapter.health()

        result = _run(run())
        assert result.name == "jira"
        assert result.healthy is True
        assert result.latency_ms is not None

    def test_health_returns_unhealthy_on_error(self, tmp_path: Path) -> None:
        """health returns unhealthy when bridge call fails."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.side_effect = McpBridgeError("Connection failed")

        async def run() -> AdapterHealth:
            return await adapter.health()

        result = _run(run())
        assert result.name == "jira"
        assert result.healthy is False
        assert "Connection failed" in result.message
