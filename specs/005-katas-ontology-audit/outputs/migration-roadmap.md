# Migration Roadmap: Katas Ontology Alignment

**Audit Date**: 2026-01-11
**Branch**: `005-katas-ontology-audit`
**Ontology Version**: 2.1.0

## Executive Summary

This roadmap provides actionable migration tasks to align the existing kata ecosystem with the RaiSE ontology v2.1. Tasks are organized by priority and effort.

| Priority | Tasks | Focus |
|----------|-------|-------|
| High | 15 | Rename-only (level prefixes L0→principios, etc.) |
| Medium | 11 | Restructure (add Jidoka Inline, update terminology) |
| Low | 6 | Archive orphan katas to project folders |

**Total Migration Tasks**: 32

---

## High Priority: Rename-Only Tasks

**Effort**: Low (file moves, no content changes)
**Goal**: Migrate to semantic level naming (`principios/flujo/patron/tecnica`)

### Principios Level (from L0)

| Task ID | Current Path | Target Path | Status |
|---------|--------------|-------------|--------|
| MIG-001 | `L0-00-raise-katas-documentation.md` | `principios/00-raise-katas-documentation.md` | Pending |
| MIG-002 | `L0-01-raise-kata-execution-protocol.md` | `principios/01-raise-kata-execution-protocol.md` | Pending |

### Flujo Level (from L1)

| Task ID | Current Path | Target Path | Status |
|---------|--------------|-------------|--------|
| MIG-003 | `L1-04-generacion-plan-implementacion-hu.md` | `flujo/04-generacion-plan-implementacion-hu.md` | Pending |
| MIG-004 | `L1-09-Ecosystem-Discovery-Feature-Design.md` | `flujo/09-ecosystem-discovery-feature-design.md` | Pending |
| MIG-005 | `L1-10-alineamiento-convenciones-repositorio-kata.md` | `flujo/10-alineamiento-convenciones-repositorio.md` | Pending |
| MIG-006 | `L1-12-Analisis-Granularidad-HUs-Multi-Repo.md` | `flujo/12-analisis-granularidad-hus-multi-repo.md` | Pending |
| MIG-007 | `L1-15-Protocolo-Verificacion-DoD-FullCycle.md` | `flujo/15-protocolo-verificacion-validation-gate.md` | Pending |
| MIG-008 | `L1-16-DoD-Historias-Usuario-kata.md` | `flujo/16-validation-gate-historias-usuario.md` | Pending |
| MIG-009 | `L1-17-DoD-Epicas-kata.md` | `flujo/17-validation-gate-epicas.md` | Pending |
| MIG-010 | `L1-implementacion-hu-asistida-por-ia.md` | `flujo/06-implementacion-hu-asistida-por-ia.md` | Pending |

### Patrón Level (from L2)

| Task ID | Current Path | Target Path | Status |
|---------|--------------|-------------|--------|
| MIG-011 | `L2-02-Analisis-Agnostico-Codigo-Fuente.md` | `patron/02-analisis-agnostico-codigo-fuente.md` | Pending |
| MIG-012 | `L2-03-Ecosystem-Discovery-Agnostico.md` | `patron/03-ecosystem-discovery-agnostico.md` | Pending |
| MIG-013 | `L2-04-Analisis-Intercomunicacion-Ecosistema-Agnostico.md` | `patron/04-analisis-intercomunicacion-ecosistema.md` | Pending |
| MIG-014 | `L2-07-Validacion-Tecnica-Dependencias.md` | `patron/07-validacion-tecnica-dependencias.md` | Pending |

### Other

| Task ID | Current Path | Target Path | Status |
|---------|--------------|-------------|--------|
| MIG-015 | `zc-kata-tech-design.md` | `patron/01-tech-design-stack-aware.md` | Pending |

---

## Medium Priority: Restructure Tasks

**Effort**: Medium (content updates required)
**Goal**: Add Jidoka Inline structure and update deprecated terminology

### Add Jidoka Inline Structure

