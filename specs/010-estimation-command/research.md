# Research: raise.6.estimation Command

**Feature**: Comando raise.6.estimation
**Date**: 2026-01-21
**Branch**: 010-estimation-command

## Research Summary

This document consolidates all research decisions made during Phase 0 planning for the `raise.6.estimation` command. All NEEDS CLARIFICATION items from Technical Context have been resolved.

## Decision 1: Command Outline Structure

**Question**: What are the 11 steps needed to transform backlog → estimation roadmap?

**Research Process**:
- Analyzed Kata L1-04 (Step 6: "Realizar la estimación detallada")
- Studied template `estimation_roadmap.md` structure
- Reviewed reference command `raise.5.backlog.md` for pattern
- Mapped functional requirements (FR-001 to FR-012) to steps

**Decision**: Follow 11-step process

### Steps Breakdown

| Step | Title | Primary Action | Output |
|------|-------|---------------|--------|
| 1 | Initialize Environment | Load template, run prerequisites | Template in memory, paths confirmed |
| 2 | Load Backlog and Extract SP | Parse backlog markdown, extract Epics/Features/US with SP | Structured backlog data, total_sp |
| 3 | Instantiate Template | Fill metadata, frontmatter YAML | File created with metadata |
| 4 | Configure Team Parameters | Use defaults or parse $ARGUMENTS | team_parameters (capacity, roles, sprint duration) |
| 5 | Generate Estimation Table | Consolidate all backlog items → table | Table with ID, Elemento, SP, Notas |
| 6 | Calculate Roadmap Projection | Total SP / Capacity = Iterations | Roadmap table with N iterations |
| 7 | Identify MVP Scope | Mark MVP iterations | MVP iterations identified |
| 8 | Document Cost Model Linkage | Explain SP → hours → cost | Section 5 complete |
| 9 | Add Disclaimers and Assumptions | Document projection nature | Disclaimers added |
| 10 | Generate Summary Metrics | Calculate totals, ratios | Metrics summary |
| 11 | Finalize & Validate | Execute gate, show handoff | Gate result, handoff offered |

**Rationale**: This structure follows the RaiSE command pattern (seen in raise.5.backlog) and covers all functional requirements. Step sequence is logical: initialize → load input → configure params → calculate → validate.

**Alternatives Considered**:
- **Fewer steps (combine some)**: Rejected because each step needs independent verification and Jidoka block
- **More steps (split calculations)**: Rejected to avoid over-complexity - 11 steps is optimal balance

---

## Decision 2: Gate Validation Criteria

**Question**: What must the roadmap contain to pass validation?

**Research Process**:
- Studied template `estimation_roadmap.md` sections
- Mapped FR-010 requirements to checkable criteria
- Reviewed `gate-backlog.md` for precedent
- Identified 7 mandatory + 3 optional criteria

**Decision**: 7 Mandatory Criteria (C1-C7)

### Criteria Justification

| Criterion | Why Mandatory | Check Method |
|-----------|---------------|--------------|
| C1: Guía de Estimación | FR-007 requires documentation of Fibonacci scale + factors | Section exists with 3+ subsections |
| C2: Estimation Table | FR-003 requires consolidation of ALL items + SP | 100% backlog coverage (count rows) |
| C3: Team Parameters | FR-004 requires team config documentation | All 4 params present (capacity calc correct) |
| C4: Roadmap Projection | FR-005 requires iteration table generation | Table complete, SP math correct |
| C5: MVP Identified | FR-006 requires MVP marking | MVP iterations marked, ratio calculated |
| C6: Cost Model | FR-008 requires SP-to-cost linkage | Section 5 exists with 3+ subsections |
| C7: Metadata Complete | FR-009 requires references to prior artifacts | YAML complete, related_docs includes 4 docs |

**Rationale**: Each criterion maps directly to a functional requirement. Gate must enforce completeness before allowing handoff to `/raise.7.sow` (which depends on complete roadmap).

**Alternatives Considered**:
- **More granular criteria (15-20)**: Rejected to avoid gate complexity - 7 criteria cover essential checks
- **Optional criteria only**: Rejected because would not enforce FR-010 requirement

---

## Decision 3: Default Team Parameters

**Question**: What are reasonable defaults for team capacity?

