# RAISE-218 Plan

## Tasks

### T1 — Regression test (RED)
File: tests/cli/commands/test_init.py
Test: `test_init_cursor_agent_sets_ide_type_cursor`
  - `rai init --agent cursor` → `manifest.ide.type == "cursor"`
  - `rai init --agent windsurf` → `manifest.ide.type == "windsurf"`
Verify: `uv run pytest tests/cli/commands/test_init.py::TestInitCommand::test_init_cursor_agent_sets_ide_type_cursor -x`
Commit: `test(RAISE-218): regression test for ide.type/agents.types consistency [RED]`

### T2 — Fix (GREEN)
File: src/raise_cli/cli/commands/init.py
Change:
  1. Add `IdeManifest` to imports from `raise_cli.onboarding.manifest`
  2. Compute `primary = valid_agent_types[0] if valid_agent_types else "claude"`
  3. `try: ide_manifest = IdeManifest(type=primary) except Exception: ide_manifest = IdeManifest()`
  4. Pass `ide=ide_manifest` when constructing `ProjectManifest`
Verify: `uv run pytest tests/cli/commands/test_init.py -x && uv run pyright && uv run ruff check src/ tests/`
Commit: `fix(RAISE-218): sync ide.type with agents.types[0] in rai init`
