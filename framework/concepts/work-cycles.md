# Work Cycles

> The five phases of work in RaiSE

---

## Overview

RaiSE organizes all work into **five cycles**. Each cycle has a specific purpose, produces specific artifacts, and has validation gates.

```
┌─────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐
│  SETUP  │ → │ SOLUTION │ → │ PROJECT │ → │ FEATURE │ → │ MAINTENANCE │
└─────────┘   └──────────┘   └─────────┘   └─────────┘   └─────────────┘
  once per      once per       once per      many per       ongoing
  codebase      system         initiative    project
```

## The Five Cycles

### 1. Setup Cycle

**When:** Once when adopting RaiSE (or onboarding to existing project)

**Purpose:** Understand current state, establish governance foundation

**Key Katas:**
- `setup/analyze` — Understand the codebase
- `setup/ecosystem` — Map integrations and dependencies
- `setup/governance` — Establish guardrails

**Artifacts Produced:**
- Codebase analysis report
- Ecosystem map
- Initial guardrails

---

### 2. Solution Cycle

**When:** Once per system/product

**Purpose:** Define the big picture—what are we building and why

**Key Katas:**
- `solution/discovery` — Business case and problem definition
- `solution/vision` — Technical vision and approach

**Artifacts Produced:**
- `governance/business_case.md`
- `governance/vision.md`

---

### 3. Project Cycle

**When:** Once per major initiative (epic, milestone)

**Purpose:** Plan a specific body of work with clear scope

**Key Katas:**
- `project/discovery` — PRD (requirements)
- `project/vision` — Project-specific vision
- `project/design` — Technical design
- `project/backlog` — Prioritized work items

**Artifacts Produced:**
- `governance/prd.md`
- `governance/design.md`
- `governance/backlog.md`

---

### 4. Feature Cycle

**When:** Many times per project

**Purpose:** Build one increment of value

**Key Katas:**
- `feature/design` — Feature technical design
- `feature/stories` — User stories with acceptance criteria
- `feature/plan` — Implementation plan
- `feature/implement` — Guided development
- `feature/review` — Validation and review

**Artifacts Produced:**
- `work/stories/{name}/spec.md`
- `work/stories/{name}/plan.md`
- Actual code and tests

---

### 5. Maintenance Cycle

**When:** Ongoing throughout project life

**Purpose:** Keep the system healthy

**Key Katas:**
- Refactoring
- Documentation updates
- Dependency updates
- Technical debt reduction

**Artifacts Produced:**
- Updated documentation
- Improved code
- Reduced technical debt

---

## Cycle Progression

Not every project needs every cycle:

| Scenario | Cycles Used |
|----------|-------------|
| New greenfield project | All five |
| New feature on existing product | Feature only |
| Major initiative | Project + Feature |
| Joining existing team | Setup + Feature |
| Bug fix | Feature (simplified) |

## Gates Between Cycles

Each cycle ends with a **gate** that validates work before proceeding:

```
Solution ──[gate-vision]──→ Project ──[gate-design]──→ Feature
```

Gates ensure:
- Artifacts are complete
- Quality criteria met
- Dependencies satisfied
- Ready for next phase

---

## Key Takeaways

1. **Five cycles** — Setup, Solution, Project, Feature, Maintenance
2. **Different frequencies** — Some once, some many times
3. **Gates between** — Validation before proceeding
4. **Not always all** — Use what fits your context

---

*Next: [Katas](./katas.md) | Reference: [Work Cycles Detail](../reference/work-cycles.md)*
