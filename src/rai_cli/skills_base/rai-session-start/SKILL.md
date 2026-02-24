---
name: rai-session-start
description: >
  Begin a session by loading context bundle, interpreting it, and proposing work.
  CLI does all data plumbing; skill does inference interpretation.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "start"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "5.0.0"
  raise.visibility: public
---

# Session Start

## Purpose

Load context bundle from CLI, interpret signals, and propose focused work for the session.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain context, progress metrics, and concepts in presentation
- **Ha**: Explain only new or non-obvious signals
- **Ri**: Minimal output — context line, focus, signals, "Go."

## Context

**When to use:** At the start of every working session.

**First-time user:** If no profile exists, ask for the developer's name and pass `--name "Name"`.

## Steps

### Step 1: Load Orientation Bundle

```bash
rai session start --project "$(pwd)" --context
```

This loads the developer profile, session state, and assembles the orientation bundle with an available context manifest.

If graph unavailable: run `rai graph build` first.

### Step 2: Load Task-Relevant Context

Based on the manifest from Step 1, load priming sections:

```bash
rai session context --sections governance,behavioral --project "$(pwd)"
```

| Session type | Recommended sections |
|-------------|---------------------|
| Feature work | `governance,behavioral` |
| Research/ideation | `behavioral` |
| Maintenance/bugs | `governance` |
| First session / new project | `governance,behavioral,coaching` |
| Near deadline (<7 days) | Add `deadlines,progress` to above |

Adapt based on manifest counts (skip empty sections) and what the human says they want to work on.

Skip this step if continuity from the narrative is sufficient.

### Step 3: Interpret & Present

1. **Check signals** (priority order):
   - Next session prompt → guidance from your past self, highest-priority continuity
   - Release/deadline pressure → flag urgency with days remaining
   - Session narrative → review decisions, research, artifacts for continuity
   - Pending decisions or blockers → address first
   - Communication preferences → adapt tone

2. **Check parking lot** (`dev/parking-lot.md`) for stale items (>2 weeks)

3. **Propose session focus** from: pending items > current story/phase > deadlines

4. **Present** (adapt verbosity to developer level):

```
## Session: YYYY-MM-DD

**Context:** [Release →] [Epic] → [Story], [phase]
**Focus:** [goal]
**Signals:** [any, or "None"]
```

## Output

| Item | Destination |
|------|-------------|
| Session summary | Displayed (not saved) |
| Signals | Displayed |
| Session state | `~/.rai/developer.yaml` (via CLI in Step 1) |

## Quality Checklist

- [ ] Bundle loaded and manifest reviewed
- [ ] Priming sections match session type
- [ ] Next session prompt addressed (if present)
- [ ] Stale parking lot items flagged (if any)
- [ ] Session focus proposed with clear goal

## References

- Profile: `~/.rai/developer.yaml`
- Session state: `.raise/rai/session-state.yaml`
- Parking lot: `dev/parking-lot.md`
- Complement: `/rai-session-close`
