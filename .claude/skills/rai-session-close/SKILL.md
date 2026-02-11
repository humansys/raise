---
name: rai-session-close
description: >
  Close a working session by reflecting on outcomes and feeding structured data to CLI.
  CLI does all writes atomically; skill does inference reflection.

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "end"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
---

# Session Close

## Purpose

Close a session by reflecting on outcomes and feeding structured data to the CLI. The CLI performs all writes atomically (session index, patterns, coaching, session state, profile). The skill only does inference: reflect and produce structured output.

## Mastery Levels (ShuHaRi)

Experience level affects verbosity of the handoff message, not the operations.

## Steps (2)

### Step 1: Reflect & Produce Structured Output

Use inference to reflect on the session:

1. **Summary:** What was accomplished? (1-2 sentences)
2. **Session type:** feature, research, maintenance, infrastructure, ideation
3. **Outcomes:** List of concrete deliverables
4. **Patterns:** Any new learnings? (check against existing — query if needed)
5. **Corrections:** Any behavioral corrections observed? (what + lesson)
6. **Coaching:** Reflect on the working relationship (see below)
7. **Current work:** Epic, story, phase, branch for continuity
8. **Pending:** Decisions, blockers, next actions
9. **Tangents:** Check conversation for ideas → add to `dev/parking-lot.md`

Write the structured output as a YAML state file:

```yaml
# /tmp/session-output.yaml
summary: "Session protocol implementation"
type: feature
outcomes:
  - "Tasks 1-6 complete"
  - "136 tests passing"
patterns:
  - description: "Pattern description here"
    context: "tag1,tag2"
    type: process
corrections:
  - what: "Behavioral observation"
    lesson: "Lesson learned"
coaching:                                # Only include fields that changed
  trust_level: "developing"              # new → developing → established → deep
  strengths:
    - "structured thinking"
    - "design discipline"
  growth_edge: "async patterns"
  autonomy: "high within defined scope"
  relationship:
    quality: "productive"                # new → productive → established → deep
    trajectory: "growing"                # starting → growing → stable → deepening
  communication_notes:
    - "prefers direct, concise"
current_work:
  epic: E15
  story: S15.7
  phase: implement
  branch: story/s15.7/session-protocol
pending:
  decisions: []
  blockers: []
  next_actions:
    - "Continue with Task 7"
notes: "Any free-form notes"
```

### Step 2: Feed CLI

```bash
rai session close --state-file /tmp/session-output.yaml --project "$(pwd)"
```

This single command atomically:
- Records session in `sessions/index.jsonl`
- Appends patterns to `patterns.jsonl`
- Updates coaching (corrections + observations) in `~/.rai/developer.yaml`
- Writes `.raise/rai/session-state.yaml`
- Clears `current_session` in profile

**Alternative (simple close):** For quick sessions without state file:
```bash
rai session close --summary "Quick fix session" --type maintenance --project "$(pwd)"
```

**With inline pattern/correction:**
```bash
rai session close \
  --summary "Session description" \
  --type feature \
  --pattern "New pattern learned" \
  --correction "What happened" \
  --correction-lesson "What to do instead" \
  --project "$(pwd)"
```

After the CLI call, output a brief handoff:

```
## Next Session
**Continue:** [next step]
**Open:** [unresolved questions, if any]
```

## Output

All writes are done by the CLI in Step 2 — the skill does NOT call separate memory/telemetry commands.

| File | Update | Writer |
|------|--------|--------|
| `.raise/rai/personal/sessions/index.jsonl` | Session record | CLI |
| `.raise/rai/memory/patterns.jsonl` | New patterns | CLI |
| `~/.rai/developer.yaml` | Coaching + clear session | CLI |
| `.raise/rai/session-state.yaml` | Working state | CLI |
| `dev/parking-lot.md` | Tangents | Skill (Edit) |

## Notes

- **One CLI call** does all data plumbing — no separate add-session/add-pattern/emit-session
- Idempotent: can close multiple times (second close overwrites with more current data)
- State file is the richest path; CLI flags are for simple/quick closes
- Calibration (if stories completed): still run separately:
  ```bash
  rai memory add-calibration {story_id} --name "Name" -s {size} -a {actual_mins}
  ```

## References

- Complement: `/rai-session-start`
- Session state: `.raise/rai/session-state.yaml`
- Memory: `.raise/rai/memory/`
- Tangents: `dev/parking-lot.md`