**Research Process**:
- Reviewed SAFe capacity norms (8 SP per full-time team member)
- Studied template example (16 SP/sprint team)
- Consulted Scrum best practices (2-week sprints standard)
- Verified with PRD assumption (Asunción 4)

**Decision**: Default Team = 16 SP/sprint

### Default Configuration

```yaml
team:
  roles:
    - name: AI Architect
      dedication: 50% (0.5)
      sp_per_sprint: 4

    - name: AI Engineer
      dedication: 100% (1.0)
      sp_per_sprint: 8

    - name: AI QA
      dedication: 50% (0.5)
      sp_per_sprint: 4

  total_capacity: 16 SP/sprint

sprint:
  duration: 2 weeks (14 days)
```

**Calculation**: (0.5 × 8) + (1.0 × 8) + (0.5 × 8) = 4 + 8 + 4 = 16 SP

**Rationale**:
- **16 SP/sprint**: Aligns with SAFe for small cross-functional team (3 members, 2 full-time equivalent)
- **2-week sprints**: Scrum standard, balances planning overhead vs feedback cycles
- **Cross-functional roles**: Covers architecture, development, QA - typical AI project needs

**Alternatives Considered**:
- **Higher capacity (24-32 SP)**: Rejected as unrealistic for initial teams without measured velocity
- **1-week sprints**: Rejected as too short for planning/review cycles in estimation context
- **No defaults (always require params)**: Rejected violates usability requirement (FR-004 allows defaults)

---

## Decision 4: Handling Missing SP Estimates

**Question**: What if backlog has User Stories without estimates?

**Research Process**:
- Reviewed edge case from spec (backlog con US sin estimaciones)
- Studied preliminary estimation heuristics (complexity analysis)
- Checked template for "Pendiente" placeholder pattern
- Verified against FR-005 (must handle missing estimates gracefully)

**Decision**: Propose Preliminary Estimates + Warn User

### Estimation Strategy

| Complexity Indicator | Preliminary SP | Rationale |
|---------------------|----------------|-----------|
| Short description (<100 chars), 1-2 acceptance criteria | 1-2 SP | Small, well-defined task |
| Medium description (100-300 chars), 3-4 acceptance criteria | 3-5 SP | Standard user story |
| Long description (>300 chars), 5+ acceptance criteria | 8 SP | Large story, may need splitting |

**Documentation Format**:
```
| US-023 | [Description] | [Pendiente - Estimado preliminar: 3 SP] | Debe refinarse en planning poker | PRD 4.2 |
```

**Warning Message**:
```
⚠ WARNING: 5 User Stories have no SP estimates
→ Proposing preliminary estimates (will need refinement):
  - US-023: 3 SP (medium complexity)
  - US-031: 5 SP (medium-high complexity)
  - US-042: 2 SP (low complexity)

These estimates are approximations. Conduct planning poker session with team to refine before commitment.
```

**Rationale**: Unblocks roadmap generation while being transparent about estimate quality. Better than blocking execution or assuming 0 SP (which breaks calculations).

**Alternatives Considered**:
- **Block execution if missing**: Rejected because violates usability (FR-004 says defaults acceptable)
- **Default all to same value (e.g., 5 SP)**: Rejected as less accurate than complexity-based heuristic
- **Interactive prompting for each**: Rejected violates automation principle

---

## Decision 5: Portable Path References

**Question**: How to ensure command works in target projects?

**Research Process**:
- Studied rule 110 critical requirement (ALL paths use `.specify/`)
- Analyzed `transform-commands.sh` injection flow
- Verified existing commands (raise.5.backlog) use `.specify/`
- Confirmed .raise-kit/ doesn't exist in target projects post-injection

**Decision**: ALL Paths Use `.specify/` Prefix

### Path Mapping

| Resource Type | Path in Command | Why |
|---------------|----------------|-----|
| Template | `.specify/templates/raise/solution/estimation_roadmap.md` | Copied by transform-commands.sh from .raise-kit/ |
| Gate | `.specify/gates/raise/gate-estimation.md` | Copied by transform-commands.sh from .raise-kit/ |
| Scripts | `.specify/scripts/bash/check-prerequisites.sh` | Copied by transform-commands.sh from .raise-kit/ |
| Output | `specs/main/estimation_roadmap.md` | Standard RaiSE artifact location |

