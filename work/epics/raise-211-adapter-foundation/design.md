---
epic_id: "RAISE-211"
grounded_in: "Gemba of context/models.py, context/builder.py (1608 LOC), governance/extractor.py, governance/parsers/ (9 parsers), context/analyzers/protocol.py, context/graph.py, pyproject.toml, ADR-033 through ADR-037"
---

# Epic Design: Adapter Foundation

## Affected Surface (Gemba)

| Module/File | Current State | Changes | Stays |
|-------------|--------------|---------|-------|
| `context/models.py` (136 LOC) | `ConceptNode` flat model, `NodeType` Literal (18 types), `EdgeType` Literal (11 types) | NodeType → class hierarchy with auto-registration. ConceptNode becomes GraphNode base. EdgeType → str + constants. | Field names, serialization shape |
| `context/builder.py` (1608 LOC) | 7 `load_*` methods, all hardcoded. `GovernanceExtractor` instantiated directly. `PythonAnalyzer` hardcoded. | `load_governance()` → registry dispatch. `load_code_structure()` → registry dispatch. Other load methods remain (memory, work, skills, etc.) | `build()` orchestration pattern, project_root injection |
| `context/graph.py` (~300 LOC) | `UnifiedGraph` wraps NetworkX. `add_concept(ConceptNode)`, `save()`/`load()` via `node_link_data` | `add_concept()` accepts `GraphNode` (base class). Serialization handles discriminated hierarchy. | NetworkX core, query methods, BFS traversal |
| `governance/extractor.py` (324 LOC) | Orchestrates 9 parsers with hardcoded paths. Returns `list[Concept]` | Becomes `RaiSEDefaultSchema` implementing `GovernanceSchemaProvider` Protocol. Parsers called via registry. | Parser logic (refactored into Protocol implementations) |
| `governance/parsers/*.py` (9 files, ~1900 LOC) | Standalone functions: `extract_X(file_path) → list[Concept]` | Each wrapped as `GovernanceParser` implementation class. Return `list[GraphNode]` instead of `list[Concept]` | Regex parsing logic, extraction heuristics |
| `context/analyzers/protocol.py` (44 LOC) | `CodeAnalyzer` Protocol — existing pattern precedent | None — already follows target pattern | Everything |
| `pyproject.toml` | Only `[project.scripts]` entry point | Add 5 `[project.entry-points.*]` groups for adapter discovery | All existing config |

## Target Components

| Component | Responsibility | Key Interface | Consumes | Produces |
|-----------|---------------|---------------|----------|----------|
| `GraphNode` (base) | Base class for all graph nodes with auto-registration | `__init_subclass__(node_type=...)` | — | Node registry |
| `adapters/protocols.py` | Protocol contracts for PM, Governance, DocTarget | `ProjectManagementAdapter`, `GovernanceSchemaProvider`, `GovernanceParser`, `DocumentationTarget` | — | Contracts |
| `adapters/models.py` | Shared Pydantic models for adapter boundaries | `IssueSpec`, `IssueRef`, `ArtifactLocator`, `ArtifactType`, `PublishResult` | — | Models |
| `adapters/registry.py` | Entry point discovery | `get_pm_adapters()`, `get_governance_schemas()`, `get_governance_parsers()`, `get_graph_backends()` | `importlib.metadata` | Adapter instances |
| `governance/default_schema.py` | Built-in `GovernanceSchemaProvider` — the `.raise/` structure | `RaiSEDefaultSchema.locate_all()` | Project filesystem | `list[ArtifactLocator]` |
| `governance/parsers/*.py` (wrapped) | Built-in `GovernanceParser` implementations | `BacklogParser.parse(locator)` | `ArtifactLocator` | `list[GraphNode]` |
| `graph/filesystem_backend.py` | Built-in `KnowledgeGraphBackend` — current JSONL/JSON persistence | `FilesystemGraphBackend.persist(graph)` | `UnifiedGraph` | `.raise/rai/memory/index.json` |
| `tier/context.py` | Tier detection and capability registry | `TierContext.has(capability)`, `TierContext.from_manifest()` | `.raise/manifest.yaml` | Capability booleans |

## Key Contracts

### GraphNode Base (S211.0)

```python
from __future__ import annotations
from typing import Any, ClassVar
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    """Base class for all knowledge graph nodes.

    Subclasses auto-register via __init_subclass__.
    Pattern: pytest Node + Airflow BaseOperator + Kedro AbstractDataset.
    """
    _registry: ClassVar[dict[str, type[GraphNode]]] = {}

    id: str
    content: str
    source_file: str | None = None
    created: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __init_subclass__(cls, node_type: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if node_type is not None:
            cls.__node_type__ = node_type
            GraphNode._registry[node_type] = cls

    @classmethod
    def resolve(cls, node_type: str) -> type[GraphNode]:
        """Resolve a node_type string to its registered class."""
        return cls._registry[node_type]

    @classmethod
    def registered_types(cls) -> dict[str, type[GraphNode]]:
        """All registered node type mappings."""
        return dict(cls._registry)

# Core types (18 — one class per current Literal value)
class PatternNode(GraphNode, node_type="pattern"): ...
class EpicNode(GraphNode, node_type="epic"): ...
class StoryNode(GraphNode, node_type="story"): ...
class DecisionNode(GraphNode, node_type="decision"): ...
# ... (all 18)

# Backward compat alias — removed after full migration
ConceptNode = GraphNode
```

