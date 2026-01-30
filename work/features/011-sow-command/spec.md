# Feature Specification: SOW Command

**Feature Branch**: `001-sow-command`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Crear comando /raise.7.sow para generar Statement of Work desde Estimation Roadmap siguiendo kata L1-04 paso 7"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Statement of Work (Priority: P1)

As an Estimation Analyst or Project Lead, I want a command that automatically generates a Statement of Work (SOW) document by consolidating information from the Estimation Roadmap, Backlog, Tech Design, and PRD, so that I can present a formal proposal to the client without manually copying and pasting data.

**Why this priority**: It is the final step of the estimation flow (L1-04) and crucial for closing the sales/estimation cycle. Currently, this is done manually, leading to inconsistencies and errors.

**Independent Test**: Can be tested by having a full set of previous artifacts (PRD, Vision, Tech Design, Backlog, Estimation) and running the command. The result should be a filled `statement_of_work.md` in `specs/main/`.

**Acceptance Scenarios**:

1. **Given** a project with `estimation_roadmap.md` and all upstream artifacts, **When** I run `/raise.7.sow`, **Then** a `specs/main/statement_of_work.md` file is created containing the implementation timeline, total costs, and scope scope definition derived from the inputs.
2. **Given** missing upstream artifacts (e.g., no Estimation Roadmap), **When** I run `/raise.7.sow`, **Then** the command should stop and warn me (Jidoka) about the missing dependencies.

### Edge Cases

- **Missing Input Artifacts**: If any required artifact (e.g., `estimation_roadmap.md`) is missing, the command should fail gracefully with a specific error message instructing the user to run the precursor command.
- **Incomplete Input Data**: If an input artifact exists but lacks required sections (e.g., empty Timeline in Roadmap), the command should proceed but mark the corresponding SOW section with a "WARNING: Source data missing" placeholder.
- **Template Missing**: If the SOW template is not found in `.specify/templates`, the command must halt immediately.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load the following input artifacts:
    - `specs/main/estimation_roadmap.md` (Primary source for timeline and costs)
    - `specs/main/project_backlog.md` (Source for deliverables list)
    - `specs/main/tech_design.md` (Source for technical scope)
    - `specs/main/solution_vision.md` (Source for project goals)
    - `specs/main/project_requirements.md` (Source for business context, exclusions, assumptions)
- **FR-002**: System MUST load the template from `.specify/templates/raise/solution/statement_of_work.md`.
- **FR-003**: System MUST map the "Timeline and Key Milestones" from Estimation Roadmap to SOW Section 5.
- **FR-004**: System MUST map the "Total Cost" and "Payment Terms" from Estimation Roadmap to SOW Section 9.
- **FR-005**: System MUST map the "Scope" and "Out of Scope" (Exclusions) from PRD to SOW Sections 3 and 8 respectively.
- **FR-006**: System MUST map the "Deliverables" from Tech Design and Backlog to SOW Section 4.
- **FR-007**: System MUST validate that all input files exist before proceeding (Jidoka).
- **FR-008**: System MUST generate the output file at `specs/main/statement_of_work.md`.
- **FR-009**: The command MUST follow the standard Raise Kit command structure (Frontmatter, User Input, Outline, High-Signaling Guidelines, AI Guidance).

### Key Entities *(include if feature involves data)*

- **Statement of Work (Artifact)**: The final contractual document defining scope, time, and cost.
- **Estimation Roadmap (Artifact)**: Input providing the schedule and financial data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The generated SOW contains populated sections for Timeline (Sec 5) and Pricing (Sec 9) that match the source Estimation Roadmap data.
- **SC-002**: The generated SOW contains populated sections for Scope (Sec 3) and Exclusions (Sec 8) that match the source PRD/Tech Design data.
- **SC-003**: The command execution completes successfully in under 30 seconds given valid inputs.
- **SC-004**: 100% of the SOW template placeholders related to scope, time, and cost are addressed (either filled or marked for manual review).

## Dependencies & Assumptions

- **Dependency**: The template `src/templates/solution/statement_of_work.md` must exist and be valid.
- **Assumption**: The upstream artifacts (PRD, Vision, Tech Design, Backlog, Estimation) follow the standard Raise Kit templates and structure, allowing for reliable parsing.
