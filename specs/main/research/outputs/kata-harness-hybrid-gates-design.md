# Kata Harness: Hybrid Gates Architecture (Option B)

**Research ID**: RES-KATA-HARNESS-002
**Date**: 2026-01-29
**Status**: Design Specification (Ready for Implementation)
**Target Timeline**: 1-2 weeks implementation

---

## Executive Summary

**What**: A middle-ground kata execution system that keeps markdown authoring but adds deterministic enforcement through bash-based gates.

**Why**: Balance contributor simplicity (markdown) with execution reliability (deterministic checks) without the complexity of a full compiled harness.

**How**: Pre-gates block execution if prerequisites fail. Post-gates validate outputs. Jidoka hooks pause on errors. JSONL traces provide observability.

**Approach**: **Declarative YAML configs + Generic Gate Runner** (no scripts por kata).

**Comparison**: Hybrid Gates is 70% of Full Harness enforcement with 20% of implementation cost.

---

## 1. Design Principles

### 1.1 Core Tenets

1. **Keep Markdown Authoring** - Contributors write katas in markdown (familiar, low barrier to entry)
2. **Add Deterministic Gates** - Bash scripts that MUST pass (actual enforcement, not LLM interpretation)
3. **Jidoka as Hook** - Shell-based triggers that can block execution at any step
4. **Minimal Infrastructure** - No state machine, no compilation, just scripts + conventions
5. **Incremental Adoption** - Existing katas work unchanged; gates are additive

### 1.2 What Changes from Current State

| Aspect | Current (LLM-only) | Hybrid Gates |
|--------|-------------------|--------------|
| Kata format | Markdown | Markdown (unchanged) |
| Execution flow | LLM interprets markdown | **PRE-GATE → LLM executes → POST-GATE** |
| Enforcement | None (LLM may skip steps) | **Deterministic checks block progress** |
| Observability | None | **JSONL trace of all events** |
| Prerequisites | LLM checks informally | **Bash script validates, blocks if fail** |
| Output validation | Manual review | **Automated gate validation** |
| Jidoka | LLM interprets "Si no puedes continuar" | **Shell script detects condition, pauses execution** |

### 1.3 What Stays the Same

- Markdown kata files (no new DSL to learn)
- LLM executes the kata steps (no change to execution model)
- Git-based versioning (no new tooling)
- Readable diffs (markdown stays human-friendly)

---

## 2. Architecture

### 2.1 Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   KATA EXECUTION FLOW                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. USER INVOKES KATA                                        │
│     $ /raise.1.discovery --context "..."                     │
│                                                              │
│  2. PRE-GATE EXECUTION (deterministic, blocks on fail)       │
│     ┌─────────────────────────────────────────────┐          │
│     │ .raise/gates/pre-discovery.sh               │          │
│     │   - Check context docs exist (any)          │          │
│     │   - Check specs/main/ writable              │          │
│     │   - Check template exists                   │          │
│     │                                             │          │
│     │ EXIT CODE:                                  │          │
│     │   0 = PASS → Continue to step 3             │          │
│     │   1 = FAIL → Block, show error + recovery   │          │
│     └─────────────────────────────────────────────┘          │
│                                                              │
│  3. LLM EXECUTES KATA STEPS (as today)                       │
│     - Read markdown instructions                            │
│     - Execute steps                                         │
│     - Generate output files                                 │
│                                                              │
│     [JIDOKA HOOK: Optional inline checks during execution]   │
│     - Shell scripts can be invoked from kata steps          │
│     - If check fails → Pause, show recovery guidance        │
│                                                              │
│  4. POST-GATE EXECUTION (deterministic, blocks on fail)      │
│     ┌─────────────────────────────────────────────┐          │
│     │ .raise/gates/post-discovery.sh              │          │
│     │   - Verify output file exists               │          │
│     │   - Check frontmatter valid                 │          │
│     │   - Count sections (≥ threshold)            │          │
│     │   - Validate references                     │          │
│     │                                             │          │
│     │ EXIT CODE:                                  │          │
│     │   0 = PASS → Complete, offer handoff        │          │
│     │   1 = FAIL → Jidoka stop, show what's wrong │          │
│     └─────────────────────────────────────────────┘          │
│                                                              │
│  5. TRACE LOGGING (every event appended to JSONL)           │
│     .raise/traces/kata-execution.jsonl                       │
│     {"event": "gate_start", "gate": "pre-discovery", ...}    │
│     {"event": "gate_pass", "gate": "pre-discovery", ...}     │
│     {"event": "kata_start", "kata": "discovery", ...}        │
│     {"event": "kata_complete", "kata": "discovery", ...}     │
│     {"event": "gate_start", "gate": "post-discovery", ...}   │
│     {"event": "gate_fail", "gate": "post-discovery", ...}    │
│                                                              │
│  6. OUTPUT                                                   │
│     - On SUCCESS: Show summary, offer handoff                │
│     - On FAILURE: Show gate failure, recovery steps          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

```
.raise/
├── gates/                      # Gate scripts (bash)
│   ├── pre-discovery.sh        # Check prerequisites for discovery
│   ├── post-discovery.sh       # Validate PRD output
│   ├── pre-vision.sh           # Check vision prerequisites
│   ├── post-vision.sh          # Validate solution vision output
│   ├── pre-design.sh           # Check design prerequisites
│   ├── post-design.sh          # Validate tech design output
│   └── lib/
│       ├── validators.sh       # Reusable validation functions
│       ├── yaml-parser.sh      # YAML frontmatter extraction
│       └── reporting.sh        # Error formatting and recovery guidance
│
├── traces/                     # Execution traces (gitignored)
│   └── kata-execution.jsonl    # Append-only event log
│
└── harness/                    # Orchestration scripts
    ├── run-kata.sh             # Main orchestrator
    ├── run-gate.sh             # Gate runner (PRE/POST)
    └── jidoka.sh               # Jidoka hook handler

.claude/commands/               # Kata commands (markdown, unchanged)
├── 01-onboarding/
│   └── raise.1.analyze.code.md
├── 02-projects/
│   ├── raise.2.vision.md
│   └── raise.3.ecosystem.md
└── ...

Katas declare gates in frontmatter:
---
description: ...
gates:
  pre: .raise/gates/pre-discovery.sh
  post: .raise/gates/post-discovery.sh
---
```

