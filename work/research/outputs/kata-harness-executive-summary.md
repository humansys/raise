---
id: kata-harness-executive-summary
title: "Kata Harness Executive Summary: From First Principles to Implementation"
date: 2026-01-29
status: complete
audience: decision-makers
related_to: ["kata-harness-first-principles-taxonomy", "ADR-008"]
---

# Kata Harness Executive Summary

## The Problem

RaiSE v2.3 introduced Katas as multi-step SDLC workflows with stated goals of **deterministic execution** and **enforced governance**. However, the current implementation (Markdown files interpreted by LLMs) provides only **suggestions**, not **guarantees**.

**The fundamental tension:**
```
Desired: Deterministic governance, guaranteed step execution, enforced gates
Reality: LLM may skip steps, hallucinate verification, ignore Jidoka triggers
```

## The Research Question

What are the fundamental primitives required to execute multi-step AI agent workflows with deterministic guarantees?

## Key Findings

### Finding 1: "Deterministic" May Be the Wrong Goal

**Traditional workflow engines** (Temporal, Prefect) achieve determinism through explicit state machines. **LLM-based systems** are inherently probabilistic.

**Better goal**: **Verifiable** and **Observable** execution
- Same input → traceable path (may vary, but logged)
- Every decision is auditable
- Failures trigger explicit halt (Jidoka)

### Finding 2: The Industry Pattern is "Thin LLM, Thick Orchestrator"

Leading frameworks (LangGraph, CrewAI) separate concerns:

```
Orchestrator (State Machine) → LLM (Decision Only) → Tools (Execution)
```

- **Orchestrator**: Controls flow, enforces gates, manages state
- **LLM**: Makes decisions ("which path?", "is this sufficient?")
- **Tools**: Execute atomic operations (deterministic)

**Benefit**: Governance is enforced by orchestrator, not suggested to LLM

### Finding 3: Markdown Authoring + Compiled Execution is the Sweet Spot

**Pattern**: Parse Markdown → JSON execution graph → State machine executes

**Pros**:
- ✅ Markdown authoring (accessible, version-controlled, pedagogical)
- ✅ Enforced execution (state machine guarantees ordering)
- ✅ Observable (every step transition logged)
- ✅ Resumable (state persisted as checkpoint)

**Examples**: DSPy (LLM generates code), Rivet (visual programming compiles to graph)

### Finding 4: Context Management is THE Bottleneck

Multi-step workflows face token window constraints:
- Each step consumes tokens
- Context can drift across steps
- Budget allocation critical

**Solution**: Explicit context manager (like RaiSE's MVC retrieval)

### Finding 5: Observability Enables Kaizen

Full MELT stack (Metrics, Events, Logs, Traces) required for:
- Debugging (what went wrong?)
- Auditing (compliance requirements)
- Improvement (which steps are slow/fail frequently?)

## The Recommendation

### Adopt a 3-Layer Execution Architecture

```
┌───────────────────────────────────────────────┐
│  LAYER 1: AUTHORING                            │
│  Humans write Markdown Katas + YAML Skills    │
└───────────────────────────────────────────────┘
                    ↓
            [Kata Compiler]
                    ↓
┌───────────────────────────────────────────────┐
│  LAYER 2: EXECUTION PLAN                       │
│  Compiled JSON graph (steps, gates, skills)   │
└───────────────────────────────────────────────┘
                    ↓
         [Kata Harness Runtime]
                    ↓
┌───────────────────────────────────────────────┐
│  LAYER 3: STATE MACHINE EXECUTION              │
│  - Enforced step ordering                     │
│  - Blocking gates (Jidoka)                    │
│  - Checkpointing (resumability)               │
│  - Full observability (JSONL traces)          │
└───────────────────────────────────────────────┘
```

### How It Works

1. **Authoring**: Orquestador writes Kata in Markdown (no code needed)
2. **Compilation**: Parser extracts steps, gates, dependencies → JSON
3. **Execution**: State machine harness enforces ordering, gates, logging
4. **Observability**: Every step logged to JSONL for replay/analysis

### What Changes from Current Approach

| Aspect | Current (Markdown + LLM) | Recommended (Harness) |
|--------|--------------------------|----------------------|
| **Step ordering** | LLM interprets | State machine enforces |
| **Gates** | Suggested | Blocking (halt on fail) |
| **Resumability** | Manual (progress.md) | Automatic (checkpoints) |
| **Observability** | Ad-hoc | Built-in (JSONL traces) |
| **Debugging** | Hard (LLM black box) | Replay from traces |

## Alignment with RaiSE Principles

| Principle | How Harness Honors It |
|-----------|----------------------|
| §1. Humanos Definen | Markdown authoring (accessible) |
| §2. Governance as Code | Gates/skills as versioned YAML |
| §4. Validation Gates | Enforced by harness, not suggested |
| §7. Jidoka | Halt on gate failure (mandatory) |
| §8. Observable Workflow | Full MELT stack (metrics, events, logs, traces) |

## MVP Scope (Weeks 1-4)

**Goal**: Prove the architecture with a single Kata

**Components**:
1. Kata Compiler (Markdown → JSON)
2. State Machine Orchestrator
3. 3 Skills: `file/load`, `llm/call`, `gate/run`
4. JSONL trace logging

**Demo Kata**: `project/discovery` (3 steps, 1 gate)

**Success Criteria**:
- ✅ Kata executes deterministically (same input → same path)
- ✅ Gate failure halts execution (Jidoka)
- ✅ Can resume from checkpoint
- ✅ Trace log shows complete history

## Trade-offs

| Benefit | Cost |
|---------|------|
| ✅ Enforced governance | ⚠️ Compilation step added |
| ✅ Observable execution | ⚠️ Trace storage overhead |
| ✅ Resumability | ⚠️ Checkpoint management |
| ✅ Deterministic path | ⚠️ Less LLM flexibility |

**Verdict**: Trade-offs are **worthwhile** because:
- Governance enforcement is a core RaiSE value
- Observability is mandated by Constitution (§8)
- Jidoka requires halt-on-failure capability

## Competitive Differentiation

RaiSE's Kata Harness uniquely combines:

1. **Lean principles as first-class citizens** (Jidoka, Kaizen, ShuHaRi)
2. **Markdown authoring** (accessible to non-developers)
3. **Enforced governance** (not suggested to LLM)
4. **Full observability** (MELT stack)
5. **"Kata" terminology** (unique in AI agent space - genuine brand differentiator)

**No other framework** (LangGraph, CrewAI, AutoGen) emphasizes:
- Stop-the-line (Jidoka) as architectural primitive
- Heutagogical learning (teach, not just execute)
- Markdown-first authoring with compiled enforcement

## Next Steps

1. **Decision**: Approve 3-layer architecture
2. **Prototype**: Build Kata Compiler (Markdown → JSON)
3. **Implement**: State Machine Orchestrator (MVP)
4. **Validate**: Execute `project/discovery` Kata end-to-end
5. **Measure**: Confirm Jidoka (gate failure halts)

## Full Research Report

For complete analysis of:
- 8 execution primitives taxonomy
- 15+ framework comparisons
- Deterministic execution patterns
- Observability data models
- Implementation roadmap

See: `/home/emilio/Code/raise-commons/specs/main/research/outputs/kata-harness-first-principles-taxonomy.md`

---

**Research completed**: 2026-01-29
**Recommendation**: Proceed with MVP (Phase 1) implementation
**Confidence**: High (based on industry patterns + RaiSE principles alignment)
