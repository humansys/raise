---
description: Generate Estimation Roadmap from Project Backlog with Story Point projections and sprint timeline
handoffs:
  - label: Create Statement of Work
    agent: tools/generate-contract
    prompt: Generate Statement of Work from this estimation roadmap
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Populate the Estimation Roadmap template (`.specify/templates/raise/solution/estimation_roadmap.md`) with content derived from the Project Backlog, producing `specs/main/estimation_roadmap.md` with team parameters, iteration projections, MVP identification, and cost model linkage. This command implements **Kata L1-04 Step 6** ("Realizar la estimación detallada").

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load the template from `.specify/templates/raise/solution/estimation_roadmap.md`.
   - Load backlog from `specs/main/project_backlog.md` to extract: Epics, Features, User Stories with SP estimates.
   - Calculate Total SP (sum of all User Story estimates).
   - Identify MVP Features (marked in backlog).
   - Prepare output file at `specs/main/estimation_roadmap.md`.
   - **Verificación**: Template loaded, backlog parsed, Total SP calculated, MVP Features identified.
   - > **Si no puedes continuar**: Template not found → **JIDOKA**: Check .raise-kit setup, verify template was copied to .specify/. Backlog not found → **JIDOKA**: Execute `/project/create-backlog` first. Backlog has no SP estimates → **JIDOKA**: Propose preliminary estimates based on complexity (1-2 SP low, 3-5 SP medium, 8 SP high) and warn user to refine in planning poker.

2. **Paso 1: Completar Guía de Estimación (Sección 1 del Template)**:
   - Instantiate template with metadata: document_id (EST-[PROJECT]-001), title, project_name, client, version (1.0), date, author.
   - Add related_docs: PRD, Vision, Tech Design, Backlog (reference their document IDs).
   - Set status to "Draft".
   - Fill Section 1 "Guía de Estimación en Puntos de Historia":
     - Document Fibonacci scale: 1, 2, 3, 5, 8, 13, 20, 40, 100
     - Explain factors to consider: Complejidad (technical difficulty), Esfuerzo (work volume), Incertidumbre/Riesgo (unknowns)
     - Describe planning poker process (6 steps from template example)
   - **Verificación**: Section 1 complete with scale, factors (3 minimum), and process description. Metadata YAML complete with all required fields.
   - > **Si no puedes continuar**: Cannot determine project name → **JIDOKA**: Use backlog project_name or ask user. Missing related_docs → **JIDOKA**: Search specs/main/ for PRD/Vision/Tech files, or note as "Pending".

3. **Paso 2: Generar Tabla de Estimación del Backlog (Sección 2 del Template)**:
   - Parse $ARGUMENTS for team parameters. If empty, use defaults:
     - 1 AI Architect (50%) = 4 SP/sprint
     - 1 AI Engineer (100%) = 8 SP/sprint
     - 1 AI QA (50%) = 4 SP/sprint
     - Total capacity = 16 SP/sprint
     - Sprint duration = 2 weeks
   - If $ARGUMENTS provided, parse team structure from natural language (e.g., "2 engineers full-time, 1 QA 50%, sprints 1 week").
   - Validate capacity: must be 8-40 SP/sprint range (reasonable for estimation).
   - Fill Section 2 "Estimación del Backlog":
     - Create table with columns: ID (Backlog), Elemento del Backlog, Estimación (SP), Notas / Supuestos Clave, Referencia (PRD/SoW Sec.)
     - Add rows for ALL Epics, Features, and User Stories from backlog (100% coverage)
     - For User Stories without SP estimates, mark as "[Pendiente - Estimado preliminar: X SP]" with note "Debe refinarse en planning poker"
     - Add TOTAL row with sum of all SP estimates
   - **Verificación**: Section 2 table complete with ALL backlog items (count matches backlog). Total SP calculated correctly. Team parameters parsed and validated (capacity in range).
   - > **Si no puedes continuar**: Capacity < 8 SP/sprint → **JIDOKA**: Alert that project would take too long, suggest increasing capacity or reducing scope. Capacity > 40 SP/sprint → **JIDOKA**: Question if team structure is feasible, suggest validation with user. Table coverage < 100% → **JIDOKA**: List missing items, add them before continuing.

