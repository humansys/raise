# Implementation Plan: Skill Scaffolding in raise init

## Overview
- **Story:** skill-scaffolding
- **Story Points:** 5 SP
- **Size:** M
- **Created:** 2026-02-06
- **Design:** `work/research/skill-distribution/design.md`

## Tasks

### Task 1: Fix session-start portability
- **Description:** Make `session-start` SKILL.md distributable by removing hardcoded `dev/parking-lot.md` references. Replace with conditional check: "If your project has a parking lot file, check it for stale items." Keep the signal table but make the parking lot step optional.
- **Files:** `.claude/skills/session-start/SKILL.md`
- **TDD Cycle:** N/A (markdown only)
- **Verification:** `grep -c "dev/parking-lot.md" .claude/skills/session-start/SKILL.md` returns 0 hardcoded references. Skill still functions correctly in raise-commons (where the file exists).
- **Size:** XS
- **Dependencies:** None

### Task 2: Create `skills_base` package
- **Description:** Create `src/raise_cli/skills_base/` package following `rai_base` pattern. Contains `__init__.py` with version and `DISTRIBUTABLE_SKILLS` manifest, plus one subdirectory per skill with `SKILL.md`. Copy the 5 onboarding skills from `.claude/skills/`: `session-start`, `discover-start`, `discover-scan`, `discover-validate`, `discover-complete`. Use the fixed `session-start` from Task 1.
- **Files:**
  - `src/raise_cli/skills_base/__init__.py` (CREATE)
  - `src/raise_cli/skills_base/session-start/SKILL.md` (CREATE)
  - `src/raise_cli/skills_base/discover-start/SKILL.md` (CREATE)
  - `src/raise_cli/skills_base/discover-scan/SKILL.md` (CREATE)
  - `src/raise_cli/skills_base/discover-validate/SKILL.md` (CREATE)
  - `src/raise_cli/skills_base/discover-complete/SKILL.md` (CREATE)
- **TDD Cycle:** RED: test that `importlib.resources.files("raise_cli.skills_base")` resolves and skills are readable → GREEN: create package → REFACTOR
- **Verification:** `pytest tests/onboarding/test_skills.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Implement `scaffold_skills()` module
- **Description:** Create `src/raise_cli/onboarding/skills.py` with `scaffold_skills(project_root, ide="claude")` function. Follows the same pattern as `bootstrap.py`: use `importlib.resources` to read from `skills_base`, copy to `.claude/skills/{name}/SKILL.md`, per-file idempotency (never overwrite), return `SkillScaffoldResult` Pydantic model. Add `SkillScaffoldResult` to schemas or keep inline (same as `BootstrapResult`).
- **Files:**
  - `src/raise_cli/onboarding/skills.py` (CREATE)
  - `tests/onboarding/test_skills.py` (CREATE)
- **TDD Cycle:** RED: test scaffold_skills copies to `.claude/skills/`, test idempotency, test result model → GREEN: implement → REFACTOR
- **Verification:** `pytest tests/onboarding/test_skills.py -v`
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Integrate into `raise init`
- **Description:** Call `scaffold_skills()` in `init_command()` after `bootstrap_rai_base()`. Add skill count to output messages for both Shu and Ri levels. Update `_get_project_message()` to include skills info.
- **Files:**
  - `src/raise_cli/cli/commands/init.py` (MODIFY)
  - `tests/cli/commands/test_init.py` (MODIFY)
- **TDD Cycle:** RED: test init command creates `.claude/skills/` → GREEN: integrate → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_init.py -v && pytest tests/ -x`
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Full test suite + lint
- **Description:** Run full test suite, pyright, ruff. Fix any issues. Ensure coverage threshold is met.
- **Files:** Any files needing fixes
- **TDD Cycle:** N/A
- **Verification:** `pytest tests/ --cov=src --cov-fail-under=90 && ruff check . && ruff format --check .`
- **Size:** S
- **Dependencies:** Task 4

### Task 6 (Final): Manual Integration Test
- **Description:** Test the full flow in an isolated environment:
  1. Set `RAI_HOME=/tmp/test-ff-user/.rai` and `HOME=/tmp/test-ff-user`
  2. Run `raise init` in a test directory
  3. Verify `.claude/skills/` contains all 5 skills
  4. Verify skills are valid SKILL.md with frontmatter
  5. Verify idempotency: run `raise init` again, skills not overwritten
- **Verification:** Manual demo of end-to-end flow
- **Size:** XS
- **Dependencies:** Task 5

## Execution Order

```
Task 1 (fix session-start)     — XS, no deps
    ↓
Task 2 (skills_base package)   — S, needs fixed skill
    ↓
Task 3 (scaffold_skills)       — M, needs package
    ↓
Task 4 (init integration)      — S, needs scaffolding
    ↓
Task 5 (full test + lint)      — S, needs integration
    ↓
Task 6 (manual integration)    — XS, final validation
```

All sequential — each task builds on the previous.

## Risks

| Risk | Mitigation |
|------|------------|
| `importlib.resources` doesn't find subdirectories in `skills_base` | Follow exact `rai_base` pattern; test with `files()` traversal |
| pyproject.toml needs `package-data` config for `.md` files | Check existing `rai_base` config and replicate |
| Session-start edit breaks raise-commons usage | Verify skill still works by reading the file after edit |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 - Fix session-start | XS | -- | |
| 2 - skills_base package | S | -- | |
| 3 - scaffold_skills | M | -- | |
| 4 - Init integration | S | -- | |
| 5 - Full test + lint | S | -- | |
| 6 - Manual integration | XS | -- | |
