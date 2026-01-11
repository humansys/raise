# Feature Specification: Evaluación Ontológica para Disclosure Progresivo Heutagógico

**Feature Branch**: `001-heutagogy-progressive-disclosure`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Evaluar ontología v2.1 desde óptica heutagógica para facilitar disclosure progresivo de complejidad del framework"

## Clarifications

### Session 2026-01-11

- Q: ¿Cuál es el formato de los artefactos de salida? → A: Documentos Markdown separados en el feature directory (`specs/001-.../`), versionados en Git antes de integración a `docs/`.
- Q: ¿Cómo se valida que el Learning Path promueve auto-dirección (§5 Heutagogía)? → A: Validación diferida — se evaluará en uso real post-implementación. El Learning Path es una hipótesis a refinar con feedback de Orquestadores reales.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auditoría de Complejidad Ontológica (Priority: P1)

Un Orquestador principal del framework RaiSE quiere entender qué elementos de la ontología v2.1 representan barreras de entrada para nuevos Orquestadores, de modo que pueda priorizar simplificaciones y crear caminos de aprendizaje graduales.

**Why this priority**: Sin esta auditoría, cualquier propuesta de disclosure progresivo sería especulativa. Necesitamos un diagnóstico basado en evidencia de dónde está la complejidad innecesaria.

**Independent Test**: Esta historia puede validarse independientemente generando un informe de auditoría que mapee cada concepto de la ontología a su nivel de complejidad y dependencias.

**Acceptance Scenarios**:

1. **Given** la ontología v2.1 documentada (Constitution, Glosario, Metodología), **When** se realiza la auditoría, **Then** cada concepto tiene asignado un nivel de complejidad (Básico/Intermedio/Avanzado) y sus dependencias conceptuales están mapeadas.

2. **Given** la auditoría completada, **When** se identifican conceptos con alta interdependencia, **Then** estos se marcan como candidatos a simplificación o disclosure tardío.

3. **Given** los conceptos auditados, **When** se aplica la lente ShuHaRi, **Then** cada concepto queda clasificado en qué fase (Shu/Ha/Ri) debería introducirse al Orquestador.

---

### User Story 2 - Propuesta de Camino de Aprendizaje Gradual (Priority: P2)

Un Orquestador principal quiere diseñar un "Learning Path" que presente el framework de forma progresiva, comenzando con los conceptos mínimos viables y revelando complejidad solo cuando el Orquestador está preparado.

**Why this priority**: Esta historia depende de la auditoría (P1). Una vez identificadas las barreras, podemos diseñar el camino que las evita o las introduce gradualmente.

**Independent Test**: Puede validarse creando un documento de Learning Path que defina 3-5 etapas de adopción del framework, cada una con su "Constitution mínima" y conceptos expuestos.

**Acceptance Scenarios**:

1. **Given** la auditoría de complejidad completada, **When** se diseña el Learning Path, **Then** existe al menos una etapa inicial (onboarding) que expone máximo 5 conceptos core.

2. **Given** un Learning Path propuesto, **When** se revisa contra principio §5 Heutagogía, **Then** cada etapa incluye checkpoint heutagógico y promueve auto-dirección (no dependencia).

3. **Given** las etapas del Learning Path, **When** se mapean a niveles de Kata, **Then** hay correspondencia clara entre etapa de aprendizaje y tipo de Kata accesible (Principios primero, luego Flujo, etc.).

---

### User Story 3 - Identificación de Mejoras Pre-Avance (Priority: P3)

Un Orquestador principal quiere identificar mejoras concretas a la ontología v2.1 que reduzcan la curva de aprendizaje, antes de avanzar con nuevas funcionalidades del framework.

**Why this priority**: El objetivo es "pagar la deuda de complejidad" antes de agregar más conceptos. Depende de las dos historias anteriores para tener contexto.

**Independent Test**: Puede validarse generando una lista priorizada de mejoras propuestas con justificación basada en la auditoría y el Learning Path.

**Acceptance Scenarios**:

1. **Given** la auditoría y el Learning Path, **When** se identifican mejoras, **Then** cada mejora tiene: descripción, justificación (qué barrera elimina), y prioridad (Quick Win/Estructural/Fundamental).

2. **Given** mejoras identificadas, **When** se evalúan contra principio de Simplicidad, **Then** las mejoras propuestas reducen conceptos, no los agregan.

3. **Given** la lista de mejoras, **When** se validan contra Gate-Coherencia, **Then** ninguna mejora introduce contradicciones con la Constitution existente.

---

### Edge Cases

- ¿Qué pasa si la auditoría revela que conceptos considerados "core" son en realidad redundantes o innecesarios?
- ¿Cómo manejar conceptos que son simples individualmente pero complejos en combinación (complejidad emergente)?
- ¿Qué ocurre si el Learning Path propuesto requiere cambios a la Constitution (principios inmutables)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El análisis DEBE cubrir los tres documentos core de la ontología v2.1: Constitution (00-constitution-v2.md), Glosario (20-glossary-v2.1.md), y Metodología (21-methodology-v2.md).

