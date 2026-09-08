---
name: rai-bugfix-fix
description: "Default variant: TDD + gates + quality-review. 11 steps vs 19 enterprise, no HITL per-task."
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Bash

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-bug
  raise.gate: gate-code
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, from_previous
  raise.outputs: |
    - code_commits: list, git
---

# Bugfix Fix

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-bugfix-fix, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-bugfix-fix
> Lean residue: 11 pasos [R9, G1, I1] de 19 en enterprise (42% ceremonia eliminada).
> Eliminado: HITL per-task pause (paso 9 del enterprise), bloques verification/if-blocked, checklist.

## Objetivo

Ejecutar el fix con TDD estricto. Sin esperar acknowledgment per-task — ejecución autónoma (Ri mode). La calidad la garantizan los gates y el quality-review al final.

**Inputs:** Bug ID, scope.md (producido por diagnose). **Expected state:** En bug branch, árbol limpio.

**Excepción — Path A (bugfix epic-scoped, RAISE-15901):** si el commit inicial de scope.md incluye trailer `Epic:`, rai-bugfix-start corrió Path A y este fix vive sobre `epic/*`, no sobre `bug/*` — es el estado esperado para ese caso, no un working tree inesperado.

## Por cada task del scope

### 0. Emitir señal de inicio

```bash
rai signal emit-work bugfix {bug_key} --event start --phase implement
```

### 1. RED [R]
Escribir test fallido que define el comportamiento esperado.

### 2. GREEN [R]
Escribir código mínimo que hace pasar el test.

### 3. REFACTOR [R]
Limpiar mientras los tests siguen verdes.

### 4. Ejecutar 4 gates [R]

**Environment setup (mandatory — eliminates RC2 path errors, RAISE-15430 AC2):**
Use absolute paths for all file operations: `$WORKTREE_ROOT/<relative-path>`.

```bash
WORKTREE_ROOT=$(git rev-parse --show-toplevel)
uv run ruff format "$WORKTREE_ROOT/packages/<changed-package>/"  # fix first (PAT-E-772, RAISE-15429)
git add -u
rai gate check gate-tests --scope {changed_test_path}
rai gate check gate-lint
rai gate check gate-format
rai gate check gate-types
```

**Interface lookup (RC1, RAISE-15431) — query before you guess.** Before invoking any `rai <cmd>` subcommand or `raise_cli` import you have NOT verified this session:
1. Query the graph: `rai graph query "<cmd> <subcommand>" --types symbol --limit 3`
   - For Jira transitions/priorities: `rai graph query "jira transition workflow" --types pattern` (PAT-F-1826 has the RAISE workflow; PAT-E-9996..9998 have priority/issue-type/transition values)
   - For SCM tools (glab, gh): `rai graph query "glab/gh <cmd> <subcommand>" --types pattern --limit 3` (glab/gh have no Python symbols — PAT-E-10000..10009 cover flags, 409/404 errors, glab vs gh distinctions)
   - For SQLite/raise.db schema: `rai graph query "raise.db <table> schema" --types pattern --limit 3` (schema is not in code symbols — PAT-E-9999..10007 have column lists)
2. Fallback if 0 results: `rai <cmd> --help` | for SCM tools: `glab/gh <cmd> --help` | for DB: `sqlite3 db ".schema"`
Skip when the interface was already verified this session. One query beats a spiral of guessed-flag retries (70% of RC1 errors spiral).

Si un gate falla → fijar y re-verificar (máx 3 intentos). Si persiste → **STOP**: documentar blocker, escalar.

### 5. Commit por task [G]

```bash
git add {files}
git commit -m "{commit message from plan}"
```

### 6. Si hay más tasks → volver al paso 1 [R]

### 7. Quality review de la implementación [R]

```bash
git diff --name-only $(git merge-base HEAD {dev_branch})..HEAD
```

Invocar `/rai-quality-review` sobre los archivos cambiados.

| Veredicto | Acción |
|-----------|--------|
| PASS / PASS WITH RECOMMENDATIONS | Continuar |
| FAIL | Atender findings críticos, re-run gates, continuar |

### 8. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work bugfix {bug_key} --event complete --phase implement
```

**STOP.** Devolver: commits realizados, veredicto QR, gate status.

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:bugfix:fix
```
