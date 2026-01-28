---
description: Generate a Project Backlog from an approved Tech Design, following the 10 steps of kata flujo-05-backlog-creation.
handoffs:
  - label: Create Estimation Roadmap
    agent: raise.6.estimation
    prompt: Generate estimation roadmap and timeline from this backlog
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Populate the Project Backlog template (`.specify/templates/raise/backlog/project_backlog.md`) with content derived from the Tech Design, producing `specs/main/project_backlog.md` with Epics, Features, User Stories, prioritization, and estimation.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load the template from `.specify/templates/raise/backlog/project_backlog.md`.
   - Prepare output file at `specs/main/project_backlog.md`.
   - **Verificación**: Template loaded, paths confirmed.
   - > **Si no puedes continuar**: Template not found → **JIDOKA**: Check .raise-kit setup and verify template was copied correctly.

2. **Paso 1: Cargar Tech Design y Contexto**:
   - Cargar `specs/main/tech_design.md` como input principal.
   - Cargar `specs/main/project_requirements.md` (PRD) como referencia de requisitos.
   - Cargar `specs/main/solution_vision.md` como referencia de visión.
   - Identificar componentes, funcionalidades y scope MVP desde el Tech Design.
   - Analizar secciones clave: Arquitectura y Componentes, Contratos de API, Modelo de Datos, Scope MVP.
   - **Verificación**: Tech Design exists and contains required sections (components, architecture, MVP scope).
   - > **Si no puedes continuar**: Tech Design missing → **JIDOKA**: Execute `/raise.4.tech-design` first to create Tech Design. Tech Design incomplete (missing components/architecture sections) → **JIDOKA**: List missing sections and request completion before continuing.

3. **Paso 2: Instanciar Template Backlog**:
   - Copiar template a `specs/main/project_backlog.md`.
   - Completar frontmatter YAML metadata: document_id (BCK-PROJECT-001), title, project_name, client, version (1.0), date, author.
   - Agregar `related_docs` referenciando PRD, Vision y Tech Design.
   - Establecer status como "Draft".
   - Completar sección "1. Descripción General" con propósito del backlog y relación con otros documentos.
   - **Verificación**: File exists at specs/main/project_backlog.md with complete metadata (no placeholders).
   - > **Si no puedes continuar**: Write permission error → **JIDOKA**: Check file system permissions. Existing file detected → Ask user if they want to overwrite or edit existing backlog.

4. **Paso 3: Identificar Epics**:
   - Analizar componentes y módulos identificados en Tech Design (sección Arquitectura).
   - Agrupar funcionalidad relacionada en 3-7 Epics (bloques grandes de trabajo).
   - Cada Epic representa un módulo o capacidad completa del sistema.
   - Asignar IDs secuenciales (EPIC-001, EPIC-002, etc.).
   - Para cada Epic: definir título descriptivo, descripción, y valor de negocio.
   - Completar tabla de Epics en sección "3. Epics" del backlog.
   - **Verificación**: 3-7 Epics identified, each with clear value proposition, mapped to Tech Design components.
   - > **Si no puedes continuar**: Too many Epics (>7) → **JIDOKA**: Consolidate related ones - multiple components can belong to same Epic. Too few Epics (<3) → **JIDOKA**: Decompose large Epics - look for natural boundaries in Tech Design architecture.

5. **Paso 4: Descomponer Epics en Features**:
   - Para cada Epic identificado, descomponer en Features (funcionalidades específicas).
   - Cada Feature debe: entregar valor independiente, ser desplegable por separado, tener tamaño 1-4 semanas.
   - Asignar Feature IDs (FEAT-001, FEAT-002, etc.).
   - Para cada Feature: definir título, descripción, criterios de aceptación alto nivel, referencias a PRD y Tech Design.
   - Completar tablas de Features en sección "4. Features" (una tabla por Epic).
   - **Verificación**: Each Epic has 2-5 Features, each Feature has name, description, acceptance criteria, and references to PRD/Tech Design sections.
   - > **Si no puedes continuar**: Features too large (>4 weeks estimated) → **JIDOKA**: Apply vertical slicing - split by user scenario or data subset. Features too small (<1 week) → **JIDOKA**: Combine related functionality into single Feature.

6. **Paso 5: Priorizar Features**:
   - Aplicar matriz de priorización: Score = Valor de Negocio / Complejidad Técnica.
   - Considerar dependencias técnicas entre Features (del Tech Design).
   - Marcar Features que pertenecen al MVP scope (identificado en Tech Design).
   - Asignar prioridad a cada Feature: Alta (MVP, core value), Media (importante but not MVP), Baja (nice-to-have).
   - Documentar justificación de prioridad en columna correspondiente.
   - Proponer defaults basados en MVP scope del Tech Design, señalar que deben validarse con Product Owner.
   - **Verificación**: All Features have priority (Alta/Media/Baja) with documented justification, MVP Features clearly marked.
   - > **Si no puedes continuar**: Unclear priorities (MVP not defined in Tech Design) → **JIDOKA**: Facilitate session with Product Owner, or use default: Core business value = Alta, enhancments = Media, nice-to-have = Baja. Document that priorities must be validated.

