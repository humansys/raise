# E650: Pluggable Domains — Brief (Updated 2026-03-28)

> Terminology updated 2026-03-28: "Cartridge" → "Domain" per RAISE-1000.
> See `governance/product/pluggable-domains-vision.md` for full product vision.

## Vision (v3.0)

Pluggable Domains are the foundational capability for RaiSE 3.0. A domain is a
self-contained, distributable knowledge module that any agent can load to gain
structured expertise in a specific area.

### The expanded vision: RaiSE as domain consumer AND domain

RaiSE itself becomes a collection of pluggable domains:

| Domain | Area | Provides |
| --- | --- | --- |
| `raise-pm` | Project Management | Stories, epics, sprints, velocity, backlog |
| `raise-docs` | Document Management | Confluence, docs publishing, search |
| `raise-governance` | Governance | ADRs, guardrails, code standards |
| `raise-knowledge` | Knowledge Infrastructure | Domain runtime, retrieval engine, gates |
| `scaling-up` | ScaleUp Methodology | 447 nodes, 4 pillars, tools, worksheets |
| `gtd` | Getting Things Done | Contexts, projects, weekly review |
| `okr` | OKR Framework | Objectives, key results, scoring |

rai-agent works with ALL domains. raise (the dev framework) uses extended domain
memory via pluggable domains. Third parties create and distribute their own.

### Strategic positioning: "npm for domain knowledge"

- Complementary to memory layers (Mem0, Letta), not competitive
- Value is in ontology quality + domain coverage, not infrastructure
- Open core: runtime is OSS, premium domains + marketplace + enterprise features are paid

## Research Foundation (SES-046, 2026-03-24)

### Literature Review — 90+ sources, 10 parallel research agents

Full evidence at `research/literature-review-synthesis.md` and `dev/research/R{1-5}-*.md`, `dev/research/M{1-5}-*.md`.

#### Key findings

1. **The concept is novel** — no system combines all domain features (typed schema + corpus + adapter + gates + HITL + symbolic retrieval + pluggable composition)
2. **Each piece is proven** — spreading activation (SYNAPSE SOTA), modular ontologies (OBO Foundry 100+), HITL (OntoChat, WebProtégé), Pydantic schemas (Graphiti/Cognee)
3. **$60M+ validates the category** — Mem0 $24M, Interloom $16.5M, Letta $10M, Cognee $8.2M
4. **Whitespace confirmed** — no competitor offers distributable domain knowledge modules
5. **TAM: $1.73B (2025) → $4.93B (2030)** for Semantic Layer + KG for Agentic AI

#### Six validated design principles

- **P1: Orthogonality** — each domain owns its concepts exclusively
- **P2: Thin upper schema** — 5-10 shared meta-types as bridge (Entity, Process, Goal, Metric, Role)
- **P3: Federated query decomposition** — route sub-queries to relevant domains
- **P4: Fail-fast composition** — conflicting types are errors
- **P5: Separate review metadata** from domain data (ChAO pattern)
- **P6: PDCA improvement model** — Plan(CQs) → Do(extraction) → Check(gates) → Act(curation)

#### Novel contributions we can claim

1. Pluggable Domain as formal concept (no precedent in this combination)
2. Domain adapter pattern for typed traversal (no existing system does this)
3. Query failures as gap signals (no mature methodology)
4. Pydantic-as-SHACL (emerging, not established)
5. HITL curation integrated with symbolic retrieval (unique)

### Market landscape

- **Closest competitors:** Cognee (Pydantic+OWL), Zep/Graphiti (Pydantic schemas), TrustGraph (Context Cores)
- **None have:** distributable packaging + HITL curation + composition
- **Moat:** ontology quality + domain coverage (infra is commoditizing)
- **First vertical recommendation:** HR/Skills (Lightcast proved at $105M)
- **LATAM advantage:** consultores/coaches as domain creators, lower creation cost, unserved market

### Competitive risk

Cognee or Zep could add domain-like packaging. ~6-12 month window. Speed matters.

## Relationship to E673 (Monorepo Consolidation)

E673's S11.9 (RAISE-704, Knowledge Refactor) was the trigger for this research. The
mechanical refactor (move protocols → raise-core, impl → raise-cli) is a prerequisite
for the domain architecture but is NOT the domain architecture itself.

**RAISE-704 should be redefined** as a story within E650, not E673. E673 can close
without it — the knowledge refactor serves the domain vision, not monorepo consolidation.

## Relationship to Versioning

This is **v3.0 work** — breaking changes to package boundaries and the knowledge architecture.

Parallel development model needed:
- `main` → releases (v2.3.x hotfixes)
- `dev` → v2.4 features (5 epics planned)
- `next` → v3.0 (Pluggable Domains)

Branching model decision required before starting implementation.

## What Already Exists (from E3)

| Component | Status | Location |
| --- | --- | --- |
| DomainAdapter Protocol | Complete | `packages/rai-agent/src/rai_agent/knowledge/retrieval/models.py` |
| DomainManifest + SchemaRef | Complete | `packages/rai-agent/src/rai_agent/knowledge/models.py` |
| Retrieval Engine (SA) | Complete | `packages/rai-agent/src/rai_agent/knowledge/retrieval/engine.py` |
| Gates (validate, reconcile, coverage) | Complete | `packages/rai-agent/src/rai_agent/knowledge/gates.py` |
| Discovery (convention-based) | Complete | `packages/rai-agent/src/rai_agent/knowledge/domain.py` |
| CLI (`rai knowledge query`) | Complete | `packages/rai-agent/src/rai_agent/knowledge/cli.py` |
| ScaleUp domain (first impl) | Complete | 447 nodes, adapter, builder, curation skill |
| HITL curation skill | Complete | `/rai-scaleup-curate` |
| 5 research axes (128 sources) | Complete | `work/research/` (R0-R4 from E3) |

## Stakeholders

- **Emilio** — framework architecture, technical decisions
- **Eduardo** — ScaleUp domain expertise, marketing, first domain creator
- **Gerardo** — sales/BD, market validation, early adopter identification

## Business Brief

See `research/knowledge-cartridges-business-brief.md` for non-technical overview
prepared for Gerardo and Eduardo.

## Next Steps

1. Planning session: define branching model (main + dev + next)
2. `/rai-epic-design` for E650 with stories decomposed from this brief
3. Move RAISE-704 from E673 to E650
4. ADR (RAISE-652) informed by the literature review
