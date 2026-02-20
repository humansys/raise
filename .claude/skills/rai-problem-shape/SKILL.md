---
name: rai-problem-shape
description: >
  Guided problem definition at portfolio level. Takes a vague business idea
  and shapes it into a well-formed problem statement before it enters the
  epic pipeline. Produces a Problem Brief that feeds /rai-epic-design.

license: MIT

metadata:
  raise.work_cycle: utility
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
[vague business idea] → /rai-problem-shape → /rai-epic-design → /rai-epic-plan → [stories]
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

### Step 3: ESTADO ACTUAL

Present the template:

> "Ahora describe la situación hoy, sin proponer soluciones todavía.
>
> Completa esta frase:
> **[quién] no puede [hacer qué] porque [razón]**
>
> Ejemplo: 'Liderazgo no puede detectar proyectos en riesgo porque no hay señal temprana.'"

**Anti-solution gate:**

Scan the response for solution-shaped language. Trigger patterns (any of these is a gate hit):
- "queremos construir", "vamos a construir"
- "necesitamos implementar", "vamos a implementar"
- "vamos a desarrollar", "hay que desarrollar"
- "la solución es", "la respuesta es"
- "necesitamos un sistema", "necesitamos una plataforma"
- "necesitamos una herramienta", "necesitamos una app"

**If triggered → challenge ONCE, with curiosity:**

> "Eso suena a una solución, no a un problema. ¿Qué está pasando hoy sin eso?
> ¿Qué no pueden hacer? ¿Qué consecuencia tiene eso para [stakeholder del Step 2]?"

**IMPORTANT:** Challenge **only once**. If the second response also contains solution language, accept it and add a warning flag to the Problem Brief:

> *(Nota en Brief: `⚠ Estado actual podría ser parcialmente solución-shaped. Revisar en /rai-epic-design Step 1.`)*

**DO NOT** challenge a second time. The stakeholder has been made aware; further pushback damages trust.

**Verification:** Estado actual captured — describes an observable gap, not a solution.

---

### Step 4: 3 WHYS

Ask exactly three sequential "why" questions to drill from symptom to root cause.

> "Muy bien. Ahora vamos a encontrar la raíz. Te haré tres preguntas."

**Why 1:**
> "¿Por qué [Estado Actual del Step 3]? ¿Cuál es la causa inmediata?"

**Why 2 (based on Why 1 answer):**
> "¿Y por qué [respuesta del Why 1]?"

**Why 3 (based on Why 2 answer):**
> "¿Y por qué [respuesta del Why 2]?"

After three answers, name the root cause explicitly before moving on:

> "La raíz que identificamos es: **[síntesis en una oración]**. ¿Correcto?"

Confirm with the stakeholder before continuing.

**IMPORTANT:** Execute exactly 3 Whys — no more, no less. The depth is intentional (Toyota Production System).

**Verification:** Root cause named and confirmed by stakeholder.

---

### Step 5: EARLY SIGNAL (~30s)

Present as multiple choice:

> "Perfecto. Ahora pensemos en señales tempranas — no el resultado final, sino cómo sabrías en **4 semanas** que vas por buen camino.
>
> **¿Qué cambiaría primero?**
>
> A) Una métrica que mejora — un número empieza a moverse en la dirección correcta
> B) Un comportamiento que cambia — alguien empieza o deja de hacer algo
> C) Un proceso que desaparece — algo que hoy se hace manual ya no es necesario
> D) Una queja que deja de escucharse — un problema recurrente ya no aparece"

**Purpose:** 4-week horizon is intentional — forces leading indicators, not lagging KPIs.

**If D (Queja):** Ask them to name the specific complaint. Record it concretely.

**Verification:** Early signal identified — concrete, 4-week horizon, leading indicator.

---

### Step 6: HIPÓTESIS

Draft a complete SAFe-compatible hypothesis using all collected context. **Do not leave blanks.**

**Format:**
```
Si [Estado Actual refinado — Step 3],
entonces [Early Signal — Step 5]
para [Stakeholder afectado — Step 2],
medido por [métrica específica y observable].
```

Present the draft to the stakeholder:

> "Basándome en lo que me dijiste, propongo esta hipótesis:
>
> *Si [...], entonces [...] para [...], medido por [...].*
>
> ¿Esto captura el problema? ¿Qué corregirías?"

Incorporate corrections. The final hypothesis belongs to the stakeholder — Rai only drafts.

**Verification:** Hypothesis accepted by stakeholder.

---

### Step 7: Save Problem Brief

Write the Problem Brief to `work/problem-briefs/` using the Write tool.

**Filename:** `{slug-proyecto}-{YYYY-MM-DD}.md`
where `{slug-proyecto}` is the project name from Step 0, lowercased, spaces replaced with hyphens.

**Template:**

```markdown
# Problem Brief — {Nombre del Proyecto}
> Generado: {YYYY-MM-DD} | Skill: /rai-problem-shape v1.0

## Dominio / Tipo de apuesta
{Step 1 answer}

## Stakeholder afectado
{Step 2 answer}

## Estado actual
{Step 3 refined answer}
{⚠ note if applicable}

## Problema raíz (3 Whys)
1. ¿Por qué {Estado Actual}? → {Why 1 answer}
2. ¿Por qué {Why 1}? → {Why 2 answer}
3. ¿Por qué {Why 2}? → {Why 3 answer}

**Raíz identificada:** {root cause in one sentence, confirmed by stakeholder}

## Early signal (4 semanas)
{Step 5 answer — specific and observable}

## Hipótesis
Si {Step 3 refined},
entonces {Step 5}
para {Step 2},
medido por {specific metric}.

---
**Next:** `/rai-epic-design` — usa este Brief como input para Step 0.7 (Objective)
```

After writing, confirm:

> "Brief guardado en `work/problem-briefs/{filename}`. El siguiente paso es `/rai-epic-design`, que lo cargará automáticamente desde Step 0.7."

**Verification:** `work/problem-briefs/{slug}-{YYYY-MM-DD}.md` exists.

---

## Output

- **Primary:** `work/problem-briefs/{slug-proyecto}-{YYYY-MM-DD}.md`
- **Next:** `/rai-epic-design` — Step 0.7 loads this Brief automatically if it exists

## Notes

- **Spanish-first (v1):** All step prompts are in Spanish. Internationalization is out of scope for v1.
- **Lite mode:** Deferred to v2. v1 always executes the full 6-step flow.
- **No epic creation:** `/rai-epic-design` handles epic initialization. This skill ends at the Problem Brief.
- **Anti-solution gate calibration:** The trigger pattern list covers common Spanish phrasing. Extend if false negatives are observed in real usage.
- **10-minute target:** Standard flow is ~10 minutes. Free-text answers in Steps 3-4 may extend it slightly.

## References

- Research base: `work/research/RES-problem-definition-frameworks/`
- Pipeline next: `.claude/skills/rai-epic-design/SKILL.md` (Step 0.7)
- Output directory: `work/problem-briefs/`
- Framework: Impact Mapping (Adzic), Lean UX (Gothelf), SAFe Hypothesis, Toyota 5 Whys
