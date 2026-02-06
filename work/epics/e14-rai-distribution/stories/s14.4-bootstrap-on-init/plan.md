# Implementation Plan: S14.4 Bootstrap on Init

## Overview
- **Story:** S14.4
- **Story Points:** 3 SP
- **Size:** M
- **Created:** 2026-02-06
- **Design:** `stories/s14.4-bootstrap-on-init/design.md`

## Tasks

### Task 1: Create BootstrapResult model and bootstrap module
- **Description:** Create `onboarding/bootstrap.py` with `BootstrapResult` Pydantic model and the core `bootstrap_rai_base()` function. Uses `importlib.resources.files()` to read bundled files from `raise_cli.rai_base` and copies them to `.raise/rai/` with per-file idempotency.
- **Files:**
  - CREATE: `src/raise_cli/onboarding/bootstrap.py`
  - CREATE: `tests/onboarding/test_bootstrap.py`
- **TDD Cycle:**
  - RED: Test `bootstrap_rai_base()` on empty project dir → expects identity, patterns, methodology copied
  - RED: Test idempotency → call twice, second returns `already_existed=True`, files unchanged
  - RED: Test partial state → identity exists but patterns don't → only patterns copied
  - GREEN: Implement with `importlib.resources.files()`, per-file existence checks, directory creation
  - REFACTOR: Extract helpers if needed
- **Verification:** `pytest tests/onboarding/test_bootstrap.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Add `get_identity_dir()` to paths.py
- **Description:** Add a `get_identity_dir()` helper to `config/paths.py` and a `get_framework_dir()` helper. Follows existing pattern of `get_memory_dir()`, `get_telemetry_dir()`.
- **Files:**
  - MODIFY: `src/raise_cli/config/paths.py`
  - MODIFY: `tests/config/test_paths.py`
- **TDD Cycle:**
  - RED: Test `get_identity_dir()` returns `.raise/rai/identity/`
  - RED: Test `get_framework_dir()` returns `.raise/rai/framework/`
  - GREEN: Implement following existing `get_memory_dir()` pattern
- **Verification:** `pytest tests/config/test_paths.py -v`
- **Size:** XS
- **Dependencies:** None

### Task 3: Integrate bootstrap into init command
- **Description:** Call `bootstrap_rai_base()` in `init_command()` after `save_manifest()`. Add bootstrap info to output messages (Shu: detailed, Ri: concise). Lazy import for startup speed.
- **Files:**
  - MODIFY: `src/raise_cli/cli/commands/init.py`
  - MODIFY: `tests/cli/commands/test_init.py`
- **TDD Cycle:**
  - RED: Test `init_command()` creates `.raise/rai/identity/core.md`
  - RED: Test `init_command()` output includes bootstrap info
  - RED: Test re-init doesn't overwrite existing files
  - GREEN: Add `bootstrap_rai_base()` call and update message templates
  - REFACTOR: Clean up message formatting
- **Verification:** `pytest tests/cli/commands/test_init.py -v`
- **Size:** S
- **Dependencies:** Task 1, Task 2

### Task 4: Manual Integration Test
- **Description:** Run `raise init` on a fresh temp directory. Verify all base files are copied correctly. Run again to verify idempotency. Check file contents match bundled originals.
- **Verification:** Demo working end-to-end in terminal
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

1. Task 1 + Task 2 (parallel — no dependencies between them)
2. Task 3 (depends on 1 and 2)
3. Task 4 (final validation)

## Risks

- `importlib.resources` `Traversable` API quirks with subdirectories: mitigate by testing with installed package, not just source tree
- Existing tests for `init_command` may need fixture updates: check test setup before modifying

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Core bootstrap logic + tests |
| 2 | XS | -- | Path helpers |
| 3 | S | -- | Init integration |
| 4 | XS | -- | Integration test |
