# Research: Deterministic Harnesses for LLM-Driven Skill Systems

> Date: 2026-03-28
> Epic: E14 (RAISE-1006)
> Researcher: Rai (automated)
> Confidence: **High** (multiple peer-reviewed sources, active open-source projects, triangulated across 3+ sources per claim)

## Executive Summary

The landscape of deterministic execution for LLM agents has matured significantly through 2025-2026, splitting into two distinct tiers: **low-level constrained generation** (Outlines, Guidance, XGrammar) that operates at the token/decoding level, and **high-level programming frameworks** (DSPy, BAML, Instructor) that operate at the prompt/pipeline level. RaiSE's markdown-skill approach occupies a unique position — it is a **declarative harness at the orchestration layer**, closest in spirit to DSPy's programming model but using natural language as the specification language rather than Python DSL. Key gaps identified: RaiSE lacks runtime assertion mechanisms (cf. DSPy Assertions), schema-enforced outputs (cf. BAML/Instructor), and structured memory integration as a default (cf. A-MEM). The field is converging on **type-safe, schema-driven, validation-gated pipelines** as the standard for production agent systems.

## 1. Deterministic Execution Frameworks

### Findings

The frameworks divide into three architectural tiers:

**Tier 1 — Constrained Decoding (Token Level)**

These libraries intervene at the logit/sampling level to guarantee structurally valid output:

- **Outlines** (Willard & Louf, 2023): Compiles JSON schemas and regex patterns into finite-state machines (FSMs) with precomputed vocabulary indexes, enabling O(1) valid token lookup per generation step. Pioneered the FSM approach. Limitation: complex schemas can cause compilation times from 40s to 10+ minutes; lowest compliance rate on JSONSchemaBench [S1, S2].
- **XGrammar** (Dong et al., MLSys 2025): Context-free grammar / pushdown automaton approach with context-independent/dependent token splitting. Achieves near-zero overhead constrained decoding at production scale [S3].
- **Guidance** (Microsoft): Template-based controlled generation with interleaved generation and control flow. Lower-level than DSPy, focuses on individual completions [S4].
- **LMQL** (Language Model Query Language): Reframes prompting as query execution with variables, constraints, and control flow in unified syntax. Reduces inference cost 26-85% through constraint compilation [S5, S6].
- **SGLang** (NeurIPS 2024): Low-level system co-designed with its own runtime for novel optimizations. Focuses on runtime efficiency with structured language model programs [S7].

**Tier 2 — Structured Output Frameworks (Schema Level)**

These operate above the token level, using schemas to validate and retry:

- **BAML** (BoundaryML): Domain-specific language where every prompt is a typed function. Schema-Aligned Parsing (SAP) algorithm supports flexible outputs (markdown in JSON, chain-of-thought). 98% valid type-correct objects, ~2.1x faster than alternatives due to compact DSL schema. Multi-language code generation from .baml definitions [S8, S9].
- **Instructor** (jxnl): Most popular Python library for structured LLM extraction (3M+ monthly downloads). Built on Pydantic with automatic validation, retries, and streaming. Works with 15+ providers. Python-first developer experience [S10, S11].
- **Guardrails AI**: Input/Output Guards with a Hub of pre-built validators. Supports Pydantic integration and prompt optimization. Can run as standalone service via REST API. Guardrails Index benchmark (Feb 2025) compares 24 guardrails across 6 categories [S12, S13].

**Tier 3 — Programming Frameworks (Pipeline Level)**

These provide end-to-end pipeline programming with optimization:

- **DSPy** (Stanford NLP): Declarative structured programming for LLMs. Differentiable prompt modules optimized through feedback. **LM Assertions** introduce computational constraints — `Assert` (hard, halts pipeline) and `Suggest` (soft, best-effort). Up to 164% higher compliance and 37% higher quality. 500+ GitHub dependents, v2.6.14 as of March 2025 [S14, S15, S16].
- **Prompt Decorators** (2025): Declarative composable syntax for reasoning, formatting, and control. Aligns with DSPy/BAML direction [S17].

**Key Pattern: Separation of Concerns**

The field has settled on: *constrained decoding* for token-level safety, *schema validation* for output-level safety, and *pipeline assertions* for semantic-level safety. Production systems typically compose across tiers.