---

## 3. Gate Specification

### 3.1 Declarative Gate Design (YAML + Generic Runner)

**Insight**: En lugar de scripts bash especializados por kata, usamos **configuración declarativa** ejecutada por un **validador genérico**. Esto es más mantenible, legible y extensible.

**Arquitectura:**

```
.raise/gates/
├── discovery.yaml       ← Configuración declarativa
├── vision.yaml          ← Configuración declarativa
├── design.yaml          ← Configuración declarativa
└── lib/
    ├── gate-runner.sh   ← Validador genérico (UNO SOLO)
    └── validators.sh    ← Funciones de validación reutilizables
```

**Ventajas sobre scripts por kata:**

| Aspecto | Scripts por kata | Config + Runner |
|---------|------------------|-----------------|
| Mantenibilidad | ❌ N scripts | ✅ 1 runner + N configs |
| Legibilidad | ⚠️ Bash code | ✅ YAML declarativo |
| Reutilización | ⚠️ Copy-paste | ✅ Validators compartidos |
| Agregar kata | Escribir script | Agregar YAML |
| Testing | Ejecutar script | Parsear YAML + unit test validators |
| Governance-as-Code | ⚠️ Code | ✅ Config versionable |

### 3.2 Gate Configuration Format (YAML)

**Location**: `.raise/gates/{kata-id}.yaml`

**Schema**:

```yaml
# .raise/gates/discovery.yaml
# Gate configuration for discovery kata
---
kata_id: discovery
version: 1.0.0
output_file: specs/main/project_requirements.md

pre:
  # Check 1: At least one context document exists
  - id: context_docs
    check: any_file_exists
    paths:
      - docs/context.md
      - docs/product-brief.md
      - docs/business-case.md
      - README.md
    severity: warning  # Don't block, just warn
    message: "No context documents found. PRD will be based solely on user input."

  # Check 2: Output directory is writable
  - id: output_writable
    check: directory_writable
    path: specs/main/
    severity: error  # Block execution
    message: "Cannot write to specs/main/. Check permissions."
    recovery: "Run: chmod u+w specs/main/"

  # Check 3: Template exists
  - id: template_exists
    check: file_exists
    path: .specify/templates/raise/solution/project_requirements.md
    severity: error
    message: "PRD template not found. RaiSE installation may be incomplete."
    recovery: "Re-run RaiSE setup or check .specify/templates/ directory."

post:
  # Check 1: PRD file was created
  - id: prd_exists
    check: file_exists
    path: "{{output_file}}"  # Interpolates to specs/main/project_requirements.md
    severity: error
    message: "PRD file not generated."

  # Check 2: Frontmatter has required field
  - id: frontmatter_titulo
    check: frontmatter_field
    path: "{{output_file}}"
    field: titulo
    severity: error
    message: "PRD missing 'titulo' field in frontmatter."

  # Check 3: Minimum functional requirements
  - id: min_functional_requirements
    check: count_pattern
    path: "{{output_file}}"
    pattern: "^### FR-[0-9]+"
    min: 5
    severity: error
    message: "Insufficient functional requirements (found: {{count}}, expected: ≥5)."
    recovery: "Add more functional requirements to the PRD."

  # Check 4: Each FR has acceptance criteria
  - id: acceptance_criteria
    check: sections_have_subsection
    path: "{{output_file}}"
    section_pattern: "^### FR-[0-9]+"
    subsection: "Criterios de Aceptación"
    severity: error
    message: "Some requirements missing 'Criterios de Aceptación' section."

  # Check 5: Non-functional requirements (warning only)
  - id: nfr_section
    check: section_present
    path: "{{output_file}}"
    section: "## Requisitos No Funcionales"
    severity: warning
    message: "No non-functional requirements section. Consider adding performance, security, etc."

  # Check 6: Success criteria
  - id: success_criteria
    check: section_present
    path: "{{output_file}}"
    section: "## Criterios de Éxito"
    severity: warning
    message: "No success criteria section. Recommend defining measurable project goals."
```

### 3.3 Built-in Validators

El `gate-runner.sh` soporta estos tipos de checks:

| Check Type | Descripción | Parámetros |
|------------|-------------|------------|
| `file_exists` | Verifica que un archivo existe | `path` |
| `directory_writable` | Verifica que un directorio es escribible | `path` |
| `any_file_exists` | Al menos uno de los archivos existe | `paths[]` |
| `frontmatter_field` | Campo YAML frontmatter presente | `path`, `field` |
| `section_present` | Sección markdown existe | `path`, `section` |
| `count_pattern` | Cuenta ocurrencias de patrón | `path`, `pattern`, `min`, `max` |
| `sections_have_subsection` | Cada sección tiene subsección | `path`, `section_pattern`, `subsection` |
| `pattern_present` | Patrón regex presente en archivo | `path`, `pattern` |
| `reference_exists` | Archivo referenciado existe | `path`, `referenced_file` |
| `gate_passed` | Gate previo pasó (consulta traces) | `gate_id` |

### 3.4 Severity Levels

| Severity | Comportamiento |
|----------|----------------|
| `error` | Bloquea ejecución, dispara Jidoka |
| `warning` | Continúa pero muestra advertencia |
| `info` | Solo log, no afecta ejecución |

### 3.5 Gate Runner (Validador Genérico)

**Archivo**: `.raise/gates/lib/gate-runner.sh`

**Uso**:
```bash
# Ejecutar pre-gate
gate-runner.sh --kata discovery --phase pre

# Ejecutar post-gate
gate-runner.sh --kata discovery --phase post
```

**Implementación**:

