# E1132 Synthesis: Claude Code Architecture Reconstruction

**Phase:** 4 (Synthesis) per ADR-016
**Source:** 16 findings across 4 waves, 35 modules, ~512K LOC analyzed
**Date:** 2026-04-01

---

## 1. Strategic Decisions

### SD-1: RaiSE Distribution — Plugin Package

**Decision:** Package RaiSE as a Claude Code plugin (`plugin.json`) combining skills, hooks, and MCP server.

**Evidence:** F11 (plugin system supports 10 capability types), F1 (skills = commands via SKILL.md), F2 (27 hook events), F3 (MCP is THE tool extension), F9 (all 3 MCP primitives supported).

**Architecture:**
```
raise-plugin/
  .claude-plugin/plugin.json     # Manifest
  commands/                       # Our 19 /rai-* skills as markdown
  hooks/hooks.json               # Session lifecycle, gate enforcement
  .mcp.json                      # RaiSE MCP server config
  userConfig:                    # Jira URL, Confluence URL, API tokens
    jira_url: { type: string, required: true }
    jira_token: { type: string, sensitive: true }
```

**Impact:** Single install, marketplace distribution, user config collects credentials at enable time.

### SD-2: Three Extension Surfaces

**Decision:** All RaiSE-CC integration flows through exactly three surfaces. No internal APIs, no forks.

| Surface | RaiSE Use | CC Mechanism |
|---------|-----------|-------------|
| **SKILL.MD** | `/rai-*` commands | `type: 'prompt'` commands (F1, F4) |
| **MCP Server** | Graph queries, backlog ops, discovery | `mcp__raise__*` tools (F3, F9) |
| **Settings.json hooks** | Gates, session tracking, memory | PreToolUse + lifecycle events (F2) |

### SD-3: Target Post-Deprecation APIs

**Decision:** When building on CC patterns, always use the new API, not the `_DEPRECATED` suffix versions.

**Evidence:** F3 (52 DEPRECATED in tools, incremental migration pattern), reconnaissance (262 DEPRECATED signals, 61% of all signals).

### SD-4: Coordinator-as-Prompt for E3

**Decision:** E3 scaleup-agent should follow CC's pattern: orchestrator intelligence lives in the system prompt, not in code.

**Evidence:** F5 (coordinator is mode flag + 370-line prompt), F6 (dual task system), F7 (query loop is while(true) + State struct).

---

## 2. Actionable Stories for Backlog

### High Priority (direct RaiSE improvement)

| # | Story | Finding | Impact |
|---|-------|---------|--------|
| A1 | **Optimize `when_to_use` in all skills** — model sees this for discovery, max ~250 chars | F1 | Skills discovered more reliably |
| A2 | **Add `allowed-tools` to all skills** — without it, auto-approved silently | F1 | Transparency, correct permission model |
| A3 | **Evaluate `context: fork` for heavy skills** — `/rai-story-implement`, `/rai-epic-design` | F1 | Own token budget, no main context pollution |
| A4 | **Implement gate enforcement via PreToolUse hooks** — `if: "Bash(git commit*)"` → `rai gate check` | F2 | Automated quality gates |
| A5 | **Package RaiSE as CC plugin** — `plugin.json` with skills + hooks + MCP | F11 | Single install, marketplace distribution |
| A6 | **Expose knowledge graph as MCP resources** — not just tools | F9 | CC can browse graph data natively |

### Medium Priority (E3 / architecture)

| # | Story | Finding | Impact |
|---|-------|---------|--------|
| B1 | **Design E3 coordinator prompt** — follow CC's pattern (mode flag + system prompt) | F5 | Proven architecture for multi-agent |
| B2 | **Implement dual task system** — runtime (in-memory) + planning (filesystem JSON with locking) | F6 | Separation of concerns for E3 |
| B3 | **Implement claimTask() atomic claiming** — one task per agent, busy-check | F6 | Prevents double-work in multi-agent |
| B4 | **Add `paths` frontmatter to language-specific skills** — conditional visibility | F1 | Skills appear only when relevant |
| B5 | **Configure `alwaysAllowRules` for trusted RaiSE MCP tools** — avoid permission fatigue | F3, F9 | Smoother developer experience |

### Low Priority (future / research)

| # | Story | Finding | Impact |
|---|-------|---------|--------|
| C1 | **Evaluate HTTP hooks for server-side governance** — RaiSE server enforcement | F2 | No local process needed for gates |
| C2 | **Explore MCP prompts as governance workflows** — expose as slash commands | F9 | Alternative to skills for simple flows |
| C3 | **Design for enterprise lockdown** — `allowManagedMcpServersOnly` blocks non-managed | F9 | Enterprise deployment readiness |
| C4 | **Monitor GrowthBook flag changes** — `tengu_*` flags can alter behavior between sessions | F15 | Operational awareness |

---

## 3. Patterns to Adopt

### From CC → RaiSE

