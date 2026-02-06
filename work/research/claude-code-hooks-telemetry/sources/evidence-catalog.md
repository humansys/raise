# Evidence Catalog: Claude Code Hooks for Telemetry

> Research ID: claude-code-hooks-telemetry-20260131
> Date: 2026-01-31
> Tool: WebSearch
> Depth: Quick scan

---

## Summary

- **Total Sources**: 10
- **Evidence Distribution**: Very High (2), High (5), Medium (3)

---

## Sources

### 1. Claude Code Hooks Reference (Official)

**Source**: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: 12 hook events covering full session lifecycle. Hooks can be embedded in skill frontmatter, scoped to skill execution.
- **Relevance**: CRITICAL - Skills can define their own hooks for telemetry.

### 2. Claude Code Monitoring Documentation (Official)

**Source**: [code.claude.com/docs/en/monitoring-usage](https://code.claude.com/docs/en/monitoring-usage)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Native OpenTelemetry support. `CLAUDE_CODE_ENABLE_TELEMETRY=1` enables OTEL export. Events include api_request, tool_result.
- **Relevance**: Built-in telemetry can be enabled without custom hooks.

### 3. DataCamp Hooks Tutorial

**Source**: [datacamp.com/tutorial/claude-code-hooks](https://www.datacamp.com/tutorial/claude-code-hooks)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Hooks give deterministic control over actions. JSON input on stdin, JSON output on stdout for structured control.
- **Relevance**: Confirms hook I/O pattern for telemetry emission.

### 4. Claude Code Internals: Telemetry and Metrics

**Source**: [kotrotsos.medium.com/claude-code-internals-part-15-telemetry](https://kotrotsos.medium.com/claude-code-internals-part-15-telemetry-and-metrics-1c4fafedbda8)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Claude Code tracks metrics throughout operation. Every API call, tool execution, and session milestone generates data.
- **Relevance**: Shows depth of built-in telemetry.

### 5. Claude Code + OpenTelemetry + Grafana Guide

**Source**: [quesma.com/blog/track-claude-code-usage-and-limits-with-grafana-cloud](https://quesma.com/blog/track-claude-code-usage-and-limits-with-grafana-cloud/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: OTEL_METRICS_EXPORTER=otlp, OTEL_EXPORTER_OTLP_ENDPOINT configure export. Privacy controls available.
- **Relevance**: Shows how to configure telemetry export.

### 6. SigNoz Claude Code Monitoring

**Source**: [signoz.io/blog/claude-code-monitoring-with-opentelemetry](https://signoz.io/blog/claude-code-monitoring-with-opentelemetry/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Claude emits structured logs for each event. Can export to log aggregation systems, columnar stores, or observability platforms.
- **Relevance**: Validates OpenTelemetry integration.

### 7. Claude Code Hook Limitations Article

**Source**: [dev.to/aabyzov/claude-code-hook-limitations](https://dev.to/aabyzov/claude-code-hook-limitations-no-skill-invocation-lazy-plugin-loading-and-how-i-solved-it-44f2)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Hooks cannot invoke skills directly. But hooks can be defined IN skill frontmatter, scoped to skill lifecycle.
- **Relevance**: Confirms skill-scoped hooks are the pattern.

### 8. Claude_telemetry GitHub Project

**Source**: [github.com/TechNickAI/claude_telemetry](https://github.com/TechNickAI/claude_telemetry)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Community wrapper that logs tool calls, token usage, costs, and execution traces to OTEL backends.
- **Relevance**: Shows community approach to telemetry.

### 9. Skill Activation Hook Article

**Source**: [claudefa.st/blog/tools/hooks/skill-activation-hook](https://claudefa.st/blog/tools/hooks/skill-activation-hook)
- **Type**: Tertiary
- **Evidence Level**: Medium
- **Key Finding**: Hooks can force skill loading. SessionStart hooks can add context.
- **Relevance**: Shows hook patterns for skill integration.

### 10. Claude Code Full Stack Explanation

**Source**: [alexop.dev/posts/understanding-claude-code-full-stack](https://alexop.dev/posts/understanding-claude-code-full-stack/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Hooks are first-class citizens across the system. Can be defined in agent frontmatter, skill frontmatter, settings.
- **Relevance**: Confirms architectural pattern.

---

## Key Findings Summary

### Hook Events Available

| Event | When | Can Block | Useful For Telemetry |
|-------|------|-----------|---------------------|
| SessionStart | Session begins | No | Log session start |
| UserPromptSubmit | Prompt submitted | Yes | Log user actions |
| PreToolUse | Before tool | Yes | Log tool attempts |
| PostToolUse | After tool success | No | Log tool completions |
| PostToolUseFailure | After tool fails | No | Log failures |
| Stop | Claude stops | Yes | Log session end |
| SubagentStart | Subagent spawns | No | Log agent spawns |
| SubagentStop | Subagent ends | Yes | Log agent results |
| SessionEnd | Session terminates | No | Cleanup, final log |

### Skill-Scoped Hooks (CRITICAL)

```yaml
---
name: story-design
description: ...
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/log-tool-use.sh"
---
```

**Skills can define their own hooks in frontmatter, scoped to skill execution!**

### Built-in OpenTelemetry

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

No custom hooks needed for basic telemetry.

---

## Evidence Gaps

1. **No direct "skill invocation" event** - Hooks fire on tools, not skill activation
2. **Custom event emission** - Must write to files or use scripts, no direct API
3. **RaiSE-specific events** - Gate validation, kata completion need custom implementation

---

*Evidence catalog complete*
