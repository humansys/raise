# Problem Brief: Agent-Orchestrated Workflow

**Date:** 2026-03-01
**Stakeholder:** Emilio (developer using RaiSE daily)
**Shaped by:** Emilio + Rai (SES-304)

---

## 1. Dominio

Experiencia de usuario + Autonomía del agente. El modelo de interacción actual no escala porque el humano opera como dispatcher en lugar de como decisor.

## 2. Stakeholder primario

El desarrollador que usa RaiSE día a día (Emilio, equipo Kurigage).

## 3. Estado actual (gap)

El desarrollador no puede **delegar el flujo de trabajo completo al agente** porque **el modelo actual requiere que el humano orqueste cada paso del proceso manualmente**, reduciendo la interacción a comandos repetitivos en lugar de decisiones de valor.

### Vertientes observadas

1. **Skills desconectados** — no usan backlog (`rai backlog`) ni documentación (`rai docs`), aunque ya existen CLIs que abstraen el backend
2. **Discovery/onboard demasiado manual** — demasiados pasos donde el humano no sabe qué hacer pero el agente sí
3. **Orquestación invertida** — el humano dice "qué sigue" cuando debería ser el agente quien orqueste y solo pida HITL donde agrega valor

## 4. Raíz (3 Whys)

1. **¿Por qué el humano orquesta manualmente?** — Era una premisa de diseño original: el desarrollador quería permanecer en control del flujo. Después de 300+ sesiones, la confianza en el agente está establecida.
2. **¿Por qué los skills no pueden tomar el control?** — No se ha intentado resolver ese problema hasta ahora.
3. **¿Qué lo impide estructuralmente?** — Nada de fondo. La barrera es de diseño: los skills se diseñaron como unidades aisladas invocadas por el humano, no como pasos de un flujo orquestado por el agente. Falta el modelo de orquestación y los acuerdos de HITL que permitan al agente fluir y solo involucrar al humano donde agrega valor.

**Raíz síntesis:** No hay impedimento técnico fundamental. Falta el modelo de orquestación agente-driven con HITL parametrizado.

## 5. Early Signal (4 semanas)

El desarrollador dice el objetivo ("quiero implementar esta story") y Rai ejecuta el ciclo completo, involucrando al humano solo en decisiones y validaciones.

## 6. Hipótesis (SAFe)

> Si transformamos el modelo de interacción de RaiSE de "humano orquesta, agente ejecuta pasos" a "agente orquesta el flujo completo con HITL en decisiones y gates", entonces el desarrollador podrá declarar objetivos y delegar la ejecución del ciclo al agente, medido por la reducción de comandos manuales por sesión y la capacidad del agente de completar un ciclo story-level sin intervención de dispatch.

---

## Elementos de diseño mencionados

- `rai backlog` CLI como interfaz al backlog (ya existe)
- `rai docs` CLI como interfaz a documentación de governance (próximamente)
- Subagentes para offloading de tareas mecánicas (token economy)
- Parámetros pre-acordados de HITL (cuándo involucrar al humano)
- Alta densidad semántica en outputs del CLI para facilitar al agente
- Modelo de conversación long-running por épica o ciclo de trabajo

## Next

→ `/rai-epic-design` (este brief se carga en Step 0.7)
