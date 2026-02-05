---
name: session-start
description: >
  Begin a session by loading memory, analyzing progress, and proposing
  focused work. Creates continuity across sessions and surfaces improvement
  signals for continuous improvement. Adapts to developer experience level.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "start"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=session-start \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Session Start: Context & Prioritization

## Purpose

Begin a working session by loading accumulated memory, analyzing progress against goals, and proposing focused work. This creates continuity across sessions and surfaces signals for continuous improvement.

**Adaptive:** This skill adapts to the developer's experience level (Shu/Ha/Ri), providing more guidance for beginners and efficiency for experts.

## Mastery Levels (ShuHaRi)

This skill adapts its behavior based on the developer's experience level:

| Level | Sessions | Behavior |
|-------|----------|----------|
| **Shu (守)** | 0-5 | Full explanations, teach RaiSE concepts, guide each step |
| **Ha (破)** | 6-20 | Explain new concepts, efficient on known patterns |
| **Ri (離)** | 21+ | Minimal ceremony, maximum efficiency, just the essentials |

The experience level is read from `~/.rai/developer.yaml`.

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
- Developer profile (`~/.rai/developer.yaml`) — experience level, personal preferences
- Unified graph (`.raise/graph/unified.json`) — primary source (sessions, patterns, work items)
- `CLAUDE.local.md` — deadlines, human notes (not in graph)
- `dev/parking-lot.md` — improvement signals (not in graph)

**Output:**
- Session start summary with proposed focus
- Improvement signals surfaced
- Clear handoff from previous session

## Steps

### Step 0: Load Developer Profile (Required)

Load the developer's personal profile to determine experience level and preferences:

```bash
raise profile show
```

> **Development note:** In raise-commons, use `uv run raise` instead of bare `raise`.

**What this returns:**
- `experience_level`: shu, ha, or ri
- `communication`: style preferences
- `sessions_total`: total sessions across all projects
- `skills_mastered`: skills the developer knows well

**If no profile exists:** This is a first-time user. Treat as Shu level and explain that you're creating their profile at session end.

**Adapt your behavior:**
- **Shu:** Include `[CONCEPT]` blocks below, explain terminology, be thorough
- **Ha:** Skip basic concepts, explain only new patterns
- **Ri:** Skip to essentials, minimal output

**Verification:** Experience level determined; behavior mode set.

---

## [CONCEPT] The RaiSE Triad (Shu Only)

> **Show this block only for Shu-level developers.**

If the developer is new to RaiSE, explain the core mental model:

```
"Before we dive in, let me explain how we'll work together.

RaiSE is built on a 'triad' — three parts working together:

    YOU (RaiSE Engineer)
    ├── Bring: Judgment, intuition, domain knowledge
    └── Own: Strategic decisions, final approval

    RAI (AI Partner)
    ├── Bring: Pattern recognition, execution, memory
    └── Own: Following governance, remembering context

    RAISE (Methodology)
    ├── Bring: Structure, validation gates, guardrails
    └── Own: Process consistency, quality assurance

Neither of us works alone. You bring what I can't (judgment), I bring what
you shouldn't have to repeat (patterns, context). RaiSE keeps us both honest.

This session start is part of that — I'm loading context so I remember
what we've learned together."
```

---

### Step 1: Query Unified Context (Required)

Query the unified graph for session-relevant context. This is the **primary** method — more efficient than reading raw files.

```bash
raise context query "session epic patterns calibration" --unified --limit 10
```

**What this returns:**
- Recent session history with outcomes
- Relevant patterns for likely work
- Calibration data for estimation
- Current epic/feature context

**Extract from results:**
- Patterns relevant to likely work
- Recent session outcomes
- Calibration signals (velocity, sizing accuracy)
- Any open questions from previous sessions

**Verification:** Context loaded; key patterns recalled.

> **If graph unavailable:** Run `raise graph build --unified` first, or fall back to Step 1b.

### Step 1b: Load Memory Files (Fallback)

**Only if unified graph is unavailable**, read raw files from `.rai/memory/`:

```
1. patterns.jsonl — Learned patterns
2. calibration.jsonl — Velocity data, sizing accuracy
3. sessions/index.jsonl — Recent session history
```

**Note:** This is less efficient than the unified query — use only as fallback.

**Verification:** Memory loaded from raw files.

> **If you can't continue:** Memory files missing → Create them via `/session-close` pattern.

---

## [CONCEPT] Why Memory Matters (Shu Only)

> **Show this block only for Shu-level developers.**

