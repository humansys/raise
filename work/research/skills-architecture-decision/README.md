# Research: Skills Architecture Decision

> **Status**: Complete - Awaiting Approval
> **Date**: 2026-01-31
> **Decision**: Migrate katas to Skills format (Option 3)

---

## 5-Minute Summary

### Question

Should RaiSE use Skills as an interface layer (Option 2) or migrate katas entirely to Skills format (Option 3)?

### Answer

**Migrate to Skills format (Option 3)** — RaiSE provides governance FOR Claude Code, not a competing executor.

### Strategic Insight

```
RaiSE is NOT a competing agentic runtime.
RaiSE IS a governance layer that teaches Claude Code how to work.
```

This means:
- **Claude Code** = Executor (runs inference)
- **RaiSE Skills** = Methodology (how to work)
- **raise-cli** = Developer tooling (scaffolding, validation, telemetry aggregation)

### Why Skills?

1. **Native format** — Claude Code already understands Skills
2. **No competition** — Augments Claude Code instead of replacing it
3. **Single source of truth** — No sync between katas and skills
4. **Industry standard** — Works with 25+ platforms (Copilot, Codex, etc.)

---

## Architecture (Clarified)

```
┌─────────────────────────────────────────────────┐
│              Claude Code (Rai)                   │
│                                                  │
│   ┌──────────────────────────────────────────┐  │
│   │           RaiSE Skills                    │  │
│   │  Methodology + Gates + Guardrails         │  │
│   └──────────────────────────────────────────┘  │
│                      │                          │
│                      ▼                          │
│              Claude's Inference                 │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              raise-cli (Tooling)                │
│                                                 │
│   - Scaffolding (raise init, raise skill new)  │
│   - Validation (raise gate check)              │
│   - Telemetry (aggregation, not collection)    │
└─────────────────────────────────────────────────┘
```

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Skills format for katas | Claude Code's native format |
| raise-cli is NOT agentic | Doesn't compete with Claude Code |
| Telemetry from Claude Code hooks | Native integration |
| `metadata.raise.*` namespace | RaiSE extensions without spec violation |
| Gates inline or as skills | Flexible validation |

---

## Artifacts

| File | Purpose |
|------|---------|
| [prompt.md](prompt.md) | Research prompt |
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | 18 sources with evidence levels |
| [synthesis.md](synthesis.md) | 5 triangulated claims |
| [recommendation.md](recommendation.md) | Full decision + implementation plan |

---

## Next Steps (After Approval)

1. Create ADR documenting this decision
2. Define `metadata.raise.*` namespace convention
3. Pilot: Convert `tools/research` kata to skill
4. Validate skill invocation in Claude Code
5. Incremental migration of remaining katas

---

## Governance Link

**This research informs**: ADR for RaiSE Skills architecture

---

*Research completed via tools/research kata*
*Researcher: Rai (Claude Opus 4.5)*
*Architecture clarification: Emilio (2026-01-31)*
