# Implementation Plan: Comando raise.5.backlog

**Branch**: `009-backlog-command` | **Date**: 2026-01-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-backlog-command/spec.md`

## Summary

Create the `/raise.5.backlog` command that generates a project backlog document from an approved Tech Design. The command follows the 10-step kata `flujo-05-backlog-creation` to decompose Tech Design into Epics, Features, and User Stories with prioritization, estimation, and validation via `gate-backlog.md`. The command is a Markdown file that orchestrates the AI agent through a structured workflow using the RaiSE Kit command pattern.

## Technical Context

**Language/Version**: Markdown (CommonMark spec) for command file, Bash for scripts
**Primary Dependencies**:
- Template: `src/templates/backlog/project_backlog.md`
- Kata: `src/katas-v2.1/flujo/05-backlog-creation.md`
- Gate: `src/gates/gate-backlog.md`
- Script: `.specify/scripts/bash/check-prerequisites.sh`
- Script: `.specify/scripts/bash/update-agent-context.sh`

**Storage**: Git-based text files (Markdown with YAML frontmatter)
**Testing**: Manual execution validation - execute command and verify output against gate criteria
**Target Platform**: Claude Code CLI (or any AI agent that can read Markdown command files)
**Project Type**: Documentation/orchestration (not traditional code)
**Performance Goals**: User can complete backlog generation in <60 minutes guided interaction
**Constraints**:
- Must follow RaiSE Kit command creation pattern
- Must use portable references (`.specify/` not `.raise-kit/`)
- Content in Spanish, instructions in English
- No modification of templates or gates

**Scale/Scope**: Single command file (~300-400 lines), orchestrates generation of backlog with 3-7 Epics, multiple Features, and User Stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### §1. Humanos Definen, Máquinas Ejecutan
**Status**: ✓ PASS

The command file defines WHAT the agent must do (10 steps from kata) in structured Markdown. The AI agent receives the command and executes it. The Líder Técnico/Arquitecto maintains ownership by guiding prioritization and estimation decisions.

### §2. Governance as Code
**Status**: ✓ PASS

The command itself is a versioned artifact in `.raise-kit/commands/02-projects/`. Templates, gates, and katas are all in Git. The command references these artifacts using paths, ensuring governance is code.

### §3. Platform Agnosticism
**Status**: ✓ PASS

The command is pure Markdown with no dependency on specific AI platforms. It works with Claude Code, Cursor, or any agent that can read Markdown commands. Git is the universal transport.

### §4. Validation Gates en Cada Fase
**Status**: ✓ PASS

The command explicitly executes `gate-backlog.md` at the end (Step 10 "Finalize & Validate"). The gate checks for:
- 3-7 Features with clear value
- Features priorizadas con justificación
- MVP slice ≤50% of total
- All US in correct format with BDD criteria
- All US estimated
- Product Owner approval

### §5. Heutagogía sobre Dependencia
**Status**: ✓ PASS (by design)

The command guides the user through decision-making (prioritization, estimation) rather than doing it automatically. Open questions Q1-Q3 in spec show awareness that user must learn and own the process. The command proposes defaults but signals that they must be validated with the team.

### §6. Mejora Continua (Kaizen)
**Status**: ✓ PASS

The command structure allows iterative improvement. If the backlog generation fails or requires many iterations, the command steps can be refined. The gate provides feedback for improvement.

### §7. Lean Software Development
**Status**: ✓ PASS

**Eliminar desperdicio**: Command reuses existing templates and gates, no duplication
**Jidoka (parar en defectos)**: Steps 1-2 implement explicit Jidoka blocks when Tech Design is missing or incomplete
**Decidir tarde**: Prioritization and estimation happen after Features are identified, not upfront
**Empoderar al equipo**: Command guides but doesn't dictate - user makes final decisions

### §8. Observable Workflow
**Status**: ✓ PASS

Every step has a **Verificación** section with observable criteria. The command produces a concrete artifact (`project_backlog.md`) that can be audited. The gate execution at the end provides traceable validation results.

**Constitution Check Result**: ALL PRINCIPLES PASS - No complexity justification needed.

## Project Structure

### Documentation (this feature)

```text
specs/009-backlog-command/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (command structure patterns)
├── quickstart.md        # Phase 1 output (how to use the command)
├── checklists/
│   └── requirements.md  # Spec quality validation (COMPLETED)
└── (tasks.md will be created by /speckit.tasks command)
```

### Source Code (repository root)

```text
.raise-kit/
├── commands/
│   └── 02-projects/
│       └── raise.5.backlog.md          # THE COMMAND (to be created)
├── templates/
│   └── raise/
│       └── backlog/
│           └── project_backlog.md      # Template (copy from src/)
├── gates/
│   └── raise/
│       └── gate-backlog.md             # Gate (copy from src/)
└── scripts/
    └── transform-commands.sh           # Existing injection script

