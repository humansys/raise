# Feature Specification: Comando raise.5.backlog

**Feature Branch**: `009-backlog-command`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Create raise.5.backlog command to generate project backlog from Tech Design"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Backlog from Tech Design (Priority: P1)

Un Líder Técnico o Arquitecto de Preventa ha completado el Tech Design de un proyecto y necesita generar un backlog estructurado con Epics, Features e Historias de Usuario que puedan ser estimadas y planificadas. El comando debe guiar el proceso de descomposición del Tech Design en elementos de backlog priorizados y estimables.

**Why this priority**: Este es el core del comando - sin la capacidad de generar backlog desde Tech Design, el flujo de estimación completo se interrumpe. Es el MVP del comando.

**Independent Test**: Puede ser completamente testado ejecutando `/raise.5.backlog` con un Tech Design existente y verificando que produce un `project_backlog.md` completo con Epics, Features y User Stories según el template.

**Acceptance Scenarios**:

1. **Given** un Tech Design aprobado en `specs/main/tech_design.md`, **When** el usuario ejecuta `/raise.5.backlog`, **Then** el sistema carga el Tech Design, identifica componentes y funcionalidades, y genera un backlog estructurado en `specs/main/project_backlog.md` con Epics y Features mapeados desde el Tech Design.

2. **Given** el comando inicia la descomposición del Tech Design, **When** el sistema identifica Features, **Then** cada Feature tiene nombre descriptivo, descripción clara, criterios de aceptación, y referencia al PRD y Tech Design correspondiente.

3. **Given** Features identificadas en el backlog, **When** el comando descompone cada Feature, **Then** se generan User Stories en formato "Como [rol], quiero [funcionalidad], para [beneficio]" con criterios de aceptación en formato BDD (Dado/Cuando/Entonces).

4. **Given** User Stories generadas, **When** se completa el backlog, **Then** cada US incluye detalles técnicos (componentes afectados, endpoints API, cambios de modelo) mapeados al Tech Design.

---

### User Story 2 - Priorización y Estimación del Backlog (Priority: P2)

El comando debe guiar al usuario en la priorización de Features y en la estimación de User Stories usando Story Points, permitiendo identificar el MVP y calcular el esfuerzo total del proyecto.

**Why this priority**: Una vez generado el backlog base (P1), la priorización y estimación son críticas para hacer el backlog útil en planificación. Sin estimaciones, no se puede continuar al siguiente comando (`raise.6.estimation`).

**Independent Test**: Testeable ejecutando el comando completo y verificando que el backlog resultante incluye: (1) Features priorizadas con justificación, (2) US con estimaciones en Story Points, (3) MVP identificado.

**Acceptance Scenarios**:

1. **Given** Features identificadas en el backlog, **When** el comando solicita priorización, **Then** el sistema guía al usuario para asignar prioridad (Alta/Media/Baja) a cada Feature considerando valor de negocio, complejidad y riesgo técnico, y documenta la justificación.

2. **Given** User Stories completas con criterios de aceptación, **When** el comando solicita estimación, **Then** el sistema guía al usuario para asignar Story Points (escala Fibonacci: 1, 2, 3, 5, 8, 13) considerando complejidad técnica, incertidumbre y dependencias.

3. **Given** Features priorizadas y US estimadas, **When** el comando solicita identificación del MVP, **Then** el sistema ayuda a identificar el subset mínimo de Features/US que entregan el core value (≤50% del backlog total) y lo marca claramente en el documento.

4. **Given** backlog priorizado y estimado, **When** se completa el documento, **Then** se genera la sección de "Resumen de Estimaciones" con totales por Epic, distribución por complejidad, y métricas del MVP.

---

### User Story 3 - Validación y Handoff (Priority: P3)

El comando debe ejecutar el gate de validación del backlog y ofrecer el handoff al siguiente comando en el flujo de estimación.

