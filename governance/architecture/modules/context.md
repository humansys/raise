---
type: module
name: context
purpose: "Unified knowledge graph — merges governance, memory, discovery, and work into a single queryable structure"
status: current
depends_on: [config, core, governance, memory]
depended_by: [cli, memory]
entry_points:
  - "raise memory build"
  - "raise memory query"
public_api:
  - "UnifiedGraph"
  - "UnifiedGraphBuilder"
  - "UnifiedQueryEngine"
  - "ConceptNode"
  - "ConceptEdge"
  - "NodeType"
  - "EdgeType"
components: 18
constraints:
  - "Graph is rebuilt from scratch on each 'raise memory build' — no incremental updates"
  - "Queries use BFS traversal, not full-text search"
  - "Node types are a closed set (Literal type) — adding new types requires schema change"
---

## Purpose

The context module is the **integration hub** of raise-cli. It takes knowledge from four domains — governance documents, developer memory (patterns/calibration/sessions), work tracking (epics/stories), and discovered components — and merges them into a single `UnifiedGraph` backed by NetworkX. This graph is what makes `raise memory query` work: any concept can find related concepts across domains.

For example, querying "testing patterns" can return a pattern from memory, a guardrail from governance, and a component from discovery — all connected by shared keywords or explicit relationships.

## Architecture

```
Governance files → GovernanceExtractor → concept nodes ─┐
JSONL memory     → MemoryLoader        → pattern nodes  ├→ UnifiedGraphBuilder → UnifiedGraph
Epic/story files → WorkParser          → work nodes     │       ↓
Components JSON  → ComponentLoader     → comp nodes     │  UnifiedQueryEngine
Architecture docs→ ArchitectureLoader  → module nodes ──┘       ↓
                                                         raise memory query
```

The `UnifiedGraphBuilder.build()` method orchestrates all loaders, adds nodes to the graph, then infers relationships (learned_from, part_of, depends_on, related_to) between them.

## Key Files

- **`models.py`** — `ConceptNode`, `ConceptEdge`, `NodeType`, `EdgeType`. The schema for all graph data. NodeType is a Literal type — adding new types here is a schema change that invalidates cached graphs (PAT-152).
- **`builder.py`** — `UnifiedGraphBuilder` with `load_*()` methods for each source. Includes `infer_relationships()` for edge creation. The `load_architecture()` method parses YAML frontmatter from module docs.
- **`graph.py`** — `UnifiedGraph` wrapping NetworkX. Provides `add_concept()`, `get_concept()`, `iter_concepts()`, and traversal methods.
- **`query.py`** — `UnifiedQueryEngine` with keyword-based search, type filtering, and BFS traversal for related concepts.
- **`extractors/skills.py`** — Parses SKILL.md YAML frontmatter into skill nodes.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Directory resolution for memory tiers |
| `core` | Text processing (stopwords for keyword extraction) |
| `governance` | GovernanceExtractor for concept extraction |
| `memory` | MemoryScope enum for three-tier precedence |

## Conventions

- The graph is always rebuilt from scratch (no incremental updates) — simplicity over performance
- Node IDs follow source-specific patterns: `PAT-*`, `§N`, `mod-*`, `comp-*`, etc.
- Edge weights: 1.0 for explicit relationships, <1.0 for inferred (keyword-based)
- Query results include token estimates for context budget management
