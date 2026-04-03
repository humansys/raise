# Retrospective: RAISE-1160

## Summary
- Root cause: incomplete migration — new S-F-* session index added alongside legacy SES-NNN, never replaced it
- Fix approach: process_session_close uses caller's session_id when provided, skips legacy append_session

## Heutagogical Checkpoint
1. Learned: additive changes to data pipelines (new index alongside old) create phantom duplicates that are hard to detect until data is cross-referenced
2. Process change: when introducing a new ID scheme, the migration ticket should include "stop writing to old scheme" as explicit acceptance criteria
3. Framework improvement: none — the bugfix skill guided correctly
4. Capability gained: understanding of the full session lifecycle: CLI command (identity + index) → orchestrator (close) → state (session-state.yaml)

## Patterns
- Added: none (insight is general software eng, not project-specific)
- Reinforced: none evaluated
