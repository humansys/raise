# Análisis Arquitectónico: speckit.util.checklist

## 1. Resumen Ejecutivo

El comando `speckit.util.checklist` genera checklists custom que funcionan como "unit tests for requirements" - validan la calidad, claridad y completitud de requirements en un dominio específico. NO verifica implementación; verifica que los REQUIREMENTS están bien escritos.

**Patrón arquitectónico clave**: Requirement Quality Testing Framework con dynamic question generation y taxonomy-based coverage.

**Innovación principal**: Concepto de "Unit Tests for English" - checklists preguntan sobre la CALIDAD de los requirements (completeness, clarity, consistency), NO sobre si la implementación funciona.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Generate a custom checklist for the current feature based on user requirements.
```

**Patrón**: Sin handoffs definidos
**Diseño**: Checklist es utility command - puede llamarse en cualquier momento para validar requirement quality.

**Filosofía**: Standalone validation tool, no parte del main pipeline.

### 2.2 Input Processing

**Patrón**: Context-driven generation
- `$ARGUMENTS`: Driver principal de clarifying questions y focus areas
- Spec/plan/tasks: Context secundario para derivar questions

**Estrategia**: Argumentos definen domain/focus; artifacts proveen contexto específico.

### 2.3 Outline Structure

**Flujo principal**: 7 pasos con dynamic question generation

1. **Setup** (prerequisite check)
2. **Clarify intent** (dynamic contextual questions, max 5)
3. **Understand user request** (combinar args + answers)
4. **Load feature context** (progressive disclosure)
5. **Generate checklist** ("Unit Tests for Requirements")
6. **Structure Reference** (seguir template canónico)
7. **Report** (summary con focus areas)

**Característica crítica**: Paso 5 implementa el concepto de "Unit Tests for English".

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **"Unit Tests for English"** | Checklists validan REQUIREMENTS, no implementation | Shift-left quality; test requirements mismo standard que code |
| **Dynamic Question Generation** | Generar questions desde signals en $ARGUMENTS, no catalog pre-baked | Relevancia contextual; evitar questions irrelevantes |
| **Quality Dimension Categories** | Completeness, Clarity, Consistency, Measurability, Coverage, etc. | Comprehensive requirement testing framework |
| **Traceability Requirements** | ≥80% items con spec reference [Spec §X.Y] o markers [Gap] | Accountability; link findings to sources |
| **Progressive Disclosure Loading** | Cargar solo portions necesarias de artifacts | Token efficiency; reduce noise |
| **Scenario Classification** | Primary, Alternate, Exception, Recovery, Non-Functional | Systematic coverage of requirement types |
| **Content Consolidation** | Merge near-duplicates; cap a ~40 items | Focus on high-impact; avoid checklist fatigue |
| **One Checklist Per Domain** | Separate files: ux.md, api.md, security.md | Focused validation; reusable across features |
| **Recommended Answer Pattern** | Provide suggested answer con best practices | Reduce decision fatigue; apply expertise |
| **Prohibited Patterns Explicit** | Listar qué NO hacer con ejemplos | Clarity; prevent common mistakes |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json` | JSON con FEATURE_DIR, AVAILABLE_DOCS | Get paths to spec/plan/tasks si existen |

**Patrón de integración**: Single generic script, graceful si artifacts faltan.

**Flexibilidad**: Checklist puede generarse sin plan/tasks (solo con spec), o incluso sin spec (exploratory).

## 5. Validation Strategy

**Quality-focused validation**:

### Validation 1: Question Relevance
- Maximum 5 questions total
- Cada question materially changes checklist content
- Skip si already answered en $ARGUMENTS
- Derived from actual signals en spec/plan/tasks, no speculative

### Validation 2: Checklist Item Quality
- Cada item pregunta sobre requirement quality (no implementation)
- Format: Question asking about what's WRITTEN (or not written)
- Include quality dimension marker [Completeness/Clarity/etc.]
- Include traceability reference [Spec §X.Y] o [Gap]

