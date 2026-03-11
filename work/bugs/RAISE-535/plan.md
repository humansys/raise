# RAISE-535: Fix Plan

## Tasks (TDD order)

### T1: Regression test RED
- Add test asserting `_analyze_module` extracts imports from both `__init__.py` and regular files
- Verify: `uv run pytest tests/context/ -k "init_imports" --tb=short` → PASS (behavior test, not failure test)

### T2: Remove dead condition
- Collapse if/else to unconditional import extraction (both branches identical)
- Verify: `uv run pytest tests/context/ --tb=short` → PASS, same behavior
