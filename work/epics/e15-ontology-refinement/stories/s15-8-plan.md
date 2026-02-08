# Implementation Plan: Graph as Single Source of Truth

## Overview
- **Story:** S15.8
- **Story Points:** 5 SP (M)
- **Tasks:** 5
- **Created:** 2026-02-08

## Tasks

### Task 1: Tag `always_on` in graph + identity extraction
- **Description:** Add `always_on: true` metadata to critical guardrails (all MUST-*) and core principles (§1, §3, §7) in their parsers. Add `_load_identity()` to builder that extracts 5 values + 10 boundaries from `.raise/rai/identity/core.md` as `principle` nodes with `always_on: true`. Rebuild graph.
- **Files:**
  - `src/raise_cli/governance/parsers/guardrails.py` — add `always_on: True` to metadata for `MUST-*` level guardrails
  - `src/raise_cli/governance/parsers/constitution.py` — add `always_on: True` to metadata for §1, §3, §7
  - `src/raise_cli/context/builder.py` — new `_load_identity()` method, call it in `build()`
- **TDD Cycle:** RED (test always_on nodes exist after build) → GREEN → REFACTOR
- **Verification:** `pytest tests/governance/parsers/ tests/context/test_builder.py -v` + rebuild graph + verify `always_on` nodes
- **Size:** M
- **Dependencies:** None

### Task 2: Session state expansion + bundle
- **Description:** Add `EpicProgress` model and `completed_epics` to `SessionState`. Expand bundle with: `get_always_on_primes()` for governance + identity primes, `_format_recent_sessions()` reading last 3 from `sessions/index.jsonl`, `_format_progress()` for epic progress. Update `assemble_context_bundle()` to include all new sections.
- **Files:**
  - `src/raise_cli/schemas/session_state.py` — add `EpicProgress`, `completed_epics`
  - `src/raise_cli/session/bundle.py` — add `get_always_on_primes()`, `_format_governance_primes()`, `_format_identity_primes()`, `_format_recent_sessions()`, `_format_progress()`
- **TDD Cycle:** RED (test bundle output has new sections) → GREEN → REFACTOR
- **Verification:** `pytest tests/schemas/test_session_state.py tests/session/test_bundle.py -v`
- **Size:** M
- **Dependencies:** Task 1 (needs always_on nodes in graph)

### Task 3: Session close + CLI + memory generate
- **Description:** Update `process_session_close()` to write progress and completed_epics to session-state.yaml. Update session CLI to accept `--progress` and `--completed-epics` flags (or via state file). Update `raise memory generate` to skip MEMORY.md creation (both canonical and Claude Code paths).
- **Files:**
  - `src/raise_cli/session/close.py` — write progress fields to state
  - `src/raise_cli/cli/commands/session.py` — accept progress in close command
  - `src/raise_cli/cli/commands/memory.py` — skip MEMORY.md writes in generate
  - `src/raise_cli/onboarding/memory_md.py` — conditional skip or deprecate
- **TDD Cycle:** RED (test close writes progress, test generate skips MEMORY.md) → GREEN → REFACTOR
- **Verification:** `pytest tests/session/test_close.py tests/cli/commands/test_session.py tests/cli/commands/test_memory.py -v`
- **Size:** M
- **Dependencies:** Task 2 (needs EpicProgress model)

### Task 4: File shrinking + skill updates
- **Description:** Rewrite CLAUDE.md to 3-line bootstrap. Rewrite CLAUDE.local.md to 2-line bootstrap. Delete MEMORY.md. Update session-start skill to document unified bundle (remove agent.md step, document governance/identity primes). Update session-close skill to document progress output.
- **Files:**
  - `CLAUDE.md` — 3 lines
  - `CLAUDE.local.md` — 2 lines
  - Delete `~/.claude/projects/-home-emilio-Code-raise-commons/memory/MEMORY.md`
  - `.claude/skills/session-start/SKILL.md` — unified bundle documentation
  - `.claude/skills/session-close/SKILL.md` — progress output documentation
- **Verification:** File contents match design spec. Skills reference correct bundle sections.
- **Size:** S
- **Dependencies:** Tasks 1-3 (bundle must work before we cut over)

### Task 5 (Final): Manual Integration Test
- **Description:** Full lifecycle validation: `raise memory build` → verify always_on nodes → `raise session start --context` → verify bundle has governance primes, identity primes, recent sessions, progress → work → `raise session close` with progress → verify session-state.yaml → `raise session start --context` again → verify continuity. Confirm zero manual file edits needed.
- **Verification:** Demo full lifecycle working end-to-end.
- **Size:** S
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (graph: always_on + identity)
    ↓
Task 2 (state model + bundle expansion)
    ↓
Task 3 (close + CLI + memory generate)
    ↓
Task 4 (file shrinking + skills)
    ↓
Task 5 (integration test)
```

All sequential — each builds on the previous.

## Risks

- **Identity parsing brittleness**: core.md has no YAML frontmatter — regex extraction of Values/Boundaries sections. Mitigate: match `### N. ` pattern for values, `### I Will`/`### I Won't` for boundaries.
- **PAT-152**: Schema changes (new metadata) require graph rebuild. Mitigate: rebuild once after Task 1.
- **Session index empty**: If no sessions in index.jsonl, recent sessions section should gracefully degrade. Mitigate: test with empty index.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Graph always_on + identity | M | — | |
| 2 — State + bundle expansion | M | — | |
| 3 — Close + CLI + memory generate | M | — | |
| 4 — File shrinking + skills | S | — | |
| 5 — Integration test | S | — | |
