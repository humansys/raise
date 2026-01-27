# Implementation Plan: Comando raise.6.estimation

**Branch**: `010-estimation-command` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-estimation-command/spec.md`

## Summary

Create the `raise.6.estimation` command that transforms a Project Backlog (with Story Point estimates) into an Estimation Roadmap with sprint projections, team capacity parameters, and cost model linkage. This command implements Step 6 of Kata L1-04 (estimation process) and follows the standard command structure defined in rule 110-raise-kit-command-creation.md.

**Primary Requirement**: Generate `specs/main/estimation_roadmap.md` from `specs/main/project_backlog.md` by:
1. Extracting SP estimates from backlog items (Epics/Features/User Stories)
2. Configuring team parameters (roles, capacity, sprint duration)
3. Projecting roadmap by calculating iterations needed (Total SP / Team Capacity)
4. Identifying MVP scope and documenting cost model linkage

**Technical Approach**: This is a **documentation transformation command** (like `raise.5.backlog` and `raise.4.tech-design`). It loads a backlog markdown file, extracts structured data (tables with SP estimates), performs calculations (capacity, iterations), and populates the `estimation_roadmap.md` template with computed values. No code generation or compilation - pure document processing following the RaiSE command pattern.

## Technical Context

**Language/Version**: Markdown (CommonMark spec) for command file + template, Bash for prerequisite scripts
**Primary Dependencies**:
- Template: `src/templates/solution/estimation_roadmap.md` (already exists)
- Gate: `.raise-kit/gates/raise/gate-estimation.md` (needs creation)
- Prerequisite scripts: `check-prerequisites.sh`, `update-agent-context.sh` (already exist)
- Reference commands: `raise.5.backlog.md` (for structure pattern)

**Storage**: Git repository (versioned Markdown files in `specs/main/`)
**Testing**: Manual validation via gate execution + comparison with existing commands
**Target Platform**: RaiSE Framework (Git-based, platform-agnostic)
**Project Type**: Single command file (.md) following raise-kit architecture
**Performance Goals**: Command execution in <10 minutes for typical backlog (50-100 User Stories)
**Constraints**:
- Must use `.specify/` paths (NOT `.raise-kit/`) for portability (critical!)
- Output must be in SPANISH, instructions in ENGLISH
- Must follow exact structure of rule 110 (6 mandatory sections)
- Must execute gate and apply Jidoka (stop on defects)

**Scale/Scope**: Single command file (~200-300 lines) + gate file (~50 lines), no code libraries needed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### §1. Humanos Definen, Máquinas Ejecutan
✅ **PASS**: The spec (spec.md) defines WHAT in natural language (functional requirements, user stories). The command file will define HOW for the AI agent (procedural outline). Clear separation maintained.

### §2. Governance as Code
✅ **PASS**:
- Command file will be versioned in Git (`.raise-kit/commands/02-projects/raise.6.estimation.md`)
- Gate file versioned in Git (`.raise-kit/gates/raise/gate-estimation.md`)
- Constitution check documented here
- All governance artifacts in the repository

### §3. Platform Agnosticism
✅ **PASS**: Command uses only Git, Markdown files, and Bash scripts. No GitHub/GitLab-specific features. Template uses CommonMark spec. Works anywhere Git works.

### §4. Validation Gates en Cada Fase
✅ **PASS**:
- Command explicitly executes `gate-estimation.md` at finalization (FR-010, step 11 in outline)
- Gate validates roadmap quality before allowing continuation
- Jidoka principle enforced: command stops on gate failures (FR-012)

### §5. Heutagogía sobre Dependencia
✅ **PASS**: Command includes "AI Guidance" section explaining the "why" behind each step (as seen in raise.5.backlog example). The agent facilitates learning about estimation, not just executes mechanically.

### §6. Mejora Continua (Kaizen)
✅ **PASS**: Command structure enables iteration - if estimation process fails or requires many corrections, the command outline and gate can be refined. Observable via Git history.

### §7. Lean Software Development
✅ **PASS**:
- **Eliminar desperdicio**: Reuses existing template, follows established pattern (no reinvention)
- **Jidoka**: Explicit stop conditions in every step's Jidoka block
- **Decidir tarde**: Command allows defaults but supports parametrization
- **Ver el todo**: References all prior artifacts (PRD, Vision, Tech Design, Backlog)

### §8. Observable Workflow
✅ **PASS**:
- Every step has explicit "Verificación" criteria (observable checkpoints)
- Gate execution provides pass/fail audit trail
- update-agent-context.sh logs command execution for traceability
- Roadmap output documents all assumptions and parameters used

**Constitution Check Result**: ✅ **ALL GATES PASS** - No violations to justify. Feature aligns perfectly with RaiSE principles.

## Project Structure

### Documentation (this feature)

```text
specs/010-estimation-command/
├── spec.md                    # Feature specification (completed)
├── plan.md                    # This file (in progress)
├── research.md                # Phase 0: Decision rationale for command structure
├── data-model.md              # Phase 1: Command outline structure, step definitions
├── quickstart.md              # Phase 1: How to use raise.6.estimation command
├── contracts/                 # Phase 1: Gate validation contract
│   └── gate-estimation.md     # Template for gate criteria
├── checklists/
│   └── requirements.md        # Spec quality checklist (completed)
└── tasks.md                   # Phase 2: Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.raise-kit/
├── commands/
│   └── 02-projects/
│       └── raise.6.estimation.md          # NEW: Command file to create
├── templates/
│   └── raise/
│       └── solution/
│           └── estimation_roadmap.md      # EXISTS: Template (already in src/)
└── gates/
    └── raise/
        └── gate-estimation.md             # NEW: Gate to create