```bash
#!/usr/bin/env bash
# Gate Runner - Generic validator that reads YAML config and runs checks
set -euo pipefail

KATA_ID="${1}"
PHASE="${2}"  # pre | post
GATE_FILE="${REPO_ROOT}/.raise/gates/${KATA_ID}.yaml"

source "${REPO_ROOT}/.raise/gates/lib/validators.sh"

# Parse YAML and run each check
run_checks() {
    local phase="${1}"
    local checks
    checks=$(yq -r ".${phase}[]" "${GATE_FILE}")

    local status=0
    local results=()

    while IFS= read -r check_json; do
        local check_type=$(echo "$check_json" | yq -r '.check')
        local check_id=$(echo "$check_json" | yq -r '.id')
        local severity=$(echo "$check_json" | yq -r '.severity // "error"')
        local path=$(echo "$check_json" | yq -r '.path // ""')

        # Interpolate {{output_file}} if present
        path=$(interpolate_vars "$path")

        # Run the appropriate validator
        if run_validator "$check_type" "$check_json"; then
            results+=("{\"id\": \"$check_id\", \"status\": \"pass\"}")
        else
            local message=$(echo "$check_json" | yq -r '.message')
            results+=("{\"id\": \"$check_id\", \"status\": \"fail\", \"severity\": \"$severity\", \"message\": \"$message\"}")

            if [[ "$severity" == "error" ]]; then
                status=1
            fi
        fi
    done <<< "$checks"

    # Output JSON result
    echo "{\"gate_id\": \"${PHASE}-${KATA_ID}\", \"checks\": [$(IFS=,; echo "${results[*]}")]}"

    return $status
}

run_checks "${PHASE}"
```

### 3.6 Exit Codes

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| 0 | All checks passed (or only warnings) | Continue execution |
| 1 | At least one `severity: error` check failed | Block execution, trigger Jidoka |

---

## 4. Gate Configuration Examples

### 4.1 Discovery Gate (Completo)

**Ver Section 3.2** para el ejemplo completo de `discovery.yaml`.

### 4.2 Vision Gate

**File**: `.raise/gates/vision.yaml`

```yaml
# Gate configuration for vision kata
---
kata_id: vision
version: 1.0.0
output_file: specs/main/solution_vision.md

pre:
  # PRD must exist
  - id: prd_exists
    check: file_exists
    path: specs/main/project_requirements.md
    severity: error
    message: "PRD not found. Run /raise.1.discovery first."
    recovery: "Execute: /raise.1.discovery"

  # PRD must have valid frontmatter
  - id: prd_frontmatter
    check: frontmatter_field
    path: specs/main/project_requirements.md
    field: titulo
    severity: error
    message: "PRD frontmatter invalid or missing 'titulo' field."

  # Discovery gate must have passed
  - id: discovery_gate_passed
    check: gate_passed
    gate_id: post-discovery
    severity: error
    message: "Discovery gate did not pass. Fix PRD issues before proceeding."
    recovery: "Review PRD, fix issues, then re-run /raise.1.discovery"

post:
  # Vision file exists
  - id: vision_exists
    check: file_exists
    path: "{{output_file}}"
    severity: error
    message: "Solution Vision not generated."

  # Required sections
  - id: problem_statement
    check: section_present
    path: "{{output_file}}"
    section: "## Problem Statement"
    severity: error
    message: "Missing 'Problem Statement' section."

  - id: strategic_alignment
    check: section_present
    path: "{{output_file}}"
    section: "## Strategic Alignment"
    severity: error
    message: "Missing 'Strategic Alignment' section."

  - id: mvp_scope
    check: section_present
    path: "{{output_file}}"
    section: "## MVP Scope"
    severity: error
    message: "Missing 'MVP Scope' section."

  # Component count (3-7 is ideal)
  - id: component_count
    check: count_pattern
    path: "{{output_file}}"
    pattern: "^### Component:"
    min: 3
    max: 10
    severity: warning
    message: "Component count outside recommended range (3-7)."
```

### 4.3 Design Gate

**File**: `.raise/gates/design.yaml`

```yaml
# Gate configuration for design kata
---
kata_id: design
version: 1.0.0
output_file: specs/main/tech_design.md

pre:
  # Vision must exist
  - id: vision_exists
    check: file_exists
    path: specs/main/solution_vision.md
    severity: error
    message: "Solution Vision not found. Run /raise.2.vision first."
    recovery: "Execute: /raise.2.vision"

  # Vision must have required sections
  - id: vision_problem_statement
    check: section_present
    path: specs/main/solution_vision.md
    section: "## Problem Statement"
    severity: error
    message: "Vision missing 'Problem Statement' section."

  - id: vision_mvp_scope
    check: section_present
    path: specs/main/solution_vision.md
    section: "## MVP Scope"
    severity: error
    message: "Vision missing 'MVP Scope' section."

  # Vision gate must have passed
  - id: vision_gate_passed
    check: gate_passed
    gate_id: post-vision
    severity: error
    message: "Vision gate did not pass. Fix Vision issues before proceeding."

post:
  # Tech Design file exists
  - id: design_exists
    check: file_exists
    path: "{{output_file}}"
    severity: error
    message: "Tech Design not generated."

  # Must reference Vision
  - id: references_vision
    check: reference_exists
    path: "{{output_file}}"
    referenced_file: solution_vision.md
    severity: error
    message: "Tech Design must reference Solution Vision."

  # Architecture diagram present (mermaid block)
  - id: architecture_diagram
    check: pattern_present
    path: "{{output_file}}"
    pattern: "```mermaid"
    severity: error
    message: "Missing architecture diagram (mermaid block)."

  # Data model section
  - id: data_model
    check: section_present
    path: "{{output_file}}"
    section: "## Data Model"
    severity: error
    message: "Missing 'Data Model' section."

  # API contracts (warning only)
  - id: api_contracts
    check: section_present
    path: "{{output_file}}"
    section: "## API"
    severity: warning
    message: "Consider adding API contracts section."

  # Testing strategy (warning only)
  - id: testing_strategy
    check: section_present
    path: "{{output_file}}"
    section: "## Testing"
    severity: warning
    message: "Consider adding Testing strategy section."
```

---

## 5. Arquitectura Unificada: Un YAML por Kata

**Insight clave**: Pre-gate y post-gate van en el **mismo archivo YAML** por kata. Esto simplifica:
- Un archivo por kata = una fuente de verdad
- Fácil ver qué se valida antes y después
- Versionado conjunto de pre y post

**Estructura final:**

```
.raise/gates/
├── discovery.yaml    # pre + post para discovery
├── vision.yaml       # pre + post para vision
├── design.yaml       # pre + post para design
├── backlog.yaml      # pre + post para backlog (futuro)
└── lib/
    ├── gate-runner.sh    # Validador genérico
    └── validators.sh     # Funciones de validación
