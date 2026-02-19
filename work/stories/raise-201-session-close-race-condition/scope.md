## Bug Scope: RAISE-201

**Jira:** RAISE-201
**Type:** Bug (data-loss, parallel-sessions)
**Priority:** High
**Epic:** RAISE-144 (Engineering Health)

### Problem

When two parallel Claude Code sessions close simultaneously, both write to the
same `/tmp/session-output.yaml` path. The second write overwrites the first
before the CLI reads it, causing session data loss. SES-218 was corrupted by
SES-217's data (confirmed 2026-02-19).

### Root Causes (Ishikawa)

1. **Shared mutable path:** `/tmp/session-output.yaml` is a convention in the
   `rai-session-close` skill — all sessions write to the same file.
2. **No coherence validation:** CLI reads state file without verifying content
   matches the active session being closed.
3. **No session_id in state file:** The YAML schema (`CloseInput`) has no
   `session_id` field, so there's nothing to validate against.

### In Scope

- Add `session_id` field to `CloseInput` model
- Generate unique temp file path per session (e.g., `/tmp/session-output-{SES-ID}.yaml`)
- Add coherence validation: CLI rejects state file if `session_id` doesn't match
- Update `rai-session-close` skill to use session-specific path
- Tests for race condition prevention

### Out of Scope

- File locking / flock mechanisms (over-engineering for this)
- Fixing already-corrupted SES-218 data (done manually)
- Orphaned session cleanup automation (separate story)

### Done Criteria

- [ ] `CloseInput` has `session_id` field
- [ ] State file path includes session ID
- [ ] CLI validates session_id coherence on structured close
- [ ] Skill template uses `{session_id}` in path
- [ ] Tests pass (including new coherence validation tests)
- [ ] Retrospective complete