7. **Paso 6: Descomponer Features en User Stories**:
   - Para cada Feature, crear 3-8 User Stories (unidades de trabajo).
   - Formato estándar: "Como [rol], quiero [acción/funcionalidad], para [beneficio/valor]".
   - Aplicar principios INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.
   - Asignar US IDs (US-001, US-002, etc.).
   - Identificar roles desde PRD (sección stakeholders) o usar roles genéricos (Usuario, Administrador, Sistema).
   - Completar tablas de User Stories en sección "5. Historias de Usuario" (una tabla por Feature).
   - **Verificación**: Each Feature has 3-8 User Stories, all follow "Como/Quiero/Para" format, each US fits in 1 sprint (≤2 weeks).
   - > **Si no puedes continuar**: Stories too large (>2 weeks) → **JIDOKA**: Apply INVEST splitting techniques - split by scenario, data, workflow, business rule, or acceptance criteria. Stories lack clear user benefit → **JIDOKA**: Revisit "para" clause - every story must deliver observable value to a user.

8. **Paso 7: Escribir Criterios de Aceptación BDD**:
   - Para cada User Story, escribir 2-3 escenarios de aceptación en formato BDD.
   - Formato estándar: "Dado que [contexto inicial], Cuando [acción del usuario], Entonces [resultado esperado]".
   - Cubrir: happy path (escenario principal), validaciones (datos incorrectos), edge cases (límites).
   - Asegurar que cada criterio es específico, testeable, y verificable.
   - Agregar criterios en columna "Criterios de Aceptación" de cada User Story.
   - **Verificación**: Each User Story has ≥2 BDD scenarios (Dado/Cuando/Entonces), scenarios are specific (not generic), cover happy path + validations/edge cases.
   - > **Si no puedes continuar**: Vague criteria (e.g., "funciona correctamente") → **JIDOKA**: Ask "How would I write the automated test for this?" for each criterion - this forces specificity. Missing edge cases → **JIDOKA**: Consider: invalid input, missing data, concurrent users, system limits.

9. **Paso 8: Añadir Detalles Técnicos**:
   - Para cada User Story, añadir contexto técnico desde Tech Design.
   - Referenciar: componentes afectados (del diagrama de arquitectura), endpoints API (de contratos), cambios en modelo de datos (de sección data model).
   - Documentar dependencias con otras User Stories si existen.
   - Completar subsección "Detalles Técnicos" para cada US (puede ser lista o mini-tabla).
   - **Verificación**: Each User Story has "Detalles Técnicos" section linking to specific Tech Design components (architecture, API, data model).
   - > **Si no puedes continuar**: User Story not mappable to Tech Design → **JIDOKA**: Review if US is in scope. If yes, Tech Design may need update to include missing components. If no, remove US from backlog.

10. **Paso 9: Estimar User Stories**:
    - Asignar Story Points a cada User Story usando escala Fibonacci: 1, 2, 3, 5, 8, 13.
    - Considerar: complejidad técnica (de Tech Design), incertidumbre (cuánto conocemos), dependencias (bloqueos).
    - Proponer estimaciones por defecto basadas en complejidad aparente del Tech Design.
    - Señalar que estimaciones son preliminares y deben refinarse en planning poker con equipo completo.
    - Documentar en columna "Estimación (SP)" de cada User Story.
    - **Verificación**: All User Stories have Story Point estimations, no User Story > 8 points.
    - > **Si no puedes continuar**: User Story > 8 points → **JIDOKA**: Subdivide into smaller stories - 8 SP is upper limit for stories (13+ indica que la historia es demasiado grande). Estimates very disparate (1 SP junto a 13 SP en mismo Feature) → **JIDOKA**: Document assumptions - may indicate misunderstanding of scope.

11. **Paso 10: Completar Backlog y Calcular Totales**:
    - Ordenar User Stories considerando: prioridad del Feature padre, dependencias técnicas, valor, reducción de riesgo.
    - Calcular totales de Story Points por Epic (sumar todas las US del Epic).
    - Generar distribución por complejidad: contar cuántas US hay de cada tamaño (1 SP, 2 SP, 3 SP, etc.).
    - Identificar MVP slice: marcar el subset mínimo de Features/US que entrega core value (debe ser ≤50% del total de Story Points).
    - Completar sección "8. Resumen de Estimaciones" con: totales por Epic, distribución por complejidad, métricas del MVP (Total SP MVP / Total SP General).
    - Completar sección "9. Listado de Dependencias Clave" si hay dependencias críticas entre elementos.
    - **Verificación**: Backlog ordered by priority+dependencies, MVP identified and ≤50% of total Story Points, summary section complete with all metrics.
    - > **Si no puedes continuar**: MVP > 50% of total → **JIDOKA**: Apply iteratively: "What can I defer to post-MVP and still deliver value?" - MVP debe ser *mínimo* viable, no máximo deseable. Remove nice-to-have Features from MVP scope.