### Validation 3: Traceability Enforcement
- **MINIMUM**: ≥80% items con traceability reference
- References: [Spec §X.Y], [Gap], [Ambiguity], [Conflict], [Assumption]

### Validation 4: Anti-Pattern Detection
- No items con "Verify", "Test", "Confirm" + implementation behavior
- No references a code execution, user actions, system behavior
- No "works properly", "displays correctly", etc.

### Validation 5: Coverage Balance
- Attempt coverage across quality dimensions
- No concentrar todo en una dimension (e.g., solo Completeness)

**Filosofía**: Self-enforcing quality - comando valida su propio output contra principios.

## 6. Error Handling Patterns

### Pattern 1: Missing Spec (Graceful)
```
If spec.md missing → generate based on $ARGUMENTS only
Note in report which artifacts were available
```
**Filosofía**: Graceful degradation - útil incluso sin artifacts.

### Pattern 2: Ambiguous Request
```
If focus unclear after $ARGUMENTS → generate up to 3 clarifying questions
Present with options table or suggested answer
```
**Principio**: Resolve ambiguity early vs. guess incorrectly.

### Pattern 3: Checklist Fatigue Prevention
```
Soft cap: If raw candidates >40 → prioritize by risk/impact
Merge near-duplicates
Consolidate low-impact edge cases
```
**Estrategia**: Quality over quantity.

### Pattern 4: File Exists
```
If checklist file exists → append to existing
Create unique filename based on domain
```
**Diseño**: Support múltiples checklists per story.

## 7. State Management

### Input State (Read-Only)
- **$ARGUMENTS**: Domain, focus, must-have items
- **spec.md** (optional): Requirements, user stories
- **plan.md** (optional): Technical details, dependencies
- **tasks.md** (optional): Implementation tasks
- **Template** (reference): Canonical checklist structure

### Intermediate State (In-Memory)
- **Clarifying answers**: User responses to dynamic questions
- **Focus areas**: Derived from args + answers
- **Coverage map**: Quality dimensions → status
- **Candidate items**: Pre-consolidation checklist items

### Output State
- **checklists/[domain].md**: Generated checklist file
  - Title, purpose, created date
  - Category sections (quality dimensions)
  - Checklist items con IDs (CHK001, CHK002...)
  - Traceability references

### State Transitions
```
Parse $ARGUMENTS → Extract signals → Generate clarifying questions →
User answers → Derive focus + depth → Load context (progressive) →
Generate candidate items → Consolidate → Apply traceability →
Write checklist file → Report summary
```

**Patrón crítico**: Dynamic question generation ANTES de context loading - questions guían qué context cargar.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **"Unit Tests for English" concept** | Apply same rigor to requirements as to code | Requires discipline; initial learning curve |
| **Test requirements, NOT implementation** | Shift-left quality; catch issues in requirements phase | May feel unnatural (tendency to test behavior) |
| **Dynamic question generation** | Contextual relevance; avoid irrelevant questions | More complex than static question catalog |
| **Max 5 clarifying questions** | Balance thoroughness y user fatigue | May need multiple runs for complex domains |
| **Recommended answers** | Apply best practices; reduce decision fatigue | User may feel guided too much |
| **Quality dimension categories** | Systematic coverage framework | Overhead de categorización |
| **≥80% traceability requirement** | Accountability; prevent vague items | Verbosity en item descriptions |
| **One file per domain** | Focused validation; reusable | Proliferation de files si many domains |
| **Soft cap ~40 items** | Focus on high-impact; avoid fatigue | May miss long tail of minor issues |
| **Progressive disclosure loading** | Token efficiency | May miss context-dependent items |
| **Prohibit implementation testing** | Enforce "unit test for requirements" concept | Requires clear anti-examples |

## 9. Comparison with Other Commands

### vs. speckit.2.clarify
- **Clarify**: Interactive workflow que MODIFICA spec
- **Checklist**: Non-interactive generation que NO modifica nada
- **Timing**: Checklist puede ejecutarse ANTES o DESPUÉS de clarify

