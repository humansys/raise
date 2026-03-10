# Implementation Plan: F3.3 Memory Graph

## Overview

- **Feature:** F3.3 Memory Graph
- **Story Points:** 2-3 SP
- **Feature Size:** S
- **Created:** 2026-02-02
- **Design:** `design.md`

## Tasks

### Task 1: Models + Loader

- **Description:** Create memory data models and JSONL loader
- **Files:**
  - `src/rai_cli/memory/__init__.py` (create)
  - `src/rai_cli/memory/models.py` (create)
  - `src/rai_cli/memory/loader.py` (create)
  - `tests/memory/__init__.py` (create)
  - `tests/memory/test_models.py` (create)
  - `tests/memory/test_loader.py` (create)
- **Verification:** `pytest tests/memory/test_models.py tests/memory/test_loader.py -v`
- **Size:** S
- **Dependencies:** None

**Deliverables:**
- `MemoryConceptType` enum (pattern, calibration, session)
- `MemoryRelationshipType` enum (learned_from, related_to, validates, applies_to)
- `MemoryConcept` Pydantic model
- `MemoryRelationship` Pydantic model
- `load_jsonl()` function → list of MemoryConcept
- Tests with real `.rai/memory/*.jsonl` fixtures

---

### Task 2: Builder + Cache

- **Description:** Build ConceptGraph from concepts, infer relationships, add caching
- **Files:**
  - `src/rai_cli/memory/builder.py` (create)
  - `src/rai_cli/memory/cache.py` (create)
  - `tests/memory/test_builder.py` (create)
  - `tests/memory/test_cache.py` (create)
- **Verification:** `pytest tests/memory/test_builder.py tests/memory/test_cache.py -v`
- **Size:** S
- **Dependencies:** Task 1

**Deliverables:**
- `MemoryGraphBuilder` class wrapping E2's `ConceptGraph`
- Relationship inference rules:
  - `learned_from`: pattern/calibration → session (via `learned_from` field)
  - `related_to`: shared context keywords
  - `validates`: calibration → pattern (same feature)
  - `applies_to`: pattern → context domains
- `MemoryCache` class with mtime-based staleness check
- `graph.json` caching in `.rai/memory/`

---

### Task 3: Query + CLI

- **Description:** Implement memory search and CLI commands
- **Files:**
  - `src/rai_cli/memory/query.py` (create)
  - `src/rai_cli/cli/commands/memory.py` (create)
  - `tests/memory/test_query.py` (create)
  - `tests/memory/test_integration.py` (create)
  - `tests/cli/test_memory_commands.py` (create)
- **Verification:** `pytest tests/memory/ tests/cli/test_memory_commands.py -v`
- **Size:** S
- **Dependencies:** Task 2

**Deliverables:**
- `MemoryQuery` class with:
  - `search(keywords, max_results, recency_weight)` → `MemoryQueryResult`
  - Keyword matching + BFS expansion
  - Recency weighting (newer = higher score)
  - Token estimation
- CLI commands:
  - `rai memory query "topic"` — search and display results
  - `rai memory dump --format json|md` — export memory stats/content
- Integration tests: full flow load → build → cache → query

---

## Execution Order

```
Task 1: Models + Loader (foundation)
    ↓
Task 2: Builder + Cache (graph construction)
    ↓
Task 3: Query + CLI (user interface)
```

Sequential — each task builds on previous.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| E2 ConceptGraph API mismatch | Low | Medium | Review E2 code before Task 2 |
| JSONL schema variations | Low | Low | Validate against actual `.rai/` files |
| Cache invalidation edge cases | Low | Low | Start with simple mtime check |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1: Models + Loader | S | 15-30 min | -- | |
| 2: Builder + Cache | S | 15-30 min | -- | |
| 3: Query + CLI | S | 15-30 min | -- | |
| **Total** | **S** | **45-90 min** | -- | Target: 2-3x velocity |

## Quality Gates

Before marking complete:
- [ ] All tests passing: `pytest tests/memory/ -v`
- [ ] Type checking: `pyright src/rai_cli/memory/`
- [ ] Linting: `ruff check src/rai_cli/memory/`
- [ ] Coverage >90%: `pytest --cov=src/rai_cli/memory`
- [ ] CLI works: `rai memory query "test"` returns results

## Notes

- Wrap E2 ConceptGraph, don't modify it
- Use actual `.rai/memory/*.jsonl` for test fixtures
- Token estimate: `len(content) // 4` (same as E2)
