# RAISE-521 — Retro

## Fix verified against root cause?
Yes. Root cause: OSError on write propagated unhandled, never returning False.
Fix: try/except OSError wrapping the write block, return False on exception.

## Regression test?
Yes — test_returns_false_on_write_error in TestAddGitignorePersonal.
Test uses chmod(0o444) on .gitignore to trigger real PermissionError — no mocking needed.
RED confirmed: PermissionError propagated. GREEN confirmed after fix.

## Regressions introduced?
No. All 15 doctor/fix tests pass. Happy path unchanged.

## Pattern to emit?
Yes — fix registry functions must handle I/O errors and return False on failure.
Bool return types are contracts, not formalities.
