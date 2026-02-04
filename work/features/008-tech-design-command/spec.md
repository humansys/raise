# Feature Specification: Tech Design Command Generation

**Feature Branch**: `001-tech-design-command`  
**Created**: 2026-01-20  
**Status**: Draft  
**Input**: User description: "Comando para generación de Tech Design desde Solution Vision"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Tech Design from Solution Vision (Priority: P1)

Un Arquitecto de Preventa o Líder Técnico ejecuta el comando `/raise.4.tech-design` después de tener una Solution Vision aprobada. El comando carga automáticamente el documento de Solution Vision, sigue los 15 pasos del kata `flujo-03-tech-design`, y genera un documento de Tech Design completo usando el template `tech_design.md`.

**Why this priority**: Este es el core del feature - sin la generación básica del Tech Design, no hay funcionalidad. Es el MVP mínimo viable que permite completar el paso 4 del kata L1-04-Estimar-Requerimiento.

**Independent Test**: Se puede probar ejecutando `/raise.4.tech-design` en un proyecto que tenga `specs/main/solution_vision.md` y verificando que se genera `specs/main/tech_design.md` con todas las secciones del template completadas.

**Acceptance Scenarios**:

1. **Given** existe `specs/main/solution_vision.md` aprobado, **When** el usuario ejecuta `/raise.4.tech-design`, **Then** se genera `specs/main/tech_design.md` con frontmatter YAML completo y todas las secciones del template instanciadas
2. **Given** el Tech Design ha sido generado, **When** el usuario revisa el documento, **Then** cada una de las 14 secciones del template contiene información coherente derivada de la Solution Vision
3. **Given** el Tech Design está completo, **When** el usuario revisa el frontmatter YAML, **Then** encuentra `handoffs` apuntando a `raise.5.backlog` como siguiente paso

---

### User Story 2 - Guided Step-by-Step Execution (Priority: P2)

El comando guía al usuario a través de los 15 pasos del kata `flujo-03-tech-design`, mostrando el paso actual, su propósito, y los criterios de verificación. Si el usuario no puede continuar en algún paso (falta información crítica), el comando implementa Jidoka (parar en defectos) y sugiere acciones correctivas.

**Why this priority**: Mejora la experiencia del usuario y asegura que se sigan las mejores prácticas del kata, pero el comando puede funcionar sin esta guía explícita.

**Independent Test**: Ejecutar el comando y verificar que muestra mensajes de progreso para cada uno de los 15 pasos del kata, y que se detiene apropiadamente si falta el archivo de Solution Vision.

**Acceptance Scenarios**:

1. **Given** el usuario ejecuta `/raise.4.tech-design`, **When** el comando procesa cada paso, **Then** muestra el número de paso, título, y criterio de verificación antes de ejecutarlo
2. **Given** no existe `specs/main/solution_vision.md`, **When** el usuario ejecuta el comando, **Then** el comando se detiene en el Paso 1 con mensaje "JIDOKA: Solution Vision no encontrado. Ejecutar `/raise.2.vision` primero."
3. **Given** el comando encuentra información ambigua en la Vision, **When** procesa el Paso 4 (Solución Propuesta), **Then** marca la sección con `[NEEDS CLARIFICATION: ...]` y continúa con valores por defecto razonables

---

### User Story 3 - Validation and Handoff (Priority: P3)

Después de generar el Tech Design, el comando valida que el documento cumple con los requisitos mínimos de completitud y sugiere al usuario ejecutar el siguiente comando del flujo (`/raise.5.backlog`).

**Why this priority**: Nice-to-have que mejora la calidad y continuidad del flujo, pero no es esencial para la funcionalidad básica.

**Independent Test**: Generar un Tech Design y verificar que el comando muestra un resumen de validación y el handoff al siguiente comando.

**Acceptance Scenarios**:

1. **Given** el Tech Design ha sido generado, **When** el comando finaliza, **Then** muestra un resumen con: "✓ Tech Design generado en specs/main/tech_design.md" y "→ Siguiente paso: `/raise.5.backlog`"
2. **Given** el Tech Design generado tiene secciones vacías críticas, **When** el comando valida, **Then** muestra advertencias: "⚠ Sección 'Arquitectura de Componentes' está vacía - revisar manualmente"

---

### Edge Cases

- ¿Qué pasa cuando `solution_vision.md` existe pero está vacío o mal formado?
- ¿Cómo maneja el comando un Tech Design parcialmente existente (regeneración vs actualización)?
- ¿Qué sucede si el template `tech_design.md` no se encuentra en `src/templates/tech/`?
- ¿Cómo se comporta si el usuario ejecuta el comando fuera del directorio del proyecto?

