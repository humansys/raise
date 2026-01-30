---
id: research-agent-frameworks-quick-reference
titulo: Agent Framework Patterns - Quick Reference Card
tipo: Research Document - Quick Reference
fecha: 2026-01-29
version: 1.0.0
tags:
  - research
  - quick-reference
  - patterns
  - kata-harness
---

# Agent Framework Patterns - Quick Reference Card

**Purpose**: One-page reference for key patterns from agent framework analysis.

---

## ⚡ Quick Decision Guide

**Need to choose an execution pattern?**

```
Is workflow structure explicit and known upfront?
├─ Yes → Graph-Based (LangGraph, Rivet)
│   └─ Complex branching/cycles? → LangGraph
│   └─ Visual prototyping? → Rivet
│
└─ No, workflow emerges from interactions
    ├─ Multi-agent collaboration? → Agent-Based (CrewAI, AutoGen)
    │   └─ Hierarchical teams? → CrewAI, Agency Swarm
    │   └─ Peer collaboration? → AutoGen
    │
    └─ Single assistant? → Conversational (OpenAI Assistants)
```

**For RaiSE Kata Harness**: Graph-Based (LangGraph pattern) - Katas are explicit, structured workflows.

---

## 🏗️ Core Patterns Summary

### Execution Models

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **State Graph** | Explicit steps, branching, cycles | LangGraph: `StateGraph` with conditional edges |
| **Pipeline** | Linear processing, function chaining | Semantic Kernel: Plugin composition |
| **Conversation** | Exploratory, adaptive workflows | AutoGen: Multi-agent chat |
| **Delegation** | Hierarchical task breakdown | CrewAI: CEO → Specialists |
| **Dataflow** | Visual workflows, prototyping | Rivet: Node graph with wires |

### Governance Patterns

| Pattern | How It Works | Code Snippet |
|---------|--------------|--------------|
| **Interrupt** | Pause at node, resume later | `compile(interrupt_before=["gate"])` |
| **Assertion** | Inline check with auto-retry | `verify(condition, "Error msg")` |
| **Filter** | Intercept function calls | `kernel.FunctionInvoking += handler` |
| **Proxy** | Dedicated human agent | `UserProxyAgent(human_input_mode="ALWAYS")` |
| **Required Action** | API pause for tool output | `run.status == "requires_action"` |

### Context Patterns

| Pattern | Data Structure | When to Use |
|---------|---------------|-------------|
| **State Object** | `TypedDict` with reducers | Bounded, typed context |
| **Message History** | List of messages | Conversational context |
| **Context Variables** | Key-value dict | Explicit parameter passing |
| **Task Output Chain** | Output N → Input N+1 | Sequential pipelines |
| **Semantic Memory** | Vector store | Long-term, searchable context |

---

## 🎯 Pattern Selection Matrix

### By Requirement

| Requirement | Best Pattern | Framework |
|-------------|--------------|-----------|
| Explicit workflow structure | State Graph | LangGraph |
| Pause/resume execution | Checkpointing | LangGraph |
| Inline validation | Assertions | DSPy |
| Human approval gates | Interrupt Pattern | LangGraph |
| Production observability | OpenTelemetry | Semantic Kernel |
| Policy enforcement | Filter Hooks | Semantic Kernel |
| Multi-agent collaboration | Agent Teams | CrewAI, AutoGen |
| Visual workflow design | Dataflow Graph | Rivet |
| Conversation-driven | Message Passing | AutoGen, OpenAI |

### By Complexity Level

| Complexity | Supported Frameworks | Pattern Choice |
|------------|---------------------|----------------|
| Linear (A→B→C) | All | Any pipeline/graph |
| Branching (if/else) | LangGraph, Rivet, Semantic Kernel | Conditional edges |
| Cycles (loops) | LangGraph, Rivet | Graph with back-edges |
| Parallel execution | LangGraph, Rivet | Parallel edges |
| Dynamic routing | LangGraph, AutoGen, OpenAI | Conditional/LLM-driven |
| Multi-agent coordination | CrewAI, AutoGen, Agency Swarm | Agent collaboration |

---

## 🔍 Observability Quick Guide

### Telemetry Approaches

| Approach | Pros | Cons | Use For |
|----------|------|------|---------|
| **Span-based (OpenTelemetry)** | Production-ready, structured | Setup overhead | Production systems |
| **Log-based** | Simple, human-readable | Hard to query | Development |
| **Visual execution** | Best DX | Not for production | Prototyping |
| **Step tracking** | Clean API | Limited detail | Managed services |

### What to Capture

