"""Tests for FilesystemPMAdapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from rai_cli.adapters.filesystem import FilesystemPMAdapter
from rai_cli.adapters.models import AdapterHealth, IssueDetail, IssueSummary
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
