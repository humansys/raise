---
id: kata-harness-decision-matrix
title: "Kata Harness: Architecture Decision Matrix"
date: 2026-01-29
status: complete
purpose: decision-support
related_to: ["kata-harness-first-principles-taxonomy", "kata-harness-executive-summary"]
---

# Kata Harness: Architecture Decision Matrix

## Quick Reference: Architecture Options

### Evaluation Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Enforcement** | 25% | Can the architecture guarantee step ordering and gate compliance? |
| **Observability** | 20% | Can every decision be traced and audited? |
| **Authoring UX** | 20% | How easy is it to create and maintain Katas? |
| **Jidoka** | 15% | Does it support stop-the-line on defects? |
| **Implementation** | 10% | How complex is the implementation? |
| **Extensibility** | 10% | Can new features be added without breaking changes? |

---

## Options Comparison

| Option | Description | Enforcement | Observability | Authoring UX | Jidoka | Implementation | Extensibility | **Total Score** |
|--------|-------------|-------------|---------------|--------------|--------|----------------|---------------|-----------------|
| **A: Enhanced Markdown** | Current approach + better prompting | 🔴 2/5 | 🟡 3/5 | 🟢 5/5 | 🔴 2/5 | 🟢 5/5 | 🟡 3/5 | **20/30 (67%)** |
| **B: State Machine + LLM** | XState-like orchestrator | 🟢 5/5 | 🟢 4/5 | 🔴 2/5 | 🟢 5/5 | 🟡 3/5 | 🟢 4/5 | **23/30 (77%)** |
| **C: Compiled Kata DSL** ⭐ | Parse MD → JSON → Execute | 🟢 5/5 | 🟢 5/5 | 🟢 4/5 | 🟢 5/5 | 🟡 3/5 | 🟢 5/5 | **27/30 (90%)** |
| **D: Pure LangGraph** | Adopt LangGraph wholesale | 🟢 5/5 | 🟢 4/5 | 🔴 2/5 | 🟡 3/5 | 🟢 4/5 | 🟡 3/5 | **21/30 (70%)** |
| **E: Hybrid Templates** | Templates → LLM fills → Execute | 🟡 4/5 | 🟡 3/5 | 🟡 3/5 | 🟡 4/5 | 🟡 3/5 | 🟡 3/5 | **20/30 (67%)** |

**Legend**: 🟢 Excellent (5-4) | 🟡 Adequate (3) | 🔴 Poor (2-1)

**Winner**: **Option C (Compiled Kata DSL)** - 90% score

---

## Detailed Breakdown

### Option A: Enhanced Markdown + Better LLM Prompting

**How it works**: Improve current system with better prompts, more explicit instructions, structured output (JSON mode)

**Pros**:
- ✅ No implementation changes needed
- ✅ Markdown authoring remains simple
- ✅ Low learning curve

**Cons**:
- ❌ No enforcement (LLM can still skip steps)
- ❌ Gates are suggestions, not blockers
- ❌ Manual state management (progress.md)
- ❌ Observability depends on LLM logging correctly

**Verdict**: **Not recommended** - Does not solve the core enforcement problem

---

### Option B: State Machine + LLM Steps

**How it works**: Define workflows as state machines (XState), LLM is invoked as a service per step

**Example**:
```typescript
const discoveryMachine = createMachine({
  initial: 'loadPRD',
  states: {
    loadPRD: {
      invoke: { src: 'loadPRDService', onDone: 'extractReqs' }
    },
    extractReqs: {
      invoke: { src: 'llmService', onDone: 'validate' }
    }
  }
});
```

**Pros**:
- ✅ State transitions enforced
- ✅ Gates as guard conditions
- ✅ Full observability (every transition logged)
- ✅ Jidoka: halt on error

**Cons**:
- ❌ Requires coding workflows (TypeScript/Python)
- ❌ Markdown katas become secondary (documentation only)
- ❌ Higher implementation complexity

**Verdict**: **Strong option** but loses Markdown-first authoring

---

### Option C: Compiled Kata DSL ⭐ **RECOMMENDED**

**How it works**:
1. Orquestador writes Kata in Markdown (pedagogical, accessible)
2. Compiler parses Markdown → JSON execution graph
3. State machine harness executes graph with enforcement

**Example**:
```markdown
## Paso 1: Cargar PRD
- Cargar `specs/main/prd.md`
**Verificación**: Archivo existe
```

→ Compiles to:
```json
{
  "id": "paso-1",
  "skill": "file/load",
  "inputs": {"path": "specs/main/prd.md"},
  "verification": {"gate": "gate-prd-loaded", "blocking": true}
}
```