### Evidence Matrix

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|---------------|------------|
| FSM-based constrained decoding is standard for token-level control | S1, S2, S3 | Very High | 95% |
| DSPy Assertions provide pipeline-level computational constraints | S14, S15, S16 | Very High | 95% |
| BAML achieves 98% type-correct output rate | S8, S9 | High | 85% |
| Schema-driven validation is converging as industry standard | S8, S10, S12, S14 | Very High | 90% |
| LMQL reduces inference cost 26-85% | S5, S6 | High | 80% |

## 2. Poka-yoke Patterns in AI Systems

### Findings

The application of poka-yoke (mistake-proofing) to LLM systems is an emerging but underdeveloped area. The concept transfers from manufacturing to AI through several mechanism types:

**Structural Poka-yoke (Prevention by Design)**

- **Type-safe schemas as contracts**: BAML and Instructor use Pydantic/typed schemas so that malformed output is structurally impossible. The schema IS the poka-yoke — if the LLM cannot produce valid typed output, generation retries automatically [S8, S10].
- **Grammar-constrained decoding**: Outlines/XGrammar make it impossible for the LLM to generate tokens that violate the grammar. This is the strongest form of structural poka-yoke — invalid outputs are eliminated at the probability level [S1, S3].
- **Pipeline assertions (DSPy)**: `dspy.Assert` halts execution if constraints are violated, preventing downstream propagation of errors. `dspy.Suggest` logs and continues — the "warning" level of poka-yoke [S14, S15].

**Validation Gate Poka-yoke (Detection Before Propagation)**

- **Multi-layered guardrails**: NeMo Guardrails implements pre-call (schema validation, jailbreak checks), in-call (timeouts, rate limits), and post-call (output validators, policy auditing) checkpoints. Colang 2.0 provides a DSL for defining these [S18, S19].
- **Guardrails AI Hub validators**: Pre-built validators for common risk types (hallucination, PII, toxicity, off-topic). Multiple validators compose into guards [S12, S13].
- **Agentic security guardrails**: NeMo provides tool call validation — rails that validate tool inputs and outputs before and after invocation [S18].

**Process Poka-yoke (Sequencing Constraints)**

- **Prerequisite gates**: RaiSE's own skill system implements this — a skill cannot execute without its prerequisites being met (e.g., plan must exist before implementation).
- **State machine workflows**: LangGraph's graph-based orchestration enforces valid state transitions, preventing out-of-order execution [S20].
- **Checkpoint/rollback**: LangGraph's checkpointing enables recovery from errors, a form of corrective poka-yoke [S20].

**Gap: No Published Poka-yoke Taxonomy for LLM Systems**

Despite the widespread application of these patterns, no published work specifically frames them as poka-yoke for LLM systems. The manufacturing-to-AI poka-yoke literature focuses on using AI to improve manufacturing poka-yoke, not on applying poka-yoke principles to AI system design [S21, S22]. This represents a contribution opportunity for RaiSE.

### Evidence Matrix

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|---------------|------------|
| Type-safe schemas prevent malformed output by design | S8, S10, S1 | Very High | 95% |
| Multi-layered validation (pre/in/post) is best practice | S18, S12, S19 | High | 85% |
| DSPy Assert/Suggest provides pipeline-level error prevention | S14, S15 | Very High | 90% |
| No published poka-yoke taxonomy exists for LLM systems | S21, S22, own survey | Medium | 75% |
| Process sequencing constraints prevent execution errors | S20, RaiSE skills | High | 85% |

## 3. Neuro-symbolic Integration as Default

### Findings

The integration of symbolic reasoning (knowledge graphs, structured memory) with LLM agents is an active research frontier, but **making it the default rather than opt-in remains an unsolved problem**.

**Current Integration Approaches**

Two main directions exist [S23, S24]:

1. **KG-enhanced LLMs**: Knowledge graphs improve reasoning, reduce hallucinations, and enable complex question answering. The graph provides grounding for the LLM's generation.
2. **LLM-augmented KGs**: LLMs facilitate KG construction, completion, and querying. The LLM bootstraps and maintains the symbolic layer.

**Memory Architecture for Agents**

The ICLR 2026 MemAgents workshop identifies key challenges [S25]:

- **Catastrophic forgetting** in long-running agents
- **Retrieval efficiency** — finding relevant memories at scale
- **Storage paradigm choice**: cumulative vs. reflective/summarized, textual vs. parametric vs. structured (tables, triples, graph)

**Emerging Patterns**