12. **Paso 11: Finalize & Validate**:
    - Confirmar que `specs/main/project_backlog.md` existe y está completo.
    - Ejecutar gate de validación: `.specify/gates/raise/gate-backlog.md`.
    - Capturar resultados del gate (criterios pasados/fallidos).
    - **Si gate FALLA**: Listar criterios fallidos específicos, sugerir correcciones concretas, permitir iteración antes de continuar.
    - **Si gate PASA**: Mostrar resumen del backlog (cantidad de Epics, Features, User Stories, Total SP, MVP SP, ratio MVP/Total).
    - Ejecutar `.specify/scripts/bash/update-agent-context.sh` para actualizar contexto del agente.
    - Mostrar handoff al siguiente comando: "→ Siguiente paso: `/raise.6.estimation` - Create estimation roadmap and timeline from this backlog".
    - **Verificación**: Gate executed, validation results shown (pass/fail with details), handoff to raise.6.estimation offered.
    - > **Si no puedes continuar**: Gate failures (criterios obligatorios fallidos) → **JIDOKA**: Iterate on failed criteria before proceeding - no continuar con backlog inválido. Gate script not found → **JIDOKA**: Verify .raise-kit setup.

---

## Notes

### Roles en User Stories

Si el Tech Design o PRD no define roles explícitamente:
- Inferir desde contexto del PRD (sección de usuarios/stakeholders)
- Usar roles genéricos: Usuario (end user), Administrador (admin user), Sistema (automated process)
- Señalar en documentación que roles deben refinarse con Product Owner

### Backlog ya Existente

Si detectas que `specs/main/project_backlog.md` ya existe:
- Preguntar al usuario si desea sobrescribir o editar el existente
- Si sobrescribir: proceder normalmente
- Si editar: cargar existente y aplicar updates incrementales

### Estimaciones Preliminares

Las estimaciones iniciales son aproximaciones basadas en Tech Design. Comunicar claramente:
- Son preliminares y deben validarse en planning poker con equipo
- Pueden cambiar significativamente después de refinamiento
- Sirven para dimensionamiento inicial del proyecto

---

## High-Signaling Guidelines

**Output**: El comando genera `specs/main/project_backlog.md` con estructura completa: Epics, Features, User Stories, criterios BDD, estimaciones, MVP identificado.

**Focus**: Backlog generation from Tech Design. Priorizar claridad, trazabilidad (cada elemento enlazado al Tech Design), y calidad de User Stories (formato estándar, INVEST principles).

**Language**: Instructions in English for AI agent. Generated backlog content in Spanish (User Stories, criterios, descripciones).

**Jidoka**: Stop immediately if: (1) Tech Design missing or incomplete, (2) MVP > 50% of total (violates minimum viable principle), (3) Gate mandatory criteria fail. Signal to user and request correction before continuing.

---

## AI Guidance

1. **Role**: You are orchestrating backlog generation as defined in kata `flujo-05-backlog-creation`. Your role is to guide the Líder Técnico/Arquitecto through structured decomposition of Tech Design into actionable backlog.

2. **Be proactive**: Propose reasonable defaults for priorities and estimations based on Tech Design analysis, but always signal that these must be validated with Product Owner and team. Don't wait for user to provide every detail - infer from available context.

3. **Follow Katas**: The 10 steps in this outline map directly to kata `src/katas-v2.1/flujo/05-backlog-creation.md`. Each step has clear inputs, outputs, and verification criteria. Do not skip steps or reorder them.

4. **Traceability**: Every Epic/Feature/User Story must be traceable back to Tech Design. Link explicitly: "Este Epic corresponde a los componentes X, Y del Tech Design". This ensures backlog is grounded in technical reality.

5. **Gates**: Execute `gate-backlog.md` at step 11. This gate has 7 mandatory criteria that MUST pass. If gate fails, identify specific issues and guide user through fixes before offering handoff to next command.

6. **Heutagogy**: This command facilitates user learning about backlog creation. Explain the "why" behind each step (e.g., "Why BDD criteria? To ensure stories are testable"). Guide, don't dictate - user makes final decisions on priorities and estimates.

7. **MVP Discipline**: Be strict about MVP scope (≤50% rule). Many projects fail because MVP is too large. Help user identify true minimum by asking: "Can we deliver value without this Feature?". Defer nice-to-haves aggressively.
