---
feature_id: "F2.2"
title: "Graph Builder"
epic: "E2: Governance Toolkit"
story_points: 2
complexity: "moderate"
status: "design"
created: "2026-01-31"
---

# F2.2: Graph Builder

## What & Why

**Problem**: RaiSE needs to build a concept-level directed graph from extracted concepts (F2.1 output) to enable semantic queries and relationship traversal for Minimum Viable Context (MVC) generation.

**Value**: Enables MVC queries via graph traversal (BFS), reducing context retrieval time and supporting deterministic "why this concept?" explanations through relationship paths.

## Approach

Build an in-memory directed graph from extracted concepts with relationship inference based on governance patterns:
- **Nodes**: Concepts from F2.1 (requirements, outcomes, principles)
- **Edges**: Relationships (`implements`, `governed_by`, `depends_on`, `related_to`)
- **Persistence**: Serialize to JSON for reuse across sessions
- **Traversal**: BFS utilities for MVC queries (F2.3)

**Components affected**:
- CREATE: `src/raise_cli/governance/graph/` (new submodule)
  - `models.py` - Graph data structures (`ConceptGraph`, `Relationship`)
  - `builder.py` - Graph construction from concepts
  - `relationships.py` - Relationship inference logic
  - `serializer.py` - JSON persistence
  - `traversal.py` - BFS and path utilities
- MODIFY: `src/raise_cli/cli/commands/graph.py` - Add `build` subcommand
- CREATE: `tests/governance/graph/` (test suite)

## Examples

### CLI Usage

```bash
# Build graph from extracted concepts (uses .raise/cache/concepts.json)
$ raise graph build

Building concept graph...
  ✓ Loaded 24 concepts
  ✓ Inferred 47 relationships
    - implements: 8
    - governed_by: 16
    - depends_on: 12
    - related_to: 11
  ✓ Saved to .raise/cache/graph.json

Graph: 24 nodes, 47 edges

# Build with specific concepts file
$ raise graph build --concepts custom_concepts.json --output my_graph.json

# Validate graph structure
$ raise graph validate

Validating graph...
  ✓ No cycles detected
  ✓ All relationships valid
  ✓ 24/24 concepts reachable

Graph is valid.
```

### Python API

```python
from raise_cli.governance.graph import GraphBuilder, ConceptGraph
from raise_cli.governance.extractor import GovernanceExtractor
from pathlib import Path

# Extract concepts (F2.1)
extractor = GovernanceExtractor()
concepts = extractor.extract_all()

# Build graph
builder = GraphBuilder()
graph = builder.build(concepts)

print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
# Output: Graph: 24 nodes, 47 edges

# Query relationships
req_rf_05 = graph.get_node("req-rf-05")
governed_by = graph.get_outgoing_edges(req_rf_05.id, edge_type="governed_by")

for edge in governed_by:
    print(f"{edge.source} governed by {edge.target}")
    # Output: req-rf-05 governed by principle-governance-as-code

# Traverse from requirement to principles
principles = graph.traverse_bfs(
    start_id="req-rf-05",
    edge_types=["governed_by"],
    max_depth=2
)

# Serialize
graph_json = graph.to_json()
Path(".raise/cache/graph.json").write_text(graph_json)

# Deserialize
loaded_graph = ConceptGraph.from_json(graph_json)
```

### Data Structures

```python
from pydantic import BaseModel, Field
from typing import Literal
from raise_cli.governance.models import Concept

# Relationship types (5 max per ADR-011)
RelationshipType = Literal[
    "implements",    # Requirement implements outcome
    "governed_by",   # Artifact governed by principle
    "depends_on",    # Concept depends on another
    "related_to",    # Semantic relationship
    "validates"      # Gate validates concept (future)
]

class Relationship(BaseModel):
    """Directed edge in concept graph"""

    source: str = Field(..., description="Source concept ID")
    target: str = Field(..., description="Target concept ID")
    type: RelationshipType = Field(..., description="Relationship type")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Relationship metadata (e.g., confidence, source)"
    )

class ConceptGraph(BaseModel):
    """In-memory concept graph"""

    nodes: dict[str, Concept] = Field(
        default_factory=dict,
        description="Concepts indexed by ID"
    )
    edges: list[Relationship] = Field(
        default_factory=list,
        description="Relationships between concepts"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Graph metadata (build time, version, stats)"
    )

    def get_node(self, concept_id: str) -> Concept | None:
        """Get concept by ID"""
        return self.nodes.get(concept_id)

    def get_outgoing_edges(
        self,
        concept_id: str,
        edge_type: RelationshipType | None = None
    ) -> list[Relationship]:
        """Get outgoing edges from a concept"""
        return [
            e for e in self.edges
            if e.source == concept_id
            and (edge_type is None or e.type == edge_type)
        ]

    def get_incoming_edges(
        self,
        concept_id: str,
        edge_type: RelationshipType | None = None
    ) -> list[Relationship]:
        """Get incoming edges to a concept"""
        return [
            e for e in self.edges
            if e.target == concept_id
            and (edge_type is None or e.type == edge_type)
        ]

    def traverse_bfs(
        self,
        start_id: str,
        edge_types: list[RelationshipType] | None = None,
        max_depth: int = 3
    ) -> list[Concept]:
        """BFS traversal from start node"""
        # Implementation in traversal.py
        pass

    def to_json(self) -> str:
        """Serialize to JSON"""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ConceptGraph":
        """Deserialize from JSON"""
        return cls.model_validate_json(json_str)
```

