---
name: rai-story-start
description: "Canonical story start: fetch+merge + raise_story_open. Sin señales de observabilidad (raise_story_open las emite server-side). ADR-143 B1."
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(git fetch *)"
  - "Bash(git merge *)"
  - "Bash(git branch --show-current)"
  - "Bash(git status *)"
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

### 1. Fetch + merge ff-only base branch [R]

```bash
DEV_BRANCH=$(python3 -c "import yaml; print(yaml.safe_load(open('.raise/manifest.yaml'))['branches']['development'])" 2>/dev/null || echo "release/3.1.0")
git fetch origin "$DEV_BRANCH"
git merge "origin/$DEV_BRANCH" --ff-only
```

Si `--ff-only` falla (árbol divergido) → **STOP**: "blocked: dev branch diverged — no force-merge". No improvises fix.

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
