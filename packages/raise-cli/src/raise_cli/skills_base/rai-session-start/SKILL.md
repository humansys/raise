---
name: rai-session-start
description: Load context and propose session focus. Use at the start of every working session.

allowed-tools:
  - Read
  - Grep
  - Glob

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
rai session start --project . --context
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

2. **Check MCP health** (non-blocking, never alarming):
   - Run `rai mcp list` to detect registered servers
   - If no servers registered: skip silently (no output)
   - If servers found: run `rai mcp health <name>` for each
   - Collect status: healthy count, unhealthy count, total
   - **If health check fails** (missing module, connection error, etc.): report as "not connected" — never show tracebacks or error details to the user. MCP servers are optional integrations, not critical infrastructure

3. **Propose session focus** from: pending items > current story/phase > deadlines

4. **Present** (adapt verbosity to developer level):

```
## Session: YYYY-MM-DD

**Context:** [Release →] [Epic] → [Story], [phase]
**Focus:** [goal]
**MCP:** [{total} servers, all healthy] or [{total} servers, {N} not connected — run /rai-mcp-status]
**Signals:** [any, or "None"]
```

Omit the **MCP:** line entirely if no servers are registered.

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
- [ ] MCP health checked when servers registered (silent skip if none)

## References

- Profile: `~/.rai/developer.yaml`
- Session state: `.raise/rai/session-state.yaml`
- MCP: `rai mcp list`, `rai mcp health`, `/rai-mcp-status`
- Complement: `/rai-session-close`
