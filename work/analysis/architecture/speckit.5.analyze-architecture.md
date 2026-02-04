# Análisis Arquitectónico: speckit.5.analyze

## 1. Resumen Ejecutivo

El comando `speckit.5.analyze` es un quality gate read-only que detecta inconsistencias, duplicaciones, ambigüedades y gaps de cobertura cross-artifact (spec.md, plan.md, tasks.md) ANTES de implementación. Opera bajo estricta disciplina de no-modificación y constitution-based validation.

**Patrón arquitectónico clave**: Read-Only Cross-Artifact Consistency Analysis con progressive disclosure para eficiencia de tokens.

**Innovación principal**: Constitution como autoridad no-negociable - violaciones de principios son automáticamente CRITICAL y bloquean avance, no se "reinterpretan" o diluyen.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
```

**Patrón**: Sin handoffs definidos
**Diseño**: Analyze es un checkpoint - el usuario decide explícitamente qué hacer después (fix issues o proceder a implement).

**Filosofía**: No forzar flujo - reportar hallazgos y dejar decisión al usuario.

### 2.2 Input Processing

**Patrón**: Single context input
- `$ARGUMENTS`: Usado en paso 1 (context for analysis)

**Estrategia**: Los argumentos pueden especificar áreas de foco o concerns específicos.

### 2.3 Outline Structure

**Flujo principal**: 8 pasos de análisis sin modificación

1. **Initialize Analysis Context** (prerequisite check)
2. **Load Artifacts** (progressive disclosure)
3. **Build Semantic Models** (internal representations)
4. **Detection Passes** (6 tipos de análisis)
5. **Severity Assignment** (CRITICAL/HIGH/MEDIUM/LOW)
6. **Produce Compact Analysis Report** (structured output)
7. **Provide Next Actions** (decision guidance)
8. **Offer Remediation** (suggestions, no auto-apply)

**Característica crítica**: STRICTLY READ-ONLY - enfatizado múltiples veces en el outline.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **Read-Only Analysis** | No modificar files; output structured report | Separation of concerns; user controls changes |
| **Progressive Disclosure** | Cargar solo contexto necesario, no full artifacts | Token efficiency; reduce noise |
| **Semantic Modeling** | Build internal representations vs. raw text | Enable structural analysis vs. string matching |
| **Multi-Pass Detection** | 6 tipos de análisis (duplication, ambiguity, etc.) | Comprehensive coverage; organized findings |
| **Severity Classification** | CRITICAL/HIGH/MEDIUM/LOW heuristic | Prioritization; decision support |
| **Constitution Authority** | Constitution conflicts auto-CRITICAL | Non-negotiable governance; no dilution |
| **Coverage Mapping** | Requirement → Task traceability matrix | Gap detection; completeness validation |
| **Compact Reporting** | Limit to 50 findings; overflow summary | Token budget management; focus on actionable |
| **Stable Finding IDs** | Category-prefixed (A1, D2, C3) | Reproducibility; referencing in discussions |
| **Remediation Offer** | Suggest fixes, don't auto-apply | User control; transparency |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json --require-tasks --include-tasks` | JSON con FEATURE_DIR, AVAILABLE_DOCS, paths to spec/plan/tasks | Ensure all 3 artifacts exist; abort if missing |

**Patrón de integración**: Specialized prerequisite check with strict requirements.

**Innovación**: `--require-tasks --include-tasks` flags - fail fast si tasks.md no existe (analyze requiere task generation completa).

## 5. Validation Strategy

**Read-only validation reporting**:

### Detection Pass A: Duplication
- Near-duplicate requirements (similar phrasing, redundant meaning)
- Mark lower-quality phrasing for consolidation

### Detection Pass B: Ambiguity
- Vague adjectives (fast, scalable, secure) sin métricas
- Unresolved placeholders (TODO, TKTK, ???, `<placeholder>`)

### Detection Pass C: Underspecification
- Requirements con verbs pero missing outcome
- User stories sin acceptance criteria
- Tasks referencing undefined files/components

### Detection Pass D: Constitution Alignment
- Any MUST principle violations
- Missing mandated sections/gates from constitution

