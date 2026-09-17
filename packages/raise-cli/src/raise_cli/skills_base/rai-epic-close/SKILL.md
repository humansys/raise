---
name: rai-epic-close
description: "Default variant: retrospectiva + tag + fixVersion. 3 steps vs 8 enterprise. Transitions engine-owned (RAISE-15034)."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(git tag *)"
  - "Bash(git add *)"
  - "Bash(git commit *)"
  - "Bash(git status *)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '9'
  raise.frequency: per-epic
  raise.gate: gate-tests
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: epic
  raise.inputs: |
    - scope_md: file_path, required, previous_skill
    - epic_dir: string, required, config
    - jira_key: string, optional, argument
  raise.outputs: |
    - retrospective_md: file_path, file
    - tag: string, git
---

# Epic Close

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-epic-close, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-epic-close
> Lean residue: 3 pasos [R2, G1] de 8 en enterprise (63% ceremonia eliminada).
> Ceremonia eliminada: invocación-fuera-de-pipeline HITL, Jira child reconciliation, ShuHaRi.

## Pipeline Context Check

Verificar que este skill fue invocado vía pipeline engine (RAISE-10715):

- Si `Run ID:` aparece en el contexto → continuar silenciosamente.
- Si **ausente** → STOP: "standalone execution detected — prior phases may have been skipped. Options: 1) continue anyway, 2) abort."

## Objetivo

Cerrar epic con retrospectiva y actualizar backlog. Expected state: todas las historias del epic completas y mergeadas.

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work epic {jira_key} --event start --phase close
```

### 1. Verificar scope.md — historias completas [R]

Leer `work/epics/{epic_dir}/scope.md`. Verificar que todas las historias estén marcadas done.

```bash
grep -E "^\s*-\s*\[ \]" "work/epics/{epic_dir}/scope.md"
```

Si hay historias incompletas → **STOP**: "blocked: incomplete stories in scope.md — complete them first or explicitly descope."

### 2. Escribir retrospectiva + tag [G]

```python
raise_docs_write(
    doc_type="retrospective",
    title="{epic_id}: {epic-name} — Retrospective",
    content="[patrones aprendidos, métricas, insights de proceso]",
    output_path="work/epics/{epic_dir}/retrospective.md",
    cwd="{cwd}"
)
```

Emitir artefacto retro (requerido por pipeline validates):

```python
raise_artifact_emit(
    artifact_type="retro",
    story_id="{JIRA_KEY}",
    content={"patterns_learned": [...], "reinforcements": [...], "notes": "..."}
    cwd="{project_or_worktree_path}"
)
```

Tag del milestone:

```bash
git add work/epics/{epic_dir}/
git commit -m "epic({epic_id}): close with retrospective

Co-Authored-By: Rai <rai@humansys.ai>"
git tag -a "epic/{epic_dir}-complete" -m "Epic {epic_id} complete"
```

### 3. Backlog update [R]

Backlog transition is engine-owned (RAISE-15034) — no skill-initiated call:
- **Pipeline de setup** (Run ID present, RAISE-15019): engine transitions epic to implement status at phase end.
- **Post-stories** context: engine transitions epic to done via terminal-close gate (RAISE-10966).
**Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

Asignar fixVersion del dev branch (e.g. release/X.Y.Z → X.Y.Z):

```bash
rai backlog update {jira_key} -F 'fixVersions=[{"name": "{version}"}]'
```

Si la asignación de fixVersion falla → **STOP**: "fixVersion assignment failed — epic close cannot complete with stale status."

### 4. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work epic {jira_key} --event complete --phase close
```

**STOP.** Devolver: retrospective.md path, tag creado, backlog actualizado.

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:epic:close
```
