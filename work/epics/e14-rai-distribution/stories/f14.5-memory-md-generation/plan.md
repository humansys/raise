# Implementation Plan: F14.5 Two-Part MEMORY.md Generation

## Overview
- **Feature:** F14.5
- **Story Points:** 3 SP
- **Feature Size:** M
- **Created:** 2026-02-06
- **Design:** `stories/f14.5-memory-md-generation/design.md`

## Tasks

### Task 1: Path helper + MemoryMdGenerator core (Part 1)
- **Description:** Add `get_claude_memory_path()` to paths.py. Create `onboarding/memory_md.py` with `MemoryMdGenerator` class that parses methodology.yaml and generates Part 1 (lifecycle, skills, gates, principles, branches). Generator returns `str`, no path knowledge.
- **Files:**
  - `src/raise_cli/config/paths.py` (modify — add `get_claude_memory_path`)
  - `src/raise_cli/onboarding/memory_md.py` (create — generator class)
  - `tests/onboarding/test_memory_md.py` (create — Part 1 tests)
  - `tests/config/test_paths.py` (modify — path helper tests)
- **TDD Cycle:**
  - RED: Test `get_claude_memory_path()` returns correct path. Test generator produces markdown with all methodology sections from a sample methodology.yaml.
  - GREEN: Implement path helper and generator Part 1.
  - REFACTOR: Extract section builders into private methods.
- **Verification:** `pytest tests/onboarding/test_memory_md.py tests/config/test_paths.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Generator Part 2 (patterns) + convenience function
- **Description:** Add Part 2 generation (read patterns.jsonl, select top N, render as markdown). Add `generate_memory_md()` convenience function wrapping class. Handle graceful degradation (empty/missing files).
- **Files:**
  - `src/raise_cli/onboarding/memory_md.py` (modify — add Part 2 + convenience function)
  - `tests/onboarding/test_memory_md.py` (modify — Part 2 tests, edge cases)
- **TDD Cycle:**
  - RED: Test Part 2 renders patterns. Test empty patterns.jsonl produces section with "No patterns yet". Test missing methodology.yaml degrades gracefully. Test full `generate_memory_md()` output.
  - GREEN: Implement Part 2 and convenience function.
  - REFACTOR: Clean up, ensure idempotency.
- **Verification:** `pytest tests/onboarding/test_memory_md.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: CLI command + init integration
- **Description:** Add `raise memory generate` subcommand that generates MEMORY.md to both canonical (`.raise/rai/memory/MEMORY.md`) and Claude Code (`~/.claude/projects/{path}/memory/MEMORY.md`) locations. Hook into `raise init` after bootstrap step.
- **Files:**
  - `src/raise_cli/cli/commands/memory.py` (modify — add `generate` command)
  - `src/raise_cli/cli/commands/init.py` (modify — call generator after bootstrap)
  - `tests/cli/commands/test_memory_generate.py` (create — CLI tests)
  - `tests/cli/commands/test_init.py` (modify — verify MEMORY.md generated)
- **TDD Cycle:**
  - RED: Test `raise memory generate` writes to both paths. Test `raise init` triggers generation. Test output messages.
  - GREEN: Implement CLI command and init integration.
  - REFACTOR: Ensure consistent error handling.
- **Verification:** `pytest tests/cli/commands/test_memory_generate.py tests/cli/commands/test_init.py -v`
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Quality gates + manual integration test
- **Description:** Run full quality suite (ruff, pyright, bandit, coverage). Then manually test `raise memory generate` and verify output matches expected MEMORY.md format. Test `raise init` in a temp directory to verify end-to-end flow.
- **Files:** None (verification only)
- **Verification:**
  - `ruff check . && ruff format --check .`
  - `pyright --strict src/raise_cli/onboarding/memory_md.py src/raise_cli/config/paths.py`
  - `pytest --cov=src/raise_cli/onboarding/memory_md --cov-fail-under=90`
  - Manual: `raise memory generate` in this project, inspect output
- **Size:** S
- **Dependencies:** Task 3

## Execution Order

```
Task 1 (path helper + Part 1 generator)
  ↓
Task 2 (Part 2 + convenience function)
  ↓
Task 3 (CLI command + init integration)
  ↓
Task 4 (quality gates + integration test)
```

All sequential — each builds on the previous.

## Risks

| Risk | Mitigation |
|------|------------|
| Claude Code path convention mismatch | Verify against actual `~/.claude/projects/` directory |
| methodology.yaml schema changes | Generator reads what's there, doesn't assume fixed keys |
| Existing init tests break with new step | Mock the generator call in existing tests |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | M | -- | |
| 4 | S | -- | |