### Detection Pass E: Coverage Gaps
- Requirements sin tasks asociadas
- Tasks sin requirement/story mapped
- Non-functional requirements (performance, security) no reflejadas

### Detection Pass F: Inconsistency
- Terminology drift (mismo concepto, nombres diferentes)
- Data entities en plan ausentes en spec (o viceversa)
- Task ordering contradictions
- Conflicting requirements

**Filosofía**: Multi-dimensional analysis framework vs. ad-hoc checks.

## 6. Error Handling Patterns

### Pattern 1: Missing Prerequisites
```
If any required file (spec/plan/tasks) missing → abort with error
Instruct user to run missing prerequisite command
```
**Filosofía**: Fail fast con guidance clara.

### Pattern 2: Token Budget Management
```
Limit to 50 findings total; aggregate remainder in overflow summary
```
**Principio**: Focus on actionable issues, no exhaust context.

### Pattern 3: Deterministic Results
```
Stable finding IDs (category-prefixed)
Rerunning without changes should produce consistent IDs and counts
```
**Diseño**: Reproducibility, regression testing, diff-friendly.

### Pattern 4: Graceful Zero Issues
```
If no issues found → emit success report with coverage statistics
```
**Estrategia**: Reportar éxito explícitamente, no silencio.

## 7. State Management

### Input State (Read-Only)
- **spec.md**: Overview, functional/non-functional requirements, user stories, edge cases
- **plan.md**: Architecture, stack, data model, phases, constraints
- **tasks.md**: Task IDs, descriptions, phase grouping, [P] markers, file paths
- **constitution.md**: Principles, MUST/SHOULD normative statements

### Intermediate State (In-Memory Only)
- **Requirements inventory**: Functional + non-functional con stable keys
- **User story/action inventory**: Discrete actions con acceptance criteria
- **Task coverage mapping**: Task → requirement/story inference
- **Constitution rule set**: Principle names + normative statements

### Output State (Report Only, No File Writes)
- **Analysis report**: Findings table con severity
- **Coverage summary**: Requirement → Task mapping
- **Constitution issues**: Violations identified
- **Unmapped tasks**: Tasks sin requirement
- **Metrics**: Coverage %, ambiguity count, duplication count

### State Transitions
```
Load artifacts → Build semantic models → Run detection passes →
Assign severity → Generate findings → Produce report → Offer remediation
```

**Patrón crítico**: Todo el análisis es in-memory; único output es report (no file modifications).

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Strictly read-only** | Separation of concerns; user controls changes | No auto-fix; requiere manual remediation |
| **Progressive disclosure** | Token efficiency; load only necessary context | May miss context-dependent issues |
| **Semantic modeling** | Enable structural analysis vs. string matching | Upfront processing overhead |
| **6 detection passes** | Comprehensive coverage | Analysis latency; token usage |
| **Severity heuristic** | Prioritization for decision-making | Subjective; may need tuning |
| **Constitution auto-CRITICAL** | Non-negotiable governance | May block progress on exploratory work |
| **50 findings limit** | Focus on actionable; token budget | May hide long tail of minor issues |
| **Stable finding IDs** | Reproducibility; referencing | ID generation complexity |
| **Requirement key slugs** | Stable reference despite wording changes | Slug collision risk |
| **Coverage mapping** | Explicit requirement → task traceability | Inference may miss implicit coverage |
| **Compact reporting** | Table format vs. prose | Less context per finding |
| **Remediation offer** | Transparency; user control | Extra turn of conversation |

## 9. Comparison with Other Commands

### vs. speckit.2.clarify
- **Clarify**: Interactive, domain-focused, modifies spec
- **Analyze**: Read-only, cross-artifact, no modifications
- **Timing**: Clarify BEFORE plan; Analyze AFTER tasks

### vs. speckit.4.tasks
- **Tasks**: Generates task breakdown
- **Analyze**: Validates task coverage and consistency
- **Handoff**: Tasks → Analyze (validation checkpoint)

### vs. speckit.6.implement
- **Analyze**: Quality gate antes de implementación
- **Implement**: Ejecuta tasks
- **Flow**: Analyze BLOCKS implement si CRITICAL issues