4. **Paso 3: Documentar Parámetros del Roadmap (Sección 3 del Template)**:
   - Fill Section 3 "Parámetros para el Roadmap":
     - Document sprint duration (e.g., "2 semanas")
     - Document team structure with roles and dedication percentages
     - Document capacity calculation showing math: "(0.5 * 8) + (1.0 * 8) + (0.5 * 8) = 16 SP"
     - Add note about velocity: "Este es un valor estimado inicial basado en la composición del equipo. La capacidad real se determinará midiendo el trabajo completado en la primera Iteración y se usará para ajustar el roadmap futuro."
   - If defaults were used, note: "Using default team structure (can be customized via command arguments)".
   - If custom parameters provided, note: "Using custom team structure as specified".
   - **Verificación**: Section 3 complete with all 4 parameters (sprint duration, team structure, capacity calculation, velocity note). Source of parameters documented (defaults or custom).
   - > **Si no puedes continuar**: Cannot parse custom team parameters → **JIDOKA**: Show example format "N engineers full-time, M QA X%, sprints Y weeks" and ask user to retry. Math doesn't add up → **JIDOKA**: Recalculate capacity, show work.

5. **Paso 4: Calcular Roadmap Proyectado (Sección 4 del Template)**:
   - Calculate iterations needed: iterations = ceil(Total SP / Team Capacity)
   - Generate iteration table with columns: Iteración, Fechas Estimadas, Objetivo de la Iteración, Elementos del Backlog Planeados (IDs), Prioridad, SP Estimados por Iteración, SP Acumulados, Notas / Dependencias Clave
   - For each iteration:
     - Número: 1, 2, 3, ...
     - Fechas: Relative dates (e.g., "Semana 1-2", "Semana 3-4" based on sprint duration)
     - Objetivo: Suggest focus based on Features (e.g., "Iteración 1: Establecer bases, recepción interna", "Iteración 2: Búsqueda externa y generación")
     - Elementos Planeados: List Epic/Feature/US IDs that fit in this iteration (prioritize by: MVP first, then priority from backlog)
     - SP Estimados: Sum of SP for items in this iteration (max = team capacity)
     - SP Acumulados: Running total of SP completed by end of this iteration
     - Mark iterations containing MVP items with "(MVP)" label or note
   - Fill Section 4 "Roadmap Proyectado":
     - Add summary: Total SP, Capacity, Number of Iterations
     - Add iteration table with all rows
     - Add disclaimer: "Este roadmap es una proyección basada en estimaciones pendientes y una capacidad inicial asumida. El alcance real completado por iteración puede variar. El roadmap se revisará y ajustará regularmente basándose en el progreso real, la velocidad medida y cualquier cambio en las prioridades o el alcance."
   - Calculate MVP metrics: MVP SP (sum from MVP iterations), MVP ratio (MVP SP / Total SP)
   - **Verificación**: Iterations calculated (> 0). Roadmap table complete with all columns. sum(SP Estimados) across iterations >= Total SP. MVP iterations clearly marked. Disclaimer present.
   - > **Si no puedes continuar**: Iterations > 26 (> 6 months with 2-week sprints) → **JIDOKA**: Warn that project is large, suggest reviewing MVP scope to reduce initial size (target: MVP ≤ 10 sprints). Cannot distribute items to iterations → **JIDOKA**: Sort backlog by priority+dependencies, assign items sequentially up to capacity per iteration.

6. **Paso 5: Documentar Vinculación con Modelo de Costos (Sección 5 del Template)**:
   - Fill Section 5 "Vinculación con Modelo de Costos":
     - Explain SP-to-effort relationship (e.g., "1 SP ≈ 4-6 horas de trabajo, dependiendo del equipo y la complejidad")
     - Document impact of changes: "Cambios en el roadmap (agregar/quitar items, cambiar prioridades) impactarán el costo total y el calendario proporcionalmente"
     - List key cost assumptions:
       - Team composition (roles as documented in Section 3)
       - Hourly rates (if known, otherwise note as "Pending - to be defined in SoW")
       - Conversion factor SP → hours (e.g., "Asumiendo 1 SP = 5 horas promedio")
     - If cost data available, calculate estimated total cost: Total SP * hours_per_SP * average_hourly_rate
     - Note: "Supuestos de costo deben validarse con el Statement of Work (SoW)"
   - **Verificación**: Section 5 complete with 3 subsections (SP-to-effort, impact, assumptions). Cost model explanation clear even if specific rates not available.
   - > **Si no puedes continuar**: Cannot estimate hours per SP → **JIDOKA**: Use industry standard "1 SP ≈ 4-6 hours" and note it's an approximation. No rate data → **JIDOKA**: Document as "Pending definition in SoW" and proceed.