**Why this priority**: La validación asegura calidad del artefacto generado y el handoff mantiene el flujo continuo, pero el backlog puede ser generado sin estas funciones (se pueden hacer manualmente).

**Independent Test**: Testeable verificando que al finalizar el comando: (1) se ejecuta `gate-backlog.md`, (2) se muestra resumen de validación, (3) se ofrece ejecutar `/raise.6.estimation`.

**Acceptance Scenarios**:

1. **Given** backlog completado en `specs/main/project_backlog.md`, **When** el comando finaliza la generación, **Then** ejecuta automáticamente el gate `.specify/gates/raise/gate-backlog.md` y muestra los resultados (criterios pasados/fallidos).

2. **Given** gate ejecutado con resultados, **When** todos los criterios obligatorios pasan, **Then** el comando muestra mensaje de éxito, resumen del backlog (cantidad de Epics, Features, US, Total SP) y ofrece handoff: "→ Siguiente paso: `/raise.6.estimation`".

3. **Given** gate ejecutado con criterios fallidos, **When** algún criterio obligatorio falla, **Then** el comando señala los problemas específicos, sugiere correcciones, y permite al usuario corregir antes de continuar (principio Jidoka).

---

### Edge Cases

- ¿Qué ocurre cuando `tech_design.md` no existe? → JIDOKA: El comando debe detectarlo en "Initialize Environment", indicar que falta el Tech Design, y sugerir ejecutar `/raise.4.tech-design` primero.
- ¿Qué ocurre si el Tech Design está incompleto (faltan secciones críticas)? → JIDOKA: Detectar en paso de carga y señalar qué secciones faltan antes de continuar.
- ¿Cómo maneja el comando un backlog ya existente? → El comando debe detectar si `project_backlog.md` existe y preguntar al usuario si desea sobrescribirlo o editarlo.
- ¿Qué pasa si el usuario no puede estimar o priorizar? → El comando debe ofrecer valores por defecto razonables (prioridad Media, estimación basada en complejidad aparente) y señalar que deben refinarse con el equipo.
- ¿Cómo se valida que el MVP es ≤50% del total? → El gate debe calcular el porcentaje automáticamente y alertar si excede el umbral.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El comando DEBE cargar Tech Design desde `specs/main/tech_design.md` como input principal
- **FR-002**: El comando DEBE usar el template `src/templates/backlog/project_backlog.md` como estructura base
- **FR-003**: El comando DEBE producir el artefacto `specs/main/project_backlog.md`
- **FR-004**: El comando DEBE seguir los 10 pasos del kata `flujo-05-backlog-creation`
- **FR-005**: El comando DEBE identificar 3-7 Epics desde el Tech Design mapeando componentes/módulos
- **FR-006**: El comando DEBE descomponer cada Epic en Features que entreguen valor independiente
- **FR-007**: El comando DEBE generar User Stories en formato "Como [rol], quiero [funcionalidad], para [beneficio]"
- **FR-008**: El comando DEBE escribir criterios de aceptación en formato BDD (Dado/Cuando/Entonces) con al menos 2 escenarios por US
- **FR-009**: El comando DEBE añadir detalles técnicos a cada US referenciando componentes del Tech Design
- **FR-010**: El comando DEBE guiar la estimación de User Stories en Story Points (escala Fibonacci: 1, 2, 3, 5, 8, 13)
- **FR-011**: El comando DEBE guiar la priorización de Features considerando valor de negocio, complejidad y riesgo
- **FR-012**: El comando DEBE identificar el MVP slice (subset ≤50% del backlog que entrega core value)
- **FR-013**: El comando DEBE generar resumen de estimaciones con totales por Epic y distribución por complejidad
- **FR-014**: El comando DEBE ejecutar el gate `.specify/gates/raise/gate-backlog.md` al finalizar
- **FR-015**: El comando DEBE incluir handoff a `raise.6.estimation` en el frontmatter YAML
- **FR-016**: El comando DEBE implementar puntos Jidoka si falta Tech Design o está incompleto
- **FR-017**: El comando DEBE actualizar agent context ejecutando `.specify/scripts/bash/update-agent-context.sh` al finalizar
- **FR-018**: El comando DEBE generar contenido en ESPAÑOL con instrucciones en INGLÉS

