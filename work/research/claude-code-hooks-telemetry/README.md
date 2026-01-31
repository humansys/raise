# Research: Claude Code Hooks for Telemetry

> **Status**: Complete
> **Date**: 2026-01-31
> **Decision**: Informs RaiSE Observable Workflow implementation

---

## Question

What hooks/mechanisms does Claude Code provide for emitting custom telemetry events?

## Answer

**Three mechanisms available:**

1. **Built-in OpenTelemetry** — Native OTEL support, just enable with env vars
2. **Skill-scoped hooks** — Skills can define hooks in frontmatter
3. **Scripts in skills** — Deterministic code can write to JSONL

---

## Key Findings

### 1. Skill-Scoped Hooks (CRITICAL for RaiSE)

Skills can define their own hooks in YAML frontmatter:

```yaml
---
name: feature-design
description: Create feature specifications
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "./scripts/log-skill-completed.sh"
---
```

**These hooks are scoped to the skill's lifecycle** — they only run when the skill is active!

### 2. Built-in OpenTelemetry

Claude Code has native OTEL support:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

Events emitted: `api_request`, `tool_result`, costs, tokens, etc.

### 3. Available Hook Events

| Event | When | RaiSE Use |
|-------|------|-----------|
| SessionStart | Session begins | Load RaiSE context |
| PostToolUse | Tool completes | Log artifact creation |
| Stop | Skill completes | Log skill completion |
| SessionEnd | Session ends | Final telemetry flush |

### 4. Hook Input/Output

**Input** (JSON on stdin):
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "tool_name": "Write",
  "tool_input": { "file_path": "...", "content": "..." }
}
```

**Output** (JSON on stdout):
```json
{
  "additionalContext": "Artifact created, logged to telemetry"
}
```

---

## RaiSE Telemetry Architecture

```
┌─────────────────────────────────────────────────┐
│              RaiSE Skill                         │
│                                                  │
│  hooks:                                          │
│    PostToolUse:                                  │
│      - matcher: "Write"                          │
│        hooks:                                    │
│          - type: command                         │
│            command: "scripts/log-event.sh"       │
│                                                  │
│  scripts/                                        │
│    log-event.sh  → writes to .raise/telemetry/  │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            .raise/telemetry/                     │
│                                                  │
│  events.jsonl                                    │
│  {"event":"skill_started","skill":"design",...}  │
│  {"event":"artifact_created","path":"..."}       │
│  {"event":"gate_validated","gate":"gate-design"} │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              raise-cli                           │
│                                                  │
│  raise telemetry summary                         │
│  raise telemetry export --format otel            │
└─────────────────────────────────────────────────┘
```

---

## Implementation Recommendations

### 1. Add Hooks to RaiSE Skills

Each RaiSE skill should include hooks for telemetry:

```yaml
---
name: feature-design
description: ...
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PROJECT_DIR}/.claude/skills/scripts/log-skill-complete.sh"
---
```

### 2. Create Shared Telemetry Scripts

```bash
# .claude/skills/scripts/log-skill-complete.sh
#!/bin/bash
INPUT=$(cat)
SKILL_NAME=$(echo "$INPUT" | jq -r '.hook_event_name')
TIMESTAMP=$(date -Iseconds)

echo "{\"event\":\"skill_completed\",\"skill\":\"$SKILL_NAME\",\"timestamp\":\"$TIMESTAMP\"}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/telemetry/events.jsonl"
```

### 3. Consider Built-in OTEL for Base Metrics

For token usage, API calls, basic tool metrics — use Claude Code's built-in OTEL.

For RaiSE-specific events (gates, skills, workflow) — use skill-scoped hooks.

---

## Limitations

1. **No "skill invocation" event** — Hooks fire on tools, not skill activation
2. **Hooks cannot invoke skills** — Only bash commands, prompts, or agents
3. **Custom events require scripts** — No direct API for custom telemetry

---

## Confidence

**HIGH** — Official documentation confirms all mechanisms.

---

## Sources

- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Monitoring](https://code.claude.com/docs/en/monitoring-usage)
- [Full evidence catalog](sources/evidence-catalog.md)

---

*Research completed using /research skill (pilot test)*
*Researcher: Rai (Claude Opus 4.5)*