```

**Ver Section 4** para los ejemplos completos de cada gate YAML.

---

## 6. Jidoka Hook Design

### 6.1 What Triggers Jidoka?

**Jidoka** = immediate stop when a critical condition is detected.

**Triggers**:
1. **Gate failure** (pre or post)
2. **Inline check failure** (during kata execution)
3. **Critical validation failure** (secrets detected, infinite loop, unsafe operation)

### 6.2 Jidoka Hook Implementation

**Location**: `.raise/harness/jidoka.sh`

**Invocation**: Can be called from gates or inline during kata execution.

**Interface**:

```bash
#!/usr/bin/env bash
# Jidoka hook - pause execution and show recovery guidance

# Usage: jidoka.sh <error_code> <error_message> [recovery_guidance...]

set -euo pipefail

ERROR_CODE="${1:-UNKNOWN}"
ERROR_MESSAGE="${2:-An error occurred}"
shift 2
RECOVERY_GUIDANCE=("$@")

# Log event to trace
log_event "jidoka_trigger" \
    "{\"error_code\": \"${ERROR_CODE}\", \"message\": \"${ERROR_MESSAGE}\"}"

# Show error to user
cat >&2 <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 JIDOKA: Execution Paused
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Error Code: ${ERROR_CODE}
Message: ${ERROR_MESSAGE}

Recovery Guidance:
EOF

for guidance in "${RECOVERY_GUIDANCE[@]}"; do
    echo "  • ${guidance}" >&2
done

cat >&2 <<EOF

To resume:
  1. Fix the issue above
  2. Re-run the same command

To investigate:
  • View trace: cat .raise/traces/kata-execution.jsonl | tail -20
  • Check logs: [kata-specific log location]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

exit 1
```

### 6.3 Inline Jidoka Checks

Kata markdown can invoke Jidoka checks during execution:

**Example in Kata Markdown**:

```markdown
## Paso 2: Cargar PRD y Contexto

- Cargar `specs/main/project_requirements.md`
- Cargar contexto técnico si existe

**Verificación**: PRD exists and has frontmatter.

> **Si no puedes continuar**: PRD no encontrado → JIDOKA: Ejecutar `/raise.1.discovery` primero.

**Inline Check** (bash script invoked by LLM):
```bash
# LLM executes this when reaching this step
bash .raise/harness/jidoka-check.sh \
    --file "specs/main/project_requirements.md" \
    --type "prd_exists" \
    --recovery "Run /raise.1.discovery to generate PRD"
```
```

**Script**: `.raise/harness/jidoka-check.sh`

```bash
#!/usr/bin/env bash
# Inline Jidoka check - validate condition, trigger Jidoka if fail

FILE="${1}"
CHECK_TYPE="${2}"
RECOVERY="${3}"

case "${CHECK_TYPE}" in
    prd_exists)
        if [[ ! -f "${FILE}" ]]; then
            bash .raise/harness/jidoka.sh \
                "PRD_NOT_FOUND" \
                "PRD not found at ${FILE}" \
                "${RECOVERY}"
        fi
        ;;
    frontmatter_valid)
        if ! grep -q "^---$" "${FILE}"; then
            bash .raise/harness/jidoka.sh \
                "INVALID_FRONTMATTER" \
                "PRD missing valid YAML frontmatter" \
                "Add YAML frontmatter at top of file"
        fi
        ;;
    *)
        echo "Unknown check type: ${CHECK_TYPE}" >&2
        exit 1
        ;;
