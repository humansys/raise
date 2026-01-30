---
id: "TEC-RAISE-F1.4"
title: "Tech Design: raise.feature.implement Command"
version: "1.0"
date: "2026-01-28"
status: "Draft"
feature_ref: "F1.4"
backlog_ref: "raise-v2-feature-commands"
template: "lean-spec-v1"
---

# Tech Design: raise.feature.implement Command

> **Feature**: F1.4 - Comando para ejecutar Plan de Implementación
> **Epic**: E1 - Feature-Level Commands para RaiSE v2

## 1. Approach

**Qué hace este feature**:
Ejecuta un Plan de Implementación task por task, siguiendo el orden definido, verificando cada checkpoint (Jidoka), y produciendo los artefactos especificados (código, tests, documentación). Actúa como el "runtime" que convierte el plan determinístico en trabajo completado.

**Cómo lo implementamos**:
Comando Markdown (`.raise/commands/03-feature/raise.feature.implement.md`) que lee tasks.md, ejecuta cada task secuencialmente respetando dependencias, marca progreso, y maneja bloqueos con guía de recuperación. El comando es un orquestador, no genera código directamente—delega a herramientas/agente según las Instructions de cada task.

**Componentes afectados**:
- `.raise/commands/03-feature/raise.feature.implement.md`: Nuevo comando
- `.claude/commands/03-feature/raise.feature.implement.md`: Copia para Claude Code
- `specs/features/{feature-id}/tasks.md`: Input (plan a ejecutar)
- `specs/features/{feature-id}/progress.md`: Tracking de progreso (nuevo)
- Archivos de código/tests según lo especificado en tasks

---

## 2. Interfaz / Contrato

```yaml
# Comando: /raise.feature.implement
input:
  - feature_id: string           # ID del feature
  - tasks_path: string           # Path a tasks.md (auto-detectado)
  - start_from: string           # Task ID opcional para resumir (e.g., "T3")
  - dry_run: boolean             # Solo mostrar qué haría, sin ejecutar

output:
  - progress_file: "specs/features/{feature-id}/progress.md"
  - artifacts: según tasks (código, tests, docs)
  - completion_status: "complete" | "blocked" | "partial"

handoffs:
  - next: "/raise.validate.feature"
    prompt: "Validate the implemented feature"
  - fallback: "/raise.feature.plan"
    prompt: "Re-plan if blocked"
```

**Ejemplo de uso**:
```bash
# Ejecutar plan completo
/raise.feature.implement raise-feature-implement

# Resumir desde task específica
/raise.feature.implement raise-feature-implement --start-from T3

# Dry run para ver qué haría
/raise.feature.implement raise-feature-implement --dry-run
```

**Output esperado** (progress.md):
```markdown
---
feature_ref: F1.4
started: 2026-01-28T10:00:00Z
last_updated: 2026-01-28T12:30:00Z
status: in_progress
current_task: T5
---

# Implementation Progress: raise.feature.implement

## Status

| Task | Status | Started | Completed | Notes |
|------|--------|---------|-----------|-------|
| T1 | ✅ done | 10:00 | 10:15 | - |
| T2 | ✅ done | 10:15 | 10:45 | - |
| T3 | ✅ done | 10:45 | 11:30 | Required clarification on X |
| T4 | ✅ done | 11:30 | 12:00 | - |
| T5 | 🔄 in_progress | 12:00 | - | Working on verification |
| T6 | ⏳ pending | - | - | - |

## Blockers Log

### T3 - 2026-01-28T11:00
**Issue**: Unclear requirement for error handling
**Resolution**: Asked user, decided to use Result<T,E> pattern
**Time lost**: 15 min

## Artifacts Created

- `.raise/commands/03-feature/raise.feature.implement.md`
- `.claude/commands/03-feature/raise.feature.implement.md`
- `specs/features/raise-feature-implement/tech-design.md`
```

---

## 3. Consideraciones

| Aspecto | Decisión | Rationale |
|---------|----------|-----------|
| Ejecución | Secuencial respetando dependencias | Determinístico, predecible, debuggeable |
| Progreso | Persistido en progress.md | Permite resumir después de interrupción |
| Bloqueos | Log + pausa + guía de recuperación | Jidoka: parar, corregir, continuar |
| Paralelización | No automática (v1) | Simplicidad. Futuro: detectar y ofrecer |
| Rollback | No incluido (v1) | Complejidad. Git es el mecanismo de rollback |

**Riesgos identificados**:
- [ ] Task con instructions ambiguas → Mitigación: Pedir clarificación, loguear en progress.md
- [ ] Interrupción a mitad de task → Mitigación: progress.md marca última task completa, --start-from para resumir
- [ ] Verificación falla repetidamente → Mitigación: Después de 3 intentos, escalar (Jidoka)

---

<details>
<summary><h2>Algoritmo / Lógica</h2></summary>

```
1. LOAD tasks.md from specs/features/{feature-id}/
2. LOAD progress.md if exists (for resume)

3. DETERMINE starting point:
   IF --start-from provided:
     - Start from that task
   ELSE IF progress.md exists:
     - Find first non-completed task
   ELSE:
     - Start from T1

4. FOR each task in order from starting point:

   a. CHECK dependencies:
      - All dependent tasks must be "done"
      - IF not: JIDOKA - report and wait

   b. UPDATE progress.md:
      - Mark task as "in_progress"
      - Record start time

   c. DISPLAY task to user/agent:
      - Show Instructions
      - Show Verification criteria
      - Show If-blocked guidance

   d. EXECUTE task:
      - Follow Instructions step by step
      - Create artifacts as specified
      - May involve: writing code, running commands, creating files

   e. VERIFY completion:
      - Check each Verification criterion
      - IF all pass: mark "done", continue
      - IF any fail:
        i. Check If-blocked guidance
        ii. Attempt recovery (max 3 times)
        iii. IF still blocked: JIDOKA - log blocker, pause

   f. UPDATE progress.md:
      - Mark completion time
      - Log any notes/blockers

5. ON completion of all tasks:
   - Update progress.md status to "complete"
   - List all artifacts created
   - Show summary

6. ON blocker:
   - Update progress.md with blocker details
   - Show handoff options:
     - "Resolve manually and run --start-from {task}"
     - "Re-plan with /raise.feature.plan"
```

</details>

<details>
<summary><h2>Testing Approach</h2></summary>

| Tipo | Qué cubre |
|------|-----------|
| Manual | Ejecutar con plan de raise-feature-implement |
| Resume | Interrumpir, luego --start-from |
| Blocker | Task con verification que falla → debe pausar correctamente |

**Casos de prueba**:
1. Plan de 3 tasks simples → Ejecuta todas, status "complete"
2. Interrupción en T2 → Resume con --start-from T2 funciona
3. Verification falla → Intenta 3 veces, luego JIDOKA con log

</details>
