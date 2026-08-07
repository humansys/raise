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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from raise_cli.adapters.models import (
    AdapterHealth,
    ArtifactLocator,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    CustomField,
    FieldDefinition,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    IssueTypeInfo,
    LinkTypeDefinition,
    PageContent,
    PageSummary,
    ProjectVersion,
    PublishResult,
    WorkflowState,
)
from raise_cli.adapters.models.docs import AttachmentSummary, CommentSummary
from raise_cli.adapters.models.sync import SyncReport

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

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult: ...

    # Relationships
    def link_to_parent(self, child_key: str, parent_key: str) -> bool: ...

    def link_issues(self, source: str, target: str, link_type: str) -> bool: ...

    def remove_link(self, link_id: str) -> None: ...

    # Comments
    def add_comment(self, key: str, body: str) -> CommentRef: ...

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]: ...

    # Query — query is adapter-specific (JQL for Jira, etc.)
    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]: ...

    # Health
    def health(self) -> AdapterHealth: ...

    # Discovery
    def discover_fields(self, project_key: str) -> list[FieldDefinition]: ...

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]: ...

    def discover_link_types(self) -> list[LinkTypeDefinition]: ...

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]: ...

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]: ...

    # Attachments (S2503.7)
    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef: ...

    def get_attachments(self, key: str) -> list[AttachmentDetail]: ...

    def download_attachment(self, attachment_id: str) -> bytes: ...


@runtime_checkable
class ProjectVersionManagementAdapter(Protocol):
    """Optional PM adapter capability for project release/fixVersion management."""

    def list_versions(self, project_key: str) -> list[ProjectVersion]: ...

    def create_version(self, project_key: str, name: str) -> ProjectVersion: ...


@runtime_checkable
class GovernanceSchemaProvider(Protocol):
    """ADR-034: Declares what artifact types exist and where to find them.

    Implementations: RaiSEDefaultSchema (built-in), OrgSchema (raise-pro).
    """

    def list_artifact_types(self) -> list[str]: ...

    def locate(self, artifact_type: str) -> list[ArtifactLocator]: ...


@runtime_checkable
class DocumentationTarget(Protocol):
    """Sync docs target contract. CLI commands consume this.

    For concrete targets, implement ``AsyncDocumentationTarget`` and wrap
    with ``SyncDocsAdapter`` for CLI consumption.
    """

    def can_publish(self, doc_type: str | None, metadata: dict[str, Any]) -> bool: ...

    def publish(
        self, doc_type: str | None, content: str, metadata: dict[str, Any]
    ) -> PublishResult: ...

    def get_page(self, identifier: str) -> PageContent: ...

    def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...

    def health(self) -> AdapterHealth: ...

    def add_label(self, page_id: str, name: str) -> None: ...

    def get_labels(self, page_id: str) -> list[str]: ...

    def get_page_children(self, page_id: str) -> list[PageSummary]: ...

    def delete_page(self, page_id: str) -> None: ...

    def add_comment(self, page_id: str, body: str) -> None: ...

    def get_comments(self, page_id: str) -> list[CommentSummary]: ...

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str: ...

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]: ...

    def embed_attachment(self, page_id: str, filename: str) -> PageContent: ...


# ---------------------------------------------------------------------------
# Async protocols (adapter implementation target)
# ---------------------------------------------------------------------------


@runtime_checkable
class AsyncProjectManagementAdapter(Protocol):
    """Async PM adapter contract. Concrete adapters implement this.

    Consumed directly by async contexts (rai-server) or via ``SyncPMAdapter``
    wrapper for CLI.

    Content convention (BASE-048 / S2503.4):
    All ``str`` parameters and return values that carry issue/comment content
    are Markdown. The adapter layer serializes (write) and deserializes (read).
    Callers must not send ADF dicts or raw plain text — pass Markdown, get Markdown.
    """

    # CRUD
    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create an issue. ``issue.description`` is Markdown."""
        ...

    async def get_issue(self, key: str) -> IssueDetail:
        """Return issue detail. ``IssueDetail.description`` is Markdown."""
        ...

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...

    async def transition_issue(self, key: str, status: str) -> IssueRef: ...

    # Batch
    async def batch_transition(self, keys: list[str], status: str) -> BatchResult: ...

    async def batch_create(self, issues: list[IssueSpec]) -> BatchResult: ...

    # Relationships
    async def link_to_parent(self, child_key: str, parent_key: str) -> bool: ...

    async def link_issues(self, source: str, target: str, link_type: str) -> bool: ...

    async def remove_link(self, link_id: str) -> None: ...

    # Comments
    async def add_comment(self, key: str, body: str) -> CommentRef:
        """Add a comment. ``body`` is Markdown."""
        ...

    async def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Return comments. ``Comment.body`` is Markdown."""
        ...

    # Query — query is adapter-specific (JQL for Jira, etc.)
    async def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]: ...

    # Health
    async def health(self) -> AdapterHealth: ...

    # Discovery
    async def discover_fields(self, project_key: str) -> list[FieldDefinition]: ...

    async def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]: ...

    async def discover_link_types(self) -> list[LinkTypeDefinition]: ...

    async def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]: ...

    async def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]: ...

    # Attachments (S2503.7)
    async def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef: ...

    async def get_attachments(self, key: str) -> list[AttachmentDetail]: ...

    async def download_attachment(self, attachment_id: str) -> bytes: ...


