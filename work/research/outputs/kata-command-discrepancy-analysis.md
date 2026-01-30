# Kata vs Command Discrepancy Analysis

**Date:** 2026-01-29
**Status:** Complete
**Researcher:** RaiSE Ontology Research Agent
**Version:** 1.0
**Related:** `command-kata-skill-ontology-report.md`, ADR-011

---

## Executive Summary

This analysis identifies structural discrepancies between the current v2 "command" architecture in `.raise/commands/` and the kata ontology defined in `docs/katas/`. The findings support the vision where:

1. **Katas** = Cultural artifacts / declarative process knowledge (adaptable by Dojos/teams)
2. **Kata Executor Harness** = Generalized runtime that interprets and executes katas (to be built on spec-kit)
3. **Skills** = Atomic operations invoked by the harness

The current "commands" conflate these concerns, embedding both process knowledge AND execution harness logic in the same files.

---

## 1. Inventory of Existing Katas

### 1.1 Current Kata Structure (docs/katas/)

| Level | File | Purpose | Template | Gate |
|-------|------|---------|----------|------|
| **principles** | `meta-kata.md` | What is a kata, ShuHaRi, Jidoka | null | null |
| **principles** | `execution-protocol.md` | 7-step protocol for any kata | null | null |
| **flow** | `discovery.md` | Phase 1: PRD creation | `project_requirements.md` | `gate-discovery` |
| **flow** | `solution-vision.md` | Phase 2: Solution Vision | `solution-vision-template.md` | `gate-vision` |
| **flow** | `tech-design.md` | Phase 3: Tech Design | `tech_design.md` | `gate-design` |
| **flow** | `backlog-creation.md` | Phase 4: Backlog | `user_story.md` | `gate-backlog` |
| **flow** | `implementation-plan.md` | Phase 5: Planning | - | `gate-plan` |
| **flow** | `development.md` | Phase 6: Code | - | `gate-code` |
| **patterns** | `code-analysis.md` | Brownfield analysis | null | null |
| **patterns** | `ecosystem-discovery.md` | Integration mapping | null | null |
| **patterns** | `tech-design-stack.md` | Stack-aware design | `tech_design.md` | `gate-design` |
| **patterns** | `dependency-validation.md` | Library adoption | null | null |

**Total: 12 katas** (2 principles, 6 flow, 4 patterns)

### 1.2 Legacy Katas (archived in .private/archive/legacy-katas/)

The archive contains 30+ legacy katas using the old L0-L3 nomenclature:

| Legacy Level | Count | Examples |
|--------------|-------|----------|
| L0 (principios) | 2 | `L0-00-raise-katas-documentation.md`, `L0-01-raise-kata-execution-protocol.md` |
| L1 (flujo) | 12+ | `L1-04-generacion-plan-implementacion-hu.md`, `L1-10-alineamiento-convenciones-repositorio-kata.md` |
| L2 (patron) | 8+ | `L2-02-Analisis-Agnostico-Codigo-Fuente.md`, `L2-07-Validacion-Tecnica-Dependencias.md` |
| cursor_rules | 10+ | `L2-01-analisis-exploratorio-repositorio.md` - specialized for rule generation |

**Key Observation:** Legacy katas were often project-specific (e.g., `zc-kata-tech-design.md` for "Zambezi Concierge") rather than generic.

### 1.3 Kata Structural Schema (from kata-schema.md)

```yaml
# Canonical Kata Frontmatter (v2.1)
---
id: flujo-01-discovery              # Pattern: {nivel}-{numero}-{nombre}
nivel: flujo                        # enum: principios, flujo, patron, tecnica
titulo: "Discovery: Creacion del PRD"
audience: beginner                  # enum: beginner, intermediate, advanced
template_asociado: templates/solution/project_requirements.md
validation_gate: gates/gate-discovery.md
prerequisites:
  - principios-01-execution-protocol
fase_metodologia: 1
tags: [discovery, prd, requisitos]
version: 1.0.0
---
```

**Mandatory Sections:**
1. `## Proposito`
2. `## Contexto` / `## Cuando Aplicar`
3. `## Pasos` (with Jidoka inline: Verificacion + Si no puedes continuar)
4. `## Output`
5. `## Validation Gate` (reference)
6. `## Referencias`

---

## 2. Inventory of Current Commands

### 2.1 Command Directory Structure

