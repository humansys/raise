---
name: problem-shape
description: >
  Guided problem definition at portfolio level. Takes a vague business idea
  and shapes it into a well-formed problem statement before it enters the
  epic pipeline. Produces a Problem Brief that feeds /rai-epic-design.

license: MIT

metadata:
  raise.work_cycle: portfolio
  raise.frequency: per-initiative
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-epic-design"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
---

# Problem Shape — Guided Problem Definition

## Purpose

Guide a portfolio owner, product leader, or business stakeholder from a vague initiative to a well-formed problem statement in ≤10 minutes.

**Position in the pipeline:**
```
[vague business idea] → /problem-shape → /rai-epic-design → /rai-epic-plan → [stories]
```

**Core principle:** Teams fail when they receive *solutions* from stakeholders instead of problems. This skill enforces the problem-first discipline before any implementation commitment is made.

**Output:** A Problem Brief saved to `work/problem-briefs/` that feeds `/rai-epic-design` as structured input.

## Context

**When to use:**
- A portfolio owner, product leader, or business stakeholder has a vague initiative, bet, or idea
- The work hasn't entered `/rai-epic-design` yet — there's no defined problem statement
- During pre-demo conversations where stakeholders describe solutions instead of problems

**When NOT to use:**
- The problem is already well-defined (go directly to `/rai-epic-design`)
- Story-level specification (use `/rai-story-design`)
- Technical spikes or research tasks (use `/rai-research`)

**Inputs required:**
- At minimum: a project name and a rough business idea
- Optionally: project context from `rai session start --context`

**Outputs:**
- `work/problem-briefs/{slug-proyecto}-{YYYY-MM-DD}.md` — Problem Brief with 6 sections
- Feeds `/rai-epic-design` Step 0.7 as structured input

---

## Framework Basis

| Framework | Contribution |
|-----------|-------------|
| Impact Mapping (Adzic) | WHY→WHO→HOW→WHAT structure |
| Lean UX Canvas Box 1 (Gothelf) | gap + adverse effect + measurable criterion |
| SAFe Epic Hypothesis | If/Then/For/Measured-by — enterprise-legible output |
| 5 Whys (Toyota) | Symptom → root cause gate |

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all 6 steps in sequence. Use multiple-choice options at each step.

**Ha (破)**: Adapt option labels to project domain if context is available from memory.

**Ri (離)**: Facilitate problem-shaping workshops with multiple stakeholders using the Brief as shared artifact.

## Steps

### Step 0: Load Project Context

Load the project context bundle to get the project name. The skill **MUST NOT execute without a project name**.

```bash
rai session start --project "$(pwd)" --context
```

Extract the project name from the bundle output. If the command fails or no project name is available, ask directly:

> "¿En qué proyecto estamos trabajando? (nombre del proyecto)"

**Gate:** Do not proceed to Step 1 without a confirmed project name.

**Verification:** Project name available.

---

### Step 1: APUESTA (~30s)

Present as multiple choice:

> "Vamos a dar forma al problema antes de comprometerte con una solución.
>
> **¿Qué tipo de problema crees que estás resolviendo?**
>
> A) Velocidad de entrega — el equipo tarda demasiado
> B) Calidad / retrabajo — hay demasiados errores o re-trabajo
> C) Visibilidad / control — no se sabe qué está pasando
> D) Otro — descríbelo en tus palabras"

**Purpose:** Anchors the domain. Sets vocabulary for subsequent steps.

**If D (Otro):** Accept free text. Summarize it back in one sentence and confirm before continuing.

**Verification:** Domain anchored.

---

### Step 2: PARA QUIÉN (~60s)

Present as multiple choice:

> "**¿Quién experimenta este problema directamente?**
>
> A) El equipo de desarrollo — los que construyen
> B) El área de negocio — los que operan
> C) Portafolio / liderazgo — los que deciden
> D) El cliente final — los que usan el producto"

**Purpose:** Impact Mapping — WHO before HOW. Establishes the affected stakeholder for the hypothesis in Step 6.

**If multiple apply:** Ask which one suffers the most. Pick one.

**Verification:** Primary stakeholder identified.

---

## Output

- **Primary:** `work/problem-briefs/{slug-proyecto}-{YYYY-MM-DD}.md`
- **Next:** `/rai-epic-design` — Step 0.7 loads this Brief automatically if it exists
