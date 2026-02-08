# Implementation Plan: Deterministic Session Protocol

## Overview
- **Story:** S15.7
- **Story Points:** 5 SP
- **Size:** M
- **Tasks:** 8
- **Created:** 2026-02-08
- **Design:** `s15-7-design.md`

## Tasks

### Task 1: Session State Schema + Persistence
- **Description:** Create `SessionState` Pydantic model and YAML reader/writer. This is the new `.raise/rai/session-state.yaml` artifact — project-level working state overwritten each session-close.
- **Files:**
  - Create `src/raise_cli/schemas/session_state.py` — `SessionState`, `CurrentWork`, `LastSession`, `PendingItems` models
  - Create `src/raise_cli/session/__init__.py` — module init
  - Create `src/raise_cli/session/state.py` — `load_session_state()`, `save_session_state()`, path constants
  - Create `tests/session/test_state.py` — round-trip serialization, missing file handling, schema validation
- **TDD Cycle:** RED (test load/save round-trip) → GREEN (implement models + persistence) → REFACTOR
- **Verification:** `pytest tests/session/test_state.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Developer Profile Extension (Coaching + Deadlines)
- **Description:** Extend `DeveloperProfile` with `CoachingContext` and `Deadline` models. Backward compatible — new fields default to empty. Add helper functions: `add_correction()` (FIFO cap 10), `add_deadline()`, `update_coaching()`.
- **Files:**
  - Modify `src/raise_cli/onboarding/profile.py` — add `CoachingContext`, `Correction`, `Deadline`, `RelationshipState` models; extend `DeveloperProfile`
  - Modify `tests/onboarding/test_profile.py` — backward compat (load without coaching), correction FIFO, deadline CRUD
- **TDD Cycle:** RED (test backward compat load) → GREEN (add models with defaults) → RED (test FIFO) → GREEN (implement helpers) → REFACTOR
- **Verification:** `pytest tests/onboarding/test_profile.py -v`
- **Size:** S
- **Dependencies:** None

### Task 3: Context Bundle Assembler
- **Description:** Create the context bundle assembly logic. Reads from developer profile, session state, and memory graph. Outputs token-optimized plain text (~150 tokens). This is the core of `raise session start --context`.
- **Files:**
  - Create `src/raise_cli/session/bundle.py` — `assemble_context_bundle()`, `format_context_bundle()`, section formatters
  - Create `tests/session/test_bundle.py` — output format validation, missing sources handling, token count check
- **TDD Cycle:** RED (test bundle format with mock data) → GREEN (implement assembler) → RED (test missing state graceful) → GREEN (handle edge cases) → REFACTOR
- **Verification:** `pytest tests/session/test_bundle.py -v`
- **Size:** M
- **Dependencies:** Task 1, Task 2

### Task 4: Redesign `raise session start`
- **Description:** Add `--context` flag to `raise session start`. When present, assemble and output the context bundle. Without flag, preserve current behavior (backward compat). Emit telemetry internally.
- **Files:**
  - Modify `src/raise_cli/cli/commands/session.py` — add `--context` flag, call `assemble_context_bundle()`, emit telemetry
  - Modify `tests/cli/commands/test_session.py` — test `--context` output, test backward compat, test telemetry emission
- **TDD Cycle:** RED (test --context outputs bundle) → GREEN (wire flag to assembler) → RED (test backward compat) → GREEN (preserve existing behavior) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_session.py -v`
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Redesign `raise session close`
- **Description:** Extend `raise session close` to accept structured input and perform all writes atomically. Flags: `--summary`, `--type`, `--pattern`, `--correction`, `--correction-lesson`, `--state-file`. Internally: write session-state.yaml, update coaching in developer.yaml, add patterns to patterns.jsonl, record session in index.jsonl, emit telemetry, clear current_session.
- **Files:**
  - Modify `src/raise_cli/cli/commands/session.py` — extend `close()` with new flags, atomic write orchestration
  - Create `src/raise_cli/session/close.py` — `process_session_close()` orchestrator (reads state-file or flags, performs all writes)
  - Modify `tests/cli/commands/test_session.py` — test each flag, test state-file input, test atomic writes, test telemetry
