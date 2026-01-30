# Observability Patterns for Kata Harness: Executive Summary

**Research ID**: RES-KATA-OBS-001
**Date**: 2026-01-29
**Full Report**: `observability-patterns-research-report.md`

---

## TL;DR

**Question**: What observability patterns enable debugging, auditing, and governance in multi-step agent execution?

**Answer**: The LLM observability ecosystem has converged on a hierarchical span model (traces → runs → steps) with OpenTelemetry as the emerging standard. However, existing tools focus on **performance optimization** (latency, cost), not **governance enforcement** (gates, policies, Jidoka).

**Recommendation for RaiSE**: Build a lightweight, local-first observability layer using:
- JSONL storage (per ADR-008)
- OpenTelemetry-compatible data model (for interoperability)
- RaiSE-specific event types (gate_check, jidoka_triggered)
- CLI-based dashboard focused on governance metrics

---

## Key Findings

### 1. Tracing Standards Landscape

| Tool | Model | Storage | Governance | Best For |
|------|-------|---------|------------|----------|
| **OpenTelemetry** | Spans + Events | OTLP collectors | ❌ | Interoperability |
| **LangSmith** | Nested runs | Cloud SaaS | ❌ | Debugging LLM apps |
| **Arize Phoenix** | Spans + Evals | Self-hosted | ⚠️ | Quality metrics |
| **OpenLLMetry** | OTLP spans | Any backend | ❌ | Auto-instrumentation |

**Gap**: No tool provides governance-first observability (gates, policies, stop-the-line)

---

### 2. What to Observe: Critical Data Model Elements

#### Trace Level (Kata Execution)
```json
{
  "trace_id": "kata_exec_20260129_103045_abc123",
  "kata_id": "flujo-001-discovery",
  "status": "completed|failed|jidoka_stopped",
  "jidoka_events": [...],  // Stop-the-line events
  "total_tokens": 45000,
  "total_cost_usd": 0.75
}
```

#### Step Level (Kata Step)
```json
{
  "span_id": "step_002",
  "step_name": "Cargar Vision y Contexto",
  "verification": {
    "criteria": "Solution Vision exists",
    "verified": true
  },
  "token_usage": {"input": 3200, "output": 150},
  "duration_ms": 75000
}
```

#### Gate Check Level
```json
{
  "gate_id": "gate-design",
  "status": "passed|failed|waived",
  "checks": [
    {
      "check_id": "C002",
      "name": "Has data model definition",
      "result": "failed",
      "evidence": "Section empty"
    }
  ],
  "overall_score": 0.75
}
```

#### Jidoka Event Level (RaiSE-Specific)
```json
{
  "event_type": "jidoka_triggered",
  "trigger": "verification_failed",
  "condition": "Solution Vision not found",
  "action": "stop_execution",
  "message": "**JIDOKA**: Execute `/raise.2.vision` first"
}
```

---

### 3. Audit Requirements

**Compliance needs** (SOC2, EU AI Act):
- ✅ **Immutable audit trail**: Hash-chained events
- ✅ **Who-What-When-Why**: Capture all governance decisions
- ✅ **Queryability**: Support compliance queries ("show all gate waivers")
- ✅ **Deterministic replay**: Reproduce execution from trace
- ✅ **PII protection**: Anonymize user IDs, never log code content

**Example query**:
```bash
raise audit query \
  --event-type gate_waived \
  --date-range "2025-12-01 to 2026-01-29" \
  --output csv
```

---

### 4. Real-time vs Post-hoc Observability

#### Real-time (During Execution)
- **Streaming feedback**: Server-Sent Events for live progress
- **Human-in-the-loop**: Block execution on Jidoka, wait for intervention
- **Immediate alerts**: Notify on gate failures

#### Post-hoc (After Execution)
- **Trend analysis**: Weekly reports on gate pass rates, Jidoka frequency
- **Kaizen loops**: Identify systemic issues, experiment with improvements
- **Cost optimization**: Analyze token usage patterns

---

## Recommended Data Model for RaiSE

### Schema Overview

**Format**: JSONL (JSON Lines)
**Storage**: `.raise/traces/{date}.jsonl`
**Retention**: 30 days (configurable)

### Event Types

| Event Type | Purpose | Frequency |
|-----------|---------|-----------|
| `trace_started` | Kata execution initiated | 1 per trace |
| `trace_completed` | Kata finished | 1 per trace |
| `step_started/completed` | Kata step execution | N per trace |
| `llm_call` | LLM invocation | M per step |
| `tool_call` | Tool execution | M per step |
| `gate_check` | Validation gate | K per trace |
| `jidoka_triggered` | Stop-the-line | 0-K per trace |
| `jidoka_resumed` | Execution resumed | 0-K per trace |

### Key Fields

**Required (all events)**:
- `trace_id`: Unique identifier
- `event_type`: Event classification
- `timestamp`: ISO 8601
- `kata_id`: Which kata
- `version`: Schema version

