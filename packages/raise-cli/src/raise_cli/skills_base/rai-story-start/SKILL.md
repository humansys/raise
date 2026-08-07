---
name: rai-story-start
description: "Canonical story start: fetch+merge + raise_story_open. Sin señales de observabilidad (raise_story_open las emite server-side). ADR-143 B1."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-story
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: story
  raise.inputs: |
    - story_id: string, required, argument (e.g. S14.1)
    - epic_dir: string, required, config
    - jira_key: string, optional, argument
  raise.outputs: |
    - story_branch: string, next_skill
    - story_md: file_path, next_skill
    - scope_md: file_path, next_skill
---

# Story Start

> ℹ DEFAULT VARIANT (ADR-143 B1) — colapso de rai-story-start + rai-story-start-lean.
> Señales eliminadas: raise_story_open (mcp_tools_story.py:72) ya las emite server-side.
> 5 pasos [R4, G1] de 14 en enterprise. Sin ShuHaRi, sin CLI fallbacks, sin checklist.

## Objetivo

Abrir una story con una llamada compuesta. Inputs: Story ID, epic dir, Jira key. Expected state: árbol limpio, worktree en branch correcto.

## Pasos

### 1. Sync dev branch — skip automático dentro de un worktree [R]

```bash
rai story sync-dev-branch -f json
```

Dentro de CUALQUIER worktree (registrado o no), este comando **nunca toca HEAD**
— no hay lógica de selección de branch dentro de un worktree, punto (Regla 2,
RAISE-15825). El HEAD del worktree ya refleja el contexto de branch con el que
fue creado (p.ej. un branch de epic); sincronizarlo contra el dev branch global
colapsaría ese contexto silenciosamente en cuanto ambos no hayan divergido
todavía. Fuera de un worktree, el comportamiento es el de siempre: fetch +
merge `--ff-only` contra el dev branch global.

| `status` (JSON) | Acción |
|------------------|--------|
| `ok` con `data.skipped: true` | Dentro de un worktree — HEAD no se tocó, correcto. Continuar. |
| `ok` (sin skip) | Sincronizado contra el dev branch. Continuar. |
| `warn` | Fetch falló pero no bloqueante (red intermitente, `origin` no configurado). Mencionar brevemente; continuar. |
| `blocked` (`dev-branch-diverged`) | **STOP**: "blocked: dev branch diverged — no force-merge". No improvises fix. |

### 2. Authoar story_content [R]

Connextra user story + Gherkin AC + SbE examples. Establecer frontmatter `jira_key={jira_key}` (gate-backlog-sync requiere este campo — RAISE-14588).

### 3. Authoar scope_content [G]

`## In Scope`, `## Out of Scope`, `## Done when` (outcomes observables).

### 4. Llamar raise_story_open [R]

```python
raise_story_open(
    story_id="{story_id}",
    slug="{slug}",
    epic_dir="{epic_dir}",
    jira_key="{jira_key}",
    story_content=story_content,
    scope_content=scope_content,
    cwd="{cwd}"
)
```

### 5. Manejar report [R]

| Estado | Acción |
|--------|--------|
| `status: ok` | Continuar — devolver branch, story.md path, scope.md path |
| `epic: blocked` | **STOP** — ejecutar `/rai-epic-start` primero |
| `branch: blocked` (`branch-exists`) | **STOP** — ¿retomar o eliminar branch? Nunca auto-resolver |
| `commit: blocked` | **STOP** — presentar razón; esperar al developer |
| `backlog/bind: warn` | Mencionar brevemente; continuar |

**STOP.** Devolver: branch creado, story.md path, scope.md path.