### vs. speckit.util.checklist
- **Checklist**: Valida quality de requirements (pre-plan)
- **Analyze**: Valida consistency cross-artifacts (post-tasks)
- **Focus**: Checklist = requirement quality; Analyze = artifact alignment

## 10. Learnings for Standardization

### Patrón 1: Read-Only Analysis Commands
**Adoptar**: Comandos de análisis NO deben modificar files.
**Aplicar a**: Quality gates, consistency checks, validation.
**Razón**: Separation of concerns, user control, transparency.

**Enforcement**:
```markdown
## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured report.
Offer an optional remediation plan (user must explicitly approve before any follow-up editing).
```

### Patrón 2: Progressive Disclosure for Token Efficiency
**Adoptar**: Cargar solo contexto necesario, no full artifacts.
**Aplicar a**: Comandos que analizan large documents.
**Razón**: Token budget management, reduce noise, faster execution.

**Implementación**:
```markdown
### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**
- Overview/Context
- Functional Requirements
- Non-Functional Requirements
(NOT: Full user stories text, examples, etc. - extract only structured data)
```

### Patrón 3: Semantic Modeling
**Adoptar**: Build internal representations antes de análisis.
**Aplicar a**: Análisis estructural, consistency checks.
**Razón**: Enable pattern detection vs. string matching.

**Componentes**:
- **Requirements inventory**: Stable keys (slugs), text, source location
- **User story inventory**: Actions, acceptance criteria
- **Task mapping**: Task ID → requirements covered
- **Constitution rules**: Normative statements extracted

### Patrón 4: Multi-Pass Detection Framework
**Adoptar**: Organizar análisis en passes temáticos.
**Aplicar a**: Comprehensive quality analysis.
**Razón**: Separation of concerns, comprehensive coverage, organized findings.

**Passes estándar**:
1. **Duplication**: Near-duplicates, redundancy
2. **Ambiguity**: Vague terms, placeholders
3. **Underspecification**: Missing details, outcomes
4. **Constitution Alignment**: Principle violations
5. **Coverage Gaps**: Requirement → artifact mapping
6. **Inconsistency**: Terminology drift, conflicts

### Patrón 5: Severity Classification
**Adoptar**: Clasificar findings con severity explícita.
**Aplicar a**: Todos los análisis de calidad.
**Razón**: Prioritization, decision support, risk assessment.

**Heurística**:
- **CRITICAL**: Constitution MUST violations, missing core artifacts, blocking issues
- **HIGH**: Duplicates, conflicting requirements, ambiguous security/performance
- **MEDIUM**: Terminology drift, missing non-functional coverage
- **LOW**: Style/wording improvements, minor redundancy

### Patrón 6: Constitution as Non-Negotiable Authority
**Adoptar**: Constitution violations son automáticamente CRITICAL.
**Aplicar a**: Governance validation, compliance checks.
**Razón**: No dilution of principles; enforce standards.

**Implementación**:
```markdown
**Constitution Authority**: The project constitution is **non-negotiable** within this analysis scope.
Constitution conflicts are automatically CRITICAL and require adjustment of spec/plan/tasks—
not dilution, reinterpretation, or silent ignoring of the principle.
```

### Patrón 7: Token Budget Management
**Adoptar**: Límites explícitos en output (max N findings).
**Aplicar a**: Análisis potencialmente ilimitados.
**Razón**: Focus on actionable, avoid context exhaustion.

**Implementación**:
```markdown
Focus on high-signal findings. Limit to 50 findings total;
aggregate remainder in overflow summary.
```

### Patrón 8: Stable Finding IDs
**Adoptar**: IDs determinísticos para findings.
**Aplicar a**: Análisis que generan reports.
**Razón**: Reproducibility, referencing, regression testing.

**Formato**:
```
[Category Initial][Sequential Number]
A1 = Ambiguity finding #1
D2 = Duplication finding #2
C3 = Coverage finding #3
```

### Patrón 9: Coverage Mapping Table
**Adoptar**: Matriz explícita requirement → artifact.
**Aplicar a**: Completeness validation.
**Razón**: Visualización de gaps, trazabilidad.

**Formato**:
```markdown
| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| user-can-upload | ✓ | T012, T013 | Complete |
| admin-can-delete | ✗ | - | MISSING COVERAGE |
| performance-500ms | Partial | T045 | Only covers frontend |
```

