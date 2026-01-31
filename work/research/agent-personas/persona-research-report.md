# Agent Personas Research Report

**Research ID**: RES-PERSONA-001
**Date**: 2026-01-31
**Status**: Complete
**Confidence Level**: HIGH
**Reading Time**: ~8 minutes

---

## TL;DR

- **Simple persona prompts do NOT improve accuracy** on factual/procedural tasks (HIGH confidence)
- **Personas DO help** with creative writing, tone, style, and guardrails (HIGH confidence)
- **For RaiSE katas**: Personas are unnecessary complexity — katas are procedural, not creative
- **Recommendation**: Don't require personas in katas; focus on clear instructions and validation gates

---

## Research Question(s)

**Primary**: Do situated personas improve AI agent performance in structured task execution?

**Secondary**:
- When do personas help vs. hurt LLM performance?
- Should RaiSE katas include agent persona definitions?
- What's the evidence quality for persona effectiveness claims?

**Decision Context**: Whether RaiSE katas should require or recommend agent personas as part of their definition schema.

---

## Methodology

**Scope**: Academic papers, industry benchmarks, and practitioner meta-analyses from 2024-2025
**Sources consulted**: 12 sources (3 Very High, 5 High, 4 Medium evidence level)
**Time invested**: ~2 hours (using ddgr CLI + WebFetch for Inference Economy)
**Limitations**: Most studies test chat/QA tasks, not structured workflow execution

---

## Key Findings

### Finding 1: Simple Persona Prompts Don't Improve Accuracy

Adding "act as an expert X" to prompts does NOT reliably improve performance on factual or reasoning tasks. A major study testing 2,410+ questions across multiple model families **reversed its original conclusions** after broader testing.

**Confidence**: HIGH
**Evidence**: #7, #8, #10, #11 (4 independent sources, including study reversal)

The Jekyll & Hyde study found a paradox: an "idiot" persona **outperformed** a "genius" persona on MMLU questions with GPT-4.

### Finding 2: Personas Help for Style, Not Substance

Personas are effective when the task involves:
- Creative writing and tone
- Communication style alignment
- Safety guardrails in system prompts
- Open-ended generation (not closed-answer)

**Confidence**: HIGH
**Evidence**: #2, #9, #10, #11 (Vanderbilt study shows correlation with task "openness")

### Finding 3: Sophisticated Personas > Simple Prompts

When personas DO help, they require:
- Detailed, comprehensive descriptions (not just "expert in X")
- Multi-stage approaches (role-setting + role-feedback)
- Often auto-generated rather than hand-crafted

The "role immersion method" achieved 10% improvement (53.5% → 63.8% on math), but required a two-stage prompt architecture.

**Confidence**: MEDIUM
**Evidence**: #6, #10, #11

### Finding 4: No Reliable Heuristic for Persona Selection

Even when personas occasionally help, "no consistent strategy emerged for choosing the best persona." Domain alignment (lawyer for legal, doctor for medical) had "only minor impact on performance."

**Confidence**: HIGH
**Evidence**: #8, #11

### Finding 5: Persona Consistency ≠ Task Performance

Research on persona consistency (self-awareness, robustness, individuality) is separate from task accuracy research. An agent can maintain a consistent persona while performing no better on tasks.

**Confidence**: MEDIUM
**Evidence**: #3, #4

---

## Patterns & Insights

### The Persona Paradox

Industry belief: "Personas make agents better"
Empirical evidence: "Personas make agents different, not necessarily better"

This gap exists because:
1. Personas DO change outputs (observably different)
2. Different ≠ more accurate
3. Confirmation bias in practitioner experience

### Task Type Matters Most

| Task Type | Persona Effect | RaiSE Relevance |
|-----------|----------------|-----------------|
| Creative/style | Positive | Low (katas are procedural) |
| Open-ended | Slight positive | Low |
| Factual/reasoning | Neutral to negative | Medium |
| Procedural/structured | Unknown (understudied) | HIGH |

### What Modern LLMs Already Have

Newer models (GPT-4, Claude 3+) have strong baseline instruction-following. The marginal value of personas has decreased as model capabilities increased.

---

## Gaps & Unknowns

- **Procedural task execution**: Most studies test QA/chat, not workflow execution like katas
- **Long-context consistency**: Does persona help maintain consistency across long workflows?
- **Escalation behavior**: Could personas improve knowing when to ask for help?

---

## Recommendation

**Decision**: Do NOT require personas in RaiSE katas

**Confidence**: HIGH

**Rationale**:
1. Katas are procedural/structured tasks — the category where personas show no benefit
2. No reliable heuristic exists for choosing effective personas
3. Adding persona requirements increases kata complexity without evidence of value
4. Modern LLMs follow clear instructions well without persona framing

**Alternative Approach**:
- Focus kata design on clear steps, validation gates, and Jidoka patterns
- If style consistency matters (e.g., commit message tone), use explicit style instructions rather than personas
- Allow optional "voice" configuration for user-facing output, not as a performance mechanism

**Trade-offs**:
- Accepting: May miss potential benefits in edge cases
- Gaining: Simpler kata schema, less maintenance, no false confidence from personas

**Risks**:
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Edge case where persona helps | Low | Low | Can add optional persona field later if evidence emerges |
| Community expects personas | Medium | Low | Document rationale; evidence-based decisions > convention |

---

## Next Steps

- [ ] Update parking lot: Mark persona question as RESOLVED
- [ ] Do NOT add persona field to kata schema
- [ ] Document this research in framework governance
- [ ] Consider "style instructions" pattern for tone-sensitive outputs

---

## References

- Evidence Catalog: `sources/evidence-catalog.md`
- Related: Parking lot item "Are agent personas really needed for katas?"
- Constitution: §7 Lean Software Development (eliminate waste)

---

*Generated via tools/research kata*
*Research method: ddgr CLI + WebFetch (Inference Economy compliant)*
