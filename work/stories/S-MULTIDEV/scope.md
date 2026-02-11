# Feature Scope: S-MULTIDEV (Implementation)

> Implement multi-developer collaboration safety decisions from spike.

## In Scope

- D1: Gitignore `index.json` + remove from git tracking
- D2: Move `session-state.yaml` to `personal/` + update CLI read/write paths
- D3: Developer-prefixed pattern IDs (`PAT-{X}-NNN`) + migrate existing patterns
- D4: Move `calibration.jsonl` to `personal/` + update CLI paths
- D5: Delete empty `sessions/index.jsonl` from tracking

## Out of Scope

- Auto-rebuild index.json on session start (future enhancement)
- Multi-developer merge conflict resolution tooling
- Pattern deduplication across developers
- CI/CD pipelines

## Done Criteria

- [ ] `index.json` gitignored and removed from tracking
- [ ] `session-state.yaml` reads/writes from `personal/` path
- [ ] Pattern IDs use developer prefix from `~/.rai/developer.yaml`
- [ ] Existing PAT-001..PAT-259 migrated to PAT-E-001..PAT-E-259
- [ ] `calibration.jsonl` reads/writes from `personal/` path
- [ ] Empty `sessions/index.jsonl` deleted from tracking
- [ ] All tests pass
- [ ] Type checks pass
