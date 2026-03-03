"""Tests for FilesystemPMAdapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from rai_cli.adapters.filesystem import FilesystemPMAdapter
from rai_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)
from rai_cli.adapters.protocols import ProjectManagementAdapter

SAMPLE_BACKLOG = """\
# Backlog: test-project

> **Status**: Active

---

## 1. Epics Overview

| ID | Epic | Status | Scope Doc | Priority |
|----|------|--------|-----------|----------|
| E1 | **Core Foundation** | ✅ Complete | `scope.md` | — |
| E2 | **API Layer** | 🚀 In Progress | `api-scope.md` | P0 |
| E3 | **Frontend** | 📋 Backlog | — | P1 |
| E4 | **Testing** | 📋 DRAFT | — | P2 |
"""


@pytest.fixture()
def backlog_dir(tmp_path: Path) -> Path:
    """Create a temp project with governance/backlog.md."""
    gov = tmp_path / "governance"
    gov.mkdir()
    (gov / "backlog.md").write_text(SAMPLE_BACKLOG, encoding="utf-8")
    return tmp_path


@pytest.fixture()
def adapter(backlog_dir: Path) -> FilesystemPMAdapter:
    return FilesystemPMAdapter(project_root=backlog_dir)


class TestProtocolCompliance:
    def test_isinstance_check(self, adapter: FilesystemPMAdapter) -> None:
        assert isinstance(adapter, ProjectManagementAdapter)


class TestHealth:
    def test_healthy_when_backlog_exists(self, adapter: FilesystemPMAdapter) -> None:
        h = adapter.health()
        assert isinstance(h, AdapterHealth)
        assert h.name == "filesystem"
        assert h.healthy is True
        assert "4 epics" in h.message

    def test_unhealthy_when_no_backlog(self, tmp_path: Path) -> None:
        a = FilesystemPMAdapter(project_root=tmp_path)
        h = a.health()
        assert h.healthy is False
        assert "not found" in h.message


class TestSearch:
    def test_search_all(self, adapter: FilesystemPMAdapter) -> None:
        results = adapter.search("", limit=50)
        assert len(results) == 4
        assert all(isinstance(r, IssueSummary) for r in results)

    def test_search_by_status(self, adapter: FilesystemPMAdapter) -> None:
        results = adapter.search("status = complete", limit=50)
        assert len(results) == 1
        assert results[0].key == "E1"

    def test_search_by_name(self, adapter: FilesystemPMAdapter) -> None:
        results = adapter.search("frontend", limit=50)
        assert len(results) == 1
        assert results[0].key == "E3"

    def test_search_case_insensitive(self, adapter: FilesystemPMAdapter) -> None:
        results = adapter.search("CORE", limit=50)
        assert len(results) == 1
        assert results[0].key == "E1"

    def test_search_respects_limit(self, adapter: FilesystemPMAdapter) -> None:
        results = adapter.search("", limit=2)
        assert len(results) == 2

    def test_search_no_backlog(self, tmp_path: Path) -> None:
        a = FilesystemPMAdapter(project_root=tmp_path)
        results = a.search("anything")
        assert results == []


class TestGetIssue:
    def test_get_existing_epic(self, adapter: FilesystemPMAdapter) -> None:
        detail = adapter.get_issue("E2")
        assert isinstance(detail, IssueDetail)
        assert detail.key == "E2"
        assert detail.summary == "API Layer"
        assert detail.status == "in_progress"
        assert detail.issue_type == "Epic"

    def test_get_missing_epic(self, adapter: FilesystemPMAdapter) -> None:
        with pytest.raises(KeyError, match="E99"):
            adapter.get_issue("E99")


class TestGetComments:
    def test_always_empty(self, adapter: FilesystemPMAdapter) -> None:
        comments = adapter.get_comments("E1")
        assert comments == []


class TestCreateIssue:
    def test_append_row_with_auto_id(self, adapter: FilesystemPMAdapter) -> None:
        ref = adapter.create_issue(
            "TEST",
            IssueSpec(
                summary="New Feature",
                issue_type="Epic",
                metadata={"priority": "P1", "scope_doc": "new-scope.md"},
            ),
        )
        assert isinstance(ref, IssueRef)
        assert ref.key == "E5"  # next after E4

        # Verify it's searchable
        results = adapter.search("New Feature")
        assert len(results) == 1
        assert results[0].key == "E5"

    def test_preserves_table_format(self, backlog_dir: Path) -> None:
        a = FilesystemPMAdapter(project_root=backlog_dir)
        a.create_issue("TEST", IssueSpec(summary="Another", issue_type="Epic"))

        content = (backlog_dir / "governance" / "backlog.md").read_text(
            encoding="utf-8"
        )
        # New row should have bold name and proper columns
        assert "| E5 | **Another** |" in content

    def test_default_status_is_backlog(self, adapter: FilesystemPMAdapter) -> None:
        adapter.create_issue("TEST", IssueSpec(summary="New Epic"))
        detail = adapter.get_issue("E5")
        # normalize_status("📋 Backlog") → "draft" (📋 emoji match)
        assert detail.status == "draft"


class TestTransitionIssue:
    def test_transition_to_complete(self, adapter: FilesystemPMAdapter) -> None:
        ref = adapter.transition_issue("E3", "complete")
        assert isinstance(ref, IssueRef)
        assert ref.key == "E3"

        detail = adapter.get_issue("E3")
        assert detail.status == "complete"

    def test_transition_to_in_progress(self, adapter: FilesystemPMAdapter) -> None:
        adapter.transition_issue("E3", "in_progress")
        detail = adapter.get_issue("E3")
        assert detail.status == "in_progress"

    def test_transition_missing_epic(self, adapter: FilesystemPMAdapter) -> None:
        with pytest.raises(KeyError, match="E99"):
            adapter.transition_issue("E99", "complete")

    def test_emoji_preserved_in_file(self, backlog_dir: Path) -> None:
        a = FilesystemPMAdapter(project_root=backlog_dir)
        a.transition_issue("E3", "complete")
        content = (backlog_dir / "governance" / "backlog.md").read_text(
            encoding="utf-8"
        )
        assert "✅ Complete" in content


class TestUpdateIssue:
    def test_update_summary(self, adapter: FilesystemPMAdapter) -> None:
        ref = adapter.update_issue("E3", {"summary": "New Frontend"})
        assert isinstance(ref, IssueRef)
        assert ref.key == "E3"

        detail = adapter.get_issue("E3")
        assert detail.summary == "New Frontend"

    def test_update_missing_epic(self, adapter: FilesystemPMAdapter) -> None:
        with pytest.raises(KeyError, match="E99"):
            adapter.update_issue("E99", {"summary": "x"})


class TestBatchTransition:
    def test_batch_success(self, adapter: FilesystemPMAdapter) -> None:
        result = adapter.batch_transition(["E3", "E4"], "complete")
        assert isinstance(result, BatchResult)
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0

    def test_batch_partial_failure(self, adapter: FilesystemPMAdapter) -> None:
        result = adapter.batch_transition(["E3", "E99"], "complete")
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.failed[0].key == "E99"


MIXED_BACKLOG = """\
# Backlog: test-project

