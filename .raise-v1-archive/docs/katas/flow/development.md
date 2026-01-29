---
id: flujo-06-development
nivel: flujo
titulo: "Development: Ejecución del Plan de Implementación"
audience: beginner
template_asociado: null
validation_gate: gates/gate-code.md
prerequisites:
  - flujo-04-implementation-plan
fase_metodologia: 6
tags: [desarrollo, implementacion, codigo, fase-6]
version: 1.0.0
---

# Development: Ejecución del Plan de Implementación

## Propósito

Ejecutar el Plan de Implementación de manera controlada, siguiendo los guardrails del proyecto y manteniendo al Orquestador informado en cada paso crítico. Esta kata implementa el principio "add-only first": preferir añadir código nuevo sobre modificar existente.

Esta kata responde a la pregunta: **¿Cómo fluye la ejecución de un plan de implementación de manera confiable?**

## Contexto

**Cuándo usar:**
- Después de que Gate-Plan ha sido aprobado
- Para ejecutar cualquier Implementation Plan
- Durante el desarrollo activo de una User Story

**Inputs requeridos:**
- Implementation Plan aprobado (output de `flujo-04-implementation-plan`)
- Guardrails del proyecto cargados
- Ambiente de desarrollo configurado

**Output:** Código implementado y probado, listo para merge

## Pre-condiciones

- [ ] Gate-Plan aprobado
- [ ] Implementation Plan disponible
- [ ] Branch de trabajo creada
- [ ] Ambiente de desarrollo funcional
- [ ] Tests base pasando (no romper lo existente)

---

## Pasos

### Paso 1: Cargar Contexto de Implementación

Cargar el Plan de Implementación y verificar el ambiente:
- Plan de Implementación completo
- User Story y criterios de aceptación
- Guardrails aplicables identificados
- Tech Design como referencia

```bash
# Verificar ambiente
git status  # branch correcta
npm test    # tests pasando (o equivalente)
```

**Verificación:** El Orquestador confirma que el plan está cargado y el ambiente está listo.

> **Si no puedes continuar:** Ambiente no funciona → Resolver issues de ambiente antes de comenzar desarrollo. No codear sobre base rota.

---

### Paso 2: Confirmar Interpretación del Plan

Antes de escribir código, el agente resume:
- Qué tareas ejecutará
- En qué orden
- Qué guardrails aplicará

**Pausa para Validación:** "Estas son las tareas que ejecutaré. ¿Confirmas la interpretación?"

**Verificación:** Orquestador aprueba la interpretación del plan.

> **Si no puedes continuar:** Interpretación incorrecta → Clarificar con Orquestador antes de escribir código. Actualizar plan si es necesario.

---

### Paso 3: Ejecutar Tareas del Plan (Bucle)

Para cada tarea en el Plan de Implementación:

#### 3a. Identificar Tipo de Cambio

- **Crear archivo nuevo**: Siempre preferido
- **Añadir a archivo existente**: Aceptable si es adición pura
- **Modificar código existente**: Requiere aprobación explícita

**Verificación:** Tipo de cambio identificado antes de escribir código.

> **Si no puedes continuar:** Tipo de cambio no claro → Revisar la tarea. Si requiere modificación compleja, pedir aprobación antes de proceder.

#### 3b. Generar Código

Escribir código siguiendo:
- Guardrails del proyecto
- Patrones del Tech Design
- Convenciones existentes del repositorio

Para **código nuevo**:
- Crear archivo completo con estructura correcta
- Seguir naming conventions

Para **modificaciones**:
- Mostrar diff antes de aplicar
- Explicar por qué la modificación es necesaria
- **Esperar aprobación explícita**

**Verificación:** Código generado sigue los guardrails aplicables.

> **Si no puedes continuar:** Guardrail violado → Corregir antes de continuar. No acumular deuda técnica.

#### 3c. Validación del Orquestador

**Pausa para Validación:** "He generado el código para [componente]. Aquí está el contenido/diff. ¿Lo apruebas?"

Esperar:
- Aprobación → continuar
- Rechazo → iterar con feedback
- Modificación solicitada → aplicar y re-validar

**Verificación:** Orquestador aprueba explícitamente cada cambio significativo.

> **Si no puedes continuar:** Rechazo sin feedback → Pedir feedback específico: "¿Qué cambiarías?"

#### 3d. Escribir Tests (si aplica)

