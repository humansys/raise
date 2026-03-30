"""Tests for generic entry-point resolver (resolve_entrypoint, resolve_adapter, resolve_docs_target).

Covers: D7 (generic resolver), MUST-4 (both backlog and docs use it).
Replaces test_adapter_resolve.py after _adapter_resolve.py → _resolve.py refactor.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from raise_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.adapters.composite_docs import CompositeDocTarget
from raise_cli.adapters.protocols import DocumentationTarget, ProjectManagementAdapter
from raise_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter

# --- Stub adapters for tests ---

# Monkeypatch target for the generic resolver
_RESOLVE_MOD = "raise_cli.cli.commands._resolve"


class _StubAsyncPM:
    """Minimal async PM stub."""

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
    """Minimal sync PM stub."""

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


class _StubAsyncDocs:
    """Minimal async docs target stub."""

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://example.com/page/1")

    async def get_page(self, identifier: str) -> PageContent:
        return PageContent(id=identifier, title="Test Page", content="# Test")

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="async-docs-stub", healthy=True)


class _StubDocs:
    """Minimal sync docs target stub."""

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://example.com/page/1")

    def get_page(self, identifier: str) -> PageContent:
        return PageContent(id=identifier, title="Test Page", content="# Test")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="docs-stub", healthy=True)


# --- PM adapter tests (migrated from test_adapter_resolve.py) ---


class TestResolveAdapter:
    """resolve_adapter() — auto-detect logic for PM adapters."""

    def test_zero_adapters_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {})
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_single_adapter_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"stub": _StubPM}
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_multiple_adapters_without_flag_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_flag_override_selects_named(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter("jira")
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_flag_unknown_name_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM}
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter("nonexistent")
        assert exc_info.value.code == 1

    def test_async_adapter_gets_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"async-jira": _StubAsyncPM}
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, SyncPMAdapter)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_sync_adapter_not_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"sync-stub": _StubPM}
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, _StubPM)
        assert not isinstance(adapter, SyncPMAdapter)


# --- Docs target tests (new) ---


class TestResolveDocsTarget:
    """resolve_docs_target() — auto-detect logic for docs targets."""

    def test_zero_targets_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_doc_targets", lambda: {})
        from raise_cli.cli.commands._resolve import resolve_docs_target

        with pytest.raises(SystemExit) as exc_info:
            resolve_docs_target(None)
        assert exc_info.value.code == 1

    def test_single_target_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets", lambda: {"confluence": _StubDocs}
        )
        from raise_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, DocumentationTarget)

    def test_multiple_targets_auto_composes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}._discover_docs",
            lambda: {"filesystem": _StubDocs, "confluence": _StubDocs},
        )
        from raise_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, CompositeDocTarget)
        assert isinstance(target, DocumentationTarget)

    def test_flag_override_selects_named(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets",
            lambda: {"confluence": _StubDocs, "notion": _StubDocs},
        )
        from raise_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target("confluence")
        assert isinstance(target, DocumentationTarget)

    def test_async_target_gets_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets",
            lambda: {"async-confluence": _StubAsyncDocs},
        )
        from raise_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, SyncDocsAdapter)
        assert isinstance(target, DocumentationTarget)

    def test_sync_target_not_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets", lambda: {"sync-stub": _StubDocs}
        )
        from raise_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, _StubDocs)
        assert not isinstance(target, SyncDocsAdapter)


# --- YAML + entry point mixed tests (S337.3) ---

_DISCOVER_MOD = "raise_cli.adapters.declarative.discovery"


class TestResolveAdapterWithYaml:
    """resolve_adapter() — YAML adapter discovery merged with entry points."""

    def test_yaml_only_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """YAML adapter auto-selected when no entry points registered."""
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {})
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {"yaml-stub": _StubPM} if protocol == "pm" else {},
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_yaml_selected_by_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """YAML adapter selected by explicit --adapter flag."""
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {})
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {"github": _StubPM} if protocol == "pm" else {},
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter("github")
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_entrypoint_wins_on_collision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Entry point takes priority over YAML when names collide."""

        class _EpStub(_StubPM):
            """Entry point stub — distinguishable from YAML stub."""

        class _YamlStub(_StubPM):
            """YAML stub — should lose on collision."""

        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _EpStub}
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {"jira": _YamlStub} if protocol == "pm" else {},
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter("jira")
        assert isinstance(adapter, _EpStub)

    def test_mixed_yaml_and_ep_no_collision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Both YAML and EP adapters available, no name collision."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM}
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {"github": _StubPM} if protocol == "pm" else {},
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        # Multiple adapters without flag → error listing both
        with pytest.raises(SystemExit):
            resolve_adapter(None)

        # With flag → selects the named one
        adapter = resolve_adapter("github")
        assert isinstance(adapter, ProjectManagementAdapter)


