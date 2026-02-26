# Research: Rovo Agent Action Design Patterns

| Field | Value |
|-------|-------|
| **Date** | 2026-02-25 |
| **Depth** | Quick scan (11 sources) |
| **Context** | E275 Shared Memory Backend — API surface design for Rovo consumption |
| **Decision** | How to structure FastAPI endpoints so Forge actions can expose them cleanly to Rovo agents |

## Navigation

| File | Purpose |
|------|---------|
| `sources/evidence-catalog.md` | All sources with evidence levels and key findings |
| `rovo-actions-report.md` | Synthesis with triangulated claims, patterns, and recommendations |

## Key Takeaway

Rovo actions are thin wrappers around Forge functions. The action manifest (name, description, actionVerb, inputs) is the AI-facing contract — Rovo uses it to decide *when* to call an action and *how* to fill parameters. Our FastAPI endpoints should mirror this: verb-aligned routes, minimal required parameters, return only essential fields, and descriptions written for LLM comprehension.
