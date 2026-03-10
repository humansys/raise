# RAISE-521 — Plan

## Tasks

### T1 — Regression test RED
Write test: mock open() to raise OSError, assert add_gitignore_personal returns False.
Test file: tests/doctor/test_fix.py
Commit: test(RAISE-521): regression — add_gitignore_personal returns False on OSError

### T2 — Fix GREEN
Wrap write block in try/except OSError, return False on exception.
Commit: fix(RAISE-521): add_gitignore_personal returns False on write failure

### T3 — Artifacts commit
Commit scope + analysis + plan.
Commit: chore(RAISE-521): scope, analysis, plan artifacts

## Verification

python -m pytest tests/doctor/test_fix.py -x -q
python -m ruff check src/raise_cli/doctor/fix.py
python -m pyright src/raise_cli/doctor/fix.py
