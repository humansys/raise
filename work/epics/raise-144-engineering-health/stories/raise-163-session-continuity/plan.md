# Implementation Plan: RAISE-163

## Overview
- **Story:** RAISE-163 — Session continuity and CLI reference improvements
- **Size:** S
- **Created:** 2026-02-17

## Tasks

### Task 1: Add `next_session_prompt` to schema and close pipeline
- **Description:** Add field to `SessionState` Pydantic model, `CloseInput` dataclass, `load_state_file`, and `process_session_close` wiring.
- **Files:**
  - `src/rai_cli/schemas/session_state.py` — add field to `SessionState`
  - `src/rai_cli/session/close.py` — add to `CloseInput`, `load_state_file`, constructor call
- **TDD Cycle:** RED (test that state file with `next_session_prompt` round-trips) → GREEN → REFACTOR
- **Verification:** `pytest tests/session/test_close.py tests/session/test_state.py -x`
- **Size:** S
- **Dependencies:** None

### Task 2: Add `next_session_prompt` to context bundle output
- **Description:** Read the field from `SessionState` and emit it in the context bundle as a dedicated section before pending items.
- **Files:**
  - `src/rai_cli/session/bundle.py` — add `_format_next_session_prompt` + wire into `assemble_context_bundle`
- **TDD Cycle:** RED (test bundle includes prompt when present, omits when empty) → GREEN → REFACTOR
- **Verification:** `pytest tests/session/test_bundle.py -x`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Update skills (session-close and session-start)
- **Description:** Add step 11 to session-close SKILL.md for writing `next_session_prompt`. Add instruction to session-start SKILL.md to read and present it. Update both source copies (skills_base/) and local copies (.claude/skills/).
- **Files:**
  - `src/rai_cli/skills_base/rai-session-close/SKILL.md`
  - `src/rai_cli/skills_base/rai-session-start/SKILL.md`
  - `.claude/skills/rai-session-close/SKILL.md`
  - `.claude/skills/rai-session-start/SKILL.md`
- **TDD Cycle:** N/A (documentation)
- **Verification:** Manual review — skills reference the new field
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Regenerate CLI reference and add behavioral rule
- **Description:** Run all `rai --help` subcommands, regenerate `cli-reference.md` from actual output. Add behavioral rule to MEMORY.md: "MUST consult cli-reference.md before running any rai command."
- **Files:**
  - `~/.claude/projects/-home-emilio-Code-raise-commons/memory/cli-reference.md`
  - `~/.claude/projects/-home-emilio-Code-raise-commons/memory/MEMORY.md`
- **TDD Cycle:** N/A (memory files)
- **Verification:** Reference matches actual --help output
- **Size:** S
- **Dependencies:** None

### Task 5: Manual Integration Test
- **Description:** Run full `rai session close` with state file containing `next_session_prompt`, then `rai session start` and verify the prompt appears in the context bundle.
- **Verification:** End-to-end round-trip works
- **Size:** XS
- **Dependencies:** Tasks 1-4

## Execution Order
1. Task 1 + Task 4 (parallel — independent)
2. Task 2 (depends on 1)
3. Task 3 (depends on 1)
4. Task 5 (integration test — depends on all)

## Risks
- Schema change could break existing session-state.yaml files → Mitigated: field has default empty string, backward compatible.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | Schema + close pipeline |
| 2 | XS | -- | Bundle formatting |
| 3 | S | -- | 4 skill files |
| 4 | S | -- | Memory files |
| 5 | XS | -- | Integration test |
