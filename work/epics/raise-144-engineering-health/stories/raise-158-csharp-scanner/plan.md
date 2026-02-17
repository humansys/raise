# Implementation Plan: C#/.NET Discovery Scanner

## Overview
- **Story:** RAISE-158
- **Size:** S
- **Created:** 2026-02-17

## Tasks

### Task 1: Add tree-sitter-c-sharp dependency and C# extractor
- **Description:** Add `tree-sitter-c-sharp` as optional dependency. Implement `_get_csharp_parser()`, `_extract_csharp_signature()`, `_extract_csharp_symbols()`, and `extract_csharp_symbols()` in scanner.py. Wire into `Language` literal, `EXTENSION_TO_LANGUAGE`, `DEFAULT_LANGUAGE_PATTERNS`, `DEFAULT_EXCLUDE_PATTERNS` (*.Designer.cs), and `extract_symbols()` dispatcher.
- **Files:** `pyproject.toml`, `src/rai_cli/discovery/scanner.py`
- **TDD Cycle:** RED (write TestExtractCsharpSymbols tests first) → GREEN (implement extractor) → REFACTOR
- **Verification:** `uv run pytest tests/discovery/test_scanner.py::TestExtractCsharpSymbols -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Wire CLI validation and update help text
- **Description:** Add `"csharp"` to language validation in `discover.py` (L109) and help string (L58). Update module docstring.
- **Files:** `src/rai_cli/cli/commands/discover.py`
- **TDD Cycle:** RED (test CLI with `--language csharp`) → GREEN (add validation) → REFACTOR
- **Verification:** `uv run pytest tests/ -k "discover" -v` + `uv run rai discover scan --help`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Manual Integration Test
- **Description:** Run `rai discover scan` on a temp directory with real C# files (class, interface, struct, record, enum, namespace, Designer.cs). Verify end-to-end: symbols extracted, Designer.cs excluded, JSON output correct.
- **Verification:** Demo working scan with `--language csharp` and `--output json`
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — core extractor + tests (foundation)
2. Task 2 — CLI wiring (depends on Task 1)
3. Task 3 — integration validation (final)

## Risks
- **tree-sitter-c-sharp API name unknown:** Mitigate by checking `dir()` after install (PAT-E-232)
- **C# node types may differ from expectation:** Mitigate by parsing a sample and inspecting AST before writing tests

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Core extractor + tests |
| 2 | XS | -- | CLI wiring |
| 3 | XS | -- | Integration test |
