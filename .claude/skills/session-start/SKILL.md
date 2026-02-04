---
name: session-start
description: >
  Begin a session by loading memory, analyzing progress, and proposing
  focused work. Creates continuity across sessions and surfaces improvement
  signals for continuous improvement.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "start"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-start \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Session Start: Context & Prioritization

## Purpose

Begin a working session by loading accumulated memory, analyzing progress against goals, and proposing focused work. This creates continuity across sessions and surfaces signals for continuous improvement.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, read all memory files, propose session goal.

**Ha (破)**: Skip steps for continuation sessions; focus on blockers and drift.

**Ri (離)**: Develop personal start rituals; integrate with external tools.

## Context

**When to use:**
- Beginning of any working session
- After a break or context switch
- When resuming interrupted work
- To get oriented after time away from project

**When to skip:**
- Immediate continuation (same conversation)
- Quick fixes where context is obvious

**Inputs required:**
- Memory files (`.rai/memory/`)
- Context files (`CLAUDE.local.md`, `RAI.md`)
- Progress tracking (`dev/epic-*.md`, `dev/parking-lot.md`)

**Output:**
- Session start summary with proposed focus
- Improvement signals surfaced
- Clear handoff from previous session

## Steps

### Step 0.5: Query Context (Optional)

If unified graph is available, query for session-relevant patterns:

```bash
raise context query "session epic patterns" --unified --types session,pattern --limit 5
```

Review returned patterns for session continuity context.

**Verification:** Context loaded or graph not available (proceed without).

> **If context unavailable:** Run `raise graph build --unified` first, or skip to Step 1.

### Step 1: Load Memory

Read accumulated knowledge from `.rai/memory/`:

```
1. patterns.jsonl — Learned patterns (auto-loaded via hook)
2. calibration.jsonl — Velocity data, sizing accuracy
3. sessions/index.jsonl — Recent session history
```

**Note:** With hook-assisted workflow, basic context is auto-loaded on session start.
This skill provides deeper analysis (parking lot, improvement signals, detailed proposal).

**Extract:**
- Patterns relevant to likely work
- Recent session outcomes
- Any open questions

**Verification:** Memory loaded; key patterns recalled.

> **If you can't continue:** Memory files missing → Create them via `/session-close` pattern.

### Step 2: Load Context

Read current state from context files:

```
1. CLAUDE.local.md — Current focus, deadlines, recent sessions
2. RAI.md — Perspective, protocols, contribution log
3. dev/epic-{current}.md — Epic progress and scope
```

**Extract:**
- Current epic and feature
- Deadline pressure
- Last session outcome

**Verification:** Know where we are and where we're going.

> **If you can't continue:** Context files outdated → Note and update during session.

### Step 3: Analyze Progress

Calculate progress metrics:

**Quantitative:**
- Epic completion % (SP completed / SP total)
- Days to next deadline
- Recent velocity (SP/session or features/week)

**Qualitative:**
- On track / behind / ahead
- Blockers present?
- Scope creep detected?

**Verification:** Progress status clear.

> **If you can't continue:** Metrics unavailable → Estimate from git history.

### Step 4: Check Parking Lot

Review `dev/parking-lot.md` for:

- Items deferred >3 sessions (decay risk)
- Items blocking other work
- Items that should be promoted or deleted

**Verification:** Parking lot reviewed; stale items flagged.

> **If you can't continue:** No parking lot → Skip or create one.

### Step 5: Detect Improvement Signals

Look for patterns indicating process issues:

| Signal | Detection | Suggested Action |
|--------|-----------|------------------|
| **Stale parking lot** | Item >3 sessions old | Promote, schedule, or delete |
| **Feature drag** | Same feature >3 sessions | Check scope, split, or timebox |
| **Recurring blocker** | Same issue appears twice | Address root cause |
| **Calibration drift** | Actuals consistently off estimates | Adjust T-shirt sizes |
| **Memory staleness** | memory.md not updated recently | Update during session |
| **Deadline pressure** | <3 days to milestone | Focus on critical path |
| **Velocity drop** | Slower than historical average | Investigate cause |

