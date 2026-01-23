# Análisis Arquitectónico: Sistema Specify

**Fecha**: 2026-01-22
**Propósito**: Abstraer patrones del sistema `specify` para estandarizar comandos RaiSE
**Autor**: RaiSE Ontology Architect

---

## 1. Resumen Ejecutivo

El sistema `specify` implementa un **patrón de Command Orchestration** donde:

- Un **archivo Markdown** actúa como orquestador (define QUÉ hacer)
- **Scripts Bash** ejecutan operaciones atómicas (CÓMO hacerlo)
- **Templates** definen estructura de outputs (QUÉ produce)

Este patrón es candidato para estandarizar todos los comandos de RaiSE.

---

## 2. Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SPECIFY SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐                                               │
│  │   COMMAND FILE       │  speckit.1.specify.md                         │
│  │   (Orchestrator)     │  - Frontmatter (metadata, handoffs)           │
│  │                      │  - User Input section                         │
│  │                      │  - Outline (pasos numerados)                  │
│  │                      │  - Guidelines (contexto para LLM)             │
│  └──────────┬───────────┘                                               │
│             │                                                            │
│             │ invoca                                                     │
│             ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SCRIPTS LAYER                                  │   │
│  │                                                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │   │
│  │  │ create-new-     │  │ check-          │  │ update-agent-   │  │   │
│  │  │ feature.sh      │  │ prerequisites.sh│  │ context.sh      │  │   │
│  │  │                 │  │                 │  │                 │  │   │
│  │  │ - Crea branch   │  │ - Valida paths  │  │ - Parsea plan   │  │   │
│  │  │ - Crea dirs     │  │ - Valida files  │  │ - Actualiza     │  │   │
│  │  │ - Copia template│  │ - Output JSON   │  │   CLAUDE.md     │  │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │   │
│  │                              │                                    │   │
│  │                              ▼                                    │   │
│  │                    ┌─────────────────┐                           │   │
│  │                    │   common.sh     │                           │   │
│  │                    │   (shared)      │                           │   │
│  │                    │                 │                           │   │
│  │                    │ - get_repo_root │                           │   │
│  │                    │ - get_feature_  │                           │   │
│  │                    │   paths         │                           │   │
│  │                    │ - check_file    │                           │   │
│  │                    └─────────────────┘                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│             │                                                            │
│             │ usa                                                        │
│             ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    TEMPLATES LAYER                                │   │
│  │                                                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │   │
│  │  │ spec-template   │  │ plan-template   │  │ tasks-template  │  │   │
│  │  │ .md             │  │ .md             │  │ .md             │  │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │   │
│  │                                                                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                        │   │
│  │  │ agent-file-     │  │ checklist-      │                        │   │
│  │  │ template.md     │  │ template.md     │                        │   │
│  │  └─────────────────┘  └─────────────────┘                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Análisis del Command File (Orquestador)

### 3.1 Estructura del Archivo

```markdown
---
description: [Descripción concisa, 1 línea]
handoffs:
  - label: [Etiqueta visible]
    agent: [comando.siguiente]
    prompt: [Texto sugerido]
    send: true|false
---

## User Input
$ARGUMENTS

## Outline
[Pasos numerados con lógica de ejecución]

## Guidelines
[Contexto y reglas para el LLM]
```

### 3.2 Patrones Identificados en el Outline

| Patrón | Descripción | Ejemplo en specify |
|--------|-------------|-------------------|
| **Initialization** | Ejecutar scripts de setup/validación | `create-new-feature.sh --json` |
| **Template Loading** | Cargar template para estructura | `Load spec-template.md` |
| **Execution Flow** | Pasos numerados con decisiones | Steps 1-7 con branching |
| **Validation Loop** | Ciclo de validación con max iteraciones | "max 3 iterations" |
| **Error Handling** | Manejo explícito de errores | `If empty: ERROR "..."` |
| **Output Generation** | Escribir artefacto final | `Write to SPEC_FILE` |
| **Finalization** | Reportar y ofrecer handoff | "Report completion" |

### 3.3 Secciones Clave del Outline

```markdown
1. **Generate branch name** (Preprocessamiento)
   - Análisis de input
   - Generación de identificadores

2. **Check existing branches** (Validación)
   - Prevenir colisiones
   - Determinar siguiente número

3. **Run script** (Delegación a Bash)
   - `create-new-feature.sh --json "$ARGUMENTS"`
   - Parsear output JSON

4. **Load template** (Carga de estructura)
   - `spec-template.md`

5. **Execution flow** (Lógica de negocio)
   - Pasos condicionales
   - Manejo de ambigüedades

6. **Write output** (Generación de artefacto)
   - Usar template
   - Reemplazar placeholders

7. **Validation** (Quality Gate inline)
   - Checklist de calidad
   - Loop de corrección

8. **Report completion** (Finalización)
   - Resumen de lo creado
   - Handoff al siguiente comando
```