src/
└── templates/
    └── solution/
        └── estimation_roadmap.md          # EXISTS: Source template
```

**Structure Decision**: Single command architecture (Option 1 equivalent). This is a pure documentation command - no multi-tier or mobile structure needed. The command file orchestrates document transformation using existing RaiSE infrastructure (templates, gates, scripts).

**Key Files**:
1. **raise.6.estimation.md**: Command file following rule 110 structure (frontmatter, User Input, Outline with 11 steps, High-Signaling Guidelines, AI Guidance)
2. **gate-estimation.md**: Validation gate checking roadmap completeness, MVP identification, iteration calculations, cost model section

## Complexity Tracking

> **No violations - this section intentionally left empty**

The Constitution Check passed all 8 principles with no exceptions needed. This feature exemplifies RaiSE design: simple, composable, transparent, observable, and Lean-aligned.

## Phase 0: Research & Decisions

### Research Questions

1. **Command Outline Structure**: What are the 11 steps needed to transform backlog → estimation roadmap?
   - **Decision**: Follow the kata L1-04 Step 6 process + rule 110 pattern
   - **Steps identified**:
     1. Initialize Environment (load template, run prerequisites)
     2. Load Backlog and extract SP estimates
     3. Instantiate Template (metadata, frontmatter)
     4. Configure Team Parameters (use defaults or user input)
     5. Generate Estimation Table (consolidate all backlog items)
     6. Calculate Roadmap Projection (iterations = Total SP / Capacity)
     7. Identify MVP Scope (mark MVP iterations)
     8. Document Cost Model Linkage (SP → hours → cost)
     9. Add Disclaimers and Assumptions
     10. Generate Summary Metrics
     11. Finalize & Validate (execute gate, show handoff)

2. **Gate Validation Criteria**: What must the roadmap contain to pass validation?
   - **Decision**: Based on template structure and FR-010 requirements
   - **Mandatory criteria**:
     1. Guía de Estimación complete (Fibonacci scale, factors, process)
     2. Estimation table with ALL backlog items + SP
     3. Team parameters documented (capacity, sprint duration, roles)
     4. Roadmap projection table (iterations with dates/objectives/SP)
     5. MVP clearly identified
     6. Cost model section present and explained
     7. Disclaimers and assumptions documented

3. **Default Team Parameters**: What are reasonable defaults for team capacity?
   - **Decision**: Based on SAFe and template example (estimation_roadmap.md)
   - **Defaults**:
     - Structure: 1 AI Architect (50%), 1 AI Engineer (100%), 1 AI QA (50%)
     - Capacity calculation: (0.5 * 8) + (1 * 8) + (0.5 * 8) = 16 SP/sprint
     - Sprint duration: 2 weeks
     - Rationale: Aligns with Scrum/SAFe norms for small cross-functional team

4. **Handling Missing SP Estimates**: What if backlog has User Stories without estimates?
   - **Decision**: Propose preliminary estimates + warn user (from FR-005, edge case handling)
   - **Strategy**:
     - Analyze complexity hints (description length, acceptance criteria count)
     - Propose: Small (1-2 SP), Medium (3-5 SP), Large (8 SP)
     - Document as "[Pendiente - Estimado preliminar: X SP]" in table
     - Add note that estimates must be refined in planning poker

5. **Portable Path References**: How to ensure command works in target projects?
   - **Decision**: ALL paths use `.specify/` prefix (critical rule from 110)
   - **Examples**:
     - Template: `.specify/templates/raise/solution/estimation_roadmap.md`
     - Gate: `.specify/gates/raise/gate-estimation.md`
     - Scripts: `.specify/scripts/bash/check-prerequisites.sh`
   - **Rationale**: Commands run AFTER injection via transform-commands.sh, where .raise-kit/ doesn't exist but .specify/ does

### Technology Choices

| Technology | Choice | Rationale |
|------------|--------|-----------|
| Command Format | Markdown (CommonMark) | Standard for all RaiSE commands, human-readable, Git-friendly |
| Template Loading | Direct file read | Simple, no parsing library needed - AI agent reads markdown directly |
| Calculation Logic | Inline in outline steps | No code execution - AI performs math (Total SP / Capacity) directly |
| Gate Execution | Markdown checklist | Standard RaiSE gate pattern - AI validates against criteria list |
| Parameterization | User input ($ARGUMENTS) | Allows custom team config via command args (optional, uses defaults if empty) |

### Alternatives Considered & Rejected

| Alternative | Why Rejected |
|-------------|--------------|
| Python script for calculations | Adds complexity - AI can perform simple math inline, no need for code |
| JSON template instead of Markdown | Breaks RaiSE convention - all templates are Markdown for readability |
| Separate config file for team params | Premature - defaults cover 80% of cases, args handle custom 20% |
| Interactive prompts for parameters | Violates automation principle - command should run unattended if defaults acceptable |
| Template modification | Violates constraint - must use template as-is (Restricción 5) |

## Phase 1: Design & Contracts

### Data Model: Command Outline Structure

**Entity: CommandOutline**

```yaml
structure:
  frontmatter:
    description: string (1 line summary)
    handoffs:
      - label: string (visible to user)
        agent: string (next command name)
        prompt: string (handoff message)
        send: boolean (auto-offer)

  user_input:
    content: $ARGUMENTS (command-line args)
    consideration: required (must check if not empty)

  outline:
    goal: string (clear objective statement)
    steps: array[11] (numbered steps)
      - title: string (Paso N: Infinitive verb + object)
      - actions: array[string] (specific executable actions)
      - verification: string (observable completion criteria)
      - jidoka_block: string (condition → corrective action)

  high_signaling_guidelines:
    output: string (what files generated)
    focus: string (command focus area)
    language: "Instructions English; Content SPANISH"
    jidoka: string (when to stop and ask)

  ai_guidance:
    role: string (agent's role during execution)
    be_proactive: string (what to propose by default)
    follow_katas: string (which kata to follow)
    traceability: string (how to link decisions)
    gates: string (what to validate)
    heutagogy: string (learning facilitation approach)
```

**Entity: GateValidation**

```yaml
structure:
  purpose: string (what this gate validates)
  mandatory_criteria: array[7] (must pass)
    - criterion: string (specific checkable condition)
    - check_method: string (how to verify)

  optional_criteria: array (nice-to-have)

  failure_handling:
    action: "JIDOKA - stop execution"
    feedback: "List specific failures + suggest fixes"

  success_output:
    action: "Show pass confirmation + summary"
    next_step: "Offer handoff to raise.7.sow"
```

**Entity: TeamParameters**

```yaml
structure:
  roles: array
    - name: string (e.g., "AI Architect")
      dedication: float (0.0-1.0, e.g., 0.5 for 50%)
      sp_per_sprint: float (dedication * 8 points baseline)

  capacity:
    total_sp_per_sprint: float (sum of all roles)

  sprint:
    duration: string (e.g., "2 semanas")
    duration_weeks: int (for date calculations)

  defaults:
    used: boolean (true if user provided no args)
    documented: boolean (must note in roadmap)
```

### Contracts: Step-by-Step Outline

**Contract 1: Step 1 - Initialize Environment**

```yaml
input:
  - none (command starts fresh)

actions:
  - run: .specify/scripts/bash/check-prerequisites.sh --json --paths-only
  - parse: REPO_ROOT from JSON output
  - load: .specify/templates/raise/solution/estimation_roadmap.md
  - prepare: output file path (specs/main/estimation_roadmap.md)

verification:
  - template loaded successfully
  - paths confirmed (REPO_ROOT exists)

jidoka:
  - condition: template not found
  - action: Check .raise-kit setup, verify template was copied to .specify/

output:
  - template content in memory
  - REPO_ROOT path available
```

**Contract 2: Step 2 - Load Backlog and Extract SP**

```yaml
input:
  - file: specs/main/project_backlog.md

actions:
  - load backlog file
  - extract: all Epics with IDs and descriptions
  - extract: all Features with IDs, Epic mapping, priorities
  - extract: all User Stories with IDs, Feature mapping, SP estimates
  - identify: which Features are marked as MVP
  - calculate: Total SP (sum of all US estimates)

verification:
  - backlog exists and parseable
  - at least 1 Epic, 1 Feature, 3 User Stories found
  - SP estimates present (or marked as Pendiente)

jidoka:
  - condition: backlog file missing
  - action: Execute /raise.5.backlog first

  - condition: backlog has no SP estimates
  - action: Propose preliminary estimates + warn must refine

output:
  - structured backlog data (Epics, Features, User Stories with SP)
  - total_sp: int
  - mvp_features: array[feature_id]
```

**Contract 3: Step 4 - Configure Team Parameters**

```yaml
input:
  - $ARGUMENTS (optional user input, e.g., "2 engineers full-time, sprints 1 week")

actions:
  - if $ARGUMENTS empty:
      use defaults:
        - 1 AI Architect (50%) = 4 SP
        - 1 AI Engineer (100%) = 8 SP
        - 1 AI QA (50%) = 4 SP
        - Total capacity = 16 SP/sprint
        - Sprint duration = 2 weeks
      document: "Using default team structure"

  - if $ARGUMENTS provided:
      parse team structure from natural language
      calculate capacity based on roles + dedication
      document: "Using custom team structure"

verification:
  - capacity > 0 SP/sprint
  - capacity reasonable (8-40 SP/sprint range)
  - sprint duration > 0

jidoka:
  - condition: capacity < 8 SP/sprint
  - action: Alert that project would take too long, suggest increase capacity or reduce scope

  - condition: capacity unrealistic (>40 SP/sprint)
  - action: Question if team structure is feasible, suggest validation

output:
  - team_parameters: object (roles, capacity, sprint_duration)
  - used_defaults: boolean
```

**Contract 4: Step 6 - Calculate Roadmap Projection**

```yaml
input:
  - total_sp: int (from Step 2)
  - team_capacity: float (from Step 4)
  - sprint_duration_weeks: int (from Step 4)

actions:
  - calculate: iterations_needed = ceil(total_sp / team_capacity)
  - generate: iteration table with N rows (one per iteration)
    for each iteration:
      - numero: int (1, 2, 3, ...)
      - fechas: relative (e.g., "Semana 1-2", "Semana 3-4")
      - objetivo: suggested focus (e.g., "Sprint 1: Core features", "Sprint 2: Integrations")
      - elementos_planeados: which backlog items fit in this sprint (based on priority + SP)
      - sp_iteracion: int (sum of SP for items in this sprint, max = capacity)
      - sp_acumulados: running total

  - identify: which iterations contain MVP items
  - mark: MVP iterations clearly

verification:
  - iterations_needed > 0
  - sum(sp_iteracion) across all iterations >= total_sp
  - MVP iterations identified

jidoka:
  - condition: iterations_needed > 26 (> 6 months with 2-week sprints)
  - action: Warn that project is large, suggest reviewing MVP scope to reduce initial size

output:
  - roadmap_table: array[iteration] (with all columns)
  - mvp_iterations: array[int] (which iteration numbers are MVP)
```

**Contract 5: Step 11 - Finalize & Validate (Gate Execution)**

```yaml
input:
  - file: specs/main/estimation_roadmap.md (generated in previous steps)

actions:
  - confirm: file exists at path
  - execute: .specify/gates/raise/gate-estimation.md
  - capture: gate results (criteria passed/failed)

  - if gate FAILS:
      list: specific criteria that failed
      suggest: concrete corrections for each failure
      allow: user to iterate before continuing

  - if gate PASSES:
      show: summary of roadmap (Total SP, iterations, MVP SP/Total ratio)
      run: .specify/scripts/bash/update-agent-context.sh
      display: handoff message "→ Siguiente paso: /raise.7.sow - Generate Statement of Work"

verification:
  - gate executed (script ran)
  - validation results shown (pass/fail with details)
  - handoff offered if passed

jidoka:
  - condition: gate mandatory criteria failed
  - action: STOP - do not continue, iterate on failed criteria, do not offer handoff until gate passes

  - condition: gate script not found
  - action: Verify .raise-kit setup, check if gate file exists

output:
  - gate_result: pass | fail
  - summary: string (if pass)
  - handoff_offered: boolean
```

### API/Interface Contract: Gate Validation Criteria

**File**: `specs/010-estimation-command/contracts/gate-estimation-criteria.md`

```markdown
# Gate Estimation - Validation Criteria

## Purpose
Validate that the generated Estimation Roadmap is complete, accurate, and ready for use in preparing the Statement of Work.

## Mandatory Criteria (MUST PASS ALL)

### C1: Guía de Estimación Completa
- [ ] Section "1. Guía de Estimación en Puntos de Historia" exists
- [ ] Fibonacci scale documented (1, 2, 3, 5, 8, 13, 20, 40, 100)
- [ ] Factors to consider explained (complejidad, esfuerzo, incertidumbre)
- [ ] Planning poker process described

**Check Method**: Verify section exists and contains at least 3 subsections (escala, factores, proceso)

### C2: Estimation Table Complete
- [ ] Section "2. Estimación del Backlog" exists
- [ ] Table includes columns: ID, Elemento, Estimación (SP), Notas, Referencia
- [ ] ALL items from backlog appear in table (100% coverage)
- [ ] Total SP calculated and displayed

**Check Method**: Count backlog items vs table rows, verify Total SP = sum of all estimates

### C3: Team Parameters Documented
- [ ] Section "3. Parámetros para el Roadmap" exists
- [ ] Sprint duration documented
- [ ] Team structure documented (roles + dedication)
- [ ] Capacity documented (SP/sprint with calculation shown)
- [ ] Note about velocity measurement included (initial vs real)

**Check Method**: Verify all 4 parameters present and capacity calculation correct

### C4: Roadmap Projection Table Present
- [ ] Section "4. Roadmap Proyectado" exists
- [ ] Table includes columns: Iteración, Fechas, Objetivo, Elementos Planeados, SP Estimados, SP Acumulados
- [ ] At least 1 iteration row exists
- [ ] Total SP in roadmap matches or exceeds backlog Total SP
- [ ] Disclaimer present (projection must be refined with real data)

**Check Method**: Verify table complete, SP math correct, disclaimer included

### C5: MVP Clearly Identified
- [ ] MVP iterations marked in roadmap table (e.g., "MVP" label or clear distinction)
- [ ] MVP SP total calculated
- [ ] MVP ratio documented (MVP SP / Total SP)

**Check Method**: Verify MVP marking visible, ratio calculated

### C6: Cost Model Section Present
- [ ] Section "5. Vinculación con Modelo de Costos" exists
- [ ] SP-to-effort relationship explained
- [ ] Impact of changes discussed
- [ ] Key cost assumptions listed

**Check Method**: Verify section exists with at least 3 subsections

### C7: Metadata and References Complete
- [ ] Frontmatter YAML complete (document_id, title, project_name, client, version, date, author, related_docs, status)
- [ ] related_docs includes: PRD, Vision, Tech Design, Backlog
- [ ] Status is "Draft" or "In Review"

**Check Method**: Parse YAML, verify all required fields present

## Optional Criteria (Nice-to-Have)

- [ ] Roadmap includes iteration objectives (not just "Iteración 1, 2, 3")
- [ ] Team structure includes specific names/roles (not just generic)
- [ ] Cost model includes hourly rates or pricing estimates

## Failure Handling

**If ANY mandatory criterion fails**:
1. List specific criterion number + description that failed
2. Quote relevant section from roadmap (or note if missing)
3. Suggest concrete fix (e.g., "Add section 5 with cost model explanation")
4. STOP execution - do not offer handoff until all criteria pass

**Example Failure Output**:
```
❌ Gate FAILED - 2 criteria not met:

C2: Estimation Table Complete
  - Issue: Table only has 45 rows but backlog has 52 User Stories (87% coverage)
  - Fix: Add missing 7 User Stories to table: US-023, US-031, US-038, US-042, US-049, US-051, US-052

C5: MVP Clearly Identified
  - Issue: No MVP marking found in roadmap table
  - Fix: Add "MVP" column or marker to iterations 1-3 that contain MVP Features (FEAT-001, FEAT-004, FEAT-005)

🛑 JIDOKA: Fix these issues before continuing. Do not offer handoff to /raise.7.sow until gate passes.
```

## Success Output

**If ALL mandatory criteria pass**:
```
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: 163 SP
- MVP Story Points: 78 SP (48% of total)
- Iterations Needed: 11 sprints (22 weeks with 2-week sprints)
- Team Capacity: 16 SP/sprint
- Backlog Coverage: 100% (52/52 User Stories)
- Cost Model: Documented

→ Siguiente paso: /raise.7.sow - Generate Statement of Work from this roadmap
```
```

### Quickstart: Using the raise.6.estimation Command

**File**: `specs/010-estimation-command/quickstart.md`

```markdown
# Quickstart: raise.6.estimation Command

## Purpose

Generate an Estimation Roadmap with Story Point projections and sprint timeline from an existing Project Backlog.

## Prerequisites

- ✅ Project Backlog exists: `specs/main/project_backlog.md`
- ✅ Backlog contains User Stories with SP estimates (or marked as "Pendiente")
- ✅ Command has been injected to project via `transform-commands.sh`

## Basic Usage

### Scenario 1: Use Default Team Parameters

```bash
# Simplest - uses default team (16 SP/sprint, 2-week sprints)
/raise.6.estimation
```

**What happens**:
1. Loads backlog from `specs/main/project_backlog.md`
2. Uses default team: 1 Architect (50%), 1 Engineer (100%), 1 QA (50%) = 16 SP/sprint
3. Calculates iterations: Total SP / 16 = N sprints
4. Generates `specs/main/estimation_roadmap.md`
5. Validates via gate, offers handoff to `/raise.7.sow`

### Scenario 2: Custom Team Parameters

```bash
# Custom team: 2 engineers full-time, 1 QA 50%, sprints 1 week
/raise.6.estimation "2 engineers full-time, 1 QA 50%, sprints 1 week"
```

**What happens**:
1. Parses custom team: 2 * 8 + 0.5 * 8 = 20 SP/sprint, 1-week sprints
2. Calculates iterations: Total SP / 20 = fewer sprints
3. Documents custom team structure in roadmap
4. Rest is same as Scenario 1

## Expected Output

**File Created**: `specs/main/estimation_roadmap.md`

**Contents**:
1. **Guía de Estimación**: Fibonacci scale, factors, planning poker process
2. **Estimación del Backlog**: Table with all items + SP, Total SP
3. **Parámetros del Roadmap**: Team structure, capacity (16 SP/sprint), sprint duration
4. **Roadmap Proyectado**: Table with iterations, dates, objectives, SP acumulados
5. **Vinculación con Modelo de Costos**: SP → hours → cost explanation

## Validation

Command executes gate at the end:

```bash
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: 163 SP
- MVP Story Points: 78 SP (48% of total)
- Iterations Needed: 11 sprints (22 weeks)
- Team Capacity: 16 SP/sprint
```

## Next Step

After roadmap generated, create Statement of Work:

```bash
/raise.7.sow
```

This will use the estimation roadmap to generate the commercial proposal document.

## Troubleshooting

### Error: "Backlog not found"

```bash
🛑 JIDOKA: specs/main/project_backlog.md not found
→ Execute /raise.5.backlog first to generate the backlog
```

**Fix**: Run `/raise.5.backlog` before estimation command.

### Warning: "Missing SP estimates"

```bash
⚠ WARNING: 5 User Stories have no SP estimates
→ Proposing preliminary estimates (will need refinement):
  - US-023: 3 SP (medium complexity)
  - US-031: 5 SP (medium-high complexity)
  - US-042: 2 SP (low complexity)
```

**Fix**: Accept preliminary estimates for now, refine in planning poker later.

### Alert: "Project too long"

```bash
⚠ ALERT: Roadmap projects 28 sprints (56 weeks)
→ Consider reviewing MVP scope to reduce initial size
→ Target: MVP ≤ 10 sprints (20 weeks) for faster feedback
```

**Fix**: Review backlog, move non-MVP Features to later phases.

## Integration with Estimation Flow

```text
/raise.1.discovery → /raise.2.vision → /raise.4.tech-design → /raise.5.backlog
                                                                      ↓
                                                              /raise.6.estimation  ← YOU ARE HERE
                                                                      ↓
                                                               /raise.7.sow
```

This command is Step 6 of Kata L1-04 (estimation process).
```

## Phase 2: Pre-Implementation Summary

**Artifacts Ready for Implementation**:

1. ✅ **spec.md**: Complete functional specification with 12 FRs, 7 success criteria, 3 prioritized user stories
2. ✅ **plan.md**: This file - detailed implementation plan with constitution check, data model, contracts
3. ✅ **research.md**: Decision rationale documented (Phase 0 complete)
4. ✅ **data-model.md**: Command outline structure + gate validation structure defined
5. ✅ **contracts/**: Step-by-step contracts for all 11 command steps + gate criteria
6. ✅ **quickstart.md**: User guide with usage scenarios and troubleshooting

**Ready for /speckit.tasks**:

The planning phase is complete. All design decisions are documented, command structure is defined, and contracts specify exact behavior for each step. The next command (`/speckit.tasks`) will generate the task list for implementation:

1. Create `.raise-kit/gates/raise/gate-estimation.md` (from contract)
2. Create `.raise-kit/commands/02-projects/raise.6.estimation.md` (from data model + contracts)
3. Validate command structure against rule 110 checklist
4. Test command execution manually
5. Document in `specs/010-estimation-command/tasks.md`

**Key Implementation Notes**:

- **Critical**: ALL paths must use `.specify/` prefix (verified in contracts)
- **Structure**: Follow raise.5.backlog.md as reference (same pattern)
- **Language**: Instructions English, content Spanish (enforced in High-Signaling Guidelines)
- **Jidoka**: Every step has explicit stop condition (contracts define these)
- **Gate**: Must create gate-estimation.md first (dependency for step 11)

**Constitution Re-Check Post-Design**: ✅ **STILL PASSING** - Design maintains alignment with all 8 principles. No new complexity introduced.
