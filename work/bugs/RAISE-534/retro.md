# RAISE-534: Retrospective

## Summary
Copy-paste error in `_read_gitignore()` — both if/else branches produced `**/{entry}/**`. Path-relative entries (containing `/`) should not get the `**/` prefix.

## Root Cause
Copy-paste during initial implementation. No tests existed for this function.

## Fix
Changed else branch to `f"{entry}/**"` (no `**/` prefix for path-relative patterns).

## Tests Added
- `test_bare_name_gets_double_star_prefix` — bare names match anywhere
- `test_path_entry_no_double_star_prefix` — path entries are relative
- `test_mixed_entries` — both patterns in same .gitignore
