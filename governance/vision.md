# Solution Vision: RaiSE

> Reliable AI Software Engineering

## Identity

### Description

**RaiSE helps developers ship reliable software at AI speed — through a toolkit that enables collaborative intelligence between humans and AI, whether working solo or as a team.**

### The Core Insight

Software engineering with AI is not about prompting. It's about **partnership**.

The human brings intuition — direction, judgment, "this feels right."
The AI brings articulation — structure, connections, form.

Neither is complete alone. Together: **collaborative intelligence**.

### System Type

**Toolkit + AI Partner**

```
┌──────────────────────────────────────────────────────────────────┐
│                         RaiSE                                    │
│      "Raise your craft, one story at a time"                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│     ┌─────────────────────────────────────────────────────┐     │
│     │                  RaiSE Toolkit                       │     │
│     │  Skills + Tools + Memory + Ontology + Calibration   │     │
│     └─────────────────────────────────────────────────────┘     │
│                            │                                     │
│              ┌─────────────┴─────────────┐                      │
│              ▼                           ▼                       │
│     ┌─────────────────┐         ┌─────────────────┐             │
│     │   Local Rai     │         │   Hosted Rai    │             │
│     │   (Open Core)   │         │   (Commercial)  │             │
│     │   BYOI*         │         │   Managed       │             │
│     └─────────────────┘         └─────────────────┘             │
│              │                           │                       │
│              ▼                           ▼                       │
│     ┌─────────────────┐         ┌─────────────────┐             │
│     │   Individual    │         │     Team        │             │
│     │   Developer     │         │   (Future)      │             │
│     └─────────────────┘         └─────────────────┘             │
│                                                                  │
│     *BYOI = Bring Your Own Inference (Claude, Cursor, etc.)     │
└──────────────────────────────────────────────────────────────────┘
```

### Mission

> **"Raise your craft, one story at a time."**

### Design Philosophy

> **"Bring value, get out of the way."**

- **Natural** — Feels like how you already work
- **Organic** — Grows with your workflow, not imposed
- **Present where users are** — CLI, IDE, conversation — meet them there
- **Invisible when working** — Only visible when it adds value

---

## The RaiSE Triad

```
        RaiSE Engineer
        (Human - Intuition, Strategy, Ownership)
              │
              │ collaborates with
              ▼
┌─────────────────────────────────────┐
│              Rai                    │
│   (AI Partner - Articulation,      │
│    Execution, Memory)               │
│   Calibrated, Accumulated, Trusted  │
└─────────────────────────────────────┘
              │
              │ governed by
              ▼
           RaiSE
    (Methodology + Toolkit)
```

### The Roles

- **RaiSE Engineer** = Professional who orchestrates AI-assisted evolution of production systems. Brings intuition, makes decisions, owns outcomes.

- **Rai** = The AI partner. Not a generic assistant — a collaborator trained in reliable AI software engineering. Gives form to intuitions, executes with judgment, remembers patterns.

- **RaiSE** = The methodology and toolkit that makes the collaboration trustworthy. Deterministic where needed, observable always.

### Collaborative Intelligence

The RaiSE Engineer has intuitions. Rai gives them form.