```yaml
Essential Telemetry:
  - trace_id: Unique execution identifier
  - span_id: Unique step identifier
  - step_name: "step_1", "verification_1", "gate_design"
  - inputs: Step input data
  - outputs: Step output data
  - duration: Execution time
  - status: success | failure | skipped

For Learning:
  - verification_result: pass | fail
  - verification_criteria: What was checked
  - jidoka_triggered: true | false
  - human_intervention: true | false
  - retry_count: Number of retries

For Production:
  - error_type: Exception class
  - error_message: Error details
  - token_usage: LLM token counts
  - cost: Estimated execution cost
```

---

## ✅ Governance Checklist

### Inline Verification (Every Step)

```python
# Pattern: DSPy-style assertions
def step_function(state):
    result = perform_action(state)

    # Verification
    verify(
        condition=meets_criteria(result),
        message="Verificación: [Observable criteria]"
    )

    # Jidoka block
    if not meets_criteria(result):
        trigger_jidoka("Si no puedes continuar: [Condition] → [Action]")

    return state_update
```

### Validation Gates (Between Phases)

```python
# Pattern: LangGraph interrupt
workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["gate_design", "gate_implementation"]
)

# Resume after gate
result = workflow.invoke(
    state,
    config={"configurable": {"thread_id": "kata_123"}}
)
```

### Policy Enforcement (Cross-Cutting)

```python
# Pattern: Semantic Kernel filters
@kernel.filter
def governance_filter(context, next):
    # Pre-execution checks
    if requires_approval(context):
        if not get_approval(context):
            raise PolicyViolation("Approval required")

    # Execute
    result = next(context)

    # Post-execution checks
    audit_log(context, result)

    return result
```

---

## 🚫 Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Fix |
|-------------|---------|-----|
| No checkpointing | Can't pause/resume | Add checkpoint manager |
| Implicit context | Hard to debug | Use typed state schema |
| Log-only observability | Can't query/analyze | Add structured telemetry |
| Manual retry logic | Inconsistent, error-prone | Use assertion-based retry |
| No verification criteria | Can't determine success | Add explicit "Verificación" |
| Emergent structure for fixed workflows | Unpredictable, unreliable | Use graph-based execution |

---

## 📋 Implementation Checklist

### MVP (Minimal Viable Pattern)

```
[ ] Execution Model
    [ ] Define state schema (TypedDict)
    [ ] Build graph from workflow definition
    [ ] Implement node execution engine
    [ ] Add conditional edges

[ ] Checkpointing
    [ ] Choose persistence (SQLite for MVP)
    [ ] Save state before/after each step
    [ ] Implement resume from checkpoint

[ ] Basic Governance
    [ ] Inline verification (assertions)
    [ ] Jidoka handler (STOP on fail)

[ ] Minimal Observability
    [ ] Log each step execution
    [ ] Capture verification results
```

### Production-Ready

```
[ ] Advanced Execution
    [ ] Parallel execution support
    [ ] Dynamic routing
    [ ] Cycle detection

[ ] Full Governance
    [ ] Validation Gates (interrupt pattern)
    [ ] Policy filters
    [ ] Human-in-the-loop integration
    [ ] Audit logging

[ ] Production Observability
    [ ] OpenTelemetry integration
    [ ] Metrics (duration, success rate)
    [ ] Distributed tracing
    [ ] Learning analytics queries

[ ] Context Management
    [ ] Artifact registry
    [ ] Memory management strategies
    [ ] Context window optimization

[ ] Reliability
    [ ] Error handling and recovery
    [ ] Retry policies
    [ ] Fallback strategies
    [ ] Circuit breakers
```

---

## 🎨 Code Templates

### Graph-Based Workflow

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

# Define state
class WorkflowState(TypedDict):
    input: str
    step_1_output: str
    step_2_output: str
    verification_passed: bool

# Define nodes
def step_1(state: WorkflowState) -> WorkflowState:
    result = process(state["input"])
    verify(is_valid(result), "Step 1 verification")
    return {"step_1_output": result}

def verification_check(state: WorkflowState) -> WorkflowState:
    passed = validate(state["step_1_output"])
    if not passed:
        trigger_jidoka("Validation failed")
    return {"verification_passed": passed}

def step_2(state: WorkflowState) -> WorkflowState:
    result = process(state["step_1_output"])
    return {"step_2_output": result}

# Build graph
workflow = StateGraph(WorkflowState)
workflow.add_node("step_1", step_1)
workflow.add_node("verify", verification_check)
workflow.add_node("step_2", step_2)

