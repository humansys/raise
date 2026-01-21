# Gate Estimation - Validation Criteria

**Gate**: gate-estimation.md
**Purpose**: Validate Estimation Roadmap completeness and quality
**Location**: `.raise-kit/gates/raise/gate-estimation.md` (source) → `.specify/gates/raise/gate-estimation.md` (runtime)
**Executed by**: raise.6.estimation command at Step 11 (Finalize & Validate)

---

## Purpose

Validate that the generated Estimation Roadmap (`specs/main/estimation_roadmap.md`) is:
- **Complete**: Contains all required sections with correct structure
- **Accurate**: SP calculations are correct, backlog coverage is 100%
- **Ready**: Can be used as input for Statement of Work generation (`/raise.7.sow`)

---

## Mandatory Criteria (MUST PASS ALL)

### C1: Guía de Estimación Completa

**What It Checks**: Section 1 provides complete guidance for Story Point estimation

**Checklist**:
- [ ] Section "1. Guía de Estimación en Puntos de Historia (Story Points)" exists
- [ ] Fibonacci scale documented (1, 2, 3, 5, 8, 13, 20, 40, 100)
- [ ] Factors to consider explained (at least 3: complejidad, esfuerzo, incertidumbre/riesgo)
- [ ] Planning poker process described (or reference to standard process)

**Check Method**:
1. Verify section header exists (case-insensitive match on "Guía de Estimación")
2. Search for "Fibonacci" or list of numbers "1, 2, 3, 5, 8"
3. Verify at least 3 factors mentioned (complejidad, esfuerzo, incertidumbre are keywords)
4. Verify planning poker mentioned (keyword "planning poker" or "estimación en equipo")

**Failure Example**:
```
❌ C1 FAILED: Guía de Estimación Completa
  - Issue: Section exists but only documents scale, missing factors and process
  - Fix: Add subsection explaining 3 factors (complejidad, esfuerzo, incertidumbre)
  - Fix: Add subsection describing planning poker process (or link to standard)
```

**Pass Example**:
```
✅ C1 PASSED: Guía de Estimación Completa
  - Section "1. Guía de Estimación..." exists
  - Fibonacci scale documented (1, 2, 3, 5, 8, 13, 20, 40, 100)
  - 3 factors explained (complejidad, esfuerzo, incertidumbre)
  - Planning poker process described
```

---

### C2: Estimation Table Complete

**What It Checks**: Section 2 table includes ALL backlog items with Story Point estimates

**Checklist**:
- [ ] Section "2. Estimación del Backlog" exists
- [ ] Table includes columns: ID, Elemento (or Item/Backlog), Estimación (SP), Notas (or Notes), Referencia (or Reference)
- [ ] ALL Epics, Features, and User Stories from backlog appear in table (100% coverage)
- [ ] Total SP row exists and sum is correct
- [ ] No "Pendiente" estimates remain (or clearly marked as preliminary if present)

**Check Method**:
1. Count rows in estimation table
2. Load `specs/main/project_backlog.md` and count total items (Epics + Features + User Stories)
3. Verify row count matches: table_rows == backlog_items
4. Verify "TOTAL" row exists with SP sum
5. Verify sum(SP column) == Total SP value
6. Check for "Pendiente" - if found, ensure marked as "[Pendiente - Estimado preliminar: X SP]"

**Failure Example**:
```
❌ C2 FAILED: Estimation Table Complete
  - Issue: Table has 45 rows but backlog has 52 items (87% coverage)
  - Missing items: US-023, US-031, US-038, US-042, US-049, US-051, US-052
  - Fix: Add 7 missing User Stories to table with their SP estimates
```

**Pass Example**:
```
✅ C2 PASSED: Estimation Table Complete
  - Table has 52 rows (100% coverage of backlog)
  - Total SP: 163 SP (sum matches)
  - 5 preliminary estimates marked clearly
```

---

### C3: Team Parameters Documented

**What It Checks**: Section 3 documents team structure and capacity calculation

**Checklist**:
- [ ] Section "3. Parámetros para el Roadmap" exists
- [ ] Sprint duration documented (e.g., "2 semanas", "1 week")
- [ ] Team structure documented (roles with dedication percentages)
- [ ] Capacity documented (SP/sprint) with calculation shown
- [ ] Note about velocity measurement included (initial estimate vs real measurement)

