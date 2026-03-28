# Pluggable Domains — Product Vision

> **Story:** RAISE-1000 (S650.9)
> **Epic:** RAISE-650
> **Date:** 2026-03-28
> **Authors:** Emilio + Rai
> **Status:** Draft — pending HITL review
> **Supersedes:** E650 brief (cartridge terminology), ADR-013 (cartridge architecture)

---

## 1. Thesis

RaiSE exists because AI agents cannot be trusted to manage their own reliability.
An agent guided only by prompting and conversational context will store documentation
in the wrong place, create backlog items with wrong fields, lose project state between
sessions, and hallucinate domain knowledge. The consequences compound: every unreliable
action erodes the artifacts that future sessions depend on.

**Pluggable Domains** solve this by separating what the agent *knows and can do* from
what the agent *decides*. A Domain is a self-contained unit that provides the agent with
structured knowledge, validated rules, deterministic actions, and quality gates for a
specific area of concern. The agent's job is reasoning and judgment. The Domain's job is
everything that must be exact.

**One-liner:** Domains are structured expertise that makes AI agents reliable.

**Differentiator:** Other tools give agents memory. RaiSE gives agents expertise.

---

## 2. Anatomy of a Domain

A Domain bundles five components. All five are required for the Domain to be complete;
partial Domains degrade reliability in proportion to what is missing.

```text
Domain
  Schema    — what concepts exist and how they relate (ontology)
  Gates     — what "correct" means (validation, poka-yoke)
  Skills    — what operations are available (orchestrated workflows)
  Adapters  — how to talk to external systems (deterministic I/O)
  Prompts   — how to reason about the domain (context for the LLM)
```

### Schema

Defines the node types, relationship types, required metadata, and constraints for the
domain. The schema is the contract between the Domain and the knowledge graph. It answers:
"what things exist in this domain and what properties must they have?"

Example (Work Domain): `epic`, `story`, `task`, `bug` as node types. An epic has
`status`, `labels`, `priority`. A story belongs to exactly one epic. A bug may exist
without an epic parent.

### Gates

Validation checkpoints that enforce domain rules deterministically. Gates are Jidoka —
they stop the line when a defect is detected. They are not suggestions; they are
constraints.

Example (Work Domain): "A story cannot be closed without a retrospective."
"An epic cannot be closed if any child story is still In Progress."

### Skills

Orchestrated workflows that compose multiple adapter calls with inference. Skills are the
user-facing API of the Domain. They are what the human (or the lifecycle) invokes.

Example (Work Domain): `/rai-story-start` creates an issue, transitions it, creates a
branch, and validates gates — a single command that would require five manual steps.

### Adapters

Deterministic I/O with external backends. Adapters do not think. They execute typed
operations against a specific system. An adapter implements a Protocol contract and can
be swapped without changing the Skills that use it.

**Adapters are NOT owned by Domains.** They are shared infrastructure. The Work Domain
and the Governance Domain both use the `DocumentationTarget` adapter. A Domain declares
which adapter Protocols it requires; it does not bundle concrete implementations.

Example: The Work Domain requires a `ProjectManagementAdapter`. Jira satisfies that
contract via `AcliJiraAdapter`. Linear could satisfy it via a `LinearAdapter`. The
Domain does not care which.

### Prompts

Context that shapes how the LLM reasons about the domain. Prompts are not instructions
to the user — they are instructions to the agent about what matters, what to watch for,
and how to interpret signals.

Example (Work Domain): "You are in story S829.1, phase implement. The story depends on
S829.7 (blocker). Check blocker status before proceeding."

---

## 3. The Adapter Role

### Why adapters exist

If an LLM decides *how* to create a Jira issue, it will get the transition ID wrong,
forget a required field, put the issue in the wrong project, or use the wrong issue type.
These are not hallucinations — they are mechanical details that no amount of prompting
can make reliable across sessions, projects, and schema variations.

The adapter absorbs this complexity. The LLM decides *what* and *why*. The adapter
handles *how* and *where*.

### Adapters as shared infrastructure

```text
                    ┌─────────────────┐
                    │  Work Domain    │ requires: ProjectManagementAdapter
                    │                 │          DocumentationTarget
                    └────────┬────────┘
                             │ uses
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼─────┐  ┌─────▼──────┐
     │ Jira ACLI  │  │ Confluence │  │ Filesystem │
     │ Adapter    │  │ Adapter    │  │ Adapter    │
     └────────────┘  └────────────┘  └────────────┘
              │              │              │
     ┌────────▼───┐  ┌──────▼─────┐  ┌─────▼──────┐
     │   Jira     │  │ Confluence │  │ Local disk │
     └────────────┘  └────────────┘  └────────────┘
```

Multiple Domains share adapters. The Work Domain and Governance Domain both publish to
Confluence. The adapter is registered once; Domains declare dependencies.

### Configuration model

Adapter configuration must be **generated, not hand-written**. A setup skill
(`/rai-adapter-setup`) should:

