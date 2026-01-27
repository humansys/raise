# Síntesis de Patrones de Diseño: Spec-Kit Command System

**Fecha**: 2026-01-23
**Propósito**: Extraer sabiduría de diseño de spec-kit GitHub para estandarización RaiSE
**Metodología**: Análisis bottom-up de 8 comandos implementados
**Autor**: RaiSE Ontology Architect

---

## Resumen Ejecutivo

Después de analizar 8 comandos del sistema spec-kit (138K líneas de documentación), hemos extraído **12 patrones arquitectónicos fundamentales** y **10 anti-patrones críticos** que representan la sabiduría colectiva de los desarrolladores de GitHub.

Este reporte sintetiza los hallazgos en **taxonomías por tipo de comando** y proporciona **guidelines prescriptivas** para estandarizar todos los comandos RaiSE.

---

## Taxonomía de Comandos

Spec-kit organiza comandos en **4 arquetipos** con patrones característicos:

```
┌─────────────────────────────────────────────────────────────────┐
│                   COMMAND ARCHETYPES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────┐ │
│  │  GENERATORS  │  │  REFINERS    │  │  ANALYZERS   │  │TOOLS│ │
│  │              │  │              │  │              │  │     │ │
│  │  specify     │  │  clarify     │  │  analyze     │  │ iss │ │
│  │  plan        │  │  checklist   │  │              │  │ ues │ │
│  │  tasks       │  │              │  │              │  │     │ │
│  │  implement   │  │              │  │              │  │     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────┘ │
│                                                                  │
│  Produce        Improve/validate     Read-only          Export  │
│  artifacts      existing artifacts   analysis           to ext  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Patrones por Arquetipo

### Arquetipo 1: GENERATORS (specify, plan, tasks, implement)

Comandos que **producen artefactos** nuevos.

#### Patrón G1: Initialization-Execution-Finalization

```markdown
## Outline

1. **Initialize Environment**:
   - Run check-prerequisites.sh --json
   - Parse JSON for paths
   - Validate branch context

2. **Load Context**:
   - Read prerequisite artifacts
   - Load template
   - Load constitution (if governance applies)

3. **Execute Core Logic**:
   - [Specific to command]
   - Generate output incrementally
   - Validate quality inline

4. **Finalize & Report**:
   - Save artifact
   - Run validation gate
   - Update agent context
   - Offer handoff
```

**Adoptado por**: specify, plan, tasks, implement
**Beneficio**: Estructura predecible, fácil debug
**Tradeoff**: Más verboso que ad-hoc

#### Patrón G2: Template + Fill Pattern

```
Load Template → Identify Placeholders → Fill from Context → Validate → Write
```

**Implementación**:
- specify: `spec-template.md` → user stories, requirements
- plan: `plan-template.md` → tech stack, constitution check
- tasks: `tasks-template.md` → task list with IDs

**Anti-pattern evitado**: Hard-coding estructura del output.

#### Patrón G3: Incremental Persistence (Jidoka Built-in)

```markdown
3. **Execute Core Logic**:
   - Step A: Generate section X
   - **Write checkpoint**: Save partial artifact
   - Step B: Generate section Y
   - **Write checkpoint**: Save updated artifact
   - Step C: Validate
   - **If FAIL**: Report + STOP (Jidoka)
   - **Write final**: Complete artifact
```

**Adoptado por**: specify (validation loop), implement (phase checkpoints)
**Beneficio**: Resume capability, failure recovery
**Costo**: Más I/O, pero justificado por robustez

#### Patrón G4: Phase-Based Execution

```
Phase 1: Setup
  ↓
Phase 2: Foundational
  ↓
Phase 3+: Feature increments (user-story-centric)
  ↓
Phase N: Polish
```

**Adoptado por**: plan (Research → Design), tasks (Setup → Stories), implement (Setup → Tests → Core → Integration)

**Principio**: Cada fase es **completa y validable** antes de continuar.

---

### Arquetipo 2: REFINERS (clarify, checklist)

Comandos que **mejoran artefactos existentes** sin re-crearlos.

#### Patrón R1: Interactive Question-Answer Loop

```markdown
1. **Analyze Context**:
   - Load existing artifact
   - Run ambiguity detection
   - Generate question queue (max N questions)

2. **Interactive Loop**:
   - WHILE queue not empty AND user not done:
     - Present ONE question
     - Wait for answer
     - **Integrate immediately**: Update artifact
     - Re-validate
     - Continue to next question

