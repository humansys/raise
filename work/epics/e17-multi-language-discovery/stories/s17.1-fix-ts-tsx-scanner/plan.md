# Implementation Plan: S17.1 — Fix TS/TSX Scanner

## Overview
- **Story:** S17.1
- **Epic:** E17 Multi-Language Discovery
- **Size:** M
- **Created:** 2026-02-09

## Tasks

### Task 1: Expand SymbolKind and fix TS glob pattern
- **Description:** Add new symbol kinds to the `SymbolKind` Literal type and fix the TypeScript glob pattern to include `.tsx` files. Also add `"svelte"` and `"php"` to the `Language` Literal and `EXTENSION_TO_LANGUAGE` map (foundation for S17.2/S17.3).
- **Files:** `src/raise_cli/discovery/scanner.py` (SymbolKind, Language, EXTENSION_TO_LANGUAGE, DEFAULT_LANGUAGE_PATTERNS)
- **TDD Cycle:**
  - RED: Test that `detect_language("foo.tsx")` returns `"typescript"`, `DEFAULT_LANGUAGE_PATTERNS["typescript"]` matches `.tsx` files, and `SymbolKind` accepts `"enum"`, `"type_alias"`, `"constant"`.
  - GREEN: Update Literal types, extension map, glob pattern.
  - REFACTOR: Ensure consistency.
- **Verification:** `pytest tests/discovery/test_scanner.py -x -q`
- **Size:** S
- **Dependencies:** None

### Task 2: TSX parser dispatch and new symbol extraction
- **Description:** Modify `_get_ts_parser()` to accept a file path/extension and dispatch `.tsx` to `language_tsx()`. Add extraction of `enum_declaration`, `type_alias_declaration`, and exported `const` variable declarations in `_extract_ts_js_symbols()`. Add signature extraction for new node types in `_extract_ts_signature()`.
- **Files:** `src/raise_cli/discovery/scanner.py` (_get_ts_parser, extract_typescript_symbols, _extract_ts_js_symbols, _extract_ts_signature)
- **TDD Cycle:**
  - RED: Test that `.tsx` source with JSX parses correctly. Test that enum, type alias, and const export produce correct Symbol objects with correct kinds.
  - GREEN: Implement parser dispatch and new node type handling.
  - REFACTOR: Clean up walker logic.
- **Verification:** `pytest tests/discovery/test_scanner.py -x -q`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Exclude-based hierarchy routing
- **Description:** Refactor `build_hierarchy()` in analyzer.py to use exclude-based routing: class and method get special treatment, everything else becomes a standalone component. Update the interface kind handling too (currently it's extracted in scanner but not routed in hierarchy).
- **Files:** `src/raise_cli/discovery/analyzer.py` (build_hierarchy)
- **TDD Cycle:**
  - RED: Test that symbols with kind="enum", "type_alias", "constant" appear in hierarchy output as standalone components. Test that existing class/method folding still works.
  - GREEN: Flip the routing logic from include-based to exclude-based.
  - REFACTOR: Simplify the second pass.
- **Verification:** `pytest tests/discovery/test_analyzer.py -x -q`
- **Size:** S
- **Dependencies:** Task 1 (needs new SymbolKind values)

### Task 4: Formatter counts for new symbol kinds
- **Description:** Update `_format_scan_summary()` to show counts for enums, type aliases, and constants when present (same conditional pattern as interfaces/modules).
- **Files:** `src/raise_cli/output/formatters/discover.py` (_format_scan_summary)
- **TDD Cycle:**
  - RED: Test that summary output includes enum/type_alias/constant counts when symbols of those kinds exist.
  - GREEN: Add conditional print lines.
  - REFACTOR: None needed.
- **Verification:** `pytest tests/ -x -q -k "format"`
- **Size:** XS
- **Dependencies:** Task 1

### Task 5: Manual integration test
- **Description:** Run `raise discover scan` against real TypeScript source with `.tsx` files, enums, const exports, and type aliases. Verify symbols appear in output. Run full test suite + quality gates.
- **Verification:** `uv run pytest tests/ -x -q && uv run ruff check src/ && uv run pyright src/raise_cli/discovery/`
- **Size:** XS
- **Dependencies:** Tasks 1-4

## Execution Order

1. Task 1 — Foundation (types, globs, extensions)
2. Task 2 — Core (parser dispatch + extraction) — depends on Task 1
3. Task 3 — Hierarchy refactor — depends on Task 1, parallel with Task 2
4. Task 4 — Formatter — depends on Task 1, parallel with Tasks 2-3
5. Task 5 — Integration validation — depends on all

Tasks 2, 3, 4 are independent of each other (only depend on Task 1), but sequential execution is fine for single-session work.

## Risks

- `Path.glob("**/*.{ts,tsx}")` may not support brace expansion → Mitigation: use two globs or `**/*.ts` + separate `**/*.tsx` pattern
- tree-sitter-typescript `language_tsx()` API may differ from `language_typescript()` → Mitigation: check import in Task 2

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1 | S | -- | |
| 2 | M | -- | |
| 3 | S | -- | |
| 4 | XS | -- | |
| 5 | XS | -- | Integration |
