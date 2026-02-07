---
id: backlog
titulo: "Backlog: Product Backlog Creation"
work_cycle: project
frequency: once-per-epic
fase_metodologia: 4

prerequisites:
  - project/design
template: templates/backlog/user_story.md
gate: gates/gate-backlog.md
next_kata: feature/stories

adaptable: true
shuhari:
  shu: "Crear todas las user stories con formato estándar"
  ha: "Agrupar stories relacionadas en features coherentes"
  ri: "Crear kata de Backlog específica del dominio"

version: 1.0.0
---

# Backlog: Product Backlog Creation

## Propósito

Transformar el Technical Design en un backlog de user stories priorizadas y estimadas, listas para implementación. El backlog es el contrato entre producto y desarrollo.

## Contexto

**Cuándo usar:**
- Después de tener un Technical Design aprobado
- Antes de iniciar la implementación de features
- Cuando se necesita planificar sprints

**Inputs requeridos:**
- Technical Design aprobado (`governance/design.md`)
- PRD para trazabilidad de requisitos

**Output:**
- `governance/backlog.md` - Backlog estructurado

## Pasos

### Paso 1: Identificar Features

Agrupar requisitos del PRD en 3-7 features lógicas.

**Verificación:** Features identificadas con valor claro para el usuario.

> **Si no puedes continuar:** Requisitos dispersos → Agrupar por dominio o user journey.

### Paso 2: Priorizar Features

Ordenar features por valor de negocio:
- MoSCoW o WSJF
- Dependencias técnicas
- Quick wins vs long-term

**Verificación:** Orden definido con justificación.

> **Si no puedes continuar:** Prioridades iguales → Usar matriz valor/esfuerzo.

### Paso 3: Identificar MVP

Marcar subset mínimo para entregar valor:
- MVP ≤50% del backlog total
- Funcionalidad end-to-end

**Verificación:** MVP claramente identificado.

> **Si no puedes continuar:** MVP muy grande → Preguntar: "¿Qué es lo mínimo para validar la hipótesis?"

### Paso 4: Crear User Stories

Para cada feature, crear stories con formato:
- "Como [rol], quiero [acción], para [beneficio]"
- Criterios de aceptación BDD

**Verificación:** Todas las stories siguen formato estándar.

> **Si no puedes continuar:** Stories técnicas → Reformular desde perspectiva del usuario.

### Paso 5: Definir Criterios BDD

Para cada story, crear ≥2 escenarios:
- Given [contexto]
- When [acción]
- Then [resultado]

**Verificación:** Cada story tiene ≥2 criterios BDD.

> **Si no puedes continuar:** Criterios vagos → Preguntar: "¿Cómo sabemos que está terminado?"

### Paso 6: Estimar Stories

Asignar story points usando Fibonacci:
- Complejidad
- Esfuerzo
- Incertidumbre

**Verificación:** Todas las stories tienen estimación.

> **Si no puedes continuar:** Estimaciones inconsistentes → Usar planning poker.

### Paso 7: Validar con Product Owner

Revisar backlog completo:
- Priorización correcta
- MVP adecuado
- Stories claras

**Verificación:** Product Owner aprueba priorización.

> **Si no puedes continuar:** Desacuerdo en prioridades → Facilitar sesión de refinamiento.

## Output

- **Artefacto:** Product Backlog
- **Ubicación:** `governance/backlog.md`
- **Gate:** `gates/gate-backlog.md`
- **Siguiente kata:** `feature/stories`

## Referencias

- Gate de validación: `gates/gate-backlog.md`
- Template: `templates/backlog/user_story.md`
- INVEST criteria: Independent, Negotiable, Valuable, Estimable, Small, Testable