**Check Method**:
1. Verify section header exists
2. Search for "Duración del Sprint" or "Sprint duration"
3. Search for team roles (Architect, Engineer, QA, or similar)
4. Search for "Capacidad" or "Capacity" with number (e.g., "16 SP")
5. Verify calculation shown (e.g., "(0.5 * 8) + (1.0 * 8) + (0.5 * 8) = 16")
6. Search for "velocidad" or "velocity" mention (note about measuring real velocity)

**Failure Example**:
```
❌ C3 FAILED: Team Parameters Documented
  - Issue: Capacity is documented (16 SP/sprint) but calculation not shown
  - Fix: Add calculation: "(0.5 * 8) + (1.0 * 8) + (0.5 * 8) = 16 SP"
  - Issue: No note about velocity measurement
  - Fix: Add: "Esta capacidad es inicial. La velocidad real se medirá en primeras iteraciones."
```

**Pass Example**:
```
✅ C3 PASSED: Team Parameters Documented
  - Sprint duration: 2 semanas
  - Team structure: 1 Architect (50%), 1 Engineer (100%), 1 QA (50%)
  - Capacity: 16 SP/sprint with calculation shown
  - Velocity measurement note included
```

---

### C4: Roadmap Projection Table Present

**What It Checks**: Section 4 contains complete roadmap table with iteration details

**Checklist**:
- [ ] Section "4. Roadmap Proyectado" exists
- [ ] Table includes columns: Iteración, Fechas (or Dates), Objetivo (or Goal/Objective), Elementos Planeados (or Planned Items), SP Estimados (or SP), SP Acumulados (or Accumulated SP)
- [ ] At least 1 iteration row exists (typically 5-15 iterations)
- [ ] Total SP in roadmap matches or exceeds backlog Total SP (within rounding tolerance)
- [ ] Disclaimer present about projection nature (must be refined with real data)

**Check Method**:
1. Verify section header exists
2. Verify table has required 6 columns (allow Spanish/English variations)
3. Count iteration rows (should be >= 1)
4. Extract SP_Acumulados from last row → compare to backlog Total SP (allow ±5 SP tolerance for rounding)
5. Search for disclaimer keywords: "proyección", "estima", "debe refinar", "velocidad medida", "actualizar"

**Failure Example**:
```
❌ C4 FAILED: Roadmap Projection Table Present
  - Issue: Table has only 3 columns (missing SP Estimados, SP Acumulados)
  - Fix: Add columns for SP per iteration and accumulated SP
  - Issue: Disclaimer missing
  - Fix: Add: "Este roadmap es una proyección inicial basada en capacidad estimada. Debe refinarse con velocidad medida."
```

**Pass Example**:
```
✅ C4 PASSED: Roadmap Projection Table Present
  - Table complete with 6 columns
  - 11 iterations documented
  - Final accumulated SP: 163 (matches backlog total)
  - Disclaimer present
```

---

### C5: MVP Clearly Identified

**What It Checks**: MVP scope is visible and quantified in the roadmap

**Checklist**:
- [ ] MVP iterations are marked in roadmap table (e.g., "(MVP)" label, separate column, or visual distinction)
- [ ] MVP SP total is calculated and displayed
- [ ] MVP ratio is documented (MVP SP / Total SP) as a percentage

**Check Method**:
1. Search roadmap table for MVP markers: "(MVP)", "MVP:", label/column
2. Count iterations marked as MVP
3. Search for "MVP SP" or "Story Points MVP" with number
4. Search for MVP ratio (e.g., "48%", "0.48", "MVP: 78 SP de 163 SP")
5. Verify ratio calculation: (MVP SP / Total SP) × 100

**Failure Example**:
```
❌ C5 FAILED: MVP Clearly Identified
  - Issue: No MVP marking found in roadmap table
  - Fix: Add "(MVP)" label or marker to iterations 1-5 that contain MVP Features (FEAT-001, FEAT-004, FEAT-005)
  - Issue: MVP SP not calculated
  - Fix: Calculate MVP SP (sum SP from MVP iterations) and document: "MVP: 78 SP (48% del total)"
```

**Pass Example**:
```
✅ C5 PASSED: MVP Clearly Identified
  - Iterations 1-5 marked with "(MVP)" label
  - MVP SP documented: 78 SP
  - MVP ratio: 48% of total (78/163)
```

---

### C6: Cost Model Section Present

**What It Checks**: Section 5 explains relationship between Story Points and costs

