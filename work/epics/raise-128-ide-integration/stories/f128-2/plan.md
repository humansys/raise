# Implementation Plan: Decouple Init from Claude Paths

## Overview
- **Feature:** F128.2
- **Story Points:** 5 SP
- **Feature Size:** M
- **Tasks:** 5 (4 refactoring + 1 integration test)
- **Created:** 2026-02-18

## Strategy

Bottom-up by architecture layer: leaf → domain → integration. Each task adds `ide_config: IdeConfig | None = None` parameter with default to Claude, writes a failing test first, then refactors.

---

## Tasks

### Task 1: Decouple `get_default_skill_dir()` in skills/locator.py

- **Description:** Add optional `ide_config` parameter to `get_default_skill_dir()`. When provided, resolve skills dir from `ide_config.skills_dir` instead of hardcoded `.claude/skills`. Default behavior unchanged. Also update `list_skills()` which calls it.
- **Files:**
  - `src/rai_cli/skills/locator.py` (modify)
  - `tests/skills/test_locator.py` (modify)
- **TDD Cycle:**
  - RED: Add test `test_default_skill_dir_with_ide_config` passing antigravity config, expect `.agent/skills`
  - GREEN: Add `ide_config` param, resolve from config when provided
  - REFACTOR: Verify existing tests still pass unchanged
- **Verification:** `uv run pytest tests/skills/test_locator.py -v`
- **Size:** S
- **Dependencies:** None (leaf layer — foundation for all others)

### Task 2: Decouple `scaffold_skills()` in onboarding/skills.py

- **Description:** Add optional `ide_config` parameter to `scaffold_skills()`. Use `ide_config.skills_dir` to determine target directory. Default behavior unchanged.
- **Files:**
  - `src/rai_cli/onboarding/skills.py` (modify)
  - `tests/onboarding/test_skills.py` (modify)
- **TDD Cycle:**
  - RED: Add test `test_scaffold_to_antigravity_dir` passing antigravity config, expect files in `.agent/skills/`
  - GREEN: Add `ide_config` param, use it for target dir resolution
  - REFACTOR: Verify existing tests pass unchanged
- **Verification:** `uv run pytest tests/onboarding/test_skills.py -v`
- **Size:** S
- **Dependencies:** Task 1 (uses same `IdeConfig` import pattern)

### Task 3: Decouple `load_skills()` in context/builder.py

- **Description:** Add optional `ide_config` parameter to `UnifiedGraphBuilder.__init__()`. Store as instance attribute, use in `load_skills()` to resolve skills directory. Default behavior unchanged.
- **Files:**
  - `src/rai_cli/context/builder.py` (modify)
  - `tests/context/test_builder.py` (modify)
- **TDD Cycle:**
  - RED: Add test `test_initializes_with_ide_config` and `test_load_skills_uses_ide_config`
  - GREEN: Add `ide_config` to `__init__`, use in `load_skills()`
  - REFACTOR: Verify all existing builder tests pass unchanged
- **Verification:** `uv run pytest tests/context/test_builder.py -v`
- **Size:** S
- **Dependencies:** Task 1 (same pattern)

### Task 4: Decouple instructions file path in onboarding/claudemd.py

- **Description:** The `ClaudeMdGenerator` content is already IDE-agnostic. The coupling is in `init.py` where it writes to `CLAUDE.md`. Add optional `ide_config` parameter to `generate_claude_md()` so the content header can reference the correct instructions file name. Verify the path in `init.py` (coupling point #6, F128.4 scope) is the only place using the hardcoded filename — document for F128.4.
- **Files:**
  - `src/rai_cli/onboarding/claudemd.py` (modify — minimal)
  - `tests/onboarding/test_claudemd.py` (modify)
- **TDD Cycle:**
  - RED: Add test verifying content adapts session-start reference when `ide_config` is antigravity
  - GREEN: Accept `ide_config`, adapt content references if needed
  - REFACTOR: Verify existing tests pass unchanged
- **Verification:** `uv run pytest tests/onboarding/test_claudemd.py -v`
- **Size:** XS
- **Dependencies:** None (parallel with Tasks 2-3, but sequential for clean commits)

### Task 5 (Final): Quality Gates + Manual Integration Test

- **Description:** Run full quality gate suite. Manually verify `rai init` in a temp directory produces identical output to pre-refactor (backward compat proof). Run all tests to confirm zero regression.
- **Files:** None (validation only)
- **Verification:**
  - `uv run pytest --tb=short` (all tests pass)
  - `uv run ruff check src/` (lint clean)
  - `uv run pyright` (type check clean)
  - Manual: `rai init` in temp dir, verify `.claude/skills/` structure unchanged
- **Size:** XS
- **Dependencies:** Tasks 1-4

---

## Execution Order

```
Task 1: get_default_skill_dir()     [leaf — foundation]
  ↓
Task 2: scaffold_skills()           [depends on pattern from T1]
  ↓
Task 3: UnifiedGraphBuilder         [depends on pattern from T1]
  ↓
Task 4: claudemd.py                 [minimal, clean up last]
  ↓
Task 5: Quality gates + integration [validates everything]
```

Sequential execution — each task builds on the import/parameter pattern established in Task 1. Clean commit history per task.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Existing tests assume `.claude/` paths in assertions | M | L | Run existing tests after each task — they must pass unchanged |
| Callers outside these 4 files also hardcode paths | L | M | Gemba review in design already mapped all 6 coupling points |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. get_default_skill_dir | S | 15 min | -- | |
| 2. scaffold_skills | S | 15 min | -- | |
| 3. UnifiedGraphBuilder | S | 15 min | -- | |
| 4. claudemd.py | XS | 10 min | -- | |
| 5. Quality gates | XS | 10 min | -- | |
| **Total** | **M** | **~65 min** | -- | |