### Patrón 10: Remediation Offer (No Auto-Apply)
**Adoptar**: Ofrecer sugerencias, no aplicar automáticamente.
**Aplicar a**: Análisis que detectan issues corregibles.
**Razón**: User control, transparency, learn what's wrong.

**Formato**:
```markdown
### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?"
(Do NOT apply them automatically.)
```

### Anti-Patrón 1: Auto-Fix Without User Consent
**Evitar**: Modificar artifacts automáticamente en análisis.
**Problema**: Loss of control, unexpected changes, trust issues.
**Solución**: Read-only + remediation offer pattern.

### Anti-Patrón 2: Full Artifact Loading
**Evitar**: Cargar contenido completo de todos los artifacts.
**Problema**: Token exhaustion, noise, slower analysis.
**Solución**: Progressive disclosure - solo lo necesario.

### Anti-Patrón 3: Unlimited Findings
**Evitar**: Reportar todos los issues sin límite.
**Problema**: Context overflow, user overwhelm, low signal-to-noise.
**Solución**: Limit + prioritization + overflow summary.

### Anti-Patrón 4: Vague Severity
**Evitar**: "This is important" sin clasificación explícita.
**Problema**: No prioritization guidance.
**Solución**: Explicit severity levels con heurística documentada.

### Patrón de Arquitectura: Quality Gate Pattern
**Concepto**: Checkpoint read-only que valida antes de continuar pipeline.

**Componentes**:
1. **Prerequisite check**: Ensure inputs exist
2. **Load & model**: Build semantic representations
3. **Multi-pass detection**: Comprehensive analysis
4. **Severity assignment**: Prioritize findings
5. **Report generation**: Structured, actionable
6. **Decision point**: User decides proceed/fix

**Aplicabilidad**: Antes de costosos steps (implementation, deployment, release).

### Patrón de Diseño: Inference-Based Coverage Mapping
**Concepto**: Mapear requirement → task usando keyword/phrase inference.

**Algorithm**:
1. Extract requirement key phrases (verbs + objects)
2. Extract task descriptions + file paths
3. Match keywords: requirement "user upload file" → task "implement upload endpoint"
4. Build coverage matrix: requirement → [task IDs]
5. Identify gaps: requirements con empty task list

**Beneficios**: No requiere explicit linking (pragmatic); catches most coverage.
**Limitación**: Puede miss implicit coverage; false positives.

### Patrón de Diseño: Deterministic Analysis
**Concepto**: Rerunning sin cambios produce resultados consistentes.

**Enforcement**:
- Stable requirement keys (slugs basados en contenido)
- Deterministic finding ID generation (category + order)
- Consistent severity heuristic (rules-based, no random)

**Beneficios**: Regression testing, diff-friendly, debugging.

### Consideración de UX: Next Actions Guidance
**Patrón**: Reporte termina con guidance explícita de next steps.
**Razón**: Decision support, reduce friction, clear options.

**Formato**:
```markdown
## Next Actions

If CRITICAL issues exist:
- Recommend resolving before /speckit.6.implement
- Provide explicit commands: "Run /speckit.1.specify to refine requirements"

If only LOW/MEDIUM:
- User may proceed, but provide improvement suggestions
- Optional: "Run /speckit.2.clarify to address ambiguities"
```

### Consideración de Token Efficiency: Compact Table Format
**Patrón**: Usar tablas para findings vs. prose.
**Razón**: Density, scanability, structure.

**Formato**:
```markdown
| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Ambiguity | HIGH | spec.md:L45 | "fast" lacks metric | Define threshold (e.g., <200ms) |
```

### Patrón de Reporting: Metrics Summary
**Adoptar**: Incluir métricas cuantitativas en reports.
**Razón**: Objetividad, trend tracking, baseline establishment.

**Métricas estándar**:
```markdown
**Metrics:**
- Total Requirements: 23
- Total Tasks: 47
- Coverage %: 87% (20/23 requirements have >=1 task)
- Ambiguity Count: 5
- Duplication Count: 2
- Critical Issues: 1
- High Issues: 3
- Medium Issues: 7
- Low Issues: 12
```
