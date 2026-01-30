---
id: research-agent-frameworks-index
titulo: Agent Framework Architecture Research - Document Index
tipo: Research Index
fecha: 2026-01-29
version: 1.0.0
tags:
  - research
  - index
  - agent-frameworks
  - kata-harness
---

# Agent Framework Architecture Research - Document Index

## Research Overview

**Research Question**: How do leading AI agent frameworks implement workflow orchestration, and what architectural patterns emerge that can inform the design of RaiSE's Kata Harness?

**Research Date**: 2026-01-29

**Frameworks Analyzed**:
- **Tier 1**: LangGraph, CrewAI, AutoGen, Semantic Kernel
- **Tier 2**: DSPy, Agency Swarm, Rivet
- **Tier 3**: Claude MCP, OpenAI Assistants API

**Key Finding**: Graph-based execution with checkpointing (LangGraph-inspired) combined with multi-layered governance (hybrid pattern) is best suited for RaiSE's Kata Harness.

---

## Document Collection

### 1. Executive Summary
**File**: `specs/main/research/agent-frameworks-executive-summary.md`

**Purpose**: High-level overview and key recommendations for decision-makers.

**Contents**:
- Three dominant execution paradigms
- Framework comparison matrix
- Critical patterns for RaiSE Kata Harness
- Recommended architecture
- Implementation priorities
- Decision summary

**Read This If**: You need a quick overview or want to understand the key recommendations without diving into details.

**Length**: ~15 min read

---

### 2. Detailed Architecture Comparison
**File**: `specs/main/research/agent-frameworks-architecture-comparison.md`

**Purpose**: In-depth analysis of each framework's architecture, patterns, and trade-offs.

**Contents**:
- **Tier 1 Frameworks** (LangGraph, CrewAI, AutoGen, Semantic Kernel):
  - Execution model
  - Observability features
  - Governance mechanisms
  - Context management
  - Architecture diagrams
- **Tier 2 Frameworks** (DSPy, Agency Swarm, Rivet)
- **Tier 3 Frameworks** (Claude MCP, OpenAI Assistants)
- Comparison matrix
- Key architectural patterns identified
- Implications for RaiSE Kata Harness

**Read This If**: You're designing the Kata Harness architecture and need detailed understanding of how each framework approaches workflow orchestration.

**Length**: ~45 min read

---

### 3. Visual Comparison
**File**: `specs/main/research/agent-frameworks-visual-comparison.md`

**Purpose**: Side-by-side visual comparisons using Mermaid diagrams.

**Contents**:
- Execution flow comparison (Linear, Graph, Agent-based)
- Governance pattern comparison (Interrupt, Proxy, Required Action, Filter)
- Context management comparison (State Object, Message History, Context Variables, Task Chain)
- Observability architecture comparison (Span-based, Log-based, Visual, Step-based)
- Error handling & recovery patterns
- Checkpoint & resume patterns
- Workflow complexity support
- Memory & context window management
- Integration & extensibility patterns
- Production readiness comparison
- Synthesis: Pattern clusters
- Recommended architecture for Kata Harness

**Read This If**: You're a visual learner or need to compare specific patterns across frameworks side-by-side.

**Length**: ~30 min read (heavy on diagrams)

---

### 4. Quick Reference Card
**File**: `specs/main/research/agent-frameworks-quick-reference.md`

**Purpose**: One-page cheat sheet for quick pattern lookups during architecture discussions.

**Contents**:
- Quick decision guide
- Core patterns summary (Execution, Governance, Context)
- Pattern selection matrix
- Observability quick guide
- Governance checklist
- Anti-patterns to avoid
- Implementation checklist
- Code templates
- Framework capabilities grid
- RaiSE Kata Harness recommendation

**Read This If**: You need a quick reference during implementation or want to look up specific patterns without reading full docs.

**Length**: ~5 min scan

---

### 5. This Index
**File**: `specs/main/research/agent-frameworks-research-index.md`

**Purpose**: Navigation guide for the research document collection.

---

## Reading Paths

### Path 1: Executive → Implementation
**For**: Developers implementing the Kata Harness

