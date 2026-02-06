---
name: session-close
description: >
  Close a working session by updating memory and preparing context for the next session.
  Preserves learnings and maintains continuity.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "end"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-close \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---

# Session Close

## Purpose

Close a session by preserving learnings and preparing handoff. Updates memory, captures tangents, and creates continuity for the next session.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Explain each step and why. All steps executed.

**Ha (破)**: Brief explanations. All steps executed.

**Ri (離)**: Minimal output. All steps executed.

Experience level affects **communication style**, not **operations**. All levels perform the same memory operations.

## Context

**When to use:**
- End of working session
- After completing feature or significant work
- Before break or context switch

**When to skip:**
- Trivial session with no learnings

**Inputs required:**
- Conversation context (learnings, tangents)
- Existing patterns (for deduplication)

**Output:**
- Memory updates (patterns, sessions, telemetry)
- Context file update (`CLAUDE.local.md`)
- Session state cleared

## Steps (6)

### Step 1: Reflect & Query (Parallel)

**Mental work** (while query runs):
- What was the goal? What was accomplished?
- What patterns/learnings emerged?
- Any tangents worth capturing?

**Query** (parallel):
```bash
uv run raise memory query "patterns" --types pattern --limit 5
```

This helps avoid duplicate patterns. Query is fast (<3ms) — always run it.

### Step 2: Update Memory (Parallel CLI Calls)

Run these in parallel (all independent):

```bash
# Patterns (if any new ones)
uv run raise memory add-pattern "Description" -c "context,tags" -t process

# Session record (always)
uv run raise memory add-session "Topic" -o "outcome1,outcome2" -t {type}

# Telemetry (always)
uv run raise memory emit-session -t {type} -o {outcome} -d {minutes}
```

**Types:** feature, research, maintenance, infrastructure, ideation
**Outcomes:** success, partial, abandoned

### Step 3: Update Context (Single Write)

Update `CLAUDE.local.md` with a **single Write operation**:

1. Read the file once
2. Plan all changes:
   - Current Focus (if changed)
   - Recent Sessions table (add row)
   - Quick References (if new artifacts)
   - Last updated line
3. Write entire file once

**Do NOT:** Make multiple Edit calls to the same file.

### Step 4: Capture Tangents

Check conversation for ideas mentioned but not pursued.

- Add to `dev/parking-lot.md` if worth revisiting
- Skip if none

**Don't skip this step** — tangents exist only in conversation context.

### Step 5: Clear Session State

```bash
uv run raise session close
```

This clears `current_session` in `~/.rai/developer.yaml`, marking the session as properly closed. Without this step, the next `/session-start` will warn about an unclosed session.

### Step 6: Handoff

Output brief suggestion:

```
## Next Session
**Continue:** [next step]
**Alternative:** [if blocked]
**Open:** [unresolved questions]
```

## Output

| File | Update |
|------|--------|
| `.raise/rai/memory/patterns.jsonl` | New patterns (CLI) |
| `.raise/rai/memory/sessions/index.jsonl` | Session record (CLI) |
| `.raise/rai/telemetry/signals.jsonl` | Session event (CLI) |
| `~/.rai/developer.yaml` | Session state cleared (CLI) |
| `CLAUDE.local.md` | Single Write |
| `dev/parking-lot.md` | Tangents (if any) |

## Notes

**Token economy:** This skill reduces future token waste by persisting learnings in structured files.

**Minimum close:** If rushed, at minimum: `add-session` + update CLAUDE.local.md "Recent Sessions".

**Calibration:** If features completed, also run:
```bash
uv run raise memory add-calibration {feature_id} --name "Name" -s {size} -a {actual_mins} -e {estimated_mins}
```

## References

- Complement: `/session-start`
- Memory: `.raise/rai/memory/`
- Context: `CLAUDE.local.md`
- Tangents: `dev/parking-lot.md`
