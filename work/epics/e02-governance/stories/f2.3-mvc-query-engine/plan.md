# Implementation Plan: F2.3 MVC Query Engine

## Overview
- **Feature:** F2.3 MVC Query Engine
- **Story Points:** 2 SP
- **Feature Size:** S (4 components, 4 query strategies, moderate complexity)
- **Created:** 2026-01-31

## Summary

Build a query engine for extracting Minimum Viable Context (MVC) from the concept graph. The engine supports 4 query strategies (concept lookup, keyword search, relationship traversal, related concepts) and multiple output formats (markdown, JSON).

**Key Design Decisions:**
- Reuse F2.2's graph traversal infrastructure (no duplication)
- Simple keyword matching (no NLP libraries needed)
- Token estimation via spike-validated heuristic (words * 1.3)
- Strategy auto-detection from query patterns

## Tasks

### Task 1: Create Query Models
- **Description:** Implement `QueryStrategy`, `MVCQuery`, `MVCResult`, and `MVCMetadata` models in `src/raise_cli/governance/query/models.py` with Pydantic validation and serialization support
- **Files:**
  - CREATE `src/raise_cli/governance/query/__init__.py`
  - CREATE `src/raise_cli/governance/query/models.py`
  - CREATE `tests/governance/query/__init__.py`
  - CREATE `tests/governance/query/test_models.py`
- **Verification:**
  - `MVCQuery` validates query string and filters
  - `MVCResult` includes concepts and metadata
  - `MVCMetadata` includes token_estimate, paths, execution_time_ms
  - JSON serialization/deserialization works (`to_json()`, `from_json()`)
  - `pyright --strict src/raise_cli/governance/query/models.py` passes
  - `pytest tests/governance/query/test_models.py -v --cov=src/raise_cli/governance/query/models.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** None (uses F2.1's Concept model, F2.2's ConceptGraph)

### Task 2: Implement Query Strategies
- **Description:** Create `strategies.py` with 4 strategy implementations: `query_concept_lookup()`, `query_keyword_search()`, `query_relationship_traversal()`, `query_related_concepts()`. Each returns list of concepts matching the strategy criteria.
- **Files:**
  - CREATE `src/raise_cli/governance/query/strategies.py`
  - CREATE `tests/governance/query/test_strategies.py`
- **Verification:**
  - **CONCEPT_LOOKUP**: Returns concept by ID + 1-hop dependencies (governed_by, implements)
  - **KEYWORD_SEARCH**: Matches keywords in section/content with optional type filter
  - **RELATIONSHIP_TRAVERSAL**: Uses F2.2's `traverse_bfs()` with edge type filtering
  - **RELATED_CONCEPTS**: Returns concepts with >2 shared keywords, sorted by relevance
  - All strategies handle edge cases (empty graph, no matches, invalid IDs)
  - `pytest tests/governance/query/test_strategies.py -v --cov=src/raise_cli/governance/query/strategies.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Implement Query Engine
- **Description:** Create `engine.py` with `MVCQueryEngine` class that orchestrates: load graph → auto-detect strategy → execute strategy → calculate metadata (token estimate, paths, execution time) → return MVCResult
- **Files:**
  - CREATE `src/raise_cli/governance/query/engine.py`
  - CREATE `tests/governance/query/test_engine.py`
- **Verification:**
  - `from_cache()` loads graph from `.raise/cache/graph.json`
  - `query()` executes correct strategy based on MVCQuery params
  - Token estimation uses `estimate_tokens(concepts)` helper (words * 1.3)
  - Relationship paths traced from query concept to results
  - Execution time tracked in metadata
  - Integration test: Query real raise-commons graph achieves >90% token savings
  - `pytest tests/governance/query/test_engine.py -v --cov=src/raise_cli/governance/query/engine.py --cov-fail-under=90` passes
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Implement Output Formatters
- **Description:** Create `formatters.py` with formatters for markdown and JSON. Markdown formatter includes concept sections with relationship annotations. Include `to_file()` utility.
- **Files:**
  - CREATE `src/raise_cli/governance/query/formatters.py`
  - CREATE `tests/governance/query/test_formatters.py`
- **Verification:**
  - `to_markdown()` formats MVCResult as markdown with headers, relationship paths, token estimate
  - `to_json()` formats as structured JSON (concepts array + metadata object)
  - `to_file(path, format)` writes result to file in specified format
  - Markdown output includes: query, strategy, concepts with type/file annotations, relationship paths, savings estimate
  - `pytest tests/governance/query/test_formatters.py -v --cov=src/raise_cli/governance/query/formatters.py --cov-fail-under=90` passes
- **Size:** S
- **Dependencies:** Task 1