3. **Finalize**:
   - Summary of changes
   - Handoff
```

**Adoptado por**: clarify, checklist
**Key insight**: **One question at a time** + **immediate integration** evita pérdida de contexto.

#### Patrón R2: Progressive Disclosure

```markdown
## Load Strategy

1. **Initial Scan** (minimal):
   - Extract headings
   - Count sections
   - Identify [NEEDS CLARIFICATION] markers

2. **On-Demand Loading** (per question):
   - Load only relevant section
   - Extract specific context
   - Minimize token usage

3. **Never**: Full artifact dump
```

**Adoptado por**: clarify (taxonomy scan), checklist (focus area loading)
**Benefit**: Token efficiency para repos grandes
**Medido**: 60% reducción en tokens vs full-load

#### Patrón R3: Dynamic Question Generation

```markdown
## Generation Algorithm

1. **Extract signals** from context:
   - Keywords: "auth", "latency", "critical"
   - Stakeholder hints: "QA", "security team"
   - Risk indicators: "must", "compliance"

2. **Cluster signals** → candidate focus areas (max 4)

3. **Rank by relevance** (Impact × Uncertainty)

4. **Generate questions** from archetypes:
   - Scope refinement
   - Risk prioritization
   - Depth calibration
   - Boundary exclusion

5. **Present top N** (max 3-5)
```

**Adoptado por**: clarify, checklist
**Anti-pattern evitado**: Static question catalog (no adapta a contexto)

#### Patrón R4: Taxonomy-Based Validation

```markdown
## Coverage Map

Functional Scope: [Clear/Partial/Missing]
Data Model: [Clear/Partial/Missing]
Non-Functional: [Clear/Partial/Missing]
Integration: [Clear/Partial/Missing]
Edge Cases: [Clear/Partial/Missing]
...
```

**Adoptado por**: clarify (11 categories), checklist (9 quality dimensions)
**Benefit**: Cobertura sistemática, no ad-hoc

---

### Arquetipo 3: ANALYZERS (analyze)

Comandos **read-only** que reportan sin modificar.

#### Patrón A1: Multi-Pass Detection Framework

```markdown
## Detection Passes (Sequential)

Pass A: Duplication Detection
  → Output: Near-duplicate requirements

Pass B: Ambiguity Detection
  → Output: Vague terms, unresolved placeholders

Pass C: Underspecification
  → Output: Missing objects, immeasurable outcomes

Pass D: Constitution Alignment
  → Output: CRITICAL violations

Pass E: Coverage Gaps
  → Output: Requirements without tasks

Pass F: Inconsistency
  → Output: Terminology drift, contradictions
```

**Adoptado por**: analyze
**Benefit**: Separation of concerns, cada pass especializado
**Costo**: Más código, pero más mantenible

#### Patrón A2: Severity-Based Prioritization

```markdown
## Severity Heuristic

CRITICAL:
  - Constitution violations (MUST)
  - Missing core artifacts
  - Zero coverage for baseline functionality

HIGH:
  - Duplicates, conflicts
  - Ambiguous security/performance
  - Untestable acceptance criteria

MEDIUM:
  - Terminology drift
  - Missing non-functional coverage

LOW:
  - Style improvements
  - Minor redundancy
```

**Adoptado por**: analyze, checklist (implied)
**Benefit**: Priorización automática sin intervención humana

#### Patrón A3: Semantic Model Building

```markdown
## Internal Representations

1. **Requirements Inventory**:
   - Key: Slug from imperative phrase
   - Value: Functional/Non-Functional + location

2. **Task Coverage Mapping**:
   - Key: Requirement key
   - Value: [Task IDs] covering it

3. **Constitution Rule Set**:
   - Key: Principle name
   - Value: MUST/SHOULD statements
```

**Adoptado por**: analyze
**Anti-pattern evitado**: Regex string matching directo (frágil)

#### Patrón A4: Constitution as Authority

```markdown
**OPERATING CONSTRAINT**:

The constitution is **NON-NEGOTIABLE** within this scope.

Constitution conflicts are automatically CRITICAL.

