---
id: research-prompt-003
title: "Kata Harness First Principles: Deterministic Governance & Observability in Agentic Workflow Execution"
date: 2026-01-29
status: draft
purpose: deep-research
estimated_depth: comprehensive
target_sources: academic, industry frameworks, open-source agents, enterprise patterns
related_to: ["ADR-008", "VIS-RAISE-003", "research-prompt-002"]
---

# Research Prompt: Kata Harness First Principles

## Context for Researcher

RaiSE v2.3 introduced the **Kata Harness** concept: a platform capability that executes Katas (multi-step SDLC workflows) with the following stated goals:

- **Deterministic execution**: Each step runs in order, gates enforce before progression
- **Observability**: Every action is traceable, verifiable, auditable
- **Governance-as-code**: Policies are versioned artifacts, not runtime suggestions

**Current implementation assumption** (inherited from spec-kit):
```
┌─────────────────────────────────────────────────────────────┐
│  Markdown Command File (.md)                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ## Outline                                            │  │
│  │ 1. Step 1: Do X                                       │  │
│  │    - Action A                                         │  │
│  │    - **Verificación**: Check Y                        │  │
│  │    - > Si no puedes continuar: Z → JIDOKA            │  │
│  │ 2. Step 2: Do W                                       │  │
│  │    ...                                                │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│              LLM interprets and executes                     │
│              (probabilistic compliance)                      │
└─────────────────────────────────────────────────────────────┘
```

**The fundamental tension:**
- **Desired**: Deterministic governance, guaranteed step execution, enforced gates
- **Reality**: LLM may skip steps, hallucinate verification, ignore Jidoka triggers
- **Question**: Is there an architecture that provides **actual enforcement** rather than **suggested compliance**?

---

## Research Questions

### RQ1: First Principles of Agentic Workflow Execution

**Question**: What are the fundamental primitives required to execute multi-step AI agent workflows with deterministic guarantees?

**Specific areas to investigate**:

1. **Execution Primitives**:
   - What is the minimal set of abstractions needed? (Task, Step, Gate, Context, Tool?)
   - How do workflow engines (non-AI) guarantee step ordering? (State machines, DAGs, sagas)
   - What makes AI agent execution different from traditional workflow execution?

2. **Control Flow Patterns**:
   - Sequential vs parallel vs conditional execution in agent workflows
   - How do frameworks handle branching decisions (agent decides vs harness decides)?
   - Interruption and resumption patterns (checkpointing, replay)

3. **Verification Mechanisms**:
   - Compile-time vs runtime verification of workflows
   - How can gates be **enforced** (not suggested) in LLM contexts?
   - Patterns for "stop-the-line" (Jidoka) in probabilistic systems

4. **Context Management**:
   - How do harnesses manage context windows across multi-step execution?
   - Token budget allocation strategies
   - Memory persistence patterns (short-term, long-term, episodic)

**Deliverable**: Taxonomy of execution primitives with definitions and relationships.

---

### RQ2: Market Landscape - Agentic Harness Implementations

**Question**: How do leading AI agent frameworks implement workflow orchestration, and what architectural patterns emerge?

**Frameworks to analyze** (prioritized):

| Tier | Framework | Why Include |
|------|-----------|-------------|
| 1 | **LangGraph** (LangChain) | Most sophisticated graph-based execution |
| 1 | **CrewAI** | Multi-agent orchestration patterns |
| 1 | **AutoGen** (Microsoft) | Conversation-based agent coordination |
| 1 | **Semantic Kernel** (Microsoft) | Enterprise-grade plugin architecture |
| 2 | **Agency Swarm** | Hierarchical agent patterns |
| 2 | **Phidata** | Tool-first approach |
| 2 | **Rivet** (Ironclad) | Visual programming for agents |
| 2 | **Flowise** | Low-code agent builder |
| 3 | **Claude MCP** | Protocol-level tool integration |
| 3 | **OpenAI Assistants API** | Threads, runs, and tool use patterns |
| 3 | **Anthropic Tool Use** | Native tool calling patterns |

**For each framework, document**:

1. **Execution Model**:
   - How is a "workflow" defined? (Code, config, visual, natural language?)
   - What enforces step ordering? (State machine, DAG, conversation, none?)
   - How are transitions between steps controlled?

2. **Observability Features**:
   - What telemetry is captured? (Inputs, outputs, latency, tokens, decisions?)
   - How is execution traced? (OpenTelemetry, custom, logs?)
   - Can execution be replayed/debugged?

3. **Governance Mechanisms**:
   - Are there gates/checkpoints? How enforced?
   - Human-in-the-loop patterns?
   - Error handling and recovery?

