# Implementation Plan: S17.2 — PHP Extractor

## Overview
- **Story:** S17.2
- **Epic:** E17 Multi-Language Discovery
- **Size:** M
- **Created:** 2026-02-09

## Tasks

### Task 1: PHP parser, walker, signatures, and dispatcher wiring
- **Description:** Implement `_get_php_parser()`, `_extract_php_signature()`, `_extract_php_symbols()`, and `extract_php_symbols()`. Wire into `extract_symbols()` dispatcher. Handle class, interface, trait, function, method, and enum node types. Track namespace as state for qualified names. Include visibility and static modifiers in method signatures.
- **Files:** `src/rai_cli/discovery/scanner.py`, `tests/discovery/test_scanner.py`
- **TDD Cycle:**
  - RED: Tests for each PHP symbol kind (class, interface, trait, function, method, enum), namespace-qualified names, class with extends/implements, method visibility/static
  - GREEN: Implement all PHP extraction functions
  - REFACTOR: Ensure consistent helper usage with TS/JS
- **Verification:** `pytest tests/discovery/test_scanner.py -x -q`
- **Size:** M
- **Dependencies:** None (S17.1 already landed SymbolKinds and tree-sitter-php is installed)

### Task 2: Blade template exclusion and edge cases
- **Description:** Ensure `.blade.php` files are skipped during scan (they match `**/*.php` glob but aren't parseable PHP classes). Add exclude pattern or filter. Test edge cases: empty files, PHP files without `<?php` tag, files with only namespace/use statements.
- **Files:** `src/rai_cli/discovery/scanner.py` (scan_directory or extract_php_symbols), `tests/discovery/test_scanner.py`
- **TDD Cycle:**
  - RED: Test that `.blade.php` files are excluded from scan results. Test empty/minimal PHP files don't crash.
  - GREEN: Add blade exclusion logic and defensive handling.
  - REFACTOR: Clean up.
- **Verification:** `pytest tests/discovery/test_scanner.py -x -q`
- **Size:** S
- **Dependencies:** Task 1

### Task 3 (Final): Manual Integration Test
- **Description:** Run `rai discover scan` against zambezi-concierge admin/app/ with `--language php`. Verify symbols from real Laravel files appear correctly. Run full test suite + quality gates.
- **Verification:** `uv run rai discover scan /home/emilio/Code/zambezi-concierge/admin --language php --format summary` shows classes, methods, interfaces. Full gates: `uv run pytest -x -q && uv run ruff check src/ && uv run pyright src/rai_cli/discovery/`
- **Size:** XS
- **Dependencies:** Tasks 1-2

## Execution Order
1. Task 1 — Core extraction (all PHP symbol kinds + namespace + signatures)
2. Task 2 — Blade exclusion + edge cases
3. Task 3 — Integration validation

## Risks
- `language_php()` vs `language_php_only()` — both return same capsule, use `language_php()` (verified in design)
- Blade templates matching `**/*.php` glob — mitigated in Task 2

## Duration Tracking
| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | XS | -- | Integration |