src/
├── templates/backlog/
│   └── project_backlog.md              # Source template (EXISTS)
├── gates/
│   └── gate-backlog.md                 # Source gate (EXISTS)
└── katas-v2.1/flujo/
    └── 05-backlog-creation.md          # Kata reference (EXISTS)
```

**Structure Decision**: This feature creates a single Markdown command file that orchestrates AI agent behavior. It's not traditional source code but rather a "program" that the AI executes. The command will be placed in `.raise-kit/commands/02-projects/` following the RaiSE Kit pattern documented in `.agent/rules/110-raise-kit-command-creation.md`.

**Critical Setup Required**:
1. Copy `src/templates/backlog/project_backlog.md` to `.raise-kit/templates/raise/backlog/`
2. Copy `src/gates/gate-backlog.md` to `.raise-kit/gates/raise/`
3. Create the command file `.raise-kit/commands/02-projects/raise.5.backlog.md`

## Complexity Tracking

> **No violations to justify** - All constitution principles pass.

---

# Phase 0: Research & Decisions

## Research Tasks

### R1: Analyze Kata flujo-05-backlog-creation Structure

**Question**: What are the 10 steps defined in the kata and how do they map to the command outline?

**Source**: `src/katas-v2.1/flujo/05-backlog-creation.md`

**Findings**:

The kata defines 10 steps for backlog creation:

1. **Cargar Tech Design y Contexto** - Load Tech Design, PRD, Solution Vision, identify components and functionalities
2. **Identificar Features/Épicas** - Group functionality into 3-7 Features, each delivering independent value
3. **Priorizar Features** - Apply prioritization matrix (Valor/Complejidad), consider dependencies and MVP
4. **Descomponer Feature en User Stories** - Create US in "Como/Quiero/Para" format, following INVEST principles
5. **Escribir Criterios de Aceptación** - Write BDD criteria (Dado/Cuando/Entonces), cover happy path + edge cases
6. **Añadir Detalles Técnicos** - Enrich US with Tech Design references (components, endpoints, data model changes)
7. **Estimar User Stories** - Assign Story Points (Fibonacci), consider complexity/uncertainty/dependencies
8. **Ordenar Backlog** - Order US considering Feature priority, dependencies, value, risk reduction
9. **Identificar MVP Slice** - Mark minimum US set for functional release (≤50% of total backlog)
10. **Validar con Product Owner** - Present backlog for approval, confirm priorities and MVP

**Decision**: Command structure will have 12 steps (10 kata steps + Initialize Environment + Finalize & Validate)

**Rationale**: The kata steps are the core workflow, but we need initialization (load template, check prerequisites) and finalization (run gate, show handoff) as standard RaiSE Kit command practice.

### R2: Analyze Template Structure

**Question**: What sections does `project_backlog.md` template contain and how do they map to kata steps?

**Source**: `src/templates/backlog/project_backlog.md`

**Findings**:

Template sections:
1. **Frontmatter YAML** - metadata (document_id, title, project, version, related_docs)
2. **Descripción General** - Purpose and relationship to other docs
3. **Estructura del Backlog** - Hierarchy explanation (Epics → Features → US)
4. **Epics** - Table with ID, título, descripción, prioridad, estimación, estado
5. **Features** - Tables per Epic with ID, título, descripción, criterios, referencias, prioridad, estimación
6. **Historias de Usuario** - Tables per Feature with ID, historia, criterios, estimación, dependencias
7. **Tareas Técnicas** - Technical tasks not tied to US
8. **Resumen de Estimaciones** - Totals per Epic, distribution by complexity
9. **Listado de Dependencias Clave** - Critical dependencies between elements
10. **Vinculación con Roadmap** - Sprint planning preview
11. **Notas Adicionales** - Assumptions and clarifications

**Decision**: Command will fill sections 1-10 of template during execution. Sections 10-11 are optional/future enhancements.

**Rationale**: MVP of command covers core backlog structure. Sprint planning (section 10) belongs to `raise.6.estimation` command.

### R3: Analyze Gate Criteria

**Question**: What are the mandatory vs recommended criteria in gate-backlog?

**Source**: `src/gates/gate-backlog.md`

**Findings**:

**Mandatory (Must Pass)**:
1. 3-7 features con nombre y valor claro
2. Features priorizadas con justificación
3. MVP identificado (subset mínimo)
4. US formato correcto ("Como/Quiero/Para")
5. Cada US tiene ≥2 escenarios BDD
6. Todas US estimadas
7. Product Owner approval

**Recommended (Should Pass)**:
8. INVEST compliance
9. US conectadas a Tech Design
10. Dependencias sin ciclos

**Decision**: Command must ensure all 7 mandatory criteria are met. Steps will have explicit verification blocks matching these criteria.

**Rationale**: Gate is the acceptance criteria for the command output. Command structure must guarantee gate passage.

### R4: Study Reference Commands

**Question**: What is the standard RaiSE Kit command structure?

**Source**:
- `.raise-kit/commands/02-projects/raise.4.tech-design.md`
- `.agent/rules/110-raise-kit-command-creation.md`

**Findings**:

**Standard Structure**:
1. **Frontmatter YAML** - description + handoffs
2. **User Input** - $ARGUMENTS placeholder
3. **Outline** - Goal + numbered steps
   - Each step: Title (infinitive verb), Actions (bullet list), Verificación (observable criterion), Jidoka block (stop conditions)
4. **Notes** (optional) - Context for different scenarios
5. **High-Signaling Guidelines** - Output, Focus, Language, Jidoka summary
6. **AI Guidance** - Role, proactive behavior, kata following, traceability, gates

**Critical Conventions**:
- References use `.specify/` not `.raise-kit/` (portable after injection)
- Step 1 always "Initialize Environment" with check-prerequisites.sh
- Last step always "Finalize & Validate" with gate execution + handoff display
- Jidoka blocks format: `> **Si no puedes continuar**: [condition] → **JIDOKA**: [action]`

**Decision**: Follow this exact structure for raise.5.backlog command.

**Rationale**: Consistency across commands. Pattern is proven (used by discovery, vision, tech-design).

### R5: Determine Handoff Target

**Question**: What command should be offered as handoff after backlog is complete?

**Source**: PRD section 4.1 (Requisito 2.5), Vision doc flow diagram

**Findings**:

The estimation flow is:
- PRD → Discovery (raise.1)
- Solution Vision → Vision (raise.2)
- Tech Design → Tech Design (raise.4)
- Backlog → **Backlog (raise.5)** ← WE ARE HERE
- Estimation Roadmap → Estimation (raise.6) ← NEXT
- Statement of Work → SoW (raise.7)

**Decision**: Handoff target is `raise.6.estimation`

**Rationale**: Linear flow. After backlog with Story Points, next step is creating estimation roadmap and timeline.

---

# Phase 1: Design & Contracts

## Command Outline Design

Based on research, the command outline is:

### Step Structure (12 steps total)

**Step 1: Initialize Environment**
- Run check-prerequisites.sh
- Load template from `.specify/templates/raise/backlog/project_backlog.md`
- Prepare output at `specs/main/project_backlog.md`
- **Verification**: Template loaded, paths confirmed
- **Jidoka**: Template not found → Check .raise-kit setup

**Step 2: Cargar Tech Design y Contexto** (Kata Step 1)
- Load `specs/main/tech_design.md` as primary input
- Load `specs/main/project_requirements.md` (PRD) as reference
- Load `specs/main/solution_vision.md` as reference
- Identify components, functionalities, MVP scope from Tech Design
- **Verification**: Tech Design exists and contains components/architecture sections
- **Jidoka**: Tech Design missing → Execute `/raise.4.tech-design` first. Tech Design incomplete → List missing sections and request completion

**Step 3: Instanciar Template Backlog** (Setup)
- Copy template to `specs/main/project_backlog.md`
- Fill frontmatter YAML metadata
- Add related_docs references (PRD, Vision, Tech Design)
- Set status to "Draft"
- **Verification**: File exists with complete metadata
- **Jidoka**: Write permission error → Check file system permissions

**Step 4: Identificar Epics** (Kata Step 2, part 1)
- Analyze Tech Design components/modules
- Group related functionality into 3-7 Epics
- Each Epic represents a major capability/module
- Assign Epic IDs (EPIC-001, EPIC-002, etc.)
- **Verification**: 3-7 Epics identified, each with clear value proposition
- **Jidoka**: Too many Epics (>7) → Consolidate related ones. Too few (<3) → Decompose large ones

**Step 5: Descomponer Epics en Features** (Kata Step 2, part 2)
- For each Epic, identify Features that deliver independent value
- Each Feature should be deployable separately
- Features sized for 1-4 weeks of work
- Assign Feature IDs (FEAT-001, FEAT-002, etc.)
- **Verification**: Each Epic has 2-5 Features, each Feature has name, description, acceptance criteria
- **Jidoka**: Features too large → Apply vertical slicing. Features too small → Combine related functionality

**Step 6: Priorizar Features** (Kata Step 3)
- Apply prioritization matrix: Score = Valor Negocio / Complejidad
- Consider dependencies between Features
- Mark MVP scope (must-have Features)
- Document justification for priorities
- **Verification**: All Features have priority (Alta/Media/Baja) with justification, MVP clearly marked
- **Jidoka**: Unclear priorities → Facilitate session with Product Owner. Use default: Core business value = Alta, Nice-to-have = Baja

**Step 7: Descomponer Features en User Stories** (Kata Step 4)
- For each Feature, create 3-8 User Stories
- Format: "Como [rol], quiero [acción], para [beneficio]"
- Ensure stories are Independent, Valuable, Small, Testable (INVEST)
- Assign US IDs (US-001, US-002, etc.)
- **Verification**: Each Feature has 3-8 US, all follow standard format, each US fits in 1 sprint
- **Jidoka**: Stories too large → Apply INVEST splitting techniques. Stories lack clear user benefit → Revisit "para" clause

**Step 8: Escribir Criterios de Aceptación BDD** (Kata Step 5)
- For each User Story, write 2-3 BDD scenarios
- Format: "Dado que [context], Cuando [action], Entonces [outcome]"
- Cover happy path, validations, edge cases
- **Verification**: Each US has ≥2 scenarios in BDD format, scenarios are specific (not generic)
- **Jidoka**: Vague criteria → Ask "How would I write the automated test?" for each criterion

**Step 9: Añadir Detalles Técnicos** (Kata Step 6)
- For each US, add technical context from Tech Design
- Reference: components affected, API endpoints, data model changes
- Document: dependencies on other US
- **Verification**: Each US has "Detalles Técnicos" section linking to Tech Design components
- **Jidoka**: US not mappable to Tech Design → Review if US is in scope. If yes, Tech Design may need update

**Step 10: Estimar User Stories** (Kata Step 7)
- Assign Story Points to each US (Fibonacci: 1, 2, 3, 5, 8, 13)
- Consider: complexity, uncertainty, dependencies
- Propose default estimates based on Tech Design complexity
- Signal that estimates should be validated with team in planning poker
- **Verification**: All US have estimations, no US > 8 points
- **Jidoka**: US > 8 points → Subdivide into smaller stories. Estimates very disparate → Document assumptions

**Step 11: Completar Backlog y Calcular Totales** (Kata Steps 8-9)
- Order backlog considering Feature priority + dependencies
- Calculate totals per Epic
- Generate distribution by complexity (count by Story Points)
- Identify MVP slice (≤50% of total SP)
- Mark MVP stories clearly
- Complete "Resumen de Estimaciones" section
- **Verification**: Backlog ordered, MVP identified and ≤50% of total, summary section complete
- **Jidoka**: MVP > 50% → Apply "What can I defer and still deliver value?" iteratively

**Step 12: Finalize & Validate** (Kata Step 10 + Standard RaiSE close)
- Confirm file existence
- Execute gate `.specify/gates/raise/gate-backlog.md`
- Show validation results (criteria passed/failed)
- If failed: List specific issues, suggest corrections
- If passed: Show summary (# Epics, # Features, # US, Total SP, MVP SP)
- Run `.specify/scripts/bash/update-agent-context.sh`
- Display handoff: "→ Siguiente paso: `/raise.6.estimation`"
- **Verification**: Gate executed, results shown, handoff offered
- **Jidoka**: Gate failures → Iterate on failed criteria before proceeding

## Data Model

**Key Entities** (from spec):

**Epic**:
- ID (string, format: EPIC-NNN)
- Título (string)
- Descripción (string)
- Prioridad (enum: Alta|Media|Baja)
- Estimación Total (number, Story Points sum)
- Estado (enum: Por Iniciar|En Progreso|Completado)

**Feature**:
- ID (string, format: FEAT-NNN)
- Título (string)
- Descripción (string)
- Criterios de Aceptación (list of strings)
- PRD Ref (string, section reference)
- Tech Ref (string, section reference)
- Prioridad (enum: Alta|Media|Baja)
- Estimación (number, Story Points sum from US)
- Estado (enum: Por Iniciar|En Progreso|Completado)
- Epic Padre (ref: Epic ID)

**User Story**:
- ID (string, format: US-NNN)
- Historia (string, format: "Como [rol], quiero [acción], para [beneficio]")
- Criterios de Aceptación (list of BDD scenarios)
- Detalles Técnicos (object: {componentes, endpoints, dependencias})
- Estimación (number, Story Points 1-13)
- Dependencias (list of US IDs)
- Estado (enum: Por Iniciar|En Progreso|Completado)
- Feature Padre (ref: Feature ID)

**Project Backlog** (the document):
- Frontmatter (metadata)
- Sections (Markdown structure per template)
- Relationships: Epics contain Features, Features contain User Stories

**Note**: This is a *conceptual* data model. The actual implementation is a Markdown document following the template structure. The "model" helps reason about the content, but there's no database or schema validation.

## Contracts

**N/A** - This feature is not an API or service. It's a command file that orchestrates document generation. The "contract" is:

**Input Contract**:
- File: `specs/main/tech_design.md` (must exist, must have sections: components, architecture, MVP scope)
- File: `specs/main/project_requirements.md` (reference, must exist)
- File: `specs/main/solution_vision.md` (reference, must exist)
- Template: `.specify/templates/raise/backlog/project_backlog.md` (must exist)

**Output Contract**:
- File: `specs/main/project_backlog.md` (created/overwritten)
- Format: Markdown with YAML frontmatter, follows template structure
- Must pass: `.specify/gates/raise/gate-backlog.md` validation

**Side Effects**:
- Updates agent context via `update-agent-context.sh`
- Offers handoff to `raise.6.estimation`

## Agent Context Update Strategy

After backlog generation, the agent context should be updated with:

**Technologies/Tools Added**: None (this command doesn't introduce new tech stack)

**Context to Add**:
- Current project has backlog at `specs/main/project_backlog.md`
- Total Story Points: [calculated value]
- MVP Story Points: [calculated value]
- Number of Epics/Features/US: [calculated values]
- Next command in flow: `raise.6.estimation`

The `update-agent-context.sh` script will add this to the appropriate agent-specific context file (e.g., `.claudecontext` for Claude Code).

---

# Phase 2: Implementation Tasks

**Note**: Implementation tasks (tasks.md) will be generated by the `/speckit.tasks` command, which is executed after this plan is approved. This plan provides the design foundation for task generation.

**Expected Task Breakdown** (preview):

1. **Setup Task**: Copy template and gate from `src/` to `.raise-kit/`
2. **Create Command File**: Create `.raise-kit/commands/02-projects/raise.5.backlog.md`
3. **Write Frontmatter**: Add description and handoff to raise.6.estimation
4. **Write Steps 1-12**: Following the outline designed in Phase 1
5. **Write High-Signaling Guidelines**: Output, Focus, Language, Jidoka summary
6. **Write AI Guidance**: Role, proactive behavior, kata following
7. **Validation**: Compare structure with reference commands (raise.1.discovery, raise.4.tech-design)
8. **Test**: Execute command manually with sample Tech Design, verify gate passes

---

# Constitution Re-Check (Post-Design)

Re-evaluating after Phase 1 design completion:

### §1. Humanos Definen, Máquinas Ejecutan
**Status**: ✓ PASS (unchanged)

The 12-step outline clearly defines WHAT must be done. The AI executes, the human guides decisions (prioritization, estimation).

### §2. Governance as Code
**Status**: ✓ PASS (unchanged)

Command, template, gate, kata - all in Git.

### §3. Platform Agnosticism
**Status**: ✓ PASS (unchanged)

Pure Markdown, no platform lock-in.

### §4. Validation Gates en Cada Fase
**Status**: ✓ PASS (unchanged)

Step 12 executes gate-backlog.md with 7 mandatory criteria.

### §5. Heutagogía sobre Dependencia
**Status**: ✓ PASS (enhanced)

The design explicitly includes decision-making guidance in Steps 6 (prioritization) and 10 (estimation), teaching the process rather than automating it blindly.

### §6. Mejora Continua (Kaizen)
**Status**: ✓ PASS (unchanged)

Command structure allows refinement based on execution feedback.

### §7. Lean Software Development
**Status**: ✓ PASS (enhanced)

**Jidoka**: 10 explicit Jidoka blocks across all steps ensure "stop on defects"
**Eliminate waste**: Reuses all existing artifacts, no duplication
**Empower team**: User makes final calls on priorities and estimates

### §8. Observable Workflow
**Status**: ✓ PASS (enhanced)

12 observable verification blocks + gate execution provides full traceability of backlog generation process.

**Final Constitution Status**: ALL PASS ✓

---

# Appendix: Decision Log

| ID  | Decision | Rationale | Alternatives Considered |
|-----|----------|-----------|------------------------|
| D1  | 12 steps (10 kata + init + finalize) | Standard RaiSE Kit pattern requires initialization and finalization wrapping kata steps | Alternative: Inline init/finalize into kata steps - rejected because breaks command structure consistency |
| D2  | Handoff target: raise.6.estimation | Linear flow: backlog → estimation roadmap | Alternative: Handoff to implementation directly - rejected because estimation step is needed for SoW |
| D3  | Propose default priorities/estimates | Maintains flow, teaches user to validate with team | Alternative: Force user interaction for each item - rejected because too time-consuming (violates SC-001: <60 min) |
| D4  | Use portable `.specify/` references | Required for command portability after injection to target projects | Alternative: Use `.raise-kit/` references - rejected because won't work after injection |
| D5  | Spanish content, English instructions | RaiSE convention for all comandos | N/A - no alternatives, this is a standard |

---

# Open Questions for Implementation Phase

None. All questions from spec (Q1-Q3) have been resolved in research phase with concrete decisions (see D3 above and research sections).

---

**Plan Status**: COMPLETE - Ready for `/speckit.tasks` command to generate implementation task list.
