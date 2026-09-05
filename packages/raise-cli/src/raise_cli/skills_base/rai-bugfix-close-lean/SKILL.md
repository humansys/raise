---
name: rai-bugfix-close-lean
description: "Lean residue de rai-bugfix-close: push + MR + Jira sync. 10 pasos vs 26 enterprise. Asume pipeline-orchestrated."
model: haiku

allowed-tools:
  - Read
  - "Bash(git:*)"
  - "Bash(glab:*)"
  - "Bash(rai:*)"
  - "mcp__rai-workspace__pipeline_status"
  - "mcp__rai-workspace__raise_backlog_update"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '5'
  raise.frequency: per-bug
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: bugfix-lean
  raise.inputs: |
    - bug_id: string, required, argument
    - run_id: string, required, injected by orchestrator in pointer prompt
    - dev_branch: string, required, config
  raise.outputs: |
    - mr_url: string, terminal
---

# Bugfix Close (Lean)

> ⚠ LEAN VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-bugfix-close, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-bugfix-close
> Lean residue: 10 pasos [R9, G1, I2] de 26 en enterprise (54% ceremonia eliminada).
> Asume siempre pipeline-orchestrated — requiere run_id en el pointer prompt.

## Pipeline Context Check

Verificar que este skill fue invocado vía pipeline engine (RAISE-10715):

- Si `Run ID:` aparece en el contexto → continuar silenciosamente.
- Si **ausente** → STOP: "standalone execution detected — prior phases may have been skipped. Options: 1) continue anyway, 2) abort."
  - Si eliges **continue anyway** → ANTES de continuar, emite señal de observabilidad del bypass (RAISE-15391 — el "continue anyway" antes no dejaba rastro queryable):
    ```bash
    rai signal emit-work bug "<bug_id>" --event blocked --phase close \
      --blocker "standalone-close: prior phases (review/retro) unverified"
    ```

## Objetivo

Push del branch de bug, crear MR, y sincronizar Jira. El lean pipeline siempre provee run_id — no hay check de contexto de pipeline. Sin ceremony.

**Inputs:** Bug ID, `run_id` (inyectado por el orquestador), `{dev_branch}`.

## Pasos

### 1. Verificar artifacts via pipeline_status [R]

```python
pipeline_status(run_id="{run_id}")
```

Construir mapa `{phase_id → status}`. Para cada artifact:
- scope.md (fase: start/diagnose) → si fase skipped: ok; si fase ran + archivo ausente: **STOP**
- analysis.md (fase: analyse) → si fase skipped: ok
- plan.md (fase: plan) → si fase skipped: ok
- retro.md (fase: review) → si fase skipped: ok

En lean, analyse/plan/review siempre son skipped → solo scope.md es obligatorio.

### 2. Verificar árbol limpio [R]

```bash
git status --short
```

Si hay cambios uncommitted → commitarlos antes de push.

### 3. AR gate [R]

```bash
rai gate check gate-ar-bugfix
```

Escape hatch para XS/docs:
```bash
RAISE_AR_SKIP_REASON="<razón>" rai gate check gate-ar-bugfix
```

> ℹ El gate emite automáticamente una señal `ar-skip` (WorkLifecycle, queryable vía `rai signal query bugfix <branch> --event ar-skip`) al usar el escape hatch — RAISE-15391. Es un rastro de observabilidad además del `governance/ar-skip-log.jsonl`. No la re-emitas manualmente (doble conteo).

Si falla sin escape hatch → **STOP**: el AR debe existir antes del close.

### 4. Alembic single-head gate [R] (si el fix incluye migraciones)

```bash
rai gate check gate-alembic-single-head
```

Si falla → la cadena alembic tiene fork. Linealizar `down_revision` antes de push — no hacer merge sin esto; `alembic upgrade head` fallará en deploy.

Si el bug no toca migraciones → este gate pasa automáticamente (skipped).

### 5-6. Push + Crear MR [G]

Write the title and human-readable description to files without shell
interpolation. Invoke `/rai-mr-create` with these required inputs:

- `source_branch:` current `bug/{issue_key}/{slug}` branch
- `target_branch:` `{dev_branch}`
- `work_id:` `{bug_key}`
- `quality_review_file:` `work/bugs/{bug_key}/qr.md`
- `title_file:` file containing the exact MR/PR title
- `description_file:` file containing the exact human-readable body

GitLab uses THIN admission. GitHub retains the local full-gate path until
equivalent remote enforcement exists. Neither provider permits manual push or
MR/PR creation outside `/rai-mr-create`.

If `/rai-mr-create` fails (sync conflict, gate failure, push rejection),
**STOP. Do not assign fixVersion, advance the pipeline, or clean up.**
There is no remote branch/MR result to finalize: returning a successful close
would allow the pipeline to transition Jira despite an unvalidated commit.

### 7. fixVersion — delegada al engine [R]

No asignar fixVersion manualmente — `_finalize_done` lo hace automáticamente
al aplicar `target_status: done` en el siguiente `pipeline_advance`, usando
`resolve_fix_version()` que lee `pyproject.toml` y preserva el prerelease
label activo (ej. `3.1.0rc5`). Asignar desde el branch name produce un
conflicto con `gate-close-jira-sync` (RAISE-16614).

### 8. Verificación post-transición delegada (blocking) [R]

No ejecutar `gate-close-jira-sync` directamente desde el skill: Jira todavía
no está en Done. Al devolver control, el siguiente `pipeline_advance` aplica
primero `target_status: done` y después ejecuta el gate en
`after:bug:close`.

Si el avance devuelve `gate_failed` para `after:bug:close` → **FAIL el close**.
No log-and-continue ni escape implícito. Corregir Jira y re-run.

### 9. Worktree-aware cleanup [R]

```bash
if [ "$(git rev-parse --git-common-dir)" != "$(git rev-parse --git-dir)" ]; then
  echo "Worktree — cleanup diferido a /rai-worktree-close"
else
  git checkout {dev_branch}
  git branch -D bug/{issue_key}/{slug}
fi
```

### 10. Bind result [I]

```python
raise_session_bind(key="RAISE_SESSION_JIRA_KEY", value="{bug_key}", cwd="{project_or_worktree_path}")
```

**Fin.** Devolver: MR URL, gate-close-jira-sync status, cleanup realizado sí/no.
