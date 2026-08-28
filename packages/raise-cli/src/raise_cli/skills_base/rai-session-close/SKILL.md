---
name: rai-session-close
description: Capture session outcomes and update memory. Use to close a working session.
model: haiku

allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "end"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "5.0.0"
  raise.visibility: public
  raise.inputs: |
    - session_id: string, required, previous_skill
  raise.outputs: |
    - session_record: file_path, file
    - patterns: list, cli
---

# Session Close

## Purpose

Close a working session in ONE composite call. All writes (session record,
patterns, corrections, journal, state) happen atomically in `raise-cli` —
this skill only composes the structured summary and presents the result
(ADR-093 / ADR-024).

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through each CloseInput field with the developer
- **Ha**: Compose autonomously, confirm summary before closing
- **Ri**: Compose and close; surface only the confirmation

## Context

**When to use:** At the end of every working session with meaningful work.

**When to skip:** No meaningful work happened (plain rai session close clears state).

**Inputs:** Session activity (this conversation), active session id.

## Steps

### Step 1: Compose the close state (judgment — this is the LLM's job)

Reflect on the session and build a CloseInput JSON object:

```json
{
  "summary": "1-2 lines: what happened this session",
  "session_type": "feature|research|kata|ideation|maintenance",
  "outcomes": ["merged S7884.1", "created RAISE-7959"],
  "patterns": [
    {"content": "Action + context + reason, 100-300 chars",
     "context": "comma,separated,keywords", "type": "process"}
  ],
  "corrections": [
    {"what": "what the developer corrected", "lesson": "what to do next time"}
  ],
  "next_session_prompt": "Guidance for your future self — highest-signal continuity",
  "narrative": "Optional: decisions, blockers, open threads"
}
```

Quality bar: patterns are insights worth recalling across sessions (not
narrative); `next_session_prompt` is the single most valuable field.

### Step 2: Close (one call)

Use the `raise_session_close_full` MCP tool with state_json="{the JSON above}",
cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:

```bash
# Write the same object as YAML/JSON to a file, then:
rai session close --state-file /tmp/session-output.yaml --project .
```

Telemetry is emitted server-side — do NOT call signal/topic tools here.

| Result | Action |
|--------|--------|
| `status: ok` | Capture from response: `session_id`, `patterns` (int), `corrections` (int), `next_session_prompt` (str). Present Step 3. |
| `status: error` | Show `reason` to the developer; fix the state and retry once; then escalate |

### Step 3: Confirm

Present the close card verbatim from the tool response — do NOT recompose these fields:

```
Session closed — {response.session_id}
Recorded: {response.patterns} patterns, {response.corrections} corrections
Next session: {response.next_session_prompt}
```

If session artifacts (memory/state files) are tracked by the repo and dirty,
offer a `chore(session)` commit — never mix with story commits.

## Output

| Item | Destination |
|------|-------------|
| Session record + patterns + state | Atomic write via `raise_session_close_full` (CLI fallback: `--state-file`) |
| Confirmation | Presented to developer |

## Quality Checklist

- [ ] ONE composite call — no separate telemetry/memory/journal commands
- [ ] Patterns follow action+context+reason, 100-300 chars
- [ ] `next_session_prompt` filled — continuity is the point of closing well

## References

- Service: `raise_cli/session/close.py::process_session_close` · Complement: `/rai-session-start`