1. Discover the backend (e.g., query Jira for available projects, workflows, transition IDs)
2. Present options to the human
3. Generate the correct YAML (`.raise/jira.yaml`, `.raise/confluence.yaml`)
4. Validate the generated config against the live backend

An adapter doctor (`rai adapter doctor`) should:

1. Read the current config
2. Query the live backend
3. Report mismatches (e.g., "transition ID 31 maps to 'Code Review' in your Jira, not 'In Progress'")
4. Suggest fixes

**Principle:** If a human must know a Jira transition ID to configure RaiSE, we have
failed. The tooling must discover it.

---

## 4. Domains in the Monorepo

### Each package is a code domain

The raise-commons monorepo contains five packages:

| Package | Purpose | Domain Analogy |
| -------------- | ----------------------------------------- | --------------------------------------- |
| `raise-core` | Protocols, models, shared infrastructure | Foundation — the thin upper schema |
| `raise-cli` | CLI commands, adapter registry, graph, gates | Tooling domain |
| `raise-pro` | Commercial adapters, advanced features | Integration domain |
| `rai-agent` | Autonomous agent, knowledge pipeline | Agent domain |
| `raise-server` | SaaS API, Forge backend | Platform domain |

### Governance per package

Today all governance lives in a single `governance/` directory at the repo root. This
conflates decisions about `raise-core` with decisions about `raise-pro`. As packages
diverge in audience and release cadence, this becomes unreliable.

**Target structure:**

```text
governance/                        # System-level (cross-product)
  product/                         # Product vision docs
    pluggable-domains-vision.md    # This document
  adrs/                            # Decisions affecting multiple packages
  architecture/                    # System context, inter-package relationships

packages/
  raise-core/
    governance/                    # Core-specific
      adrs/                        # Decisions about core protocols
      architecture/                # Core module docs
  raise-cli/
    governance/
      adrs/
      architecture/
  raise-pro/
    governance/
      adrs/
      architecture/
  ...
```

**Rules:**

- A decision that affects one package lives in that package's `governance/`
- A decision that affects multiple packages lives in the root `governance/`
- The knowledge graph composes all governance sources into a unified view
- When a package is extracted to its own repo, its governance travels with it

This is the Domain model applied to ourselves: each package has its own schema
(architecture), gates (quality standards), and governance (ADRs). The root governance
is the thin upper schema that ensures coherence.

---

## 5. The Three System Domains

RaiSE requires three Domains for reliable operation. These are not optional extensions —
they are the minimum for the system to function as a complete development partner.

### Work Domain

Manages the lifecycle of work items: initiatives, epics, stories, tasks, bugs.

| Component | Current State | Target State |
| ----------- | -------------- | -------------- |
| Schema | `IssueSpec` model (partial — missing component, fixVersion, parent_key) | Complete model reflecting Jira taxonomy (RAISE-829) |
| Gates | Lifecycle gates in skills (implicit) | Explicit gate definitions in domain config |
| Skills | 12 lifecycle skills (session, epic, story) | Same skills, loading config from domain |
| Adapters | `AcliJiraAdapter`, `FilesystemPMAdapter` | Same + setup skill + doctor |
| Prompts | Session bundle (`rai session start --context`) | Domain-aware context compiler |

**Requires:** `ProjectManagementAdapter`

### Governance Domain

Manages architectural decisions, code standards, patterns, and documentation.

| Component | Current State | Target State |
| ----------- | -------------- | -------------- |
| Schema | `GovernanceSchemaProvider` + `GovernanceParser` (ADR-034) | Extended with quality metadata, staleness tracking |
| Gates | `rai gate check` (partial) | Coverage gates, consistency gates, staleness gates |
| Skills | `/rai-framework-sync`, `/rai-docs-update` | Same + publish routing by artifact type |
| Adapters | `McpConfluenceAdapter` (publish + search) | Full CRUD + artifact-type routing + label management |
| Prompts | Coaching signals, behavioral context | Domain-aware with governance health |

**Requires:** `DocumentationTarget`

### Project Domain

Manages session state, releases, milestones, deadlines, and metrics.

| Component | Current State | Target State |
| ----------- | -------------- | -------------- |
| Schema | `session-state.yaml` (ad-hoc) | Typed models for session, release, milestone |
| Gates | `rai release check` (10 gates) | Extended with deadline pressure, freeze detection |
| Skills | `/rai-session-start`, `/rai-session-close`, `/rai-publish` | Same + release planning + milestone tracking |
| Adapters | None (session state is local file I/O) | `SessionAdapter` + `ReleaseAdapter` |
| Prompts | Next-session prompt, deadline signals | Domain-aware urgency and state |

**Requires:** No external adapter initially (filesystem is sufficient). Later:
calendar integration, CI/CD adapter for DORA metrics.

---

## 6. Relationship Map

