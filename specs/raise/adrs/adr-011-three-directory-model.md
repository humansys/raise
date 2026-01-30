---
id: "ADR-011"
title: "Three-Directory Model: .raise/, governance/, work/"
date: "2026-01-30"
status: "Proposed"
related_to: ["ADR-010", "ADR-009"]
supersedes: []
---

# ADR-011: Three-Directory Model for Project Structure

## Contexto

### Problema Identificado

RaiSE projects currently scatter "golden data" across multiple locations:

```
current-state/
├── .raise/              # Framework config + context/ (golden data)
├── specs/
│   ├── raise/           # Framework vision, ADRs (golden data)
│   ├── main/            # Project artifacts (golden data)
│   └── NNN-feature/     # Feature work (work-in-progress)
└── docs/                # Research, archive (some golden data?)
```

**Problems:**

1. **Scattered knowledge**: Golden data lives in 4+ locations
2. **Agent inefficiency**: Must explore multiple directories to understand the system
3. **Semantic confusion**: `specs/` contains both stable knowledge AND work-in-progress
4. **Inherited baggage**: `specs/` naming comes from spec-kit, implies "specifications" but contains diverse work
5. **Golden data drift**: Without clear structure and tooling, authoritative knowledge drifts from reality

### Analysis

We identified three distinct concerns with different lifecycles:

| Concern | Nature | Lifecycle | Who Updates |
|---------|--------|-----------|-------------|
| Configuration | How to work | Synced from central (enterprise) | Framework maintainers |
| Governance | What governs | Curated, stable, approved | Project team (via gates) |
| Work | What we're doing | Transient, in-progress | Individual contributors |

The current structure conflates these concerns, especially mixing governance and work in `specs/`.

### Key Insight

> `specs/` is a **workbench** — but we've been using it as a **library**.

The distinction:
- **Workbench**: Where you DO work (messy, evolving, temporary)
- **Authority**: Where you STORE governance (curated, stable, authoritative)

### Why "Governance" Not "Corpus" or "Knowledge"

SAFe introduced "Solution Intent" specifically to avoid the word "governance" — they were designing for corporate settings where governance has negative connotations that might "kill innovation."

RaiSE has a different problem domain:

| Framework | Problem Domain | Stance on Governance |
|-----------|---------------|---------------------|
| **SAFe** | Corporate innovation at scale | Governance = friction → soften it |
| **RaiSE** | Reliable AI-assisted engineering | Governance = the point → embrace it |

RaiSE exists because AI agents need **explicit constraints** to produce reliable output. Governance isn't something to hide — it's the core value proposition. Therefore, we name the directory what it is: `governance/`.

## Decisión

### Adopt Three-Directory Model

```
project/
├── .raise/                 # CONFIGURATION (the engine)
│   ├── katas/              # Process definitions
│   ├── gates/              # Validation criteria
│   ├── templates/          # Scaffolds
│   ├── skills/             # Atomic operations
│   └── harness.yaml        # Local config (enterprise: synced)
│
├── governance/             # AUTHORITY (what governs)
│   ├── index.yaml          # Manifest for agents
│   ├── solution/           # Solution-level artifacts
│   │   ├── business_case.md
│   │   ├── vision.md
│   │   └── guardrails.md   # The rules (constraints)
│   ├── projects/           # Project-level artifacts (approved)
│   │   └── {project-name}/
│   │       ├── vision.md
│   │       ├── design.md
│   │       └── backlog.md
│   └── decisions/          # ADRs (accepted)
│       └── adr-NNN.md
│
└── work/                   # ACTIVITY (the workbench)
    ├── features/           # Feature-level work
    │   └── NNN-name/
    │       ├── spec.md
    │       ├── plan.md
    │       └── tasks.md
    ├── proposals/          # ADRs in draft
    ├── research/           # Spikes, investigations
    └── {any-governed-work}/
```

### The Triad

| Directory | Metaphor | Purpose | Stability |
|-----------|----------|---------|-----------|
| `.raise/` | The engine | How to govern | Stable (synced) |
| `governance/` | The authority | What governs | Curated (approved) |
| `work/` | The workbench | What's governed | Transient (WIP) |

