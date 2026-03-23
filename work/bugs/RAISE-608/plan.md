# Plan: RAISE-608

## Tasks

### Task 1: Regression test (RED)
Write a test that verifies `pattern add` without --scope writes to project scope and can be found by `reinforce` without --scope.

File: `tests/cli/commands/test_pattern.py`
Test: `test_add_then_reinforce_default_scope_round_trip`

Verification: `uv run pytest tests/cli/commands/test_pattern.py::TestPatternAddCommand::test_add_then_reinforce_default_scope_round_trip -x`
Expected: FAIL (red)
Commit: `test(RAISE-608): add regression test for add→reinforce default scope round-trip`

### Task 2: Fix — change default scope (GREEN)
Change `pattern add` default scope from `"personal"` to `"project"`.

File: `src/raise_cli/cli/commands/pattern.py:176`
Change: `] = "personal"` → `] = "project"`

Verification: run regression test → PASS (green)
Commit: `fix(RAISE-608): change pattern add default scope from personal to project`

### Task 3: Update affected tests
Update tests that assert the old personal-default behavior:
- `test_add_pattern_creates_missing_dir`: change assertion from personal_dir to memory_dir
- `test_add_pattern_defaults_to_personal_scope`: rename + invert — now tests project default

File: `tests/cli/commands/test_pattern.py`
Verification: `uv run pytest tests/cli/commands/test_pattern.py -x`
Commit: `test(RAISE-608): update tests to reflect project as default scope for pattern add`

### Task 4: Full gate verification
Run all four gates.

Commands:
  uv run pytest --tb=short
  uv run ruff check src/ tests/
  uv run ruff format --check src/ tests/
  uv run pyright