- **TDD Cycle:** RED (test close with --summary writes state) → GREEN (implement orchestrator) → RED (test --state-file) → GREEN (implement file parsing) → RED (test --pattern writes to JSONL) → GREEN (wire to memory writer) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_session.py -v`
- **Size:** M
- **Dependencies:** Task 1, Task 2

### Task 6: Tag Foundational Patterns
- **Description:** Add `"foundational": true` to metadata of 10 curated patterns in `patterns.jsonl`. Rebuild graph. Verify foundational patterns appear in graph query results with metadata.
- **Files:**
  - Modify `.raise/rai/memory/patterns.jsonl` — add metadata to PAT-187, 183, 186, 150, 154, 159, 149, 152, 153, 151
  - Add PAT-187 (Code as Gemba) if not yet recorded
- **TDD Cycle:** N/A (data curation, not code)
- **Verification:** `uv run raise memory build && uv run raise memory query "foundational" --types pattern`
- **Size:** S
- **Dependencies:** None (parallel with Tasks 1-2)

### Task 7: Update Skills (Session-Start + Session-Close)
- **Description:** Thin both skills to 2-step protocols. Session-start: call `raise session start --context`, interpret bundle, propose focus. Session-close: reflect on session (inference), write state-file, call `raise session close --state-file`. Remove all separate CLI calls from skills.
- **Files:**
  - Modify `.claude/skills/session-start/SKILL.md` — rewrite to 2 steps
  - Modify `.claude/skills/session-close/SKILL.md` — rewrite to 2 steps
- **TDD Cycle:** N/A (markdown skills, validated by usage)
- **Verification:** Manual — run `/session-start` and `/session-close` with new protocol
- **Size:** S
- **Dependencies:** Task 4, Task 5

### Task 8 (Final): Manual Integration Test
- **Description:** Full session lifecycle with new protocol. Start a session, verify context bundle output, do some work, close session with structured input, start next session and verify continuity (state carried, coaching updated, foundational patterns surfaced).
- **Verification:**
  1. `raise session start --project . --context` → verify bundle format
  2. `raise session close --summary "test" --type feature --state-file output.yaml` → verify all writes
  3. `raise session start --project . --context` → verify state carries over
  4. Check `~/.rai/developer.yaml` has coaching section
  5. Check `.raise/rai/session-state.yaml` exists and is correct
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (session-state schema) ──┐
Task 2 (profile extension)   ──┼──► Task 3 (bundle assembler) ──► Task 4 (start cmd)──┐
Task 6 (tag patterns)        ──┘                                                       ├──► Task 7 (skills) ──► Task 8 (integration)
                                                                Task 5 (close cmd)  ───┘
```

**Parallel opportunities:**
- Tasks 1, 2, 6 are independent — can run in parallel
- Tasks 4, 5 are independent after their deps — can run in parallel
- Task 7 needs both 4 and 5 complete
- Task 8 is final validation

**Recommended sequential order:**
1. Task 1 (schema foundation)
2. Task 2 (profile extension)
3. Task 6 (pattern tagging — data, quick)
4. Task 3 (bundle assembler — core logic)
5. Task 4 + Task 5 (CLI commands — can parallelize)
6. Task 7 (skill updates)
7. Task 8 (integration test)

## Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Profile schema change breaks existing YAML | M | H | Backward compat: all new fields have defaults. Test with current developer.yaml. |
| Session close atomicity — partial writes on failure | M | M | Write to temp files first, rename on success. Or accept partial (JSONL append is already atomic). |
| Context bundle format not token-efficient enough | L | L | Measure actual token count in integration test. Target <200. |
| Graph query for foundational patterns returns nothing | L | M | Task 6 tags patterns and rebuilds graph before Task 3 needs them. Verify in isolation. |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1. Session State Schema | S | — | |
| 2. Profile Extension | S | — | |
| 3. Bundle Assembler | M | — | |
| 4. Start Command | S | — | |
| 5. Close Command | M | — | |
| 6. Tag Patterns | S | — | Data curation |
| 7. Update Skills | S | — | Markdown only |
| 8. Integration Test | XS | — | |
