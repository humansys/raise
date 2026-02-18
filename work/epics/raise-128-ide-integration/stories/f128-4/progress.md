# Progress: F128.4 — Init --ide Flag + E2E Tests

## Status
- **Started:** 2026-02-18
- **Current Task:** 3 of 3
- **Status:** Complete

## Completed Tasks

### Task 1: Add --ide flag and wire IdeConfig through init_command
- **Files:** `src/rai_cli/cli/commands/init.py`
- **Changes:**
  - Added `--ide` Typer option (IdeType, default "claude")
  - Created IdeConfig via `get_ide_config(ide)`
  - Passed `ide_config` to `scaffold_skills()`, `scaffold_workflows()`, `generate_claude_md()`
  - Made MEMORY.md Claude Code copy conditional on `ide_type == "claude"`
  - Updated `_get_project_message()` to use dynamic `skills_dir` from IdeConfig
  - Updated both `--detect` code paths (brownfield + greenfield) to use `ide_config.instructions_file`
- **Size:** S

### Task 2: E2E tests for both IDE paths
- **Files:** `tests/cli/commands/test_init.py`
- **Tests added (6):**
  1. `test_default_produces_claude_structure` — backward compat
  2. `test_explicit_claude_identical_to_default` — explicit flag same as default
  3. `test_antigravity_produces_agent_structure` — .agent/ skills + workflows
  4. `test_antigravity_no_claude_memory_copy` — no Claude Code MEMORY.md
  5. `test_antigravity_with_detect` — instructions file at .agent/rules/raise.md
  6. `test_canonical_memory_exists_for_both_ides` — canonical always present
- **Size:** S

### Task 3: Quality gates + manual integration test
- **Results:**
  - ruff: All checks passed
  - pyright: 0 errors
  - pytest: 39/39 passed (all existing + 6 new)
  - `--help` shows `--ide [claude|antigravity]` with correct default
- **Size:** XS

## Blockers
- None

## Discoveries
- `generate_claude_md()` accepts `ide_config` but the internal `ClaudeMdGenerator` doesn't use it yet — content is still Claude-centric. Acceptable for now since the caller controls the file path.
- The `--detect` code path had two separate places writing to hardcoded `CLAUDE.md` (brownfield + greenfield) — both needed updating.
- Testing MEMORY.md non-creation for antigravity required mocking `get_claude_memory_path` at the source module level, not the init module, due to lazy imports.
