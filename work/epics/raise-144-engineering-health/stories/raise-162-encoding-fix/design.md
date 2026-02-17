# RAISE-162: Add encoding="utf-8" to read_text() calls in test suite

## What & Why

**Problem:** 123 `read_text()` calls across 26 test files lack explicit `encoding="utf-8"`. On Linux this works by accident (UTF-8 is the OS default), but on Windows `pathlib` defaults to `cp1252`, causing `UnicodeDecodeError` when test fixtures contain non-ASCII characters.

**Value:** Cross-platform test reliability. Any dev (or future CI) on Windows can run the test suite without encoding failures.

## Approach

Two-part fix:

1. **Mechanical replacement** — `sed` to replace `.read_text()` → `.read_text(encoding="utf-8")` across all test files. Deterministic, no judgment calls.

2. **Regression prevention** — A `local` pre-commit hook that greps for bare `.read_text()` in `tests/` and fails if found. Catches future occurrences at commit time.

### Components affected

| File/Path | Change |
|-----------|--------|
| `tests/**/*.py` (26 files) | Modify — add encoding param |
| `.pre-commit-config.yaml` | Modify — add local grep hook |

## Examples

**Before:**
```python
data = json.loads(patterns_file.read_text().strip())
```

**After:**
```python
data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
```

**Pre-commit hook:**
```yaml
- repo: local
  hooks:
    - id: check-read-text-encoding
      name: check read_text has encoding
      entry: bash -c '! grep -rn "\.read_text()" tests/ --include="*.py"'
      language: system
      types: [python]
      pass_filenames: false
```

## Acceptance Criteria

**MUST:**
- All `read_text()` calls in `tests/` include `encoding="utf-8"`
- `grep -rn '\.read_text()' tests/ --include='*.py'` returns zero hits
- Pre-commit hook prevents bare `read_text()` in future test code
- All tests pass
- Type checks pass

**MUST NOT:**
- Touch production code (`src/`) — already fixed in RAISE-161
- Change test logic or assertions — encoding param is additive
