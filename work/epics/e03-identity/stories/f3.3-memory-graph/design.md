# Feature Design: F3.3 Memory Graph

```yaml
story_id: F3.3
title: Memory Graph
size: S
status: design
created: 2026-02-02
research: work/research/memory-systems/RES-MEMORY-001.md
```

---

## What & Why

**Problem:** Rai's memories are stored in JSONL files but can't be queried intelligently — we load everything or nothing, wasting tokens.

**Value:** Enable MVC (Minimum Viable Context) for memories — query only what's relevant, achieving >80% token savings like E2 governance did.

---

## Approach

**Strategy:** Wrap E2's ConceptGraph infrastructure in a new memory module.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reuse strategy | Wrap (not extend/fork) | E2 stays untouched, memory evolves independently |
| Module location | `src/rai_cli/memory/` | Top-level, parallel to governance/ |
| Graph rebuild | Cache + staleness check | Balance of simplicity and performance |
| Retrieval | Keyword + BFS + recency | Proven pattern + time awareness |
| Concept types | `pattern`, `calibration`, `session` | YAGNI — what we have now |
| Relationship types | 4 types | Enough for meaningful traversal |
| CLI commands | `query` + `dump` | MVP retrieval + inspection |

**Components:**

| Component | Action | Description |
|-----------|--------|-------------|
| `src/rai_cli/memory/models.py` | Create | MemoryConcept, MemoryRelationship, MemoryConceptType |
| `src/rai_cli/memory/loader.py` | Create | Load JSONL files → list of MemoryConcept |
| `src/rai_cli/memory/builder.py` | Create | Build ConceptGraph from concepts, infer relationships |
| `src/rai_cli/memory/query.py` | Create | MemoryQuery with keyword + BFS + recency |
| `src/rai_cli/memory/cache.py` | Create | Graph caching with staleness check |
| `src/rai_cli/cli/commands/memory.py` | Create | CLI commands: query, dump |

---

## Examples

### JSONL Input (existing format)

```jsonl
{"type": "pattern", "id": "PAT-001", "content": "Singleton with get/set/configure for module state", "context": ["testing", "module-design"], "learned_from": "SES-001", "created": "2026-01-31"}
{"type": "pattern", "id": "PAT-002", "content": "BFS traversal reuse across features", "context": ["architecture", "graph"], "learned_from": "SES-003", "created": "2026-01-31"}
{"type": "calibration", "id": "CAL-001", "feature": "F2.1", "size": "S", "estimated_min": 180, "actual_min": 52, "ratio": 3.5, "created": "2026-01-31"}
{"type": "session", "id": "SES-003", "date": "2026-01-31", "type": "feature", "summary": "F2.3 MVC Query complete", "features": ["F2.3"], "created": "2026-01-31"}
```

### CLI Usage: Query

```bash
$ rai memory query "graph traversal"

Relevant memories (3 found, 847 tokens):

PAT-002: BFS traversal reuse across features
  Context: architecture, graph
  Learned from: SES-003 (2026-01-31)

PAT-001: Singleton with get/set/configure for module state
  Context: testing, module-design
  Related: shares "architecture" context

CAL-001: F2.1 velocity 3.5x
  Size: S, Estimated: 180min, Actual: 52min
  Related: same session cluster
```

### CLI Usage: Dump

```bash
$ rai memory dump --format json

{
  "concepts": 48,
  "relationships": 23,
  "patterns": 26,
  "calibrations": 10,
  "sessions": 12,
  "token_estimate": 4200
}

$ rai memory dump --format md > memory-snapshot.md
# Exports human-readable markdown
```

### Python API

```python
from raise_cli.memory import MemoryGraph, MemoryQuery

# Load and query
graph = MemoryGraph.from_rai_directory(Path(".rai"))
query = MemoryQuery(graph)

# Find relevant memories
results = query.search(
    keywords=["velocity", "calibration"],
    max_results=5,
    recency_weight=0.3  # 30% boost for recent entries
)

for concept in results.concepts:
    print(f"{concept.id}: {concept.content[:50]}...")

print(f"Token estimate: {results.token_estimate}")
```

### Models

```python
from enum import Enum
from pydantic import BaseModel
from datetime import date

class MemoryConceptType(str, Enum):
    PATTERN = "pattern"
    CALIBRATION = "calibration"
    SESSION = "session"

class MemoryRelationshipType(str, Enum):
    LEARNED_FROM = "learned_from"    # Pattern → Session
    RELATED_TO = "related_to"        # Any → Any (shared context)
    VALIDATES = "validates"          # Calibration → Pattern
    APPLIES_TO = "applies_to"        # Pattern → Context domain

class MemoryConcept(BaseModel):
    id: str
    type: MemoryConceptType
    content: str
    context: list[str] = []
    created: date
    metadata: dict[str, Any] = {}

class MemoryQueryResult(BaseModel):
    concepts: list[MemoryConcept]
    relationships: list[MemoryRelationship]
    token_estimate: int
    query_time_ms: float
```

### Cache Behavior

```python
# First query: rebuilds graph, caches
$ rai memory query "patterns"  # ~50ms (cold)

# Second query: loads from cache
$ rai memory query "velocity"  # ~5ms (warm)

# After JSONL edit: detects staleness, rebuilds
$ echo '{"type":"pattern"...}' >> .rai/memory/patterns.jsonl
$ rai memory query "new"       # ~50ms (rebuild)
```

---

## Acceptance Criteria

### MUST

- [ ] Load all JSONL files from `.rai/memory/` directory
- [ ] Build ConceptGraph with pattern, calibration, session nodes
- [ ] Infer relationships (learned_from, related_to, validates, applies_to)
- [ ] `rai memory query "topic"` returns relevant concepts
- [ ] `rai memory dump` outputs concept/relationship counts
- [ ] Cache graph.json with staleness detection
- [ ] Token estimate in query results
- [ ] >90% test coverage on new code

### SHOULD

- [ ] Recency weighting boosts newer entries
- [ ] Query execution time <100ms warm, <200ms cold
- [ ] `--format md` produces human-readable export

### MUST NOT

- [ ] Modify E2 governance code (wrap only)
- [ ] Require external dependencies (no vector DB)
- [ ] Break existing `.rai/` structure

---

## Testing Approach

```python
# Unit tests
tests/memory/
├── test_models.py      # MemoryConcept, types, validation
├── test_loader.py      # JSONL parsing, error handling
├── test_builder.py     # Graph construction, relationship inference
├── test_query.py       # Search, BFS, recency weighting
└── test_cache.py       # Staleness detection, rebuild triggers

# Integration tests
tests/memory/
└── test_integration.py # Full flow: load → build → query → cache
```

**Test data:** Use fixtures based on actual `.rai/memory/*.jsonl` files.

---

## Out of Scope (V3)

- Vector/semantic search (requires embedding infrastructure)
- Incremental graph updates (rebuild is fast enough)
- Memory consolidation/pruning (manual for now)
- Multi-project memory aggregation

---

## References

- Research: `work/research/memory-systems/RES-MEMORY-001.md`
- E2 Graph: `src/rai_cli/governance/graph/`
- ADR-016: Memory format decision (JSONL + Graph)
- Epic scope: `dev/epic-e3-scope.md`
