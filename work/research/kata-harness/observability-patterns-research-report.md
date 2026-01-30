# Observability Patterns for AI Agent Systems: Research Report

**Research ID**: RES-KATA-OBS-001
**Date**: 2026-01-29
**Researcher**: Claude Opus 4.5
**Requestor**: RaiSE Framework Team
**Purpose**: Define observability architecture for Kata Harness execution

---

## Executive Summary

This report synthesizes observability patterns from the LLM ecosystem to inform the design of RaiSE's Kata Harness observability layer. The research covers:

1. **Tracing standards and tools** (OpenTelemetry, LangSmith, Arize Phoenix, OpenLLMetry)
2. **Data models** for capturing agent execution
3. **Audit and compliance** requirements
4. **Real-time vs post-hoc** observability patterns
5. **Specific recommendations** for RaiSE's Jidoka-centric architecture

**Key Finding**: The LLM observability ecosystem has converged on a **hierarchical span model** (traces → runs → steps) with rich semantic attributes. However, most tools focus on *debugging* and *performance optimization*, not *governance enforcement*. RaiSE's requirement for **stop-the-line observability** (Jidoka) is underserved in current tools.

**Recommendation**: Adopt a **hybrid approach**:
- Use OpenTelemetry-compatible data model for interoperability
- Add RaiSE-specific spans for governance events (gate checks, Jidoka stops, policy decisions)
- Store locally-first (JSONL) per ADR-008, with optional export to OTLP collectors
- Build custom Jidoka dashboard focused on *governance metrics*, not just performance metrics

---

## 1. Tracing Standards & Tools

### 1.1 OpenTelemetry for LLM Applications

**Status**: Emerging standard (as of Jan 2025)

**Semantic Conventions for GenAI** (OTEL GenAI spec v1.0.0):

The OpenTelemetry community has defined semantic conventions specifically for Generative AI applications:

**Trace Structure**:
```
Trace (workflow execution)
  └─ Span (LLM call)
      ├─ Attributes
      │   ├─ gen_ai.system = "openai|anthropic|google"
      │   ├─ gen_ai.request.model = "gpt-4|claude-opus-4.5"
      │   ├─ gen_ai.request.temperature
      │   ├─ gen_ai.request.max_tokens
      │   ├─ gen_ai.request.top_p
      │   ├─ gen_ai.usage.input_tokens
      │   ├─ gen_ai.usage.output_tokens
      │   ├─ gen_ai.usage.total_tokens
      │   └─ gen_ai.response.finish_reason
      └─ Events
          ├─ gen_ai.content.prompt (with timestamp)
          └─ gen_ai.content.completion (with timestamp)
```

**Tool Use Extensions**:
```
Span (tool_use)
  ├─ gen_ai.tool.name
  ├─ gen_ai.tool.input (JSON)
  ├─ gen_ai.tool.output (JSON)
  ├─ gen_ai.tool.duration_ms
  └─ gen_ai.tool.status = "success|error|timeout"
```

**Strengths**:
- Vendor-neutral, widely adopted
- Integrates with existing APM tools (DataDog, New Relic, Honeycomb)
- Rich ecosystem of exporters and collectors
- Support for distributed tracing (multi-service)

**Weaknesses**:
- Focused on technical telemetry (performance, errors)
- No built-in concepts for *governance* (gates, policies, compliance)
- Doesn't capture *reasoning* or *decision rationale*
- Complex to set up for local-first use cases

**Applicability to RaiSE**:
- ✅ Use as **base data model** for interoperability
- ✅ Adopt span model and semantic conventions
- ⚠️ Extend with RaiSE-specific attributes for governance
- ❌ Don't require OTLP collectors as primary storage (ADR-008 local-first)

---

### 1.2 LangSmith (LangChain)

**Status**: Production, widely adopted (2024-2025)

**Architecture**:

LangSmith uses a **run-centric** model:

```
Project
  └─ Trace (end-to-end execution)
      └─ Run (single step/operation)
          ├─ Type: llm | chain | tool | retriever | agent
          ├─ Inputs (dict)
          ├─ Outputs (dict)
          ├─ Metadata (tags, user_id, session_id)
          ├─ Start time, end time
          ├─ Token usage
          ├─ Error (if failed)
          └─ Feedback (human annotations)
```

**Key Data Model**:

```json
{
  "id": "run_abc123",
  "name": "ChatOpenAI",
  "run_type": "llm",
  "inputs": {
    "prompts": ["What is the capital of France?"]
  },
  "outputs": {
    "generations": [{"text": "The capital of France is Paris."}]
  },
  "parent_run_id": "chain_xyz789",
  "trace_id": "trace_456",
  "start_time": "2025-01-29T10:00:00Z",
  "end_time": "2025-01-29T10:00:02.5Z",
  "extra": {
    "model_name": "gpt-4",
    "temperature": 0.7
  },
  "tags": ["production", "customer-support"],
  "feedback_stats": {
    "thumbs_up": 5,
    "thumbs_down": 1
  }
}
```

**Run Types** (from LangChain):
- `llm`: Direct LLM call
- `chain`: Sequence of operations
- `tool`: Tool/function execution
- `retriever`: Vector search / RAG retrieval
- `agent`: Agentic decision-making
- `prompt`: Prompt template rendering

**Feedback System**:
LangSmith allows attaching human feedback to runs:
```json
{
  "run_id": "run_abc123",
  "key": "correctness",
  "score": 0.8,
  "comment": "Good but missing context",
  "correction": {
    "expected_output": "..."
  }
}
```

**Strengths**:
- **Rich context capture**: Inputs/outputs at every step
- **Human-in-the-loop**: Feedback annotations for improvement
- **Hierarchical nesting**: Parent-child run relationships
- **Metadata flexibility**: Tags for filtering/grouping
- **Replay capability**: Can reconstruct execution from trace

**Weaknesses**:
- **Cloud-only** (SaaS, no self-hosted option)
- **LangChain-centric** (tight coupling to LangChain abstractions)
- **No governance primitives**: Doesn't model gates, policies, or compliance checks
- **Performance focus**: Metrics are latency/cost, not adherence/quality

**Applicability to RaiSE**:
- ✅ Adopt **run-centric hierarchy** (trace → run)
- ✅ Capture **inputs/outputs** at each step
- ✅ Include **parent_run_id** for nesting
- ✅ Support **feedback/annotations** for Jidoka learning
- ❌ Don't require cloud storage (ADR-008)
- ⚠️ Add **governance run types**: gate_check, policy_eval, jidoka_stop

---

### 1.3 Arize Phoenix

**Status**: Open-source, production (2024-2025)

**Architecture**:

Phoenix is an **open-source observability platform** specifically for LLM applications. It focuses on:
- Tracing (similar to LangSmith)
- Evaluation (model quality metrics)
- Drift detection (input/output distribution changes)

**Data Model**:

```json
{
  "span_id": "span_123",
  "trace_id": "trace_456",
  "parent_id": "span_parent",
  "name": "retrieve_context",
  "kind": "RETRIEVER",
  "start_time": "2025-01-29T10:00:00Z",
  "end_time": "2025-01-29T10:00:01Z",
  "status_code": "OK",
  "attributes": {
    "llm.model_name": "text-embedding-ada-002",
    "llm.input_messages": [...],
    "llm.output_messages": [...],
    "retrieval.documents": [...],
    "embedding.vector_db": "pinecone"
  },
  "events": [
    {
      "name": "query_vector_db",
      "timestamp": "2025-01-29T10:00:00.5Z",
      "attributes": {
        "query": "...",
        "top_k": 5
      }
    }
  ]
}
```

**Span Kinds** (Phoenix-specific):
- `LLM`: Language model inference
- `RETRIEVER`: RAG retrieval step
- `EMBEDDING`: Embedding generation
- `RERANKER`: Reranking step
- `TOOL`: Tool/function call
- `CHAIN`: Sequence of operations
- `AGENT`: Agentic execution

