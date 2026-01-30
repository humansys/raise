# Kata Harness Research

This directory contains research artifacts for the RaiSE Kata Harness, the platform capability that executes multi-step SDLC workflows (Katas) with deterministic governance and observability.

## Research Questions

The Kata Harness research addresses fundamental questions about agentic workflow execution:

1. **First Principles**: What primitives enable deterministic execution in probabilistic LLM systems?
2. **Market Landscape**: How do leading frameworks (LangGraph, CrewAI, AutoGen) solve orchestration?
3. **Deterministic Patterns**: How to achieve reliability in inherently non-deterministic systems?
4. **Observability**: How to debug, audit, and govern multi-step agent execution?
5. **Governance as Code**: How to enforce (not suggest) policies in agent workflows?

## Research Artifacts

### Completed Research

| Document | Research ID | Topic | Status |
|----------|------------|-------|--------|
| `observability-patterns-research-report.md` | RES-KATA-OBS-001 | Observability patterns for AI agents | ✅ Complete |
| `observability-executive-summary.md` | RES-KATA-OBS-001 | Executive summary of observability research | ✅ Complete |

### Planned Research

| Topic | Research ID | Priority | Status |
|-------|------------|----------|--------|
| Execution Primitives | RES-KATA-PRIM-001 | P0 | 📋 Planned |
| Framework Comparison | RES-KATA-COMP-001 | P0 | 📋 Planned |
| Deterministic Patterns | RES-KATA-DET-001 | P0 | 📋 Planned |
| Governance Architecture | RES-KATA-GOV-001 | P1 | 📋 Planned |

## Observability Research (RES-KATA-OBS-001)

**Date**: 2026-01-29
**Status**: ✅ Complete

### Research Question

What observability patterns enable debugging, auditing, and governance in multi-step agent execution?

### Key Findings

1. **LLM observability ecosystem** has converged on OpenTelemetry-compatible hierarchical span models (traces → runs → steps)
2. **Existing tools** (LangSmith, Arize Phoenix, OpenLLMetry) focus on **performance optimization**, not **governance enforcement**
3. **RaiSE's governance-first approach** (gates, Jidoka, policies as first-class primitives) is novel and underserved by existing tools
4. **Local-first observability** is feasible with JSONL storage + CLI tools (per ADR-008)

### Recommended Data Model

**Storage**: `.raise/traces/{date}.jsonl` (JSONL format)

**Core event types**:
- `trace_started` / `trace_completed` (kata execution)
- `step_started` / `step_completed` (kata steps)
- `gate_check` (validation gates) - **RaiSE-specific**
- `jidoka_triggered` / `jidoka_resumed` (stop-the-line) - **RaiSE-specific**
- `llm_call` / `tool_call` (primitives)

**Key innovation**: First-class support for governance events (gates, Jidoka, policy decisions)

### Implementation Roadmap

| Phase | Scope | Duration | Deliverable |
|-------|-------|----------|-------------|
| 1 | Basic trace logging | 2 weeks | Audit trail |
| 2 | Step-level tracing | 2 weeks | Performance insights |
| 3 | Gate observability | 2 weeks | Governance metrics |
| 4 | CLI dashboard | 2 weeks | Real-time visibility |
| 5 | OTLP export | Future | Enterprise integration |

### Documents

- **Full report**: `observability-patterns-research-report.md` (62KB, ~15,000 words)
  - Detailed analysis of 4 observability platforms
  - Complete data model specification
  - Audit and compliance requirements
  - Real-time vs post-hoc patterns
  - Integration recommendations

- **Executive summary**: `observability-executive-summary.md` (9KB, ~2,000 words)
  - TL;DR and key findings
  - Recommended architecture
  - Implementation phases
  - Governance dashboard design

### Next Steps

1. ✅ Research complete
2. 📋 Review with RaiSE team
3. 📋 Prioritize implementation phases
4. 📋 Begin Phase 1 prototype (basic trace logging)

---

## Related Research

### Prior Research (Referenced)

- **Kata Harness First Principles**: `specs/main/research/prompts/kata-harness-first-principles-research.md`
  - Comprehensive research prompt covering all 6 research questions
  - Defines scope and expected deliverables

- **Feature 003: Observable Validation Gates**: `specs/main/research/speckit-critiques/features/feature-003-observable-gates.md`
  - Spec-kit feature for telemetry and metrics
  - ROI measurement approach
  - A/B testing framework

- **ADR-008: Observable Workflow Local**: `.private/decisions/adr-008-observable-workflow.md`
  - Decision to use local-first observability
  - JSONL format and retention policy
  - Privacy and compliance considerations

### Semantic Density Research

Related work on rule representation density (for RAG):
- `specs/main/research/prompts/semantic-density-research.md`
- `specs/main/research/sar-component/semantic-density/semantic-density-research-report.md`

**Intersection**: Both research areas address "how to represent knowledge for LLM consumption" (rules vs. traces)

---

## Methodology

### Research Process

1. **Landscape Analysis**: Survey existing observability tools (LangSmith, Arize Phoenix, OpenLLMetry)
2. **Standard Review**: Analyze OpenTelemetry GenAI semantic conventions
3. **Data Model Design**: Synthesize learnings into RaiSE-specific schema
4. **Requirements Mapping**: Align with ADR-008 and RaiSE principles
5. **Implementation Planning**: Define incremental rollout phases

### Sources

**Primary sources**:
- OpenTelemetry Semantic Conventions for GenAI (v1.0.0)
- LangSmith documentation and data model
- Arize Phoenix architecture and evaluation framework
- OpenLLMetry implementation patterns

**Secondary sources**:
- Academic papers on LLM observability
- Industry reports (a16z, Sequoia on AI agents)
- Community discussions (r/LocalLLaMA, HackerNews)

### Confidence Level

**HIGH** - Research based on:
- Established standards (OpenTelemetry)
- Production tools with public documentation
- Clear alignment with RaiSE principles
- Feasible implementation path

---

## Contributing to This Research

### Adding New Research

1. Create research prompt in `specs/main/research/prompts/`
2. Conduct research, produce report in this directory
3. Update this README with new entry
4. Link to related RaiSE documents

### Research Template

```markdown
# [Topic] Research Report

**Research ID**: RES-KATA-[TOPIC]-001
**Date**: YYYY-MM-DD
**Status**: Draft|In Progress|Complete

## Research Question
[Clear, specific question]

## Methodology
[How research was conducted]

## Findings
[Key discoveries]

## Recommendations
[Actionable next steps]

## References
[Sources cited]
```

---

## Governance

### Research Status Workflow

1. **Planned**: Research identified, not yet started
2. **In Progress**: Active research underway
3. **Complete**: Research finished, findings documented
4. **Archived**: Research superseded or no longer relevant

### Review Process

All research in this directory should be reviewed by:
- RaiSE Ontology Architect (semantic alignment)
- Technical Lead (feasibility)
- Product Owner (business value)

---

## Contact

For questions about Kata Harness research:
- See `specs/main/research/prompts/kata-harness-first-principles-research.md` for full research scope
- Reference specific Research ID (e.g., RES-KATA-OBS-001) in discussions
- Related ADRs: ADR-008 (Observable Workflow)

---

*Last updated: 2026-01-29*
*Research coordinator: RaiSE Framework Team*
