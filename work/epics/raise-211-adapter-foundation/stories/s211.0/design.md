---
story_id: "S211.0"
grounded_in: "Gemba of context/models.py (136 LOC), context/graph.py (301 LOC), 8 src/ consumers, 83 ConceptNode( in tests, 32 ConceptEdge( in tests"
---

# Story Design: GraphNode class hierarchy with auto-registration

## 1. What & Why

**Problem:** NodeType is a closed Literal with 18 values. Plugins cannot define new node types or add typed fields without modifying core.

**Value:** After this change, any Python package can define `class JiraSprintNode(GraphNode, node_type="jira.sprint"): sprint_id: str` — auto-registered, typed, validated. The codebase demonstrates the extensibility pattern that RaiSE's adapter architecture is built on.

## 2. Approach

Three-layer implementation following the C+E+D pattern (pytest/Airflow/Kedro):

1. **GraphNode base** with `__init_subclass__` auto-registration + `model_validator` for auto-default type field
2. **18 core subclasses** — one per current Literal value, documented as extension points
3. **Deserialization** in graph.py — registry lookup with graceful fallback for unknown types

ConceptNode/ConceptEdge become aliases. EdgeType becomes str + CoreEdgeTypes constants.

**Components affected:**
- `context/models.py` — modify (major: hierarchy + 18 subclasses + constants)
- `context/graph.py` — modify (deserialization with registry lookup)
- `context/__init__.py` — modify (export new types)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `context/models.py` | `NodeType = Literal[18 values]`, `ConceptNode(BaseModel)` with `type: NodeType`, `ConceptEdge(BaseModel)` with `type: EdgeType` | GraphNode base with `__init_subclass__`, 18 subclasses, `model_validator` for auto-type. EdgeType → str + CoreEdgeTypes. ConceptNode = GraphNode alias. | Field names (id, type, content, source_file, created, metadata), token_estimate property |
| `context/graph.py` | `get_concept()` → `ConceptNode.model_validate(data)`, `get_concepts_by_type(node_type: NodeType)`, `iter_concepts()` → yields `ConceptNode` | Deserialization uses `GraphNode._registry.get(type)` → correct subclass. Fallback to GraphNode base for unknown. Type annotations updated. | NetworkX core, save() format (node_link_data), all query logic |
| `context/__init__.py` | Exports `ConceptNode, ConceptEdge, NodeType, EdgeType` | Add exports for `GraphNode, GraphEdge, CoreNodeTypes, CoreEdgeTypes` | Existing exports (aliases) |

## 4. Target Interfaces

### GraphNode Base + Subclasses (context/models.py)

