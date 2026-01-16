---
id: flujo-05-backlog-creation
nivel: flujo
titulo: "Backlog Creation: De Tech Design a User Stories"
audience: intermediate
template_asociado: templates/backlog/user_story.md
validation_gate: gates/gate-backlog.md
prerequisites:
  - flujo-03-tech-design
fase_metodologia: 4
tags: [backlog, user-stories, priorizacion, fase-4]
version: 1.0.0
---

# Backlog Creation: De Tech Design a User Stories

## Propósito

Descomponer el Tech Design en Features y User Stories priorizadas que puedan ser planificadas e implementadas incrementalmente. Este proceso traduce arquitectura técnica en unidades de trabajo entregables.

Esta kata responde a la pregunta: **¿Cómo fluye el diseño técnico hacia un backlog priorizado y ejecutable?**

## Contexto

**Cuándo usar:**
- Después de que Gate-Design ha sido aprobado
- Cuando se necesita crear el backlog para un proyecto/épica
- Para descomponer diseño en incrementos entregables

**Inputs requeridos:**
- Tech Design aprobado (output de `flujo-03-tech-design`)
- PRD y Solution Vision como referencia
- Criterios de priorización del proyecto

**Output:** Backlog de User Stories priorizadas

## Pre-condiciones

- [ ] Gate-Design aprobado
- [ ] Tech Design disponible en `.raise/specs/{proyecto}-tech-design.md`
- [ ] Product Owner disponible para priorización
- [ ] Criterios de valor de negocio definidos

---

## Pasos

### Paso 1: Cargar Tech Design y Contexto

Cargar todos los documentos relevantes:
- Tech Design (fuente principal)
- PRD (requisitos originales)
- Solution Vision (metas de negocio)

Identificar:
- Componentes a implementar
- Funcionalidades descritas
- MVP scope definido

**Verificación:** Existe resumen de componentes y funcionalidades principales del Tech Design.

> **Si no puedes continuar:** Tech Design incompleto → Regresar a `flujo-03-tech-design` para completar secciones faltantes.

---

### Paso 2: Identificar Features/Épicas

Agrupar la funcionalidad en Features de alto nivel:
- Cada Feature entrega valor independiente al usuario
- Features son deployables por separado
- Features tienen tamaño similar (1-4 semanas de trabajo)

**Verificación:** Lista de 3-7 Features para el proyecto, cada una con nombre descriptivo y resumen de valor.

> **Si no puedes continuar:** Features muy grandes → Subdividir hasta que cada Feature sea entregable en 2-4 semanas. Features muy pequeñas → Combinar features relacionadas.

---

### Paso 3: Priorizar Features

Aplicar matriz de priorización:

| Feature | Valor de Negocio (1-5) | Complejidad (1-5) | Riesgo Técnico (1-5) | Score |
|---------|----------------------|-------------------|---------------------|-------|
| Feature A | 5 | 3 | 2 | 5/3=1.67 |
| Feature B | 3 | 5 | 4 | 3/5=0.60 |

**Score = Valor / Complejidad** (mayor es mejor)

Considerar también:
- Dependencias entre features
- MVP scope (must-have primero)
- Riesgos técnicos (abordar temprano)

**Verificación:** Features ordenadas por prioridad con justificación. MVP claramente identificado.

> **Si no puedes continuar:** Priorización no clara → Sesión con Product Owner para establecer valor de negocio de cada feature.

---

### Paso 4: Descomponer Feature en User Stories

Para cada Feature, crear User Stories que:
- Siguen formato: "Como [rol], quiero [acción], para [beneficio]"
- Son independientes (pueden entregarse por separado)
- Son testeables (criterios de aceptación claros)
- Caben en un sprint (1-5 días de trabajo)

**Verificación:** Cada Feature tiene 3-8 User Stories. Cada US tiene título, descripción y rol identificado.

> **Si no puedes continuar:** Stories muy grandes → Aplicar técnica INVEST. Si una US no es "Small", subdividir por escenarios o por datos.

---

### Paso 5: Escribir Criterios de Aceptación

Para cada User Story, escribir criterios en formato BDD:

```gherkin
Escenario: [Nombre del escenario]
  Dado que [contexto inicial]
  Cuando [acción del usuario]
  Entonces [resultado esperado]
```

Cubrir:
- Happy path (escenario principal)
- Validaciones y errores
- Edge cases importantes

**Verificación:** Cada US tiene al menos 2-3 escenarios. Los escenarios son específicos (datos concretos, no genéricos).

