"""Tests for AcliJiraAdapter — full protocol implementation over ACLI."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from rai_pro.adapters.acli_jira import (
    AcliJiraAdapter,
    _adf_to_text,
    normalize_status,
    to_jql,
)

from raise_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)

# ── Fixtures ────────────────────────────────────────────────────────────────

JIRA_YAML = """\
default_instance: humansys

instances:
  humansys:
    site: humansys.atlassian.net
    email: emilio@humansys.ai
    projects: [RAISE]
  rai-agent:
    site: rai-agent.atlassian.net
    email: emilio@humansys.ai
    projects: [RAI]

projects:
  RAISE:
    instance: humansys
    name: RAISE
  RAI:
    instance: rai-agent
    name: Rai Dev
"""


def _run(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    return asyncio.run(coro)


def _make_adapter(tmp_path: Path, yaml_content: str = JIRA_YAML) -> AcliJiraAdapter:
    """Create adapter with a temporary jira.yaml."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    (raise_dir / "jira.yaml").write_text(yaml_content)
    return AcliJiraAdapter(project_root=tmp_path)


# ── Config loading ──────────────────────────────────────────────────────────


class TestConfigLoading:
    """__init__ loads jira.yaml with instances and cross-validation."""

    def test_loads_instances(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert "humansys" in adapter._instances  # pyright: ignore[reportPrivateUsage]
        assert "rai-agent" in adapter._instances  # pyright: ignore[reportPrivateUsage]
        assert adapter._instances["humansys"]["site"] == "humansys.atlassian.net"  # pyright: ignore[reportPrivateUsage]

    def test_loads_default_instance(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter._default_site == "humansys.atlassian.net"  # pyright: ignore[reportPrivateUsage]

    def test_loads_project_instance_mapping(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter._projects["RAISE"]["instance"] == "humansys"  # pyright: ignore[reportPrivateUsage]
        assert adapter._projects["RAI"]["instance"] == "rai-agent"  # pyright: ignore[reportPrivateUsage]

    def test_raises_on_missing_jira_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="jira.yaml"):
            AcliJiraAdapter(project_root=tmp_path)

    def test_raises_on_missing_instances(self, tmp_path: Path) -> None:
        yaml_no_instances = """\
default_instance: humansys
projects:
  RAISE:
    instance: humansys
    name: RAISE
"""
        with pytest.raises(ValueError, match="instances"):
            _make_adapter(tmp_path, yaml_no_instances)

    def test_raises_on_missing_default_instance(self, tmp_path: Path) -> None:
        yaml_no_default = """\
instances:
  humansys:
    site: humansys.atlassian.net
    projects: [RAISE]
projects:
  RAISE:
    instance: humansys
    name: RAISE
"""
        with pytest.raises(ValueError, match="default_instance"):
            _make_adapter(tmp_path, yaml_no_default)

    def test_raises_on_invalid_default_instance(self, tmp_path: Path) -> None:
        yaml_bad_default = """\
default_instance: nonexistent
instances:
  humansys:
    site: humansys.atlassian.net
    projects: [RAISE]
projects:
  RAISE:
    instance: humansys
    name: RAISE
"""
        with pytest.raises(ValueError, match="nonexistent.*not found.*instances"):
            _make_adapter(tmp_path, yaml_bad_default)

    def test_raises_on_project_without_instance(self, tmp_path: Path) -> None:
        yaml_no_proj_instance = """\
default_instance: humansys
instances:
  humansys:
    site: humansys.atlassian.net
    projects: [RAISE]
projects:
  RAISE:
    name: RAISE
"""
        with pytest.raises(ValueError, match="RAISE.*instance"):
            _make_adapter(tmp_path, yaml_no_proj_instance)

    def test_cross_validation_warns_on_mismatch(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        yaml_mismatch = """\
default_instance: humansys
instances:
  humansys:
    site: humansys.atlassian.net
    projects: [OTHER]
projects:
  RAISE:
    instance: humansys
    name: RAISE
"""
        import logging

        with caplog.at_level(logging.WARNING):
            _make_adapter(tmp_path, yaml_mismatch)
        assert "RAISE" in caplog.text
        assert "humansys" in caplog.text


# ── Site resolution ─────────────────────────────────────────────────────────


class TestSiteResolution:
    """_resolve_site maps project key → instance → site."""

    def test_resolve_from_project_key(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter._resolve_site("RAISE") == "humansys.atlassian.net"  # pyright: ignore[reportPrivateUsage]
        assert adapter._resolve_site("RAI") == "rai-agent.atlassian.net"  # pyright: ignore[reportPrivateUsage]

    def test_unknown_project_returns_default(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        adapter = _make_adapter(tmp_path)
        with caplog.at_level(logging.WARNING):
            site = adapter._resolve_site("UNKNOWN")  # pyright: ignore[reportPrivateUsage]
        assert site == "humansys.atlassian.net"
        assert "UNKNOWN" in caplog.text

    def test_resolve_from_issue_key(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter._resolve_site_from_key("RAISE-123") == "humansys.atlassian.net"  # pyright: ignore[reportPrivateUsage]
        assert adapter._resolve_site_from_key("RAI-45") == "rai-agent.atlassian.net"  # pyright: ignore[reportPrivateUsage]

    def test_resolve_from_jql_with_project(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert (
            adapter._resolve_site_from_jql("project = RAISE AND status = Done")
            == "humansys.atlassian.net"
        )  # pyright: ignore[reportPrivateUsage]
        assert (
            adapter._resolve_site_from_jql("project = RAI ORDER BY created")
            == "rai-agent.atlassian.net"
        )  # pyright: ignore[reportPrivateUsage]

    def test_resolve_from_jql_without_project_uses_default(
        self, tmp_path: Path
    ) -> None:
        adapter = _make_adapter(tmp_path)
        assert (
            adapter._resolve_site_from_jql('text ~ "something"')
            == "humansys.atlassian.net"
        )  # pyright: ignore[reportPrivateUsage]

    def test_malformed_key_returns_default_silently(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        # No dash → no project extraction → default, no warning
        assert adapter._resolve_site_from_key("malformed") == "humansys.atlassian.net"  # pyright: ignore[reportPrivateUsage]

    def test_resolve_from_jql_quoted_project(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert (
            adapter._resolve_site_from_jql('project = "RAISE"')
            == "humansys.atlassian.net"
        )  # pyright: ignore[reportPrivateUsage]


# ── Status normalization ────────────────────────────────────────────────────


class TestNormalizeStatus:
    """normalize_status uses convention: replace('-', ' ').title()."""

    def test_in_progress(self) -> None:
        assert normalize_status("in-progress") == "In Progress"

    def test_done(self) -> None:
        assert normalize_status("done") == "Done"

    def test_backlog(self) -> None:
        assert normalize_status("backlog") == "Backlog"

    def test_selected_for_development(self) -> None:
        assert (
            normalize_status("selected for development") == "Selected For Development"
        )


# ── URL construction ────────────────────────────────────────────────────────


class TestBuildUrl:
    """build_url constructs web URL from site + key."""

    def test_builds_browse_url(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert (
            adapter.build_url("RAISE-99")
            == "https://humansys.atlassian.net/browse/RAISE-99"
        )

    def test_unknown_project_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter.build_url("UNKNOWN-1") == ""


# ── Health ──────────────────────────────────────────────────────────────────


class TestHealth:
    """health() delegates to AcliJiraBridge.health()."""

    def test_delegates_to_bridge(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        expected = AdapterHealth(
            name="jira-acli", healthy=True, message="OK", latency_ms=100
        )
        adapter._bridge.health = AsyncMock(return_value=expected)  # pyright: ignore[reportPrivateUsage]

        result = _run(adapter.health())
        assert result.healthy is True
        assert result.name == "jira-acli"


# ── Helpers for mocking bridge ──────────────────────────────────────────────


def _adapter_with_mock_bridge(tmp_path: Path) -> AcliJiraAdapter:
    """Create adapter with mocked bridge.call()."""
    adapter = _make_adapter(tmp_path)
    adapter._bridge.call = AsyncMock()  # pyright: ignore[reportPrivateUsage]
    return adapter


def _set_bridge_response(adapter: AcliJiraAdapter, response: Any) -> None:
    """Set the return value for the next bridge.call()."""
    adapter._bridge.call.return_value = response  # pyright: ignore[reportPrivateUsage, reportAttributeAccessIssue]


def _get_bridge_call_args(
    adapter: AcliJiraAdapter,
) -> tuple[list[str], dict[str, str]]:
    """Get (subcommand, flags) from last bridge.call()."""
    call: AsyncMock = adapter._bridge.call  # pyright: ignore[reportPrivateUsage, reportAssignmentType]
    args = call.call_args
    return args[0][0], args[0][1]  # type: ignore[return-value]


# ── Result envelope (shared by write ops) ───────────────────────────────────

RESULT_ENVELOPE = {
    "results": [{"status": "SUCCESS", "message": "OK", "id": "RAISE-99"}],
    "totalCount": 1,
    "successCount": 1,
}

# ACLI create returns the full issue, not an envelope
CREATE_RESPONSE: dict[str, Any] = {
    "key": "RAISE-99",
    "id": "12345",
    "fields": {"summary": "Test issue", "status": {"name": "Backlog"}},
}


# ── Write ops ───────────────────────────────────────────────────────────────


class TestCreateIssue:
    """create_issue maps IssueSpec → ACLI flags, parses full issue → IssueRef."""

    def test_creates_issue_with_correct_flags(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, CREATE_RESPONSE)

        spec = IssueSpec(summary="Test issue", issue_type="Story", labels=["backend"])
        result = _run(adapter.create_issue("RAISE", spec))

        assert isinstance(result, IssueRef)
        assert result.key == "RAISE-99"
        assert "humansys.atlassian.net" in result.url

        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "create"]
        assert flags["--project"] == "RAISE"
        assert flags["--summary"] == "Test issue"
        assert flags["--type"] == "Story"

    def test_passes_site_to_bridge(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, CREATE_RESPONSE)

        spec = IssueSpec(summary="Test", issue_type="Story")
        _run(adapter.create_issue("RAISE", spec))

        call: AsyncMock = adapter._bridge.call  # pyright: ignore[reportPrivateUsage, reportAssignmentType]
        _, kwargs = call.call_args[0], call.call_args[1]
        assert kwargs["site"] == "humansys.atlassian.net"

    def test_passes_rai_site_to_bridge(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, CREATE_RESPONSE)

        spec = IssueSpec(summary="Test", issue_type="Story")
        _run(adapter.create_issue("RAI", spec))

        call: AsyncMock = adapter._bridge.call  # pyright: ignore[reportPrivateUsage, reportAssignmentType]
        _, kwargs = call.call_args[0], call.call_args[1]
        assert kwargs["site"] == "rai-agent.atlassian.net"

    def test_creates_issue_with_description(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, CREATE_RESPONSE)

        spec = IssueSpec(summary="Test", description="Body text")
        _run(adapter.create_issue("RAISE", spec))

        _, flags = _get_bridge_call_args(adapter)
        assert flags["--description"] == "Body text"


class TestUpdateIssue:
    """update_issue maps fields dict → ACLI flags."""

    def test_updates_issue(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, RESULT_ENVELOPE)

        result = _run(adapter.update_issue("RAISE-99", {"summary": "New title"}))

        assert result.key == "RAISE-99"
        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "edit"]
        assert flags["--key"] == "RAISE-99"
        assert flags["--summary"] == "New title"


class TestTransitionIssue:
    """transition_issue normalizes status and calls ACLI."""

    def test_transitions_with_normalized_name(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, RESULT_ENVELOPE)

        result = _run(adapter.transition_issue("RAISE-99", "in-progress"))

        assert result.key == "RAISE-99"
        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "transition"]
        assert flags["--status"] == "In Progress"


class TestBatchTransition:
    """batch_transition loops with error isolation."""

    def test_batch_all_succeed(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        envelopes = [
            {"results": [{"status": "SUCCESS", "id": f"RAISE-{i}"}]} for i in range(3)
        ]
        adapter._bridge.call = AsyncMock(side_effect=envelopes)  # pyright: ignore[reportPrivateUsage]

        result = _run(
            adapter.batch_transition(["RAISE-0", "RAISE-1", "RAISE-2"], "done")
        )

        assert isinstance(result, BatchResult)
        assert len(result.succeeded) == 3
        assert len(result.failed) == 0

    def test_batch_partial_failure(self, tmp_path: Path) -> None:
        from rai_pro.adapters.acli_bridge import AcliBridgeError

        adapter = _adapter_with_mock_bridge(tmp_path)
        adapter._bridge.call = AsyncMock(  # pyright: ignore[reportPrivateUsage]
            side_effect=[
                {"results": [{"status": "SUCCESS", "id": "RAISE-1"}]},
                AcliBridgeError("transition failed"),
                {"results": [{"status": "SUCCESS", "id": "RAISE-3"}]},
            ]
        )

        result = _run(
            adapter.batch_transition(["RAISE-1", "RAISE-2", "RAISE-3"], "done")
        )

        assert len(result.succeeded) == 2
        assert len(result.failed) == 1
        assert result.failed[0].key == "RAISE-2"


# ── Read ops ────────────────────────────────────────────────────────────────

NESTED_ISSUE: dict[str, Any] = {
    "key": "RAISE-42",
    "self": "https://api.atlassian.net/rest/api/2/issue/12345",
    "fields": {
        "summary": "Test issue",
        "status": {"name": "In Progress"},
        "issuetype": {"name": "Story"},
        "priority": {"name": "Medium"},
        "assignee": {"displayName": "Emilio Osorio"},
        "labels": ["backend", "acli"],
        "parent": {"key": "RAISE-10"},
        "created": "2026-03-19T10:00:00.000+0000",
        "updated": "2026-03-19T12:00:00.000+0000",
        "description": {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Fix the ADF bug."}],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Step one"}],
                                }
                            ],
                        },
                    ],
                },
            ],
        },
    },
}

NESTED_ISSUE_MINIMAL: dict[str, Any] = {
    "key": "RAISE-43",
    "fields": {
        "summary": "Minimal issue",
        "status": {"name": "Backlog"},
        "issuetype": {"name": "Task"},
        "priority": None,
        "assignee": None,
        "labels": [],
        "parent": None,
        "created": "2026-03-19T10:00:00.000+0000",
        "updated": "",
        "description": "",
    },
}


# ── ADF to text ─────────────────────────────────────────────────────────────


class TestAdfToText:
    """_adf_to_text converts ADF dicts to plain text; passes strings through."""

    def test_plain_string_passthrough(self) -> None:
        assert _adf_to_text("hello world") == "hello world"

    def test_empty_string_passthrough(self) -> None:
        assert _adf_to_text("") == ""

    def test_none_returns_empty(self) -> None:
        assert _adf_to_text(None) == ""

    def test_empty_doc(self) -> None:
        assert _adf_to_text({"type": "doc", "content": []}) == ""

    def test_paragraph_with_text(self) -> None:
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello world"}],
                }
            ],
        }
        result = _adf_to_text(adf)
        assert "Hello world" in result
        assert "{'type'" not in result

    def test_bullet_list(self) -> None:
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
                                    "content": [{"type": "text", "text": "Item A"}],
                                }
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Item B"}],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
        result = _adf_to_text(adf)
        assert "Item A" in result
        assert "Item B" in result

    def test_nested_doc_from_fixture(self) -> None:
        """NESTED_ISSUE description must yield readable text."""
        description = NESTED_ISSUE["fields"]["description"]
        result = _adf_to_text(description)
        assert "Fix the ADF bug." in result
        assert "Step one" in result
        assert "{'type'" not in result
        assert "{'version'" not in result