```python
from __future__ import annotations
from typing import Any, ClassVar
from pydantic import BaseModel, Field, model_validator

class GraphNode(BaseModel):
    """Base class for all knowledge graph nodes. Auto-registers subclasses.

    Pattern: pytest Node + Airflow BaseOperator + Kedro AbstractDataset.
    Subclasses define node_type and optionally add typed fields.
    """
    _registry: ClassVar[dict[str, type[GraphNode]]] = {}

    id: str = Field(..., description="Unique identifier (e.g., 'PAT-001', '§2')")
    type: str = Field(default="", description="Node type (auto-set by subclass)")
    content: str = Field(..., description="Main text content or description")
    source_file: str | None = Field(default=None, description="Path to source file")
    created: str = Field(..., description="ISO timestamp when created")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Type-specific attributes")

    def __init_subclass__(cls, node_type: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if node_type is not None:
            cls.__node_type__ = node_type
            GraphNode._registry[node_type] = cls

    @model_validator(mode="before")
    @classmethod
    def _set_default_type(cls, data: Any) -> Any:
        """Auto-set type field from subclass registration."""
        if isinstance(data, dict) and hasattr(cls, "__node_type__"):
            data.setdefault("type", cls.__node_type__)
        return data

    @classmethod
    def resolve(cls, node_type: str) -> type[GraphNode]:
        """Resolve a node_type string to its registered class."""
        return cls._registry[node_type]

    @classmethod
    def registered_types(cls) -> dict[str, type[GraphNode]]:
        """All registered node type mappings."""
        return dict(cls._registry)

    @property
    def token_estimate(self) -> int:
        """Estimate tokens for this concept."""
        return len(self.content) // 4

# --- Core node types (18) — documented extension points ---

class PatternNode(GraphNode, node_type="pattern"):
    """Learned patterns from memory. Extension: confidence scores, decay metadata."""
    ...

class CalibrationNode(GraphNode, node_type="calibration"):
    """Velocity/estimation data. Extension: per-team calibration fields."""
    ...

class SessionNode(GraphNode, node_type="session"):
    """Session history records. Extension: agent-specific session data."""
    ...

class PrincipleNode(GraphNode, node_type="principle"):
    """Constitution principles. Extension: org-level principle overrides."""
    ...

class RequirementNode(GraphNode, node_type="requirement"):
    """PRD requirements. Extension: priority, stakeholder fields."""
    ...

class OutcomeNode(GraphNode, node_type="outcome"):
    """Vision outcomes. Extension: OKR linkage fields."""
    ...

class ProjectNode(GraphNode, node_type="project"):
    """Project definitions. Extension: multi-repo project metadata."""
    ...

class EpicNode(GraphNode, node_type="epic"):
    """Epic scopes. Extension: Jira epic fields (key, board, sprint)."""
    ...

class StoryNode(GraphNode, node_type="story"):
    """Story work items. Extension: PM tool fields (assignee, status)."""
    ...

class SkillNode(GraphNode, node_type="skill"):
    """Skill metadata. Extension: registry, versioning, ownership."""
    ...

class DecisionNode(GraphNode, node_type="decision"):
    """Architecture decisions. Extension: review status, superseded-by."""
    ...

class GuardrailNode(GraphNode, node_type="guardrail"):
    """Code standards. Extension: enforcement level, exceptions."""
    ...

class TermNode(GraphNode, node_type="term"):
    """Glossary definitions. Extension: translations, domain scope."""
    ...

class ComponentNode(GraphNode, node_type="component"):
    """Discovered code components. Extension: language-specific metadata."""
    ...

class ModuleNode(GraphNode, node_type="module"):
    """Architecture module knowledge. Extension: dependency metrics."""
    ...

class ArchitectureNode(GraphNode, node_type="architecture"):
    """Architecture docs. Extension: diagram links, review dates."""
    ...

class BoundedContextNode(GraphNode, node_type="bounded_context"):
    """DDD bounded contexts. Extension: team ownership, API surface."""
    ...

class LayerNode(GraphNode, node_type="layer"):
    """Architectural layers. Extension: deployment mapping."""
    ...

class ReleaseNode(GraphNode, node_type="release"):
    """Release milestones. Extension: changelog, artifact URLs."""
    ...

# --- Backward compat aliases ---
ConceptNode = GraphNode
NodeType = str  # was Literal — now open

# --- Edges (open type, no hierarchy needed — edges have no per-type fields) ---
EdgeType = str  # was Literal — now open

class CoreEdgeTypes:
    """Constants for the 11 core edge types."""
    LEARNED_FROM = "learned_from"
    GOVERNED_BY = "governed_by"
    APPLIES_TO = "applies_to"
    NEEDS_CONTEXT = "needs_context"
    IMPLEMENTS = "implements"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    BELONGS_TO = "belongs_to"
    IN_LAYER = "in_layer"
    CONSTRAINED_BY = "constrained_by"

class GraphEdge(BaseModel):
    """An edge in the unified context graph. Open type system."""
    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)

ConceptEdge = GraphEdge
```

### Deserialization (context/graph.py — changes only)

```python
def _reconstruct_node(self, node_id: str, data: dict[str, Any]) -> GraphNode:
    """Reconstruct a typed GraphNode from serialized dict."""
    data["id"] = node_id
    node_type = data.get("type", "")
    cls = GraphNode._registry.get(node_type)
    if cls:
        return cls.model_validate(data)
    logger.warning(
        "Node type '%s' not registered (missing plugin?). "
        "Run 'rai memory build' to regenerate graph.",
        node_type,
    )
    return GraphNode.model_validate(data)

# Used by: get_concept(), get_concepts_by_type(), iter_concepts()
```

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Zero test changes:** All 1610 tests pass via ConceptNode alias
- **pyright strict:** No new type errors
- **Edges stay flat:** No hierarchy for edges — they have no per-type fields. str + CoreEdgeTypes is sufficient.

### Design Decision: Why hierarchy for nodes but not edges?

Nodes benefit from hierarchy because plugins WILL add per-type fields (JiraSprintNode.sprint_id). Edges don't — an edge is always (source, target, type, weight, metadata). No plugin needs typed edge fields. Applying hierarchy to edges would be pure ceremony.