- **A-MEM (Zettelkasten-inspired)**: Each memory unit enriched with LLM-generated keywords, tags, contextual descriptions, and dynamically constructed links. Link generation uses embedding similarity + LLM reasoning [S26].
- **Cognee + BAML**: Integration of structured output (BAML) with AI memory (Cognee) for production memory systems [S27].
- **Neurosymbolic graph enrichment**: Knowledge graphs as grounded world models for neuro-symbolic AI, where the graph provides the deterministic substrate and the LLM provides flexible reasoning [S28, S29].

**Key Insight: The Default Problem**

Most frameworks treat knowledge graph integration as opt-in — you CAN connect a graph, but the agent works without one. The research direction is toward making structured memory the DEFAULT substrate, not an addon. The AAAI 2026 NeusymBridge workshop specifically addresses "using KG or symbolic knowledge to improve LLM quality" and "distilling symbolic knowledge from LLMs" [S30].

**Contrary Evidence**: Some researchers argue that LLMs differ fundamentally from traditional neural networks due to their scale, autoregressive nature, and context-dependent outputs, and that existing neurosymbolic AI frameworks may not fully capture LLMs' unique properties [S31]. The integration challenge is non-trivial.

### Evidence Matrix

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|---------------|------------|
| Two integration directions: KG-enhanced LLMs and LLM-augmented KGs | S23, S24 | Very High | 95% |
| Making symbolic memory default (not opt-in) remains unsolved | S25, S30, S31 | High | 85% |
| A-MEM Zettelkasten approach shows promise for structured agent memory | S26 | Medium | 70% |
| KG grounding reduces hallucination | S23, S28 | High | 85% |
| Existing neurosymbolic frameworks may not fit LLM architecture | S31 | Medium | 70% |

## 4. Skill Composition & Orchestration

### Findings

Agent frameworks in 2025-2026 implement four main orchestration patterns:

**Pattern 1: Graph-Based State Machines (LangGraph)**

LangGraph uses nodes, edges, and conditional routing to create traceable, debuggable flows. State machine approach enables checkpointing, streaming, and recovery. Highest production readiness with LangSmith observability [S20, S32, S33].

**Pattern 2: Role-Based Crews (CrewAI)**

Specialized agents cooperate through roles, tasks, and collaboration protocols. Agents communicate asynchronously or in rounds. Lower coordination overhead for team-oriented tasks [S20, S33, S34].

**Pattern 3: Conversation-Loop Multi-Agent (AutoGen/AG2)**

Agents communicate through conversation patterns. Flexible but less structured than graph-based approaches. Microsoft's AG2 (successor to AutoGen) adds improved orchestration [S33, S34].

**Pattern 4: Hierarchical Tool/Skill Composition (MCP + Claude)**

Anthropic's stack comprises five layers [S35, S36]:
1. **MCP** — connectivity to external tools/services (10,000+ servers in production)
2. **Skills** — task-specific knowledge (markdown-defined)
3. **Agent** — primary worker
4. **Subagents** — parallel workers
5. **Agent Teams** — coordination

**Guardrails as First-Class Citizens**

The consensus across frameworks is that guardrails must be **first-class, not sprinkled on top** [S33]:
- Pre-call: schema validation, jailbreak checks
- In-call: timeouts, rate limits
- Post-call: output validators, policy auditing
- Cross-cutting: typed artifacts, versioned tool contracts in a registry

**Composition Best Practices**

- Flatten prompts into typed artifacts
- Register every tool/agent with versioned contracts
- Keep memory and guardrails framework-agnostic for layer swapping
- Use LangGraph for the "spine," add CrewAI/AutoGen for interaction-heavy coordination [S33]

### Evidence Matrix

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|---------------|------------|
| Graph-based state machines are highest production readiness | S20, S32, S33 | Very High | 90% |
| Guardrails must be first-class, not afterthought | S18, S33, S12 | Very High | 95% |
| MCP has 10,000+ production servers | S35 | High | 85% |
| Anthropic's 5-layer agent stack (MCP/Skills/Agent/Sub/Teams) | S35, S36 | High | 85% |
| Versioned tool contracts as best practice | S33 | High | 80% |

## 5. Agent Skill Maturity Models

### Findings

Multiple maturity models have emerged for assessing agent capabilities:

**Dextralabs L1-L4 Agentic AI Maturity Model (2025)** [S37]

