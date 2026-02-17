# RAISE-162: Add encoding="utf-8" to read_text() calls in test suite

## Scope

**In:**
- Add `encoding="utf-8"` to all `read_text()` calls in test files
- 26 test files, ~123 call sites (mechanical fix)

**Out:**
- Production code changes (already handled in RAISE-161)
- Adding Windows CI

**Done Criteria:**
- [ ] All `read_text()` calls in tests include `encoding="utf-8"`
- [ ] `grep -r 'read_text()' tests/` returns zero hits (all should have encoding param)
- [ ] All tests pass
- [ ] Type checks pass
