# Implementation Plan: S15.2 Bounded Context + Layer Nodes

## Overview
- **Story:** S15.2
- **Story Points:** 3 SP
- **Size:** S
- **Created:** 2026-02-08
- **Design:** `s15-2-design.md`

## Tasks

### Task 1: Schema + Tests RED
- **Description:** Add `bounded_context` and `layer` to NodeType. Add `belongs_to` and `in_layer` to EdgeType. Write failing tests for BC/layer extraction — nodes created, edges created, edge safety (no dangling), graceful degradation when arch nodes missing.
- **Files:**
  - `src/raise_cli/context/models.py` (modify NodeType, EdgeType)
  - `tests/context/test_builder.py` (add TestExtractBoundedContexts, TestExtractLayers classes)
- **TDD Cycle:** RED — schema changes + 6-8 failing tests
- **Verification:** `pytest tests/context/test_builder.py` — new tests FAIL, existing tests PASS. `pyright --strict src/raise_cli/context/models.py` — passes.
- **Size:** S
- **Dependencies:** None

### Task 2: Builder GREEN
- **Description:** Implement `_extract_bounded_contexts()` and `_extract_layers()` in builder. Wire into `load_architecture()` to return nodes + edges. Both methods read from in-memory arch node metadata (no file re-parsing). Create `belongs_to` and `in_layer` edges only when target module node exists.
- **Files:**
  - `src/raise_cli/context/builder.py` (add extraction methods, update `load_architecture()` return, update `build()` to handle edges from load_architecture)
- **TDD Cycle:** GREEN — all tests pass
- **Verification:** `pytest tests/context/test_builder.py` — all GREEN. `ruff check src/ && pyright --strict src/raise_cli/context/`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Integration Verify
- **Description:** Rebuild the real graph with `raise memory build`. Verify BC/layer nodes and edges exist. Query with `raise memory query` to confirm navigability. Spot-check: `mod-memory` → `bc-ontology` via `belongs_to`, `mod-memory` → `lyr-integration` via `in_layer`.
- **Verification:** `raise memory build` succeeds. `raise memory query "ontology" --types bounded_context` returns `bc-ontology`. Full quality gates: `ruff check . && ruff format --check . && pyright --strict src/ && pytest --cov=src --cov-fail-under=90`
- **Size:** S
- **Dependencies:** Task 2

## Execution Order
1. Task 1 — Schema + tests RED (foundation)
2. Task 2 — Builder GREEN (depends on 1)
3. Task 3 — Integration verify (depends on 2)

## Risks
- **Schema change (PAT-152):** Adding NodeType/EdgeType invalidates cached graph. Mitigated by rebuilding in Task 3.
- **build() method signature:** `load_architecture()` currently returns `list[ConceptNode]` but now needs to also return edges. Options: (a) return edges separately, (b) have build() call extraction after load_architecture, (c) change return type to tuple. Design note says approach (b) — extract in build() after all nodes loaded, so module nodes are available for edge safety checks.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1. Schema + Tests RED | S | -- | |
| 2. Builder GREEN | M | -- | |
| 3. Integration Verify | S | -- | |
