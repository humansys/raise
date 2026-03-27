---
id: ADR-034
title: "Reformular P1: Humanos Definen Metas y Límites, Máquinas Negocian Ejecución"
status: proposed
date: 2026-03-27
decision_makers: [emilio]
epic: RAISE-789
story: S789.2
supersedes: "P1 original: Humans Define, Machines Execute"
---

# ADR-034: Reformulación de P1

## Contexto

P1 como está escrito dice: **"Humans Define, Machines Execute"** — los humanos definen qué se construye, las máquinas ejecutan la definición.

### Intención Original

P1 fue diseñado para prevenir tres modos de falla:
1. **Scope creep del agente** — que el agente expanda el alcance más allá de la intención humana
2. **Decisiones arquitectónicas sin supervisión** — que el agente tome decisiones irreversibles sin revisión humana
3. **Dirección estratégica autónoma** — que el agente decida qué construir sin que el humano lo defina

Estas tres protecciones son correctas y deben permanecer.

### Evidencia Operacional (500+ sesiones)

Después de 500+ sesiones de trabajo con RaiSE, la realidad operacional no coincide con el binario "define/ejecuta":

| Actividad | Quién decide | P1 dice | Realidad |
|-----------|-------------|---------|----------|
| Scope de la historia | Humano | Humano ✓ | Alineado |
| Estrategia de épica | Humano | Humano ✓ | Alineado |
| Decisiones de arquitectura | Humano (con input de Rai) | Humano ✓ | Alineado |
| Descomposición de tareas (/rai-story-plan) | Agente (humano revisa) | ¿Humano? | Agente propone, humano aprueba |
| Enfoque de ejecución (qué archivos, en qué orden) | Agente | Máquina ✓ | Alineado |
| Auto-evaluación (¿esto cumple las AC?) | Agente | ¿? | No cubierto por P1 |
| Metodología de investigación | Agente | ¿? | No cubierto por P1 |
| Selección de herramientas | Agente | Máquina ✓ | Alineado |
| Juicio de calidad ("¿es suficientemente bueno?") | Agente propone, humano revisa | ¿? | Compartido — P1 no modela esto |

**Observación clave:** La zona gris es "juicio compartido" — actividades donde el agente propone y el humano revisa. P1 no modela esto. Modela un binario limpio (humano define / máquina ejecuta) que no refleja la realidad colaborativa.

### Evidencia de S789.2 (E-ANTHROPIC Research)

El análisis de G13 (contract negotiation) reveló que:
- Anthropic no describe negociación de scope entre agentes
- Describe evaluación de calidad dentro de criterios definidos por humanos
- El patrón evaluador-optimizador (Art.1) es "un LLM genera, otro evalúa y da feedback en un loop" — esto es evaluación de ejecución, no definición de scope
- Clasificar esto como violación de P1 impide adoptar patrones de evaluación que son compatibles con la promesa de reliability de RaiSE

## Decisión

Reformular P1 de:

> **Antes:** "Humans Define, Machines Execute" — los humanos definen qué se construye, las máquinas ejecutan la definición.

A:

> **Después:** "Humans Define Goals and Boundaries — Machines Negotiate Execution within them." — Los humanos definen metas y límites; las máquinas negocian la ejecución dentro de esos límites.

## Clasificación de Actividades

### Propiedad Humana (no negociable)

Estas actividades requieren definición humana explícita. El agente NO puede iniciarlas ni modificarlas unilateralmente:

- **Metas estratégicas** — qué se construye, por qué, para quién
- **Límites de scope** — qué está dentro y fuera del alcance
- **Decisiones arquitectónicas irreversibles** — cambios que afectan múltiples sistemas o son costosos de revertir
- **Principios y valores** — las reglas del framework
- **Quality gates** — cuáles gates existen y cuándo se aplican (los gates mismos son no-negociables, per ADR-039)

### Negociable por la Máquina (dentro de límites humanos)

Estas actividades pueden ser propuestas y ejecutadas por el agente, sujetas a revisión humana cuando aplique:

- **Descomposición de tareas** — cómo dividir el trabajo dentro del scope definido
- **Enfoque de ejecución** — qué archivos modificar, en qué orden, qué herramientas usar
- **Evaluación de calidad** — verificar si el output cumple los criterios definidos por el humano
- **Selección de herramientas** — qué CLI commands, qué MCP tools
- **Metodología de investigación** — cómo buscar, qué fuentes consultar, cómo triangular

### Compartido (agente propone, humano revisa)

Estas actividades requieren propuesta del agente Y aprobación humana:

