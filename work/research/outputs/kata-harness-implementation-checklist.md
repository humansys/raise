---
id: kata-harness-implementation-checklist
title: "Kata Harness: MVP Implementation Checklist"
date: 2026-01-29
status: ready-for-implementation
phase: mvp-phase-1
related_to: ["kata-harness-first-principles-taxonomy", "kata-harness-executive-summary"]
---

# Kata Harness: MVP Implementation Checklist

## Overview

This checklist provides the concrete steps to implement the Kata Harness MVP (Phase 1: Weeks 1-4).

**Goal**: Prove the 3-layer architecture with a single Kata (`project/discovery`).

---

## Phase 1: MVP Components

### Component 1: Kata Compiler

**Purpose**: Parse Markdown Kata → JSON Execution Graph

**Location**: `.raise/harness/compiler/`

#### Files to Create

```
.raise/harness/compiler/
├── kata-compiler.ts          # Main compiler class
├── markdown-parser.ts        # Parse MD to AST
├── step-extractor.ts         # Extract steps from ## Outline
├── skill-mapper.ts           # Map actions to skills
├── gate-mapper.ts            # Map verifications to gates
├── graph-builder.ts          # Build execution graph
└── types.ts                  # TypeScript interfaces
```

#### Implementation Checklist

- [ ] **Parse Frontmatter**
  - [ ] Extract `id`, `version` from YAML frontmatter
  - [ ] Validate required fields

- [ ] **Parse Outline Section**
  - [ ] Find `## Outline` H2 heading
  - [ ] Extract numbered steps (H3: `**Paso N: ...**`)
  - [ ] Extract bullet points (actions)
  - [ ] Extract `**Verificación**: ...`
  - [ ] Extract `> **Si no puedes continuar**: ...`

- [ ] **Map Actions to Skills**
  - [ ] Detect "Cargar `path`" → `file/load`
  - [ ] Detect "Usar LLM" → `llm/call`
  - [ ] Detect "Ejecutar gate" → `gate/run`
  - [ ] Extract inputs (e.g., `path: "specs/main/prd.md"`)

- [ ] **Map Verification to Gates**
  - [ ] Parse verification text
  - [ ] Match to gate ID (convention: `gate-{kata-name}-{step-num}`)
  - [ ] Mark as blocking (default: true)

- [ ] **Extract Jidoka Logic**
  - [ ] Parse "Si no puedes continuar" block
  - [ ] Detect `escalate`, `retry`, `skip`
  - [ ] Extract escalation message

- [ ] **Build Execution Graph**
  - [ ] Create `ExecutionGraph` object
  - [ ] Populate `steps` array
  - [ ] Set `next` transitions (sequential for MVP)
  - [ ] Validate graph (no orphan steps, valid skill refs)

- [ ] **Output JSON**
  - [ ] Serialize to `.raise/harness/plans/{kata-id}-{timestamp}.json`
  - [ ] Pretty-print for human readability

#### Test Cases

- [ ] **TC-1**: Parse simple 2-step Kata
- [ ] **TC-2**: Extract skills correctly
- [ ] **TC-3**: Map verification to gate
- [ ] **TC-4**: Handle missing verification gracefully
- [ ] **TC-5**: Validate malformed Markdown (error handling)

---

### Component 2: State Machine Orchestrator

**Purpose**: Execute compiled graph with enforcement guarantees

**Location**: `.raise/harness/runtime/`

#### Files to Create

```
.raise/harness/runtime/
├── kata-harness.ts           # Main harness class
├── state-manager.ts          # Manage execution state
├── skill-executor.ts         # Execute skills
├── gate-checker.ts           # Run gates
├── observer.ts               # Telemetry/logging
├── checkpoint-manager.ts     # Save/load checkpoints
└── types.ts                  # Shared types
```

#### Implementation Checklist

- [ ] **Initialize Execution**
  - [ ] Load execution graph JSON
  - [ ] Check for existing checkpoint
  - [ ] Initialize or restore state
  - [ ] Create trace ID

- [ ] **Execute Steps (Loop)**
  - [ ] For each step in graph:
    - [ ] Log "step_started" event
    - [ ] Run pre-gate (if exists)
    - [ ] Execute skill
    - [ ] Run post-gate (verification)
    - [ ] Update state with outputs
    - [ ] Log "step_completed" event
    - [ ] Checkpoint state
    - [ ] Resolve next step

