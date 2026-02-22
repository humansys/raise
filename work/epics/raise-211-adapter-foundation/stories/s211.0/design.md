---
story_id: "S211.0"
grounded_in: "Gemba of context/models.py (136 LOC), context/graph.py (301 LOC), 8 src/ consumers, 83 ConceptNode( in tests"
---

# Story Design: Open NodeType/EdgeType

## 1. What & Why

**Problem:** NodeType is a closed Literal with 18 values. Plugins cannot define new node types without modifying core.

**Value:** After this change, any string is a valid node type. Core types are guided by constants, not enforced by Literal.

## 2. Approach

Change `NodeType` and `EdgeType` from `Literal[...]` to `str`. Add `CoreNodeTypes` and `CoreEdgeTypes` classes with constants for the 18+11 current values. Keep `ConceptNode` and `ConceptEdge` model names unchanged.

**Components affected:**
- `context/models.py` — modify (Literal → str, add constants classes)
- `context/graph.py` — modify (type annotations: NodeType param → str)
- `context/__init__.py` — modify (export new constants)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `context/models.py` | `NodeType = Literal["pattern", ...]` (18 values), `EdgeType = Literal[...]` (11 values) | Both → `str`. Add `CoreNodeTypes`, `CoreEdgeTypes` classes. | `ConceptNode`, `ConceptEdge` models, all field names |
| `context/graph.py` | `get_concepts_by_type(node_type: NodeType)`, `get_neighbors(..., edge_types: list[EdgeType])` | Parameter types widen from Literal to str | All method behavior, NetworkX internals |
| `context/__init__.py` | Exports `ConceptNode, ConceptEdge, NodeType, EdgeType` | Add exports for `CoreNodeTypes, CoreEdgeTypes` | Existing exports |

## 4. Target Interfaces

```python
# context/models.py — changes only

NodeType = str  # was Literal[18 values]
EdgeType = str  # was Literal[11 values]

class CoreNodeTypes:
    """Constants for the 18 core node types."""
    PATTERN = "pattern"
    CALIBRATION = "calibration"
    SESSION = "session"
    PRINCIPLE = "principle"
    REQUIREMENT = "requirement"
    OUTCOME = "outcome"
    PROJECT = "project"
    EPIC = "epic"
    STORY = "story"
    SKILL = "skill"
    DECISION = "decision"
    GUARDRAIL = "guardrail"
    TERM = "term"
    COMPONENT = "component"
    MODULE = "module"
    ARCHITECTURE = "architecture"
    BOUNDED_CONTEXT = "bounded_context"
    LAYER = "layer"
    RELEASE = "release"

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
```

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Zero test changes:** All 1610 tests must pass without modification. The str type is a superset of the old Literal — all existing string values remain valid.
- **pyright strict:** No new type errors introduced.
