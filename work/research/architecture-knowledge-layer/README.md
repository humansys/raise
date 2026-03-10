# Research: Architecture Knowledge Layer

> **ID:** RES-ARCH-KNOWLEDGE-001
> **Date:** 2026-02-07
> **Decision informs:** Story discover-document — format spec, graph integration, naming
> **Depth:** Standard | **Sources:** 36 entries, 50+ URLs | **Confidence:** High

---

## Research Question

**Primary:** What format and structure should architectural documentation have to serve both humans (readability, onboarding) and AI (semantic density, deterministic retrieval, graph integration)?

**Secondary:**
1. What prior art exists for dual-purpose code documentation?
2. What information do developers actually need from architecture docs?
3. What structure enables deterministic AI retrieval without losing human readability?
4. How should this integrate with the existing memory graph as Tier 2 knowledge?
5. What granularity — monolithic file vs per-module?

---

## Key Findings

### Finding 1: The Two-Layer Model is the Converged Pattern

**Confidence: HIGH** (7 independent sources)

Every mature approach separates **structure** (extractable from code) from **intent** (requires human authorship):

| Layer | Auto-generable? | Half-life | Consumer | Sources |
|-------|----------------|-----------|----------|---------|
| **Structural** (symbols, deps, APIs) | Yes | Days-weeks | AI primarily | Aider, Cursor, Continue, `rai discover` |
| **Intentional** (rationale, goals, non-goals) | No | Months-indefinite | Human + AI | ADRs, Google Design Docs, RFCs, C4 |

> "Models infer structure, not intent." — InfoQ 2025

**Triangulation:**
1. Aider repo-map = auto-generated structure, no intent
2. ADRs = human-authored intent, no structure
3. C4 + Structurizr = both layers in one model
4. Dual-channel documentation pattern (InfoQ 2025) = explicit separation
5. DORA 2024: "developers need to understand the why behind code"
6. vFunction 2025: 93% negative outcomes when docs don't match reality (structure layer must be auto-generated)
7. Anthropic context engineering: "informative yet tight" (structure must be compressed)

**Implication:** The architecture doc should combine auto-generated structure with human-authored intent. Structure refreshes automatically; intent is maintained manually at milestone boundaries.

---

### Finding 2: Markdown + YAML Frontmatter is the Universal Dual-Purpose Format

**Confidence: HIGH** (6 independent tools converged)

| Tool | Format | Dual-purpose mechanism |
|------|--------|----------------------|
| Claude Code | CLAUDE.md (Markdown) | Freeform, system prompt |
| Cursor | .mdc (Markdown + metadata) | Frontmatter + body |
| Continue | .md (Markdown) | Rules files |
| Copilot | .md (Markdown + YAML) | `applyTo` frontmatter |
| llms.txt | Markdown | Index + full content |
| DITA | XML typed topics | → Achievable via YAML `type:` field |

**Triangulation:**
1. Every AI coding tool reads Markdown natively
2. YAML frontmatter adds machine-parseable metadata without sacrificing readability
3. JSON-LD / XML / custom DSLs rejected by all modern tools
4. llms.txt standard (844K+ websites) validates Markdown for LLM consumption
5. Hugo/Jekyll/MDX all use frontmatter — battle-tested pattern
6. DITA's topic typing is valuable but achievable with `type:` in YAML

**Implication:** Use Markdown with YAML frontmatter. Don't invent a custom format. Frontmatter carries typed metadata; body carries human narrative.

---

### Finding 3: Three Abstraction Levels Cover All Needs

**Confidence: HIGH** (C4 model + internal analysis + developer needs research)

| Level | C4 Analog | Content | Consumer |
|-------|-----------|---------|----------|
| **System** | Context | What is this? Who uses it? External dependencies. | Human onboarding |
| **Module** | Component | Packages, purposes, dependencies, constraints | Human + AI |
| **Symbol** | Code | Key classes/functions, signatures, roles | AI primarily |

**Triangulation:**
1. C4 model: 4 explicit levels (we skip Container — single deployable)
2. Internal analysis: 300 components in graph, zero module-level dependency edges
3. GitHub engineers: "start with entry points, follow data flow" (module level)
4. Microsoft onboarding: "Simple-Complex" progressive disclosure strategy
5. Aider: repo → file → symbol hierarchy

**Implication:** The missing layer is **Module** — between system vision and individual components. This is what Rai re-discovers every session.

---

### Finding 4: Freshness Determines Trust — Automate What Changes Fast

**Confidence: VERY HIGH** (4 independent studies)

| Content | Half-life | Strategy | Evidence |
|---------|-----------|----------|----------|
| Design rationale / ADRs | Indefinite (immutable) | Append-only | Nygard, ECSA 2024 |
| System mental model | 6-12 months | Manual at milestones | arc42, C4 |
| Module purposes | 3-6 months | Semi-automated (generate + validate) | vFunction 2025, Episteca |
| Dependency graphs | 1-3 months | Fully automated from code | Aider, CodeScene |
| API signatures | Days-weeks | Fully automated (tree-sitter/AST) | Aider, Sphinx |

