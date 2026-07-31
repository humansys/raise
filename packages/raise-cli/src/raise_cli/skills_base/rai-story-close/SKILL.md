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

### 5. Actualizar epic scope.md [G]

Marcar story completa en `work/epics/{epic_dir}/scope.md`:
- Checkbox de criterios de done
- Tabla de progreso: `| {story_id} | ✅ Done | {date} |`

Commit en el merge target.

### 6. Si story standalone: marcar mission objective [R]

Solo si `epic_dir` está vacío (story sin épica):
```bash
rai mission list  # identificar la misión activa (*)
rai mission accomplish {index}
```

**STOP.** Devolver: merge commit, Jira status, branch cleanup.
