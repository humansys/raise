# Análisis Arquitectónico: speckit.6.implement

## 1. Resumen Ejecutivo

El comando `speckit.6.implement` ejecuta la implementación completa de un feature procesando y ejecutando todas las tareas definidas en tasks.md. Opera bajo un modelo de fases secuenciales con validación de checklists pre-ejecución y soporte para ejecución paralela de tareas independientes.

**Patrón arquitectónico clave**: Phase-Based Sequential Execution con Checklist Gate y Parallel Task Support.

**Innovación principal**: Checklist validation gate ANTES de comenzar implementación - si hay checklists incompletos, el comando pregunta antes de continuar, implementando un quality gate humano.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
```

**Patrón**: Sin handoffs definidos
**Diseño**: Implement es el comando final del pipeline - después de esto, el feature está implementado.

**Filosofía**: No hay siguiente paso automático - implementación completa es el deliverable final.

### 2.2 Input Processing

**Patrón**: Single context input
- `$ARGUMENTS`: Considerado antes de proceder

**Estrategia**: Los argumentos pueden especificar opciones de ejecución (skip tests, specific phase, etc.).

### 2.3 Outline Structure

**Flujo principal**: 9 pasos con checkpoint de checklists al inicio

1. **Initialize** (prerequisite check con flags especiales)
2. **Check checklists status** (BLOCKER si incompletos)
3. **Load implementation context** (todos los design artifacts)
4. **Project Setup Verification** (crear/verificar ignore files)
5. **Parse tasks.md structure** (extraer fases, dependencies, detalles)
6. **Execute implementation** (phase-by-phase con dependencies)
7. **Implementation execution rules** (orden de ejecución)
8. **Progress tracking and error handling** (reporting + jidoka)
9. **Completion validation** (verificación final)

**Característica crítica**: Paso 2 es BLOCKER - puede detener ejecución si checklists incompletos.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **Checklist Gate** | Validar checklists ANTES de empezar implementación | Quality gate humano; shift-left validation |
| **Phase-Based Execution** | Setup → Tests → Core → Integration → Polish | Estructurar trabajo; manage dependencies |
| **Parallel Task Support** | Identificar y ejecutar tasks [P] juntas | Optimización de tiempo; concurrent work |
| **TDD Enforcement** | Tests before implementation cuando aplica | Calidad; prevent test-after antipattern |
| **Dynamic Ignore File Management** | Detectar tech stack y crear ignore files | Robustez; evitar commits no deseados |
| **Progress Tracking** | Reportar después de cada task + marcar [X] | Visibilidad; resume capability |
| **Jidoka on Failures** | Halt en task failure (non-parallel) | Parar en defectos; no acumular errores |
| **Graceful Parallel Failure** | Continue con successful, report failed [P] tasks | Optimización; no bloquear trabajo independiente |
| **Multi-Artifact Context Loading** | Cargar todos los design artifacts disponibles | Completitud de contexto; informed implementation |
| **Technology Detection** | Auto-detect tech stack para patterns correctos | Automation; reduce manual config |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json --require-tasks --include-tasks` | JSON con FEATURE_DIR, AVAILABLE_DOCS | Ensure tasks.md exists; get paths to all artifacts |
| `git rev-parse` | `--git-dir` | Git directory path o error | Detectar si repo es git (para .gitignore) |

**Patrón de integración**: Prerequisite check + technology detection.

**Innovación**: Dynamic technology detection para crear ignore files apropiados.

## 5. Validation Strategy

**Multi-checkpoint validation**:

### Checkpoint 1: Checklist Validation (Pre-Implementation)
- Scan all checklist files en checklists/ directory
- Count total vs. completed items
- Calculate overall status (PASS si todos completos)
- **BLOCKER**: Si algún checklist incompleto → ask user proceed?

**Formato del gate**:
```
| Checklist | Total | Completed | Incomplete | Status |
|-----------|-------|-----------|------------|--------|
| ux.md     | 12    | 12        | 0          | ✓ PASS |
| test.md   | 8     | 5         | 3          | ✗ FAIL |
```

### Checkpoint 2: Project Setup Verification
- Detectar tech stack (Dockerfile, package.json, etc.)
- Crear/verificar ignore files (.gitignore, .dockerignore, etc.)
- Validar essential patterns presentes

### Checkpoint 3: Phase Completion Validation
- Verificar todas las tareas de la fase completadas antes de siguiente
- Halt si non-parallel task falla

### Checkpoint 4: Final Validation (Step 9)
- Verify all required tasks completed
- Check features match spec
- Validate tests pass and coverage meets requirements
- Confirm implementation follows technical plan

