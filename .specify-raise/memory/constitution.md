<!--
  SYNC IMPACT REPORT
  Version change: N/A (initial) → 1.0.0

  Added sections:
  - Core Principles (5 principles)
  - Workflow Standards
  - Quality Assurance
  - Governance

  Templates validated:
  ✅ .specify/templates/spec-template.md - Aligns with Specification-First principle
  ✅ .specify/templates/plan-template.md - Contains Constitution Check gate
  ✅ .specify/templates/tasks-template.md - Supports Incremental Delivery (user story phases)
  ✅ .specify/templates/checklist-template.md - Supports Quality Gates principle
  ✅ .specify/templates/agent-file-template.md - Supports Agent-Agnostic principle

  Follow-up TODOs: None
-->

# Speckit Constitution

## Core Principles

### I. Specification-First

Every feature MUST begin with a requirements specification focused on user needs.

- Specifications MUST describe WHAT users need and WHY, never HOW to implement
- No implementation details (languages, frameworks, APIs, code structure) in specs
- Written for business stakeholders, not developers
- Success criteria MUST be measurable and technology-agnostic
- Maximum 3 `[NEEDS CLARIFICATION]` markers per spec; prioritize by: scope > security > UX

**Rationale**: Clear requirements prevent scope creep and ensure alignment between
stakeholders before development begins.

### II. Incremental Delivery

Features MUST be structured as independently implementable and testable user stories.

- Each user story MUST be a viable MVP that delivers standalone value
- Stories are prioritized (P1, P2, P3) and can be developed/tested/deployed independently
- Phase structure: Setup → Foundational (blocking) → User Stories (parallel-capable) → Polish
- Foundational phase MUST complete before ANY user story work begins
- Implementation stops at checkpoints to validate each story independently

**Rationale**: Reduces risk by enabling early validation and deployment of partial
functionality without waiting for complete feature sets.

### III. Quality Gates

Constitution compliance and requirements quality MUST be validated at defined checkpoints.

- Constitution Check is a mandatory GATE before Phase 0 research and after Phase 1 design
- Checklists are "Unit Tests for English" - they validate requirements quality, NOT implementation
- Checklist items test: Completeness, Clarity, Consistency, Measurability, Coverage
- Items MUST NOT verify system behavior; they MUST ask if requirements are well-specified
- Violations of constitution principles are automatically CRITICAL severity

**Rationale**: Catching ambiguities and gaps in requirements is cheaper than fixing them
in implementation. Quality gates enforce discipline.

### IV. Artifact Consistency

All design artifacts (spec, plan, tasks) MUST maintain cross-document consistency.

- `/speckit.analyze` performs read-only consistency analysis across all artifacts
- Detect: duplications, ambiguities, underspecification, coverage gaps, terminology drift
- Requirements MUST map to tasks; orphan tasks or uncovered requirements are flagged
- Severity levels: CRITICAL (blocks implementation) → HIGH → MEDIUM → LOW
- Constitution conflicts are non-negotiable; adjust artifacts, not principles

**Rationale**: Inconsistent artifacts lead to implementation confusion and rework.
Automated analysis catches drift early.

### V. Agent-Agnostic Design

The system MUST support multiple AI coding agents without vendor lock-in.

- Scripts detect and update agent-specific context files (CLAUDE.md, GEMINI.md, etc.)
- Templates use generic placeholders; agent names only in agent-specific output files
- Manual additions preserved between `<!-- MANUAL ADDITIONS START/END -->` markers
- Feature context auto-propagates to all active agent files via `update-agent-context.sh`
- No hardcoded references to specific AI agents in core templates or commands

**Rationale**: Teams use different AI tools. The workflow should support any agent
capable of following structured prompts.

## Workflow Standards

### Command Execution Flow

The standard workflow follows this sequence:

1. `/speckit.discovery` - Transform raw notes into a Product Requirements Document (PRD)
2. `/speckit.vision` - Derive a Solution Vision from a PRD
3. `/speckit.specify` - Create feature specification from natural language
4. `/speckit.clarify` - Resolve ambiguities (max 5 questions per session)
5. `/speckit.plan` - Generate technical plan with research and contracts
6. `/speckit.tasks` - Create dependency-ordered task list by user story
7. `/speckit.analyze` - Validate cross-artifact consistency (read-only)
8. `/speckit.checklist` - Generate requirements quality checklists
9. `/speckit.implement` - Execute tasks phase by phase
10. `/speckit.taskstoissues` - Convert tasks to GitHub issues (optional)

### Artifact Structure

Each feature produces artifacts in `specs/[###-feature-name]/`:

- `spec.md` - Feature specification (from specify)
- `plan.md` - Technical implementation plan (from plan)
- `research.md` - Technical decisions and rationale (from plan Phase 0)
- `data-model.md` - Entities and relationships (from plan Phase 1)
- `contracts/` - API schemas (from plan Phase 1)
- `tasks.md` - Ordered task list (from tasks)
- `checklists/` - Quality validation checklists (from checklist)

## Quality Assurance

### Checklist Principles

Checklists validate REQUIREMENTS quality, not implementation correctness:

- Items ask: "Are requirements complete/clear/consistent/measurable?"
- Items MUST NOT ask: "Does the system do X correctly?"
- Minimum 80% of items MUST include traceability references (`[Spec §X.Y]`, `[Gap]`)
- Soft cap of 40 items per checklist; prioritize by risk/impact

### Prohibited Patterns in Checklists

- Starting items with "Verify", "Test", "Confirm" + implementation behavior
- References to code execution, user actions, system behavior
- Implementation details (frameworks, APIs, algorithms)

### Required Patterns in Checklists

- "Are [requirement type] defined/specified/documented for [scenario]?"
- "Is [vague term] quantified/clarified with specific criteria?"
- "Can [requirement] be objectively measured/verified?"

## Governance

### Authority Hierarchy

1. **Constitution** (highest): Non-negotiable principles; violations require constitution
   amendment, not artifact adjustment
2. **Templates**: Define artifact structure; MUST align with constitution
3. **Commands**: Execute workflows; MUST respect constitution and templates
4. **Artifacts**: Generated outputs; MUST comply with all above

### Amendment Procedure

1. Amendments MUST be made via `/speckit.constitution` command
2. Version increments follow semantic versioning:
   - MAJOR: Principle removal or incompatible redefinition
   - MINOR: New principle or materially expanded guidance
   - PATCH: Clarifications, wording fixes, non-semantic refinements
3. All templates MUST be validated for consistency after amendment
4. Sync Impact Report MUST document all changes

### Compliance Enforcement

- Constitution Check is mandatory before planning (Phase 0) and after design (Phase 1)
- `/speckit.analyze` flags constitution violations as CRITICAL
- Implementation MUST NOT proceed with unresolved CRITICAL issues
- Complexity violations MUST be justified in plan.md Complexity Tracking table

**Version**: 1.0.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-14
