# Research & Decisions: SOW Command

**Feature**: SOW Command (`/raise.7.sow`)
**Date**: 2026-01-21

## Key Design Decisions

### 1. Command Architecture
- **Decision**: Implement as a Markdown command file in `.raise-kit/commands/02-projects/`.
- **Rationale**: Consistent with existing Raise Kit commands (`raise.1.discovery`, etc.). Allows for easy versioning and distribution via `transform-commands.sh`.
- **Alternatives Considered**: Creating a standalone script. Rejected because it breaks the "text-first" and "agent-centric" architecture of Raise Kit.

### 2. Template Strategy
- **Decision**: Reuse existing `src/templates/solution/statement_of_work.md`.
- **Rationale**: The template is already validated (v1.0) and contains all necessary sections.
- **Action**: Ensure the template is present in `.raise-kit/templates/raise/solution/` during setup.

### 3. Data Flow
- **Decision**: Use a "consolidator" pattern where the agent reads multiple source files (`estimation_roadmap.md`, `project_backlog.md`, etc.) and fills the target template in one pass.
- **Rationale**: Minimizes user interaction steps. The agent context window is large enough to handle these 4-5 markdown files.
- **Risk**: Context limit with very large backlogs. Mitigated by `read_file` tools that can read chunks if needed, though for standard documents entire file reading is usually fine.

## Technical Unknowns Resolution

| Unknown | Resolution |
|---------|------------|
| Template Location | Confirmed at `src/templates/solution/statement_of_work.md` |
| Command Path | Confirmed at `.raise-kit/commands/02-projects/raise.7.sow.md` |
| Execution Context | Confirmed target references must be `.specify/...` |