Each step MUST include the required format:
```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

| Task ID | Kata | Steps Affected | Current Jidoka | Target Jidoka |
|---------|------|----------------|----------------|---------------|
| MIG-RST-001 | principios/00-raise-katas-documentation.md | All | Partial | Full |
| MIG-RST-002 | principios/01-raise-kata-execution-protocol.md | All | None | Full |
| MIG-RST-003 | flujo/04-generacion-plan-implementacion-hu.md | 5 steps | None | Full |
| MIG-RST-004 | flujo/09-ecosystem-discovery-feature-design.md | 6 steps | Partial | Full |
| MIG-RST-005 | flujo/10-alineamiento-convenciones-repositorio.md | All | None | Full |
| MIG-RST-006 | flujo/12-analisis-granularidad-hus-multi-repo.md | 5 steps | Partial | Full |
| MIG-RST-007 | patron/02-analisis-agnostico-codigo-fuente.md | 9 steps | Partial | Full |
| MIG-RST-008 | patron/03-ecosystem-discovery-agnostico.md | 10 steps | Partial | Full |
| MIG-RST-009 | patron/04-analisis-intercomunicacion-ecosistema.md | 5 steps | Partial | Full |
| MIG-RST-010 | patron/07-validacion-tecnica-dependencias.md | 5 steps | Partial | Full |
| MIG-RST-011 | patron/01-tech-design-stack-aware.md | 12 steps | Partial | Full |

### Update Deprecated Terminology

| Task ID | Kata | Deprecated Term | Canonical Term | Occurrences |
|---------|------|-----------------|----------------|-------------|
| MIG-TERM-001 | flujo/15-protocolo-verificacion-validation-gate.md | DoD | Validation Gate | ~15 |
| MIG-TERM-002 | flujo/15-protocolo-verificacion-validation-gate.md | Developer | Orquestador | ~5 |
| MIG-TERM-003 | flujo/16-validation-gate-historias-usuario.md | DoD | Validation Gate | ~30 |
| MIG-TERM-004 | flujo/17-validation-gate-epicas.md | DoD | Validation Gate | ~20 |
| MIG-TERM-005 | flujo/06-implementacion-hu-asistida-por-ia.md | Developer | Orquestador | ~3 |

---

## Low Priority: Archive Tasks

**Effort**: Low (file moves only)
**Goal**: Archive orphan katas to preserve history while cleaning active kata set

### Archive Structure

```
archive/
└── projects/
    ├── prosa/
    │   └── L1-01-proceso-estimacion.md
    ├── sar/
    │   └── L1-07-Generacion-Documentacion-Esencial-SAR.md
    ├── jafra/
    │   ├── L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md
    │   ├── L1-10-Extraccion-Backlog-Imagenes-Jafra.md
    │   └── L1-11-Feature-YAML-Extraction-From-Images.md
    └── rag/
        └── L1-09-Documentacion-Completa-Microservicio-RAG.md
```

### Archive Tasks

| Task ID | Current Path | Target Path | Project | Status |
|---------|--------------|-------------|---------|--------|
| MIG-ARC-001 | `L1-01-proceso-estimacion.md` | `archive/projects/prosa/` | PROSA PMO | Pending |
| MIG-ARC-002 | `L1-07-Generacion-Documentacion-Esencial-SAR.md` | `archive/projects/sar/` | SAR | Pending |
| MIG-ARC-003 | `L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md` | `archive/projects/jafra/` | Jafra | Pending |
| MIG-ARC-004 | `L1-09-Documentacion-Completa-Microservicio-RAG.md` | `archive/projects/rag/` | RAG | Pending |
| MIG-ARC-005 | `L1-10-Extraccion-Backlog-Imagenes-Jafra.md` | `archive/projects/jafra/` | Jafra | Pending |
| MIG-ARC-006 | `L1-11-Feature-YAML-Extraction-From-Images.md` | `archive/projects/jafra/` | Jafra | Pending |

---

## Gap-Filling Recommendations

**Priority**: Medium (new kata creation)
**Goal**: Fill unfilled ontology slots to achieve 100% coverage

### Técnica Level (L3) - Currently Empty

| Task ID | Slot | Topic | Recommendation | Effort |
|---------|------|-------|----------------|--------|
| MIG-GAP-001 | TEC-001 | Modelado de Datos | Create `tecnica/01-modelado-datos.md` | High |
| MIG-GAP-002 | TEC-002 | API Design | Create `tecnica/02-api-design.md` | High |

### Suggested Content Sources

**TEC-001 (Modelado de Datos)**:
- Extract patterns from existing L2 katas related to domain modeling
- Reference DDD concepts from methodology
- Include data validation and schema design

**TEC-002 (API Design)**:
- Extract patterns from zc-kata-tech-design.md API sections
- Include REST and gRPC design patterns
- Reference contract-first design from L2 ecosystem katas

---

## Implementation Phases

### Phase A: Preparation (Day 1)

1. Create target directory structure:
   ```bash
   mkdir -p src/katas/{principios,flujo,patron,tecnica}
   mkdir -p archive/projects/{prosa,sar,jafra,rag}
   ```

2. Create archive README explaining rationale

### Phase B: High Priority Renames (Day 1-2)

Execute MIG-001 through MIG-015 using `git mv`:
```bash
git mv src/katas/L0-00-*.md src/katas/principios/00-*.md
# ... continue for all renames
```

### Phase C: Archive Orphans (Day 2)

Execute MIG-ARC-001 through MIG-ARC-006:
```bash
git mv src/katas/L1-01-proceso-estimacion.md archive/projects/prosa/
# ... continue for all archives
```

### Phase D: Restructure Content (Week 1-2)

Execute MIG-RST-001 through MIG-RST-011:
- Add Jidoka Inline structure to each step
- Requires manual content editing per kata

### Phase E: Terminology Updates (Week 2)

Execute MIG-TERM-001 through MIG-TERM-005:
- Replace deprecated terms with canonical equivalents
- Can be partially automated with sed/find-replace

### Phase F: Gap Filling (Week 3+)

Execute MIG-GAP-001 and MIG-GAP-002:
- Create new katas for Técnica level
- Requires significant content creation

---

## Execution Commands

### Bulk Rename (High Priority)

```bash
#!/bin/bash
# Execute from src/katas/

