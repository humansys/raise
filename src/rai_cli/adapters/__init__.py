"""Adapter contracts and registry for raise-cli extensibility.

Public API: 5 Protocols + 6 boundary models + 5 registry functions + 5 group constants.

Architecture: ADR-033 (PM), ADR-034 (Governance), ADR-036 (Graph Backend)
"""

from rai_cli.adapters.models import (
    ArtifactLocator,
    BackendHealth,
    CoreArtifactType,
    IssueRef,
    IssueSpec,
    PublishResult,
)
from rai_cli.adapters.protocols import (
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
    KnowledgeGraphBackend,
    ProjectManagementAdapter,
)
from rai_cli.adapters.registry import (
    EP_DOC_TARGETS,
    EP_GOVERNANCE_PARSERS,
    EP_GOVERNANCE_SCHEMAS,
    EP_GRAPH_BACKENDS,
    EP_PM_ADAPTERS,
    get_doc_targets,
    get_governance_parsers,
    get_governance_schemas,
    get_graph_backends,
    get_pm_adapters,
)

__all__ = [
    # Protocols
    "DocumentationTarget",
    "GovernanceParser",
    "GovernanceSchemaProvider",
    "KnowledgeGraphBackend",
    "ProjectManagementAdapter",
    # Models
    "ArtifactLocator",
    "BackendHealth",
    "CoreArtifactType",
    "IssueRef",
    "IssueSpec",
    "PublishResult",
    # Registry functions
    "get_doc_targets",
    "get_governance_parsers",
    "get_governance_schemas",
    "get_graph_backends",
    "get_pm_adapters",
    # Entry point group constants
    "EP_DOC_TARGETS",
    "EP_GOVERNANCE_PARSERS",
    "EP_GOVERNANCE_SCHEMAS",
    "EP_GRAPH_BACKENDS",
    "EP_PM_ADAPTERS",
]
