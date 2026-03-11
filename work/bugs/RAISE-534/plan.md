# RAISE-534: Fix Plan

## Tasks (TDD order)

### T1: Regression test RED
- Add test for `_parse_gitignore_patterns` verifying bare names get `**/name/**` and path entries get `entry/**`
- Verify: `uv run pytest tests/discovery/test_scanner.py -k gitignore --tb=short` → FAIL

### T2: Fix the else branch
- Change else branch from `f"**/{entry}/**"` to `f"{entry}/**"`
- Verify: `uv run pytest tests/discovery/test_scanner.py -k gitignore --tb=short` → PASS
