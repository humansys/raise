---
id: flujo-04-implementation-plan
nivel: flujo
titulo: "Implementation Plan: De User Story a Plan Detallado"
audience: beginner
template_asociado: null
validation_gate: gates/gate-plan.md
prerequisites:
  - flujo-05-backlog-creation
fase_metodologia: 5
tags: [planning, implementacion, tareas, fase-5]
version: 1.0.0
---

# Implementation Plan: De User Story a Plan Detallado

## Propósito

Transformar una User Story (o conjunto de stories) en un Plan de Implementación paso a paso que guíe la ejecución determinista por el agente de desarrollo. Este es el **kata core** del sistema RaiSE: toda implementación pasa por aquí.

Esta kata responde a la pregunta: **¿Cómo fluye una User Story hacia un plan de implementación ejecutable?**

> ⚠️ **Regla fundamental:** Las katas no se ejecutan directamente. Siempre se crea un Plan de Implementación específico para el contexto usando esta kata.

## Contexto

**Cuándo usar:**
- Antes de implementar cualquier User Story
- Cuando se necesita planificación determinista para el agente
- Para descomponer trabajo complejo en pasos atómicos

**Inputs requeridos:**
- User Story con criterios de aceptación (de `flujo-05-backlog-creation`)
- Tech Design como referencia arquitectónica
- Guardrails aplicables al proyecto

**Output:** Implementation Plan documento con tareas atómicas y verificables

## Pre-condiciones

- [ ] User Story existe con criterios de aceptación en formato BDD
- [ ] Tech Design disponible para referencia
- [ ] Guardrails del proyecto identificados
- [ ] Ambiente de desarrollo listo

---

## Pasos

### Paso 1: Cargar Contexto de la User Story

Cargar y comprender la User Story completa:
- Título y descripción
- Criterios de aceptación (Dado/Cuando/Entonces)
- Dependencias y relaciones
- Referencias al Tech Design

**Verificación:** El Orquestador puede explicar en una oración qué valor entrega esta User Story al usuario final.

> **Si no puedes continuar:** User Story no clara → Solicitar clarificación al Product Owner antes de planificar. No planificar sobre ambigüedad.

---

### Paso 2: Identificar Componentes Afectados

Mapear la User Story a los componentes del Tech Design:
- ¿Qué capas se modifican? (API, Service, Repository, DB)
- ¿Hay componentes nuevos o solo modificaciones?
- ¿Qué integraciones se tocan?

**Verificación:** Lista de componentes afectados con indicación de "nuevo" o "modificar".

> **Si no puedes continuar:** Componentes no claros → Revisar Tech Design. Si no mapea, la User Story puede requerir diseño adicional antes de planificar.

---

### Paso 3: Identificar Guardrails Aplicables

Determinar qué guardrails del proyecto aplican:
- Guardrails de arquitectura (capas, dependencias)
- Guardrails de código (naming, estructura)
- Guardrails de testing (cobertura, tipos)
- Guardrails de seguridad

**Verificación:** Lista de IDs de guardrails que el agente debe seguir durante implementación.

> **Si no puedes continuar:** Guardrails no claros → Revisar `.cursor/rules/` o equivalente. Si no hay guardrails, documentar como riesgo.

---

### Paso 4: Descomponer en Tareas Atómicas

Crear lista de tareas que:
- Son atómicas (una sola responsabilidad)
- Son verificables (criterio de done claro)
- Están ordenadas por dependencia
- Son ejecutables por el agente

Formato por tarea:
```markdown
### Tarea N: [Nombre descriptivo]

**Componente:** [Qué se modifica]
**Acción:** [Crear | Modificar | Eliminar]
**Guardrails:** [IDs aplicables]

**Descripción:**
[Qué hacer específicamente]

**Criterio de Verificación:**
[Cómo saber que está completo]

**Dependencias:**
- Tarea X (debe completarse antes)
```

**Verificación:** Cada tarea puede completarse en una sesión de trabajo (< 2 horas). Si requiere más, subdividir.

> **Si no puedes continuar:** Tareas demasiado grandes → Aplicar "Si puedo explicar el verificación en una oración, la tarea es atómica". Subdividir las que no cumplen.

---

### Paso 5: Ordenar por Dependencia

Establecer orden de ejecución:
1. Primero: tareas sin dependencias (fundaciones)
2. Después: tareas que dependen de las anteriores
3. Identificar tareas paralelizables

