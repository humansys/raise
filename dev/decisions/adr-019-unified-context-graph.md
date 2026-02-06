---
id: "ADR-019"
title: "Unified Context Graph Architecture"
date: "2026-02-03"
status: "Accepted"
related_to: ["ADR-011", "ADR-015", "ADR-016"]
supersedes: []
research: "RES-CONTEXT-001"
---

# ADR-019: Unified Context Graph Architecture

## Context

### The Problem

Rai has three separate graph systems that don't communicate:

| Graph | Location | Status |
|-------|----------|--------|
| Governance | `.raise/graph/` | Extractor exists, graph never built |
| Memory | `.rai/memory/graph.json` | Works, but skills don't query it |
| Work | Extends governance | No base graph to extend |

Skills operate without accumulated knowledge because there's no unified way to query relevant context. This impacts quality and lead time — Rai re-discovers patterns instead of using what's learned.

### Research Findings (RES-CONTEXT-001)

Industry research revealed:

1. **Hybrid retrieval** (semantic + keyword + graph) is standard practice
2. **Unified graph > federated** for small-scale systems (<10K nodes)
3. **NetworkX** sufficient for in-memory graphs without external dependencies
4. **GraphRAG pattern** shows 20-35% precision improvement over vector-only

Key sources: Microsoft GraphRAG, Neo4j, Graphiti/Zep, LlamaIndex Property Graph.

### Design Constraints

- **No new dependencies** — NetworkX already in dependency tree
- **Local-first** — Must work offline, no external services
- **F&F timeline** — Must be implementable in ~4-5 hours
- **Extensible** — Can add embeddings/vector search later

## Decision

**Implement a single unified NetworkX graph containing all concept types with a unified query interface.**

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Unified Context Graph                      │
│                    (.raise/graph/unified.json)                │
│                                                              │
│  Node Types:                                                 │
│  ├── pattern (PAT-*)      — learned patterns                 │
│  ├── calibration (CAL-*)  — velocity data                    │
│  ├── session (SES-*)      — session history                  │
│  ├── principle (§N)       — constitution principles          │
│  ├── requirement (RF-*)   — PRD requirements                 │
│  ├── outcome (OUT-*)      — vision outcomes                  │
│  ├── epic (E*)            — epic scopes                      │
│  ├── feature (F*.*)       — story work                     │
│  └── skill (/name)        — skill metadata                   │
│                                                              │
│  Edge Types:                                                 │
│  ├── learned_from    — pattern → session                     │
│  ├── governed_by     — requirement → principle               │
│  ├── applies_to      — pattern → skill                       │
│  ├── needs_context   — skill → concept types                 │
│  ├── implements      — feature → requirement                 │
│  ├── part_of         — feature → epic                        │
│  └── related_to      — generic semantic relationship         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Unified Query Interface                    │
│              raise context query "planning F11.1"             │
│                                                              │
│  1. Keyword match on node content                            │
│  2. BFS traversal from matched nodes                         │
│  3. Filter by relevance/type                                 │
│  4. Return Minimum Viable Context                            │
└──────────────────────────────────────────────────────────────┘
```

### Schema

```python
from pydantic import BaseModel
from typing import Literal
import networkx as nx

NodeType = Literal[
    "pattern", "calibration", "session",
    "principle", "requirement", "outcome",
    "epic", "feature", "skill"
]

EdgeType = Literal[
    "learned_from", "governed_by", "applies_to",
    "needs_context", "implements", "part_of", "related_to"
]

class ConceptNode(BaseModel):
    id: str
    type: NodeType
    content: str
    source_file: str | None = None
    created: str
    metadata: dict = {}

class ConceptEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    metadata: dict = {}