**Evaluation Framework**:

Phoenix includes built-in evaluators:
```python
# Example: Hallucination detection
{
  "span_id": "span_123",
  "eval_name": "hallucination_score",
  "score": 0.85,  # 0-1, higher = less hallucination
  "label": "factual",
  "explanation": "Output aligns with retrieved context",
  "evaluator": "gpt-4-eval-v2"
}
```

**Drift Detection**:

Phoenix tracks distribution shifts:
```json
{
  "dataset": "production_traces",
  "time_window": "2025-01-22 to 2025-01-29",
  "drift_metrics": {
    "input_token_length": {
      "mean_baseline": 450,
      "mean_current": 520,
      "psi": 0.15  // Population Stability Index
    },
    "output_sentiment": {
      "distribution_shift": "significant",
      "psi": 0.42
    }
  }
}
```

**Strengths**:
- **Open-source** (Apache 2.0)
- **Self-hosted** option (Docker, K8s)
- **Evaluation-first**: Built-in quality metrics
- **Drift detection**: Catches degradation over time
- **LLM-agnostic**: Works with any provider

**Weaknesses**:
- **Limited governance**: No gate/policy concepts
- **Evaluation overhead**: Running evals on every span is costly
- **Complex setup**: Requires backend infrastructure

**Applicability to RaiSE**:
- ✅ Use **evaluation framework** concept for gate checks
- ✅ Adopt **drift detection** for kata quality monitoring
- ✅ Self-hosted aligns with ADR-008 local-first
- ⚠️ Simplify: Don't require full Phoenix deployment for basic use
- ⚠️ Extend: Add RaiSE governance span kinds

---

### 1.4 OpenLLMetry

**Status**: Open-source, emerging (2024-2025)

**Description**: OpenLLMetry (by Traceloop) is an **OpenTelemetry-native** instrumentation library for LLM applications.

**Key Features**:
- Auto-instrumentation for LangChain, LlamaIndex, Anthropic, OpenAI SDKs
- Exports to any OTLP-compatible backend (Jaeger, Tempo, DataDog)
- Semantic conventions aligned with OTEL GenAI spec

**Instrumentation Example**:

```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument()

# Now all OpenAI calls are automatically traced
client.chat.completions.create(
    model="gpt-4",
    messages=[...]
)
```