## Requirements *(mandatory)*

### Functional Requirements

#### Estructura de Archivos en .raise-kit

- **FR-001**: El comando DEBE crearse en `.raise-kit/commands/02-projects/raise.4.tech-design.md` siguiendo la estructura de comandos existentes
- **FR-002**: El template `tech_design.md` DEBE copiarse desde `src/templates/tech/tech_design.md` a `.raise-kit/templates/raise/tech/tech_design.md` (crear directorio `tech/` si no existe)
- **FR-003**: El gate `gate-design.md` DEBE verificarse que existe en `.raise-kit/gates/gate-design.md` (ya existe desde `src/gates/gate-design.md`)

#### Referencias dentro del Comando (usando .specify)

- **FR-004**: El comando DEBE referenciar el template como `.specify/templates/raise/tech/tech_design.md` (no `.raise-kit/templates/...`)
- **FR-005**: El comando DEBE referenciar el gate como `.specify/gates/raise/gate-design.md` (no `.raise-kit/gates/...`)
- **FR-006**: El comando DEBE referenciar scripts helper como `.specify/scripts/bash/check-prerequisites.sh` (siguiendo patrón de `raise.1.discovery`)

#### Comportamiento del Comando

- **FR-007**: El comando DEBE cargar `specs/main/solution_vision.md` como input antes de iniciar la generación
- **FR-008**: El comando DEBE producir el archivo de salida en `specs/main/tech_design.md`
- **FR-009**: El comando DEBE seguir los 15 pasos definidos en el kata `flujo-03-tech-design` en orden secuencial
- **FR-010**: El comando DEBE completar el frontmatter YAML con: document_id, title, project_name, client, version, date, author, related_docs (incluyendo referencia a solution_vision.md), y status
- **FR-011**: El comando DEBE incluir en el frontmatter un campo `handoffs` que apunte a `raise.5.backlog` como siguiente comando
- **FR-012**: El comando DEBE implementar Jidoka: si `solution_vision.md` no existe, DEBE detenerse y mostrar mensaje de error indicando ejecutar `/raise.2.vision` primero
- **FR-013**: El comando DEBE generar contenido en español para todas las secciones del Tech Design
- **FR-014**: El comando DEBE completar las 14 secciones del template: Visión General, Solución Propuesta, Arquitectura de Componentes, Flujo de Datos, Contratos de API, Modelo de Datos, Algoritmos Clave, Seguridad, Manejo de Errores, Alternativas Consideradas, Preguntas Abiertas, Consideraciones para Estimación, y Estrategia de Pruebas
- **FR-015**: El comando DEBE ejecutar el gate de validación `.specify/gates/raise/gate-design.md` al finalizar la generación

### Key Entities *(include if feature involves data)*

- **Comando Raise**: Archivo markdown ubicado en `.raise-kit/commands/02-projects/raise.4.tech-design.md` que contiene las instrucciones para el agente. Usa referencias a `.specify/` para portabilidad cuando se inyecta en proyectos target.
- **Template Tech Design**: Archivo markdown ubicado en `.raise-kit/templates/raise/tech/tech_design.md` (copiado desde `src/templates/tech/tech_design.md`), define la estructura y secciones requeridas para el documento de diseño técnico.
- **Gate Design**: Archivo markdown ubicado en `.raise-kit/gates/gate-design.md` (ya existe, copiado desde `src/gates/gate-design.md`), contiene los criterios de validación que debe cumplir un Tech Design.
- **Solution Vision Document**: Documento de entrada ubicado en `specs/main/solution_vision.md` del proyecto target, contiene la visión de alto nivel de la solución.
- **Tech Design Document**: Documento de salida ubicado en `specs/main/tech_design.md` del proyecto target, contiene el diseño técnico detallado generado por el comando.
- **Kata Flujo Tech Design**: Documento de proceso ubicado en `src/katas-v2.1/flujo/03-tech-design.md`, define los 15 pasos a seguir para crear un Tech Design (usado como referencia para estructurar el comando).

### Arquitectura de .raise-kit

El proceso de inyección funciona así:

1. **Desarrollo en raise-commons**: Los artefactos se crean/actualizan en `.raise-kit/` (comandos, templates, gates)
2. **Referencias portables**: Los comandos usan rutas `.specify/` en lugar de `.raise-kit/` para que funcionen cuando se inyecten
3. **Inyección en proyecto target**: El script `transform-commands.sh` copia todo desde `.raise-kit/` a `.specify/` del proyecto target
4. **Ejecución en proyecto target**: El comando ahora encuentra sus dependencias en `.specify/` del proyecto donde se ejecuta

