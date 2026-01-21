# Quickstart: raise.5.backlog Command

**Feature**: `009-backlog-command`
**Command**: `/raise.5.backlog`
**Purpose**: Generate a project backlog from an approved Tech Design

## What This Command Does

The `/raise.5.backlog` command transforms a Tech Design document into a structured backlog containing:

- **Epics**: Major capabilities or modules (3-7 per project)
- **Features**: Independently valuable functionalities (2-5 per Epic)
- **User Stories**: Specific work items in "Como/Quiero/Para" format (3-8 per Feature)
- **BDD Criteria**: Acceptance criteria in Given/When/Then format (2-3 per Story)
- **Story Point Estimates**: Fibonacci-scale effort estimates
- **MVP Identification**: Minimum viable product subset (≤50% of total effort)

**Output**: `specs/main/project_backlog.md`

## Prerequisites

Before running this command, ensure:

1. **Tech Design exists**: `specs/main/tech_design.md` must be present and approved
   - If missing: Run `/raise.4.tech-design` first
   - Tech Design should have passed `gate-design.md`

2. **Tech Design is complete**: Must contain these sections:
   - Componentes y Arquitectura
   - MVP Scope
   - Requisitos Funcionales

3. **Reference documents available**:
   - `specs/main/project_requirements.md` (PRD)
   - `specs/main/solution_vision.md`

4. **Template and gate setup**:
   - Template: `.specify/templates/raise/backlog/project_backlog.md`
   - Gate: `.specify/gates/raise/gate-backlog.md`
   - (Automatically available after `transform-commands.sh` injection)

## How to Run

### Basic Execution

```bash
/raise.5.backlog
```

The command runs with no arguments. It automatically:
1. Loads Tech Design from `specs/main/tech_design.md`
2. Analyzes components and functionality
3. Guides you through backlog generation
4. Validates output with `gate-backlog.md`
5. Offers handoff to `/raise.6.estimation`

### Expected Interaction

The command is **guided, not fully automated**. You'll be involved in:

**Prioritization (Step 6)**:
- The command proposes Feature priorities based on MVP scope from Tech Design
- Review and adjust priorities (Alta/Media/Baja) based on business value

**Estimation (Step 10)**:
- The command proposes Story Point estimates based on Tech Design complexity
- Review and adjust estimates (1, 2, 3, 5, 8, 13) based on team capacity

**MVP Definition (Step 11)**:
- The command proposes MVP scope based on Tech Design
- Confirm or adjust which Features/Stories are must-have vs nice-to-have

**Estimated Time**: 45-60 minutes for typical project (5-6 Epics, 20-30 Features, 100-150 User Stories)

## Output Structure

After successful execution, `specs/main/project_backlog.md` will contain:

```markdown
---
document_id: "BCK-[PROJECT]-001"
title: "Backlog de Proyecto: [Nombre]"
version: "1.0"
related_docs: ["PRD-...", "VIS-...", "TECH-..."]
status: "Draft"
---

## 1. Descripción General
[Purpose and context]

## 2. Estructura del Backlog
[Hierarchy: Epics → Features → User Stories]

## 3. Epics
| ID | Título | Descripción | Prioridad | Est. (SP) | Estado |
|----|--------|-------------|-----------|-----------|--------|
| EPIC-001 | ... | ... | Alta | 120 | Por Iniciar |

## 4. Features
### Epic: EPIC-001
| ID | Título | Descripción | Criterios | Prioridad | Est. (SP) |
|----|--------|-------------|-----------|-----------|-----------|
| FEAT-001 | ... | ... | ... | Alta | 45 |

## 5. Historias de Usuario
### Feature: FEAT-001
| ID | Historia | Criterios (BDD) | Est. (SP) | Dependencias |
|----|----------|-----------------|-----------|--------------|
| US-001 | Como [rol]... | Dado...Cuando...Entonces | 5 | - |

## 6-9. [Additional sections: Technical Tasks, Estimates Summary, Dependencies, etc.]
```

## Validation

The command automatically runs `gate-backlog.md` validation, which checks:

**7 Mandatory Criteria** (must all pass):
1. ✓ 3-7 Features with clear names and value
2. ✓ Features prioritized with justification
3. ✓ MVP identified (≤50% of total Story Points)
4. ✓ All User Stories follow "Como/Quiero/Para" format
5. ✓ Each User Story has ≥2 BDD scenarios
6. ✓ All User Stories have Story Point estimates
7. ✓ Product Owner approval noted (or scheduled)

**If Gate Fails**:
- Command shows which criteria failed
- Suggests specific corrections
- You can iterate to fix issues before proceeding

