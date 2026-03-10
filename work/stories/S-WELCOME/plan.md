# Implementation Plan: S-WELCOME — Developer Onboarding Skill

## Overview
- **Story:** S-WELCOME
- **Feature Size:** S
- **Created:** 2026-02-11

## Notes

This is a **prompt-only skill** — no Python source code changes. The deliverable is a SKILL.md file that orchestrates existing CLI commands and Claude Code tools. TDD doesn't apply in the traditional sense; verification is through manual invocation and structural checks.

## Tasks

### Task 1: Create skill directory and SKILL.md
- **Description:** Create `.claude/skills/rai-welcome/SKILL.md` with the full skill prompt. The prompt must:
  1. Detect scenario (check `~/.rai/developer.yaml` + `.raise/` dir)
  2. Guard-rail scenarios 2 & 4 (no `.raise/` → tell user to run `rai init`, exit)
  3. Ask name + confirm pattern_prefix (if no profile)
  4. Run `rai session start --name "X" --project "$(pwd)"` to create profile
  5. Edit `~/.rai/developer.yaml` to set `pattern_prefix`
  6. Run `rai memory build` if `index.json` missing
  7. Create `CLAUDE.local.md` from minimal template if missing
  8. Offer optional personalization (language, communication style, redirect permission)
  9. Verify with `rai session start --project "$(pwd)" --context`
  10. Print welcome message with next steps
- **Files:** `.claude/skills/rai-welcome/SKILL.md` (create)
- **Verification:** File exists, has valid YAML frontmatter (name, description, metadata fields), follows rai-session-start pattern
- **Size:** S
- **Dependencies:** None

### Task 2: Register skill in project settings
- **Description:** Add `rai-welcome` to the project's skill configuration so Claude Code discovers it. Follow the same registration pattern used by existing skills (check how rai-session-start is registered).
- **Files:** `.claude/settings.local.json` or equivalent config
- **Verification:** `/rai-welcome` appears in available skills list
- **Size:** XS
- **Dependencies:** Task 1

### Task 3 (Final): Manual Integration Test
- **Description:** Test the skill in a simulated new-developer scenario:
  1. Verify `/rai-welcome` is recognized as a skill
  2. Read through the SKILL.md and verify it covers all 4 scenarios from the design
  3. Verify the prompt references correct CLI commands and file paths
  4. Spot-check: does the personalization section use `AskUserQuestion` framing (not identity questions)?
  5. Spot-check: is personalization clearly optional/skippable?
- **Verification:** Skill prompt is complete, correct, and follows design spec
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 (create SKILL.md — the core deliverable)
2. Task 2 (register skill)
3. Task 3 (manual integration test)

## Risks
- **Skill registration mechanism unclear:** Need to verify how existing skills are registered. Mitigation: inspect settings files and existing skill config.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
| 3 | XS | -- | Integration test |
