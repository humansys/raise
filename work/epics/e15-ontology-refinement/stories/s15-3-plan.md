# Implementation Plan: S15.3 Constraint Edges

## Overview
- **Story:** S15.3 Constraint Edges
- **Story Points:** 3 SP
- **Size:** S
- **Created:** 2026-02-08
- **Design:** `s15-3-design.md`

## Tasks

### Task 1: Guardrails frontmatter + parser scope propagation
- **Description:** Add YAML frontmatter with `constraint_scopes` to `governance/guardrails.md`. Update the guardrails parser to read frontmatter, extract scope per category, and propagate `constraint_scope` to each guardrail's metadata.
- **Files:**
  - `governance/guardrails.md` — Add frontmatter
  - `src/raise_cli/governance/parsers/guardrails.py` — Parse frontmatter, resolve scope, add to metadata
  - `tests/governance/parsers/test_guardrails.py` — Test frontmatter parsing + scope propagation + backward compat (no frontmatter)
- **TDD Cycle:**
  - RED: Test that guardrails with frontmatter get `constraint_scope` in metadata; test that no frontmatter still works
  - GREEN: Implement `_parse_frontmatter()`, `_strip_frontmatter()`, `_extract_prefix()`, update `extract_guardrails()`
  - REFACTOR: Clean up
- **Verification:** `pytest tests/governance/parsers/test_guardrails.py -v && ruff check src/raise_cli/governance/parsers/guardrails.py && pyright --strict src/raise_cli/governance/parsers/guardrails.py`
- **Size:** M
- **Dependencies:** None

### Task 2: Schema + builder constraint edges
- **Description:** Add `constrained_by` to EdgeType. Add `_extract_constraints()` to builder that reads `constraint_scope` from guardrail metadata and creates edges from BC/layer → guardrail. Integrate into `build()` after structural nodes.
- **Files:**
  - `src/raise_cli/context/models.py` — Add `constrained_by` to EdgeType
  - `src/raise_cli/context/builder.py` — Add `_extract_constraints()`, update `build()` to call it after BC/layer extraction
  - `tests/context/test_builder.py` — Test constraint edge extraction: universal scope, specific overrides, graceful degradation
- **TDD Cycle:**
  - RED: Test `_extract_constraints()` with guardrail nodes that have `constraint_scope` metadata; test both `all_bounded_contexts` and specific list scopes; test no guardrails → no edges
  - GREEN: Implement method, integrate into `build()`
  - REFACTOR: Clean up
- **Verification:** `pytest tests/context/test_builder.py -v && pyright --strict src/raise_cli/context/models.py src/raise_cli/context/builder.py`
- **Size:** M
- **Dependencies:** Task 1 (parser produces scope metadata that builder reads)

### Task 3: Integration test — rebuild graph, verify edges
- **Description:** Rebuild graph with `raise memory build`. Verify 195 constrained_by edges created. Verify two-hop traversal: module → BC → constraints works.
- **Verification:** `uv run raise memory build && uv run python -c "..."` to count edges and verify traversal
- **Size:** S
- **Dependencies:** Task 1, Task 2

## Execution Order

1. **Task 1** — Data layer: frontmatter + parser (foundation)
2. **Task 2** — Graph layer: schema + builder (depends on Task 1)
3. **Task 3** — Integration: rebuild + verify (depends on all)

Sequential — each task feeds the next.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontmatter breaks existing guardrail table parsing | Tests fail | Parser strips frontmatter before section finding; backward compat test |
| Scope prefix extraction edge cases | Wrong mappings | Test with real IDs: `MUST-CODE-001`, `SHOULD-CLI-001`, `MUST-ARCH-002` |
| node_by_id doesn't include structural nodes | Missing edges | Update node_by_id before calling _extract_constraints (design specifies this) |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | M | -- | |
| 3 | S | -- | |
