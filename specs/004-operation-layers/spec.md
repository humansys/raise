# Feature Specification: Ciclos de Trabajo RaiSE

**Feature Branch**: `004-operation-layers`
**Created**: 2026-01-11
**Status**: Draft
**Input**: Definir ontológicamente los ciclos de trabajo de RaiSE, clarificando dónde opera spec-kit y qué necesita raise-kit.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Orquestador Identifica en Qué Ciclo Está (Priority: P1)

Un Orquestador necesita saber qué herramientas y katas usar según la fase de su trabajo. Al consultar el documento de Ciclos de Trabajo, identifica rápidamente si está en Onboarding, Proyecto, Feature o Mejora, y qué recursos aplican.

**Why this priority**: Sin esta claridad, los Orquestadores usan herramientas incorrectas para el contexto (ej: spec-kit para onboarding).

**Independent Test**: Un Orquestador responde correctamente: "Estoy configurando un repo nuevo, ¿qué ciclo es?" → "Ciclo de Onboarding."

**Acceptance Scenarios**:

1. **Given** un Orquestador iniciando trabajo en un repo nuevo, **When** consulta el documento, **Then** identifica que está en Ciclo de Onboarding y encuentra referencia a las katas L0-01/L2-01/L2-02.
2. **Given** un Orquestador que va a implementar un feature, **When** consulta el documento, **Then** identifica que está en Ciclo de Feature y que spec-kit aplica aquí.

---

### User Story 2 - Contributor Diseña raise-kit (Priority: P2)

Un contributor quiere hacer fork de spec-kit para crear raise-kit. Al consultar el documento, entiende qué comandos de spec-kit se reutilizan (Ciclo Feature) y qué comandos nuevos se necesitan (otros ciclos).

**Why this priority**: Este documento es el blueprint para raise-kit. Sin él, el fork sería ad-hoc.

**Independent Test**: Un contributor puede listar qué comandos nuevos necesita raise-kit sin ambigüedad.

**Acceptance Scenarios**:

1. **Given** un contributor planificando raise-kit, **When** consulta el documento, **Then** encuentra tabla de ciclos con columna "Comandos spec-kit" vs "Comandos raise-kit nuevos".
2. **Given** el documento, **When** se evalúa un comando propuesto, **Then** se puede determinar a qué ciclo pertenece.

---

### User Story 3 - Orquestador Consulta Glosario (Priority: P3)

Un Orquestador encuentra el término "Ciclo de Trabajo" y quiere la definición precisa.

**Why this priority**: Coherencia terminológica con el glosario.

**Independent Test**: El término "Work Cycle" existe en el glosario con los 4 ciclos definidos.

**Acceptance Scenarios**:

1. **Given** el glosario actualizado, **When** se busca "Work Cycle", **Then** se encuentran definiciones de los 4 ciclos.

---

### Edge Cases

- **Proyectos pequeños**: Pueden saltar Ciclo de Proyecto e ir directo de Onboarding a Feature. El documento debe indicar esto como válido.
- **Repos sin onboarding previo**: Si se usa spec-kit sin haber hecho onboarding, el documento debe indicar qué se pierde (context, guardrails).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El documento DEBE definir cuatro ciclos de trabajo: Onboarding, Proyecto, Feature, Mejora Continua.
- **FR-002**: Cada ciclo DEBE especificar: trigger, unidad de trabajo, fases RaiSE que cubre, katas existentes que aplican.
- **FR-003**: El documento DEBE indicar explícitamente que spec-kit cubre solo el Ciclo de Feature.
- **FR-004**: El documento DEBE referenciar las katas existentes en `src/katas/cursor_rules/` que ya implementan el Ciclo de Onboarding.
- **FR-005**: El documento DEBE incluir una tabla resumen de ciclos con columnas: Ciclo, Trigger, Unidad, Fases RaiSE, Katas Existentes, Cobertura spec-kit.
- **FR-006**: El glosario DEBE actualizarse con entrada "Work Cycle" y los 4 ciclos.
- **FR-007**: El documento DEBE seguir formato de documentos en `docs/framework/v2.1/model/`.

### Key Entities

- **Work Cycle (Ciclo de Trabajo)**: Contexto operacional con trigger, unidad de trabajo, y recursos específicos. Los ciclos son ortogonales (un Orquestador puede estar en cualquiera según el momento).
- **Ciclo de Onboarding**: Preparación inicial de repositorio. Katas: L0-01, L2-01, L2-02.
- **Ciclo de Proyecto**: Trabajo a nivel épica/iniciativa. Fases 1-3 de RaiSE.
- **Ciclo de Feature**: Desarrollo de feature individual. Fases 4-6. spec-kit opera aquí.
- **Ciclo de Mejora**: Retrospectiva y refinamiento. Fase 7+.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un Orquestador identifica su ciclo actual en menos de 1 minuto de lectura.
- **SC-002**: El documento pasa Gate-Terminología: términos nuevos definidos en glosario.
- **SC-003**: El documento pasa Gate-Coherencia: sin contradicciones con metodología existente.
- **SC-004**: Las katas de `src/katas/cursor_rules/` están referenciadas correctamente en Ciclo de Onboarding.

## Assumptions

- Ubicación: `docs/framework/v2.1/model/26-work-cycles-v2.1.md`
- Este documento describe estructura existente (implícita en katas), no crea nuevas reglas.
- Los ciclos son descriptivos del "qué existe", no prescriptivos del "qué debe existir en raise-kit" (eso es futuro).

## Dependencies

- **20-glossary-v2.1.md**: Actualizar con "Work Cycle".
- **21-methodology-v2.md**: Referencia para fases.
- **src/katas/cursor_rules/**: Fuente de verdad para Ciclo de Onboarding.

## Out of Scope

- Diseño detallado de comandos raise-kit (YAGNI - eso es para cuando hagamos el fork).
- Creación de nuevas katas para ciclos sin cobertura (Proyecto, Mejora).
- Especificación de raise-kit como producto (este documento es solo ontología).