@runtime_checkable
class AsyncProjectVersionManagementAdapter(Protocol):
    """Optional async PM adapter capability for project release/fixVersion management."""

    async def list_versions(self, project_key: str) -> list[ProjectVersion]: ...

    async def create_version(self, project_key: str, name: str) -> ProjectVersion: ...


@runtime_checkable
class AsyncDocumentationTarget(Protocol):
    """Async docs target contract. Concrete targets implement this."""

    async def can_publish(
        self, doc_type: str | None, metadata: dict[str, Any]
    ) -> bool: ...

    async def publish(
        self, doc_type: str | None, content: str, metadata: dict[str, Any]
    ) -> PublishResult: ...

    async def get_page(self, identifier: str) -> PageContent: ...

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...

    async def health(self) -> AdapterHealth: ...

    async def add_label(self, page_id: str, name: str) -> None: ...

    async def get_labels(self, page_id: str) -> list[str]: ...

    async def get_page_children(self, page_id: str) -> list[PageSummary]: ...

    async def delete_page(self, page_id: str) -> None: ...

    async def add_comment(self, page_id: str, body: str) -> None: ...

    async def get_comments(self, page_id: str) -> list[CommentSummary]: ...

    async def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str: ...

    async def get_attachments(self, page_id: str) -> list[AttachmentSummary]: ...

    async def embed_attachment(self, page_id: str, filename: str) -> PageContent: ...


# ---------------------------------------------------------------------------
# Optional capability protocol — SyncVerifiable
# ---------------------------------------------------------------------------


@runtime_checkable
class SyncVerifiable(Protocol):
    """Adapter that can verify local→remote parity via real GET requests.

    Implemented by composite adapters that have a local ledger + remote access.
    The gate does isinstance(adapter, SyncVerifiable) and skips if not applicable.

    is_server_first exposes _server_first publicly so discovery can filter
    standalone adapters without accessing a private attribute (QR-C1).
    """

    @property
    def is_server_first(self) -> bool: ...

    def verify_sync(self, keys: frozenset[str] | None = None) -> SyncReport:
        """Verify entries against remote.

        keys=None: verify all ledger entries (--all mode).
        keys: verify only entries where local_key or remote_key is in keys.
        Returns SyncReport with entries=() if nothing is registered.
        """
        ...


# ---------------------------------------------------------------------------
# SCM adapter protocol (S10724.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScmPrResult:
    """Structured PR/MR result from SCM operations."""

    number: int
    title: str
    state: str
    url: str
    source_branch: str
    target_branch: str
    author: str


@dataclass(frozen=True)
class ScmRepoInfo:
    """Repository summary from SCM provider."""

    provider_repo_id: str
    name: str
    full_name: str
    visibility: str = "private"
    default_branch: str = "main"


@runtime_checkable
class ScmAdapter(Protocol):
    """SCM adapter for PR/MR and repo operations via server proxy."""

    async def create_pr(
        self,
        *,
        provider: str,
        repo_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = "",
    ) -> ScmPrResult: ...

    async def get_pr(
        self,
        *,
        provider: str,
        repo_id: str,
        pr_number: int,
    ) -> ScmPrResult: ...

    async def list_repos(
        self,
        *,
        provider: str,
        search: str = "",
        limit: int = 50,
    ) -> list[ScmRepoInfo]: ...

    async def list_branches(
        self,
        *,
        provider: str,
        repo_id: str,
    ) -> list[str]: ...

    async def disconnect(
        self,
        *,
        provider: str,
    ) -> bool: ...
