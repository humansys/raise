---
id: "ADR-013"
title: "Pluggable Domain Architecture: Data Contracts for Agent Knowledge"
date: "2026-03-22"
status: "Proposed"
related_to: ["ADR-011", "ADR-012", "ADR-002"]
supersedes: []
story: "RAISE-652"
research: "RAISE-653"
---

# ADR-013: Pluggable Domain Architecture

## Context

### Problem

RaiSE agents consume knowledge from heterogeneous sources — work trackers (Jira), governance documents (Confluence, filesystem), domain ontologies (knowledge graph), and codebases — without quality guarantees. Current approaches across the industry treat knowledge delivery as either:

- **A documentation problem**: write better markdown (CLAUDE.md, .cursorrules). No validation, no schema, staleness is the primary failure mode.
- **A retrieval problem**: better embeddings, bigger context windows, RAG. Optimizes for relevance, not reliability. Chunks fracture governing logic.

Neither provides structural, compositional, temporal, or boundary guarantees on the knowledge an agent consumes.

### Evidence

Formal research (RAISE-653, 22 + 52 sources triangulated) validates three claims:

1. **Agent reliability is bounded by knowledge source quality, not LLM capability.** A 7B model with structured KG outperforms GPT-4 by 37% on knowledge reasoning (SymAgent, ACM 2025). "Reliability gains lag behind capability progress" across 14 frontier models (arXiv 2602.16666). Sonnet + Augment Context Engine outperforms Opus without it — 5x functional correctness improvement.

2. **This requires dedicated infrastructure — contracts, validation, traceability.** Industry consensus: "data pipeline failures are the most prevalent cause of agent failure in production." The Neuro-Symbolic Gap (arXiv 2512.00520) shows that unvalidated symbolic inputs are executed without question — boundary validation is mandatory. No existing system combines schema contracts + multi-domain knowledge + build-time validation.

3. **Delivery must be JIT with minimum viable context.** Google ADK: "every model call sees the minimum context required." Martin Fowler: "less context often works better." Devin's team found that fragmenting context across multiple agents causes alignment drift — a single well-contextualized agent outperforms swarms. MVC (Minimum Viable Context) is emerging as the formal discipline: optimize for cost-of-not-knowing, not relevance.

### Principle at Stake

**Observability IS Trust** (RaiSE constitution): "show my work, explain my reasoning, let you verify." An agent consuming unvalidated knowledge from opaque sources violates this principle. Knowledge must be contractual, traceable, and verifiable.

## Decision

### Adopt the Pluggable Domain Architecture

A **Domain** is a pluggable module that owns a knowledge area and delivers validated, schema-conformant knowledge to the agent's context. Each domain bundles:

```text
Domain = Schema + Provider + Gates + Skills + Prompting
```

The system operates on five design principles, each grounded in research:

### P1: Schema-as-Contract at the Boundary

Each domain declares its data contract in a machine-readable manifest (`domain.yaml`). The adapter (provider) validates external data against the schema before producing graph nodes. Invalid data is rejected, not silently ingested.

**Grounding:** Data Contract Specification (Dehghani 2022, Jones 2023), PydanticAI RunContext as contract enforcer, Neuro-Symbolic Gap research mandating boundary validation.

**Implementation:** Pydantic models per domain. The adapter IS the Anti-Corruption Layer (DDD). Validation happens at ingestion, not at query time.

```yaml
# .raise/domains/work/domain.yaml
name: work
version: "1.0"
kind: domain

schema:
  node_types: [epic, story, task, bug]
  required_metadata:
    epic:
      - field: status
        type: enum
        values: [backlog, selected, in_progress, done]
      - field: labels
        type: list[str]
        min_items: 1
    story:
      - field: epic_key
        type: str
        required: true
```

### P2: Provider-Owns-Bucket Isolation

Each provider owns an isolated namespace of entities. The JiraWorkAdapter owns all `epic-RAISE-*` and `story-RAISE-*` nodes. The FilesystemGovernanceAdapter owns all `adr-*` nodes. Neither can produce nodes in the other's namespace.

**Grounding:** Backstage EntityProvider isolation, Apollo Federation subgraphs, DDD Bounded Contexts.

**Implementation:** Provider ID prefixes node IDs. Graph builder merges buckets into a union overlay graph.

### P3: Composition over Rigid Schema

The `GraphNode` model is shared across domains but extensible via typed metadata. Each domain defines which metadata fields are required for its scope. The graph is the union of all domain outputs.

**Grounding:** GitLab work item widgets, Backstage extensible kinds, Notion block properties.

**Implementation:** `GraphNode.metadata: dict[str, Any]` validated per-domain by Pydantic discriminated unions.

### P4: Build-Time Validation (Shift Left)

`rai graph build` is the composition step. Schema validation runs during build — before any query. A work item missing required labels produces a build warning. A governance artifact without required frontmatter produces a build error. CI gates on `rai graph build --strict`.

**Grounding:** Apollo Rover CLI composition validation, Haystack assembly validation, dbt contract enforcement. No existing tool applies build-time composition to agent knowledge.

**Implementation:** Each domain registers validators. Build step runs all validators and reports. `--strict` mode fails on warnings.

### P5: Overlay Graph (No Data Copy)

The graph is a **view** over existing data, not a copy. Data stays in Jira, Confluence, filesystem. `rai graph build` queries live sources at build time and produces graph nodes. No migration, no sync, no staleness from stale copies.

**Grounding:** Rovo Teamwork Graph, Obsidian Dataview, SOAR's principle that "the world is its own best model."

**Implementation:** Providers query live sources. Graph is ephemeral — rebuilt on demand. Cached for performance with change detection for incremental builds.

