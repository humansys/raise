# Implementation Plan: S18.2 — README

## Overview
- **Story:** S18.2 — README
- **Size:** M
- **Created:** 2026-02-12
- **Note:** Content rewrite only — no source code changes, no TDD cycles.

## Tasks

### Task 1: Write README.md
- **Description:** Full rewrite following FastAPI/Ruff pattern (D4). Structure: title + badges → session transcript → why → features → quick start → how it works → docs/community → license. Target ~120-150 lines.
- **Files:** `README.md`
- **Verification:** File exists, follows design structure, no GitLab URLs (`grep -i gitlab README.md` returns nothing)
- **Size:** M
- **Dependencies:** None

### Task 2: Move Developer Content to CONTRIBUTING.md
- **Description:** Ensure development setup, repo structure, and branch model details that were in README are preserved in CONTRIBUTING.md (already updated in S18.1, verify nothing lost).
- **Files:** `CONTRIBUTING.md` (verify, minor edits if needed)
- **Verification:** Development setup instructions present in CONTRIBUTING.md
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Verification & Commit
- **Description:** Verify badges render, links work, all tests still pass. Commit.
- **Files:** All modified
- **Verification:** `pytest` passes, no broken markdown links, badges use correct shield.io URLs
- **Size:** XS
- **Dependencies:** Tasks 1-2

## Execution Order

1. Task 1 — README rewrite (the bulk of the work)
2. Task 2 — Verify CONTRIBUTING.md has developer content
3. Task 3 — Verification & commit

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Session transcript doesn't feel authentic | Medium | Low | Base on real `rai init --detect` output |
| Badge URLs incorrect | Low | Low | Use shields.io standard patterns, verify render |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1. README rewrite | M | -- | |
| 2. CONTRIBUTING verify | XS | -- | |
| 3. Verify & commit | XS | -- | |
