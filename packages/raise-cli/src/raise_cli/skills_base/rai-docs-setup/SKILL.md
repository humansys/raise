---
allowed-tools:
- Bash(rai:*)
- Bash([ -n:*)
- Read
description: 'Configure the docs adapter for all RaiSE skills in one session — docs
  adapter config complete. Currently supports Confluence.

  '
model: haiku
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '0'
  raise.frequency: once
  raise.gate: ''
  raise.next: rai-backlog-setup
  raise.prerequisites: ''
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: utility
name: rai-docs-setup
---

# Docs Setup

## Purpose

Configure `.raise/docs.yaml` para 1 o 2 espacios de Confluence en una sola sesión conversacional. Configuración recomendada: **2 espacios** (governance + work) — routing automático sin `--target`. Currently supported backend: Confluence.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps in order; detect existing config, recommend 2-space, show routing map per target at the end
- **Ha**: Detect config, run 2-space flow or `--append`; verify with `rai doctor`
- **Ri** (2-space, mismo site): `rai adapter setup confluence --site {site} --instance {prefix}-governance --space {GOV} --yes --structure governance && rai adapter setup confluence --site {site} --instance {prefix}-work --space {WORK} --yes --structure work --append && rai docs search "{GOV}"`

## When to use this skill

| Need | Skill |
|------|-------|
| Configure **docs adapter** (Confluence, routing automático) | **This skill** (`rai-docs-setup`) |
| Configure **backlog adapter** (Jira, custom fields, statuses) | `rai-backlog-setup` |
| Configuración avanzada (routing custom por artefacto) | `rai-docs-setup-advanced` |
| Configure both at once (legacy) | `rai-adapter-setup` *(deprecated)* |

Use this skill after rai init, when setting up the docs adapter, or when `/rai-doctor` reports missing docs adapter config.

**When to skip:** `rai docs search "test"` returns results without error — adapter already configured. Use `--overwrite` to regenerate.

## Context

**Prerequisites:** `CONFLUENCE_URL` + `CONFLUENCE_API_TOKEN` + `CONFLUENCE_USERNAME` must exist in `~/.rai/.env` or `.env` in the project root. rai init complete.

## Steps

### Step 0: Credential Gate

Check that all three credentials are present. Never print or log their values.

```bash
[ -n "$CONFLUENCE_URL" ] || {
  echo "CONFLUENCE_URL no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: CONFLUENCE_URL=https://tu-instancia.atlassian.net"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
[ -n "$CONFLUENCE_API_TOKEN" ] || {
  echo "CONFLUENCE_API_TOKEN no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: CONFLUENCE_API_TOKEN=tu-token"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
[ -n "$CONFLUENCE_USERNAME" ] || {
  echo "CONFLUENCE_USERNAME no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: CONFLUENCE_USERNAME=tu-email"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
```

If any check fails: stop and present the message above. Do NOT ask the user to type the token in the chat. Do NOT suggest running `source`. `rai` loads credentials automatically from `.env` in the project (higher priority) or `~/.rai/.env` as global fallback — rai init ya genera `.env.example` con las vars necesarias.

**Nota:** Si el shell reporta MISSING pero las vars están en `.env`, está bien — `rai` las carga directamente sin necesidad de `export`.

<verification>
`CONFLUENCE_URL`, `CONFLUENCE_API_TOKEN`, and `CONFLUENCE_USERNAME` are present in the environment OR exist in `.env`/`~/.rai/.env`. Skill proceeds.
</verification>

### Step 1: Detect Existing Configuration

Read `.raise/docs.yaml` (use the `Read` tool). Count the keys under `targets:`.

| Targets found | Action |
|---------------|--------|
| File missing or 0 targets | Continue to Step 2 (new project flow) |
| 1 target | Continue to Step 1b |
| 2+ targets | Continue to Step 1c |

#### Step 1b: 1 Existing Target — Offer Append

Present the existing target and offer to add a second:

```
Encontré 1 target configurado: {name} (espacio: {space_key})

¿Qué quieres hacer?
  [1] Agregar target governance — ADRs, arquitectura, developer docs (10 tipos)
  [2] Agregar target work — epics, stories, bugs, sessions, research (17 tipos)
  [3] Reconfigurar desde cero (--overwrite)
```

- **[1] o [2]**: Ask which space key to use for the new target. Derive `{site}` from the existing target's URL in `.raise/docs.yaml` (e.g. `url: https://humansys.atlassian.net/wiki` → `site: humansys.atlassian.net`). If the new target is on a different site, ask the developer. Then run one CLI call from Step 4 adding `--append --structure {governance|work}`. Skip to Step 5.
- **[3]**: Continue to Step 2 (treat as new project; add `--overwrite` to all CLI calls in Step 4).

#### Step 1c: 2+ Existing Targets — Show Map

Read the routing from `.raise/docs.yaml` and present it grouped by target, then by section (same format as Step 5). Then:

```
Tu configuración de docs ya tiene {N} targets. ¿Quieres reconfigurar desde cero?
  [y] Sí — continuar con setup completo (--overwrite)
  [n] No — salir, la configuración está lista
```

- **[n]**: Declare setup complete and exit.
- **[y]**: Continue to Step 2 (treat as new project; use `--overwrite` in all CLI calls).

<verification>
Existing configuration detected and developer has chosen a path. New project, append, or overwrite clearly established.
</verification>

### Step 2: New Project — Recommend 2-Space (Default)

Present the recommendation:

```
La configuración recomendada usa 2 espacios en Confluence:
  • governance — ADRs, arquitectura, developer docs (docs estables)
  • work       — epics, stories, bugs, sessions, research (artefactos activos)

Esto habilita routing automático: rai docs write adr va al espacio
correcto sin flags extra.

¿Tienes 2 espacios en Confluence? (y/n)
```

- **[y]**: Continue to Step 3 (2-space flow).
- **[n]**: Continue to Step 2b (fallback).

#### Step 2b: Fallback — No Second Space

```
Para la configuración 2-space necesitas dos espacios en Confluence.

Opciones:
  [1] Crear el segundo espacio ahora
       Confluence → Create space → Team space (o Blank)
       Dale una clave corta, ej. WORK o {PROYECTO}W
       Cuando lo tengas, corre /rai-docs-setup de nuevo —
       detectará el target existente y solo pedirá la clave del segundo espacio.

  [2] Un solo espacio — estructura RaiSE completa (27 tipos)
       Todos los artefactos en el mismo espacio, routing por sección.

  [3] Configuración avanzada
       /rai-docs-setup-advanced
```

- **[1]**: Exit. The developer will return after creating the space; Step 1b will handle the append.
- **[2]**: Continue to Step 3b (single-space flow).
- **[3]**: Exit and point to `/rai-docs-setup-advanced`.

### Step 3: 2-Space Setup (≤4 questions)

Ask in order — one question at a time, do not bundle:

1. **Governance site** — "¿Cuál es el Confluence site de tu espacio de governance? (ej. `miempresa.atlassian.net`)"

   Derive `{prefix}` from the first subdomain: `humansys.atlassian.net` → `humansys`.

2. **Governance space key** — "¿Cuál es la clave del espacio de governance? La encuentras en la URL: `…/wiki/spaces/{CLAVE}/…`"

3. **Same site for work?** — "¿El espacio de work también está en `{governance_site}`? (y/n)"
   - **[y]**: Skip to question 4 (same site).
   - **[n]**: Ask "¿Cuál es el site del espacio de work?" → derive `{work_prefix}`.

4. **Work space key** — "¿Cuál es la clave del espacio de work?"

Instance names are derived automatically:
- Governance: `{prefix}-governance` (e.g. `humansys-governance`)
- Work: `{work_prefix}-work` (e.g. `humansys-work`)

Where `{work_prefix}` = `{prefix}` when both spaces are on the same site (Step 3 Q3 = y), or the first subdomain of the work site when different (Step 3 Q3 = n).

No need to ask for instance names.

Continue to Step 4 (2-space).

#### Step 3b: Single-Space Setup (fallback [2])

Ask in order:

1. **Site** — "¿Cuál es tu Confluence site? (ej. `miempresa.atlassian.net`)"

   Derive `{instance}` from the first subdomain automatically.

2. **Space key** — "¿Cuál es la clave de tu espacio? La encuentras en la URL: `…/wiki/spaces/{CLAVE}/…`"

Continue to Step 4b (single-space).

### Step 4: Run 2-Space Setup

Run the two CLI calls in sequence:

```bash
# Step 4a: Configure governance target
rai adapter setup confluence \
  --site {governance_site} \
  --instance {prefix}-governance \
  --space {governance_space} \
  --yes \
  --structure governance

# Step 4b: Add work target (--append preserves governance)
rai adapter setup confluence \
  --site {work_site} \
  --instance {work_prefix}-work \
  --space {work_space} \
  --yes \
  --structure work \
  --append
```

Add `--overwrite` to **both** calls if coming from Step 1b [3] or Step 1c (reconfigure paths).

The CLI auto-discovers each space and validates credentials against the live API — if credentials are wrong or a space key doesn't exist, it fails here with a clear error.

<verification>
Both CLI calls completed. `.raise/docs.yaml` has 2 targets: `{prefix}-governance` and `{prefix}-work`. `default_target` is `{prefix}-governance`.
</verification>

#### Step 4b: Run Single-Space Setup

```bash
rai adapter setup confluence \
  --site {site} \
  --instance {instance} \
  --space {space} \
  --yes \
  --structure raise
```

Add `--overwrite` if coming from Step 1b [3] or Step 1c.

<verification>
CLI output shows "✓ Injecting RaiSE routing preset (27 artifact types)". Config written to `.raise/docs.yaml`.
</verification>

Continue to Step 5.

### Step 5: Show Routing Map

Read `.raise/docs.yaml` and present the routing grouped by target, then by `parent_title` within each target:

**For 2-target config:**

```
✓ Tu configuración de docs tiene 2 targets:

  {prefix}-governance ({GOV_SPACE}) — 10 tipos:
    Architecture   → adr, architecture-domain-model, architecture-index,
                     architecture-module, architecture-system-context, architecture-system-design
    Developer Docs → project-vision, project-prd, project-guardrails, project-backlog

  {prefix}-work ({WORK_SPACE}) — 17 tipos:
    Epics    → epic-brief, epic-scope, epic-design, epic-docs
    Stories  → story, story-scope, story-design, story-plan
    Bugs     → bugfix-scope, bugfix-analysis, bugfix-plan, bugfix-retro
    Sessions → session-diary, retrospective, mission-retro
    Research → research, proposal

Las páginas padre se crean automáticamente la primera vez que publiques a cada sección.
```

**For single-target config:**

```
✓ Tu espacio {space} está mapeado en {N} secciones:

  Epics          → epic-brief, epic-scope, epic-design, epic-docs
  Stories        → story, story-scope, story-design, story-plan
  Bugs           → bugfix-scope, bugfix-analysis, bugfix-plan, bugfix-retro
  Sessions       → session-diary, retrospective, mission-retro
  Architecture   → adr, architecture-domain-model, architecture-index,
                   architecture-module, architecture-system-context, architecture-system-design
  Research       → research, proposal
  Developer Docs → project-vision, project-prd, project-guardrails, project-backlog

Las páginas padre se crean automáticamente la primera vez que publiques a cada sección.
```

Explica brevemente: el tipo de artefacto (`adr`, `story`, `session-diary`, etc.) determina el target y la página padre — no hay que especificar nada manualmente.

### Step 6: Demo de rai docs write

**Para configuración 2-target:**

```bash
# Publica un ADR → va al espacio de governance automáticamente
rai docs write adr \
  --title "ADR-001: Mi primera decisión" \
  --stdin \
  --output-path governance/adrs/adr-001-mi-decision.md << 'EOF'
# ADR-001: Mi primera decisión
...
EOF

# Publica una story → va al espacio de work automáticamente
rai docs write story \
  --title "S1.1: Mi primera story" \
  --stdin \
  --output-path work/epics/e1-nombre/stories/s1.1-story.md << 'EOF'
# Story S1.1
...
EOF
```

**Para configuración single-target:**

```bash
# Publicar desde stdin (útil en pipes y scripts):
echo "# Contenido" | rai docs write session-diary \
  --title "Mi primera sesión" \
  --stdin \
  --output-path .raise/sessions/hoy.md
```

**Sobre `--output-path`:** necesario cuando la ruta en `docs.yaml` no tiene `local_dir` configurado (el caso por defecto). Sin él, el CLI no sabe dónde guardar la copia local y falla. Siempre inclúyelo cuando publiques desde stdin.

### Step 7: Verify

```bash
rai doctor
rai docs search "{any_configured_space_key}"
```

Show both outputs. Confirm that `rai doctor` reports no adapter errors and `rai docs search` returns results.

Confirm routing:
- 2-target: governance target has 10 types, work target has 17 types
- Single-target: setup output showed "✓ Injecting RaiSE routing preset (27 artifact types)"

Declare setup complete.

<verification>
`rai doctor` passes. `rai docs search` returns ≥1 result. Routing count confirmed.
</verification>

## Output

| Artifact | Destination |
|----------|-------------|
| Docs adapter config | `.raise/docs.yaml` |
| Routing map | Shown in conversation (Step 5) |
| Write demo | Shown in conversation (Step 6) |

## Quality Checklist

- [ ] Credential gate passed — `CONFLUENCE_URL`, `CONFLUENCE_API_TOKEN`, and `CONFLUENCE_USERNAME` present (or in `.env`)
- [ ] NEVER print, log, or request the value of a credential in the conversation
- [ ] NEVER suggest running `source` — credentials are loaded automatically by `rai`
- [ ] NEVER ask the user to type a token in the chat
- [ ] NEVER show internal ticket references or roadmap items to the developer
- [ ] Detected existing target count before asking any questions (Step 1)
- [ ] Presented 2-space as the default recommendation (Step 2) — not as an option
- [ ] 2-space flow completed in ≤4 questions (credentials not counted)
- [ ] Fallback menu offered when developer has no second space: [1] create, [2] single-space raise, [3] /rai-docs-setup-advanced
- [ ] Called `rai adapter setup confluence` with `--site`, `--instance`, `--space`, `--yes` (no TTY)
- [ ] Used `--append` for second target in 2-space flow — did NOT overwrite existing target
- [ ] Routing map shown grouped by target, then by section (Step 5)
- [ ] Demo shows routing to correct target without `--target` flag (Step 6)
- [ ] `rai doctor` reports no adapter errors after setup
- [ ] `rai docs search` returns ≥1 result

## References

- CLI help: `rai adapter setup confluence --help`, `rai docs write --help`
- Diagnostics: `/rai-doctor`
- Complement: `/rai-backlog-setup` (backlog adapter)
- Advanced: `/rai-docs-setup-advanced` (custom routing per artifact type)
- Deprecated: `/rai-adapter-setup` (combined setup — use dedicated skills instead)
