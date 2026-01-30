# Katas

> **Work Cycle processes** — Cultural wisdom for software development

---

## What is a Kata

A kata is a process pattern adapted to a Work Cycle context. Each kata encodes:

| Component | Purpose |
|-----------|---------|
| **Work Cycle** | When this kata applies (solution, project, feature, setup, improve) |
| **Frequency** | How often executed (once-per-solution, once-per-project, per-feature, continuous) |
| **ShuHaRi** | Mastery levels for adaptation |
| **Jidoka Inline** | Stop-on-defect pattern in each step |

## Three-Level Hierarchy (ADR-010)

```
SOLUTION LEVEL (System - endures)
├── solution/discovery    → Business Case
├── solution/vision       → Solution Vision
└── setup/governance      → Governance (guardrails)
        │
        │ constrains all projects
        ▼
PROJECT LEVEL (Initiative - time-bound)
├── project/discovery     → PRD
├── project/vision        → Project Vision
├── project/design        → Tech Design
└── project/backlog       → Backlog
        │
        │ implements via features
        ▼
FEATURE LEVEL (Implementation)
├── feature/plan          → Implementation plan
├── feature/implement     → Working code
└── feature/review        → Retrospective
```

## Work Cycles

```
katas/
├── solution/     # Per-solution (once) — system definition
├── project/      # Per-project (once) — initiative artifacts
├── feature/      # Per-feature (many) — implementation cycles
├── setup/        # Per-solution (once) — governance & environment
└── improve/      # Continuous — retrospective and evolution
```

## Available Katas

### solution/ (Per-Solution) — NEW in v2.4

| Kata | Purpose | Output |
|------|---------|--------|
| `discovery.md` | Business Case creation | `governance/solution/business_case.md` |
| `vision.md` | Solution Vision | `governance/solution/vision.md` |

> **Flow**: `discovery` → `vision` → `setup/governance`

### setup/ (Per-Solution)

| Kata | Purpose | Output |
|------|---------|--------|
| `governance.md` | System-wide Guardrails | `governance/solution/guardrails.md` |
| `rules.md` | Codebase Patterns | `.cursor/rules/*.mdc` |
| `ecosystem.md` | Dependency Mapping | `governance/solution/ecosystem.md` |

> **Flow**: `governance` → `rules` → `ecosystem` (see ADR-009)
> **Prerequisite**: `solution/vision` for greenfield governance

### project/ (Per-Project)

| Kata | Purpose | Output (approved) |
|------|---------|-------------------|
| `discovery.md` | PRD creation | `governance/projects/{name}/prd.md` |
| `vision.md` | Project Vision | `governance/projects/{name}/vision.md` |
| `design.md` | Technical Architecture | `governance/projects/{name}/design.md` |
| `backlog.md` | Product Backlog | `governance/projects/{name}/backlog.md` |

> **Note**: Project Vision was renamed from "Solution Vision" in v2.4 (ADR-010)
> **Note**: Drafts are created in `work/projects/{name}/`, promoted to `governance/` after gate passes

### feature/ (Per-Feature)

| Kata | Purpose | Output |
|------|---------|--------|
| `plan.md` | Implementation Planning | `work/features/{NNN-name}/plan.md` |
| `implement.md` | Development Workflow | Working code |
| `review.md` | Retrospective & Learning | `work/features/{NNN-name}/retrospective.md` |

> **Note**: Feature artifacts are transient and stay in `work/` (ADR-011)

---

## Kata Schema

```yaml
---
id: solution-discovery
titulo: "Solution Discovery: Crear Business Case"
work_cycle: solution
frequency: once-per-solution
fase_metodologia: 0

prerequisites: []
template: templates/raise/solution/business_case.md
gate: null
next_kata: solution/vision

adaptable: true
shuhari:
  shu: "Seguir todos los pasos exactamente"
  ha: "Combinar pasos si métricas claras"
  ri: "Crear kata específica del dominio"

version: 1.0.0
---
```

## Jidoka Inline Pattern

Each step includes verification and recovery action:

```markdown
### Paso N: [Action]

[Description]

**Verificación**: [How to know it's correct]

> **Si no puedes continuar**: [Condition] → [Recovery action]
```

This enables **stopping on defects** and correcting before proceeding.

---

## ShuHaRi Levels

| Level | Meaning | Application |
|-------|---------|-------------|
| **Shu (守)** | Follow | Execute kata exactly as written |
| **Ha (破)** | Adapt | Modify steps based on context |
| **Ri (離)** | Transcend | Create domain-specific katas |

---

## Three-Directory Model (ADR-011)

Artifacts are stored in:

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `governance/` | Approved, authoritative artifacts | Solution Vision, Project Vision (after gate) |
| `work/` | Work-in-progress | Feature specs, draft proposals |
| `.raise/` | Framework configuration | Katas, gates, templates |

**Promotion flow**: `work/` → (gate passes) → `governance/`

## References

- **ADR-011**: Three-Directory Model (governance/, work/, .raise/)
- **ADR-010**: Three-Level Artifact Hierarchy (Solution → Project → Feature)
- **ADR-009**: Continuous Governance Model
- **ADR-008**: Kata/Skill/Context Simplification
