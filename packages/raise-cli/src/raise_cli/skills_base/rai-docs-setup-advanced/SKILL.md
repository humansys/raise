---
allowed-tools:
- Read
- Write
- Bash(rai:*)
- Bash([ -n:*)
description: 'Configure advanced custom routing — add new Confluence spaces and set
  per-artifact parent_path hierarchy. Full wizard for complex multi-space orgs.

  '
model: haiku
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '0'
  raise.frequency: once
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: rai-docs-setup
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: utility
name: rai-docs-setup-advanced
---

# Docs Setup — Advanced

## Purpose

Full wizard for complex multi-space Confluence orgs. Covers everything `rai-docs-setup` defers:
- **Agregar nuevos espacios** — crea targets adicionales vía CLI (`rai adapter setup confluence --append`)
- **Routing custom por grupo** — configura `parent_path` jerárquico por artifact group
- **Asignación libre** — mueve grupos entre espacios sin límite

**When to use this skill**

| Need | Skill |
|------|-------|
| Initial 1-2 space setup (80% case) | `rai-docs-setup` |
| Agregar espacios + routing custom complejo | **This skill** (`rai-docs-setup-advanced`) |
| Routing drift / re-sync after config drifts | `rai-docs-update` |

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through every routing decision and verify credentials before writes
- **Ha**: Reuse existing targets and only ask about changed routing
- **Ri**: Apply known routing updates with concise confirmation checkpoints

## Context

**Prerequisites:**
- `.raise/docs.yaml` exists and has ≥1 Confluence target (run `/rai-docs-setup` first)
- `CONFLUENCE_URL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_USERNAME` in env or `.env`

## Artifact Groups Reference

| Group | Artifact Types |
|-------|---------------|
| Architecture | adr, architecture-domain-model, architecture-index, architecture-module, architecture-system-context, architecture-system-design |
| Developer Docs | project-vision, project-prd, project-guardrails, project-backlog |
| Epics | epic-brief, epic-scope, epic-design, epic-docs |
| Stories | story, story-scope, story-design, story-plan |
| Bugs | bugfix-scope, bugfix-analysis, bugfix-plan, bugfix-retro |
| Sessions | session-diary, retrospective, mission-retro |
| Research | research, proposal |

## Steps

### Step 0: Credential + Prerequisite Gate

Check credentials:

```bash
[ -n "$CONFLUENCE_URL" ] || echo "MISSING: CONFLUENCE_URL"
[ -n "$CONFLUENCE_API_TOKEN" ] || echo "MISSING: CONFLUENCE_API_TOKEN"
[ -n "$CONFLUENCE_USERNAME" ] || echo "MISSING: CONFLUENCE_USERNAME"
```

Read `.raise/docs.yaml` using the `Read` tool.

| Condition | Action |
|-----------|--------|
| Credentials missing | **STOP** — explain which var is missing and how to set it (`.env` or `~/.rai/.env`) |
| File missing | **STOP** — "`.raise/docs.yaml` no encontrado. Corre `/rai-docs-setup` primero." |
| File exists with ≥1 target | Continue to Step 1 |

<verification>
Credentials present. `.raise/docs.yaml` exists with at least one Confluence target.
</verification>

### Step 1: Show Current Config Summary

Parse `.raise/docs.yaml` and present all targets and their routing:

```
Configuración actual de docs:

  [1] humansys-governance (GOV) — 10 tipos
        Architecture   → adr, architecture-*  [parent_title: Architecture]
        Developer Docs → project-*            [parent_title: Developer Docs]

  [2] humansys-work (WORK) — 17 tipos
        Epics    → epic-*      [parent_title: Epics]
        Stories  → story-*     [parent_title: Stories]
        Bugs     → bugfix-*    [parent_title: Bugs]
        Sessions → session-*   [parent_title: Sessions]
        Research → research, proposal  [parent_title: Research]

Grupos sin asignar a ningún target: ninguno
```

Mark routing entries as `[parent_title: X]` (preset/flat) or `[parent_path: X/Y/Z]` (already custom).

If any artifact group has types not assigned to any target, list them as "sin asignar".

<verification>
Developer sees the full routing picture before making any decision.
</verification>

### Step 2: Mode Selection

```
¿Qué quieres hacer?

  [1] Agregar nuevos espacios de Confluence (crear targets + asignar grupos)
  [2] Personalizar routing de espacios existentes (cambiar parent_path)
  [3] Ambos — agregar nuevos espacios y reconfigurar routing existente
```

Store selection. Continue to Step 3 (always shown), then Step 4 (modes 1 and 3), then Step 5 (modes 2 and 3).

<verification>
Mode selected. Steps to execute are determined.
</verification>

### Step 3: New Space Setup (modes 1 and 3)

Ask: "¿Cuántos espacios nuevos quieres agregar?"

For **each new space**, collect in sequence (one question at a time):

**Q1 — Site:**
```
¿Cuál es el Confluence site para este espacio?
  El site actual es: {existing_site} — ¿usamos ese mismo u otro?
```
Default = existing site if all current targets share the same site.

**Q2 — Space key:**
```
¿Cuál es la clave del espacio en Confluence?
  (La encuentras en la URL: .../wiki/spaces/{CLAVE}/...)
```

**Q3 — Instance name** (derived, confirm):
```
Nombre del target en docs.yaml: {prefix}-{space_key.lower()}
  ¿Lo usamos o prefieres otro nombre?
```

**Q4 — Which groups go here:**
```
¿Qué grupos van a este espacio ({space_key})?

  Disponibles (aún no asignados a este espacio):
    [1] Architecture  (6 tipos)
    [2] Developer Docs (4 tipos)
    [3] Epics         (4 tipos)
    [4] Stories       (4 tipos)
    [5] Bugs          (4 tipos)
    [6] Sessions      (3 tipos)
    [7] Research      (2 tipos)
    [8] Tipo específico
    [s] Saltar — no asignar grupos ahora

  Selecciona uno o varios (ej: 1 3 5):
```

Multi-select allowed. Groups assigned here will be **moved** from their current target to this new one.

After collecting all new spaces, build the **CLI execution plan**:

```
Comandos a ejecutar:

  rai adapter setup confluence \
    --site {site1} --instance {instance1} --space {space_key1} \
    --yes --append

  rai adapter setup confluence \
    --site {site2} --instance {instance2} --space {space_key2} \
    --yes --append

  (3 comandos en total)
```

Show this preview and ask: "¿Ejecutamos?"

On confirm: run each command in sequence. Show output. Stop on error.

<verification>
All new targets created in `.raise/docs.yaml`. No routing yet — that comes in Steps 4–5.
</verification>

### Step 4: Group Assignment (reassign groups across all targets)

Show the full group → target assignment matrix, including new targets just created:

```
Asignación de grupos:

  Grupo             Espacio actual
  ──────────────────────────────────
  Architecture      governance (GOV)
  Developer Docs    governance (GOV)
  Epics             work (WORK)
  Stories           work (WORK)
  Bugs              work (WORK)
  Sessions          work (WORK)
  Research          work (WORK)

Targets disponibles:
  [1] humansys-governance (GOV)
  [2] humansys-work (WORK)
  [3] mi-nuevo-espacio (NEW1)      ← recién creado

Para cada grupo, indica el número del target destino o confirma que se mantiene en el actual.
```

Ask one group at a time. Record any reassignments.

**Note on reassignment:** Moving a group from target A to target B means:
- Removing those artifact types from target A's routing
- Adding them to target B's routing (with a parent_path to be collected in Step 5)

<verification>
Final group → target mapping complete. Every artifact group assigned to exactly one target.
</verification>

### Step 5: Parent Path Input (per group per target)

For each group in each target (new assignments + any existing ones to customize), ask:

```
Grupo: {G} → target: {target_name} ({space_key})
¿Cuál es el parent path?
  Ejemplo: Governance/Architecture/ADRs
  (Usa / para separar niveles. El actual es: {current} — ¿lo mantenemos o cambiamos?)
```

Rules:
- Sin cambio → keep existing `parent_title` or `parent_path` unchanged
- Input text → split on `/`, strip whitespace → `parent_path: [A, B, C]`
- Single segment → `parent_path: [A]`
- Reject empty segments — re-prompt once

After collecting all paths, build the full routing plan in memory.

<verification>
parent_path collected for every group being changed. Unchanged groups have their existing value preserved.
</verification>

### Step 6: Preview All Changes

Show the complete picture before writing anything:

```
─── Preview completo ──────────────────────────────────────────────────────

  Comandos CLI ya ejecutados:
    ✓ rai adapter setup confluence --site x --instance nuevo-space --space NEW1 --yes --append

  Cambios en routing (.raise/docs.yaml):

    humansys-governance (GOV):
      ELIMINAR:  Epics (epic-brief, epic-scope, epic-design, epic-docs)
                 → movidos a nuevo-space (NEW1)
      MANTENER:  Architecture, Developer Docs

    humansys-work (WORK):
      MANTENER:  Stories, Bugs, Sessions, Research

    nuevo-space (NEW1) — nuevo:
      AGREGAR:   Epics → parent_path: [Engineering, Projects, Epics]
                   epic-brief:   parent_path: [Engineering, Projects, Epics]
                   epic-scope:   parent_path: [Engineering, Projects, Epics]
                   epic-design:  parent_path: [Engineering, Projects, Epics]
                   epic-docs:    parent_path: [Engineering, Projects, Epics]

  Total: 4 entradas agregadas, 4 entradas eliminadas de governance.

───────────────────────────────────────────────────────────────────────────

¿Escribimos los cambios de routing a .raise/docs.yaml?
```

| Answer | Action |
|--------|--------|
| y | Continue to Step 7 |
| n | "Cancelado. Los targets CLI ya creados se mantienen, pero sin routing custom." |

<verification>
Developer reviewed complete picture. No routing written yet.
</verification>

### Step 7: Write Routing Changes

For each target + group collected in Steps 4–5, call one command per group:

```bash
rai adapter route patch --target {target} --group "{group}" --parent-path "{A/B/C}"
```

Or per individual artifact type:

```bash
rai adapter route patch --target {target} --type {artifact_type} --parent-path "{A/B/C}"
# or with parent_title:
rai adapter route patch --target {target} --type {artifact_type} --parent-title "{Page Title}"
```

Example — Epics group moved to a new space:
```bash
rai adapter route patch --target nuevo-space --group "Epics" --parent-path "Engineering/Projects/Epics"
```

Use the concrete target names and paths collected in Steps 4–5. Run one command per group per target.

**Note on removals:** `rai adapter route patch` handles additions and updates only. If a group is being *moved away* from a target (reassigned in Step 4), edit `.raise/docs.yaml` directly to remove those routing entries from the old target — or leave them in place if the target will no longer be used for those types.

<verification>
`.raise/docs.yaml` written atomically. All target routing reflects the plan from Step 6.
</verification>

### Step 8: Verify

```bash
rai doctor
```

Show output. Then present the **publish reference** for the new config:

```
✓ rai-docs-setup-advanced completado

  Targets configurados: {N}

  Para publicar a cada espacio:
    rai docs write adr ...          → humansys-governance (GOV)
    rai docs write story ...        → humansys-work (WORK)
    rai docs write epic-brief ...   → nuevo-space (NEW1)

  Los artifact types que viven en targets no-default necesitan:
    rai docs write epic-brief --target nuevo-space ...

  Las páginas del parent_path se crean automáticamente en el primer publish.
```

**Important note on `--target` flag:** Artifact types in the `default_target` resolve automatically. Types in other targets require `--target {instance_name}` in every rai docs write call. Make this explicit in the output.

## Output

| Artifact | Destination |
|----------|-------------|
| Nuevos targets | `.raise/docs.yaml` (via `rai adapter setup confluence --append`) |
| Routing custom | `.raise/docs.yaml` (via Python write, Step 7) |
| Publish reference | Shown in conversation (Step 8) |

## Quality Checklist

- [ ] Gate: `.raise/docs.yaml` y credenciales presentes antes de cualquier pregunta
- [ ] NEVER ejecutar `rai adapter setup confluence --append` sin confirmación previa (Step 3 preview)
- [ ] NEVER modificar targets no seleccionados
- [ ] NEVER escribir `parent_path` como string — siempre como lista YAML
- [ ] NEVER omitir el preview (Step 6) antes de escribir routing
- [ ] Python script con valores reales, no placeholders
- [ ] `parent_title` removido cuando `parent_path` es seteado
- [ ] Advertir sobre `--target` flag para tipos en targets no-default (Step 8)
- [ ] `rai doctor` corrido al final — errores de adapter son bloqueantes

## References

- Base: `/rai-docs-setup` (configuración inicial 1-2 espacios)
- Diagnóstico: `/rai-doctor`
- Re-sync: `/rai-docs-update`
- Schema: `packages/raise-cli/src/raise_cli/adapters/confluence_config.py` (`ArtifactRouting`)
- CLI: `rai adapter setup confluence --help`
