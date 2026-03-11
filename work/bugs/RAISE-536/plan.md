# RAISE-536: Fix Plan

### T1: Regression test
- Test `has_unreleased_entries` with content that has no next section (hits `\Z` branch)
- Test `has_unreleased_entries` with content that has a next section (hits `^## \[` branch)

### T2: Fix regex grouping
- Add explicit `(?:...)` groups in the lookahead alternation
