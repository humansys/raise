---
name: rai-initiative-shaped
description: "Default variant: hypothesis → treatment.md + mvp-spec.md with Machine section (ADR-135). 4 steps vs 8 enterprise."
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(grep *)"
  - "Bash(cat *)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-initiative
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: initiative
  raise.inputs: |
    - initiative_id: string, required, argument (e.g. RAISE-14844)
    - initiative_slug: string, required, argument (e.g. lean-methodology)
    - initiative_dir: string, derived, path (e.g. work/initiatives/{slug})
    - jira_key: string, optional, argument
  raise.outputs: |
    - treatment_md: file_path, next_skill
    - mvp_spec_md: file_path, next_skill
---

# Initiative Shaped

> ℹ DEFAULT VARIANT (ADR-134 v2) — lean merge of enterprise shaped+validated phases.
> work_cycle: initiative | ADR-135 Machine section OBLIGATORIO en artefactos.
> ADR-136 attribution contract: emitir señales start/complete/blocked + outcome block.
> Lean residue: 4 pasos [R2, G2] (67% ceremonia enterprise eliminada).
> Solo pasos [R]+[G] — sin ShuHaRi, sin HITL gate (Ri mode), sin validación separada.

## Objetivo

Producir treatment.md + mvp-spec.md para una iniciativa en un solo paso (lean merge de enterprise shaped+validated). Inputs: initiative_id, initiative_slug. Expected state: iniciativa capturada, Theme parent registrado.

## ADR-135: Machine Section (OBLIGATORIO)

Cada artefacto escrito (treatment.md, mvp-spec.md) DEBE incluir sección `### Machine` con YAML estructurado. Esta sección es contexto inyectado por el orquestador en fases posteriores.

Formato requerido:

```markdown
### Machine
```yaml
modules_affected:
  - path: <repo_path_or_system_affected>
    change: create | modify | delete
decisions:
  - id: D1
    choice: "<decisión tomada>"
    rationale: "<por qué — una línea>"
    constraint: "<lo que NO está permitido>"
constraints:
  - "<invariante que el agente debe respetar>"
```
```

## Pasos

### 0. Emitir señal de inicio

```bash
rai signal emit-work initiative {jira_key} --event start --phase shaped 2>/dev/null || true
```

### 1. Graph query — patrones de iniciativas anteriores [R]

```python
raise_graph_query(
    query="patterns for initiative shaping hypothesis treatment mvp",
    strategy="concept_lookup",
    limit=5,
    format="compact"
    cwd="{project_or_worktree_path}"
)
```

0 resultados = válido, no es fallo. Continuar.

### 2. Validar inputs de shaping [R]

Verificar que la iniciativa tiene:
- Hipótesis claramente enunciada (problema + solución propuesta)
- Apetito definido (scope/budget/timeline rough)
- Bets framed (qué asumimos que es verdad para que esto funcione)
- Theme parent registrado en backlog

Si falta alguno → **STOP**: "blocked: shaping inputs incompletos — {campo_faltante} requerido antes de continuar".

### 3. Escribir treatment.md [G]

```python
raise_docs_write(
    doc_type="initiative-treatment",
    title="{initiative_id}: {initiative_slug} — Treatment",
    content="""### Human

## Iniciativa

**Hipótesis:** {hypothesis_statement}
**Outcome objetivo:** {target_outcome}
**Owner:** {owner}
**Theme parent:** {theme_parent}

## Tratamiento

**Problema:** {problem_statement}
**Valor propuesto:** {value_proposition}
**Enfoque:** {approach}
**Apetito:** {appetite} (tiempo/scope/presupuesto aproximado)

## Bets

{bet_1}
{bet_2}

### Machine
```yaml
modules_affected:
  - path: work/initiatives/{initiative_slug}/
    change: create
decisions:
  - id: D1
    choice: "{key_design_decision}"
    rationale: "{one_line_rationale}"
    constraint: "{what_is_not_allowed}"
constraints:
  - "No HITL gate en lean mode — decisión de portfolio queda documentada aquí"
  - "treatment.md y mvp-spec.md son artefactos de esta fase — no crear otros"
```
""",
    output_path="work/initiatives/{initiative_slug}/treatment.md",
    cwd="{cwd}"
)
```

Si `result.status != "ok"` → **STOP**: "treatment.md write failed: {error}". No continuar sin artefacto.

### 4. Escribir mvp-spec.md [G]

```python
raise_docs_write(
    doc_type="initiative-mvp-spec",
    title="{initiative_id}: {initiative_slug} — MVP Spec",
    content="""### Human

## MVP Specification

**Hipótesis medible:** {measurable_hypothesis}
**Métrica de éxito:** {success_metric} (cómo sabremos que funcionó)
**Scope mínimo:** {minimum_scope}
**Out of scope:** {out_of_scope}
**Epics planeados:** {planned_epics}
**Criterio de portfolio go/no-go:** {portfolio_criteria}

### Machine
```yaml
modules_affected:
  - path: work/initiatives/{initiative_slug}/
    change: modify
decisions:
  - id: D2
    choice: "{mvp_scope_decision}"
    rationale: "{one_line_rationale}"
    constraint: "{what_mvp_excludes}"
constraints:
  - "MVP spec debe tener hipótesis medible — sin métrica no puede avanzar a delivered"
  - "Epic decomposition ocurre en la fase delivering — no crear epics aquí"
```
""",
    output_path="work/initiatives/{initiative_slug}/mvp-spec.md",
    cwd="{cwd}"
)
```

Si `result.status != "ok"` → **STOP**: "mvp-spec.md write failed: {error}". No continuar sin artefacto.

El motor de pipeline transiciona el status de Jira vía `target_status`
declarado en `initiative.yaml` (fase `shaped` → `committed`) — esta skill
no escribe status (RAISE-15876).

### 5. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work initiative {jira_key} --event complete --phase shaped 2>/dev/null || true
```

**STOP.** Devolver: treatment.md path, mvp-spec.md path, initiative_slug.