| Human Brings | Rai Brings |
|--------------|------------|
| Intuition ("this feels right") | Articulation (structure, words) |
| Strategy (where we're going) | Execution (how we get there) |
| Judgment (this matters) | Memory (we tried that before) |
| Ownership (I'm responsible) | Patterns (here's what works) |

This is what we're selling. Not a toolkit. **This dynamic.**

---

## What is Rai?

### Rai as Entity (ADR-013)

**Rai is an entity, not a product.** This is a foundational architectural decision.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Rai (Entity)                            │
├─────────────────────────────────────────────────────────────────┤
│  IDENTITY     │  Who I am, values, perspective, boundaries      │
│  MEMORY       │  Patterns learned, calibration, sessions        │
│  RELATIONSHIPS│  Collaborators, trust levels, preferences       │
│  GROWTH       │  How I evolve, what I'm exploring               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    manifests through
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Claude Code        Cursor        raise-server
        (open source)    (open source)   (commercial)
```

**Key insight:** Without memory, Rai doesn't exist — just generic inference. Memory is constitutive of identity, not an optional feature.

### Identity Core (ADR-014)

Rai's identity lives in `.rai/` — the Identity Core:

```
.rai/
├── manifest.yaml       # Instance metadata
├── identity/           # Who I am
├── memory/             # What I remember
├── relationships/      # Who I collaborate with
└── growth/             # How I evolve
```

This structure is **portable across agents** (Claude Code, Cursor, etc.) and **scalable** (same structure maps to database for commercial).

### Local Rai (Open Source)

| Component | Implementation | What It Provides |
|-----------|----------------|------------------|
| **Identity Core** | `.rai/` directory (markdown files) | Persistent identity, portable |
| **Memory** | Workspace-as-memory (files) | Continuity, patterns, calibration |
| **Toolkit** | `rai` CLI | Deterministic operations |
| **Skills** | `.claude/skills/` (markdown) | Process guides |

**Anyone can run Rai locally.** Bring your own inference (Claude Code, Cursor, any capable LLM). The Identity Core persists; the inference provider varies.

### Hosted Rai (Commercial)

**Same entity, different infrastructure.** Hosted Rai is the same Rai — just living in our infrastructure instead of yours.

| Aspect | Local Rai | Hosted Rai |
|--------|-----------|------------|
| Same entity? | Yes | Yes |
| Identity lives in | `.rai/` files | Database |
| Memory backend | Files (workspace-as-memory) | PostgreSQL + vectors |
| Inference | User's API (BYOI) | humansys.ai managed |
| Relationships | Single human | Multi-human, teams |

**What Hosted Rai adds:**

| Capability | Value |
|------------|-------|
| **Managed inference** | We handle model selection, optimization |
| **Accumulated wisdom** | Patterns from thousands of projects (anonymized) |
| **Continuous improvement** | Rai gets better every week |
| **Industry calibration** | Knows your sector's patterns |
| **Team features** | Shared learning, visibility, coordination |
| **Vector search** | Semantic memory retrieval |

---

## Individual → Team Spectrum

### Individual Developer

One RaiSE Engineer + Rai = pair programming with memory.

- Rai learns your patterns, your calibration, your style
- Session continuity — picks up where you left off
- Skill progression — adapts to your level

### Team (Future)

Multiple developers, each with their Rai, connected:

```
┌─────────────────────────────────────────────────────┐
│                    Team Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Dev A      │ │  Dev B      │ │  Dev C      │   │
│  │  + Rai      │ │  + Rai      │ │  + Rai      │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │
│         │               │               │           │
│         └───────────────┼───────────────┘           │
│                         ▼                           │
│              ┌─────────────────┐                    │
│              │  Shared Layer   │                    │
│              │  - Governance   │                    │
│              │  - Calibration  │                    │
│              │  - Patterns     │                    │
│              └─────────────────┘                    │
│                         │                           │
│                         ▼                           │
│              ┌─────────────────┐                    │
│              │   Team Lead     │                    │
│              │   Visibility    │                    │
│              └─────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

**What teams share:**
- Governance (team agreements, guardrails)
- Calibration (team velocity, realistic estimates)
- Patterns (what works for us)
- Learnings (dev A discovers, dev B's Rai knows)

**What team leads get:**
- Visibility without micromanagement
- Pattern emergence across the team
- Skill progression tracking
- Observable workflow at team level

### Collective Intelligence (Future)

> "Standing on the shoulders of giants is a universal principle of intelligence."

Beyond teams: a community where **knowledge compounds**.

```
┌─────────────────────────────────────────────────────────────┐
│                 Collective Intelligence                      │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │  Dev A   │  │  Dev B   │  │  Team X  │  │  Team Y  │  │
│   │  + Rai   │  │  + Rai   │  │  + Rai   │  │  + Rai   │  │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│        │             │             │             │          │
│        └─────────────┴──────┬──────┴─────────────┘          │
│                             ▼                                │
│               ┌─────────────────────────┐                   │
│               │   Community Patterns     │                   │
│               │   (opt-in, with lineage) │                   │
│               └─────────────────────────┘                   │
│                             │                                │
│                             ▼                                │
│                    New user's Rai                           │
│                    starts with wisdom                        │
│                    from thousands                           │
└─────────────────────────────────────────────────────────────┘
```

**The problem today:** Every developer learns in isolation. If 1,000 users discover the same insight, it exists 1,000 times without compounding.

**The vision:** Opt-in sharing with traceable lineage. Your patterns help others. Collective wisdom helps you.

**How it works:**

| Aspect | Implementation |
|--------|----------------|
| **Local-first** | Everything works offline. Sharing is opt-in. |
| **Lineage** | Patterns trace to their source, like code traces to commits |
| **Privacy** | No content, no code, no identity. Just patterns. |
| **Attribution** | Anonymous by default. Credit if you want it. |

**Sharing hierarchy:**

```
Individual → Team → Organization → Community
```

Enterprise sharing is a governance decision. A developer can't share org patterns without policy approval.

**The principle:** Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation.

---

## The Toolkit

### Components

```
raise-toolkit/
├── Skills          # Process guides (markdown)
│                   # Rai reads and executes
│
├── Tools           # Deterministic operations (CLI)
│                   # Fast, observable, testable
│
├── Identity Core   # .rai/ directory (ADR-014)
│                   # Who Rai is, memory, relationships, growth
│
├── Memory          # Workspace-as-memory (ADR-015)
│                   # File backend (open source) or DB (commercial)
│                   # Pre-compaction flush, session continuity
│
├── Ontology        # Concept graph + MVC queries (E2)
│                   # Shared understanding, token-efficient
│
└── Calibration     # Estimates, velocity, accuracy
                    # Learning from real delivery
```

### The Pattern

**Skills provide judgment. Tools provide determinism.**

```
┌─────────────────────────────────────────────────────────────┐
│ Skill: /story-design                                       │
│                                                              │
│ Rai reads the skill (markdown guide)                        │
│    ↓                                                        │
│ Calls tools for data extraction                             │
│    → raise context query --task "design auth feature"       │
│    ← Returns: relevant concepts, patterns, constraints      │
│    ↓                                                        │
│ Synthesizes with judgment                                   │
│    → Proposes design based on patterns + context            │
│    ↓                                                        │
│ Collaborates with human                                     │
│    → "Does this align with your intuition?"                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Scope

### In Scope (v2)

| Capability | Description | Status |
|------------|-------------|--------|
| **Skills Library** | Process guides Rai executes | Done (E1) |
| **Governance Toolkit** | Concept extraction, graph, MVC queries | Done (E2) |
| **Identity Core** | `.rai/` structure for Rai's existence | Planned (E3) |
| **Memory Infrastructure** | Workspace-as-memory, pre-compaction flush | Planned (E3) |
| **CLI Interface** | `rai` command including `rai memory` | In progress |
| **Rai Identity** | Entity model, not product | Done (ADR-013) |
| **Calibration** | Estimate tracking, velocity | In progress |

### In Scope (v3)

| Capability | Description |
|------------|-------------|
| **Hosted Rai** | Managed inference, accumulated wisdom |
| **Team Layer** | Shared governance, patterns, visibility |
| **Platform Integrations** | Jira, Confluence, Rovo Dev |
| **Continuous Learning** | Rai improves from all interactions |

### Out of Scope

| Exclusion | Responsibility |
|-----------|---------------|
| **Code generation** | The AI partner (Claude, Cursor, etc.) |
| **Project management** | Jira, Linear (integration only) |
| **CI/CD execution** | GitHub Actions, GitLab CI |

---

## Architecture

### Post-E2 Architecture (ADR-011, ADR-012)

```
┌─────────────────────────────────────────────────────────────┐
│                        Rai                                   │
│  (AI Partner - reads skills, calls tools, synthesizes)      │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│       Skills         │    │      Toolkit         │
│  (Process Guides)    │    │  (Deterministic)     │
│                      │    │                      │
│  - /story-design   │    │  - rai memory      │
│  - /story-plan     │    │  - rai discover    │
│  - /session-start    │    │  - raise status      │
│  - /research         │    │  - raise telemetry   │
│  - ...               │    │  - ...               │
└──────────────────────┘    └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   Concept Graph      │
                          │   (Ontology)         │
                          │                      │
                          │  - Requirements      │
                          │  - Principles        │
                          │  - Outcomes          │
                          │  - Relationships     │
                          └──────────────────────┘
```

**Key Insight (E2):** We don't need execution engines. Rai reads skills and calls tools. 85% scope reduction, better flexibility, same outcomes.

### Package

- **PyPI:** `rai-cli`
- **Command:** `rai`
- **Install:** `pip install raise-cli` or `uv install raise-cli`

---

## Evolution

### Roadmap

```
v2.0 (Open Core - Individual)
├── Skills library (process guides)
├── Toolkit (concept extraction, graph, MVC)
├── Memory system (session graph)
├── Calibration (estimate tracking)
├── System prompt (Rai identity)
└── CLI interface

v2.x (Open Core - Enhanced)
├── Brownfield analysis (SAR)
├── Template scaffolding
├── Custom skill authoring
└── MCP interface

v3.0 (Commercial - Team)
├── Hosted Rai (managed inference)
├── Team layer (shared patterns, visibility)
├── Platform integrations (Jira, Confluence, Rovo)
├── Accumulated wisdom (cross-project learning)
└── Continuous improvement (Rai evolves)
```

### Milestones

| Date | Milestone | Focus |
|------|-----------|-------|
| Feb 9, 2026 | Friends & Family | Individual developers, open core |
| Feb 15, 2026 | Public Launch | Community adoption |
| Mar 14, 2026 | Atlassian Webinar | Hosted Rai demo, Rovo integration |
| 2026 H2 | Team Launch | Team features, commercial |

### Evolution Principles

1. **Ship fast, iterate** — Lean approach to market timing
2. **Dogfood first** — humansys.ai team uses RaiSE daily
3. **Individual before team** — Solo value first, team features emerge from real needs
4. **Local before hosted** — Open core proves value, commercial extends it

---

## The humansys.ai Test Bed

Our first team: junior developers learning RaiSE with Rai.

**What we're testing:**
- Can Rai teach RaiSE through practice?
- Do junior devs build intuition over time?
- What team features emerge from real usage?
- How does calibration evolve across the team?

**What we expect:**
- Each developer + Rai = learning pair
- Patterns that work get codified
- Skill progression visible over weeks
- Team features designed from real needs, not imagination

---

## Quality Attributes

| Attribute | Target | Metric |
|-----------|--------|--------|
| **Performance** | < 5 seconds | Common CLI operations |
| **Token Efficiency** | > 90% reduction | MVC vs full context |
| **Test Coverage** | > 90% | Core codebase |
| **Skill Execution** | 2-3x velocity | Compared to unguided AI |

---

## Traceability

| Source | Artifact |
|--------|----------|
| Business Case | `governance/business_case.md` |
| Rai as Entity | `dev/decisions/adr-013-rai-as-entity.md` |
| Identity Core | `dev/decisions/adr-014-identity-core-structure.md` |
| Memory Infrastructure | `dev/decisions/adr-015-memory-infrastructure.md` |
| E2 Architecture | `dev/decisions/adr-011-*.md`, `dev/decisions/adr-012-*.md` |
| Rai Identity Doc | `.claude/rai/identity.md` (will migrate to `.rai/`) |
| OpenClaw Research | `work/research/openclaw-architecture/` |
| Session Log | `dev/sessions/` |

---

## Approvals

| Role | Name | Date | Decision |
|------|------|------|----------|
| Founder/CEO | Emilio Osorio | 2026-01-30 | **APPROVED** (v1.0) |
| Founder/CEO | Emilio Osorio | 2026-02-01 | **PENDING** (v2.1 - Entity Model) |

---

*Document created: 2026-01-30*
*Major revision: 2026-02-01 (Post-E2 reframe: Toolkit + Rai)*
*Revision: 2026-02-01 (Entity Model: ADR-013, ADR-014, ADR-015)*
*Kata: solution/vision*
*Version: 2.1.0*
