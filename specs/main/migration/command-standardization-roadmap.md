# Command Standardization Migration Roadmap

**Estado**: 📝 Active - Living Document
**Fecha Inicio**: 2026-01-23
**Objetivo**: Refactorizar comandos RaiSE aplicando patrones extraídos de spec-kit GitHub
**Referencias**: ADR-012, specs/main/analysis/architecture/

---

## Contexto

Hemos analizado 8 comandos de spec-kit GitHub y extraído 12 patrones arquitectónicos fundamentales. Esta migración aplica esos patrones para:
- Mejorar Developer Experience
- Estandarizar estructura de comandos
- Eliminar inconsistencias de nomenclatura
- Reducir carga cognitiva

**Cambios principales**:
- 18 comandos → 14 comandos (reducción 22%)
- Absorber comandos QA en comandos core
- Renombrar para claridad (verbo + sustantivo)
- Aplicar patrones de diseño consistentes

---

## Alcance

### Comandos Afectados

```
ACTUAL (18):                    OBJETIVO (14):

01-onboarding/                  setup/
├── raise.1.analyze.code    →   ├── analyze-codebase
├── raise.rules.generate    →   ├── generate-rules
├── raise.rules.edit        →   ├── edit-rule
└── speckit.2.constitution  →   └── init-project

02-projects/                    project/
├── raise.1.discovery       →   ├── create-prd
├── raise.2.vision          →   ├── define-vision
├── raise.3.ecosystem       →   ├── map-ecosystem
├── raise.4.tech-design     →   ├── design-architecture
├── raise.5.backlog         →   ├── create-backlog
└── raise.6.estimation      →   └── estimate-effort

03-feature/                     feature/
├── speckit.1.specify       →   ├── create-spec
├── speckit.2.clarify       →   [ABSORBER en create-spec]
├── speckit.3.plan          →   ├── plan-implementation
├── speckit.4.tasks         →   ├── generate-tasks
├── speckit.5.analyze       →   [ABSORBER en generate-tasks]
├── speckit.6.implement     →   └── implement
├── speckit.util.checklist  →   [DEPRECAR]
└── speckit.util.issues     →   tools/export-issues
```

---

## Estrategia de Migración: 3 Waves

### Wave 1: Core Feature Flow (CRÍTICO - Hacer primero)

**Objetivo**: Comandos más usados, mayor impacto en DX.

| # | Comando Actual | Comando Nuevo | Acción | Prioridad | Status |
|---|----------------|---------------|--------|-----------|--------|
| 1.1 | speckit.1.specify | feature/create-spec | Refactor + absorber clarify | P0 | ⏸️ Pending |
| 1.2 | speckit.3.plan | feature/plan-implementation | Refactor | P0 | ⏸️ Pending |
| 1.3 | speckit.4.tasks | feature/generate-tasks | Refactor + absorber analyze | P0 | ⏸️ Pending |
| 1.4 | speckit.6.implement | feature/implement | Refactor | P0 | ⏸️ Pending |

**Duración estimada**: 2-3 sesiones de trabajo

**Criterios de Done para Wave 1**:
- [ ] Los 4 comandos core refactorizados
- [ ] Lógica de clarify integrada en create-spec
- [ ] Lógica de analyze integrada en generate-tasks
- [ ] Todos pasan checklist de estandarización (ver abajo)
- [ ] Flujo end-to-end funcional: create-spec → plan → tasks → implement

---

### Wave 2: Setup & Tools (IMPORTANTE - Hacer segundo)

**Objetivo**: Comandos de soporte y herramientas auxiliares.

| # | Comando Actual | Comando Nuevo | Acción | Prioridad | Status |
|---|----------------|---------------|--------|-----------|--------|
| 2.1 | speckit.2.constitution | setup/init-project | Refactor + reubicar | P1 | ⏸️ Pending |
| 2.2 | raise.1.analyze.code | setup/analyze-codebase | Refactor | P1 | ⏸️ Pending |
| 2.3 | raise.rules.generate | setup/generate-rules | Refactor | P1 | ⏸️ Pending |
| 2.4 | raise.rules.edit | setup/edit-rule | Refactor | P1 | ⏸️ Pending |
| 2.5 | speckit.util.issues | tools/export-issues | Refactor | P2 | ⏸️ Pending |
| 2.6 | speckit.util.checklist | deprecated/checklist | Deprecar | P2 | ⏸️ Pending |

**Duración estimada**: 2 sesiones de trabajo

**Criterios de Done para Wave 2**:
- [ ] Comandos setup refactorizados
- [ ] export-issues en tools/
- [ ] checklist movido a deprecated/ con nota
- [ ] Todos pasan checklist de estandarización

---

### Wave 3: Project Commands (OPCIONAL - Hacer tercero)

**Objetivo**: Comandos de proyecto (menos críticos, menor uso).

