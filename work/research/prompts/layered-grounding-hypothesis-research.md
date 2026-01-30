---
id: layered-grounding-hypothesis-research
title: "Research Prompt: Layered Grounding Hypothesis for AI Agent Behavior"
date: 2026-01-30
status: ready
type: first-principles-research
hypothesis: "Effective AI agent grounding requires a layered model: Principles → Architecture → Guardrails"
output_expected: specs/main/research/outputs/layered-grounding-analysis.md
related_to: ["ADR-009", "kata-harness-design", "continuous-governance-model"]
---

# Research Prompt: Layered Grounding Hypothesis for AI Agent Behavior

## Executive Context

RaiSE is designing a governance model for AI coding agents. A fundamental design question has emerged:

> **What should ground an AI agent's behavior when working on a codebase?**

Two competing positions exist:

| Position | Claim | Proponents |
|----------|-------|------------|
| **Architecture-First** | Architecture Model should ground the agent | System-specific context enables coherent action |
| **Principles-First** | Principles should ground the agent | Architecture can be wrong; principles are the judge |

**Our hypothesis:** Neither position is complete. Effective grounding requires a **layered model**:

```
PRINCIPLES (Universal, Immutable)
    ↓ constrain + evaluate
ARCHITECTURE (System-Specific, Mutable)
    ↓ ground + contextualize
GUARDRAILS (Actionable, Derived)
    ↓ execute + validate
AGENT BEHAVIOR (Concrete Actions)
```

**Research Goal:** Validate or refute this hypothesis through multi-disciplinary analysis.

---

## Primary Research Questions

### RQ1: Cognitive Science - How Do Expert Architects Reason?

**Question:** Do expert software architects reason primarily from principles (top-down) or from patterns (bottom-up)? Is there a developmental progression?

**Sub-questions:**
- How do novices vs. experts approach architectural decisions?
- What role does pattern recognition play in expert reasoning?
- Do experts "see" principles, or do they see patterns that embody principles?
- How does chunking and expertise development inform this?

