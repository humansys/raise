# E1132 Reconnaissance: Claude Code Architecture Map

**Phase:** 1 (Reconnaissance) per ADR-016
**Source:** `~/Code/claude-code-main/src/` — 1,902 .ts/.tsx files
**Generated:** 2026-04-01 via TypeScriptAnalyzer + SignalScanner (dogfood)

---

## 1. Module Catalog

35 top-level modules under `src/`. Sorted by component count (descending).

| # | Module | Files | Size | Components | Exports | Imports | Signals | RaiSE Relevance |
|---|--------|------:|-----:|-----------:|--------:|--------:|--------:|:---------------:|
| 1 | **utils** | 564 | 6.3M | 4711 | 3556 | 18 | 214 | Media |
| 2 | **components** | 389 | 9.1M | 1686 | 622 | 20 | 35 | Baja |
| 3 | **services** | 130 | 1.8M | 1127 | 797 | 16 | 35 | Alta |
| 4 | **tools** | 184 | 2.6M | 873 | 453 | 16 | 63 | Alta |
| 5 | **ink** | 96 | 1.0M | 491 | 383 | 2 | 6 | Baja |
| 6 | **commands** | 189 | 2.4M | 423 | 97 | 19 | 18 | Alta |
| 7 | **hooks** | 104 | 1.2M | 337 | 184 | 22 | 13 | Alta |
| 8 | **bootstrap** | 1 | 55K | 218 | 215 | 0 | 0 | Media |
| 9 | **bridge** | 31 | 467K | 192 | 161 | 8 | 3 | Media |
| 10 | **types** | 11 | 111K | 155 | 124 | 6 | 5 | Media |
| 11 | **native-ts** | 4 | 125K | 123 | 39 | 2 | 0 | Baja |
| 12 | **cli** | 19 | 489K | 111 | 69 | 13 | 6 | Media |
| 13 | **tasks** | 12 | 320K | 107 | 92 | 8 | 1 | Alta |
| 14 | **keybindings** | 14 | 143K | 82 | 59 | 4 | 2 | Baja |
| 15 | **skills** | 20 | 147K | 78 | 44 | 7 | 3 | Alta |
| 16 | **constants** | 21 | 112K | 60 | 161 | 7 | 13 | Media |
| 17 | **context** | 9 | 106K | 57 | 36 | 4 | 0 | Alta |
| 18 | **vim** | 5 | 41K | 55 | 39 | 1 | 0 | Baja |
| 19 | **memdir** | 8 | 81K | 44 | 48 | 4 | 0 | Alta |
| 20 | **screens** | 3 | 1.0M | 42 | 5 | 18 | 3 | Baja |
| 21 | **buddy** | 6 | 73K | 40 | 53 | 6 | 0 | Baja |
| 22 | **entrypoints** | 8 | 152K | 35 | 220 | 4 | 3 | Media |
| 23 | **state** | 6 | 58K | 29 | 24 | 9 | 2 | Alta |
| 24 | **remote** | 4 | 32K | 27 | 14 | 4 | 0 | Baja |
| 25 | **upstreamproxy** | 2 | 24K | 23 | 9 | 1 | 0 | Baja |
| 26 | **migrations** | 11 | 20K | 11 | 11 | 3 | 2 | Baja |
| 27 | **query** | 4 | 22K | 11 | 8 | 7 | 0 | Alta |
| 28 | **server** | 3 | 9K | 11 | 11 | 3 | 0 | Baja |
| 29 | **plugins** | 2 | 6K | 8 | 8 | 3 | 2 | Media |
| 30 | **schemas** | 1 | 8K | 8 | 10 | 1 | 0 | Baja |
| 31 | **assistant** | 1 | 2K | 7 | 6 | 3 | 0 | Media |
| 32 | **coordinator** | 1 | 19K | 5 | 4 | 4 | 0 | Alta |
| 33 | **voice** | 1 | 2K | 3 | 3 | 2 | 0 | Baja |
| 34 | **moreright** | 1 | 3K | 2 | 1 | 0 | 0 | Baja |
| 35 | **outputStyles** | 1 | 3K | 1 | 2 | 2 | 0 | Baja |

### Root Files (not in modules)

| File | Size | Purpose |
|------|-----:|---------|
| main.tsx | 804K | Entry point — CLI parsing, init, REPL launch |
| query.ts | 69K | Query orchestration |
| QueryEngine.ts | 47K | Core LLM caller |
| interactiveHelpers.tsx | 57K | Interactive UI helpers |
| Tool.ts | 30K | Tool base types and protocol |
| commands.ts | 25K | Command registry |
| tools.ts | 17K | Tool registry |
| context.ts | 6K | System/user context collection |

