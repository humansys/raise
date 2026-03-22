# Implementation Plan: F7.7 Guided First Session

## Overview
- **Feature:** F7.7
- **Story Points:** 3 SP
- **Feature Size:** M
- **Created:** 2026-02-05

## Architecture Decision

The `/session-start` skill is **markdown** — it guides Rai's behavior, not code. The adaptive behavior will be:

1. **New Step 0** in skill: Load personal profile via CLI
2. **Conditional content** based on experience level
3. **Session increment** at end of skill
4. **CLI command** to support the skill: `rai profile show` (read profile)

## Tasks

### Task 1: Add Profile CLI Command
- **Description:** Create `rai profile show` command that outputs developer profile in YAML format. This lets the skill read the profile.
- **Files:**
  - `src/rai_cli/cli/commands/profile.py` (new)
  - `src/rai_cli/cli/main.py` (register command)
  - `tests/cli/commands/test_profile.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run pytest tests/cli/commands/test_profile.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Add Session Increment Function
- **Description:** Add `increment_session()` function to profile module that increments `sessions_total`, updates `last_session`, and adds project if new.
- **Files:**
  - `src/rai_cli/onboarding/profile.py`
  - `tests/onboarding/test_profile.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run pytest tests/onboarding/test_profile.py -v`
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Add Profile Session CLI Command
- **Description:** Create `rai profile session` command that increments session and optionally creates profile for first-time users.
- **Files:**
  - `src/rai_cli/cli/commands/profile.py` (extend)
  - `tests/cli/commands/test_profile.py` (extend)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run pytest tests/cli/commands/test_profile.py -v`
- **Size:** S
- **Dependencies:** Task 1, Task 2

### Task 4: Update Session-Start Skill with Adaptive Sections
- **Description:** Modify `/session-start` skill to:
  1. Load profile at start (`rai profile show`)
  2. Branch behavior based on experience level
  3. Add educational content for Shu users
  4. Add efficient content for Ri users
  5. Increment session at end (`rai profile session`)
- **Files:**
  - `.claude/skills/session-start/SKILL.md`
- **TDD Cycle:** N/A (skill markdown, not code)
- **Verification:** Manual review of skill content
- **Size:** M
- **Dependencies:** Task 3

### Task 5 (Final): Manual Integration Test
- **Description:** Test the full adaptive flow:
  1. Create new profile (Shu)
  2. Run `/session-start` — verify educational content
  3. Manually set profile to Ri
  4. Run `/session-start` — verify concise content
  5. Verify session count increments
- **Verification:** Demo both Shu and Ri paths working
- **Size:** XS
- **Dependencies:** Task 4

## Execution Order

```
Task 1 ──┐
         ├──► Task 3 ──► Task 4 ──► Task 5
Task 2 ──┘
```

1. **Task 1 + Task 2** (parallel) — Foundation
2. **Task 3** — Combine into session command
3. **Task 4** — Skill update (the main deliverable)
4. **Task 5** — Integration test

## Risks

| Risk | Mitigation |
|------|------------|
| Skill markdown complexity | Keep Shu/Ri sections clearly separated |
| First-time user flow | `rai profile session` creates profile if missing |

## Duration Tracking

| Task | Size | Estimate | Actual | Notes |
|------|------|----------|--------|-------|
| 1 | S | 15 min | -- | |
| 2 | S | 15 min | -- | |
| 3 | S | 15 min | -- | |
| 4 | M | 30 min | -- | |
| 5 | XS | 10 min | -- | |
| **Total** | | ~85 min | -- | |
