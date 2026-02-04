# Feature Specification: Comando raise.6.estimation

**Feature Branch**: `010-estimation-command`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Ya tengo el de backlog, haz el que sigue de estimacion, sigue regla 110-raise-kit-command-creation.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generar Roadmap de Estimación desde Backlog (Priority: P1)

Como Arquitecto de Preventa, quiero ejecutar un comando que transforme el Project Backlog en un Estimation Roadmap estructurado con estimaciones en Story Points y proyección de sprints, para poder dimensionar el esfuerzo del proyecto y presentar una propuesta realista al cliente.

**Why this priority**: Este es el core value del comando - sin esta capacidad, el comando no cumple su propósito. La estimación es el paso crítico que conecta el backlog técnico con la propuesta comercial (SoW).

**Independent Test**: Se puede testear ejecutando `/raise.6.estimation` con un backlog válido y verificando que genera `specs/main/estimation_roadmap.md` con: (1) tabla de estimaciones por item del backlog, (2) parámetros de capacidad del equipo, (3) roadmap proyectado por iteraciones, (4) métricas de esfuerzo total.

**Acceptance Scenarios**:

1. **Given** existe `specs/main/project_backlog.md` con Epics, Features y User Stories estimadas en SP, **When** ejecuto `/raise.6.estimation`, **Then** se genera `specs/main/estimation_roadmap.md` con guía de estimación, tabla de estimaciones del backlog, parámetros de roadmap y proyección por iteraciones.

2. **Given** el backlog tiene User Stories sin estimaciones (SP vacíos o marcados como "Pendiente"), **When** ejecuto el comando, **Then** el sistema propone estimaciones preliminares basadas en complejidad aparente y señala que deben refinarse con el equipo.

3. **Given** el roadmap proyectado supera 6 meses de duración, **When** el comando calcula las iteraciones, **Then** muestra un warning sugiriendo revisar el scope del MVP para reducir el tamaño inicial del proyecto.

---

### User Story 2 - Configurar Parámetros de Equipo y Capacidad (Priority: P2)

Como Líder Técnico, quiero que el comando me permita especificar la estructura del equipo (roles y dedicación) y duración de sprints, para que el roadmap refleje la realidad del equipo disponible y no use valores genéricos.

**Why this priority**: Sin parametrización, el roadmap sería poco realista. Esta capacidad permite adaptar la estimación a diferentes configuraciones de equipo, lo cual es esencial para propuestas precisas.

**Independent Test**: Se puede testear proporcionando parámetros custom (ej. "2 dev full-time, 1 QA 50%, sprints de 1 semana") y verificando que el roadmap calcula correctamente la capacidad por iteración y ajusta el número de sprints necesarios.

**Acceptance Scenarios**:

1. **Given** no proporciono parámetros de equipo explícitos, **When** ejecuto el comando, **Then** usa valores por defecto razonables (ej. 1 architect 50%, 1 engineer 100%, 1 QA 50%, sprints de 2 semanas, capacidad de 16 SP/sprint) y documenta estos defaults en el roadmap.

2. **Given** proporciono estructura de equipo custom (ej. "3 engineers full-time, sprints de 1 semana"), **When** ejecuto el comando, **Then** calcula la capacidad total (3 * 8 = 24 SP/sprint) y genera roadmap acorde.

3. **Given** la capacidad del equipo (SP/sprint) no se ajusta bien al backlog (ej. backlog tiene 163 SP, capacidad es 16 SP/sprint), **When** calcula iteraciones, **Then** muestra el cálculo: 163/16 = 10.2 → 11 sprints, redondeando hacia arriba.

---

### User Story 3 - Vincular Estimación con Modelo de Costos (Priority: P3)

Como Analista de Estimaciones, quiero que el roadmap incluya una sección explicando cómo los Story Points se relacionan con el costo final del proyecto, para poder preparar el Statement of Work con información de pricing.

**Why this priority**: Nice-to-have que facilita la transición al siguiente comando (`raise.7.sow`). No bloquea la generación del roadmap, pero añade valor para el proceso comercial.

**Independent Test**: Se puede testear generando el roadmap y verificando que la sección "Vinculación con Modelo de Costos" existe y explica la relación SP → esfuerzo → costo, incluyendo factores de conversión (ej. 1 SP = X horas, tasa horaria del equipo).

**Acceptance Scenarios**:

1. **Given** el roadmap está completo con estimaciones, **When** el comando finaliza, **Then** genera sección "Vinculación con Modelo de Costos" explicando: relación SP/horas, impacto de cambios en el roadmap, supuestos de costo clave (composición equipo, tarifas).

2. **Given** los parámetros de equipo incluyen tarifas horarias, **When** el comando calcula el costo total, **Then** proyecta: Total SP * factor de conversión * tasa promedio = Costo Estimado, y documenta esto en la sección de costos.

---

### Edge Cases