1. Read **Executive Summary** (~15 min)
   - Understand key recommendations
2. Skim **Visual Comparison** (~15 min)
   - Look at recommended architecture diagrams
3. Keep **Quick Reference** open during implementation
   - Use for pattern lookups and code templates

**Total Time**: ~30 min + ongoing reference

---

### Path 2: Deep Dive → Design
**For**: Architects designing the Kata Harness

1. Read **Executive Summary** (~15 min)
   - Understand landscape and recommendations
2. Read **Detailed Comparison** (~45 min)
   - Deep understanding of each framework
3. Study **Visual Comparison** (~30 min)
   - Compare patterns visually
4. Use **Quick Reference** for decisions
   - Pattern selection and trade-offs

**Total Time**: ~90 min

---

### Path 3: Quick Decision
**For**: Leadership making architectural decisions

1. Read **Executive Summary** (~15 min)
   - Key findings and recommendations
2. Review **Quick Reference** (~5 min)
   - Pattern overview and capabilities grid
3. Ask questions based on **Detailed Comparison**
   - Consult for specific concerns

**Total Time**: ~20 min

---

### Path 4: Research Validation
**For**: Reviewers validating research quality

1. Skim **Executive Summary** (~10 min)
   - Understand conclusions
2. Review **Detailed Comparison** in depth (~60 min)
   - Validate analysis per framework
3. Check **Visual Comparison** (~30 min)
   - Verify pattern synthesis
4. Cross-check **Quick Reference** (~10 min)
   - Ensure consistency with detailed docs

**Total Time**: ~110 min

---

## Key Insights by Topic

### Execution Models
- **Best for structured workflows**: Graph-based (LangGraph)
- **Best for exploration**: Conversation-based (AutoGen)
- **Best for collaboration**: Agent-based (CrewAI)
- **Best for optimization**: Declarative + Compile (DSPy)

**→ For RaiSE Katas**: Graph-based (explicit steps, branching, cycles)

### Checkpointing
- **Only framework with automatic checkpointing**: LangGraph
- **Thread-level persistence**: OpenAI Assistants
- **Manual snapshots**: Rivet
- **Most frameworks**: No checkpointing

**→ For RaiSE Katas**: Critical requirement, adopt LangGraph pattern

### Governance
- **Interrupt pattern** (LangGraph): Clean pause/resume for gates
- **Assertion pattern** (DSPy): Inline verification with auto-retry
- **Filter pattern** (Semantic Kernel): Policy enforcement hooks
- **Proxy pattern** (AutoGen): Dedicated human agent

**→ For RaiSE Katas**: Multi-layered (all four patterns)

### Observability
- **Production-ready**: LangGraph (LangSmith), Semantic Kernel (OpenTelemetry)
- **Development-friendly**: CrewAI, AutoGen (logs)
- **Visual**: Rivet (real-time graph)
- **API-native**: OpenAI Assistants (run steps)

**→ For RaiSE Katas**: OpenTelemetry for production, plus learning analytics

### Context Management
- **Typed state**: LangGraph (StateGraph with schema)
- **Message history**: AutoGen, OpenAI Assistants
- **Context variables**: Semantic Kernel
- **Task chaining**: CrewAI

**→ For RaiSE Katas**: Typed state + Artifact registry (hybrid)

---

## Frameworks at a Glance

| Framework | Best For | RaiSE Relevance | Learn More |
|-----------|----------|-----------------|------------|
| **LangGraph** | Structured workflows with complex control flow | ⭐⭐⭐⭐⭐ Highest | Detailed Comparison §1 |
| **CrewAI** | Multi-agent collaboration, role-based teams | ⭐⭐ Limited structure | Detailed Comparison §2 |
| **AutoGen** | Conversational workflows, code generation | ⭐⭐ Emergent flow | Detailed Comparison §3 |
| **Semantic Kernel** | Enterprise integration, plugin ecosystems | ⭐⭐⭐⭐ Governance patterns | Detailed Comparison §4 |
| **DSPy** | Optimizable programs, ML pipelines | ⭐⭐⭐⭐ Verification pattern | Detailed Comparison §5 |
| **Agency Swarm** | Hierarchical agent teams | ⭐ Early stage | Detailed Comparison §6 |
| **Rivet** | Visual workflow design, prototyping | ⭐⭐⭐ Visual inspiration | Detailed Comparison §7 |
| **Claude MCP** | Tool integration (protocol, not framework) | ⭐ Not orchestration | Detailed Comparison §8 |
| **OpenAI Assistants** | Conversational assistants, file processing | ⭐⭐ Limited control | Detailed Comparison §9 |

