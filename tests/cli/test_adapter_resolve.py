"""Tests for resolve_adapter() — auto-detect logic (D3, AR3)."""

from __future__ import annotations

from typing import Any

import pytest

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
from rai_cli.adapters.protocols import ProjectManagementAdapter
from rai_cli.adapters.sync import SyncPMAdapter

# --- Stub adapters for tests ---


class _StubAsyncPM:
    """Minimal async PM stub — satisfies AsyncProjectManagementAdapter."""

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-1")

    async def get_issue(self, key: str) -> IssueDetail:
        return IssueDetail(key=key, summary="Test", status="Open", issue_type="Task")

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return IssueRef(key=key)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        return IssueRef(key=key)

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return BatchResult(succeeded=[IssueRef(key=k) for k in keys])

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        pass

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        pass

    async def add_comment(self, key: str, body: str) -> CommentRef:
        return CommentRef(id="1")

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return []

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return []

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="async-stub", healthy=True)


class _StubPM:
    """Minimal sync PM stub — satisfies ProjectManagementAdapter."""

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-1")

    def get_issue(self, key: str) -> IssueDetail:
        return IssueDetail(key=key, summary="Test", status="Open", issue_type="Task")

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        return IssueRef(key=key)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return BatchResult(succeeded=[IssueRef(key=k) for k in keys])

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        pass

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        pass

    def add_comment(self, key: str, body: str) -> CommentRef:
        return CommentRef(id="1")

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return []

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return []

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="stub", healthy=True)


class TestResolveAdapter:
    """4 cases: 0 adapters, 1 adapter, 2+ adapters, flag override."""

    def test_zero_adapters_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No adapters registered → clear error."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_single_adapter_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exactly 1 adapter registered → auto-select it."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"stub": _StubPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_multiple_adapters_without_flag_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """2+ adapters and no --adapter flag → error listing names."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_flag_override_selects_named_adapter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--adapter flag selects by name, even with multiple registered."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        adapter = resolve_adapter("jira")
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_flag_override_unknown_name_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--adapter flag with unknown name → error."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"jira": _StubPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter("nonexistent")
        assert exc_info.value.code == 1

    def test_async_adapter_gets_auto_wrapped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Async adapter gets auto-wrapped to SyncPMAdapter (AR-1)."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"async-jira": _StubAsyncPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, SyncPMAdapter)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_sync_adapter_not_wrapped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sync adapter is NOT wrapped — no regression."""
        monkeypatch.setattr(
            "rai_cli.cli.commands._adapter_resolve.get_pm_adapters",
            lambda: {"sync-stub": _StubPM},
        )
        from rai_cli.cli.commands._adapter_resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, _StubPM)
        assert not isinstance(adapter, SyncPMAdapter)