- [ ] **Gate Enforcement**
  - [ ] Load gate definition (YAML)
  - [ ] Evaluate criteria
  - [ ] Return pass/fail + reason
  - [ ] If blocking gate fails: throw `JidokaError`
  - [ ] If non-blocking gate fails: log warning

- [ ] **Error Handling**
  - [ ] Catch skill execution errors
  - [ ] Apply retry logic (if `on_failure: retry`)
  - [ ] Apply escalation logic (if `on_failure: escalate`)
  - [ ] Halt execution on critical failure (Jidoka)

- [ ] **Checkpointing**
  - [ ] After each step: save state to disk
  - [ ] State includes: current_step, completed_steps, context
  - [ ] Resume logic: load checkpoint, continue from current_step

- [ ] **Observability**
  - [ ] Emit trace events: step_started, step_completed, step_failed
  - [ ] Log to JSONL file (one line per trace)
  - [ ] Capture metrics: tokens, latency, gate results

#### Test Cases

- [ ] **TC-1**: Execute 2-step Kata successfully
- [ ] **TC-2**: Gate failure halts execution
- [ ] **TC-3**: Resume from checkpoint after interruption
- [ ] **TC-4**: Retry logic works (max 3 attempts)
- [ ] **TC-5**: Trace log contains all steps

---

### Component 3: Skill Executors

**Purpose**: Implement atomic operations (skills)

**Location**: `.raise/harness/skills/`

#### Files to Create

```
.raise/harness/skills/
├── file-load.ts              # file/load skill
├── file-write.ts             # file/write skill
├── llm-call.ts               # llm/call skill
├── gate-run.ts               # gate/run skill
├── skill-registry.ts         # Register and lookup skills
└── types.ts                  # Skill interfaces
```

#### Skill Definitions (YAML)

Create skill definitions in `.raise/skills/`:

```
.raise/skills/
├── file/
│   ├── load.yaml
│   └── write.yaml
├── llm/
│   └── call.yaml
└── gate/
    └── run.yaml
```

#### Implementation Checklist

**Skill: `file/load`**

- [ ] YAML definition with inputs/outputs
- [ ] Handler: `file-load.ts`
- [ ] Read file from filesystem
- [ ] Return `{content: string, exists: boolean}`
- [ ] Handle file not found gracefully

**Skill: `llm/call`**

- [ ] YAML definition with inputs/outputs
- [ ] Handler: `llm-call.ts`
- [ ] Call LLM API (Claude, GPT-4, etc.)
- [ ] Handle retry on rate limits
- [ ] Return `{response: string, tokens_used: number}`

**Skill: `gate/run`**

- [ ] YAML definition with inputs/outputs
- [ ] Handler: `gate-run.ts`
- [ ] Load gate YAML definition
- [ ] Evaluate criteria (file_exists, yaml_frontmatter, etc.)
- [ ] Return `{passed: boolean, reason: string}`

**Skill Registry**

- [ ] `registerSkill(id, handler)` function
- [ ] `getSkill(id)` function
- [ ] Pre-register built-in skills (file/load, llm/call, gate/run)

#### Test Cases

- [ ] **TC-1**: `file/load` reads existing file
- [ ] **TC-2**: `file/load` handles missing file
- [ ] **TC-3**: `llm/call` returns response
- [ ] **TC-4**: `llm/call` handles API error
- [ ] **TC-5**: `gate/run` evaluates criteria correctly

---

### Component 4: Observer (Telemetry)

**Purpose**: Capture execution traces for observability

**Location**: `.raise/harness/observer/`

#### Files to Create

```
.raise/harness/observer/
├── execution-observer.ts     # Main observer class
├── trace-writer.ts           # Write JSONL traces
├── metrics-collector.ts      # Aggregate metrics
└── types.ts                  # Trace data structures
```

#### Implementation Checklist

- [ ] **Trace Structure**
  - [ ] Define `ExecutionTrace` interface
  - [ ] Fields: trace_id, kata_id, started_at, status, steps

- [ ] **Event Emission**
  - [ ] `startTrace(kata_id)` → create trace
  - [ ] `stepStarted(step_id)` → add step to trace
  - [ ] `stepCompleted(step_id, result)` → update step
  - [ ] `stepFailed(step_id, error)` → mark step failed
  - [ ] `completeTrace(trace_id, status)` → finalize trace

