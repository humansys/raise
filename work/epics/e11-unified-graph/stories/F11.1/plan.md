# Implementation Plan: F11.1 Unified Graph Schema

## Overview

| Field | Value |
|-------|-------|
| Feature | F11.1 Unified Graph Schema |
| Epic | E11 Unified Context Architecture |
| Size | S (2 SP) |
| Status | Plan |
| Design | `work/stories/F11.1/design.md` |

## Tasks

### Task 1: Create context module structure

- **Description:** Create `src/raise_cli/context/` module with `__init__.py`
- **Files:** `src/raise_cli/context/__init__.py`
- **Verification:** Module imports successfully
- **Size:** XS
- **Dependencies:** None

### Task 2: Create type definitions and models

- **Description:** Create `models.py` with `NodeType`, `EdgeType`, `ConceptNode`, `ConceptEdge`
- **Files:** `src/raise_cli/context/models.py`
- **Verification:** `pyright src/raise_cli/context/models.py` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Create UnifiedGraph class

- **Description:** Create `graph.py` with `UnifiedGraph` class wrapping NetworkX MultiDiGraph
- **Files:** `src/raise_cli/context/graph.py`
- **Verification:** `pyright src/raise_cli/context/graph.py` passes
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Write unit tests

- **Description:** Create tests for models and graph class
- **Files:** `tests/context/test_models.py`, `tests/context/test_graph.py`
- **Verification:** `pytest tests/context/ -v` passes with >90% coverage
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Update module exports and verify quality

- **Description:** Update `__init__.py` exports, run full quality checks
- **Files:** `src/raise_cli/context/__init__.py`
- **Verification:** `ruff check . && pyright src/ && pytest tests/context/`
- **Size:** XS
- **Dependencies:** Task 4

## Execution Order

```
Task 1 (module structure)
    ↓
Task 2 (models)
    ↓
Task 3 (graph class)
    ↓
Task 4 (tests)
    ↓
Task 5 (exports + quality)
```

Linear dependency chain — no parallel opportunities.

## Risks

| Risk | Mitigation |
|------|------------|
| NetworkX serialization edge cases | Test with realistic node/edge data |
| Type compatibility with existing models | Follow patterns from `memory/models.py` |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1 | XS | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | S | -- | |
| 5 | XS | -- | |

## Success Criteria

- [ ] All 5 tasks complete
- [ ] `ConceptNode` and `ConceptEdge` models defined
- [ ] `UnifiedGraph` class with add/get/save/load operations
- [ ] Unit tests passing with >90% coverage
- [ ] All quality checks pass (ruff, pyright, bandit)

---

*Plan created: 2026-02-03*
*Design: work/stories/F11.1/design.md*
