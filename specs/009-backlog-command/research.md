# Research: Comando raise.5.backlog

**Feature**: `009-backlog-command`
**Date**: 2026-01-21
**Purpose**: Research findings for implementing the raise.5.backlog command

## Overview

This document consolidates research findings from Phase 0 of the implementation plan. All "NEEDS CLARIFICATION" items from Technical Context have been resolved through analysis of existing artifacts.

## Research Areas

### 1. Kata Structure Analysis

**Question**: How do the 10 steps of `flujo-05-backlog-creation` map to command structure?

**Source Analyzed**: `src/katas-v2.1/flujo/05-backlog-creation.md`

**Key Findings**:
- Kata provides 10 well-defined steps from loading Tech Design to Product Owner validation
- Each step has clear inputs, outputs, and verification criteria
- Steps follow logical progression: Identify → Prioritize → Decompose → Estimate → Validate
- Kata includes Jidoka blocks for each step with stop conditions

**Decision**: Command will implement 12 steps:
1. Initialize Environment (RaiSE Kit standard)
2-11. Kata steps 1-10 (core workflow)
12. Finalize & Validate (RaiSE Kit standard)

**Rationale**: Kata steps are solid. RaiSE Kit pattern requires wrapping with init/finalize for consistency with other commands.

---

### 2. Template Structure Analysis

**Question**: What sections exist in the backlog template and how should they be populated?

**Source Analyzed**: `src/templates/backlog/project_backlog.md`

**Key Findings**:
- Template has 11 numbered sections
- Sections 1-9 are core backlog content (Epics, Features, US, Estimates)
- Section 10 (Vinculación con Roadmap) is optional and overlaps with `raise.6.estimation` scope
- Section 11 (Notas Adicionales) is catch-all for assumptions

**Decision**: Command MVP focuses on sections 1-9. Section 10 deferred to estimation command. Section 11 populated with any assumptions made during generation.

**Rationale**: Clear separation of concerns. Backlog defines WHAT, Estimation command defines WHEN. Avoids duplication.

---

### 3. Gate Criteria Analysis

**Question**: What validation criteria must the command satisfy?

**Source Analyzed**: `src/gates/gate-backlog.md`

**Key Findings**:

**7 Mandatory Criteria** (MUST PASS):
1. 3-7 features con nombre y valor claro
2. Features priorizadas con justificación
3. MVP identificado (subset ≤50% del total)
4. US formato correcto ("Como/Quiero/Para")
5. Cada US tiene ≥2 escenarios BDD (Dado/Cuando/Entonces)
6. Todas US estimadas en Story Points
7. Product Owner approval (or documented for later approval)

**3 Recommended Criteria** (SHOULD PASS):
8. INVEST compliance (Independent, Negotiable, Valuable, Estimable, Small, Testable)
9. US conectadas a Tech Design (technical details section)
10. Dependencias sin ciclos (DAG validation)

**Decision**: Command design ensures all 7 mandatory criteria are met by construction. Verification blocks in each step map directly to gate criteria.

**Rationale**: Gate is the acceptance test. Command must be designed to pass it. Recommended criteria are quality enhancers but not blockers.

**Mapping**:
- Criterion 1 → Step 4 (Identificar Epics) + Step 5 (Descomponer en Features)
- Criterion 2 → Step 6 (Priorizar Features)
- Criterion 3 → Step 11 (Identificar MVP Slice)
- Criterion 4 → Step 7 (Descomponer en User Stories)
- Criterion 5 → Step 8 (Escribir Criterios BDD)
- Criterion 6 → Step 10 (Estimar User Stories)
- Criterion 7 → Step 12 (Finalize - includes Product Owner validation note)

---

### 4. Reference Command Pattern Analysis

**Question**: What is the standard structure for RaiSE Kit commands?

**Sources Analyzed**:
- `.raise-kit/commands/02-projects/raise.4.tech-design.md`
- `.raise-kit/commands/02-projects/raise.1.discovery.md`
- `.raise-kit/commands/02-projects/raise.2.vision.md`
- `.agent/rules/110-raise-kit-command-creation.md`

**Key Findings**:

