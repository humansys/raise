---
id: vision
titulo: "Vision: Project Vision"
work_cycle: project
frequency: once-per-epic
fase_metodologia: 2

prerequisites:
  - project/discovery
template: templates/project/project_vision.md
gate: gates/gate-vision.md
next_kata: project/design

adaptable: true
shuhari:
  shu: "Seguir los 11 pasos exactamente como se describen"
  ha: "Combinar pasos de alineamiento si los stakeholders ya están alineados"
  ri: "Crear kata de Vision específica del dominio (ej: Vision-Microservices, Vision-Monolith)"

version: 2.0.0
---

# Vision: Project Vision

## Propósito

Traducir un PRD aprobado en una Project Vision de alto nivel que alinee objetivos de negocio con decisiones técnicas. Este documento es el puente entre el "qué" (PRD) y el "cómo" (Technical Design).

La Project Vision asegura que el equipo técnico entienda el valor de negocio y que los stakeholders de negocio comprendan las implicaciones técnicas.

> **Nota ADR-010**: "Project Vision" es el artefacto a nivel de proyecto. Para visión a nivel de sistema/solución, ver `solution/vision` kata.

## Contexto

**Cuándo usar:**
- Después de tener un PRD aprobado
- Antes de iniciar el diseño técnico detallado
- Cuando se necesita alinear negocio y tecnología

**Inputs requeridos:**
- PRD aprobado (`governance/projects/{project}/prd.md` or `work/projects/{project}/prd.md` if draft)
- Contexto técnico (stack actual, restricciones, integraciones)

**Output:**
- `governance/projects/{project}/vision.md` - Project Vision estructurada (after gate passes)

## Pasos

### Paso 1: Cargar PRD y Contexto Técnico

Cargar el PRD aprobado y recopilar información del contexto técnico: stack actual, restricciones técnicas, integraciones existentes.

**Verificación:** El PRD existe y hay un resumen claro del contexto técnico.

> **Si no puedes continuar:** PRD no encontrado → Ejecutar `project/discovery` primero. Contexto técnico desconocido → Ejecutar `setup/analyze` para entender el código existente.

### Paso 2: Instanciar Template Project Vision

Crear el archivo `work/projects/{project}/vision.md` basado en el template de Project Vision. After gate passes, promote to `governance/projects/{project}/vision.md`.

**Verificación:** Existe el archivo con todas las secciones del template presentes.

> **Si no puedes continuar:** Template no encontrado → Verificar que existe el template de Project Vision.

### Paso 3: Sintetizar Problem Statement

Reformular el problema de negocio conectándolo con la capacidad técnica faltante. Debe ser más conciso que el PRD y añadir perspectiva técnica.

**Verificación:** El Problem Statement es más conciso que el PRD y añade perspectiva técnica clara.

> **Si no puedes continuar:** Problem Statement técnicamente vago → Revisar con un Arquitecto para identificar el "dolor técnico" subyacente.

### Paso 4: Definir Visión de Alto Nivel

Articular la solución en 2-3 párrafos:
- Valor principal que entrega
- Diferenciadores clave
- Resultados esperados

**Verificación:** Stakeholders de negocio y técnicos pueden entenderlo por igual.

> **Si no puedes continuar:** Visión demasiado técnica → Aplicar la prueba del "elevator pitch" (explicarlo en 30 segundos a alguien no técnico).

### Paso 5: Mapear Alineamiento Estratégico

Crear tabla conectando cada Business Goal del PRD con un Mecanismo Técnico específico.

| Business Goal | Mecanismo Técnico | Métrica |
|---------------|-------------------|---------|
| [Del PRD] | [Cómo se logra técnicamente] | [Cómo se mide] |

**Verificación:** 100% de los goals del PRD tienen un mecanismo técnico asociado.

> **Si no puedes continuar:** Goals sin mecanismo claro → Identificar si falta un requisito en el PRD o una capacidad técnica.

### Paso 6: Documentar Impacto por Stakeholder

Mapear stakeholders del PRD a beneficios técnicos concretos (Expected Benefits).

**Verificación:** La tabla cubre todos los stakeholders con beneficios específicos y medibles.

> **Si no puedes continuar:** Beneficios genéricos → Reformular como acciones: "El usuario podrá [acción] en [tiempo] en lugar de [actual]".

### Paso 7: Definir MVP Scope

Traducir alcance del PRD a categorías técnicas:
- **Must Have (MVP):** 3-5 items máximo
- **Nice to Have:** Mejoras post-MVP
- **Out of Scope:** Explícitamente excluido

**Verificación:** Must Have contiene máximo 3-5 items clave.

> **Si no puedes continuar:** MVP demasiado grande → Preguntar: "¿Si solo pudiéramos entregar UNA cosa, cuál sería?" e iterar desde ahí.

### Paso 8: Establecer Métricas de Éxito Técnicas

Traducir métricas de negocio a métricas técnicas medibles:
- Response time P95
- Error rate
- Throughput
- Availability SLA

**Verificación:** Cada métrica de negocio tiene al menos una métrica técnica medible automáticamente.

> **Si no puedes continuar:** No medibles automáticamente → Definir cómo se instrumentará (logs, APM, dashboards) antes de seguir.

### Paso 9: Documentar Constraints y Assumptions

Consolidar restricciones y supuestos:
- Restricciones de negocio (budget, timeline, compliance)
- Restricciones técnicas (stack, infraestructura, dependencias)
- Supuestos explícitos

**Verificación:** Las restricciones son específicas (ej: "cumplimiento SOC2 Type II") y no genéricas.

> **Si no puedes continuar:** Constraints vagas → Preguntar: "¿Qué pasaría específicamente si no se cumple?"

### Paso 10: Identificar Componentes de Alto Nivel

Esbozar servicios/módulos principales:
- 3-7 componentes máximo
- Integraciones externas
- Flujos de alto nivel

**Verificación:** Existe una lista O diagrama de 3-7 componentes (no más de 7).

> **Si no puedes continuar:** Demasiado detalle → Abstraer hasta tener máximo 7 componentes. El detalle va en Technical Design.

### Paso 11: Validar con Stakeholders

Presentar la Project Vision para validación:
- Revisión con stakeholders de negocio (alineamiento)
- Revisión con equipo técnico (factibilidad)
- Documentar trade-offs acordados

**Verificación:** La visión refleja necesidades de negocio y es técnicamente factible.

> **Si no puedes continuar:** Desacuerdo negocio vs técnico → Facilitar sesión conjunta y documentar trade-offs explícitamente.

## Output

- **Artefacto:** Project Vision
- **Ubicación (draft):** `work/projects/{project}/vision.md`
- **Ubicación (approved):** `governance/projects/{project}/vision.md`
- **Gate:** `gates/gate-vision.md`
- **Siguiente kata:** `project/design`

## Notas

### Nivel de Detalle

Mantener el documento a nivel de "boxes and arrows" - no diseño detallado. El objetivo es alineamiento, no especificación técnica completa.

### Trazabilidad

Todas las decisiones técnicas DEBEN justificar un objetivo de negocio. Si una decisión técnica no tiene justificación de negocio, cuestionar si es necesaria.

## Referencias

- Gate de validación: `gates/gate-vision.md`
- Template: `templates/project/project_vision.md`
- Kata previa: `project/discovery`
- ADR: `dev/decisions/framework/adr-010-three-level-artifact-hierarchy.md`