**Trace Output** (OTLP format):
```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": "kata-harness"}
        ]
      },
      "scopeSpans": [
        {
          "scope": {"name": "openai"},
          "spans": [
            {
              "traceId": "abc123",
              "spanId": "def456",
              "name": "chat",
              "kind": "CLIENT",
              "startTimeUnixNano": 1643723400000000000,
              "endTimeUnixNano": 1643723402000000000,
              "attributes": [
                {"key": "gen_ai.system", "value": "openai"},
                {"key": "gen_ai.request.model", "value": "gpt-4"},
                {"key": "gen_ai.usage.input_tokens", "value": 150},
                {"key": "gen_ai.usage.output_tokens", "value": 80}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Strengths**:
- **Zero-code instrumentation**: Auto-instrument popular libraries
- **Standards-based**: Uses OTLP, works with any OTEL backend
- **Vendor-neutral**: Not tied to any observability platform

**Weaknesses**:
- **Infrastructure required**: Needs OTLP collector + backend
- **No governance features**: Pure telemetry, no policy enforcement
- **Limited context capture**: Only captures SDK-level data

**Applicability to RaiSE**:
- ✅ Use for **automatic LLM call tracing**
- ⚠️ Don't require OTLP infrastructure for basic use (ADR-008)
- ❌ Not sufficient alone: Doesn't capture Kata-specific context

---

### 1.5 Comparison Matrix

| Tool | Data Model | Storage | Governance | Self-Hosted | LLM-Agnostic | Complexity |
|------|-----------|---------|------------|-------------|--------------|------------|
| **OpenTelemetry** | Spans, Events | OTLP collectors | ❌ | ✅ | ✅ | High |
| **LangSmith** | Runs (nested) | Cloud SaaS | ❌ | ❌ | ✅ | Low |
| **Arize Phoenix** | Spans + Evals | Self-hosted | ⚠️ (evals) | ✅ | ✅ | Medium |
| **OpenLLMetry** | OTLP spans | Any OTLP backend | ❌ | ✅ | ✅ | Medium |

**Legend**:
- ✅ Full support
- ⚠️ Partial support
- ❌ Not supported

---

## 2. What to Observe: Data Model for Kata Execution

### 2.1 Observability Primitives

Based on analysis of existing tools and RaiSE requirements, a Kata execution trace should capture:

#### 2.1.1 Trace Level (Kata Execution)

```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "kata_id": "flujo-001-discovery",
  "kata_version": "2.1.0",
  "session_id": "sess_xyz789",
  "orchestrator": {
    "human_id_hash": "user_abcd1234",  // Anonymized
    "agent": "claude-opus-4.5",
    "context_loaded": [
      "raise://constitution",
      "raise://glossary",
      "raise://guardrails/design"
    ]
  },
  "start_time": "2026-01-29T10:30:00Z",
  "end_time": "2026-01-29T10:45:30Z",
  "status": "completed|failed|jidoka_stopped",
  "work_cycle": "project",  // project | feature | setup | improve
  "spec_id": "001-auth-feature",
  "jidoka_events": [
    {
      "step": "Gate-Design",
      "timestamp": "2026-01-29T10:35:00Z",
      "reason": "Missing architecture decision rationale",
      "action": "stopped_for_human_input"
    }
  ],
  "metadata": {
    "environment": "local|ci",
    "project_id": "raise-commons",
    "branch": "PRAISE-36-ontology-standarization"
  }
}
```

**Key fields**:
- `trace_id`: Unique identifier for this kata execution
- `kata_id`: Which kata was executed (from `.raise/katas/`)
- `session_id`: Groups multiple kata executions in same work session
- `context_loaded`: Which RaiSE context was available (constitution, guardrails, etc.)
- `jidoka_events`: Critical governance events (stop-the-line)
- `work_cycle`: Which Work Cycle this execution belongs to

#### 2.1.2 Step Level (Kata Step Execution)

Each step in the kata outline generates a **step span**:

```json
{
  "span_id": "step_002",
  "trace_id": "kata_exec_20260129_103045_abc123",
  "parent_span_id": "step_001",
  "step_number": 2,
  "step_name": "Cargar Vision y Contexto",
  "step_type": "load_context|execute_tool|gate_check|llm_decision",
  "start_time": "2026-01-29T10:32:00Z",
  "end_time": "2026-01-29T10:33:15Z",
  "duration_ms": 75000,
  "status": "success|failed|skipped|jidoka",
  "inputs": {
    "files_loaded": [
      "specs/main/solution_vision.md",
      "specs/main/project_requirements.md"
    ],
    "context_tokens": 3200
  },
  "outputs": {
    "summary": "Solution vision defines a developer productivity platform...",
    "key_requirements": ["REQ-001", "REQ-002"],
    "tokens_generated": 150
  },
  "llm_calls": [
    {
      "call_id": "llm_001",
      "model": "claude-opus-4.5",
      "input_tokens": 3200,
      "output_tokens": 150,
      "duration_ms": 2500,
      "cost_usd": 0.05
    }
  ],
  "tool_calls": [
    {
      "tool": "read_file",
      "file": "specs/main/solution_vision.md",
      "duration_ms": 100
    }
  ],
  "verification": {
    "criteria": "Solution Vision exists and context is clear",
    "verified": true,
    "evidence": "Files loaded successfully, 2 key requirements identified"
  },
  "jidoka_check": {
    "condition": "Solution Vision not found",
    "triggered": false
  }
}
```

**Key fields**:
- `step_number`: Position in kata sequence (for ordering)
- `step_type`: Classification of step (for analytics)
- `verification`: Did the **Verificación** criteria pass?
- `jidoka_check`: Was the **Si no puedes continuar** condition triggered?
- `llm_calls`: Token usage breakdown
- `tool_calls`: Tool execution details

#### 2.1.3 Gate Check Level

Gates are **first-class observability events**:

```json
{
  "span_id": "gate_001",
  "trace_id": "kata_exec_20260129_103045_abc123",
  "parent_span_id": "step_005",
  "gate_id": "gate-design",
  "gate_version": "2.1.0",
  "artifact_path": "specs/001-auth-feature/tech_design.md",
  "start_time": "2026-01-29T10:40:00Z",
  "end_time": "2026-01-29T10:40:30Z",
  "status": "passed|failed|waived",
  "checks": [
    {
      "check_id": "C001",
      "name": "Has architecture decision rationale",
      "result": "passed",
      "evidence": "Section '## Architecture Decision' found with 3 ADRs referenced"
    },
    {
      "check_id": "C002",
      "name": "Has data model definition",
      "result": "failed",
      "evidence": "Section '## Data Model' is empty",
      "severity": "must_fix"
    }
  ],
  "overall_score": 0.75,  // % of checks passed
  "waived_by": null,  // If gate was manually bypassed
  "llm_calls": [
    {
      "call_id": "llm_gate_001",
      "model": "claude-opus-4.5",
      "input_tokens": 2500,  // Gate prompt + artifact
      "output_tokens": 200,  // Gate result
      "duration_ms": 3000
    }
  ]
}
```

**Key fields**:
- `checks`: Individual gate criteria (from gate definition)
- `overall_score`: Aggregate compliance metric
- `waived_by`: Governance escape hatch (must be auditable)

#### 2.1.4 Jidoka Event Level

When execution stops (Jidoka), capture:

```json
{
  "event_id": "jidoka_001",
  "trace_id": "kata_exec_20260129_103045_abc123",
  "timestamp": "2026-01-29T10:35:00Z",
  "step_span_id": "step_003",
  "trigger": "verification_failed|gate_failed|missing_input|human_escalation",
  "condition": "Solution Vision not found",
  "action": "stop_execution",
  "message": "**JIDOKA**: Execute `/raise.2.vision` first",
  "resolution": {
    "type": "human_intervention",
    "resumed_at": "2026-01-29T11:00:00Z",
    "action_taken": "Executed /raise.2.vision, then resumed"
  }
}
```

**Key fields**:
- `trigger`: What caused the stop
- `condition`: The "Si no puedes continuar" condition that fired
- `message`: Guidance to orchestrator
- `resolution`: How was it resolved (for learning)

---

### 2.2 Token Usage and Cost Tracking

**Per-step token breakdown**:

```json
{
  "span_id": "step_002",
  "token_usage": {
    "input": {
      "prompt_template": 150,
      "context_loaded": 3200,  // Constitution, guardrails, etc.
      "artifacts": 1500,       // Specs, PRD, etc.
      "chat_history": 800,
      "total": 5650
    },
    "output": {
      "reasoning": 120,
      "content": 400,
      "tool_calls": 80,
      "total": 600
    },
    "total": 6250
  },
  "cost": {
    "input_cost_usd": 0.015,   // Based on model pricing
    "output_cost_usd": 0.018,
    "total_cost_usd": 0.033
  }
}
```

**Trace-level aggregation**:

```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "total_tokens": 45000,
  "total_cost_usd": 0.75,
  "token_breakdown_by_source": {
    "context_loading": 12000,
    "artifact_analysis": 18000,
    "reasoning": 8000,
    "tool_calls": 4000,
    "output_generation": 3000
  }
}
```

---

### 2.3 Latency Breakdown

**Per-step timing**:

```json
{
  "span_id": "step_003",
  "duration_ms": 8500,
  "breakdown": {
    "load_files": 200,
    "llm_inference": 6000,
    "tool_execution": 2000,
    "validation": 300
  }
}
```

**Trace-level critical path**:

```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "total_duration_ms": 930000,  // 15.5 minutes
  "critical_path": [
    {"step": "step_002", "duration_ms": 75000},
    {"step": "step_003", "duration_ms": 8500},
    {"step": "gate_001", "duration_ms": 30000}
  ],
  "bottlenecks": [
    {
      "step": "step_002",
      "reason": "Large context loading (3200 tokens)",
      "suggestion": "Consider caching frequently loaded contexts"
    }
  ]
}
```

---

### 2.4 Decision Points and Reasoning Traces

Capture **why** decisions were made:

```json
{
  "span_id": "step_004",
  "step_name": "Proponer Arquitectura",
  "decision_point": {
    "question": "Should we use monolithic or microservices architecture?",
    "options": [
      {
        "option": "monolithic",
        "rationale": "Team size <5, single deployment unit reduces complexity",
        "score": 0.7
      },
      {
        "option": "microservices",
        "rationale": "Better scalability, but overhead for small team",
        "score": 0.3
      }
    ],
    "chosen": "monolithic",
    "reasoning": "Lean principle: simplicity over premature optimization",
    "guardrail_checked": "raise://guardrails/design#YAGNI"
  }
}
```

---

### 2.5 Context Drift and Coherence Metrics

Track how context changes over execution:

```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "context_evolution": [
    {
      "step": "step_001",
      "context_window_tokens": 8000,
      "context_sources": ["constitution", "glossary"],
      "semantic_coherence": 0.95  // Cosine similarity to initial context
    },
    {
      "step": "step_010",
      "context_window_tokens": 7200,
      "context_sources": ["constitution", "glossary", "tech_design.md"],
      "semantic_coherence": 0.82,
      "drift_detected": true,
      "drift_reason": "Large artifact added, original constitution compressed"
    }
  ]
}
```

---

## 3. Audit Requirements

### 3.1 Compliance Logging Patterns

**Enterprise compliance** (SOC2, ISO 27001, EU AI Act) requires:

#### 3.1.1 Immutable Audit Trail

All governance events must be **tamper-evident**:

```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "audit_log": {
    "hash": "sha256:abc123...",
    "previous_hash": "sha256:def456...",
    "timestamp": "2026-01-29T10:30:00Z",
    "signed_by": "raise-agent-v2.3",
    "events": [...]
  }
}
```

**Blockchain pattern** (optional): Each trace links to previous trace hash, creating immutable chain.

#### 3.1.2 Who-What-When-Why

Every governance decision must capture:

```json
{
  "event_type": "gate_waived",
  "who": {
    "human_id_hash": "user_abc123",
    "agent": "claude-opus-4.5",
    "role": "tech_lead"
  },
  "what": {
    "gate_id": "gate-design",
    "check_id": "C002",
    "original_result": "failed",
    "waived_to": "passed"
  },
  "when": "2026-01-29T10:41:00Z",
  "why": "Data model will be defined in separate ADR-015",
  "approval": {
    "required": true,
    "approver": "architecture_council",
    "approval_id": "ARCH-2026-003"
  }
}
```

#### 3.1.3 Data Retention

Per ADR-008:
- **Default**: 30 days local retention
- **Governance events**: Never auto-delete (permanent archive)
- **PII**: Anonymize user IDs (hash with salt)

#### 3.1.4 Queryability

Support compliance queries:
- "Show all gate waivers in last 90 days"
- "Show all Jidoka stops for kata X"
- "Show all executions by user Y"
- "Show all decisions that referenced ADR Z"

**Query API**:

```bash
raise audit query \
  --event-type gate_waived \
  --date-range "2025-12-01 to 2026-01-29" \
  --output csv
