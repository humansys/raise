# Implementation Plan: F7.1 `raise init` Command

## Overview

- **Feature:** F7.1
- **Story Points:** 3 SP
- **Feature Size:** M
- **Created:** 2026-02-05

## Tasks

### Task 1: Project Detection Module

- **Description:** Create `src/raise_cli/onboarding/detection.py` with project type detection logic (greenfield/brownfield based on code file count)
- **Files:**
  - `src/raise_cli/onboarding/detection.py` (new)
  - `tests/onboarding/test_detection.py` (new)
- **TDD Cycle:**
  - RED: Test `detect_project_type()` returns greenfield for empty dir
  - RED: Test returns brownfield for dir with code files
  - GREEN: Implement with file counting logic
  - REFACTOR: Extract code extensions constant
- **Verification:** `pytest tests/onboarding/test_detection.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Project Manifest Schema

- **Description:** Create Pydantic model for `.rai/manifest.yaml` and save/load functions
- **Files:**
  - `src/raise_cli/onboarding/manifest.py` (new)
  - `tests/onboarding/test_manifest.py` (new)
- **TDD Cycle:**
  - RED: Test `ProjectManifest` schema validates correctly
  - RED: Test `save_manifest()` creates file with correct YAML
  - RED: Test `load_manifest()` reads back correctly
  - GREEN: Implement schema and persistence
  - REFACTOR: Add docstrings
- **Verification:** `pytest tests/onboarding/test_manifest.py -v`
- **Size:** S
- **Dependencies:** None (can parallel with Task 1)

### Task 3: Init CLI Command

- **Description:** Create `raise init` command that ties detection, manifest, and profile together
- **Files:**
  - `src/raise_cli/cli/commands/init.py` (new)
  - `src/raise_cli/cli/main.py` (modify to register)
  - `src/raise_cli/onboarding/__init__.py` (update exports)
  - `tests/cli/commands/test_init.py` (new)
- **TDD Cycle:**
  - RED: Test init creates `.rai/manifest.yaml`
  - RED: Test init loads existing profile
  - RED: Test init creates new profile when missing
  - RED: Test Shu output is verbose, Ri output is concise
  - GREEN: Implement command using existing modules
  - REFACTOR: Extract message templates
- **Verification:** `pytest tests/cli/commands/test_init.py -v`
- **Size:** M
- **Dependencies:** Task 1, Task 2

### Task 4: Quality Gates

- **Description:** Run full quality checks (type checking, linting, coverage)
- **Files:** None new
- **TDD Cycle:** N/A (validation only)
- **Verification:**
  - `ruff check src/raise_cli/onboarding/ src/raise_cli/cli/commands/init.py`
  - `ruff format --check src/raise_cli/onboarding/ src/raise_cli/cli/commands/init.py`
  - `pyright src/raise_cli/onboarding/ src/raise_cli/cli/commands/init.py`
  - `pytest tests/onboarding/ tests/cli/commands/test_init.py --cov=src/raise_cli/onboarding --cov=src/raise_cli/cli/commands/init --cov-report=term-missing`
- **Size:** XS
- **Dependencies:** Tasks 1-3

### Task 5 (Final): Manual Integration Test

- **Description:** Test `raise init` on real directories (greenfield + brownfield)
- **Verification:**
  1. Create temp greenfield dir → `raise init` → verify output/files
  2. Run `raise init` on existing project → verify brownfield detection
  3. Delete `~/.rai/developer.yaml` → run init → verify new profile created
  4. Run init again → verify existing profile loaded
- **Size:** XS
- **Dependencies:** Tasks 1-4

## Execution Order

```
Task 1 (detection) ─┬─► Task 3 (CLI command) ─► Task 4 (quality) ─► Task 5 (integration)
Task 2 (manifest)  ─┘
```

1. **Task 1 + Task 2** (parallel) — Foundation modules
2. **Task 3** — CLI command integrating both
3. **Task 4** — Quality gates
4. **Task 5** — Manual integration test

## Risks

| Risk | Mitigation |
|------|------------|
| Profile loading interferes with test isolation | Use `tmp_path` fixture and mock `Path.home()` |
| Existing `.rai/` in test dir | Clean up in fixture teardown |

## Duration Tracking

| Task | Size | Estimate | Actual | Notes |
|------|:----:|:--------:|:------:|-------|
| 1. Detection | S | 20 min | -- | |
| 2. Manifest | S | 20 min | -- | |
| 3. CLI Command | M | 40 min | -- | |
| 4. Quality | XS | 10 min | -- | |
| 5. Integration | XS | 10 min | -- | |
| **Total** | **M** | **~1.5h** | -- | |

---

*Plan created: 2026-02-05*