| Pattern | Source | Description | Adopt? |
|---------|--------|-------------|:------:|
| Convention over configuration | F1-F4 | SKILL.md in dir = command, MCP server = tool, settings.json = hook | ✓ Already doing |
| Prompt-driven coordination | F5 | Orchestrator intelligence in system prompt, not code | ✓ For E3 |
| Dual task system | F6 | Separate runtime tracking from work planning | ✓ For E3 |
| AsyncGenerator streaming | F7 | Progressive output, composable pipeline layers | Consider |
| while(true) + State struct | F7 | Explicit state machine (not recursion) for agent loops | ✓ For E3 |
| Filesystem scratchpad | F5 | Cross-agent shared state via files | ✓ Simple, observable |
| Sticky-on latches | F16 | Once activated, never deactivate (cache stability) | Consider |
| DAG leaf for global state | F16 | ESLint-enforced isolation prevents circular deps | ✓ For bootstrap modules |
| Background memory extraction | F13 | Forked cheap model reviews transcripts post-turn | Research |
| Sonnet side-query for recall | F13 | Cheap classifier for memory relevance | Research |

### CC Patterns to Avoid

| Pattern | Source | Why Avoid |
|---------|--------|-----------|
| 4,683-line god file (main.tsx) | Recon | Maintainability nightmare |
| 5-layer compaction (accretion) | F7 | Design context management upfront |
| God module (utils: 564 files, 18 imports) | Recon | Utility layer should not contain business logic |
| Global mutable singleton (bootstrap) | F16 | Works for CC but doesn't scale; prefer DI |
| `_DEPRECATED` suffix migration | F3 | Works but creates long transition periods |

---

## 4. Architecture Model (consolidated)

### CC's Extension Stack

```
Layer 5: Plugin Package        ← Distribution unit (skills + hooks + MCP)
Layer 4: Three Extension Surfaces
           ├── SKILL.MD files  ← Commands (prompt injection)
           ├── MCP Servers     ← Tools (model-invoked, Zod-validated)
           └── Settings.json   ← Hooks (27 events, 6 types)
Layer 3: Permission System     ← 9-step resolution chain, 8 rule sources
Layer 2: Query Pipeline        ← while(true), 5-layer compaction, AsyncGenerator
Layer 1: State Management      ← AppState (single atom) + Bootstrap (singleton)
Layer 0: Persistence           ← Filesystem (tasks, memory, config, output)
```

### CC's Agent Orchestration Stack

```
Coordinator System Prompt  → What to do (intelligence)
Agent Tool + Task Tools    → How to do it (orchestration API)
Query Pipeline             → LLM interaction loop
Dual Task System           → Runtime (memory) + Planning (filesystem)
State Store                → Single atom, reactive
Filesystem + Locking       → Persistence + cross-agent coordination
```

---

## 5. Key Numbers

| Metric | Value |
|--------|-------|
| Modules analyzed | 35 |
| Root files analyzed | 8 |
| Findings produced | 16 |
| Total components | 11,358 |
| Total exports | 7,907 |
| Technical debt signals | 429 (61% DEPRECATED) |
| Feature flags | 145 (92 compile + 53 runtime) |
| Hook events | 27 |
| Tool count | ~40+ built-in |
| Plugin capabilities | 10 types |
| MCP config scopes | 6 |
| Tooling analysis time | ~3 seconds |
| Research agent time | ~4 waves × 4 agents × ~2 min = ~32 min |
| Confluence pages published | 5 |
| Actionable stories identified | 15 |

---

## 6. Process Lessons (for rai-discover playbook)

### What Worked

1. **Dogfooding tooling first** — Building TypeScriptAnalyzer + SignalScanner before analysis gave us automated reconnaissance in 3 seconds
2. **Parallel research agents** — 4 agents per wave, ~2 min each, produced consistent structured findings
3. **ADR-016 method** — Reconnaissance → Hypothesis → Deep Dives → Synthesis provided clear structure
4. **Wave prioritization by business value** — Extension Points first (direct impact), UI last (indirect)
5. **Small batch sizes** — 4 stories for tooling (lean), 4 waves for analysis (focused)

### What Could Improve

1. **No automated E2E validation** of findings — agent findings are source-code authoritative but not cross-checked
2. **Wave 5 (UI) skipped** — acceptable for RaiSE but incomplete for full reconstruction
3. **Entry point detection (S1132.0d) deferred** — source had no package.json
4. **No performance analysis** — module sizes known but no runtime profiling
5. **Retrospectives deferred** — should batch after synthesis, not at epic close

### Productizable for rai-discover

| Component | Status | Productize? |
|-----------|--------|:-----------:|
| TypeScriptAnalyzer (tree-sitter) | Done, tested | ✓ Ship in 2.4.0 |
| SignalScanner (regex) | Done, tested | ✓ Ship in 2.4.0 |
| Module dependency aggregation | Done, tested | ✓ Ship in 2.4.0 |
| Parallel research agents | Manual (prompt-driven) | Research — needs structured output |
| Finding format (F1-F16) | Convention | ✓ Document in playbook |
| Wave prioritization | Manual | Consider — heuristic based on relevance ratings |
| Confluence publication | Manual | ✓ Automate via `rai docs publish` |

---

*Epic E1132 — Claude Code Architecture Reconstruction*
*Method: ADR-016 — Architecture Reconstruction Practice*
*16 findings, 4 waves, 35 modules, ~512K LOC*
*Generated 2026-04-01*
