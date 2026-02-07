# Implementation Plan: Architecture Knowledge Layer

## Overview
- **Story:** discover-describe
- **Story Points:** 8 SP
- **Size:** L (complex, 6 components)
- **Created:** 2026-02-07
- **Design:** `work/stories/discover-document/design.md`
- **Research:** `work/research/architecture-knowledge-layer/`

## Tasks

### Task 1: Extend Graph Schema (module + depends_on)

- **Description:** Add `module` to NodeType and `depends_on` to EdgeType in context/models.py. This is the foundation — everything else builds on the graph being able to represent module-level knowledge.
- **Files:**
  - `src/raise_cli/context/models.py` — Add to Literal types
  - `tests/context/test_models.py` — Test new types are valid
- **TDD Cycle:** RED (test module node creation) → GREEN (add to Literal) → REFACTOR
- **Verification:** `pytest tests/context/ -x -q`
- **Size:** XS
- **Dependencies:** None

### Task 2: Describer Module — Core Generation Logic

- **Description:** Create `src/raise_cli/discovery/describer.py` with:
  - `ModuleDescription` and `DescribeResult` Pydantic models
  - `detect_modules()` — walk source tree, extract deps from imports, map components
  - `render_module_doc()` — generate Markdown + YAML frontmatter per module
  - `render_index()` — generate compact index (<2K tokens)
  - `merge_with_existing()` — preserve human-authored sections on re-generation
- **Files:**
  - `src/raise_cli/discovery/describer.py` — Create
  - `tests/discovery/test_describer.py` — Create (>90% coverage)
- **TDD Cycle:**
  - RED: Test detect_modules returns correct module list from fixture
  - GREEN: Implement detection from source tree
  - RED: Test render_module_doc produces valid YAML frontmatter
  - GREEN: Implement rendering with f-strings
  - RED: Test merge preserves human sections
  - GREEN: Implement section-aware merge
- **Verification:** `pytest tests/discovery/test_describer.py -x -q --cov=src/raise_cli/discovery/describer --cov-fail-under=90`
- **Size:** L
- **Dependencies:** Task 1 (needs NodeType for model validation)

### Task 3: CLI Command — `raise discover describe`

- **Description:** Add `describe` subcommand to discover_app in discover.py. Options: `--module`, `--index-only`, `--output-dir`, `--output`. Calls describer module and writes output files.
- **Files:**
  - `src/raise_cli/cli/commands/discover.py` — Add describe command
  - `src/raise_cli/output/formatters/discover.py` — Add format_describe_result
  - `tests/cli/commands/test_discover.py` — Add describe command tests
- **TDD Cycle:** RED (test CLI invocation) → GREEN (wire command) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_discover.py -x -q -k describe`
- **Size:** M
- **Dependencies:** Task 2 (needs describer module)

### Task 4: Graph Builder Integration

- **Description:** Extend UnifiedGraphBuilder to parse `governance/architecture/modules/*.md` YAML frontmatter and create `module` nodes with `depends_on` edges in the unified graph.
- **Files:**
  - `src/raise_cli/context/builder.py` — Add architecture doc extraction
  - `tests/context/test_builder.py` — Test module nodes appear in graph
- **TDD Cycle:** RED (test graph contains module nodes after build) → GREEN (implement extraction) → REFACTOR
- **Verification:** `pytest tests/context/test_builder.py -x -q -k module`
- **Size:** M
- **Dependencies:** Task 1 (needs NodeType), Task 2 (needs generated docs to parse)

### Task 5: Dogfood — Generate raise-commons Architecture Docs

- **Description:** Run `raise discover describe` on our own repo. Validate output: correct modules detected, accurate dependencies, useful content, compact index under 2K tokens. Fix any issues found.
- **Files:**
  - `governance/architecture/index.md` — Generated
  - `governance/architecture/modules/*.md` — Generated (11 files)
- **Verification:**
  - All 11 modules documented
  - `wc -w governance/architecture/index.md` approximates <2K tokens
  - YAML frontmatter parses cleanly: `python -c "import yaml; [yaml.safe_load(open(f)) for f in glob('governance/architecture/modules/*.md')]"` (conceptual)
  - `raise memory build` succeeds with module nodes in graph
  - `raise memory query "discovery dependencies"` returns module relationships
- **Size:** M
- **Dependencies:** Tasks 2, 3, 4

### Task 6: Manual Integration Test

- **Description:** End-to-end validation: run full pipeline, verify docs are accurate and useful, check graph queries work, verify re-generation preserves human edits.
- **Verification:**
  - `raise discover describe` completes without error
  - Generated docs are human-readable and accurate
  - `raise memory build && raise memory query "module depends_on"` returns edges
  - Add a custom section to one module doc, re-run describe, verify section preserved
  - All tests pass: `pytest --cov=src --cov-fail-under=90`
  - Linting clean: `ruff check . && ruff format --check .`
- **Size:** S
- **Dependencies:** Task 5

## Execution Order

```
Task 1 (XS) — Schema extension
    ↓
Task 2 (L) — Describer module (core work)
    ↓
Task 3 (M) ──┬── Task 4 (M)   ← parallel after Task 2
              ↓
         Task 5 (M) — Dogfood
              ↓
         Task 6 (S) — Integration test
```

1. **Task 1** — Foundation (schema)
2. **Task 2** — Core logic (biggest task, highest risk)
3. **Tasks 3 + 4** — Can run in parallel (CLI + graph builder are independent)
4. **Task 5** — Dogfood validates everything together
5. **Task 6** — Final integration verification

## Risks

| Risk | Mitigation |
|------|------------|
| Import dependency extraction is fragile | Use AST or simple regex on `from raise_cli.X import` — our codebase follows conventions |
| Module detection misses packages | Walk `src/raise_cli/*/` with `__init__.py` — deterministic |
| Re-generation merge logic is complex | Start simple: replace known sections, append unknown. Iterate if needed. |
| Schema change breaks existing graphs | PAT-152: rebuild graph after schema change. Include in dogfood step. |
| Compact index exceeds 2K tokens | Use terse descriptions. Module map table is the core — prose is optional. |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | L | -- | Core logic — biggest risk |
| 3 | M | -- | |
| 4 | M | -- | Parallel with 3 |
| 5 | M | -- | Dogfood — may surface fixes |
| 6 | S | -- | Final validation |
