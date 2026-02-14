# Decision Log: S19.1 — Consolidate Research into Decisions

> **Story:** S19.1
> **Date:** 2026-02-13
> **Participants:** Emilio + Rai
> **Input:** RES-V3-TIERS §8 (5 open questions)
> **Status:** Complete — all 5 questions resolved

---

## Q1: One Rai per Project vs Multiple Instances?

**Decision:** Hybrid framing — conceptually one Rai per project, technically multiple instances that sync.

**Rationale:** The git analogy is exact: one repo (project memory), many clones (developer instances), sync via push/pull. Rai is one entity per project with multiple runtime instances. This gives Marketing a simple story ("your team's Rai gets smarter with every session") while Engineering builds honest sync infrastructure.

**Evidence:** ADR-013 (Rai as Entity), ADR-015 (dual-backend memory), RQ3 (sync engine is critical path)

**Affects:** S19.3 (ADR-026 sync protocol framing), E20 (shared memory architecture)

---

## Q2: Per-Project Pricing Component?

**Decision:** Deferred — launch with pure per-user pricing ($79/user/mo PRO, $149/user/mo ENTERPRISE). Revisit with usage data from design partners.

**Rationale:** No data on how many projects customers will run. First 3 customers are design partners at 50% discount — their usage patterns will inform whether per-project pricing captures meaningful value. Per-user is the industry norm and easiest to sell. Adding pricing complexity before launch is premature optimization.

**Evidence:** RQ1 (per-user is standard), competitive analysis (Copilot, GitLab, Continue all per-user)

**Affects:** S19.2 (tier doc uses pure per-user pricing), Marketing Rai (simple pricing page)

---

## Q3: Trial Model?

**Decision:** COMMUNITY is the trial. No separate trial mechanism. Upgrade when team needs shared intelligence.

**Rationale:** COMMUNITY is already free forever with full CLI, all 20 skills, and local memory. The upgrade trigger is natural: "I need my team to share what Rai learns." No trial infrastructure to build. No urgency hacks. The product sells itself bottom-up. Design partners skip this entirely (PRO from day 1 at 50%). If conversion proves too slow later, time-limited PRO trials can be added without architecture changes.

**Evidence:** RQ2 (BYOK trending, developer tools converge on free tier + paid team features), current tier model already supports this

**Affects:** S19.2 (no "trial" section needed — just COMMUNITY/PRO/ENTERPRISE), Marketing Rai (messaging: "free forever for individuals, upgrade for teams")

---

## Q4: INVEX On-Prem Timeline?

**Decision:** Design for on-prem in ADRs, don't build until INVEX confirms CNBV requirement.

**Rationale:** INVEX is in exploration, not procurement. No confirmed CNBV requirement. S19.3 ADRs (especially ADR-026 hosted infrastructure) should explicitly document how on-prem deployment would work — architecture must not preclude it. BYOK already means inference is local; only the sync/graph layer would need on-prem options. If INVEX confirms, scope a focused E22 story and adjust roadmap.

**Evidence:** RQ4 (CNBV may require on-prem for financial data, but not confirmed), business context (INVEX in exploration phase)

**Affects:** S19.3 (ADR-026 includes on-prem deployment option in design), S19.5 (roadmap keeps E22 post-March 14 unless confirmed)

---

## Q5: Daniel/Fernando Onboarding Plan?

**Decision:** Hybrid ramp — one parking lot story as onboarding kata, then E21 adapters against BacklogProvider interface contract.

**Rationale:** One safe story teaches the full RaiSE development cycle (branch, implement, test, review, merge). Recommended: "Unified" prefix removal — touches multiple files, requires running tests, can't break anything. After that, E21 adapters against a well-defined `BacklogProvider` interface. Key constraint: S19.3 must define the interface before they start E21.

**Evidence:** E21 architecture (Port/Adapter pattern enables parallel development against contracts), parking lot items (safe ramp-up candidates available)

**Affects:** S19.5 (team allocation: Week 1 onboarding kata, Week 2+ E21 adapters), S19.3 (must include BacklogProvider interface definition)

---

## Summary

| # | Question             | Resolution                                                                 | Type          |
| - | -------------------- | -------------------------------------------------------------------------- | ------------- |
| 1 | One Rai vs multiple? | **Decided:** Hybrid — one entity, multiple instances, git-like sync | Architectural |
| 2 | Per-project pricing? | **Deferred:** Per-user only at launch, revisit with data             | Business      |
| 3 | Trial model?         | **Decided:** COMMUNITY is the trial, no separate mechanism           | Business      |
| 4 | INVEX on-prem?       | **Decided:** Design for it in ADRs, build when confirmed             | Timeline      |
| 5 | Team onboarding?     | **Decided:** One parking lot kata, then E21 adapters                 | Team          |

All 5 questions resolved. S19.2 (tier governance doc) and S19.3 (architecture ADRs) can proceed without ambiguity.
