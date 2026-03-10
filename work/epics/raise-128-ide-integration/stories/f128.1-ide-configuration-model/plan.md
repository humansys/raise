# Implementation Plan: F128.1 IDE Configuration Model

## Overview
- **Feature:** F128.1
- **Size:** S
- **Tasks:** 3 (2 implementation + 1 integration test)
- **Created:** 2026-02-17

## Tasks

### Task 1: IdeType + IdeConfig + factory with tests
- **Description:** Create `config/ide.py` with `IdeType` literal, `IdeConfig` frozen Pydantic model, `IDE_CONFIGS` registry dict, and `get_ide_config()` factory. Write tests in `tests/config/test_ide.py`. Export from `config/__init__.py`.
- **Files:**
  - Create: `src/rai_cli/config/ide.py`
  - Create: `tests/config/test_ide.py`
  - Modify: `src/rai_cli/config/__init__.py`
- **TDD Cycle:**
  - RED: Tests for IdeConfig construction, frozen immutability, factory returns correct config for `claude` and `antigravity`, factory defaults to `claude`
  - GREEN: Implement model + factory
  - REFACTOR: Verify exports clean
- **Verification:** `pytest tests/config/test_ide.py -v && ruff check src/rai_cli/config/ide.py && pyright src/rai_cli/config/ide.py`
- **Size:** S
- **Dependencies:** None

### Task 2: Manifest schema extension with backward compat tests
- **Description:** Add `IdeManifest` model to `onboarding/manifest.py` with `type: IdeType` defaulting to `"claude"`. Add `ide: IdeManifest` field to `ProjectManifest` with `default_factory`. Write tests: roundtrip with ide field, backward compat loading manifest without ide field.
- **Files:**
  - Modify: `src/rai_cli/onboarding/manifest.py`
  - Modify: `tests/onboarding/test_manifest.py`
- **TDD Cycle:**
  - RED: Test `IdeManifest` defaults to claude, test `ProjectManifest` with ide field roundtrips, test legacy manifest without ide field loads with claude default
  - GREEN: Add IdeManifest + field to ProjectManifest
  - REFACTOR: Verify existing tests still pass
- **Verification:** `pytest tests/onboarding/test_manifest.py -v && pyright src/rai_cli/onboarding/manifest.py`
- **Size:** S
- **Dependencies:** Task 1 (imports IdeType from config.ide)

### Task 3 (Final): Manual Integration Test
- **Description:** Verify full suite passes, quality gates clean, and IdeConfig is usable from a Python REPL or test script (import, construct, factory call).
- **Verification:** `pytest tests/config/test_ide.py tests/onboarding/test_manifest.py -v && ruff check src/ && pyright src/`
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — IdeConfig model + factory (foundation, no dependencies)
2. Task 2 — Manifest extension (depends on Task 1 for IdeType import)
3. Task 3 — Integration validation (depends on all)

## Risks
- **Frozen model breaks serialization:** Pydantic frozen models serialize fine with `model_dump()` — low risk, but verify in roundtrip test.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1: IdeConfig + factory | S | -- | |
| 2: Manifest extension | S | -- | |
| 3: Integration test | XS | -- | |
