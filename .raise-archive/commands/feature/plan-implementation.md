---
description: Generate an Implementation Plan from User Stories, ordering tasks by dependencies and producing atomic task lists for deterministic execution.
handoffs:
  - label: Implement Feature
    agent: feature/implement
    prompt: Implement this feature following the plan
    send: true
  - label: Validate Plan
    agent: validate/validate-plan
    prompt: Validate the implementation plan
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should be:
- A feature ID (e.g., "F1.3", "raise-feature-plan")
- Or a path to the stories/ directory

## Outline

Goal: Generate an Implementation Plan (`specs/features/{feature-id}/plan.md`) and Task List (`specs/features/{feature-id}/tasks.md`) from User Stories, with tasks ordered by dependencies.

1. **Initialize Environment**:
   - Identify feature from user input.
   - Locate stories at `specs/features/{feature-id}/stories/`.
   - Load tech-design for context: `specs/features/{feature-id}/tech-design.md`.

2. **Paso 1: Cargar User Stories**:
   - Leer todos los archivos `US-*.md` del directorio stories/.
   - Parsear frontmatter YAML de cada story (id, title, priority, estimate).
   - Leer index.md para obtener resumen y dependencias.
   - **Verificación**: Al menos 1 story cargada con frontmatter válido.
   - > **Si no puedes continuar**: Stories no encontradas → **JIDOKA**: Ejecutar `/feature/generate-stories {feature-id}` primero. Frontmatter inválido → Corregir formato de stories.

3. **Paso 2: Construir Grafo de Dependencias**:
   - Para cada story, identificar dependencias:
     - Explícitas: campo "depends_on" o "blocked_by" en frontmatter
     - Implícitas: P1 antes de P2, P2 antes de P3
   - Construir grafo dirigido: nodo = story, edge = "depende de"
   - **Verificación**: Grafo construido con todas las stories como nodos.
   - > **Si no puedes continuar**: Story referencia dependencia inexistente → Warning y continuar sin esa edge.

4. **Paso 3: Detectar Ciclos**:
   - Ejecutar detección de ciclos en el grafo (DFS).
   - Si hay ciclo: **JIDOKA** - parar y reportar.
   - **Verificación**: Grafo es acíclico (DAG).
   - > **Si no puedes continuar**: Ciclo detectado → **JIDOKA**: Reportar las stories involucradas. Ejemplo: "Ciclo: US-001 → US-003 → US-001". Solicitar al usuario resolver antes de continuar.

5. **Paso 4: Ordenar Topológicamente**:
   - Aplicar ordenamiento topológico al grafo.
   - Resultado: lista de stories en orden de ejecución.
   - Dentro del mismo nivel, ordenar por prioridad (P1 primero).
   - **Verificación**: Lista ordenada contiene todas las stories.
   - > **Si no puedes continuar**: Error en ordenamiento → Verificar que el grafo es DAG (paso anterior).

6. **Paso 5: Generar Tasks por Story**:
   - Para cada story en orden:
     - Leer estimate (S/M/L)
     - Generar tasks según estimate:
       - **S** (Small): 1 task
       - **M** (Medium): 2-3 tasks
       - **L** (Large): 3-5 tasks
     - Cada task incluye:
       - **Instructions**: Pasos atómicos a ejecutar
       - **Verification**: Checkboxes para confirmar completitud
       - **If blocked**: Guía de recuperación (Jidoka)
   - Asignar IDs secuenciales: T1, T2, T3...
   - **Verificación**: Cada story tiene al menos 1 task asociada.
   - > **Si no puedes continuar**: Story sin tasks → Revisar si story es demasiado vaga. Agregar al menos 1 task con los acceptance criteria como verification.

7. **Paso 6: Escribir plan.md**:
   - Crear `specs/features/{feature-id}/plan.md` con:
     - Frontmatter: id, feature_ref, created, status, total_tasks, estimated_effort
     - Diagrama Mermaid de orden de ejecución
     - Tabla resumen de tasks
     - Sección de Checkpoints (Jidoka)
   - **Verificación**: Archivo creado con todas las secciones.
   - > **Si no puedes continuar**: Error de escritura → Verificar permisos.

