# RAISE-535: Retrospective

## Summary
Dead if-condition in `_analyze_module()` — both branches extracted imports identically. Collapsed to unconditional code.

## Root Cause
Premature branching during initial implementation. The comment suggested different handling for `__init__.py` imports, but the implementation was identical in both paths.

## Fix
Removed the if/else, kept unconditional import extraction. Net -6 lines.
