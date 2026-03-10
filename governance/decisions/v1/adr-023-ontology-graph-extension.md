---
id: "ADR-023"
title: "Ontology Graph Extension — Bounded Contexts, Layers, and Constraint Edges"
date: "2026-02-08"
status: "Accepted"
related_to: ["ADR-019", "ADR-020"]
supersedes: []
research: "RES-ARCH-KNOWLEDGE-001"
epic: "E15"
---

# ADR-023: Ontology Graph Extension — Bounded Contexts, Layers, and Constraint Edges

## Context

### The Problem

The unified graph (ADR-019) works as a query tool but doesn't encode architectural structure. Design skills query it with ad-hoc keywords and get unpredictable results. There is no way to ask:

- "What constraints apply to this module?"
- "Which bounded context owns this module?"
- "What layer is this module in?"

E14 evidence quantifies the cost: **14 SP of rework** (60% of epic effort) directly caused by missing ontology structure — 5,200 dead lines from 3 graph classes that should have been 1, 315 files renamed from undefined terminology, session concept scattered across 4 systems.

### Research Findings

Research into reliable knowledge graph retrieval (Microsoft GraphRAG, LlamaIndex PropertyGraph, Zep/Graphiti) revealed:

1. **Typed queries** (by edge type) have guaranteed recall for constraint discovery
2. **Keyword-only queries** have ~40% false negative rate for semantic matches
3. **Two-stage retrieval** (typed first, keyword second) is industry standard
4. **Edge-type filtering** is the primary mechanism for progressive disclosure
5. **NetworkX `get_neighbors()` with edge_types already exists** in our codebase — the gap is at the query engine level

### Design Constraints

- No new dependencies — NetworkX sufficient
- Schema change (PAT-152) — adding NodeType/EdgeType requires graph rebuild
- Must be deterministic — no AI inference in graph construction
- Data sources already structured — domain-model.md and system-design.md have YAML frontmatter with bounded contexts, layers, and module assignments

## Decision

**Extend the ontology graph with architectural structure nodes and typed constraint edges. Use typed queries (not keyword search) as the primary retrieval mechanism for architectural context.**

### Schema Extension

```python
# New NodeTypes (added to existing 15)
NodeType = Literal[
    # ... existing types ...
    "bounded_context",  # BC-* — DDD bounded context
    "layer",            # LYR-* — architectural layer
]

# New EdgeTypes (added to existing 8)
EdgeType = Literal[
    # ... existing types ...
    "belongs_to",       # module → bounded_context
    "in_layer",         # module → layer
    "constrained_by",   # bounded_context/layer → guardrail
]
```

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 Extended Ontology Graph                        │
│                                                              │
│  New Nodes:                                                  │
│  ├── bounded_context (BC-*)    — 7 contexts + shared_kernel  │
│  └── layer (LYR-*)            — 4 architectural layers       │
│                                                              │
│  New Edges:                                                  │
│  ├── belongs_to     — module → bounded_context               │
│  ├── in_layer       — module → layer                         │
│  └── constrained_by — bounded_context/layer → guardrail      │
│                                                              │
│  Query Enhancement:                                          │
│  └── edge_types parameter exposed in query engine            │
│      (already works at graph level)                          │
└──────────────────────────────────────────────────────────────┘
```

### Constraint Mapping Strategy

Guardrails are mapped to scopes via their ID prefix — deterministic, no inference:

```
MUST-CODE-* → ALL bounded contexts (code quality is universal)
MUST-TEST-* → ALL bounded contexts
MUST-SEC-*  → ALL bounded contexts
MUST-ARCH-* → Ontology + Skills BCs (architecture-specific)
MUST-DEV-*  → ALL bounded contexts
SHOULD-CLI-* → Orchestration layer only
SHOULD-*    → ALL bounded contexts (suggestions apply broadly)
```

Module-specific constraints come from the `constraints` field in module architecture docs.

### Query Strategy

**For architectural context:** Use CONCEPT_LOOKUP with edge_types (typed BFS)
**For exploratory search:** Use KEYWORD_SEARCH (existing behavior)

```python
# Typed query: "What constraints apply to the memory module?"
engine.query(UnifiedQuery(
    query="mod-memory",
    strategy="concept_lookup",
    edge_types=["constrained_by", "belongs_to", "in_layer"],
    max_depth=2,
))

