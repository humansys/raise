# Implementation Plan: F2.2 Graph Builder

## Overview
- **Feature:** F2.2 Graph Builder
- **Story Points:** 2 SP
- **Feature Size:** S (5 components, moderate complexity)
- **Created:** 2026-01-31

## Tasks

### Task 1: Create Graph Models
- **Description:** Implement `Relationship`, `RelationshipType`, and `ConceptGraph` models in `src/rai_cli/governance/graph/models.py` with graph query methods (get_node, get_outgoing_edges, get_incoming_edges)
- **Files:**
  - CREATE `src/rai_cli/governance/graph/__init__.py`
  - CREATE `src/rai_cli/governance/graph/models.py`
  - CREATE `tests/governance/graph/__init__.py`
  - CREATE `tests/governance/graph/test_models.py`
- **Verification:**
  - Models instantiate correctly with valid data
  - Graph query methods work (get_node, get_outgoing_edges, get_incoming_edges)
  - JSON serialization/deserialization roundtrip preserves data
  - `pyright --strict src/rai_cli/governance/graph/models.py` passes
  - `pytest tests/governance/graph/test_models.py -v --cov=src/rai_cli/governance/graph/models.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** None (uses F2.1's Concept model)

### Task 2: Implement Relationship Inference Logic
- **Description:** Create `relationships.py` with `infer_relationships()` function implementing 4 rules: implements (keyword matching), governed_by (§N refs), depends_on (explicit refs), related_to (shared keywords)
- **Files:**
  - CREATE `src/rai_cli/governance/graph/relationships.py`
  - CREATE `tests/governance/graph/test_relationships.py`
- **Verification:**
  - All 4 relationship rules work correctly
  - `extract_keywords()` helper filters stopwords correctly
  - Relationship metadata includes confidence and method
  - No duplicate edges created (same source, target, type)
  - `pytest tests/governance/graph/test_relationships.py -v --cov=src/rai_cli/governance/graph/relationships.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Implement BFS Traversal Utilities
- **Description:** Create `traversal.py` with `traverse_bfs()` function supporting depth limit, edge type filtering, and cycle detection
- **Files:**
  - CREATE `src/rai_cli/governance/graph/traversal.py`
  - CREATE `tests/governance/graph/test_traversal.py`
- **Verification:**
  - BFS traversal respects max_depth parameter
  - Edge type filtering works correctly
  - Handles disconnected graphs gracefully
  - Performance <100ms for 50-node graph
  - `pytest tests/governance/graph/test_traversal.py -v --cov=src/rai_cli/governance/graph/traversal.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Implement GraphBuilder Orchestrator
- **Description:** Create `builder.py` with `GraphBuilder` class that builds graph from concepts by creating nodes dict, inferring relationships, and populating metadata (build time, stats)
- **Files:**
  - CREATE `src/rai_cli/governance/graph/builder.py`
  - CREATE `tests/governance/graph/test_builder.py`
- **Verification:**
  - `build()` creates graph from concept list
  - Graph metadata includes build time and statistics
  - Handles empty concept list gracefully
  - Integration test: build from real raise-commons governance (20+ nodes, 30+ edges)
  - `pytest tests/governance/graph/test_builder.py -v --cov=src/rai_cli/governance/graph/builder.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** Task 2, Task 3

### Task 5: Add CLI Commands `rai graph build` and `rai graph validate`
- **Description:** Extend `src/rai_cli/cli/commands/graph.py` with `build` and `validate` subcommands, with options for custom input/output paths
- **Files:**
  - MODIFY `src/rai_cli/cli/commands/graph.py`
  - MODIFY `tests/cli/commands/test_graph.py`
- **Verification:**
  - `rai graph build` loads concepts from `.raise/cache/concepts.json` and saves graph to `.raise/cache/graph.json`
  - `rai graph build --concepts <path> --output <path>` works with custom paths
  - `rai graph validate` checks for cycles, validates relationships
  - CLI displays graph statistics (nodes, edges per type)
  - `pytest tests/cli/commands/test_graph.py -v` passes
