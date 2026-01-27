# Quickstart: raise.6.estimation Command

**Command**: `/raise.6.estimation`
**Purpose**: Generate Estimation Roadmap with Story Point projections and sprint timeline
**Input**: Project Backlog (`specs/main/project_backlog.md`)
**Output**: Estimation Roadmap (`specs/main/estimation_roadmap.md`)

---

## Prerequisites

Before running this command, ensure:

- ✅ **Project Backlog exists**: `specs/main/project_backlog.md`
- ✅ **Backlog has SP estimates**: User Stories have Story Point values (or marked as "Pendiente")
- ✅ **Command injected**: `.raise-kit/` files copied to `.specify/` via `transform-commands.sh`
- ✅ **Previous steps complete**: `/raise.1.discovery`, `/raise.2.vision`, `/raise.4.tech-design`, `/raise.5.backlog`

---

## Basic Usage

### Scenario 1: Use Default Team Parameters

**Command**:
```bash
/raise.6.estimation
```

**What Happens**:
1. Loads backlog from `specs/main/project_backlog.md`
2. Uses default team structure:
   - 1 AI Architect (50% dedication) = 4 SP/sprint
   - 1 AI Engineer (100% dedication) = 8 SP/sprint
   - 1 AI QA (50% dedication) = 4 SP/sprint
   - **Total capacity: 16 SP/sprint**
   - Sprint duration: 2 weeks
3. Calculates iterations: Total SP / 16 = N sprints
4. Generates `specs/main/estimation_roadmap.md`
5. Executes validation gate
6. Offers handoff to `/raise.7.sow` if gate passes

**Example Output**:
```
✅ Backlog loaded: 52 User Stories, 163 Total SP
✅ Team configured: 16 SP/sprint (default structure)
✅ Roadmap calculated: 11 sprints (22 weeks)
✅ MVP identified: Iterations 1-5 (78 SP, 48% of total)
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: 163 SP
- MVP Story Points: 78 SP (48% of total)
- Iterations Needed: 11 sprints (22 weeks with 2-week sprints)
- Team Capacity: 16 SP/sprint
- Backlog Coverage: 100% (52/52 User Stories)

→ Siguiente paso: /raise.7.sow - Generate Statement of Work from this roadmap
```

---

### Scenario 2: Custom Team Parameters

**Command**:
```bash
/raise.6.estimation "2 engineers full-time, 1 QA 50%, sprints 1 week"
```

**What Happens**:
1. Parses custom team structure:
   - 2 AI Engineers (100% each) = 16 SP/sprint
   - 1 AI QA (50% dedication) = 4 SP/sprint
   - **Total capacity: 20 SP/sprint**
   - Sprint duration: 1 week
2. Calculates iterations: 163 SP / 20 = 9 sprints (rounded up)
3. Generates roadmap with custom parameters documented
4. Rest is same as Scenario 1

**Example Output**:
```
✅ Team configured: 20 SP/sprint (custom: 2 engineers full-time, 1 QA 50%)
✅ Roadmap calculated: 9 sprints (9 weeks with 1-week sprints)
```

---

## Expected Output File

**File Created**: `specs/main/estimation_roadmap.md`

### Structure

```markdown
---
document_id: "EST-[PROJECT]-001"
title: "Estimación de Proyecto y Roadmap: [Project Name]"
project_name: "[Project Name]"
related_docs:
  - "PRD-[PROJECT]-001"
  - "VIS-[PROJECT]-001"
  - "TEC-[PROJECT]-001"
  - "BCK-[PROJECT]-001"
---

# Estimación de Proyecto y Roadmap: [Project Name]

## 1. Guía de Estimación en Puntos de Historia

- Escala Fibonacci modificada: 1, 2, 3, 5, 8, 13, 20, 40, 100
- Factores a considerar: complejidad, esfuerzo, incertidumbre
- Proceso de planning poker

## 2. Estimación del Backlog

| ID | Elemento | Estimación (SP) | Notas | Referencia |
|----|----------|-----------------|-------|------------|
| EPIC-001 | [Epic name] | - | [Epic description] | PRD 1.1 |
| FEAT-001 | [Feature name] | - | [Feature description] | PRD 2.1 |
| US-001 | [User Story] | 3 | [Notes] | PRD 2.1.1 |
| ... | ... | ... | ... | ... |
| **TOTAL** | | **163 SP** | | |

## 3. Parámetros para el Roadmap

- **Duración del Sprint/Iteración:** 2 semanas
- **Estructura del Equipo:**
  - 1 AI Architect (50%)
  - 1 AI Engineer (100%)
  - 1 AI QA (50%)
- **Capacidad Estimada Inicial:** 16 SP/sprint
  - Cálculo: (0.5 * 8) + (1.0 * 8) + (0.5 * 8) = 16 SP
- **Nota sobre Velocidad:** Este es un valor estimado inicial. La capacidad real se determinará midiendo el trabajo completado en la primera iteración.

## 4. Roadmap Proyectado

**Total SP Estimados:** 163 SP
**Capacidad Estimada:** 16 SP/sprint
**Número Estimado de Iteraciones:** 11 sprints (22 weeks)

| Iteración | Fechas | Objetivo | Elementos Planeados | SP Estimados | SP Acumulados | Notas |
|-----------|--------|----------|---------------------|--------------|---------------|-------|
| 1 (MVP) | Semana 1-2 | Establecer bases | EPIC-001, FEAT-001, US-001 a US-008 | 16 SP | 16 SP | Core features |
| 2 (MVP) | Semana 3-4 | Funcionalidad principal | FEAT-002, US-009 a US-015 | 14 SP | 30 SP | |
| ... | ... | ... | ... | ... | ... | ... |
| 11 | Semana 21-22 | Refinamientos finales | FEAT-008, US-048 a US-052 | 11 SP | 163 SP | |

**Descargo:** Este roadmap es una proyección inicial. El alcance real puede variar. Se revisará después de cada iteración basándose en velocidad medida.

## 5. Vinculación con Modelo de Costos

- **Relación Esfuerzo-Costo:** 1 SP ≈ 4-6 horas de trabajo
- **Costo Total Estimado:** [Total SP * factor conversión * tasa promedio]
- **Impacto de Cambios:** Cambios en el roadmap impactarán costo y calendario
- **Supuestos de Costo:** Composición del equipo, tarifas definidas
```