---

## Recommended Next Steps

### 1. Architecture Design Session
**Documents to Bring**:
- Executive Summary (for alignment)
- Visual Comparison (for architecture diagrams)
- Quick Reference (for pattern decisions)

**Goals**:
- Finalize Kata Harness architecture
- Define component interfaces
- Create data models (KataState, VerificationResult, etc.)

### 2. Prototype Sprint
**Reference Documents**:
- Quick Reference (code templates)
- Detailed Comparison (pattern details)

**Goals**:
- Build MVP: Graph execution + checkpointing
- Test with existing Kata (e.g., flujo-1-discovery)
- Validate Jidoka handler flow

### 3. Governance Implementation
**Reference Documents**:
- Visual Comparison (governance patterns)
- Quick Reference (governance checklist)

**Goals**:
- Implement inline verification (assertions)
- Implement Validation Gates (interrupt pattern)
- Build Jidoka handler with human intervention

### 4. Observability Integration
**Reference Documents**:
- Detailed Comparison (Semantic Kernel telemetry)
- Quick Reference (telemetry schema)

**Goals**:
- OpenTelemetry integration
- Define learning analytics schema
- Build queries for Kata execution insights

### 5. Validation & Iteration
**Reference Documents**:
- All documents (for validation against principles)

**Goals**:
- Review against RaiSE Constitution
- Validate with real Kata use cases
- Iterate based on team feedback

---

## Research Methodology Notes

**Limitations**:
- Web search and web fetch tools were unavailable during research due to permission restrictions
- Analysis based on framework knowledge as of January 2025 (training cutoff)
- Some frameworks may have released updates since cutoff date

**Strengths**:
- Comprehensive analysis across 9 major frameworks
- Multi-dimensional evaluation (execution, observability, governance, context)
- Practical code examples and templates
- Visual comparisons for pattern clarity
- Clear recommendations for RaiSE use case

**Validation Needed**:
- Confirm current framework capabilities (especially post-Jan 2025 updates)
- Prototype recommended patterns with real Katas
- Validate performance characteristics under load
- Confirm integration compatibility with RaiSE toolchain

---

## Questions for Further Research

1. **Performance**: How do checkpointing strategies impact execution latency?
2. **Scale**: Can graph-based execution handle complex multi-Kata workflows (10+ Katas)?
3. **Learning**: What telemetry schema best supports heutagogical learning analytics?
4. **Integration**: How to integrate Kata Harness with existing RaiSE commands?
5. **User Experience**: What visibility do Orquestadores need during Kata execution?

**Recommendation**: Prototype and measure before committing to final architecture.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial research publication |

---

## Document Locations

All documents in this collection are located in:

```
raise-commons/
└── specs/
    └── main/
        └── research/
            ├── agent-frameworks-research-index.md           [This file]
            ├── agent-frameworks-executive-summary.md        [Summary]
            ├── agent-frameworks-architecture-comparison.md  [Detailed]
            ├── agent-frameworks-visual-comparison.md        [Visual]
            └── agent-frameworks-quick-reference.md          [Reference]
```

---

## Related RaiSE Documents

- **Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`
- **Glossary**: `docs/framework/v2.1/model/20-glossary-v2.1.md`
- **Methodology**: `docs/framework/v2.1/model/21-methodology-v2.md`
- **Katas**: `docs/framework/v2.1/katas/`

---

**Document Status**: Complete
**Research Status**: Phase 1 Complete (Framework Analysis)
**Next Phase**: Architecture Design + Prototyping
