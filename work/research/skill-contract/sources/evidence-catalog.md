# Evidence Catalog: Skill Contract Design

> Research ID: RES-SKILL-CONTRACT-001
> Date: 2026-02-23
> Decision: ADR for Skill Contract (E250)

---

## Primary Sources (Very High Evidence)

### S1: Anthropic — Claude 4 Best Practices

- **URL**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
- **Type**: Primary (vendor documentation)
- **Evidence Level**: Very High
- **Key Findings**:
  - XML tags as primary structuring mechanism: `<instructions>`, `<context>`, `<example>`
  - Sequential steps via numbered lists when order matters
  - Long data at top, query/instructions at bottom → up to 30% quality improvement
  - Role in system prompt makes a difference (even one sentence)
  - 3-5 examples wrapped in `<example>` tags for best results
  - "Golden rule": if a colleague would be confused, Claude will be too
  - Tell what TO do, not what NOT to do
  - Provide "why" behind instructions — Claude generalizes from explanations
  - Over-prompting from older models causes overtriggering in Claude 4.6
  - "Prefer general instructions over prescriptive steps"
  - Explicit "avoid over-engineering" needed (Claude 4.6 tendency)

### S2: Anthropic — Effective Context Engineering for AI Agents

- **URL**: https://anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Type**: Primary (vendor engineering blog)
- **Evidence Level**: Very High
- **Key Findings**:
  - "Right altitude": specific enough to guide, flexible enough for heuristics
  - Avoid extremes: hardcoded if-else (fragile) vs vague guidance (ineffective)
  - "Smallest information set that fully outlines expected behavior" — minimal ≠ short
  - Context is finite with diminishing returns (n² pairwise token relationships)
  - Just-in-time context: lightweight identifiers, load dynamically via tools
  - Progressive disclosure: agents discover context through exploration
  - Examples are "pictures worth a thousand words" — curate diverse canonical examples
  - Minimal, clear toolsets with no overlapping functionality
  - Anti-patterns: exhaustive edge-case lists, bloated tool sets, pre-loading all data

### S3: OpenAI — GPT-4.1 Prompting Guide

- **URL**: https://cookbook.openai.com/examples/gpt4-1_prompting_guide
- **Type**: Primary (vendor documentation)
- **Evidence Level**: Very High
- **Key Findings**:
  - Hierarchy: Role/Objective → Instructions → Sub-categories → Reasoning → Output → Examples → Context
  - Instructions at both beginning AND end of context for long prompts
  - Later instructions override earlier ones when conflicting
  - GPT-4.1 follows literally — demands unambiguous directives
  - Planning between tool calls: +4% success rate
  - Markdown as default, XML for structured data, avoid JSON for documents
  - Over-incentivization (ALL CAPS, bribes) counterproductive
  - Audit failure modes: misunderstood intent, insufficient context, incomplete reasoning

### S4: OpenAI — GPT-5 Prompting Guide

- **URL**: https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide
- **Type**: Primary (vendor documentation)
- **Evidence Level**: Very High
- **Key Findings**:
  - Explicit precedence rules for conflicting directives (waste reasoning tokens otherwise)
  - Order: context gathering → stop conditions → workflow steps as checklist
  - Nested XML subsections for complex domains (mirrors decision trees)
  - "Domain basics" section BEFORE workflows
  - Eagerness calibration: explicit autonomy level control
  - Newer models need FEWER detailed prompts — over-specification counterproductive
  - Contradictory instructions waste reasoning tokens (model tries to reconcile)
  - Metaprompting: use the model to optimize its own prompts

### S5: Lost in the Middle (Liu et al., TACL 2024)

- **URL**: https://arxiv.org/abs/2307.03172
- **Type**: Primary (peer-reviewed, TACL)
- **Evidence Level**: Very High
- **Key Finding**: U-shaped attention — models attend best to beginning and end, worst in middle
- **Data**: >30% accuracy drop for middle-positioned information

### S6: Same Task, More Tokens (Levy et al., ACL 2024)

- **URL**: https://arxiv.org/abs/2402.14848
- **Type**: Primary (peer-reviewed, ACL)
- **Evidence Level**: Very High
- **Key Finding**: Reasoning degrades at ~3,000 tokens, well below context limits
- **Data**: Accuracy dropped 0.92 → 0.68 at 3K tokens. Even relevant padding causes degradation.

### S7: IFScale — How Many Instructions Can LLMs Follow? (2025)