7. **Finalize & Validate**:
   - Confirm `specs/main/estimation_roadmap.md` file exists and is complete.
   - Generate summary section at end of roadmap (if not in template):
     - Total SP: [X]
     - MVP SP: [Y] ([Z]% of total)
     - Iterations needed: [N] sprints ([W] weeks)
     - Team capacity: [C] SP/sprint
   - Execute validation gate: `.specify/gates/raise/gate-estimation.md`
   - Capture gate results (7 mandatory criteria):
     - C1: Guía de Estimación completa
     - C2: Estimation table complete (100% backlog coverage)
     - C3: Team parameters documented
     - C4: Roadmap projection table present
     - C5: MVP clearly identified
     - C6: Cost model section present
     - C7: Metadata complete
   - If gate FAILS:
     - List specific criteria that failed
     - Quote relevant sections or note "Section missing"
     - Suggest concrete fixes for each failure
     - **STOP execution** - do NOT offer handoff until gate passes
   - If gate PASSES:
     - Show summary: Total SP, MVP SP/ratio, iterations, team capacity, backlog coverage
     - Run `.specify/scripts/bash/update-agent-context.sh` to update agent context
     - Display handoff: "→ Siguiente paso: `/tools/generate-contract` - Generate Statement of Work from this roadmap"
   - **Verificación**: Gate executed (results shown). If pass: summary displayed + handoff offered. If fail: specific issues listed + execution stopped.
   - > **Si no puedes continuar**: Gate mandatory criteria failed → **JIDOKA**: Iterate on failed criteria before proceeding - do NOT continue with invalid roadmap. Gate file not found → **JIDOKA**: Verify .raise-kit setup, check if gate file exists at .specify/gates/raise/.

---

## Notes

### About Team Parameters ($ARGUMENTS)

Users can customize team structure via command arguments in natural language:

**Examples**:
- Empty (default): Uses 16 SP/sprint team (1 architect 50%, 1 engineer 100%, 1 QA 50%)
- "2 engineers full-time, 1 QA 50%, sprints 1 week": 2 * 8 + 0.5 * 8 = 20 SP/sprint, 1-week sprints
- "1 architect 100%, 3 engineers 100%, sprints 2 weeks": 1 * 8 + 3 * 8 = 32 SP/sprint

**Parsing logic**:
- Roles: "architect", "engineer", "QA" (case-insensitive)
- Dedication: "full-time" = 100%, "50%" = 50%, "25%" = 25%
- Sprint: "sprints N week(s)" or "sprints N semana(s)"
- Capacity: sum(role.dedication * 8 SP baseline)

### Handling Missing SP Estimates

If backlog User Stories have no SP estimates (marked as "Pendiente" or empty):
- Analyze complexity: description length, acceptance criteria count
- Propose preliminary estimate: 1-2 SP (low), 3-5 SP (medium), 8 SP (high)
- Mark in table: "[Pendiente - Estimado preliminar: X SP]"
- Add note: "Debe refinarse en planning poker"
- Warn user: "⚠ WARNING: N User Stories have no SP estimates → Proposing preliminary estimates (will need refinement)"

This unblocks roadmap generation while being transparent about estimate quality.

### MVP Identification

MVP scope is determined from backlog:
- Features marked as "is_mvp: true" or with "MVP" label → MVP Features
- User Stories belonging to MVP Features → MVP stories
- Iterations containing MVP stories → MVP iterations (mark with "(MVP)" label)
- Calculate: MVP SP = sum(SP from MVP stories), MVP ratio = (MVP SP / Total SP) * 100

Target: MVP ≤ 50% of total SP for faster feedback.

### Iteration Distribution Algorithm

```
remaining_items = all User Stories sorted by (is_mvp DESC, priority DESC, dependencies)
for iteration in 1..iterations_needed:
    capacity_left = team_capacity
    iteration_items = []

    for item in remaining_items:
        if item.sp_estimate <= capacity_left:
            iteration_items.append(item)
            capacity_left -= item.sp_estimate
            remaining_items.remove(item)
        if capacity_left == 0:
            break

    iteration.items = iteration_items
    iteration.sp = team_capacity - capacity_left
    iteration.sp_accumulated = previous_iteration.sp_accumulated + iteration.sp
```

