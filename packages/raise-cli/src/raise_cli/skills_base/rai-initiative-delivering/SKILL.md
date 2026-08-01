---
name: rai-initiative-delivering
description: "Default variant: validate-only — verifies epic decomposition without creating artifacts. 3 steps vs 5 enterprise."
model: haiku

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(find *)"
  - "Bash(ls *)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-initiative
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: initiative
  raise.inputs: |
    - jira_key: string, required, argument (e.g. RAISE-14844)
    - initiative_slug: string, required, argument
    - treatment_md: file_path, required, previous_skill
    - mvp_spec_md: file_path, required, previous_skill
  raise.outputs: |
    - outcome: yaml_block, next_skill
---

# Initiative Delivering

> ℹ DEFAULT VARIANT (ADR-134 v2) — validate-only, no artifact creation.
> work_cycle: initiative | ADR-136 attribution contract: señales start/complete/blocked + outcome block.
> Lean residue: 3 pasos [R3] de 5 en enterprise (40% ceremonia eliminada).
> Solo validaciones [R] — no escribe artefactos, no crea epics, no hace design.

## Objetivo

Verificar que la initiative tiene al menos un epic descompuesto con scope.md. Validate-only: no crea artefactos, no modifica estado del árbol git. Inputs: jira_key, initiative_slug.

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work initiative {jira_key} --event start --phase delivering 2>/dev/null || true
```

### 1. Verificar work items bajo la iniciativa [R]

```bash
rai backlog search "parent={jira_key}" --limit 10 2>/dev/null || true
```

Si el backlog search falla (sin conexión) → continuar con validación de filesystem.

Verificar que existan epics hijos en el backlog. Si ninguno → **STOP**: "blocked: no epics found under {jira_key} — decompose into epics first".

### 2. Verificar epic scope en filesystem [R]

```bash
find work/epics/ -name "scope.md" -maxdepth 4 2>/dev/null | head -5
```

Debe existir al menos un `work/epics/**/scope.md`. Si no hay ninguno → **STOP**: "blocked: epic scope not found — create epic with scope.md before delivering".

### 3. Verificar al menos un epic en progreso o completo [R]

```bash
rai backlog search "parent={jira_key} AND status in ('In Progress', 'Done', 'Closed')" --limit 5 2>/dev/null || true
```

Si el backlog search falla → asumir ok (filesystem scope.md ya validado en paso anterior).

Si backlog responde y 0 epics en progreso/done → **STOP**: "blocked: no epic in-progress or done under {jira_key} — start epic work first".

Actualizar estado de la iniciativa en backlog:

```python
raise_backlog_update(
    issue_key="{jira_key}",
    fields={"status": "Delivering"}
)
```

Si falla → log y continuar (best-effort, backlog no bloquea delivering).

### 4. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work initiative {jira_key} --event complete --phase delivering 2>/dev/null || true
```

**STOP.** Devolver: epic scope paths validados, backlog status actualizado.
