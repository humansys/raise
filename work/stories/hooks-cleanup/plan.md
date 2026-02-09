# Implementation Plan: Remove Duplicate Bash Hook Telemetry

## Overview
- **Story:** hooks-cleanup
- **Size:** S
- **Created:** 2026-02-08
- **Design:** `work/stories/hooks-cleanup/design.md`

## Tasks

### Task 1: Strip hooks from distributable skills
- **Description:** Remove the `hooks:` YAML frontmatter block from all 20 distributable SKILL.md files in `src/raise_cli/skills_base/*/SKILL.md`. The block is always the last section before the closing `---`, with a consistent format (4 lines: `hooks:`, `  Stop:`, `    - hooks:`, `        - type: command`, `          command: ...`).
- **Files:** 20 files in `src/raise_cli/skills_base/*/SKILL.md`
- **TDD Cycle:** GREEN only — mechanical removal, verified by grep
- **Verification:** `grep -r "^hooks:" src/raise_cli/skills_base/ | wc -l` → 0
- **Size:** S
- **Dependencies:** None

### Task 2: Strip hooks from source skills
- **Description:** Remove the `hooks:` YAML frontmatter block from all 21 source SKILL.md files in `.claude/skills/*/SKILL.md`. Same format as Task 1.
- **Files:** 21 files in `.claude/skills/*/SKILL.md`
- **TDD Cycle:** GREEN only — mechanical removal, verified by grep
- **Verification:** `grep -r "^hooks:" .claude/skills/ | wc -l` → 0
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Remove bash scripts and bootstrap wiring
- **Description:** Delete the 5 bash scripts from `src/raise_cli/rai_base/scripts/` and remove the `_copy_scripts()` function + `scripts_copied` field from `bootstrap.py`. Remove the call to `_copy_scripts` in `bootstrap_rai_base()`.
- **Files:**
  - Delete: `src/raise_cli/rai_base/scripts/log-skill-complete.sh`, `log-skill-start.sh`, `log-session-event.sh`, `log-artifact-created.sh`, `log-error-event.sh`
  - Modify: `src/raise_cli/onboarding/bootstrap.py`
- **TDD Cycle:** RED (update tests first) → GREEN (remove code)
- **Verification:** `pytest tests/onboarding/test_bootstrap.py -v`
- **Size:** S
- **Dependencies:** None (parallel with Tasks 1-2)

### Task 4: Remove hooks from scaffold template
- **Description:** Remove the `hooks:` block from the skill template in `scaffold.py` so newly created skills don't include hooks.
- **Files:** `src/raise_cli/skills/scaffold.py`
- **TDD Cycle:** RED → GREEN — verify scaffold output has no hooks
- **Verification:** `pytest tests/skills/ -v`
- **Size:** XS
- **Dependencies:** None (parallel with Tasks 1-3)

### Task 5: Full validation
- **Description:** Run full test suite + type checks + lint to confirm nothing is broken.
- **Verification:**
  - `pytest --tb=short`
  - `uv run pyright`
  - `uv run ruff check src/ tests/`
- **Size:** XS
- **Dependencies:** Tasks 1-4

### Task 6: Manual integration test
- **Description:** Run `raise init` on a temp directory to verify bootstrap no longer copies scripts. Run `raise skill validate` on a distributable skill to verify it parses without hooks.
- **Verification:** Demo both commands working correctly
- **Size:** XS
- **Dependencies:** Task 5

## Execution Order
1. Tasks 1-4 (parallel — all independent)
2. Task 5 (full validation)
3. Task 6 (manual integration test)

## Risks
- **Long tail of hook references:** Mitigated by grep verification after each task
- **Tests referencing hooks in skills:** Parser/schema tests test hooks generically, not via distributable skills — should be unaffected

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | 20 distributable skills |
| 2 | S | -- | 21 source skills |
| 3 | S | -- | Scripts + bootstrap |
| 4 | XS | -- | Scaffold template |
| 5 | XS | -- | Full validation |
| 6 | XS | -- | Integration test |