**Triangulation:**
1. vFunction 2025: 56% of orgs acknowledge docs don't reflect production
2. Episteca: 30-90 day half-life for technical docs
3. DORA 2024: High-quality docs → 2x reliability targets
4. Stack Overflow 2024: Hunting for missing docs disrupts flow state

**Key principle:** Automate what changes fast, curate what changes slow, make immutable what should never change.

---

### Finding 5: Token Budget Awareness is Non-Negotiable for AI Consumption

**Confidence: HIGH** (3 independent sources)

| Tool | Token Strategy |
|------|---------------|
| Aider | 1K default budget, PageRank selection |
| Cursor | 10-50K context chunks |
| llms.txt | Summary index + full content (two-tier) |

**Triangulation:**
1. Aider: 1K token budget selects only highest-ranked symbols
2. Anthropic: "informative yet tight" — irrelevant context degrades performance
3. Factory.ai: Enterprise repos span millions of tokens; need structured overviews

**Implication:** Produce two views: **compact** (~1-2K tokens, always loadable) and **full** (on-demand, retrievable by module/concern). The compact view is the equivalent of llms.txt for architecture.

---

### Finding 6: The Internal Gap — Zero Dependency Edges

**Confidence: VERY HIGH** (direct data analysis)

The memory graph has 5,739 nodes and 4,739 edges, but:
- 300 components with **zero `depends_on` edges** between them
- No module-level relationship data
- No architectural constraints captured
- No data flow paths represented

**What Rai re-discovers per session:**

| Knowledge | Re-discovery cost | Should be |
|-----------|------------------|-----------|
| Module dependencies | ~5-10 min | Pre-computed graph edges |
| CLI → module mapping | ~1 min | Registry |
| Data flow through system | ~10 min | Queryable flow paths |
| Parser plugin protocol | ~1 min | Schema |
| Skill workflow DAG | ~1 min | Pre-built from frontmatter |

**Implication:** The architecture knowledge layer fills the gap between "what exists" (components) and "how things relate" (dependencies, flows, constraints).

---

## Triangulated Claims

### Claim 1: Dual-purpose docs need two representations, not one

**Sources:** Aider (AI-only map), ADRs (human-only rationale), C4 (both via DSL), InfoQ dual-channel, llms.txt (index + full)
**Confidence:** HIGH
**Contrary evidence:** CLAUDE.md works with single freeform format — but lacks structure for deterministic retrieval.

### Claim 2: YAML frontmatter is the right metadata mechanism

**Sources:** Hugo, Copilot, Cursor (MDC), llms.txt, DITA (typed topics → YAML type:)
**Confidence:** HIGH
**Contrary evidence:** JSON-LD offers richer semantics — but overkill for this use case. CLAUDE.md has no frontmatter and works — but can't be queried programmatically.

### Claim 3: Module-level is the missing abstraction

**Sources:** C4 Component level, internal gap analysis (zero depends_on), GitHub engineer onboarding, Microsoft "Simple-Complex"
**Confidence:** VERY HIGH
**Contrary evidence:** None found. All sources agree this level is critical and commonly missing.

### Claim 4: Generated docs without narrative are useless

**Sources:** Stack Overflow 2024 meta-study, vFunction 2025, DX cognitive load research, arXiv 2025 architecture explanations
**Confidence:** HIGH
**Contrary evidence:** Aider's repo-map is pure structure, no narrative — but it's not documentation, it's context injection. Different use case.

### Claim 5: Graph integration enables deterministic retrieval

**Sources:** Internal analysis (memory graph has query infrastructure), Aider (PageRank on graph), C4 + Structurizr (model-based)
**Confidence:** MEDIUM-HIGH
**Contrary evidence:** CLAUDE.md and .cursorrules prove that freeform markdown with grep is "good enough" for many use cases. Graph adds value when you need cross-module queries.

---

## Recommendation

**Decision:** Create an **Architecture Knowledge Layer** as Tier 2 in RaiSE's information hierarchy.

**Confidence:** HIGH

### What It Is

A structured, dual-purpose documentation system that:
1. **Combines auto-generated structure with human-authored intent**
2. **Uses Markdown + YAML frontmatter** — universal, tooling-free, graph-ingestible
3. **Organizes by module** — filling the gap between system vision and individual components
4. **Produces two views** — compact (session context) and full (on-demand detail)
5. **Integrates into the memory graph** as new node types with dependency edges

### Proposed Structure

```
.raise/architecture/          # Tier 2 knowledge layer
├── index.md                  # Compact system overview (~1-2K tokens)
├── modules/                  # Per-module docs (the core)
│   ├── cli.md
│   ├── config.md
│   ├── context.md
│   ├── core.md
│   ├── discovery.md
│   ├── governance.md
│   ├── memory.md
│   ├── onboarding.md
│   ├── output.md
│   ├── schemas.md
│   └── telemetry.md
└── flows/                    # Cross-module data flows (optional, v2)
    ├── governance-extraction.md
    ├── discovery-pipeline.md
    └── session-lifecycle.md
```

