## Retrospective: RAISE-588

### Summary
- Root cause: NOSONAR suppression missing — the except SystemExit was intentional graceful degradation but not annotated for the analyzer
- Fix approach: Added `# NOSONAR` with inline justification comment (commit bb88ae5e, part of RAISE-541 batch)
- Classification: Logic/S3-Low/Code/Missing

### Verification
- Fix in bundle.py:102 — `except SystemExit:  # NOSONAR — intentional: degrade gracefully when adapter unavailable`
- Behavior unchanged, only annotation added
- Correct: _query_adapter must not crash when adapter calls sys.exit()

### Process Improvement
**Prevention:** Every suppression comment needs justification at write time, not retroactively. Code review should flag bare `except` blocks without rationale.
**Pattern:** Logic + Code + Missing → suppression annotations missing from intentional exception handling. Low severity but creates noise in SAST reports that hides real issues.

### Heutagogical Checkpoint
1. Learned: NOSONAR without justification is worse than no NOSONAR — it suppresses without explaining why, making future reviewers unable to judge if the suppression is still valid.
2. Process change: Require justification comment on every NOSONAR/noqa/type: ignore annotation.
3. Framework improvement: None — this is a code review discipline issue.
4. Capability gained: None new — standard practice reinforced.

### Patterns
- Added: none (covered by PAT-F-003 class — SAST noise from missing annotations)
- Reinforced: none evaluated