**If Gate Passes**:
- Command shows summary (# Epics, # Features, # US, Total SP, MVP SP)
- Offers handoff: "→ Siguiente paso: `/raise.6.estimation`"

## Next Steps

After successful backlog generation:

1. **Review with Product Owner**:
   - Validate priorities
   - Confirm MVP scope
   - Adjust estimates based on team feedback

2. **Planning Poker Session** (recommended):
   - Review Story Point estimates with full team
   - Calibrate estimates using team velocity

3. **Run Estimation Command**:
   ```bash
   /raise.6.estimation
   ```
   - Generates Estimation Roadmap with timeline and sprints
   - Uses backlog Story Points to project delivery dates

## Common Issues

### Issue: "Tech Design not found"
**Cause**: `specs/main/tech_design.md` doesn't exist
**Solution**: Run `/raise.4.tech-design` first to create Tech Design

### Issue: "Tech Design incomplete - missing sections"
**Cause**: Tech Design lacks required sections (components, architecture, MVP)
**Solution**: Complete missing sections in Tech Design, or re-run `/raise.4.tech-design`

### Issue: "MVP > 50% of total"
**Cause**: Too many Features marked as MVP (must-have)
**Solution**: Review MVP Features and apply "What can I defer and still deliver value?" iteratively

### Issue: "User Stories too large (>8 SP)"
**Cause**: Stories are not broken down enough
**Solution**: Apply INVEST splitting techniques - split by scenario, data, or workflow

### Issue: "Gate criterion failed: BDD scenarios missing"
**Cause**: Some User Stories lack "Dado/Cuando/Entonces" criteria
**Solution**: Add at least 2 BDD scenarios per User Story (happy path + validation/edge case)

## Tips for Best Results

1. **Have Tech Design approved** before running backlog command
   - Quality in = quality out
   - Incomplete Tech Design → incomplete backlog

2. **Schedule 60-90 minutes** for initial generation
   - Don't rush prioritization and estimation
   - These decisions impact entire project

3. **Involve Product Owner** in prioritization decisions
   - They understand business value best
   - Their buy-in is critical (gate criterion 7)

4. **Start with defaults, refine later**
   - Command proposes reasonable defaults
   - Fine-tune estimates with team in planning poker

5. **Keep Stories small**
   - Target: 1-5 days of work per Story
   - If Story > 8 SP, split it further

6. **Mark MVP conservatively**
   - MVP should be the *minimum* to validate hypothesis
   - Defer nice-to-haves to post-MVP

## Examples

### Example 1: Clean Execution

```bash
$ /raise.5.backlog

[Command loads Tech Design...]
[Command identifies 5 Epics from components...]
[Command decomposes into 24 Features...]
[Command creates 120 User Stories with BDD criteria...]
[Command proposes estimates: Total 480 SP, MVP 210 SP (44%)...]
[Gate validation: ALL PASS ✓]

Summary:
- 5 Epics
- 24 Features (18 MVP, 6 Post-MVP)
- 120 User Stories (65 MVP, 55 Post-MVP)
- Total: 480 SP
- MVP: 210 SP (44%)

Backlog saved to: specs/main/project_backlog.md

→ Siguiente paso: /raise.6.estimation
```

### Example 2: Iteration on Gate Failure

```bash
$ /raise.5.backlog

[Command generates backlog...]
[Gate validation: FAIL ✗]

Gate failures:
- Criterion 3: MVP is 285 SP / 480 SP = 59% (exceeds 50% limit)
- Criterion 5: 12 User Stories missing BDD scenarios

Suggested corrections:
- MVP too large: Defer Features FEAT-018, FEAT-022 to post-MVP
- Missing BDD: Add scenarios to US-045, US-056, US-078, ...

[Fix issues in specs/main/project_backlog.md]
[Re-run gate manually or via command]
```

## Related Commands

- **Prerequisite**: `/raise.4.tech-design` - Create Tech Design
- **Next Step**: `/raise.6.estimation` - Create Estimation Roadmap
- **Parallel**: `/raise.1.analyze` - Analyze brownfield codebase (if needed)

## Architecture Notes

This command is a **Markdown orchestration file**, not traditional code. It:
- Lives in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- Uses RaiSE Kit command pattern (frontmatter, outline, guidelines, AI guidance)
- References template via `.specify/templates/raise/backlog/project_backlog.md`
- Executes gate via `.specify/gates/raise/gate-backlog.md`
- Follows kata `flujo-05-backlog-creation` (10 steps)

**For Implementation Details**: See `specs/009-backlog-command/plan.md`

---

**Status**: Ready for use after implementation in branch `009-backlog-command`
