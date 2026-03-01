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
  raise.inputs: |
    - project_path: string, required, argument
    - developer_profile: file_path, required, config
  raise.outputs: |
    - session_id: string, next_skill
    - context_bundle: string, cli
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

**When to skip:** Continuation of an active session (context already loaded).

**Inputs:** Developer profile (`~/.rai/developer.yaml`). If no profile exists, ask for the developer's name and pass `--name "Name"`.

## Steps

### Step 1: Load Orientation Bundle

```bash
rai session start --project "$(pwd)" --context
```

Loads developer profile, session state, and orientation bundle. If graph unavailable: run `rai graph build` first.

**IMPORTANT:** This is the ONLY CLI command in this skill. The context bundle output is complete — do NOT invent additional flags (e.g. `--section`), sub-commands (e.g. `rai context load`), or follow-up CLI calls to "fetch more". If the bundle mentions available context sections, that information is for display only. All interpretation happens in Step 2 using inference, not additional tool calls.

### Step 2: Interpret & Present

1. **Check signals** (priority order):
   - Next session prompt → guidance from your past self, highest-priority continuity
   - Release/deadline pressure → flag urgency with days remaining
   - Session narrative → review decisions, research, artifacts for continuity
   - Pending decisions or blockers → address first
   - Communication preferences → adapt tone

2. **Propose session focus** from: pending items > current story/phase > deadlines

3. **Present** (adapt verbosity to developer level):

```
## Session: YYYY-MM-DD

**Context:** [Release →] [Epic] → [Story], [phase]
**Focus:** [goal]
**Signals:** [any, or "None"]
```

## Output

| Item | Destination |
|------|-------------|
| Session initialized | CLI session state updated |
| Focus proposed | Presented to developer |
| Next | Begin work on proposed focus |

## Quality Checklist

- [ ] Orientation bundle loaded successfully
- [ ] Signals interpreted in priority order
- [ ] Session focus proposed from pending work
- [ ] Verbosity adapted to developer ShuHaRi level

## References

- Profile: `~/.rai/developer.yaml`
- Session state: `.raise/rai/session-state.yaml`
- Complement: `/rai-session-close`
