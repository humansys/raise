# Tasks: SOW Command

**Feature**: SOW Command (`/raise.7.sow`)
**Status**: Planned

## Phase 1: Setup

Goal: Initialize environment and ensure prerequisites.

- [x] T001 Verify template existence and copy to `.raise-kit` if needed
  - Check `src/templates/solution/statement_of_work.md`
  - Ensure directory `.raise-kit/templates/raise/solution/` exists
  - Copy template to `.raise-kit/templates/raise/solution/statement_of_work.md`

## Phase 2: Foundational

Goal: N/A (No shared libraries or complex infrastructure).

## Phase 3: User Story 1 - Generate Statement of Work

Goal: Implement the core command to generate SOW from estimation artifacts.

- [x] T002 [US1] Create command file infrastructure
  - Create `.raise-kit/commands/02-projects/raise.7.sow.md`
  - Define Frontmatter (description, handoffs)
  - Define User Input section
  - Define High-Signaling Guidelines & AI Guidance

- [x] T003 [US1] Implement Environment Initialization Step
  - Add `Initialize Environment` step to command
  - Check for `specs/main/estimation_roadmap.md`, `specs/main/project_backlog.md`, `specs/main/tech_design.md`
  - Check for `specs/main/solution_vision.md`, `specs/main/project_requirements.md`
  - Add Jidoka blocks for missing files

- [x] T004 [US1] Implement Data Loading & Mapping Logic
  - Add steps to read inputs and map to SoW sections (Plan Sec 4.1)
  - Map Timeline & Cost -> Sec 5 & 9
  - Map Scope & Exclusions -> Sec 3 & 8
  - Map Deliverables -> Sec 4

- [x] T005 [US1] Implement Final Validation & Handoff
  - Add verification step for generated files
  - Since this is the last step, handoff might be manual review or export

## Final Phase: Polish

- [x] T006 [P] Verify portability of path references
  - Ensure all paths use `.specify/...` not `.raise-kit/...`

## Dependencies

- T001 -> T002
- T002 -> T003 -> T004 -> T005
- T006 can run after T002

## Implementation Strategy

1. **Sequential**: Follow task order T001 -> T005
2. **Setup**: Ensure template is in place first.
3. **Command Construction**: Build the markdown file step-by-step.