### Key Entities

- **Epic**: Bloque grande de trabajo que representa un módulo o capacidad completa del sistema. Atributos: ID, título, descripción, prioridad, estimación total (SP), estado.
- **Feature**: Funcionalidad específica dentro de un Epic que entrega valor por sí misma. Atributos: ID, título, descripción, criterios de aceptación, referencias (PRD, Tech Design), prioridad, estimación (SP), estado.
- **User Story**: Unidad de trabajo que describe funcionalidad desde perspectiva del usuario. Atributos: ID, historia ("Como/Quiero/Para"), criterios de aceptación (BDD), detalles técnicos, estimación (SP), dependencias, estado.
- **Tech Design**: Artefacto de entrada que contiene arquitectura técnica, componentes, y decisiones de diseño.
- **Project Backlog**: Artefacto de salida que consolida Epics, Features y User Stories en estructura jerárquica priorizada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un Arquitecto/Líder Técnico puede ejecutar el comando y obtener un backlog completo en menos de 60 minutos de interacción guiada
- **SC-002**: El backlog generado contiene 100% de Features mapeadas a componentes identificables del Tech Design
- **SC-003**: El 100% de User Stories generadas cumplen formato estándar y tienen criterios de aceptación en formato BDD
- **SC-004**: El 100% de User Stories están estimadas en Story Points
- **SC-005**: El MVP identificado representa entre 30-50% del esfuerzo total del backlog
- **SC-006**: El backlog generado pasa el gate-backlog con todos los criterios obligatorios cumplidos
- **SC-007**: El comando detecta y señala 100% de casos donde falta el Tech Design o está incompleto (Jidoka)
- **SC-008**: El usuario recibe handoff claro al siguiente comando (`raise.6.estimation`) al completar exitosamente

## Dependencies *(optional)*

### External Dependencies

- **Comando `raise.4.tech-design`**: Debe existir y haber generado `tech_design.md` antes de ejecutar este comando
- **Template `src/templates/backlog/project_backlog.md`**: Debe estar disponible y completo
- **Gate `src/gates/gate-backlog.md`**: Debe estar disponible para validación
- **Kata `flujo-05-backlog-creation`**: Define los 10 pasos que el comando debe seguir
- **Script `update-agent-context.sh`**: Para actualizar contexto al finalizar

### Internal Dependencies

- El comando debe ser ubicado en `.raise-kit/commands/02-projects/raise.5.backlog.md`
- El template debe estar disponible en `.raise-kit/templates/raise/backlog/project_backlog.md`
- El gate debe estar disponible en `.raise-kit/gates/raise/gate-backlog.md`

## Assumptions *(optional)*

1. El template `src/templates/backlog/project_backlog.md` está completo y listo para usar
2. El kata `flujo-05-backlog-creation` define correctamente los 10 pasos del proceso
3. El usuario que ejecuta el comando tiene conocimiento del contexto del proyecto y puede tomar decisiones de priorización
4. El Tech Design contiene suficiente detalle para identificar Epics y Features (secciones de componentes, arquitectura, scope)
5. El gate `gate-backlog.md` está configurado con criterios apropiados de validación
6. El comando sigue la misma estructura que `raise.1.discovery`, `raise.2.vision` y `raise.4.tech-design`
7. El flujo de comandos va: `raise.4.tech-design` → `raise.5.backlog` → `raise.6.estimation`
8. Story Points usan escala Fibonacci estándar (1, 2, 3, 5, 8, 13, 20, 40, 100)

## Constraints *(optional)*

