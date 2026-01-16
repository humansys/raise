<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0
Modified principles: N/A (initial population from template)
Added sections:
  - 5 Core Principles derived from RaiSE Constitution v2.0.0
  - Restricciones de Trabajo section
  - Proceso de Cambios section
  - Complete Governance section
Removed sections: N/A (template placeholders replaced)
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ updated (Constitution Check table added)
  - .specify/templates/spec-template.md: ✅ reviewed (compatible)
  - .specify/templates/tasks-template.md: ✅ reviewed (compatible)
  - .specify/templates/checklist-template.md: ✅ reviewed (compatible)
  - .specify/templates/agent-file-template.md: ✅ reviewed (compatible)
Follow-up TODOs: None
-->

# RaiSE Commons Constitution

## Principios Fundamentales

### I. Coherencia Semántica Primero

Toda documentación y artefacto DEBE mantener coherencia semántica con la ontología RaiSE. Los términos, conceptos y relaciones definidos en el glosario son la fuente de verdad. Ningún documento puede contradecir o redefinir términos establecidos sin proceso formal de enmienda.

**Implicación práctica:** Antes de crear o modificar documentación, verificar alineación con `20-glossary-v2.1.md` y la ontología vigente.

### II. Governance como Código

Las políticas, estructuras y estándares son artefactos versionados en Git, no documentos estáticos. Lo que no está en el repositorio, no existe oficialmente. Cada cambio a la ontología requiere trazabilidad completa.

**Jerarquía de documentos:**
```
Constitution (Principios inmutables)
    ↓
ADRs (Decisiones arquitectónicas)
    ↓
Modelo Ontológico (Glosario, Metodología, Templates)
    ↓
Artefactos Derivados (Specs, Plans, Tasks)
```

### III. Validación en Cada Fase

No existe un solo "Done". Cada artefacto tiene criterios de validación que DEBEN cumplirse antes de considerarse completo. La calidad semántica no es un evento final; es un proceso continuo.

**Validation Gates para este repositorio:**
| Gate | Artefacto | Criterio |
|------|-----------|----------|
| Gate-Terminología | Glosario | Términos sin ambigüedad, definiciones completas |
| Gate-Coherencia | Cualquier .md | Sin contradicciones con ontología existente |
| Gate-Trazabilidad | ADRs, Cambios | Historial y rationale documentado |
| Gate-Estructura | Templates | Secciones requeridas presentes |

### IV. Simplicidad sobre Completitud

Preferir documentación concisa que cubra el 80% de casos sobre documentación exhaustiva que nadie lee. Los conceptos complejos DEBEN descomponerse en unidades comprensibles. Evitar abstracciones prematuras en la ontología.

**Principio YAGNI aplicado:** No crear términos, categorías o estructuras "por si acaso". Cada adición a la ontología debe justificarse con uso concreto.

### V. Mejora Continua (Kaizen)

Si un término genera confusión o un template no se usa correctamente, se refina. El sistema aprende de sus fallos y mejora para la siguiente iteración. Toda retroalimentación sobre la ontología es valiosa.

**Ciclo de mejora:**
```
Documentar → Usar → Observar fricciones → Reflexionar → Mejorar → Documentar...
```

## Restricciones de Trabajo

### Nunca:
- Crear documentación sin verificar coherencia con ontología existente
- Introducir términos nuevos sin definición en el glosario
- Modificar definiciones establecidas sin ADR que lo justifique
- Sacrificar claridad por brevedad
- Usar terminología inconsistente entre documentos

### Siempre:
- Validar specs y plans contra esta constitution
- Documentar decisiones significativas en ADRs
- Mantener referencias cruzadas entre documentos relacionados
- Proveer ejemplos concretos para conceptos abstractos
- Incluir fecha y versión en documentos formales

## Proceso de Cambios

Esta Constitution puede modificarse bajo las siguientes condiciones:

1. **Propuesta documentada** con rationale claro
2. **Evaluación de impacto** en documentos dependientes
3. **Aprobación** del maintainer del repositorio
4. **Actualización** de documentos afectados
5. **Comunicación** del cambio con changelog

## Governance

**Política de versionado:**
- MAJOR: Cambios incompatibles en principios o estructura
- MINOR: Nuevas secciones o expansión de guidance
- PATCH: Clarificaciones, correcciones menores

**Revisión de compliance:**
- Todo PR debe verificar que no viola principios de esta constitution
- Cambios a la ontología requieren revisión explícita de coherencia
- Los templates deben mantenerse alineados con los principios

**Archivo de referencia:** `.specify/memory/constitution.md` es la fuente de verdad para governance del workflow speckit en este repositorio.

**Versión**: 1.0.0 | **Ratificada**: 2026-01-11 | **Última Enmienda**: 2026-01-11
