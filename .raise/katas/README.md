# Katas

> **Work Cycle processes** — Cultural wisdom for software development

---

## What is a Kata

A kata is a process pattern adapted to a Work Cycle context. Each kata encodes:

| Component | Purpose |
|-----------|---------|
| **Work Cycle** | When this kata applies (project, feature, setup, improve) |
| **Frequency** | How often executed (once-per-epic, per-feature, continuous) |
| **ShuHaRi** | Mastery levels for adaptation |
| **Jidoka Inline** | Stop-on-defect pattern in each step |

## Work Cycles

```
katas/
├── project/      # Per-epic (once) — strategic artifacts
├── feature/      # Per-feature (many) — implementation cycles
├── setup/        # Per-project (once) — environment preparation
└── improve/      # Continuous — retrospective and evolution
```

## Available Katas

### project/ (Per-Epic)

| Kata | Purpose | Output |
|------|---------|--------|
| `discovery.md` | PRD creation | `specs/main/project_requirements.md` |
| `vision.md` | Solution Vision | `specs/main/solution_vision.md` |
| `design.md` | Technical Architecture | `specs/main/tech_design.md` |
| `backlog.md` | Product Backlog | `specs/main/project_backlog.md` |

### feature/ (Per-Feature)

| Kata | Purpose | Output |
|------|---------|--------|
| `plan.md` | Implementation Planning | `specs/{feature}/plan.md` |
| `implement.md` | Development Workflow | Working code |
| `review.md` | Retrospective & Learning | `specs/{feature}/retrospective.md` |

### setup/ (Per-Project)

| Kata | Purpose | Output |
|------|---------|--------|
| `analyze.md` | Codebase Analysis | `specs/main/codebase_analysis.md` |
| `ecosystem.md` | Dependency Mapping | `specs/main/ecosystem_map.md` |

---

## Kata Schema

```yaml
---
id: discovery
titulo: "Discovery: Creación del PRD"
work_cycle: project
frequency: once-per-epic
fase_metodologia: 1

prerequisites: []
template: templates/solution/project_requirements.md
gate: gates/gate-discovery.md
next_kata: project/vision

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

*See: `specs/raise/adrs/adr-008-kata-skill-context-simplification.md`*
