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
  raise.version: "4.0.0"
  raise.visibility: public
---

# Session Start

## Purpose

Load deterministic context bundle from CLI, interpret it, propose focused work. The CLI assembles all data (profile, session state, memory graph, deadlines, coaching). The skill only does inference: interpret and present.

## Mastery Levels (ShuHaRi)

Experience level is in the context bundle — adapt output verbosity accordingly.

- **Shu**: Detailed explanations, teach concepts
- **Ha**: Balanced output, explain new concepts only
- **Ri**: Minimal output, essentials only

## Steps (3)

### Step 1: Load Orientation Bundle

```bash
rai session start --project "$(pwd)" --context
```

This single command:
- Loads developer profile from `~/.rai/developer.yaml`
- Loads session state from `.raise/rai/session-state.yaml`
- Assembles a lean bundle: **orientation** (work state, continuity, pending) + **manifest** (available priming sections with counts)
- Records the session start (increments count, sets active session)
- Warns about orphaned sessions if detected

**First-time user:** If no profile exists, ask for name:
```bash
rai session start --name "Name" --project "$(pwd)" --context
```

**If graph unavailable:** Run `rai memory build` first, then retry.

The bundle output includes an `# Available Context` manifest listing sections by name, item count, and token estimate. Use this to decide what to load in Step 2.

### Step 2: Load Task-Relevant Context

Based on the manifest from Step 1, load priming sections relevant to this session. The CLI serves sections by name — the skill decides what to load.

```bash
rai session context --sections governance,behavioral --project "$(pwd)"
```

**Available sections:** `governance`, `behavioral`, `coaching`, `deadlines`, `progress`

**Decision heuristic (in-context learning):**

| Session type | Recommended sections |
|-------------|---------------------|
| Feature work | `governance,behavioral` |
| Research/ideation | `behavioral` |
| Maintenance/bugs | `governance` |
| First session / new project | `governance,behavioral,coaching` |
| Near deadline (<7 days) | `deadlines,progress` (add to any above) |

**IMPORTANT:** These are recommendations, not rules. Adapt based on:
- What the manifest shows (if `governance: 0 items`, skip it)
- What the human says they want to work on
- What the next session prompt suggests

**Grounding check:** If a section shows 0 items where content is expected (e.g., `governance: 0`), flag it to the human and ask where to find grounding.

**Skip condition:** If no priming is needed (quick maintenance, clear continuity from narrative), skip Step 2 entirely.

### Step 3: Interpret & Present

With orientation from Step 1 and priming from Step 2, use inference to:

1. **Check signals:**
   - **Next session prompt** → if present, this is guidance from your past self. Read it first, use it to shape focus and proactively guide the human. This is your highest-priority continuity signal.
   - Release deadline pressure (<30 days → flag urgency, include days remaining)
   - Deadline pressure (<3 days → focus critical path)
   - Session narrative → review decisions, research, artifacts from last session for continuity
   - Coaching corrections → reinforce behavioral primes
   - Pending decisions or blockers → address first
   - Communication preferences (language, style, skip_praise, redirect) → adapt tone accordingly

2. **Check parking lot:** If `dev/parking-lot.md` exists, scan for stale items (>2 weeks).

3. **Propose session focus** based on:
   - Pending items from previous session (highest priority)
   - Current story/phase (continue where left off)
   - Deadlines (urgency modulation)

4. **Present** (adapt to experience level from bundle):

**Ri output:**
```
## Session: YYYY-MM-DD

**Context:** REL-{id} → [Epic] → [Story], [phase], N days to release
**Focus:** [goal]
**Signals:** [any, or "None"]

Go.
```

> Release appears in context line only when the current epic belongs to a release (from bundle output). Omit if no release.

**Shu output** adds: explanation of context, progress metrics, concepts.

## Output

| Item | Destination |
|------|-------------|
| Session summary | Displayed (not saved) |
| Signals | Displayed |
| Session state | `~/.rai/developer.yaml` (via CLI in Step 1) |

## Notes

- **Two-phase context loading:** Step 1 = orientation (always-on, ~100 tokens), Step 2 = priming (task-relevant, loaded by name)
- CLI is generic plumbing (serves sections by name), skill is composing intelligence (decides what to load)
- Manifest is self-describing — skill reads counts to make informed decisions
- Context bundle is deterministic — same inputs produce same output
- Skill is a thin inference layer — interpret, don't gather

## References

- Context bundle: `rai session start --context`
- Profile: `~/.rai/developer.yaml`
- Session state: `.raise/rai/session-state.yaml`
- Memory graph: `.raise/rai/memory/index.json`
- Parking lot: `dev/parking-lot.md`
- Complement: `/rai-session-close`
