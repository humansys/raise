# Implementation Plan: S-NAMESPACE

## Overview
- **Story:** S-NAMESPACE — Add rai- prefix namespace to all skills
- **Size:** M
- **Created:** 2026-02-11
- **Design:** `work/stories/S-NAMESPACE/design.md`

## Tasks

### Task 1: Rename skill directories in skills_base
- **Description:** Rename all 20 skill directories in `src/rai_cli/skills_base/` by adding `rai-` prefix. Use `git mv` to preserve history.
- **Files:** 20 directories in `src/rai_cli/skills_base/`
- **TDD Cycle:** N/A — infrastructure rename, verified by directory listing
- **Verification:** `ls src/rai_cli/skills_base/ | grep -v __ | grep -v __pycache__` — all dirs start with `rai-`
- **Size:** S
- **Dependencies:** None

### Task 2: Rename skill directories in .claude/skills
- **Description:** Rename all 23 skill directories in `.claude/skills/` (20 distributed + 3 local: docs-update, framework-sync, skill-create). Use `git mv`.
- **Files:** 23 directories in `.claude/skills/`
- **TDD Cycle:** N/A — infrastructure rename
- **Verification:** `ls .claude/skills/` — all dirs start with `rai-`
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Update SKILL.md frontmatter in both locations
- **Description:** Update the `name:` field in every SKILL.md to match the new directory name. ~43 files across both locations. Also update `description:` if it contains the old name.
- **Files:** All `SKILL.md` files in `src/rai_cli/skills_base/rai-*/` and `.claude/skills/rai-*/`
- **TDD Cycle:** N/A — metadata update
- **Verification:** `grep -rn "^name:" src/rai_cli/skills_base/*/SKILL.md .claude/skills/*/SKILL.md | grep -v "rai-"` — should be empty
- **Size:** M
- **Dependencies:** Tasks 1, 2

### Task 4: Update DISTRIBUTABLE_SKILLS and Python source
- **Description:** Update `DISTRIBUTABLE_SKILLS` list in `src/rai_cli/skills_base/__init__.py`. Update `KNOWN_LIFECYCLES` and `NAMING_PATTERN` in `name_checker.py` to account for `rai-` prefix. Update `migration.py` known_skills set.
- **Files:**
  - `src/rai_cli/skills_base/__init__.py`
  - `src/rai_cli/skills/name_checker.py`
  - `src/rai_cli/onboarding/migration.py`
- **TDD Cycle:** RED — test that `rai-session-start` is in DISTRIBUTABLE_SKILLS and name checker accepts it; GREEN — update lists; REFACTOR — clean up
- **Verification:** `pytest tests/skills/test_name_checker.py tests/onboarding/test_migration.py tests/onboarding/test_skills.py -x`
- **Size:** S
- **Dependencies:** Tasks 1, 2

### Task 5: Update cross-references in SKILL.md bodies
- **Description:** Update ~188 cross-references between skills in SKILL.md body text and references/ files. Patterns: `/session-start` → `/rai-session-start`, `Complement: /session-close` → `Complement: /rai-session-close`, etc.
- **Files:** ~26 files in `.claude/skills/rai-*/SKILL.md` and `.claude/skills/rai-*/references/`
- **TDD Cycle:** N/A — documentation update
- **Verification:** `grep -rn "/session-start\|/session-close\|/story-start\|/story-design\|/story-plan\|/story-implement\|/story-review\|/story-close\|/epic-start\|/epic-design\|/epic-plan\|/epic-close\|/discover-start\|/discover-scan\|/discover-validate\|/discover-document\|/project-create\|/project-onboard\b\|/research\b\|/debug\b\|/docs-update\|/framework-sync\|/skill-create" .claude/skills/ | grep -v "rai-"` — should be empty
- **Size:** M
- **Dependencies:** Task 2

### Task 6: Update methodology.yaml (both copies)
- **Description:** Update all ~27 skill name references in `src/rai_cli/rai_base/framework/methodology.yaml` and `.raise/rai/framework/methodology.yaml` to use `rai-` prefix.
- **Files:**
  - `src/rai_cli/rai_base/framework/methodology.yaml`
  - `.raise/rai/framework/methodology.yaml`