```
.raise/commands/
├── project/
│   ├── create-prd.md              # Flow: Phase 1
│   ├── define-vision.md           # Flow: Phase 2
│   ├── map-ecosystem.md           # Pattern
│   ├── design-architecture.md     # Flow: Phase 3
│   ├── create-backlog.md          # Flow: Phase 4
│   └── estimate-effort.md         # Utility
├── feature/
│   ├── generate-stories.md        # Flow: Backlog
│   ├── design-feature.md          # Flow: Design
│   ├── plan-implementation.md     # Flow: Phase 5
│   └── implement.md               # Flow: Phase 6
├── setup/
│   ├── analyze-codebase.md        # Pattern: Code analysis
│   ├── generate-rules.md          # Utility: Rule generation
│   └── edit-rule.md               # Skill: Atomic operation
├── context/
│   ├── get.md                     # Skill: MVC retrieval
│   ├── check.md                   # Skill: Compliance check
│   └── explain.md                 # Skill: Rule explanation
├── validate/
│   ├── prd.md                     # Gate executor
│   ├── vision.md                  # Gate executor
│   ├── architecture.md            # Gate executor
│   ├── design.md                  # Gate executor
│   ├── backlog.md                 # Gate executor
│   └── estimation.md              # Gate executor
└── tools/
    └── generate-contract.md       # Utility
```

**Total: 23 commands** across 6 categories

### 2.2 Command Structural Schema (from analyzed files)

```yaml
# Command Frontmatter (current)
---
description: Transform raw discovery notes into a structured PRD
handoffs:
  - label: Define Solution Vision
    agent: project/define-vision
    prompt: Create the solution vision for this PRD
    send: true
---
```

**Typical Command Sections:**
1. `## User Input` - `$ARGUMENTS` placeholder
2. `## Outline` - Goal + numbered steps
3. `## Notas` (optional context notes)
4. `## High-Signaling Guidelines` - Output, Focus, Language, Jidoka
5. `## AI Guidance` - Role, behavior instructions

---

## 3. Comparison Matrix: Kata Sections vs Command Sections

| Aspect | Kata | Command | Discrepancy |
|--------|------|---------|-------------|
| **Identity** | `id`, `nivel`, `titulo` | `description` only | Commands lack semantic classification |
| **Level/Type** | `nivel: flujo/patron/tecnica` | Directory-based (`project/`, `context/`) | Categories don't map to kata levels |
| **Audience** | `audience: beginner/intermediate/advanced` | None | Commands lack progressive disclosure |
| **Prerequisites** | `prerequisites: [kata-ids]` | Implicit in handoffs | Commands lack explicit dependency graph |
| **Template Link** | `template_asociado` | Inline in steps | Commands embed template path in instructions |
| **Gate Link** | `validation_gate` | Inline in steps | Commands embed gate path in instructions |
| **Purpose** | `## Proposito` (1-2 paragraphs) | Part of `description` (1 line) | Commands lack rich purpose explanation |
| **Context** | `## Contexto` / `## Cuando Aplicar` | Implicit in Outline | Commands lack explicit applicability criteria |
| **Steps** | `## Pasos` with H3 per step | `## Outline` with numbered list | Similar but different formatting |
| **Jidoka Pattern** | `**Verificacion:** ... > **Si no puedes continuar:**` | Same pattern adopted | Aligned |
| **Output** | `## Output` (artifact + location + next step) | Part of Outline | Commands embed in steps |
| **References** | `## Referencias` (links) | Minimal | Commands lack reference section |
| **Handoffs** | Implicit (next kata mentioned) | `handoffs:` YAML in frontmatter | Commands have explicit handoffs |
| **User Input** | None | `## User Input` with `$ARGUMENTS` | Commands have user input handling |
| **AI Guidance** | None | `## AI Guidance` with role/behavior | Commands have execution instructions |
| **High-Signaling** | None | `## High-Signaling Guidelines` | Commands have operational directives |

---

## 4. List of Discrepancies with Severity

### 4.1 Critical Discrepancies (Architectural)

| ID | Discrepancy | Severity | Impact |
|----|-------------|----------|--------|
| **D1** | **Commands conflate process and execution** | CRITICAL | Commands embed both "what to do" (kata) AND "how the agent should behave" (harness) |
| **D2** | **Command categories don't align with kata levels** | CRITICAL | `project/`, `context/`, `setup/` are operational groupings, not ontological levels |
| **D3** | **Commands lack semantic classification** | HIGH | No `nivel` field means commands can't be filtered by principios/flujo/patron/tecnica |
| **D4** | **No shared schema between kata and command** | HIGH | Commands have different frontmatter than katas - no common ancestor |

### 4.2 High-Severity Discrepancies (Process Knowledge)

