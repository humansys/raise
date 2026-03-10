# RAISE-522 — Plan

## Tasks

### T1 — Regression test RED
Write test: call reinforce_pattern() with a traversal path (e.g., /tmp/safe/../evil).
Verify that file_path.resolve() is called before file access.
Test file: tests/memory/test_writer.py
Commit: test(RAISE-522): regression — reinforce_pattern resolves file_path internally

### T2 — Fix GREEN
Add `file_path = file_path.resolve()` at entry of reinforce_pattern().
Commit: fix(RAISE-522): reinforce_pattern resolves file_path at entry

### T3 — Scope commit
Commit scope + analysis + plan artifacts.
Commit: chore(RAISE-522): scope, analysis, plan artifacts

## Verification

uv run pytest tests/memory/test_writer.py -x -q
uv run ruff check src/raise_cli/memory/writer.py
uv run pyright src/raise_cli/memory/writer.py
