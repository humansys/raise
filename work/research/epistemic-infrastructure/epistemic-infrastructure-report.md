# Research Report: Epistemic Infrastructure for AI Coding Agents

> **Date:** 2026-03-22
> **Researcher:** Emilio + Rai
> **Depth:** Standard (22 sources, 4 research tracks)
> **Confidence:** HIGH — all three thesis claims validated with 5+ independent sources each
> **Story:** RAISE-653 / S650.1
> **Feeds into:** ADR for Domain Cartridge Architecture (RAISE-652)

---

## Executive Summary

The three thesis claims are **validated by converging evidence** from academic research, production systems, and industry practice. However, the research reveals that **no existing system combines all three** into a unified framework. This gap — the integration of schema-validated domain cartridges with neuro-symbolic JIT delivery — is RaiSE's genuine frontier contribution.

The closest prior art is "Codified Context" (three-tier docs for coding agents) and Augment Code (semantic knowledge graph over codebases). Neither implements schema contracts, build-time validation, or pluggable multi-domain knowledge.

---

## 1. Thesis Validation

### T1: Agent reliability is bounded by knowledge source quality ✓

**Confidence: VERY HIGH**

The strongest evidence comes from two directions:

1. **Formal measurement** (S02, arXiv 2602.16666): Across 14 frontier models over 18 months, "reliability gains lag noticeably behind capability progress." Making the model better doesn't make the agent more reliable — the bottleneck is elsewhere.

2. **Empirical demonstration** (S03, ACM 2025): A 7B-parameter model with structured knowledge graph reasoning outperforms GPT-4 by 37% on knowledge-graph QA. This is the single most powerful data point: **structured knowledge infrastructure compensates for orders-of-magnitude less model capability.**

3. **Production evidence** (S01, S15): Both the Codified Context study (283 sessions) and industry practitioners identify knowledge staleness and data pipeline failures as the primary failure modes — not LLM limitations.

### T2: Requires dedicated infrastructure — contracts, validation, traceability ✓

**Confidence: HIGH (with a nuance)**

The nuance: everyone agrees infrastructure is needed, but **nobody has formalized it as contracts + validation**. The prior art is:

- **Codified Context** (S01): Three tiers of documentation. No contracts, no validation. Staleness is their #1 problem — which contracts would solve.
- **Google ADK** (S05): Three-layer context architecture. Scoping and compaction, but no domain-specific validation.
- **Industry consensus** (S15): "Tight input/output contracts" and "governed knowledge index with freshness SLAs" are recommended best practices, but no system implements them.

**This is the gap.** Everyone says "knowledge quality matters" but treats it as a documentation problem. Nobody treats it as a **contract enforcement problem** analogous to API contracts or data contracts in data mesh.

### T3: Neuro-symbolic JIT delivery with minimum viable context ✓

**Confidence: VERY HIGH**

This is emerging consensus from independent sources:

- **Google ADK** (S05): "Every model call sees the minimum context required" — architectural principle, not suggestion.
- **Martin Fowler** (S04): "Start minimal — models are powerful enough that less context often works better."
- **SymAgent** (S03): Neural planner + symbolic executor outperforms pure neural approaches.
- **Augment Code** (S06): Contextual compression (4,456 → 682 sources) as key differentiator.
- **ACE** (S10): Structured itemized context > monolithic prompts.

The industry is converging on this independently. Our contribution is applying it with **domain-specific contracts** rather than generic compression.

---

## 2. What Exists (Prior Art Map)

### Layer 1: Knowledge Infrastructure for Coding Agents

```
                    Schema Contracts    Multi-Domain    Build Validation    JIT Delivery
Codified Context         ✗                 ✗                ✗                 ✓ (tiers)
Augment Engine           ✗                 ✗ (code only)    ✗                 ✓ (compression)
Google ADK               ✗                 ✓ (generic)      ✗                 ✓ (scoping)
CLAUDE.md/.cursorrules   ✗                 ✗                ✗                 ✗ (dump all)
RaiSE Cartridges         ✓                 ✓                ✓                 ✓
```

**Nobody has all four columns.** RaiSE's unique position is the intersection.

### Layer 2: Academic Foundations

| Concept | Maturity | Key Reference | RaiSE Application |
|---------|----------|---------------|-------------------|
| Neuro-symbolic agent architectures | Mature (2020+) | S07, S08 | Serial coupling: symbolic schema → neural reasoning → symbolic validation |
| Knowledge graph for LLM grounding | Mature (2023+) | S03, S09 | Overlay graph as union of cartridge outputs |
| Minimum viable context | Emerging consensus (2025+) | S05, S04 | JIT loading per cartridge based on task domain |
| Data contracts | Mature in data engineering (2022+) | Dehghani, Jones | Applied to agent knowledge sources (novel application) |
| Agent reliability measurement | Emerging (2025+) | S02 | Four-dimension framework adoptable for cartridge impact measurement |
| Epistemic verification | Nascent (2025+) | S13 | Validation at adapter boundary |

