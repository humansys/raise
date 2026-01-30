---
id: research-agent-frameworks-executive-summary
titulo: Agent Framework Architecture Research - Executive Summary
tipo: Research Document - Executive Summary
fecha: 2026-01-29
version: 1.0.0
tags:
  - research
  - agent-frameworks
  - executive-summary
  - kata-harness
---

# Agent Framework Architecture Research - Executive Summary

## Research Question

**How do leading AI agent frameworks implement workflow orchestration, and what architectural patterns can inform the design of RaiSE's Kata Harness?**

---

## Key Findings

### Three Dominant Execution Paradigms

| Paradigm | Frameworks | Best For | Key Characteristic |
|----------|-----------|----------|-------------------|
| **Explicit Orchestration** | LangGraph, Rivet, Semantic Kernel | Structured workflows, compliance | Deterministic, graph/pipeline-based |
| **Conversational Emergence** | AutoGen, OpenAI Assistants | Exploratory tasks, creative work | LLM-driven, message-based |
| **Collaborative Execution** | CrewAI, Agency Swarm | Multi-specialty tasks, research | Role-based, delegation-driven |
| **Optimizable Programs** | DSPy | ML pipelines, performance-critical | Declarative, compile/optimize |

---

## Framework Comparison Matrix

| Framework | Execution Model | Checkpointing | Observability | Governance | Production Ready | Best Fit for RaiSE |
|-----------|----------------|---------------|---------------|------------|------------------|-------------------|
| **LangGraph** | State graph w/ conditional edges | ✅ Automatic | ⭐⭐⭐ LangSmith tracing | ⭐⭐⭐ Interrupt pattern | ⭐⭐⭐⭐⭐ | **✅ Highest** |
| **CrewAI** | Sequential/hierarchical agents | ❌ None | ⭐⭐ Task logs | ⭐⭐ Human tool | ⭐⭐⭐ | ⚠️ Limited structure |
| **AutoGen** | Conversation-driven | ❌ None | ⭐⭐ Message logs | ⭐⭐⭐ Proxy pattern | ⭐⭐⭐ | ⚠️ Emergent flow |
| **Semantic Kernel** | Plugin/planner orchestration | ❌ None | ⭐⭐⭐ OpenTelemetry | ⭐⭐⭐ Filter pattern | ⭐⭐⭐⭐⭐ | ✅ Governance patterns |
| **DSPy** | Module composition + compile | ❌ None | ⭐⭐ Trace inspection | ⭐⭐⭐ Assertions | ⭐⭐⭐⭐ | ✅ Verification pattern |
| **Agency Swarm** | CEO delegation hierarchy | ❌ None | ⭐⭐ Message/tool logs | ⭐ CEO approval | ⭐⭐ | ❌ Early stage |
| **Rivet** | Visual dataflow graph | ✅ Manual snapshots | ⭐⭐⭐ Visual execution | ⭐⭐ Approval nodes | ⭐⭐ Dev only | ✅ Visual inspiration |
| **Claude MCP** | Protocol (not framework) | N/A | ⭐ Protocol logging | ❌ App-level | N/A | ❌ Not orchestration |
| **OpenAI Assistants** | Thread-based runs | ✅ Thread-level | ⭐⭐ Run steps | ⭐⭐ Required actions | ⭐⭐⭐⭐ | ⚠️ Limited control |

**Legend**: ⭐ = Limited, ⭐⭐ = Basic, ⭐⭐⭐ = Good, ⭐⭐⭐⭐ = Excellent, ⭐⭐⭐⭐⭐ = Industry-leading

---

## Critical Patterns for RaiSE Kata Harness

### 1. Execution Model: Graph-Based (LangGraph-inspired)

**Why?**
- Katas have **explicit steps** → Graph nodes
- Katas support **branching** and **cycles** → Conditional edges
- Clear **verification points** → Node boundaries
- **Jidoka requires pause/resume** → Checkpointing

**Pattern**:
```python
# Pseudo-code illustration
kata_graph = StateGraph(KataState)
kata_graph.add_node("step_1", step_1_func)
kata_graph.add_node("verification_1", verify_1_func)
kata_graph.add_conditional_edges(
    "verification_1",
    route_on_verification,
    {"pass": "step_2", "fail": "jidoka_handler"}
)
kata_graph.add_node("validation_gate", gate_func)
```

### 2. Checkpointing: Automatic per Step (LangGraph pattern)