**Standard Structure** (6 sections):
1. **Frontmatter YAML** - `description` (1 line) + `handoffs` (array)
2. **User Input** - `$ARGUMENTS` placeholder with instruction
3. **Outline** - Goal statement + numbered steps (each with: title, actions, verification, jidoka block)
4. **Notes** (optional) - Scenario-specific guidance (brownfield, greenfield, etc.)
5. **High-Signaling Guidelines** - 4 bullet points: Output, Focus, Language, Jidoka
6. **AI Guidance** - 5 numbered points: Role, Be proactive, Follow Katas, Traceability, Gates

**Critical Conventions**:
- All file references use `.specify/` not `.raise-kit/` (for portability after injection)
- Step 1 always "Initialize Environment" running `check-prerequisites.sh --json --paths-only`
- Last step always "Finalize & Validate" running gate + `update-agent-context.sh` + handoff display
- Jidoka blocks use format: `> **Si no puedes continuar**: [condition] → **JIDOKA**: [corrective action]`
- Content in Spanish, instructions in English (bilingual convention)

**Decision**: Follow this structure exactly for raise.5.backlog command.

**Rationale**: Proven pattern used by 3 existing commands. Consistency reduces cognitive load for users and maintainers.

---

### 5. Handoff Chain Analysis

**Question**: What command should be offered as next step after backlog?

**Sources Analyzed**:
- PRD section 4.1 (Requisito 2.5: handoff a raise.6.estimation)
- Vision doc (flow diagram showing command sequence)
- Kata prerequisites (raise.5 is prerequisite for raise.6)

**Key Findings**:

**Estimation Flow**:
```
raise.1.discovery → raise.2.vision → raise.4.tech-design → raise.5.backlog → raise.6.estimation → raise.7.sow
```

Current position: raise.5.backlog
Next command: raise.6.estimation

**Decision**: Handoff target is `raise.6.estimation` with prompt: "Generate estimation roadmap and timeline from this backlog"

**Rationale**: Linear flow. Backlog provides Story Points, which are input for estimation roadmap (velocity calculation, sprint planning, timeline projection).

---

## Technology Decisions

### Command File Format
**Decision**: Markdown with YAML frontmatter
**Rationale**: Standard for RaiSE Kit commands. Platform-agnostic, Git-friendly, human-readable.

### Execution Environment
**Decision**: Claude Code CLI (primary), compatible with Cursor/Windsurf
**Rationale**: Command is pure Markdown, works with any agent that can read Markdown files.

### Dependencies
**Decision**: Reuse all existing artifacts (template, gate, kata, scripts)
**Rationale**: No new dependencies. Zero waste. Leverages existing governance artifacts.

### Validation Approach
**Decision**: Manual execution testing against gate criteria
**Rationale**: No unit testing framework for Markdown command files. Human-in-the-loop validation is appropriate for orchestration commands.

---

## Risk Analysis

### Risk 1: Tech Design Quality Variability
**Description**: If Tech Design input is incomplete or ambiguous, backlog quality suffers.

**Mitigation**:
- Step 2 includes explicit checks for required sections (components, architecture, MVP scope)
- Jidoka block stops execution and lists missing sections
- Command suggests running `/raise.4.tech-design` to complete missing sections

**Residual Risk**: Low - Gate-Design (prerequisite) should catch incomplete Tech Designs before they reach this command.

### Risk 2: Prioritization Subjectivity
**Description**: Prioritization (Step 6) is inherently subjective and may not reflect true business value.

**Mitigation**:
- Command provides prioritization matrix framework (Value/Complexity score)
- Proposes defaults based on MVP scope identification from Tech Design
- Signals that priorities must be validated with Product Owner
- Gate includes "Product Owner approval" criterion

**Residual Risk**: Medium - This is inherent to prioritization. Command can guide but not eliminate subjectivity.

### Risk 3: Estimation Accuracy
**Description**: Initial Story Point estimates may be incorrect without full team participation.

**Mitigation**:
- Command proposes estimates based on Tech Design complexity analysis
- Explicitly documents that estimates are preliminary
- Recommends planning poker session with full team for refinement
- Gate checks that all stories are estimated, not that estimates are "correct"