class TestResolveAdapterManifestDefault:
    """resolve_adapter() — manifest default resolution (S347.1)."""

    def test_manifest_default_used_when_no_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Manifest adapter_default selects adapter when no -a flag."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "filesystem": _StubPM},
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        # Simulate manifest with backlog.adapter_default = "jira"
        from raise_cli.onboarding.manifest import BacklogConfig, ProjectManifest

        _fake_manifest = ProjectManifest(
            project={"name": "test", "project_type": "brownfield"},  # type: ignore[arg-type]
            backlog=BacklogConfig(adapter_default="jira"),
        )
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.load_manifest", lambda _path: _fake_manifest
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_explicit_flag_overrides_manifest_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Explicit -a flag wins over manifest default."""

        class _JiraStub(_StubPM):
            pass

        class _FsStub(_StubPM):
            pass

        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _JiraStub, "filesystem": _FsStub},
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        from raise_cli.onboarding.manifest import BacklogConfig, ProjectManifest

        _fake_manifest = ProjectManifest(
            project={"name": "test", "project_type": "brownfield"},  # type: ignore[arg-type]
            backlog=BacklogConfig(adapter_default="jira"),
        )
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.load_manifest", lambda _path: _fake_manifest
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter("filesystem")
        assert isinstance(adapter, _FsStub)

    def test_no_manifest_falls_through_to_autodetect(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No manifest → auto-detect still works for single adapter."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM}
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _path: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_no_manifest_multiple_adapters_errors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No manifest + multiple adapters + no flag → error."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "filesystem": _StubPM},
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _path: None)
        from raise_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_manifest_without_backlog_section(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Manifest exists but no backlog section → falls through."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM}
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        from raise_cli.onboarding.manifest import ProjectManifest

        _fake_manifest = ProjectManifest(
            project={"name": "test", "project_type": "brownfield"},  # type: ignore[arg-type]
        )
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.load_manifest", lambda _path: _fake_manifest
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        # Single adapter, no backlog config → auto-detect works
        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_manifest_default_not_registered_errors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Manifest default points to adapter that isn't registered → clear error."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "filesystem": _StubPM},
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        from raise_cli.onboarding.manifest import BacklogConfig, ProjectManifest

        _fake_manifest = ProjectManifest(
            project={"name": "test", "project_type": "brownfield"},  # type: ignore[arg-type]
            backlog=BacklogConfig(adapter_default="linear"),
        )
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.load_manifest", lambda _path: _fake_manifest
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_manifest_empty_string_default_falls_through(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Manifest adapter_default: '' treated as no default → auto-detect."""
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM}
        )
        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: {},
        )
        from raise_cli.onboarding.manifest import BacklogConfig, ProjectManifest

        _fake_manifest = ProjectManifest(
            project={"name": "test", "project_type": "brownfield"},  # type: ignore[arg-type]
            backlog=BacklogConfig(adapter_default=""),
        )
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.load_manifest", lambda _path: _fake_manifest
        )
        from raise_cli.cli.commands._resolve import resolve_adapter

        # Empty string → falls through to auto-detect → single adapter selected
        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)


class TestResolveAdapterE2E:
    """End-to-end: YAML file on disk → resolve_adapter → working adapter."""

    def test_yaml_file_to_adapter_instance(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Full path: YAML config file → discover → resolve → instantiate."""
        import shutil

        fixtures = Path(__file__).parents[1] / "adapters" / "declarative" / "fixtures"
        adapters_dir = tmp_path / ".raise" / "adapters"
        adapters_dir.mkdir(parents=True)
        shutil.copy(fixtures / "minimal.yaml", adapters_dir / "minimal.yaml")

        # Patch EP to empty so only YAML is found
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {})
        monkeypatch.setattr(f"{_RESOLVE_MOD}.load_manifest", lambda _: None)
        # Patch discover to use our tmp dir
        from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

        monkeypatch.setattr(
            f"{_DISCOVER_MOD}.discover_yaml_adapters",
            lambda protocol, **kw: discover_yaml_adapters(
                protocol, adapters_dir=adapters_dir
            ),
        )

        from raise_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        # Should be wrapped in SyncPMAdapter since DeclarativeMcpAdapter is async
        assert isinstance(adapter, SyncPMAdapter)