| ID | Discrepancy | Severity | Impact |
|----|-------------|----------|--------|
| **D5** | **Commands lack explicit prerequisites** | HIGH | Dependency graph is implicit via handoffs, not declarative |
| **D6** | **Commands lack audience differentiation** | HIGH | Beginner vs advanced users see same content |
| **D7** | **Commands embed template/gate paths** | HIGH | Process knowledge is coupled to execution paths |
| **D8** | **Commands lack rich context/applicability** | MEDIUM | Users don't know when NOT to use a command |

### 4.3 Medium-Severity Discrepancies (Consistency)

| ID | Discrepancy | Severity | Impact |
|----|-------------|----------|--------|
| **D9** | **Output section differs** | MEDIUM | Katas have dedicated `## Output`, commands embed in Outline |
| **D10** | **References section missing** | MEDIUM | Commands lack `## Referencias` for traceability |
| **D11** | **Purpose vs Description depth** | MEDIUM | Commands have 1-line description vs kata's 1-2 paragraphs |

### 4.4 Low-Severity Discrepancies (Style)

| ID | Discrepancy | Severity | Impact |
|----|-------------|----------|--------|
| **D12** | **Heading conventions differ** | LOW | Katas use `## Pasos`, commands use `## Outline` |
| **D13** | **Step numbering style** | LOW | Katas use `### Paso N:`, commands use numbered list |

---

## 5. Analysis: What Should Be Extracted to "Kata Executor Harness"

The current commands contain three distinct concerns:

### 5.1 Pure Process Knowledge (Should remain in Kata)

These elements describe **WHAT** to do and **WHY**:

```markdown
# From kata: flujo-01-discovery.md
## Proposito
Transformar las notas de reuniones de discovery... en un PRD estructurado

## Contexto
**Cuando usar:**
- Al iniciar un nuevo proyecto
- Al comenzar una nueva epica...

## Pasos
### Paso 1: Cargar Contexto Inicial
Recopilar todas las notas de reuniones...

**Verificacion:** Existe un documento con todo el contexto consolidado.
> **Si no puedes continuar:** Contexto disperso → Solicitar consolidacion...
```

**Cultural/Declarative elements:**
- Purpose and context
- Step sequence with descriptions
- Verification criteria
- Recovery guidance (Jidoka)
- Pre-conditions and post-conditions
- References to templates and gates

### 5.2 Execution Harness Logic (Should be extracted to Harness)

These elements describe **HOW** the agent should execute:

```markdown
# From command: project/create-prd.md
## User Input
```text
$ARGUMENTS
```
You **MUST** consider the user input before proceeding...

## Outline
1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load and copy the template from `.specify/templates/...`

## High-Signaling Guidelines
- **Output**: A single Markdown document (`specs/main/project_requirements.md`)...
- **Language**: Instructions English; Content **SPANISH**
- **Jidoka**: Stop and ask if critical goals/metrics are missing...

## AI Guidance
When executing this workflow:
1. **Role**: You are a Technical Writer...
2. **Be proactive**: Propose standard industry metrics...
```

**Harness/Execution elements:**
- User input handling (`$ARGUMENTS`)
- Environment initialization scripts
- File path resolution (`.specify/...`)
- Language directives
- Role assignment for AI agent
- Behavioral guidelines

### 5.3 Skill Invocations (Should be extracted to Skills)

Atomic operations that could be invoked by the harness:

| Current Location | Skill Candidate | Type |
|------------------|-----------------|------|
| `context/get.md` | `retrieve-mvc` | Pure Skill |
| `context/check.md` | `check-compliance` | Pure Skill |
| `validate/prd.md` | `run-gate` (parameterized) | Skill |
| `setup/edit-rule.md` | `edit-rule` | Pure Skill |
| Script calls | `check-prerequisites`, `update-agent-context` | Skill (external) |

---

## 6. Proposed Separation of Concerns

### 6.1 Three-Layer Architecture

```
+------------------------------------------------------------------+
|                         KATA (Cultural Layer)                      |
|  ----------------------------------------------------------------  |
|  - Process knowledge in declarative form                          |
|  - Adaptable by Dojos/teams                                       |
|  - Contains: Purpose, Context, Steps, Verification, References    |
|  - Location: docs/katas/{nivel}/                                  |
+------------------------------------------------------------------+
                              |
                              | Interpreted by
                              v
+------------------------------------------------------------------+
|                   KATA EXECUTOR HARNESS (Runtime)                  |
|  ----------------------------------------------------------------  |
|  - Generalized interpreter for any kata                           |
|  - Handles: User input, environment setup, progress tracking      |
|  - Contains: AI guidance, high-signaling, handoff orchestration   |
|  - Built on: spec-kit infrastructure                              |
+------------------------------------------------------------------+
                              |
                              | Invokes
                              v
+------------------------------------------------------------------+
|                        SKILLS (Atomic Operations)                  |
|  ----------------------------------------------------------------  |
|  - Single-purpose utility functions                               |
|  - Examples: retrieve-mvc, run-gate, check-prerequisites          |
|  - Location: .raise/skills/ or as MCP tools                       |
+------------------------------------------------------------------+
```

