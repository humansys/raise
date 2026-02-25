"""Adapter contracts and registry for raise-cli extensibility.

Public API: 4 Protocols + 5 boundary models + 5 registry functions + 5 group constants.
KnowledgeGraphBackend + BackendHealth moved to rai_core (E275).

Architecture: ADR-033 (PM), ADR-034 (Governance)
"""

from rai_cli.adapters.models import (
    ArtifactLocator,
    CoreArtifactType,
    IssueRef,
    IssueSpec,
    PublishResult,
)
from rai_cli.adapters.protocols import (
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
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
from rai_core.graph.backends.models import BackendHealth
from rai_core.graph.backends.protocol import KnowledgeGraphBackend

__all__ = [
    # Protocols (4 local + 1 from rai_core)
    "DocumentationTarget",
    "GovernanceParser",
    "GovernanceSchemaProvider",
    "KnowledgeGraphBackend",
    "ProjectManagementAdapter",
    # Models (5 local + 1 from rai_core)
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
