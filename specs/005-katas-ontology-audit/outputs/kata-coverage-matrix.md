# Kata Coverage Matrix

**Audit Date**: 2026-01-11
**Ontology Version**: 2.1.0
**Branch**: `005-katas-ontology-audit`

## Reference Data

### Ontology Slots (Target State)

The ontology defines **10 expected kata slots** across 4 semantic levels:

| Slot ID | Level | Topic | Source Reference | Status | Filled By |
|---------|-------|-------|------------------|--------|-----------|
| PRIN-001 | Principios | Rol del Orquestador | Methodology line 86 | **filled** | L0-00-raise-katas-documentation.md |
| PRIN-002 | Principios | Heutagogía | Methodology line 86 | **filled** | L0-01-raise-kata-execution-protocol.md |
| FLUJO-001 | Flujo | Discovery | Methodology line 87 | **filled** | L1-09-Ecosystem-Discovery-Feature-Design.md |
| FLUJO-002 | Flujo | Planning | Methodology line 87 | **filled** | L1-10-alineamiento-convenciones-repositorio-kata.md, L1-12, L1-15, L1-16, L1-17 |
| FLUJO-003 | Flujo | Generación de Plan | Methodology line 87, Fase 5 | **filled** | L1-04-generacion-plan-implementacion-hu.md, L1-implementacion-hu-asistida-por-ia.md |
| PATRON-001 | Patrón | Tech Design | Methodology line 88 | **filled** | L2-07-Validacion-Tecnica-Dependencias.md, zc-kata-tech-design.md |
| PATRON-002 | Patrón | Análisis de Código | Methodology line 88, Brownfield | **filled** | L2-02-Analisis-Agnostico-Codigo-Fuente.md |
| PATRON-003 | Patrón | Discovery de Ecosistema | Methodology Brownfield section | **filled** | L2-03-Ecosystem-Discovery-Agnostico.md, L2-04-Analisis-Intercomunicacion-Ecosistema-Agnostico.md |
| TEC-001 | Técnica | Modelado de Datos | Methodology line 89 | **gap** | - |
| TEC-002 | Técnica | API Design | Methodology line 89 | **gap** | - |

### Deprecated Terminology Mapping

| Deprecated | Canonical | Migration Note |
|------------|-----------|----------------|
| L0 | principios | Level prefix migration |
| L1 | flujo | Level prefix migration |
| L2 | patron | Level prefix migration |
| L3 | tecnica | Level prefix migration |
| DoD | Validation Gate | HITL terminology (v2.0) |
| Developer | Orquestador | Role evolution |

### Project-Specific Markers

Markers that indicate project-specific (orphan) katas:
- `Jafra` - Client name
- `SAR` - Project code
- `PROSA` - Client name
- `PMO` - Department
- `RAG` - Technology stack (when project-specific)

### Jidoka Inline Validation Criteria

