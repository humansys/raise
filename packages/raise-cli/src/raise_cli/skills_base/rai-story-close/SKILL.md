---
name: rai-story-close
description: "Canonical story close: gates + raise_story_close_full + scope.md. Sin señales de observabilidad (raise_story_close_full las emite server-side). ADR-143 B2."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"
  - "Bash(uv:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '4'
  raise.frequency: per-story
  raise.gate: gate-ar-story
  raise.skillset: raise-maintainability
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: story
  raise.inputs: |
    - story_id: string, required, argument (e.g. S14.1)
    - slug: string, required, argument
    - epic_dir: string, required, argument
    - jira_key: string, optional, argument
    - run_id: string, required, from_orchestrator
  raise.outputs: |
    - merge_commit: string, git
---

# Story Close

> ℹ DEFAULT VARIANT (ADR-143 B2) — colapso de rai-story-close + rai-story-close-lean.
> Señales eliminadas: raise_story_close_full (mcp_tools_story.py:102) ya las emite server-side.
> CLI fallback rai story close (exit 1, deprecated ADR-143 B2) — usar pipeline engine.
> 6 pasos [R5, G1] de 19 en enterprise. Sin checklist.

## Pipeline Context Check

Verificar que este skill fue invocado vía pipeline engine (RAISE-10715):

- Si `Run ID:` aparece en el contexto → continuar silenciosamente.
- Si **ausente** → STOP: "standalone execution detected — prior phases may have been skipped. Options: 1) continue anyway, 2) abort."
  - Si eliges **continue anyway** → ANTES de continuar, emite señal de observabilidad del bypass (RAISE-15391 — el "continue anyway" antes no dejaba rastro queryable):
    ```bash
    rai signal emit-work story "<story_id>" --event blocked --phase close \
      --blocker "standalone-close: prior phases (review/retro) unverified"
    ```

## Objetivo

Cerrar la story con una llamada compuesta. Inputs: story ID, slug, epic dir, Jira key, run_id (del orquestador). Expected state: árbol limpio, retro artifact presente.

## Pasos

### 1. Ejecutar gate before:story:close [R]

```bash
rai gate check --point before:story:close
```

Si falla → resolver defecto antes de continuar. No usar `--all` (demasiado broad para story close).

### 2. Ejecutar AR gate [R]

```bash
rai gate check gate-ar-story
```

Escape hatch para XS/docs:
```bash
RAISE_AR_SKIP_REASON="<reason>" rai gate check gate-ar-story
```

> ℹ El gate emite automáticamente una señal `ar-skip` (WorkLifecycle, queryable vía `rai signal query story <branch> --event ar-skip`) al usar el escape hatch — RAISE-15391. Es un rastro de observabilidad además del `governance/ar-skip-log.jsonl`. No la re-emitas manualmente (doble conteo).

Solo verifica que la attestation existe (escrita por `/rai-story-review`). No crear el marker aquí — ADR-130 / RAISE-14277.

### 2.5. Regenerate architecture diagram ground-truth manifests [G]

Run regen for the two Python components whose manifests the CI fidelity gate checks.
The script is idempotent — outputs "unchanged" and exits 0 when nothing is stale.

```bash
uv run python scripts/regen-architecture-diagrams.py \
  --component raise-server \
  --component raise-cli
```

Failure (regen exits non-zero): stop and report; do not continue to Step 3.

Commit only if the regen wrote any files:

```bash
DIRTY=$(git status --short docs/diagrams/ground-truth/ dev/docs/architecture/)
if [ -n "$DIRTY" ]; then
  git add docs/diagrams/ground-truth/ dev/docs/architecture/
  git commit -m "chore: regenerate architecture diagram ground-truth manifests

Co-Authored-By: Rai <rai@humansys.ai>"
fi
```

### 3. Llamar raise_story_close_full [R]

```python
raise_story_close_full(
    story_id="{story_id}",
    slug="{slug}",
    epic_dir="{epic_dir}",
    jira_key="{jira_key}",
    merge_summary="{story_id}: {name} — {1-line summary}",
    cwd="{cwd}"
)
```

### 4. Manejar report [R]

| Estado | Acción |
|--------|--------|
| `status: ok` | Continuar al paso 5 |
| `retro: blocked` | **STOP** — ejecutar `/rai-story-review` primero, sin excepciones |
| `hygiene: blocked` | **STOP** — presentar opciones discard/stash/keep; nunca auto-resolver |
| `merge: blocked` (`merge-conflict`) | Resolver conflicto en story branch, reintentar |
| `backlog: blocked` | **STOP** — Jira no puede divergir de git; fijar sync y reintentar |
| `cleanup/restore: warn` | Mencionar; continuar |

### 4.5. Regenerate skills catalog if skills changed [G]

Check whether any skill files changed in this story. If so, regenerate
`docs/skills/index.md` (and the ES mirror) and commit if dirty.

```bash
# RAISE-17066: declared, never inferred — CI env > registered worktree target > manifest. Fail loud.
DEV_BRANCH="${RAISE_DEVELOPMENT_BRANCH:-$(rai worktree context --field merge_target 2>/dev/null || true)}"
[ -n "$DEV_BRANCH" ] || DEV_BRANCH="$(rai manifest env | python3 -c "import json,sys; print(json.load(sys.stdin)['branches']['development'])")"
[ -n "$DEV_BRANCH" ] || { echo "ERROR: cannot resolve target branch — set branches.development in .raise/manifest.yaml"; exit 1; }
SKILLS_CHANGED=$(git diff --name-only "$(git merge-base HEAD "${DEV_BRANCH}")..HEAD" \
  | grep -E "skills_base/|\.claude/skills/|\.agent/skills/" | head -1)
if [ -n "$SKILLS_CHANGED" ]; then
  python3 scripts/generate_skills_catalog.py
  DIRTY=$(git status --short docs/skills/ docs/es/skills/)
  if [ -n "$DIRTY" ]; then
    git add docs/skills/ docs/es/skills/
    git commit -m "docs: regenerate skills catalog after skill changes

Co-Authored-By: Rai <rai@humansys.ai>"
  fi
fi
```

Failure (script exits non-zero): stop and report; do not continue.

### 5. Actualizar epic scope.md [G]

Marcar story completa en `work/epics/{epic_dir}/scope.md`:
- Checkbox de criterios de done
- Tabla de progreso: `| {story_id} | ✅ Done | {date} |`

Commit en el merge target.

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:story:close
```

**STOP.** Devolver: merge commit, Jira status, branch cleanup.