### 6.2 Kata Schema (Pure Process Knowledge)

```yaml
---
# IDENTIFICATION
id: flujo-01-discovery
nivel: flujo                      # principios | flujo | patron | tecnica
titulo: "Discovery: Creacion del PRD"

# TAXONOMY
audience: beginner
tags: [discovery, prd, requisitos]
fase_metodologia: 1

# RELATIONSHIPS
prerequisites: []
template_asociado: templates/solution/project_requirements.md
validation_gate: gates/gate-discovery.md

# ADAPTABILITY
adaptable_by: [dojo, project]     # NEW: Who can customize
shuhari_notes:                     # NEW: Adaptation guidance
  shu: "Follow all steps exactly"
  ha: "Combine steps 4-5 if metrics are well-known"
  ri: "Create domain-specific PRD kata"

version: 1.0.0
---

# Discovery: Creacion del PRD

## Proposito
[1-2 paragraphs explaining WHY this kata exists]

## Contexto
**Cuando usar:** [Applicability criteria]
**Inputs requeridos:** [List]
**Output:** [Description]

## Pre-condiciones
- [ ] [Checklist of prerequisites]

## Pasos

### Paso 1: [Action in infinitive]
[Description of what to do]

**Verificacion:** [Observable success criterion]
> **Si no puedes continuar:** [Cause] -> [Resolution]

[... more steps ...]

## Output
- **Artefacto:** [Name]
- **Ubicacion:** [Path pattern, not hardcoded]
- **Siguiente kata:** [Reference]

## Notas
[Context-specific guidance: brownfield, greenfield, spike]

## Referencias
- [Links to related documents]
```

### 6.3 Harness Configuration (Execution Layer)

```yaml
# .raise/harness/config.yaml
harness:
  version: "1.0"

  # Environment setup
  initialization:
    - skill: check-prerequisites
      args: ["--json", "--paths-only"]
    - skill: load-golden-data

  # User input handling
  input:
    source: $ARGUMENTS
    required: false
    prompt_if_empty: "Describe the project context or paste discovery notes:"

  # AI behavior configuration
  ai_guidance:
    role: "Technical Writer populating a template"
    language:
      instructions: "English"
      content: "Spanish"
    proactive_behavior:
      - "Propose standard industry metrics if notes are vague"
      - "Suggest clarifications after 3 failed attempts"

  # Progress tracking
  progress:
    tracker: "specs/{feature}/progress.md"
    on_step_complete: "update-progress"
    on_error: "log-and-pause"

  # Handoff orchestration
  handoffs:
    on_complete:
      - label: "Define Solution Vision"
        kata: "flujo-02-solution-vision"
        auto_suggest: true

  # Jidoka behavior
  jidoka:
    max_retry: 3
    on_verification_fail: "pause-and-escalate"
    on_blocker: "document-and-notify"
```

### 6.4 Skill Definition (Atomic Operations)

```yaml
# .raise/skills/retrieve-mvc.yaml
---
id: retrieve-mvc
name: "Retrieve Minimum Viable Context"
type: skill
description: "Retrieves rules and conventions relevant to a specific task scope"

# Contract
input:
  task: { type: string, required: true }
  scope: { type: string, default: "." }
  min_confidence: { type: number, default: 0.80 }

output:
  type: object
  schema:
    primary_rules: [{ id, name, content }]
    context_rules: [{ id, name, summary }]
    warnings: [{ type, message, affected_rules }]

# Implementation reference
implementation:
  type: "mcp-tool"  # or "bash-script", "inline"
  ref: "context/get"
---
```

---

## 7. Observations and Recommendations

### 7.1 Key Findings

1. **Commands are "compiled" katas** - They take the declarative kata structure and add execution-specific logic, losing the clean separation of concerns.

2. **Command categories are operational, not ontological** - `project/`, `setup/`, `context/` are action-oriented groupings that don't map to the kata level hierarchy (principios/flujo/patron/tecnica).

3. **The Jidoka pattern is preserved** - Both katas and commands use the same `Verificacion` + `Si no puedes continuar` pattern, showing this is a cultural element that should remain in katas.

