---
name: rai-bugfix-start
description: "Default variant: branch + reproduce + scope. 11 steps vs 25 enterprise."
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
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument (e.g. RAISE-251)
    - dev_branch: string, required, config
  raise.outputs: |
    - bug_branch: string, next_skill
    - scope_md: file_path, next_skill
---

# Bugfix Start

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-bugfix-start, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-bugfix-start
> Lean residue: 11 pasos [R6, G2, I3] de 25 en enterprise (56% ceremonia eliminada).

## Objetivo

Crear branch de bug, reproducir el defecto, y escribir el scope artifact. Solo pasos [R]+[G]+[I] — sin ceremony (ADR-134 v2).

**Inputs:** Bug ID (e.g. RAISE-251). **Expected state:** Árbol limpio.

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work bugfix {issue_key} --event start --phase start
```

### 1. Verificar working tree [R]

```bash
git rev-parse --show-toplevel
git status --short
```

Si el toplevel es inesperado o hay cambios uncommitted → **STOP**: "blocked: working tree inesperado". No improvises fix. NUNCA `git reset --hard` ni `git clean -fd`.

### 2. Reconciliar dev_branch contra remoto [R]

```bash
git fetch origin
LOCAL_DEV="$(grep 'development:' .raise/manifest.yaml | awk '{print $2}' | tr -d ' ')"
REMOTE_DEV="$(git branch -r --list 'origin/release/*' | sed 's|.*origin/||' | sort -V | tail -1)"
```

Si `LOCAL_DEV != REMOTE_DEV` → usar `REMOTE_DEV` como `{dev_branch}`, advertir al developer.
Si no hay `origin/release/*` → usar `LOCAL_DEV`.

### 3. Detectar contexto de branch y crear/reutilizar branch [R]

```bash
CURRENT_BRANCH="$(git branch --show-current)"
EPIC_KEY="$(echo "$CURRENT_BRANCH" | sed -nE 's|^epic/([A-Z]+-[0-9]+).*|\1|p')"
```

**Path A — `$CURRENT_BRANCH` empieza con `epic/` (RAISE-15901, RAISE-15765):** el prefijo de branch es la señal PRIMARIA y BASTA por sí solo — **no** la condiciones a que `rai backlog get {issue_key}` → `parent` coincida con `$EPIC_KEY`. En este proyecto los bugs suelen estar parentados a epics de planeación (ej. RAISE-15979) y no a la epic de ejecución que realmente posee la branch (ej. RAISE-15851), y muchos bugs no tienen `parent` seteado en Jira en absoluto — condicionar al parent deja el fix inerte para su propio caso motivador (RAISE-15765 nunca tuvo parent y volvería a orfandarse en silencio). Esto cubre tanto `epic/RAISE-{N}-*` como formas legacy sin key JIRA (`epic/e15736-...`, `epic/e2099-...`, `epic/e-mission-lifecycle-governance`); en esos casos `$EPIC_KEY` queda vacío y el trailer `Epic:` del paso 6 se omite, pero sigue siendo Path A.

Si `$CURRENT_BRANCH` empieza con `epic/` → **NO crear branch nuevo**. Permanecer en `$CURRENT_BRANCH` y commitear el scope ahí mismo en el paso 6. Esto evita orfandar el bug: si se hiciera `checkout -b ... origin/{dev_branch}`, el working tree perdería acceso a design.md/ADRs/evidence que solo existen como commits sin mergear en la epic branch.

Confirmación secundaria (best-effort, informativa — NUNCA gating): si `$EPIC_KEY` no está vacío, intentar rai worktree context (stories asociadas al worktree, ADR-130) y/o `rai backlog get {issue_key}` → `parent`. Si ninguna confirma la asociación epic↔issue, **no caer a Path B en silencio**: imprimir advertencia visible — `⚠ Path A activado por nombre de branch ($CURRENT_BRANCH); no se pudo confirmar la asociación epic↔issue vía worktree/Jira parent — verificar manualmente.` — y continuar en Path A de todos modos.

**Path B — `$CURRENT_BRANCH` no empieza con `epic/` (standalone, comportamiento por defecto sin cambios):**

```bash
git checkout -b bug/{issue_key}/{bug-slug} origin/{dev_branch}
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

Path A (`$EPIC_KEY` no vacío): agregar una línea `Epic: {EPIC_KEY}` entre `Done when:` y `Co-Authored-By:`. Path A con `$EPIC_KEY` vacío (branch legacy sin key JIRA) o Path B: omitir esa línea por completo — nunca dejar el placeholder ni un comentario dentro del mensaje real.

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

### 9. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work bugfix {issue_key} --event complete --phase start
```

**STOP.** Devolver: branch creado, scope.md path, bug reproducido sí/no.
