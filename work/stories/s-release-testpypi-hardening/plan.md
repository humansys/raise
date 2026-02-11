# Implementation Plan: TestPyPI Hardening

## Overview
- **Story:** S-RELEASE
- **Story Points:** 5 SP
- **Size:** S
- **Created:** 2026-02-10

## Analysis

### Task 1: Add `vendor` to default exclude patterns
The `--exclude` flag and infrastructure **already exist** (discover.py:77-84, scanner.py:1028-1037, `_should_exclude`, `.gitignore` integration). What's missing is `**/vendor/**` in `DEFAULT_EXCLUDE_PATTERNS` — PHP/Composer projects need this out of the box.

### Task 2: Absorb discover-complete into discover-validate
**discover-complete** (skill + `skills_base`) does one thing: filter validated components from draft YAML, transform to JSON, write `components-validated.json`. This is a mechanical export step after validation. Absorbing it means:
- Append Steps 1-7 of discover-complete as a final step in discover-validate
- Remove discover-complete skill from `.claude/skills/` and `skills_base/`
- Update `DISTRIBUTABLE_SKILLS` list
- Update references in discover-validate (`raise.next`), CLI hints, methodology.yaml
- Update migration.py references

### Task 3: Rename discover-describe → discover-document
Affects:
- `.claude/skills/discover-describe/` → `.claude/skills/discover-document/`
- `skills_base/discover-describe/` → `skills_base/discover-document/`
- `DISTRIBUTABLE_SKILLS` list entry
- `skills_base/__init__.py` docstring
- Skill internal `name:` field
- Any cross-references in other skills/docs

### Task 4: Build + publish to TestPyPI
- Version bump if needed (current: `2.0.0-alpha.1`)
- Build wheel + sdist
- Upload to TestPyPI
- Verify install in clean venv

## Tasks

### Task 1: Add `vendor` to scanner default excludes
- **Description:** Add `**/vendor/**` to `DEFAULT_EXCLUDE_PATTERNS` in scanner.py
- **Files:** `src/raise_cli/discovery/scanner.py`
- **TDD Cycle:** RED (test that vendor/ is excluded by default) → GREEN (add pattern) → REFACTOR
- **Verification:** `uv run pytest tests/ -k "exclude" -x -q`
- **Size:** XS
- **Dependencies:** None

### Task 2: Absorb discover-complete into discover-validate skill
- **Description:** Merge the export step (Steps 1-7 from discover-complete) as a final step in discover-validate. Remove discover-complete skill from both `.claude/skills/` and `src/raise_cli/skills_base/`. Update all references.
- **Files:**
  - `src/raise_cli/skills_base/discover-validate/SKILL.md` (add export step)
  - `src/raise_cli/skills_base/discover-complete/` (delete directory)
  - `src/raise_cli/skills_base/__init__.py` (remove from list + docstring)
  - `src/raise_cli/rai_base/framework/methodology.yaml` (remove reference)
  - `src/raise_cli/onboarding/migration.py` (remove reference)
  - `src/raise_cli/cli/commands/discover.py` (update hint messages)
  - `.claude/skills/discover-complete/` (delete directory)
  - `.claude/skills/discover-validate/SKILL.md` (add export step)
- **TDD Cycle:** No code logic change — skill content only. Verify with `uv run raise skill list` and grep for stale references.
- **Verification:** `grep -r "discover-complete" src/raise_cli/` returns zero hits. `uv run pytest -x -q`
- **Size:** M
- **Dependencies:** None

### Task 3: Rename discover-describe → discover-document
- **Description:** Rename skill in both `.claude/skills/` and `src/raise_cli/skills_base/`. Update all internal references.
- **Files:**
  - `src/raise_cli/skills_base/discover-describe/` → `discover-document/` (rename dir + update `name:` field)
  - `src/raise_cli/skills_base/__init__.py` (update list + docstring)
  - `.claude/skills/discover-describe/` → `.claude/skills/discover-document/` (rename dir + update `name:` field)
  - Any cross-references in other skills
- **TDD Cycle:** Verify with `uv run raise skill list` — should show `discover-document`, not `discover-describe`.
- **Verification:** `grep -r "discover-describe" src/raise_cli/` returns zero hits. `uv run pytest -x -q`
- **Size:** S
- **Dependencies:** None

### Task 4: Full validation gate
- **Description:** Run full test suite, type check, lint to confirm nothing broke.
- **Verification:** `uv run pytest -x -q && uv run ruff check src/ && uv run pyright src/raise_cli/`
- **Size:** XS
- **Dependencies:** Tasks 1-3

### Task 5: Build and publish to TestPyPI
- **Description:** Build wheel + sdist, upload to TestPyPI, verify install.
- **Steps:**
  1. Verify version in `pyproject.toml` and `__init__.py` match
  2. `uv build` (creates dist/)
  3. `uv publish --publish-url https://test.pypi.org/legacy/` (or twine)
  4. Verify: `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ raise-cli`
  5. `raise --version` works
- **Size:** S
- **Dependencies:** Task 4

### Task 6 (Final): Manual Integration Test
- **Description:** Install from TestPyPI in clean venv, run `raise init --detect` on a test project, verify skills list shows correct names (no discover-complete, discover-document present).
- **Verification:** End-to-end install → init → skill list works
- **Size:** XS
- **Dependencies:** Task 5

## Execution Order
1. Tasks 1, 2, 3 (parallel — independent changes)
2. Task 4 (gate — depends on 1-3)
3. Task 5 (publish — depends on 4)
4. Task 6 (integration test — depends on 5)

## Risks
- **TestPyPI name collision:** `raise-cli` may already be taken on TestPyPI. Mitigation: check availability first, rename package if needed.
- **Stale references:** Renaming/removing skills may leave references in unexpected places. Mitigation: grep broadly after each change.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | M | -- | |
| 3 | S | -- | |
| 4 | XS | -- | |
| 5 | S | -- | |
| 6 | XS | -- | Integration test |