---

## High-Signaling Guidelines

- **Output**: This command generates `specs/main/estimation_roadmap.md` with 5 main sections: Guía de Estimación, Tabla de Estimación del Backlog, Parámetros del Roadmap, Roadmap Proyectado, Vinculación con Modelo de Costos.

- **Focus**: Estimation roadmap generation from backlog. Prioritize: (1) 100% backlog coverage in estimation table, (2) correct SP math (iterations = Total SP / Capacity), (3) clear MVP identification, (4) transparent assumptions documentation.

- **Language**: Instructions in English for AI agent. Generated roadmap content in **SPANISH** (sections, tables, notes - all in Spanish).

- **Jidoka**: Stop immediately if: (1) Backlog missing or incomplete → execute /project/create-backlog first, (2) Team capacity < 8 SP/sprint → alert project too long, (3) Gate mandatory criteria fail → list specific failures and do NOT offer handoff until fixed.

---

## AI Guidance

When executing this workflow:

1. **Role**: You are orchestrating estimation roadmap generation as defined in **Kata L1-04 Step 6** ("Realizar la estimación detallada"). Your role is to guide the Presales Architect through systematic transformation of backlog SP estimates into a sprint-based roadmap with cost projections.

2. **Be proactive**: Propose reasonable defaults for team parameters (16 SP/sprint) if user provides no arguments. Propose preliminary estimates for User Stories missing SP (based on complexity heuristics). Signal when estimates need refinement but don't block execution.

3. **Follow Katas**: This command implements **Kata L1-04 Step 6** but does NOT have a dedicated kata flujo like project/create-backlog.

   Instead, it follows:
   - **Template structure**: `estimation_roadmap.md` has 5 sections (steps 2-6 map 1:1 to these sections)
   - **L1-04 acceptance criteria**: "El roadmap resume esfuerzo por historia, epic y total. Se documentan supuestos de estimación, riesgos y buffers explícitos."
   - **Logical workflow**: Initialize → Fill each template section sequentially → Validate

   **Each step = One template section**:
   - Step 2 → Section 1 (Guía de Estimación)
   - Step 3 → Section 2 (Tabla de Estimación)
   - Step 4 → Section 3 (Parámetros)
   - Step 5 → Section 4 (Roadmap Proyectado)
   - Step 6 → Section 5 (Vinculación Costos)

   This makes the command easy to follow and maintain.

4. **Traceability**: Every iteration in the roadmap must reference specific backlog items (Epics, Features, User Stories by ID). Link roadmap back to: PRD (requirements), Vision (scope), Tech Design (architecture), Backlog (detailed items). Document in related_docs.

5. **Gates**: Execute `gate-estimation.md` at step 7. This gate has 7 mandatory criteria that MUST pass:
   - C1-C7 check completeness of all 5 sections + metadata
   - If gate fails, identify specific issues (e.g., "C2: Table only 87% coverage, missing US-023, US-031...") and guide user through fixes
   - Do NOT offer handoff to `/tools/generate-contract` until gate passes (Jidoka principle)

6. **Heutagogy**: This command facilitates learning about agile estimation, not just mechanical execution. Explain the "why":
   - Why Fibonacci scale? (Reflects increasing uncertainty at larger sizes)
   - Why Story Points not hours? (Relative sizing more accurate, velocity-based planning)
   - Why planning poker? (Team consensus, knowledge sharing, reduces anchoring bias)
   - Why disclaimers? (Initial roadmap is hypothesis, must validate with real velocity)

   Guide, don't dictate - user makes final decisions on parameters and accepts estimates.

7. **MVP Discipline**: Be strict about MVP scope. If MVP > 50% of total SP, alert user and suggest deferring non-essential Features. Ask: "Can we deliver value without this Feature?" Help prioritize ruthlessly. Many projects fail because MVP is too large.

8. **Estimation Quality**: If User Stories lack estimates:
   - Propose preliminary values (don't block)
   - Base on observable complexity (description, criteria)
   - Always warn estimates are preliminary and need refinement
   - Better to unblock with transparent approximation than block execution

9. **Math Accuracy**: Verify calculations at each step:
   - Total SP = sum(all User Story estimates) - check this matches
   - Iterations = ceil(Total SP / Capacity) - always round up
   - SP Acumulados = running total - verify last iteration equals Total SP
   - MVP ratio = (MVP SP / Total SP) * 100 - show as percentage