**Pros**:
- ✅ Markdown authoring (accessible, Git-friendly)
- ✅ Enforced execution (state machine)
- ✅ Full observability (MELT stack)
- ✅ Jidoka: blocking gates
- ✅ Resumability: automatic checkpoints
- ✅ Best of both worlds (flexibility + enforcement)

**Cons**:
- ⚠️ Compilation step adds complexity
- ⚠️ Need to maintain compiler
- ⚠️ Markdown parsing can be fragile

**Verdict**: **RECOMMENDED** - Optimal balance of enforcement and UX

---

### Option D: Pure LangGraph

**How it works**: Adopt LangGraph framework for all workflows

**Example**:
```python
workflow = StateGraph(WorkflowState)
workflow.add_node("load_prd", load_prd_node)
workflow.add_node("extract_reqs", extract_reqs_node)
workflow.add_edge("load_prd", "extract_reqs")
app = workflow.compile()
```

**Pros**:
- ✅ Battle-tested framework
- ✅ Full state machine semantics
- ✅ Checkpointing built-in
- ✅ LangSmith observability

**Cons**:
- ❌ Python/coding required (no Markdown authoring)
- ❌ Vendor lock-in (LangChain ecosystem)
- ❌ Loses RaiSE's pedagogical approach
- ❌ Not platform-agnostic (violates §3)

**Verdict**: **Not recommended** - Conflicts with RaiSE principles (Markdown authoring, platform agnosticism)

---

### Option E: Hybrid Templates

**How it works**: Pre-defined templates with slots, LLM fills slots, harness executes

**Example**:
```yaml
template: discovery
steps:
  - load_document:
      path: {{LLM_FILL: document_path}}
  - extract_requirements:
      method: {{LLM_FILL: extraction_method}}
```

**Pros**:
- ✅ Some enforcement (template structure)
- ✅ LLM has flexibility (fill slots)
- ✅ Easier to parse than free-form Markdown

**Cons**:
- ⚠️ Less flexible than full Markdown
- ⚠️ Template maintenance burden
- ⚠️ Still relies on LLM for critical decisions

**Verdict**: **Middle ground** but less appealing than Compiled Kata DSL

---

## Decision Criteria Deep Dive

### 1. Enforcement (25% weight)

**Question**: Can the architecture guarantee step ordering and gate compliance?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 2/5 | LLM interpretation - no guarantees |
| B: State Machine | 5/5 | State machine enforces transitions |
| C: Compiled DSL | 5/5 | State machine + compiled semantics |
| D: LangGraph | 5/5 | Graph execution guarantees |
| E: Hybrid Templates | 4/5 | Template structure + LLM slots |

**Winner**: B, C, D (tie)

---

### 2. Observability (20% weight)

**Question**: Can every decision be traced and audited?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 3/5 | LLM must log correctly (unreliable) |
| B: State Machine | 4/5 | State transitions logged |
| C: Compiled DSL | 5/5 | Harness logs every step + MELT stack |
| D: LangGraph | 4/5 | LangSmith integration |
| E: Hybrid Templates | 3/5 | Depends on LLM logging |

**Winner**: C (full MELT stack)

---

### 3. Authoring UX (20% weight)

**Question**: How easy is it to create and maintain Katas?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 5/5 | Pure Markdown (familiar) |
| B: State Machine | 2/5 | Coding required (TypeScript/Python) |
| C: Compiled DSL | 4/5 | Markdown + conventions (minor learning curve) |
| D: LangGraph | 2/5 | Coding required (Python) |
| E: Hybrid Templates | 3/5 | YAML templates (less familiar) |

**Winner**: A (but fails enforcement)

---

### 4. Jidoka Compliance (15% weight)

**Question**: Does it support stop-the-line on defects?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 2/5 | LLM interprets Jidoka blocks (unreliable) |
| B: State Machine | 5/5 | Error states halt execution |
| C: Compiled DSL | 5/5 | Blocking gates enforced by harness |
| D: LangGraph | 3/5 | Can implement, not first-class |
| E: Hybrid Templates | 4/5 | Template can enforce, LLM can bypass |

**Winner**: B, C (tie)

---

### 5. Implementation Complexity (10% weight)

**Question**: How complex is the implementation?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 5/5 | Minimal changes to current system |
| B: State Machine | 3/5 | State machine lib + integration |
| C: Compiled DSL | 3/5 | Compiler + harness runtime |
| D: LangGraph | 4/5 | Adopt existing framework |
| E: Hybrid Templates | 3/5 | Template engine + LLM integration |

**Winner**: A (but fails enforcement)

---

### 6. Extensibility (10% weight)

**Question**: Can new features be added without breaking changes?