---

## 3. Contribution Map

### What is NOT novel (integration of existing work)

1. **Knowledge graphs for agent grounding** — well-established (S03, S07, S09)
2. **Tiered context delivery** — proven at scale (S01, S05)
3. **Minimum viable context principle** — emerging consensus (S04, S05)
4. **Neuro-symbolic architecture** — mature field (S07, S08)
5. **Data contracts pattern** — mature in data engineering (Dehghani 2022, Jones 2023)

### What IS novel (frontier contribution)

1. **Data contracts applied to AI agent knowledge sources** — Nobody has taken the data contract pattern from data engineering and applied it to the knowledge that feeds AI agents. Codified Context uses markdown docs. Augment uses semantic indexing. Neither validates knowledge against a schema before the agent consumes it.

2. **Multi-domain pluggable knowledge with unified graph** — Augment builds a code graph. Codified Context organizes docs. Neither supports heterogeneous domains (work items + governance + domain knowledge) as pluggable cartridges producing a unified queryable graph.

3. **Build-time composition validation** — Apollo Federation validates schema composition at build time for GraphQL. Nobody applies this to AI agent knowledge. `rai graph build --strict` as a quality gate is novel in this context.

4. **Overlay graph architecture for agent knowledge** — The overlay pattern exists (Rovo, Obsidian Dataview). Applying it to agent operational knowledge (querying Jira + filesystem + ontology at build time, no data copy) is a novel combination.

### Summary: Integration + Novel Application

RaiSE's contribution is **NOT a new algorithm or architecture**. It's the application of proven patterns (data contracts, federated graphs, neuro-symbolic coupling) to a problem domain where nobody has applied them (AI agent knowledge infrastructure). The novelty is in the **combination and application**, not in the individual components.

This is analogous to how Backstage didn't invent service catalogs or plugin architectures — it combined them for developer experience. RaiSE combines data contracts + knowledge graphs + JIT delivery for agent epistemic reliability.

---

## 4. Formalized Problem Statement

### The Problem (Tractable)

**AI coding agents consume knowledge from heterogeneous sources (work trackers, governance docs, domain ontologies, codebase) without quality guarantees.** Current approaches treat knowledge delivery as a documentation problem (write better markdown) or a retrieval problem (better embeddings). Neither provides:

- **Structural guarantees**: Is the knowledge complete and well-formed?
- **Compositional guarantees**: Are cross-domain references consistent?
- **Temporal guarantees**: Is the knowledge current?
- **Boundary guarantees**: Is external data validated before agent consumption?

### Decomposition into Implementable Decisions

| Sub-problem | Decision | Approach |
|-------------|----------|----------|
| SP1: How to declare knowledge structure per domain? | Schema format | `cartridge.yaml` with required_metadata per node type |
| SP2: How to validate at domain boundaries? | Adapter pattern | Pydantic validation at adapter output (ACL) |
| SP3: How to compose cross-domain knowledge? | Build step | `rai graph build` merges cartridge outputs into overlay graph |
| SP4: How to validate composition? | Build-time gates | Schema cross-references checked at build time |
| SP5: How to deliver minimum viable context? | JIT loading | Cartridge declares what to load per skill/task type |
| SP6: How to measure impact? | Reliability metrics | Adopt S02 framework: consistency, robustness, predictability |

---

## 5. What to Adopt vs. Build

### ADOPT (accelerates time-to-market)

| Component | From | How |
|-----------|------|-----|
| Three-tier context model | Codified Context (S01) | Our hot/warm/cold already aligns. Validate our tiering is complete |
| Minimum viable context principle | Google ADK (S05) | Adopt scoping pattern: each skill sees only its cartridge's context |
| Agent reliability metrics | S02 framework | Adopt 4 dimensions + 12 metrics for measuring cartridge impact |
| Serial hybrid coupling | Neuro-symbolic taxonomy (S08) | Formalize our approach: symbolic contracts → neural reasoning → symbolic validation |
| Artifacts-as-handles pattern | Google ADK (S05) | Large knowledge chunks as references, loaded on demand |

### BUILD (our frontier)

| Component | Why it doesn't exist |
|-----------|---------------------|
| Cartridge manifest (`cartridge.yaml`) | Nobody defines domain knowledge schemas for AI agents |
| Adapter validation (Pydantic at boundary) | Knowledge quality is assumed, not enforced |
| Build-time composition (`rai graph build --strict`) | No equivalent of Apollo composition for agent knowledge |
| Overlay graph from heterogeneous live sources | Existing tools either copy data or index code only |
| Domain-aware JIT loading | Existing JIT is generic compression, not domain-contract-aware |