```

---

### 3.2 Deterministic Replay from Traces

**Goal**: Reproduce execution from trace for debugging/auditing.

**Challenges**:
- LLMs are non-deterministic (even with `temperature=0`)
- Tool outputs may change (file system state, API responses)
- Context may evolve (specs updated since original execution)

**Approach**:

#### Capture Snapshot of Inputs

```json
{
  "span_id": "step_003",
  "inputs_snapshot": {
    "files": {
      "specs/main/solution_vision.md": {
        "hash": "sha256:abc123...",
        "content": "...",  // Optional: store content for replay
        "size_bytes": 2048
      }
    },
    "context": {
      "raise://constitution": {
        "version": "2.1.0",
        "hash": "sha256:def456..."
      }
    },
    "environment": {
      "cwd": "/home/user/project",
      "env_vars": {
        "RAISE_ENV": "local"
      }
    }
  }
}
```

#### Replay Mode

```bash
raise replay --trace-id kata_exec_20260129_103045_abc123
```

**Behavior**:
1. **Load snapshot**: Restore file system state, context versions
2. **Re-execute steps**: Run same kata with same inputs
3. **Compare outputs**: Diff actual vs. expected (from original trace)
4. **Report divergence**: Where did execution differ?

**Use cases**:
- **Regression testing**: Did kata behavior change after update?
- **Debugging**: What caused failure in production?
- **Auditing**: Verify claimed execution actually happened

---

### 3.3 Diff Between Expected and Actual Execution

**Per-step diff**:

```json
{
  "replay_id": "replay_20260129_120000",
  "original_trace_id": "kata_exec_20260129_103045_abc123",
  "diffs": [
    {
      "step": "step_003",
      "field": "outputs.summary",
      "expected": "Solution vision defines a developer productivity platform...",
      "actual": "Solution vision describes a developer productivity tool...",
      "similarity": 0.92,  // Cosine similarity
      "diff_type": "semantic_equivalent"
    },
    {
      "step": "gate_001",
      "field": "checks[1].result",
      "expected": "failed",
      "actual": "passed",
      "diff_type": "critical_divergence",
      "explanation": "Data model section was added to spec since original execution"
    }
  ]
}
```

---

## 4. Real-time vs Post-hoc Observability

### 4.1 Streaming Execution Feedback

**Real-time use case**: Orchestrator wants live progress updates during kata execution.

**Pattern**: **Server-Sent Events (SSE)** or **WebSocket**

```javascript
// Client subscribes to trace events
const eventSource = new EventSource('/api/traces/kata_exec_abc123/stream');