4. **Handoffs are a harness concern** - The `handoffs:` YAML in command frontmatter is orchestration logic, not process knowledge.

5. **Skills already exist implicitly** - Commands like `context/get` and `validate/*` are essentially skills wrapped in command structure.

### 7.2 Recommendations

1. **Refactor commands into three artifacts:**
   - **Kata** (in `docs/katas/`) - Pure process knowledge
   - **Harness config** (in `.raise/harness/`) - Execution configuration
   - **Skills** (in `.raise/skills/`) - Atomic operations

2. **Align kata levels with methodology phases:**
   - `principios/` = Meta-process (when/why)
   - `flujo/` = Methodology phases 1-7
   - `patron/` = Reusable structures (brownfield, greenfield)
   - `tecnica/` = Specific techniques (future)

3. **Create a "Kata Executor" harness** that:
   - Reads kata files and interprets steps
   - Handles user input and environment setup
   - Invokes skills for atomic operations
   - Tracks progress and manages handoffs
   - Applies AI guidance consistently

4. **Extract pure skills from commands:**
   - `context/get.md` -> `skills/retrieve-mvc.yaml`
   - `context/check.md` -> `skills/check-compliance.yaml`
   - `validate/*.md` -> `skills/run-gate.yaml` (parameterized)

5. **Add missing kata metadata to current katas:**
   - `audience` field for progressive disclosure
   - `adaptable_by` field for governance
   - `shuhari_notes` for adaptation guidance

### 7.3 Migration Path

| Phase | Action | Deliverable |
|-------|--------|-------------|
| 1 | Define Harness schema | `.raise/harness/schema.yaml` |
| 2 | Define Skill schema | `.raise/skills/schema.yaml` |
| 3 | Extract skills from commands | `skills/retrieve-mvc.yaml`, etc. |
| 4 | Create harness configs | `harness/config-flow.yaml`, etc. |
| 5 | Validate kata coverage | Ensure all methodology phases have katas |
| 6 | Build Kata Executor | spec-kit based interpreter |
| 7 | Deprecate commands | Archive `.raise/commands/` |

---

## 8. Appendix: Detailed Command Analysis

### 8.1 project/create-prd.md

**Kata equivalent:** `flujo-01-discovery.md`
**Entanglement analysis:**

| Element | Classification | Notes |
|---------|---------------|-------|
| `description:` | Process | 1-line summary |
| `handoffs:` | Harness | Orchestration logic |
| `## User Input` | Harness | Input handling |
| `Initialize Environment` | Harness | Scripts, path resolution |
| `Paso 1-8` | Kata | Process steps with Jidoka |
| `Paso 9: Validar` | Hybrid | Process step + Harness scripts |
| `## Notas` | Kata | Context notes |
| `## High-Signaling Guidelines` | Harness | Operational directives |
| `## AI Guidance` | Harness | Behavioral instructions |

### 8.2 context/get.md

**Classification:** Pure Skill (should not be a "kata-like" command)
**Evidence:**
- Single-purpose: Retrieve MVC
- Atomic: No multi-step process
- Utility: Used by other commands/katas

**Recommended skill definition:**
```yaml
id: retrieve-mvc
inputs: [task, scope, min_confidence]
outputs: [primary_rules, context_rules, warnings]
```

### 8.3 feature/implement.md

**Kata equivalent:** `flujo-06-development.md`
**Unique elements:**
- Task-by-task execution loop
- Progress tracking in `progress.md`
- Resume capability (`--start-from`)

**Harness elements to extract:**
- Loop execution logic
- Progress persistence
- Resume capability
- Task dependency validation

---

## 9. Conclusion

The current command architecture successfully captures process knowledge but conflates it with execution harness logic. The proposed separation into Kata (cultural) / Harness (runtime) / Skill (atomic) layers would:

1. **Preserve cultural adaptability** - Dojos can customize katas without touching execution logic
2. **Enable reusable execution infrastructure** - One harness interprets all katas
3. **Allow atomic skill composition** - Skills can be invoked by multiple katas/harness configs
4. **Maintain RaiSE philosophy** - Jidoka, ShuHaRi, and Lean principles remain in the cultural layer

The existing research on Kata/Skill/Gate terminology (see `command-kata-skill-ontology-report.md`) supports this architectural direction, and ADR-011 (Hybrid Model) already established the Template/Kata/Gate separation. This analysis extends that model to include the execution harness layer.

---

*Analysis completed: 2026-01-29*
*RaiSE Ontology Research Agent*
