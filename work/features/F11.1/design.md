# Design Spec: F11.1 Unified Graph Schema

## Overview

| Field | Value |
|-------|-------|
| Feature | F11.1 Unified Graph Schema |
| Epic | E11 Unified Context Architecture |
| Size | S (2 SP) |
| Status | Design |
| ADR | ADR-019 Unified Context Graph Architecture |

## Problem Statement

Rai's context is fragmented across three separate graph systems (governance, memory, work) with no unified schema. Skills cannot query a single context source, leading to re-discovery of patterns and inconsistent context availability.

## Solution

Create the foundational schema for a unified context graph:

1. **ConceptNode model** — Pydantic model for all node types
2. **ConceptEdge model** — Pydantic model for all relationship types
3. **UnifiedGraph class** — NetworkX MultiDiGraph wrapper with typed operations
4. **Serialization** — JSON via `node_link_data`/`node_link_graph`

## Schema Design (from ADR-019)

### Node Types

```python
NodeType = Literal[
    "pattern",      # PAT-* — learned patterns
    "calibration",  # CAL-* — velocity data
    "session",      # SES-* — session history
    "principle",    # §N — constitution principles
    "requirement",  # RF-* — PRD requirements
    "outcome",      # OUT-* — vision outcomes
    "epic",         # E* — epic scopes
    "feature",      # F*.* — feature work
    "skill",        # /name — skill metadata
]
```

### Edge Types

```python
EdgeType = Literal[
    "learned_from",   # pattern → session
    "governed_by",    # requirement → principle
    "applies_to",     # pattern → skill
    "needs_context",  # skill → concept types
    "implements",     # feature → requirement
    "part_of",        # feature → epic
    "related_to",     # generic semantic relationship
]
```

### ConceptNode Model

```python
class ConceptNode(BaseModel):
    id: str                      # PAT-001, §2, F11.1, /feature-plan
    type: NodeType               # Node type
    content: str                 # Main text/description
    source_file: str | None      # Where it came from
    created: str                 # ISO timestamp
    metadata: dict[str, Any]     # Type-specific attributes
```

### ConceptEdge Model

```python
class ConceptEdge(BaseModel):
    source: str                  # Source node ID
    target: str                  # Target node ID
    type: EdgeType               # Relationship type
    weight: float = 1.0          # Edge weight
    metadata: dict[str, Any]     # Additional metadata
```

### UnifiedGraph Class

```python
class UnifiedGraph:
    """NetworkX-based unified context graph."""

    def __init__(self) -> None
    def add_concept(self, node: ConceptNode) -> None
    def add_relationship(self, edge: ConceptEdge) -> None
    def get_concept(self, concept_id: str) -> ConceptNode | None
    def get_concepts_by_type(self, node_type: NodeType) -> list[ConceptNode]
    def get_neighbors(self, concept_id: str, depth: int = 1) -> list[ConceptNode]
    def save(self, path: Path) -> None
    @classmethod
    def load(cls, path: Path) -> UnifiedGraph

    # Properties
    @property
    def node_count(self) -> int
    @property
    def edge_count(self) -> int
```

## File Structure

```
src/raise_cli/context/
├── __init__.py          # Module exports
├── models.py            # ConceptNode, ConceptEdge, NodeType, EdgeType
└── graph.py             # UnifiedGraph class
```

## Acceptance Criteria

- [ ] `ConceptNode` model with all 9 node types
- [ ] `ConceptEdge` model with all 7 edge types
- [ ] `UnifiedGraph` class wrapping NetworkX MultiDiGraph
- [ ] JSON serialization via `node_link_data`/`node_link_graph`
- [ ] Unit tests with >90% coverage
- [ ] All quality checks pass (ruff, pyright, bandit)

## Out of Scope

- Graph building (F11.2)
- Query operations (F11.3)
- Vector embeddings (post-F&F)
- Graph validation rules (SHOULD, not MUST)

## Dependencies

- **Upstream**: ADR-019 (architecture decision) ✓
- **Downstream**: F11.2 Builder, F11.3 Query depend on this schema

## References

- ADR-019: `dev/decisions/adr-019-unified-context-graph.md`
- E11 Scope: `dev/epic-e11-scope.md`
- Existing patterns: `src/raise_cli/governance/graph/models.py`, `src/raise_cli/memory/models.py`

---

*Design created: 2026-02-03*
*Architecture: ADR-019*