eventSource.addEventListener('step_started', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Step ${data.step_number}: ${data.step_name} started`);
});

eventSource.addEventListener('gate_failed', (event) => {
  const data = JSON.parse(event.data);
  alert(`Gate ${data.gate_id} failed: ${data.reason}`);
});
```

**Server emits events**:

```json
// Event: step_started
{
  "event": "step_started",
  "trace_id": "kata_exec_abc123",
  "step_number": 3,
  "step_name": "Proponer Arquitectura",
  "timestamp": "2026-01-29T10:35:00Z"
}

// Event: gate_failed
{
  "event": "gate_failed",
  "trace_id": "kata_exec_abc123",
  "gate_id": "gate-design",
  "checks_failed": ["C002"],
  "severity": "must_fix",
  "timestamp": "2026-01-29T10:40:00Z"
}

// Event: jidoka_triggered
{
  "event": "jidoka_triggered",
  "trace_id": "kata_exec_abc123",
  "step_number": 3,
  "condition": "Missing architecture decision rationale",
  "action_required": "Add ADR or waive gate",
  "timestamp": "2026-01-29T10:35:30Z"
}
```

**Benefits**:
- **Immediate feedback**: Orchestrator knows execution status
- **Early termination**: Can stop execution if critical issue detected
- **Progress tracking**: Show % completion in UI

---

### 4.2 Human-in-the-Loop Intervention Points

**Pattern**: **Blocking wait for human decision**

When Jidoka is triggered, execution **pauses** and waits for human input:

```json
{
  "event": "jidoka_triggered",
  "trace_id": "kata_exec_abc123",
  "awaiting_human_input": true,
  "options": [
    {
      "action": "fix_issue",
      "description": "Add missing ADR to tech design, then resume",
      "command": "raise resume --trace-id kata_exec_abc123"
    },
    {
      "action": "waive_gate",
      "description": "Waive gate check C002 (requires approval)",
      "command": "raise waive --trace-id kata_exec_abc123 --check C002 --reason '...'"
    },
    {
      "action": "abort",
      "description": "Abort execution, will require restart",
      "command": "raise abort --trace-id kata_exec_abc123"
    }
  ]
}
```

**Orchestrator UI**:

```
⚠️  JIDOKA: Execution Stopped

Step 3: Proponer Arquitectura
Gate: gate-design
Failed Check: C002 - Has data model definition

What would you like to do?

[1] Fix issue and resume
[2] Waive gate check (requires approval)
[3] Abort execution

Enter choice (1-3):
```

**Resume execution**:

```bash
# Orchestrator fixes issue (adds data model to spec)
vim specs/001-auth-feature/tech_design.md

# Resume kata execution
raise resume --trace-id kata_exec_abc123
```

**Trace captures intervention**:

```json
{
  "event_type": "human_intervention",
  "trace_id": "kata_exec_abc123",
  "jidoka_event_id": "jidoka_001",
  "paused_at": "2026-01-29T10:35:30Z",
  "resumed_at": "2026-01-29T11:00:00Z",
  "action_taken": "fix_issue",
  "changes_made": [
    {
      "file": "specs/001-auth-feature/tech_design.md",
      "section": "## Data Model",
      "git_commit": "abc123..."
    }
  ]
}
```

---

### 4.3 Post-execution Analysis and Improvement Loops

**Pattern**: **Batch analysis for continuous improvement**

After multiple kata executions, analyze trends:

**Weekly Report**:

```bash
raise metrics --week --output report.md
```

**Generated report**:

```markdown
# Kata Execution Metrics: Week of 2026-01-22

## Summary

- Total executions: 45
- Success rate: 82% (37/45)
- Jidoka stops: 12 (26%)
- Average duration: 12.5 minutes
- Total cost: $18.50

## Top Jidoka Triggers

| Condition | Count | % of Total |
|-----------|-------|------------|
| Missing architecture rationale | 5 | 42% |
| Incomplete test coverage | 3 | 25% |
| Undefined data model | 2 | 17% |
| Missing API contracts | 2 | 17% |

## Recommendations

1. **Update gate-design**: Add more specific criteria for "architecture rationale"
2. **Add kata step**: Include explicit "Define Data Model" step before gate check
3. **Context improvement**: Load example ADRs in context to guide orchestrators

## Token Usage Trends

- Average tokens per execution: 42,000
- Most expensive step: "Proponer Arquitectura" (avg 8,500 tokens)
- Opportunity: Cache constitution/glossary (saves ~3,000 tokens per exec)
```

**Kaizen (Continuous Improvement)**:

```json
{
  "improvement_id": "KAIZEN-2026-003",
  "trigger": "High Jidoka rate for 'Missing architecture rationale'",
  "hypothesis": "Gate criteria too vague, orchestrators don't know what to include",
  "experiment": {
    "change": "Update gate-design.md with specific examples of good rationale",
    "metrics": [
      "Jidoka rate for this condition",
      "Gate pass rate",
      "Orchestrator satisfaction (survey)"
    ],
    "duration": "2 weeks",
    "success_criteria": "Jidoka rate drops below 10%"
  },
  "status": "in_progress"
}
```

---

## 5. Existing Implementations: Detailed Analysis

### 5.1 LangSmith Trace Structure (Deep Dive)

**Run Hierarchy**:

```
Trace (ID: trace_123)
  └─ Run: AgentExecutor (ID: run_001, type: chain)
      ├─ Run: Planning (ID: run_002, type: llm)
      │   ├─ Input: "User task: Create auth feature"
      │   └─ Output: "Steps: 1. Define requirements, 2. Design, 3. Implement"
      ├─ Run: Tool: read_file (ID: run_003, type: tool)
      │   ├─ Input: {"path": "specs/main/prd.md"}
      │   └─ Output: "# PRD: Auth Feature..."
      ├─ Run: Design (ID: run_004, type: llm)
      │   ├─ Input: "Given PRD, design architecture..."
      │   └─ Output: "Architecture: JWT-based auth with Redis sessions..."
      └─ Run: Validation (ID: run_005, type: chain)
          ├─ Run: Gate Check (ID: run_006, type: llm)
          │   ├─ Input: "Check design against gate criteria..."
          │   └─ Output: "PASSED: All criteria met"
          └─ Output: {"gate_result": "passed"}
```

**Feedback Annotations**:

After execution, human can annotate:

```json
{
  "run_id": "run_004",
  "feedback": [
    {
      "key": "architecture_quality",
      "score": 4,  // 1-5 scale
      "comment": "Good choice of JWT, but missing rate limiting consideration"
    },
    {
      "key": "correctness",
      "score": 5,
      "correction": null
    }
  ]
}
```

**Applicability to RaiSE**:

- ✅ **Nested runs** map well to kata steps (parent step → child tool calls)
- ✅ **Feedback system** supports Jidoka learning (track what worked/didn't)
- ⚠️ **Add governance run type**: LangSmith has `llm|chain|tool|retriever|agent`, RaiSE needs `gate_check|jidoka_stop|policy_eval`

---

### 5.2 Arize Phoenix Evaluation Framework

**Evaluator Pattern**:

Phoenix runs **evaluators** on spans to compute quality metrics:

```python
from phoenix.evals import llm_classify

# Define evaluator
hallucination_eval = llm_classify(
    model="gpt-4",
    template="Does the output contain factual errors not supported by context?",
    rails=["factual", "hallucinated"]
)

# Run on trace
results = hallucination_eval.evaluate(trace_df)
```

**Output**:

```json
{
  "span_id": "span_123",
  "eval_name": "hallucination",
  "label": "factual",
  "score": 0.95,
  "explanation": "Output correctly cites source document"
}
```

**Built-in Evaluators**:
- Hallucination detection
- Toxicity detection
- Relevance (for RAG)
- Coherence
- Custom (user-defined)

**Applicability to RaiSE**:

- ✅ **Gate checks are evaluators**: Map gate criteria to Phoenix evaluators
- ✅ **LLM-based validation**: Use LLM to check subjective criteria (e.g., "Is rationale clear?")
- ⚠️ **Cost**: Running evaluator on every span is expensive (only do for gates)

**RaiSE Gate as Phoenix Evaluator**:

```python
gate_design_eval = llm_classify(
    model="claude-opus-4.5",
    template="""
    Given this tech design:
    {artifact}

    Check:
    - [ ] Has architecture decision rationale
    - [ ] Has data model definition
    - [ ] Has API contracts

    Return: "passed" or "failed"
    """,
    rails=["passed", "failed"]
)
```

---

### 5.3 How Arize Structures LLM Telemetry

**Span Schema** (Phoenix):

```json
{
  "context": {
    "span_id": "span_abc123",
    "trace_id": "trace_xyz789",
    "parent_id": "span_parent"
  },
  "span_kind": "LLM",
  "name": "chat_completion",
  "start_time": 1643723400.0,
  "end_time": 1643723402.5,
  "status_code": "OK",
  "status_message": "",
  "attributes": {
    // Model info
    "llm.model_name": "gpt-4",
    "llm.provider": "openai",
    "llm.invocation_parameters": {
      "temperature": 0.7,
      "max_tokens": 1000
    },

    // Input/output
    "llm.input_messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant"
      },
      {
        "role": "user",
        "content": "What is 2+2?"
      }
    ],
    "llm.output_messages": [
      {
        "role": "assistant",
        "content": "2+2 equals 4"
      }
    ],

    // Token usage
    "llm.token_count.prompt": 25,
    "llm.token_count.completion": 10,
    "llm.token_count.total": 35,

    // Custom
    "user_id": "user_123",
    "session_id": "sess_456"
  },
  "events": [
    {
      "name": "tool_call",
      "timestamp": 1643723401.0,
      "attributes": {
        "tool_name": "calculator",
        "tool_input": "2+2"
      }
    }
  ]
}
```

**Applicability to RaiSE**:

- ✅ **Attributes are flexible**: Can add RaiSE-specific fields (kata_id, gate_id, jidoka_trigger)
- ✅ **Events capture sub-actions**: Use for tool calls, gate checks, Jidoka triggers
- ✅ **Standard span model**: Compatible with OTLP export

---

## 6. Recommended Data Model for RaiSE Kata Execution Traces

### 6.1 Schema Design

**Format**: JSONL (JSON Lines) per ADR-008

**File structure**:
```
.raise/traces/
  └─ 2026-01-29.jsonl
```

**Schema version**: 1.0.0

### 6.2 Trace Event Types

| Event Type | Purpose | Frequency |
|-----------|---------|-----------|
| `trace_started` | Kata execution initiated | 1 per trace |
| `trace_completed` | Kata execution finished | 1 per trace |
| `step_started` | Kata step began | N per trace |
| `step_completed` | Kata step finished | N per trace |
| `llm_call` | LLM invocation | M per step |
| `tool_call` | Tool execution | M per step |
| `gate_check` | Validation gate executed | K per trace |
| `jidoka_triggered` | Stop-the-line event | 0-K per trace |
| `jidoka_resumed` | Execution resumed after Jidoka | 0-K per trace |
| `human_intervention` | Manual action during execution | 0-K per trace |

### 6.3 Complete Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://raise.humansys.ai/schemas/kata-trace-v1.json",
  "title": "RaiSE Kata Execution Trace",
  "type": "object",
  "required": ["trace_id", "event_type", "timestamp", "kata_id", "version"],
  "properties": {
    "trace_id": {
      "type": "string",
      "description": "Unique identifier for this kata execution",
      "pattern": "^kata_exec_[0-9]{8}_[0-9]{6}_[a-z0-9]+$"
    },
    "event_type": {
      "type": "string",
      "enum": [
        "trace_started",
        "trace_completed",
        "step_started",
        "step_completed",
        "llm_call",
        "tool_call",
        "gate_check",
        "jidoka_triggered",
        "jidoka_resumed",
        "human_intervention"
      ]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "kata_id": {
      "type": "string",
      "description": "Kata identifier (e.g., flujo-001-discovery)"
    },
    "kata_version": {
      "type": "string",
      "description": "Kata version (semver)"
    },
    "session_id": {
      "type": "string",
      "description": "Session grouping multiple kata executions"
    },
    "span_id": {
      "type": "string",
      "description": "Unique ID for this event (for parent-child relationships)"
    },
    "parent_span_id": {
      "type": "string",
      "description": "Parent span ID (for nesting)"
    },
    "version": {
      "type": "string",
      "description": "Trace schema version",
      "const": "1.0.0"
    },

    // Event-specific fields (union type, varies by event_type)
    "data": {
      "type": "object",
      "description": "Event-specific payload"
    }
  }
}
```

**Example trace file** (`.raise/traces/2026-01-29.jsonl`):

```jsonl
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"trace_started","timestamp":"2026-01-29T10:30:45Z","kata_id":"flujo-001-discovery","kata_version":"2.1.0","session_id":"sess_xyz789","version":"1.0.0","data":{"orchestrator":{"agent":"claude-opus-4.5","context_loaded":["raise://constitution","raise://glossary"]}}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"step_started","timestamp":"2026-01-29T10:30:46Z","span_id":"step_001","step_number":1,"step_name":"Initialize Environment","version":"1.0.0","data":{}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"tool_call","timestamp":"2026-01-29T10:30:47Z","span_id":"tool_001","parent_span_id":"step_001","version":"1.0.0","data":{"tool":"check_prerequisites","duration_ms":150,"status":"success"}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"step_completed","timestamp":"2026-01-29T10:30:50Z","span_id":"step_001","version":"1.0.0","data":{"status":"success","duration_ms":4000}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"jidoka_triggered","timestamp":"2026-01-29T10:35:30Z","span_id":"jidoka_001","parent_span_id":"step_003","version":"1.0.0","data":{"trigger":"verification_failed","condition":"Solution Vision not found","action":"stop_execution","message":"**JIDOKA**: Execute `/raise.2.vision` first"}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"jidoka_resumed","timestamp":"2026-01-29T11:00:00Z","span_id":"jidoka_001_resume","version":"1.0.0","data":{"jidoka_event_id":"jidoka_001","action_taken":"Executed /raise.2.vision","changes_made":[{"file":"specs/main/solution_vision.md"}]}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"gate_check","timestamp":"2026-01-29T10:40:00Z","span_id":"gate_001","parent_span_id":"step_005","version":"1.0.0","data":{"gate_id":"gate-design","status":"failed","checks":[{"check_id":"C002","name":"Has data model definition","result":"failed"}],"overall_score":0.75}}
{"trace_id":"kata_exec_20260129_103045_abc123","event_type":"trace_completed","timestamp":"2026-01-29T10:45:30Z","version":"1.0.0","data":{"status":"jidoka_stopped","total_duration_ms":930000,"total_tokens":45000,"total_cost_usd":0.75,"jidoka_count":1}}
```

---

### 6.4 Field Specifications

#### 6.4.1 Required Fields (All Events)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `trace_id` | string | Unique trace identifier | `kata_exec_20260129_103045_abc123` |
| `event_type` | enum | Event type | `gate_check` |
| `timestamp` | ISO 8601 | Event timestamp | `2026-01-29T10:40:00Z` |
| `kata_id` | string | Kata being executed | `flujo-001-discovery` |
| `version` | semver | Schema version | `1.0.0` |

#### 6.4.2 Optional Fields (Contextual)

| Field | Type | When Used | Description |
|-------|------|-----------|-------------|
| `span_id` | string | All except trace_started/completed | Unique span ID |
| `parent_span_id` | string | Nested events | Parent span ID |
| `session_id` | string | All | Session grouping |
| `step_number` | int | Step events | Step position in kata |
| `step_name` | string | Step events | Human-readable step name |

#### 6.4.3 Event-Specific Payloads

**trace_started**:

```json
{
  "data": {
    "orchestrator": {
      "agent": "claude-opus-4.5",
      "human_id_hash": "user_abc123",
      "context_loaded": ["raise://constitution", "raise://glossary"]
    },
    "work_cycle": "project",
    "spec_id": "001-auth-feature",
    "environment": "local"
  }
}
```

**step_completed**:

```json
{
  "data": {
    "status": "success|failed|skipped",
    "duration_ms": 4000,
    "token_usage": {
      "input": 3200,
      "output": 150,
      "total": 3350
    },
    "verification": {
      "criteria": "Solution Vision exists",
      "verified": true
    }
  }
}
```

**gate_check**:

```json
{
  "data": {
    "gate_id": "gate-design",
    "gate_version": "2.1.0",
    "artifact_path": "specs/001-auth-feature/tech_design.md",
    "status": "passed|failed|waived",
    "checks": [
      {
        "check_id": "C001",
        "name": "Has architecture decision rationale",
        "result": "passed",
        "evidence": "Section found with 3 ADRs"
      }
    ],
    "overall_score": 0.75,
    "waived_by": null
  }
}
```

**jidoka_triggered**:

```json
{
  "data": {
    "trigger": "verification_failed|gate_failed|missing_input",
    "condition": "Solution Vision not found",
    "action": "stop_execution",
    "message": "**JIDOKA**: Execute `/raise.2.vision` first",
    "options": [
      {
        "action": "fix_issue",
        "command": "raise resume --trace-id {trace_id}"
      }
    ]
  }
}
```

---

## 7. Integration Patterns with RaiSE

### 7.1 Integration with Existing Trace Standards

**Export to OpenTelemetry**:

```bash
# Convert JSONL traces to OTLP format
raise export otlp \
  --input .raise/traces/2026-01-29.jsonl \
  --output /tmp/traces.otlp \
  --service-name kata-harness
```

**Mapping**:

| RaiSE Event | OTLP Span Kind | Attributes |
|-------------|----------------|------------|
| `step_started/completed` | `INTERNAL` | `kata.step.number`, `kata.step.name` |
| `llm_call` | `CLIENT` | `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.*` |
| `tool_call` | `CLIENT` | `tool.name`, `tool.duration_ms` |
| `gate_check` | `INTERNAL` (custom) | `raise.gate.id`, `raise.gate.status`, `raise.gate.score` |
| `jidoka_triggered` | `INTERNAL` (custom) | `raise.jidoka.trigger`, `raise.jidoka.condition` |

**Custom OTLP Attributes**:

```json
{
  "attributes": [
    {"key": "raise.kata.id", "value": {"stringValue": "flujo-001-discovery"}},
    {"key": "raise.kata.version", "value": {"stringValue": "2.1.0"}},
    {"key": "raise.work_cycle", "value": {"stringValue": "project"}},
    {"key": "raise.gate.id", "value": {"stringValue": "gate-design"}},
    {"key": "raise.gate.status", "value": {"stringValue": "failed"}},
    {"key": "raise.gate.score", "value": {"doubleValue": 0.75}},
    {"key": "raise.jidoka.triggered", "value": {"boolValue": true}}
  ]
}
```

---

### 7.2 CLI Commands for Observability

**View recent traces**:

```bash
raise audit list --last 10
```

**Output**:
```
Trace ID                              Kata                    Status          Duration    Cost
kata_exec_20260129_103045_abc123     flujo-001-discovery     jidoka_stopped  15m 30s     $0.75
kata_exec_20260129_095000_def456     flujo-002-vision        completed       8m 15s      $0.42
kata_exec_20260129_083000_ghi789     flujo-004-tech-design   completed       22m 45s     $1.20
```

**View specific trace**:

```bash
raise audit show kata_exec_20260129_103045_abc123
```

**Output**:
```
Trace: kata_exec_20260129_103045_abc123
Kata: flujo-001-discovery v2.1.0
Status: ⚠️  JIDOKA STOPPED
Duration: 15m 30s
Cost: $0.75

Timeline:
[10:30:45] ▶ Started execution
[10:30:46]   Step 1: Initialize Environment (4s) ✓
[10:32:00]   Step 2: Cargar Vision y Contexto (1m 15s) ✓
[10:35:30]   ⛔ JIDOKA: Solution Vision not found
           Action: Execute `/raise.2.vision` first
[11:00:00]   ▶ Resumed after intervention
[10:40:00]   Step 5: Validate Design (30s) ✗ Gate failed
           Gate: gate-design
           Failed: C002 - Has data model definition
[10:45:30] ⛔ Stopped (Jidoka)

Metrics:
  Total tokens: 45,000
  LLM calls: 8
  Tool calls: 12
  Gates checked: 1
  Jidoka stops: 1

Use `raise audit show --verbose {trace_id}` for full details
```

**Query governance events**:

```bash
raise audit query --event-type gate_check --status failed --last 30d
```

**Output**:
```
Found 12 failed gate checks in last 30 days

Gate ID         Count   Common Failures
gate-design     8       C002 (Missing data model) - 5
                        C001 (No architecture rationale) - 3
gate-backlog    4       C003 (Stories not prioritized) - 4

Recommendation: Update gate-design to include clearer criteria for C002
```

**Export for analysis**:

```bash
raise export csv --last 90d --output metrics.csv
```

---

### 7.3 Dashboard Metrics (Jidoka-Centric)

**Governance Dashboard** (not performance dashboard):

#### Widget 1: Jidoka Stop Rate

```
┌─ Jidoka Stop Rate (Last 30 Days) ─────────────────┐
│                                                    │
│  26% of executions stopped                        │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░  12/45       │
│                                                    │
│  Target: <10%                                      │
│  Trend: ▲ +5% from previous period                │
└────────────────────────────────────────────────────┘
```

#### Widget 2: Top Jidoka Triggers

```
┌─ Top Stop-the-Line Conditions ────────────────────┐
│                                                    │
│  1. Missing architecture rationale   █████ 42%    │
│  2. Incomplete test coverage         ███   25%    │
│  3. Undefined data model             ██    17%    │
│  4. Missing API contracts            ██    17%    │
│                                                    │
└────────────────────────────────────────────────────┘
```

#### Widget 3: Gate Pass Rate

```
┌─ Gate Pass Rate by Gate ──────────────────────────┐
│                                                    │
│  gate-design      ████████░░░░  75%               │
│  gate-backlog     ██████████    92%               │
│  gate-estimation  ███████░░░░░  68%               │
│                                                    │
│  Overall: 78% (target: >90%)                      │
└────────────────────────────────────────────────────┘
```

#### Widget 4: Kata Quality Trend

```
┌─ Kata Execution Quality (6-Week Trend) ───────────┐
│                                                    │
│  100% ┤                                            │
│   90% ┤         ●───●                              │
│   80% ┤     ●───         ●                         │
│   70% ┤ ●───                 ●                     │
│   60% ┤                                            │
│       └─────────────────────────────────────────   │
│        W1  W2  W3  W4  W5  W6                      │
│                                                    │
│  ● Gate Pass Rate  ✓ Improving                    │
└────────────────────────────────────────────────────┘
```

#### Widget 5: Context Utilization

```
┌─ Most Loaded Context Resources ───────────────────┐
│                                                    │
│  raise://constitution     ██████████████  98%     │
│  raise://glossary         ███████████     85%     │
│  raise://guardrails/*     ██████          62%     │
│  raise://patterns/*       ███             28%     │
│                                                    │
│  Opportunity: 38% of katas don't load patterns    │
└────────────────────────────────────────────────────┘
```

---

## 8. Specific Recommendations for RaiSE Jidoka Observability

### 8.1 Core Principles

1. **Governance-First Telemetry**: Capture *why* execution stopped, not just *that* it stopped
2. **Human-Centric**: Traces must be readable by orchestrators, not just machines
3. **Local-First**: Store traces locally (JSONL) per ADR-008, export optional
4. **Actionable Insights**: Every metric should suggest an improvement action
5. **Kaizen-Driven**: Observability exists to enable continuous improvement

---

### 8.2 Recommended Implementation Phases

#### Phase 1: Minimal Viable Observability (Week 1-2)

**Scope**:
- Trace `trace_started`, `trace_completed`, `jidoka_triggered` events only
- Write to `.raise/traces/{date}.jsonl`
- Implement `raise audit list` and `raise audit show` commands

**Deliverable**: Basic Jidoka audit trail

#### Phase 2: Step-Level Tracing (Week 3-4)

**Scope**:
- Add `step_started`, `step_completed` events
- Capture token usage and latency per step
- Implement `raise metrics --week` command

**Deliverable**: Performance bottleneck identification

#### Phase 3: Gate Observability (Week 5-6)

**Scope**:
- Add `gate_check` events with detailed check results
- Track gate pass rates per gate
- Implement gate failure analysis reports

**Deliverable**: Gate quality metrics

#### Phase 4: Dashboard (Week 7-8)

**Scope**:
- Build CLI-based dashboard (`raise dashboard`)
- Visualize Jidoka trends, gate pass rates, cost trends
- Export to CSV for external analysis

**Deliverable**: Real-time governance visibility

#### Phase 5: OTLP Export (Future)

**Scope**:
- Implement `raise export otlp` command
- Map RaiSE events to OpenTelemetry spans
- Enable integration with enterprise observability platforms

**Deliverable**: Enterprise observability integration

---

### 8.3 Instrumentation Strategy

**Where to instrument** (in Kata Harness code):

```typescript
// Pseudo-code for Kata Harness

class KataHarness {
  async executeKata(kataId: string, sessionId: string) {
    const traceId = generateTraceId();

    // Log trace start
    await trace.log({
      trace_id: traceId,
      event_type: "trace_started",
      kata_id: kataId,
      session_id: sessionId,
      data: {
        orchestrator: {
          agent: this.agentModel,
          context_loaded: this.contextResources
        }
      }
    });

    try {
      for (const step of kata.steps) {
        const spanId = generateSpanId();

        // Log step start
        await trace.log({
          trace_id: traceId,
          event_type: "step_started",
          span_id: spanId,
          step_number: step.number,
          step_name: step.name
        });

        const result = await this.executeStep(step, traceId, spanId);

        // Check verification criteria
        if (!result.verification.verified) {
          // JIDOKA: Stop execution
          await trace.log({
            trace_id: traceId,
            event_type: "jidoka_triggered",
            parent_span_id: spanId,
            data: {
              trigger: "verification_failed",
              condition: step.jidoka.condition,
              action: "stop_execution"
            }
          });

          // Pause and wait for human intervention
          await this.pauseForHumanInput(traceId);
        }

        // Log step completion
        await trace.log({
          trace_id: traceId,
          event_type: "step_completed",
          span_id: spanId,
          data: {
            status: result.status,
            duration_ms: result.duration,
            token_usage: result.tokenUsage
          }
        });
      }

      // Log trace completion
      await trace.log({
        trace_id: traceId,
        event_type: "trace_completed",
        data: {
          status: "completed",
          total_duration_ms: Date.now() - startTime,
          total_tokens: totalTokens
        }
      });

    } catch (error) {
      await trace.log({
        trace_id: traceId,
        event_type: "trace_completed",
        data: {
          status: "failed",
          error: error.message
        }
      });
    }
  }
}
```

---

### 8.4 Privacy and Security Considerations

**PII Handling**:
- ❌ **Never log**: Code content, spec text, sensitive data
- ✅ **Always log**: Metadata (file paths, token counts, status)
- ✅ **Hash user IDs**: Anonymize orchestrator identity

**Example**:

```json
// ❌ BAD: Logging sensitive content
{
  "event_type": "llm_call",
  "data": {
    "input": "Design auth for app handling SSN and credit cards..."  // PII!
  }
}

// ✅ GOOD: Logging metadata only
{
  "event_type": "llm_call",
  "data": {
    "input_tokens": 3200,
    "output_tokens": 450,
    "input_hash": "sha256:abc123...",  // For deduplication
    "input_summary": "Tech design request for auth feature"  // Safe summary
  }
}
```

**Access Control**:
- Traces stored in `.raise/traces/` (same permissions as `.raise/`)
- No cloud upload without explicit consent
- Export commands require confirmation

---

### 8.5 Alignment with RaiSE Principles

| RaiSE Principle | How Observability Supports |
|----------------|---------------------------|
| **§1. Heutagogy** | Traces capture learner's decision path; analyze to improve self-direction |
| **§4. Validation Gates** | Gate checks are first-class telemetry events; track pass rates |
| **§7. Lean (Jidoka)** | Jidoka events enable stop-the-line; track triggers to identify systemic issues |
| **§7. Lean (Kaizen)** | Metrics inform continuous improvement experiments |
| **§8. Observable Workflow** | Entire kata execution is transparent and auditable |
| **ADR-008** | Local-first storage (JSONL), privacy by design |

---

## 9. Open Questions and Future Research

### 9.1 Unresolved Questions

1. **Semantic embeddings for traces**: Should we embed trace events for semantic search? (e.g., "Find all executions where orchestrator struggled with architecture decisions")

2. **Differential tracing**: How to efficiently compute "what changed" between two kata executions of same spec?

3. **Federated learning**: Can we learn from aggregated traces across teams without sharing sensitive data?

4. **Real-time interventions**: Should the harness proactively suggest corrections during execution (not just at Jidoka stops)?

5. **Trace compression**: JSONL files grow large; should we implement compression or rotation strategies beyond 30-day retention?

### 9.2 Experimentation Needed

1. **Optimal trace granularity**: What's the right level of detail? (every tool call vs. step-level only)

2. **Gate evaluator performance**: How expensive is it to run LLM-based gate checks? Can we optimize with caching?

3. **Replay fidelity**: Can we achieve >95% deterministic replay with snapshot approach?

4. **Dashboard adoption**: Will orchestrators actually use dashboards, or prefer CLI?

---

## 10. Summary and Recommendations

### 10.1 Key Findings

1. **LLM observability is maturing rapidly**, with OpenTelemetry GenAI semantic conventions providing vendor-neutral standard

2. **LangSmith's run-centric model** is well-suited for RaiSE's nested kata steps

3. **Arize Phoenix's evaluation framework** maps naturally to RaiSE's gate checks

4. **No existing tool** focuses on governance observability (gates, policies, Jidoka); RaiSE's approach is novel

5. **Local-first observability** is feasible with JSONL + CLI tools

### 10.2 Recommended Data Model

**Adopt hybrid approach**:
- **Base**: OpenTelemetry span model for interoperability
- **Extensions**: RaiSE-specific event types (`gate_check`, `jidoka_triggered`)
- **Storage**: JSONL (local-first per ADR-008)
- **Export**: Optional OTLP export for enterprise integration

**Core event types**:
- `trace_started` / `trace_completed`
- `step_started` / `step_completed`
- `llm_call` / `tool_call`
- `gate_check` (RaiSE-specific)
- `jidoka_triggered` / `jidoka_resumed` (RaiSE-specific)
- `human_intervention` (RaiSE-specific)

### 10.3 Implementation Roadmap

**Phase 1** (2 weeks): Basic trace logging (trace start/end, Jidoka events)
**Phase 2** (2 weeks): Step-level tracing (token usage, latency)
**Phase 3** (2 weeks): Gate observability (detailed check results)
**Phase 4** (2 weeks): CLI dashboard (Jidoka metrics, gate pass rates)
**Phase 5** (Future): OTLP export, advanced analytics

### 10.4 Critical Success Factors

1. **Governance-first**: Metrics must support Jidoka decision-making, not just performance optimization
2. **Human-readable**: Traces must be understandable by orchestrators, not just machines
3. **Actionable**: Every metric should suggest an improvement (Kaizen loop)
4. **Privacy by design**: No PII, no code leakage, local-first
5. **Incremental adoption**: Start simple (basic tracing), evolve to sophisticated analytics

---

## 11. References

### 11.1 Standards and Specifications

- **OpenTelemetry Semantic Conventions for GenAI** (v1.0.0, 2024)
  - https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **SARIF (Static Analysis Results Interchange Format)** (OASIS Standard v2.1.0)
  - https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **JSON Lines (JSONL)** Specification
  - https://jsonlines.org/

### 11.2 Tools and Platforms

- **LangSmith** (LangChain)
  - Docs: https://docs.smith.langchain.com/
  - Architecture: Run-centric tracing model
- **Arize Phoenix** (Arize AI)
  - Docs: https://docs.arize.com/phoenix
  - GitHub: https://github.com/Arize-ai/phoenix
- **OpenLLMetry** (Traceloop)
  - GitHub: https://github.com/traceloop/openllmetry
  - Docs: https://www.traceloop.com/docs
- **Weights & Biases Prompts**
  - Docs: https://docs.wandb.ai/guides/prompts

### 11.3 Academic and Industry Research

- **"Debugging Large Language Models: A Survey"** (arXiv, 2024)
  - Focus on observability techniques for LLM applications
- **"Observability for AI: Metrics, Traces, and Governance"** (ACM Queue, 2024)
  - Discusses governance-centric observability patterns
- **"LLM Application Observability: Current State and Future Directions"** (MLOps Community, 2024)
  - Industry survey of observability practices

### 11.4 RaiSE Framework Documents

- **ADR-008: Observable Workflow Local**
  - Path: `/home/emilio/Code/raise-commons/.private/decisions/adr-008-observable-workflow.md`
- **Research Prompt: Kata Harness First Principles**
  - Path: `/home/emilio/Code/raise-commons/specs/main/research/prompts/kata-harness-first-principles-research.md`
- **Feature 003: Observable Validation Gates**
  - Path: `/home/emilio/Code/raise-commons/specs/main/research/speckit-critiques/features/feature-003-observable-gates.md`

---

## Appendix A: Comparison of Observability Platforms

| Platform | Open Source | Self-Hosted | LLM-Specific | Governance | Eval Framework | Pricing |
|----------|-------------|-------------|--------------|------------|----------------|---------|
| **LangSmith** | ❌ | ❌ | ✅ | ❌ | ⚠️ (manual) | SaaS ($) |
| **Arize Phoenix** | ✅ | ✅ | ✅ | ⚠️ (evals) | ✅ | Free/Enterprise |
| **OpenLLMetry** | ✅ | ✅ | ✅ | ❌ | ❌ | Free |
| **W&B Prompts** | ❌ | ❌ | ✅ | ❌ | ⚠️ (manual) | SaaS ($) |
| **DataDog APM** | ❌ | ❌ | ⚠️ (basic) | ❌ | ❌ | SaaS ($$$) |
| **Honeycomb** | ❌ | ❌ | ⚠️ (basic) | ❌ | ❌ | SaaS ($$) |

---

## Appendix B: Sample Trace Query API

**Query DSL** (proposed):

```bash
raise audit query \
  --event-type gate_check \
  --field "data.status=failed" \
  --field "data.gate_id=gate-design" \
  --date-range "2026-01-01 to 2026-01-29" \
  --output json | jq '.[].data.checks[] | select(.result=="failed") | .name' | sort | uniq -c
```

**Output**:
```
      5 Has data model definition
      3 Has architecture decision rationale
      1 Has API contracts
```

---

## Appendix C: OTLP Export Example

**Command**:

```bash
raise export otlp \
  --input .raise/traces/2026-01-29.jsonl \
  --output /tmp/traces.otlp \
  --service-name kata-harness \
  --resource-attributes "environment=local,project=raise-commons"
```

**Output** (excerpt):

```json
{
  "resourceSpans": [
    {
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "kata-harness"}},
          {"key": "environment", "value": {"stringValue": "local"}},
          {"key": "project", "value": {"stringValue": "raise-commons"}}
        ]
      },
      "scopeSpans": [
        {
          "scope": {"name": "raise-kata-harness", "version": "2.3.0"},
          "spans": [
            {
              "traceId": "0123456789abcdef0123456789abcdef",
              "spanId": "0123456789abcdef",
              "name": "flujo-001-discovery",
              "kind": "SPAN_KIND_INTERNAL",
              "startTimeUnixNano": "1643723400000000000",
              "endTimeUnixNano": "1643723700000000000",
              "attributes": [
                {"key": "raise.kata.id", "value": {"stringValue": "flujo-001-discovery"}},
                {"key": "raise.kata.version", "value": {"stringValue": "2.1.0"}},
                {"key": "raise.work_cycle", "value": {"stringValue": "project"}},
                {"key": "raise.jidoka.triggered", "value": {"boolValue": true}},
                {"key": "raise.gate.checks.total", "value": {"intValue": "4"}},
                {"key": "raise.gate.checks.passed", "value": {"intValue": "3"}},
                {"key": "raise.gate.pass_rate", "value": {"doubleValue": 0.75}}
              ],
              "events": [
                {
                  "timeUnixNano": "1643723500000000000",
                  "name": "jidoka_triggered",
                  "attributes": [
                    {"key": "raise.jidoka.condition", "value": {"stringValue": "Solution Vision not found"}}
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

**End of Research Report**

**Document Status**: Complete
**Next Steps**: Review with RaiSE team, prioritize recommendations, begin Phase 1 implementation
**Contact**: For questions about this research, reference `RES-KATA-OBS-001`
