---
type: module
name: context
purpose: "Unified knowledge graph — merges governance, memory, discovery, work, and code structure into a single queryable structure"
status: current
depends_on: [config, core, governance, memory]
depended_by: [cli, session]
entry_points:
  - "raise memory build"
  - "raise memory query"
public_api:
  - "ConceptEdge"
  - "ConceptNode"
  - "EdgeType"
  - "GraphDiff"
  - "NodeChange"
  - "NodeType"
  - "UnifiedGraph"
  - "UnifiedGraphBuilder"
  - "UnifiedQuery"
  - "UnifiedQueryEngine"
  - "UnifiedQueryMetadata"
  - "UnifiedQueryResult"
  - "UnifiedQueryStrategy"
  - "diff_graphs"
components: 25
constraints:
  - "Graph is rebuilt from scratch on each 'raise memory build' — no incremental updates"
  - "Queries use BFS traversal, not full-text search"
  - "Node types are a closed set (Literal type) — adding new types requires schema change"
  - "Code analyzers enrich existing mod-* nodes, they do not create new nodes"
---

## Purpose

The context module is the **integration hub** of raise-cli. It takes knowledge from five domains — governance documents, developer memory (patterns/calibration/sessions), work tracking (epics/stories), discovered components, and code structure — and merges them into a single `UnifiedGraph` backed by NetworkX. This graph is what makes `rai memory query` work: any concept can find related concepts across domains.

For example, querying "testing patterns" can return a pattern from memory, a guardrail from governance, a component from discovery, and actual code imports/exports from module analysis — all connected by shared keywords or explicit relationships. As of S16.1 (Code-Aware Graph), the builder now enriches module nodes with real code analysis data (imports, exports, component counts) via language-specific analyzers.

## Architecture

```
Governance files → GovernanceExtractor → concept nodes ─┐
JSONL memory     → MemoryLoader        → pattern nodes  ├→ UnifiedGraphBuilder → UnifiedGraph
Epic/story files → WorkParser          → work nodes     │       ↓
Components JSON  → ComponentLoader     → comp nodes     │  UnifiedQueryEngine
Architecture docs→ ArchitectureLoader  → module nodes   │       ↓
Source code      → CodeAnalyzer        → enriched mods ─┘  rai memory query
                                           (S16.1)
```

The `UnifiedGraphBuilder.build()` method orchestrates all loaders:

1. Load nodes from all sources (governance, memory, work, skills, components, architecture, identity)
2. Enrich module nodes with real code analysis via `load_code_structure()` (S16.1) — adds `code_imports`, `code_exports`, `code_components` to metadata
3. Add all nodes to graph
4. Extract structural nodes (bounded contexts, layers) and create explicit edges (belongs_to, in_layer, constrained_by)
5. Infer relationships (learned_from, part_of, depends_on, related_to) using metadata and keyword heuristics

## Key Files

- **`models.py`** — `ConceptNode`, `ConceptEdge`, `NodeType`, `EdgeType`. The schema for all graph data. NodeType is a Literal type — adding new types here is a schema change that invalidates cached graphs (PAT-152).
- **`builder.py`** — `UnifiedGraphBuilder` with `load_*()` methods for each source. Includes `infer_relationships()` for edge creation. The `load_architecture()` method parses YAML frontmatter from module docs. As of S16.1, `load_code_structure()` enriches module nodes with real code analysis.
- **`graph.py`** — `UnifiedGraph` wrapping NetworkX. Provides `add_concept()`, `get_concept()`, `iter_concepts()`, and traversal methods.
- **`query.py`** — `UnifiedQueryEngine` with keyword-based search, type filtering, and BFS traversal for related concepts.
- **`extractors/skills.py`** — Parses SKILL.md YAML frontmatter into skill nodes.
- **`analyzers/protocol.py`** — `CodeAnalyzer` protocol for language-specific analyzers (S16.1).
- **`analyzers/python.py`** — `PythonAnalyzer` implementation using AST to extract imports, exports, and component counts (S16.1).
- **`analyzers/models.py`** — `ModuleInfo` dataclass holding code analysis results (S16.1).

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
