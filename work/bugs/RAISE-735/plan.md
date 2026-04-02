## Plan: RAISE-735

### T1: Regression test (RED)
Add test that greps source + framework for stale `raise <cmd>` patterns.
Verify: test fails (RED).
Commit: `test(RAISE-735): RED — detect stale 'raise' command references`

### T2: Fix source files (GREEN)
Replace `raise <cmd>` → `rai <cmd>` in 9 source files.
Verify: T1 test passes, all gates green.
Commit: `fix(RAISE-735): rename stale 'raise' → 'rai' in source`

### T3: Fix framework docs
Replace in glossary.md, compliance.md, philosophy.md, greenfield.md.
Verify: T1 test passes, all gates green.
Commit: `fix(RAISE-735): rename stale 'raise' → 'rai' in framework docs`

### T4: Fix test docstrings/fixtures
Replace in 9 test files.
Verify: all gates green.
Commit: `fix(RAISE-735): rename stale 'raise' → 'rai' in tests`