---

## 4. Análisis del Scripts Layer

### 4.1 Taxonomía de Scripts

| Script | Responsabilidad | Input | Output | Idempotente |
|--------|-----------------|-------|--------|-------------|
| `create-new-feature.sh` | Setup de feature | descripción, flags | JSON con paths | No (crea branch) |
| `check-prerequisites.sh` | Validación de estado | flags | JSON con paths/status | Sí |
| `update-agent-context.sh` | Sync de contexto | agent type | archivos actualizados | Sí |
| `common.sh` | Funciones compartidas | — | funciones bash | N/A |

### 4.2 Patrón de Comunicación Script ↔ LLM

```
┌─────────────┐         ┌─────────────┐
│    LLM      │         │   Script    │
│ (Orchestr.) │         │   (Bash)    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │  ./script.sh --json   │
       │ ───────────────────►  │
       │                       │
       │  {"KEY":"value",...}  │
       │ ◄───────────────────  │
       │                       │
       │  [LLM parsea JSON]    │
       │                       │
```

**Principio clave**: Scripts retornan JSON para comunicación estructurada.

### 4.3 Funciones Compartidas (common.sh)

```bash
# Funciones de contexto
get_repo_root()          # Encuentra raíz del repo
get_current_branch()     # Obtiene branch actual
has_git()                # Detecta si hay git

# Funciones de paths
get_feature_dir()        # Directorio de feature
get_feature_paths()      # Todos los paths relevantes
find_feature_dir_by_prefix()  # Búsqueda por prefijo numérico

# Funciones de validación
check_feature_branch()   # Valida naming de branch
check_file()             # Verifica existencia de archivo
check_dir()              # Verifica existencia de directorio
```

### 4.4 Patrón de Paths Centralizados

```bash
# get_feature_paths() retorna:
REPO_ROOT='...'
CURRENT_BRANCH='...'
HAS_GIT='true|false'
FEATURE_DIR='...'
FEATURE_SPEC='$FEATURE_DIR/spec.md'
IMPL_PLAN='$FEATURE_DIR/plan.md'
TASKS='$FEATURE_DIR/tasks.md'
RESEARCH='$FEATURE_DIR/research.md'
DATA_MODEL='$FEATURE_DIR/data-model.md'
QUICKSTART='$FEATURE_DIR/quickstart.md'
CONTRACTS_DIR='$FEATURE_DIR/contracts'
```

**Beneficio**: Todos los scripts usan los mismos paths, evitando inconsistencias.

---

## 5. Análisis del Templates Layer

### 5.1 Templates Disponibles

| Template | Comando que lo usa | Output |
|----------|-------------------|--------|
| `spec-template.md` | specify | `spec.md` |
| `plan-template.md` | plan | `plan.md` |
| `tasks-template.md` | tasks | `tasks.md` |
| `checklist-template.md` | (inline en specify) | `checklists/*.md` |
| `agent-file-template.md` | update-agent-context | `CLAUDE.md`, etc. |

### 5.2 Patrón de Placeholders

```markdown
# Template con placeholders
[PROJECT NAME]
[DATE]
[EXTRACTED FROM ALL PLAN.MD FILES]
[ACTUAL STRUCTURE FROM PLANS]
```

Los placeholders se reemplazan:
- Por el LLM (en commands)
- Por scripts (en update-agent-context.sh)

---

## 6. Patrones Abstractos para Estandarización

### 6.1 Command Contract (Interfaz de Comando)

Todo comando RaiSE debería seguir este contrato:

```yaml
# FRONTMATTER (Obligatorio)
---
description: string           # Una línea
handoffs:                     # Opcional
  - label: string
    agent: string
    prompt: string
    send: boolean
---

# SECTIONS (Obligatorias)
## User Input
$ARGUMENTS

## Outline
Goal: [descripción del objetivo]

1. **Initialize**: [setup y validación]
2. **Load Context**: [cargar inputs necesarios]
3. **Execute**: [lógica principal]
4. **Validate**: [quality gate inline]
5. **Finalize**: [output y handoff]

## Guidelines
[Reglas específicas para el LLM]
```

### 6.2 Script Contract (Interfaz de Script)

Todo script de soporte debería:

```bash
#!/usr/bin/env bash
set -e

# 1. Parse arguments (soportar --json, --help)
# 2. Source common.sh
# 3. Validate environment
# 4. Execute logic
# 5. Output JSON (si --json) o texto legible
```

### 6.3 Validation Pattern (Patrón de Validación)

