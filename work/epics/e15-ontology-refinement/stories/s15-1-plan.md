# Implementation Plan: S15.1 — Ingest All Architecture Docs

## Overview
- **Story:** S15.1
- **Story Points:** 3 SP
- **Size:** S
- **Design:** `s15-1-design.md` (5 decisions, research-validated)
- **Created:** 2026-02-07

## Tasks

### Task 1: Add `architecture` NodeType + write tests (RED → GREEN)
- **Description:** Add `"architecture"` to the `NodeType` Literal in models.py. Then write tests for the three new doc type handlers (architecture_context, architecture_design, architecture_domain_model) — tests go RED first, then implement the handlers in Task 2 to make them GREEN.
- **Files:**
  - `src/raise_cli/context/models.py` — Add `"architecture"` to NodeType
  - `tests/context/test_builder.py` — Add test class `TestLoadArchitectureDocTypes` with tests:
    - `test_loads_architecture_context_doc` — system-context.md frontmatter → arch-context node
    - `test_loads_architecture_design_doc` — system-design.md frontmatter → arch-design node
    - `test_loads_architecture_domain_model_doc` — domain-model.md frontmatter → arch-domain-model node
    - `test_skips_architecture_index_doc` — index.md skipped (generated summary)
    - `test_scans_parent_and_modules_directories` — both dirs scanned
    - `test_existing_module_parsing_unchanged` — backward compatibility
- **TDD Cycle:** RED (write failing tests) → Task 2 makes them GREEN
- **Verification:** `pytest tests/context/test_builder.py::TestLoadArchitectureDocTypes -x` — all tests FAIL (expected)
- **Size:** S
- **Dependencies:** None

### Task 2: Extend builder with type-dispatch (GREEN → REFACTOR)
- **Description:** Refactor `load_architecture()` to scan both `governance/architecture/*.md` and `governance/architecture/modules/*.md`. Refactor `_parse_architecture_doc()` from hard-filtering `type != "module"` to a type-dispatch pattern. Add handler methods for each doc type:
  - `_parse_module_doc(frontmatter, file_path)` — existing logic, extracted
  - `_parse_architecture_context(frontmatter, file_path)` — tech_stack + external_deps → content
  - `_parse_architecture_design(frontmatter, file_path)` — layers summary → content
  - `_parse_architecture_domain_model(frontmatter, file_path)` — bounded_contexts summary → content
  - Skip `architecture_index` (return None)
- **Files:**
  - `src/raise_cli/context/builder.py` — Extend `load_architecture()`, refactor `_parse_architecture_doc()`, add 3 handler methods
- **TDD Cycle:** GREEN (make Task 1 tests pass) → REFACTOR (clean up)
- **Verification:** `pytest tests/context/test_builder.py -x` — all tests pass (new + existing)
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Integration verification
- **Description:** Run full quality suite. Rebuild graph with `raise memory build`. Verify new architecture nodes appear. Run `raise memory query` to confirm queryability.
- **Verification:**
  - `ruff check src/raise_cli/context/ && ruff format --check src/raise_cli/context/`
  - `pyright src/raise_cli/context/models.py src/raise_cli/context/builder.py`
  - `pytest --cov=src/raise_cli/context -x`
  - `uv run raise memory build` — succeeds
  - `uv run raise memory query "architecture" --types architecture` — returns arch-context, arch-design, arch-domain-model
- **Size:** XS
- **Dependencies:** Task 2

## Execution Order

```
Task 1 (schema + tests RED)
    ↓
Task 2 (builder implementation GREEN)
    ↓
Task 3 (integration verification)
```

Sequential — each task depends on the previous.

## Risks

| Risk | Mitigation |
|------|-----------|
| PAT-152: Schema Literal change invalidates cached graph | Rebuild graph in Task 3. Don't rebuild mid-story. |
| YAML parsing edge cases in arch docs | Tests use real frontmatter structure from actual docs |
| Existing module tests break | Task 1 includes backward-compat test |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | — | |
| 2 | M | — | |
| 3 | XS | — | |