```text
┌─────────────────────────────────────────────────┐
│                  MVC Compiler                    │
│  (Minimum Viable Context — routes and compacts)  │
└──────────┬──────────┬──────────┬────────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼────────┐
    │  Work   │ │Governance│ │  Project  │
    │ Domain  │ │  Domain  │ │  Domain   │
    └────┬────┘ └────┬─────┘ └─────┬─────┘
         │           │             │
         │    ┌──────┴──────┐      │
         │    │             │      │
    ┌────▼────▼──┐  ┌───────▼──┐  │
    │    PM      │  │   Docs   │  │
    │  Adapter   │  │  Adapter │  │
    └─────┬──────┘  └────┬─────┘  │
          │              │        │
    ┌─────▼──┐   ┌───────▼──┐  ┌─▼──────────┐
    │  Jira  │   │Confluence│  │ Filesystem  │
    │        │   │          │  │             │
    └────────┘   └──────────┘  └─────────────┘
```

**Data flow:**

1. Human invokes a Skill (e.g., `/rai-story-start`)
2. Skill consults the Domain's Schema and Gates
3. Skill calls Adapter(s) for deterministic I/O
4. Adapter talks to backend, returns typed result
5. Domain's Gates validate the outcome
6. MVC Compiler incorporates new state into future context

**The MVC Compiler** is the integration point. Today `rai session start --context`
performs this role ad-hoc. The target is a formal compiler that:
- Receives a query ("I'm implementing S829.1")
- Decomposes by Domain: Work (story state), Governance (code standards, adapter protocol), Project (release pressure)
- Compacts to token budget
- Delivers deterministic context

---

## 7. MVP Scope

### For v2.4.0 (current release)

The goal is **adapter reliability**, not full Domain infrastructure. Lay the foundation
that Domains will build on in v3.0.

| Deliverable | Epic | Why Now |
|-------------|------|---------|
| Complete `IssueSpec` model (component, fixVersion, parent_key) | RAISE-829 S829.1 | Skills cannot create idiomatic Jira issues without these fields |
| Fix `default_instance` blocker | RAISE-829 S829.7 / RAISE-744 | Adapter fails on fresh installs |
| Bug/Initiative lifecycle in BacklogHook | RAISE-829 S829.3 | Work Domain needs complete lifecycle coverage |
| Confluence artifact-type routing | RAISE-830 S830.2 | Governance Domain needs deterministic publish locations |
| Confluence label support | RAISE-830 S830.1 | Cross-cutting queries depend on labels |
| Adapter setup skill (`/rai-adapter-setup`) | New story | Config must be generated, not hand-written |
| Adapter doctor (`rai adapter doctor`) | New story | Config must be validated against live backend |

### For v3.0 (Pluggable Domains)

| Deliverable | Epic | Why |
|-------------|------|-----|
| Domain manifest format (`domain.yaml` v2) | RAISE-650 | Formal declaration of Schema + Gates + Skills + Prompts |
| Domain discovery and loading | RAISE-650 | `rai domain add`, `rai domain list` |
| MVC Compiler | RAISE-650 | Context routing by Domain |
| Governance per package | New epic | Monorepo-as-domains structure |
| `rai domain doctor` | New epic | Domain-level health validation |
| Third-party domain support | RAISE-650 | `rai domain add scaleup` from registry |

### Not in scope

- Marketplace distribution (requires raise-server infrastructure)
- Domain versioning and compatibility checks (requires registry)
- Multi-tenant domain governance (requires raise-pro)

---

## 8. Epics Generated

This vision document generates or updates the following epics:

| Epic | Status | Relationship to This Vision |
|------|--------|----------------------------|
| **RAISE-650** (Domain Cartridges → Pluggable Domains) | Update scope | Rename, expand to include Domain manifest, discovery, MVC Compiler |
| **RAISE-829** (Stabilize Backlog Adapter v2) | Existing | Adapter reliability foundation for Work Domain |
| **RAISE-830** (Stabilize Documentation Adapter v2) | Existing | Adapter reliability foundation for Governance Domain |
| **NEW: Adapter Setup & Doctor** | To create | Config generation, validation, doctor checks |
| **NEW: Governance Per Package** | To create | Monorepo restructure, per-package governance |
| **NEW: Project Domain Foundation** | To create | Session adapter, release adapter, milestone tracking |

---

## Appendix: Terminology Decision

**Decision (2026-03-28):** The term "Cartridge" is replaced by "Domain" throughout RaiSE.

**Rationale:**
- "Domain" is already the term in the codebase (`DomainManifest`, `DomainAdapter`, `domain.yaml`)
- Aligns with Domain-Driven Design vocabulary familiar to the target audience
- "Cartridge" carries dated connotations (game consoles, printer cartridges)
- In the context of "RaiSE Domains" the term implies installable, structured expertise

**Affected artifacts:**
- ADR-013 (Domain Cartridge Architecture → Pluggable Domain Architecture)
- RAISE-650 epic scope and title
- E650 brief (`work/epics/e650-domain-cartridges/brief.md`)
- Research docs referencing "cartridge" terminology
- Business brief and market analysis documents

**What does NOT change:**
- The concept: Schema + Gates + Skills + Adapters + Prompts bundled as a distributable unit
- The architecture: ADR-013 decisions remain valid, only naming changes
- The implementation: `domain.yaml`, `DomainManifest`, `DomainAdapter` already use correct naming
