# Análisis Arquitectónico: speckit.3.plan

## 1. Resumen Ejecutivo

El comando `speckit.3.plan` ejecuta el workflow de planning técnico que transforma una especificación funcional en artefactos de diseño ejecutables. Opera en 2 fases estructuradas (Research + Design) con validación constitucional integrada.

**Patrón arquitectónico clave**: Template-Driven Workflow Execution con constitution-based validation gates.

**Innovación principal**: Integración automática de agent context update - el comando actualiza el contexto del agente con nuevas tecnologías, manteniendo sincronización entre plan y capacidades del agente.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs:
  - label: Create Tasks
    agent: speckit.4.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.util.checklist
    prompt: Create a checklist for the following domain...
```

**Patrón**: Dual handoffs con prioridades implícitas
- **Primary handoff**: `speckit.4.tasks` (send: true) - flujo principal
- **Alternative handoff**: `speckit.util.checklist` - flujo de validación opcional

**Diseño**: Permite tanto avance lineal (tasks) como validación lateral (checklist).

### 2.2 Input Processing

**Patrón**: Single input source
- `$ARGUMENTS`: Usado directamente en el workflow

**Estrategia**: A diferencia de clarify, plan no tiene priorización compleja de input - los args se consideran pero el driver principal es el spec.

### 2.3 Outline Structure

**Flujo principal**: 4 pasos de alto nivel con 2 fases internas

1. **Setup** (prerequisite check via JSON con modo especial)
2. **Load context** (spec + constitution + template)
3. **Execute plan workflow** (2 fases: Research → Design)
4. **Stop and report** (no continúa a implementación)

**Decisión crítica**: El comando termina después de Phase 2 planning - no ejecuta implementación.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **Template-Driven Execution** | Cargar IMPL_PLAN template y seguir su estructura | Consistencia cross-project; separar formato de lógica |
| **Two-Phase Workflow** | Phase 0 (Research) → Phase 1 (Design) | Resolver unknowns antes de diseñar |
| **Constitution-Based Validation** | Constitution Check antes y después de diseño | Governance integrado; shift-left compliance |
| **NEEDS CLARIFICATION Pattern** | Marcar unknowns explícitamente → resolver en research | Visibilidad de gaps; no avanzar con incertidumbre |
| **Agent Context Sync** | Auto-actualizar agent context con tech stack | Mantener agent capabilities alineadas con plan |
| **ERROR on Gate Violations** | Fallar hard si violaciones no justificadas | Jidoka aplicado: parar en defectos |
| **Artifact Generation Pipeline** | research.md → data-model.md → contracts → quickstart | Dependencias claras entre artefactos |
| **Multi-Artifact Output** | Generar múltiples archivos en un solo comando | Completitud; evitar múltiples runs manuales |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `setup-plan.sh` | `--json` | JSON con FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH | Setup específico para planning con paths y contexto git |
| `update-agent-context.sh` | `claude` (agent type) | Agent-specific file updated | Sincronizar capacidades del agente con tech stack |

**Patrón de integración**: Specialized setup script + agent sync script.

**Innovación**: `setup-plan.sh` es específico para este comando (no generic check-prerequisites) - encapsula lógica de setup del plan.

**Diseño**: Agent context update es AUTOMÁTICO (no requiere acción manual) - el comando lo llama después de generar contracts.

## 5. Validation Strategy

**Multi-gate validation**:

### Gate 1: Constitution Check (Pre-Design)
- Ejecutar antes de Phase 0
- Validar spec contra los principios de constitution
- **ERROR** si violaciones unjustified

### Gate 2: Research Completeness (End of Phase 0)
- Verificar que todos los NEEDS CLARIFICATION están resueltos
- **ERROR** si unknowns persisten

### Gate 3: Constitution Re-Check (Post-Design)
- Re-evaluar constitution después de decisiones técnicas
- Capturar si el diseño introdujo violaciones

### Gate 4: Artifact Completeness
- Verificar existencia de artefactos generados
- Validar estructura de data-model, contracts, quickstart

**Filosofía**: Multi-checkpoint validation en puntos clave del workflow.

## 6. Error Handling Patterns

### Pattern 1: Gate Violations
```
ERROR on gate failures or unresolved clarifications
```
**Filosofía**: Fail fast con visibilidad explícita de violaciones.

### Pattern 2: Unresolved NEEDS CLARIFICATION
```
If unknowns persist after Phase 0 → ERROR
```
**Principio**: No avanzar a diseño con incertidumbres fundamentales.

### Pattern 3: Missing Prerequisites
```
If spec missing → suggest running /speckit.1.specify
```
**Diseño**: Guidance hacia comando correcto, no creación ad-hoc.

### Pattern 4: Agent Context Update Failure
```
Script detects AI agent type; updates appropriate file
Preserves manual additions between markers
```
**Estrategia**: Inteligencia integrada en el script para manejar múltiples agentes.

## 7. State Management

### Input State
- **FEATURE_SPEC**: Requerimientos funcionales (read-only)
- **Constitution**: Principios y gates (read-only)
- **IMPL_PLAN template**: Estructura vacía (read)

### Intermediate State
- **research.md**: Decisiones + rationale (write)
- **Technical Context section**: NEEDS CLARIFICATION markers (write)

### Output State
- **IMPL_PLAN**: Plan completo con todas secciones (write)
- **data-model.md**: Entidades + relaciones (write)
- **contracts/**: API specs (write)
- **quickstart.md**: Escenarios de integración (write)
- **Agent context file**: Actualizado con tech stack (write)

### State Transitions
```
Load spec/constitution → Fill Technical Context → Mark NEEDS CLARIFICATION →
Research unknowns → Resolve clarifications → Design data model →
Generate contracts → Update agent context → Re-validate constitution
```

**Patrón crítico**: Two-phase state evolution - unknowns → resolutions → design.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Two-phase workflow (Research → Design)** | Resolver unknowns antes de decisiones técnicas | Más upfront time; mejor calidad de diseño |
| **NEEDS CLARIFICATION pattern** | Visibilidad explícita de gaps | Requiere discipline para marcar y resolver |
| **Constitution check pre + post design** | Detectar violaciones early + catch diseño inadecuado | Overhead de doble validación |
| **ERROR on gate violations** | Jidoka: parar en defectos | Puede bloquear progreso en exploratory spikes |
| **Auto-generate multiple artifacts** | Completitud en un solo run | Comando más complejo; más difícil de debuggear |
| **Auto-update agent context** | Mantener sync sin acción manual | Coupling con agent-specific tooling |
| **Template-driven execution** | Consistencia cross-project | Menos flexibilidad para formatos custom |
| **Specialized setup script** | Encapsular lógica específica de planning | Más scripts que mantener |
| **Stop after Phase 2** | Separar planning de implementation | Requiere handoff manual a implement |
| **Absolute paths requirement** | Evitar ambiguedad en multi-repo contexts | Verbosity en comandos |

## 9. Comparison with Other Commands

### vs. speckit.2.clarify
- **Clarify**: Resuelve ambigüedades funcionales/de dominio
- **Plan**: Resuelve decisiones técnicas/arquitectónicas
- **Input**: Plan consume output de clarify (spec refinado)

### vs. speckit.4.tasks
- **Plan**: Genera DISEÑO (qué construir, cómo estructurar)
- **Tasks**: Genera EJECUCIÓN (orden, pasos, dependencies)
- **Handoff**: Plan → Tasks (tasks consume plan + spec)

### vs. speckit.1.specify
- **Specify**: Creación de spec desde natural language
- **Plan**: Transformación de spec a diseño técnico
- **Relación**: Sequential pipeline (specify → clarify → plan)

### vs. speckit.5.analyze
- **Plan**: Generación de artefactos de diseño
- **Analyze**: Validación de consistencia cross-artifacts
- **Timing**: Plan ANTES de analyze (analyze consume plan output)

## 10. Learnings for Standardization

### Patrón 1: Two-Phase Execution (Research → Action)
**Adoptar**: Separar resolución de unknowns de ejecución principal.
**Aplicar a**: Cualquier comando con decisiones técnicas complejas.
**Razón**: Mejor calidad de output, decisiones más informadas, menos retrabajo.

**Estructura estándar**:
```markdown
## Phase 0: Research & Unknowns
1. Identify NEEDS CLARIFICATION items
2. Research each unknown
3. Document decisions + rationale
4. Resolve all unknowns before Phase 1

