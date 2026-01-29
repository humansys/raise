---
id: kata-harness-architecture-diagrams
title: "Kata Harness Architecture: Visual Reference"
date: 2026-01-29
status: complete
purpose: visual-documentation
related_to: ["kata-harness-first-principles-taxonomy", "kata-harness-executive-summary"]
---

# Kata Harness Architecture: Visual Reference

This document provides visual diagrams for the recommended Kata Harness architecture.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Execution Primitive Relationships](#execution-primitive-relationships)
3. [Compilation Flow](#compilation-flow)
4. [Runtime Execution Flow](#runtime-execution-flow)
5. [State Management](#state-management)
6. [Observability Flow](#observability-flow)
7. [Comparison: Current vs Recommended](#comparison-current-vs-recommended)

---

## High-Level Architecture

### The 3-Layer Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      LAYER 1: AUTHORING                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  Human-authored artifacts (Git-versioned)                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Katas      │  │   Skills     │  │    Gates     │          │
│  │ (Markdown)   │  │   (YAML)     │  │   (YAML)     │          │
│  │              │  │              │  │              │          │
│  │ .raise/      │  │ .raise/      │  │ .raise/      │          │
│  │  katas/      │  │  skills/     │  │  gates/      │          │
│  │   project/   │  │   context/   │  │   gate-*.    │          │
│  │   feature/   │  │   file/      │  │    yaml      │          │
│  │   setup/     │  │   llm/       │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Kata Compiler   │
                    │                  │
                    │  - Parse MD      │
                    │  - Extract steps │
                    │  - Resolve deps  │
                    │  - Generate JSON │
                    └──────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LAYER 2: EXECUTION PLAN                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  Machine-readable workflow definition (JSON)                     │
│                                                                  │
│  {                                                               │
│    "kata_id": "project/discovery",                               │
│    "version": "2.3.0",                                           │
│    "steps": [                                                    │
│      {                                                           │
│        "id": "paso-1",                                           │
│        "description": "Cargar PRD",                              │
│        "skill": "file/load",                                     │
│        "inputs": {"path": "specs/main/prd.md"},                  │
│        "verification": {                                         │
│          "gate": "gate-prd-loaded",                              │
│          "blocking": true                                        │
│        },                                                        │
│        "on_failure": "escalate",                                 │
│        "next": "paso-2"                                          │
│      },                                                          │
│      {...}                                                       │
│    ]                                                             │
│  }                                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  ┌────────────────────────┐
                  │  Kata Harness Runtime  │
                  │                        │
                  │  - State machine       │
                  │  - Gate enforcement    │
                  │  - Checkpointing       │
                  │  - Observability       │
                  └────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 3: EXECUTION                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  State Machine Orchestrator                            │    │
│  │  ────────────────────────────────────────────────────  │    │
│  │                                                         │    │
│  │  For each step:                                        │    │
│  │    1. Load step definition                             │    │
│  │    2. Check pre-gate (if exists)                       │    │
│  │    3. Execute skill                                    │    │
│  │    4. Check post-gate (verification)                   │    │
│  │    5. Log trace event                                  │    │
│  │    6. Checkpoint state                                 │    │
│  │    7. Transition to next OR halt (Jidoka)              │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Skill Executors                                       │    │
│  │  ────────────────────────────────────────────────────  │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │ file/    │  │ context/ │  │ llm/     │            │    │
│  │  │  load    │  │  get-mvc │  │  call    │    ...     │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Observer (Telemetry)                                  │    │
│  │  ────────────────────────────────────────────────────  │    │
│  │                                                         │    │
│  │  - Trace events → JSONL file                           │    │
│  │  - Optional: Export to OpenTelemetry                   │    │
│  │  - Metrics: tokens, latency, gate pass/fail            │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  Outputs         │
                    │  ──────────────  │
                    │  - Artifacts     │
                    │  - Trace logs    │
                    │  - Checkpoints   │
                    └──────────────────┘
```

---

## Execution Primitive Relationships

### The 8 Core Primitives

```
┌─────────────────────────────────────────────────────────────┐
│                       WORKFLOW                               │
│  (Composition: Directed graph of steps)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  STEP 1                                            │    │
│  │  ─────────────────────────────────────────────────│    │
│  │                                                     │    │
│  │  ┌──────────┐   ┌───────────┐   ┌──────────┐     │    │
│  │  │ Pre-GATE │ → │ OPERATION │ → │ Post-GATE│     │    │
│  │  └──────────┘   └───────────┘   └──────────┘     │    │
│  │       ↓              ↓                ↓            │    │
│  │    [Check]      [Execute]        [Verify]         │    │
│  │                      ↓                             │    │
│  │              ┌───────────────┐                     │    │
│  │              │ CONTEXT MGR   │                     │    │
│  │              │ (Manage state)│                     │    │
│  │              └───────────────┘                     │    │
│  │                      ↓                             │    │
│  │              ┌───────────────┐                     │    │
│  │              │  STATE        │                     │    │
│  │              │  (Shared data)│                     │    │
│  │              └───────────────┘                     │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                        ↓                                     │
│                  [TRANSITION]                                │
│                   (Control flow)                             │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  STEP 2                                             │    │
│  │  ────────────────────────────────────────────────── │    │
│  │  (Same structure)                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                        ↓                                     │
│                       ...                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                        ↓
              ┌──────────────────┐
              │    OBSERVER      │
              │  (Trace all)     │
              └──────────────────┘
```

**Primitive Definitions**:

1. **OPERATION**: Atomic unit of work (skill execution)
2. **STEP**: Operation + pre/post conditions (gates)
3. **TRANSITION**: How to move between steps
4. **STATE**: Persistent data shared across steps
5. **WORKFLOW**: Graph of steps connected by transitions
6. **GATE**: Checkpoint enforcing criteria
7. **CONTEXT MANAGER**: Controls information available to operations
8. **OBSERVER**: Captures execution traces

---

## Compilation Flow

### From Markdown to Executable Graph

```
┌───────────────────────────────────────────────────────────────┐
│  INPUT: Kata Markdown                                          │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  ---                                                           │
│  id: project/discovery                                         │
│  version: 2.3.0                                                │
│  ---                                                           │
│                                                                │
│  ## Outline                                                    │
│                                                                │
│  1. **Paso 1: Cargar PRD**:                                    │
│     - Cargar `specs/main/prd.md`                               │
│     - Verificar que existe                                     │
│     **Verificación**: El archivo existe y tiene frontmatter    │
│     > **Si no puedes continuar**: PRD no encontrado →          │
│       Ejecutar `/raise.discovery`                              │
│                                                                │
│  2. **Paso 2: Extraer Requirements**:                          │
│     - Usar LLM para extraer requisitos del PRD                 │
│     - Generar lista estructurada                               │
│     **Verificación**: Al menos 5 requisitos extraídos          │
│                                                                │
└───────────────────────────────────────────────────────────────┘
                              ↓
              ┌───────────────────────────┐
              │   KATA COMPILER           │
              │   ───────────────────────  │
              │                           │
              │   1. Parse frontmatter    │
              │   2. Extract steps from   │
              │      "## Outline"         │
              │   3. For each step:       │
              │      - Extract actions    │
              │      - Map to skills      │
              │      - Extract gate       │
              │      - Extract Jidoka     │
              │   4. Build dependency     │
              │      graph                │
              │   5. Generate JSON        │
              │                           │
              └───────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│  OUTPUT: Execution Graph JSON                                  │
│  ────────────────────────────────────────────────────────────  │
│                                                                │
│  {                                                             │
│    "kata_id": "project/discovery",                             │
│    "version": "2.3.0",                                         │
│    "steps": [                                                  │
│      {                                                         │
│        "id": "paso-1",                                         │
│        "description": "Cargar PRD",                            │
│        "skill": "file/load",                                   │
│        "inputs": {                                             │
│          "path": "specs/main/prd.md"                           │
│        },                                                      │
│        "verification": {                                       │
│          "gate": "gate-prd-loaded",                            │
│          "blocking": true                                      │
│        },                                                      │
│        "on_failure": "escalate",                               │
│        "escalation_message": "Ejecutar `/raise.discovery`",    │
│        "next": "paso-2"                                        │
│      },                                                        │
│      {                                                         │
│        "id": "paso-2",                                         │
│        "description": "Extraer Requirements",                  │
│        "skill": "llm/call",                                    │
│        "inputs": {                                             │
│          "prompt": "Extraer requisitos del PRD",               │
│          "context": ["{{state.prd_content}}"]                  │
│        },                                                      │
│        "verification": {                                       │
│          "gate": "gate-requirements-extracted",                │
│          "blocking": true                                      │
│        },                                                      │
│        "on_failure": "retry",                                  │
│        "max_retries": 3,                                       │
│        "next": "paso-3"                                        │
│      }                                                         │
│    ]                                                           │
│  }                                                             │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

## Runtime Execution Flow

### Step-by-Step Execution with Enforcement

```
┌────────────────────────────────────────────────────────────┐
│  START: Execute Kata                                        │
└────────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Load Execution Graph         │
        │  (compiled JSON)              │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Initialize State             │
        │  - Load checkpoint (if resume)│
        │  - Create new context         │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Start Trace                  │
        │  (assign trace_id)            │
        └───────────────────────────────┘
                        ↓
    ┌───────────────────────────────────────┐
    │  FOR EACH STEP in graph:              │
    └───────────────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Log: Step Started            │
        │  (step_id, timestamp)         │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Pre-Gate Check               │
        │  (if defined)                 │
        └───────────────────────────────┘
                        ↓
              ┌─────────────┐
              │  Passed?    │
              └─────────────┘
                 │        │
           Yes   │        │  No
                 ↓        ↓
        ┌─────────┐  ┌────────────────┐
        │Continue │  │ JIDOKA: HALT   │
        └─────────┘  │ Log failure    │
                     │ Escalate/Retry │
                     └────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Load Skill Definition        │
        │  (YAML spec)                  │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Execute Skill                │
        │  (atomic operation)           │
        │  - Get inputs from state      │
        │  - Run skill handler          │
        │  - Capture outputs            │
        └───────────────────────────────┘
                        ↓
              ┌─────────────┐
              │  Success?   │
              └─────────────┘
                 │        │
           Yes   │        │  No
                 ↓        ↓
        ┌─────────┐  ┌────────────────┐
        │Continue │  │ Error Handler  │
        └─────────┘  │ - Retry logic  │
                     │ - Escalation   │
                     └────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Update State                 │
        │  (merge skill outputs)        │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Post-Gate Check              │
        │  (verification)               │
        └───────────────────────────────┘
                        ↓
              ┌─────────────┐
              │  Passed?    │
              └─────────────┘
                 │        │
           Yes   │        │  No
                 ↓        ↓
        ┌─────────┐  ┌────────────────┐
        │Continue │  │ JIDOKA: HALT   │
        └─────────┘  │ (blocking gate)│
                     └────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Log: Step Completed          │
        │  (outputs, metrics)           │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Checkpoint State             │
        │  (save to disk)               │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Resolve Next Step            │
        │  (transition logic)           │
        └───────────────────────────────┘
                        ↓
              ┌─────────────┐
              │  More steps?│
              └─────────────┘
                 │        │
           Yes   │        │  No
                 ↓        ↓
        ┌─────────┐  ┌────────────────┐
        │ Loop    │  │ Complete Trace │
        └─────────┘  │ Mark success   │
                     └────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  FINISH: Kata Executed        │
        │  - Return trace_id            │
        │  - Artifacts created          │
        │  - Metrics collected          │
        └───────────────────────────────┘
```

---

## State Management

### Checkpoint and Resume Flow

```
┌────────────────────────────────────────────────────────────┐
│  Execution State Structure                                  │
│  ────────────────────────────────────────────────────────  │
│                                                             │
│  {                                                          │
│    "kata_id": "project/discovery",                          │
│    "execution_id": "discovery-f14-1738151445",              │
│    "status": "in_progress",                                 │
│    "current_step": "paso-2",                                │
│    "completed_steps": ["paso-1"],                           │
│    "context": {                                             │
│      "prd_content": "...",                                  │
│      "requirements": [...],                                 │
│      "token_budget_remaining": 45000                        │
│    },                                                       │
│    "checkpointed_at": "2026-01-29T10:35:20Z"                │
│  }                                                          │
│                                                             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  Normal Execution Flow                                      │
└────────────────────────────────────────────────────────────┘

    Step 1 → Checkpoint → Step 2 → Checkpoint → Step 3 → Done
      ↓          ↓          ↓          ↓          ↓
    [Save]    [Save]    [Save]    [Save]    [Save]

┌────────────────────────────────────────────────────────────┐
│  Interrupted Execution Flow                                 │
└────────────────────────────────────────────────────────────┘

    Step 1 → Checkpoint → Step 2 → CRASH ⚠
      ↓          ↓          ↓
    [Save]    [Save]    [Save]
                           │
                           │ Resume from last checkpoint
                           ↓
                  Load checkpoint (paso-2)
                           ↓
                      Continue → Step 3 → Done

┌────────────────────────────────────────────────────────────┐
│  Manual Resume Flow                                         │
└────────────────────────────────────────────────────────────┘

    User runs: `raise kata project/discovery --resume paso-2`
                           ↓
                  Load checkpoint (paso-2)
                           ↓
                  Restore state (context, completed steps)
                           ↓
                      Continue from paso-2
```

---

## Observability Flow

### MELT Stack Implementation

```
┌─────────────────────────────────────────────────────────────┐
│  METRICS (Quantitative)                                      │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Collected per step:                                         │
│  - Tokens used (prompt + completion)                         │
│  - Latency (start to finish)                                 │
│  - Gate pass/fail rate                                       │
│                                                              │
│  Aggregated per kata:                                        │
│  - Total tokens                                              │
│  - Total duration                                            │
│  - Escalation count                                          │
│  - Success/failure rate                                      │
│                                                              │
│  Storage: Time-series DB or aggregated in trace              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  EVENTS (Discrete Occurrences)                               │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Captured events:                                            │
│  - Kata started                                              │
│  - Step started                                              │
│  - Step completed                                            │
│  - Step failed                                               │
│  - Gate passed                                               │
│  - Gate failed                                               │
│  - Escalation triggered                                      │
│  - Kata completed                                            │
│  - Kata failed                                               │
│                                                              │
│  Format: Event name + timestamp + context                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LOGS (Contextual Messages)                                  │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Logged messages:                                            │
│  - "Loaded PRD from specs/main/prd.md"                       │
│  - "Verification failed: Missing frontmatter"                │
│  - "Retrying step paso-2 (attempt 2/3)"                      │
│  - "Escalation: Human approval required"                     │
│                                                              │
│  Format: Structured logs (JSON) with levels                  │
│  - INFO, WARN, ERROR                                         │
│                                                              │
│  Storage: JSONL file                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TRACES (End-to-End Flow)                                    │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Trace structure:                                            │
│  {                                                           │
│    "trace_id": "discovery-f14-1738151445",                   │
│    "kata_id": "project/discovery",                           │
│    "started_at": "...",                                      │
│    "completed_at": "...",                                    │
│    "status": "success",                                      │
│    "steps": [                                                │
│      {                                                       │
│        "step_id": "paso-1",                                  │
│        "started_at": "...",                                  │
│        "completed_at": "...",                                │
│        "status": "success",                                  │
│        "skill": "file/load",                                 │
│        "inputs": {...},                                      │
│        "outputs": {...},                                     │
│        "verification": {                                     │
│          "gate": "gate-prd-loaded",                          │
│          "result": "pass"                                    │
│        },                                                    │
│        "metrics": {                                          │
│          "tokens_used": 1250,                                │
│          "latency_ms": 340                                   │
│        }                                                     │
│      },                                                      │
│      {...}                                                   │
│    ]                                                         │
│  }                                                           │
│                                                              │
│  Storage: JSONL (one line per trace)                         │
│  Optional: Export to OpenTelemetry backend                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                        ↓ ↓ ↓

┌─────────────────────────────────────────────────────────────┐
│  ANALYSIS & REPLAY                                           │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Queries:                                                    │
│  - "Which katas failed most often?"                          │
│  - "Which steps take longest?"                               │
│  - "Which gates fail most frequently?"                       │
│                                                              │
│  Replay:                                                     │
│  - Load trace by trace_id                                    │
│  - Re-execute using cached LLM responses                     │
│  - Compare expected vs actual outputs                        │
│                                                              │
│  Kaizen:                                                     │
│  - Identify bottlenecks → optimize                           │
│  - Identify failure patterns → improve katas/gates           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparison: Current vs Recommended

### Current Approach (Markdown + LLM)

```
┌──────────────────────────────────────────────────────────┐
│  Kata Markdown File                                       │
│  ───────────────────────────────────────────────────────  │
│  ## Outline                                               │
│  1. Paso 1: Cargar PRD                                    │
│     - Cargar specs/main/prd.md                            │
│     **Verificación**: Archivo existe                      │
│  2. Paso 2: Extraer requirements                          │
│     - Usar LLM...                                         │
└──────────────────────────────────────────────────────────┘
                        ↓
            ┌───────────────────────┐
            │  LLM Interprets       │
            │  (probabilistic)      │
            └───────────────────────┘
                        ↓
            ┌───────────────────────┐
            │  LLM Executes         │
            │  - May skip steps     │
            │  - May hallucinate    │
            │  - May ignore gates   │
            └───────────────────────┘
                        ↓
            ┌───────────────────────┐
            │  Manual Logging       │
            │  (progress.md)        │
            │  - LLM updates file   │
            │  - No enforcement     │
            └───────────────────────┘

Problems:
❌ No step ordering guarantee
❌ Gates are suggestions
❌ Manual state management
❌ No automatic observability
❌ Hard to debug (LLM black box)
```

### Recommended Approach (Harness)

```
┌──────────────────────────────────────────────────────────┐
│  Kata Markdown File (same authoring)                      │
│  ───────────────────────────────────────────────────────  │
│  ## Outline                                               │
│  1. Paso 1: Cargar PRD                                    │
│     - Cargar specs/main/prd.md                            │
│     **Verificación**: Archivo existe                      │
│  2. Paso 2: Extraer requirements                          │
│     - Usar LLM...                                         │
└──────────────────────────────────────────────────────────┘
                        ↓
            ┌───────────────────────┐
            │  Kata Compiler        │
            │  (deterministic)      │
            └───────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Execution Graph JSON                                     │
│  {                                                        │
│    "steps": [                                             │
│      {"id": "paso-1", "skill": "file/load", ...},         │
│      {"id": "paso-2", "skill": "llm/call", ...}           │
│    ]                                                      │
│  }                                                        │
└──────────────────────────────────────────────────────────┘
                        ↓
            ┌───────────────────────┐
            │  State Machine        │
            │  (enforced execution) │
            └───────────────────────┘
                        ↓
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Pre-Gate   │→ │ Skill Exec │→ │ Post-Gate  │
    │ (enforced) │  │ (atomic)   │  │ (enforced) │
    └────────────┘  └────────────┘  └────────────┘
                        ↓
            ┌───────────────────────┐
            │  Automatic Logging    │
            │  (JSONL traces)       │
            │  - Every step logged  │
            │  - Enforced by harness│
            └───────────────────────┘

Benefits:
✅ Step ordering enforced
✅ Gates are blocking
✅ Automatic state management
✅ Built-in observability
✅ Replay capability for debugging
```

---

## Summary

The recommended 3-layer architecture provides:

1. **Familiar authoring** (Markdown katas)
2. **Enforced execution** (state machine harness)
3. **Complete observability** (MELT stack)
4. **Resumability** (automatic checkpointing)
5. **Jidoka compliance** (blocking gates, halt on failure)

This architecture honors all RaiSE principles while providing the enforcement guarantees that the current markdown-only approach cannot deliver.

---

**Next Steps**: Prototype the Kata Compiler and minimal State Machine Orchestrator (Phase 1 MVP).