**Filosofía**: Multi-layer validation - quality gate humano (checklists) + automated checks.

## 6. Error Handling Patterns

### Pattern 1: Incomplete Checklists
```
If any checklist incomplete:
- Display table with incomplete counts
- ASK: "Some checklists are incomplete. Do you want to proceed anyway? (yes/no)"
- Wait for user response
- If "no"/"wait"/"stop" → halt execution
- If "yes"/"proceed"/"continue" → continue to step 3
```
**Filosofía**: Quality gate con user override - balance between governance y pragmatism.

### Pattern 2: Sequential Task Failure
```
Halt execution if any non-parallel task fails
```
**Principio**: Jidoka - parar en defectos, no continuar acumulando errores.

### Pattern 3: Parallel Task Failure
```
For parallel tasks [P]:
- Continue with successful tasks
- Report failed ones
```
**Estrategia**: Maximize progress en trabajo independiente.

### Pattern 4: Missing Prerequisites
```
If tasks.md missing → suggest running /speckit.4.tasks
```
**Diseño**: Guidance hacia prerequisito, no generación ad-hoc.

### Pattern 5: Progress Loss Prevention
```
For completed tasks, mark off as [X] in tasks file
```
**Robustez**: Permitir resume si comando se interrumpe.

## 7. State Management

