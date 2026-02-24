---
id: "ADR-040"
title: "Skill Contract — Canonical structure for AI agent skill files"
date: "2026-02-23"
status: "Accepted"
---

# ADR-040: Skill Contract — Canonical Structure for AI Agent Skill Files

## Context

RaiSE has 23 built-in skills implemented as SKILL.md markdown files that instruct LLM agents
step-by-step. These skills grew organically over 3 months without a conscious structural pattern.

A structural audit (SES-270) revealed:
- **35-75% substance ratio** — the rest is bloat (philosophy, duplicate templates, stale refs)
- **Inconsistent sections** across skills (ShuHaRi in 21/23, HITL in 5/23, gates in 2/23)
- **Fractional step numbering** from organic insertion (0.1, 1.5, 4b)
- **Duplicated content blocks** copied across 3+ skills
- **Agent-friendliness scores** ranging from 3/5 to 5/5

Research (RES-SKILL-CONTRACT-001) across 23 sources — Anthropic, OpenAI, ACL/TACL papers,
OWASP, and 5 agent frameworks — converges on a clear finding: **instruction count and
positioning matter more than instruction quality**.

Three forces in tension:
1. Skills must be reliable for LLM agents (compliance, token efficiency)
2. Skills must be readable for human developers (maintainability, onboarding)
3. Skills must be consistent across 23+ files (auditability, shared base)

## Decision

### 1. Seven-section canonical structure, fixed order

Every SKILL.md file follows exactly this structure:

```markdown
# {Skill Name}

## Purpose
One sentence: what this skill does and what success looks like.

## Mastery Levels (ShuHaRi)
≤5 lines. Adapt verbosity per level. No philosophy — just behavior deltas.

## Context
When to use / not use. Inputs required. Prerequisites (gates).
Decision tables for conditional logic, not prose paragraphs.

## Steps
### Step N: {Verb Phrase}
- What to do (affirmative phrasing)
- Verification: how to check this step succeeded
- If blocked: recovery path

## Output
What this skill produces. Where artifacts go. State changes.

## Quality Checklist
Atomic, verifiable items. The last thing the agent reads before finishing.

## References
Links only, no inline content. File paths, ADRs, related skills.
```

**Rationale** (evidence-traced):

| Section | Position | Evidence |
|---------|----------|---------|
| Purpose | Top (primacy zone) | U-shaped attention: >30% accuracy for top-positioned info (Liu et al., TACL 2024) |
| Steps | Middle | Sequential by nature. Compensate with clear headings per step |
| Quality Checklist | Bottom (recency zone) | Recency bias: instructions closest to generation get most attention (Google Research 2024, Anthropic docs) |
| No philosophy section | Removed | Newer models need fewer prompts (Anthropic Claude 4.6 docs, OpenAI GPT-5 guide). "Motivation paragraphs" are counterproductive |
| 7 sections, not 12+ | Fixed | Compliance ≈ p(each)^n. Fewer sections = higher compliance (IFScale 2025) |

### 2. Quantitative targets per skill

| Metric | Target | Current Avg | Rationale |
|--------|--------|-------------|-----------|
| Total lines | ≤150 | 340 | Stay under 3K token degradation threshold (Levy et al., ACL 2024) |
| Discrete rules | ≤15 | ~30-60 | 0.97^15 = 63% full compliance vs 0.95^30 = 21% |
| Substance ratio | ≥80% | 35-75% | Semantically similar noise is worse than random (MLOps Community/GSM-IC) |
| Examples | 1-2 per skill | 0-5 | "Pictures worth 1000 words" (Anthropic). >5 counterproductive (Few-shot Dilemma, 2025) |
| Negative phrases | ≤3 per skill | Uncounted | Affirmative > negative (Anthropic, Elements.cloud) |

### 3. Content principles

**Affirmative over negative.** Write "do X when Y" instead of "don't do X." Reserve "NEVER"
for true safety guardrails (≤3 per skill), positioned in the Quality Checklist (recency zone).

**Decision tables over prose conditionals.** Any branching logic expressed as markdown tables
or numbered lists, not nested if-else paragraphs. Structured formats improve conditional
reasoning accuracy (Code Prompting, arxiv 2024).

**Examples over rules.** One well-chosen input/output example replaces 10-20 lines of rules.
Place examples inside the relevant Step, wrapped in a clear delimiter. Max 2 per skill.

**Atomic instructions.** Each rule is one verifiable statement. Compound instructions
("do X, Y, and Z in format W") become 4 potential failure points. The dominant failure
mode is omission, not misinterpretation (IFScale 2025: 34.88x omission-to-modification ratio).

**Consistent terminology.** One term per concept across all skills. If "story", "task", and
"work item" refer to the same thing, pick one. Inconsistency fragments the agent's model
of the instruction set (Elements.cloud production analysis).

### 4. Shared base for cross-cutting content

Content appearing in 3+ skills is extracted into a shared base loaded once per session,
not duplicated across files:

| Content | Extraction Target |
|---------|------------------|
| ShuHaRi adaptation rules | Shared preamble (3-line reference in each skill) |
| Gate checking logic | Gate engine (ADR-039). Skill declares prerequisites only |
| Commit discipline | Post-step hook. Not repeated in skill content |
| Session context loading | Shared step template, parameterized per skill |

**Token savings estimate**: ~30 duplicated lines × 23 skills = ~690 lines removed.
At 3-5 tokens/line = 2,000-3,500 tokens saved per session.

### 5. Hybrid markdown + XML for critical boundaries

Markdown headers for human readability. Selective XML tags at semantic boundaries where
agent parsing reliability is critical:

```markdown
## Steps

### Step 1: Load Context

<verification>
- [ ] Context bundle loaded
- [ ] Session state accessible
</verification>

<if-blocked>
Run `rai graph build` first, then retry.
</if-blocked>
```

**Rationale**: XML provides stronger section boundaries than markdown (~30% quality
improvement for complex inputs, Anthropic docs). Markdown saves ~15% tokens (OpenAI
Community analysis). The hybrid captures both benefits.

## Consequences

**Positive:**
- Predictable structure across all 23 skills → easier auditing and automated validation
- ≤150 lines target keeps skills under cognitive and token degradation thresholds
- Shared base eliminates ~690 lines of duplication
- Evidence-based positioning (primacy/recency) maximizes instruction compliance
- Fixed section count enables `rai skill validate` to check contract compliance

**Negative:**
- Refactoring 23 skills is significant effort (mitigated by compounding pattern: PAT-E-442)
- Less self-documenting for new human readers (mitigated by external reference docs)
- Prescriptive structure may feel constraining for novel skill types (mitigated by References
  section linking to supporting material)

**Risks:**
- Over-compression may lose critical nuance → pilot on 1 skill first, measure compliance
- Model-specific recommendations (XML for Claude) may not generalize → hybrid approach covers
  multi-model (all models parse markdown well; XML adds boundaries for Claude-primary usage)

## References

- Research: `work/research/skill-contract/skill-contract-report.md` (RES-SKILL-CONTRACT-001)
- Evidence catalog: `work/research/skill-contract/sources/evidence-catalog.md` (23 sources)
- Structural audit: SES-270 conversation context
- ADR-039: Lifecycle Hooks & Workflow Gates (shared base via hooks)
- ADR-012: Skills Toolkit Architecture (original skills format)
- PAT-E-442: Extraction compounding (refactoring velocity pattern)
