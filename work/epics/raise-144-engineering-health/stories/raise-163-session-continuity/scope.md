## Story Scope: RAISE-163

**Epic:** RAISE-144 (Engineering Health)
**Size:** S
**Priority:** P2 — affects Kurigage class experience

### Problem

1. **Rai fumbles her own CLI** — users see trial-and-error with rai-cli flags, eroding trust. Root cause: inference guessing syntax instead of consulting reference.
2. **No forward-looking session continuity** — session-close captures what happened (narrative) but not what Rai would tell her future self to prioritize, watch for, or remind the human about.

### In Scope

- Add `next_session_prompt` field to `SessionState` schema (Pydantic)
- Wire it through `CloseInput` → `load_state_file` → `process_session_close`
- Include it in session-start context bundle output
- Update session-close SKILL.md with step to write it
- Update session-start SKILL.md with step to read/present it
- Regenerate `cli-reference.md` from actual `rai --help` output
- Add behavioral rule in MEMORY.md to always consult before running rai commands

### Out of Scope

- `rai cli reference --compact` auto-generation command (future)
- Changes to CLI argument parsing
- New CLI flags

### Done Criteria

- [ ] `next_session_prompt` persisted in session-state.yaml via CLI
- [ ] session-start context bundle includes the prompt
- [ ] Both skills updated (source + local copies)
- [ ] cli-reference.md regenerated from --help
- [ ] MEMORY.md behavioral rule added
- [ ] Tests pass (existing + new)
- [ ] Retrospective complete
