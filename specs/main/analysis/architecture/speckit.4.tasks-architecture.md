# Análisis Arquitectónico: speckit.4.tasks

## 1. Resumen Ejecutivo

El comando `speckit.4.tasks` transforma artefactos de diseño (spec + plan) en una lista de tareas ejecutables, dependency-ordered, y organizadas por user story. Implementa el principio de "independent deployability" - cada user story es un incremento completo e independientemente testable.

**Patrón arquitectónico clave**: User-Story-Centric Task Organization con dependency graph explícito.

**Innovación principal**: Formato estricto de checklist con markers de paralelización ([P]) y story labels ([US1], [US2]) que permiten ejecución optimizada y trazabilidad requirement → task.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.5.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.6.implement
    prompt: Start the implementation in phases
    send: true
```

**Patrón**: Dual handoffs con propósitos diferentes
- **Primary (Quality Gate)**: `speckit.5.analyze` - validación antes de implementar
- **Alternative (Skip Validation)**: `speckit.6.implement` - ir directo a implementación

**Diseño**: El primer handoff (analyze) tiene send:true, sugiriendo que la validación es el flujo recomendado.

### 2.2 Input Processing

**Patrón**: Context-enhanced input
- `$ARGUMENTS`: Usado en paso 3 (Task Generation Rules context)
- Design artifacts: Driver principal (plan.md, spec.md, data-model, contracts, research, quickstart)

**Estrategia**: Los argumentos contextualizan la generación pero no la dirigen - la estructura viene de los artifacts.

### 2.3 Outline Structure

**Flujo principal**: 5 pasos de transformación artifacts → tasks

1. **Setup** (prerequisite check con JSON)
2. **Load design documents** (required vs. optional artifacts)
3. **Execute task generation workflow** (extracción + organización + mapping)
4. **Generate tasks.md** (usando template estructurado)
5. **Report** (summary con métricas de calidad)

**Paso crítico**: El paso 3 implementa lógica compleja de mapping artifacts → user stories → tasks.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **User-Story-Centric Organization** | Una fase por user story; tareas agrupadas por story | Incrementos independientes, trazabilidad |
| **Strict Checklist Format** | `- [ ] [TID] [P?] [Story?] Description + path` | Parseability, tool integration, clarity |
| **Parallel Execution Markers** | `[P]` tag en tareas independientes | Optimización de ejecución, work planning |
| **Dependency Graph Explicit** | Sección separada mostrando orden de stories | Visualización, planning, risk assessment |
| **Priority-Based Phases** | P1 → P2 → P3 orden de user stories | MVP-first, incremental delivery |
| **Required vs. Optional Artifacts** | Graceful degradation si algunos faltan | Flexibilidad, robustez |
| **Test-Optional Pattern** | Tests solo si spec lo pide o TDD approach | Evita overhead innecesario |
| **Phase Structure Standard** | Setup → Foundational → Stories → Polish | Consistencia, predecibilidad |
| **Story Independence Goal** | "Most stories should be independent" | Reducir coupling, permitir parallel work |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json` | JSON con FEATURE_DIR, AVAILABLE_DOCS list | Obtener paths + detectar qué artifacts existen |

**Patrón de integración**: Single generic script con standard flags.

**Innovación**: `AVAILABLE_DOCS` list permite graceful degradation - generar tasks basado en lo que existe.

## 5. Validation Strategy

**Multi-level validation**:

### Nivel 1: Input Validation (Paso 2)
- **Required**: plan.md (tech stack), spec.md (user stories)
- **Optional**: data-model, contracts, research, quickstart
- Abortar si required falta; generar tasks basado en available

### Nivel 2: Format Validation (Paso 5 Report)
- Confirmar ALL tasks siguen checklist format
- Validar checkbox, Task ID, labels, file paths presentes

### Nivel 3: Completeness Validation (Paso 5 Report)
- Cada user story tiene todas las tareas necesarias
- Cada user story es independientemente testable
- Total task count razonable
- Parallel opportunities identificadas

### Nivel 4: Structure Validation (Embedded en paso 4)
- Template sections presentes
- Phases en orden correcto
- Dependency graph coherente
- MVP scope identificado

**Filosofía**: Validación distribuida a lo largo del proceso, reporte consolidado al final.

## 6. Error Handling Patterns

