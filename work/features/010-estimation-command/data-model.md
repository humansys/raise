# Data Model: raise.6.estimation Command

**Feature**: Comando raise.6.estimation
**Date**: 2026-01-21
**Branch**: 010-estimation-command

## Overview

This document defines the data structures and command outline structure for the `raise.6.estimation` command. Since this is a documentation transformation command (not code), the "data model" refers to the conceptual entities manipulated during execution and the structure of the command file itself.

---

## Entity 1: CommandOutline

The command file structure that orchestrates the estimation roadmap generation.

### Structure

```yaml
command_file: raise.6.estimation.md

sections:
  frontmatter:
    type: YAML
    fields:
      description: string (1-line summary of command purpose)
      handoffs: array
        - label: string (visible to user, e.g., "Create Statement of Work")
          agent: string (next command name, e.g., "raise.7.sow")
          prompt: string (handoff message text)
          send: boolean (true = auto-offer handoff)

  user_input:
    type: markdown section
    content: "$ARGUMENTS (command-line arguments)"
    consideration_note: "You **MUST** consider the user input before proceeding (if not empty)."

  outline:
    type: markdown section
    goal: string (clear objective statement for this command)
    steps: array[11]
      - number: int (1-11)
        title: string (format: "Paso N: [Infinitive Verb] [Object]")
        actions: array[string] (specific, executable actions)
        verification: string (observable completion criteria)
        jidoka_block: string (format: "> **Si no puedes continuar**: [Condition] → **JIDOKA**: [Action]")

  high_signaling_guidelines:
    type: markdown section
    fields:
      output: string (what files this command generates)
      focus: string (what this command focuses on)
      language: string (always "Instructions English; Content **SPANISH**")
      jidoka: string (when to stop and ask for help)

  ai_guidance:
    type: markdown section
    fields:
      role: string (agent's role during execution)
      be_proactive: string (what to propose by default)
      follow_katas: string (which kata to follow, if applicable)
      traceability: string (how to link decisions to artifacts)
      gates: string (what to validate at finalization)
      heutagogy: string (how to facilitate learning, not just execute)
```

### Constraints

- **Mandatory sections**: All 6 sections must be present (frontmatter, user input, outline, notes optional, high-signaling, AI guidance)
- **Outline steps**: Exactly 11 steps (matches research decision)
- **Step structure**: Each step must have title, actions, verification, jidoka_block
- **Language rule**: Instructions in English, generated content in Spanish
- **Path references**: ALL paths must use `.specify/` prefix

### Example Fragment

```markdown
---
description: Generate Estimation Roadmap from Project Backlog with Story Point projections and sprint timeline
handoffs:
  - label: Create Statement of Work
    agent: raise.7.sow
    prompt: Generate Statement of Work from this estimation roadmap
    send: true
---

## User Input

​```text
$ARGUMENTS
​```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Populate the Estimation Roadmap template (`.specify/templates/raise/solution/estimation_roadmap.md`) with content derived from the Project Backlog, producing `specs/main/estimation_roadmap.md` with team parameters, iteration projections, MVP identification, and cost model linkage.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load the template from `.specify/templates/raise/solution/estimation_roadmap.md`.
   - Prepare output file at `specs/main/estimation_roadmap.md`.
   - **Verificación**: Template loaded, paths confirmed.
   - > **Si no puedes continuar**: Template not found → **JIDOKA**: Check .raise-kit setup and verify template was copied correctly to .specify/.
```

---

## Entity 2: GateValidation

The gate file structure that validates the generated estimation roadmap.

### Structure

```yaml
gate_file: gate-estimation.md

sections:
  purpose:
    type: markdown header
    content: string (what this gate validates)

  mandatory_criteria:
    type: markdown checklist
    count: 7
    structure:
      - criterion_id: string (C1, C2, etc.)
        criterion_name: string (e.g., "Guía de Estimación Completa")
        checklist_items: array[string] (checkable conditions)
        check_method: string (how to verify this criterion)

  optional_criteria:
    type: markdown checklist
    count: 3
    structure: (same as mandatory, but failures allowed)

  failure_handling:
    type: markdown section
    fields:
      action: string (always "JIDOKA - stop execution")
      feedback_format: string (list failures + suggest fixes)
      example_output: code block (showing failure message format)

  success_output:
    type: markdown section
    fields:
      action: string (show pass confirmation + summary)
      next_step: string (offer handoff to raise.7.sow)
      example_output: code block (showing success message format)
```

### Mandatory Criteria (7)