```markdown
N. **Validate Output**:
   - Run validation against [criteria]
   - **If PASS**: Continue to finalize
   - **If FAIL**:
     - Attempt fix (max N iterations)
     - If still failing: STOP (Jidoka) and report
```

### 6.4 Handoff Pattern (Patrón de Transición)

```markdown
N. **Finalize**:
   - Confirm artifact created at [path]
   - Run [gate script] if applicable
   - Report summary:
     - Created: [files]
     - Next: [suggested command]
   - Offer handoff: "→ Continue with `/[next-command]`"
```

---

## 7. Recomendaciones para Estandarización

### 7.1 Estructura de Directorios Propuesta

```
.agent/
├── workflows/
│   ├── setup/
│   │   └── [commands].md
│   ├── project/
│   │   └── [commands].md
│   ├── feature/
│   │   └── [commands].md
│   └── tools/
│       └── [commands].md
│
├── scripts/
│   ├── bash/
│   │   ├── common.sh              # Funciones compartidas
│   │   ├── check-prerequisites.sh # Validación universal
│   │   └── [domain]/              # Scripts por dominio
│   │       └── [script].sh
│   └── pwsh/                      # PowerShell equivalents
│
└── templates/
    ├── commands/                  # Templates para outputs de comandos
    │   ├── spec-template.md
    │   ├── plan-template.md
    │   └── ...
    └── internal/                  # Templates para infra
        └── agent-file-template.md
```

### 7.2 Checklist de Estandarización por Comando

Para cada comando existente, verificar:

- [ ] **Frontmatter completo** (description, handoffs)
- [ ] **User Input section** presente
- [ ] **Outline con Goal** explícito
- [ ] **Initialization step** que usa `check-prerequisites.sh`
- [ ] **Validation step** antes de finalizar
- [ ] **Jidoka inline** (qué hacer si falla)
- [ ] **Handoff claro** al siguiente comando
- [ ] **Guidelines** específicas para el dominio

### 7.3 Scripts a Crear/Refactorizar

| Script | Propósito | Prioridad |
|--------|-----------|-----------|
| `validate-artifact.sh` | Validación genérica de artefactos | Alta |
| `init-feature-context.sh` | Setup de contexto para cualquier comando | Alta |
| `run-gate.sh` | Ejecutar validation gates | Media |

---

## 8. Aplicabilidad a Comandos RaiSE

### 8.1 Comandos que Ya Siguen el Patrón

| Comando | Usa scripts | Tiene validation | Tiene handoffs |
|---------|-------------|------------------|----------------|
| `speckit.1.specify` | ✅ | ✅ | ✅ |
| `speckit.3.plan` | ✅ | ✅ | ✅ |
| `speckit.4.tasks` | ✅ | ✅ | ✅ |
| `speckit.6.implement` | ✅ | ✅ | ✅ |

### 8.2 Comandos que Necesitan Refactorización

| Comando | Problema | Acción |
|---------|----------|--------|
| `raise.1.discovery` | No usa check-prerequisites | Agregar initialization |
| `raise.2.vision` | Handoffs incompletos | Revisar flujo |
| `raise.3.ecosystem` | Sin validation inline | Agregar Jidoka |
| `raise.rules.*` | Sin frontmatter estándar | Normalizar estructura |

### 8.3 Beneficios de Estandarización

1. **Consistencia**: Todos los comandos siguen el mismo patrón
2. **Mantenibilidad**: Cambios en scripts afectan a todos los comandos
3. **Discoverability**: Usuarios aprenden un patrón, aplican a todos
4. **Testabilidad**: Scripts pueden testearse independientemente
5. **Extensibilidad**: Nuevos comandos siguen el template

---

## 9. Conclusión

El sistema `specify` implementa un patrón maduro de **Command Orchestration** que puede abstraerse como estándar para todos los comandos RaiSE. Los elementos clave son:

1. **Markdown como orquestador** (QUÉ hacer)
2. **Bash como ejecutor** (CÓMO hacerlo)
3. **JSON como contrato** (comunicación estructurada)
4. **Templates como estructura** (QUÉ produce)
5. **Validation inline** (Jidoka built-in)
6. **Handoffs explícitos** (flujo continuo)

La adopción de este patrón para todos los comandos RaiSE resultará en una experiencia de desarrollador más coherente y predecible.

---

## Referencias

- `speckit.1.specify.md` — Comando principal analizado
- `check-prerequisites.sh` — Script de validación
- `create-new-feature.sh` — Script de setup
- `common.sh` — Funciones compartidas
- `update-agent-context.sh` — Script de contexto
- ADR-012 — Reestructuración de comandos (propuesto)

---

*Este análisis sirve como base para estandarizar la arquitectura de comandos en RaiSE v2.1.*
