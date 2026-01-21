# Gate: Estimation Roadmap Validation

**Purpose**: Validate that `specs/main/estimation_roadmap.md` is complete, accurate, and ready for Statement of Work generation.

**Executed by**: raise.6.estimation command at Step 7 (Finalize & Validate)

---

## Mandatory Criteria (MUST PASS ALL 7)

### C1: Guía de Estimación Completa

**Check**:
- [ ] Section "1. Guía de Estimación en Puntos de Historia" exists
- [ ] Fibonacci scale documented (must include: 1, 2, 3, 5, 8, 13)
- [ ] At least 3 factors explained (e.g., complejidad, esfuerzo, incertidumbre)
- [ ] Planning poker process described (or reference to estimation process)

**How to verify**: Search for section header, verify "Fibonacci" mentioned and numbers listed, count factors (≥3), check for "planning poker" or "proceso de estimación".

**If fails**: Add missing elements to Section 1.

---

### C2: Estimation Table Complete

**Check**:
- [ ] Section "2. Estimación del Backlog" exists
- [ ] Table has columns: ID, Elemento, Estimación (SP), Notas, Referencia
- [ ] Table includes ALL items from backlog (100% coverage)
- [ ] TOTAL row exists with correct sum of SP

**How to verify**:
1. Count table rows (excluding header and TOTAL)
2. Load `specs/main/project_backlog.md` and count Epics + Features + User Stories
3. Verify: table_rows == backlog_items
4. Verify: sum(SP column) == TOTAL row value

**If fails**: List missing items and add them to table. Recalculate TOTAL.

---

### C3: Team Parameters Documented

**Check**:
- [ ] Section "3. Parámetros para el Roadmap" exists
- [ ] Sprint duration documented
- [ ] Team structure documented (roles with dedication %)
- [ ] Capacity documented with calculation shown
- [ ] Velocity note included (about initial vs real measurement)

**How to verify**: Search for "Duración del Sprint", team roles (architect/engineer/QA), "Capacidad", calculation formula, "velocidad" mention.

**If fails**: Add missing parameters. Show capacity calculation math.

---

### C4: Roadmap Projection Table Present

**Check**:
- [ ] Section "4. Roadmap Proyectado" exists
- [ ] Table has columns: Iteración, Fechas, Objetivo, Elementos Planeados, SP Estimados, SP Acumulados
- [ ] At least 1 iteration row exists
- [ ] Final SP Acumulados matches Total SP from backlog (±5 SP tolerance for rounding)
- [ ] Disclaimer present about projection nature

**How to verify**: Verify table structure, count rows (≥1), compare last SP Acumulados to backlog Total SP, search for "proyección" or "debe refinar" in disclaimer.

**If fails**: Complete table columns, verify math, add disclaimer.

---

### C5: MVP Clearly Identified

**Check**:
- [ ] MVP iterations are marked in roadmap (e.g., "(MVP)" label, separate column, or note)
- [ ] MVP SP total calculated
- [ ] MVP ratio documented (MVP SP / Total SP as %)

**How to verify**: Search table for "(MVP)" markers, search document for "MVP SP" or "MVP:" with number, search for ratio/percentage.

**If fails**: Mark MVP iterations clearly. Calculate: MVP SP = sum(SP from MVP iterations), ratio = (MVP SP / Total SP) * 100. Document both values.

---

### C6: Cost Model Section Present

**Check**:
- [ ] Section "5. Vinculación con Modelo de Costos" exists
- [ ] SP-to-effort relationship explained (e.g., "1 SP ≈ X horas")
- [ ] Impact of changes discussed
- [ ] Key cost assumptions listed

**How to verify**: Verify section exists, search for "SP" + "horas" or "hours", search for "impacto" or "cambios", search for "supuesto" or "asume".

**If fails**: Add section with 3 subsections: relationship, impact, assumptions.

---

### C7: Metadata and References Complete

**Check**:
- [ ] Frontmatter YAML exists (between `---` delimiters)
- [ ] Required fields present: document_id, title, project_name, version, date, author, related_docs, status
- [ ] related_docs includes at least 4 items: PRD, Vision, Tech Design, Backlog
- [ ] Status is "Draft" or "In Review" (not empty)

**How to verify**: Parse YAML block, verify all fields present, count related_docs (≥4), check status value.

**If fails**: Add missing YAML fields. Add missing documents to related_docs.

---

## Gate Execution Result

### If ALL 7 criteria PASS:

```
✅ Gate PASSED - Estimation Roadmap validated

Summary:
- Total Story Points: [X] SP
- MVP Story Points: [Y] SP ([Z]% of total)
- Iterations Needed: [N] sprints ([W] weeks)
- Team Capacity: [C] SP/sprint
- Backlog Coverage: 100% ([count]/[count] items)
- Cost Model: Documented

Mandatory Criteria: 7/7 PASSED

→ Siguiente paso: /raise.7.sow - Generate Statement of Work from this roadmap
```

**Action**: Offer handoff to `/raise.7.sow`

---

### If ANY criterion FAILS:

```
❌ Gate FAILED - [N] criteria not met:

[For each failed criterion:]
C#: [Criterion Name]
  - Issue: [Specific problem]
  - Location: [Quote from roadmap or "Section missing"]
  - Fix: [Concrete action needed]

🛑 JIDOKA: Fix these issues before continuing.
Do NOT offer handoff to /raise.7.sow until ALL criteria pass.

Recommendations:
1. [First fix suggestion]
2. [Second fix suggestion]
```

**Action**: STOP execution. List ALL failures. Do NOT offer handoff.

---

## Validation Algorithm

```
For each criterion C1-C7:
    If criterion passes:
        Mark as PASS
    Else:
        Mark as FAIL
        Record specific issue
        Suggest concrete fix

Count failures = |{criteria where status == FAIL}|

If failures == 0:
    Display PASS output with summary
    Offer handoff to raise.7.sow
Else:
    Display FAIL output with all issues
    Execute Jidoka (stop, no handoff)
```

---

## Notes

- Gate is executed by AI agent (Claude interprets criteria and validates roadmap)
- All criteria are mandatory - even 1 failure blocks gate pass
- Fixes should be specific and actionable (quote sections, list missing items)
- Gate result determines if handoff is offered (pass) or execution stops (fail)