- **FR-002**: Cada concepto del glosario DEBE ser evaluado con tres dimensiones: (a) complejidad intrínseca, (b) dependencias hacia otros conceptos, (c) utilidad para Orquestadores novatos.

- **FR-003**: El análisis DEBE identificar "conceptos semilla" — los mínimos necesarios para que un Orquestador pueda comenzar a usar el framework productivamente.

- **FR-004**: La propuesta de mejoras DEBE incluir análisis Lean (Muda/Mura/Muri) para identificar desperdicio conceptual.

- **FR-005**: El Learning Path propuesto DEBE respetar el modelo ShuHaRi existente como lente de progresión del Orquestador.

- **FR-006**: Cada mejora propuesta DEBE incluir rationale documentado siguiendo el formato de ADRs del repositorio.

- **FR-007**: El análisis DEBE preservar la coherencia con los 8 principios de la Constitution — ninguna propuesta puede violar principios inmutables.

- **FR-008**: Los artefactos de salida DEBEN ser documentos Markdown separados en el feature directory (`specs/001-heutagogy-progressive-disclosure/`), estructurados como:
  - `audit-report.md` — Informe de auditoría de complejidad
  - `learning-path.md` — Propuesta de camino de aprendizaje gradual
  - `improvement-proposals.md` — Lista priorizada de mejoras

### Key Entities

- **Concepto Ontológico**: Término definido en el glosario o principio de la Constitution, con atributos de complejidad, dependencias, y fase ShuHaRi recomendada.

- **Barrera de Entrada**: Obstáculo identificado que dificulta la adopción del framework por nuevos Orquestadores. Puede ser conceptual, terminológica, o estructural.

- **Etapa de Aprendizaje**: Fase definida en el Learning Path con su conjunto de conceptos expuestos, Katas accesibles, y checkpoint heutagógico.

- **Mejora Propuesta**: Cambio sugerido a la ontología con justificación, prioridad, e impacto estimado en reducción de complejidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El análisis produce un inventario completo donde 100% de los conceptos del glosario v2.1 están clasificados por nivel de complejidad y fase ShuHaRi.

- **SC-002**: Se identifican los "conceptos semilla" (máximo 7 ± 2 conceptos) que un Orquestador novato necesita para ser productivo en fase Shu.

- **SC-003**: El Learning Path propuesto tiene entre 3 y 5 etapas claramente definidas, cada una con criterios de transición explícitos.

- **SC-004**: Al menos el 80% de los conceptos pueden asociarse a una etapa específica del Learning Path sin ambigüedad.

- **SC-005**: Las mejoras propuestas, de implementarse, reducirían el número de conceptos expuestos en la etapa inicial en al menos un 30% respecto al estado actual.

- **SC-006**: Cada mejora propuesta pasa los Validation Gates de Terminología, Coherencia, y Trazabilidad definidos en CLAUDE.md.

## Assumptions

- La ontología v2.1 es la versión de referencia y no hay cambios pendientes significativos.
- El público objetivo del disclosure progresivo son Orquestadores nuevos al framework RaiSE, pero con experiencia en desarrollo de software.
- El principio de Heutagogía (§5) tiene prioridad sobre la completitud documental — preferimos menos documentación que promueva auto-dirección que más documentación que genere dependencia.
- Los ADRs existentes representan decisiones arquitectónicas válidas que deben respetarse a menos que el análisis proponga su revisión formal.
- El Learning Path propuesto es una hipótesis inicial; su efectividad heutagógica se validará con feedback de uso real, no mediante validación teórica previa.

## Out of Scope

- Implementación de cambios a la ontología (solo análisis y propuestas).
- Creación de herramientas o automatización para el disclosure progresivo.
- Evaluación de otras versiones del framework (v1.x, drafts futuros).
- Cambios a la Constitution que requieran el proceso formal de enmienda.
- Desarrollo de material de capacitación (videos, cursos interactivos).

## Dependencies

- Acceso a todos los documentos de la carpeta `docs/framework/v2.1/`.
- Acceso a ADRs existentes en `docs/framework/v2.1/adrs/`.
- Comprensión del proceso de enmienda de la Constitution (para saber qué cambios son viables sin proceso formal).

## Risks

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| El análisis revela que la complejidad es irreducible | Media | Alto | Aceptar que cierta complejidad es inherente; enfocarse en disclosure progresivo, no en eliminación |
| Propuestas de mejora crean contradicciones con Constitution | Baja | Alto | Validar cada propuesta contra Gate-Coherencia antes de documentar |
| El Learning Path queda demasiado abstracto para ser accionable | Media | Medio | Incluir ejemplos concretos y criterios de transición verificables |