Según la tarea y estrategia de testing:
- Unit tests para lógica de negocio
- Integration tests para APIs
- Seguir guardrails de testing

**Verificación:** Tests escritos siguen el patrón AAA (Arrange-Act-Assert) o equivalente.

> **Si no puedes continuar:** No claro qué testear → Cubrir al menos: happy path y un error case por cada función pública.

#### 3e. Ejecutar Verificación

Después de cada tarea o grupo de tareas:

```bash
# Ejecutar tests
npm test  # o equivalente

# Verificar linting
npm run lint  # o equivalente
```

**Verificación:** Tests pasan. No hay errores de linting.

> **Si no puedes continuar:** Tests fallan → Corregir antes de continuar (Jidoka). No avanzar con tests rotos.

#### 3f. Marcar Tarea Completada

Actualizar el Plan de Implementación:
```markdown
- [x] Tarea N: [Descripción]
```

**Verificación:** Tarea marcada como completada en el plan.

---

### Paso 4: Verificación Integral

Después de completar todas las tareas:

1. **Ejecutar suite completa de tests**
2. **Verificar criterios de aceptación** de la User Story
3. **Revisar código generado** en conjunto

```bash
# Tests completos
npm run test:all

# Build
npm run build

# Verificación manual si aplica
```

**Verificación:** Todos los tests pasan. Build exitoso. Criterios de aceptación cubiertos.

> **Si no puedes continuar:** Algún criterio de aceptación no cubierto → Revisar tareas faltantes. Puede requerir tareas adicionales.

---

### Paso 5: Documentar Cambios

Si el cambio afecta APIs o comportamiento:
- Actualizar documentación inline (JSDoc, docstrings)
- Actualizar README si hay nuevos endpoints
- Notas de changelog si aplica

**Verificación:** Documentación actualizada donde sea necesario.

> **Si no puedes continuar:** No claro qué documentar → Documentar al menos: funciones públicas nuevas, cambios en APIs, configuración nueva.

---

### Paso 6: Preparar para Review

Crear commit(s) con mensaje descriptivo:

```bash
git add .
git commit -m "feat(module): description of change

- Detail 1
- Detail 2

Closes: US-XXX"
```

**Verificación:** Commits creados con mensajes que siguen convención del proyecto.

> **Si no puedes continuar:** Convención de commits no clara → Usar Conventional Commits como default: `type(scope): description`.

---

### Paso 7: Validación Final con Orquestador

Presentar el trabajo completado:

**Pausa para Validación:** "Todas las tareas del plan están completadas. Los tests pasan. ¿Hay algo más que revisar o ajustar?"

**Verificación:** Orquestador confirma que la implementación está completa.

> **Si no puedes continuar:** Ajustes solicitados → Iterar hasta satisfacción. Actualizar plan si se añaden tareas.

---

## Output

**Artefactos producidos:**
- Código implementado en branch de feature
- Tests asociados
- Documentación actualizada
- Commits listos para PR

**Siguiente paso:**
1. Ejecutar `gates/gate-code.md` para validación final
2. Si pasa el gate, crear Pull Request
3. Proceder a code review y merge

---

## Principios de Desarrollo

### Add-Only First
Preferir añadir código nuevo sobre modificar existente:
1. **Crear nuevo archivo** > Modificar existente
2. **Añadir función** > Cambiar función
3. **Extender clase** > Modificar clase

Solo modificar código existente cuando:
- Es estrictamente necesario para el requisito
- El Orquestador aprueba explícitamente

### Jidoka en Desarrollo
- Tests fallan → **STOP** → Corregir → Continuar
- Guardrail violado → **STOP** → Corregir → Continuar
- Orquestador rechaza → **STOP** → Iterar → Continuar

### Explicabilidad
Antes de generar código complejo, el agente debe:
1. Explicar el approach
2. Esperar confirmación
3. Entonces generar

---

## Escalation Gate

Durante desarrollo, escalar si:

| Condición | Escalar a |
|-----------|-----------|
| Código generado incomprensible para Orquestador | Explicación detallada antes de continuar |
| Requisito imposible de implementar | Product Owner para re-scope |
| Bug en dependencia externa | Tech Lead para workaround |
| Decisión arquitectónica no cubierta en Tech Design | Arquitecto |

---

## Referencias

- Prerequisito: [`flujo-04-implementation-plan`](./04-implementation-plan.md)
- Gate: [`gates/gate-code.md`](../../gates/gate-code.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 6
