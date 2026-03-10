# Implementation Plan: S-BRANCH-CONFIG

## Overview
- **Story:** S-BRANCH-CONFIG — Configurable development branch
- **Size:** S
- **Created:** 2026-02-11

## Tasks

### Task 1: Add BranchConfig to manifest schema
- **Description:** Add `branches` field to `ProjectManifest` with `development` and `main` fields, both with sensible defaults (`main`/`main`). Update `ProjectManifest` version to `1.1`.
- **Files:** `src/rai_cli/onboarding/manifest.py`
- **TDD:** RED (test new schema) → GREEN (add model) → REFACTOR
- **Verification:** `uv run pytest tests/ -k manifest`
- **Size:** XS
- **Dependencies:** None

### Task 2: Replace hardcoded `v2` in distributed skills
- **Description:** Replace all hardcoded `v2` references with `{dev_branch}` placeholder in skills_base AND .claude/skills. Add a note at skill top: "Read `branches.development` from `.raise/manifest.yaml` for the project's development branch."
- **Files:** `src/rai_cli/skills_base/rai-epic-start/SKILL.md`, `src/rai_cli/skills_base/rai-epic-close/SKILL.md`, `src/rai_cli/skills_base/rai-story-close/SKILL.md`, plus `.claude/skills/` copies
- **Verification:** `grep -rn "v2" src/rai_cli/skills_base/ --include="*.md"` returns only template version refs
- **Size:** S
- **Dependencies:** None

### Task 3: Add branch config to onboarding skills
- **Description:** Add branch config question to `/rai-project-create` and `/rai-project-onboard` skills.
- **Files:** `src/rai_cli/skills_base/rai-project-create/SKILL.md`, `src/rai_cli/skills_base/rai-project-onboard/SKILL.md`, plus `.claude/skills/` copies
- **Verification:** Skills reference branch config capture
- **Size:** XS
- **Dependencies:** Task 1

### Task 4: Update raise-commons manifest
- **Description:** Add branch config to raise-commons's own `.raise/manifest.yaml`
- **Files:** `.raise/manifest.yaml`
- **Size:** XS
- **Dependencies:** Task 1

### Task 5: Manual integration test
- **Description:** Verify no hardcoded v2 leaks, manifest loads with branch config, skills read cleanly
- **Size:** XS
- **Dependencies:** All previous

## Execution Order
1. Task 1 (schema)
2. Task 2 + Task 3 (parallel, independent)
3. Task 4
4. Task 5

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
| 4 | XS | -- | |
| 5 | XS | -- | |
