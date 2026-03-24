"""Tests for adapters public API surface."""

from __future__ import annotations

from pydantic import BaseModel


class TestPublicAPIExportsAllProtocols:
    def test_import_all_protocols(self) -> None:
        from raise_cli.adapters import (
            AsyncDocumentationTarget,
            AsyncProjectManagementAdapter,
            DocumentationTarget,
            GovernanceParser,
            GovernanceSchemaProvider,
            KnowledgeGraphBackend,
            ProjectManagementAdapter,
        )

        protocols = [
            ProjectManagementAdapter,
            AsyncProjectManagementAdapter,
            GovernanceSchemaProvider,
            GovernanceParser,
            DocumentationTarget,
            AsyncDocumentationTarget,
            KnowledgeGraphBackend,
        ]
        for proto in protocols:
            assert hasattr(proto, "__protocol_attrs__")


class TestPublicAPIExportsAllModels:
    def test_import_all_models(self) -> None:
        from raise_cli.adapters import (
            AdapterHealth,
            ArtifactLocator,
            BackendHealth,
            BatchResult,
            Comment,
            CommentRef,
            CoreArtifactType,
            FailureDetail,
            IssueDetail,
            IssueRef,
            IssueSpec,
            IssueSummary,
            PageContent,
            PageSummary,
            PublishResult,
        )

        models = [
            AdapterHealth,
            ArtifactLocator,
            BackendHealth,
            BatchResult,
            Comment,
            CommentRef,
            FailureDetail,
            IssueDetail,
            IssueRef,
            IssueSpec,
            IssueSummary,
            PageContent,
            PageSummary,
            PublishResult,
        ]
        for model_cls in models:
            assert issubclass(model_cls, BaseModel)

        # CoreArtifactType is StrEnum, not BaseModel
        assert issubclass(CoreArtifactType, str)


class TestPublicAPIExportsSyncWrappers:
    def test_import_sync_wrappers(self) -> None:
        from raise_cli.adapters import SyncDocsAdapter, SyncPMAdapter

        assert SyncPMAdapter is not None
        assert SyncDocsAdapter is not None


class TestDunderAll:
    def test_all_exports_are_importable(self) -> None:
        from raise_cli import adapters

        for name in adapters.__all__:
            assert hasattr(adapters, name), f"{name} in __all__ but not importable"

    def test_all_count(self) -> None:
        """Guardrail: __all__ has expected number of exports."""
        from raise_cli import adapters

        # 7 protocols + 2 wrappers + 15 models + 5 registry fns + 5 constants = 34
        assert len(adapters.__all__) == 34
