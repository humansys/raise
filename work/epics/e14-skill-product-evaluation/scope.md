# Epic E14: Skill Product Evaluation — Scope

> **Status:** IN PROGRESS
> **Jira:** [RAISE-1006](https://humansys.atlassian.net/browse/RAISE-1006)
> **Capability:** C1 (Skill Engine) — RAISE-795
> **Created:** 2026-03-28

## Objective

Evaluate RaiSE skill system maturity from a product perspective against the state of the art. Produce actionable stories that close critical gaps for adoption — respecting the architectural separation of ADR-012 (skills = probabilistic guidance, toolkit/runtime = deterministic enforcement).

**Value:** Transform skills from internally-tested markdown guides into a product with execution guarantees, integrated memory, and defined author/user experience.

## Dimensions

| # | Dimension | Question | Where enforcement lives (ADR-012) |
|---|-----------|----------|-----------------------------------|
| D1 | Runtime Guardrails | What controls prevent skill drift? | rai-agent runtime (governance hooks, max_turns, permissions) |
| D2 | Neuro-symbolic Memory | Is graph/memory default or opt-in? | rai-agent runtime (context injection) + skill steps (manual query) |
| D3 | Structural Poka-yoke | Does skill structure prevent errors by design? | ADR-040 contract (structure) + runtime (input/output validation) |
| D4 | Deterministic Execution | Are deterministic execution guardrails complete? | CLI toolkit (deterministic data) + governance hooks (assertions) |
| D5 | Author Experience | How easy is it to create/modify a skill? | /rai-skill-create + rai skill scaffold + ADR-040 + validate |
| D6 | User Experience | Does the user understand and see value quickly? | Skill content (onboarding, feedback) + CLI UX |

## Scoring Rubric

| Score | Label | Criteria |
|:-----:|-------|----------|
| 0 | Absent | Dimension not addressed at all |
| 1 | Informal | Addressed in markdown/comments but no enforcement |
| 2 | Partial | Some enforcement exists (CLI gates, manual checks) |
| 3 | Systematic | Runtime enforcement, validated, observable |

## Stories

| ID | Story | Size | Status | Description | Deps |
|----|-------|:----:|:------:|-------------|------|
| S14.1 | Skill Inventory & Dimension Scorecard | M | Pending | Audit 35 skills × 6 dimensions, produce scorecard, identify patterns/outliers | — |
| S14.2 | Gap Analysis & Story Generation | M | Pending | Synthesize scorecard + research + gemba → prioritized gap map → create Jira stories for v3.x | S14.1 |
| S14.3 | Skill Runtime Orchestration Proposal | S | Pending | ADR proposal for pre/execute/post skill orchestration in rai-agent (hooks, memory injection, output validation) | S14.1 |
| S14.4 | Free/PRO Skill Classification | S | Pending | Define criteria, classify 35 skills, document for RAISE-621 (PRO Licensing) | S14.1 |
| S14.5 | Sync raise-commons Assets | XS | Pending | Sync /rai-skill-create, ADR-040, validate tooling from raise-commons to rai | — |

**Total:** 5 stories (~16 SP estimated: 3+3+2+2+1)

## Architectural Context

| Decision | Source | Impact |
|----------|--------|--------|
| ADR-012: Skills + CLI Toolkit | raise-commons | Determinism from runtime/CLI, not markdown. Evaluate accordingly |
| ADR-024: Deterministic Session Protocol | raise-commons | Context assembly is deterministic; skill interpretation is not |
| ADR-040: Skill Contract | raise-commons | 7-section structural contract exists; behavior contract missing |
| Governance hooks (RAISE-1007) | rai-agent | Biggest quick win — existing enforcement disabled by SDK bug |
| `invoke_structured()` | rai-agent | Typed output pattern exists, not used in skill orchestration |

## Research Grounding

- **Report:** `work/epics/e14-skill-product-evaluation/research-deterministic-harnesses.md`
- **Sources:** 42 (academic papers, frameworks, production systems)
- **Confidence:** High
- **Key finding:** Field converging on type-safe, schema-driven, validation-gated pipelines. RaiSE's unique advantage is natural language as harness language.

## Scope

**In scope (MUST):**
- Inventory of 35 skills with scorecard (6 dimensions × 0-3 scale)
- Gap analysis grounded in research (42 sources) and gemba findings
- Actionable stories created in Jira, distributed across v3.x
- ADR proposal for skill runtime orchestration
- Free/PRO classification

**In scope (SHOULD):**
- Poka-yoke taxonomy for LLM skills (original contribution, no published taxonomy exists)

**Out of scope (NOT):**
- Implementation of fixes (audit + story creation only)
- Redesign of ADR-012 (probabilistic/deterministic separation preserved)
- Skill composition patterns (LangGraph-style) — deferred to v4.x
- Quantitative maturity scoring framework — deferred (no universal standard yet)

## Done Criteria

- [ ] Scorecard complete: 35 skills × 6 dimensions
- [ ] Gap map prioritized with stories created in Jira
- [ ] ADR proposal for skill runtime orchestration layer
- [ ] Free/PRO classification documented
- [ ] raise-commons assets synced
- [ ] Retrospective complete

## Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Scope creep — evaluation becomes redesign | Med | High | Strict: document and create stories, don't implement |
| Scoring subjectivity | Med | Med | Rubric defined before auditing (0-3 scale with concrete criteria) |
| raise-commons sync breaks rai | Low | Med | Run `rai skill validate` after sync |