- **TDD Cycle:** N/A — config update, verified by methodology test
- **Verification:** `pytest tests/rai_base/test_methodology.py -x`
- **Size:** S
- **Dependencies:** None (parallel with Tasks 1-2)

### Task 7: Update CLAUDE.md, CLAUDE.local.md, and MEMORY.md references
- **Description:** Update `/session-start` reference in `CLAUDE.md` and `CLAUDE.local.md`. Update skill list in `.claude/projects/-home-emilio-Code-raise-commons/memory/MEMORY.md`.
- **Files:**
  - `CLAUDE.md`
  - `CLAUDE.local.md`
  - `.claude/projects/-home-emilio-Code-raise-commons/memory/MEMORY.md`
- **TDD Cycle:** N/A — docs update
- **Verification:** `grep -rn "session-start\|story-start" CLAUDE.md CLAUDE.local.md | grep -v "rai-"` — should be empty
- **Size:** XS
- **Dependencies:** None (parallel)

### Task 8: Update tests
- **Description:** Update all test files that assert on skill names, paths, or DISTRIBUTABLE_SKILLS values. Key files: test_skills.py, test_migration.py, test_name_checker.py, test_locator.py, test_parser.py, test_methodology.py, test_skill.py (CLI).
- **Files:**
  - `tests/skills/test_name_checker.py`
  - `tests/skills/test_parser.py`
  - `tests/skills/test_schema.py`
  - `tests/skills/test_locator.py`
  - `tests/skills/test_scaffold.py`
  - `tests/onboarding/test_skills.py`
  - `tests/onboarding/test_migration.py`
  - `tests/onboarding/test_profile.py`
  - `tests/rai_base/test_methodology.py`
  - `tests/cli/commands/test_skill.py`
  - `tests/cli/commands/test_init.py`
- **TDD Cycle:** Update test expectations → run → verify green
- **Verification:** `pytest tests/ -x --tb=short`
- **Size:** M
- **Dependencies:** Tasks 3, 4, 6

### Task 9: Full validation gate
- **Description:** Run full test suite, type checks, linting. Final grep sweep for stale references (PAT-151, PAT-181). Rebuild graph. Regenerate MEMORY.md.
- **Files:** None (verification only)
- **TDD Cycle:** N/A
- **Verification:**
  1. `pytest tests/ --tb=short` — all pass
  2. `pyright src/` — 0 errors
  3. `ruff check .` — clean
  4. Stale reference grep (from design.md verification gate)
  5. `rai memory build` — graph builds
  6. `rai memory generate` — MEMORY.md regenerated
- **Size:** S
- **Dependencies:** All previous tasks

### Task 10: Manual integration test
- **Description:** Verify skill discovery works end-to-end: invoke `/rai-session-start` via Claude Code and confirm it loads correctly. Verify `rai init` scaffolds skills with `rai-` prefix in a temp directory.
- **Verification:** Skills discoverable and invocable with new names
- **Size:** XS
- **Dependencies:** Task 9

## Execution Order

```
Phase 1 (parallel):  Task 1 + Task 2 + Task 6 + Task 7
Phase 2 (depends 1,2): Task 3 + Task 4 + Task 5
Phase 3 (depends all): Task 8
Phase 4 (validation):  Task 9
Phase 5 (manual):      Task 10
```

## Risks

| Risk | Mitigation |
|------|-----------|
| Long tail of missed references (PAT-151) | Final grep sweep in Task 9 |
| Stale terminology breaks CLI (PAT-181) | Test suite covers CLI commands |
| Graph extraction breaks on renamed dirs | Graph rebuild + verify in Task 9 |
| MEMORY.md skill list stale | Regenerate in Task 9 |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | git mv 20 dirs |
| 2 | S | -- | git mv 23 dirs |
| 3 | M | -- | ~43 SKILL.md frontmatter |
| 4 | S | -- | 3 Python files |
| 5 | M | -- | ~188 cross-refs in ~26 files |
| 6 | S | -- | 2 YAML files, ~27 refs |
| 7 | XS | -- | 3 files |
| 8 | M | -- | ~11 test files |
| 9 | S | -- | validation gate |
| 10 | XS | -- | manual test |
