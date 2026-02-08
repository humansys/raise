---
story_id: "S15.4"
title: "Edge-Type Filtering"
epic_ref: "E15 Ontology Graph Refinement"
story_points: 2
complexity: "simple"
status: "draft"
version: "1.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Story: Edge-Type Filtering

> **Epic**: E15 - Ontology Graph Refinement
> **Complexity**: simple | **SP**: 2

---

## 1. What & Why

**Problem**: The graph layer (`get_neighbors()`) already supports `edge_types` filtering, but neither the query engine nor the CLI expose it. Users cannot filter by relationship type when querying — e.g., "show me only `constrained_by` edges for this module."

**Value**: Enables M2 milestone (constraint-aware graph) — `raise memory query mod-memory --strategy concept_lookup --edge-types constrained_by` returns guardrails that constrain a module. Foundation for S15.5 query helpers.

---

## 2. Approach

Thread the existing `edge_types` parameter from graph layer through query engine and CLI. Three touch points: model, engine, CLI.

**Components affected**:
- **`context/query.py` — `UnifiedQuery` model**: Add `edge_types` field (modify)
- **`context/query.py` — `UnifiedQueryEngine._concept_lookup()`**: Pass `edge_types` to `get_neighbors()` (modify)
- **`cli/commands/memory.py` — `query` command**: Add `--edge-types` CLI option (modify)
- **Tests**: Add edge-type filtering tests for query engine + CLI (modify)

**Design decision — `concept_lookup` only**:
`edge_types` filtering applies only to `concept_lookup` strategy (BFS traversal). Keyword search iterates node content — no BFS, no edges. Providing `--edge-types` with `keyword_search` is a no-op (silently ignored, consistent with `--types` behavior on irrelevant strategies). Advanced edge-aware keyword queries are S15.5 scope (`find_constraints_for()`).

---

## 3. Interface / Examples

### CLI Usage

```bash
# Lookup module with constrained_by edges only
$ raise memory query mod-memory --strategy concept_lookup --edge-types constrained_by

# Multiple edge types (comma-separated, same pattern as --types)
$ raise memory query mod-memory --strategy concept_lookup --edge-types constrained_by,depends_on

# Combined with node type filter
$ raise memory query mod-memory --strategy concept_lookup --edge-types constrained_by --types guardrail
```

### Expected Output

```
Querying memory for: mod-memory
Strategy: concept_lookup

# Memory Query Results

**Query:** `mod-memory`
**Strategy:** concept_lookup
**Concepts:** 4 | **Tokens:** ~120 | **Types:** guardrail=3, module=1

---

## Module (1)

### mod-memory
**Source:** governance/architecture/modules/memory.md | **Created:** 2026-02-08
Manage Rai's persistent memory — patterns, calibration, and sessions stored as JSONL

## Guardrail (3)

### GR-testing
**Source:** governance/guardrails.md | **Created:** 2026-02-08
Testing — >90% coverage on core, pytest fixtures, mock externals...

---
```

### Data Structures

```python
# UnifiedQuery — add edge_types field
class UnifiedQuery(BaseModel):
    query: str
    strategy: UnifiedQueryStrategy = UnifiedQueryStrategy.KEYWORD_SEARCH
    max_depth: int = Field(default=1, ge=0, le=5)
    types: list[NodeType] | None = None          # existing
    edge_types: list[EdgeType] | None = None     # NEW
    limit: int = Field(default=10, ge=1, le=50)
```

```python
# CLI option — same pattern as --types
@memory_app.command()
def query(
    ...
    edge_types: Annotated[
        str | None,
        typer.Option(
            "--edge-types",
            help="Filter by edge types (comma-separated: constrained_by,depends_on,etc.)",
        ),
    ] = None,
    ...
)
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `UnifiedQuery` has `edge_types: list[EdgeType] | None` field (default `None`)
- [ ] `_concept_lookup()` passes `edge_types` to `graph.get_neighbors()`
- [ ] CLI `--edge-types` option parses comma-separated edge types and passes to query
- [ ] Test: concept_lookup with `edge_types=["constrained_by"]` returns only constraint-connected neighbors
- [ ] Test: concept_lookup with `edge_types=None` returns all neighbors (backward compat)
- [ ] Test: CLI `--edge-types constrained_by` produces filtered output

### Should Have

- [ ] `edge_types` silently ignored for `keyword_search` (no error, no effect)

### Must NOT

- [ ] Must NOT break existing queries — `edge_types=None` is identical to current behavior
- [ ] Must NOT add edge-type-aware keyword search (S15.5 scope)

---

## References

**Related ADRs**:
- [ADR-019: Unified Context Graph](../../../dev/decisions/adr-019-unified-context-graph.md)
- [ADR-023: Ontology Graph Extension](../../../dev/decisions/adr-023-ontology-graph-extension.md)

**Related Stories**:
- S15.3: Constraint Edges (provides `constrained_by` edges to filter on)
- S15.5: Query Helpers (consumes edge-type filtering for `find_constraints_for()`)

**Architecture validation**:
- `graph.get_neighbors()` already accepts `edge_types` (graph.py:136-141) — tested in test_graph.py:156-164
- `_concept_lookup()` calls `get_neighbors()` without `edge_types` (query.py:329) — this is the gap
- CLI follows `--types` pattern for consistency (memory.py:105-112)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-08
