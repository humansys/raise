# Retrospective: RAISE-1174

## Summary
- Root cause: Confluence REST API requires CQL syntax; search() passed user input directly without wrapping
- Fix approach: `_ensure_cql()` static method detects plain text vs CQL operators and wraps in `siteSearch ~ "..."` (already applied in 784d1a56)
- Classification: Interface/S2-Medium/Code/Missing

## Process Improvement
**Prevention:** Any adapter method that bridges user input to a query language should auto-detect and convert — never expose raw syntax requirements to callers.
**Pattern:** Interface + Code + Missing → missing input normalization layer between user-facing API and backend query syntax.

## Heutagogical Checkpoint
1. Learned: The fix was applied informally (784d1a56) but never tracked through the pipeline — no tests, no triage, no closure. Informal fixes accumulate technical debt in test coverage.
2. Process change: When applying quick fixes during other work, file a follow-up to add regression tests rather than leaving the fix untested.
3. Framework improvement: None — fix and tests are self-contained.
4. Capability gained: Pattern for detecting/wrapping query languages at adapter boundaries.

## Patterns
- Added: none (pattern already covered by PAT-E-593 CQL search behavior)
- Reinforced: none evaluated
