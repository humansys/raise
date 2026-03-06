"""Protocol contracts for raise-cli adapters.

Defines the typed interfaces that adapter implementations must satisfy.
All Protocols are ``@runtime_checkable`` for isinstance() checks.

**Sync vs Async:**
- ``AsyncProjectManagementAdapter`` / ``AsyncDocumentationTarget`` are the primary
  protocols. Concrete adapters (JiraAdapter, ConfluenceTarget) implement these.
- ``ProjectManagementAdapter`` / ``DocumentationTarget`` are the sync facades.
  CLI commands consume these. Use ``SyncPMAdapter`` / ``SyncDocsAdapter`` wrappers
  (from ``adapters.sync``) to bridge async adapters to sync consumption.

Architecture: ADR-033 (PM), ADR-034 (Governance)
Note: KnowledgeGraphBackend moved to raise_core.graph.backends.protocol (E275)
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from raise_cli.adapters.models import (
    AdapterHealth,
    ArtifactLocator,
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
from raise_core.graph.models import GraphNode

# ---------------------------------------------------------------------------
# Sync protocols (CLI consumption)
# ---------------------------------------------------------------------------


@runtime_checkable
class ProjectManagementAdapter(Protocol):
    """Sync PM adapter contract. CLI commands consume this.

    For concrete adapters, implement ``AsyncProjectManagementAdapter`` and wrap
    with ``SyncPMAdapter`` for CLI consumption.
    """

    # CRUD
    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...

    def get_issue(self, key: str) -> IssueDetail: ...

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...

    def transition_issue(self, key: str, status: str) -> IssueRef: ...

    # Batch
    def batch_transition(self, keys: list[str], status: str) -> BatchResult: ...

    # Relationships
    def link_to_parent(self, child_key: str, parent_key: str) -> None: ...

    def link_issues(self, source: str, target: str, link_type: str) -> None: ...

    # Comments
    def add_comment(self, key: str, body: str) -> CommentRef: ...

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]: ...

    # Query — query is adapter-specific (JQL for Jira, etc.)
    def search(self, query: str, limit: int = 50) -> list[IssueSummary]: ...

    # Health
    def health(self) -> AdapterHealth: ...


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
    """Sync docs target contract. CLI commands consume this.

    For concrete targets, implement ``AsyncDocumentationTarget`` and wrap
    with ``SyncDocsAdapter`` for CLI consumption.
    """

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult: ...

    def get_page(self, identifier: str) -> PageContent: ...

    def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...

    def health(self) -> AdapterHealth: ...


# ---------------------------------------------------------------------------
# Async protocols (adapter implementation target)
# ---------------------------------------------------------------------------


@runtime_checkable
class AsyncProjectManagementAdapter(Protocol):
    """Async PM adapter contract. Concrete adapters implement this.

    Consumed directly by async contexts (rai-server) or via ``SyncPMAdapter``
    wrapper for CLI.
    """

    # CRUD
    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...

    async def get_issue(self, key: str) -> IssueDetail: ...

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...

    async def transition_issue(self, key: str, status: str) -> IssueRef: ...

    # Batch
    async def batch_transition(self, keys: list[str], status: str) -> BatchResult: ...

    # Relationships
    async def link_to_parent(self, child_key: str, parent_key: str) -> None: ...

    async def link_issues(self, source: str, target: str, link_type: str) -> None: ...

    # Comments
    async def add_comment(self, key: str, body: str) -> CommentRef: ...

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]: ...

    # Query — query is adapter-specific (JQL for Jira, etc.)
    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]: ...

    # Health
    async def health(self) -> AdapterHealth: ...


@runtime_checkable
class AsyncDocumentationTarget(Protocol):
    """Async docs target contract. Concrete targets implement this."""

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult: ...

    async def get_page(self, identifier: str) -> PageContent: ...

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...

    async def health(self) -> AdapterHealth: ...
