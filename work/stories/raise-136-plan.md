---
story: RAISE-136
title: Graph schema crash on unknown NodeType — graceful degradation
size: S
date: 2026-02-24
branch: story/standalone/raise-136-graph-nodetype-graceful-degradation
---

## Overview

Root cause (from /rai-debug): `iter_concepts()` in `context/graph.py` has no error
boundary. Any `ValidationError` from `_reconstruct_node()` propagates unhandled and
crashes the process. Fix: wrap in try/except, log warning, skip node.

Affected callers: `rai graph build` (diff path) and `rai session start` (query path).

## Tasks

### T1 — Write failing test (RED)
**Size:** XS
**Dependencies:** none
**Files:** `tests/context/test_graph.py`

Build a `UnifiedGraph` fixture with a node whose required field (`content`) is missing
(simulating schema drift / unknown type), call `iter_concepts()`, assert it does NOT
raise and emits a warning instead.

```
RED: iter_concepts raises ValidationError → test fails
```

**Verification:**
```bash
pytest tests/context/test_graph.py::test_iter_concepts_skips_invalid_node -x
# Expected: FAILED (red — ValidationError raised)
```

---

### T2 — Add error boundary in iter_concepts (GREEN + REFACTOR)
**Size:** XS
**Dependencies:** T1
**Files:** `src/rai_cli/context/graph.py`

Wrap `_reconstruct_node()` call in `iter_concepts()` with `try/except` catching
`pydantic.ValidationError` (and bare `Exception` as fallback). On failure: log
`logger.warning("Skipping node '%s' (type=%s): %s", node_id, data.get('type'), e)`
and `continue`.

Do NOT change `_reconstruct_node` signature — it stays a throwing function (easier
to unit-test in isolation).

```python
def iter_concepts(self) -> Iterator[ConceptNode]:
    node_id: str
    for node_id in self.graph.nodes:
        data: dict[str, Any] = dict(self.graph.nodes[node_id])
        try:
            yield self._reconstruct_node(node_id, data)
        except Exception as e:
            logger.warning(
                "Skipping node '%s' (type=%s): %s",
                node_id,
                data.get("type", "unknown"),
                e,
            )
```

**Verification:**
```bash
pytest tests/context/test_graph.py::test_iter_concepts_skips_invalid_node -x
# Expected: PASSED (green)
pytest tests/context/ -x
# Expected: all pass
ruff check src/rai_cli/context/graph.py
pyright src/rai_cli/context/graph.py
```

---

### T3 — Integration test: rai graph build survives corrupt graph
**Size:** XS
**Dependencies:** T2
**Files:** `tests/context/test_graph.py` or `tests/graph/test_filesystem_backend.py`

Build a minimal corrupt graph JSON (missing `content` field on one node), persist
it to a temp file, load it, call `iter_concepts()`, verify the valid nodes are
returned and the invalid node is silently skipped (no exception raised).

This mirrors the actual crash path: `build()` calls `backend.load()` then
`diff_graphs(old_graph, graph)` which iterates `old_graph.iter_concepts()`.

**Verification:**
```bash
pytest tests/ -x
ruff check src/
pyright src/
# rai graph build (manual) — verify no crash with existing graph
```

---

## Execution Order

```
T1 (RED test) → T2 (GREEN fix) → T3 (integration test)
```

Sequential — each task depends on the prior.

## Risks

| Risk | Mitigation |
|------|-----------|
| `Exception` too broad — masks real bugs | Log with node_id + type for debuggability |
| Skipped nodes silently corrupt query results | Warning is emitted; graph build logs node count |
| `iter_relationships()` has same gap | Out of scope — `ConceptEdge.model_validate` is simpler; add note in follow-up |

## Follow-up (parking lot)

- `iter_relationships()` has no error boundary either — same pattern, lower risk
  (edges have fewer required fields). Track as separate XS.