**Why?**
- **Jidoka demands STOP capability** → Must save state
- **Learning requires replay** → Checkpoint history
- **Human intervention** → Resume from exact point

**Pattern**:
- Checkpoint **before** each step execution
- Checkpoint **after** each step execution
- Support resume from any checkpoint
- Enable time-travel debugging for learning

### 3. Verification: Assertion-Based (DSPy-inspired)

**Why?**
- Every Kata step has **"Verificación"** criteria
- Inline checks match Kata structure
- Automatic retry with feedback

**Pattern**:
```python
# Pseudo-code
@kata_step
def step_1(state):
    result = perform_action(state)

    # Inline verification (DSPy-style)
    verify(
        condition=meets_criteria(result),
        message="Verificación: Result meets quality criteria"
    )

    # Jidoka block
    if not meets_criteria(result):
        trigger_jidoka("Criteria not met → Check inputs")

    return {"result": result}
```

### 4. Validation Gates: Interrupt Pattern (LangGraph pattern)

**Why?**
- Katas have **explicit Validation Gates**
- Gates may require **human judgment**
- Clean pause/resume API

**Pattern**:
```python
# Mark gate nodes for interruption
kata_graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["validation_gate_design", "validation_gate_implementation"]
)

# Resume after gate approval
kata_graph.invoke(state, config={"thread_id": "kata_123"})
```

### 5. Observability: OpenTelemetry + Step Traces (Semantic Kernel pattern)

**Why?**
- **Production-ready** monitoring
- **Learning analytics** from trace data
- Industry-standard tooling

**Pattern**:
- Each Kata step = trace span
- Capture: inputs, outputs, verification results, duration
- Aggregate for learning insights
- Integration with standard observability platforms

### 6. Governance: Multi-Layered (Hybrid pattern)

**Why?**
- **Inline verification** (DSPy assertions)
- **Validation Gates** (LangGraph interrupts)
- **Policy enforcement** (Semantic Kernel filters)

**Governance Stack**:
```
Layer 1: Inline Verification (assertions in each step)
Layer 2: Validation Gates (interrupt before gate nodes)
Layer 3: Policy Filters (cross-cutting concerns)
Layer 4: Human Oversight (manual intervention points)
```

### 7. Context Management: Typed State + Artifact Registry (Hybrid)

**Why?**
- **Kata State**: Explicit inputs/outputs per step (LangGraph)
- **Artifact Registry**: Work products for gates (Semantic Kernel plugins)
- Clear handoffs between Katas

**Pattern**:
```python
class KataState(TypedDict):
    kata_id: str
    current_step: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    verification_results: List[VerificationResult]
    artifacts: List[str]  # References to artifact registry

class ArtifactRegistry:
    def store(self, artifact_type: str, content: Any) -> str:
        """Store work product, return reference"""

    def retrieve(self, reference: str) -> Any:
        """Retrieve work product by reference"""
```

---