1. El comando DEBE usar el template existente sin modificarlo
2. El comando DEBE seguir la estructura de comandos existentes (frontmatter YAML, User Input, Outline, etc.)
3. El comando DEBE ubicarse en `.raise-kit/commands/02-projects/`
4. El comando DEBE usar referencias portables (`.specify/` en lugar de `.raise-kit/`)
5. El comando DEBE generar contenido en ESPAÑOL con instrucciones en INGLÉS
6. El comando NO DEBE modificar el Tech Design de entrada
7. El comando NO DEBE crear nuevos templates o gates (usar los existentes)

## Open Questions & Risks *(optional)*

### Open Questions

- **Q1**: ¿El comando debe permitir iteración sobre el backlog (regenerar o editar partes) o solo generación completa inicial?
  - **Suggested Answer**: Solo generación inicial completa. Si el usuario necesita editar, lo hace manualmente en el archivo MD. El comando detecta si el archivo existe y pregunta si desea sobrescribir.

- **Q2**: ¿Cómo se determina el "rol" en las User Stories si el Tech Design no define roles de usuario explícitamente?
  - **Suggested Answer**: El comando debe inferir roles desde el contexto del PRD (sección de usuarios/stakeholders) o usar roles genéricos (Usuario, Administrador, Sistema) y señalar que deben refinarse.

- **Q3**: ¿El comando debe interactuar con el usuario para priorización/estimación o proponer valores por defecto?
  - **Suggested Answer**: Proponer valores por defecto razonables basados en análisis del Tech Design (complejidad aparente, cantidad de componentes afectados) y señalar que deben validarse con el equipo. Esto mantiene el flujo ágil.

### Risks Identified

- **Riesgo 1**: Tech Design incompleto o ambiguo dificulta la identificación de Features
  - **Mitigación**: Implementar checks en paso de carga para verificar que existen secciones mínimas (componentes, arquitectura, scope MVP) y señalar deficiencias vía Jidoka

- **Riesgo 2**: Backlog generado es demasiado grande o granular
  - **Mitigación**: Aplicar heurísticas (3-7 Features, cada Feature 3-8 US, cada US ≤8 SP) y señalar cuando se exceden estos límites

- **Riesgo 3**: Estimaciones iniciales son incorrectas sin participación del equipo completo
  - **Mitigación**: Documentar en el backlog que las estimaciones son preliminares y deben refinarse en planning poker con el equipo

- **Riesgo 4**: MVP slice es subjetivo y puede no reflejar verdadero valor mínimo
  - **Mitigación**: Ofrecer criterios claros (funcionalidad core, sin "nice-to-have", ≤50% esfuerzo) y sugerir validación con Product Owner

## Project-Specific Glossary *(optional)*

| Término | Definición |
|---------|------------|
| Epic | Bloque grande de trabajo que representa un módulo o capacidad completa, típicamente implementable en múltiples sprints |
| Feature | Funcionalidad específica dentro de un Epic que entrega valor independiente, típicamente implementable en 1-4 semanas |
| User Story (US) | Unidad de trabajo que describe funcionalidad desde perspectiva del usuario, formato: "Como [rol], quiero [acción], para [beneficio]" |
| Story Points (SP) | Unidad de estimación relativa que considera complejidad, incertidumbre y esfuerzo (escala Fibonacci) |
| MVP Slice | Subset mínimo del backlog que entrega core value (≤50% del esfuerzo total) |
| BDD | Behavior-Driven Development - Formato de criterios de aceptación: Dado/Cuando/Entonces |
| INVEST | Criterio de calidad para User Stories: Independent, Negotiable, Valuable, Estimable, Small, Testable |
| Jidoka | Principio Lean de "parar en defectos" - detener el proceso cuando se detecta un problema |
| Handoff | Referencia en YAML que conecta un comando con el siguiente en el flujo |
| Gate | Punto de validación que verifica calidad y completitud de un artefacto antes de proceder |
