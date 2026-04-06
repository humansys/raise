## Retrospective: RAISE-1063

### Summary
- Root cause: Auth refactor renamed OrgContext/verify_api_key/ApiKey without updating raise-pro tests
- Fix approach: Updated all imports, mocks, and assertions to match new auth model
- Classification: Interface/S2-Medium/Code/Incorrect

### Process Improvement
**Prevention:** Cross-package test suites should be run in CI when the dependency package changes.
**Pattern:** Interface=Incorrect + Code → renames must grep all consumers, not just the package being changed.

### Heutagogical Checkpoint
1. Learned: The auth model evolved from simple org-scoped (OrgContext) to member-scoped (MemberContext) with plan/role gating. Tests needed plan="team" to pass requires_plan checks.
2. Process change: When refactoring shared auth, run all downstream test suites.
3. Framework improvement: CI should run raise-pro tests when raise-server changes.
4. Capability gained: Understanding of the FastAPI dependency override chain with nested Depends.