4. **Context Management**:
   - How is context passed between steps?
   - Token/memory management strategies?
   - Persistence patterns?

**Deliverable**: Comparison matrix with architectural diagrams for top 5 frameworks.

---

### RQ3: Deterministic Execution Patterns

**Question**: What patterns exist for achieving determinism in inherently probabilistic LLM-based systems?

**Specific areas to investigate**:

1. **Structured Output Enforcement**:
   - JSON mode, function calling, tool use as structure enforcement
   - Grammar-constrained generation (Outlines, Guidance, LMQL)
   - Schema validation as gate mechanism

2. **State Machine Approaches**:
   - XState + LLM integration patterns
   - Finite state machines for agent control flow
   - Statecharts for hierarchical agent behavior

3. **Program Synthesis Patterns**:
   - DSPy's declarative programming model
   - Prompt chaining as functional composition
   - Code generation for deterministic execution

4. **Hybrid Architectures**:
   - "Thin LLM" patterns (LLM decides, code executes)
   - Tool-first architectures (LLM as router, tools as executors)
   - Separation of planning from execution

5. **Verification Layers**:
   - Output validators (Guardrails AI, NeMo Guardrails)
   - Constitutional AI patterns for self-verification
   - Multi-agent verification (checker agents)

**Deliverable**: Pattern catalog with implementation examples and trade-offs.

---

### RQ4: Observability & Tracing in Agent Systems

**Question**: What observability patterns enable debugging, auditing, and governance in multi-step agent execution?

**Specific areas to investigate**:

1. **Tracing Standards**:
   - OpenTelemetry for LLM applications (semantic conventions)
   - LangSmith, Arize, Weights & Biases tracing approaches
   - Custom trace formats for agent workflows

2. **What to Observe**:
   - Token usage per step
   - Latency breakdown (inference, tool execution, I/O)
   - Decision points and reasoning traces
   - Context drift and coherence metrics

3. **Audit Requirements**:
   - Compliance logging patterns (SOC2, GDPR implications)
   - Deterministic replay from traces
   - Diff between expected and actual execution

4. **Real-time vs Post-hoc**:
   - Streaming execution feedback
   - Human-in-the-loop intervention points
   - Post-execution analysis and improvement

**Deliverable**: Observability framework recommendation with data model.

---

### RQ5: Governance-as-Code for Agent Workflows

**Question**: How can governance policies be encoded as executable artifacts rather than suggested guidelines?

**Specific areas to investigate**:

1. **Policy Languages**:
   - OPA/Rego for agent policy enforcement
   - Cedar (AWS) permission policies
   - Custom DSLs for agent governance

2. **Gate Enforcement Mechanisms**:
   - Pre-execution validators (can this step run?)
   - Post-execution validators (did the output meet criteria?)
   - Continuous validators (is the agent staying on track?)

3. **Separation of Concerns**:
   - Policy vs mechanism separation in agent architectures
   - How to update governance without changing agent code
   - Version control for policies

4. **Existing Implementations**:
   - Guardrails AI (structural validation)
   - NeMo Guardrails (conversational guardrails)
   - Anthropic's Constitutional AI (training-time governance)
   - Runtime policy enforcement patterns

**Deliverable**: Governance architecture patterns with applicability to RaiSE Kata Harness.

---

### RQ6: Design Recommendations for Kata Harness

**Question**: Given RaiSE's principles (Jidoka, Heutagogy, Governance-as-Code), what architecture should the Kata Harness adopt?

**Specific synthesis required**:

1. **Architecture Options**:
   - Option A: Pure markdown + enhanced LLM prompting (status quo improved)
   - Option B: State machine orchestrator + LLM steps
   - Option C: Compiled kata DSL + runtime interpreter
   - Option D: Graph-based execution (LangGraph-like)
   - Option E: Hybrid (design-time flexibility, runtime enforcement)

2. **For each option, evaluate**:
   - Alignment with RaiSE principles (Jidoka, Heutagogy, Lean)
   - Implementation complexity
   - Observability capabilities
   - Governance enforcement strength
   - Developer experience (authoring katas)
   - Extensibility

3. **RaiSE-Specific Requirements**:
   - Must support Work Cycles (project/, feature/, setup/, improve/)
   - Must integrate with Skills (atomic operations)
   - Must load Context (constitution, guardrails, patterns)
   - Must enable Jidoka (stop-the-line on defects)
   - Must support heutagogic learning (agent self-direction with governance)

**Deliverable**: Architectural recommendation with rationale, trade-offs, and implementation roadmap.

---

