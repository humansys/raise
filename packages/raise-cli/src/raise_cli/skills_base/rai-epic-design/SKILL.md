---
name: rai-epic-design
description: "Default variant: graph query + code read + story breakdown + ADR-135 artifacts. Produces scope.md + design.md with Machine section."
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
  raise.fase: '3'
  raise.frequency: per-epic
  raise.gate: ''
  raise.skillset: raise-maintainability
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: epic
  raise.inputs: |
    - brief_md: file_path, optional, previous_skill
    - scope_md: file_path, required, previous_skill
    - epic_dir: string, required, config
    - jira_key: string, optional, argument
  raise.outputs: |
    - scope_md: file_path, next_skill
    - design_md: file_path, next_skill
---

# Epic Design

> ℹ DEFAULT VARIANT (ADR-134 v2) — si cambias lógica [R]/[G] en rai-epic-design, propaga aquí.
> Fuente: work/epics/e14770-lean-methodology/skill-audit.md §rai-epic-design
> Lean residue: 5 pasos [R3, G2] de 14 en enterprise (57% ceremonia eliminada).
> ADR-135: cada artefacto escrito DEBE incluir sección `### Machine` con YAML estructurado.

## Objetivo

Diseñar el scope ejecutable del epic: leer código real, descomponer en historias, escribir scope.md + design.md con Machine sections (ADR-135). Inputs: epic_dir, brief.md/scope.md anteriores.

## ADR-135: Machine Section (OBLIGATORIO)

Cada artefacto escrito (scope.md, design.md) DEBE incluir sección `### Machine` con YAML estructurado. Esta sección es contexto inyectado por el orquestador en fases posteriores.

Formato requerido:

```markdown
### Machine
```yaml
modules_affected:
  - path: packages/raise-cli/src/raise_cli/<module>/
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
rai signal emit-work epic {jira_key} --event start --phase implement
```

### 1. Graph query (1 llamada) [R]

```python
raise_graph_query(
    query="patterns for {epic_domain} architecture decisions",
    strategy="concept_lookup",
    limit=5,
    format="compact"
    cwd="{project_or_worktree_path}"
)
```

0 resultados = válido, no es fallo. Continuar.

### 2. Leer módulos afectados [R]

Leer el código real que este epic tocará. No diseñar sobre abstracciones. 1-3 archivos clave.

```bash
grep -r "{domain_pattern}" packages/raise-cli/src/ --include="*.py" -l
```

**Portfolio context** — fail-open:

```bash
rai portfolio suggest "$JIRA_KEY" 2>/dev/null || true
```

Si produce output → usar `components_touched` y `change_mode` como punto de partida para la lista de módulos afectados en el paso 3 y en los artefactos scope.md/design.md. Si no produce output, continuar sin contexto de portafolio — no bloquear.

| Hallazgo | Acción |
|----------|--------|
| Componente similar existe | Reusar o extender — NO proponer historia duplicada |
| Patrón establecido encontrado | Seguirlo — consistencia > novedad |

Read `governance/prd.md` and `governance/vision.md` before decomposing (graceful degradation: if absent or placeholder-only, continue without blocking). Use PRD requirements and Vision outcomes to answer the waste filter — a story that serves no requirement or outcome is a deferral candidate.

### 3. Descomponer en historias [R]

3-10 historias independientes y entregables. Por historia: ID (S{N}.{seq}), nombre, descripción 1-línea, tamaño (XS/S/M/L), dependencias.

Filtro de waste: "¿Qué pasa si no la construimos?" — si el epic igual logra su objetivo, diferir.

ADR si aplica (decisión arquitectónica significativa, múltiples enfoques válidos). Un ADR por decisión.

### 4. Escribir scope.md [G]

```python
raise_docs_write(
    doc_type="epic-scope",
    title="{epic_id}: {epic-name} scope",
    content="""[objetivo, in/out scope, historias planeadas, done criteria]

### Machine
```yaml
modules_affected:
  - path: <path>
    change: <create|modify|delete>
decisions:
  - id: D1
    choice: "<decisión>"
    rationale: "<razón>"
    constraint: "<restricción>"
constraints:
  - "<invariante>"
```
""",
    output_path="work/epics/{epic_dir}/scope.md",
    cwd="{cwd}"
)
```

Si `result.status != "ok"` → **STOP**: "scope.md write failed: {error}".

### 5. Escribir design.md [G]

```python
raise_docs_write(
    doc_type="epic-design",
    title="{epic_id}: {epic-name} design",
    content="""[hallazgos gemba, componentes objetivo, contratos clave]

### Machine
```yaml
modules_affected:
  - path: <path>
    change: <create|modify|delete>
decisions:
  - id: D1
    choice: "<decisión>"
    rationale: "<razón>"
    constraint: "<restricción>"
constraints:
  - "<invariante>"
```
""",
    output_path="work/epics/{epic_dir}/design.md",
    cwd="{cwd}"
)
```

Si `result.status != "ok"` → **STOP**: "design.md write failed: {error}".

Ambos documentos son obligatorios. Para epics simples, design.md es corto (hallazgos gemba + enfoque), no ausente.

### 6. Emitir outcome + señal de cierre

Emitir bloque outcome antes de devolver control:

```yaml
outcome:
  verdict: PASS  # PASS | FAIL | BLOCKED
  route: standard  # standard | escape | blocked
  blocked_reason: null  # string if BLOCKED, null otherwise
```

```bash
rai signal emit-work epic {jira_key} --event complete --phase implement
```

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:epic:design
```

**STOP.** Devolver: scope.md path, design.md path, historias descompuestas (lista), ADRs creados si aplica.