### vs. speckit.5.analyze
- **Checklist**: Valida quality de requirements (single artifact)
- **Analyze**: Valida consistency cross-artifacts (spec vs. plan vs. tasks)
- **Focus**: Checklist = requirement quality; Analyze = artifact alignment

### vs. speckit.6.implement
- **Checklist**: Genera quality validation items
- **Implement**: VALIDA checklists antes de ejecutar implementación
- **Integration**: Implement usa checklist output como quality gate

### vs. speckit.4.tasks
- **Tasks**: Execution breakdown (qué código escribir)
- **Checklist**: Quality validation (qué validar en requirements)
- **Audience**: Tasks = developers; Checklist = spec authors/reviewers

## 10. Learnings for Standardization

### Patrón 1: "Unit Tests for Requirements" Concept
**Adoptar**: Aplicar testing rigor a requirements writing.
**Aplicar a**: Spec validation, quality gates, reviews.
**Razón**: Shift-left quality; catch issues antes de costly implementation.

**Core principle**:
```
If your spec is code written in English,
the checklist is its unit test suite.
```

**What to test**:
- **Completeness**: Are all necessary requirements documented?
- **Clarity**: Are requirements specific and unambiguous?
- **Consistency**: Do requirements align without conflicts?
- **Measurability**: Can requirements be objectively verified?
- **Coverage**: Are all scenarios/edge cases addressed?

**Examples**:
- ❌ WRONG: "Verify button clicks correctly" (tests implementation)
- ✅ CORRECT: "Are button interaction requirements defined for all states?" (tests requirement quality)

### Patrón 2: Quality Dimension Framework
**Adoptar**: Categorizar checklist items por quality dimension.
**Aplicar a**: Requirement validation, code reviews, documentation quality.
**Razón**: Systematic coverage, prevent bias hacia una dimension.

**Dimensions estándar**:
```markdown
## Requirement Completeness
(Are all necessary requirements documented?)

## Requirement Clarity
(Are requirements specific and unambiguous?)

## Requirement Consistency
(Do requirements align without conflicts?)

## Acceptance Criteria Quality
(Are success criteria measurable?)

## Scenario Coverage
(Are all flows/cases addressed?)

## Edge Case Coverage
(Are boundary conditions defined?)

## Non-Functional Requirements
(Performance, Security, Accessibility - are they specified?)

## Dependencies & Assumptions
(Are they documented and validated?)

## Ambiguities & Conflicts
(What needs clarification?)
```

### Patrón 3: Dynamic Question Generation
**Adoptar**: Generar questions desde context signals vs. static catalog.
**Aplicar a**: Interactive workflows que necesitan clarification.
**Razón**: Relevancia contextual; evitar questions irrelevantes.

**Algorithm**:
```markdown
1. Extract signals: domain keywords, risk indicators, stakeholder hints
2. Cluster signals into candidate focus areas (max 4)
3. Identify probable audience & timing
4. Detect missing dimensions
5. Formulate questions from archetypes:
   - Scope refinement
   - Risk prioritization
   - Depth calibration
   - Audience framing
   - Boundary exclusion
   - Scenario class gap
```

**Question archetypes**:
- "Should this include integration touchpoints with X?" (Scope)
- "Which risk areas need mandatory gating?" (Risk)
- "Is this pre-commit sanity or formal release gate?" (Depth)
- "Will this be used by author only or peers?" (Audience)
- "Should we exclude performance tuning this round?" (Boundary)
- "No recovery flows detected - are rollback paths in scope?" (Gap)

### Patrón 4: Recommended Answer Pattern
**Adoptar**: Proporcionar suggested answer basado en best practices.
**Aplicar a**: Questions con respuesta "mejor práctica" conocida.
**Razón**: Reduce decision fatigue, aplica expertise, preserva autonomía.

**Format**:
```markdown
**Suggested:** <proposed answer> - <brief reasoning>

You can accept the suggestion by saying "yes" or "suggested",
or provide your own answer.
```

