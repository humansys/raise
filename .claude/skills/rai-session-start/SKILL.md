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
---

# Session Start

## Purpose

Load deterministic context bundle from CLI, interpret it, propose focused work. The CLI assembles all data (profile, session state, memory graph, deadlines, coaching). The skill only does inference: interpret and present.

## Mastery Levels (ShuHaRi)

Experience level is in the context bundle — adapt output verbosity accordingly.

- **Shu**: Detailed explanations, teach concepts
- **Ha**: Balanced output, explain new concepts only
- **Ri**: Minimal output, essentials only

## Steps (2)

### Step 1: Load Context Bundle

```bash
rai session start --project "$(pwd)" --context
```

This single command:
- Loads developer profile from `~/.rai/developer.yaml`
- Loads session state from `.raise/rai/session-state.yaml`
- Queries memory graph for foundational patterns
- Assembles a ~150 token context bundle
- Records the session start (increments count, sets active session)
- Warns about orphaned sessions if detected

**First-time user:** If no profile exists, ask for name:
```bash
rai session start --name "Name" --project "$(pwd)" --context
```

**If graph unavailable:** Run `rai memory build` first, then retry.

### Step 2: Interpret & Present

With the context bundle from Step 1, use inference to:

1. **Check signals:**
   - Deadline pressure (<3 days → focus critical path)
   - Coaching corrections → reinforce behavioral primes
   - Pending decisions or blockers → address first

2. **Check parking lot:** If `dev/parking-lot.md` exists, scan for stale items (>2 weeks).

3. **Propose session focus** based on:
   - Pending items from previous session (highest priority)
   - Current story/phase (continue where left off)
   - Deadlines (urgency modulation)

4. **Present** (adapt to experience level from bundle):

**Ri output:**
```
## Session: YYYY-MM-DD

**Context:** [Epic] → [Story], [phase], N days to deadline
**Focus:** [goal]
**Signals:** [any, or "None"]

Go.
```

**Shu output** adds: explanation of context, progress metrics, concepts.

## Output

| Item | Destination |
|------|-------------|
| Session summary | Displayed (not saved) |
| Signals | Displayed |
| Session state | `~/.rai/developer.yaml` (via CLI in Step 1) |

## Notes

- **One CLI call** does all data plumbing — no separate profile/memory/graph queries
- Context bundle is deterministic — same inputs produce same output
- Skill is a thin inference layer — interpret, don't gather
- Foundational patterns in bundle serve as behavioral primes

## References

- Context bundle: `rai session start --context`
- Profile: `~/.rai/developer.yaml`
- Session state: `.raise/rai/session-state.yaml`
- Memory graph: `.raise/rai/memory/index.json`
- Parking lot: `dev/parking-lot.md`
- Complement: `/rai-session-close`
