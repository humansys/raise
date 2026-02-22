"""Tests for adapters public API surface."""

from __future__ import annotations

from pydantic import BaseModel


class TestPublicAPIExportsAllProtocols:
    def test_import_all_protocols(self) -> None:
        from rai_cli.adapters import (
            DocumentationTarget,
            GovernanceParser,
            GovernanceSchemaProvider,
            KnowledgeGraphBackend,
            ProjectManagementAdapter,
        )

        protocols = [
            ProjectManagementAdapter,
            GovernanceSchemaProvider,
            GovernanceParser,
            DocumentationTarget,
            KnowledgeGraphBackend,
        ]
        for proto in protocols:
            assert hasattr(proto, "__protocol_attrs__")


class TestPublicAPIExportsAllModels:
    def test_import_all_models(self) -> None:
        from rai_cli.adapters import (
            ArtifactLocator,
            BackendHealth,
            CoreArtifactType,
            IssueRef,
            IssueSpec,
            PublishResult,
        )

        models = [ArtifactLocator, BackendHealth, IssueRef, IssueSpec, PublishResult]
        for model_cls in models:
            assert issubclass(model_cls, BaseModel)

        # CoreArtifactType is StrEnum, not BaseModel
        assert issubclass(CoreArtifactType, str)


class TestDunderAll:
    def test_all_has_eleven_entries(self) -> None:
        import rai_cli.adapters as adapters

        assert len(adapters.__all__) == 11