**Checklist**:
- [ ] Section "5. Vinculación con Modelo de Costos" exists
- [ ] SP-to-effort relationship explained (e.g., "1 SP ≈ 4-6 hours")
- [ ] Impact of changes on cost/timeline discussed
- [ ] Key cost assumptions listed (team composition, rates, factors)

**Check Method**:
1. Verify section header exists (search for "Vinculación", "Modelo de Costos", "Cost Model")
2. Search for SP-to-hours conversion (keywords: "horas", "hours", "esfuerzo", "effort")
3. Search for impact statement (keywords: "impacto", "cambios", "afecta", "impact")
4. Search for assumptions list (keywords: "supuesto", "asume", "assumption")

**Failure Example**:
```
❌ C6 FAILED: Cost Model Section Present
  - Issue: Section exists but only has placeholder text
  - Fix: Add SP-to-hours conversion: "1 SP ≈ 4-6 horas de trabajo"
  - Fix: Add impact statement: "Cambios en el roadmap impactarán costo y calendario proporcionalmente"
  - Fix: Add assumptions: "Asume equipo estable, tarifas X, factor de conversión Y"
```

**Pass Example**:
```
✅ C6 PASSED: Cost Model Section Present
  - Section complete with 3 subsections
  - SP-to-hours: 1 SP ≈ 4-6 hours
  - Impact of changes discussed
  - Key assumptions documented
```

---

### C7: Metadata and References Complete

**What It Checks**: Frontmatter YAML is complete and references prior artifacts

**Checklist**:
- [ ] Frontmatter YAML block exists (between `---` delimiters)
- [ ] Required fields present: document_id, title, project_name, client (optional), version, date, author, related_docs, status
- [ ] related_docs includes at least 4 documents: PRD, Vision, Tech Design, Backlog
- [ ] Status is "Draft" or "In Review" (not empty or "Final" before approval)

**Check Method**:
1. Parse YAML frontmatter (first `---` to second `---`)
2. Verify all required fields present (allow null for optional client)
3. Check related_docs array has >= 4 items
4. Verify related_docs includes keywords: "PRD", "VIS", "TEC", "BCK" (or full names)
5. Verify status is not empty and not "Final"

**Failure Example**:
```
❌ C7 FAILED: Metadata and References Complete
  - Issue: related_docs only has 2 items (PRD, Vision)
  - Missing: Tech Design, Backlog
  - Fix: Add to related_docs:
      - "TEC-PROJECT-001" (Tech Design)
      - "BCK-PROJECT-001" (Backlog)
  - Issue: Status is empty
  - Fix: Set status: "Draft"
```

**Pass Example**:
```
✅ C7 PASSED: Metadata and References Complete
  - All required fields present
  - related_docs has 4 items: PRD, Vision, Tech Design, Backlog
  - Status: "Draft"
```

---

## Optional Criteria (Nice-to-Have)

These criteria are NOT required for gate pass, but enhance roadmap quality:

### O1: Iteration Objectives Meaningful

- [ ] Each iteration has descriptive objective (not just "Iteración 1", "Iteración 2")
- [ ] Objectives indicate focus (e.g., "Establecer bases", "Core features", "Integrations")

### O2: Team Structure Specific

- [ ] Team structure includes specific names/roles (not just generic "Engineer", "QA")
- [ ] Clear ownership indicated (e.g., "María González - Lead Architect")

### O3: Cost Model Detailed

- [ ] SP-to-hours conversion includes range (e.g., "1 SP = 4-6 hours, avg 5 hours")
- [ ] Hourly rates or total cost estimate included (if available)
- [ ] Breakdown by role (Architect rate, Engineer rate, QA rate)

**Note**: Optional criteria failures do NOT block gate pass. They are suggestions for improvement.

---

## Gate Execution

### If ALL Mandatory Criteria Pass

**Output**:
```
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: 163 SP
- MVP Story Points: 78 SP (48% of total)
- Iterations Needed: 11 sprints (22 weeks with 2-week sprints)
- Team Capacity: 16 SP/sprint
- Backlog Coverage: 100% (52/52 User Stories)
- Cost Model: Documented

Mandatory Criteria: 7/7 PASSED
Optional Criteria: 2/3 PASSED (O2 not met - team structure is generic)

→ Siguiente paso: /raise.7.sow - Generate Statement of Work from this roadmap
```

**Action**: Offer handoff to `/raise.7.sow` command

---

### If ANY Mandatory Criterion Fails