### Rename `specs/` to `work/`

**Rationale:**

| `specs/` | `work/` |
|----------|---------|
| Implies output is "specifications" | Neutral — any governed activity |
| Inherited from spec-kit | Clean slate, intentional naming |
| Confuses with `governance/` (both sound like documents) | Clear distinction: authority vs activity |

The name `work/` is honest about what the directory contains: work-in-progress that may or may not become authoritative.

### The Governance Index (`governance/index.yaml`)

A manifest that enables agents to understand the project without exploration:

```yaml
schema_version: "1.0.0"
solution:
  name: "My Product"
  status: active

artifacts:
  # Solution-level
  - path: solution/vision.md
    level: solution
    type: vision
    version: 2.0.0
    status: approved
    approved_date: 2026-01-15

  - path: solution/guardrails.md
    level: solution
    type: guardrails
    version: 1.5.0
    status: approved
    derives_from: solution/vision.md

  # Project-level
  - path: projects/kata-harness/vision.md
    level: project
    type: vision
    version: 1.0.0
    status: approved
    parent: solution/vision.md

  # Decisions
  - path: decisions/adr-010.md
    level: solution
    type: decision
    status: accepted
    supersedes: null

relationships:
  - from: solution/guardrails.md
    to: solution/vision.md
    type: derives_from

  - from: projects/kata-harness/vision.md
    to: solution/vision.md
    type: implements
```

**Agent workflow:**
1. Read `governance/index.yaml` (one read)
2. Know exactly what exists, versions, relationships
3. Read only artifacts needed for current task

### Governance Promotion Flow

Work becomes governance when approved:

```
work/ (workbench)                     governance/ (authority)
─────────────────                     ──────────────────────

work/proposals/adr-011.md      →      governance/decisions/adr-011.md
     (draft)                               (accepted)

work/features/NNN/             →      (nothing — ephemeral)
     (feature work)

work/projects/new-project/     →      governance/projects/new-project/
  project_vision.md                     vision.md
     (draft)                               (approved)
```

**The gate determines promotion**: When a gate passes, the artifact moves from `work/` to `governance/`.

### Enterprise Sync Model

For enterprise deployments, `.raise/` becomes a sync target:

```
Central Repository                    Local Project
──────────────────                    ─────────────

.raise-central/                       .raise/
├── katas/                    sync    ├── katas/
├── gates/                    ───→    ├── gates/
├── templates/                        ├── templates/
└── skills/                           ├── skills/
                                      └── harness.yaml (local overrides)
```

The `harness.yaml` allows local configuration:

```yaml
# .raise/harness.yaml
sync:
  source: "https://raise.company.com/central"
  frequency: daily

overrides:
  gates:
    - gate-security: strict  # Override default

local:
  team: "platform"
  environment: development
```

### Governance Maintenance Tooling

Without tooling, governance drifts from reality:

```
governance/           work/
    │                   │
    │    (time passes)  │
    │                   │
    ▼                   ▼
  stale              evolved
  authority          reality
         ↓
    "golden data drift"
```

To prevent drift, orchestrators need maintenance tools in `dev/`:

```
dev/
├── skills/
│   ├── governance-sync.md      # Promote work → governance after gates pass
│   ├── governance-audit.md     # Detect drift between governance and reality
│   └── impact-analysis.md      # What needs updating when governance changes
└── governance-index.yaml       # Meta-index for change tracking
```

**Key workflows:**

| Workflow | Trigger | Action |
|----------|---------|--------|
| **Promotion** | Gate passes | Move artifact from `work/` to `governance/`, update index |
| **Audit** | Periodic / on-demand | Compare governance claims vs. codebase reality |
| **Impact Analysis** | Before changing governance | Show all artifacts affected by proposed change |

These tools are for **framework maintainers and orchestrators**, not end users. They live in `dev/` and are not part of the injected framework.

## Consecuencias

### Positivas