### The MVC Compiler (The Moat)

The competitive differentiation is not in the domains themselves — it's in the **Minimum Viable Context Compiler** that sits between the knowledge graph and the agent execution layer.

Current tools provide access to knowledge (MCP, RAG, grep). They don't curate it. The MVC Compiler:

1. **Trigger**: Agent signals intent (skill invocation, task start)
2. **Domain Assembly**: Compiler identifies relevant domains from task metadata
3. **MVC Compaction**: Per-domain contracts define what to include. Cost-of-not-knowing determines priority. Token budget is respected.
4. **JIT Injection**: Compacted payload injected into agent context via dependency injection (PydanticAI RunContext pattern)

**Grounding:** Google ADK minimum-viable-context principle, MVC formalization (Broda 2025), Augment contextual compression (4,456 → 682 sources). Devin's finding that single well-contextualized agent > multi-agent swarms.

## Consequences

### Positive

- **Validated knowledge**: Agent never consumes unvalidated data. Schema contracts catch staleness, missing fields, type errors at ingestion.
- **Multi-domain unified graph**: Work items, governance docs, and domain knowledge queryable through one graph interface.
- **Measurable reliability**: Adopt SeekBench/TrustBench epistemic competence dimensions to measure domain impact.
- **Ecosystem play**: Third-party domains (code analysis, security, performance) follow the same contract pattern — like Backstage plugins.
- **Platform agnostic**: Domains are YAML + Pydantic. No IDE dependency. Works with Claude Code, Cursor, any MCP-compatible tool.

### Negative

- **Schema maintenance overhead**: Each domain requires schema definitions. Mitigated by starting with 2 domains (Work + Knowledge) and keeping schemas minimal.
- **Build time cost**: `rai graph build` queries live sources. Mitigated by caching and incremental builds with change detection.
- **Ontology alignment remains manual**: Aligning schemas across domains is NP-hard in the general case (Euzenat & Shvaiko 2013). We accept this and provide validation tooling, not automation.
- **Adoption barrier**: Developers must define domains for their projects. Mitigated by shipping default domains and making creation lightweight.

### What We Adopt

| Component | From | Why |
|-----------|------|-----|
| Contract enforcement | PydanticAI RunContext + Pydantic models | Already in our stack, exact fit for domain DI |
| External data access | MCP servers | Already in our stack, industry standard |
| KG storage (evaluate) | LlamaIndex PropertyGraphIndex | Mature, Text2Cypher, self-correction. Evaluate as overlay graph backend |
| Data ingestion | dlt (data load tool) | Schema inference + normalization for messy API data |
| Reliability metrics | SeekBench/TrustBench dimensions | Formal epistemic competence measurement |
| Three-tier context | Codified Context pattern | Hot (constitution) / Warm (domain) / Cold (knowledge base) |
| Min-viable-context | Google ADK scoping principle | Every agent call sees minimum required context |

### What We Build

| Component | Why it doesn't exist |
|-----------|---------------------|
| `domain.yaml` manifest | Nobody defines domain knowledge schemas for AI agents |
| Adapter validation layer | Knowledge quality is assumed, not enforced |
| Build-time composition (`rai graph build --strict`) | No equivalent of Apollo composition for agent knowledge |
| Overlay graph from heterogeneous live sources | Existing tools copy data or index code only |
| MVC Compiler (domain-aware routing) | Existing JIT is generic compression, not contract-aware |

### What We Watch

| Component | Status | Trigger |
|-----------|--------|---------|
| Augment Context Engine API | Available as MCP server (Feb 2026) | When we need code analysis domain |
| Standardized agent reliability benchmarks | Emerging (arXiv 2602.16666) | When benchmarks stabilize |
| LlamaIndex PropertyGraph maturity | Active development | Before committing to graph backend |

## Implementation Path

### Phase 1: Foundation (2 domains)

1. Define `domain.yaml` schema (the manifest format)
2. Implement Work domain (Jira adapter → validated GraphNodes)
3. Implement Knowledge domain (ontology → validated GraphNodes)
4. Evolve `rai graph build` to consume domain manifests
5. Build-time validation with `--strict` mode

### Phase 2: MVC Compiler

1. Context routing based on active skill/task metadata
2. Per-domain context extraction rules
3. Token budget management
4. Integration with PydanticAI RunContext pattern

### Phase 3: Ecosystem

1. Governance domain (Confluence/filesystem)
2. Code domain (evaluate Augment API vs custom indexing)
3. Third-party domain spec and developer docs
4. Domain marketplace/registry

## Prior Art Summary

| System | Relationship |
|--------|-------------|
| Backstage Software Catalog | Inspiration for entity kinds, YAML manifests, plugin ecosystem |
| Apollo Federation | Inspiration for build-time composition validation |
| Data Contract Specification | Inspiration for schema-as-contract pattern |
| Codified Context (arXiv 2602.20478) | Closest prior art — tiered docs for coding agents, but without contracts or validation |
| Augment Context Engine | Most advanced commercial competitor — semantic KG, but code-only and closed |
| Google ADK | Minimum viable context principle and three-layer architecture |
| SymAgent (ACM 2025) | Evidence that structured KG + weak model > unstructured + strong model |

## References

- Research report: `work/research/epistemic-infrastructure/epistemic-infrastructure-report.md`
- Evidence catalog: `work/research/epistemic-infrastructure/sources/evidence-catalog.md`
- Gemini research: `work/research/epistemic-infrastructure/sources/epistemic-infrastructure-gemini.md`
- Prior domain architecture research: `work/research/domain-cartridge-architecture/domain-cartridge-architecture-report.md`