**Verificación:** Existe diagrama o lista ordenada donde cada tarea tiene sus dependencias satisfechas cuando llega su turno.

> **Si no puedes continuar:** Dependencias circulares → Hay un problema de diseño. Revisar la descomposición y eliminar el ciclo.

---

### Paso 6: Añadir Tareas de Testing

Para cada tarea de implementación, considerar:
- ¿Requiere unit test?
- ¿Requiere integration test?
- ¿Modifica tests existentes?

Añadir tareas de testing explícitas siguiendo TDD cuando sea apropiado.

**Verificación:** Cobertura de testing definida. Las tareas de test están en el orden correcto (antes o junto con implementación).

> **Si no puedes continuar:** Sin estrategia de testing → Mínimo: lógica de negocio tiene unit tests, APIs tienen integration tests.

---

### Paso 7: Incluir Pasos de Verificación

Después de cada grupo lógico de tareas, añadir paso de verificación:
- Ejecutar tests
- Verificar manualmente (si aplica)
- Validar contra criterios de aceptación

**Verificación:** Hay al menos un paso de verificación cada 3-5 tareas de implementación.

> **Si no puedes continuar:** Verificaciones muy espaciadas → Añadir verificaciones intermedias para detectar problemas temprano (Jidoka).

---

### Paso 8: Documentar Rollback/Recovery

Para tareas de riesgo, documentar:
- Qué puede salir mal
- Cómo revertir si falla
- Cómo recuperarse

**Verificación:** Tareas que modifican datos o infraestructura tienen plan de rollback.

> **Si no puedes continuar:** Sin plan de rollback → Para tareas de alto riesgo, añadir paso previo de backup/snapshot.

---

### Paso 9: Estimar y Validar Scope

Revisar el plan completo:
- ¿El esfuerzo total es razonable para la User Story?
- ¿Hay scope creep respecto a los criterios de aceptación?
- ¿Todas las tareas contribuyen al objetivo?

**Verificación:** El plan implementa exactamente los criterios de aceptación de la User Story, ni más ni menos.

> **Si no puedes continuar:** Scope creep detectado → Separar tareas que no son estrictamente necesarias para los AC. Moverlas a User Story futura.

---

### Paso 10: Revisión con Orquestador

Presentar el plan al Orquestador para validación:
1. Walkthrough de tareas
2. Confirmar entendimiento correcto
3. Ajustar según feedback
4. Obtener aprobación para ejecutar

**Verificación:** Orquestador aprueba el plan explícitamente y confirma que puede comenzar la ejecución.

> **Si no puedes continuar:** Orquestador tiene dudas → Resolver cada duda antes de comenzar. No ejecutar sobre incertidumbre.

---

## Output

**Artefacto producido:** Implementation Plan

**Estructura del documento:**
```markdown
# Implementation Plan: [Título de User Story]

**User Story:** [ID y link]
**Fecha:** YYYY-MM-DD
**Autor:** [Orquestador + Agente]

## Contexto
[Resumen de la User Story y su valor]

## Componentes Afectados
- [ ] Componente A (modificar)
- [ ] Componente B (crear)

## Guardrails Aplicables
- guard-001, guard-002, ...

## Tareas

### Fase 1: [Nombre]
- [ ] Tarea 1.1: ...
- [ ] Tarea 1.2: ...
- [ ] **Verificación**: ...

### Fase 2: [Nombre]
- [ ] Tarea 2.1: ...

## Criterios de Aceptación
[Copiados de la User Story para referencia]

## Notas de Rollback
[Para tareas de riesgo]
```

**Ubicación:** `.raise/plans/{us-id}-plan.md`

**Siguiente paso:**
1. Ejecutar `gates/gate-plan.md` para validar
2. Si pasa el gate, proceder a `flujo-06-development`

---

## Notas

### Granularidad Correcta
- **Muy grande:** "Implementar el módulo de usuarios" (no atómico)
- **Muy pequeña:** "Añadir import statement" (demasiado detalle)
- **Correcta:** "Crear endpoint POST /users con validación de email"

### Relación con Katas de Patrón
Las tareas pueden referenciar katas de patrón para guía específica:
- "Seguir `patron-entity-creation` para la entidad User"
- "Aplicar `tecnica-api-validation` para validaciones"

---

## Referencias

- Prerequisito: [`flujo-05-backlog-creation`](./05-backlog-creation.md)
- Siguiente kata: [`flujo-06-development`](./06-development.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 5