## Recommended Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Kata Harness                             │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Kata      │  │  Execution   │  │   Checkpoint     │   │
│  │ Definition  │─▶│   Graph      │─▶│    Manager       │   │
│  │  (Markdown) │  │  (Nodes +    │  │ (Persistence)    │   │
│  └─────────────┘  │   Edges)     │  └──────────────────┘   │
│                    └──────────────┘                          │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Governance Layer                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │   │
│  │  │  Assertions  │  │    Gates     │  │  Filters   │ │   │
│  │  │  (Inline)    │  │ (Interrupt)  │  │ (Policy)   │ │   │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Observability Layer                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │   │
│  │  │    Traces    │  │   Metrics    │  │   Logs     │ │   │
│  │  │(OpenTelemetry│  │  (Step-level)│  │ (Structured│ │   │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                   │
│                           ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Context Layer                                │   │
│  │  ┌──────────────┐  ┌──────────────┐                  │   │
│  │  │ Kata State   │  │  Artifact    │                  │   │
│  │  │ (Typed Dict) │  │  Registry    │                  │   │
│  │  └──────────────┘  └──────────────┘                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow

```
1. Load Kata Definition (Markdown)
   ↓
2. Build Execution Graph (Nodes = Steps, Edges = Transitions)
   ↓
3. Execute Graph with Checkpointing
   ├─ Before each step: Save checkpoint
   ├─ Execute step function
   ├─ Run inline verification (assertion)
   ├─ If fail → Jidoka handler (STOP, human intervention)
   ├─ If pass → Continue
   └─ After each step: Save checkpoint
   ↓
4. Validation Gate (interrupt pattern)
   ├─ Pause execution
   ├─ Evaluate gate criteria
   ├─ If fail → Jidoka handler
   └─ If pass → Resume
   ↓
5. Next Kata or Complete
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Source Analysis |
|-------------|---------|-----------------|
| **Emergent workflows** | Katas have explicit structure; don't rely on LLM to decide flow | AutoGen, CrewAI |
| **No checkpointing** | Jidoka requires pause/resume; must save state | Most frameworks lack this |
| **Log-only observability** | Need structured telemetry for learning analytics | CrewAI, AutoGen |
| **Implicit context** | Kata state must be explicit and typed | Message history approach |
| **Manual retry** | Jidoka blocks should trigger automatic handling | Most frameworks |
| **No inline verification** | Every step needs "Verificación" criteria | Frameworks without assertions |

---

## Implementation Priorities

### Phase 1: Core Execution (MVP)
- [ ] Graph builder from Kata Markdown
- [ ] State management (typed schema)
- [ ] Basic checkpointing (SQLite)
- [ ] Step execution engine

### Phase 2: Governance
- [ ] Inline verification (assertions)
- [ ] Validation Gates (interrupt pattern)
- [ ] Jidoka handler (STOP, human intervention)

### Phase 3: Observability
- [ ] OpenTelemetry integration
- [ ] Step-level traces
- [ ] Verification result capture
- [ ] Learning analytics queries

### Phase 4: Advanced Features
- [ ] Policy filters (cross-cutting)
- [ ] Artifact registry
- [ ] Multi-Kata workflows
- [ ] Time-travel debugging

---

## Decision Summary

| Decision | Rationale | Framework Inspiration |
|----------|-----------|---------------------|
| **Graph-based execution** | Explicit Kata steps, cycles, branching | LangGraph |
| **Automatic checkpointing** | Jidoka pause/resume, learning replay | LangGraph |
| **Assertion-based verification** | Inline "Verificación" in Kata steps | DSPy |
| **Interrupt pattern for gates** | Clean pause for Validation Gates | LangGraph |
| **Typed state schema** | Clear Kata inputs/outputs | LangGraph |
| **OpenTelemetry traces** | Production-ready observability | Semantic Kernel |
| **Step replay capability** | Learning and debugging | LangGraph + Rivet |
| **Filter hooks for policy** | Custom governance rules | Semantic Kernel |
| **Artifact-based handoffs** | Clear boundaries between Katas | Semantic Kernel plugins |

---

## References

### Full Analysis Documents

1. **Detailed Comparison**: `specs/main/research/agent-frameworks-architecture-comparison.md`
   - In-depth analysis of each framework
   - Execution models, observability, governance, context management
   - Architecture diagrams per framework

2. **Visual Comparison**: `specs/main/research/agent-frameworks-visual-comparison.md`
   - Side-by-side visual comparisons
   - Execution flow diagrams
   - Pattern comparisons

3. **This Document**: `specs/main/research/agent-frameworks-executive-summary.md`
   - Quick reference
   - Key findings and recommendations

### Framework Documentation

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **CrewAI**: https://docs.crewai.com/
- **AutoGen**: https://microsoft.github.io/autogen/
- **Semantic Kernel**: https://learn.microsoft.com/en-us/semantic-kernel/
- **DSPy**: https://dspy-docs.vercel.app/
- **Agency Swarm**: https://github.com/VRSEN/agency-swarm
- **Rivet**: https://rivet.ironcladapp.com/
- **Claude MCP**: https://modelcontextprotocol.io/
- **OpenAI Assistants**: https://platform.openai.com/docs/assistants/overview

---

## Next Steps

1. **Architecture Design**:
   - Design detailed Kata Harness architecture based on recommended patterns
   - Define interfaces for each layer
   - Create data models (KataState, VerificationResult, etc.)

2. **Prototype**:
   - Build MVP with graph execution + checkpointing
   - Test with existing Katas
   - Validate Jidoka handler flow

3. **Integrate Governance**:
   - Implement inline verification (assertions)
   - Implement Validation Gates (interrupt pattern)
   - Build Jidoka handler

4. **Add Observability**:
   - OpenTelemetry integration
   - Define telemetry schema for Kata execution
   - Build learning analytics queries

5. **Validate with RaiSE Team**:
   - Review architecture against RaiSE principles
   - Validate against real Kata use cases
   - Iterate based on feedback

---

**Document Status**: Complete
**Date**: 2026-01-29
**Author**: Research via Claude Code
**Version**: 1.0.0
