# RAISE-482: Retrospective

## Fix Summary

Added `check_legacy_packages()` in `compat.py` that detects co-installed
`rai-cli` / `rai-core` (pre-rename packages) via `importlib.metadata.version()`.
Wired into CLI startup callback in `main.py` to emit a clear Rich warning with
the exact `pip uninstall` command.

## Root Cause Confirmed

Package rename (`rai-cli` -> `raise-cli`) without automated cleanup. pip treats
differently-named packages as independent — `pip install raise-cli` does not
uninstall `rai-cli`.

## What Went Well

- Simple fix with clear user-facing message
- No changes to hook/adapter registry needed — existing error isolation was correct
- Test uses `unittest.mock.patch` on `version()` — clean and fast

## Systemic Insight

Package renames need a migration checklist:
1. Runtime detection of old packages (this fix)
2. Migration instructions in CHANGELOG/release notes
3. CI gate that validates clean environment

This is the second time (related to PAT-E-597/598) that optional/stale imports
caused confusing errors. Guard pattern: detect and explain, don't just fail.