- **Backlog sin MVP identificado**: El comando debe calcular roadmap completo y sugerir que las primeras 3-5 iteraciones representen el MVP, o pedir al usuario que clarifique qué Features son MVP.

- **Backlog con User Stories muy grandes (>13 SP)**: El comando debe detectarlas y recomendar subdividirlas antes de proyectar el roadmap, o aplicar un factor de incertidumbre adicional en el cálculo de iteraciones.

- **Equipo con capacidad muy baja (<8 SP/sprint)**: El comando debe alertar que con esta capacidad el proyecto tomaría demasiado tiempo y sugerir aumentar recursos o reducir scope.

- **Backlog muy grande (>500 SP)**: El comando debe recomendar dividir en fases o releases y estimar solo la primera fase en detalle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El comando DEBE cargar `specs/main/project_backlog.md` como input principal y extraer: Epics, Features, User Stories con sus estimaciones en Story Points.

- **FR-002**: El comando DEBE usar el template `src/templates/solution/estimation_roadmap.md` como base estructural para generar `specs/main/estimation_roadmap.md`.

- **FR-003**: El comando DEBE generar una tabla de estimaciones consolidando todos los items del backlog con sus Story Points, ordenados por prioridad y dependencias.

- **FR-004**: El comando DEBE permitir configurar parámetros del equipo: estructura (roles y dedicación %), duración de sprints, y capacidad estimada en SP por sprint.

- **FR-005**: El comando DEBE calcular el roadmap proyectado dividiendo el total de SP estimados entre la capacidad del equipo, generando una tabla de iteraciones con: número de iteración, fechas estimadas (relativas), objetivo, elementos del backlog planeados, y SP acumulados.

- **FR-006**: El comando DEBE identificar y marcar claramente qué iteraciones corresponden al MVP basándose en las Features marcadas como MVP en el backlog.

- **FR-007**: El comando DEBE documentar en el roadmap: guía de estimación (escala Fibonacci, factores a considerar, proceso de planning poker), supuestos clave, y disclaimers sobre que es una proyección inicial.

- **FR-008**: El comando DEBE incluir una sección "Vinculación con Modelo de Costos" explicando cómo los Story Points se traducen a esfuerzo y costo.

- **FR-009**: El comando DEBE referenciar los documentos previos en la cadena de estimación: PRD, Solution Vision, Tech Design, Backlog.

- **FR-010**: El comando DEBE ejecutar un gate de validación (`.specify/gates/raise/gate-estimation.md`) antes de finalizar, verificando que el roadmap cumple criterios de calidad.

- **FR-011**: El comando DEBE incluir handoff al siguiente comando (`raise.7.sow`) en el frontmatter YAML para mantener la continuidad del flujo de estimación.

- **FR-012**: El comando DEBE aplicar el principio Jidoka (parar en defectos) si: (1) el backlog no existe o está incompleto, (2) el backlog no tiene estimaciones en SP, (3) la capacidad del equipo es inválida o no realista.

### Key Entities

- **Estimation Roadmap Document**: Artefacto resultante que contiene guía de estimación, tabla de items del backlog con SP, parámetros de equipo/sprints, roadmap proyectado por iteraciones, métricas totales, vinculación con costos.

- **Team Parameters**: Configuración del equipo (estructura de roles con dedicación %, capacidad en SP/sprint, duración de sprints) que determina la velocidad del proyecto.

- **Iteration**: Unidad de tiempo (sprint) en el roadmap proyectado, con atributos: número, fechas estimadas, objetivo, items planeados del backlog, SP de la iteración, SP acumulados.

- **Backlog Item Estimation**: Mapeo de cada Epic/Feature/User Story a su estimación en Story Points, con contexto de prioridad y dependencias.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Arquitectos de Preventa pueden generar un Estimation Roadmap completo desde un Backlog en menos de 10 minutos de ejecución del comando.

- **SC-002**: El roadmap proyectado tiene un error de proyección menor al 20% cuando se compara con la duración real del proyecto (basado en retrospectivas de proyectos previos).

- **SC-003**: El 100% de los items del backlog con estimaciones en SP aparecen en la tabla de estimaciones del roadmap generado.

- **SC-004**: El roadmap incluye una explicación clara de cómo Story Points se convierten en esfuerzo (horas/días) y costo, permitiendo al usuario preparar el SoW sin información faltante.

- **SC-005**: El comando detecta y alerta sobre backlog items sin estimaciones, sugiriendo valores preliminares y señalando que deben refinarse.

- **SC-006**: El comando identifica correctamente qué iteraciones corresponden al MVP basándose en las Features marcadas como MVP en el backlog.

- **SC-007**: Usuarios pueden parametrizar la estructura del equipo (roles, dedicación, capacidad) y el roadmap se ajusta dinámicamente al cálculo.

## Dependencies *(mandatory)*

### Internal Dependencies

