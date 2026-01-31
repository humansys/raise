# Research Synthesis: AI Research Prompt Structuring

> Triangulated findings from 20 sources (7 Very High, 8 High, 5 Medium evidence)
> Date: 2026-01-31

---

## Major Claims (Triangulated)

### Claim 1: Structured Prompts Improve Research Quality

**Confidence**: HIGH
**Evidence**:
1. [The Prompt Report](https://arxiv.org/abs/2406.06608) - Taxonomy of 58 techniques with standardized vocabulary
2. [Systematic Survey](https://arxiv.org/abs/2402.07927) - Five hierarchical prompting strategies
3. [Reliable Task Flows](https://www.nature.com/articles/s41598-025-19170-9) - Structured prompts improve reliability with robust evaluation
4. [Structured Prompts for Consistency](https://ubiai.tools/ensuring-consistent-llm-outputs-using-structured-prompts-2/) - Numbered lists/bullets facilitate modifications and enhance performance
5. [Prompt Structure Fundamentals](https://learnprompting.org/docs/basics/prompt_structure) - Combining instructions + context + input + output indicators

**Disagreement**: None found
**Implication**: Research prompt template should enforce structural elements

---

### Claim 2: Epistemological Rigor Requires Human-AI Collaboration

**Confidence**: HIGH
**Evidence**:
1. [Hybrid Framework](https://link.springer.com/article/10.1007/s11301-025-00522-8) - Framework anchored in transparency, validity, reliability with robust human oversight
2. [Statistical Reasoning](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1658316/full) - Performance assessment becomes epistemological, not just technical
3. [Clinical Research Optimization](https://pmc.ncbi.nlm.nih.gov/articles/PMC11444847/) - Transparent reporting of prompting methods crucial; separate optimization from test data
4. [1,500+ Papers Analysis](https://aakashgupta.medium.com/i-spent-a-month-reading-1-500-research-papers-on-prompt-engineering-7236e7a80595) - Rigorous testing matters more than clever techniques

**Disagreement**: None found
**Implication**: Research kata should mandate human review gates; AI generates, human validates

---

### Claim 3: Two-Step/Iterative Approaches Outperform Single-Pass

**Confidence**: HIGH
**Evidence**:
1. [Evidence Triangulator](https://www.nature.com/articles/s41467-025-62783-x) - Two-step extraction (concepts first, then relations) F1=0.86 vs one-step
2. [Hybrid Framework](https://link.springer.com/article/10.1007/s11301-025-00522-8) - Iterative prompt engineering with feedback loops
3. [Clinical Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC11444847/) - Iterative optimization separate from test evaluation

**Disagreement**: None found
**Implication**: Research workflow should include: Frame → Execute → Refine → Validate cycles

---

### Claim 4: Hierarchical Delegation Patterns Enable Specialization

**Confidence**: HIGH
**Evidence**:
1. [LLM Agents Guide](https://www.promptingguide.ai/research/llm-agents) - Agent patterns for delegation and orchestration
2. [Multi-Agent Patterns ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - "Agents as Tools" pattern; hierarchical delegation with LLM-driven routing
3. [Palantir Best Practices](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering) - Separation of concerns; hierarchical delegation with clear chain of command
4. [Agentic AI Patterns](https://research.aimultiple.com/agentic-ai-design-patterns/) - Dispatcher pattern routes to specialist agents

**Disagreement**: None found
**Implication**: Research kata should define orchestrator → specialist agent pattern

---

### Claim 5: Clear Agent Descriptions Critical for Routing Decisions

**Confidence**: MEDIUM
**Evidence**:
1. [Multi-Agent Patterns ADK](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) - AutoFlow relies on agent descriptions for delegation
2. [Palantir Best Practices](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering) - Crystal-clear docstrings critical; LLM uses these for tool selection

**Disagreement**: None found
**Limitation**: Only 2 sources (need 3+ for HIGH confidence)
**Implication**: Research prompt template should include agent capability descriptions

---

### Claim 6: Role-Based Prompting Improves Task-Specific Performance

**Confidence**: MEDIUM
**Evidence**:
1. [Systematic Survey](https://arxiv.org/abs/2402.07927) - Role-Based prompting as complexity level
2. [Role Prompting Guide](https://learnprompting.org/docs/advanced/zero_shot/role_prompting) - Role assignment improves performance
3. [AI Research Strategies](https://www.qualtrics.com/articles/strategy-research/ai-research-strategies/) - Specialist framing for validation tasks

**Disagreement**: None found
**Implication**: Research prompt should assign "Research Specialist" role with epistemological responsibilities

---

### Claim 7: Transparency and Reproducibility Are Foundational

**Confidence**: HIGH
**Evidence**:
1. [Hybrid Framework](https://link.springer.com/article/10.1007/s11301-025-00522-8) - Anchored in transparency and comprehensiveness
2. [Clinical Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC11444847/) - Transparent reporting of methods crucial
3. [Systematic Reviews](https://pmc.ncbi.nlm.nih.gov/articles/PMC11143948/) - Reproducibility essential for validation
4. [Research Kata Foundation](../../../.raise/katas/tools/research.md) - Reproducibility principle already embedded

**Disagreement**: None found
**Implication**: Research outputs must include: prompt used, tool/model, timestamp, sources

---

### Claim 8: Triangulation via Multiple Sources Minimizes Bias

**Confidence**: HIGH
**Evidence**:
1. [AI Research Strategies](https://www.qualtrics.com/articles/strategy-research/ai-research-strategies/) - Cross-validation from multiple sources increases reliability
2. [Evidence Triangulator](https://www.nature.com/articles/s41467-025-62783-x) - Systematic extraction across study designs
3. [Triangulation Methods](https://insight7.io/types-of-triangulation-in-qualitative-research-methods/) - Multiple types enhance validity
4. [Research Kata](../../../.raise/katas/tools/research.md) - 3+ sources per major claim

**Disagreement**: None found
**Implication**: Research prompt must explicitly require multi-source validation

---

## Patterns & Paradigm Shifts

### Pattern 1: Structured Prompt Anatomy

**Convergent structure across sources:**
```
Role Definition
  ↓
Task Context (what decision this informs)
  ↓
Instructions (what to find, how to evaluate)
  ↓
Output Format (how to structure findings)
  ↓
Quality Criteria (evidence levels, triangulation requirements)
```

**Sources**: 1, 2, 3, 14, 18
**Confidence**: HIGH

---

### Pattern 2: Hierarchical Delegation Architecture

**Convergent architecture:**
```
Orchestrator (human or primary agent)
  ↓
Research Specialist Agent (search + extract)
  ↓
Synthesis Agent (triangulate + analyze)
  ↓
Validation Gate (human review)
```

**Sources**: 9, 10, 11, 12
**Confidence**: HIGH

---

### Pattern 3: Iterative Refinement Cycle

**Convergent workflow:**
```
1. Frame question → 2. Execute search → 3. Evaluate results
         ↑                                        ↓
         └──────────── 4. Refine prompt ─────────┘
```

**Sources**: 3, 4, 15
**Confidence**: HIGH

---

### Paradigm Shift: Research as Code

**Observation**: Multiple sources treat research prompts as versioned, testable artifacts:
- Separate optimization from test data (Source 15)
- Transparent reporting of methods (Sources 3, 15, 17)
- Reproducibility as requirement (Sources 3, 17)

**RaiSE Alignment**: "Governance as Code" principle applies to research methodology
**Implication**: Research prompts should be versioned in Git, referenced in ADRs

---

## Gaps & Unknowns

### Gap 1: Tool Availability Variance

**Issue**: No standard toolchain for research delegation
**Evidence**: Experiential (ddgr failed, llm not installed, WebSearch succeeded)
**Consequence**: Research kata must account for fallback strategies
**Recommendation**: Tiered approach (ddgr → perplexity → WebSearch → manual)

---

### Gap 2: RaiSE-Specific Research Patterns

**Issue**: General prompt engineering research exists; RaiSE governance context novel
**Evidence**: Zero sources address governance-driven research workflows
**Consequence**: Must synthesize general patterns + RaiSE principles
**Recommendation**: Create RaiSE research prompt template from first principles + evidence

---

### Gap 3: Comparative Tool Evaluations

**Issue**: Limited empirical comparisons of research tools (perplexity vs SearchGPT vs WebSearch)
**Evidence**: Sources discuss patterns but not tool performance
**Consequence**: Can't definitively recommend one tool over another
**Recommendation**: Document tool selection rationale; allow user override

---

### Gap 4: Evidence Level Calibration for Code/Engineering

**Issue**: Evidence levels well-defined for academic research, less so for engineering contexts
**Evidence**: Medical research standards (Sources 5, 15) don't map to GitHub repos, engineering blogs
**Consequence**: Need engineering-specific evidence hierarchy
**Recommendation**: Adapt research kata evidence levels for software engineering domain

---

## Contested Claims

**None identified.** All major claims show convergent evidence across independent sources.

---

## Confidence Calibration

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|----------------|------------|
| Structured prompts improve quality | 5 | Very High + High | HIGH |
| Human-AI collaboration required | 4 | Very High | HIGH |
| Two-step approaches outperform | 3 | Very High | HIGH |
| Hierarchical delegation enables specialization | 4 | High | HIGH |
| Clear descriptions critical for routing | 2 | High | MEDIUM |
| Role-based prompting improves performance | 3 | Mixed | MEDIUM |
| Transparency/reproducibility foundational | 4 | Very High + High | HIGH |
| Triangulation minimizes bias | 4 | High + Medium | HIGH |

**Overall Research Quality**: HIGH (75% of claims at HIGH confidence, 25% at MEDIUM)

---

## Key Takeaways

1. **Prompt Structure Matters**: Instructions + Context + Output Format + Quality Criteria
2. **Human Oversight Non-Negotiable**: AI generates, human validates against epistemological standards
3. **Iterative > Single-Pass**: Frame → Execute → Refine → Validate
4. **Delegation Hierarchy**: Orchestrator → Specialist agents with clear role definitions
5. **Reproducibility Essential**: Version prompts, log tools/models, timestamp outputs
6. **Triangulation Required**: 3+ independent sources per major claim
7. **Tool Flexibility**: Support ddgr → perplexity → WebSearch fallback chain

---

*Synthesis completed: 2026-01-31*
*Next: Formulate recommendation for research prompt template*
