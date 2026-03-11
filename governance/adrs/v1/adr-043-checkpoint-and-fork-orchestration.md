---
id: ADR-043
title: "Checkpoint & Fork — Quality-Preserving Skill Orchestration"
date: "2026-03-03"
status: "Proposed"
epic: "E353 / RAISE-398"
relates_to:
  - ADR-005 (skills format)
  - ADR-040 (skill contract)
  - "work/research/orchestration-quality/report.md"
---

# ADR-043: Checkpoint & Fork — Quality-Preserving Skill Orchestration

## Contexto

Los orchestrators (`rai-story-run`, `rai-epic-run`) ejecutan 6-8 skills secuencialmente en un solo contexto conversacional. Medición real: quality review en orchestrator produjo 2,196 chars / 1 tool call vs 10,064 chars / 28 tool calls standalone — un **gap de 4.6x**.

Causa raíz: el contexto se satura (~60% capacidad) para la fase 5 de 8. La calidad de inference se degrada 15-25% con contexto saturado (evidencia: SFEIR research, practitioner reports).

Las fuerzas en tensión son: (1) los orchestrators deben coordinar múltiples fases secuenciales, pero (2) cada fase necesita contexto fresco para producir output de calidad, y (3) los subagentes no pueden spawner otros subagentes (constraint de Claude Code).

## Decisión

**Adoptar el patrón Checkpoint & Fork: el orchestrator es un coordinador ligero que forkea fases pesadas a subagentes con contexto fresco. Los artefactos en disco son el contrato explícito entre fases.**

### Reglas del patrón

1. **Artifacts are the API:** Fase N escribe archivos a disco. Fase N+1 lee archivos de disco. No hay paso implícito de contexto conversacional.
2. **Orchestrator is thin:** Solo phase detection, delegation gates, progress tracking. No razonamiento pesado.
3. **Skills are self-contained:** Cada skill lee sus inputs de disco. Funciona idénticamente standalone o forkeado.
4. **Summary protocol:** Cada fase forkeada retorna un resumen estructurado (no raw output) para mantener el contexto del orchestrator ligero.

### Aplicación por nivel

| Orchestrator | Runs in | Fork unit | Mechanism | Subagent depth |
|-------------|---------|-----------|-----------|----------------|
| `rai-story-run` | Main thread (always) | Per heavy phase | Agent tool | 1 (main → phase) |
| `rai-epic-run` | Main thread | Delegates to story-run | Skill tool (inline) | 0 (story-run inherits main thread) |

**Regla crítica:** `rai-epic-run` invoca `rai-story-run` inline en el main thread (via Skill tool), NO como subagente. Esto permite que story-run forkee sus fases pesadas. Forkear story-run como subagente lo degradaría a ejecución inline sin forks — exactamente el problema que queremos eliminar. No operamos en niveles de calidad conocidamente inferiores.

### Fases clasificadas

**Todas las fases fork.** El orchestrator es un coordinador puro — nunca ejecuta lógica de skill directamente. Esto mantiene la terminal limpia (output del subagente contenido) y el contexto del orchestrator mínimo.

| Phase | Classification | Rationale |
|-------|---------------|-----------|
| start | Fork | Branch + scope commit. Fork for clean terminal output. |
| design | Fork | Creative reasoning, reads scope, writes design.md |
| plan | Fork | Decomposition, reads design.md, writes plan.md |
| implement | Fork | Code generation, TDD, reads plan.md |
| AR | Fork | Architecture analysis, reads all prior artifacts |
| QR | Fork | Quality analysis, reads all prior artifacts |
| review | Fork | Retrospective synthesis, reads all artifacts |
| close | Fork | Merge + cleanup. Fork for clean terminal output. |

## Consecuencias

| Tipo | Impacto |
|------|---------|
| Positivo | Contexto fresco para cada fase pesada — elimina degradación por saturación |
| Positivo | Calidad idéntica standalone vs orchestrated (mismo SKILL.md, mismos inputs) |
| Positivo | Orchestrator se mantiene ligero — solo lee resúmenes entre fases |
| Positivo | Usa mecanismos probados de Claude Code (Agent tool), no infraestructura custom |
| Negativo | Subagente no ve historial conversacional de fases previas (by design) |
| Negativo | Latencia adicional ~150-250ms por fork (negligible vs quality gain) |
| Negativo | Main thread acumula resúmenes entre stories en epic-run (mitigado: orchestrator thin, solo resúmenes) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| `context: fork` en frontmatter de cada skill | No confirmado que funcione con invocación via Skill tool; Agent tool es mecanismo probado |
| Custom agents (`.claude/agents/`) | Infraestructura adicional innecesaria — Agent tool logra lo mismo sin setup |
| Agent Teams | Experimental, overkill para cadenas secuenciales |
| Document & Clear (checkpoint + reset manual) | Requiere que el usuario ejecute /clear manualmente — no automatizable desde skill |

---

<details>
<summary><strong>Referencias</strong></summary>

- Research report: `work/research/orchestration-quality/report.md`
- Evidence catalog: `work/research/orchestration-quality/evidence-catalog.md`
- SFEIR context degradation study (Source 3 in evidence catalog)
- Claude Code Agent tool documentation (Source 1 in evidence catalog)

</details>
