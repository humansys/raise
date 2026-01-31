# Evidence Catalog: Agent Personas in LLMs

> Sources consulted for RES-PERSONA-001

---

## Summary

| Metric | Value |
|--------|-------|
| Total sources | 12 |
| Very High evidence | 3 |
| High evidence | 5 |
| Medium evidence | 4 |
| Low evidence | 0 |

---

## Sources by Category

### Academic Papers (Peer-Reviewed)

#### #1: Two Tales of Persona in LLMs: A Survey of Role-Playing and Personalization

**Link**: https://arxiv.org/abs/2406.01171 / https://aclanthology.org/2024.findings-emnlp.969/
**Type**: Primary
**Evidence Level**: Very High (ACL EMNLP 2024, comprehensive survey)
**Date**: 2024

**Key Finding**: First systematic survey of persona in LLMs, covering role-playing (assigning personas to LLMs) and personalization (LLMs handling user personas).

**Relevance**: Provides taxonomic framework for understanding persona applications.

---

#### #2: Evaluating Persona Prompting for Question Answering Tasks

**Link**: https://www.dre.vanderbilt.edu/~schmidt/PDF/Evaluating_Personified_Expert_Effectiveness_Conference.pdf
**Type**: Primary
**Evidence Level**: Very High (Vanderbilt University, empirical study)
**Date**: 2024

**Key Finding**: Single-agent persona prompting shows performance increase "commensurate with increased openness from dataset to dataset" — meaning personas help more on open-ended tasks than closed/factual ones.

**Relevance**: Directly addresses when personas help vs. hurt.

---

#### #3: Enhancing Persona Consistency with Large Language Models

**Link**: https://dl.acm.org/doi/10.1145/3670105.3670140
**Type**: Primary
**Evidence Level**: Very High (ACM peer-reviewed)
**Date**: 2024

**Key Finding**: Fine-tuned models with persona training demonstrated "superior performance over baseline models" for consistency metrics (self-awareness, robustness, individuality).

**Relevance**: Consistency matters more than accuracy for persona effectiveness.

---

#### #4: From prompt to persona: LLMs as single cognitive agents

**Link**: https://link.springer.com/article/10.1007/s12652-025-05029-4
**Type**: Primary
**Evidence Level**: High (Springer, literature review)
**Date**: 2025

**Key Finding**: Reviews whether LLMs can act as "single cognitive agents" with memory, persona, planning, and situatedness. Identifies cognitive agency as distinct from task performance.

**Relevance**: Situatedness and memory are separate from persona effectiveness on tasks.

---

#### #5: Persona Prompting as a Lens on LLM Social Reasoning

**Link**: https://arxiv.org/pdf/2601.20757
**Type**: Primary
**Evidence Level**: High (arXiv preprint, 2025)
**Date**: 2025

**Key Finding**: Persona prompting reveals LLM social reasoning patterns; baseline (no persona) compared to persona-based approaches on demographic reasoning tasks.

**Relevance**: Personas affect social/reasoning patterns, not raw accuracy.

---

### Industry Research & Benchmarks

#### #6: Better Zero-Shot Reasoning with Role-Play Prompting

**Link**: Referenced in PromptHub article
**Type**: Secondary
**Evidence Level**: High (cited empirical study)
**Date**: 2024

**Key Finding**: 10% performance improvement (53.5% → 63.8% on math) using "role immersion method" — a two-stage approach with role-setting and role-feedback prompts.

**Relevance**: Shows personas CAN help, but requires sophisticated multi-stage approach.

---

#### #7: When "A Helpful Assistant" Is Not Really Helpful (Updated)

**Link**: Referenced in PromptHub blog
**Type**: Secondary
**Evidence Level**: High (2,410+ questions tested, multiple model families)
**Date**: 2024 (updated)

**Key Finding**: Original paper supported persona prompting, but **reversed conclusions** after broader testing. "Adding personas in system prompts does NOT improve model performance."

**Relevance**: Critical evidence that simple personas don't help accuracy.

---

#### #8: Jekyll & Hyde Framework Study

**Link**: Referenced in PromptHub blog
**Type**: Secondary
**Evidence Level**: High (GPT-4 testing, paradoxical findings)
**Date**: 2024

**Key Finding**: Minimal performance gap between basic and persona-enhanced prompts. Paradoxically, "idiot" persona outperformed "genius" persona on MMLU.

**Relevance**: Counterintuitive evidence that domain-aligned personas don't guarantee improvement.

---

### Practitioner Sources

#### #9: Role Prompting: Guide LLMs with Persona-Based Tasks (LearnPrompting)

**Link**: https://learnprompting.org/docs/advanced/zero_shot/role_prompting
**Type**: Tertiary
**Evidence Level**: Medium (practitioner documentation)
**Date**: 2024

**Key Finding**: Role prompting "enhances text clarity and accuracy by aligning the response with the role, improving task performance in reasoning and explanation."

**Relevance**: Practitioner view (potentially optimistic bias).

---

#### #10: Role-Prompting: Does Adding Personas Really Make a Difference?

**Link**: https://www.prompthub.us/blog/role-prompting-does-adding-personas-to-your-prompts-really-make-a-difference
**Type**: Secondary
**Evidence Level**: Medium (meta-analysis of papers)
**Date**: 2024

**Key Finding**: "Simple persona prompts rarely help accuracy tasks, especially with newer models. Role prompting remains most effective for creative writing and establishing safety guardrails."

**Relevance**: Synthesized view across multiple studies.

---

#### #11: The Truth About Persona Prompting (PromptHub Substack)

**Link**: https://prompthub.substack.com/p/act-like-a-or-maybe-not-the-truth
**Type**: Secondary
**Evidence Level**: Medium (practitioner meta-analysis)
**Date**: 2024

**Key Finding**: When personas did improve performance, "no consistent strategy emerged for choosing the best persona." Gender-neutral, in-domain roles showed "minimal effect size."

**Relevance**: No reliable heuristic for picking effective personas.

---

#### #12: Building AI Agents with Personas, Goals, and Dynamic Memory

**Link**: https://medium.com/@leviexraspk/building-ai-agents-with-personas-goals-and-dynamic-memory-6253acacdc0a
**Type**: Tertiary
**Evidence Level**: Medium (practitioner article)
**Date**: 2024

**Key Finding**: Personas, goals, and memory are "foundational" for AI agents — but conflates architectural components with prompting techniques.

**Relevance**: Industry belief vs. empirical evidence distinction.

---

## Cross-Reference Matrix

| Claim | Sources (by #) | Confidence |
|-------|----------------|------------|
| Personas don't improve accuracy on factual tasks | #7, #8, #10, #11 | HIGH |
| Personas help with creative/style tasks | #2, #9, #10, #11 | HIGH |
| Sophisticated personas > simple "act as X" | #6, #10, #11 | MEDIUM |
| Consistency ≠ accuracy improvement | #3, #4 | MEDIUM |
| No reliable heuristic for persona selection | #8, #11 | HIGH |

---

## Contrary Evidence

| Claim | Contrary Source | Resolution |
|-------|-----------------|------------|
| Personas improve performance | #6 shows 10% improvement | Only with sophisticated two-stage approach, not simple prompts |
| Domain-aligned personas help | #8 shows "idiot" > "genius" | Domain alignment is not the key variable |

---

*Generated via tools/research kata*
*Research method: ddgr CLI + WebFetch synthesis*
