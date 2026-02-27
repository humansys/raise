"""Protocol contracts for raise-cli adapters.

Defines the typed interfaces that adapter implementations must satisfy.
All Protocols are ``@runtime_checkable`` for isinstance() checks.

Architecture: ADR-033 (PM), ADR-034 (Governance)
Note: KnowledgeGraphBackend moved to rai_core.graph.backends.protocol (E275)
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from rai_cli.adapters.models import (
    ArtifactLocator,
    IssueRef,
    IssueSpec,
    PublishResult,
)
from rai_core.graph.models import GraphNode


@runtime_checkable
class ProjectManagementAdapter(Protocol):
    """ADR-033: PM adapter contract.

    Implementations: JiraAdapter (raise-pro), GitLabAdapter (future).
    """

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...

    def get_issue(self, ref: IssueRef) -> IssueRef: ...

    def update_issue(self, ref: IssueRef, fields: dict[str, Any]) -> IssueRef: ...

    def transition_issue(self, ref: IssueRef, transition: str) -> IssueRef: ...


@runtime_checkable
class GovernanceSchemaProvider(Protocol):
    """ADR-034: Declares what artifact types exist and where to find them.

    Implementations: RaiSEDefaultSchema (built-in), OrgSchema (raise-pro).
    """

    def list_artifact_types(self) -> list[str]: ...

    def locate(self, artifact_type: str) -> list[ArtifactLocator]: ...


@runtime_checkable
class GovernanceParser(Protocol):
    """ADR-034: Parses a governance artifact into graph nodes.

    Implementations: BacklogParser, AdrParser, etc. (S211.3 wraps existing).
    """

    def can_parse(self, locator: ArtifactLocator) -> bool: ...

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]: ...


@runtime_checkable
class DocumentationTarget(Protocol):
    """ADR-034: Publishes documentation to a target.

    Implementations: ConfluenceTarget (raise-pro), StaticSiteTarget (future).
    """

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult: ...