esac
```

### 6.4 Resume After Jidoka

**User Action**:
1. User fixes the issue (e.g., creates missing file, fixes permissions)
2. User re-runs the same command: `/raise.2.vision`
3. System re-runs gates and resumes from last successful step

**No manual state management needed** - gates are idempotent.

---

## 7. Trace Format

### 7.1 JSONL Structure

**File**: `.raise/traces/kata-execution.jsonl`

**Format**: One JSON object per line (JSONL = JSON Lines)

**Why JSONL**: Append-only, no need to re-parse entire file, streamable

**Fields per Event**:

```json
{
  "event": "string",           // Event type
  "timestamp": "ISO8601",      // When it happened
  "kata_id": "string",         // discovery, vision, design, etc.
  "kata_version": "string",    // 2.1.0
  "session_id": "uuid",        // Unique per execution run
  "data": {}                   // Event-specific data
}
```

### 7.2 Event Types

| Event Type | When | Data Fields |
|------------|------|-------------|
| `kata_invoked` | User runs kata command | `kata_id`, `args`, `user` |
| `gate_start` | Gate begins execution | `gate_id`, `gate_type` (PRE/POST) |
| `gate_pass` | Gate passed | `gate_id`, `checks_passed`, `checks_failed` |
| `gate_fail` | Gate failed | `gate_id`, `failures` (array) |
| `kata_start` | LLM begins executing kata steps | `kata_id` |
| `kata_step` | LLM completes a kata step | `step_number`, `step_name` |
| `kata_complete` | Kata execution finished | `kata_id`, `output_files` |
| `jidoka_trigger` | Jidoka hook triggered | `error_code`, `message`, `recovery_guidance` |
| `handoff_offered` | Next kata offered to user | `next_kata_id`, `prompt` |
| `handoff_accepted` | User accepted handoff | `next_kata_id` |

### 7.3 Example Trace

```jsonl
{"event":"kata_invoked","timestamp":"2026-01-29T14:32:15Z","kata_id":"discovery","kata_version":"2.1.0","session_id":"a1b2c3d4","data":{"args":"--context 'Build a CRM'","user":"emilio"}}
{"event":"gate_start","timestamp":"2026-01-29T14:32:16Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"gate_id":"pre-discovery","gate_type":"PRE"}}
{"event":"gate_pass","timestamp":"2026-01-29T14:32:17Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"gate_id":"pre-discovery","checks_passed":3,"checks_failed":0}}
{"event":"kata_start","timestamp":"2026-01-29T14:32:18Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{}}
{"event":"kata_step","timestamp":"2026-01-29T14:35:42Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"step_number":1,"step_name":"Cargar Contexto"}}
{"event":"kata_step","timestamp":"2026-01-29T14:38:12Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"step_number":2,"step_name":"Extraer Requisitos"}}
{"event":"kata_complete","timestamp":"2026-01-29T14:45:30Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"output_files":["specs/main/project_requirements.md"]}}
{"event":"gate_start","timestamp":"2026-01-29T14:45:31Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"gate_id":"post-discovery","gate_type":"POST"}}
{"event":"gate_fail","timestamp":"2026-01-29T14:45:33Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"gate_id":"post-discovery","failures":["VAL-003: Only 3 FRs found, expected ≥5","VAL-004: FR-001 missing acceptance criteria"]}}
{"event":"jidoka_trigger","timestamp":"2026-01-29T14:45:34Z","kata_id":"discovery","session_id":"a1b2c3d4","data":{"error_code":"GATE_FAILURE","message":"Post-discovery gate failed","recovery_guidance":["Review PRD and add more requirements","Ensure each FR has acceptance criteria"]}}
```

### 7.4 Trace Queries

**CLI commands for trace analysis**:

```bash
# Show last 20 events
cat .raise/traces/kata-execution.jsonl | tail -20 | jq .

# Filter by event type
jq 'select(.event == "gate_fail")' .raise/traces/kata-execution.jsonl

# Filter by kata
jq 'select(.kata_id == "discovery")' .raise/traces/kata-execution.jsonl

# Count gate failures by gate ID
jq 'select(.event == "gate_fail") | .data.gate_id' .raise/traces/kata-execution.jsonl | sort | uniq -c

# Show all Jidoka triggers
jq 'select(.event == "jidoka_trigger")' .raise/traces/kata-execution.jsonl

# Generate execution timeline
jq -r '[.timestamp, .event, .kata_id] | @tsv' .raise/traces/kata-execution.jsonl
```

---

## 8. Integration with Existing Commands

### 8.1 Markdown Command Changes

**Current** (no gates):

```yaml
---
description: Perform an integral brownfield codebase analysis.
---

## Outline
...
```

**With Hybrid Gates** (declarativo):

```yaml
---
description: Perform an integral brownfield codebase analysis.
gates: discovery  # Referencia a .raise/gates/discovery.yaml
output_file: specs/main/project_requirements.md
---

## Outline
...
```

**Campos agregados**:
- `gates`: ID del gate (mapea a `.raise/gates/{id}.yaml`)
- `output_file`: Archivo de output esperado (para post-gate validation)

**El orchestrator**:
1. Lee `gates: discovery`
2. Carga `.raise/gates/discovery.yaml`
3. Ejecuta sección `pre:` antes del kata
4. Ejecuta sección `post:` después del kata

### 8.2 Orchestrator Wrapper

**Current**: LLM interprets markdown directly

**With Hybrid Gates**: Wrapper script orchestrates flow

**Script**: `.raise/harness/run-kata.sh`

```bash
#!/usr/bin/env bash
# Kata orchestrator with gate integration

set -euo pipefail

KATA_COMMAND="${1}"  # e.g., "raise.1.discovery"
KATA_ARGS="${2:-}"   # Optional user arguments

# 1. Load kata frontmatter (extract gates, output_file)
KATA_FILE="${REPO_ROOT}/.claude/commands/$(kata_id_to_path "${KATA_COMMAND}")"
KATA_ID=$(extract_frontmatter "${KATA_FILE}" "description" | kata_name_from_description)
PRE_GATE=$(extract_frontmatter "${KATA_FILE}" "gates.pre")
POST_GATE=$(extract_frontmatter "${KATA_FILE}" "gates.post")
OUTPUT_FILE=$(extract_frontmatter "${KATA_FILE}" "output_file")

# 2. Generate session ID
SESSION_ID=$(uuidgen)
export SESSION_ID

# 3. Log kata invocation
log_event "kata_invoked" \
    "{\"kata_id\": \"${KATA_ID}\", \"args\": \"${KATA_ARGS}\", \"user\": \"$(whoami)\"}"

# 4. Run PRE-GATE (if defined)
if [[ -n "${PRE_GATE}" ]]; then
    log_event "gate_start" \
        "{\"gate_id\": \"$(basename "${PRE_GATE}" .sh)\", \"gate_type\": \"PRE\"}"

    if bash "${PRE_GATE}"; then
        log_event "gate_pass" \
            "{\"gate_id\": \"$(basename "${PRE_GATE}" .sh)\"}"
    else
        log_event "gate_fail" \
            "{\"gate_id\": \"$(basename "${PRE_GATE}" .sh)\"}"
        log_event "jidoka_trigger" \
            "{\"error_code\": \"PRE_GATE_FAILURE\", \"message\": \"Pre-gate failed\"}"
        exit 1
    fi
fi

# 5. Execute kata (LLM interprets markdown)
log_event "kata_start" "{\"kata_id\": \"${KATA_ID}\"}"

# Invoke Claude with the kata markdown + user args
# (This is the existing behavior - LLM reads and executes the kata)
claude_execute_kata "${KATA_FILE}" "${KATA_ARGS}"

log_event "kata_complete" \
    "{\"kata_id\": \"${KATA_ID}\", \"output_files\": [\"${OUTPUT_FILE}\"]}"

# 6. Run POST-GATE (if defined)
if [[ -n "${POST_GATE}" ]]; then
    log_event "gate_start" \
        "{\"gate_id\": \"$(basename "${POST_GATE}" .sh)\", \"gate_type\": \"POST\"}"

    export OUTPUT_FILE  # Pass to gate
    if bash "${POST_GATE}"; then
        log_event "gate_pass" \
            "{\"gate_id\": \"$(basename "${POST_GATE}" .sh)\"}"
    else
        log_event "gate_fail" \
            "{\"gate_id\": \"$(basename "${POST_GATE}" .sh)\"}"
        log_event "jidoka_trigger" \
            "{\"error_code\": \"POST_GATE_FAILURE\", \"message\": \"Post-gate failed\"}"
        exit 1
    fi
fi

# 7. Offer handoff (if gate passed)
HANDOFF=$(extract_frontmatter "${KATA_FILE}" "handoffs[0].agent")
if [[ -n "${HANDOFF}" ]]; then
    log_event "handoff_offered" \
        "{\"next_kata_id\": \"${HANDOFF}\"}"
    echo "✓ Kata complete. Next: /${HANDOFF}"
fi
```

### 8.3 Backward Compatibility

**Katas without gates work unchanged**:
- If `gates.pre` not defined → skip pre-gate
- If `gates.post` not defined → skip post-gate
- LLM execution remains the same

**Incremental adoption**:
1. Start with critical katas (discovery, vision)
2. Add gates to high-value katas
3. Gradually expand coverage

---

## 9. Validator Library (Funciones Reutilizables)

### 9.1 Purpose

El gate-runner llama a estas funciones basándose en el `check` type definido en YAML.

### 9.2 Location

`.raise/gates/lib/validators.sh`

### 9.3 Validator Functions

```bash
#!/usr/bin/env bash
# Validator library - called by gate-runner based on YAML config

# Dispatcher: runs the appropriate validator based on check type
run_validator() {
    local check_type="${1}"
    local check_json="${2}"

    case "${check_type}" in
        file_exists)
            local path=$(echo "$check_json" | yq -r '.path')
            path=$(interpolate_vars "$path")
            [[ -f "${REPO_ROOT}/${path}" ]]
            ;;
        directory_writable)
            local path=$(echo "$check_json" | yq -r '.path')
            [[ -d "${REPO_ROOT}/${path}" ]] && [[ -w "${REPO_ROOT}/${path}" ]]
            ;;
        any_file_exists)
            local paths=$(echo "$check_json" | yq -r '.paths[]')
            for path in $paths; do
                [[ -f "${REPO_ROOT}/${path}" ]] && return 0
            done
            return 1
            ;;
        frontmatter_field)
            local path=$(echo "$check_json" | yq -r '.path')
            local field=$(echo "$check_json" | yq -r '.field')
            path=$(interpolate_vars "$path")
            validate_frontmatter_field "${REPO_ROOT}/${path}" "${field}"
            ;;
        section_present)
            local path=$(echo "$check_json" | yq -r '.path')
            local section=$(echo "$check_json" | yq -r '.section')
            path=$(interpolate_vars "$path")
            grep -q "^${section}$" "${REPO_ROOT}/${path}"
            ;;
        count_pattern)
            local path=$(echo "$check_json" | yq -r '.path')
            local pattern=$(echo "$check_json" | yq -r '.pattern')
            local min=$(echo "$check_json" | yq -r '.min // 0')
            local max=$(echo "$check_json" | yq -r '.max // 999999')
            path=$(interpolate_vars "$path")
            local count=$(grep -cE "${pattern}" "${REPO_ROOT}/${path}" || echo 0)
            [[ ${count} -ge ${min} ]] && [[ ${count} -le ${max} ]]
            ;;
        sections_have_subsection)
            local path=$(echo "$check_json" | yq -r '.path')
            local section_pattern=$(echo "$check_json" | yq -r '.section_pattern')
            local subsection=$(echo "$check_json" | yq -r '.subsection')
            path=$(interpolate_vars "$path")
            validate_sections_have_subsection "${REPO_ROOT}/${path}" "${section_pattern}" "${subsection}"
            ;;
        pattern_present)
            local path=$(echo "$check_json" | yq -r '.path')
            local pattern=$(echo "$check_json" | yq -r '.pattern')
            path=$(interpolate_vars "$path")
            grep -qE "${pattern}" "${REPO_ROOT}/${path}"
            ;;
        reference_exists)
            local path=$(echo "$check_json" | yq -r '.path')
            local referenced=$(echo "$check_json" | yq -r '.referenced_file')
            path=$(interpolate_vars "$path")
            grep -q "${referenced}" "${REPO_ROOT}/${path}"
            ;;
        gate_passed)
            local gate_id=$(echo "$check_json" | yq -r '.gate_id')
            check_gate_passed "${gate_id}"
            ;;
        *)
            echo "Unknown check type: ${check_type}" >&2
            return 1
            ;;
    esac
}