**Relevant domains:**
- Cognitive psychology of expertise (Dreyfus model, Klein's naturalistic decision-making)
- Software engineering expertise studies
- Pattern recognition in professional practice

**Expected insight:** Whether human experts use layered reasoning, and if so, how.

---

### RQ2: AI/LLM Agents - What Grounding Produces Better Outcomes?

**Question:** In LLM-based coding agents, does grounding in abstract principles or concrete architectural patterns produce better code quality, consistency, and maintainability?

**Sub-questions:**
- How do current AI coding assistants (Copilot, Cursor, Claude) handle grounding?
- Is there evidence that context-rich prompts (architecture) outperform principle-only prompts?
- How do RAG systems balance retrieved context (concrete) with system prompts (abstract)?
- What does the "prompt engineering" literature say about abstraction levels?

**Relevant domains:**
- LLM prompt engineering research
- AI coding assistant evaluations
- Retrieval-augmented generation (RAG) studies
- Context window utilization studies

**Expected insight:** Empirical evidence on what grounding strategies work for AI agents.

---

### RQ3: Organizational Theory - Espoused vs. In-Use Values

**Question:** Should agents be grounded in espoused values (stated principles) or values-in-use (actual architecture)?

**Sub-questions:**
- What does Argyris's theory of action tell us about this tension?
- When stated principles and actual practice diverge, which should guide new work?
- How do organizations handle the gap between "what we say" and "what we do"?
- Is the codebase the "real" values of the team?

**Relevant domains:**
- Argyris & Schön: Theory of Action, Double-Loop Learning
- Organizational behavior and culture
- Technical debt as values divergence

**Expected insight:** Whether grounding in "what is" (architecture) or "what should be" (principles) is more appropriate.

---

### RQ4: Lean/TPS - Principles and Practices Relationship

**Question:** How does Toyota's relationship between principles (pillars) and practices (tools) inform agent design?

**Sub-questions:**
- How does TPS balance universal principles with context-specific practices?
- What does "understand principles, adapt practices" mean operationally?
- How do Lean practitioners decide when to follow vs. adapt a practice?
- Is there a Shu-Ha-Ri progression in principle/practice application?

**Relevant domains:**
- Toyota Production System literature
- Lean software development (Poppendieck)
- Kata (Mike Rother) - Improvement Kata, Coaching Kata
- Shu-Ha-Ri and mastery progression

**Expected insight:** A model for how principles and practices (architecture) should relate.

---

### RQ5: Philosophy - Symbol Grounding Problem

**Question:** How do abstract principles become concrete actions? What is the grounding mechanism?

**Sub-questions:**
- What is the symbol grounding problem in AI?
- How do humans ground abstract concepts in concrete action?
- Is there a necessary intermediate representation (architecture as "middle layer")?
- What does embodied cognition say about abstraction and action?

**Relevant domains:**
- Philosophy of mind and AI
- Symbol grounding problem (Harnad)
- Embodied cognition
- Pragmatism (Dewey, Peirce) - knowledge as action-oriented

**Expected insight:** Theoretical foundation for why a middle layer (architecture) might be necessary.

---

### RQ6: Software Engineering - Principles, Patterns, Practices Hierarchy

**Question:** What is the relationship between principles (SOLID), patterns (Clean Architecture), and practices (specific code structure)?

**Sub-questions:**
- Are patterns "encoded principles"?
- How do architecture patterns relate to underlying principles?
- What happens when you try to apply principles without patterns?
- Is there a necessary progression: principle → pattern → practice?

**Relevant domains:**
- Software architecture theory
- Design patterns literature (GoF, POSA)
- SOLID principles and their application
- Architecture decision records (ADRs) as principle/context encoding

**Expected insight:** Whether architecture is a necessary intermediary between principles and code.

---

## Hypothesis to Test

### The Layered Grounding Hypothesis

**Statement:**

> Effective AI agent grounding requires three layers:
> 1. **Principles** (universal, immutable) - constrain and evaluate
> 2. **Architecture** (system-specific, mutable) - ground and contextualize
> 3. **Guardrails** (actionable, derived) - execute and validate
>
> Each layer serves a distinct function. Removing any layer produces suboptimal outcomes:
> - Without principles: Agent perpetuates bad patterns
> - Without architecture: Agent lacks context for coherent action
> - Without guardrails: Agent lacks actionable constraints

**Testable predictions:**

| Prediction | How to Test |
|------------|-------------|
| P1: Principles alone are insufficient for action | Find cases where principle-only guidance produces inconsistent results |
| P2: Architecture alone is insufficient for quality | Find cases where following existing patterns perpetuates problems |
| P3: Both together produce better outcomes | Find evidence that layered approaches outperform single-layer |
| P4: The layers have distinct functions | Map each layer to distinct cognitive/operational functions |
| P5: Expert humans use layered reasoning | Evidence from cognitive science that experts use multiple levels |

---

## Counter-Arguments to Address

### Counter-Argument 1: "Principles Should Be Sufficient"

**Claim:** A well-trained agent with good principles should derive correct architecture.

**Questions to explore:**
- Is this true for humans? Can humans derive architecture from principles alone?
- Does this work in greenfield? What about brownfield?
- What is the cognitive/computational cost of deriving vs. retrieving?

### Counter-Argument 2: "Architecture Encodes Principles Already"

**Claim:** If architecture properly embodies principles, you don't need explicit principles.

**Questions to explore:**
- Is all architecture principled? What about legacy/technical debt?
- Can architecture become disconnected from its original principles?
- Does explicit principle reference improve agent reasoning?

### Counter-Argument 3: "Just Use Examples (Few-Shot)"

**Claim:** Instead of principles or architecture, just show examples of good code.

**Questions to explore:**
- Are examples sufficient for novel situations?
- How do examples relate to principles and architecture?
- Is few-shot learning a form of implicit architecture grounding?

### Counter-Argument 4: "The Agent Should Figure It Out"

**Claim:** Modern LLMs have enough world knowledge to reason without explicit grounding.

**Questions to explore:**
- What is the cost of re-deriving context each time?
- How reliable is implicit knowledge vs. explicit grounding?
- What happens when implicit knowledge conflicts with project reality?

---

## Research Methodology

### Phase 1: Literature Review

1. **Cognitive Science**: Expert reasoning, pattern recognition, Dreyfus model
2. **AI/ML**: Prompt engineering, RAG, context utilization
3. **Organizational Theory**: Argyris, espoused vs. in-use values
4. **Lean/TPS**: Principles and practices, Kata, Shu-Ha-Ri
5. **Philosophy**: Symbol grounding, embodied cognition, pragmatism
6. **Software Engineering**: Architecture theory, patterns, SOLID

### Phase 2: Case Analysis

1. **AI Coding Assistants**: How do Copilot, Cursor, Claude handle grounding?
2. **Agent Frameworks**: How do LangChain, CrewAI, AutoGPT approach this?
3. **RaiSE Current State**: What grounding does spec-kit/BMAD use?
4. **Failure Cases**: Examples where single-layer grounding failed

### Phase 3: Synthesis

1. **Evidence Mapping**: What supports/refutes each prediction?
2. **Model Refinement**: Adjust hypothesis based on evidence
3. **Design Implications**: What should RaiSE implement?
4. **Counter-Argument Responses**: Prepare responses to objections

---

## Expected Outputs

### 1. Evidence Matrix

| Prediction | Supporting Evidence | Contradicting Evidence | Confidence |
|------------|--------------------|-----------------------|------------|
| P1 | ... | ... | High/Medium/Low |
| P2 | ... | ... | ... |
| ... | ... | ... | ... |

### 2. Theoretical Model

Refined version of the layered grounding hypothesis with:
- Clear definitions of each layer
- Functions of each layer
- Relationships between layers
- Failure modes when layers are missing

### 3. Design Recommendations

For RaiSE governance model:
- How to implement each layer
- How layers should interact
- How to handle conflicts between layers
- Kata design implications

### 4. Counter-Argument Playbook

For each objection:
- The argument
- The evidence-based response
- Acknowledgment of valid points
- Synthesis position

---

## Output Format

Produce a comprehensive research document:

```markdown
# Layered Grounding Analysis: Principles, Architecture, and Agent Behavior

## Executive Summary
[Key findings, hypothesis validation status, recommendations]

## 1. Cognitive Science Findings
[RQ1 analysis]

## 2. AI/LLM Agent Evidence
[RQ2 analysis]

## 3. Organizational Theory Perspective
[RQ3 analysis]

## 4. Lean/TPS Insights
[RQ4 analysis]

## 5. Philosophical Foundations
[RQ5 analysis]

## 6. Software Engineering Theory
[RQ6 analysis]

## 7. Hypothesis Evaluation
[Evidence matrix, prediction validation]

## 8. Refined Model
[Updated layered grounding model]

## 9. Counter-Arguments Addressed
[Playbook for each objection]

## 10. Design Recommendations for RaiSE
[Specific implementation guidance]

## 11. Open Questions
[What we still don't know]

## References
[Academic and industry sources]
```

---

## Constraints

1. **Academic rigor**: Cite sources, distinguish evidence from speculation
2. **Practical focus**: Keep RaiSE design decisions in view
3. **Intellectual honesty**: If hypothesis is wrong, say so
4. **Balanced perspective**: Steel-man counter-arguments before refuting
5. **Actionable output**: Conclude with concrete recommendations

---

## Success Criteria

The research is successful if it:

1. ✅ Provides clear evidence for/against the layered grounding hypothesis
2. ✅ Addresses all major counter-arguments with evidence
3. ✅ Produces actionable design recommendations for RaiSE
4. ✅ Identifies remaining open questions
5. ✅ Enables confident decision-making on governance model design

---

*Research Prompt Version: 1.0*
*Created: 2026-01-30*
*Context: Kata Harness Design Session - Greenfield Setup*