| # | Comando Actual | Comando Nuevo | Acción | Prioridad | Status |
|---|----------------|---------------|--------|-----------|--------|
| 3.1 | raise.1.discovery | project/create-prd | Refactor | P2 | ⏸️ Pending |
| 3.2 | raise.2.vision | project/define-vision | Refactor | P2 | ⏸️ Pending |
| 3.3 | raise.3.ecosystem | project/map-ecosystem | Refactor | P2 | ⏸️ Pending |
| 3.4 | raise.4.tech-design | project/design-architecture | Refactor | P2 | ⏸️ Pending |
| 3.5 | raise.5.backlog | project/create-backlog | Refactor | P2 | ⏸️ Pending |
| 3.6 | raise.6.estimation | project/estimate-effort | Refactor | P2 | ⏸️ Pending |

**Duración estimada**: 2-3 sesiones de trabajo

**Criterios de Done para Wave 3**:
- [ ] Los 6 comandos project refactorizados
- [ ] Todos pasan checklist de estandarización
- [ ] Handoffs conectan correctamente

---

## Checklist de Estandarización (por comando)

Para cada comando refactorizado, verificar:

### Estructura Básica
- [ ] **Frontmatter completo** (description, handoffs)
- [ ] **User Input section** con `$ARGUMENTS`
- [ ] **Outline** sigue patrón IEF (Initialize → Execute → Finalize)
- [ ] **Guidelines** específicas para el LLM

### Script Integration
- [ ] **Initialize step** ejecuta `check-prerequisites.sh --json`
- [ ] **Parse JSON** correctamente (FEATURE_DIR, paths, etc.)
- [ ] **Error handling** si script falla

### Validation & Quality
- [ ] **Validation step** antes de finalizar (inline Jidoka)
- [ ] **Quality gate** ejecutado si aplica
- [ ] **Constitution check** si involucra governance/arquitectura

### Output & Handoff
- [ ] **Output format** es parseable (si consumido por otro comando)
- [ ] **Handoff** al siguiente comando lógico definido
- [ ] **Finalize step** reporta resumen + siguiente paso

### Patrones Aplicados
- [ ] **Arquetipo identificado** (Generator/Refiner/Analyzer/Tool)
- [ ] **Patrones correctos** aplicados según arquetipo
- [ ] **Anti-patrones evitados** (ver lista abajo)

### Documentación
- [ ] **Rationale** de decisiones clave documentado
- [ ] **Trade-offs** explícitos
- [ ] **Referencias** a análisis arquitectónico

---

## Patrones a Aplicar (por Arquetipo)

### GENERATORS (specify, plan, tasks, implement)

**Patrones obligatorios**:
1. ✓ IEF (Initialize-Execute-Finalize)
2. ✓ Template + Fill
3. ✓ Validation Gate Integration
4. ✓ Handoff Chain

**Patrones opcionales** (según duración):
- Incremental Persistence (si >2 min)
- Phase-Based Execution (si multi-etapa)

### REFINERS (clarify - será absorbido)

**Patrones obligatorios**:
1. ✓ Interactive Question Loop
2. ✓ Progressive Disclosure
3. ✓ Incremental Integration

### ANALYZERS (analyze - será absorbido)

**Patrones obligatorios**:
1. ✓ Read-Only (no modificar)
2. ✓ Multi-Pass Detection
3. ✓ Severity Prioritization
4. ✓ Constitution Authority

### TOOLS (issues)

**Patrones obligatorios**:
1. ✓ Safety-First Validation
2. ✓ CAUTION blocks explícitos

---

## Anti-Patrones a Evitar

### Top 10 (verificar que NO aparecen)

| # | Anti-Patrón | Cómo Detectar | Cómo Corregir |
|---|-------------|---------------|---------------|
| 1 | Batch Updates | Acumula cambios, escribe al final | Escribir después de cada paso |
| 2 | Auto-Bypass Gates | Skip validation sin user consent | Pedir confirmación explícita |
| 3 | Technical Grouping | Agrupar por tipo (models/services) | Agrupar por user story |
| 4 | Full Artifact Loading | `cat file.md` completo | Progressive disclosure |
| 5 | Vague Constraints | "Answer briefly" | "Answer in ≤5 words" |
| 6 | Static Catalogs | Preguntas fijas | Generación dinámica |
| 7 | Silent Validation | No avisar antes de destructivo | CAUTION blocks |
| 8 | Testing Implementation | "Verify button works" | "Is button specified?" |
| 9 | Unlimited Output | Sin límites | Cap at 50 findings |
| 10 | Implicit Dependencies | No documentar deps | Dependency graph explícito |

---

## Proceso de Trabajo (por comando)

### 1. Preparación
```bash
# Crear feature branch
git checkout -b refactor-command-{nombre}

# Leer análisis arquitectónico relevante
cat specs/main/analysis/architecture/speckit.{X}.{nombre}-architecture.md
```

