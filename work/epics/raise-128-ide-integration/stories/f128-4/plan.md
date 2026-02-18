# Implementation Plan: F128.4 — Init --ide Flag + E2E Tests

## Overview
- **Feature:** F128.4
- **Size:** S
- **Created:** 2026-02-18

## Tasks

### Task 1: Add --ide flag and wire IdeConfig through init_command
- **Description:** Add `--ide` Typer option to `init_command()`. Create `IdeConfig` via `get_ide_config(ide)`. Pass it to `scaffold_skills()`, `scaffold_workflows()`, and `generate_claude_md()`. Update instructions file write path to use `ide_config.instructions_file`. Make MEMORY.md Claude Code copy conditional on `ide_type == "claude"`. Update `_get_project_message()` to use `ide_config.skills_dir` in output messages instead of hardcoded `.claude/skills/`.
- **Files:** `src/rai_cli/cli/commands/init.py`
- **TDD Cycle:** RED (write failing test for `--ide antigravity`) → GREEN (wire the flag) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_init.py -x`
- **Size:** S
- **Dependencies:** None

### Task 2: E2E tests for both IDE paths
- **Description:** Add test class `TestInitIdeFlag` with tests covering: (1) default `rai init` produces `.claude/skills/` + `CLAUDE.md` (backward compat), (2) explicit `--ide claude` identical to default, (3) `--ide antigravity` produces `.agent/skills/`, `.agent/rules/raise.md`, `.agent/workflows/`, (4) `--ide antigravity` does NOT create Claude Code MEMORY.md copy, (5) `--ide antigravity` with `--detect` writes to `.agent/rules/raise.md` not `CLAUDE.md`, (6) canonical MEMORY.md still exists for both IDEs.
- **Files:** `tests/cli/commands/test_init.py`
- **TDD Cycle:** RED (tests fail before Task 1 implementation) → GREEN (pass after Task 1)
- **Verification:** `pytest tests/cli/commands/test_init.py::TestInitIdeFlag -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Quality gates + manual integration test
- **Description:** Run all quality gates (ruff, pyright, bandit, pytest with coverage). Then manually verify `rai init --help` shows `--ide` option. Verify full test suite passes.
- **Files:** None (verification only)
- **Verification:** `ruff check src/ && pyright && pytest --tb=short`
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 + Task 2 (write tests first in RED, then implement in Task 1 to go GREEN)
2. Task 3 (final validation)

## Risks
- `generate_claude_md` ignores `ide_config` internally (content is Claude-centric). For now this is acceptable — the function returns generic content, and the caller controls the file path. A future story could make the content IDE-aware.
- The `--detect` code path also writes `CLAUDE.md` — must update both the normal and `--detect` paths to use `ide_config.instructions_file`.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
