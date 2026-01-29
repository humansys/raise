---
description: Execute an Implementation Plan task by task, following dependencies, verifying checkpoints (Jidoka), and producing specified artifacts.
handoffs:
  - label: Validate Feature
    agent: validate/validate-feature
    prompt: Validate the implemented feature
    send: true
  - label: Re-plan Feature
    agent: feature/plan-implementation
    prompt: Re-plan the feature if blocked
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input may include:
- A feature ID (e.g., "F1.4", "raise-feature-implement")
- `--start-from T{N}` to resume from a specific task
- `--dry-run` to show what would be done without executing

## Outline

Goal: Execute the Implementation Plan (`specs/features/{feature-id}/tasks.md`) task by task, tracking progress in `specs/features/{feature-id}/progress.md`, and creating the specified artifacts.

1. **Initialize Environment**:
   - Identify feature from user input.
   - Load tasks from `specs/features/{feature-id}/tasks.md`.
   - Load or create `specs/features/{feature-id}/progress.md`.
   - Determine starting point (--start-from, progress.md, or T1).

2. **Paso 1: Cargar Plan y Estado**:
   - Parsear tasks.md para obtener lista de tasks con:
     - ID, título, story_ref, estimate
     - Dependencies
     - Instructions, Verification, If-blocked
   - Si progress.md existe, cargar estado actual.
   - Identificar primera task pendiente.
   - **Verificación**: Tasks cargadas y punto de inicio determinado.
   - > **Si no puedes continuar**: tasks.md no encontrado → **JIDOKA**: Ejecutar `/feature/plan-implementation {feature-id}` primero.

3. **Paso 2: Validar Dependencias de Task Actual**:
   - Para la task actual, verificar que todas las dependencias están "done".
   - Si hay dependencias pendientes, esperar o reportar.
   - **Verificación**: Todas las dependencias de la task actual están completadas.
   - > **Si no puedes continuar**: Dependencia no completada → Mostrar qué tasks faltan. Si es --start-from incorrecto, sugerir task correcta.

4. **Paso 3: Mostrar Task al Usuario/Agente**:
   - Actualizar progress.md: marcar task como "in_progress".
   - Mostrar claramente:
     ```
     ═══════════════════════════════════════════
     📋 Task {ID}: {título}
     ═══════════════════════════════════════════
     Story: {story_ref}
     Estimate: {estimate}
     Dependencies: {deps o "ninguna"}

     ## Instructions
     {instructions paso a paso}

     ## Verification
     {criteria con checkboxes}

     ## If Blocked
     {guía de recuperación}
     ═══════════════════════════════════════════
     ```
   - **Verificación**: Task mostrada correctamente.
   - > **Si no puedes continuar**: Error al mostrar → Verificar formato de tasks.md.

5. **Paso 4: Ejecutar Instructions**:
   - Seguir cada instrucción de la task secuencialmente.
   - Crear artefactos según especificado (código, archivos, etc.).
   - Si una instrucción no es clara: pedir clarificación, loguear en progress.md.
   - **Verificación**: Todas las instrucciones ejecutadas.
   - > **Si no puedes continuar**: Instrucción ambigua → Pedir clarificación al usuario. Loguear pregunta y respuesta en progress.md para referencia futura.

6. **Paso 5: Verificar Completion**:
   - Revisar cada criterio de Verification:
     - Si pasa: ✅ marcar
     - Si falla: intentar corregir
   - Máximo 3 intentos de corrección por criterio.
   - **Verificación**: Todos los criteria pasan.
   - > **Si no puedes continuar**: Verification falla después de 3 intentos → **JIDOKA**:
     > 1. Loguear en progress.md: qué falló, qué se intentó
     > 2. Consultar sección "If Blocked" de la task
     > 3. Si no se puede resolver: pausar y escalar
     > 4. Mostrar: "⚠ Task {ID} bloqueada. Resolver manualmente y ejecutar `/feature/implement {feature} --start-from {ID}`"

7. **Paso 6: Registrar Completitud**:
   - Actualizar progress.md:
     - Marcar task como "done"
     - Registrar timestamp de completion
     - Agregar notas si hubo issues
   - Listar artefactos creados en esta task.
   - **Verificación**: progress.md actualizado correctamente.
   - > **Si no puedes continuar**: Error de escritura → Mostrar estado en consola para registro manual.

8. **Paso 7: Avanzar a Siguiente Task**:
   - Identificar siguiente task en orden.
   - Si hay más tasks: volver a Paso 2.
   - Si no hay más tasks: ir a Paso 8.
   - **Verificación**: Siguiente task identificada o fin alcanzado.
   - > **Si no puedes continuar**: Estado inconsistente → Recargar tasks.md y progress.md.

9. **Paso 8: Finalizar Implementación**:
   - Actualizar progress.md:
     - status: "complete"
     - completion_time: timestamp
   - Compilar lista de todos los artefactos creados.
   - Mostrar resumen final:
     ```
     ═══════════════════════════════════════════
     ✅ Feature Implementation Complete
     ═══════════════════════════════════════════

     📊 Summary:
        - Feature: {feature-id}
        - Tasks completed: {N}/{total}
        - Time: {start} → {end}
        - Blockers resolved: {count}

     📁 Artifacts Created:
        - {path/to/file1}
        - {path/to/file2}
        - ...

     📋 Progress Log: specs/features/{feature-id}/progress.md

     → Siguiente paso: `/validate/validate-feature {feature-id}`
     ═══════════════════════════════════════════
     ```
   - **Verificación**: Resumen mostrado, progress.md finalizado.
   - > **Si no puedes continuar**: Si hay tasks incompletas, mostrar status "partial" con lista de pendientes.

## Notas

### Modos de Ejecución
- **Normal**: Ejecuta desde T1 o desde última task completada
- **--start-from T{N}**: Resume desde task específica (útil después de resolver blocker)
- **--dry-run**: Muestra qué haría sin ejecutar (para revisar plan)

### Jidoka en Implementación
El ciclo Jidoka se aplica a cada task:
1. **Detectar**: Verification falla
2. **Parar**: No avanzar a siguiente task
3. **Corregir**: Seguir "If Blocked", intentar hasta 3 veces
4. **Continuar**: Solo si Verification pasa

### Artefactos Típicos
- Archivos de código (.ts, .py, .md, etc.)
- Tests
- Configuración
- Documentación

### Interrupción y Resume
- progress.md persiste estado entre sesiones
- Ctrl+C o cierre de sesión → resume automático desde última task completada
- --start-from para override manual

## High-Signaling Guidelines

- **Output**: Artefactos según plan + progress.md
- **Focus**: Ejecutar plan determinísticamente, task por task
- **Language**: Instructions English; Content **SPANISH** (en artefactos)
- **Jidoka**: Parar si verification falla después de 3 intentos. Nunca saltar tasks.
- **Traceability**: Todo queda registrado en progress.md

## AI Guidance

When executing this workflow:
1. **Role**: You are an executor following a deterministic plan. Don't improvise—follow Instructions exactly.
2. **One task at a time**: Complete current task fully before moving to next.
3. **Verification is mandatory**: Never skip verification. If it fails, stop and address.
4. **Log everything**: Blockers, clarifications, decisions—all go to progress.md.
5. **Ask don't assume**: If an instruction is unclear, ask the user rather than guessing.
6. **Respect dependencies**: Never execute a task before its dependencies are done.
7. **Artifacts match plan**: Only create artifacts specified in the task. No extras.
