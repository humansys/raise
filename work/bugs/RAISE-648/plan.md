# RAISE-648: Plan

## Tasks

### T1: Regression test — duplicate node causes crash (RED)
- Test that `GraphBuilder.build()` with duplicate nodes crashes (current behavior)
- Test that with `strict=False`, duplicates are skipped with warnings
- Test that with `strict=True`, duplicates raise ValueError
- Verify: `uv run pytest packages/raise-cli/tests/context/test_builder.py -x -k duplicate` — FAILS
- Commit: `test(RAISE-648): regression tests for duplicate node ID handling`

### T2: Add strict param + warn+skip to GraphBuilder (GREEN)
- Add `strict: bool = False` to `GraphBuilder.__init__()`
- Replace ValueError with warn+skip when `strict=False`, keep raise when `strict=True`
- Store warnings in `self.warnings: list[str]` for CLI consumption
- Verify: `uv run pytest packages/raise-cli/tests/context/test_builder.py -x -k duplicate` — PASSES
- Commit: `fix(RAISE-648): warn+skip duplicate node IDs, --strict to raise`

### T3: Add --strict flag to CLI command
- Add `--strict` flag to `rai graph build` in `cli/commands/graph.py`
- Pass to `GraphBuilder(strict=strict)`
- Print warnings after build if any
- Verify: `uv run pytest packages/raise-cli/tests/cli/ -x -k graph_build` + lint + types
- Commit: `feat(RAISE-648): add --strict flag to rai graph build`