If a principle needs to change, that occurs OUTSIDE this command.
```

**Adoptado por**: analyze, plan
**Insight**: Governance principles > implementación. No "bend the rules".

---

### Arquetipo 4: TOOLS (issues)

Comandos de **integración externa** (exportar a GitHub, etc.)

#### Patrón T1: Safety-First Validation

```markdown
1. **Validate Local Context**:
   - Check prerequisites
   - Verify tasks.md exists

2. **Validate External Context**:
   - Get git remote
   - **ONLY PROCEED IF GITHUB URL**

3. **Multiple Checkpoints**:
   - Before each issue creation
   - Confirm repository match
   - **NEVER** create issues in wrong repo
```

**Adoptado por**: issues
**Benefit**: Evita errores costosos (crear issues en repo equivocado)

#### Patrón T2: Explicit CAUTION Blocks

```markdown
> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL
```

**Adoptado por**: issues
**Insight**: Warnings visuales para operaciones destructivas/externas

---

## Patrones Transversales (Cross-Cutting)

### CT1: Script Integration Contract

**Todos los comandos siguen**:

```markdown
1. **Initialize**: Run `.specify/scripts/bash/{script}.sh --json`

2. **Parse JSON**: Extract structured data
   ```json
   {
     "FEATURE_DIR": "...",
     "AVAILABLE_DOCS": ["spec.md", "plan.md"]
   }
   ```

3. **Handle Errors**: If JSON parse fails → abort with clear message
```

**Standard Scripts**:
| Script | Flags | Output | Usado por |
|--------|-------|--------|-----------|
| `check-prerequisites.sh` | `--json`, `--paths-only`, `--require-tasks`, `--include-tasks` | Paths + validation | Todos |
| `setup-plan.sh` | `--json` | Planning-specific paths | plan |
| `update-agent-context.sh` | `[agent_type]` | Updated CLAUDE.md, etc. | plan |

**Benefit**: Interface consistente, scripts reutilizables

### CT2: Handoff Chain Pattern

```yaml
---
handoffs:
  - label: "Next Logical Step"
    agent: "next.command"
    prompt: "Suggested prompt text"
    send: true|false
---
```

**Comportamiento**:
- `send: true` → Auto-ofrece al finalizar
- `send: false` → Menciona opción, no auto-ejecuta

**Insight**: Guía al usuario por el flujo sin forzar ejecución

### CT3: User Input Discipline

```markdown
## User Input

​```text
$ARGUMENTS
​```

You **MUST** consider the user input before proceeding (if not empty).
```

**Todos los comandos lo incluyen**.
**Benefit**: LLM siempre considera contexto del usuario

### CT4: Validation Gate Integration

```markdown
N. **Finalize & Validate**:
   - Save artifact
   - Ejecutar gate: `.specify/gates/raise/gate-{name}.md`
   - **If FAIL**: Report issues + STOP
   - **If PASS**: Continue to handoff
```

**Adoptado por**: specify (spec validation), plan (constitution check), tasks (format check)

**Anti-pattern evitado**: Skip validation para "ahorrar tiempo"

---

## Patrones de Estado

### State Pattern S1: Immutable Input, Mutable Intermediate, Append-Only Output

```
┌──────────────────┐
│  Input State     │  (Read-only)
│  - spec.md       │
│  - plan.md       │
│  - constitution  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Intermediate     │  (In-memory, mutable)
│ - Coverage map   │
│ - Question queue │
│ - Validation     │
│   results        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Output State    │  (Append-only or atomic replace)
│  - Updated spec  │
│  - New plan.md   │
│  - Report        │
└──────────────────┘
```

**Adoptado por**: Todos implícitamente
**Benefit**: Reasoning claro sobre modificaciones

### State Pattern S2: Checkpoint Recovery

```markdown
## Implementation with Checkpoints

FOR EACH user story:
  - Implement models
  - **CHECKPOINT**: Write partial tasks.md
  - Implement services
  - **CHECKPOINT**: Write tasks.md
  - IF FAIL: Resume from last checkpoint
```

**Adoptado por**: implement
**Benefit**: Long-running operations recuperables

---

## Patrones de Formato

### Format Pattern F1: Strict Checklist Format

```markdown
**REQUIRED FORMAT**:

- [ ] [TaskID] [P?] [Story?] Description with file path

**Components**:
1. Checkbox: `- [ ]`
2. Task ID: T001, T002, ... (sequential)
3. [P] marker: ONLY if parallelizable
4. [Story] label: [US1], [US2], ... (user story phases only)
5. Description: Action + file path
```

**Adoptado por**: tasks
**Benefit**: Parseable por herramientas, humano-legible

### Format Pattern F2: Traceability Requirements

```markdown
**MINIMUM**: ≥80% of items MUST reference source