class UnifiedGraph:
    """NetworkX-based unified context graph."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_concept(self, node: ConceptNode) -> None:
        self.graph.add_node(node.id, **node.model_dump())

    def add_relationship(self, edge: ConceptEdge) -> None:
        self.graph.add_edge(
            edge.source, edge.target,
            type=edge.type, weight=edge.weight,
            **edge.metadata
        )

    def query(self, query: str, max_depth: int = 2) -> list[ConceptNode]:
        """BFS from keyword-matched nodes."""
        ...

    def save(self, path: Path) -> None:
        data = nx.node_link_data(self.graph)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "UnifiedGraph":
        data = json.loads(path.read_text())
        instance = cls()
        instance.graph = nx.node_link_graph(data)
        return instance
```

### Query Flow

```
User invokes /story-plan F11.1
    │
    ▼
Skill Step 0.5: Query Context
    │
    ├─► raise context query "planning F11.1 estimation"
    │
    ▼
Query Engine:
    1. Keyword match: Find nodes containing "planning", "F11.1", "estimation"
    2. BFS traversal: Expand to depth 2 from matched nodes
    3. Filter: Prioritize patterns, calibration for planning context
    4. Rank: By relevance score (keyword hits + recency)
    │
    ▼
Return MVC:
    - PAT-013 (task granularity)
    - PAT-014 (T-shirt sizing)
    - CAL-* (similar feature calibration)
    - §5 (Validation Gates principle)
    - F11.1 scope from epic
```

### Why Unified > Federated

| Aspect | Federated | Unified |
|--------|-----------|---------|
| Query complexity | Multiple dispatches, merge logic | Single query |
| Cross-domain links | Hard (separate graphs) | Natural (same graph) |
| Consistency | Risk of drift | Single source of truth |
| Implementation | More code, more maintenance | Simpler |
| Our scale | Overkill | Right-sized |

Federated makes sense for enterprise with 100K+ nodes and separate teams. We have <1K nodes and one team.

## Consequences

### Positive ✅

1. **Single query interface** — One command gets all relevant context
2. **Cross-domain relationships** — Patterns can link to principles, skills to features
3. **No new dependencies** — NetworkX is lightweight, already available
4. **Extensible** — Can add embeddings later without redesign
5. **Skills become smarter** — Every skill invocation starts with context
6. **Self-improvement loop** — I actually use what I've learned

### Negative ⚠️

1. **Migration effort** — Must merge existing graph infrastructure
2. **Single rebuild trigger** — Any source change triggers full rebuild
3. **Schema complexity** — Multiple node types in one schema

### Neutral 🔄

1. **Existing code reusable** — Extractors, parsers still work
2. **Storage format changes** — From multiple files to one unified.json
3. **Query interface changes** — `raise context query` becomes unified

## Implementation (E11)

| Feature | Description | Size |
|---------|-------------|:----:|
| F11.1 | Unified Graph Schema | S |
| F11.2 | Graph Builder (merge sources) | M |
| F11.3 | Unified Query Command | S |
| F11.4 | Skill Integration (9 skills) | S |

**Total:** ~7 SP, ~4-5 hours

## Alternatives Considered

### Alternative 1: Federated Queries

Query each graph separately, merge results.

**Rejected because:**
- More complex implementation
- No cross-domain relationships
- Overkill for our scale

### Alternative 2: Add Embeddings First

Build vector search before graph unification.

**Rejected because:**
- Adds complexity and dependencies
- Research shows keyword + graph is sufficient for our scale
- Can add later if needed

### Alternative 3: Use Graphiti/External Library

Adopt Graphiti or similar for temporal knowledge graph.

**Rejected because:**
- Requires Neo4j dependency
- Overkill for our scale
- Violates local-first, no-dependency constraint

## Validation

### Success Criteria

| Metric | Target |
|--------|--------|
| Concepts in graph | >50 (patterns + principles + skills) |
| Query latency | <100ms |
| Relevant results | >2 per skill invocation |
| Skills integrated | 9 workflow skills |

### Test Query

```bash
raise context query "planning estimation"
# Should return:
# - PAT-013, PAT-014 (planning patterns)
# - Calibration data for similar features
# - §5 Validation Gates
# - /story-plan skill
```

## References

- **Research:** `work/research/unified-context-architecture/README.md`
- **ADR-011:** Concept-level graph architecture (original MVC design)
- **ADR-015:** Memory infrastructure (file backend pattern)
- **ADR-016:** Memory format (JSONL + graph)
- **NetworkX docs:** https://networkx.org/documentation/stable/

---

**Status**: Accepted (2026-02-03)

**Approved by**: Emilio Osorio, Rai

**Next steps**:
1. Update E11 scope with confirmed architecture
2. Implement F11.1 (schema)
3. Implement F11.2 (builder)
4. Implement F11.3 (query)
5. Implement F11.4 (skill integration)
