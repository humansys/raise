# E1131: Adapter Reliability — Telemetry, Degradation, Error Messages

## Objective

Make adapters observable, resilient, and user-friendly when things go wrong.
An adapter that fails silently or with a traceback is worse than one that
explains what happened and how to fix it.

## Context

- ADR-015: scoped to 1 session, 1 worktree
- Depends on RAISE-1130 (doctor must exist for error messages to reference it)
- Depends on RAISE-1052 (new Jira adapter for degradation logic)
- Partial work: ACLI adapter has logfire spans (E494), needs generalization

## Design Decisions

1. **Telemetry is adapter-level, not call-level** — one span per adapter operation, not per subprocess/HTTP call
2. **Degradation is opt-in per protocol** — PM adapter degrades to filesystem; docs adapter does not (no filesystem PM equivalent for docs)
3. **Error messages reference doctor** — "Run `rai adapter doctor` to diagnose" is the standard recovery suggestion
4. **Health check at session start** — non-blocking, warning only

## Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S1131.1 | Generalized Adapter Telemetry | S | Structured event per adapter operation: operation, duration, success/failure, backend. All adapters, not just ACLI. |
| S1131.2 | Graceful Degradation | M | PM adapter: Jira fail → Filesystem fallback with warning. Docs adapter: fail with actionable message. |
| S1131.3 | Human Error Messages | S | Replace tracebacks with actionable messages. Reference `rai adapter doctor` for config issues. |
| S1131.4 | Session-Start Health Check | S | `rai session start` checks adapter health. Warning if unhealthy, not blocking. |

## Dependencies

```
RAISE-1052 (Jira transport) ──┐
                               ├──→ S1131.1 (Telemetry)
RAISE-1130 (Self-Service) ────┤     S1131.2 (Degradation) ← needs both adapters
                               │     S1131.3 (Error Messages) ← needs doctor
                               └──→ S1131.4 (Health Check)
```

All stories can run in parallel once both prerequisites are merged.

## Done Criteria

1. All adapter operations emit structured telemetry events
2. `rai backlog search` with Jira down returns filesystem results with warning
3. Config errors show human-readable message + `rai adapter doctor` suggestion
4. `rai session start` reports adapter health status

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Filesystem fallback produces confusing results | Medium | Medium | Clear warning: "Using local fallback — Jira unavailable" |
| Telemetry overhead noticeable on slow connections | Low | Low | Async emit, non-blocking |