### WATCH (may become adoptable)

| Component | Status | When |
|-----------|--------|------|
| Augment Context Engine as cartridge provider | API available Feb 2026 | When we need code-domain cartridge (vs building our own) |
| MCP as cartridge transport | Already integrated | Already in our stack |
| Agent reliability benchmarks | Emerging (S02) | When standardized benchmarks exist |

---

## 6. Competitive Moat Assessment

### Where current tools are

All major AI coding tools (Cursor, Copilot, Windsurf, Claude Code, Augment, Devin) treat knowledge as either:
- **Static files** (markdown rules, unvalidated, tool-specific)
- **Code indexing** (semantic search over codebase, no domain structure)
- **Behavioral inference** (tracking developer actions, implicit only)

None provide: schema-validated, multi-domain, pluggable knowledge with build-time composition guarantees.

### Where the market is heading

"Context engineering" is the 2025-2026 buzzword. QCon has dedicated tracks. Gartner predicts 40% agent adoption by late 2026. But the focus is on **better retrieval** (RAG++, GraphRAG), not on **knowledge contracts**.

### The moat

RaiSE's moat is NOT in any single component — it's in the **integration thesis**:

> **Epistemic infrastructure = data contracts + federated knowledge graph + neuro-symbolic JIT delivery, applied to AI agent operational knowledge.**

This is defensible because:
1. It requires domain expertise (data contracts + KG + agent architectures)
2. It requires the full stack (adapter → schema → graph → delivery → validation)
3. Competitors would need to shift from "better retrieval" to "knowledge engineering" — a paradigm change
4. First-mover advantage in defining the cartridge standard

The risk: if a major player (Augment, Anthropic, Google) decides to build this, they have more resources. Mitigation: ship fast, establish the pattern, make cartridges an ecosystem play (like Backstage plugins).

---

## 7. Contrary Evidence & Risks

### CE1: "Models are getting good enough that structure doesn't matter"
- **Source:** Fowler (S04) notes models are powerful enough that less context works
- **Assessment:** Partially valid for simple tasks. SymAgent data (S03) shows structure matters MORE for complex reasoning. For professional software development (our target), tasks are complex.
- **Risk level:** Low

### CE2: "Data contracts add overhead that slows iteration"
- **Source:** General Fowler/startup critique of premature structure
- **Assessment:** Valid concern. Mitigated by our overlay approach (no migration), and by starting with 2 cartridges (Work + Knowledge) before expanding.
- **Risk level:** Medium — we must keep cartridge creation lightweight

### CE3: "RAG is good enough — GraphRAG closes the gap"
- **Source:** S09 shows GraphRAG reduces hallucination significantly
- **Assessment:** GraphRAG improves retrieval quality but doesn't provide contracts, validation, or domain structure. It's a better search engine, not knowledge infrastructure. Complementary, not competing.
- **Risk level:** Low

### CE4: "Augment Code already solved this"
- **Source:** S06, S20 — most advanced commercial knowledge infrastructure
- **Assessment:** Augment builds a code graph. We build a multi-domain knowledge graph with contracts. Augment could become a provider IN our system (code cartridge via their API). Not competing on same layer.
- **Risk level:** Medium — they could expand to multi-domain

---

## 8. Recommendations

### R1: Proceed with ADR (HIGH confidence)

The research validates our thesis and identifies a clear gap. The ADR should formalize:
- The problem statement (Section 4)
- The five design principles (validated P1-P5 from prior research, now grounded)
- What we adopt vs. build (Section 5)
- The competitive moat (Section 6)

### R2: Frame as "Data Contracts for Agent Knowledge" (HIGH confidence)

This is the most precise articulation of our contribution. It connects to the established data contract ecosystem while being clearly novel in application domain.

### R3: Adopt the Agent Reliability Framework metrics (MEDIUM confidence)

S02 provides a formal measurement framework. Using it to demonstrate cartridge impact (before/after on consistency, robustness, predictability) would be powerful validation and marketing.

### R4: Start with 2 cartridges, not 3 (HIGH confidence)

Work (Jira) + Knowledge (ontology). Governance (Confluence/filesystem) comes later. Reduces overhead, validates pattern faster.

### R5: Watch Augment Code API closely (MEDIUM confidence)

Their code graph could be a cartridge provider, saving us from building code indexing. But dependency on a competitor's API has risks.

---

*Evidence catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)*
*Research directory: `work/research/epistemic-infrastructure/`*
*Next: ADR draft → RAISE-652*
