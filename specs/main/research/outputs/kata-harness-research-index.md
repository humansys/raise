---
id: kata-harness-research-index
title: "Kata Harness Research: Complete Index"
date: 2026-01-29
status: complete
purpose: navigation
research_id: research-prompt-003
---

# Kata Harness Research: Complete Index

This index provides navigation across all deliverables from the Kata Harness first principles research.

**Research Question**: What are the fundamental primitives required to execute multi-step AI agent workflows with deterministic guarantees?

**Status**: ✅ Complete (2026-01-29)

**Researcher**: Claude Sonnet 4.5

---

## Executive Summary

**For decision-makers and stakeholders**

📄 **[Executive Summary](kata-harness-executive-summary.md)**
- The problem (Markdown suggestions vs. enforced governance)
- 5 key findings
- Recommended 3-layer architecture
- MVP scope (4 weeks)
- Trade-offs analysis

**Read this first**: 10-minute overview of the entire research.

---

## Comprehensive Research Report

**For architects and implementers**

📘 **[First Principles Taxonomy](kata-harness-first-principles-taxonomy.md)**
- RQ1: 8 execution primitives (Operation, Step, Transition, State, Workflow, Gate, Context Manager, Observer)
- RQ2: Market landscape (15+ frameworks analyzed)
- RQ3: Deterministic execution patterns (structured output, state machines, hybrid architectures)
- RQ4: Observability & tracing (MELT stack, trace data models, replay capability)
- RQ5: Governance-as-code (gate enforcement, policy DSLs, separation of concerns)
- RQ6: Kata Harness design recommendation (3-layer architecture, alignment with RaiSE principles)
- Implementation roadmap (4 phases)

**Read this for**: Complete technical analysis, pattern catalog, framework comparisons.

---

## Visual Architecture Guide

**For understanding system design**

🎨 **[Architecture Diagrams](kata-harness-architecture-diagrams.md)**
- High-level architecture (3-layer model)
- Execution primitive relationships
- Compilation flow (Markdown → JSON)
- Runtime execution flow (step-by-step)
- State management (checkpointing, resume)
- Observability flow (MELT stack)
- Current vs. Recommended comparison

**Read this for**: Visual understanding of how the system works.

---

## Decision Support

**For choosing the right architecture**

📊 **[Decision Matrix](kata-harness-decision-matrix.md)**
- 5 architecture options evaluated
- Scoring across 6 criteria (enforcement, observability, authoring UX, Jidoka, implementation, extensibility)
- Detailed breakdown per option
- Risk analysis
- Constitution compliance matrix
- Trade-off summary
- Final recommendation: **Option C (Compiled Kata DSL)** - 90% score

**Read this for**: Rationale behind the recommended architecture.

---

## Implementation Checklist

**For building the MVP**

✅ **[Implementation Checklist](kata-harness-implementation-checklist.md)**
- Component 1: Kata Compiler (Markdown parser, skill mapper, graph builder)
- Component 2: State Machine Orchestrator (execution loop, gate enforcement, checkpointing)
- Component 3: Skill Executors (`file/load`, `llm/call`, `gate/run`)
- Component 4: Observer (trace writer, metrics collector)
- Component 5: Gate Definitions (YAML schemas)
- Component 6: Demo Kata (`project/discovery-mvp`)
- Integration testing (end-to-end test flow)
- Definition of Done (MVP acceptance criteria)
- Complete file structure

**Read this for**: Step-by-step implementation guide for developers.

---

## Quick Reference

### Key Insights

1. **"Deterministic" may be the wrong goal** - Aim for "verifiable" and "observable" instead
2. **Markdown authoring + compiled execution** is the sweet spot
3. **State machines provide governance** - The harness enforces what Markdown suggests
4. **Context management is THE bottleneck** - Multi-step workflows must manage token budgets
5. **Observability enables Kaizen** - Traces are the foundation of continuous improvement

### Recommended Architecture

```
Markdown Katas (authoring)
         ↓
    Kata Compiler
         ↓
JSON Execution Graph
         ↓
  State Machine Harness
         ↓
  Observable Execution
```

**3 Layers**:
1. **Authoring**: Humans write Markdown Katas
2. **Compilation**: Parser generates JSON execution graphs
3. **Execution**: State machine enforces ordering, gates, observability

### MVP Success Criteria

- ✅ Kata executes deterministically (same input → same path)
- ✅ Gate failure halts execution (Jidoka)
- ✅ Can resume from checkpoint after interruption
- ✅ Trace log shows complete execution history

### MVP Scope

- **Timeline**: 4 weeks
- **Demo Kata**: `project/discovery` (3 steps, 1 gate)
- **Components**: Compiler + Harness + 3 Skills + Observer
- **Output**: JSONL traces, checkpoints, execution graphs

---

## Related Documents

### Research Inputs

📝 **Research Prompt**: [`specs/main/research/prompts/kata-harness-first-principles-research.md`](../prompts/kata-harness-first-principles-research.md)
- Original research questions
- Methodology suggestions
- Expected deliverables

📋 **Prior Ontology Research**: [`command-kata-skill-ontology-report.md`](command-kata-skill-ontology-report.md)
- Kata vs. Command vs. Skill terminology analysis
- Industry framework comparison (15+ frameworks)
- Recommendation: Kata/Skill/Gate (scored 22/25)

### RaiSE Context