---

## 2. Dependency Map

### Dependency Hubs (most depended-upon)

| Module | Dependents | Role |
|--------|--------:|------|
| **utils** | 32 | Universal utility layer — every module depends on it |
| **services** | 20 | Business logic services (MCP, API, analytics, policy) |
| **bootstrap** | 18 | Configuration/initialization — zero imports itself |
| **types** | 17 | Shared type definitions |
| **constants** | 14 | Feature flags, product constants |
| **tools** | 13 | Tool system |
| **ink** | 12 | Rendering primitives |
| **state** | 12 | Application state management |
| **hooks** | 10 | React hooks for UI + permissions |
| **keybindings** | 10 | Keyboard configuration |

### Highest Coupling (most imports)

| Module | Imports | Observation |
|--------|--------:|------------|
| **hooks** | 22 | Cross-cutting concern — touches almost everything |
| **components** | 20 | UI orchestration — assembles all features |
| **commands** | 19 | Command implementations need broad access |
| **screens** | 18 | Full screens compose commands + components + services |
| **utils** | 18 | Utility layer surprisingly imports from many modules |

### Architectural Layers (inferred from dependency flow)

```
Layer 0 — Foundation (zero or minimal imports):
  bootstrap, moreright, types (partial)

Layer 1 — Infrastructure:
  ink, utils, constants, schemas, types

Layer 2 — Domain Services:
  services, tools, tasks, memdir, context, state, skills, query, coordinator

Layer 3 — Features:
  commands, hooks, bridge, entrypoints, cli

Layer 4 — Composition:
  components, screens

Layer 5 — Entry:
  main.tsx → launchRepl → screens → components
```

### Anomalies

- **utils imports 18 modules** — a utility layer should ideally import nothing or only foundation modules. This suggests utils/ contains business logic, not just pure utilities.
- **hooks imports 22 modules** — highest coupling in the codebase. Hooks are cross-cutting React hooks for permissions, tools, UI state.
- **bootstrap has 218 components but 0 imports** — it's a pure configuration/type module, likely re-exporting generated or static config.

---

## 3. Entry Point Trace

```
main.tsx (4,683 lines)
  ├─ Side effects at import time:
  │   ├─ profileCheckpoint('main_tsx_entry')   ← startup profiling
  │   ├─ startMdmRawRead()                    ← MDM settings prefetch (parallel)
  │   └─ startKeychainPrefetch()              ← macOS keychain prefetch (parallel)
  │
  ├─ Feature-gated imports:
  │   ├─ COORDINATOR_MODE → coordinator/coordinatorMode.js
  │   └─ KAIROS → assistant/index.js
  │
  ├─ run() → main()
  │   ├─ eagerLoadSettings()                  ← parse --settings flag
  │   ├─ init()                               ← full initialization
  │   ├─ Commander CLI parsing                ← 20+ subcommands
  │   └─ launchRepl(root, config, renderAndRun)
  │       └─ REPL.tsx (in screens/)           ← main interaction loop
  │           ├─ Query engine                  ← LLM calls
  │           ├─ Tool dispatch                 ← tool execution
  │           └─ MCP connections               ← server management
  │
  └─ startDeferredPrefetches()                ← after first render
      ├─ analytics, feature flags
      ├─ settings/skill change detectors
      └─ autoupdate check
```

Key insight: **main.tsx is 4,683 lines** — a god file that handles all CLI modes (interactive, print, pipe, remote, resume, teleport, assistant, conversation-viewer). Refactoring target.

---

## 4. Signal Distribution

### Global Summary

| Tag | Count | % |
|-----|------:|--:|
| DEPRECATED | 262 | 61% |
| TODO | 134 | 31% |
| @deprecated | 29 | 7% |
| XXX | 4 | 1% |
| **Total** | **429** | |

### Hotspots (top 5 by signal density)

| Module | Signals | Dominant Tag | Interpretation |
|--------|--------:|:------------:|----------------|
| utils | 214 | DEPRECATED (140) | Massive deprecation wave in progress |
| tools | 63 | DEPRECATED (52) | Tool API in transition |
| components | 35 | DEPRECATED (25) | UI component migration |
| services | 35 | TODO (21) | Active development, unfinished work |
| commands | 18 | DEPRECATED (11) | Command API in transition |