### Setup Requerido para Tech Design

Para completar el setup del comando de tech design en `.raise-kit`, se requieren estos pasos:

1. **Crear directorio para templates tech**:
   ```bash
   mkdir -p .raise-kit/templates/raise/tech
   ```

2. **Copiar template desde src**:
   ```bash
   cp src/templates/tech/tech_design.md .raise-kit/templates/raise/tech/tech_design.md
   ```

3. **Crear el comando**:
   Crear `.raise-kit/commands/02-projects/raise.4.tech-design.md` con referencias a `.specify/`

4. **Verificar gate** (ya debe existir):
   ```bash
   ls -la .raise-kit/gates/gate-design.md
   ```

**IMPORTANTE**: El script `transform-commands.sh` **NO requiere modificación**. Ya está diseñado para copiar recursivamente todos los subdirectorios de `templates/`, `gates/`, y `commands/`. Cuando se ejecute la inyección, automáticamente copiará:
- `.raise-kit/templates/raise/tech/*` → `.specify/templates/raise/tech/*`
- `.raise-kit/gates/*` → `.specify/gates/*`
- `.raise-kit/commands/02-projects/*` → `.claude/commands/02-projects/*`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El comando genera un Tech Design completo en menos de 5 minutos de ejecución
- **SC-002**: El 100% de las secciones del template `tech_design.md` contienen contenido (no están vacías ni con placeholders sin reemplazar)
- **SC-003**: El Tech Design generado es comprensible para un desarrollador senior que no ha leído el PRD ni la Vision (auto-contenido)
- **SC-004**: El comando se detiene apropiadamente si falta el archivo de Solution Vision (Jidoka implementado)
- **SC-005**: El frontmatter YAML del Tech Design generado incluye el handoff correcto a `/raise.5.backlog`
- **SC-006**: El comando sigue el patrón de estructura de los comandos existentes (`raise.1.discovery` y `raise.2.vision`) en términos de formato, secciones, y estilo de instrucciones
- **SC-007**: El setup en `.raise-kit` está completo: template en `templates/raise/tech/`, comando en `commands/02-projects/`, y gate verificado en `gates/`, sin necesidad de modificar `transform-commands.sh`

## Assumptions

- **A-001**: El template `src/templates/tech/tech_design.md` está completo, validado, y listo para copiar a `.raise-kit/templates/raise/tech/`
- **A-002**: El gate `src/gates/gate-design.md` ya existe en `.raise-kit/gates/gate-design.md` (fue copiado previamente)
- **A-003**: El kata `src/katas-v2.1/flujo/03-tech-design.md` define correctamente los 15 pasos necesarios para crear un Tech Design
- **A-004**: Los comandos existentes (`raise.1.discovery`, `raise.2.vision`) en `.raise-kit/commands/02-projects/` son el patrón canónico a seguir
- **A-005**: El script `transform-commands.sh` en `.raise-kit/scripts/` funciona correctamente para inyectar el kit en proyectos target
- **A-006**: Cuando se ejecuta en un proyecto target, la Solution Vision (`specs/main/solution_vision.md`) ha pasado por Gate-Vision y está aprobada
- **A-007**: El usuario ejecutará el comando desde el directorio raíz del proyecto target (no desde raise-commons)

## Dependencies

### Fase de Desarrollo (en raise-commons)

- **D-001**: Template source `src/templates/tech/tech_design.md` debe existir para copiar a `.raise-kit/templates/raise/tech/`
- **D-002**: Gate source `src/gates/gate-design.md` debe existir (ya copiado a `.raise-kit/gates/`)
- **D-003**: Kata `src/katas-v2.1/flujo/03-tech-design.md` debe existir para estructurar los pasos del comando
- **D-004**: Comandos de referencia (`raise.1.discovery`, `raise.2.vision`) deben existir en `.raise-kit/commands/02-projects/` para seguir el patrón

### Fase de Ejecución (en proyecto target)

- **D-005**: Solution Vision (`specs/main/solution_vision.md`) debe existir en el proyecto target antes de ejecutar el comando
- **D-006**: El kit debe haber sido inyectado al proyecto target usando `transform-commands.sh` (copia `.raise-kit/` → `.specify/`)
- **D-007**: Scripts helper (`.specify/scripts/bash/check-prerequisites.sh`) deben estar disponibles en el proyecto target