**Verification:** Signals identified or explicitly none.

> **If you can't continue:** No signals → Good! Note healthy state.

### Step 6: Propose Session Goal

Based on analysis, propose:

**Primary focus:** What to work on this session
**Rationale:** Why this, why now (urgency, dependency, momentum)
**Scope:** What "done" looks like for this session
**Alternative:** Backup if primary is blocked

**Good session goals are:**
- Specific (not "make progress")
- Achievable in one session
- Aligned with deadlines
- Building on momentum

**Verification:** Clear, actionable session goal proposed.

> **If you can't continue:** Multiple competing priorities → Ask user to choose.

### Step 7: Present Summary

Output the session start summary:

```markdown
## Session Start: YYYY-MM-DD

### Context Loaded
- **Memory:** X patterns, Y learnings loaded
- **Last session:** [brief outcome]
- **Current focus:** [Epic] → [Feature]

### Progress Check
| Metric | Status |
|--------|--------|
| Epic | X% complete (N/M SP) |
| Deadline | N days to [milestone] |
| Velocity | [assessment] |

### Suggested Focus
**Primary:** [specific goal]
**Rationale:** [why this, why now]
**Done when:** [clear completion criteria]

### Improvement Signals
- [signals detected, or "None - healthy state"]

### Alternatives
- [if blocked or priorities shift]

Ready when you are, or redirect if priorities changed.
```

**Verification:** Summary presented; waiting for user direction.

## Output

- Session start summary (displayed, not saved)
- Improvement signals surfaced
- Proposed session goal

## Improvement Signal Details

### Stale Parking Lot Detection

Items in parking lot should be:
- **<1 week:** Fresh, will get to it
- **1-2 weeks:** Aging, consider scheduling
- **>2 weeks:** Stale, promote or delete

### Feature Drag Detection

Track session count per feature:
- **1-2 sessions:** Normal
- **3 sessions:** Check scope
- **4+ sessions:** Split or timebox

### Calibration Drift Detection

Compare estimates vs actuals in calibration.md:
- **Ratio <2x:** Calibrated well
- **Ratio 2-5x:** Minor adjustment needed
- **Ratio >5x:** Significant recalibration needed

## Integration with Session Close

These skills form a continuity loop:

```
┌─────────────────────────────────────────┐
│                                         │
│  /session-start                         │
│    ↓ load memory                        │
│    ↓ analyze progress                   │
│    ↓ propose goal                       │
│                                         │
│  [WORK SESSION]                         │
│                                         │
│  /session-close                         │
│    ↓ extract learnings                  │
│    ↓ update memory                      │
│    ↓ log session                        │
│    ↓ suggest next                       │
│                                         │
└─────────────────────────────────────────┘
```

Memory persists across the gap between sessions, creating continuity.

## Notes

### Token Economy

The purpose of loading memory first is to **avoid re-discovering** patterns through conversation. If I know from memory.md that "singleton pattern works well here," I don't need to figure that out again.

### Prioritization Philosophy

Prioritization emerges from:
1. **Deadlines** — What's urgent?
2. **Dependencies** — What unblocks other work?
3. **Momentum** — What builds on recent progress?
4. **Energy** — What matches current capacity?

### Continuous Improvement Loop

Improvement signals feed back into the process:
- Stale parking lot → Clean it up
- Feature drag → Improve scoping
- Calibration drift → Adjust estimates
- Recurring blockers → Fix root causes

This makes the start/close loop a **learning system**, not just bookkeeping.

## References

- Memory files: `.rai/memory/`
- Context: `CLAUDE.local.md`, `.claude/RAI.md`
- Progress: `dev/epic-*.md`
- Parking lot: `dev/parking-lot.md`
- Complement: `/session-close`