Each kata step MUST include:
```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

---

## Kata Analysis

### Principios Level (L0)

| Kata | Status | Mapped Slot | Jidoka | Deprecated Terms | Project Markers | Notes |
|------|--------|-------------|--------|------------------|-----------------|-------|
| L0-00-raise-katas-documentation.md | **Mapped** | PRIN-001 | ❌ Partial | L0 (level prefix) | None | Kata philosophy & documentation principles; matches Rol del Orquestador |
| L0-01-raise-kata-execution-protocol.md | **Mapped** | PRIN-002 | ❌ No | L0 (level prefix) | None | Execution protocol for HITL learning; matches Heutagogía |

### Flujo Level (L1)

| Kata | Status | Mapped Slot | Jidoka | Deprecated Terms | Project Markers | Notes |
|------|--------|-------------|--------|------------------|-----------------|-------|
| L1-01-proceso-estimacion.md | **Orphan** | - | ❌ No | L1, DoD | PROSA PMO | Project-specific estimation process; archive candidate |
| L1-04-generacion-plan-implementacion-hu.md | **Mapped** | FLUJO-003 | ❌ No | L1 | None | Implementation plan generation; matches Generación de Plan |
| L1-07-Generacion-Documentacion-Esencial-SAR.md | **Orphan** | - | ❌ No | L1 | SAR | Project-specific SAR documentation; archive candidate |
| L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md | **Orphan** | - | ❌ Partial | L1 | Jafra | Project-specific Jafra backend design; archive candidate |
| L1-09-Documentacion-Completa-Microservicio-RAG.md | **Orphan** | - | ❌ No | L1 | RAG | Project-specific RAG documentation; archive candidate |
| L1-09-Ecosystem-Discovery-Feature-Design.md | **Mapped** | FLUJO-001 | ❌ Partial | L1 | None | Ecosystem discovery flow; matches Discovery slot |
| L1-10-alineamiento-convenciones-repositorio-kata.md | **Mapped** | FLUJO-002 | ❌ No | L1 | None | Repository alignment planning; can map to Planning |
| L1-10-Extraccion-Backlog-Imagenes-Jafra.md | **Orphan** | - | ❌ No | L1 | Jafra | Project-specific Jafra backlog extraction; archive candidate |
| L1-11-Feature-YAML-Extraction-From-Images.md | **Orphan** | - | ❌ No | L1 | Implied Jafra | Feature YAML extraction from images; project-specific context |
| L1-12-Analisis-Granularidad-HUs-Multi-Repo.md | **Mapped** | FLUJO-002 | ❌ Partial | L1 | None | Multi-repo HU granularity analysis; generic pattern, extends Planning |
| L1-15-Protocolo-Verificacion-DoD-FullCycle.md | **Mapped** | FLUJO-002 | ❌ Partial | L1, DoD, Developer | None | DoD verification protocol; maps to Planning with terminology updates |
| L1-16-DoD-Historias-Usuario-kata.md | **Mapped** | FLUJO-002 | ✅ Yes | L1, DoD | None | HU DoD definition; has Jidoka-like structure, maps to Planning |
| L1-17-DoD-Epicas-kata.md | **Mapped** | FLUJO-002 | ✅ Yes | L1, DoD | None | Epic DoD definition; has Jidoka-like structure, maps to Planning |
| L1-implementacion-hu-asistida-por-ia.md | **Mapped** | FLUJO-003 | ❌ No | L1, Developer | None | AI-assisted HU implementation; extends Generación de Plan |

### Patrón Level (L2)

| Kata | Status | Mapped Slot | Jidoka | Deprecated Terms | Project Markers | Notes |
|------|--------|-------------|--------|------------------|-----------------|-------|
| L2-02-Analisis-Agnostico-Codigo-Fuente.md | **Mapped** | PATRON-002 | ❌ Partial | L2 | None | Tech-agnostic source code analysis; matches Análisis de Código |
| L2-03-Ecosystem-Discovery-Agnostico.md | **Mapped** | PATRON-003 | ❌ Partial | L2 | None | Tech-agnostic ecosystem discovery; matches Discovery de Ecosistema |
| L2-04-Analisis-Intercomunicacion-Ecosistema-Agnostico.md | **Mapped** | PATRON-003 | ❌ Partial | L2 | None | Ecosystem intercommunication analysis; extends Discovery de Ecosistema |
| L2-07-Validacion-Tecnica-Dependencias.md | **Mapped** | PATRON-001 | ❌ Partial | L2 | None | Technical dependency validation spike; can map to Tech Design |

### Técnica Level (L3)

| Kata | Status | Mapped Slot | Jidoka | Deprecated Terms | Project Markers | Notes |
|------|--------|-------------|--------|------------------|-----------------|-------|
| _No L3 katas found_ | - | - | - | - | - | GAP: TEC-001 (Modelado de Datos), TEC-002 (API Design) unfilled |

### Other/Unclassified

| Kata | Status | Mapped Slot | Jidoka | Deprecated Terms | Project Markers | Notes |
|------|--------|-------------|--------|------------------|-----------------|-------|
| zc-kata-tech-design.md | **Mapped** | PATRON-001 | ❌ Partial | None | Zambezi Concierge | Stack-aware tech design; project-specific BUT generic pattern; maps to Tech Design |

---

## Summary

### Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Katas Analyzed** | 21 | - |
| **Mapped Katas** | 15 | 71.4% |
| **Orphan Katas** | 6 | 28.6% |
| **Total Ontology Slots** | 10 | - |
| **Filled Slots** | 8 | 80.0% |
| **Gap Slots** | 2 | 20.0% |

### By Level

| Level | Slots | Filled | Gap | Katas | Mapped | Orphan |
|-------|-------|--------|-----|-------|--------|--------|
| Principios (L0) | 2 | 2 | 0 | 2 | 2 | 0 |
| Flujo (L1) | 3 | 3 | 0 | 14 | 8 | 6 |
| Patrón (L2) | 3 | 3 | 0 | 4 | 4 | 0 |
| Técnica (L3) | 2 | 0 | 2 | 0 | 0 | 0 |
| Other | 0 | 0 | 0 | 1 | 1 | 0 |

### Jidoka Inline Compliance

| Compliance | Count | Percentage |
|------------|-------|------------|
| **Full Compliance** | 2 | 9.5% |
| **Partial Compliance** | 9 | 42.9% |
| **No Compliance** | 10 | 47.6% |

### Key Findings

1. **Gap Coverage**: The Técnica level (L3) has **2 unfilled slots**:
   - TEC-001: Modelado de Datos
   - TEC-002: API Design

2. **Orphan Katas**: 6 katas are project-specific and should be archived:
   - L1-01-proceso-estimacion.md (PROSA PMO)
   - L1-07-Generacion-Documentacion-Esencial-SAR.md (SAR)
   - L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md (Jafra)
   - L1-09-Documentacion-Completa-Microservicio-RAG.md (RAG)
   - L1-10-Extraccion-Backlog-Imagenes-Jafra.md (Jafra)
   - L1-11-Feature-YAML-Extraction-From-Images.md (Jafra implied)

3. **Deprecated Terminology**: 100% of katas use deprecated level prefixes (L0, L1, L2, L3). Multiple katas also use deprecated terms:
   - DoD (should be Validation Gate): 5 katas
   - Developer (should be Orquestador): 3 katas

4. **Jidoka Non-Compliance**: Only 9.5% of katas fully implement Jidoka Inline structure. Most katas have steps but lack the required `**Verificación:**` and `> **Si no puedes continuar:**` blocks.

5. **Overpopulated Slots**: FLUJO-002 (Planning) has 5+ katas mapped to it, suggesting potential consolidation opportunities.

---

*Generated by `/speckit.implement` - Katas Ontology Alignment Audit*
*Analysis completed: 2026-01-11*