- **Planes de implementación** — el agente propone el plan, el humano lo revisa antes de ejecutar
- **Diseños de historias** — el agente propone el diseño, el humano valida
- **Evaluaciones de trabajo significativo** — el agente evalúa, el humano revisa el veredicto
- **Cambios de principios** — como este ADR — el agente puede proponer, pero el humano decide

## Verificación: ¿Preserva las Protecciones Originales?

| Modo de falla original | ¿P1 reformulado lo previene? | Cómo |
|------------------------|------------------------------|------|
| Scope creep del agente | ✓ Sí | "Goals and Boundaries" son propiedad humana. El agente no puede expandirlos. |
| Decisiones arquitectónicas sin supervisión | ✓ Sí | "Boundaries" incluye decisiones irreversibles. Requieren aprobación humana. |
| Dirección estratégica autónoma | ✓ Sí | "Goals" son propiedad humana. El agente no puede redefinir qué se construye. |

## Verificación: ¿Desbloquea Patrones Legítimos?

| Patrón | P1 original | P1 reformulado | Resultado |
|--------|------------|----------------|-----------|
| G13: Evaluación de calidad por LLM | Ambiguo — ¿la máquina "define" calidad? | Ejecución dentro de criterios humanos ✓ | Desbloqueado |
| G3: Loop iterativo de evaluación | Ambiguo — ¿la máquina decide cuándo parar? | Ejecución dentro de threshold humano ✓ | Desbloqueado |
| G2: Rubric scoring por agente | Ambiguo — ¿la máquina "juzga"? | Evaluación dentro de rubric humano ✓ | Desbloqueado |
| Agente redefine scope unilateralmente | ✗ Bloqueado | ✗ Bloqueado | Sin cambio |
| Agente elimina quality gates | ✗ Bloqueado | ✗ Bloqueado | Sin cambio |

## Consecuencias

### Positivas

1. **Honestidad arquitectónica** — P1 refleja cómo RaiSE realmente funciona después de 500+ sesiones
2. **Desbloquea evaluación OSS** — G2 (rubrics) y G3 (eval loops) son OSS-compatible bajo la reformulación
3. **Mejor modelo para Enterprise** — la clasificación Human/Machine/Shared da un framework claro para configurar autonomía por equipo
4. **Preserva la promesa de reliability** — las protecciones originales se mantienen intactas

### Negativas

1. **Comunicación más compleja** — "Humans Define, Machines Execute" es fácil de explicar. La reformulación requiere la tabla de clasificación.
2. **Requiere actualización de documentación** — CLAUDE.md, core.yaml, perspective.md, y cualquier material que cite P1
3. **Riesgo de interpretación laxa** — "Machines Negotiate Execution" podría ser malinterpretado como "machines decide everything within scope." La tabla de clasificación es el antídoto.

### Mitigación del Riesgo

- La tabla de clasificación (Human/Machine/Shared) es parte integral del ADR — no puede citarse P1 reformulado sin ella
- Las protecciones originales se listan explícitamente como no-negociables
- El principio simplificado para comunicación externa puede seguir siendo "Humans Define, Machines Execute" — la reformulación es para gobierno interno del framework

## Alternativas Consideradas

### A: Mantener P1 como está
- Pro: Simple, establecido
- Contra: Inexacto. Bloquea patrones legítimos. Fuerza workarounds que no reconocen lo que ya hacemos.
- **Rechazado:** La evidencia operacional es demasiado fuerte.

### B: Agregar una excepción para evaluación
- Pro: Cambio mínimo — "Humans Define, Machines Execute (except evaluation)"
- Contra: Ad-hoc. No resuelve el problema de fondo (la zona gris de "juicio compartido" va más allá de evaluación).
- **Rechazado:** Parche, no solución.

### C: Eliminar P1 completamente
- Pro: Si ya no es preciso, ¿para qué tenerlo?
- Contra: Las protecciones son reales y necesarias. Sin P1, no hay principio que prevenga scope creep del agente.
- **Rechazado:** Las protecciones deben existir.

## Referencias

- S789.2 research report: `work/epics/e789-anthropic-patterns/stories/s789.2-research.md`
- RaiSE Blueprint: `work/epics/e789-anthropic-patterns/raise-blueprint.md`
- ADR-039: Lifecycle Hooks and Workflow Gates (quality gates son non-negotiable)
- Art.1: Building Effective Agents (evaluator-optimizer pattern)
- Art.2: Effective Harnesses (feature verification, immutable criteria)

---

*Status: Proposed — pendiente de ratificación después de completar E-ANTHROPIC research (S789.3, S789.4 pueden agregar evidencia).*
*Autor: Emilio + Rai, derivado de S789.2 research.*