class TestGetIssue:
    """get_issue parses nested Jira API format → IssueDetail."""

    def test_parses_full_issue(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, NESTED_ISSUE)

        result = _run(adapter.get_issue("RAISE-42"))

        assert isinstance(result, IssueDetail)
        assert result.key == "RAISE-42"
        assert result.summary == "Test issue"
        assert result.status == "In Progress"
        assert result.issue_type == "Story"
        assert result.parent_key == "RAISE-10"
        assert result.assignee == "Emilio Osorio"
        assert result.priority == "Medium"
        assert result.labels == ["backend", "acli"]
        assert "humansys.atlassian.net" in result.url
        assert "Fix the ADF bug." in result.description
        assert "{'type'" not in result.description

    def test_handles_null_fields(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, NESTED_ISSUE_MINIMAL)

        result = _run(adapter.get_issue("RAISE-43"))

        assert result.parent_key is None
        assert result.assignee is None
        assert result.priority is None

    def test_handles_fields_null(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, {"key": "RAISE-44", "fields": None})

        result = _run(adapter.get_issue("RAISE-44"))

        assert result.key == "RAISE-44"
        assert result.summary == ""
        assert result.status == ""


class TestSearch:
    """search handles top-level array (not {issues: [...]})."""

    def test_parses_array_response(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, [NESTED_ISSUE, NESTED_ISSUE_MINIMAL])

        results = _run(adapter.search("project = RAISE", limit=10))

        assert len(results) == 2
        assert all(isinstance(r, IssueSummary) for r in results)
        assert results[0].key == "RAISE-42"
        assert results[1].key == "RAISE-43"
        assert results[0].status == "In Progress"

    def test_empty_results(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, [])

        results = _run(adapter.search("project = NONEXISTENT"))
        assert results == []

    def test_passes_jql_and_limit(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, [])

        _run(adapter.search("project = RAISE ORDER BY created", limit=5))

        _, flags = _get_bridge_call_args(adapter)
        assert flags["--jql"] == 'project = "RAISE" ORDER BY created'
        assert flags["--limit"] == "5"