## Phase 1: Execution
[Main workflow here]
```

### Patrón 2: NEEDS CLARIFICATION Marker
**Adoptar**: Marcar unknowns explícitamente en lugar de "TODO" o ignorar.
**Aplicar a**: Cualquier proceso de diseño o planning.
**Razón**: Visibilidad, trazabilidad, enforcement de resolución.

**Formato estándar**:
```markdown
**Technology Choice**: NEEDS CLARIFICATION
**Integration Pattern**: NEEDS CLARIFICATION (API vs. events?)
```

### Patrón 3: Constitution-Based Validation Gates
**Adoptar**: Validar contra constitution en puntos clave del workflow.
**Aplicar a**: Comandos que toman decisiones significativas.
**Razón**: Governance as code, shift-left compliance, trazabilidad de principios.

**Implementación**:
```markdown
## Constitution Check (Pre-Design)
- §1 Principle X: [PASS/FAIL] - Rationale
- §2 Principle Y: [PASS/FAIL] - Rationale

## Constitution Check (Post-Design)
[Re-evaluate after technical decisions]
```

### Patrón 4: Auto-Update Agent Context
**Adoptar**: Comandos que introducen nuevas tecnologías deben actualizar agent context.
**Aplicar a**: Plan, research, tech decisions.
**Razón**: Mantener agent capabilities sync con project stack.

**Implementación**:
```bash
# After generating design artifacts
.specify/scripts/bash/update-agent-context.sh claude
```

### Patrón 5: Specialized Setup Scripts
**Adoptar**: Scripts de setup específicos por comando cuando la lógica difiere significativamente.
**Aplicar a**: Comandos con prerequisites únicos.
**Razón**: Encapsulación, mantainability, clarity.

**Ejemplo**:
- `check-prerequisites.sh` - Generic (usado por clarify, tasks, analyze)
- `setup-plan.sh` - Specialized (usado solo por plan)

### Patrón 6: Multi-Artifact Generation
**Adoptar**: Generar múltiples artefactos relacionados en un solo comando.
**Aplicar a**: Workflows donde artefactos tienen dependencias claras.
**Razón**: Completitud, evitar múltiples manual runs, consistencia.

**Estructura**:
```markdown
Phase 1: Design & Contracts
1. Generate data-model.md
2. Generate contracts/ (depende de data-model)
3. Generate quickstart.md (depende de contracts)
4. Update agent context (depende de todo)
```

### Patrón 7: ERROR on Blocking Conditions
**Adoptar**: Fallar explícitamente (ERROR) en condiciones que bloquean progreso.
**Aplicar a**: Todos los comandos con validation gates.
**Razón**: Jidoka - parar en defectos, no acumular errores.

**Ejemplos**:
```
ERROR: Constitution gate violation (§4 - Validation Gates)
ERROR: Unresolved NEEDS CLARIFICATION items in Technical Context
ERROR: Missing spec.md (run /speckit.1.specify first)
```

### Patrón 8: Stop-and-Report Pattern
**Adoptar**: Comandos terminan con reporte explícito, no continúan automáticamente.
**Aplicar a**: Comandos intermedios en pipeline (no finales).
**Razón**: Usuario controla handoffs, puede revisar antes de continuar.

**Formato estándar**:
```markdown
4. **Stop and report**: Command ends after Phase 2 planning. Report:
   - Branch: <current-branch>
   - IMPL_PLAN path: <absolute-path>
   - Generated artifacts:
     - research.md
     - data-model.md
     - contracts/ (N files)
     - quickstart.md
   - Agent context: Updated with [tech list]

   Suggested next: /speckit.4.tasks