- **Comando `raise.5.backlog`**: Este comando (`raise.6.estimation`) depende de que el backlog haya sido generado previamente. Sin `specs/main/project_backlog.md`, el comando no puede ejecutarse.

- **Template `estimation_roadmap.md`**: Debe existir en `src/templates/solution/` y estar completo con todas las secciones requeridas.

- **Gate `gate-estimation.md`**: Debe existir en `.raise-kit/gates/raise/` para validar el roadmap generado.

### External Dependencies

- **Kata L1-04 (Paso 6)**: El comando implementa el paso 6 del kata L1-04-Estimar-Requerimiento.md: "Realizar la estimación detallada".

- **Principios de Estimación Ágil**: El comando asume conocimiento de Story Points, escala Fibonacci, y planning poker. Estos conceptos se explican en el roadmap generado.

### Data Dependencies

- **Backlog con Estimaciones en SP**: El comando requiere que las User Stories en el backlog tengan estimaciones (columna "Estimación (SP)"). Si faltan, el comando debe proponer valores preliminares.

- **Parámetros de Capacidad del Equipo**: Si no se proporcionan, el comando usa defaults razonables (1 architect 50%, 1 engineer 100%, 1 QA 50%, sprints de 2 semanas, capacidad de 16 SP/sprint).

## Assumptions *(mandatory)*

- **Asunción 1**: El Project Backlog ya fue generado usando `/raise.5.backlog` y contiene User Stories con estimaciones en Story Points. Si faltan estimaciones, el comando puede proponer preliminares.

- **Asunción 2**: El template `estimation_roadmap.md` sigue la estructura del ejemplo en `src/templates/solution/estimation_roadmap.md` (visto en el template real del repo).

- **Asunción 3**: La escala de estimación por defecto es Fibonacci modificada: 1, 2, 3, 5, 8, 13, 20, 40, 100 (como se usa en SAFe y otros frameworks ágiles).

- **Asunción 4**: La capacidad del equipo se mide en Story Points por sprint, no en horas directamente. La conversión SP → horas se documenta en la sección de costos del roadmap pero no es obligatoria para generar el roadmap.

- **Asunción 5**: Las iteraciones (sprints) tienen duración fija (por defecto 2 semanas) y la capacidad del equipo se asume constante a lo largo del proyecto (no hay ramp-up o ramp-down).

- **Asunción 6**: El roadmap es una proyección inicial que debe refinarse después de las primeras iteraciones reales, cuando el equipo haya medido su velocidad real.

- **Asunción 7**: Los supuestos de costo (tarifas horarias, factores de conversión SP/horas) pueden estar ausentes en el roadmap inicial y completarse luego para el SoW. Esta información es opcional para generar el roadmap.

- **Asunción 8**: El comando se ejecuta en el contexto del framework RaiSE donde todos los artefactos previos (PRD, Vision, Tech Design, Backlog) ya existen en `specs/main/`.

## Constraints *(mandatory)*

- **Restricción 1**: El comando DEBE ubicarse en `.raise-kit/commands/02-projects/raise.6.estimation.md` siguiendo la convención de la regla 110.

- **Restricción 2**: El comando DEBE seguir la estructura estándar de comandos RaiSE (frontmatter YAML, User Input, Outline, High-Signaling Guidelines, AI Guidance) como se define en la regla 110-raise-kit-command-creation.md.

- **Restricción 3**: Todas las referencias a templates, gates y scripts DEBEN usar rutas `.specify/` (NO `.raise-kit/`) para portabilidad cuando el comando se inyecte a proyectos target.

- **Restricción 4**: El contenido generado (roadmap) DEBE estar en ESPAÑOL, mientras las instrucciones del comando (outline, guidelines) están en INGLÉS.

- **Restricción 5**: El comando NO DEBE modificar el template `estimation_roadmap.md` existente - solo lo usa como base para instanciar el roadmap del proyecto.

- **Restricción 6**: El comando DEBE ejecutar el gate de validación y NO continuar si el gate falla en criterios obligatorios (principio Jidoka).

## Non-Functional Requirements *(optional)*

### Usability

- El comando debe ser fácil de ejecutar: simplemente `/raise.6.estimation` sin argumentos obligatorios (usa defaults razonables).

- El roadmap generado debe ser legible por stakeholders no técnicos: usar lenguaje claro, evitar jerga innecesaria, incluir explicaciones de conceptos (qué es un Story Point, qué es un sprint).

### Maintainability

- El comando debe seguir estrictamente la estructura de la regla 110 para facilitar mantenimiento futuro y consistencia con otros comandos del framework.

- Cada paso del outline debe tener verificación y Jidoka block documentados para facilitar debugging si el comando falla.

### Documentation

- El roadmap debe incluir disclaimers claros sobre que es una proyección inicial y debe refinarse con datos reales.

- El roadmap debe documentar todos los supuestos clave (capacidad del equipo, duración de sprints, factores de conversión) para que el usuario pueda ajustarlos si no aplican a su contexto.