```
"You might wonder why I'm loading all this context.

Without memory, every session starts cold. I'd ask the same questions,
make the same mistakes, suggest the same things you've already rejected.

With memory, I remember:
- Patterns that worked in this codebase
- Your velocity (how fast we actually ship)
- What we tried and why it failed
- Where we left off

This is the 'reliable' in Reliable AI Software Engineering — I don't
forget what we've learned together."
```

---

### Step 2: Load Human Context

Read **only** what the graph doesn't contain:

```
CLAUDE.local.md — Deadlines, human notes, quick references
```

**Why only this file:**
- Identity is preloaded via SessionStart hook (no need to read RAI.md)
- Epic/feature info is in the unified graph (work items)
- Session history is in the unified graph (session nodes)
- CLAUDE.local.md has human-maintained context: deadlines, focus notes, references

**Extract:**
- Deadline pressure (dates not in graph)
- Human notes about current focus
- Quick reference paths

**Verification:** Deadlines and human context loaded.

> **If you can't continue:** File outdated → Note and update during session.

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

### Step 4: Check Parking Lot (Skip for Ri)

> **Ri-level developers:** Skip this step unless deadline pressure detected.

Read `dev/parking-lot.md` (not in unified graph — informal capture, not structured):

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

Output the session start summary. **Adapt format to experience level:**

#### For Shu (Detailed)

```markdown
## Session Start: YYYY-MM-DD

Welcome back! Here's where we stand.

### Context Loaded
- **Memory:** X patterns, Y calibrations loaded
- **Your level:** Shu (I'll explain concepts as we go)
- **Last session:** [brief outcome]
- **Current focus:** [Epic] → [Feature]

### What This Means
[Brief explanation of current state in plain language]

### Progress Check
| Metric | Status | What It Means |
|--------|--------|---------------|
| Epic | X% complete | [explanation] |
| Deadline | N days | [urgency level] |
| Velocity | [rate] | [comparison to baseline] |

### Suggested Focus
**What:** [specific goal]
**Why now:** [rationale in plain language]
**Done when:** [clear criteria]

### Improvement Signals
- [signals with explanations]

### What's Next
[Clear guidance on how to proceed]

Ready when you are. Ask questions anytime — that's how we both learn.
```

#### For Ha (Balanced)

```markdown
## Session Start: YYYY-MM-DD

### Context
- **Memory:** X patterns loaded
- **Last session:** [outcome]
- **Focus:** [Epic] → [Feature]

### Progress
| Metric | Status |
|--------|--------|
| Epic | X% (N/M SP) |
| Deadline | N days |
| Velocity | [assessment] |

### Suggested Focus
**Primary:** [goal]
**Rationale:** [why]
**Done when:** [criteria]

### Signals
- [any signals, or "Healthy"]

Ready to proceed.
```

#### For Ri (Minimal)

```markdown
## Session: YYYY-MM-DD

**Context:** [Epic] → [Feature], X% complete, N days to deadline
**Focus:** [specific goal]
**Signals:** [any, or "None"]

Go.
```

**Verification:** Summary presented; waiting for user direction.

### Step 8: Record Session (Required)

At the end of the skill, record this session in the developer profile:

```bash
raise profile session --project "$(pwd)"
```

This:
- Increments `sessions_total`
- Updates `last_session` to today
- Adds project to `projects` list if new

**For first-time users (no profile):**
```bash
raise profile session --name "[ask user's name]" --project "$(pwd)"
```

**Verification:** Session recorded; profile updated.

---

## Output

- Session start summary (displayed, not saved)
- Improvement signals surfaced
- Proposed session goal
- Developer profile updated (session count incremented)

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
│    ↓ load profile (experience level)    │
│    ↓ load memory                        │
│    ↓ analyze progress                   │
│    ↓ propose goal (adapted to level)    │
│    ↓ record session                     │
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
Profile persists across projects, creating a personal relationship.

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

### Adaptive Interaction Philosophy

The goal isn't to dumb things down for beginners or rush experts. It's to:
- **Shu:** Build understanding so they can eventually work independently
- **Ha:** Reinforce patterns while introducing new concepts
- **Ri:** Respect their time and expertise

Education is built into the workflow, not bolted on.

## References

- **Developer profile:** `~/.rai/developer.yaml` — experience level, preferences
- **Primary:** Unified graph (`.raise/graph/unified.json`) — sessions, patterns, work items
- **Fallback:** Memory files (`.rai/memory/`) — only if graph unavailable
- **Human context:** `CLAUDE.local.md` — deadlines, notes (not in graph)
- **Improvement signals:** `dev/parking-lot.md` — informal captures (not in graph)
- **Complement:** `/session-close`
