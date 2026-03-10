# Implementation Plan: RAISE-161 — Windows Compatibility

## Overview
- **Story:** RAISE-161
- **Size:** XS (scoped tight despite many files — changes are mechanical)
- **Created:** 2026-02-17

## Tasks

### Task 1: Create `rai_cli/compat.py` with platform abstractions
- **Description:** Create the compat module with `file_lock`, `file_unlock`, `portable_path`, `to_file_uri`, `secure_permissions`. Platform guard for fcntl/msvcrt inside the module.
- **Files:** `src/rai_cli/compat.py` (create), `tests/test_compat.py` (create)
- **TDD Cycle:** RED (test each function) → GREEN (implement with platform guards) → REFACTOR
- **Verification:** `pytest tests/test_compat.py`
- **Size:** S
- **Dependencies:** None

### Task 2: Wire telemetry writer through compat
- **Description:** Replace `import fcntl` and direct `fcntl.flock` calls in `telemetry/writer.py` with `compat.file_lock`/`file_unlock`.
- **Files:** `src/rai_cli/telemetry/writer.py`
- **Verification:** `pytest tests/telemetry/`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Wire path serialization through compat
- **Description:** Replace all 15 `str(path.relative_to(...))` sites with `compat.portable_path()`. Files: `context/builder.py` (3), `context/analyzers/python.py` (1), `governance/parsers/*.py` (9), `discovery/scanner.py` (1), `cli/commands/memory.py` (1 — file URI fix via `compat.to_file_uri`), `rai_pro/providers/auth/credentials.py` (1 — chmod via `compat.secure_permissions`).
- **Files:** 12 files across parsers, context, discovery, CLI
- **Verification:** `pytest tests/` (full suite — cross-cutting change)
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Fix encoding gaps
- **Description:** Add `encoding="utf-8"` to all `write_text()`/`read_text()` calls that lack it. ~35 call sites across src/. Mechanical find-and-fix, no compat needed.
- **Files:** `cli/commands/init.py` (5), `cli/commands/memory.py` (3), `cli/commands/publish.py` (2), `cli/commands/base.py` (1), `cli/commands/discover.py` (1), `skills/scaffold.py` (1), `skills_base/__init__.py` (1), `viz/generator.py` (2), `context/graph.py` (2), `publish/version.py` (4), `publish/check.py` (2), `onboarding/skills.py` (2), `onboarding/governance.py` (2), `onboarding/bootstrap.py` (6), `session/bundle.py` (1), `rai_base/__init__.py` (1)
- **Verification:** `pytest tests/` + `ruff check src/`
- **Size:** S
- **Dependencies:** None (parallel with Tasks 2-3)

### Task 5: Integration test
- **Description:** Run full test suite, verify no regressions. Verify `import rai_cli` path doesn't hit fcntl at module level.
- **Files:** None (validation only)
- **Verification:** `pytest tests/` + `pyright src/`
- **Size:** XS
- **Dependencies:** Tasks 1-4

## Execution Order
1. Task 1 — compat.py foundation
2. Task 2 + Task 3 + Task 4 (parallel — all independent after Task 1)
3. Task 5 — final validation

## Risks
- **Many files touched:** All changes are mechanical (import swap, add kwarg). Low logic risk, but typo risk. Mitigated by full test suite.
- **scanner.py path handling:** Discovery scanner has its own `rel_str = str(rel_path)` pattern. Need to verify it's for serialization, not filesystem ops.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | compat.py + tests |
| 2 | XS | -- | telemetry writer |
| 3 | S | -- | path serialization (~15 sites) |
| 4 | S | -- | encoding (~35 sites) |
| 5 | XS | -- | integration test |