# Convenience helper (same result, simpler API):
engine.get_architectural_context("memory")
# → ArchitecturalContext(domain="ontology", layer="integration",
#     constraints=[...guardrails...], dependencies=[...modules...])
```

## Consequences

### Positive

1. **Reliable constraint discovery** — Typed queries guarantee recall (no keyword matching failures)
2. **Architecture-aware design** — Skills know the bounded context, layer, and constraints before designing
3. **Deterministic extraction** — All data comes from structured YAML frontmatter, no AI inference
4. **Backward compatible** — Existing keyword queries continue to work unchanged
5. **Eliminates E14-class errors** — Domain boundary violations, scattered concepts, undefined terminology caught at design time
6. **Minimal code change for Story 4** — Graph layer already has edge_types; just exposing in query engine

### Negative

1. **Schema change** (PAT-152) — Adding NodeType/EdgeType requires full graph rebuild
2. **More edges** — Constraint edges increase graph density (mitigated by edge-type filtering)
3. **Maintenance of mapping table** — Guardrail category → scope mapping must stay current

### Neutral

1. **Existing extractors unchanged** — Governance, discovery, memory extractors work as-is
2. **Graph size increase** — ~12 new nodes (8 BCs + 4 layers), ~200 new edges (constraint mapping)
3. **No new dependencies** — Pure NetworkX, Pydantic, existing infrastructure

## Alternatives Considered

### Alternative 1: Metadata on Existing Nodes

Store bounded context and layer as metadata fields on module nodes, not as separate nodes.

**Rejected because:**
- Can't navigate from context to modules ("show me all modules in Ontology BC")
- Can't attach constraints to contexts (guardrails constrain contexts, not individual modules)
- Loses the graph navigability that makes ontology-guided design work

### Alternative 2: Keyword-Based Constraint Discovery

Keep keyword search, add "constraint" as a keyword to guardrail content.

**Rejected because:**
- Research shows ~40% false negative rate for keyword matching
- PAT-062: "Query keywords must match actual node content" — fragile
- Typed queries are strictly superior for structural relationships

### Alternative 3: LLM-Based Inference for Guardrail Mapping

Use AI to infer which guardrails apply to which modules based on semantic similarity.

**Rejected because:**
- Violates "no AI inference in graph construction" constraint
- Non-deterministic — different runs could produce different edges
- Guardrail IDs already encode scope deterministically — inference is unnecessary

## Validation

### Success Criteria

| Metric | Target |
|--------|--------|
| New node types | 2 (bounded_context, layer) |
| New edge types | 3 (belongs_to, in_layer, constrained_by) |
| Bounded context nodes | 8 (7 BCs + shared_kernel) |
| Layer nodes | 4 |
| Module → BC edges | 14 (one per module) |
| Module → Layer edges | 14 (one per module) |
| Constraint edges | ~150-200 (22 guardrails × avg 7 scopes) |
| `rai memory context <module>` latency | <100ms |
| Design skill improvement | Dogfood with real story design |

### Test Query

```bash
rai memory context memory
# Should return:
# Domain: ontology (persists, integrates, queries knowledge)
# Layer: integration (combines domains)
# Constraints:
#   - MUST-CODE-001: Type hints on all code
#   - MUST-TEST-001: >90% test coverage
#   - MUST-ARCH-002: Pydantic models for all schemas
#   - Module-specific: "JSONL append-only — never edit historical entries"
# Dependencies: core, config, schemas (via depends_on edges)
```

## References

- **ADR-019:** Unified Context Graph Architecture (foundation)
- **ADR-020:** Extended Node Types (precedent for schema extension)
- **PAT-152:** Schema Literal changes invalidate cached graphs
- **PAT-175:** Ontology-guided design pattern
- **E14 Evidence:** 14 SP rework from missing ontology structure
- **Research:** Microsoft GraphRAG, LlamaIndex PropertyGraph, Zep/Graphiti

---

**Status**: Accepted (2026-02-08)

**Approved by**: Emilio Osorio, Rai

**Next steps**:
1. Implement E15 stories (S1-S6)
2. Rebuild graph after schema changes
3. Dogfood with real story design