### Task 5: Add CLI Command `raise context query`
- **Description:** Create new CLI command group `context` with `query` subcommand. Support options: `--format (markdown|json)`, `--output <path>`, `--strategy <strategy>`, `--max-depth <int>`
- **Files:**
  - CREATE `src/raise_cli/cli/commands/context.py`
  - MODIFY `src/raise_cli/cli/app.py` (register context_app)
  - CREATE `tests/cli/commands/test_context.py`
- **Verification:**
  - `raise context query "req-rf-05"` displays MVC in markdown format
  - `raise context query "validation" --format json` outputs JSON
  - `raise context query "req-rf-05" --output context.md` writes to file
  - `raise context query "req-rf-05" --strategy relationship_traversal --max-depth 2` works with explicit params
  - CLI displays token estimate and savings percentage
  - Error handling: graph not found → suggests `raise graph build`
  - `pytest tests/cli/commands/test_context.py -v` passes
- **Size:** M
- **Dependencies:** Task 3, Task 4

### Task 6: Integration Tests and Documentation
- **Description:** Create integration tests using real raise-commons governance graph. Verify >90% token savings. Update component catalog and add docstrings to all public APIs.
- **Files:**
  - CREATE `tests/governance/query/test_integration.py`
  - MODIFY `dev/components.md` (add query module entry)
  - MODIFY all `src/raise_cli/governance/query/*.py` (add/verify docstrings)
- **Verification:**
  - Integration test: Query RF-05 from real graph returns <500 tokens vs ~6,796 manual
  - Integration test: Keyword search returns relevant concepts only
  - Integration test: End-to-end CLI workflow (extract → build → query) works
  - All public APIs have Google-style docstrings
  - Component catalog includes: query module location, purpose, public API, dependencies
  - `pytest tests/governance/query/test_integration.py -v` passes
  - `pytest --cov=src/raise_cli/governance/query --cov-fail-under=90` passes (full module coverage)
- **Size:** S
- **Dependencies:** Task 5

## Execution Order

**Sequential dependencies:**
1. Task 1 (models - foundation)
2. Task 2 (strategies - depends on models)
3. Task 3 (engine - depends on strategies)

**Parallel after Task 1:**
- Task 4 (formatters - depends only on models)

**Final integration:**
5. Task 5 (CLI - depends on engine + formatters)
6. Task 6 (integration tests + docs - depends on all)

**Optimized sequence:**
1. Task 1 (models)
2. Task 2 + Task 4 in parallel (strategies + formatters)
3. Task 3 (engine)
4. Task 5 (CLI)
5. Task 6 (integration + docs)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Token estimation inaccurate | Medium | Use spike-validated heuristic (words * 1.3); adjust if needed |
| Query strategies too slow | Low | Reuse F2.2's BFS (proven <100ms); keyword matching is O(n) |
| Strategy auto-detection complex | Medium | Start with explicit strategy param; add auto-detection in Task 3 as nice-to-have |
| Markdown formatting breaks rendering | Low | Use simple markdown syntax; test with commonmark parser |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1 | S | 20 min | -- | Models straightforward, similar to F2.2 Task 1 |
| 2 | M | 45 min | -- | 4 strategies, most reuse existing code |
| 3 | M | 40 min | -- | Orchestration + metadata calculation |
| 4 | S | 20 min | -- | Formatting is string manipulation |
| 5 | M | 40 min | -- | CLI integration, similar to F2.2 Task 5 |
| 6 | S | 25 min | -- | Integration tests + docs |
| **Total** | | **~3 hours** | -- | 2 SP = 3-4 hours; on track |

**Calibration notes:**
- F2.2 delivered 2.3-3.2x faster than estimate
- F2.3 similar complexity, expect 2-3x velocity multiplier
- Actual target: 60-90 min (vs 180 min estimate)

## Acceptance Criteria (from Design)

**MUST:**
- [x] Implement 4 query strategies (concept lookup, keyword search, relationship traversal, related concepts)
- [x] Load graph from JSON (`.raise/cache/graph.json`)
- [x] Return MVCResult with concepts + metadata (token estimate, paths)
- [x] Format as markdown (sections, relationship annotations)
- [x] Format as JSON (structured output)
- [x] CLI command `raise context query <query>` with `--format` and `--output` options
- [x] Token estimation using words * 1.3 heuristic
- [x] Include relationship paths in metadata
- [x] >90% test coverage on query module
- [x] All code passes `pyright --strict`

**SHOULD:**
- [ ] Auto-detect strategy from query pattern (nice-to-have in Task 3)
- [ ] Query result caching (defer to post-MVP)
- [ ] Include confidence scores in results (metadata already supports this)
- [ ] Warn if query returns 0 concepts (CLI error handling)
- [ ] Suggest alternatives if query fails (defer to post-MVP)

## Next Steps

After plan approval:
1. Execute tasks in order (1 → 2+4 parallel → 3 → 5 → 6)
2. Track actual duration for calibration
3. Update `progress.md` as tasks complete
4. Run full test suite before PR
5. Create retrospective after story complete

---

*Ready for: `/story-implement`*
