# Implementation Plan: S17.3 — Svelte Extractor

## Overview
- **Story:** S17.3
- **Size:** S
- **Created:** 2026-02-09

## Tasks

### Task 1: Svelte extractor core + tests
- **Description:** Implement `_get_svelte_parser()`, `_extract_svelte_script_info()`, and `extract_svelte_symbols()` in `scanner.py`. Two-pass approach: parse with tree-sitter-svelte to find `<script>` blocks, detect `lang="ts"` attribute, re-parse script content with JS/TS parser. Register component symbol. Add line offset correction. Wire into `extract_symbols()` dispatcher.
- **Files:**
  - Modify: `src/raise_cli/discovery/scanner.py`
  - Modify: `tests/discovery/test_scanner.py`
- **TDD Cycle:**
  - RED: Tests for `extract_svelte_symbols()` — JS script block, TS script block, no script block, empty script, component registration, line number correctness
  - RED: Test for `extract_symbols("...", "test.svelte", "svelte")` dispatch
  - GREEN: Implement extractor functions
  - REFACTOR: Clean up
- **Verification:** `pytest tests/discovery/test_scanner.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: CLI integration + scan_directory test
- **Description:** Verify `scan_directory(path, language="svelte")` finds `.svelte` files and extracts symbols. Test with a temp directory containing `.svelte` files.
- **Files:**
  - Modify: `tests/discovery/test_scanner.py`
- **TDD Cycle:**
  - RED: Test `scan_directory` with `.svelte` files in tmp_path
  - GREEN: Should work already since EXTENSION_TO_LANGUAGE and DEFAULT_LANGUAGE_PATTERNS already include svelte
  - REFACTOR: Verify all checks pass
- **Verification:** `pytest tests/discovery/test_scanner.py -v && uv run ruff check src/ && uv run pyright`
- **Size:** S
- **Dependencies:** Task 1

### Task 3 (Final): Manual Integration Test
- **Description:** Run `raise discover scan` on a real `.svelte` file or small Svelte project to validate end-to-end. Verify component symbol and script symbols appear in output.
- **Verification:** Demo working with CLI
- **Size:** XS
- **Dependencies:** Tasks 1-2

## Execution Order
1. Task 1 — core extractor + unit tests (foundation)
2. Task 2 — scan_directory integration test (depends on 1)
3. Task 3 — manual integration test (final validation)

## Risks
- **Line offset calculation:** Script content starts mid-file; off-by-one risk → mitigate with explicit line number test
- **`<script context="module">` handling:** Svelte has two script blocks (instance + module); SHOULD handle both but won't block

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Core extractor |
| 2 | S | -- | Integration |
| 3 | XS | -- | Manual test |