### Per-Module Document Format

```markdown
---
type: module
name: discovery
purpose: "Codebase analysis and component extraction"
status: current
depends_on: [core, schemas]
depended_by: [cli, context]
entry_points: ["raise discover start", "raise discover scan", "raise discover analyze"]
public_api: [Scanner, Analyzer, DriftDetector]
constraints:
  - "Independent of governance module"
  - "No direct CLI output — uses output formatters"
last_validated: 2026-02-07
---

## Purpose

One paragraph: what this module does and WHY it exists.

## Architecture

How it's organized internally. Key classes and their responsibilities.
Mermaid diagram if relationships are non-trivial.

## Dependencies

What it imports and why. What imports it and why.
Constraints on what it MUST NOT depend on.

## Non-Goals

What this module explicitly does NOT do.
What concerns it does NOT own.

## Conventions

Patterns specific to this module.
How to add new functionality.
```

### Graph Integration

New node types for Tier 2:

| Node Type | Source | Edges |
|-----------|--------|-------|
| `module` | YAML frontmatter | `depends_on`, `depended_by` |
| `flow` | Flow docs (optional) | `involves` modules |
| `constraint` | Module `constraints:` field | `applies_to` modules |

This adds **module-level dependency edges** — the critical gap identified in internal analysis.

### Naming Decision

**Recommendation: `rai discover describe`** (verb: describe)

| Candidate | Pros | Cons |
|-----------|------|------|
| `discover document` | Clear intent | "document" as verb is awkward |
| `discover describe` | Natural verb, fits pipeline | New verb in discover family |
| `discover report` | Clear output type | Implies one-time report, not living docs |
| `discover map` | Spatial metaphor | Conflicts with Aider "repo-map" meaning |
| `describe` (top-level) | Clean, distinct | Breaks discover pipeline grouping |

The discover pipeline becomes: `start` → `scan` → `analyze` → `validate` → `describe` → `complete`

### Freshness Strategy

| Content | Strategy | Trigger |
|---------|----------|---------|
| YAML frontmatter (deps, API, entry points) | Auto-generated from code | `rai discover describe` |
| Purpose, Architecture, Non-Goals | Human-authored, validated | Milestone / story-close |
| Mermaid diagrams | Auto-generated | `rai discover describe` |
| Constraints | Human-authored | ADR creation |

### Trade-offs

**Accepting:**
- Per-module files add file count (11+ files) — but each is small and focused
- YAML frontmatter is less expressive than JSON-LD — but universally understood
- Human-authored sections can drift — but freshness strategy mitigates

**Rejecting:**
- Single monolithic architecture doc (doesn't scale, can't query by module)
- Pure auto-generation (can't capture intent, non-goals, constraints)
- Custom DSL or XML format (unnecessary complexity, no tool support)
- Embedding-only approach like Cursor (no human readability, black box)

### Risks

| Risk | Mitigation |
|------|------------|
| Frontmatter schema changes break graph | Version frontmatter schema, backward compat in reader |
| Human sections go stale | Validate at story-close; drift detection in `rai discover` |
| Over-engineering for F&F | Start with index.md + 3 key modules, grow incrementally |
| Token budget exceeded | Compact index.md stays under 2K; modules loaded on demand |

---

## Governance Linkage

- **Story:** discover-document (scope updated by this research)
- **ADR needed:** ADR-025 — Architecture Knowledge Layer format and integration
- **Parking lot:** Update `/discover-document` entry with new naming and structure
- **Graph:** New node types (`module`, `flow`, `constraint`) in unified graph

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 36 sources consulted (standard depth)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources each)
- [x] Confidence level explicitly stated
- [x] Contrary evidence acknowledged
- [x] Recommendation is actionable
- [x] Governance linkage established

---

## Sources

Full evidence catalog: `sources/evidence-catalog.md`

### Key Sources (Top 10)

1. [Aider Repository Map](https://aider.chat/docs/repomap.html) — Very High
2. [C4 Model](https://c4model.com/) — Very High
3. [DORA 2024 State of DevOps](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report) — Very High
4. [Claude Code CLAUDE.md](https://www.builder.io/blog/claude-md-guide) — Very High
5. [vFunction 2025 Architecture Report](https://vfunction.com/resources/report-2025-architecture-in-software-development/) — High
6. [Effective Context Engineering (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — High
7. [llms.txt Standard](https://gitbook.com/docs/publishing-documentation/llm-ready-docs) — High
8. [DevEx: What Drives Productivity (ACM Queue)](https://queue.acm.org/detail.cfm?id=3595878) — Very High
9. [Documentation Decay (Episteca)](https://episteca.ai/blog/documentation-decay/) — High
10. [Dual-Channel Documentation (InfoQ)](https://www.infoq.com/articles/architects-ai-era/) — High
