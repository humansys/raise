---
story: RAISE-200
title: "/problem-shape — Guided problem definition at portfolio level"
size: M
module: mod-skills
layer: lyr-domain
jira: https://humansys.atlassian.net/browse/RAISE-200
---

## What & Why

**Problem:** El pipeline de RaiSE asume que quien invoca `/rai-epic-design` ya tiene un problema bien definido. En la práctica (observado directamente en la conversación pre-demo con Coppel), los stakeholders llegan con *soluciones* disfrazadas de requerimientos. El epic-design no tiene gate para detectar esto.

**Value:** Un stakeholder no técnico puede pasar de "tenemos un problema de visibilidad" a una hipótesis SAFe-compatible en ≤10 minutos. El output alimenta `/rai-epic-design` con un Problem Brief estructurado, eliminando el gap entre portafolio e implementación.

## Architectural Context

| Field | Value |
|-------|-------|
| Module | `mod-skills` |
| Domain | `bc-skills` |
| Layer | `lyr-domain` |
| Dependencies | `mod-output`, `mod-cli` |

**Constraints aplicables (MUST):** guardrail-must-arch-001 (engine/content separation — skill content en `.claude/skills/`, no lógica en CLI), guardrail-must-arch-002 (Pydantic donde haya schemas — no aplica: este deliverable es solo SKILL.md).

## Approach

Dos entregables:

1. **`.claude/skills/problem-shape/SKILL.md`** — nuevo skill conversacional con 6 pasos + anti-solution gate + output Problem Brief
2. **`.claude/skills/rai-epic-design/SKILL.md`** — añadir Step 0.7 que carga el Problem Brief si existe

**Integración rai-cli:**
- Gate de inicio: `rai session start --project "$(pwd)" --context` — extrae nombre del proyecto del bundle. Si no puede ejecutarse, el skill pide el nombre explícitamente. **MUST NOT ejecutar sin nombre de proyecto.**
- Output: escritura a `work/problem-briefs/{slug-proyecto}-{YYYY-MM-DD}.md` vía Write tool

**Anti-solution gate (Step 3):**
- El agente detecta lenguaje de solución: "queremos construir", "necesitamos implementar", "vamos a desarrollar", "la solución es"
- Si detecta → desafía *una vez*: "Eso es una solución, no un problema. ¿Qué pasa hoy sin eso? ¿Qué no pueden hacer?"
- Si segunda respuesta también es solución → acepta con nota en el Brief: `⚠ Estado actual podría ser parcialmente solución-shaped`
- **NEVER** desafiar dos veces — genera fricción innecesaria con el stakeholder

**Lite mode:** Diferido a v2 — flujo completo siempre en v1.

**Components affected:**

| Component | Change | Detail |
|-----------|--------|--------|
| `.claude/skills/problem-shape/SKILL.md` | create | Skill completo: 6 pasos, gate, output |
| `.claude/skills/rai-epic-design/SKILL.md` | modify | Step 0.7: Load Problem Brief si existe |
| `work/problem-briefs/.gitkeep` | create | Ya existe (scope commit) |

## Examples

### Invocación y flujo

```
Usuario: /problem-shape

Rai: [Step 0 — carga contexto del proyecto vía rai session start --context]
     Proyecto: Kurigage Jumpstart. ¡Empecemos!

     Step 1 — APUESTA
     ¿Qué tipo de problema crees que estás resolviendo?
     A) Velocidad de entrega
     B) Calidad / retrabajo
     C) Visibilidad / control
     D) Otro

Usuario: C) Visibilidad / control

Rai: Step 2 — PARA QUIÉN
     ¿Quién experimenta este problema directamente?
     A) El equipo de desarrollo
     B) El área de negocio
     C) Portafolio / liderazgo
     D) El cliente final

Usuario: C) Portafolio / liderazgo

Rai: Step 3 — ESTADO ACTUAL
     Completa: [quién] no puede [hacer qué] porque [razón]

Usuario: "Queremos construir un dashboard de métricas"

Rai: Eso es una solución, no un problema.
     ¿Qué no puede hacer hoy portafolio/liderazgo? ¿Qué consecuencia tiene eso?

Usuario: "Liderazgo no puede saber si un proyecto va bien o mal hasta que ya es tarde"

Rai: Perfecto. Step 4 — 3 WHYS
     ¿Por qué no pueden saberlo?
     ...
```