workflow.set_entry_point("step_1")
workflow.add_edge("step_1", "verify")
workflow.add_conditional_edges(
    "verify",
    lambda s: "step_2" if s["verification_passed"] else "jidoka",
    {"step_2": "step_2", "jidoka": "jidoka_handler"}
)

# Compile with checkpointing
app = workflow.compile(checkpointer=checkpointer)
```

### Assertion-Based Verification

```python
class VerificationError(Exception):
    pass

def verify(condition: bool, message: str, retry: bool = True):
    """DSPy-style assertion"""
    if not condition:
        if retry:
            raise VerificationError(f"RETRY: {message}")
        else:
            raise VerificationError(f"FAIL: {message}")

# Usage in step
def step_with_verification(state):
    result = perform_action(state)

    # Hard assertion (no retry)
    verify(
        result is not None,
        "Result must not be None",
        retry=False
    )

    # Soft assertion (with retry)
    verify(
        quality_check(result),
        "Result quality insufficient",
        retry=True
    )

    return {"result": result}
```

### Checkpoint Manager

```python
import sqlite3
import json

class CheckpointManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                workflow_id TEXT,
                step_name TEXT,
                state TEXT,
                timestamp REAL
            )
        """)

    def save(self, workflow_id: str, step_name: str, state: dict):
        self.conn.execute(
            "INSERT INTO checkpoints (workflow_id, step_name, state, timestamp) VALUES (?, ?, ?, ?)",
            (workflow_id, step_name, json.dumps(state), time.time())
        )
        self.conn.commit()

    def load(self, workflow_id: str, step_name: str = None) -> dict:
        if step_name:
            cursor = self.conn.execute(
                "SELECT state FROM checkpoints WHERE workflow_id = ? AND step_name = ? ORDER BY timestamp DESC LIMIT 1",
                (workflow_id, step_name)
            )
        else:
            cursor = self.conn.execute(
                "SELECT state FROM checkpoints WHERE workflow_id = ? ORDER BY timestamp DESC LIMIT 1",
                (workflow_id,)
            )

        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
```

---

## 📚 Framework Capabilities Grid

| Framework | Graph | Cycles | Parallel | Checkpoints | Tracing | Gates | HITL | Production |
|-----------|-------|--------|----------|-------------|---------|-------|------|------------|
| LangGraph | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Semantic Kernel | ⚠️ | ❌ | ✅ | ❌ | ⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| AutoGen | ❌ | ⚠️ | ❌ | ❌ | ⭐⭐ | ⚠️ | ✅ | ⭐⭐⭐ |
| CrewAI | ⚠️ | ❌ | ⚠️ | ❌ | ⭐⭐ | ⚠️ | ✅ | ⭐⭐⭐ |
| DSPy | ❌ | ❌ | ❌ | ❌ | ⭐⭐ | ✅ | ❌ | ⭐⭐⭐⭐ |
| Rivet | ✅ | ✅ | ✅ | ⚠️ | ⭐⭐⭐ | ✅ | ✅ | ⭐⭐ |
| OpenAI Assistants | ❌ | ❌ | ❌ | ⚠️ | ⭐⭐ | ⚠️ | ✅ | ⭐⭐⭐⭐ |

**Legend**: ✅ Full support | ⚠️ Partial/Limited | ❌ Not supported | ⭐ Quality rating

---

## 🎯 RaiSE Kata Harness Recommendation

**Execution**: Graph-Based (LangGraph pattern)
**Checkpointing**: Automatic per step (LangGraph pattern)
**Verification**: Assertion-based inline (DSPy pattern)
**Gates**: Interrupt pattern (LangGraph pattern)
**Observability**: OpenTelemetry (Semantic Kernel pattern)
**Governance**: Multi-layered (Assertions + Gates + Filters)
**Context**: Typed state + Artifact registry (Hybrid)

**Why this combination?**
- Katas have **explicit structure** → Graph execution
- Jidoka requires **pause/resume** → Checkpointing
- Every step has **"Verificación"** → Assertions
- Validation Gates are **explicit** → Interrupt pattern
- Need **production observability** → OpenTelemetry
- Multiple **governance layers** → Hybrid approach

---

## 🔗 Quick Links

- **Full Analysis**: `specs/main/research/agent-frameworks-architecture-comparison.md`
- **Visual Comparison**: `specs/main/research/agent-frameworks-visual-comparison.md`
- **Executive Summary**: `specs/main/research/agent-frameworks-executive-summary.md`
- **This Reference**: `specs/main/research/agent-frameworks-quick-reference.md`

---

**Last Updated**: 2026-01-29
**Version**: 1.0.0
