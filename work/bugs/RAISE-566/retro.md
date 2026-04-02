## Retrospective: RAISE-566

### Summary
- Root cause: load_session_state() called after migrate_flat_to_session() — migration moved the file before anyone read it. Composition order error.
- Fix approach: Read state before migration, use prev_state directly (commit f568ed84). 3 net lines.
- Classification: Functional/S1-High/Code/Incorrect

### Verification
- session.py: prev_state = load_session_state() before migrate_flat_to_session()
- Regression test: close→start cycle verifies current_work, narrative, next_session_prompt present
- Fix is correct and minimal. High severity because every session lost all context.

### Process Improvement
**Prevention:** When a function moves/transforms a shared resource, audit all readers in the same call scope. Each function may be correct in isolation; the composition order creates the bug.
**Pattern:** Functional + Code + Incorrect → read-after-move race in sequential code. Not a concurrency bug but same conceptual class: resource accessed after invalidation.

### Heutagogical Checkpoint
1. Learned: This is the most impactful bug in the batch — every developer lost session context on every start. The fix was 3 lines. The cost was weeks of degraded DX before detection.
2. Process change: Integration test for close→start cycle should have existed from day 1. Unit tests of migrate and load separately couldn't catch the composition bug.
3. Framework improvement: Pattern captured as PAT-E-425 (already existed from original fix).
4. Capability gained: Recognize "works in isolation, fails in composition" as a class requiring integration tests.

### Patterns
- Added: none (PAT-E-425 already captured during original fix)
- Reinforced: none evaluated