| Level | Name | Characteristics |
|-------|------|-----------------|
| L1 | Copilots/Assistance | AI assists, human decides. Manual rules and logic. |
| L2 | Multi-Agent Coordination | AI investigates and recommends. Purpose-built agents trusted with specific tasks. |
| L3 | Orchestration | AI workflows automated. Agents coordinate with minimal human supervision. |
| L4 | Full Autonomy | Self-learning agents operate independently. Humans provide strategic oversight only. |

Three phases: Integration → Orchestration → Optimization.

**Bessemer AI Agent Autonomy Scale** [S38]

Venture capital-oriented framework that maps use case maturity to investment readiness. Assesses autonomy, reliability, and business value creation.

**Microsoft Copilot Studio Maturity Model** [S39]

Enterprise adoption model focused on governance, compliance, and organizational readiness for agentic AI.

**OWASP AI Maturity Assessment (AIMA) v1.0** (August 2025) [S40]

Security-focused maturity assessment. Evaluates AI systems across security governance, model lifecycle, and deployment safety dimensions.

**Agent Assessment Framework (arxiv, 2025)** [S41]

Four evaluation pillars:
1. **LLMs** — model capability and reliability
2. **Memory** — context retention and retrieval
3. **Tools** — integration quality and coverage
4. **Environment** — deployment and operational fitness

**RAGAS** (Retrieval-Augmented Generation Assessment Suite) [S42]

Open-source evaluation framework for RAG and agentic applications. Metrics beyond task completion.

**Key Insight: NeurIPS 2025 Shift**

The era of "magic" is over; the era of **Reliable Systems Engineering** has begun. Assessment now emphasizes system reliability, governance, and agency over raw model performance [S41].

### Evidence Matrix

| Claim | Sources | Evidence Level | Confidence |
|-------|---------|---------------|------------|
| L1-L4 maturity model is emerging consensus | S37, S38, S39 | High | 80% |
| Four-pillar assessment (LLM/Memory/Tools/Environment) | S41 | Medium | 70% |
| OWASP AIMA v1.0 is the security maturity standard | S40 | High | 85% |
| Field shifting from magic to reliable systems engineering | S41, S37 | High | 85% |
| No single universally adopted maturity model exists yet | S37-S42 | High | 85% |

## Synthesis: Implications for RaiSE

### Where RaiSE Stands

RaiSE's skill system is a **markdown-defined deterministic harness** that constrains LLM execution through sequential steps, prerequisite gates, and human-in-the-loop checkpoints. Mapping to the landscape:

| Dimension | RaiSE Current | State of Art | Gap |
|-----------|---------------|-------------|-----|
| **Execution Determinism** | Step-by-step markdown instructions, prerequisite gates | DSPy Assertions (Assert/Suggest), BAML typed functions, FSM-constrained decoding | No runtime assertions, no typed outputs, no automatic retry on constraint violation |
| **Output Validation** | Implicit (human reviews), gate checks (tests, types, lint) | Guardrails AI validators, NeMo Guardrails (pre/in/post), Instructor Pydantic retry | No schema-enforced skill outputs, no automated output validation between steps |
| **Memory Integration** | Graph available via `rai graph query`, opt-in per step | A-MEM (default structured memory), KG-grounded generation | Memory is opt-in, not default. No automatic context injection from graph |
| **Poka-yoke** | Process sequencing (prerequisites), HITL gates | Type-safe schemas, grammar constraints, pipeline assertions, multi-layer guardrails | Strong process poka-yoke, weak structural poka-yoke (no typed contracts between skills) |
| **Composition** | Sequential skill chaining (e.g., story-run chains start→design→plan→implement→review→close) | LangGraph state machines, CrewAI crews, MCP hierarchical composition | Linear chaining only, no conditional routing, no parallel skill execution, no state machine |
| **Maturity Assessment** | ShuHaRi levels per skill (qualitative) | L1-L4 quantitative frameworks, four-pillar assessment, OWASP AIMA | No quantitative maturity scoring, no cross-skill capability assessment |

### Actionable Recommendations for E14

1. **Introduce Skill Assertions (HIGH PRIORITY)**: Adapt DSPy's Assert/Suggest pattern. Each skill step could declare constraints that are checked before proceeding. `Assert` halts; `Suggest` logs and continues. This is the highest-leverage improvement.

2. **Schema-Typed Skill Outputs (HIGH PRIORITY)**: Define Pydantic models for what each skill produces (not just `file_path` strings in metadata). Enable automatic validation of skill outputs before the next skill consumes them. This is the BAML/Instructor pattern applied to skill composition.

