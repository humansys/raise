# Epic E13: Discovery — Codebase Understanding for Rai

> **Status:** Pre-Design (research phase)
> **Branch:** `feature/e13/discovery`
> **Created:** 2026-02-04
> **Target:** Feb 9, 2026 (F&F MVP)
> **Research:** `work/research/architecture-representation-for-ai/` (RES-ARCH-REP-001)

---

## Problem Statement

Rai lacks a fast way to understand what's already developed in a codebase and what can be reused or adapted. This leads to:
- Re-discovering patterns by reading code each session
- Risk of duplicating functionality
- Inconsistent extension of existing components
- No protection against architectural drift from external contributors

---

## Vision

**Discovery** = A toolkit for Rai to analyze codebases and produce human-validated architecture documentation that feeds the unified knowledge graph.

### The Discovery Lifecycle

```
1. ESTABLISH (initial discovery)
   /discover-start → scan → describe → complete
   Result: Component catalog in unified graph

2. GUARD (ongoing)
   /discover-check (on PR/commit)
   Compare changes against baseline
   Flag: violations, potential evolutions

3. EVOLVE (when patterns change)
   /discover-update
   Human approves evolution
   Baseline updated in graph

4. REFRESH (periodic)
   /discover-scan (re-scan)
   Detect accumulated drift
   Reconcile baseline with reality
```

---

## Research Completed

### RES-ARCH-REP-001: Architecture Representation for AI

**Key Findings:**
1. **Aider's Repository Map** is the proven pattern (82% vs 68% accuracy with context)
2. **C4 Model's 4 levels** provide the right abstraction hierarchy
3. **Tree-sitter** is the modern standard for extraction
4. **Component catalogs** (Backstage pattern) enable reuse
5. **Hybrid extraction** (deterministic + LLM) is academically validated

**Recommended Node Types:**
- `system` — Top-level system description
- `module` — Package/directory level
- `component` — Class/service/function with interface
- `convention` — Observed coding pattern

---

## Pre-Design Research: Aider Reverse Engineering

**Status:** Pending
**Purpose:** Decide whether to fork, adapt, or just learn from Aider's repo map implementation

**Questions to answer:**
1. How is Aider's repo map architecturally structured? Is it separable?
2. What dependencies does it require? (Tree-sitter bindings, etc.)
3. What graph ranking algorithm do they use?
4. How do they handle token budgeting?
5. What does the output format look like?

**Output:** Decision on implementation approach (fork/adapt/inspire)

---

## Scope (Draft — Pending Design)

### In Scope (F&F MVP)

**Must:**
- [ ] Component catalog in unified graph (system, module, component nodes)
- [ ] Extraction tools using Tree-sitter/ast-grep
- [ ] Human-sequenced discovery skills (`/discover-*`)
- [ ] Basic drift detection on changes

**Should:**
- [ ] Pattern/convention extraction
- [ ] CLI commands (`raise discover`)

### Out of Scope (Post-F&F)

- Function-level granularity
- Call graphs / data flow analysis
- Git history integration
- Full CI/CD drift detection
- Multi-repo support

---

## Features (Draft)

| ID | Feature | Size | Status |
|----|---------|:----:|:------:|
| F13.0 | Aider Reverse Engineering | XS | Pending |
| F13.1 | Schema Extension (node types) | S | Pending |
| F13.2 | Extraction Toolkit | M | Pending |
| F13.3 | Discovery Skills | M | Pending |
| F13.4 | Drift Detection | S | Pending |

---

## Dependencies

- **E11 Unified Graph** ✅ — Node type extension
- **E12 Knowledge Graph** ✅ — Graph infrastructure
- **Tree-sitter/ast-grep** — External tool dependency

---

## Open Questions

1. Fork Aider's repo map code or implement from scratch?
2. How much of the old SAR vision (confidence scores, enforcement levels) do we keep?
3. Should drift detection block merges or just warn?
4. What's the minimum extraction for F&F that validates the approach?

---

## Timeline (Tentative)

| Day | Date | Work | Status |
|:---:|------|------|:------:|
| 1 | Feb 4 | Pre-design: Aider reverse engineering | In Progress |
| 1 | Feb 4 | Epic design finalization | Pending |
| 2-3 | Feb 5-6 | Implementation (F13.1, F13.2) | Pending |
| 4 | Feb 7 | Skills + Integration (F13.3) | Pending |
| 5 | Feb 8 | Drift detection + Polish (F13.4) | Pending |
| — | Feb 9 | **F&F Ready** | Target |

---

*Epic tracking — update per feature completion*
*Created: 2026-02-04*
*Phase: Pre-Design (Aider research pending)*
