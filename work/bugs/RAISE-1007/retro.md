## Retrospective: RAISE-1007

### Summary
- Root cause: claude-agent-sdk v0.1.48 closes stdin before in-flight hook callbacks complete
- Fix approach: bump SDK to >=0.1.52 (upstream fix), remove `and False` hack

### Heutagogical Checkpoint
1. Learned: the rai-agent package was migrated from the rai repo to raise-commons in S11.4 (e673). The worktree created from an older commit didn't have it — worktree base commit matters.
2. Process change: when creating worktrees for bugfixes, verify the worktree HEAD matches the target branch HEAD before starting work.
3. Framework improvement: the manifest still says `branches.development: dev` but the actual branch is `release/2.4.0` per ADR-033. Manifest should be updated.
4. Capability gained: understanding of claude-agent-sdk hook lifecycle and ProcessTransport shutdown sequence.

### Patterns
- Added: none (upstream SDK fix, no codebase pattern to extract)
- Reinforced: none evaluated (no behavioral patterns were consciously applied)