- [ ] **JSONL Writer**
  - [ ] Append trace to `.raise/harness/traces/{date}.jsonl`
  - [ ] One line per trace (JSON.stringify + newline)
  - [ ] Flush after each step (real-time logging)

- [ ] **Metrics Collection**
  - [ ] Per step: tokens_used, latency_ms
  - [ ] Per kata: total_tokens, total_duration, escalation_count
  - [ ] Store in trace JSON

#### Test Cases

- [ ] **TC-1**: Trace created with unique ID
- [ ] **TC-2**: Steps logged with timestamps
- [ ] **TC-3**: JSONL file is valid JSON per line
- [ ] **TC-4**: Metrics captured correctly
- [ ] **TC-5**: Trace can be replayed from JSONL

---

### Component 5: Gate Definitions

**Purpose**: Define validation criteria for gates

**Location**: `.raise/gates/`

#### Files to Create

```
.raise/gates/
├── gate-prd-loaded.yaml      # PRD exists + has frontmatter
├── gate-requirements-extracted.yaml
└── gate-discovery-complete.yaml
```

#### Gate YAML Format

```yaml
id: gate-prd-loaded
description: Verify PRD exists and has valid structure
type: post_execution
blocking: true
criteria:
  - type: file_exists
    path: specs/main/prd.md
    error_message: "PRD not found. Run /raise.discovery first."

  - type: yaml_frontmatter
    path: specs/main/prd.md
    required_fields: [title, date, status]
    error_message: "PRD missing required frontmatter fields"

  - type: section_exists
    path: specs/main/prd.md
    section: "## Functional Requirements"
    error_message: "PRD missing Functional Requirements section"
```

#### Implementation Checklist

- [ ] Define `gate-prd-loaded.yaml`
- [ ] Define `gate-requirements-extracted.yaml`
- [ ] Define `gate-discovery-complete.yaml`

**Criteria Checkers**:

- [ ] `file_exists`: Check file exists
- [ ] `yaml_frontmatter`: Parse frontmatter, check required fields
- [ ] `section_exists`: Check markdown has H2 heading
- [ ] `min_count`: Check array length >= N

#### Test Cases

- [ ] **TC-1**: Gate passes when all criteria met
- [ ] **TC-2**: Gate fails when file missing
- [ ] **TC-3**: Gate fails when frontmatter invalid
- [ ] **TC-4**: Error message is descriptive

---

### Component 6: Demo Kata

**Purpose**: Simple kata for testing harness

**Location**: `.raise/katas/project/discovery-mvp.md`

#### Kata Content

```markdown
---
id: project/discovery-mvp
version: 2.3.0
description: Minimal discovery kata for harness testing
---

# Discovery Kata (MVP)

## Outline

Goal: Load PRD, extract requirements, validate completeness.

1. **Paso 1: Cargar PRD**:
   - Cargar `specs/main/prd.md`
   - Verificar que existe
   - **Verificación**: El archivo existe y tiene frontmatter YAML
   - > **Si no puedes continuar**: PRD no encontrado → **JIDOKA**: Crear PRD manualmente

2. **Paso 2: Extraer Requirements**:
   - Usar LLM para extraer requisitos del PRD
   - Generar lista estructurada en JSON
   - **Verificación**: Al menos 5 requisitos extraídos
   - > **Si no puedes continuar**: Menos de 5 requisitos → **JIDOKA**: Revisar PRD, agregar más contexto

3. **Paso 3: Validar Discovery**:
   - Ejecutar gate de completitud
   - Confirmar que discovery está listo para siguiente fase
   - **Verificación**: Gate `gate-discovery-complete` pasa
   - > **Si no puedes continuar**: Gate falla → **JIDOKA**: Revisar requisitos faltantes
```

#### Test PRD

Create test PRD in `specs/main/prd.md`:

```markdown
---
title: Test PRD for Harness MVP
date: 2026-01-29
status: draft
---

# Product Requirements Document

## Functional Requirements

1. User can create a new project
2. User can add features to a project
3. User can view project status
4. User can generate reports
5. User can export data
6. User can invite collaborators

## Non-Functional Requirements

- Performance: API response < 200ms
- Security: OAuth 2.0 authentication
```

---

## Integration Testing

### End-to-End Test Flow

