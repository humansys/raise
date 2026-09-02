---
name: rai-epic-start
description: "Default variant: git status + raise_docs_write brief/scope + backlog. 3 steps vs 9 enterprise."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(git status *)"
  - "Bash(git branch --show-current)"
  - "Bash(git add *)"
  - "Bash(git commit *)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-epic
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: epic
  raise.inputs: |
    - epic_id: string, required, argument (e.g. E14770)
    - epic_slug: string, required, argument (e.g. lean-methodology)
    - epic_dir: string, derived, path (e.g. work/epics/e14770-lean-methodology)
    - jira_key: string, optional, argument
  raise.outputs: |
    - brief_md: file_path, next_skill
    - scope_md: file_path, next_skill
---

# Epic Start

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-epic-start, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-epic-start
> Lean residue: 3 pasos [R2, G1] de 9 en enterprise (67% ceremonia eliminada).
> Solo pasos [R]+[G] — sin ShuHaRi, sin directory collision explanation, sin quality checklist.

## Objetivo

Crear el epic_dir con brief.md + scope.md y registrar en backlog. Inputs: Epic ID, slug, Jira key opcional. Expected state: árbol limpio, en dev branch.

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work epic {jira_key} --event start --phase start
```

### 1. Verificar working tree [R]

```bash
git status --short
git branch --show-current
```

Si hay cambios uncommitted → **STOP**: "blocked: working tree not clean". NUNCA `git reset --hard`, `git clean -fd`, ni `git stash` sin confirmación explícita del developer.

### 2. Crear brief.md + scope.md [G]

Read `governance/guardrails.md` before drafting (graceful degradation: if absent, continue without blocking). Factor guardrails into rabbit holes and scope decisions.

Crear `work/epics/{epic_dir}/` y escribir dos artefactos:

```python
raise_docs_write(
    doc_type="epic-brief",
    title="{epic_id}: {epic-name} brief",
    content="[hipótesis, success metrics, appetite, rabbit holes]",
    output_path="work/epics/{epic_dir}/brief.md",
    cwd="{cwd}"
)
raise_docs_write(
    doc_type="epic-scope",
    title="{epic_id}: {epic-name} scope",
    content="[objetivo, in/out scope, historias planeadas, done criteria, jira_key si aplica]",
    output_path="work/epics/{epic_dir}/scope.md",
    cwd="{cwd}"
)
```

Si cualquier `result.status != "ok"` → **STOP**: "Epic artifact write failed: {error}". No continuar sin artefacto.

Commit (solo el epic_dir — nunca `git add -A`):

```bash
git add work/epics/{epic_dir}/
git commit -m "epic({epic_id}): initialize {epic-slug}

Objetivo: {1-line}

Co-Authored-By: Rai <rai@humansys.ai>"
```

### 3. Capturar portfolio metadata [G]

Si el argumento `--skip-portfolio` está presente en los argumentos del skill → saltar este paso.

Preguntar al developer (respuesta en texto libre):
- **`components_touched`**: lista de IDs de componentes del manifest (ej: `portfolio,storage,gates`)
- **`change_mode`**: uno de `additive` | `evolutionary` | `breaking`

Si jira_key no está vacío y el developer responde:

```bash
rai portfolio epic-profile create {jira_key} \
  --components {components_touched_comma_separated} \
  --change-mode {change_mode} \
  --project .
```

Si el developer pasa `--skip-portfolio` o prefiere no responder → continuar sin persistir (best-effort; no bloquear epic start).

### 4. Actualizar backlog [I]

Backlog transition is engine-owned (RAISE-15034) — no skill-initiated call.
Engine transitions epic to Implement via `apply_phase_transition` at phase completion.

Persistir jira_key en scope.md si no está ya.

### 5. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work epic {jira_key} --event complete --phase start
```

**STOP.** Devolver: epic_dir creado, brief.md path, scope.md path.