### 2. Refactorización
- Identificar arquetipo (Generator/Refiner/Analyzer/Tool)
- Aplicar patrones del arquetipo
- Verificar checklist de estandarización
- Evitar anti-patrones

### 3. Testing
- Ejecutar comando manualmente
- Verificar output correcto
- Verificar handoff funciona
- Verificar error handling

### 4. Documentación
- Actualizar CLAUDE.md si cambió nombre
- Actualizar handoffs en comandos relacionados
- Documentar decisiones clave

### 5. Commit
```bash
git add .
git commit -m "refactor: standardize {comando} according to spec-kit patterns

- Applied {pattern1}, {pattern2}
- Avoided {anti-pattern}
- Related: ADR-012

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 6. Update Roadmap
- Marcar comando como ✅ Completed
- Documentar learnings si hay

---

## Decisiones Pendientes

| # | Decisión | Opciones | Owner | Deadline | Status |
|---|----------|----------|-------|----------|--------|
| D1 | ¿Eliminar comandos deprecated o mantenerlos? | A) Eliminar, B) Mantener con warning | Emilio | Before Wave 2 | 🟡 Pending |
| D2 | ¿Versioning de comandos durante migración? | A) Breaking change directo, B) v1/v2 coexisten | Emilio | Before Wave 1 | 🟡 Pending |
| D3 | ¿Backward compatibility en handoffs? | A) Update todos, B) Mantener aliases | Emilio | Before Wave 1 | 🟡 Pending |

---

## Métricas de Éxito

### Cuantitativas

| Métrica | Baseline | Target | Medición |
|---------|----------|--------|----------|
| Comandos totales | 18 | 14 | Cuenta archivos |
| Prefijos diferentes | 3 | 0 | Análisis nombres |
| Colisiones nombre | 1 | 0 | Búsqueda duplicados |
| Comandos con IEF | 4/18 (22%) | 14/14 (100%) | Manual review |
| Comandos con gates | 4/18 (22%) | ~10/14 (71%) | Script analysis |
| Anti-patrones detectados | ? | 0 | Code review |

### Cualitativas

| Métrica | Método |
|---------|--------|
| Claridad de nomenclatura | User survey (1-5) |
| Tiempo para aprender flujo | Observación nuevos usuarios |
| Errores de uso | Tracking de issues |
| Satisfacción general | User survey (1-5) |

---

## Riesgos & Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Breaking changes rompen workflows existentes | Media | Alto | Tests manuales antes de merge |
| Comandos absorbidos pierden funcionalidad | Baja | Medio | Review cuidadoso de lógica |
| Tiempo de migración > estimado | Media | Bajo | Priorizar Wave 1, Wave 2/3 opcional |
| Inconsistencias entre comandos migrados | Media | Medio | Checklist riguroso por comando |

---

## Timeline Estimado

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Week 1    │   Week 2    │   Week 3    │   Week 4    │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ Wave 1      │ Wave 1      │ Wave 2      │ Wave 3      │
│ (2 cmd)     │ (2 cmd)     │ (6 cmd)     │ (6 cmd)     │
│             │             │             │ [OPCIONAL]  │
└─────────────┴─────────────┴─────────────┴─────────────┘

Milestone 1: Wave 1 complete (core flow functional)
Milestone 2: Wave 2 complete (full feature set)
Milestone 3: Wave 3 complete (entire system standardized)
```

**Nota**: Timeline es indicativo, puede ajustarse según capacidad.

---

## Referencias

### Análisis Arquitectónico
- `specs/main/analysis/architecture/README.md` - Índice maestro
- `specs/main/analysis/architecture/speckit-design-patterns-synthesis.md` - Patrones sintetizados
- `specs/main/analysis/architecture/speckit.{N}.{name}-architecture.md` - Reportes individuales

### Decisiones
- `.private/decisions/adr-012-speckit-command-consolidation.md` - ADR principal

### Código Fuente
- `.agent/workflows/` - Comandos actuales
- `.specify/scripts/bash/` - Scripts de integración
- `.specify/templates/` - Templates

---

## Log de Cambios

| Fecha | Wave | Comando | Status | Notas |
|-------|------|---------|--------|-------|
| 2026-01-23 | - | Roadmap creado | ✅ | Baseline establecido |
| [YYYY-MM-DD] | [1/2/3] | [comando] | [status] | [learnings] |

---

## Siguiente Sesión

**Prioridad**: Wave 1, Comando 1.1 (feature/create-spec)

**Preparación**:
1. Leer `specs/main/analysis/architecture/speckit.2.clarify-architecture.md`
2. Leer comando actual: `.agent/workflows/03-feature/speckit.1.specify.md`
3. Identificar qué absorber de clarify

**Outcome esperado**: feature/create-spec refactorizado y funcional

---

**Última actualización**: 2026-01-23
**Maintained by**: Emilio + RaiSE Ontology Architect
**Status**: 📝 Active - actualizar después de cada comando completado