| Aspecto | Beneficio |
|---------|-----------|
| **Clarity** | Three concerns, three directories — no ambiguity |
| **Agent efficiency** | Single entry point (`governance/index.yaml`) for authority |
| **Honest naming** | `governance/` embraces RaiSE's core value; `work/` is what it is |
| **Clean lifecycle** | Work → (gate) → Governance is explicit |
| **Enterprise-ready** | `.raise/` as sync target enables centralized governance |
| **Minimal exploration** | Agents read index, not file trees |
| **Drift prevention** | Maintenance tooling keeps governance aligned with reality |

### Negativas

| Aspecto | Impacto | Mitigación |
|---------|---------|------------|
| **Breaking change** | `specs/` → `work/` rename | Migration script, deprecation period |
| **New concept** | `governance/` directory is new | Clear documentation, gradual adoption |
| **Index maintenance** | `governance/index.yaml` must stay in sync | Gates update index on promotion; audit tools detect drift |
| **spec-kit compatibility** | Breaks spec-kit conventions | spec-kit evolves with RaiSE |
| **File rename** | `governance.md` → `guardrails.md` | Update ADR-009 references |

### Impacto en Artefactos Existentes

| Actual | Nuevo | Acción |
|--------|-------|--------|
| `specs/main/solution_vision.md` | `governance/solution/vision.md` | Move + rename |
| `specs/main/governance.md` | `governance/solution/guardrails.md` | Move + rename |
| `specs/main/tech_design.md` | `governance/projects/{name}/design.md` | Move |
| `specs/NNN-feature/` | `work/features/NNN-feature/` | Move |
| `specs/raise/adrs/` | `governance/decisions/` (for consumer projects) | Move |
| `.raise/context/glossary.md` | `governance/context/glossary.md` | Move |

## Alternativas Consideradas

### A1: Keep `specs/` naming, add `governance/`

```
├── .raise/
├── governance/  # New: authority
└── specs/       # Keep: work
```

**Rejected**: `specs/` name still implies "specifications" which conflicts with the workbench purpose. Creates confusion about what goes where.

### A2: Single `data/` directory with subdirectories

```
├── .raise/
└── data/
    ├── governance/
    └── work/
```

**Rejected**: Extra nesting without benefit. The three top-level directories are cleaner.

### A3: Use `corpus/` instead of `governance/`

**Rejected**: "Corpus" comes from linguistics/NLP ("body of text"). It's semantically neutral but doesn't capture the PURPOSE of the directory. RaiSE's value proposition is explicit governance for reliability — the directory name should reflect that.

### A4: Use `knowledge/` or `golden/`

**Rejected**: These describe the NATURE of the content (knowledge, golden data) but not its PURPOSE. "Governance" says both what it contains AND why it matters.

### A5: Avoid "governance" (à la SAFe "Solution Intent")

**Rejected**: SAFe avoided "governance" to not stifle corporate innovation. RaiSE has a different problem domain — reliability optimization, not innovation enablement. Governance is the point, not a side effect to soften.

## Plan de Implementación

### Fase 1: Schema & Documentation

- [ ] Define `governance/index.yaml` JSON Schema
- [ ] Update glossary with new terms
- [ ] Create migration guide
- [ ] Update ADR-009 to reference `guardrails.md` instead of `governance.md`

### Fase 2: Structure Migration

- [ ] Create `governance/` directory structure
- [ ] Move solution-level artifacts to `governance/solution/`
- [ ] Move project-level artifacts to `governance/projects/`
- [ ] Rename `specs/` to `work/`
- [ ] Create initial `governance/index.yaml`
- [ ] Move `.raise/context/` to `governance/context/`

### Fase 3: Tooling

- [ ] Update katas to output to correct directories
- [ ] Update gates to manage promotion to `governance/`
- [ ] Create skill for index maintenance
- [ ] Update `.raise` injection script
- [ ] Create `dev/skills/governance-sync.md`
- [ ] Create `dev/skills/governance-audit.md`
- [ ] Create `dev/skills/impact-analysis.md`

### Fase 4: Deprecation

- [ ] Add deprecation warning for `specs/` usage
- [ ] Support both `specs/` and `work/` during transition (6 months)
- [ ] Remove `specs/` support in v3.0

## Glosario de Términos (Extensión v2.4)

