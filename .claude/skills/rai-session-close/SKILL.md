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
  raise.version: "4.0.0"
  raise.visibility: public
---

# Session Close

## Purpose

Close a session by reflecting on outcomes and feeding structured data to the CLI for atomic persistence.

## Mastery Levels (ShuHaRi)

- **Shu**: Detailed handoff with explanations of what was captured
- **Ha**: Standard handoff, explain only notable items
- **Ri**: Minimal handoff — next step and open items only

## Context

**When to use:** At the end of every working session.

**Quick close:** For short sessions, use CLI flags directly instead of a state file:
```bash
rai session close --summary "Quick fix session" --type maintenance --project "$(pwd)"
```

## Steps

### Step 1: Reflect & Produce State File

Use inference to reflect on the session and write a YAML state file:

```yaml
# /tmp/session-output-{SES-ID}.yaml
session_id: "{SES-ID}"
summary: "What was accomplished"
type: feature  # feature | research | maintenance | infrastructure | ideation
outcomes:
  - "Concrete deliverable 1"
patterns:
  - description: "Pattern learned"
    context: "tag1,tag2"
    type: process
corrections:
  - what: "Behavioral observation"
    lesson: "Lesson learned"
coaching:                          # Only include fields that changed
  trust_level: "established"
  strengths: ["structured thinking"]
  growth_edge: "async patterns"
  autonomy: "high within defined scope"
  relationship:
    quality: "productive"
    trajectory: "stable"
current_work:
  release: V3.0
  epic: E15
  story: S15.7
  phase: implement
  branch: story/s15.7/session-protocol
pending:
  decisions: []
  blockers: []
  next_actions: ["Continue with Task 7"]
narrative: |
  ## Decisions
  - Key decisions and WHY
  ## Research
  - Conclusions with file paths
  ## Artifacts
  - Files created/modified
  ## Branch State
  - Branch and commits ahead of base
next_session_prompt: |
  Forward-looking guidance to future Rai. What to prioritize,
  what to watch for, what context will be critical.
```

**Capture tangents:** Check conversation for ideas → add to `dev/parking-lot.md`.

### Step 2: Feed CLI

```bash
rai session close --state-file /tmp/session-output-{SES-ID}.yaml --session {SES-ID} --project "$(pwd)"
```

This atomically: records session in index, appends patterns, updates coaching, writes session state, clears active session.

Present a brief handoff:
```
## Next Session
**Continue:** [next step]
**Open:** [unresolved questions, if any]
```

## Output

| File | Update | Writer |
|------|--------|--------|
| `.raise/rai/personal/sessions/index.jsonl` | Session record | CLI |
| `.raise/rai/memory/patterns.jsonl` | New patterns | CLI |
| `~/.rai/developer.yaml` | Coaching + clear session | CLI |
| `.raise/rai/session-state.yaml` | Working state | CLI |
| `dev/parking-lot.md` | Tangents | Skill (Edit) |

## Quality Checklist

- [ ] Session ID matches the active session from session-start
- [ ] Summary reflects actual outcomes (not planned intent)
- [ ] Narrative enables next session to resume immediately
- [ ] Next session prompt is actionable and specific
- [ ] Tangents captured in parking lot (if any)
- [ ] CLI close command executed successfully

## References

- Complement: `/rai-session-start`
- Session state: `.raise/rai/session-state.yaml`
- Parking lot: `dev/parking-lot.md`