> **Si no puedes continuar:** Criterios vagos → Para cada criterio, preguntarse "¿cómo escribiría el test automatizado?" Si no es claro, refinar.

---

### Paso 6: Añadir Detalles Técnicos

Enriquecer cada User Story con contexto técnico del Tech Design:
- Componentes afectados
- Endpoints de API relacionados
- Cambios de modelo de datos
- Dependencias técnicas

**Verificación:** Cada US tiene sección "Detalles Técnicos" que conecta con el Tech Design.

> **Si no puedes continuar:** Conexión con Tech Design no clara → Trazar cada US a los componentes del Tech Design. Si no mapea, revisar si la US está en scope.

---

### Paso 7: Estimar User Stories

Asignar estimación a cada US:
- Story Points (Fibonacci: 1, 2, 3, 5, 8, 13)
- O T-shirt sizes (XS, S, M, L, XL)

Considerar:
- Complejidad técnica
- Incertidumbre
- Dependencias externas

**Verificación:** Todas las US tienen estimación. Ninguna US es > 8 puntos (si lo es, subdividir).

> **Si no puedes continuar:** Estimaciones muy dispares → Sesión de planning poker para calibrar estimaciones del equipo.

---

### Paso 8: Ordenar Backlog

Ordenar las User Stories considerando:
1. Prioridad de la Feature padre
2. Dependencias técnicas entre stories
3. Valor de negocio individual
4. Reducción de riesgo temprano

**Verificación:** Lista ordenada de US donde cada story tiene sus dependencias satisfechas cuando llega su turno.

> **Si no puedes continuar:** Dependencias circulares → Revisar diseño. Puede requerir refactor de cómo se dividieron las stories.

---

### Paso 9: Identificar MVP Slice

Marcar las US mínimas para un release funcional:
- ¿Cuál es el conjunto mínimo que entrega valor?
- ¿Qué se puede diferir sin perder el core value?

**Verificación:** MVP slice identificado, representa ≤50% del backlog total y entrega el valor core.

> **Si no puedes continuar:** MVP demasiado grande → Aplicar "¿Qué puedo quitar y aún entregar valor?" iterativamente hasta llegar a 30-50% del backlog.

---

### Paso 10: Validar con Product Owner

Presentar el backlog completo para aprobación:
1. Features y su priorización
2. User Stories por feature
3. MVP slice propuesto
4. Estimaciones totales

**Verificación:** Product Owner aprueba el backlog, confirma prioridades, y valida el MVP slice.

> **Si no puedes continuar:** Desacuerdo en prioridades → Facilitar sesión de negociación. Documentar trade-offs y decisiones.

---

## Output

**Artefactos producidos:**
1. **Feature Prioritization Matrix** (`.raise/specs/{proyecto}-features.md`)
2. **User Stories individuales** (`.raise/specs/{proyecto}/US-{id}.md`)

**Formato de User Story:**
```markdown
---
id: US-001
feature: [Feature padre]
priority: P1
story_points: 5
status: ready
---

# US-001: [Título descriptivo]

**Como** [rol]
**Quiero** [acción]
**Para** [beneficio]

## Criterios de Aceptación

```gherkin
Escenario: Happy path
  Dado que ...
  Cuando ...
  Entonces ...
```

## Detalles Técnicos

**Componentes:**
- API: `/endpoint`
- Service: `UserService`
- Repository: `UserRepository`

**Dependencias:**
- US-000 (debe completarse antes)

## Notas
[Consideraciones adicionales]
```

**Siguiente paso:**
1. Ejecutar `gates/gate-backlog.md` para validar
2. Para cada US, ejecutar `flujo-04-implementation-plan`

---

## Notas

### INVEST para User Stories
- **I**ndependent: Puede entregarse sola
- **N**egotiable: Detalle negociable hasta planificación
- **V**aluable: Entrega valor al usuario
- **E**stimable: Se puede estimar con confianza
- **S**mall: Cabe en un sprint
- **T**estable: Criterios claros de done

### Granularidad
- **Épica**: 1-3 meses de trabajo → Features
- **Feature**: 1-4 semanas de trabajo → User Stories
- **User Story**: 1-5 días de trabajo → Tasks (en flujo-04)

---

## Referencias

- Template: [`templates/backlog/user_story.md`](../../templates/backlog/user_story.md)
- Prerequisito: [`flujo-03-tech-design`](./03-tech-design.md)
- Siguiente kata: [`flujo-04-implementation-plan`](./04-implementation-plan.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 4
