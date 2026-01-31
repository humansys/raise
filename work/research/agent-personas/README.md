# Agent Personas Research

> Do situated personas improve AI agent performance?

**Status**: Complete
**Date**: 2026-01-31
**Research ID**: RES-PERSONA-001

---

## Question

From parking lot: "Are agent personas really needed for katas? Or is this unnecessary complexity?"

## Answer

**No.** Personas are unnecessary for RaiSE katas.

- Simple persona prompts don't improve accuracy on procedural tasks
- Personas help with creative/style tasks, which katas are not
- No reliable heuristic exists for choosing effective personas
- Focus on clear instructions + validation gates instead

## Documents

| Document | Purpose |
|----------|---------|
| `persona-research-report.md` | Full findings and recommendation |
| `sources/evidence-catalog.md` | 12 sources with evidence ratings |

## Key Evidence

- 2,410+ question study **reversed conclusions** — personas don't help accuracy
- "Idiot" persona outperformed "genius" on MMLU (paradox)
- 10% improvement possible only with sophisticated two-stage approaches

## Decision

Do NOT add persona field to kata schema. Document rationale.

---

*Research conducted using tools/research kata with ddgr CLI (Inference Economy)*