### Pattern 1: Missing Required Artifacts
```
If plan.md or spec.md missing → suggest running /speckit.3.plan or /speckit.1.specify
```
**Filosofía**: Guidance hacia prerequisitos, no generación parcial.

### Pattern 2: Missing Optional Artifacts
```
Generate tasks based on what's available
Note in report which artifacts were used
```
**Principio**: Graceful degradation, no bloquear progreso.

### Pattern 3: Format Validation Failure
```
Report in step 5: Format validation - confirm ALL tasks follow checklist format
```
**Diseño**: Self-check integrado en el comando.

### Pattern 4: Incomplete User Stories
```
Validation: Each user story has all needed tasks, independently testable
```
**Estrategia**: Completitud a nivel de story, no solo tasks globales.

## 7. State Management

### Input State (Read-Only)
- **plan.md**: Tech stack, libraries, structure
- **spec.md**: User stories con priorities (P1, P2, P3)
- **data-model.md** (optional): Entities
- **contracts/** (optional): API endpoints
- **research.md** (optional): Decisions
- **quickstart.md** (optional): Test scenarios

### Intermediate State (In-Memory)
- **Tech stack extraction**: Languages, frameworks, libraries
- **User story extraction**: Stories con priorities
- **Entity mapping**: Entity → stories que la usan
- **Endpoint mapping**: Endpoint → stories que lo necesitan
- **Dependency analysis**: Story dependencies

### Output State
- **tasks.md**: Complete task breakdown con:
  - Feature name (from plan)
  - Phase structure (Setup → Foundational → Stories → Polish)
  - Tasks con IDs, markers, descriptions, paths
  - Dependency graph
  - Parallel execution examples
  - Implementation strategy

### State Transitions
```
Load artifacts → Extract tech/stories/entities/endpoints → Map to stories →
Generate phases → Generate tasks per phase → Build dependency graph →
Create parallel examples → Validate completeness → Write tasks.md
```

**Patrón crítico**: Multi-source extraction seguido de mapping consolidado.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **User-story-centric organization** | Incrementos independientes, trazabilidad clara | Puede haber overlap entre stories (shared components) |
| **Strict checklist format** | Parseability, tool integration (GitHub issues, etc.) | Verbosity, rigidez |
| **Parallel markers [P]** | Optimización de ejecución, work planning | Requiere análisis de dependencies manual |
| **Story labels [US1], [US2]** | Trazabilidad requirement → task | Overhead de labeling, puede ser redundante en fases |
| **Tests optional by default** | Evita overhead si no se requiere TDD | Puede olvidarse agregar tests |
| **Priority-based phases** | MVP-first, incremental delivery | Reordering difícil si priorities cambian |
| **Dependency graph separado** | Visualización clara de orden de stories | Duplicación de info (también implícito en phases) |
| **Parallel execution examples** | Guía para work planning | Puede quedar desincronizado si tasks cambian |
| **MVP = User Story 1** | Simplicidad, fuerza scope minimal | Puede ser demasiado restrictivo |
| **Story independence goal** | Reduce coupling, permite parallel work | No siempre realista (shared infra, auth, etc.) |

## 9. Comparison with Other Commands

### vs. speckit.3.plan
- **Plan**: Diseño (qué construir, arquitectura, data model)
- **Tasks**: Ejecución (orden, steps, file paths)
- **Input**: Tasks consume plan + spec
- **Output**: Plan genera design artifacts; Tasks genera execution breakdown

### vs. speckit.5.analyze
- **Tasks**: Generación de task list
- **Analyze**: Validación cross-artifact (spec vs. plan vs. tasks)
- **Handoff**: Tasks → Analyze (analyze valida task output)

### vs. speckit.6.implement
- **Tasks**: Planning (generar lista de tareas)
- **Implement**: Execution (ejecutar las tareas)
- **Handoff**: Tasks → (Analyze) → Implement

### vs. speckit.util.checklist
- **Tasks**: Execution breakdown (qué código escribir)
- **Checklist**: Quality validation (qué validar en requirements)
- **Propósito**: Tasks es para developers; Checklist es para spec authors

### vs. speckit.util.issues
- **Tasks**: Genera tasks.md (archivo local)
- **Issues**: Convierte tasks.md → GitHub issues (external system)
- **Relación**: Issues consume tasks como input

## 10. Learnings for Standardization

### Patrón 1: User-Story-Centric Organization
**Adoptar**: Organizar work breakdown por user story, no por tipo técnico.
**Aplicar a**: Cualquier task generation, project planning.
**Razón**: Trazabilidad, incrementos independientes, foco en valor.

**Anti-pattern**:
```markdown
## All Models
- [ ] T001 Create User model
- [ ] T002 Create Post model

## All Services
- [ ] T003 Create UserService
- [ ] T004 Create PostService
```

**Pattern correcto**:
```markdown
## User Story 1: User Registration
- [ ] T001 [US1] Create User model in src/models/user.py
- [ ] T002 [US1] Create UserService in src/services/user_service.py
- [ ] T003 [US1] Create /register endpoint in src/api/auth.py

## User Story 2: Create Posts
- [ ] T004 [US2] Create Post model in src/models/post.py
- [ ] T005 [US2] Create PostService in src/services/post_service.py
```

### Patrón 2: Strict Checklist Format
**Adoptar**: Formato estricto y parseable para task lists.
**Aplicar a**: Todos los comandos que generan work breakdown.
**Razón**: Tool integration, automation, clarity.

**Formato estándar**:
```
- [ ] [TaskID] [Marker?] [Label?] Description with file path
```

**Componentes**:
1. **Checkbox**: `- [ ]` (markdown standard)
2. **Task ID**: Sequential (T001, T002) para referencia
3. **Markers**: [P] para parallelizable
4. **Labels**: [US1], [US2] para traceability
5. **Description**: Acción clara + file path absoluto o relativo consistente

### Patrón 3: Parallel Execution Markers
**Adoptar**: Marcar explícitamente tareas que pueden ejecutarse en paralelo.
**Aplicar a**: Task lists, work planning.
**Razón**: Optimización, work distribution, timeline planning.

**Criterios para [P]**:
- Diferentes archivos
- Sin dependencias en tareas incompletas
- No requieren estado compartido

**Ejemplos**:
```markdown
- [ ] T005 [P] [US1] Create User model in src/models/user.py
- [ ] T006 [P] [US1] Write User contract test in tests/contracts/user_test.py
```
(Pueden ejecutarse en paralelo porque tocan archivos diferentes)

### Patrón 4: Dependency Graph Explicit
**Adoptar**: Documentar dependencias entre unidades de trabajo explícitamente.
**Aplicar a**: Project planning, task management.
**Razón**: Visualización, risk assessment, critical path analysis.

**Formato**:
```markdown
## Dependencies

Story Completion Order:
1. US1 (User Registration) - No dependencies
2. US2 (Create Posts) - Depends on: US1 (needs User model)
3. US3 (Comments) - Depends on: US1, US2

Critical Path: US1 → US2 → US3
Parallel Opportunities: US4 (Analytics) can start after US1 independently
```

### Patrón 5: Required vs. Optional Artifacts
**Adoptar**: Graceful degradation cuando artifacts opcionales faltan.
**Aplicar a**: Comandos que integran múltiples sources.
**Razón**: Flexibilidad, robustez, usability.

**Implementación**:
```markdown
2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack), spec.md (user stories)
   - **Optional**: data-model.md, contracts/, research.md, quickstart.md
   - Note: Not all projects have all documents. Generate based on what's available.
```

### Patrón 6: Test-Optional Pattern
**Adoptar**: Solo generar tests si explícitamente requerido.
**Aplicar a**: Task generation, code scaffolding.
**Razón**: Evitar overhead innecesario, respetar team practices.

**Detección**:
```
If spec mentions "TDD" or "test-driven" → generate test tasks
If user args include "with tests" → generate test tasks
Otherwise → skip test tasks
```

### Patrón 7: Phase Structure Standardization
**Adoptar**: Estructura de fases consistente cross-project.
**Aplicar a**: Project planning, task breakdown.
**Razón**: Predictability, onboarding, tooling.

**Estructura estándar**:
```markdown
## Phase 1: Setup
(Project initialization, dependencies, config)

## Phase 2: Foundational
(Blocking prerequisites - MUST complete before stories)

## Phase 3+: User Stories (P1, P2, P3...)
(Each story is a complete, testable increment)

## Final Phase: Polish & Cross-Cutting
(Optimization, docs, deployment)
```

### Patrón 8: MVP Scope Explicit
**Adoptar**: Identificar explícitamente MVP scope en task list.
**Aplicar a**: Project planning, sprint planning.
**Razón**: Foco, scope management, delivery predictability.

**Formato**:
```markdown
## Summary
- Total tasks: 47
- MVP scope: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 12 tasks
- Full scope: All phases = 47 tasks
```

### Anti-Patrón 1: Technical Grouping
**Evitar**: Agrupar tasks por tipo técnico (All Models, All Services, All Tests).
**Problema**: No trazabilidad a requirements, no incrementos valiosos.
**Solución**: Agrupar por user story.

### Anti-Patrón 2: Vague Task Descriptions
**Evitar**: "Create user functionality", "Implement auth".
**Problema**: No actionable, no claro qué archivos tocar.
**Solución**: "Create User model in src/models/user.py" - específico + file path.

### Anti-Patrón 3: Missing File Paths
**Evitar**: Tasks sin especificar qué archivos modificar.
**Problema**: Ambiguedad, inconsistencia en estructura de proyecto.
**Solución**: Cada task incluye file path relativo al repo root.

### Anti-Patrón 4: Implicit Dependencies
**Evitar**: Asumir que dependencies son obvias.
**Problema**: Ordering errors, blocked work, rework.
**Solución**: Dependency graph explícito + markers de dependencies en descriptions.

### Patrón de Arquitectura: Multi-Source Task Synthesis
**Concepto**: Generar tasks combinando info de múltiples artifacts.

**Sources y su contribución**:
- **spec.md** → User stories (qué construir)
- **plan.md** → Tech stack (con qué construir), structure (dónde construir)
- **data-model.md** → Entities (qué modelos crear)
- **contracts/** → Endpoints (qué APIs implementar)
- **research.md** → Decisions (cómo construir)
- **quickstart.md** → Integration scenarios (cómo testear)

**Synthesis algorithm**:
1. Extract user stories from spec (P1, P2, P3...)
2. Extract tech stack from plan (frameworks, libraries)
3. For each user story:
   - Map entities needed (from data-model)
   - Map endpoints needed (from contracts)
   - Map integration scenarios (from quickstart)
   - Generate tasks: Tests → Models → Services → Endpoints → Integration
4. Build dependency graph between stories
5. Identify parallel opportunities within stories

### Patrón de Diseño: Traceability Labels
**Concepto**: Usar labels para mantener trazabilidad requirement → task.

**Beneficios**:
- Filtrar tasks por user story
- Validar coverage (cada story tiene tasks)
- Generar reports por story
- Integration con issue trackers

**Formato**:
```markdown
- [ ] T012 [P] [US1] Create User model in src/models/user.py
         ^    ^    ^
         |    |    +-- Story label (traceability)
         |    +------- Parallel marker (execution)
         +------------ Task ID (reference)
```

### Patrón de Diseño: Parallel Execution Examples
**Concepto**: Documentar explícitamente qué tasks pueden ejecutarse en paralelo.

**Propósito**:
- Guía para developers (qué trabajar en paralelo)
- Work distribution (asignar tasks a múltiples personas)
- Timeline optimization (reducir critical path)

**Formato**:
```markdown
## Parallel Execution Examples

### User Story 1 Parallelization:
Can work simultaneously on:
- [T005] User model (src/models/user.py)
- [T006] User contract test (tests/contracts/user_test.py)
- [T007] UserService interface (src/services/user_service.py)

Sequential after above:
- [T008] UserService implementation (needs model + contract)
```

### Consideración de Escalabilidad: Sequential Task IDs
**Patrón**: IDs secuenciales (T001, T002...) en orden de ejecución.
**Razón**: Fácil referencia, claro orden, simple parsing.
**Alternativa rechazada**: UUIDs (difícil referencia), hierarchical IDs (complejidad).

### Consideración de UX: Format Validation Self-Check
**Patrón**: Comando reporta si su propio output cumple el formato.
**Razón**: Quality gate integrado, feedback inmediato.
**Formato**:
```markdown
## Report Summary
- Total tasks: 47
- Format validation: ✓ ALL tasks follow checklist format
- Coverage validation: ✓ All user stories have complete task sets
- Parallel opportunities: 23 tasks marked [P]
```