### Patrón 5: Traceability Enforcement
**Adoptar**: Requerir ≥80% items con traceability reference.
**Aplicar a**: Checklists, findings reports, validation items.
**Razón**: Accountability, link findings to sources, prevent vague items.

**Reference types**:
- `[Spec §X.Y]` - Specific section reference
- `[Gap]` - Missing requirement identified
- `[Ambiguity]` - Vague/unclear requirement
- `[Conflict]` - Contradictory requirements
- `[Assumption]` - Undocumented assumption

**Examples**:
```markdown
- [ ] CHK001 - Is "fast loading" quantified with timing thresholds? [Clarity, Spec §NFR-2]
- [ ] CHK002 - Are error handling requirements defined for API failures? [Gap]
- [ ] CHK003 - Do navigation requirements conflict between §FR-10 and §FR-10a? [Conflict]
```

### Patrón 6: Progressive Disclosure Context Loading
**Adoptar**: Cargar solo portions relevantes de artifacts.
**Aplicar a**: Analysis commands que procesan large documents.
**Razón**: Token efficiency, reduce noise, faster execution.

**Strategy**:
```markdown
**Context Loading Strategy**:
- Load only necessary portions relevant to active focus areas
- Prefer summarizing long sections into scenario/requirement bullets
- Use progressive disclosure: add follow-on retrieval only if gaps detected
- If source docs large, generate interim summary items instead of embedding
```

### Patrón 7: Scenario Classification Coverage
**Adoptar**: Verificar requirements para todas las scenario classes.
**Aplicar a**: Requirement completeness validation.
**Razón**: Systematic coverage, prevent blind spots.

**Scenario classes**:
- **Primary**: Happy path scenarios
- **Alternate**: Alternative paths to same goal
- **Exception/Error**: Failure scenarios
- **Recovery**: Rollback, retry, fallback paths
- **Non-Functional**: Performance, security, accessibility

**Checklist pattern**:
```markdown
- [ ] CHK010 - Are primary flow requirements complete and clear? [Coverage]
- [ ] CHK011 - Are alternate path requirements defined? [Coverage]
- [ ] CHK012 - Are error scenario requirements specified? [Coverage, Gap]
- [ ] CHK013 - Are recovery/rollback requirements defined? [Coverage, Gap]
- [ ] CHK014 - Are non-functional requirements quantified? [Clarity]
```

### Patrón 8: Content Consolidation
**Adoptar**: Consolidar items similares; cap total count.
**Aplicar a**: Generación de checklists, findings reports.
**Razón**: Focus on high-impact, avoid fatigue, maintain quality.

**Rules**:
```markdown
- Soft cap: If raw candidates >40, prioritize by risk/impact
- Merge near-duplicates checking the same requirement aspect
- If >5 low-impact edge cases, create one consolidated item:
  "Are edge cases X, Y, Z addressed in requirements? [Coverage]"
```

### Patrón 9: One File Per Domain
**Adoptar**: Separate checklists por domain (ux, api, security).
**Aplicar a**: Quality validation artifacts.
**Razón**: Focused validation, reusable, easier navigation.

**Naming convention**:
```
checklists/ux.md
checklists/api.md
checklists/security.md
checklists/performance.md
```

**Benefits**:
- Different stakeholders can focus on their domain
- Reusable across features
- Parallel validation by different teams
- Clear responsibility assignment

### Patrón 10: Prohibited Patterns Explicit
**Adoptar**: Documentar explícitamente qué NO hacer con ejemplos.
**Aplicar a**: Templates, guidelines, style guides.
**Razón**: Prevent common mistakes, clarity sobre boundaries.

**Format**:
```markdown
## 🚫 ABSOLUTELY PROHIBITED

❌ Any item starting with "Verify", "Test", "Confirm" + implementation behavior
❌ References to code execution, user actions, system behavior
❌ "Displays correctly", "works properly", "functions as expected"

## ✅ REQUIRED PATTERNS

✅ "Are [requirement type] defined/specified for [scenario]?"
✅ "Is [vague term] quantified with specific criteria?"
✅ "Are requirements consistent between [section A] and [section B]?"
```

