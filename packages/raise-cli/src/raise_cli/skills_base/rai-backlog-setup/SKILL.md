---
name: rai-backlog-setup
description: >
  Configure a Jira instance for all RaiSE skills in one session: connection,
  custom fields, workflow statuses, and link types — backlog.yaml complete.

model: haiku
allowed-tools:
  - "Bash(rai:*)"
  - "Bash([ -n:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: once
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: "rai-bugfix-triage"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "4.0.0"
  raise.visibility: public
---

# Backlog Setup

## Purpose

Configure `.raise/backlog.yaml` for a new Jira instance through a conversational flow — the agent asks two questions and calls the CLI with non-interactive flags. Ends with discovery of custom fields, workflow statuses, and link types, verified by a live `rai backlog get` call.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps in order; explain purpose of each section before running
- **Ha**: Run steps 0–3 directly; verify once at the end
- **Ri**: Gate → ask site + projects → `rai adapter setup jira --site x.atlassian.net --instance x --projects Z --yes` → discover → verify

## When to use this skill

| Need | Skill |
|------|-------|
| Configure **Jira** (backlog.yaml, custom fields, statuses, link types) | **This skill** (`rai-backlog-setup`) |
| Configure **Confluence** (docs.yaml, space, routing) | `rai-docs-setup` |
| Configure both at once (legacy) | `rai-adapter-setup` *(deprecated)* |

Use this skill after rai init, when connecting to a new Jira instance, or when `/rai-doctor` reports missing adapter config.

**When to skip:** `rai backlog fields list` shows configured fields — adapter already set up.

## Context

**Prerequisites:** `JIRA_URL` + `JIRA_API_TOKEN` + `JIRA_USERNAME` must exist in `~/.rai/.env` or `.env` in the project root. rai init complete.

## Steps

### Step 0: Credential Gate

```bash
[ -n "$JIRA_URL" ] || {
  echo "JIRA_URL no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: JIRA_URL=https://tu-instancia.atlassian.net"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
[ -n "$JIRA_API_TOKEN" ] || {
  echo "JIRA_API_TOKEN no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: JIRA_API_TOKEN=tu-token"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
[ -n "$JIRA_USERNAME" ] || {
  echo "JIRA_USERNAME no está seteada."
  echo "Opciones:"
  echo "  1. Llena .env.example y cópialo a .env en el proyecto: JIRA_USERNAME=tu-email"
  echo "  2. O agrégala globalmente en ~/.rai/.env para todos los worktrees"
  exit 1
}
```

If any check fails: stop and present the message above. Do NOT ask the user to type the token in the chat. Do NOT suggest running `source`. `rai` carga `~/.rai/.env` y `.env` del proyecto automáticamente en cada comando.

<verification>
`JIRA_URL`, `JIRA_API_TOKEN`, and `JIRA_USERNAME` are present in the environment. Skill proceeds.
</verification>

### Step 1: Ask Site Domain

Ask the user (one question):

> "¿Cuál es tu Jira site? (ej. `humansys.atlassian.net`)"

Store the answer as `{site}` (dominio completo). Derive the instance label automatically: `{instance}` = first part of the domain (e.g. `humansys.atlassian.net` → `humansys`).

### Step 2: Ask Projects

Ask the user (one question):

> "¿Qué proyectos incluir? (coma-separados, ej. `RAISE,DEMO`)"

Store the answer as `{projects}`. Save the first project key as `{first_project}` for later verification.

### Step 3: Run Adapter Setup

```bash
rai adapter setup jira \
  --site {site} \
  --instance {instance} \
  --projects {projects} \
  --yes
```

Where `{site}` = `humansys.atlassian.net` and `{instance}` = `humansys` (derived from site).

Use `--overwrite` if `.raise/backlog.yaml` already exists and the user wants to regenerate.

**Warning:** Running `--overwrite` after Steps 4–6 are complete will erase all custom fields, workflow, and link-type config. Only use it to reset the base config before running discovery again.

<verification>
`.raise/backlog.yaml` exists and `rai backlog get {first_project}-1` succeeds.

```bash
rai backlog get {first_project}-1
```
</verification>

### Step 3.5: Discover Issue Types

```bash
rai backlog issue-types discover {first_project}
```

Registers all project issue types with key prefixes in backlog.yaml
(Epic→e, Story→s, Bug→b; custom types get the shortest unique lowercase prefix).
Without this step, `rai backlog create --type {CustomType}` cannot resolve the type.

<verification>
`rai backlog issue-types list {first_project}` shows issue types and `.raise/backlog.yaml` contains an `issue_type_prefixes` section.
</verification>