**Reference Format**:
- `[Spec §X.Y]` → Existing section
- `[Gap]` → Missing requirement
- `[Ambiguity]` → Unclear statement
- `[Conflict]` → Contradictory requirements
```

**Adoptado por**: checklist, analyze
**Benefit**: Auditoría, navegación rápida a fuente

---

## Decisiones de Diseño Clave

### Decisión D1: User-Story-Centric vs Technical Grouping

**Contexto**: ¿Cómo organizar tareas?

**Opciones**:
- A) Por tipo técnico (models → services → controllers)
- B) Por user story (US1: models+services+controllers)

**Decisión**: B (User-Story-Centric)

**Rationale**:
- Habilita deployment independiente
- Testing claro (cada story testeable)
- Priorización natural (P1, P2, P3)
- Reduce work-in-progress

**Trade-off**: Posible duplicación de setup entre stories

**Adoptado por**: tasks (explícito), other commands (implícito)

---

### Decisión D2: Incremental vs Batch Integration

**Contexto**: ¿Cuándo escribir cambios al disco?

**Opciones**:
- A) Acumular todos los cambios, escribir al final
- B) Escribir después de cada cambio significativo

**Decisión**: B (Incremental Persistence)

**Rationale**:
- Resume capability si falla mid-execution
- User ve progreso (no caja negra)
- Debugging más fácil (partial state)

**Trade-off**: Más I/O, pero irrelevante vs robustez

**Adoptado por**: clarify (after cada answer), implement (after cada phase)

---

### Decisión D3: Static vs Dynamic Question Generation

**Contexto**: ¿Cómo generar preguntas de clarificación?

**Opciones**:
- A) Catalog estático de preguntas pre-definidas
- B) Generación dinámica según contexto

**Decisión**: B (Dynamic Generation)

**Rationale**:
- Relevancia > breadth
- Adapta a dominio específico
- Evita preguntas obvias

**Trade-off**: Más complejidad en algoritmo

**Adoptado por**: clarify, checklist

---

### Decisión D4: Read-Only vs Mutating Analysis

**Contexto**: ¿El análisis debe modificar artefactos?

**Opciones**:
- A) Auto-fix detected issues
- B) Report only, no modifications

**Decisión**: B (Read-Only)

**Rationale**:
- No sorprender al usuario
- Permite review antes de cambios
- Evita cambios incorrectos automatizados

**Trade-off**: Usuario debe ejecutar fixes manualmente

**Adoptado por**: analyze

---

## Top 12 Patrones para Estandarización RaiSE

### 1. Initialization-Execution-Finalization (IEF)

**Qué**: Estructura estándar de 3 fases para todo comando.

**Dónde aplicar**: Todos los comandos RaiSE.

**Template**:
```markdown
1. Initialize:
   - check-prerequisites.sh
   - Load context
   - Validate environment

2. Execute:
   - [Command-specific logic]
   - Incremental checkpoints
   - Inline validation

3. Finalize:
   - Save artifacts
   - Run gates
   - Update context
   - Offer handoff
```

---

### 2. Progressive Disclosure

**Qué**: Cargar solo el contexto mínimo necesario, expandir bajo demanda.

**Dónde aplicar**: Comandos que leen artefactos grandes.

**Anti-pattern**: `cat spec.md | full-context-to-LLM`

**Patrón correcto**:
```markdown
1. Scan headings (lightweight)
2. IF need section X → load section X only
3. IF need validation → load validation section only
```

---

### 3. Incremental Persistence (Jidoka)

**Qué**: Escribir estado después de cada paso significativo.

**Dónde aplicar**: Comandos de larga duración (>2 min estimado).

**Implementation**:
```markdown
FOR EACH major step:
  - Execute step
  - **CHECKPOINT**: Save partial artifact
  - IF FAIL: Report + STOP
```

---

### 4. Constitution-Based Validation

**Qué**: Constitution = authority no-negociable.

**Dónde aplicar**: Comandos que generan diseño/arquitectura.

**Rule**:
```markdown
IF constitution violation detected:
  → Severity = CRITICAL (auto)
  → STOP execution
  → Report violation + affected principle