# Principios level
git mv L0-00-raise-katas-documentation.md principios/00-raise-katas-documentation.md
git mv L0-01-raise-kata-execution-protocol.md principios/01-raise-kata-execution-protocol.md

# Flujo level
git mv L1-04-generacion-plan-implementacion-hu.md flujo/04-generacion-plan-implementacion-hu.md
git mv L1-09-Ecosystem-Discovery-Feature-Design.md flujo/09-ecosystem-discovery-feature-design.md
git mv L1-10-alineamiento-convenciones-repositorio-kata.md flujo/10-alineamiento-convenciones-repositorio.md
git mv L1-12-Analisis-Granularidad-HUs-Multi-Repo.md flujo/12-analisis-granularidad-hus-multi-repo.md
git mv L1-15-Protocolo-Verificacion-DoD-FullCycle.md flujo/15-protocolo-verificacion-validation-gate.md
git mv L1-16-DoD-Historias-Usuario-kata.md flujo/16-validation-gate-historias-usuario.md
git mv L1-17-DoD-Epicas-kata.md flujo/17-validation-gate-epicas.md
git mv L1-implementacion-hu-asistida-por-ia.md flujo/06-implementacion-hu-asistida-por-ia.md

# Patrón level
git mv L2-02-Analisis-Agnostico-Codigo-Fuente.md patron/02-analisis-agnostico-codigo-fuente.md
git mv L2-03-Ecosystem-Discovery-Agnostico.md patron/03-ecosystem-discovery-agnostico.md
git mv L2-04-Analisis-Intercomunicacion-Ecosistema-Agnostico.md patron/04-analisis-intercomunicacion-ecosistema.md
git mv L2-07-Validacion-Tecnica-Dependencias.md patron/07-validacion-tecnica-dependencias.md
git mv zc-kata-tech-design.md patron/01-tech-design-stack-aware.md
```

### Bulk Archive (Low Priority)

```bash
#!/bin/bash
# Execute from src/katas/

git mv L1-01-proceso-estimacion.md ../archive/projects/prosa/
git mv L1-07-Generacion-Documentacion-Esencial-SAR.md ../archive/projects/sar/
git mv L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md ../archive/projects/jafra/
git mv L1-09-Documentacion-Completa-Microservicio-RAG.md ../archive/projects/rag/
git mv L1-10-Extraccion-Backlog-Imagenes-Jafra.md ../archive/projects/jafra/
git mv L1-11-Feature-YAML-Extraction-From-Images.md ../archive/projects/jafra/
```

---

## Validation Checklist

After migration completion, verify:

- [ ] All katas use semantic level paths (principios/flujo/patron/tecnica)
- [ ] No deprecated L0/L1/L2/L3 prefixes in active kata paths
- [ ] All orphan katas moved to archive/projects/
- [ ] Jidoka Inline structure present in all steps
- [ ] No deprecated terminology (DoD→Validation Gate, Developer→Orquestador)
- [ ] Gap slots (TEC-001, TEC-002) filled with new katas

---

*Generated by `/speckit.implement` - Katas Ontology Alignment Audit*
*Roadmap created: 2026-01-11*
