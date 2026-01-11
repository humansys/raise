# Feature Specification: Glosario Mínimo (Seed) para Stage 0

**Feature Branch**: `002-glossary-seed`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Crear glossary-seed.md con los 5 conceptos esenciales de Stage 0 del framework RaiSE. El documento debe ser conciso (~500 palabras), usar lenguaje simplificado accesible para cualquier desarrollador, e incluir ejemplos concretos. Los 5 conceptos son: Orquestador, Spec, Agent, Validation Gate, y Constitution. Este glosario mínimo elimina la barrera B-03 (sobrecarga cognitiva) permitiendo a nuevos Orquestadores comenzar sin leer el glosario completo de ~35 términos. Reducción de complejidad proyectada: 10%."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear Glosario Mínimo para Onboarding (Priority: P1)

Un nuevo Orquestador quiere comenzar a usar el framework RaiSE sin leer el glosario completo de ~35 términos. Necesita un documento ultra-conciso que le explique los 5 conceptos absolutamente esenciales para empezar, usando lenguaje simple y ejemplos concretos.

**Why this priority**: Este es un Quick Win (QW-03) del backlog de mejoras del feature 001. Reduce la barrera de entrada B-03 (sobrecarga cognitiva) en un 10%, permitiendo que nuevos Orquestadores pasen de ~35 conceptos a 5 en la etapa inicial.

**Independent Test**: Se puede validar independientemente verificando que el archivo `glossary-seed.md` existe, contiene exactamente 5 conceptos, tiene entre 400-600 palabras, y cada concepto tiene definición + ejemplo.

**Acceptance Scenarios**:

1. **Given** un nuevo Orquestador que nunca ha usado RaiSE, **When** lee glossary-seed.md, **Then** puede entender los 5 conceptos core sin necesidad de consultar el glosario completo.

2. **Given** el glosario mínimo creado, **When** se compara con el glosario v2.1 completo, **Then** usa terminología canónica idéntica (sin contradicciones).

3. **Given** un Orquestador en Stage 0, **When** necesita referencia rápida, **Then** encuentra los 5 conceptos en un documento de ~500 palabras (legible en 2-3 minutos).

---

### Edge Cases

- ¿Qué pasa si un concepto semilla requiere más de 100 palabras para explicarse adecuadamente? (Solución: priorizar claridad sobre límite estricto)
- ¿Cómo manejamos referencias a conceptos avanzados que no están en el seed? (Solución: mencionar que existen pero no profundizar)
- ¿Qué pasa si la terminología del glosario v2.1 cambia después de crear el seed? (Solución: el seed debe actualizarse en sincronía)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El documento DEBE contener exactamente 5 conceptos: Orquestador, Spec, Agent, Validation Gate, Constitution (los identificados en learning-path.md Stage 0).

- **FR-002**: Cada concepto DEBE tener dos componentes: (a) definición simplificada en lenguaje accesible para cualquier desarrollador, (b) ejemplo concreto de uso.

- **FR-003**: El documento DEBE tener una longitud total de 400-600 palabras, optimizado para lectura en 2-3 minutos.

- **FR-004**: La terminología DEBE ser idéntica al glosario v2.1 canónico (docs/framework/v2.1/model/20-glossary-v2.1.md) - sin redefiniciones ni contradicciones.

- **FR-005**: El documento DEBE incluir al final una referencia explícita al glosario completo para que los Orquestadores sepan dónde profundizar.

- **FR-006**: El documento DEBE crearse en la ruta `docs/framework/v2.1/model/20a-glossary-seed.md` (nomenclatura "20a" indica que es derivado del glosario principal "20").

- **FR-007**: Cada definición DEBE evitar jerga técnica innecesaria y usar frases de máximo 20 palabras.

### Key Entities

- **Concepto Semilla**: Término fundamental del framework RaiSE que un Orquestador necesita conocer en Stage 0. Tiene: nombre canónico, definición simplificada (<100 palabras), y ejemplo concreto de uso.

- **Glosario Seed Document**: Artefacto markdown que agrupa los 5 conceptos semilla en formato accesible. Propiedades: longitud controlada (~500 palabras), sin dependencias conceptuales (cada término se explica de forma autónoma).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El documento `20a-glossary-seed.md` existe en la ruta especificada y contiene exactamente 5 secciones (una por concepto).

- **SC-002**: La longitud del documento está entre 400 y 600 palabras (verificable con `wc -w`).

- **SC-003**: Cada uno de los 5 conceptos tiene al menos un ejemplo concreto (verificable por revisión manual o regex `Ejemplo:|ejemplo:`).

- **SC-004**: Todos los términos usados están en el glosario v2.1 o son lenguaje natural común (sin términos nuevos no definidos).

- **SC-005**: El documento pasa Gate-Terminología (usa términos canónicos) y Gate-Coherencia (sin contradicciones con Constitution o glosario v2.1).

- **SC-006**: Un nuevo Orquestador puede leer y comprender el documento en menos de 5 minutos (tiempo de lectura promedio: 2-3 minutos a 200 palabras/min).

## Assumptions

- Los 5 conceptos semilla fueron correctamente identificados en el feature 001 (learning-path.md Stage 0) y no cambiarán durante este feature.
- El público objetivo son desarrolladores con experiencia general en software, pero nuevos al framework RaiSE.
- El formato Markdown es adecuado (no se requiere versión PDF, HTML, u otro formato).
- El documento será versionado en Git junto al resto de la documentación del framework.
- La "reducción de complejidad del 10%" es una proyección basada en pasar de ~35 a 5 conceptos iniciales, no requiere validación empírica en este feature.

## Out of Scope

- Creación de ejemplos interactivos o tutoriales paso a paso (solo ejemplos textuales).
- Traducción a otros idiomas (solo español).
- Integración con herramientas de búsqueda o índices automáticos.
- Validación empírica con usuarios reales de la efectividad del glosario seed (se valida en uso posterior).
- Modificación del glosario v2.1 completo (este feature solo crea el seed).

## Dependencies

- Acceso a `docs/framework/v2.1/model/20-glossary-v2.1.md` (glosario canónico para verificar terminología).
- Acceso a `specs/001-heutagogy-progressive-disclosure/learning-path.md` (para confirmar los 5 conceptos de Stage 0).
- Acceso a `.specify/memory/constitution.md` y `docs/framework/v2.1/model/00-constitution-v2.md` (para pasar Gate-Coherencia).

## Risks

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Definiciones demasiado simplificadas pierden precisión técnica | Media | Medio | Revisar contra glosario v2.1 para asegurar coherencia conceptual |
| 500 palabras insuficientes para 5 conceptos con ejemplos | Baja | Bajo | Permitir rango 400-600 palabras; priorizar claridad sobre límite estricto |
| Terminología del glosario v2.1 cambia post-creación | Baja | Medio | Documentar en CLAUDE.md que seed debe actualizarse en sincronía con v2.1 |
| Ejemplos concretos no resuenan con desarrolladores reales | Media | Medio | Usar casos de uso reales del framework (crear spec, ejecutar validation gate) |