**Critical Rule**: NEVER reference `.raise-kit/` in commands - only in source repo during development.

**Rationale**: Commands are developed in raise-commons (.raise-kit/) but executed in target projects (.specify/). The injection script (`transform-commands.sh`) copies everything from .raise-kit/ to .specify/ in the target. References to .raise-kit/ would break at runtime.

**Alternatives Considered**:
- **Relative paths without prefix**: Rejected because ambiguous in different execution contexts
- **Environment variable for base path**: Rejected adds unnecessary complexity when convention works
- **Symlinks from .specify/ to .raise-kit/**: Rejected because .raise-kit/ doesn't exist in targets

---

## Technology Choices Summary

| Technology | Choice | Rationale |
|------------|--------|-----------|
| Command Format | Markdown (CommonMark) | RaiSE standard, human-readable, Git-friendly |
| Template Loading | Direct file read | Simple, no parsing library - AI reads markdown directly |
| Calculation Logic | Inline in outline steps | AI performs math (Total SP / Capacity) - no code needed |
| Gate Execution | Markdown checklist | Standard RaiSE gate pattern - AI validates against criteria |
| Parameterization | User input ($ARGUMENTS) | Allows custom team config via args, uses defaults if empty |
| SP Handling | Preliminary estimation | Proposes values for missing SP, warns user to refine |
| Path Resolution | `.specify/` prefix convention | Ensures portability after injection to target projects |

---

## Alternatives Considered & Rejected

### Alternative 1: Python Script for Calculations

**Proposal**: Create a Python script that parses backlog, calculates iterations, generates roadmap.

**Rejection Rationale**:
- Adds complexity (need Python runtime, dependencies, error handling)
- AI agent can perform simple math inline (Total SP / Capacity = iterations)
- Breaks RaiSE convention (commands are pure markdown, not code executables)
- Reduces transparency (script is black box vs inline steps)

### Alternative 2: JSON Template Instead of Markdown

**Proposal**: Use JSON template for structured data, generate markdown from JSON.

**Rejection Rationale**:
- Breaks RaiSE convention - ALL templates are Markdown for human readability
- JSON is harder for humans to review/edit (PRD, Vision, Tech Design all markdown)
- Adds parsing complexity (need JSON parser, validation)
- Platform agnosticism principle violated (JSON less universally editable than markdown)

### Alternative 3: Separate Config File for Team Parameters

**Proposal**: Store team parameters in `.specify/config/team-parameters.json`.

**Rejection Rationale**:
- Premature optimization - defaults cover 80% of use cases
- $ARGUMENTS handles custom 20% without extra file
- Config file needs creation workflow, validation, precedence rules
- Violates simplicity principle (§7 Lean: eliminar desperdicio)

### Alternative 4: Interactive Prompts for Parameters

**Proposal**: Prompt user for team structure, capacity, sprint duration during execution.

**Rejection Rationale**:
- Violates automation principle - command should run unattended if defaults acceptable
- Breaks CI/CD integration (can't prompt in automated pipelines)
- Increases execution time vs instant defaults
- Use case covered by $ARGUMENTS (user provides params if needed)

### Alternative 5: Modify Template During Execution

**Proposal**: Edit `estimation_roadmap.md` template to add project-specific sections.

**Rejection Rationale**:
- Violates Restricción 5 (must use template as-is)
- Template modification breaks updates from src/ (conflicts)
- Violates §2 Governance as Code (templates are governance artifacts)
- Correct approach: instantiate template → populate with data

---

## Research Validation

All NEEDS CLARIFICATION items from Technical Context have been resolved:

✅ **Language/Version**: Markdown (CommonMark) + Bash - confirmed
✅ **Primary Dependencies**: Template, gate, scripts - all identified with paths
✅ **Storage**: Git repo (specs/main/) - confirmed
✅ **Testing**: Manual validation via gate - method defined
✅ **Target Platform**: RaiSE Framework - confirmed
✅ **Project Type**: Single command file - confirmed
✅ **Performance Goals**: <10 min execution - validated as feasible
✅ **Constraints**: .specify/ paths, Spanish content, rule 110 structure, gate execution - all confirmed
✅ **Scale/Scope**: ~200-300 lines command + ~50 lines gate - realistic estimate

**Phase 0 Complete**: All research questions answered. Ready for Phase 1 (Design & Contracts).