### Anti-Patrón 1: Testing Implementation
**Evitar**: Checklist items que verifican si el código funciona.
**Problema**: Confunde testing de requirements con testing de implementation.
**Solución**: "Unit Tests for English" - test the requirements themselves.

**Examples**:
```markdown
❌ WRONG - Testing implementation:
- [ ] Verify landing page displays 3 episode cards
- [ ] Test hover states work on desktop
- [ ] Confirm logo click navigates home

✅ CORRECT - Testing requirements:
- [ ] Are the number/layout of featured episodes explicitly specified? [Completeness]
- [ ] Are hover state requirements consistently defined? [Consistency]
- [ ] Are navigation requirements clear for brand elements? [Clarity]
```

### Anti-Patrón 2: Vague Quality Checks
**Evitar**: Items sin traceability o quality dimension.
**Problema**: No accountability, difícil validar.
**Solución**: Require traceability reference + dimension marker.

**Examples**:
```markdown
❌ WRONG - Vague:
- [ ] Check if requirements are good
- [ ] Verify completeness

✅ CORRECT - Specific:
- [ ] Are error handling requirements defined for all API failure modes? [Completeness, Gap]
- [ ] Is "fast loading" quantified with timing thresholds? [Clarity, Spec §NFR-2]
```

### Anti-Patrón 3: Static Question Catalog
**Evitar**: Pre-baked list de questions sin considerar context.
**Problema**: Irrelevant questions, user fatigue, low signal.
**Solución**: Dynamic generation desde signals en $ARGUMENTS y artifacts.

### Anti-Patrón 4: Unlimited Checklist Size
**Evitar**: Generar todos los items posibles sin limit.
**Problema**: Checklist fatigue, low completion rate, noise.
**Solución**: Soft cap ~40 items con consolidation.

### Patrón de Arquitectura: Quality Testing Framework
**Concepto**: Framework sistemático para testing requirement quality.

**Components**:
1. **Quality Dimensions**: Completeness, Clarity, Consistency, Measurability, Coverage
2. **Scenario Classes**: Primary, Alternate, Exception, Recovery, Non-Functional
3. **Traceability**: Link cada finding a source (spec section, gap, conflict)
4. **Prohibited Patterns**: Explicit anti-examples
5. **Consolidation**: Focus on high-impact items

**Application**:
```markdown
For each quality dimension:
  For each scenario class:
    Generate checklist items asking:
      - Are requirements present? [Completeness]
      - Are requirements clear? [Clarity]
      - Are requirements consistent? [Consistency]
      - Can requirements be measured? [Measurability]
      - Are all cases covered? [Coverage]
```

### Patrón de Diseño: Domain-Specific Checklists
**Concepto**: Diferentes checklists para diferentes domains.

**Common domains**:
- **UX**: Visual hierarchy, interaction states, accessibility, responsive design
- **API**: Error formats, rate limiting, versioning, authentication
- **Performance**: Latency targets, throughput, load conditions, degradation
- **Security**: Authentication, data protection, threat model, breach response
- **Data**: Entity definitions, relationships, validation, lifecycle

**Benefits**:
- Focused questions
- Domain expertise applied
- Stakeholder assignment
- Parallel validation

### Consideración de UX: Example Checklist Types
**Patrón**: Documentar examples de checklists por domain.
**Razón**: Claridad sobre qué generar, learning by example.

**Format**:
```markdown
## Example Checklist Types & Sample Items

**UX Requirements Quality:** `ux.md`
- "Are visual hierarchy requirements defined with measurable criteria?"
- "Is fallback behavior defined when images fail to load?"

**API Requirements Quality:** `api.md`
- "Are error response formats specified for all failure scenarios?"
- "Is versioning strategy documented in requirements?"
```

### Consideración de Token Efficiency: Question Limits
**Patrón**: Max 5 initial questions + up to 2 follow-ups si necesario.
**Razón**: Balance entre thoroughness y user fatigue.
**Enforcement**: Explicitly stop at limits, no exceed.
