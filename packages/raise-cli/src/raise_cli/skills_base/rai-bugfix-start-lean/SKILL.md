---
name: rai-bugfix-start-lean
description: "Lean residue de rai-bugfix-start: branch + reproduce + scope. 11 pasos vs 25 enterprise."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(git fetch *)"
  - "Bash(git checkout -b *)"
  - "Bash(git rev-parse *)"
  - "Bash(git branch --show-current)"
  - "Bash(git status *)"
  - "Bash(git add *)"
  - "Bash(git commit *)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-bug
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: bugfix-lean
  raise.inputs: |
    - bug_id: string, required, argument (e.g. RAISE-251)
    - dev_branch: string, required, config
    - fix_version: string, optional (disambiguates target release line — RAISE-17066)
  raise.outputs: |
    - bug_branch: string, next_skill
    - scope_md: file_path, next_skill
---

# Bugfix Start (Lean)

> ⚠ LEAN VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-bugfix-start, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-bugfix-start
> Lean residue: 11 pasos [R6, G2, I3] de 25 en enterprise (56% ceremonia eliminada).

## Objetivo

Crear branch de bug, reproducir el defecto, y escribir el scope artifact. Solo pasos [R]+[G]+[I] — sin ceremony (ADR-134 v2).

**Inputs:** Bug ID (e.g. RAISE-251). **Expected state:** Árbol limpio.

## Pasos

### 1. Verificar working tree [R]

```bash
git rev-parse --show-toplevel
git status --short
```

Si el toplevel es inesperado o hay cambios uncommitted → **STOP**: "blocked: working tree inesperado". No improvises fix. NUNCA `git reset --hard` ni `git clean -fd`.

### 2. Resolver dev_branch desde el manifest [R]

```bash
# RAISE-17066: target declarado en .raise/manifest.yaml (branches.release_lines[] /
# branches.development), nunca inferido de origin/release/*. Ambigüedad falla ruidoso.
RESOLVED="$(rai worktree resolve-base --work-type bugfix ${fix_version:+--fix-version "$fix_version"} -f json)" \
  || { echo "blocked: target branch ambiguo — pasar fix_version o corregir branches.release_lines"; exit 1; }
DEV_BRANCH="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['branch'])")"
BASE_REF="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['base_ref'])")"
```

Presentar `data.warnings` verbatim si los hay.

### 3. Crear branch [R]

```bash
git checkout -b bug/{issue_key}/{bug-slug} "$BASE_REF"
```

Si el branch ya existe → **STOP**: "blocked: branch ya existe — ¿retomar o eliminar?"

### 4. Reproducir bug [R]

Confirmar que el bug es observable antes de investigar. **No investigar sin reproducir.** Si no se puede reproducir → **STOP**: documentar y escalar.

### 5. Escribir scope artifact [G]

```python
raise_docs_write(
    doc_type="bugfix-scope",
    title="{issue_key}: scope",
    content="WHAT: {behavior}\nWHEN: {conditions}\nWHERE: {file:line}\nEXPECTED: {correct}\nDone when: {criteria}",
    output_path="work/bugs/{issue_key}/scope.md",
    cwd="{cwd}"
)
```

### 6. Commit scope artifact [G]

```bash
git add work/bugs/{issue_key}/scope.md
git commit -m "bug({issue_key}): initialize scope

WHAT: {summary}
Done when: {criteria}

Co-Authored-By: Rai <rai@humansys.ai>"
```

### 7. Bind session a Jira key [I]

```python
raise_session_bind(key="RAISE_SESSION_JIRA_KEY", value="{bug_key}", cwd="{project_or_worktree_path}")
```

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:bugfix:start
```

**STOP.** Devolver: branch creado, scope.md path, bug reproducido sí/no.