**Output Format**:
```
❌ Gate FAILED - N criteria not met:

[For each failed criterion:]
C#: [Criterion Name]
  - Issue: [Specific problem found]
  - Location: [Quote from roadmap or "Section missing"]
  - Fix: [Concrete action to resolve]

🛑 JIDOKA: Fix these issues before continuing. Do not offer handoff to /raise.7.sow until gate passes.

Recommendations:
1. [First fix suggestion]
2. [Second fix suggestion]
```

**Action**: STOP execution. Do NOT offer handoff. List all failures with specific fixes.

**Example**:
```
❌ Gate FAILED - 2 criteria not met:

C2: Estimation Table Complete
  - Issue: Table only has 45 rows but backlog has 52 User Stories (87% coverage)
  - Location: Section "2. Estimación del Backlog" table
  - Fix: Add missing 7 User Stories to table: US-023, US-031, US-038, US-042, US-049, US-051, US-052

C5: MVP Clearly Identified
  - Issue: No MVP marking found in roadmap table
  - Location: Section "4. Roadmap Proyectado" table
  - Fix: Add "MVP" column or label to iterations 1-5 that contain MVP Features (FEAT-001, FEAT-004, FEAT-005)
  - Fix: Calculate MVP SP: sum(SP from iterations 1-5) and document ratio

🛑 JIDOKA: Fix these issues before continuing. Do not offer handoff to /raise.7.sow until gate passes.

Recommendations:
1. Review backlog file to find missing User Stories (run: grep -E "US-[0-9]+" specs/main/project_backlog.md)
2. Review backlog MVP markers to identify which Features are MVP (look for "is_mvp: true" or "MVP" labels)
```

---

## Implementation Notes

### For Gate File (gate-estimation.md)

The gate file should:
1. Be written in Markdown with clear checklist format
2. Be executable by AI agent (Claude interprets and validates)
3. Use Spanish for content (matching roadmap language)
4. Use English for meta-instructions (matching command language)
5. Include examples of both pass and fail outputs

### For Command (raise.6.estimation.md Step 11)

At finalization step, the command should:
1. Load gate file from `.specify/gates/raise/gate-estimation.md`
2. Load roadmap from `specs/main/estimation_roadmap.md`
3. Execute each criterion check programmatically
4. Collect all failures (don't stop at first failure)
5. Display consolidated result (pass or fail with all issues)
6. If pass: show summary + offer handoff
7. If fail: list issues + stop (no handoff)

### Validation Algorithm

```python
# Pseudocode for gate execution

def execute_gate(roadmap_path, backlog_path):
    roadmap = load_markdown(roadmap_path)
    backlog = load_markdown(backlog_path)

    results = {
        "C1": check_estimation_guide(roadmap),
        "C2": check_estimation_table(roadmap, backlog),
        "C3": check_team_parameters(roadmap),
        "C4": check_roadmap_projection(roadmap, backlog),
        "C5": check_mvp_identified(roadmap),
        "C6": check_cost_model(roadmap),
        "C7": check_metadata(roadmap)
    }

    failures = [c for c, passed in results.items() if not passed]

    if len(failures) == 0:
        display_pass_output(roadmap)
        offer_handoff("raise.7.sow")
    else:
        display_fail_output(failures, roadmap)
        jidoka_stop()
```

---

## Success Metrics

**Gate Quality**: Measure how well gate prevents incomplete roadmaps

| Metric | Target | Measurement |
|--------|--------|-------------|
| False Positives | <5% | Gate fails on valid roadmap |
| False Negatives | <2% | Gate passes on invalid roadmap |
| Execution Time | <10 sec | Time to validate criteria |
| Clarity | 100% | Failures provide actionable fixes |

**Roadmap Quality**: Measure roadmap completeness

| Metric | Target | Measurement |
|--------|--------|-------------|
| First-Pass Rate | >80% | Roadmaps that pass gate on first execution |
| Coverage | 100% | % of backlog items in estimation table |
| Accuracy | ±20% | Actual project duration vs projected |

---

## References

- **Functional Requirement**: FR-010 (Command must execute gate before finalization)
- **Kata**: L1-04 Step 6 (Realizar la estimación detallada)
- **Template**: `src/templates/solution/estimation_roadmap.md`
- **Command**: `.raise-kit/commands/02-projects/raise.6.estimation.md` Step 11
- **Rule 110**: Section on gate execution and Jidoka principle
