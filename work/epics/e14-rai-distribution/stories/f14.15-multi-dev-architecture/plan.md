# Implementation Plan: Multi-Developer Architecture

## Overview

- **Feature:** F14.15
- **Story Points:** 5 SP
- **Feature Size:** L
- **Created:** 2026-02-05
- **Research:** RES-MULTIDEV-001, RES-MULTIDEV-002

## Architecture Summary

Three-tier data separation with graph as abstraction layer:

```
~/.rai/                      # GLOBAL (cross-repo)
├── developer.yaml           # Identity (exists)
├── patterns.jsonl           # Universal patterns (NEW)
└── calibration.jsonl        # Global calibration (NEW)

.raise/rai/memory/           # PROJECT (shared, committed)
├── patterns.jsonl           # Project patterns
└── index.json               # Graph index

.raise/rai/personal/         # PERSONAL (gitignored)
├── sessions/index.jsonl     # My sessions
├── telemetry/signals.jsonl  # My telemetry
├── calibration.jsonl        # Project-specific calibration
└── patterns.jsonl           # Project-specific learnings
```

## Tasks

### Task 1: Add Path Helpers
- **Description:** Add `get_global_rai_dir()` and `get_personal_dir()` to paths.py
- **Files:** `src/rai_cli/config/paths.py`, `tests/config/test_paths.py`
- **TDD Cycle:** RED (test new functions) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/config/test_paths.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Add Scope to Memory Models
- **Description:** Add `MemoryScope` enum and update loader to track scope in metadata
- **Files:** `src/rai_cli/memory/models.py`, `src/rai_cli/memory/loader.py`, `tests/memory/test_loader.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/memory/test_loader.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Multi-Source Graph Builder
- **Description:** Modify `UnifiedGraphBuilder.load_memory()` to load from global, project, and personal directories with scope tracking
- **Files:** `src/rai_cli/context/builder.py`, `tests/context/test_builder.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/context/test_builder.py -v`
- **Size:** M
- **Dependencies:** Task 1, Task 2

### Task 4: Precedence Logic
- **Description:** Add `_deduplicate_by_precedence()` for handling same ID in multiple tiers (personal > project > global)
- **Files:** `src/rai_cli/context/builder.py`, `tests/context/test_builder.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/context/test_builder.py::test_precedence -v`
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Scope-Aware Memory Writer
- **Description:** Update `append_pattern`, `append_calibration`, `append_session` to write to correct location based on scope
- **Files:** `src/rai_cli/memory/writer.py`, `tests/memory/test_writer.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/memory/test_writer.py -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 6: Update Memory CLI Commands
- **Description:** Add `--scope` option to `emit-pattern`, `emit-calibration` commands; update `add-session` to write to personal
- **Files:** `src/rai_cli/cli/commands/memory.py`, `tests/cli/commands/test_memory.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_memory.py -v`
- **Size:** M
- **Dependencies:** Task 5

### Task 7: Migration Logic
- **Description:** Add migration function to move existing sessions/telemetry/calibration to personal dir on first access
- **Files:** `src/rai_cli/memory/migration.py` (new), `tests/memory/test_migration.py` (new)
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/memory/test_migration.py -v`
- **Size:** M
- **Dependencies:** Task 1

### Task 8: Update Gitignore
- **Description:** Add `.raise/rai/personal/` to project .gitignore template and update existing .gitignore
- **Files:** `.gitignore`, `src/rai_cli/onboarding/templates/gitignore.txt` (if exists)
- **TDD Cycle:** N/A (config change)
- **Verification:** `git check-ignore .raise/rai/personal/test.txt` returns path
- **Size:** XS
- **Dependencies:** None

### Task 9: Global Directory Bootstrap
- **Description:** Add `ensure_global_rai_dir()` to create `~/.rai/` with empty patterns.jsonl and calibration.jsonl on first use
- **Files:** `src/rai_cli/config/paths.py`, `tests/config/test_paths.py`
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/config/test_paths.py::test_ensure_global -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 10: Integration - Memory Build Command
- **Description:** Ensure `rai memory build` loads from all three tiers correctly
- **Files:** `src/rai_cli/cli/commands/memory.py` (verify), integration test
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `uv run rai memory build && uv run rai memory query "test" --format json | grep scope`
- **Size:** S
- **Dependencies:** Task 3, Task 4, Task 7

### Task 11 (Final): Manual Integration Test
- **Description:** Validate full flow: create global pattern, create project pattern, query returns both with correct scope
- **Verification:**
  1. `echo '{"id":"PAT-GLOBAL","type":"process","content":"Global test","context":[],"created":"2026-02-05"}' >> ~/.rai/patterns.jsonl`
  2. `uv run rai memory build`
  3. `uv run rai memory query "Global test"` shows scope: global
  4. Clean up test data
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (paths) ──┬── Task 2 (models) ── Task 3 (builder) ── Task 4 (precedence) ──┐
                 │                                                                  │
                 ├── Task 5 (writer) ── Task 6 (CLI) ─────────────────────────────┤
                 │                                                                  │
                 ├── Task 7 (migration) ───────────────────────────────────────────┤
                 │                                                                  │
                 ├── Task 8 (gitignore) ───────────────────────────────────────────┤
                 │                                                                  │
                 └── Task 9 (bootstrap) ───────────────────────────────────────────┤
                                                                                    │
                                                          Task 10 (integration) ───┤
                                                                                    │
                                                          Task 11 (manual test) ───┘
```

**Parallel opportunities:**
- Tasks 2, 5, 7, 8, 9 can run in parallel after Task 1
- Tasks 3, 6 depend on their predecessors

**Recommended sequence:**
1. Task 1 (foundation)
2. Task 8 (quick win, no deps)
3. Task 2, Task 9 (parallel, both small)
4. Task 3 (core logic)
5. Task 4 (precedence)
6. Task 5 (writer)
7. Task 6 (CLI)
8. Task 7 (migration)
9. Task 10 (integration)
10. Task 11 (manual test)

## Risks

| Risk | Mitigation |
|------|------------|
| Migration loses data | Copy first, verify, then mark original as backup |
| Precedence logic complex | Start simple (last wins), add smarter merging later |
| Global dir permissions | Use standard ~/.rai/ pattern, same as developer.yaml |
| Tests flaky with home dir | Use tmp dirs with monkeypatch for HOME |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1 | S | 15-30 min | -- | |
| 2 | S | 15-30 min | -- | |
| 3 | M | 30-60 min | -- | Core complexity |
| 4 | S | 15-30 min | -- | |
| 5 | M | 30-60 min | -- | |
| 6 | M | 30-60 min | -- | |
| 7 | M | 30-60 min | -- | |
| 8 | XS | <15 min | -- | |
| 9 | S | 15-30 min | -- | |
| 10 | S | 15-30 min | -- | |
| 11 | XS | <15 min | -- | |
| **Total** | **L** | **3-5 hours** | -- | |

## References

- Research: `work/research/multi-dev-config/`
- Epic scope: `work/epics/e14-rai-distribution/scope.md` (F14.15 section)
- Pattern PAT-053: Graph-first context loading
- Pattern PAT-054: Query graph first, raw files as fallback