| ID | Criterion Name | What It Checks | Check Method |
|----|----------------|----------------|--------------|
| C1 | Guía de Estimación Completa | Section 1 exists with Fibonacci scale, factors, process | Verify section has 3+ subsections |
| C2 | Estimation Table Complete | Section 2 exists with ALL backlog items + SP, Total SP | Count rows vs backlog items (100% coverage) |
| C3 | Team Parameters Documented | Section 3 exists with sprint duration, structure, capacity, velocity note | Verify all 4 parameters present |
| C4 | Roadmap Projection Table Present | Section 4 exists with iteration table, SP math correct, disclaimer | Verify table complete, math correct |
| C5 | MVP Clearly Identified | MVP iterations marked, MVP SP calculated, ratio documented | Verify MVP marking visible |
| C6 | Cost Model Section Present | Section 5 exists with SP-to-effort, impact of changes, assumptions | Verify section has 3+ subsections |
| C7 | Metadata and References Complete | YAML frontmatter complete, related_docs includes PRD/Vision/Tech/Backlog | Parse YAML, verify fields |

### Example Fragment

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
```

---

## Entity 3: TeamParameters

Configuration for team capacity that drives roadmap calculations.

### Structure

```yaml
team_parameters:
  roles: array
    - name: string (e.g., "AI Architect", "AI Engineer", "AI QA")
      dedication: float (0.0-1.0, where 1.0 = 100% full-time)
      sp_per_sprint: float (calculated as: dedication * 8 SP baseline)

  capacity:
    total_sp_per_sprint: float (sum of all roles' sp_per_sprint)
    calculation_note: string (documenting the math)

  sprint:
    duration: string (e.g., "2 semanas", "1 week")
    duration_weeks: int (for date calculations in roadmap)

  source:
    used_defaults: boolean (true if $ARGUMENTS empty)
    custom_config: string (if provided, natural language from $ARGUMENTS)
    documented: boolean (must be true - parameters always documented in roadmap)
```

### Default Values

```yaml
default_team_parameters:
  roles:
    - name: "AI Architect"
      dedication: 0.5
      sp_per_sprint: 4.0

    - name: "AI Engineer"
      dedication: 1.0
      sp_per_sprint: 8.0

    - name: "AI QA"
      dedication: 0.5
      sp_per_sprint: 4.0

  capacity:
    total_sp_per_sprint: 16.0
    calculation_note: "(0.5 * 8) + (1.0 * 8) + (0.5 * 8) = 16 SP"

  sprint:
    duration: "2 semanas"
    duration_weeks: 2

  source:
    used_defaults: true
    custom_config: null
    documented: true
```

### Validation Rules

```yaml
validation:
  capacity_range:
    min: 8.0 (SP/sprint)
    max: 40.0 (SP/sprint)
    reason: "Below 8 = too slow, above 40 = unrealistic for estimation phase"

  sprint_duration_range:
    min_weeks: 1
    max_weeks: 4
    reason: "Below 1 week = too short for planning, above 4 weeks = too long for feedback"

  jidoka_conditions:
    - condition: "capacity < 8.0"
      action: "Alert project too long, suggest increase capacity or reduce scope"

    - condition: "capacity > 40.0"
      action: "Question if team structure is feasible, suggest validation"
```

---

## Entity 4: BacklogData

Structured representation of the project backlog loaded from markdown.

### Structure

```yaml
backlog_data:
  source_file: "specs/main/project_backlog.md"

  epics: array
    - id: string (e.g., "EPIC-001")
      title: string
      description: string
      features: array[feature_id] (which features belong to this epic)

  features: array
    - id: string (e.g., "FEAT-001")
      title: string
      description: string
      epic_id: string (parent epic)
      priority: enum [Alta, Media, Baja]
      is_mvp: boolean
      user_stories: array[user_story_id] (which US belong to this feature)

  user_stories: array
    - id: string (e.g., "US-001")
      title: string
      description: string
      feature_id: string (parent feature)
      sp_estimate: float | "Pendiente" (Story Points estimate)
      acceptance_criteria: array[string]
      technical_details: string
      priority_inherited: enum [Alta, Media, Baja] (from parent feature)

  metrics:
    total_sp: float (sum of all user_stories.sp_estimate where not "Pendiente")
    total_user_stories: int (count)
    pending_estimates: int (count where sp_estimate == "Pendiente")
    mvp_features: array[feature_id]
    mvp_sp: float (sum of SP for US in MVP features)
    mvp_ratio: float (mvp_sp / total_sp)
```

### Extraction Process

```yaml
extraction_steps:
  1_load_file:
    action: "Read specs/main/project_backlog.md"
    output: "markdown content string"

  2_parse_epics:
    action: "Find all '### Epic' sections, extract EPIC-XXX IDs + titles"
    output: "array of epic objects"

  3_parse_features:
    action: "Find all '#### Feature' sections, extract FEAT-XXX IDs + titles + priorities + MVP markers"
    output: "array of feature objects"

  4_parse_user_stories:
    action: "Find all tables with columns: ID | Historia | Estimación (SP) | ..., extract rows"
    output: "array of user_story objects"

  5_calculate_metrics:
    action: "Sum SP, count items, identify MVP"
    output: "metrics object"
```

### Handling Missing SP Estimates

```yaml
missing_estimates_strategy:
  detection:
    condition: "sp_estimate == 'Pendiente' OR sp_estimate == null OR sp_estimate == ''"

  preliminary_estimation:
    analyze:
      - description_length (characters)
      - acceptance_criteria_count

    rules:
      - condition: "description < 100 chars AND criteria <= 2"
        preliminary_sp: 2
        complexity: "low"

      - condition: "description 100-300 chars AND criteria 3-4"
        preliminary_sp: 3
        complexity: "medium"

      - condition: "description 300-500 chars AND criteria 5-6"
        preliminary_sp: 5
        complexity: "medium-high"

      - condition: "description > 500 chars OR criteria > 6"
        preliminary_sp: 8
        complexity: "high"

  documentation:
    format: "[Pendiente - Estimado preliminar: X SP]"
    note: "Debe refinarse en planning poker"

  warning:
    message: "⚠ WARNING: N User Stories have no SP estimates → Proposing preliminary estimates (will need refinement)"
```

---

## Entity 5: RoadmapProjection

The calculated roadmap with iterations, dates, and SP distribution.

### Structure

```yaml
roadmap_projection:
  input_data:
    total_sp: float (from backlog_data.metrics)
    team_capacity: float (from team_parameters)
    sprint_duration_weeks: int (from team_parameters)

  iterations: array
    - number: int (1, 2, 3, ...)
      dates_estimated: string (relative, e.g., "Semana 1-2", "Semana 3-4")
      objective: string (suggested focus for this sprint)
      backlog_items_planned: array[string] (which Epics/Features/US IDs in this sprint)
      sp_iteration: float (sum of SP for items in this sprint, max = team_capacity)
      sp_accumulated: float (running total of SP completed by end of this iteration)
      is_mvp: boolean (true if this iteration contains MVP items)

  metrics:
    iterations_needed: int (calculated as: ceil(total_sp / team_capacity))
    total_weeks: int (iterations_needed * sprint_duration_weeks)
    mvp_iterations_count: int (how many iterations contain MVP work)
    mvp_weeks: int (mvp_iterations_count * sprint_duration_weeks)

  warnings: array
    - condition: string
      message: string
    # Example: {condition: "iterations_needed > 26", message: "Project > 6 months, consider reducing MVP scope"}
```

### Calculation Process

```yaml
calculation_steps:
  1_calculate_iterations:
    formula: "iterations_needed = ceil(total_sp / team_capacity)"
    example: "ceil(163 SP / 16 SP/sprint) = ceil(10.19) = 11 iterations"

  2_distribute_items:
    algorithm: |
      for each iteration (1 to iterations_needed):
        remaining_capacity = team_capacity
        iteration_items = []

        for each backlog item (sorted by priority, then dependencies):
          if item.sp_estimate <= remaining_capacity:
            iteration_items.append(item)
            remaining_capacity -= item.sp_estimate
          if remaining_capacity == 0:
            break

        iterations[i].backlog_items_planned = iteration_items
        iterations[i].sp_iteration = team_capacity - remaining_capacity

  3_calculate_dates:
    algorithm: |
      for each iteration (1 to iterations_needed):
        start_week = (iteration.number - 1) * sprint_duration_weeks + 1
        end_week = start_week + sprint_duration_weeks - 1
        iteration.dates_estimated = f"Semana {start_week}-{end_week}"

  4_identify_mvp:
    algorithm: |
      for each iteration:
        if any(item in iteration.backlog_items_planned is_mvp == true):
          iteration.is_mvp = true

  5_calculate_metrics:
    algorithm: |
      metrics.iterations_needed = iterations.count
      metrics.total_weeks = iterations_needed * sprint_duration_weeks
      metrics.mvp_iterations_count = count(iteration where is_mvp == true)
      metrics.mvp_weeks = mvp_iterations_count * sprint_duration_weeks
```

---

## Step-by-Step Data Flow

### Flow Diagram

```
[Initialize] → [Load Backlog] → [Configure Team] → [Calculate Roadmap] → [Validate]
     ↓              ↓                  ↓                    ↓              ↓
  Template     BacklogData      TeamParameters     RoadmapProjection    Gate
  (loaded)     (extracted)       (configured)       (calculated)      (executed)
```

### Detailed Flow

```yaml
step_1_initialize:
  input: []
  actions:
    - run_prerequisites: ".specify/scripts/bash/check-prerequisites.sh"
    - load_template: ".specify/templates/raise/solution/estimation_roadmap.md"
  output:
    - template_content: string
    - repo_root: path

step_2_load_backlog:
  input:
    - backlog_file: "specs/main/project_backlog.md"
  actions:
    - read_file: backlog_file
    - parse_markdown: (extract Epics, Features, User Stories)
    - calculate_metrics: (total_sp, mvp_sp, ratios)
  output:
    - backlog_data: BacklogData entity

step_3_instantiate_template:
  input:
    - template_content: string
    - backlog_data: BacklogData
  actions:
    - fill_metadata: (document_id, title, project_name, dates)
    - write_file: "specs/main/estimation_roadmap.md"
  output:
    - roadmap_file: path (created)

step_4_configure_team:
  input:
    - user_arguments: $ARGUMENTS (optional)
  actions:
    - if arguments_empty: use_defaults()
    - else: parse_custom_team(arguments)
    - validate_capacity: (8 <= capacity <= 40)
  output:
    - team_parameters: TeamParameters entity

step_5_generate_estimation_table:
  input:
    - backlog_data: BacklogData
    - roadmap_file: path
  actions:
    - create_table_rows: for each US in backlog_data
    - calculate_total_sp: sum(all estimates)
    - write_section_2: to roadmap_file
  output:
    - estimation_table: written to file

step_6_calculate_roadmap:
  input:
    - backlog_data: BacklogData
    - team_parameters: TeamParameters
  actions:
    - calculate_iterations: ceil(total_sp / capacity)
    - distribute_items: to iterations
    - calculate_dates: for each iteration
    - identify_mvp: mark iterations with MVP items
  output:
    - roadmap_projection: RoadmapProjection entity

step_7_identify_mvp:
  input:
    - roadmap_projection: RoadmapProjection
  actions:
    - mark_mvp_iterations: in roadmap table
    - calculate_mvp_metrics: (mvp_sp, mvp_ratio)
  output:
    - mvp_marked: boolean

step_8_document_cost_model:
  input:
    - team_parameters: TeamParameters
    - roadmap_projection: RoadmapProjection
  actions:
    - explain_sp_to_hours: (e.g., "1 SP ≈ 4-6 hours")
    - document_team_cost: (capacity * rate * weeks)
    - write_section_5: to roadmap_file
  output:
    - cost_model_section: written to file

step_9_add_disclaimers:
  input:
    - team_parameters: TeamParameters
  actions:
    - document_assumptions: (used_defaults, sprint_duration, etc.)
    - add_disclaimer: "This is initial projection, refine with real velocity"
  output:
    - disclaimers: written to file

step_10_generate_summary:
  input:
    - roadmap_projection: RoadmapProjection
  actions:
    - calculate_totals: (total_sp, iterations, weeks)
    - calculate_ratios: (mvp/total)
  output:
    - summary_metrics: written to file

step_11_finalize_validate:
  input:
    - roadmap_file: path
  actions:
    - confirm_file_exists: roadmap_file
    - execute_gate: ".specify/gates/raise/gate-estimation.md"
    - if gate_passes: show_summary(), offer_handoff()
    - if gate_fails: list_failures(), stop_execution()
  output:
    - gate_result: pass | fail
    - handoff_offered: boolean (if pass)
```

---

## Relationships

```
CommandOutline (1) --contains--> (11) Step
CommandOutline (1) --references--> (1) GateValidation
CommandOutline (1) --uses--> (1) Template (estimation_roadmap.md)

Step[2] (1) --produces--> (1) BacklogData
Step[4] (1) --produces--> (1) TeamParameters
Step[6] (1) --consumes--> (1) BacklogData + TeamParameters
Step[6] (1) --produces--> (1) RoadmapProjection
Step[11] (1) --executes--> (1) GateValidation

BacklogData (1) --contains--> (N) Epic
BacklogData (1) --contains--> (N) Feature
BacklogData (1) --contains--> (N) UserStory

RoadmapProjection (1) --contains--> (N) Iteration
RoadmapProjection (1) --references--> (N) BacklogItem (via backlog_items_planned)
```

---

## Summary

This data model defines 5 core entities:

1. **CommandOutline**: Structure of the command file (raise.6.estimation.md)
2. **GateValidation**: Structure of the validation gate (gate-estimation.md)
3. **TeamParameters**: Team capacity configuration (defaults or custom)
4. **BacklogData**: Parsed representation of project_backlog.md
5. **RoadmapProjection**: Calculated iteration plan with dates and SP

These entities flow through 11 steps, transforming input (backlog) into output (estimation roadmap) through a series of calculations and documentation steps. The gate validates the final output before handoff to the next command in the estimation flow.
