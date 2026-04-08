# RAISE-1433: Plan

## Approach B — Deprecate journal, warn on hollow close, keep diary skill

### T1: Deprecate journal CLI commands
- Mark `rai session journal add` and `rai session journal show` as deprecated
- Print deprecation warning when called: "Deprecated — journal will be removed in v3.1"
- Keep code functional for backward compat (don't delete yet)
- Commit

### T2: Remove pre-compact-journal.sh hook
- Delete `.claude/scripts/pre-compact-journal.sh`
- Remove hook reference from `.claude/settings.json` if present
- Commit

### T3: CLI warning on hollow --summary close
- In `session.py` close(), when structured close from --summary (no --state-file):
  warn that narrative/next_session_prompt are empty
- Suggest: "For full session continuity, use /rai-session-close skill"
- Commit

### T4: Update rai-session-diary skill
- Remove journal dependency (`rai session journal show --compact`)
- Update to read from conversation context directly (the skill runs inside
  a Claude session — it has access to the conversation)
- Skill should synthesize diary from: git log, session state, conversation context
- Commit

### T5: Update CHANGELOG + docs
- Add deprecation notice for journal
- Update CLAUDE.md post-compaction instructions (remove journal reference)
- Commit
