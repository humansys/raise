"""Adapter boundary models — organized by protocol concern.

Re-exports all public models for backwards compatibility.
Consumers can import from here or from the specific submodule:

    from raise_cli.adapters.models import IssueSpec          # works
    from raise_cli.adapters.models.pm import IssueSpec        # also works

Submodules:
    pm          — ProjectManagementAdapter boundary models
    docs        — DocumentationTarget boundary models
    governance  — GovernanceSchemaProvider / GovernanceParser models
    health      — Cross-cutting AdapterHealth

Architecture: ADR-033 (Open-core adapter architecture), ADR-034 (Governance extensibility)
RAISE-1060: Split from monolithic models.py into per-protocol modules.
"""

from raise_cli.adapters.models.docs import (
    PageContent,
    PageSummary,
    PublishResult,
    SpaceInfo,
)
from raise_cli.adapters.models.governance import (
    ArtifactLocator,
    CoreArtifactType,
)
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.adapters.models.pm import (
    BatchResult,
    Comment,
    CommentRef,
    FailureDetail,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)

__all__ = [
    # PM boundary models
    "IssueSpec",
    "IssueRef",
    "IssueDetail",
    "IssueSummary",
    "Comment",
    "CommentRef",
    "FailureDetail",
    "BatchResult",
    # Docs boundary models
    "PageContent",
    "PageSummary",
    "PublishResult",
    "SpaceInfo",
    # Governance models
    "CoreArtifactType",
    "ArtifactLocator",
    # Health (cross-cutting)
    "AdapterHealth",
]
