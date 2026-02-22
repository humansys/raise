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


class TestPublicAPIExportsRegistryFunctions:
    def test_import_all_registry_functions(self) -> None:
        from rai_cli.adapters import (
            get_doc_targets,
            get_governance_parsers,
            get_governance_schemas,
            get_graph_backends,
            get_pm_adapters,
        )

        fns = [
            get_pm_adapters,
            get_governance_schemas,
            get_governance_parsers,
            get_doc_targets,
            get_graph_backends,
        ]
        for fn in fns:
            assert callable(fn)

    def test_import_all_registry_constants(self) -> None:
        from rai_cli.adapters import (
            EP_DOC_TARGETS,
            EP_GOVERNANCE_PARSERS,
            EP_GOVERNANCE_SCHEMAS,
            EP_GRAPH_BACKENDS,
            EP_PM_ADAPTERS,
        )

        constants = [
            EP_PM_ADAPTERS,
            EP_GOVERNANCE_SCHEMAS,
            EP_GOVERNANCE_PARSERS,
            EP_DOC_TARGETS,
            EP_GRAPH_BACKENDS,
        ]
        for const in constants:
            assert isinstance(const, str)
            assert const.startswith("rai.")


class TestDunderAll:
    def test_all_exports_are_importable(self) -> None:
        import rai_cli.adapters as adapters

        for name in adapters.__all__:
            assert hasattr(adapters, name), f"{name} in __all__ but not importable"