> **Status**: Active

---

## 1. Epics Overview

| ID | Epic | Status | Scope Doc | Priority |
|----|------|--------|-----------|----------|
| E1 | **Core Foundation** | ✅ Complete | `scope.md` | — |
| [RAISE-301](https://example.com/RAISE-301) | **Agent Tool Abstraction** | 🚀 In Progress | `e301/scope.md` | P0 |
| [RAISE-325](https://example.com/RAISE-325) | **Orchestrated Workflow** | 📋 Backlog | — | P1 |
"""


class TestJiraLinkFormat:
    @pytest.fixture()
    def mixed_dir(self, tmp_path: Path) -> Path:
        gov = tmp_path / "governance"
        gov.mkdir()
        (gov / "backlog.md").write_text(MIXED_BACKLOG, encoding="utf-8")
        return tmp_path

    @pytest.fixture()
    def mixed_adapter(self, mixed_dir: Path) -> FilesystemPMAdapter:
        return FilesystemPMAdapter(project_root=mixed_dir)

    def test_search_includes_jira_link_epics(
        self, mixed_adapter: FilesystemPMAdapter
    ) -> None:
        results = mixed_adapter.search("", limit=50)
        keys = {r.key for r in results}
        assert "E1" in keys
        assert "RAISE-301" in keys
        assert "RAISE-325" in keys
        assert len(results) == 3

    def test_get_jira_link_epic(self, mixed_adapter: FilesystemPMAdapter) -> None:
        detail = mixed_adapter.get_issue("RAISE-301")
        assert detail.summary == "Agent Tool Abstraction"
        assert detail.status == "in_progress"

    def test_transition_jira_link_epic(
        self, mixed_adapter: FilesystemPMAdapter
    ) -> None:
        mixed_adapter.transition_issue("RAISE-301", "complete")
        detail = mixed_adapter.get_issue("RAISE-301")
        assert detail.status == "complete"

    def test_health_counts_all_formats(
        self, mixed_adapter: FilesystemPMAdapter
    ) -> None:
        h = mixed_adapter.health()
        assert "3 epics" in h.message


class TestNoOps:
    def test_add_comment_returns_empty_ref(self, adapter: FilesystemPMAdapter) -> None:
        ref = adapter.add_comment("E1", "hello")
        assert isinstance(ref, CommentRef)
        assert ref.id == ""

    def test_link_to_parent_is_noop(self, adapter: FilesystemPMAdapter) -> None:
        adapter.link_to_parent("E1", "E2")  # should not raise

    def test_link_issues_is_noop(self, adapter: FilesystemPMAdapter) -> None:
        adapter.link_issues("E1", "E2", "blocks")  # should not raise