### Problem Brief output

```markdown
# Problem Brief — Kurigage Jumpstart
> Generado: 2026-02-19 | Duración: 8 min | Skill: /problem-shape v1.0

## Dominio / Tipo de apuesta
Visibilidad / control

## Stakeholder afectado
Portafolio / liderazgo

## Estado actual
Liderazgo no puede detectar proyectos en riesgo hasta que ya es tarde,
porque no existe una señal de alerta temprana que no requiera escalación manual.

## Problema raíz (3 Whys)
1. ¿Por qué no pueden detectarlo? → No hay indicadores visibles hasta el sprint review
2. ¿Por qué no hay indicadores? → El equipo reporta a demanda, no proactivamente
3. ¿Por qué reporta a demanda? → No hay proceso ni herramienta que genere señal automática

**Raíz identificada:** Ausencia de señal automática de salud de proyecto.

## Early signal (4 semanas)
Una métrica que mejora — % de proyectos con estado actualizado automáticamente ≥80%

## Hipótesis
Si liderazgo recibe señal automática de salud por proyecto cada semana,
entonces detectará proyectos en riesgo en ≤48h (vs. semanas actuales)
para portafolio/liderazgo,
medido por: tiempo-promedio-de-detección-de-riesgo y % de escalaciones reactivas.

---
**Next:** `/rai-epic-design` — usa este Brief como input para Step 1 (Objective)
```

### Integración en rai-epic-design (Step 0.7)

```bash
# Step 0.7: Load Problem Brief (if exists)
ls work/problem-briefs/*.md 2>/dev/null | tail -1
```

Si existe → leerlo y usarlo como input directo para Step 1 (Objective) en lugar de solicitarlo verbalmente.

## Acceptance Criteria

**MUST:**
- [ ] Gate: `rai session start --context` ejecutado al inicio — si falla, pide nombre del proyecto explícitamente antes de continuar
- [ ] 6 pasos completos en orden: APUESTA → PARA QUIÉN → ESTADO ACTUAL → 3 WHYS → EARLY SIGNAL → HIPÓTESIS
- [ ] Anti-solution gate en Step 3: desafía UNA VEZ con curiosidad, no juicio. Acepta en segunda instancia con nota `⚠`
- [ ] Step 4 ejecuta exactamente 3 Why questions y nombra la raíz identificada explícitamente
- [ ] Step 6 produce hipótesis SAFe completa (If/Then/For/Measured-by) — el agente propone, el usuario corrige
- [ ] Problem Brief guardado en `work/problem-briefs/{slug}-{YYYY-MM-DD}.md`
- [ ] `/rai-epic-design` tiene Step 0.7 que detecta y carga Problem Brief si existe

**SHOULD:**
- [ ] Duración total ≤10 minutos en flujo estándar
- [ ] Problem Brief incluye sección "Next: /rai-epic-design" con ruta al archivo

**MUST NOT:**
- [ ] Desafiar el estado actual más de una vez en Step 3
- [ ] Producir un Problem Brief con solución en "Estado Actual" sin nota `⚠`
- [ ] Ejecutar sin nombre de proyecto disponible

## Patrones aplicables

- **PAT-E-263:** Research before design for UX-facing features — investigación ya realizada (RES-problem-definition-frameworks: Cagan, Gothelf, Torres, Adzic)
- **PAT-E-186:** Design is not optional — este design.md es la prueba
- **ADR-024:** CLI assembles context, skill interprets — `rai session start --context` es el plumbing, el skill hace la inferencia

## References

- Research base: `work/research/RES-problem-definition-frameworks/`
- Confluence: Problem Definition Frameworks research report
- Skill referencia (conversacional): `.claude/skills/rai-welcome/SKILL.md`
- Skill que modifica: `.claude/skills/rai-epic-design/SKILL.md`
- Output dir: `work/problem-briefs/`
