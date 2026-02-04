# Implementation Plan: F11.2 Graph Builder

## Overview
- **Feature:** F11.2 Graph Builder
- **Epic:** E11 Unified Context Architecture
- **Story Points:** 2 SP
- **Feature Size:** M
- **Created:** 2026-02-03

## Tasks

### Task 1: Skill Extractor
- **Description:** Create new module to parse SKILL.md YAML frontmatter and return ConceptNode
- **Files:**
  - `src/raise_cli/context/extractors/__init__.py` (new)
  - `src/raise_cli/context/extractors/skills.py` (new)
  - `tests/context/extractors/__init__.py` (new)
  - `tests/context/extractors/test_skills.py` (new)
- **TDD Cycle:**
  - RED: Test `extract_skill_metadata()` returns ConceptNode from SKILL.md
  - RED: Test `extract_all_skills()` finds all skills in directory
  - GREEN: Implement YAML frontmatter parsing
  - REFACTOR: Extract constants, clean up
- **Verification:** `uv run pytest tests/context/extractors/ -v`
- **Size:** S
- **Dependencies:** None

### Task 2: UnifiedGraphBuilder with Loaders
- **Description:** Create UnifiedGraphBuilder class with `load_governance()`, `load_memory()`, `load_work()`, `load_skills()` methods. Each returns `list[ConceptNode]`.
- **Files:**
  - `src/raise_cli/context/builder.py` (new)
  - `tests/context/test_builder.py` (new)
- **TDD Cycle:**
  - RED: Test `load_governance()` converts Concept → ConceptNode
  - RED: Test `load_memory()` reads JSONL → ConceptNode
  - RED: Test `load_work()` converts epic/feature → ConceptNode
  - RED: Test `load_skills()` uses skill extractor
  - GREEN: Implement each loader
  - REFACTOR: DRY conversion helpers
- **Verification:** `uv run pytest tests/context/test_builder.py -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Relationship Inference
- **Description:** Add `infer_relationships()` method with explicit edges (weight=1.0) and heuristic edges (weight<1.0)
- **Files:**
  - `src/raise_cli/context/builder.py` (extend)
  - `tests/context/test_builder.py` (extend)
- **TDD Cycle:**
  - RED: Test explicit `learned_from` edges (pattern → session)
  - RED: Test explicit `part_of` edges (feature → epic)
  - RED: Test explicit skill prerequisite edges
  - RED: Test inferred `related_to` edges (shared keywords)
  - GREEN: Implement inference rules
  - REFACTOR: Extract inference helpers
- **Verification:** `uv run pytest tests/context/test_builder.py -v -k "infer"`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: CLI Command
- **Description:** Add `--unified` flag to `raise graph build` command. When set, use UnifiedGraphBuilder and save to `.raise/graph/unified.json`
- **Files:**
  - `src/raise_cli/cli/commands/graph.py` (extend)
  - `src/raise_cli/context/__init__.py` (export builder)
  - `tests/cli/commands/test_graph.py` (extend)
- **TDD Cycle:**
  - RED: Test `raise graph build --unified` creates unified graph file
  - RED: Test output shows node/edge counts by type
  - GREEN: Implement CLI flag and integration
  - REFACTOR: Clean up output formatting
- **Verification:** `uv run pytest tests/cli/commands/test_graph.py -v -k "unified"`
- **Size:** S
- **Dependencies:** Task 3

### Task 5 (Final): Manual Integration Test
- **Description:** Build actual unified graph from real project data, verify it contains expected nodes and edges
- **Verification:**
  - Run `uv run raise graph build --unified`
  - Verify `.raise/graph/unified.json` created
  - Check node count >50 (patterns + governance + work + skills)
  - Check edges exist between domains
  - Demo: query a pattern, see related skill via edge
- **Size:** XS
- **Dependencies:** Task 4

## Execution Order

```
Task 1 (Skill Extractor) ─► Task 2 (Loaders) ─► Task 3 (Inference) ─► Task 4 (CLI) ─► Task 5 (Integration)
```

Linear dependency chain — each task builds on the previous.

## Risks

| Risk | Mitigation |
|------|------------|
| E2 extractor output format mismatch | Inspect actual output, add adapter if needed |
| Memory JSONL field variations | Handle missing fields with defaults |
| Skill frontmatter edge cases | Graceful error handling, skip malformed |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1 - Skill Extractor | S | 20m | -- | |
| 2 - Loaders | M | 35m | -- | |
| 3 - Inference | S | 20m | -- | |
| 4 - CLI | S | 15m | -- | |
| 5 - Integration | XS | 10m | -- | |
| **Total** | **M** | **~90m** | -- | |

---

*Plan created: 2026-02-03*
*Ready for: /feature-implement*
