# Implementation Plan: Session Narrative

## Overview
- **Story:** HF-1
- **Story Points:** 3 SP
- **Size:** S
- **Created:** 2026-02-14
- **Design:** `work/hotfixes/hf-1-session-narrative/design.md`
- **Research:** `work/research/session-memory-continuity/`

## Tasks

### Task 1: Schema + Close Wiring
- **Description:** Add `narrative: str = ""` to `SessionState` model. Add `narrative: str = ""` to `CloseInput` dataclass. Wire `load_state_file` to extract narrative from YAML. Wire `process_session_close` to pass narrative into SessionState.
- **Files:**
  - `src/rai_cli/schemas/session_state.py` — add field
  - `src/rai_cli/session/close.py` — add to CloseInput, load_state_file, process_session_close
  - `tests/schemas/test_session_state.py` — schema tests
  - `tests/session/test_close.py` — close wiring tests
- **TDD Cycle:**
  - RED: Test SessionState accepts narrative field, test backward compat (no narrative in YAML), test load_state_file extracts narrative, test process_session_close persists narrative
  - GREEN: Add field + wiring
  - REFACTOR: Verify no dead code
- **Verification:** `pytest tests/schemas/test_session_state.py tests/session/test_close.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Bundle Wiring
- **Description:** Add `_format_narrative()` to bundle.py that loads `state.narrative` and formats it as a `# Session Narrative` section. Include in `assemble_context_bundle` after "Last:" and recent sessions, before primes. Omit section when narrative is empty.
- **Files:**
  - `src/rai_cli/session/bundle.py` — add formatter, wire into assembly
  - `tests/session/test_bundle.py` — bundle tests
- **TDD Cycle:**
  - RED: Test bundle includes narrative section when present, test bundle omits narrative when empty, test narrative is NOT truncated
  - GREEN: Add formatter + wire into assembly
  - REFACTOR: Verify section ordering
- **Verification:** `pytest tests/session/test_bundle.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Skill Updates + Integration Test
- **Description:** Update session-close skill template to include `narrative` field with structure guidance (4 sections: Decisions, Research, Artifacts, Branch State; ~300-500 tokens). Update session-start skill to mention narrative in bundle description. Run full test suite + manual integration test with `rai session` commands.
- **Files:**
  - `.claude/skills/rai-session-close/SKILL.md` — add narrative to YAML template
  - `.claude/skills/rai-session-start/SKILL.md` — mention narrative section
- **TDD Cycle:** N/A (skill files, no code tests)
- **Verification:**
  - `pytest tests/ -x -q` (full suite passes)
  - `pyright src/` (type checks pass)
  - `ruff check src/` (lint passes)
  - Manual: create state file with narrative, run `rai session close`, verify session-state.yaml has narrative, run `rai session start --context`, verify narrative appears in bundle
- **Size:** S
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — Schema + Close (foundation)
2. Task 2 — Bundle (depends on schema)
3. Task 3 — Skills + Integration (depends on both)

## Risks
| Risk | Mitigation |
|------|------------|
| Existing tests break from schema change | Pydantic default `""` ensures backward compat — no existing test touches narrative |
| Bundle output too large with narrative | Skill template guides size (~300-500 tokens). No enforcement needed for v1 |
| PAT-E-240 (skill instructions are code) | Task 3 explicitly updates both skills to match new behavior |

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