**Key insight:** 61% of signals are DEPRECATED — Claude Code is mid-migration from old APIs to new ones. This is relevant for RaiSE: we should target the NEW APIs, not the deprecated ones.

---

## 5. Interest Areas & Wave Assignment

### Wave 1: Extension Points (direct RaiSE impact)

| Module | Why | Hypothesis |
|--------|-----|-----------|
| **skills** | We build skills — need to match CC's contracts | How does CC load, validate, and execute a skill? What contracts does it assume? |
| **hooks** | Our hooks extend CC's permission model | How are permissions resolved? What info does the hook have at execution time? |
| **tools** | We may need custom tools | How is a tool registered? Is it extensible or hardcoded? What's the new API (post-deprecation)? |
| **commands** | We build slash commands | How is a command registered and dispatched? |

### Wave 2: Agent Infrastructure (informs E3 scaleup-agent)

| Module | Why | Hypothesis |
|--------|-----|-----------|
| **coordinator** | Multi-agent orchestration | How does CC coordinate sub-agents? What context do they share? |
| **tasks** | Task management across agents | How does CC persist and coordinate tasks? |
| **query** | Core query pipeline | What's the query lifecycle? How does the engine decide what to do? |
| **state** | Application state management | How is state shared across components? |

### Wave 3: Integration Layer (informs adapters E1130/E1131)

| Module | Why | Hypothesis |
|--------|-----|-----------|
| **services** | MCP, API, analytics, policy | How does CC manage MCP connections? What does it assume about servers? |
| **bridge** | IDE integration (VS Code, JetBrains) | How does the bridge protocol work? |
| **plugins** | Plugin system | What can a plugin do? What's the API surface? |
| **entrypoints** | SDK and initialization | How do external consumers initialize CC? |

### Wave 4: State & Persistence (explains bugs we've hit)

| Module | Why | Hypothesis |
|--------|-----|-----------|
| **memdir** | Persistent memory (CLAUDE.md etc.) | How does memdir work? What triggers auto-memory? |
| **context** | System/user context collection | What context does CC collect and inject? |
| **constants** | Feature flags and config | How are feature flags managed? What's gated? |
| **bootstrap** | Configuration/initialization | What's the bootstrap sequence? Why 218 exports with 0 imports? |

### Wave 5: UI & Rendering (understand, lower priority)

| Module | Why | Hypothesis |
|--------|-----|-----------|
| **components** | UI composition layer | How are components structured? |
| **ink** | Rendering framework | What rendering primitives exist? |
| **screens** | REPL, Doctor, Resume screens | How is the main REPL structured? |
| **cli** | CLI parsing and output | How does print mode differ from interactive? |

---

## 6. Key Observations for RaiSE

1. **Target post-deprecation APIs** — 262 DEPRECATED signals mean the codebase is mid-migration. Our integrations should use the new patterns.

2. **utils is a god module** — 564 files, 4711 components, imports 18 other modules. This is where CC puts shared logic, but it has grown beyond a utility role. Contains business logic we may need to understand.

3. **bootstrap is the config spine** — 218 components, 0 imports, 18 dependents. Pure configuration/type definitions. Likely generated or static. Understanding bootstrap tells us what CC configures.

4. **hooks is the permission layer** — 22 imports (highest coupling). This is where CC's permission model lives. Critical for RaiSE since we extend permissions.

5. **coordinator is tiny but strategic** — 1 file, 19K, 5 components. Multi-agent coordination in a single file. High-value for E3 (scaleup-agent).

6. **main.tsx is a 4,683-line god file** — handles all CLI modes. Entry point understanding requires reading this file, but it's orchestration code, not reusable logic.

7. **Feature flags gate major features** — COORDINATOR_MODE, KAIROS (assistant mode). CC uses Bun's dead code elimination with feature flags. We should inventory what's gated.

---

## 7. Reconnaissance Metrics

| Metric | Value |
|--------|-------|
| Modules cataloged | 35/35 |
| Root files cataloged | 8 |
| Total components | 11,358 |
| Total exports | 7,907 |
| Unique inter-module deps | 32 |
| Technical debt signals | 429 |
| DEPRECATED signals | 262 (61%) |
| TODO signals | 134 (31%) |
| Modules with 0 signals | 14 (40%) |
| Analysis time (tooling) | ~3s |
| Method | Automated (TypeScriptAnalyzer + SignalScanner) |

---

*Generated by RaiSE tooling (S1132.0a-c) — dogfood of rai-discover capabilities.*