## Acceptance Criteria

**MUST:**
- Build directed graph from `list[Concept]` (F2.1 output)
- Infer relationships using rule-based patterns:
  - `implements`: Requirements → Outcomes (extract outcome keywords from requirement content)
  - `governed_by`: Requirements → Principles (extract principle references like "§2")
  - `depends_on`: Explicit "depends on RF-XX" in content
  - `related_to`: Shared keywords between concepts
- Store graph as `ConceptGraph` with nodes (dict) and edges (list)
- Serialize to JSON (`graph.to_json()`) and deserialize (`ConceptGraph.from_json()`)
- Provide BFS traversal utility with depth limit and edge type filtering
- CLI command `raise graph build` functional
- >90% test coverage on graph module
- All code passes type checking (`pyright --strict`)

**SHOULD:**
- Detect and warn about cycles in `depends_on` relationships
- Include relationship metadata (confidence score, inference source)
- Log graph statistics (nodes, edges per type, density)
- Support incremental graph updates (add concepts without full rebuild)

**MUST NOT:**
- Require external graph databases (in-memory + JSON only)
- Implement complex NLP (keyword matching is sufficient)
- Build visualization (deferred to post-MVP)
- Mutate concepts during graph building (graph is view over concepts)

## Algorithm Details

### Relationship Inference

```python
def infer_relationships(concepts: list[Concept]) -> list[Relationship]:
    """Infer relationships between concepts using rule-based patterns"""
    relationships = []

    # Index concepts by type for efficient lookup
    requirements = [c for c in concepts if c.type == ConceptType.REQUIREMENT]
    outcomes = [c for c in concepts if c.type == ConceptType.OUTCOME]
    principles = [c for c in concepts if c.type == ConceptType.PRINCIPLE]

    # Rule 1: implements (requirement → outcome)
    for req in requirements:
        for outcome in outcomes:
            # Check if requirement mentions outcome keywords
            outcome_keywords = extract_keywords(outcome.metadata.get("title", ""))
            if any(kw in req.content.lower() for kw in outcome_keywords):
                relationships.append(Relationship(
                    source=req.id,
                    target=outcome.id,
                    type="implements",
                    metadata={"confidence": 0.8, "method": "keyword_match"}
                ))

    # Rule 2: governed_by (requirement/outcome → principle)
    for concept in requirements + outcomes:
        # Look for §N references in content
        principle_refs = re.findall(r'§(\d+)', concept.content)
        for ref in principle_refs:
            # Find matching principle
            principle = next(
                (p for p in principles if f"§{ref}" in p.section),
                None
            )
            if principle:
                relationships.append(Relationship(
                    source=concept.id,
                    target=principle.id,
                    type="governed_by",
                    metadata={"confidence": 1.0, "method": "explicit_reference"}
                ))

    # Rule 3: depends_on (explicit dependencies)
    for concept in concepts:
        # Look for "depends on RF-XX" or "requires RF-XX"
        dep_refs = re.findall(r'(?:depends on|requires) (RF-\d+)', concept.content)
        for ref in dep_refs:
            target_id = f"req-{ref.lower()}"
            if target_id in {c.id for c in concepts}:
                relationships.append(Relationship(
                    source=concept.id,
                    target=target_id,
                    type="depends_on",
                    metadata={"confidence": 1.0, "method": "explicit_reference"}
                ))

    # Rule 4: related_to (shared keywords)
    for i, c1 in enumerate(concepts):
        for c2 in concepts[i+1:]:
            # Extract keywords from both concepts
            kw1 = extract_keywords(c1.section + " " + c1.content[:200])
            kw2 = extract_keywords(c2.section + " " + c2.content[:200])

            # If >3 shared keywords, create related_to edge
            shared = kw1 & kw2
            if len(shared) >= 3:
                relationships.append(Relationship(
                    source=c1.id,
                    target=c2.id,
                    type="related_to",
                    metadata={
                        "confidence": 0.6,
                        "method": "keyword_overlap",
                        "shared_keywords": list(shared)
                    }
                ))

    return relationships

def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text (lowercase, no stopwords)"""
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    words = re.findall(r'\b\w+\b', text.lower())
    return {w for w in words if len(w) > 3 and w not in stopwords}
```

### BFS Traversal

