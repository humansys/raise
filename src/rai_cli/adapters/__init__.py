"""Adapter contracts for raise-cli extensibility.

Public API: 5 Protocols + 6 boundary models.

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
]