**Contextual**:
- `span_id`: For nested events
- `parent_span_id`: For hierarchy
- `session_id`: Group multiple executions

**Event-specific**:
- `data`: Payload varies by event type

---

## Integration with Existing Standards

### OpenTelemetry Compatibility

**Export command**:
```bash
raise export otlp \
  --input .raise/traces/2026-01-29.jsonl \
  --output /tmp/traces.otlp
```

**Custom OTLP attributes**:
```json
{
  "attributes": [
    {"key": "raise.kata.id", "value": "flujo-001-discovery"},
    {"key": "raise.gate.status", "value": "failed"},
    {"key": "raise.jidoka.triggered", "value": true}
  ]
}
```

---

## Governance Dashboard (Jidoka-Centric)

### Key Metrics

1. **Jidoka Stop Rate**: % of executions stopped (target: <10%)
2. **Top Stop Conditions**: Which conditions trigger most (e.g., "Missing ADR rationale")
3. **Gate Pass Rate**: % passing per gate (target: >90%)
4. **Kata Quality Trend**: Weekly improvement tracking
5. **Context Utilization**: Which resources loaded most

### CLI Interface

```bash
# View recent traces
raise audit list --last 10

# Show specific trace
raise audit show kata_exec_20260129_103045_abc123

# Query governance events
raise audit query --event-type gate_check --status failed

# Weekly metrics
raise metrics --week --output report.md

# Interactive dashboard
raise dashboard
```

---

## Implementation Roadmap

### Phase 1: Minimal Viable Observability (2 weeks)
- Trace start/end events
- Jidoka events
- Basic CLI (`raise audit list/show`)

**Deliverable**: Basic audit trail

### Phase 2: Step-Level Tracing (2 weeks)
- Step start/end events
- Token usage and latency
- `raise metrics` command

**Deliverable**: Performance insights

### Phase 3: Gate Observability (2 weeks)
- Gate check events
- Detailed check results
- Gate failure analysis

**Deliverable**: Governance metrics

### Phase 4: Dashboard (2 weeks)
- CLI-based dashboard
- Jidoka trends, gate pass rates
- CSV export for analysis

**Deliverable**: Real-time visibility

### Phase 5: OTLP Export (Future)
- OpenTelemetry export
- Enterprise integration
- Advanced analytics

**Deliverable**: Enterprise observability

---

## Alignment with RaiSE Principles

| Principle | How Observability Supports |
|-----------|---------------------------|
| **§1. Heutagogy** | Traces capture decision paths; analyze for self-improvement |
| **§4. Validation Gates** | Gates are first-class telemetry; track compliance |
| **§7. Lean (Jidoka)** | Stop-the-line events enable root cause analysis |
| **§7. Lean (Kaizen)** | Metrics drive continuous improvement experiments |
| **§8. Observable Workflow** | Full transparency and auditability |
| **ADR-008** | Local-first storage, privacy by design |

---

## Critical Success Factors

1. **Governance-first**: Metrics support Jidoka decision-making
2. **Human-readable**: Traces understandable by orchestrators
3. **Actionable**: Every metric suggests an improvement
4. **Privacy by design**: No PII, no code leakage
5. **Incremental adoption**: Start simple, evolve sophistication

---

## Novel Contributions

**RaiSE's approach is unique**:

1. **Governance observability**: First-class support for gates and policies (not just performance)
2. **Jidoka telemetry**: Stop-the-line events as core primitive
3. **Local-first**: No cloud dependency for basic observability
4. **Kaizen-driven**: Metrics explicitly designed for continuous improvement
5. **Human-centric**: Traces optimize for orchestrator understanding, not just machine analysis

---

## Open Questions

1. Should we embed trace events for semantic search?
2. How to efficiently compute diffs between executions?
3. Can we learn from aggregated traces without sharing sensitive data?
4. Should harness proactively suggest corrections (not just at Jidoka stops)?
5. What's optimal trace granularity? (every tool call vs. step-level)

---

## References

**Full report**: `observability-patterns-research-report.md`

**Key sources**:
- OpenTelemetry GenAI Semantic Conventions (v1.0.0)
- LangSmith Documentation (LangChain)
- Arize Phoenix (open-source observability)
- OpenLLMetry (OTLP for LLMs)

**Related RaiSE docs**:
- ADR-008: Observable Workflow Local
- Research Prompt: Kata Harness First Principles
- Feature 003: Observable Validation Gates

---

## Next Steps

1. **Review** this summary with RaiSE team
2. **Prioritize** recommendations (likely focus on Phase 1-3)
3. **Prototype** basic trace logging (Phase 1)
4. **Validate** with pilot kata executions
5. **Iterate** based on real-world usage

---

**Document Status**: Complete
**Confidence Level**: HIGH (based on comprehensive tool analysis and RaiSE requirements)
**Action Required**: Team review and decision on implementation phases
