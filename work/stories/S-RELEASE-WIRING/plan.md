# Implementation Plan: S-RELEASE-WIRING

## Overview
- **Story:** S-RELEASE-WIRING — Wire release into CLI, session & skills
- **Size:** M (moderate — 8 files modified, 1 created, 7 skills updated)
- **Created:** 2026-02-13

## Tasks

### Task 1: Add `release` field to CurrentWork schema + close wiring
- **Description:** Add `release: str = ""` to `CurrentWork` model with validator. Wire through `CloseInput` → `process_session_close` so the release field persists in session-state.yaml.
- **Files:**
  - `src/rai_cli/schemas/session_state.py` — add field + validator
  - `src/rai_cli/session/close.py` — wire `release` in CurrentWork construction
- **TDD Cycle:**
  - RED: Test `CurrentWork(release="V3.0")` works, `CurrentWork(release=None)` coerces to `""`
  - RED: Test close persists release field in session state
  - GREEN: Add field, update validator, wire through close
  - REFACTOR: Verify existing tests still pass
- **Verification:** `uv run pytest tests/schemas/ tests/session/ -x`
- **Size:** S
- **Dependencies:** None

### Task 2: Add `find_release_for()` to query engine
- **Description:** Add helper method to `UnifiedQueryEngine` that follows `part_of` edges from an epic node to find its parent release. Same pattern as `find_domain_for()`.
- **Files:**
  - `src/rai_cli/context/query.py` — add `find_release_for()` method
- **TDD Cycle:**
  - RED: Test with mock graph containing epic→release part_of edge returns release node
  - RED: Test with epic that has no release returns None
  - RED: Test with nonexistent epic returns None
  - GREEN: Implement method
- **Verification:** `uv run pytest tests/context/test_query*.py -x`
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Surface release in session context bundle
- **Description:** Update `_format_work_section()` in bundle.py to query graph for release context when the current epic is part of a release. Add release line before Story line. Graceful degradation when graph missing or no release found.
- **Files:**
  - `src/rai_cli/session/bundle.py` — update `_format_work_section()` signature and logic
- **TDD Cycle:**
  - RED: Test bundle output includes release line when graph has release→epic edge
  - RED: Test bundle output omits release line when no graph / no release found
  - GREEN: Load graph in bundle, call `find_release_for()`, format release line
  - REFACTOR: Ensure token budget stays reasonable
- **Verification:** `uv run pytest tests/session/test_bundle*.py -x`
- **Size:** M
- **Dependencies:** Task 2 (needs `find_release_for()`)

### Task 4: Create `rai release list` CLI command
- **Description:** New command group `release` with `list` subcommand. Loads the memory graph, filters for `type="release"` nodes, formats output as table. Errors with hint if graph not built.
- **Files:**
  - `src/rai_cli/cli/commands/release.py` — **create** release_app with `list` command
  - `src/rai_cli/cli/main.py` — register release_app
- **TDD Cycle:**
  - RED: Test `rai release list` with graph containing 2 releases shows both
  - RED: Test with no graph shows error + hint
  - RED: Test with graph but no releases shows empty message
  - GREEN: Implement command
- **Verification:** `uv run pytest tests/cli/test_release*.py -x`
- **Size:** M
- **Dependencies:** None (uses graph directly, not query engine)

### Task 5: Add release to `rai memory validate` expected types
- **Description:** Add `"release": 1` to `expected_types` dict in validate command so completeness check flags missing release nodes.
- **Files:**
  - `src/rai_cli/cli/commands/memory.py` — update `expected_types` dict
- **TDD Cycle:**
  - RED: Test validate reports completeness gap when no release nodes exist
  - GREEN: Add `"release": 1` to dict
- **Verification:** `uv run pytest tests/cli/test_memory*.py -x`
- **Size:** XS
- **Dependencies:** None (parallel with all)

### Task 6: Update 7 skills with release language
- **Description:** Edit SKILL.md files to add release context, templates, and guidance. Pure documentation — no code changes.
- **Files:**
  - `.claude/skills/rai-session-start/SKILL.md`
  - `.claude/skills/rai-session-close/SKILL.md`
  - `.claude/skills/rai-epic-start/SKILL.md`
  - `.claude/skills/rai-epic-design/SKILL.md`
  - `.claude/skills/rai-epic-plan/SKILL.md`
  - `.claude/skills/rai-epic-close/SKILL.md`
  - `.claude/skills/rai-story-start/SKILL.md`
- **Changes per skill:** See design.md § Skill Updates
- **TDD Cycle:** N/A (SKILL.md files, not code)
- **Verification:** Manual review — each skill mentions release in appropriate context
- **Size:** M
- **Dependencies:** Tasks 1-5 (skills reference CLI behavior that must exist first)

### Task 7: Full validation + manual integration test
- **Description:** Run full test suite, type checks, lint. Then manually test: `rai memory build`, `rai release list`, `rai session start --context`, `rai memory validate`.
- **Verification:**
  - `uv run pytest --tb=short`
  - `uv run pyright`
  - `uv run ruff check src/`
  - Manual: `rai memory build && rai release list`
  - Manual: `rai session start --project "$(pwd)" --context` (verify release line)
  - Manual: `rai memory validate` (verify release check)
- **Size:** S
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (schema)  ──┐
Task 2 (query)   ──┼── parallel, no deps
Task 5 (validate)──┘
         │
         ▼
Task 3 (bundle) ── depends on Task 2
Task 4 (CLI)    ── parallel with Task 3
         │
         ▼
Task 6 (skills) ── after code tasks complete
         │
         ▼
Task 7 (integration test) ── final validation
```

**Optimal sequence:** T1 + T2 + T5 (parallel) → T3 + T4 (parallel) → T6 → T7

**Practical sequence (single agent):** T1 → T2 → T3 → T4 → T5 → T6 → T7

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Bundle graph loading adds latency to session start | M | L | Graph already loaded for primes; reuse same instance |
| Existing bundle tests break with new signature | L | M | Read existing tests first, extend don't replace |
| Session state YAML migration (existing files lack `release`) | L | L | Default `""` handles missing field via validator |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1. Schema + close | S | -- | |
| 2. Query helper | S | -- | |
| 3. Bundle | M | -- | |
| 4. CLI command | M | -- | |
| 5. Validate | XS | -- | |
| 6. Skills (7) | M | -- | |
| 7. Integration test | S | -- | |
