---
id: plan
titulo: "Plan: Implementation Planning"
work_cycle: story
frequency: per-story
fase_metodologia: 5

prerequisites:
  - project/backlog
template: null
gate: gates/gate-plan.md
next_kata: story/implement

adaptable: true
shuhari:
  shu: "Descomponer cada story en tasks atómicos"
  ha: "Ajustar granularidad según complejidad"
  ri: "Crear kata de Plan para contextos específicos"

version: 1.0.0
---

# Plan: Implementation Planning

## Propósito

Descomponer user stories en tasks atómicos ejecutables, identificar dependencias, y crear un plan de implementación determinista que guíe al agente de desarrollo.

## Contexto

**Cuándo usar:**
- Después de tener stories priorizadas en el backlog
- Antes de comenzar la implementación de un feature
- Para cada feature que se va a desarrollar

**Inputs requeridos:**
- User stories del feature a implementar
- Technical Design para contexto arquitectónico

**Output:**
- `work/stories/{feature}/plan.md` - Plan de implementación

## Pasos

### Paso 1: Seleccionar Story

Identificar la próxima story a implementar según prioridad.

**Verificación:** Story seleccionada tiene criterios BDD claros.

> **Si no puedes continuar:** Story sin criterios → Completar criterios BDD primero.

### Paso 2: Descomponer en Tasks

Dividir story en tasks atómicos:
- 1-4 horas de trabajo cada uno
- Independientes cuando sea posible
- Verificables individualmente

**Verificación:** Cada task es atómico y verificable.

> **Si no puedes continuar:** Tasks muy grandes → Dividir hasta que sean atómicos.

### Paso 3: Identificar Dependencias

Mapear dependencias entre tasks:
- Secuenciales vs paralelos
- Dependencias externas
- Blockers potenciales

**Verificación:** Grafo de dependencias sin ciclos.

> **Si no puedes continuar:** Dependencias circulares → Refactorizar tasks para romper ciclos.

### Paso 4: Ordenar Ejecución

Definir orden óptimo de ejecución:
- Respetar dependencias
- Maximizar paralelismo
- Quick wins primero

**Verificación:** Orden de ejecución definido.

> **Si no puedes continuar:** Orden ambiguo → Priorizar por riesgo (lo más riesgoso primero).

### Paso 5: Definir Verificación por Task

Para cada task, definir:
- Criterio de completitud
- Comando de verificación (test, lint, etc.)
- Rollback si falla

**Verificación:** Cada task tiene criterio de verificación.

> **Si no puedes continuar:** Verificación no clara → Añadir test específico para el task.

### Paso 6: Documentar Plan

Crear documento de plan con:
- Lista ordenada de tasks
- Dependencias
- Verificaciones
- Estimación total

**Verificación:** Plan documentado y completo.

> **Si no puedes continuar:** N/A.

## Output

- **Artefacto:** Implementation Plan
- **Ubicación:** `work/stories/{feature}/plan.md`
- **Gate:** `gates/gate-plan.md`
- **Siguiente kata:** `feature/implement`

## Referencias

- Gate de validación: `gates/gate-plan.md`