- **Size:** M
- **Dependencies:** Task 4

### Task 6: Integration Tests & Performance Validation
- **Description:** Create end-to-end integration tests with real governance files, validate performance constraints, and add edge case tests
- **Files:**
  - CREATE `tests/governance/graph/test_integration.py`
- **Verification:**
  - E2E test: Extract concepts (F2.1) → Build graph (F2.2) → Validate structure
  - Performance test: Build graph from 50 concepts in <2 seconds
  - Edge cases tested: empty graph, single node, disconnected nodes, circular dependencies
  - Graph statistics match expectations (20+ nodes, 30+ edges from raise-commons)
  - `pytest tests/governance/graph/test_integration.py -v` passes
- **Size:** S
- **Dependencies:** Task 5

### Task 7: Documentation & Component Catalog
- **Description:** Update component catalog, add docstrings (Google-style) to all public APIs, verify all quality gates pass
- **Files:**
  - MODIFY `dev/components.md` (add graph module entry)
  - VERIFY all files have complete docstrings
- **Verification:**
  - All public APIs have Google-style docstrings
  - `dev/components.md` documents graph module with dependencies, public API
  - `ruff check src/rai_cli/governance/graph/` passes
  - `pyright --strict src/rai_cli/governance/graph/` passes
  - `pytest tests/governance/graph/ --cov=src/rai_cli/governance/graph --cov-fail-under=90` passes
  - `bandit -r src/rai_cli/governance/graph/` passes
- **Size:** XS
- **Dependencies:** Task 6

## Execution Order

**Sequential foundation:**
1. Task 1 (models) - Foundation for all other components

**Parallel core logic:**
2. Task 2 (relationship inference), Task 3 (BFS traversal) - Can be done in parallel

**Sequential integration:**
3. Task 4 (GraphBuilder) - Integrates inference + traversal
4. Task 5 (CLI commands) - User-facing interface
5. Task 6 (Integration tests) - E2E validation
6. Task 7 (Documentation) - Final polish

**Optimal order:**
```
Task 1
  ├─→ Task 2 ┐
  └─→ Task 3 ├─→ Task 4 ─→ Task 5 ─→ Task 6 ─→ Task 7
```

## Risks

| Risk | Mitigation |
|------|------------|
| Relationship inference too noisy (false positives) | Start with conservative thresholds (>3 shared keywords); tune based on real data |
| BFS traversal performance on large graphs | Limit max_depth to 3; early testing with 50+ concepts |
| JSON serialization of complex graph | Pydantic handles this well; test roundtrip early |
| Cycle detection complexity | Use simple visited set; warn but don't fail on cycles |
| Keyword extraction too simple | Good enough for MVP; can enhance later with NLP if needed |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Graph models |
| 2 | M | -- | Relationship inference |
| 3 | S | -- | BFS traversal |
| 4 | M | -- | GraphBuilder |
| 5 | M | -- | CLI commands |
| 6 | S | -- | Integration tests |
| 7 | XS | -- | Documentation |

## Definition of Done (Feature-Level)

- [ ] All tasks complete (1-7)
- [ ] Build graph from 20+ concepts with 30+ relationships
- [ ] CLI commands `rai graph build` and `rai graph validate` functional
- [ ] JSON serialization/deserialization preserves graph structure
- [ ] BFS traversal supports depth limit and edge type filtering
- [ ] >90% test coverage on graph module
- [ ] All type checks pass (`pyright --strict`)
- [ ] All linting passes (`ruff check`)
- [ ] Performance: <2s for 50 concepts, <100ms for BFS
- [ ] Component catalog updated
- [ ] No security issues (`bandit -r src/rai_cli/governance/graph/`)

---

*Created: 2026-01-31*
*Ready for: `/story-implement`*