```bash
# 1. Compile Kata
cd .raise/harness
node compiler/kata-compiler.ts \
  --input ../../katas/project/discovery-mvp.md \
  --output plans/discovery-mvp.json

# Expected output: plans/discovery-mvp.json created

# 2. Execute Kata
node runtime/kata-harness.ts \
  --plan plans/discovery-mvp.json \
  --project-root /home/emilio/Code/raise-commons

# Expected output:
# ✅ Paso 1: Cargar PRD - COMPLETED
# ✅ Paso 2: Extraer Requirements - COMPLETED
# ✅ Paso 3: Validar Discovery - COMPLETED
# 📊 Trace: discovery-mvp-1738151445
# 📁 Trace log: traces/2026-01-29.jsonl

# 3. Verify Trace
cat traces/2026-01-29.jsonl | jq .

# Expected: Valid JSON with all 3 steps logged

# 4. Test Resume
# Kill process during Paso 2
# Re-run with --resume
node runtime/kata-harness.ts \
  --plan plans/discovery-mvp.json \
  --resume

# Expected: Resumes from Paso 2, skips Paso 1

# 5. Test Gate Failure
# Delete PRD file
rm specs/main/prd.md

# Re-run
node runtime/kata-harness.ts \
  --plan plans/discovery-mvp.json

# Expected: Jidoka error at Paso 1
# Error: Gate gate-prd-loaded failed: PRD not found
```

---

## Definition of Done (Phase 1 MVP)

### Must Have (P0)

- [ ] Kata Compiler parses `discovery-mvp.md` → JSON
- [ ] Harness executes all 3 steps sequentially
- [ ] Gate `gate-prd-loaded` enforces file existence
- [ ] Gate failure halts execution (Jidoka)
- [ ] Checkpoint created after each step
- [ ] Resume from checkpoint works
- [ ] JSONL trace log captures all steps
- [ ] End-to-end test passes

### Should Have (P1)

- [ ] Error messages are descriptive
- [ ] CLI has `--help` option
- [ ] Trace log includes metrics (tokens, latency)
- [ ] README with usage examples
- [ ] TypeScript types for all interfaces

### Could Have (P2)

- [ ] Pretty-print execution progress
- [ ] Trace visualization (ASCII diagram)
- [ ] Replay capability (from trace log)

---

## File Structure (Complete)

```
.raise/
├── katas/
│   └── project/
│       └── discovery-mvp.md
├── skills/
│   ├── file/
│   │   ├── load.yaml
│   │   └── write.yaml
│   ├── llm/
│   │   └── call.yaml
│   └── gate/
│       └── run.yaml
├── gates/
│   ├── gate-prd-loaded.yaml
│   ├── gate-requirements-extracted.yaml
│   └── gate-discovery-complete.yaml
└── harness/
    ├── compiler/
    │   ├── kata-compiler.ts
    │   ├── markdown-parser.ts
    │   ├── step-extractor.ts
    │   ├── skill-mapper.ts
    │   ├── gate-mapper.ts
    │   ├── graph-builder.ts
    │   └── types.ts
    ├── runtime/
    │   ├── kata-harness.ts
    │   ├── state-manager.ts
    │   ├── skill-executor.ts
    │   ├── gate-checker.ts
    │   ├── observer.ts
    │   ├── checkpoint-manager.ts
    │   └── types.ts
    ├── skills/
    │   ├── file-load.ts
    │   ├── file-write.ts
    │   ├── llm-call.ts
    │   ├── gate-run.ts
    │   ├── skill-registry.ts
    │   └── types.ts
    ├── observer/
    │   ├── execution-observer.ts
    │   ├── trace-writer.ts
    │   ├── metrics-collector.ts
    │   └── types.ts
    ├── plans/               # Generated execution graphs
    │   └── discovery-mvp-{timestamp}.json
    ├── traces/              # Execution traces (JSONL)
    │   └── 2026-01-29.jsonl
    ├── checkpoints/         # State snapshots
    │   └── discovery-mvp-{execution-id}.json
    └── README.md
```

---

## Next Steps After MVP

Once MVP passes all tests:

1. **Phase 2**: Expand to all Work Cycles
   - Implement branching logic (conditional transitions)
   - Add loop support (retry up to N times)
   - Implement all skills from taxonomy

2. **Phase 3**: Full observability
   - OpenTelemetry export
   - Replay capability
   - Analysis CLI (`rai trace analyze`)

3. **Phase 4**: Production hardening
   - Performance optimization
   - Error handling polish
   - Developer experience (VSCode extension, autocomplete)

---

**Implementation Start Date**: TBD
**Target Completion**: 4 weeks from start
**Owner**: TBD
