# Design: S19.1 — Consolidate Research into Decisions

> **Type:** Decision session (governance, not code)
> **Approach:** For each open question: state evidence, propose decision, get human judgment
> **Timebox:** 1 session — decide or defer with rationale, no open-ended discussion

---

## Problem

5 open questions from RES-V3-TIERS §8 block all downstream E19 stories. Without these answers, S19.2 (tier doc) hedges on pricing, S19.3 (ADRs) hedges on architecture, and Marketing Rai can't build the pricing page.

## Value

Closing these questions unblocks the entire V3 decision cascade. Every hour of delay here multiplies across Marketing, Engineering, and Sales.

## Approach

For each question, I will:

1. **Summarize evidence** from RQ1-RQ4
2. **Present options** with trade-offs
3. **Propose a recommendation** with rationale
4. **You decide** — accept, modify, or defer with rationale

No new research. We use what RES-V3-TIERS already gathered.

---

## Decision Framework

### Q1: One Rai per project vs multiple Rai instances?

**Evidence basis:** RQ3 (infrastructure), ADR-013 (Rai as Entity), ADR-015 (dual-backend memory)
**Decision type:** Architectural — affects E20 sync design
**Consumers:** S19.3 (ADR-026/027), E20 scope

### Q2: Per-project pricing component?

**Evidence basis:** RQ1 (enterprise tiers), pricing strategy from synthesis §5
**Decision type:** Business — affects tier structure and S19.2
**Consumers:** S19.2 (tier governance doc), Marketing Rai

### Q3: Trial model (time-limited, feature-limited, usage-limited)?

**Evidence basis:** RQ2 (AI dev tools market), competitive analysis
**Decision type:** Business — affects marketing messaging and onboarding flow
**Consumers:** S19.2, Marketing Rai (website copy)

### Q4: INVEX on-prem timeline — does CNBV force E22 forward?

**Evidence basis:** RQ4 (enterprise adoption, CNBV banking regs)
**Decision type:** Timeline — affects critical path and S19.5
**Consumers:** S19.5 (roadmap), E22 scope

### Q5: Daniel/Fernando onboarding plan

**Evidence basis:** Current parking lot items, V2 polish needs
**Decision type:** Team allocation — affects S19.5
**Consumers:** S19.5 (roadmap, team allocation)

---

## Acceptance Criteria

**MUST:**

- Each question has exactly one of: decision, deferral-with-rationale, or experiment-proposal
- Each decision traces to specific RQ evidence (not opinion)
- Output is a decision log (`decisions.md`) that S19.2/S19.3 can reference directly

**MUST NOT:**

- Open new research threads (use existing evidence only)
- Leave any question without a resolution status
