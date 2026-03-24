"""Adapter contracts and registry for raise-cli extensibility.

Public API: 7 Protocols + 15 boundary models + 2 sync wrappers
+ 5 registry functions + 5 group constants.
KnowledgeGraphBackend + BackendHealth moved to raise_core (E275).

Architecture: ADR-033 (PM), ADR-034 (Governance)
"""

from raise_cli.adapters.models import (
    AdapterHealth,
    ArtifactLocator,
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
from raise_cli.adapters.protocols import (
    AsyncDocumentationTarget,
    AsyncProjectManagementAdapter,
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
    ProjectManagementAdapter,
)
from raise_cli.adapters.registry import (
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
from raise_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter
from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import KnowledgeGraphBackend

__all__ = [
    # Protocols — sync (4 local + 1 from raise_core)
    "DocumentationTarget",
    "GovernanceParser",
    "GovernanceSchemaProvider",
    "KnowledgeGraphBackend",
    "ProjectManagementAdapter",
    # Protocols — async (2)
    "AsyncDocumentationTarget",
    "AsyncProjectManagementAdapter",
    # Sync wrappers (2)
    "SyncDocsAdapter",
    "SyncPMAdapter",
    # Models (14 local + 1 from raise_core)
    "AdapterHealth",
    "ArtifactLocator",
    "BackendHealth",
    "BatchResult",
    "Comment",
    "CommentRef",
    "CoreArtifactType",
    "FailureDetail",
    "IssueDetail",
    "IssueRef",
    "IssueSpec",
    "IssueSummary",
    "PageContent",
    "PageSummary",
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
