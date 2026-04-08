"""Tests for PythonApiJiraAdapter (S1052.3 / RAISE-1052)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.adapters.jira_config import JiraConfig, JiraInstance, JiraProject

# ── Shared fixtures ─────────────────────────────────────────────────


def _make_config() -> JiraConfig:
    """Create a minimal JiraConfig for testing."""
    return JiraConfig(
        default_instance="humansys",
        instances={
            "humansys": JiraInstance(
                site="humansys.atlassian.net",
                email="emilio@humansys.com",
                projects=["RAISE", "HSA"],
            ),
        },
        projects={
            "RAISE": JiraProject(instance="humansys"),
            "HSA": JiraProject(instance="humansys"),
        },
    )


def _make_adapter(
    config: JiraConfig | None = None,
) -> Any:
    """Create a PythonApiJiraAdapter with mocked config loading."""
    from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

    cfg = config or _make_config()
    with patch("raise_cli.adapters.jira_adapter.load_jira_config", return_value=cfg):
        adapter = PythonApiJiraAdapter(project_root=Path("/fake"))
    return adapter


def _make_adapter_with_client() -> tuple[Any, MagicMock]:
    """Create adapter + inject a mock JiraClient for all instances."""
    adapter = _make_adapter()
    mock_client = MagicMock()
    # Pre-populate client cache so _client_for returns mock
    adapter._clients["humansys.atlassian.net"] = mock_client
    return adapter, mock_client


# ── T1: Constructor + _client_for + health + entry point ────────────


class TestConstructor:
    """Adapter loads config and initializes empty client cache."""

    def test_loads_config_from_project_root(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        cfg = _make_config()
        with patch(
            "raise_cli.adapters.jira_adapter.load_jira_config", return_value=cfg
        ) as mock_load:
            adapter = PythonApiJiraAdapter(project_root=Path("/my/project"))

        mock_load.assert_called_once_with(Path("/my/project"))
        assert adapter._config is cfg

    def test_defaults_to_cwd_when_no_root(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        cfg = _make_config()
        with (
            patch(
                "raise_cli.adapters.jira_adapter.load_jira_config", return_value=cfg
            ) as mock_load,
            patch("raise_cli.adapters.jira_adapter.Path") as mock_path,
        ):
            mock_path.cwd.return_value = Path("/cwd")
            PythonApiJiraAdapter(project_root=None)

        mock_load.assert_called_once_with(Path("/cwd"))

    def test_client_cache_starts_empty(self) -> None:
        adapter = _make_adapter()
        assert adapter._clients == {}


class TestClientFor:
    """_client_for resolves project → instance → cached client."""

    def test_creates_client_on_first_call(self) -> None:
        adapter = _make_adapter()
        mock_client = MagicMock()
        with patch(
            "raise_cli.adapters.jira_adapter.JiraClient.from_config",
            return_value=mock_client,
        ):
            client = adapter._client_for("RAISE")

        assert client is mock_client
        assert "humansys.atlassian.net" in adapter._clients

    def test_returns_cached_client_on_second_call(self) -> None:
        adapter = _make_adapter()
        mock_client = MagicMock()
        with patch(
            "raise_cli.adapters.jira_adapter.JiraClient.from_config",
            return_value=mock_client,
        ) as mock_factory:
            first = adapter._client_for("RAISE")
            second = adapter._client_for("HSA")  # same instance

        assert first is second
        mock_factory.assert_called_once()  # only one creation

    def test_unknown_project_uses_default_instance(self) -> None:
        adapter = _make_adapter()
        mock_client = MagicMock()
        with patch(
            "raise_cli.adapters.jira_adapter.JiraClient.from_config",
            return_value=mock_client,
        ):
            client = adapter._client_for("UNKNOWN")

        assert client is mock_client


class TestHealth:
    """health() delegates to JiraClient.server_info()."""

    @pytest.mark.asyncio
    async def test_healthy_response(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.server_info.return_value = {
            "baseUrl": "https://humansys.atlassian.net",
            "version": "1001.0.0",
        }

        result = await adapter.health()

        assert result.name == "jira"
        assert result.healthy is True
        assert result.latency_ms is not None

    @pytest.mark.asyncio
    async def test_unhealthy_on_exception(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.server_info.side_effect = Exception("connection refused")

        result = await adapter.health()

        assert result.name == "jira"
        assert result.healthy is False
        assert "connection refused" in result.message


# ── T2: CRUD methods + response parsing ─────────────────────────────


class TestBuildUrl:
    """build_url constructs browse URL from config."""

    def test_known_project(self) -> None:
        adapter = _make_adapter()
        url = adapter._build_url("RAISE-123")
        assert url == "https://humansys.atlassian.net/browse/RAISE-123"

    def test_unknown_project_uses_default(self) -> None:
        adapter = _make_adapter()
        url = adapter._build_url("UNKNOWN-1")
        assert url == "https://humansys.atlassian.net/browse/UNKNOWN-1"

    def test_no_hyphen_uses_default(self) -> None:
        adapter = _make_adapter()
        url = adapter._build_url("NOHYPHEN")
        assert url == "https://humansys.atlassian.net/browse/NOHYPHEN"


class TestExtractIssueFields:
    """_extract_issue_fields parses nested Jira format."""

    def test_full_issue(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        data = {
            "key": "RAISE-1",
            "fields": {
                "summary": "Test issue",
                "status": {"name": "In Progress"},
                "issuetype": {"name": "Story"},
                "parent": {"key": "RAISE-0"},
            },
        }
        result = PythonApiJiraAdapter._extract_issue_fields(data)
        assert result["key"] == "RAISE-1"
        assert result["summary"] == "Test issue"
        assert result["status"] == "In Progress"
        assert result["issue_type"] == "Story"
        assert result["parent_key"] == "RAISE-0"

    def test_missing_fields_default_to_empty(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        data = {"key": "RAISE-1", "fields": {}}
        result = PythonApiJiraAdapter._extract_issue_fields(data)
        assert result["summary"] == ""
        assert result["status"] == ""
        assert result["issue_type"] == ""
        assert result["parent_key"] is None

    def test_none_fields(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        data = {"key": "RAISE-1", "fields": None}
        result = PythonApiJiraAdapter._extract_issue_fields(data)
        assert result["summary"] == ""


class TestAdfToText:
    """_adf_to_text converts ADF dicts to plain text."""

    def test_plain_string_passthrough(self) -> None:
        from raise_cli.adapters.jira_adapter import _adf_to_text

        assert _adf_to_text("hello") == "hello"

    def test_none_returns_empty(self) -> None:
        from raise_cli.adapters.jira_adapter import _adf_to_text

        assert _adf_to_text(None) == ""

    def test_empty_string_returns_empty(self) -> None:
        from raise_cli.adapters.jira_adapter import _adf_to_text

        assert _adf_to_text("") == ""

    def test_adf_paragraph(self) -> None:
        from raise_cli.adapters.jira_adapter import _adf_to_text

        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}],
                }
            ],
        }
        assert _adf_to_text(adf) == "Hello world"

    def test_adf_bullet_list(self) -> None:
        from raise_cli.adapters.jira_adapter import _adf_to_text

        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Item 1"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = _adf_to_text(adf)
        assert "- Item 1" in result


class TestGetIssue:
    """get_issue delegates to client and parses response."""

    @pytest.mark.asyncio
    async def test_returns_issue_detail(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_issue.return_value = {
            "key": "RAISE-1",
            "fields": {
                "summary": "Test issue",
                "description": "Some description",
                "status": {"name": "To Do"},
                "issuetype": {"name": "Story"},
                "parent": {"key": "RAISE-0"},
                "labels": ["rai-auto"],
                "assignee": {"displayName": "Emilio"},
                "priority": {"name": "Medium"},
                "created": "2026-03-01T10:00:00Z",
                "updated": "2026-03-02T10:00:00Z",
            },
        }

        result = await adapter.get_issue("RAISE-1")

        from raise_cli.adapters.models.pm import IssueDetail

        assert isinstance(result, IssueDetail)
        assert result.key == "RAISE-1"
        assert result.summary == "Test issue"
        assert result.status == "To Do"
        assert result.issue_type == "Story"
        assert result.parent_key == "RAISE-0"
        assert result.labels == ["rai-auto"]
        assert result.assignee == "Emilio"
        assert result.priority == "Medium"
        assert result.url == "https://humansys.atlassian.net/browse/RAISE-1"

    @pytest.mark.asyncio
    async def test_handles_none_assignee_and_priority(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_issue.return_value = {
            "key": "RAISE-2",
            "fields": {
                "summary": "Minimal",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "assignee": None,
                "priority": None,
                "labels": [],
                "created": "",
                "updated": "",
            },
        }

        result = await adapter.get_issue("RAISE-2")

        assert result.assignee is None
        assert result.priority is None


class TestCreateIssue:
    """create_issue builds fields and delegates to client."""

    @pytest.mark.asyncio
    async def test_creates_issue_with_all_fields(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.create_issue.return_value = {
            "key": "RAISE-100",
            "id": "10100",
        }

        from raise_cli.adapters.models.pm import IssueSpec

        spec = IssueSpec(
            summary="New feature",
            description="Details here",
            issue_type="Story",
            labels=["rai-auto", "e1052"],
        )
        result = await adapter.create_issue("RAISE", spec)

        assert result.key == "RAISE-100"
        assert result.url == "https://humansys.atlassian.net/browse/RAISE-100"
        call_fields = mock_client.create_issue.call_args[0][0]
        assert call_fields["project"]["key"] == "RAISE"
        assert call_fields["summary"] == "New feature"
        assert call_fields["issuetype"]["name"] == "Story"
        assert call_fields["labels"] == ["rai-auto", "e1052"]

    @pytest.mark.asyncio
    async def test_creates_issue_minimal(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.create_issue.return_value = {"key": "RAISE-101", "id": "10101"}

        from raise_cli.adapters.models.pm import IssueSpec

        spec = IssueSpec(summary="Minimal issue")
        result = await adapter.create_issue("RAISE", spec)

        assert result.key == "RAISE-101"
        call_fields = mock_client.create_issue.call_args[0][0]
        assert "description" not in call_fields  # empty description omitted

    @pytest.mark.asyncio
    async def test_creates_issue_with_parent(self) -> None:
        """RAISE-1574: --parent metadata must reach Jira fields dict."""
        adapter, mock_client = _make_adapter_with_client()
        mock_client.create_issue.return_value = {"key": "RAISE-102", "id": "10102"}

        from raise_cli.adapters.models.pm import IssueSpec

        spec = IssueSpec(
            summary="Child issue",
            issue_type="Task",
            metadata={"parent": "RAISE-764"},
        )
        result = await adapter.create_issue("RAISE", spec)

        assert result.key == "RAISE-102"
        call_fields = mock_client.create_issue.call_args[0][0]
        assert call_fields["parent"] == {"key": "RAISE-764"}


class TestUpdateIssue:
    """update_issue delegates field update to client."""

    @pytest.mark.asyncio
    async def test_updates_and_returns_ref(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.update_issue.return_value = {"key": "RAISE-1"}

        result = await adapter.update_issue("RAISE-1", {"summary": "Updated"})

        assert result.key == "RAISE-1"
        assert result.url == "https://humansys.atlassian.net/browse/RAISE-1"
        mock_client.update_issue.assert_called_once_with(
            "RAISE-1", {"summary": "Updated"}
        )

    @pytest.mark.asyncio
    async def test_assignee_normalized_to_account_id(self) -> None:
        """RAISE-1152: assignee email → {"accountId": "..."} before reaching Jira."""
        adapter, mock_client = _make_adapter_with_client()
        mock_client.search_users.return_value = [
            {"accountId": "abc123", "emailAddress": "fer@test.com"}
        ]
        mock_client.update_issue.return_value = {}

        await adapter.update_issue(
            "RAISE-1", {"summary": "Updated", "assignee": "fer@test.com"}
        )

        mock_client.update_issue.assert_called_once_with(
            "RAISE-1", {"summary": "Updated", "assignee": {"accountId": "abc123"}}
        )


# ── T3: transition_issue + batch_transition + search ────────────────


class TestNormalizeStatus:
    """normalize_status converts CLI slugs to Jira display names."""

    def test_hyphenated(self) -> None:
        from raise_cli.adapters.jira_adapter import normalize_status

        assert normalize_status("in-progress") == "In Progress"

    def test_simple(self) -> None:
        from raise_cli.adapters.jira_adapter import normalize_status

        assert normalize_status("done") == "Done"


class TestToJql:
    """to_jql normalizes user queries to valid JQL."""

    def test_issue_key(self) -> None:
        from raise_cli.adapters.jira_adapter import to_jql

        assert to_jql("RAISE-123") == "issue = RAISE-123"

    def test_plain_text(self) -> None:
        from raise_cli.adapters.jira_adapter import to_jql

        assert to_jql("fix login bug") == 'text ~ "fix login bug"'

    def test_jql_passthrough(self) -> None:
        from raise_cli.adapters.jira_adapter import to_jql

        assert to_jql("project = RAISE AND status = Done") == 'project = "RAISE" AND status = Done'

    def test_escaped_bang_becomes_jql_operator(self) -> None:
        r"""After unescaping \! -> !, the ! is a JQL operator, so passthrough."""
        from raise_cli.adapters.jira_adapter import to_jql

        # \! unescapes to !, which matches JQL operator regex, so passthrough
        assert to_jql("\\!important") == "!important"

    def test_plain_text_no_operators(self) -> None:
        from raise_cli.adapters.jira_adapter import to_jql

        assert to_jql("important feature") == 'text ~ "important feature"'


class TestTransitionIssue:
    """transition_issue looks up transition ID then executes."""

    @pytest.mark.asyncio
    async def test_finds_and_executes_transition(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_transitions.return_value = [
            {"id": "11", "name": "To Do"},
            {"id": "21", "name": "In Progress"},
            {"id": "31", "name": "Done"},
        ]

        result = await adapter.transition_issue("RAISE-1", "in-progress")

        mock_client.transition_issue.assert_called_once_with("RAISE-1", "21")
        assert result.key == "RAISE-1"

    @pytest.mark.asyncio
    async def test_case_insensitive_match(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_transitions.return_value = [
            {"id": "21", "name": "IN PROGRESS"},
        ]

        await adapter.transition_issue("RAISE-1", "in-progress")

        mock_client.transition_issue.assert_called_once_with("RAISE-1", "21")

    @pytest.mark.asyncio
    async def test_no_matching_transition_raises(self) -> None:
        from raise_cli.adapters.jira_exceptions import JiraApiError

        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_transitions.return_value = [
            {"id": "11", "name": "To Do"},
        ]

        with pytest.raises(JiraApiError, match="No transition"):
            await adapter.transition_issue("RAISE-1", "in-progress")


class TestBatchTransition:
    """batch_transition iterates keys with error isolation."""

    @pytest.mark.asyncio
    async def test_all_succeed(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_transitions.return_value = [
            {"id": "31", "name": "Done"},
        ]

        result = await adapter.batch_transition(["RAISE-1", "RAISE-2"], "done")

        assert len(result.succeeded) == 2
        assert len(result.failed) == 0

    @pytest.mark.asyncio
    async def test_partial_failure(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_transitions.return_value = [
            {"id": "31", "name": "Done"},
        ]
        mock_client.transition_issue.side_effect = [None, Exception("boom")]

        result = await adapter.batch_transition(["RAISE-1", "RAISE-2"], "done")

        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.failed[0].key == "RAISE-2"


class TestSearch:
    """search normalizes query and returns IssueSummary list."""

    @pytest.mark.asyncio
    async def test_returns_summaries(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.jql.return_value = [
            {
                "key": "RAISE-1",
                "fields": {
                    "summary": "First",
                    "status": {"name": "To Do"},
                    "issuetype": {"name": "Story"},
                },
            },
            {
                "key": "RAISE-2",
                "fields": {
                    "summary": "Second",
                    "status": {"name": "Done"},
                    "issuetype": {"name": "Bug"},
                },
            },
        ]

        result = await adapter.search("project = RAISE", limit=10)

        assert len(result) == 2
        assert result[0].key == "RAISE-1"
        assert result[1].status == "Done"

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.jql.return_value = []

        result = await adapter.search("RAISE-99999")

        assert result == []

    @pytest.mark.asyncio
    async def test_jql_normalization_applied(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.jql.return_value = []

        await adapter.search("RAISE-123")

        mock_client.jql.assert_called_once_with("issue = RAISE-123", limit=50)


# ── T4: Relationships + comments ────────────────────────────────────


class TestLinkToParent:
    """link_to_parent delegates to client.set_parent."""

    @pytest.mark.asyncio
    async def test_delegates(self) -> None:
        adapter, mock_client = _make_adapter_with_client()

        await adapter.link_to_parent("RAISE-2", "RAISE-1")

        mock_client.set_parent.assert_called_once_with("RAISE-2", "RAISE-1")


class TestLinkIssues:
    """link_issues delegates to client.create_link."""

    @pytest.mark.asyncio
    async def test_delegates(self) -> None:
        adapter, mock_client = _make_adapter_with_client()

        await adapter.link_issues("RAISE-1", "RAISE-2", "Blocks")

        mock_client.create_link.assert_called_once_with("RAISE-1", "RAISE-2", "Blocks")


class TestAddComment:
    """add_comment delegates to client and returns CommentRef."""

    @pytest.mark.asyncio
    async def test_returns_comment_ref(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.add_comment.return_value = {
            "id": "10001",
            "self": "https://humansys.atlassian.net/rest/api/2/issue/RAISE-1/comment/10001",
        }

        result = await adapter.add_comment("RAISE-1", "Test comment")

        assert result.id == "10001"
        mock_client.add_comment.assert_called_once_with("RAISE-1", "Test comment")


class TestGetComments:
    """get_comments delegates to client and parses to Comment models."""

    @pytest.mark.asyncio
    async def test_returns_comment_list(self) -> None:
        adapter, mock_client = _make_adapter_with_client()
        mock_client.get_comments.return_value = [
            {
                "id": "10001",
                "body": "First comment",
                "author": {"displayName": "Emilio"},
                "created": "2026-03-01T10:00:00Z",
            },
            {
                "id": "10002",
                "body": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ADF comment"}]}]},
                "author": {"displayName": "Rai"},
                "created": "2026-03-02T10:00:00Z",
            },
        ]

        result = await adapter.get_comments("RAISE-1", limit=10)

        assert len(result) == 2
        assert result[0].id == "10001"
        assert result[0].body == "First comment"
        assert result[0].author == "Emilio"
        assert result[1].body == "ADF comment"


# ── T5: Protocol compliance + entry point ───────────────────────────


class TestProtocolCompliance:
    """Adapter structurally satisfies AsyncProjectManagementAdapter."""

    def test_isinstance_check(self) -> None:
        from raise_cli.adapters.protocols import AsyncProjectManagementAdapter

        adapter = _make_adapter()
        assert isinstance(adapter, AsyncProjectManagementAdapter)

    def test_all_protocol_methods_exist(self) -> None:
        adapter = _make_adapter()
        required = [
            "create_issue", "get_issue", "update_issue", "transition_issue",
            "batch_transition", "search", "link_to_parent", "link_issues",
            "add_comment", "get_comments", "health",
        ]
        for method_name in required:
            assert hasattr(adapter, method_name), f"Missing method: {method_name}"
            assert callable(getattr(adapter, method_name))


class TestEntryPoint:
    """Entry point registration is loadable."""

    def test_entry_point_importable(self) -> None:
        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        assert PythonApiJiraAdapter is not None
        assert hasattr(PythonApiJiraAdapter, "__init__")