- **URL**: https://arxiv.org/abs/2507.11538
- **Type**: Primary (academic)
- **Evidence Level**: Very High
- **Key Finding**: Best models achieve 68% at 500 instructions. Omission (not misinterpretation) is dominant failure.
- **Data**: Reasoning models maintain near-perfect compliance until ~150 instructions, then cliff. Omission-to-modification error ratio: 34.88x.

### S8: Design Patterns for Securing LLM Agents (2025)

- **URL**: https://arxiv.org/html/2506.08837v1
- **Type**: Primary (academic)
- **Evidence Level**: Very High
- **Key Finding**: Structural separation of data and instructions. Context minimization after parsing.

### S9: OWASP LLM Prompt Injection Prevention

- **URL**: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- **Type**: Secondary (industry standard)
- **Evidence Level**: Very High
- **Key Finding**: Layered defense required. No single technique sufficient.

### S10: Prompt Repetition Improves Non-Reasoning LLMs (Google Research, 2024)

- **URL**: https://arxiv.org/abs/2512.14982
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: Repeating critical constraints at START and END improves compliance (primacy/recency). Do NOT duplicate large blocks in the middle.

---

## Secondary Sources (High Evidence)

### S11: Lakera — Prompt Engineering Guide 2026

- **URL**: https://www.lakera.ai/blog/prompt-engineering-guide
- **Evidence Level**: High
- **Key Finding**: Prompt compression can reduce tokens 40-65% without quality loss. Conflicting instructions are top failure mode.

### S12: Elements.cloud — Agent Instruction Patterns and Anti-Patterns

- **URL**: https://elements.cloud/blog/agent-instruction-patterns-and-antipatterns
- **Evidence Level**: High (production Salesforce analysis)
- **Key Finding**: 10 anti-patterns identified. Negative phrasing confuses agents. Overlapping conditions, inconsistent terminology harm compliance.

### S13: Lilian Weng (OpenAI) — Prompt Engineering

- **URL**: https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/
- **Evidence Level**: High
- **Key Finding**: Examples communicate intent more effectively than rules.

### S14: IFEval (Google, 2023)

- **URL**: https://arxiv.org/abs/2311.07911
- **Evidence Level**: Very High
- **Key Finding**: Standard benchmark for instruction-following. Format/constraint instructions most testable.

### S15: InFoBench (ACL 2024)

- **URL**: https://aclanthology.org/2024.findings-acl.772/
- **Evidence Level**: High
- **Key Finding**: Decomposing complex instructions into atomic criteria enables detailed compliance analysis.

### S16: Code Prompting Elicits Conditional Reasoning (2024)

- **URL**: https://arxiv.org/html/2401.10065v1
- **Evidence Level**: High
- **Key Finding**: Structured code representations improve conditional reasoning accuracy over prose.

### S17: The Few-shot Dilemma: Over-prompting LLMs (2025)

- **URL**: https://arxiv.org/html/2509.13196v1
- **Evidence Level**: High
- **Key Finding**: Diminishing returns past 2-5 examples. Over-prompting degrades performance.

### S18: MLOps Community — Impact of Prompt Bloat

- **URL**: https://mlops.community/the-impact-of-prompt-bloat-on-llm-output-quality/
- **Evidence Level**: High
- **Key Finding**: Semantically similar noise is MORE damaging than random noise. CoT doesn't mitigate length degradation.

---

## Framework Evidence (High Evidence)

### S19: CrewAI — Task/Agent Structure

- **Evidence Level**: High
- **Key Finding**: Role/Goal/Backstory triad. Prompt slices for specialized behavior. Tasks have `description` + `expected_output`.

### S20: LangChain/LangGraph — Agent Structure

- **Evidence Level**: High
- **Key Finding**: System/Human/AI message roles. Tools auto-described from function signatures. State through typed schemas.

### S21: AutoGen (Microsoft) — Agent Structure

- **Evidence Level**: High
- **Key Finding**: Minimal flat structure: name + system_message + tools. `description` for orchestration (separate from system_message).

### S22: Claude Code — System Prompt Architecture

- **Evidence Level**: High
- **Key Finding**: 110+ prompt strings in 5 categories. Layered CLAUDE.md override system. Skills as Markdown loaded on demand. Mid-conversation system reminders.

### S23: OpenAI Agents SDK / Codex

- **Evidence Level**: High
- **Key Finding**: First-class guardrails (InputGuardrail/OutputGuardrail) separate from instructions. AGENTS.md with directory-based precedence. Dynamic instructions via functions.

---

## Source Count: 23 sources (10 Very High, 10 High, 3 Medium)

## Cross-references: 45+ triangulation points
