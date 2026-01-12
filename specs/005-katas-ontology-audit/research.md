# Research: Katas Ontology Alignment Audit

**Date**: 2026-01-11
**Sources**: `20-glossary-v2.1.md`, `21-methodology-v2.md`

## Summary

This document consolidates findings from parsing the RaiSE ontology v2.1 to define the target kata ecosystem and establish validation criteria for the audit.

---

## 1. Ontology-Defined Kata Levels

**Decision**: Katas are organized in four semantic levels reflecting abstraction.

**Source**: Glossary §Kata [v2.1], Methodology §Niveles de Kata

| Level | Question | Purpose | Deviation Signal | Lean Connection |
|-------|----------|---------|------------------|-----------------|
| **Principios** | ¿Por qué? ¿Cuándo? | Apply Constitution | "Cannot justify this decision" | Toyota Way |
| **Flujo** | ¿Cómo fluye? | Value sequences | "Missing required input" | Value Stream |
| **Patrón** | ¿Qué forma? | Recurring structures | "Output doesn't meet structure" | Standardized Work |
| **Técnica** | ¿Cómo hacer? | Specific instructions | "Technical validation fails" | Work Instructions |

**Target Directory Structure** (from Methodology §Estructura de Directorios):
```
raise-config/katas/
├── principios/     # ¿Por qué? ¿Cuándo?
├── flujo/          # ¿Cómo fluye?
├── patron/         # ¿Qué forma?
└── tecnica/        # ¿Cómo hacer?
```

**Rationale**: Semantic names make the "guiding question" implicit in the folder name, improving discoverability.

---

## 2. Expected Kata Slots (Minimum Coverage)

**Decision**: The ontology examples define minimum expected kata topics per level.

**Source**: Methodology §Niveles de Kata table (Ejemplos column), explicit file references in phases

### Principios Level (L0)

| Slot ID | Topic | Source Reference |
|---------|-------|------------------|
| PRIN-001 | Rol del Orquestador | Methodology line 86 |
| PRIN-002 | Heutagogía | Methodology line 86 |

### Flujo Level (L1)

| Slot ID | Topic | Source Reference |
|---------|-------|------------------|
| FLUJO-001 | Discovery | Methodology line 87 |
| FLUJO-002 | Planning | Methodology line 87 |
| FLUJO-003 | Generación de Plan | Methodology line 87, Fase 5: `flujo/04-generacion-plan.md` |

### Patrón Level (L2)

| Slot ID | Topic | Source Reference |
|---------|-------|------------------|
| PATRON-001 | Tech Design | Methodology line 88 |
| PATRON-002 | Análisis de Código | Methodology line 88, Brownfield: `patron/02-analisis-codigo.md` |
| PATRON-003 | Discovery de Ecosistema | Brownfield section: `patron/03-discovery-ecosistema.md` |

### Técnica Level (L3)

| Slot ID | Topic | Source Reference |
|---------|-------|------------------|
| TEC-001 | Modelado de Datos | Methodology line 89 |
| TEC-002 | API Design | Methodology line 89 |

**Note**: These represent MINIMUM expected coverage. Additional katas beyond these are valid if they fit the level's guiding question.

---

## 3. Jidoka Inline Format Requirement

**Decision**: All katas MUST implement Jidoka Inline structure per step.

**Source**: Glossary §Jidoka [v2.1], Methodology §Jidoka Inline

**Required Format** (literal from glossary lines 106-111):
```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

**Validation Criteria**:
- Each step heading follows `### Paso N:` or `### Step N:` pattern
- Each step includes `**Verificación:**` or `**Verification:**` line
- Each step includes `> **Si no puedes continuar:**` or `> **If you cannot continue:**` block

**Rationale**: Jidoka Inline embeds the correction cycle in context, not in a separate troubleshooting section.

---

## 4. Deprecated Terminology Mapping

**Decision**: Map deprecated terms to canonical equivalents.

**Source**: Glossary §Anti-Términos, §Migración L0-L3

### Level Prefixes

