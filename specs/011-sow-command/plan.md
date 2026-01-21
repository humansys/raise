# Implementation Plan: SOW Command

**Branch**: `001-sow-command` | **Date**: 2026-01-21 | **Spec**: [specs/001-sow-command/spec.md](../spec.md)
**Input**: Feature specification from `/specs/001-sow-command/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement the `/raise.7.sow` command to finalize the estimation flow (L1-04). This command will consolidate data from `project_requirements.md`, `solution_vision.md`, `tech_design.md`, `project_backlog.md`, and `estimation_roadmap.md` into a contractual `statement_of_work.md` using the existing template. This ensures a standardized, error-free handoff from estimation to contract.

## Technical Context

**Language/Version**: Markdown (for command definition) + Bash (for scripts)
**Primary Dependencies**: `raise-kit` existing scripts (`check-prerequisites.sh`, `update-agent-context.sh`)
**Storage**: Local Filesystem (reading inputs from `specs/main/`, writing output to `specs/main/`)
**Testing**: Manual execution of the command in a test workspace with mock data.
**Target Platform**: Speckit CLI (generic)
**Project Type**: Specification & Command Definition
**Performance Goals**: N/A (Text processing)
**Constraints**: Must use absolute paths valid in the target environment (referencing `.specify/` instead of `.raise-kit/`).
**Scale/Scope**: Single command file + 1 template usage.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Heutagogy**: The command facilitates self-directed work by guiding the user through the final estimation step.
- [x] **Jidoka**: The command includes explicit checks (Jidoka blocks) for missing upstream artifacts before proceeding.
- [x] **Governance as Code**: The process is codified in a versioned command file.
- [x] **Simplicity**: Reuses existing templates and scripts; does not introduce new binaries or complex logic.

## Project Structure

### Documentation (this feature)

```text
specs/001-sow-command/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A for this command)
├── quickstart.md        # Phase 1 output (Usage guide)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
.raise-kit/
├── commands/
│   └── 02-projects/
│       └── raise.7.sow.md      # The new command file
└── templates/
    └── raise/
        └── solution/
            └── statement_of_work.md  # Template (verify existence)

specs/main/                     # Target directory for execution tests
```