---

## Validation

The command executes a validation gate at step 11:

**Gate Checks (7 Mandatory Criteria)**:
1. ✅ Guía de Estimación completa (Fibonacci scale, factors, process)
2. ✅ Estimation table with ALL backlog items (100% coverage)
3. ✅ Team parameters documented (capacity, sprint duration)
4. ✅ Roadmap projection table complete (iterations, dates, SP)
5. ✅ MVP clearly identified (marked iterations, ratio calculated)
6. ✅ Cost model section present (SP-to-cost linkage)
7. ✅ Metadata and references complete (YAML, related_docs)

**Gate Pass Output**:
```
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: 163 SP
- MVP Story Points: 78 SP (48% of total)
- Iterations Needed: 11 sprints (22 weeks)
- Team Capacity: 16 SP/sprint
- Backlog Coverage: 100% (52/52 User Stories)
- Cost Model: Documented

→ Siguiente paso: /raise.7.sow - Generate Statement of Work from this roadmap
```

---

## Next Step

After roadmap is generated and validated, proceed to create the Statement of Work:

```bash
/raise.7.sow
```

This command will use the estimation roadmap to generate the commercial proposal document with pricing, timeline, deliverables, and terms.

---

## Troubleshooting

### Error: "Backlog not found"

**Symptom**:
```
🛑 JIDOKA: specs/main/project_backlog.md not found
→ Execute /raise.5.backlog first to generate the backlog
```

**Fix**: Run `/raise.5.backlog` before the estimation command.

**Root Cause**: The estimation command depends on a complete project backlog. Without it, there's no input data to process.

---

### Warning: "Missing SP estimates"

**Symptom**:
```
⚠ WARNING: 5 User Stories have no SP estimates
→ Proposing preliminary estimates (will need refinement):
  - US-023: 3 SP (medium complexity based on description length)
  - US-031: 5 SP (medium-high complexity based on acceptance criteria count)
  - US-042: 2 SP (low complexity)
  - US-045: 8 SP (high complexity - may need splitting)
  - US-048: 3 SP (medium complexity)

These estimates are approximations. Conduct planning poker session with team to refine before commitment.
```

**Fix**: Accept preliminary estimates for now. The roadmap will note these need refinement.

**Root Cause**: Backlog was generated but some User Stories don't have Story Point estimates yet. This is normal - estimation is often iterative.

**Recommendation**: After roadmap generation, schedule planning poker session with team to validate/refine all estimates before execution phase.

---

### Alert: "Project too long"

**Symptom**:
```
⚠ ALERT: Roadmap projects 28 sprints (56 weeks with 2-week sprints)
→ Consider reviewing MVP scope to reduce initial size
→ Target: MVP ≤ 10 sprints (20 weeks) for faster feedback and value delivery
```

**Fix**: Review backlog and move non-MVP Features to Phase 2 or later releases.

**Root Cause**: The total Story Points (or MVP scope) is very large. Projects >6 months have higher risk of requirements drift and delayed feedback.

**Recommendation**:
1. Review which Features are truly "minimum viable" - can some be deferred?
2. Consider splitting project into phases (MVP → Enhancement 1 → Enhancement 2)
3. Re-run `/raise.5.backlog` with reduced MVP scope, then re-run `/raise.6.estimation`

---

### Alert: "Capacity too low"

**Symptom**:
```
⚠ ALERT: Team capacity is 6 SP/sprint
→ With this capacity, project would take 27 sprints (54 weeks)
→ Suggest: Increase team size OR reduce scope OR accept extended timeline
```