class TestToJql:
    """to_jql normalizes user queries to valid JQL."""

    def test_issue_key(self) -> None:
        assert to_jql("RAISE-123") == "issue = RAISE-123"

    def test_jql_passthrough(self) -> None:
        assert (
            to_jql("project = RAISE AND status = Done")
            == 'project = "RAISE" AND status = Done'
        )

    def test_text_search(self) -> None:
        assert to_jql("some text query") == 'text ~ "some text query"'

    def test_escaped_operators(self) -> None:
        assert (
            to_jql("project = RAISE AND status \\!= Done")
            == 'project = "RAISE" AND status != Done'
        )

    def test_reserved_word_project_value_quoted(self) -> None:
        assert (
            to_jql("project = RAISE AND status = Done")
            == 'project = "RAISE" AND status = Done'
        )

    def test_already_quoted_project_unchanged(self) -> None:
        assert (
            to_jql('project = "RAISE" AND status = Done')
            == 'project = "RAISE" AND status = Done'
        )

    def test_non_reserved_project_also_quoted(self) -> None:
        """Quoting non-reserved words is safe and consistent."""
        assert (
            to_jql("project = MYPROJ AND status = Done")
            == 'project = "MYPROJ" AND status = Done'
        )


# ── Comments ────────────────────────────────────────────────────────────────