| Option | Score | Justification |
|--------|-------|---------------|
| A: Enhanced Markdown | 3/5 | Ad-hoc prompting patterns |
| B: State Machine | 4/5 | Add new states/transitions |
| C: Compiled DSL | 5/5 | Extend compiler, add skills/gates |
| D: LangGraph | 3/5 | Framework constraints |
| E: Hybrid Templates | 3/5 | New templates needed for new patterns |

**Winner**: C (modular architecture)

---

## Alignment with RaiSE Principles

### Constitution Compliance Matrix

| Principle | Option A | Option B | Option C ⭐ | Option D | Option E |
|-----------|----------|----------|------------|----------|----------|
| **§1. Humanos Definen** | ✅ | ⚠️ Code | ✅ MD | ❌ Code | ⚠️ Templates |
| **§2. Governance as Code** | ⚠️ Suggested | ✅ | ✅ | ✅ | ✅ |
| **§3. Platform Agnostic** | ✅ | ✅ | ✅ | ❌ LangChain | ✅ |
| **§4. Validation Gates** | ❌ Suggested | ✅ Guards | ✅ Enforced | ⚠️ Custom | ⚠️ Partial |
| **§5. Heutagogía** | ✅ | ❌ Code | ✅ MD | ❌ Code | ⚠️ |
| **§7. Jidoka** | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| **§8. Observable Workflow** | ⚠️ | ✅ | ✅ MELT | ✅ LangSmith | ⚠️ |

**Legend**: ✅ Fully compliant | ⚠️ Partially compliant | ❌ Non-compliant

**Winner**: **Option C** - Fully compliant with all principles

---

## Risk Analysis

### Option C: Compiled Kata DSL (Recommended)

**Risks**:

1. **Parsing Fragility**
   - **Risk**: Markdown parsing is complex, prone to edge cases
   - **Mitigation**: Strict Kata conventions, validation at compile time, extensive test suite
   - **Severity**: Medium

2. **Compilation Overhead**
   - **Risk**: Extra step between authoring and execution
   - **Mitigation**: Fast compiler (<1s), cache compiled graphs, watch mode for development
   - **Severity**: Low

3. **Mapping Ambiguity**
   - **Risk**: Markdown actions may not map cleanly to skills
   - **Mitigation**: Well-documented conventions, compiler validation, clear error messages
   - **Severity**: Medium

4. **Maintenance Burden**
   - **Risk**: Compiler needs updates as Markdown conventions evolve
   - **Mitigation**: Modular compiler architecture, comprehensive tests, versioning
   - **Severity**: Medium

**Overall Risk**: **Medium** (manageable with good engineering practices)

---

## Trade-off Summary

| What You Gain | What You Trade |
|---------------|----------------|
| ✅ Enforced governance | ⚠️ Compilation step |
| ✅ Observable execution | ⚠️ Trace storage |
| ✅ Resumability | ⚠️ Checkpoint management |
| ✅ Jidoka compliance | ⚠️ Less LLM flexibility |
| ✅ Deterministic path | ⚠️ Markdown conventions |

**Verdict**: **Trade-offs are worthwhile**

Enforcement and observability are core RaiSE values (Constitution §2, §4, §8). The trade-offs (compilation, storage) are acceptable costs for achieving governance goals.

---

## Final Recommendation

### Primary Recommendation: **Option C (Compiled Kata DSL)**

**Why**:

1. **90% score** (highest across all criteria)
2. **Fully compliant** with RaiSE Constitution (all 8 principles)
3. **Best balance** of enforcement and UX
4. **Extensible** (modular architecture)
5. **Unique differentiator** (no other framework does this)

**Implementation**: 3-layer architecture
- Layer 1: Markdown authoring (Katas, Skills, Gates)
- Layer 2: JSON execution graphs (compiled)
- Layer 3: State machine runtime (enforced)

**MVP Scope**: Single Kata (`project/discovery`), 3 steps, 3 skills, 1 gate, JSONL traces

**Timeline**: 4 weeks (Phase 1)

---

### Fallback Option: **Option B (State Machine + LLM)**

**If** compilation proves too complex, fall back to pure state machine approach.

**Trade-off**: Lose Markdown authoring, require coding workflows.

**Trigger**: If compiler cannot reliably parse 80%+ of Katas by Week 2.

---

## Next Steps

1. **Decision**: Approve Option C (Compiled Kata DSL)
2. **Prototype**: Build minimal compiler (parse 1 Kata → JSON)
3. **Validate**: Execute demo Kata end-to-end
4. **Measure**: Confirm enforcement (gate failure halts)
5. **Iterate**: Expand to all Work Cycles (Phase 2)

---

**Decision Date**: TBD
**Approved By**: TBD
**Status**: Pending approval
