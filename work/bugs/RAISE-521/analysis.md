# RAISE-521 — Analysis

## Tier: XS — Cause evident

## Root Cause

add_gitignore_personal() has three return sites:
1. line 57: `return True` — entry already present (correct, no-op)
2. line 65: `return True` — after successful write (correct)
3. (implicit) — if write raises OSError, Python unwinds past line 65,
   but there is no except clause — the exception propagates to run_fixes(),
   which does not catch it either, crashing the fix runner entirely.

SonarCloud's "always returns same value" flag reveals a design gap:
the function promises a bool success signal but never returns False.

## Causal Chain (5 Whys)

Problem:  add_gitignore_personal never returns False
Why 1:    No try/except around file write operations
Why 2:    Initial implementation only handled the happy path
Root:     Missing error handling at I/O boundary

## Fix Approach

Wrap the write block (lines 63-64) in try/except OSError.
Return False on exception. shutil.copy2 backup also wrapped.
No behavior change on happy path.
