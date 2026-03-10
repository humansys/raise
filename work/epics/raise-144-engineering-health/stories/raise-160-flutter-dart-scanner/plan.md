# Implementation Plan: Flutter/Dart Discovery Scanner

## Overview
- **Feature:** RAISE-160
- **Size:** S
- **Created:** 2026-02-17
- **Design:** design.md (reviewed)
- **Pattern:** 4th tree-sitter parser — expect 1.5-1.75x velocity (PAT-E-064)

## Tasks

### Task 1: Add dependency and wire Dart into Language types
- **Description:** Add `tree-sitter-language-pack` to pyproject.toml. Add `"dart"` to `Language` literal, `EXTENSION_TO_LANGUAGE` (`.dart`), and `DEFAULT_LANGUAGE_PATTERNS`. Add `"dart"` case to `extract_symbols()` dispatch.
- **Files:** `pyproject.toml`, `src/rai_cli/discovery/scanner.py`
- **TDD Cycle:** RED — test that `detect_language("foo.dart")` returns `"dart"` and `extract_symbols()` dispatches to dart. GREEN — add types and wiring.
- **Verification:** `pytest tests/discovery/test_scanner_dart.py -x`
- **Size:** S
- **Dependencies:** None

### Task 2: Implement Dart parser and symbol extraction
- **Description:** Implement `_get_dart_parser()` (using `tree-sitter-language-pack`), `_extract_dart_signature()`, `_extract_dart_symbols_from_tree()`, and `extract_dart_symbols()`. Handle: classes, abstract classes, mixins, extensions, enums, top-level functions, methods. First step: install dependency and explore actual Dart AST node types to verify design assumptions.
- **Files:** `src/rai_cli/discovery/scanner.py`, `tests/discovery/test_scanner_dart.py`
- **TDD Cycle:** RED — write tests for each symbol type (class, mixin, extension, enum, function, method). GREEN — implement extraction. REFACTOR — clean up.
- **Verification:** `pytest tests/discovery/test_scanner_dart.py -x -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Manual integration test
- **Description:** Run `rai discover scan` on a real `.dart` file or small Flutter sample to verify end-to-end integration. Run full test suite.
- **Verification:** `pytest tests/ -x --no-cov` passes (2021+), dart symbols appear in scan output
- **Size:** XS
- **Dependencies:** Task 2

## Execution Order
1. Task 1 — wiring (foundation)
2. Task 2 — parser implementation (core work)
3. Task 3 — integration validation (final)

## Risks
- **Dart AST node types may differ from design assumptions:** Mitigation — explore actual grammar before coding extraction logic (built into Task 2).
- **`tree-sitter-language-pack` compatibility with our `tree-sitter>=0.25.2`:** Mitigation — dry-run install already passed, verify at Task 1.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | M | -- | |
| 3 | XS | -- | Integration test |
