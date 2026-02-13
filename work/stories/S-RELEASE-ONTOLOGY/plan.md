# Implementation Plan: S-RELEASE-ONTOLOGY

## Overview
- **Story:** S-RELEASE-ONTOLOGY — Add release as first-class ontology concept
- **Size:** S (3-5 SP)
- **Created:** 2026-02-13
- **Design:** `work/stories/S-RELEASE-ONTOLOGY/design.md`

## Tasks

### Task 1: Add release to type literals
- **Description:** Add `"release"` to `NodeType` in context/models.py and `RELEASE` to `ConceptType` enum in governance/models.py.
- **Files:** `src/rai_cli/context/models.py`, `src/rai_cli/governance/models.py`
- **TDD Cycle:** GREEN only — trivial additions to Literal/Enum, existing tests validate schema.
- **Verification:** `pyright src/rai_cli/context/models.py src/rai_cli/governance/models.py && pytest tests/ -x -q --timeout=30`
- **Size:** XS
- **Dependencies:** None

### Task 2: Create roadmap parser with tests
- **Description:** Create `governance/parsers/roadmap.py` with `extract_releases()` function. Parses the Releases table from `governance/roadmap.md`. Follows `parsers/backlog.py` pattern exactly: regex table parsing, Concept output, normalize_status reuse. Also create `tests/governance/parsers/test_roadmap.py` with tests for: basic extraction, status normalization, epics column parsing, missing/empty file, no table found.
- **Files:** `src/rai_cli/governance/parsers/roadmap.py` (create), `tests/governance/parsers/test_roadmap.py` (create)
- **TDD Cycle:** RED (write parser tests with fixture) → GREEN (implement parser) → REFACTOR
- **Verification:** `pytest tests/governance/parsers/test_roadmap.py -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Create governance/roadmap.md
- **Description:** Create the governance artifact with REL-V2.0 (E18) and REL-V3.0 (E19-E22). Table format per design. Include detail sections for REL-V3.0 with the epic candidates from our synthesis.
- **Files:** `governance/roadmap.md` (create)
- **TDD Cycle:** N/A — governance artifact, validated by parser tests
- **Verification:** Parser tests pass against real file
- **Size:** S
- **Dependencies:** Task 2 (parser must exist to validate format)

### Task 4: Wire parser into extractor
- **Description:** Add roadmap extraction to `GovernanceExtractor.extract_with_result()` — follows the exact pattern of backlog/guardrails/glossary extraction blocks. Add `"roadmap"` case to `_infer_concept_type()`.
- **Files:** `src/rai_cli/governance/extractor.py`
- **TDD Cycle:** RED (add test to existing extractor tests verifying release concepts appear) → GREEN (wire parser) → REFACTOR
- **Verification:** `pytest tests/governance/test_extractor.py -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 5: Wire release edges into graph builder
- **Description:** Add `_infer_release_part_of()` method to `UnifiedGraphBuilder.infer_relationships()`. Creates `part_of` edges from `epic-e{N}` nodes to `rel-*` nodes using the release metadata `epics` list. Same safety pattern as `_infer_part_of` (skip if target node missing). Add test to `tests/context/test_builder_release.py` verifying release nodes appear in graph and part_of edges are created.
- **Files:** `src/rai_cli/context/builder.py`, `tests/context/test_builder_release.py` (create)
- **TDD Cycle:** RED (test that graph build produces release nodes + edges) → GREEN (add builder method + wire into infer_relationships) → REFACTOR
- **Verification:** `pytest tests/context/test_builder_release.py -v`
- **Size:** M
- **Dependencies:** Task 1, Task 4

### Task 6: Full gate validation + integration test
- **Description:** Run full test suite, pyright, ruff. Then run `rai memory build` and verify release nodes appear in the graph. Query the graph to confirm `rel-v3.0` node exists with correct metadata and `part_of` edges connect to epics.
- **Verification:** `ruff check src/ && pyright && pytest tests/ -x -q && rai memory build --project . && rai memory query "release" --types release`
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (XS) — Type literals (foundation, no deps)
    ↓
Task 2 (M) — Parser + tests (depends on types)
    ↓
Task 3 (S) ─── Task 4 (S) — parallel: roadmap.md + extractor wiring
    ↓              ↓
    └──────────────┘
           ↓
Task 5 (M) — Builder wiring + edges (needs extractor + types)
    ↓
Task 6 (XS) — Full validation + integration
```

Tasks 3 and 4 can run in parallel (independent files, both depend only on Task 2).

## Risks

- **Existing test regressions** — NodeType/ConceptType changes could break snapshot-style tests. Mitigation: run full suite after Task 1.
- **Roadmap table format drift** — Parser assumes specific column order. Mitigation: strict regex with clear error on mismatch.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Type literals | XS | -- | |
| 2 — Parser + tests | M | -- | |
| 3 — roadmap.md | S | -- | |
| 4 — Extractor wiring | S | -- | |
| 5 — Builder wiring | M | -- | |
| 6 — Integration test | XS | -- | |