```

---

### 5. User-Story-Centric Organization

**Qué**: Organizar por valor de negocio, no por tipo técnico.

**Dónde aplicar**: Cualquier comando que agrupe trabajo.

**Example**:
```
❌ WRONG:
Phase 1: All models
Phase 2: All services
Phase 3: All controllers

✅ CORRECT:
Phase 1: US1 (model + service + controller)
Phase 2: US2 (model + service + controller)
```

---

### 6. Strict Format Enforcement

**Qué**: Outputs parseables por herramientas.

**Dónde aplicar**: Cualquier artefacto consumido por otro comando.

**Example**: tasks.md checklist format
```
- [ ] T001 [P] [US1] Description with path/to/file.ext
```

---

### 7. Interactive Question Loop

**Qué**: Una pregunta a la vez + integración inmediata.

**Dónde aplicar**: Comandos que refinan artefactos.

**Anti-pattern**: Preguntar todo al inicio, integrar al final.

**Patrón correcto**:
```
ASK question 1 → WAIT answer → INTEGRATE → ASK question 2 → ...
```

---

### 8. Safety-First Validation

**Qué**: Múltiples checkpoints antes de operaciones destructivas.

**Dónde aplicar**: Comandos que modifican sistemas externos.

**Template**:
```markdown
1. Validate local state
2. Validate external state
3. **CAUTION block**: Explicit warning
4. Confirm operation
5. Execute
```

---

### 9. Taxonomy-Based Validation

**Qué**: Framework sistemático de categorías de calidad.

**Dónde aplicar**: Comandos de análisis/validación.

**Example domains**:
- Functional scope
- Data model
- Non-functional requirements
- Edge cases
- Integration points

---

### 10. Phase-Based Execution

**Qué**: Dividir trabajo en fases completas y validables.

**Dónde aplicar**: Comandos con múltiples etapas.

**Rule**: Cada fase debe poder validarse independientemente.

---

### 11. Handoff Chain

**Qué**: Conectar comandos en flujo continuo.

**Dónde aplicar**: Todos los comandos que tienen "siguiente paso lógico".

**Implementation**:
```yaml
handoffs:
  - label: "Create Implementation Plan"
    agent: "next-command"
    prompt: "..."
    send: true  # Auto-offer
```

---

### 12. Traceability Requirements

**Qué**: ≥80% de items deben referenciar fuente.

**Dónde aplicar**: Comandos que generan listas de validación/análisis.

**Format**: `[Spec §X.Y]`, `[Gap]`, `[Ambiguity]`, `[Conflict]`

---

## Top 10 Anti-Patrones a Evitar

### AP1: Batch Updates (vs Incremental)

❌ **MAL**:
```markdown
1. Generate all sections
2. Accumulate in memory
3. Write everything at end
```

✅ **BIEN**:
```markdown
1. Generate section A → Write
2. Generate section B → Write
3. Validate → Write if needed
```

---

### AP2: Auto-Bypass Quality Gates

❌ **MAL**:
```markdown
IF gate fails:
  Log warning
  Continue anyway  # Auto-bypass
```

✅ **BIEN**:
```markdown
IF gate fails:
  Report issues
  Ask user: "Proceed anyway? (yes/no)"
  IF user says no: STOP
```

---

### AP3: Technical Grouping (vs User-Story)

❌ **MAL**:
```
Phase 1: Database layer
Phase 2: Service layer
Phase 3: API layer
```

✅ **BIEN**:
```
Phase 1: User Story 1 (DB + Service + API)
Phase 2: User Story 2 (DB + Service + API)
```

---

### AP4: Full Artifact Loading

❌ **MAL**:
```markdown
spec_content = read_file("spec.md")  # 50K tokens
Analyze all at once
```

✅ **BIEN**:
```markdown
headings = scan_headings("spec.md")  # 500 tokens
FOR EACH section_needed:
  section = read_section(section_needed)  # 2K tokens
  Analyze section
```

---

### AP5: Vague Constraints

❌ **MAL**:
```markdown
- Present "a few" questions
- Answer "briefly"
- Load "relevant" context
```

✅ **BIEN**:
```markdown
- Present maximum 5 questions
- Answer in ≤5 words
- Load sections matching keywords X, Y, Z only
```

---

### AP6: Static Question Catalogs

❌ **MAL**:
```markdown
questions = [
  "What is the primary database?",
  "What framework are you using?",
  "What is the deployment target?"
]
# Always ask these, regardless of context
```

✅ **BIEN**:
```markdown
signals = extract_signals(context)
focus_areas = cluster_signals(signals)
questions = generate_from_archetypes(focus_areas)
# Dynamic, context-driven
```

---

### AP7: Silent Validation

❌ **MAL**:
```markdown
IF remote_url != "github.com":
  # Silently skip
  return