8. **Paso 7: Escribir tasks.md**:
   - Crear `specs/features/{feature-id}/tasks.md` con:
     - Header con metadata del feature
     - Cada task en formato completo:
       ```markdown
       ## T{N}: {título}
       **Story**: {story-id}
       **Estimate**: {S|M|L}
       **Dependencies**: {lista o "ninguna"}

       ### Instructions
       1. {paso 1}
       2. {paso 2}

       ### Verification
       - [ ] {criterio 1}
       - [ ] {criterio 2}

       ### If blocked
       - {condición} → {acción}
       ---
       ```
   - **Verificación**: Archivo creado con todas las tasks.
   - > **Si no puedes continuar**: Error de escritura → Verificar permisos.

9. **Paso 8: Calcular Métricas**:
   - Sumar estimaciones: S=1, M=3, L=5 puntos
   - Calcular esfuerzo total estimado:
     - 1-4 puntos: "S (< 4 horas)"
     - 5-12 puntos: "M (4-16 horas)"
     - 13-25 puntos: "L (16-40 horas)"
     - 25+ puntos: "XL (> 40 horas) - considerar dividir"
   - **Verificación**: Métricas calculadas y consistentes.
   - > **Si no puedes continuar**: Estimación XL → Warning: feature muy grande, considerar dividir.

10. **Finalize & Validate**:
    - Confirmar archivos creados:
      - `specs/features/{feature-id}/plan.md`
      - `specs/features/{feature-id}/tasks.md`
    - Validar consistencia:
      - [ ] Todas las stories tienen tasks
      - [ ] Todas las tasks tienen verification
      - [ ] Orden de tasks respeta dependencias
    - Mostrar resumen:
      ```
      ✓ Implementation Plan generado para {feature-name}

      📁 specs/features/{feature-id}/
         ├── plan.md (overview + diagram)
         └── tasks.md ({N} tasks)

      📊 Resumen:
         - Stories: {N}
         - Tasks: {M}
         - Esfuerzo estimado: {S|M|L|XL}
         - Orden: {lista de task IDs}

      📋 Execution Order:
         T1 → T2 → T3 → [T4, T5] → T6
         (tasks en [] pueden ejecutarse en paralelo)
      ```
    - Mostrar warnings si aplican:
      - "⚠ Esfuerzo XL: considerar dividir feature en sub-features"
      - "⚠ Tasks sin dependencias claras: verificar orden manualmente"
    - Mostrar handoff: "→ Siguiente paso: `/feature/implement` para ejecutar el plan"

## Notas

### Relación Task ↔ Story
- Cada task pertenece a exactamente 1 story
- Stories pequeñas (S) = 1 task
- Stories medianas (M) = 2-3 tasks (setup + implement + verify)
- Stories grandes (L) = 3-5 tasks (dividir por sub-componentes)

### Paralelización
- Tasks sin dependencias entre sí pueden ejecutarse en paralelo
- El diagrama Mermaid muestra esto visualmente
- tasks.md las lista secuencialmente pero indica paralelos

### Checkpoints (Jidoka)
Cada task tiene verificación. El agente/humano debe:
1. Ejecutar Instructions
2. Verificar cada checkbox
3. Si alguno falla → consultar "If blocked"
4. Solo avanzar a siguiente task si todo pasa

## High-Signaling Guidelines

- **Output**: `plan.md` (overview) + `tasks.md` (detalles ejecutables)
- **Focus**: Convertir stories en secuencia de trabajo determinística
- **Language**: Instructions English; Content **SPANISH**
- **Jidoka**: Stop si hay ciclos en dependencias. Cada task tiene verification.
- **Lean**: Tasks atómicas (1-4 horas). Si task > 4 horas, subdividir.

## AI Guidance

When executing this workflow:
1. **Role**: You are a Tech Lead creating an execution plan that a developer (human or AI) can follow step by step.
2. **Be deterministic**: The plan should produce the same result regardless of who executes it.
3. **Atomic tasks**: Each task should be completable in one sitting (1-4 hours).
4. **Verification-first**: Write verification criteria before instructions (TDD mindset).
5. **Dependencies matter**: Never allow a task to start before its dependencies are done.
6. **Parallel when possible**: Identify tasks that can run in parallel to optimize execution.
