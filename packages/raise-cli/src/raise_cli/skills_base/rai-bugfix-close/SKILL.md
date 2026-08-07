---
name: rai-bugfix-close
description: "Default variant: push + MR + Jira sync. 12 steps vs 26 enterprise. Assumes pipeline-orchestrated."
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
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - run_id: string, required, injected by orchestrator in pointer prompt
    - dev_branch: string, required, config
  raise.outputs: |
    - mr_url: string, terminal
---

# Bugfix Close

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-bugfix-close, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-bugfix-close
> Lean residue: 12 pasos [R9, G1, I2] de 26 en enterprise (54% ceremonia eliminada).
> Asume siempre pipeline-orchestrated — requiere run_id en el pointer prompt.

## Pipeline Context Check

Verificar que este skill fue invocado vía pipeline engine (RAISE-10715):

- Si `Run ID:` aparece en el contexto → continuar silenciosamente.
- Si **ausente** → STOP: "standalone execution detected — prior phases may have been skipped. Options: 1) continue anyway, 2) abort."

## Objetivo

Push del branch de bug, crear MR, y sincronizar Jira.

**Inputs:** Bug ID, `run_id` (inyectado por el orquestador), `{dev_branch}`.

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work bugfix {bug_key} --event start --phase close
```

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

Si falla sin escape hatch → **STOP**: el AR debe existir antes del close.

### 3.5. Detectar Path A (bugfix epic-scoped, RAISE-15901) [R]

```bash
CURRENT_BRANCH="$(git branch --show-current)"
```

Si `$CURRENT_BRANCH` empieza con `epic/` → este bugfix corrió Path A en rai-bugfix-start: no existe branch `bug/{issue_key}/{slug}` dedicada, los commits del fix viven directamente en la epic branch. **Saltar los pasos 4-5 (push + MR) y el paso 9 (delete de branch)** — no hay branch de bug que pushear, MRear ni borrar. Esos commits se integran cuando la epic misma cierra (`/rai-epic-close`), no por bugfix individual. Emitir advertencia visible: `⚠ Path A detectado ($CURRENT_BRANCH) — bugfix close se detiene antes de push/MR/branch-delete; estos commits se integran vía el MR de la epic.` Continuar con los pasos 6 (fixVersion), 8 (verificación Jira) y 10-11 (bind + señal de cierre).

Si `$CURRENT_BRANCH` NO empieza con `epic/` → Path B, comportamiento sin cambios, continuar normalmente.

### 4-5. Push + Crear MR [G] (Path B únicamente — ver paso 3.5)

Invoke `/rai-mr-create` — it handles push, gate suite, and MR creation
across SCM providers (GitLab, GitHub).

### 6. Asignar fixVersion [R]

```bash
rai backlog update {bug_key} -F 'fixVersions=[{"name": "{version}"}]'
```

Derivar `{version}` del manifest `branches.development` (ej. `release/3.1.0` → `3.1.0`).

### 8. Verificación post-transición delegada (blocking) [R]

No ejecutar `gate-close-jira-sync` directamente desde el skill: Jira todavía
no está en Done. Al devolver control, el siguiente `pipeline_advance` aplica
primero `target_status: done` y después ejecuta el gate en
`after:bug:close`.

Si el avance devuelve `gate_failed` para `after:bug:close` → **FAIL el close**.
No log-and-continue ni escape implícito. Corregir Jira y re-run.

### 9. Worktree-aware cleanup [R] (Path B únicamente — ver paso 3.5)

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

### 11. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work bugfix {bug_key} --event complete --phase close
```

**Fin.** Devolver: MR URL, gate-close-jira-sync status, cleanup realizado sí/no.
