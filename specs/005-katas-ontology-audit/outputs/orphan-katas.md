# Orphan Katas Analysis

**Audit Date**: 2026-01-11
**Branch**: `005-katas-ontology-audit`

## Summary

This document details katas that have been classified as **Orphan** during the ontology alignment audit. Orphan katas are those that do not fill any defined ontology slot, typically because they are project-specific implementations without generic patterns applicable to the v0 RaiSE framework.

| Total Orphan Katas | Recommendation |
|--------------------|----------------|
| 6 | Archive to `archive/projects/` |

---

## Orphan Classification Criteria

A kata is classified as Orphan if ANY of these conditions apply:

1. **Project markers in filename**: Kata filename contains known project identifiers (Jafra, SAR, PROSA, RAG)
2. **Project-specific audience**: Kata specifies a project-specific audience or context
3. **No ontology slot fit**: Kata content doesn't answer any level's guiding question in a generic way
4. **Project-coupled logic**: Business logic is tightly coupled to a specific client's requirements

---

## Detailed Orphan Analysis

### 1. L1-01-proceso-estimacion.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-01-proceso-estimacion.md` |
| **Project Markers** | PROSA PMO |
| **Orphan Reason** | Project-specific estimation process for PROSA PMO client |
| **Generic Pattern Extractable?** | Partial - estimation flow could be generalized |
| **Deprecated Terms Found** | L1, DoD |
| **Jidoka Compliance** | ❌ None |
| **Recommendation** | Archive to `archive/projects/prosa/L1-01-proceso-estimacion.md` |

**Analysis**: This kata describes an estimation process specific to the PROSA PMO project. While estimation is a valid Flujo-level concern, the current implementation is heavily coupled to PROSA's specific workflow and terminology. A generic estimation kata could be extracted, but that would require significant rework.

---

### 2. L1-07-Generacion-Documentacion-Esencial-SAR.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-07-Generacion-Documentacion-Esencial-SAR.md` |
| **Project Markers** | SAR |
| **Orphan Reason** | Project-specific documentation generation for SAR project |
| **Generic Pattern Extractable?** | Yes - "Essential Documentation Generation" is a valid pattern |
| **Deprecated Terms Found** | L1 |
| **Jidoka Compliance** | ❌ None |
| **Recommendation** | Archive to `archive/projects/sar/L1-07-Generacion-Documentacion-Esencial-SAR.md` |

**Analysis**: This kata generates essential documentation specifically for the SAR project. The underlying pattern of "minimum viable documentation" is valuable and could be extracted into a generic kata. However, the current implementation is too specific to SAR's requirements.

**Potential Generic Extraction**: Create `flujo/07-documentacion-esencial.md` based on this pattern (separate task).

---

### 3. L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md` |
| **Project Markers** | Jafra |
| **Orphan Reason** | Project-specific backend design for Jafra microservices |
| **Generic Pattern Extractable?** | Yes - microservices feature design is generic |
| **Deprecated Terms Found** | L1 |
| **Jidoka Compliance** | ❌ Partial |
| **Recommendation** | Archive to `archive/projects/jafra/L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md` |

**Analysis**: This kata describes backend feature design specifically for the Jafra project's microservices architecture. The general pattern of "Backend Feature Design for Microservices" is valuable, but this implementation includes Jafra-specific conventions and dependencies.

**Note**: The generic pattern is already covered by `zc-kata-tech-design.md` which provides a stack-agnostic approach.

---

### 4. L1-09-Documentacion-Completa-Microservicio-RAG.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-09-Documentacion-Completa-Microservicio-RAG.md` |
| **Project Markers** | RAG (technology stack context) |
| **Orphan Reason** | Project-specific RAG microservice documentation |
| **Generic Pattern Extractable?** | Limited - very specific to RAG implementation |
| **Deprecated Terms Found** | L1 |
| **Jidoka Compliance** | ❌ None |
| **Recommendation** | Archive to `archive/projects/rag/L1-09-Documentacion-Completa-Microservicio-RAG.md` |