ACLI_COMMENTS_RESPONSE: dict[str, Any] = {
    "comments": [
        {"id": "101", "author": "Emilio Osorio", "body": "First comment"},
        {"id": "102", "author": "Rai", "body": "Second comment"},
    ],
    "isLast": True,
    "maxResults": 10,
    "startAt": 0,
    "total": 2,
}

COMMENT_CREATE_ENVELOPE: dict[str, Any] = {
    "results": [{"status": "SUCCESS", "id": "101"}],
    "totalCount": 1,
    "successCount": 1,
}


class TestAddComment:
    """add_comment sends body to ACLI, parses envelope → CommentRef."""

    def test_creates_comment(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, COMMENT_CREATE_ENVELOPE)

        result = _run(adapter.add_comment("RAISE-99", "test body"))

        assert isinstance(result, CommentRef)
        assert result.id == "101"

        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "comment", "create"]
        assert flags["--key"] == "RAISE-99"
        assert flags["--body"] == "test body"


class TestGetComments:
    """get_comments parses ACLI comment format (author string, no created)."""

    def test_parses_comments(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, ACLI_COMMENTS_RESPONSE)

        results = _run(adapter.get_comments("RAISE-99", limit=10))

        assert len(results) == 2
        assert all(isinstance(c, Comment) for c in results)
        assert results[0].id == "101"
        assert results[0].author == "Emilio Osorio"
        assert results[0].body == "First comment"
        assert results[0].created == ""  # ACLI omits created

    def test_empty_comments(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, {"comments": [], "total": 0})

        results = _run(adapter.get_comments("RAISE-99"))
        assert results == []

    def test_passes_limit(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, {"comments": [], "total": 0})

        _run(adapter.get_comments("RAISE-99", limit=5))

        _, flags = _get_bridge_call_args(adapter)
        assert flags["--limit"] == "5"


# ── Links ───────────────────────────────────────────────────────────────────

LINK_ENVELOPE: dict[str, Any] = {
    "results": [{"status": "SUCCESS", "id": "link-1"}],
    "totalCount": 1,
    "successCount": 1,
}


class TestLinkIssues:
    """link_issues sends out/in/type flags to ACLI."""

    def test_creates_link(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, LINK_ENVELOPE)

        _run(adapter.link_issues("RAISE-1", "RAISE-2", "blocks"))

        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "link", "create"]
        assert flags["--out"] == "RAISE-1"
        assert flags["--in"] == "RAISE-2"
        assert flags["--type"] == "blocks"


class TestLinkToParent:
    """link_to_parent sets parent via workitem edit."""

    def test_sets_parent(self, tmp_path: Path) -> None:
        adapter = _adapter_with_mock_bridge(tmp_path)
        _set_bridge_response(adapter, RESULT_ENVELOPE)

        _run(adapter.link_to_parent("RAISE-2", "RAISE-1"))

        sub, flags = _get_bridge_call_args(adapter)
        assert sub == ["workitem", "edit"]
        assert flags["--key"] == "RAISE-2"
        assert flags["--parent"] == "RAISE-1"