## Research Methodology Suggestions

### Primary Sources

1. **Framework Documentation**:
   - LangChain/LangGraph: https://python.langchain.com/docs/langgraph
   - CrewAI: https://docs.crewai.com/
   - AutoGen: https://microsoft.github.io/autogen/
   - Semantic Kernel: https://learn.microsoft.com/semantic-kernel/
   - DSPy: https://dspy-docs.vercel.app/

2. **Observability Platforms**:
   - LangSmith documentation
   - Arize Phoenix
   - OpenTelemetry semantic conventions for GenAI

3. **Governance Tools**:
   - Guardrails AI: https://www.guardrailsai.com/docs
   - NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails
   - OPA/Rego: https://www.openpolicyagent.org/

### Secondary Sources

1. **Academic Papers**:
   - "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al.)
   - "Toolformer: Language Models Can Teach Themselves to Use Tools"
   - "Constitutional AI: Harmlessness from AI Feedback" (Anthropic)
   - Workflow orchestration literature (Saga pattern, State machines)

2. **Industry Analysis**:
   - a]16z reports on AI agent architectures
   - Sequoia AI agent landscape
   - Conference talks: AI Engineer Summit, LangChain ecosystem

3. **Community Discussions**:
   - r/LocalLLaMA, r/MachineLearning threads on agent reliability
   - GitHub discussions on agent framework design decisions
   - HackerNews threads on determinism in LLM applications

---

## Expected Deliverables

1. **Primitives Taxonomy** (RQ1)
   - Visual diagram of execution primitives and relationships
   - Definitions aligned with RaiSE terminology

2. **Framework Comparison Matrix** (RQ2)
   - 10+ frameworks compared across 15+ dimensions
   - Architecture diagrams for top 5

3. **Determinism Pattern Catalog** (RQ3)
   - 10+ patterns documented
   - Implementation examples with code snippets
   - Trade-off analysis

4. **Observability Framework** (RQ4)
   - Data model for Kata execution traces
   - Recommended tooling stack
   - Integration patterns with existing RaiSE concepts

5. **Governance Architecture** (RQ5)
   - Gate enforcement mechanisms
   - Policy language recommendations
   - Integration with Jidoka principle

6. **Kata Harness Design Recommendation** (RQ6)
   - Scored architecture options matrix
   - Recommended architecture with rationale
   - Implementation roadmap (phases)
   - Prototype scope definition

---

## Success Criteria

The research is successful if it enables RaiSE to:

1. **Decide**: Choose an architectural approach for Kata Harness implementation
2. **Differentiate**: Understand how RaiSE's approach differs from existing frameworks
3. **Design**: Have sufficient detail to begin implementation
4. **Prioritize**: Know which features to build first (MVP vs future)
5. **Validate**: Have criteria to verify the implementation meets governance goals

---

## Constraints and Considerations

### Technical Constraints
- **Platform agnostic**: Must work across Claude, GPT-4, local models
- **Minimal dependencies**: Prefer simple, auditable components
- **TypeScript/Node preferred**: Align with existing RaiSE tooling (if code needed)

### Philosophical Constraints
- **Jidoka first**: Stop-the-line must be a first-class citizen, not afterthought
- **Heutagogy compatible**: Agent self-direction within governance bounds
- **Lean**: Simplest architecture that achieves governance goals
- **Facts not gaps**: Research what IS, not what we wish existed

### Practical Constraints
- **Incremental adoption**: Must be possible to migrate from current markdown commands
- **Authoring UX**: Kata authors shouldn't need to learn programming
- **Debugging UX**: Operators must be able to diagnose failures easily

---

## Related RaiSE Documents

- `specs/raise/vision.md` (v2.3) - Kata Harness concept definition
- `specs/raise/adrs/adr-008-kata-skill-context-simplification.md` - Ontology decision
- `.raise/context/glossary.md` (v2.3) - Canonical terminology
- `.raise/context/work-cycles.md` - Work Cycle definitions
- `.raise/katas/` - Current kata implementations (target for harness)
- `specs/main/research/prompts/command-kata-skill-ontology-research.md` - Related terminology research

---

## Open Questions for Research

1. Is "deterministic" the right goal, or is "verifiable" more achievable?
2. How do we balance LLM flexibility with governance strictness?
3. What's the minimum viable harness that provides meaningful improvement over current state?
4. Should the harness be a library, a runtime, or a protocol?
5. How does MCP (Model Context Protocol) fit into harness architecture?

---

*This prompt is designed for deep research. Expected effort: 8-12 hours of focused investigation. Output should be a structured report addressing all RQs with actionable recommendations.*