### GraphEdge (S211.0)

```python
EdgeType = str  # open for plugins

class CoreEdgeTypes:
    LEARNED_FROM = "learned_from"
    GOVERNED_BY = "governed_by"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    # ... (all 11 current types)

class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)

# Backward compat alias
ConceptEdge = GraphEdge
```

### Adapter Protocols (S211.1)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProjectManagementAdapter(Protocol):
    """ADR-033: PM adapter contract."""
    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    def get_issue(self, ref: IssueRef) -> Issue: ...
    def update_issue(self, ref: IssueRef, fields: dict[str, Any]) -> IssueRef: ...
    def transition_issue(self, ref: IssueRef, transition: str) -> IssueRef: ...

@runtime_checkable
class GovernanceSchemaProvider(Protocol):
    """ADR-034: Declares what artifact types exist and where to find them."""
    def list_artifact_types(self) -> list[ArtifactType]: ...
    def locate(self, artifact_type: ArtifactType) -> list[ArtifactLocator]: ...

@runtime_checkable
class GovernanceParser(Protocol):
    """ADR-034: Parses a governance artifact into graph nodes."""
    def can_parse(self, locator: ArtifactLocator) -> bool: ...
    def parse(self, locator: ArtifactLocator) -> list[GraphNode]: ...

@runtime_checkable
class DocumentationTarget(Protocol):
    """ADR-034: Publishes documentation to a target."""
    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...
    def publish(self, doc_type: str, content: str, metadata: dict[str, Any]) -> PublishResult: ...

@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    """ADR-036: Graph storage abstraction."""
    def persist(self, graph: UnifiedGraph) -> None: ...
    def load(self, path: Path) -> UnifiedGraph: ...
    def health(self) -> BackendHealth: ...
```

### Entry Point Registry (S211.2)

```python
from importlib.metadata import entry_points

# Entry point group names
PM_GROUP = "rai.adapters.pm"
SCHEMA_GROUP = "rai.governance.schemas"
PARSER_GROUP = "rai.governance.parsers"
DOC_TARGET_GROUP = "rai.docs.targets"
GRAPH_BACKEND_GROUP = "rai.graph.backends"

def get_pm_adapters() -> list[ProjectManagementAdapter]: ...
def get_governance_schemas() -> list[GovernanceSchemaProvider]: ...
def get_governance_parsers() -> list[GovernanceParser]: ...
def get_doc_targets() -> list[DocumentationTarget]: ...
def get_graph_backends() -> list[KnowledgeGraphBackend]: ...
```

### TierContext (S211.5)

```python
from dataclasses import dataclass, field
from enum import StrEnum

class Capability(StrEnum):
    SHARED_MEMORY = "shared_memory"
    SEMANTIC_SEARCH = "semantic_search"
    TEAM_AWARENESS = "team_awareness"
    JIRA_INTEGRATION = "jira_integration"
    DOCS_PUBLISH = "docs_publish"
    ORG_GOVERNANCE = "org_governance"
    AUDIT_LOGGING = "audit_logging"

class TierLevel(StrEnum):
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class TierContext:
    tier: TierLevel = TierLevel.COMMUNITY
    backend_url: str | None = None
    capabilities: set[Capability] = field(default_factory=set)

    def has(self, capability: Capability) -> bool: ...
    def require_or_suggest(self, capability: Capability) -> None: ...

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> TierContext: ...

    @classmethod
    def community(cls) -> TierContext: ...
```

## Migration Path

### Backward Compatibility Strategy
- **ConceptNode** becomes alias for `GraphNode` during migration. Removed after all consumers updated.
- **ConceptEdge** becomes alias for `GraphEdge`. Same lifecycle.
- **NodeType Literal** removed. Code that does `node.type == "epic"` still works (string comparison). Code that type-checks against `Literal` breaks — must update to `isinstance(node, EpicNode)` or `node.__node_type__ == "epic"`.
- **Serialized graph**: No migration layer. Users run `rai memory build` after upgrade. Graph is derived from sources, not authoritative.

### Consumer Changes
- `UnifiedGraphBuilder.build()`: Returns graph with `GraphNode` subclass instances instead of flat `ConceptNode`.
- `UnifiedGraph.add_concept()`: Accepts `GraphNode` (base class).
- `GovernanceExtractor`: Becomes `RaiSEDefaultSchema`. Consumers that import it directly must update.
- All governance parsers: Return `list[GraphNode]` subclass instances instead of `list[Concept]`.
- Tests: ~1610 tests, many reference `ConceptNode` — alias covers initial migration, then batch update.

## What Does NOT Change

- **NetworkX core** — `UnifiedGraph` still wraps `networkx.MultiDiGraph`
- **Memory JSONL format** — patterns.jsonl, calibration.jsonl unchanged
- **CLI command surface** — `rai memory build`, `rai memory query` unchanged (new: `rai adapters`)
- **Governance markdown format** — all `.md` files parsed identically
- **Discovery module** — `CodeAnalyzer` Protocol stays, analyzers stay in-place
- **Session module** — no changes
- **Skill framework** — no changes
