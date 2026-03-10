# RAISE-520 Plan — Path injection via --memory-dir flag

## Tasks

### T1 — Regression tests RED
Write tests that pass a `../`-traversal path via `memory_dir` and assert
it resolves to a canonical absolute path (no `..` components).

Verify: `uv run pytest tests/cli/test_pattern_commands.py -k "memory_dir" --tb=short` (red)
Commit: `test(RAISE-520): regression tests RED — --memory-dir path traversal`

### T2 — Apply .resolve() in pattern.py (3 sites)
- line 110: `mem_dir = (memory_dir or get_memory_dir_for_scope(memory_scope)).resolve()`
- line 211: same
- line 282: same pattern for `personal_dir`

Verify: `uv run pytest --tb=short && uv run ruff check src/ tests/ && uv run pyright`
Commit: `fix(RAISE-520): apply .resolve() to --memory-dir in pattern commands`