**Analysis**: This kata focuses on documenting a RAG (Retrieval Augmented Generation) microservice implementation. While RAG is a valuable AI pattern, this documentation kata is too specific to a particular implementation to be generic.

---

### 5. L1-10-Extraccion-Backlog-Imagenes-Jafra.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-10-Extraccion-Backlog-Imagenes-Jafra.md` |
| **Project Markers** | Jafra |
| **Orphan Reason** | Project-specific backlog extraction from Jafra images |
| **Generic Pattern Extractable?** | Yes - "Backlog Extraction from Images" is generic |
| **Deprecated Terms Found** | L1 |
| **Jidoka Compliance** | ❌ None |
| **Recommendation** | Archive to `archive/projects/jafra/L1-10-Extraccion-Backlog-Imagenes-Jafra.md` |

**Analysis**: This kata extracts backlog items from images, specifically tailored for Jafra's visual documentation format. The technique of extracting structured data from images is valuable, but this implementation is coupled to Jafra's specific image formats.

**Related**: See L1-11-Feature-YAML-Extraction-From-Images.md which also handles image extraction.

---

### 6. L1-11-Feature-YAML-Extraction-From-Images.md

| Attribute | Value |
|-----------|-------|
| **Current Path** | `src/katas/L1-11-Feature-YAML-Extraction-From-Images.md` |
| **Project Markers** | Jafra (implied from context) |
| **Orphan Reason** | Continuation of Jafra-specific image extraction workflow |
| **Generic Pattern Extractable?** | Partial - YAML extraction is generic, but context is Jafra |
| **Deprecated Terms Found** | L1 |
| **Jidoka Compliance** | ❌ None |
| **Recommendation** | Archive to `archive/projects/jafra/L1-11-Feature-YAML-Extraction-From-Images.md` |

**Analysis**: This kata focuses on extracting YAML-formatted feature definitions from images. While the title doesn't contain "Jafra", the content and workflow are continuations of the Jafra-specific image extraction process established in L1-10.

**Consolidation Opportunity**: L1-10 and L1-11 could be consolidated into a single archived kata or a generic "Image-to-Structured-Data Extraction" pattern.

---

## Migration Recommendations

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

### Generic Pattern Extraction Opportunities

Based on orphan analysis, the following generic patterns could be extracted:

| Source Orphan | Potential Generic Kata | Priority |
|---------------|------------------------|----------|
| L1-07-*-SAR.md | `flujo/documentacion-esencial.md` | High |
| L1-10, L1-11 (Jafra) | `flujo/extraccion-datos-imagenes.md` | Medium |
| L1-01-proceso-estimacion.md | `flujo/proceso-estimacion.md` | Low |

### Migration Tasks (for roadmap)

1. **MIG-A01**: Create `archive/projects/` directory structure
2. **MIG-A02**: Move orphan katas to archive with preserved history (`git mv`)
3. **MIG-A03**: Update any cross-references in remaining katas
4. **MIG-A04**: Add archive README explaining the archival rationale

---

## Validation

**SC-005 Check**: All orphan katas tagged with reason

| Kata | Reason Tagged | ✓ |
|------|---------------|---|
| L1-01-proceso-estimacion.md | PROSA PMO | ✅ |
| L1-07-Generacion-Documentacion-Esencial-SAR.md | SAR | ✅ |
| L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md | Jafra | ✅ |
| L1-09-Documentacion-Completa-Microservicio-RAG.md | RAG | ✅ |
| L1-10-Extraccion-Backlog-Imagenes-Jafra.md | Jafra | ✅ |
| L1-11-Feature-YAML-Extraction-From-Images.md | Jafra (implied) | ✅ |

**Total**: 6/6 orphan katas have documented reasons

---

*Generated by `/speckit.implement` - Katas Ontology Alignment Audit*
*Analysis completed: 2026-01-11*
