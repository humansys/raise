# Implementation Plan: S17.4 — Analyzer Adjustments

## Overview
- **Feature:** S17.4
- **Size:** S
- **Created:** 2026-02-10

## Tasks

### Task 1: Extend DEFAULT_CATEGORY_MAP with multi-language patterns
- **Description:** Add Laravel (Controllers/, Models/, Middleware/, etc.) and Svelte/TS (components/, stores/, lib/, etc.) path patterns to DEFAULT_CATEGORY_MAP
- **Files:** `src/raise_cli/discovery/analyzer.py`, `tests/discovery/test_analyzer.py`
- **TDD Cycle:** RED (test PHP/Svelte paths return correct categories) → GREEN (add patterns) → REFACTOR
- **Verification:** `pytest tests/discovery/test_analyzer.py -x -q`
- **Size:** S
- **Dependencies:** None

### Task 2: Generalize _file_to_module for non-Python extensions
- **Description:** Handle `app/`, `lib/` source prefixes and `.php`, `.ts`, `.tsx`, `.svelte`, `.js`, `.jsx` extensions. Add constants `_SOURCE_PREFIXES` and `_CODE_EXTENSIONS`.
- **Files:** `src/raise_cli/discovery/analyzer.py`, `tests/discovery/test_analyzer.py`
- **TDD Cycle:** RED (test PHP/TS/Svelte paths produce correct module paths) → GREEN (generalize function) → REFACTOR
- **Verification:** `pytest tests/discovery/test_analyzer.py -x -q`
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Quality gates + manual integration test
- **Description:** Run full quality gates (ruff, pyright, bandit, tests). Then run `raise discover analyze` on a real scan to verify categories and module paths look correct for non-Python files.
- **Verification:** All gates pass + visual inspection of analyze output
- **Size:** XS
- **Dependencies:** Tasks 1, 2

## Execution Order
1. Task 1 (category map — independent)
2. Task 2 (module paths — independent, but sequential in single session)
3. Task 3 (gates + integration validation)

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