# Variable interpolation (e.g., {{output_file}})
interpolate_vars() {
    local str="${1}"
    str="${str//\{\{output_file\}\}/${OUTPUT_FILE}}"
    str="${str//\{\{kata_id\}\}/${KATA_ID}}"
    echo "${str}"
}

# Helper: validate frontmatter field exists
validate_frontmatter_field() {
    local file="${1}"
    local field="${2}"
    sed -n '/^---$/,/^---$/p' "${file}" | grep -q "^${field}:"
}

# Helper: validate all sections have a subsection
validate_sections_have_subsection() {
    local file="${1}"
    local section_pattern="${2}"
    local subsection="${3}"

    local sections=$(grep -E "${section_pattern}" "${file}" || true)
    [[ -z "$sections" ]] && return 1

    while IFS= read -r section; do
        local content=$(sed -n "/${section}/,/^###/p" "${file}")
        echo "${content}" | grep -q "${subsection}" || return 1
    done <<< "$sections"
    return 0
}

# Helper: check if gate passed in trace
check_gate_passed() {
    local gate_id="${1}"
    [[ -f "${TRACE_FILE}" ]] && \
    jq -e "select(.event == \"gate_pass\" and .data.gate_id == \"${gate_id}\")" \
        "${TRACE_FILE}" > /dev/null 2>&1
}

