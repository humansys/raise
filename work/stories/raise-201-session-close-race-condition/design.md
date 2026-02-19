---
story_id: RAISE-201
type: bugfix
size: S
modules: [mod-session]
domain: session lifecycle
---

# Design: RAISE-201 — Session Close Race Condition

## Problem

Two parallel Claude Code sessions writing to the same `/tmp/session-output.yaml`
causes data loss. The second write overwrites the first before the CLI reads it.
No validation exists to detect this.

## Value

Prevents silent data corruption in multi-session workflows. Session telemetry
is the foundation for calibration, coaching, and continuity — losing it
degrades the entire memory system.

## Approach

Three-layer defense:

1. **Unique file path per session** — Eliminate the shared mutable resource.
   Skill writes to `/tmp/session-output-{SES-ID}.yaml` instead of a fixed path.

2. **`session_id` in CloseInput** — Add the field to the data model so the
   state file carries identity.

3. **Coherence validation in CLI** — When `--session` is provided (or resolved),
   and the state file has a `session_id` field, reject if they don't match.

### Components

| Component | Change | File |
|-----------|--------|------|
| `CloseInput` | Add `session_id` field | `src/rai_cli/session/close.py` |
| `load_state_file()` | Read `session_id` from YAML | `src/rai_cli/session/close.py` |
| `close()` command | Validate coherence | `src/rai_cli/cli/commands/session.py` |
| `rai-session-close` skill | Use `{SES-ID}` in path | `.claude/skills/rai-session-close/SKILL.md` |

## Examples

### State file (before)

```yaml
# /tmp/session-output.yaml
summary: "Session protocol implementation"
type: feature
```

### State file (after)

```yaml
# /tmp/session-output-SES-219.yaml
session_id: SES-219
summary: "Session protocol implementation"
type: feature
```

### CLI coherence validation

```bash
# Happy path — session_id matches
rai session close --state-file /tmp/session-output-SES-219.yaml --session SES-219 --project .
# ✓ Session SES-219 closed.

# Mismatch — rejected
rai session close --state-file /tmp/session-output-SES-217.yaml --session SES-219 --project .
# ERROR: State file session_id (SES-217) does not match target session (SES-219).

# No session_id in file — backwards compatible, no validation
rai session close --state-file /tmp/session-output.yaml --session SES-219 --project .
# ✓ Session SES-219 closed. (no coherence check — old format)
```

### Skill template change

```yaml
# Step 2 in rai-session-close SKILL.md
# Before:
rai session close --state-file /tmp/session-output.yaml --project "$(pwd)"

# After:
rai session close --state-file /tmp/session-output-{SES-ID}.yaml --session {SES-ID} --project "$(pwd)"
```

## Acceptance Criteria

**MUST:**
- `CloseInput.session_id` field exists (str, default "")
- `load_state_file()` reads `session_id` from YAML
- CLI rejects state file when `session_id` doesn't match `--session`
- Skill template uses session-specific path
- Backwards compatible: old state files without `session_id` still work

**SHOULD:**
- Error message includes both IDs for debugging

**MUST NOT:**
- Break existing `rai session close` without `--state-file` (legacy path)
- Require `session_id` in state file (optional for backwards compat)