```

### Anti-Patrón 1: Advancing with Unknowns
**Evitar**: Proceder a diseño con NEEDS CLARIFICATION sin resolver.
**Problema**: Decisiones basadas en assumptions incorrectas, retrabajo.
**Solución**: ERROR enforcement en Phase 0 → Phase 1 transition.

### Anti-Patrón 2: Single Constitution Check
**Evitar**: Validar constitution solo una vez (pre o post).
**Problema**: Perder violaciones introducidas por diseño técnico.
**Solución**: Dual checkpoint (pre + post).

### Anti-Patrón 3: Manual Agent Context Update
**Evitar**: Requerir usuario ejecute script manualmente.
**Problema**: Step olvidado → agent desincronizado → respuestas incorrectas.
**Solución**: Auto-execute en el comando.

### Patrón de Arquitectura: Template-Driven Workflow
**Concepto**: Usar templates estructurados para guiar ejecución de workflows complejos.

**Componentes**:
1. **Template**: Estructura vacía con secciones y guías
2. **Executor**: Comando que llena el template paso a paso
3. **Validation**: Gates que verifican completitud de secciones

**Beneficios**:
- Consistencia cross-project
- Documentación de proceso
- Onboarding simplificado
- Testability (verificar secciones requeridas)

**Aplicabilidad**: Planning, documentation, reports, ADRs.

### Patrón de Diseño: Artifact Pipeline
**Concepto**: Generar artefactos en orden de dependencia explícito.

**Ejemplo del comando**:
```
spec.md → research.md → data-model.md → contracts/ → quickstart.md → agent context
```

**Dependencias**:
- contracts depende de data-model (necesita entities)
- quickstart depende de contracts (necesita endpoints)
- agent context depende de todo (necesita tech stack completo)

**Enforcement**:
```markdown
Phase 1: Design & Contracts
1. Extract entities from spec → data-model.md
2. Generate API contracts from requirements (uses data-model) → contracts/
3. Generate quickstart scenarios (uses contracts) → quickstart.md
4. Update agent context (uses tech from all above)
```

### Consideración de Escalabilidad: Absolute Paths
**Patrón**: Requerir absolute paths en todos los comandos.
**Razón**: Multi-repo contexts, script execution desde diferentes directorios.
**Implementación**: Setup scripts retornan absolute paths en JSON.

### Consideración de Robustez: Preserve Manual Additions
**Patrón**: Agent context update preserva contenido manual entre markers.
**Razón**: Usuario puede agregar notas/context custom - no sobrescribir.
**Implementación**: Scripts usan markers para delimitar secciones auto-generated.

### Patrón de UX: Clear Handoff Recommendations
**Patrón**: Reporte final sugiere explícitamente next command.
**Beneficio**: Guía flujo sin forzar, usuario mantiene control.
**Formato**:
```
Suggested next: /speckit.4.tasks
Alternative: /speckit.util.checklist (for validation before tasks)
```
