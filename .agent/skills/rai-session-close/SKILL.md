---
description: 'Close a working session by reflecting on outcomes and feeding structured
  data to CLI. CLI does all writes atomically; skill does inference reflection.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: end
  raise.frequency: per-session
  raise.gate: ''
  raise.inputs: '- session_id: string, required, previous_skill

    '
  raise.next: ''
  raise.outputs: '- session_record: file_path, file

    - patterns: list, cli

    '
  raise.prerequisites: ''
  raise.version: 4.1.0
  raise.visibility: public
  raise.work_cycle: session
name: rai-session-close
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
rai session close --summary "Quick fix session" --type maintenance --project .
```

## Steps

### Step 1: Craft Session Title

Generate a descriptive session title (max 80 chars) that captures what was accomplished — not planned, accomplished. Include the **epic/story name** (not just the number) so the title is self-explanatory without looking up Jira. Use the format: `SES-{ID}: {title}`.

**Good** (descriptive, includes context):
- `SES-321: E355 Branch Model Evolution cerrado + backlog review y priorización E354`
- `SES-318: E347 Backlog Automation — epic completo, 7 stories, merge a dev`
- `SES-316: Backlog sync + Semgrep MCP investigation`

**Bad** (too terse, requires lookup):
- `SES-321: E355 complete + backlog review`
- `SES-318: E347 done`

The title will be used in the `summary` field of the state file AND presented to the human for `/rename`.

### Step 2: Reflect & Produce State File

Use inference to reflect on the session and write a YAML state file.

**IMPORTANT:** Read `.raise/rai/personal/session-output.yaml` first if it exists — Claude Code requires reading a file before overwriting it. Same for `dev/parking-lot.md` when capturing tangents.

State file structure:

```yaml
# .raise/rai/personal/session-output.yaml
session_id: "{SES-ID}"
summary: "{session_title}"  # The concise title from Step 1
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

### Step 3: Clean Working Tree

Before closing, ensure no uncommitted changes are left behind:

1. Run `git status`
2. If working tree is clean → proceed to Step 3
3. If there are uncommitted changes → present them to the human with options:
   - **Commit**: stage and commit with a descriptive message
   - **Discard**: `git restore` the files (confirm first)
   - **Leave**: explicitly acknowledge the leftovers in the handoff
4. Do NOT close the session with a dirty working tree unless the human explicitly chooses "Leave"

### Step 4: Feed CLI

```bash
rai session close --state-file .raise/rai/personal/session-output.yaml --session {SES-ID} --project .
```

This atomically: records session in index, appends patterns, updates coaching, writes session state, clears active session.

Present the closing card:

```
## Session Closed: SES-{ID} {session_title}

**Type:** {type}
**Outcomes:**
- {outcome 1}
- {outcome 2}
**Patterns:** {N new} | **Working tree:** {clean | N files uncommitted}

### Next Session
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
- [ ] Working tree clean (or leftovers explicitly acknowledged)
- [ ] CLI close command executed successfully

## References

- Complement: `/rai-session-start`
- Session state: `.raise/rai/session-state.yaml`
- Parking lot: `dev/parking-lot.md`
