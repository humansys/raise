---
name: session-start
description: >
  Begin a session by loading memory, analyzing progress, and proposing focused work.
  Creates continuity across sessions. Adapts communication to experience level.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "start"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-start \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Session Start

## Purpose

Load context, analyze progress, propose focused work. Creates continuity across sessions by loading memory and adapting to experience level.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Detailed explanations, teach concepts. All steps executed.

**Ha (破)**: Balanced output, explain new concepts only. All steps executed.

**Ri (離)**: Minimal output, essentials only. All steps executed.

Experience level affects **communication style**, not **operations**. All levels load the same data.

## Context

**When to use:**
- Beginning of working session
- After break or context switch
- Resuming interrupted work

**When to skip:**
- Immediate continuation in same conversation

**Inputs required:**
- Developer profile (`~/.rai/developer.yaml`)
- Unified graph (`.raise/graph/unified.json`)
- Human context (`CLAUDE.local.md`)

**Output:**
- Session summary (displayed)
- Session count update (`~/.rai/developer.yaml`)

## Steps (4)

### Step 1: Load Context (Parallel)

Run these in parallel (all independent):

```bash
# Developer profile
uv run raise profile show

# Unified graph context
uv run raise memory query "session epic patterns" --limit 10

# Human context (deadlines, notes)
# Read: CLAUDE.local.md
```

**If graph unavailable:** Run `uv run raise memory build` first.

**Extract from results:**
- Experience level (for output style)
- Current epic/feature focus
- Recent patterns and calibration
- Deadlines and human notes

### Step 2: Analyze

With data from Step 1, analyze:

**Progress:**
- Epic completion %
- Days to deadline
- Recent velocity

**Improvement signals:**

| Signal | Detection | Action |
|--------|-----------|--------|
| Stale parking lot | Item >2 weeks | Promote or delete |
| Feature drag | Same feature >3 sessions | Split or timebox |
| Deadline pressure | <3 days | Focus critical path |
| Stale branches | >5 branches | Cleanup |

**Check parking lot** (`dev/parking-lot.md`) for stale items or blockers.

### Step 3: Propose & Present

Propose session focus and present summary. Adapt verbosity to level:

**Shu output:**
```
## Session Start: YYYY-MM-DD

### Context
- Memory: X patterns loaded
- Level: Shu (I'll explain concepts as we go)
- Last session: [outcome]
- Focus: [Epic] → [Feature]

### Progress
| Metric | Status |
|--------|--------|
| Epic | X% complete |
| Deadline | N days |

### Suggested Focus
**What:** [goal]
**Why:** [rationale]
**Done when:** [criteria]

### Signals
[any issues, or "Healthy"]

Ready when you are.
```

**Ri output:**
```
## Session: YYYY-MM-DD

**Context:** [Epic] → [Feature], X% complete, N days to deadline
**Focus:** [goal]
**Signals:** [any, or "None"]

Go.
```

Ha is between these — balanced detail.

### Step 4: Record Session

```bash
uv run raise session start --project "$(pwd)"
```

This command:
- Increments session count and updates last_session date
- Sets `current_session` state (for orphan detection)
- **Warns** if a previous session wasn't closed (stale >24h = warning, recent = note)

**First-time user:** Ask name, then:
```bash
uv run raise session start --name "Name" --project "$(pwd)"
```

**If warned about unclosed session:** Inform the user that learnings from the previous session may have been lost. Suggest using `/session-close` before ending work.

## Output

| Item | Destination |
|------|-------------|
| Session summary | Displayed (not saved) |
| Signals | Displayed |
| Session count | `~/.rai/developer.yaml` (CLI) |

## Shu-Level Concepts

For new developers (0-5 sessions), explain these concepts when relevant:

**The RaiSE Triad:**
```
YOU (judgment, decisions) + RAI (patterns, execution) + RAISE (methodology, gates)
```

**Why Memory Matters:**
```
Without memory, every session starts cold. With memory, I remember patterns,
velocity, and where we left off. This is continuity.
```

Only include these explanations for Shu-level developers.

## Notes

**Token economy:** Loading memory avoids re-discovering patterns through conversation.

**Prioritization:** Deadlines → Dependencies → Momentum → Energy.

**Continuity loop:** session-start loads → work → session-close saves.

## References

- Profile: `~/.rai/developer.yaml`
- Graph: `.raise/graph/unified.json`
- Human context: `CLAUDE.local.md`
- Parking lot: `dev/parking-lot.md`
- Complement: `/session-close`
