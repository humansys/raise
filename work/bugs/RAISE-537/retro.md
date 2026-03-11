# RAISE-537: Retrospective

## Summary
Same pattern as RAISE-536. Regex alternation in lookahead without explicit grouping.

## Root Cause
Consistent with RAISE-536 — regex alternation `^##\s|\Z` flagged by SonarCloud.

## Fix
Added `(?:...)` non-capturing group: `(?=(?:^##\s)|\Z)`.