### Input State (Read-Only)
- **tasks.md** (REQUIRED): Task list completo con fases, IDs, dependencies
- **plan.md** (REQUIRED): Tech stack, arquitectura, file structure
- **data-model.md** (IF EXISTS): Entities y relationships
- **contracts/** (IF EXISTS): API specs y test requirements
- **research.md** (IF EXISTS): Technical decisions y constraints
- **quickstart.md** (IF EXISTS): Integration scenarios
- **checklists/** (IF EXISTS): Quality validation checklists

### Intermediate State (In-Memory)
- **Task phases**: Setup, Tests, Core, Integration, Polish
- **Task dependencies**: Sequential vs. parallel execution rules
- **Task details**: ID, description, file paths, [P] markers
- **Execution flow**: Order y dependency requirements
- **Progress tracking**: Tasks completed, tasks pending

### Output State (Modified Files)
- **tasks.md**: Tasks marcadas como [X] cuando completan
- **Ignore files**: Created/updated (.gitignore, .dockerignore, etc.)
- **Project structure**: Directories, files, code implementado
- **Implementation artifacts**: Todos los files especificados en tasks

### State Transitions
```
Load tasks/plan/artifacts → Validate checklists → User approves →
Setup project (ignore files) → Parse tasks → Execute Setup phase →
Execute Tests phase → Execute Core phase → Execute Integration phase →
Execute Polish phase → Validate completion → Report final status
```

**Patrón crítico**: Checklist gate ANTES de cualquier ejecución - no bypass automático.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Checklist gate pre-implementation** | Quality gate humano; catch issues before costly work | Puede bloquear exploratory spikes |
| **User override en checklists** | Balance governance y pragmatism | Puede ignorarse y acumular deuda |
| **Phase-based execution** | Manage dependencies; structured approach | Menos flexible para non-standard workflows |
| **Halt on sequential failures** | Jidoka; no acumular errores | Puede bloquear trabajo independiente |
| **Continue on parallel failures** | Maximize progress en tasks independientes | Puede acumular failures en [P] tasks |
| **Mark tasks [X] progressively** | Resume capability; progress visibility | File writes durante ejecución |
| **Dynamic ignore file creation** | Automation; reduce manual config | Puede sobrescribir custom configs |
| **Technology auto-detection** | Correct patterns por stack | Detection puede fallar en setups custom |
| **Multi-artifact context loading** | Completitud de contexto | Overhead si algunos artifacts innecesarios |
| **TDD enforcement when applicable** | Quality; prevent test-after | Overhead si tests no son necesarios |

## 9. Comparison with Other Commands

### vs. speckit.4.tasks
- **Tasks**: Planning (genera task list)
- **Implement**: Execution (ejecuta task list)
- **Input**: Implement consume tasks.md generado por tasks

### vs. speckit.5.analyze
- **Analyze**: Quality gate (valida consistency)
- **Implement**: Execution (ejecuta implementation)
- **Flow**: Analyze ANTES de implement (validación antes de costly work)

### vs. speckit.util.checklist
- **Checklist**: Genera quality validation checklists
- **Implement**: Valida checklists ANTES de ejecutar
- **Integration**: Implement usa checklists como quality gate

### vs. speckit.3.plan
- **Plan**: Genera design artifacts
- **Implement**: Ejecuta basado en design artifacts
- **Input**: Implement consume plan output (plan.md, data-model, contracts)

## 10. Learnings for Standardization

### Patrón 1: Human Quality Gate Pattern
**Adoptar**: Checklist validation ANTES de costly operations.
**Aplicar a**: Implementation, deployment, release.
**Razón**: Shift-left quality; catch issues before expensive work.

**Implementación**:
```markdown
2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files
   - Count total vs. completed items
   - Calculate overall status (PASS/FAIL)
   - **If any incomplete**:
     - Display status table
     - ASK: "Some checklists incomplete. Proceed anyway? (yes/no)"
     - Wait for user response before continuing
```

**Beneficios**:
- Catch requirement quality issues
- Prevent implementing underspecified features
- User maintains control (can override)
- Audit trail (checklist completion visible)

### Patrón 2: User Override with Explicit Consent
**Adoptar**: Gates bloqueantes con override explícito.
**Aplicar a**: Quality gates que pueden tener false positives.
**Razón**: Balance entre governance y pragmatism.

**Formato de pregunta**:
```
Display issue clearly (table, metrics, etc.)
ASK: "Do you want to proceed anyway? (yes/no)"
Accept variations: "yes"/"proceed"/"continue" vs. "no"/"wait"/"stop"
```

### Patrón 3: Phase-Based Execution
**Adoptar**: Organizar ejecución en fases con dependencies claras.
**Aplicar a**: Workflows complejos multi-step.
**Razón**: Manage dependencies, progress tracking, clarity.

**Fases estándar**:
```markdown
1. Setup: Initialize structure, dependencies, config
2. Tests: Write tests ANTES de implementation (TDD)
3. Core: Implement models, services, core logic
4. Integration: Database, middleware, external services
5. Polish: Optimization, documentation, cleanup
```

### Patrón 4: Jidoka on Sequential Failures
**Adoptar**: Halt ejecución en task failures secuenciales.
**Aplicar a**: Workflows con dependencies entre steps.
**Razón**: Parar en defectos; no acumular errores.

**Implementación**:
```markdown
8. Progress tracking and error handling:
   - Halt execution if any non-parallel task fails
   - Provide clear error messages with context
   - Suggest next steps if implementation cannot proceed
```

### Patrón 5: Graceful Parallel Failure Handling
**Adoptar**: Continue con successful tasks, report failed en parallel work.
**Aplicar a**: Tasks marcadas como parallelizable.
**Razón**: Maximize progress en trabajo independiente.

**Implementación**:
```markdown
For parallel tasks [P]:
- Continue with successful tasks
- Report failed ones at end of phase
- Don't block other parallel work
```

### Patrón 6: Progressive State Persistence
**Adoptar**: Marcar progreso incrementalmente durante ejecución.
**Aplicar a**: Long-running processes que pueden interrumpirse.
**Razón**: Resume capability, progress visibility, debugging.

**Formato**:
```markdown
8. Progress tracking:
   - Report progress after each completed task
   - **IMPORTANT**: Mark completed tasks as [X] in tasks file
   - Enable resume if execution interrupted
```

### Patrón 7: Dynamic Technology Detection
**Adoptar**: Auto-detect tech stack y aplicar patterns apropiados.
**Aplicar a**: Project setup, configuration, tooling.
**Razón**: Automation, reduce manual config, correctness.

**Implementación**:
```markdown
4. **Project Setup Verification**:
   **Detection & Creation Logic**:
   - Check if git repo → create/verify .gitignore
   - Check if Dockerfile exists → create/verify .dockerignore
   - Check if .eslintrc exists → create/verify .eslintignore
   - Apply technology-specific patterns from plan.md
```

**Patterns por tecnología**:
```markdown
**Common Patterns by Technology** (from plan.md tech stack):
- **Node.js**: `node_modules/`, `dist/`, `.env*`
- **Python**: `__pycache__/`, `*.pyc`, `.venv/`
- **Java**: `target/`, `*.class`, `.gradle/`
- **Universal**: `.DS_Store`, `Thumbs.db`, `.vscode/`
```

### Patrón 8: Multi-Artifact Context Loading
**Adoptar**: Cargar todos los design artifacts disponibles antes de ejecución.
**Aplicar a**: Implementation, code generation.
**Razón**: Completitud de contexto; informed decisions.

**Estructura**:
```markdown
3. Load implementation context:
   - **REQUIRED**: tasks.md, plan.md
   - **IF EXISTS**: data-model.md, contracts/, research.md, quickstart.md
   - Graceful degradation si optional artifacts faltan
```

### Patrón 9: TDD Enforcement When Applicable
**Adoptar**: Ejecutar test tasks ANTES de implementation tasks.
**Aplicar a**: Features que requieren TDD approach.
**Razón**: Quality, prevent test-after antipattern.

**Detección**:
```markdown
7. Implementation execution rules:
   - **Tests before code**: If you need to write tests for contracts, entities, integration
   - Execute test tasks before their corresponding implementation tasks
```

### Patrón 10: Completion Validation Multi-Dimensional
**Adoptar**: Validar múltiples dimensiones al completar.
**Aplicar a**: Workflows complejos con múltiples deliverables.
**Razón**: Thoroughness, quality assurance.

**Dimensiones**:
```markdown
9. Completion validation:
   - All required tasks completed
   - Implemented features match spec
   - Tests pass and coverage meets requirements
   - Implementation follows technical plan
   - Report final status with summary
```

### Anti-Patrón 1: Auto-Bypass Quality Gates
**Evitar**: Continuar automáticamente ignorando checklists incompletos.
**Problema**: Quality issues pasan a production, accumulate debt.
**Solución**: Explicit user consent pattern.

### Anti-Patrón 2: Continue on All Failures
**Evitar**: Continuar ejecución cuando tareas secuenciales fallan.
**Problema**: Acumular errores, trabajo basado en foundations incorrectas.
**Solución**: Jidoka - halt on sequential failures.

### Anti-Patrón 3: Manual Ignore File Setup
**Evitar**: Requerir usuario crear .gitignore, .dockerignore manualmente.
**Problema**: Step olvidado → commits no deseados (node_modules, .env).
**Solución**: Dynamic detection y creation.

### Anti-Patrón 4: No Progress Tracking
**Evitar**: No marcar qué tasks completaron.
**Problema**: Si comando interrumpe, perder progreso, re-ejecutar todo.
**Solución**: Mark tasks [X] progressively.

### Patrón de Arquitectura: Gated Phase Pipeline
**Concepto**: Pipeline con quality gates entre fases costosas.

**Estructura**:
```
Checklist Gate → Setup Phase → Tests Phase → Core Phase → Integration Phase → Polish Phase → Validation
     ↓                                                                                            ↓
  User approves                                                                         Final verification
```

**Gates**:
- **Pre-execution**: Checklist validation (human gate)
- **Between phases**: Phase completion validation (automated)
- **Post-execution**: Final validation (automated + manual review)

**Beneficios**:
- Catch issues early (shift-left)
- Prevent costly rework
- Progress visibility
- Resume capability

### Patrón de Diseño: Technology-Aware Automation
**Concepto**: Detectar tech stack y aplicar patterns específicos automáticamente.

**Components**:
1. **Detection**: Scan project files (package.json, Dockerfile, etc.)
2. **Pattern Selection**: Map detected tech → ignore patterns, configs, etc.
3. **Application**: Create/update files con patterns apropiados
4. **Preservation**: No sobrescribir custom configs

**Aplicaciones**:
- Ignore file patterns
- Linter configurations
- Build tool setup
- CI/CD templates

### Patrón de Diseño: Parallel vs. Sequential Task Execution
**Concepto**: Diferentes estrategias de error handling según dependencies.

**Sequential Tasks** (sin [P] marker):
- Halt on failure
- No continuar fase
- Report error con context
- Suggest remediation

**Parallel Tasks** (con [P] marker):
- Continue con successful
- Collect failures
- Report all failures at end
- Don't block independent work

**Detección**: Presencia de `[P]` marker en task description.

### Consideración de Robustez: Verify Before Append
**Patrón**: Al actualizar ignore files, verificar patterns existentes antes de append.
**Razón**: No duplicar, respetar custom additions.

**Implementación**:
```markdown
**If ignore file already exists**:
- Verify it contains essential patterns
- Append ONLY missing critical patterns

**If ignore file missing**:
- Create with full pattern set for detected technology
```

### Consideración de UX: Progress Reporting
**Patrón**: Reportar progress después de cada task completada.
**Razón**: Visibility, user confidence, debugging.

**Formato**:
```
✓ [T001] Create project structure - COMPLETED
✓ [T002] Install dependencies - COMPLETED
✗ [T003] Configure database - FAILED (connection error)
```

### Consideración de Escalabilidad: Checklist Directory Scan
**Patrón**: Scan todos los checklists en directory, no hardcode nombres.
**Razón**: Soportar múltiples checklists custom.

**Implementación**:
```markdown
2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan ALL checklist files in the checklists/ directory
   - For each checklist, count total/completed/incomplete
   - Calculate overall status
```