```python
from collections import deque

def traverse_bfs(
    graph: ConceptGraph,
    start_id: str,
    edge_types: list[RelationshipType] | None = None,
    max_depth: int = 3
) -> list[Concept]:
    """BFS traversal from start node with depth limit"""

    if start_id not in graph.nodes:
        return []

    visited = {start_id}
    queue = deque([(start_id, 0)])  # (concept_id, depth)
    result = [graph.nodes[start_id]]

    while queue:
        current_id, depth = queue.popleft()

        if depth >= max_depth:
            continue

        # Get outgoing edges (optionally filtered by type)
        edges = graph.get_outgoing_edges(current_id)
        if edge_types:
            edges = [e for e in edges if e.type in edge_types]

        for edge in edges:
            target_id = edge.target
            if target_id not in visited:
                visited.add(target_id)
                result.append(graph.nodes[target_id])
                queue.append((target_id, depth + 1))

    return result
```

## Constraints

**Performance:**
- Build graph from 50 concepts in <2 seconds
- Memory usage <100MB for typical governance corpus (50 concepts, 100 edges)
- BFS traversal of full graph <100ms

**Quality:**
- Relationship inference precision >80% (few false positives)
- Recall >60% (capture most real relationships)
- No duplicate edges (same source, target, type)

**Compatibility:**
- Python 3.12+
- JSON serialization compatible with standard JSON parsers
- Graph structure supports future extensions (new relationship types)

## Testing Approach

**Unit tests** for relationship inference:
```python
def test_infer_implements_relationships():
    """Test requirement → outcome relationship inference"""
    # Given: Requirement mentioning "context generation"
    requirement = Concept(
        id="req-rf-05",
        type=ConceptType.REQUIREMENT,
        content="The system MUST generate context for agents..."
    )
    outcome = Concept(
        id="outcome-context-generation",
        type=ConceptType.OUTCOME,
        metadata={"title": "Context Generation"}
    )

    # When: Infer relationships
    rels = infer_relationships([requirement, outcome])

    # Then: Should find implements relationship
    implements = [r for r in rels if r.type == "implements"]
    assert len(implements) == 1
    assert implements[0].source == "req-rf-05"
    assert implements[0].target == "outcome-context-generation"

def test_infer_governed_by_relationships():
    """Test explicit §N principle references"""
    # Given: Requirement referencing §2
    requirement = Concept(
        id="req-rf-05",
        content="Per §2, standards must be versioned in Git..."
    )
    principle = Concept(
        id="principle-governance-as-code",
        section="§2. Governance as Code"
    )

    # When: Infer relationships
    rels = infer_relationships([requirement, principle])

    # Then: Should find governed_by relationship
    governed = [r for r in rels if r.type == "governed_by"]
    assert len(governed) == 1
    assert governed[0].source == "req-rf-05"
    assert governed[0].target == "principle-governance-as-code"
```

**Integration tests** for graph builder:
```python
def test_build_graph_from_real_governance():
    """Test graph building from raise-commons governance"""
    # Given: Real extracted concepts
    extractor = GovernanceExtractor()
    concepts = extractor.extract_all()

    # When: Build graph
    builder = GraphBuilder()
    graph = builder.build(concepts)

    # Then: Should have reasonable graph statistics
    assert len(graph.nodes) >= 20
    assert len(graph.edges) >= 30
    assert any(e.type == "implements" for e in graph.edges)
    assert any(e.type == "governed_by" for e in graph.edges)

def test_graph_serialization_roundtrip():
    """Test JSON serialization preserves graph"""
    # Given: Built graph
    graph = build_test_graph()

    # When: Serialize and deserialize
    json_str = graph.to_json()
    loaded_graph = ConceptGraph.from_json(json_str)

    # Then: Graphs should be equivalent
    assert len(loaded_graph.nodes) == len(graph.nodes)
    assert len(loaded_graph.edges) == len(graph.edges)
    assert loaded_graph.nodes.keys() == graph.nodes.keys()
```

**Edge cases:**
- Empty concept list → Empty graph (no crash)
- Single concept → 1 node, 0 edges
- Concepts with no relationships → Disconnected nodes (OK)
- Circular dependencies → Detect and warn

## Dependencies

**Blocked by**:
- F2.1 (Concept Extraction) ✓ COMPLETE

**Blocks**:
- F2.3 (MVC Query Engine) - needs graph for traversal queries
- F2.4 (CLI Commands) - needs graph for context queries

**External dependencies**:
- Standard library only (re, pathlib, typing, collections)
- Pydantic (already in project)
- No new packages required

## References

- **F2.1 output**: `Concept` objects from `src/raise_cli/governance/models.py`
- **Spike validation**: `dev/experiments/test_mvc.py` (BFS traversal proven)
- **Architecture**: `dev/decisions/adr-011-concept-level-graph-architecture.md`
- **Epic scope**: `dev/epic-e2-scope.md`
- **Glossary**: `framework/reference/glossary.md` (Concept Graph, Relationship types)

---

*Created: 2026-01-31*
*Ready for: `/feature-plan`*