```

✅ **BIEN**:
```markdown
> [!CAUTION]
> ONLY PROCEED IF REMOTE IS GITHUB URL

IF remote_url != "github.com":
  ERROR: "Remote is not GitHub. Found: {remote_url}"
  STOP
```

---

### AP8: Testing Implementation (vs Requirements)

❌ **MAL (en checklist)**:
```markdown
- [ ] Verify landing page displays 3 cards
- [ ] Test hover states work
```

✅ **BIEN**:
```markdown
- [ ] Are the number and layout of cards specified? [Completeness]
- [ ] Are hover state requirements consistently defined? [Consistency]
```

---

### AP9: Unlimited Output

❌ **MAL**:
```markdown
FOR EACH requirement:
  FOR EACH issue_found:
    report(issue)
# Could generate 1000+ findings
```

✅ **BIEN**:
```markdown
findings = detect_all_issues()
prioritized = sort_by_severity(findings)
report(prioritized[:50])  # Cap at 50
IF len(findings) > 50:
  report_summary(findings[50:])
```

---

### AP10: Implicit Dependencies

❌ **MAL**:
```markdown
# tasks.md
- T001: Implement UserService
- T002: Create User endpoint
# (T002 depends on T001, but not stated)
```

✅ **BIEN**:
```markdown
## Dependencies

T002 depends on: T001
T005 depends on: T003, T004

## Parallel Opportunities

T001, T003 can run in parallel (different files)
```

---

## Guidelines para Diseñadores de Comandos RaiSE

### Checklist de Diseño

Antes de implementar un comando RaiSE, verificar:

- [ ] **Arquetipo identificado**: ¿Es Generator, Refiner, Analyzer, o Tool?
- [ ] **Patrones aplicables**: ¿Cuáles de los 12 patrones aplican?
- [ ] **Anti-patrones evitados**: ¿Ninguno de los 10 anti-patrones?
- [ ] **Estructura IEF**: ¿Tiene Initialize → Execute → Finalize?
- [ ] **Script integration**: ¿Usa check-prerequisites.sh?
- [ ] **Validation gates**: ¿Tiene quality check inline?
- [ ] **Handoff chain**: ¿Conecta con siguiente comando?
- [ ] **Error handling**: ¿Jidoka explícito (STOP on CRITICAL)?
- [ ] **User input**: ¿Considera $ARGUMENTS?
- [ ] **Output format**: ¿Es parseable si consumido por otro comando?
- [ ] **Traceability**: ¿Referencias a fuente cuando aplica?
- [ ] **Documentation**: ¿Rationale de decisiones clave?

### Decision Tree: Selección de Patrones

```
1. ¿Qué tipo de comando?
   ├─ Genera artefacto nuevo → GENERATOR
   │  ├─ Usa: IEF, Template+Fill, Incremental Persistence
   │  └─ Considera: Phase-Based si multi-etapa
   │
   ├─ Refina artefacto existente → REFINER
   │  ├─ Usa: Interactive Loop, Progressive Disclosure
   │  └─ Considera: Dynamic Question Generation
   │
   ├─ Analiza sin modificar → ANALYZER
   │  ├─ Usa: Multi-Pass Detection, Severity Prioritization
   │  └─ Considera: Taxonomy-Based, Constitution Authority
   │
   └─ Exporta a sistema externo → TOOL
      ├─ Usa: Safety-First Validation
      └─ SIEMPRE: CAUTION blocks

2. ¿Operación larga (>2 min)?
   └─ SÍ → Incremental Persistence obligatorio

3. ¿Involucra governance/arquitectura?
   └─ SÍ → Constitution-Based Validation obligatorio

4. ¿Agrupa trabajo?
   └─ SÍ → User-Story-Centric obligatorio

5. ¿Lee artefactos grandes?
   └─ SÍ → Progressive Disclosure obligatorio

6. ¿Tiene siguiente paso lógico?
   └─ SÍ → Handoff Chain obligatorio