# Logging helper
log_event() {
    local event_type="${1}"
    local data_json="${2:-{}}"

    cat >> "${TRACE_FILE}" <<EOF
{"event":"${event_type}","timestamp":"$(date -Iseconds)","kata_id":"${KATA_ID}","session_id":"${SESSION_ID}","data":${data_json}}
EOF
}
```

### 9.4 Adding Custom Validators

Para agregar un nuevo tipo de validador:

1. Agregar case en `run_validator()`:
   ```bash
   my_custom_check)
       local param1=$(echo "$check_json" | yq -r '.param1')
       # Lógica de validación
       ;;
   ```

2. Usar en YAML:
   ```yaml
   - id: my_check
     check: my_custom_check
     param1: value
     severity: error
     message: "Check failed"
   ```

---

## 10. Comparison: Hybrid Gates vs Full Harness

### 10.1 Comparison Table

| Aspect | Hybrid Gates (Option B) | Full Harness (Option C) |
|--------|------------------------|------------------------|
| **Enforcement Level** | Deterministic gates at kata boundaries + inline checks | Deterministic at every step + state machine |
| **Can LLM skip steps?** | Yes (within kata), No (between katas) | No (every step validated) |
| **Contributor Learning Curve** | Low (markdown + bash) | Medium (markdown → JSON DSL → compilation) |
| **Implementation Effort** | 1-2 weeks | 4-6 weeks |
| **Observability** | JSONL trace (good) | Full state machine + trace (excellent) |
| **Resumability** | Manual (re-run) | Automatic (state machine resumes) |
| **Infrastructure** | Bash scripts + conventions | Compiler + executor + state engine |
| **Suitable for** | Open core, rapid iteration | Enterprise, regulated industries |
| **Can enforce "every FR has AC"?** | Yes (post-gate) | Yes (step-level validation) |
| **Can enforce "step 3 before step 4"?** | No (LLM controls order within kata) | Yes (state machine controls flow) |
| **Can detect infinite loops?** | No (no step tracking) | Yes (state machine detects cycles) |
| **Maintenance burden** | Low (bash scripts) | Medium (maintain compiler + executor) |
| **Portability** | High (bash everywhere) | Medium (requires runtime) |

### 10.2 When to Use Each

**Use Hybrid Gates (Option B) if**:
- Open core project, need fast iteration
- Contributors are familiar with bash/markdown
- Enforcement at kata boundaries is sufficient
- Observability via traces is acceptable
- Budget: 1-2 weeks implementation

**Use Full Harness (Option C) if**:
- Enterprise adoption, need maximum enforcement
- Regulated industry (finance, healthcare) requires audit trails
- Step-level validation is required
- State machine resumability is essential
- Budget: 4-6 weeks implementation

### 10.3 Can Hybrid Gates Evolve to Full Harness?

**Yes, incrementally**:

1. **Phase 1**: Implement Hybrid Gates (gates at kata boundaries)
2. **Phase 2**: Add more inline checks (increase granularity)
3. **Phase 3**: Introduce light state machine (track which steps completed)
4. **Phase 4**: Full compilation (markdown → JSON → executable)

**Migration Path**:
- Gates remain valid (become policy files in full harness)
- JSONL trace format remains (becomes input to state machine)
- Bash validators become validator plugins

**No throw-away work** - Hybrid Gates is a stepping stone, not a dead end.

---

## 11. Implementation Plan (1-2 Weeks)

### Week 1: Core Infrastructure

**Day 1-2: Gate Runner + Validators**
- [ ] Implement `.raise/gates/lib/gate-runner.sh` (parsea YAML, ejecuta validators)
- [ ] Implement `.raise/gates/lib/validators.sh` (10 funciones base)
- [ ] Implement `.raise/gates/lib/reporting.sh` (formateo de errores)
- [ ] Test con YAML de prueba

**Day 3-4: Gate Configurations (YAML)**
- [ ] Crear `.raise/gates/discovery.yaml` (pre + post)
- [ ] Crear `.raise/gates/vision.yaml` (pre + post)
- [ ] Crear `.raise/gates/design.yaml` (pre + post)
- [ ] Test cada gate manualmente con gate-runner.sh

**Day 5: Orchestrator + Jidoka**
- [ ] Implement `.raise/harness/run-kata.sh` (orchestrator)
- [ ] Implement `.raise/harness/jidoka.sh` (Jidoka hook)
- [ ] Test flow completo: pre-gate → kata → post-gate

### Week 2: Integration + Validation

**Day 6-7: Command Integration**
- [ ] Update 3 command frontmatters (add `gates: {kata-id}`)
- [ ] Test full flow: `/raise.1.discovery` with gates
- [ ] Test full flow: `/raise.2.vision` with gates
- [ ] Fix any orchestration issues

**Day 8: Trace System**
- [ ] Implement JSONL logging in orchestrator
- [ ] Implement `log_event()` en validators.sh
- [ ] Test trace output for full kata run
- [ ] Implement basic trace queries (bash/jq scripts)

**Day 9: Jidoka + Edge Cases**
- [ ] Test Jidoka on gate failure (severity: error)
- [ ] Test warnings (severity: warning) continue execution
- [ ] Verify recovery guidance displays correctly
- [ ] Test resume after fix

**Day 10: Documentation + Testing**
- [ ] Write user guide for gates
- [ ] Write contributor guide for adding gates (YAML)
- [ ] Run full test suite (3 katas end-to-end)
- [ ] Document cómo agregar nuevos validators

### Success Criteria

Al final de 2 semanas:
- [ ] Gate runner funcional (parsea YAML, ejecuta validators)
- [ ] 3 gate configs YAML funcionales (discovery, vision, design)
- [ ] 10+ validators implementados (file_exists, section_present, etc.)
- [ ] Orchestrator ejecuta katas con gate integration
- [ ] Jidoka hook pausa en failure, muestra recovery
- [ ] JSONL trace captura todos los eventos
- [ ] Katas sin gates siguen funcionando (backward compatible)
- [ ] Documentación: user guide + contributor guide para agregar gates YAML

---

## 12. Known Limitations

### 12.1 What Hybrid Gates Cannot Do

1. **Enforce step order within kata** - LLM controls execution within kata boundaries
2. **Detect infinite loops** - No state machine tracking
3. **Automatic resume from failure** - User must re-run (gates are idempotent)
4. **Cross-kata state validation** - Each kata is independent (no global state)
5. **Dynamic gate selection** - Gates are declared in frontmatter (no runtime selection)

### 12.2 Workarounds

| Limitation | Workaround |
|------------|-----------|
| Can't enforce step order | Add inline checks at critical steps (Jidoka hooks) |
| Can't detect infinite loops | Add timeout to orchestrator (max 30 min per kata) |
| No automatic resume | Gates are fast (<5s), re-running is acceptable |
| No cross-kata validation | Pre-gates check previous kata outputs (indirect validation) |
| No dynamic gate selection | Use environment variables to parameterize gates |

### 12.3 Future Enhancements

If Hybrid Gates proves successful, consider:

1. **Gate composition** - Reusable gate modules (like policy composition in DSL spec)
2. **Parameterized gates** - Pass thresholds via environment variables
3. **Gate testing framework** - Unit tests for gates
4. **Gate marketplace** - Share community gates (via MCP resources)
5. **Visual trace viewer** - Web UI for JSONL trace analysis

---

## 13. Open Questions

### 13.1 Design Decisions TBD

1. **Gate timeout**: Should gates have a max execution time? (Proposed: 30s)
2. **Parallel gates**: Can we run multiple pre-gates in parallel? (Proposed: No, sequential is simpler)
3. **Gate versioning**: Should gates declare compatible kata versions? (Proposed: Yes, in frontmatter)
4. **Trace rotation**: Should trace files rotate by date/size? (Proposed: Daily rotation, keep 7 days)
5. **Gate discovery**: How does orchestrator find gates for a kata? (Proposed: Frontmatter `gates` field)

### 13.2 Implementation Details TBD

1. **YAML parsing in bash**: Use `yq` or write custom parser? (Proposed: `yq` if available, fallback to `grep`)
2. **Session ID generation**: Use `uuidgen` or `date +%s%N`? (Proposed: `uuidgen` for uniqueness)
3. **Trace locking**: What if multiple katas run concurrently? (Proposed: Append is atomic, no locking needed)
4. **Error codes**: Should we standardize error codes across gates? (Proposed: Yes, document in style guide)
5. **Recovery guidance format**: Markdown or plain text? (Proposed: Plain text for simplicity)

---

## 14. References

### 14.1 Internal References

- **Policy DSL Specification**: `/home/emilio/Code/raise-commons/specs/main/research/governance-as-code-agents/policy-dsl-specification.md` - Pattern for validators and policy structure
- **Strategic Decision Report**: `/home/emilio/Code/raise-commons/specs/main/research/bmad-brownfield-analysis/strategic-decision-report.md` - Deterministic pipeline patterns (Phase 0/1)
- **Current gates**: `.raise/gates/gate-*.md` - Existing markdown checklists (to be replaced)
- **Current commands**: `.claude/commands/**/*.md` - Kata markdown files
- **Orchestrator scripts**: `.specify/scripts/bash/` - Existing bash utilities

### 14.2 External References

- **Bash scripting best practices**: Google Shell Style Guide
- **JSONL specification**: jsonlines.org
- **Jidoka (Toyota Production System)**: Principle of "automation with a human touch"
- **YAGNI (You Aren't Gonna Need It)**: Extreme Programming principle

### 14.3 Related Research

- **Option A (Status Quo)**: LLM-only interpretation (no enforcement)
- **Option C (Full Harness)**: Compiled DSL + state machine (maximum enforcement)
- **BMAD brownfield analysis**: Operational patterns for multi-phase pipelines

---

## Appendix A: File Tree (Post-Implementation)

```
.raise/
├── gates/
│   ├── discovery.yaml          # Gate config: pre + post para discovery
│   ├── vision.yaml             # Gate config: pre + post para vision
│   ├── design.yaml             # Gate config: pre + post para design
│   ├── backlog.yaml            # Gate config: pre + post para backlog (futuro)
│   └── lib/
│       ├── gate-runner.sh      # Validador genérico (LEE YAML, ejecuta checks)
│       ├── validators.sh       # Funciones de validación reutilizables
│       └── reporting.sh        # Formateo de errores y recovery guidance
│
├── harness/
│   ├── run-kata.sh             # Main orchestrator (gate → LLM → gate)
│   ├── jidoka.sh               # Jidoka hook (pause + show recovery)
│   └── jidoka-check.sh         # Inline Jidoka checks (opcional)
│
├── traces/                     # Gitignored
│   └── kata-execution.jsonl    # Append-only event log
│
└── docs/
    ├── user-guide-gates.md     # Cómo usar gates como orquestador
    └── contributor-guide-gates.md  # Cómo agregar gates como contributor

