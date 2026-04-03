## Retrospective: RAISE-591

### Summary
- Root cause: AsyncDocumentationTarget protocol requires async methods, but can_publish has no I/O — just returns True. Sonar flags async without await as unnecessary.
- Fix approach: Added NOSONAR with docstring explaining why async is required by protocol (commit 78c1ab71)
- Classification: Interface/S3-Low/Design/Incorrect

### Verification
- Fix in mcp_confluence.py:115 — NOSONAR + docstring explaining protocol requirement
- Correct: removing async would break the protocol contract

### Process Improvement
**Prevention:** When designing async protocols, consider adding a sync alternative or documenting that trivial implementations will trigger S7503. This is a design trade-off, not a code bug.
**Pattern:** Interface + Design + Incorrect → protocol forces async on implementations that don't need it. NOSONAR is the correct fix when the protocol contract is non-negotiable.

### Heutagogical Checkpoint
1. Learned: Not all Sonar findings are bugs. S7503 on protocol-required async is a false positive by design. The fix is documentation (NOSONAR + docstring), not code change.
2. Process change: None — NOSONAR with justification is the right response to protocol-forced async.
3. Framework improvement: None.
4. Capability gained: Distinguishing SAST false positives from real bugs based on protocol contracts.

### Patterns
- Added: none (too specific to generalize)
- Reinforced: none evaluated
