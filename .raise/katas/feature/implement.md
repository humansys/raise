---
id: implement
titulo: "Implement: Development Workflow"
work_cycle: feature
frequency: per-feature
fase_metodologia: 6

prerequisites:
  - feature/plan
template: null
gate: gates/gate-code.md
next_kata: feature/review

adaptable: true
shuhari:
  shu: "Ejecutar tasks en orden, verificar cada uno"
  ha: "Ajustar plan según descubrimientos durante implementación"
  ri: "Crear kata de Implement para stacks específicos"

version: 1.0.0
---

# Implement: Development Workflow

## Propósito

Ejecutar el plan de implementación task por task, verificando cada paso, y produciendo código de calidad que pase los gates de validación.

## Contexto

**Cuándo usar:**
- Después de tener un plan de implementación
- Para cada feature que se va a desarrollar
- Repetido para cada task del plan

**Inputs requeridos:**
- Plan de implementación (`specs/{feature}/plan.md`)
- Contexto de reglas del proyecto

**Output:**
- Código implementado y verificado
- `specs/{feature}/progress.md` - Registro de progreso

## Pasos

### Paso 1: Cargar Plan y Contexto

Cargar el plan de implementación y obtener contexto de reglas aplicables.

**Verificación:** Plan cargado y contexto disponible.

> **Si no puedes continuar:** Plan no encontrado → Ejecutar `feature/plan` primero.

### Paso 2: Identificar Siguiente Task

Seleccionar el próximo task no completado según el orden del plan.

**Verificación:** Task identificado con sus dependencias resueltas.

> **Si no puedes continuar:** Dependencias no resueltas → Resolver dependencias primero.

### Paso 3: Ejecutar Task

Implementar el código del task siguiendo:
- Reglas del proyecto
- Patrones establecidos
- Tests requeridos

**Verificación:** Código implementado compila/funciona.

> **Si no puedes continuar:** Error de implementación → Documentar blocker y escalar.

### Paso 4: Verificar Task

Ejecutar verificación definida en el plan:
- Tests unitarios
- Linting
- Type checking

**Verificación:** Todas las verificaciones pasan.

> **Si no puedes continuar:** Verificación falla → Corregir y re-verificar (máx 3 intentos).

### Paso 5: Registrar Progreso

Actualizar `specs/{feature}/progress.md`:
- Task completado
- Tiempo real vs estimado
- Notas o descubrimientos

**Verificación:** Progreso registrado.

> **Si no puedes continuar:** N/A.

### Paso 6: Iterar o Finalizar

Si hay más tasks → volver a Paso 2.
Si todos los tasks completados → ejecutar gate de código.

**Verificación:** Todos los tasks del plan completados.

> **Si no puedes continuar:** Tasks bloqueados → Documentar y escalar.

## Output

- **Artefacto:** Código implementado
- **Ubicación:** Según arquitectura del proyecto
- **Gate:** `gates/gate-code.md`
- **Siguiente kata:** `feature/review`

## Notas

### Resumabilidad

El progreso se persiste en `progress.md`, permitiendo retomar la implementación si se interrumpe.

### Límite de Intentos

Máximo 3 intentos por verificación fallida antes de escalar.

## Referencias

- Gate de validación: `gates/gate-code.md`
