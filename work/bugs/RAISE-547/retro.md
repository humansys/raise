## Retrospective: RAISE-547

### Summary
- Root cause: promote_unreleased regex lookahead only matched `^## [` (next section) but not `\Z` (end of string). has_unreleased_entries already had `|\Z` — inconsistency between paired functions.
- Fix approach: Add `|\Z` to promote_unreleased lookahead (commit 2cc7e909). 1-line fix + regression test.
- Classification: Functional/S2-Medium/Code/Missing

### Verification
- changelog.py:47 — `(?=^## \[)` → `(?=^## \[|\Z)`. Same pattern as has_unreleased_entries.
- Regression test added: promote with Unreleased as last section.

### Process Improvement
**Prevention:** When two functions operate on the same format (changelog), their regex patterns should be derived from a shared constant or tested together. Inconsistency between paired functions is the same class as RAISE-608 (asymmetric defaults).
**Pattern:** Functional + Code + Missing → edge case not covered in regex. Paired functions with similar regexes drift when changed independently.

### Patterns
- Added: none (covered by existing asymmetric-pair insight from RAISE-608/PAT-F-045)
- Reinforced: none evaluated
