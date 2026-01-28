---
description: Create Statement of Work from Estimation Roadmap (L1-04 Step 7)
handoffs:
  - label: Review and Send SoW
    agent: system
    prompt: Review the generated Statement of Work and prepare for client delivery
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Create a formal `statement_of_work.md` by consolidating project data from PRD, Vision, Tech Design, Backlog, and Estimation Roadmap.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Use `find_by_name` to locate these input files (search in `specs/main`):
     - `project_requirements.md` (PRD)
     - `solution_vision.md` (Vision)
     - `tech_design.md` (Tech Design)
     - `project_backlog.md` (Backlog)
     - `estimation_roadmap.md` (Roadmap)
   - Load template from `.specify/templates/raise/solution/statement_of_work.md`
   - **Verification**: All 5 input files must be found. The template must be loaded.
   - > **Si no puedes continuar**: Missing `estimation_roadmap.md` → **JIDOKA**: Stop and suggest running `/raise.6.estimation`. Missing other files → Warn user but proceed if Roadmap exists.

2. **Phase 1: Project Overview & Objectives**:
   - Extract `Introduction` and `Vision` from `project_requirements.md` and `solution_vision.md`.
   - Populate SoW **Section 1 (Introduction)** using PRD Sec 1.1.
   - Using `solution_vision.md`, populate SoW **Section 2 (Objectives)** with clear bullets.
   - **Verification**: Sections 1 and 2 are filled with coherent business language.

3. **Phase 2: Scope & Deliverables**:
   - Extract `Scope` and `Exclusions` from `project_requirements.md`.
   - Extract `Deliverables` and `Epics` from `project_backlog.md` and `tech_design.md`.
   - Populate SoW **Section 3 (Scope)** specifically filling `3.2 Actividades Principales`.
   - Populate SoW **Section 4 (Entregables)** listing documentation and software.
   - Populate SoW **Section 8 (Exclusions)** explicitly listing what is out of scope.
   - **Verification**: Scope and Exclusions clearly differentiate what IS and IS NOT included.

4. **Phase 3: Timeline & Milestones**:
   - Extract `Implementation Roadmap` table from `estimation_roadmap.md`.
   - Populate SoW **Section 5 (Cronograma)** mapping the phases and durations.
   - **Verification**: Timeline table matches the Estimation Roadmap.

5. **Phase 4: Pricing & Terms**:
   - Extract `Total Cost` and `Payment Terms` from `estimation_roadmap.md`.
   - Populate SoW **Section 9 (Precio y Condiciones)**.
   - Ensure specific numbers are used (or "TBD" if ranges are present, with a note).
   - **Verification**: Financial data is present in Section 9.

6. **Finalize & Review**:
   - Save the result to `specs/main/statement_of_work.md`.
   - Run `.specify/scripts/bash/update-agent-context.sh`.
   - Display summary of the generated SOW (Total cost, Duration, Key deliverables).
   - **Verification**: File exists and is non-empty.

## High-Signaling Guidelines

- **Output**: `specs/main/statement_of_work.md`
- **Focus**: Contractual clarity, binding scope, and accurate financial/temporal data.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: IF `estimation_roadmap.md` is missing, STOP immediately. This command requires cost/time data.

## AI Guidance

When executing this workflow:
1. **Role**: Contract Administrator & Technical Account Manager.
2. **Be proactive**: If the PRD excludes something (Section 3.2), ensure it appears in SoW Section 8.
3. **Follow Katas**: This implements Step 7 of Kata L1-04 (Formalize Proposal).
4. **Traceability**: Reference source document IDs in the SoW header where possible.