### Step 4: Discover Custom Fields

Before running, explain: "Custom fields let RaiSE skills read and write structured data on issues (e.g. classification fields for bugs, priority tiers, etc.)."

Run first to show available issue types (project key is a positional argument, no flag):

```bash
rai backlog issue-types list {first_project}
```

Ask (one at a time):
1. "Which issue types do you want to configure custom fields for?"
2. For each chosen type: "What custom fields? If unsure, I can search first." — if unsure, run `rai backlog fields search --project {first_project} "{term}"` for each term (note: `fields search` returns all project fields — it does not filter by issue type)

```bash
rai backlog fields discover --names "{field1},{field2},..." --issue-type {IssueTypeName}
```

`--issue-type` here accepts the **display name** returned by `issue-types` (e.g. `Historia`, `Error`).

Repeat for each chosen issue type.

<verification>
`rai backlog fields list` shows `custom_fields.{IssueTypeName}` with ≥1 field for each configured type.
</verification>

### Step 5: Discover Workflow Statuses

Ask: "Which issue types should I configure workflow statuses for?"

Run once per selected type:

```bash
rai backlog statuses discover {first_project} --issue-type {DISPLAY_TYPE_NAME}
```

`--issue-type` accepts the **display name** returned by `rai backlog issue-types list` (e.g. `Historia`, `Tarea`, `Error`). The CLI resolves aliases from `backlog.yaml` automatically — internal English names are not needed.

Each run saves statuses under `workflow.{IssueType}` — running for multiple types accumulates without overwriting.

Verify with:

```bash
rai backlog statuses list
```

<verification>
`.raise/backlog.yaml` contains `workflow.{IssueType}.states` for each selected type.
</verification>

### Step 6: Discover Link Types

```bash
rai backlog link-types discover
```

0 link types is valid — some instances don't use them.

<verification>
`.raise/backlog.yaml` contains `relation_types` (may be empty list).
</verification>

### Step 7: Final Verification

```bash
rai backlog fields list
```

Show the output. Confirm `custom_fields.{IssueTypeName}` for each configured type, `workflow.states`, and `relation_types` are present.

Declare setup complete.

### Step 8: Sync Backlog Items (Recommended Next Step)

Suggest running:

```bash
rai backlog sync --project {first_project}
```

This fetches the project's issues into the backlog-items cartridge
(`.raise/cartridges/backlog-*/instances/items.json`), regenerates
`governance/backlog.md`, and rebuilds the knowledge graph so backlog items
are queryable via rai graph query. Without it, rai graph build shows
0 backlog items and prints a cold-start hint.

This is a suggestion — do not run it automatically without user confirmation.

## Output

| Artifact | Destination |
|----------|-------------|
| Base adapter config | `.raise/backlog.yaml` — organizations, projects |
| Custom fields | `.raise/backlog.yaml` — `custom_fields.{IssueTypeName}` |
| Workflow statuses | `.raise/backlog.yaml` — `workflow.states` |
| Link types | `.raise/backlog.yaml` — `relation_types` |

## Quality Checklist

- [ ] Credential gate passed — `JIRA_URL`, `JIRA_API_TOKEN`, and `JIRA_USERNAME` present
- [ ] NEVER print, log, or request the value of a credential in the conversation
- [ ] NEVER suggest running `source` — credentials are loaded automatically by `rai`
- [ ] Asked site and projects conversationally (2 questions max before CLI call)
- [ ] Called `rai adapter setup jira` with `--site`, `--instance`, `--projects`, `--yes` (no TTY)
- [ ] Ran `rai backlog issue-types discover {KEY}` (Step 3.5) — writes `issue_type_prefixes` to backlog.yaml
- [ ] Ran `rai backlog issue-types list {KEY}` (positional, no `--project`) to review types before configuring custom fields
- [ ] Used display names for both `fields discover --issue-type` and `statuses discover --issue-type` (e.g. `Historia`, `Tarea`, `Error`)
- [ ] Asked user to confirm field names (or ran search first)
- [ ] `rai backlog fields list` shows entries for each configured issue type
- [ ] NEVER use `--context` flag — use `--issue-type` instead
- [ ] Did NOT run `adapter setup jira --overwrite` after discovery steps
- [ ] Suggested `rai backlog sync --project {KEY}` as the next step (do not auto-run)

## References

- CLI help: `rai adapter setup --help`, `rai backlog fields --help`
- Complement: `/rai-docs-setup` (configures Confluence)
- Legacy: `/rai-adapter-setup` *(deprecated — use `/rai-backlog-setup` + `/rai-docs-setup`)*
- Custom field discovery: `rai backlog fields search --project KEY "term"`
