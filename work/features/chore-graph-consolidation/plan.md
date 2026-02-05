# Chore: Graph Consolidation — Deprecate MemoryGraph

> **Type:** Maintenance / Technical Debt
> **Branch:** v2 (direct)
> **Created:** 2026-02-05
> **Estimated:** 2-3 hours

---

## Objective

Consolidate from two graph systems to one. Remove redundant MemoryGraph, use UnifiedGraph for all queries.

**Before:**
```
JSONL files → MemoryGraph (.rai/memory/graph.json)
           → UnifiedGraph (.raise/graph/unified.json) [includes memory]
```

**After:**
```
JSONL files → UnifiedGraph (.raise/graph/unified.json) [single source]
```

---

## Tasks

### Task 1: Update `raise memory query` to use UnifiedGraph
- [ ] Modify `src/raise_cli/cli/commands/memory.py`
- [ ] Use `UnifiedQueryEngine` with `--types pattern,calibration,session` filter
- [ ] Preserve existing output format
- [ ] Update tests

### Task 2: Deprecate MemoryGraph classes
- [ ] Mark `MemoryGraph`, `MemoryGraphBuilder`, `MemoryCache` as deprecated
- [ ] Add deprecation warnings if called directly
- [ ] Keep code for one release cycle (or remove if no external users)

### Task 3: Remove `.rai/memory/graph.json` generation
- [ ] Remove cache file generation from memory module
- [ ] Update `raise memory` commands that touch the cache
- [ ] Clean up existing graph.json files (optional)

### Task 4: Update skill references
- [ ] Check if any skills reference memory graph specifically
- [ ] Update to use unified graph query

### Task 5: Update tests
- [ ] Remove/update tests for deprecated classes
- [ ] Ensure memory query tests pass with new implementation
- [ ] Verify unified graph includes memory data correctly

### Task 6: Documentation
- [ ] Update any docs referencing two graphs
- [ ] Note deprecation in changelog/release notes

---

## Files to Modify

| File | Change |
|------|--------|
| `src/raise_cli/cli/commands/memory.py` | Use UnifiedQueryEngine |
| `src/raise_cli/memory/__init__.py` | Add deprecation notices |
| `src/raise_cli/memory/cache.py` | Deprecate or remove |
| `src/raise_cli/memory/builder.py` | Deprecate MemoryGraph |
| `src/raise_cli/memory/query.py` | Deprecate or redirect |
| `tests/memory/test_*.py` | Update for new behavior |

---

## Done Criteria

- [x] `raise memory query` works using UnifiedGraph
- [x] No new `.rai/memory/graph.json` created
- [x] All tests pass (1135 passed)
- [x] Deprecation warnings added for old classes

---

## Progress

| Task | Status | Notes |
|------|--------|-------|
| Task 1 | Done | CLI commands use UnifiedGraph |
| Task 2 | Done | Runtime deprecation warnings added |
| Task 3 | Done | Removed .rai/memory/graph.json |
| Task 4 | Done | Updated session-close skill reference |
| Task 5 | Done | Memory module tests pass (107), CLI tests pass (16) |
| Task 6 | Done | Module docstrings, skill references updated |