| Término | Definición |
|---------|------------|
| **Governance Directory** | The authoritative source of curated, approved artifacts that govern a solution. Contains stable artifacts that have passed validation gates. |
| **Work Directory** | The workbench for governed work-in-progress. Contains drafts, proposals, and feature work that has not yet been promoted to governance. |
| **Governance Index** | A manifest file (`governance/index.yaml`) that describes all artifacts in the governance directory, enabling agents to understand the project without exploration. |
| **Governance Promotion** | The process of moving an artifact from `work/` to `governance/` after passing a validation gate. |
| **Golden Data Drift** | The condition where governance artifacts become stale and no longer reflect the reality of the codebase or project state. |
| **Configuration Sync** | Enterprise feature where `.raise/` is synchronized from a central repository. |
| **Guardrails** | The specific constraints and rules within governance. Renamed from `governance.md` to `guardrails.md` to avoid naming collision with the directory. |

## raise-commons Específico

Since raise-commons is both "the framework" AND "a project using the framework", it has a unique structure with a parallel between `governance/` and `framework/`:

| Directory | Governs | Purpose |
|-----------|---------|---------|
| `governance/` | Projects using RaiSE | Authoritative artifacts for consumer projects |
| `framework/` | RaiSE itself | Authoritative artifacts for the framework |

Both serve the same purpose (authoritative knowledge) for different domains.

### Structure

```
raise-commons/
├── .raise/                 # Framework engine (THE framework)
│   ├── katas/              # Process definitions
│   ├── gates/              # Validation criteria
│   ├── templates/          # Scaffolds
│   └── skills/             # Atomic operations
│
├── framework/              # Governance OF the framework (meta-level)
│   ├── index.yaml          # Manifest for framework artifacts
│   ├── vision.md           # What RaiSE IS (framework vision)
│   ├── schemas/            # JSON Schemas for validation
│   ├── context/            # Framework wisdom
│   │   ├── glossary.md
│   │   ├── constitution.md
│   │   └── philosophy.md
│   └── decisions/          # Framework ADRs (accepted)
│       └── adr-*.md
│
├── governance/             # Governance FOR dogfooding (if applicable)
│   └── ...                 # If we treat raise-commons as a project
│
├── work/                   # Active development work
│   ├── features/           # Feature-level work
│   ├── proposals/          # Draft ADRs
│   └── research/           # Spikes, investigations
│
└── dev/                    # Governance maintenance tooling (internal)
    ├── skills/
    │   ├── governance-sync.md
    │   ├── governance-audit.md
    │   └── impact-analysis.md
    └── framework-index.yaml  # Meta-index for change tracking
```

### The Parallel

```
Consumer Project                      raise-commons (Framework)
────────────────                      ────────────────────────

governance/                           framework/
├── solution/                         ├── vision.md
│   └── vision.md                     ├── context/
├── context/                          │   └── glossary.md
│   └── glossary.md                   └── decisions/
└── decisions/                            └── adr-*.md
    └── adr-*.md

    ↓                                     ↓
"What governs                         "What governs
 THIS project"                         THE framework"
```

### Governance Maintenance for Framework

The `dev/` directory contains tools for framework maintainers to prevent golden data drift:

```
dev/
├── skills/
│   ├── governance-sync.md      # Promote work → framework after gates pass
│   ├── governance-audit.md     # Detect drift between framework docs and reality
│   └── impact-analysis.md      # What needs updating when framework changes
└── framework-index.yaml        # Index of all framework artifacts for impact analysis
```

These tools are **not part of RaiSE** — they're how we BUILD RaiSE. They don't get injected to consumer projects.

---

<details>
<summary><strong>Referencias</strong></summary>

- **ADR-010**: Three-Level Artifact Hierarchy
- **ADR-009**: Continuous Governance Model
- **spec-kit**: Original source of `specs/` convention
- **SAFe Solution Intent**: Contrast case — SAFe avoids "governance" to protect innovation; RaiSE embraces it for reliability
- **Industry**: Golden source patterns, governance-as-code

</details>

---

*Proposed: 2026-01-30*
*Author: Kata Harness Design Session*