```

---

## Casos de Estudio

### Caso 1: Diseñar `/raise.ecosystem` (map external dependencies)

**Análisis**:
- Tipo: GENERATOR (produce ecosystem.md)
- Duración estimada: 1-2 min
- Involucra arquitectura: Sí

**Patrones aplicables**:
1. **IEF**: ✓ (estructura estándar)
2. **Template+Fill**: ✓ (ecosystem-template.md)
3. **Constitution-Based**: ✓ (validar principios de integración)
4. **Handoff**: ✓ (→ design-architecture)
5. **Progressive Disclosure**: ✗ (artifact pequeño)
6. **Incremental Persistence**: ✗ (operación rápida)

**Anti-patrones a evitar**:
- ❌ Technical grouping (agrupar por API vs. Database)
- ✓ User-Story-Centric: Agrupar por capacidad de negocio

---

### Caso 2: Diseñar `/raise.rules.edit` (edit specific guardrail)

**Análisis**:
- Tipo: REFINER (modifica rule existente)
- Duración: <1 min
- Involucra governance: Sí

**Patrones aplicables**:
1. **IEF**: ✓
2. **Interactive Loop**: ✓ (preguntar qué cambiar)
3. **Constitution-Based**: ✓ (rules son governance)
4. **Progressive Disclosure**: ✓ (cargar solo rule específico)
5. **Incremental Persistence**: ✗ (operación rápida)

**Diseño**:
```markdown
## Outline

1. **Initialize**:
   - check-prerequisites.sh
   - List available rules

2. **Interactive Selection**:
   - Ask: "Which rule to edit?"
   - Load selected rule only (Progressive Disclosure)

3. **Interactive Edit**:
   - Ask: "What to change?"
   - Apply change
   - Validate against constitution
   - **Write immediately** (Incremental, aunque rápido)

4. **Finalize**:
   - Confirm change
   - Offer re-edit or handoff
```

---

## Evolución del Framework

### Métricas de Adopción

Para medir éxito de estandarización:

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **Comandos con IEF** | 100% | Manual review |
| **Comandos con gates** | 100% generators | Script analysis |
| **Comandos con handoffs** | ≥80% | YAML parsing |
| **Anti-patrones detectados** | 0 | Code review |
| **Traceability coverage** | ≥80% en analyzers | Automated check |

### Proceso de Review

1. **Pre-implementation**: Diseñador completa checklist
2. **Implementation**: Seguir patrones seleccionados
3. **Review**: Arquitecto verifica contra checklist
4. **Merge**: Solo si pasa todas las verificaciones

### Actualización de Patrones

Cuando agregar nuevo patrón:
- Observado en ≥2 comandos independientes
- Resuelve problema recurrente
- No duplica patrón existente
- Documentar rationale + trade-offs

---

## Referencias

### Reportes de Arquitectura Individuales

- [specify-system-architecture.md](./specify-system-architecture.md) - Sistema general
- [speckit.2.clarify-architecture.md](./speckit.2.clarify-architecture.md) - Interactive refinement
- [speckit.3.plan-architecture.md](./speckit.3.plan-architecture.md) - Two-phase planning
- [speckit.4.tasks-architecture.md](./speckit.4.tasks-architecture.md) - User-story-centric
- [speckit.5.analyze-architecture.md](./speckit.5.analyze-architecture.md) - Read-only analysis
- [speckit.6.implement-architecture.md](./speckit.6.implement-architecture.md) - Phase-based execution
- [speckit.util.checklist-architecture.md](./speckit.util.checklist-architecture.md) - Requirements testing
- [speckit.util.issues-architecture.md](./speckit.util.issues-architecture.md) - Safe external integration

### Documentación RaiSE

- [Constitution v2.1](../../../docs/framework/v2.1/model/00-constitution-v2.md)
- [Glossary v2.1](../../../docs/framework/v2.1/model/20-glossary-v2.1.md)
- [ADR-012: Command Consolidation](../../../.private/decisions/adr-012-speckit-command-consolidation.md)
- [Rule 110: Command Creation Pattern](../../../.claude/rules/110-raise-kit-command-creation.md)

---

**Versión**: 1.0.0
**Estado**: Living Document - se actualiza con nuevos aprendizajes
**Última actualización**: 2026-01-23
**Contribuidores**: Análisis basado en spec-kit de GitHub + RaiSE Ontology Architect
