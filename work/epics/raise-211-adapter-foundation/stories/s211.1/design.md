---
story_id: "S211.1"
title: "Protocol contracts"
epic_ref: "RAISE-211"
grounded_in: "Gemba of context/models.py (S211.0 output), context/analyzers/protocol.py (CodeAnalyzer precedent), governance/extractor.py, governance/models.py, governance/parsers/*.py, epic design.md §Adapter Protocols"
---

# Design: Protocol Contracts

## 1. What & Why

**Problem:** raise-cli extensions (PM tools, governance schemas, graph backends) have no typed contracts. `GovernanceExtractor` hardcodes 9 parsers via direct imports. No interface exists for a plugin to implement.

**Value:** Typed Protocol contracts + Pydantic boundary models let any Python package implement an adapter. pyright validates conformance statically; `isinstance()` validates at runtime. Foundation for raise-pro as installable plugin, not fork.

## 2. Approach

Create `src/rai_cli/adapters/` module with three files:

| File | Responsibility | Creates |
|------|---------------|---------|
| `protocols.py` | 5 `@runtime_checkable` Protocol classes | Contracts |
| `models.py` | Pydantic models for adapter boundaries | Data types |
| `__init__.py` | Public API re-exports | Surface |

**No implementations.** Pure contracts only. Implementations come in S211.2+ (registry), S211.3 (governance refactor), S211.4 (graph backend).

**Dependency direction:** `adapters/` is a leaf module. Uses `TYPE_CHECKING` for `UnifiedGraph` reference in `KnowledgeGraphBackend` to avoid runtime dependency on `context.graph`.

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `context/models.py` | `GraphNode` base + 18 subclasses | Nothing — Protocols consume it | Everything |
| `context/analyzers/protocol.py` | `CodeAnalyzer` Protocol (precedent) | Nothing — pattern to follow | Everything |
| `governance/extractor.py` | `GovernanceExtractor`, 9 hardcoded imports | Nothing in S211.1 (S211.3 refactors) | Everything |
| `governance/models.py` | `Concept`, `ConceptType`, `ExtractionResult` | Nothing — legacy coexists | Everything |
| `governance/parsers/*.py` | `extract_*()` → `list[Concept]` | Nothing in S211.1 (S211.3 wraps) | Everything |
| **`adapters/`** | **Does not exist** | **CREATE** | — |

**Precedent from Gemba:** `CodeAnalyzer` in `context/analyzers/protocol.py` uses exactly this pattern: `@runtime_checkable`, methods with type hints, docstrings. We replicate it.

## 4. Target Interfaces

### protocols.py — 5 Protocol Classes

```python
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from rai_cli.adapters.models import (
    ArtifactLocator,
    BackendHealth,
    IssueRef,
    IssueSpec,
    PublishResult,
)
from rai_cli.context.models import GraphNode

if TYPE_CHECKING:
    from rai_cli.context.graph import UnifiedGraph


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


@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    """ADR-036: Graph storage abstraction.

    Implementations: FilesystemGraphBackend (S211.4), SupabaseBackend (raise-pro).
    """

    def persist(self, graph: UnifiedGraph) -> None: ...
    def load(self, path: Path) -> UnifiedGraph: ...
    def health(self) -> BackendHealth: ...
```

### models.py — Pydantic Boundary Models

```python
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CoreArtifactType(StrEnum):
    """Core governance artifact types. Plugins use arbitrary strings."""

    BACKLOG = "backlog"
    ADR = "adr"
    CONSTITUTION = "constitution"
    PRD = "prd"
    VISION = "vision"
    GUARDRAILS = "guardrails"
    GLOSSARY = "glossary"
    ROADMAP = "roadmap"
    EPIC_SCOPE = "epic_scope"


class ArtifactLocator(BaseModel):
    """Points to a governance artifact for parsing."""

    path: str = Field(..., description="Relative path from project root")
    artifact_type: str = Field(..., description="Artifact type (CoreArtifactType or custom str)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Type-specific context")


class IssueSpec(BaseModel):
    """Specification for creating a PM issue."""

    summary: str = Field(..., description="Issue title")
    description: str = Field(default="", description="Issue body (markdown)")
    issue_type: str = Field(default="Task", description="Issue type name")
    labels: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict, description="PM-specific fields")


class IssueRef(BaseModel):
    """Reference to an existing PM issue."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    url: str = Field(default="", description="Web URL to the issue")
    metadata: dict[str, Any] = Field(default_factory=dict)


class PublishResult(BaseModel):
    """Result of publishing documentation."""

    success: bool = Field(..., description="Whether publish succeeded")
    url: str = Field(default="", description="URL of published content")
    message: str = Field(default="", description="Status or error message")


class BackendHealth(BaseModel):
    """Health check result for a graph backend."""

    status: str = Field(..., description="'healthy', 'degraded', or 'unavailable'")
    message: str = Field(default="", description="Human-readable status detail")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Backend-specific diagnostics")
```

### __init__.py — Public API

```python
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
```

### Integration Points

- `adapters.models` imports nothing from raise-cli (leaf)
- `adapters.protocols` imports `GraphNode` from `context.models` (stable, S211.0)
- `adapters.protocols` uses `TYPE_CHECKING` for `UnifiedGraph` (no runtime dep on `context.graph`)
- `GovernanceSchemaProvider.list_artifact_types()` returns `list[str]`, not `list[CoreArtifactType]` — plugins aren't restricted to the enum
- `GovernanceParser.parse()` returns `list[GraphNode]` — target architecture, not legacy `Concept`

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **MUST:** pyright strict clean — zero errors on new module
- **MUST:** All Protocols `@runtime_checkable` — isinstance checks work
- **MUST:** All models inherit `BaseModel` (Pydantic) — guardrail-must-arch-002
- **MUST NOT:** Import from `governance/` — adapters is upstream of governance in the dependency graph
- **MUST NOT:** Create any concrete adapter implementation — contracts only
