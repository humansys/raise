# Implementation Plan: Antigravity Scaffolding

## Overview
- **Feature:** F128.3
- **Story Points:** 3 SP
- **Feature Size:** S
- **Tasks:** 2 (1 implementation + 1 quality gate)
- **Created:** 2026-02-18

## Strategy

Single-module implementation. Create `onboarding/workflows.py` with `scaffold_workflows()` function that reads skill frontmatter via existing `parse_frontmatter()` and generates workflow shim files. Follows the exact pattern of `onboarding/skills.py`.

---

## Tasks

### Task 1: Create scaffold_workflows() — onboarding/workflows.py

- **Description:** Create new module `onboarding/workflows.py` with:
  - `WorkflowScaffoldResult` Pydantic model (matches `SkillScaffoldResult` pattern)
  - `scaffold_workflows(project_root, *, ide_config)` function that:
    1. Returns early with `skipped_no_workflows_dir=True` when `ide_config.workflows_dir` is `None`
    2. Iterates `DISTRIBUTABLE_SKILLS`
    3. Reads each skill's SKILL.md frontmatter via `parse_frontmatter()` from `skills/parser.py`
    4. Generates a workflow shim `.md` file with YAML frontmatter (name + description) and one-line body
    5. Per-file idempotency: skip existing files
- **Files:**
  - `src/rai_cli/onboarding/workflows.py` (create)
  - `tests/onboarding/test_workflows.py` (create)
- **TDD Cycle:**
  - RED: Tests for (a) Claude config → no-op, (b) Antigravity → generates N workflow files, (c) idempotency — second call skips existing
  - GREEN: Implement `scaffold_workflows()` using `parse_frontmatter()` + `DISTRIBUTABLE_SKILLS`
  - REFACTOR: Verify existing tests unchanged
- **Verification:** `uv run pytest tests/onboarding/test_workflows.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2 (Final): Quality Gates + Integration Test

- **Description:** Run full quality gate suite. Verify the generated workflow files contain valid YAML frontmatter by reading them back with `parse_frontmatter()`.
- **Files:** None (validation only)
- **Verification:**
  - `uv run pytest --tb=short` (all tests pass)
  - `uv run ruff check src/` (lint clean)
  - `uv run pyright` (type check clean)
- **Size:** XS
- **Dependencies:** Task 1

---

## Execution Order

```
Task 1: scaffold_workflows()     [single implementation task]
  ↓
Task 2: Quality gates            [validates everything]
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| SKILL.md frontmatter parsing fails for some skills | L | L | `parse_frontmatter()` is battle-tested (22 skills already parsed by graph builder) |
| Antigravity workflow format assumption is wrong | L | M | Minimal shim format — easy to adjust later. F128.4 E2E tests will validate |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. scaffold_workflows | S | 15 min | -- | Single new module, follows existing pattern |
| 2. Quality gates | XS | 5 min | -- | |
| **Total** | **S** | **~20 min** | -- | Applying PAT-F-012: pattern is established from skills.py |