.claude/commands/               # Kata commands (markdown)
├── 01-onboarding/
│   └── raise.1.analyze.code.md  # Con frontmatter: gates: discovery
├── 02-projects/
│   ├── raise.2.vision.md        # Con frontmatter: gates: vision
│   └── raise.3.ecosystem.md     # Con frontmatter: gates: ecosystem
└── ...
```

### Diferencia con diseño anterior

| Antes (scripts) | Ahora (declarativo) |
|-----------------|---------------------|
| `pre-discovery.sh` | `discovery.yaml` → sección `pre:` |
| `post-discovery.sh` | `discovery.yaml` → sección `post:` |
| 6 scripts bash | 3 archivos YAML |
| Lógica duplicada | Validators compartidos |
| `run-gate.sh` wrapper | `gate-runner.sh` genérico |

---

## Appendix B: Sample User Flow

### Scenario: User runs `/raise.1.discovery`

**Step 1: User invokes command**

```bash
$ /raise.1.discovery --context "Build a CRM for small businesses"
```

**Step 2: Orchestrator starts, runs pre-gate**

```
Running pre-discovery gate...
  ✓ Context documents found
  ✓ Output directory writable
  ✓ Template exists
Pre-gate passed.

Starting discovery kata...
```

**Step 3: LLM executes kata steps** (as today)

```
Paso 1: Cargar contexto...
[LLM reads context documents]

Paso 2: Extraer requisitos...
[LLM generates requirements]

...

Generating PRD at specs/main/project_requirements.md
```

**Step 4: Orchestrator runs post-gate**

```
Running post-discovery gate...
  ✓ PRD file exists
  ✓ Frontmatter has 'titulo' field
  ✗ Only 3 functional requirements found (expected ≥5)
  ✗ FR-001 missing 'Criterios de Aceptación' section

Post-gate failed.
```

**Step 5: Jidoka triggered**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 JIDOKA: Execution Paused
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Error Code: POST_GATE_FAILURE
Message: Discovery post-gate validation failed

Gate Failures:
  • VAL-003: Only 3 functional requirements found (expected ≥5)
  • VAL-004: FR-001 missing 'Criterios de Aceptación' section

Recovery Guidance:
  • Review PRD and add more functional requirements
  • Ensure each FR-* section has a 'Criterios de Aceptación' subsection
  • Re-run /raise.1.discovery after fixes

To investigate:
  • View full gate output: bash .raise/gates/post-discovery.sh
  • View trace: jq 'select(.data.gate_id == "post-discovery")' .raise/traces/kata-execution.jsonl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 6: User fixes issues and re-runs**

```bash
$ /raise.1.discovery
# [Orchestrator re-runs gates + kata, now passes]

✓ Discovery complete!
  Output: specs/main/project_requirements.md
  Gate: post-discovery PASSED

Next step: /raise.2.vision
```

---

**End of Design Specification**

**Status**: Ready for implementation
**Estimated Effort**: 1-2 weeks (10 days)
**Next Steps**: Assign to implementation team, create feature branch, begin Week 1 tasks