**Fix**: Choose one:
- **Option A**: Increase team capacity (add resources)
  ```bash
  /raise.6.estimation "2 engineers full-time, 1 architect 50%, 1 QA 50%"
  ```
- **Option B**: Reduce scope (revisit backlog MVP)
- **Option C**: Accept longer timeline (document in roadmap)

**Root Cause**: Team capacity (SP/sprint) is below recommended minimum for reasonable project duration.

---

### Gate Failure: "Incomplete roadmap"

**Symptom**:
```
❌ Gate FAILED - 2 criteria not met:

C2: Estimation Table Complete
  - Issue: Table only has 45 rows but backlog has 52 User Stories (87% coverage)
  - Fix: Add missing 7 User Stories to table: US-023, US-031, US-038, US-042, US-049, US-051, US-052

C5: MVP Clearly Identified
  - Issue: No MVP marking found in roadmap table
  - Fix: Add "MVP" label to iterations 1-5 that contain MVP Features

🛑 JIDOKA: Fix these issues before continuing. Do not offer handoff to /raise.7.sow until gate passes.
```

**Fix**: The command will automatically iterate and fix issues. If manual intervention needed:
1. Review gate failure details
2. Update `specs/main/estimation_roadmap.md` manually if needed
3. Re-run command or continue with corrected roadmap

**Root Cause**: Command logic missed some backlog items or failed to mark MVP iterations. This is a bug - report if reproducible.

---

## Integration with Estimation Flow

```text
Estimation Kata L1-04 Flow:

Step 1: PRD           → /raise.1.discovery  ✅
Step 3: Vision        → /raise.2.vision     ✅
Step 4: Tech Design   → /raise.4.tech-design ✅
Step 5: Backlog       → /raise.5.backlog    ✅
Step 6: Estimation    → /raise.6.estimation ← YOU ARE HERE
Step 7: SoW           → /raise.7.sow        ⏭ Next
```

This command implements **Step 6** of Kata L1-04 (Proceso de Estimación de Requerimientos a Propuesta).

---

## Command Parameters Reference

### $ARGUMENTS Format (Optional)

**Syntax**: Natural language team structure description

**Examples**:
```bash
# Example 1: Default (no args)
/raise.6.estimation

# Example 2: Larger team
/raise.6.estimation "3 engineers full-time, 2 QA 50%, sprints 2 weeks"

# Example 3: Shorter sprints
/raise.6.estimation "1 architect 100%, 2 engineers 100%, 1 QA 50%, sprints 1 week"

# Example 4: Part-time team
/raise.6.estimation "1 engineer 50%, 1 QA 25%, sprints 2 weeks"
```

**Parsing Rules**:
- Roles: "architect", "engineer", "QA" (case-insensitive)
- Dedication: "full-time" = 100%, "50%" = 50%, "25%" = 25%, etc.
- Sprint: "sprints N week(s)" or "sprints N semana(s)"

**Capacity Calculation**:
- Each role: dedication × 8 SP baseline
- Total capacity = sum of all roles

---

## FAQs

**Q: Can I edit the roadmap after generation?**
A: Yes, `specs/main/estimation_roadmap.md` is a markdown file. You can manually edit any section. Just re-run the gate to validate your changes.

**Q: What if my team uses hours instead of Story Points?**
A: The command generates Story Point-based roadmap. You can add hour conversions manually in Section 5 (Vinculación con Modelo de Costos). Example: "1 SP ≈ 4-6 hours" → "163 SP ≈ 652-978 hours".

**Q: Can I re-run the command with different team parameters?**
A: Yes. The command overwrites `specs/main/estimation_roadmap.md`, so you can experiment with different capacities. Save previous versions if needed (`cp estimation_roadmap.md estimation_roadmap_v1.md`).

**Q: Does the command account for holidays, vacations, or interruptions?**
A: No. The roadmap assumes continuous sprints with constant velocity. Add buffer manually (e.g., "11 sprints ≈ 14 weeks accounting for interruptions").

**Q: What if my backlog changes after generating the roadmap?**
A: Re-run `/raise.5.backlog` to update the backlog, then re-run `/raise.6.estimation` to regenerate the roadmap with new data.

---

## Tips & Best Practices

1. **Start with defaults**: Use default team parameters first, then customize if needed
2. **Validate estimates**: Schedule planning poker session after roadmap generation to refine preliminary SP
3. **Track velocity**: After first sprint, measure actual velocity and update capacity parameter
4. **MVP discipline**: Keep MVP ≤ 50% of total SP for faster feedback
5. **Buffer for unknowns**: Add 20% buffer to timeline for unexpected complexity
6. **Iterate**: Roadmap is a living document - update after each sprint based on actual progress

---

**For more details**: See `specs/010-estimation-command/plan.md` (implementation plan) and `.raise-kit/commands/02-projects/raise.6.estimation.md` (command source).
