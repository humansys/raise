# RAISE-663 — Plan

## Tasks

### Task 1 — Regression tests (RED)
Write tests in `tests/adapters/test_acli_jira.py`:
- `TestAdfToText` class: unit-test `_adf_to_text()` for paragraph, nested content, string passthrough, empty/None
- `test_parses_adf_description_as_text`: extend `TestGetIssue` — verify `result.description` is readable text, not a repr

Verify: `uv run pytest tests/adapters/test_acli_jira.py -x` → **RED** (ImportError or assertion failure)

Commit: `test(RAISE-663): add regression tests for ADF description parsing`

### Task 2 — Implement _adf_to_text + wire it (GREEN)
Add `_adf_to_text(value: object) -> str` to `packages/raise-pro/src/rai_pro/adapters/acli_jira.py` (after module-level helpers).
Replace `str(fields.get("description", ""))` → `_adf_to_text(fields.get("description", ""))` at line 220.

Verify: `uv run pytest tests/adapters/test_acli_jira.py -x` → **GREEN**

Commit: `fix(RAISE-663): replace str() with _adf_to_text() in _parse_issue_detail`

### Task 3 — Remove hard-cap in backlog.py
Remove lines 231–232 in `src/raise_cli/cli/commands/backlog.py`:
```python
        if len(desc) > 500:
            desc = desc[:500] + "..."
```

Verify: `uv run pytest tests/ -x -q` + all gates

Commit: `fix(RAISE-663): remove 500-char hard-cap on description display`

### Task 4 — All gates
`uv run pytest --tb=short`
`uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
`uv run pyright`
