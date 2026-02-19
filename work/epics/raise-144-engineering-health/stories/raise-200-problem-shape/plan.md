# Implementation Plan: RAISE-200 — /problem-shape

## Overview
- **Story:** RAISE-200
- **Title:** /problem-shape — Guided problem definition at portfolio level
- **Size:** M
- **Created:** 2026-02-19
- **Module:** mod-skills (bc-skills, lyr-domain)
- **Deliverables:** 2 SKILL.md files (1 new, 1 modified)

## Context

Este story es **puro contenido** — no hay código Python. No aplica TDD ciclo RED/GREEN/REFACTOR.
La verificación es structural (`rai skill validate`) + end-to-end manual.

Patrones aplicados:
- PAT-E-357: SKILL.md es el formato estándar AgentSkills — mismo YAML frontmatter cross-tool
- PAT-E-055: Skills necesitan MVC por fase — el skill usa rai-cli donde corresponde
- PAT-E-263: Research ya realizada (RES-problem-definition-frameworks) — no re-investigar

---

## Tasks

### Task 1: Scaffold + Steps 0-2 (Context gate, APUESTA, PARA QUIÉN)
- **Description:** Crear `.claude/skills/problem-shape/SKILL.md` completo con frontmatter YAML, Purpose, Mastery Levels. Implementar Steps 0 (gate `rai session start --context`), Step 1 (APUESTA — 4 opciones), Step 2 (PARA QUIÉN — 4 opciones). El gate de Step 0 extrae el nombre del proyecto del bundle; si falla, pide el nombre explícitamente antes de continuar.
- **Files:**
  - `.claude/skills/problem-shape/SKILL.md` → CREATE
- **Verification:**
  ```bash
  rai skill validate problem-shape
  grep -c "Step" .claude/skills/problem-shape/SKILL.md  # debe ser ≥6
  ```
- **Size:** S
- **Dependencies:** None

---

### Task 2: Step 3 — Anti-solution gate
- **Description:** Implementar Step 3 (ESTADO ACTUAL) en el SKILL.md. Incluye: plantilla `[quién] no puede [hacer qué] porque [razón]`, lista de patrones de detección de solución (`"queremos construir"`, `"necesitamos implementar"`, `"vamos a desarrollar"`, `"la solución es"`, `"hay que hacer"`), protocolo de desafío UNA VEZ con curiosidad (`"Eso es una solución, no un problema. ¿Qué pasa hoy sin eso?"`), y aceptación en segunda instancia con nota `⚠ Estado actual podría ser parcialmente solución-shaped`.

  **IMPORTANT:** El gate nunca desafía dos veces — documentarlo explícitamente en el skill.

- **Files:**
  - `.claude/skills/problem-shape/SKILL.md` → MODIFY (añadir Step 3)
- **Verification:**
  ```bash
  grep -A5 "anti-solution\|solución-shaped\|ONCE\|una vez" .claude/skills/problem-shape/SKILL.md
  ```
- **Size:** S
- **Dependencies:** Task 1

---

### Task 3: Steps 4-6 + Problem Brief output
- **Description:** Completar el skill con:
  - Step 4 (3 WHYS): exactamente 3 preguntas por qué, secuenciales; el agente nombra la raíz identificada explícitamente antes de continuar
  - Step 5 (EARLY SIGNAL): 4 opciones de indicador a 4 semanas (métrica / comportamiento / proceso / queja)
  - Step 6 (HIPÓTESIS): formato SAFe If/Then/For/Measured-by; agente propone draft completo, usuario corrige
  - Sección Output: template completo del Problem Brief en Markdown con las 6 secciones, instrucción de Write a `work/problem-briefs/{slug-proyecto}-{YYYY-MM-DD}.md`, sección "Next: `/rai-epic-design`"
  - Sección Notes y References

- **Files:**
  - `.claude/skills/problem-shape/SKILL.md` → MODIFY (añadir Steps 4-6 + Output)
- **Verification:**
  ```bash
  rai skill validate problem-shape
  # Verificar que el template del Problem Brief incluye las 6 secciones
  grep -c "##" .claude/skills/problem-shape/SKILL.md
  ```
- **Size:** M
- **Dependencies:** Task 2

---

### Task 4: /rai-epic-design Step 0.7
- **Description:** Insertar Step 0.7 en `.claude/skills/rai-epic-design/SKILL.md` después de Step 0.6 (Load Architectural Context) y antes de Step 1. El paso verifica si existe un Problem Brief en `work/problem-briefs/`, lo carga y lo usa como input pre-poblado para Step 1 (Objective) en lugar de solicitarlo verbalmente.

  ```bash
  # Step 0.7: Load Problem Brief (if exists)
  ls work/problem-briefs/*.md 2>/dev/null | tail -1
  ```

  Si existe → leer y resumir en Step 1 como "Objective (from Problem Brief)". Si no existe → continuar normalmente (Step 0.7 es opcional, no blocking).

- **Files:**
  - `.claude/skills/rai-epic-design/SKILL.md` → MODIFY (insertar Step 0.7)
- **Verification:**
  ```bash
  grep -n "0.7\|Problem Brief" .claude/skills/rai-epic-design/SKILL.md
  # Debe aparecer entre Step 0.6 y Step 1
  ```
- **Size:** XS
- **Dependencies:** Task 1 (para entender el output format del Brief)

---

### Task 5 (Final): Manual Integration Test
- **Description:** Ejecutar `/problem-shape` end-to-end en un escenario de demo realista (contexto Kurigage o Coppel). Verificar: (1) `rai session start --context` carga el nombre del proyecto, (2) los 6 pasos fluyen en orden, (3) el anti-solution gate se activa si se da lenguaje de solución, (4) el Problem Brief se guarda en `work/problem-briefs/`, (5) invocar `/rai-epic-design` y confirmar que Step 0.7 detecta y carga el Brief.
- **Verification:**
  ```bash
  ls work/problem-briefs/*.md  # archivo creado
  # Step 0.7 en rai-epic-design carga el Brief en un run real
  ```
- **Size:** XS
- **Dependencies:** Tasks 1, 2, 3, 4

---

## Execution Order

```
Task 1 — Scaffold + Steps 0-2
    ↓
Task 2 — Step 3 anti-solution gate
    ↓
Task 3 — Steps 4-6 + Problem Brief output
    ↓  ←── (independiente, puede paralelizar con Task 3 si hay contexto suficiente)
Task 4 — rai-epic-design Step 0.7
    ↓
Task 5 — Integration test (todos completos)
```

Tasks 3 y 4 son independientes entre sí — pueden ejecutarse en paralelo si el contexto del output format está claro desde Task 1.

## Risks

- **Gate fallback:** Si `rai session start --context` no está disponible (proyecto sin `.raise/`), el skill debe degradar elegantemente pidiendo el nombre. Documentar el fallback explícitamente.
- **Anti-solution gate calibration:** Los patrones de detección son heurísticos. Una lista demasiado corta falla; una demasiado larga genera falsos positivos con stakeholders. Calibrar en la integration test.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Scaffold + Steps 0-2 | S | -- | |
| 2 — Anti-solution gate | S | -- | Parte más delicada |
| 3 — Steps 4-6 + Output | M | -- | Incluye template completo |
| 4 — rai-epic-design Step 0.7 | XS | -- | Modificación quirúrgica |
| 5 — Integration test | XS | -- | Demo scenario |