**Residual Risk**: Medium - Accuracy improves with team calibration over time. Initial estimates are starting point.

### Risk 4: MVP Scope Inflation
**Description**: MVP slice may exceed 50% of total effort, defeating "minimum" purpose.

**Mitigation**:
- Step 11 applies explicit check: MVP ≤50% of total Story Points
- Jidoka block suggests iterative removal: "What can I defer and still deliver value?"
- Gate criterion 3 enforces this limit

**Residual Risk**: Low - Explicit validation prevents scope creep.

---

## Alternative Approaches Considered

### Alternative 1: Interactive Prompts for Prioritization
**Approach**: Command could pause and prompt user interactively for each Feature priority.

**Rejected Because**:
- Violates SC-001 (completion in <60 minutes)
- Breaks command flow
- Not feasible in all execution environments (batch mode, CI/CD)

**Chosen Instead**: Propose defaults based on Tech Design analysis, signal for later validation.

### Alternative 2: Automatic Epic Identification via NLP
**Approach**: Use AI to cluster Tech Design components into Epics automatically.

**Rejected Because**:
- Over-engineering for MVP
- Epic grouping requires business domain knowledge, not just text similarity
- Human judgment is necessary for meaningful Epic boundaries

**Chosen Instead**: Guide user through Epic identification with heuristics (3-7 Epics, map to components/modules).

### Alternative 3: Skip MVP Identification
**Approach**: Generate full backlog without MVP slice, let user mark it manually later.

**Rejected Because**:
- MVP identification is gate criterion 3 (mandatory)
- Critical for downstream estimation roadmap (MVP = Phase 1 target)
- Missing MVP makes backlog less actionable

**Chosen Instead**: Include MVP identification as Step 11 with clear criteria (≤50%, core value).

---

## Best Practices Identified

From analysis of existing commands and katas:

1. **Observable Verification**: Every step must have concrete, testable verification criterion.
   - Good: "All Features have priority (Alta/Media/Baja) with justification"
   - Bad: "Features are prioritized appropriately"

2. **Actionable Jidoka**: Stop conditions must include corrective action, not just error message.
   - Good: "Tech Design missing → **JIDOKA**: Execute `/raise.4.tech-design` first"
   - Bad: "Tech Design missing → Cannot continue"

3. **Reference Portability**: Use `.specify/` in all paths, never `.raise-kit/`.
   - Reason: Commands are injected to target projects via `transform-commands.sh`

4. **Bilingual Convention**: Instructions in English, generated content in Spanish.
   - Reason: RaiSE standard for all commands in 02-projects category

5. **Step Title Format**: Use infinitive verb + object.
   - Good: "Cargar Tech Design y Contexto"
   - Bad: "Loading the Tech Design"

---

## Open Questions Resolved

All open questions from spec have been resolved:

**Q1: ¿Iteración o generación única?**
- **Resolved**: Generación única completa. Si archivo existe, preguntar si sobrescribir.
- **Source**: Decision D3 in plan.md

**Q2: ¿Cómo determinar roles en User Stories?**
- **Resolved**: Inferir desde PRD (sección stakeholders) o usar roles genéricos (Usuario, Administrador, Sistema) y señalar para refinamiento.
- **Source**: Step 7 design in plan.md

**Q3: ¿Interactuar o proponer defaults?**
- **Resolved**: Proponer defaults razonables, señalar validación con equipo. Mantiene flujo ágil.
- **Source**: Decision D3 in plan.md, Steps 6 and 10 design

---

## References

- Kata: `src/katas-v2.1/flujo/05-backlog-creation.md`
- Template: `src/templates/backlog/project_backlog.md`
- Gate: `src/gates/gate-backlog.md`
- Reference Command: `.raise-kit/commands/02-projects/raise.4.tech-design.md`
- Pattern Documentation: `.agent/rules/110-raise-kit-command-creation.md`
- PRD: `specs/main/prd-estimation-commands.md`
- Vision: `specs/main/vision-estimation-commands.md`

---

**Research Status**: COMPLETE - All NEEDS CLARIFICATION items resolved. Ready for implementation.