📜 **Constitution**: [`.raise/context/constitution.md`](../../../.raise/context/constitution.md)
- §8 Observable Workflow (MELT stack requirement)
- §4 Validation Gates (enforcement mandate)
- §7 Lean Software Development (Jidoka principle)

📖 **Glossary**: [`.raise/context/glossary.md`](../../../.raise/context/glossary.md)
- Kata: Process structured to make deviation visible
- Skill: Atomic operation with defined inputs/outputs
- Gate: Checkpoint enforcing criteria
- Kata Harness: Motor de ejecución de katas (v2.3)

🏗️ **ADR-008**: Ontology simplification (Context/Kata/Skill model)

### Current Implementation

🔧 **Example Command**: [`.claude/commands/03-feature/raise.feature.implement.md`](../../../.claude/commands/03-feature/raise.feature.implement.md)
- Current execution model (Markdown + LLM interpretation)
- Progress tracking via `progress.md`
- Jidoka blocks: "Si no puedes continuar"

---

## Research Methodology

### Approach

1. **First Principles Analysis**: Taxonomy of execution primitives from workflow theory
2. **Market Landscape**: 15+ frameworks analyzed (LangGraph, CrewAI, AutoGen, Temporal, etc.)
3. **Pattern Catalog**: Deterministic execution patterns (structured output, state machines, hybrid)
4. **Observability Design**: MELT stack implementation
5. **Governance Architecture**: Gate enforcement mechanisms
6. **Design Synthesis**: 5 architecture options evaluated, scored, ranked

### Limitations

- **No live web access**: Research based on existing knowledge + RaiSE codebase analysis
- **No user testing**: Recommendations theoretical, require validation
- **No benchmarking**: Performance metrics estimated, not measured

### Confidence Level

**High (90%+)** on:
- Execution primitives taxonomy
- Industry patterns (state machines, observability)
- RaiSE principles alignment

**Medium (70-80%)** on:
- Compilation feasibility (Markdown parsing complexity)
- MVP timeline (4 weeks estimate)

---

## Deliverables Checklist

### Research Questions (RQs)

- ✅ **RQ1**: First Principles of Agentic Workflow Execution
  - ✅ 8 execution primitives taxonomy
  - ✅ Traditional workflow guarantees vs. AI execution
  - ✅ 6 control flow patterns
  - ✅ Interruption and resumption patterns

- ✅ **RQ2**: Market Landscape Analysis
  - ✅ Framework comparison matrix (15+ frameworks)
  - ✅ Architecture deep dives (LangGraph, CrewAI, Temporal)
  - ✅ 3 emerging patterns

- ✅ **RQ3**: Deterministic Execution Patterns
  - ✅ Determinism spectrum (stochastic → deterministic)
  - ✅ Structured output enforcement
  - ✅ State machine approaches (XState + LLM)
  - ✅ Hybrid architectures (recommended pattern)

- ✅ **RQ4**: Observability & Tracing
  - ✅ MELT stack (Metrics, Events, Logs, Traces)
  - ✅ Trace data model for Kata execution
  - ✅ Real-time vs. post-hoc observability
  - ✅ Replay capability

- ✅ **RQ5**: Governance-as-Code Architecture
  - ✅ Policy enforcement challenge
  - ✅ 3 gate enforcement mechanisms (pre/post/continuous)
  - ✅ Policy as code patterns (OPA/Rego, YAML gates)
  - ✅ Separation of concerns (policy vs. mechanism)

- ✅ **RQ6**: Kata Harness Design Recommendations
  - ✅ 5 architecture options evaluated
  - ✅ Scoring matrix (90% for Compiled Kata DSL)
  - ✅ Component specifications (Compiler, Orchestrator, Skills, Observer)
  - ✅ RaiSE principles alignment
  - ✅ Trade-offs analysis

### Documents Produced

- ✅ Executive Summary (10 pages)
- ✅ First Principles Taxonomy (60 pages)
- ✅ Architecture Diagrams (15 diagrams)
- ✅ Decision Matrix (scoring + risk analysis)
- ✅ Implementation Checklist (MVP roadmap)
- ✅ Research Index (this document)

---

## Recommendation Summary

### Primary Recommendation

**Adopt Option C: Compiled Kata DSL**

**3-Layer Architecture**:
1. **Layer 1 (Authoring)**: Markdown Katas + YAML Skills/Gates
2. **Layer 2 (Compilation)**: JSON Execution Graphs
3. **Layer 3 (Execution)**: State Machine Harness + Observable MELT stack

**Why**:
- ✅ 90% score across all criteria
- ✅ Fully compliant with RaiSE Constitution
- ✅ Best balance of enforcement and UX
- ✅ Unique differentiator (no other framework uses this approach)

**MVP Timeline**: 4 weeks (Phase 1)

**Next Steps**:
1. Approve architecture
2. Prototype Kata Compiler
3. Implement State Machine Orchestrator
4. Execute demo Kata end-to-end
5. Validate Jidoka (gate failure halts)

---

## Contact

**Research Conducted By**: Claude Sonnet 4.5
**Date Completed**: 2026-01-29
**Research ID**: research-prompt-003
**Related RaiSE Version**: v2.3

For questions or clarifications, refer to the comprehensive [First Principles Taxonomy](kata-harness-first-principles-taxonomy.md) or the [Decision Matrix](kata-harness-decision-matrix.md).

---

**Status**: ✅ Research complete, ready for decision and implementation