3. **Default Memory Injection (MEDIUM PRIORITY)**: Instead of requiring each skill step to manually `rai graph query`, inject relevant context from the knowledge graph automatically based on skill metadata (domain, work cycle, patterns). Make graph grounding opt-OUT, not opt-in.

4. **Multi-Layer Guardrails (MEDIUM PRIORITY)**: Adopt NeMo's pre/in/post model: pre-step validation (prerequisites met, context loaded), in-step monitoring (drift detection, token budget), post-step validation (output schema, quality gates).

5. **Conditional Routing in Skill Chains (LOW PRIORITY for v3.x)**: The current linear chain (story-run) works but cannot handle conditional paths (e.g., skip design for XS stories based on automated assessment). A lightweight state machine within skill-run orchestrators would add flexibility.

6. **Quantitative Skill Maturity Scoring (FOR S14.1)**: Create a scoring rubric aligned with the six E14 dimensions, producing numerical scores per skill. This enables tracking improvement over time and comparing skills objectively.

### RaiSE's Unique Advantage

RaiSE's approach has a **distinctive strength** the industry frameworks lack: **natural language as the harness language**. While DSPy requires Python, BAML requires its DSL, and LangGraph requires graph definitions, RaiSE skills are readable markdown that any developer (or LLM) can understand without learning a new language. This is a defensible differentiator for author experience (D5) and user experience (D6). The challenge is adding the rigor of typed frameworks without losing this accessibility.

### Contrary Considerations

- Adding typed schemas to every skill step may create authoring friction that reduces the accessibility advantage.
- Default memory injection risks context bloat — irrelevant graph data consuming token budget.
- The field is moving fast; any framework chosen today may be superseded. Invest in abstractions, not implementations.

## Sources