| Deprecated | Canonical | Alias (preserved) |
|------------|-----------|-------------------|
| `L0` | `principios` | `L0`, `meta` |
| `L1` | `flujo` | `L1`, `proceso` |
| `L2` | `patron` | `L2`, `componente` |
| `L3` | `tecnica` | `L3`, `tecnico` |

### Terminology

| Deprecated | Canonical | Migration Note |
|------------|-----------|----------------|
| DoD | Validation Gate | HITL terminology standard (v2.0) |
| DoD Fractal | Validation Gate | Same |
| Rule (isolated) | Guardrail | More specific, connotes active protection |
| Developer | Orquestador | Role evolution in RaiSE |
| micro-kaizen | Jidoka inline | Correction cycle is embedded, not separate |

**Validation Criteria**: Grep for deprecated terms and flag occurrences with line numbers.

---

## 5. Project-Specific Markers

**Decision**: Identify katas as "Orphan" if they contain project-specific markers without generic patterns.

**Source**: Spec assumptions, kata filename analysis

### Known Markers

| Marker | Type | Example File |
|--------|------|--------------|
| `Jafra` | Client name | L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md |
| `SAR` | Project code | L1-07-Generacion-Documentacion-Esencial-SAR.md |
| `PROSA` | Client name | L1-01-proceso-estimacion.md (PROSA PMO) |
| `PMO` | Department | Same |
| `RAG` | Tech stack | L1-09-Documentacion-Completa-Microservicio-RAG.md |

### Detection Strategy

1. **Filename markers**: Check if filename contains known project markers
2. **Content markers**: Grep for project names in content body
3. **Audience section**: Check if kata specifies project-specific audience (e.g., "Arquitecto de Preventa PROSA")

**Classification Logic**:
- Marker in filename AND content is project-specific → **Orphan**
- Marker in content but pattern is generic → **Mapped** (with note: "project examples, generic pattern")
- No markers → Evaluate against ontology slots

---

## 6. Naming Convention for Migrated Katas

**Decision**: Use semantic level names with numeric prefix for ordering.

**Source**: Methodology §Estructura de Directorios, existing file references

### Pattern

```
{level}/{nn}-{descriptive-name}.md
```

Examples from methodology:
- `flujo/04-generacion-plan.md` (referenced in Fase 5)
- `patron/02-analisis-codigo.md` (referenced in Brownfield section)
- `patron/03-discovery-ecosistema.md` (referenced in Brownfield section)

### Migration Mapping

| Current Pattern | Target Pattern |
|-----------------|----------------|
| `L0-00-*.md` | `principios/00-*.md` |
| `L1-04-*.md` | `flujo/04-*.md` |
| `L2-02-*.md` | `patron/02-*.md` |
| `L3-01-*.md` | `tecnica/01-*.md` |

---

## 7. Validation Checklist for Audit

Based on research findings, each kata must be validated against:

### Structural Compliance

- [ ] Uses semantic level naming (principios/flujo/patron/tecnica)
- [ ] Implements Jidoka Inline per step (Verificación + Si no puedes continuar)
- [ ] Contains no deprecated terminology without canonical equivalent noted

### Ontology Mapping

- [ ] Fills a defined ontology slot OR
- [ ] Fits the level's guiding question (additional coverage) OR
- [ ] Is classified as Orphan with rationale

### Project-Specificity

- [ ] No project markers OR
- [ ] Project markers are examples, pattern is generic (Mapped) OR
- [ ] Project-specific content dominates (Orphan)

---

## Research Status

| Task | Status | Findings |
|------|--------|----------|
| Ontology slot extraction | ✅ Complete | 10 minimum slots across 4 levels |
| Jidoka Inline format | ✅ Complete | Exact format documented |
| Project-specific markers | ✅ Complete | 5 markers identified (Jafra, SAR, PROSA, PMO, RAG) |
| Deprecated terminology | ✅ Complete | 6 term mappings documented |
| Naming convention | ✅ Complete | Pattern: `{level}/{nn}-{name}.md` |

**All NEEDS CLARIFICATION items resolved.** Ready for Phase 1.

---

*Research completed: 2026-01-11*
