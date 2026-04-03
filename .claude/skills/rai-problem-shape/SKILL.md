---
name: rai-problem-shape
description: Shape a vague idea into a problem brief. Use before epic design for new initiatives.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: per-initiative
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-epic-design"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Problem Shape

## Purpose

Guide a stakeholder from a vague initiative to a well-formed problem statement in ≤10 minutes. Produces a Problem Brief that feeds `/rai-epic-design`.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all 6 steps in sequence with multiple-choice options
- **Ha**: Adapt option labels to project domain from memory context
- **Ri**: Facilitate multi-stakeholder problem-shaping workshops

## Context

**When to use:** A stakeholder has a vague initiative or idea that hasn't entered `/rai-epic-design` yet.

**When to skip:** Problem is already well-defined (go to `/rai-epic-design`), or this is story-level (use `/rai-story-design`).

**Inputs:** Project name (required), rough business idea.

**Pipeline:** `[vague idea]` → `/rai-problem-shape` → `/rai-epic-design` → `/rai-epic-plan` → `[stories]`

**Frameworks:** Impact Mapping (Adzic), Lean UX Canvas (Gothelf), SAFe Epic Hypothesis, Toyota 5 Whys.

## Steps

### Step 1: APUESTA — Anchor the Domain (~30s)

Present multiple choice (Spanish-first):
> "¿Qué tipo de problema crees que estás resolviendo?"
> A) Velocidad de entrega  B) Calidad / retrabajo  C) Visibilidad / control  D) Otro

If "Otro": accept free text, summarize back in one sentence, confirm.

<verification>
Domain anchored.
</verification>

### Step 2: PARA QUIÉN — Identify Stakeholder (~60s)

> "¿Quién experimenta este problema directamente?"
> A) Equipo de desarrollo  B) Área de negocio  C) Portafolio / liderazgo  D) Cliente final

If multiple apply: ask which suffers most, pick one.

<verification>
Primary stakeholder identified.
</verification>

### Step 3: ESTADO ACTUAL — Describe the Gap

> "Completa: **[quién] no puede [hacer qué] porque [razón]**"

**Anti-solution gate:** Scan for solution-shaped language ("queremos construir", "necesitamos implementar", "la solución es", etc.). If triggered, challenge **once**:
> "Eso suena a una solución. ¿Qué está pasando hoy sin eso?"

If second response also solution-shaped: accept it, add warning flag to Brief. Do not challenge twice.

<verification>
Gap described (observable, not solution-shaped).
</verification>

### Step 4: 3 WHYS — Find Root Cause

Ask exactly 3 sequential "why" questions, then name the root cause:
> "La raíz que identificamos es: **[síntesis]**. ¿Correcto?"

Confirm with stakeholder before continuing.

<verification>
Root cause named and confirmed.
</verification>

### Step 5: EARLY SIGNAL — Leading Indicator (~30s)

> "¿Qué cambiaría primero en **4 semanas**?"
> A) Métrica que mejora  B) Comportamiento que cambia  C) Proceso que desaparece  D) Queja que deja de escucharse

4-week horizon forces leading indicators, not lagging KPIs.

<verification>
Concrete early signal identified.
</verification>

### Step 6: HIPÓTESIS & Save Brief

Draft SAFe hypothesis: `Si [estado actual], entonces [early signal] para [stakeholder], medido por [métrica].`

Present to stakeholder for corrections. Save to `work/problem-briefs/{slug}-{YYYY-MM-DD}.md` with all 6 sections.

<verification>
Brief saved. Stakeholder confirmed hypothesis.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Problem Brief | `work/problem-briefs/{slug}-{YYYY-MM-DD}.md` |
| Next | `/rai-epic-design` (loads Brief at Step 0.7) |

## Quality Checklist

- [ ] Project name confirmed before starting (gate)
- [ ] Anti-solution gate applied in Step 3 (challenge once, max)
- [ ] Exactly 3 Whys executed (not 2, not 5)
- [ ] Root cause confirmed by stakeholder before continuing
- [ ] Early signal is 4-week horizon (leading, not lagging)
- [ ] Hypothesis uses SAFe format (Si/entonces/para/medido por)
- [ ] NEVER challenge solution language more than once — trust damages outweigh precision

## References

- Pipeline next: `/rai-epic-design` (Step 0.7 loads Brief)
- Output directory: `work/problem-briefs/`
- Frameworks: Impact Mapping, Lean UX, SAFe Hypothesis, Toyota 5 Whys
- Research: `work/research/RES-problem-definition-frameworks/`
