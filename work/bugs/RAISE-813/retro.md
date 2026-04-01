## Retrospective: RAISE-813

### Summary
- Root cause: --phase defaulted to "design", output always showed it, callers never pass it
- Fix: --phase default None, output conditional, telemetry gets "init" as neutral value
- Classification: UX/S3-Low/Code/Incorrect

### Process Improvement
**Prevention:** CLI flags with defaults should be validated against real caller usage before release
**Pattern:** UX + Code + Incorrect → misleading default that 100% of callers inherit silently

### Heutagogical Checkpoint
1. Learned: the BacklogHook (S325.4) was deleted in S1052.5 — context matters for bug triage
2. Process change: check git history for deleted code before assuming a component never existed
3. Framework improvement: none
4. Capability gained: tracing deleted features via git log --grep

### Patterns
- Added: none
- Reinforced: none
