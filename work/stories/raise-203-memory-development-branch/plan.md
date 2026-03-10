# Implementation Plan: RAISE-203

## Overview
- **Story:** RAISE-203
- **Title:** Remove raise-commons-specific hardcoding from distributable assets
- **Size:** M (5-8 SP)
- **Created:** 2026-02-20

## Tasks

### Task 1: methodology.yaml — Replace "v2" with placeholder
- **Description:** In `methodology.yaml`, replace the two literal "v2" occurrences in the branches section with `{development_branch}` placeholder. This is the template source; substitution happens at generation time.
- **Files:** `src/rai_cli/rai_base/framework/methodology.yaml`
- **TDD Cycle:** RED — write test that generates MEMORY.md from a methodology with `{development_branch}` and asserts the placeholder is NOT in output (replaced by actual branch). GREEN — modify methodology.yaml. REFACTOR — n/a.
- **Verification:** `pytest tests/onboarding/test_memory_md.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: memory_md.py — Substitute placeholder in _add_branches_section
- **Description:** Add `development_branch` parameter to `_add_branches_section()`, `generate()` method, and the `generate_memory_md()` convenience function. Replace `{development_branch}` in structure and flow strings with the actual branch name. Default to `"main"` when not provided.
- **Files:** `src/rai_cli/onboarding/memory_md.py`
- **TDD Cycle:** RED — test from Task 1 should now go green. GREEN — implement substitution. REFACTOR — ensure flow items also get substituted.
- **Verification:** `pytest tests/onboarding/test_memory_md.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: init.py — Pass development_branch from manifest
- **Description:** In `cli/commands/init.py`, read `branches.development` from the manifest and pass it to `generate_memory_md()`. This connects the source of truth (manifest.yaml) to the generation pipeline.
- **Files:** `src/rai_cli/cli/commands/init.py`
- **TDD Cycle:** RED — test that `init` command produces MEMORY.md with manifest's branch name. GREEN — add parameter passing. REFACTOR — n/a.
- **Verification:** `pytest tests/cli/ -k init -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: SKILL.md — Replace "Emilio" with generic placeholder
- **Description:** In `rai-session-close/SKILL.md` line 107, replace "Emilio mentioned interest in [topic] — if he brings it up" with "The developer mentioned interest in [topic] — if they bring it up". No code change, just template text.
- **Files:** `src/rai_cli/skills_base/rai-session-close/SKILL.md`
- **TDD Cycle:** N/A (template text, no logic)
- **Verification:** `grep -c "Emilio" src/rai_cli/skills_base/rai-session-close/SKILL.md` returns 0
- **Size:** XS
- **Dependencies:** None

### Task 5: migration.py — Rename migrate_emilio_profile → migrate_developer_profile
- **Description:** Rename function, update default name parameter from "Emilio" to "Developer", update docstring. Also update import in `__init__.py` and `__all__` export.
- **Files:** `src/rai_cli/onboarding/migration.py`, `src/rai_cli/onboarding/__init__.py`
- **TDD Cycle:** RED — rename references in test first (they break). GREEN — rename in source. REFACTOR — verify no other callers.
- **Verification:** `pytest tests/onboarding/test_migration.py -v`
- **Size:** S
- **Dependencies:** None

### Task 6: Quality gates
- **Description:** Run full quality suite: pyright, ruff, pytest with coverage, bandit.
- **Files:** None (validation only)
- **TDD Cycle:** N/A
- **Verification:** `pyright && ruff check . && pytest --tb=short && bandit -r src/ -q`
- **Size:** XS
- **Dependencies:** Tasks 1-5

### Task 7 (Final): Manual Integration Test
- **Description:** Run `rai init` on a temp directory and verify: (1) generated MEMORY.md shows "main" not "v2" in branch model, (2) no "Emilio" in skills templates, (3) `migrate_developer_profile` importable.
- **Verification:** Demo the story working with actual CLI
- **Size:** XS
- **Dependencies:** Task 6

## Execution Order
1. Task 1 + Task 4 + Task 5 (parallel — independent changes)
2. Task 2 (depends on Task 1)
3. Task 3 (depends on Task 2)
4. Task 6 (quality gates after all changes)
5. Task 7 (manual integration test)

## Risks
- **methodology.yaml has other consumers:** Mitigated — `_add_branches_section` is the only reader of `branches.structure`, and we control substitution there.
- **Backward compat of migrate_emilio_profile:** Low risk — no external callers in `src/`, only test references. Not part of public API.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | XS | -- | |
| 5 | S | -- | |
| 6 | XS | -- | |
| 7 | XS | -- | |
