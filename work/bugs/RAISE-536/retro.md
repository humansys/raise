# RAISE-536: Retrospective

## Summary
Regex alternation `^## \[|\Z` in lookahead was ambiguous per SonarCloud static analysis. Added explicit `(?:...)` grouping. Behavior unchanged.

## Root Cause
Missing explicit grouping — Python interprets it correctly but static analyzers flag the ambiguity.

## Tests Added
- `test_unreleased_as_last_section` — content with no following version section
- `test_unreleased_as_last_section_empty` — empty unreleased as only section