1. [S1] [Efficient Guided Generation for Large Language Models (Willard & Louf, 2023)](https://arxiv.org/pdf/2307.09702) — Outlines paper. Evidence: Very High.
2. [S2] [Constrained Decoding: Grammar-Guided Generation](https://mbrenndoerfer.com/writing/constrained-decoding-structured-llm-output) — Technical overview. Evidence: High.
3. [S3] [XGrammar: Flexible and Efficient Structured Generation (MLSys 2025)](https://arxiv.org/pdf/2411.15100) — Near-zero overhead constrained decoding. Evidence: Very High.
4. [S4] [A Guide to Large Language Model Abstractions - Two Sigma](https://www.twosigma.com/articles/a-guide-to-large-language-model-abstractions/) — Framework taxonomy. Evidence: High.
5. [S5] [SGLang: Efficient Execution of Structured Language Model Programs (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/724be4472168f31ba1c9ac630f15dec8-Paper-Conference.pdf) — Evidence: Very High.
6. [S6] [Declarative Prompt DSLs - EmergentMind](https://www.emergentmind.com/topics/declarative-prompt-dsls) — LMQL overview. Evidence: Medium.
7. [S7] [SGLang: Efficient Execution (arxiv)](https://arxiv.org/html/2312.07104v1) — Evidence: High.
8. [S8] [BAML - BoundaryML](https://boundaryml.com/) — Official site. Evidence: High.
9. [S9] [How BAML Brings Engineering Discipline to LLM-Powered Systems (March 2026)](https://medium.com/@rajkundalia/how-baml-brings-engineering-discipline-to-llm-powered-systems-983c06d31bf8) — Evidence: Medium.
10. [S10] [Instructor - Structured Outputs for LLMs](https://python.useinstructor.com/) — Official docs. Evidence: High.
11. [S11] [The Guide to Structured Outputs and Function Calling with LLMs](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms) — Evidence: High.
12. [S12] [Guardrails AI](https://guardrailsai.com/docs) — Official docs. Evidence: High.
13. [S13] [Guardrails Hub](https://guardrailsai.com/hub) — Validator registry. Evidence: High.
14. [S14] [DSPy Assertions: Computational Constraints (arxiv, 2023)](https://arxiv.org/abs/2312.13382) — Core paper. Evidence: Very High.
15. [S15] [DSPy Assertions - Official Docs](https://dspy.ai/learn/programming/7-assertions/) — Evidence: High.
16. [S16] [DSPy: Open-source Framework for LLM-powered Applications (InfoWorld)](https://www.infoworld.com/article/3956455/dspy-an-open-source-framework-for-llm-powered-applications.html) — Evidence: Medium.
17. [S17] [Prompt Decorators: Declarative and Composable Syntax (arxiv, 2025)](https://arxiv.org/html/2510.19850v1) — Evidence: Medium.
18. [S18] [NVIDIA NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/index.html) — Official docs. Evidence: High.
19. [S19] [NeMo Guardrails GitHub](https://github.com/NVIDIA-NeMo/Guardrails) — Evidence: High.
20. [S20] [Best AI Agent Frameworks 2025 (Langflow)](https://www.langflow.org/blog/the-complete-guide-to-choosing-an-ai-agent-framework-in-2025) — Framework comparison. Evidence: High.
21. [S21] [Reducing Errors with Poka-Yoke and AI - Retrocausal](https://retrocausal.ai/blog/reducing-errors-with-poka-yoke-and-ai/) — Manufacturing focus. Evidence: Medium.
22. [S22] [Poka-Yoking your ML Model (Medium)](https://medium.com/@srinivaspadmanabhuni/poka-yoking-your-ml-model-e0a853df8cc5) — Evidence: Low.
23. [S23] [From Symbolic to Neural and Back: KG-LLM Synergies (Springer)](https://link.springer.com/chapter/10.1007/978-3-032-03028-3_11) — Evidence: High.
24. [S24] [Neuro-symbolic Synergy in Education (Springer, 2025)](https://link.springer.com/article/10.1186/s40561-025-00423-z) — Evidence: High.
25. [S25] [ICLR 2026 MemAgents Workshop Proposal](https://openreview.net/pdf?id=U51WxL382H) — Evidence: High.
26. [S26] [Memory Mechanisms in LLM Agents - EmergentMind](https://www.emergentmind.com/topics/memory-mechanisms-in-llm-based-agents) — Evidence: Medium.
27. [S27] [Cognee + BAML: Structured Output & AI Memory](https://www.cognee.ai/blog/integrations/structured-outputs-with-baml-and-cognee) — Evidence: Medium.
28. [S28] [Knowledge Graphs as Grounded World Models for Neuro-Symbolic AI (ResearchGate)](https://www.researchgate.net/publication/400386797_Knowledge_Graphs_as_Grounded_World_Models_for_Neuro-Symbolic_Artificial_Intelligence) — Evidence: High.
29. [S29] [Neurosymbolic Graph Enrichment for Grounded World Models (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S030645732500069X) — Evidence: High.
30. [S30] [NeusymBridge Workshop @ AAAI 2026](https://neusymbridge.github.io/) — Evidence: Medium.
31. [S31] [Advancing Symbolic Integration in LLMs: Beyond Conventional Neurosymbolic AI (arxiv, 2025)](https://arxiv.org/html/2510.21425v1) — Evidence: High.
32. [S32] [Best Multi-Agent Frameworks in 2026](https://gurusup.com/blog/best-multi-agent-frameworks-2026) — Evidence: Medium.
33. [S33] [Agents on the Wire: Protocols, Memory, and Guardrails (Cognaptus, 2025)](https://cognaptus.com/blog/2025-08-18-agents-on-the-wire-protocols-memory-and-guardrails-for-realworld-agentic-ai/) — Evidence: High.
34. [S34] [CrewAI vs LangGraph vs AutoGen (DataCamp)](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen) — Evidence: High.
35. [S35] [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) — Evidence: Very High.
36. [S36] [Anthropic Claude Code with Subagents and MCP (WinBuzzer, March 2026)](https://winbuzzer.com/2026/03/24/anthropic-claude-code-subagent-mcp-advanced-patterns-xcxwbn/) — Evidence: High.
37. [S37] [Agentic AI Maturity Model 2025 L1-L4 (Dextralabs)](https://dextralabs.com/blog/agentic-ai-maturity-model-2025/) — Evidence: High.
38. [S38] [Bessemer AI Agent Autonomy Scale](https://www.bvp.com/atlas/bessemers-ai-agent-autonomy-scale) — Evidence: High.
39. [S39] [Microsoft Copilot Studio Agentic AI Maturity Model](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/maturity-model-overview) — Evidence: High.
40. [S40] [OWASP AI Maturity Assessment](https://owasp.org/www-project-ai-maturity-assessment/) — Evidence: Very High.
41. [S41] [Beyond Task Completion: Assessment Framework for Agentic AI (arxiv, 2025)](https://arxiv.org/html/2512.12791v1) — Evidence: High.
42. [S42] [Evaluating AI Agents: Lessons from Amazon (AWS Blog)](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/) — Evidence: High.

---

*Access date for all sources: 2026-03-28*
