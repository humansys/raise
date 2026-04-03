# E1132 Wave 4: State & Persistence — Deep Dive Findings

**Phase:** 2 (Targeted Deep Dives) per ADR-016
**Wave:** 4 — State & Persistence (memdir, context, constants, bootstrap)
**Source:** `~/Code/claude-code-main/src/`
**Date:** 2026-04-01

---

## Executive Summary

1. **Auto-memory is a background extraction agent** (forked Sonnet) that reviews transcripts and writes memories we never asked for. Query-time recall selects up to 5 topic files via Sonnet side-query.

2. **CLAUDE.md is loaded once per session** into user context (not system prompt). Changes mid-session are invisible unless `/compact` fires. Git status is a snapshot that never updates.

3. **Two-tier feature flags:** 92 compile-time (`bun:bundle feature()`), 53 runtime (GrowthBook `tengu_*` obfuscated). COORDINATOR_MODE requires the `ant` build.

4. **Bootstrap is a global mutable singleton** (~90 fields, 210 getters/setters), deliberately kept as a DAG leaf via ESLint rule.

---

## Finding F13: Memdir (Persistent Memory)

**Question:** How does CC's persistent memory work? What triggers auto-memory?

**Files:** `memdir/memdir.ts`, `memdir/memoryTypes.ts`, `memdir/paths.ts`, `memdir/findRelevantMemories.ts`, `memdir/memoryScan.ts`, `memdir/memoryAge.ts`, `memdir/teamMemPaths.ts`, `memdir/teamMemPrompts.ts`, `services/extractMemories/extractMemories.ts`

### Storage Model

- **Location:** `~/.claude/projects/<sanitized-git-root>/memory/`
- **Format:** Individual `.md` files with YAML frontmatter (`name`, `description`, `type`)
- **Index:** `MEMORY.md` — always loaded into system prompt, capped at 200 lines / 25KB
- **Team:** `memory/team/` subdirectory with heavy security (symlink traversal protection)

### Two Save Mechanisms

| Mechanism | Trigger | Model |
|-----------|---------|-------|
| **Inline** | Main agent writes via Write tool when it detects something worth saving | Prompt-driven |
| **Background extraction** | Forked Sonnet agent reviews transcript post-turn | Automatic, uses `extractMemories` |

Background extraction is mutual-exclusive with inline: if main agent wrote memories in the turn range, extraction skips.

### Query-Time Recall

Not all memories loaded — only MEMORY.md index + up to **5 topic files** selected per query via **Sonnet side-query** (cheap classifier, not main model). Memories >1 day old get staleness warnings.

### 4-Type Taxonomy

| Type | Purpose | Scope |
|------|---------|-------|
| `user` | Role, preferences, knowledge | Always private |
| `feedback` | Corrections AND confirmations | Private or team |
| `project` | Ongoing work context | Bias toward team |
| `reference` | Pointers to external systems | Usually team |

Explicitly excluded: code patterns, architecture, git history, debugging solutions, anything in CLAUDE.md.

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| Background extraction writes memories autonomously | Explains "ghost" files in our memory dir |
| Frontmatter description is critical for recall | Side-query matches on description, not content |
| Team memory has heavy security | Good model for multi-developer RaiSE sessions |
| Our MEMORY.md IS the auto-memory index | Loaded every turn, capped at 200 lines |
| Staleness warnings after 1 day | Our memory drift concerns are addressed |

**Confidence:** Alta

---

## Finding F14: Context Collection

**Question:** What context does CC collect and inject into the system prompt?

**Files:** `context.ts`, `utils/claudemd.ts`, `utils/api.ts`, `utils/queryContext.ts`, `constants/prompts.ts`, `constants/systemPromptSections.ts`, `utils/context.ts`, `services/compact/autoCompact.ts`

### Three Context Layers

| Layer | Position | Content | Caching |
|-------|----------|---------|---------|
| **System prompt** | `system` parameter | Instructions, tools, tone, env info, memory prompt | Static zone cached `{scope: 'org'}` |
| **System context** | Appended to system prompt | Git status (snapshot), branch, user | Memoized per session |
| **User context** | First user message `<system-reminder>` | CLAUDE.md files, current date | Memoized, cleared on compact |

### CLAUDE.md Loading Order (lowest → highest priority)

1. **Managed** — `/etc/claude-code/CLAUDE.md`, `.claude/rules/*.md`
2. **User** — `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md`
3. **Project** — Walk from root to CWD: `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md`
4. **Local** — `CLAUDE.local.md` at each level
5. **Additional** — `--add-dir` CLAUDE.md files
6. **AutoMem** — MEMORY.md from memdir (loaded last = highest attention)

### Context Budget

| Window | Auto-compact threshold |
|--------|----------------------|
| 200K tokens | ~167K |
| 1M tokens | ~967K |

No explicit budget split between context and conversation — context is fixed overhead.

### Cache Invalidation

| Event | Clears |
|-------|--------|
| `/clear` | Everything (git, system, user context, session date) |
| `/compact` | User context + memory. NOT git status |
| MCP instructions | Recompute every turn (only dynamic context) |

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| CLAUDE.md loaded once, invisible mid-session | `/compact` needed after editing CLAUDE.md |
| Git status never updates (snapshot) | Only `/clear` refreshes |
| CLAUDE.md is user context, not system prompt | Does NOT benefit from `cache_control` caching |
| AutoMem loads last = highest priority | Our MEMORY.md gets most model attention |
| `@include` directive exists | Can keep CLAUDE.md lean, include reference docs |
| 40K char soft limit per file | Keep combined files well under auto-compact overhead |

**Confidence:** Alta

---

## Finding F15: Constants & Feature Flags

**Question:** How are features gated in CC? What's configurable?

**Files:** `constants/product.ts`, `constants/common.ts`, `constants/apiLimits.ts`, `constants/tools.ts`, `constants/betas.ts`, `constants/system.ts`, `constants/toolLimits.ts`, `constants/keys.ts`, `constants/oauth.ts`, `constants/cyberRiskInstruction.ts`, `constants/prompts.ts`, `services/analytics/growthbook.ts`

### Two-Tier Architecture

| Tier | Mechanism | Count | Resolution |
|------|-----------|------:|-----------|
| **Compile-time** | `feature()` from `bun:bundle` | 92 | Dead-code eliminated at build |
| **Runtime** | GrowthBook `tengu_*` flags | 53 | Fetched from server, cached 20min/6h |
| **Env vars** | `process.env.*` | ~10 | Per-process override |

### Major Compile-Time Flags

| Flag | Feature |
|------|---------|
| KAIROS | Assistant/proactive mode (daily logs, channels, dream) |
| COORDINATOR_MODE | Pure orchestrator (no direct tools) |
| FORK_SUBAGENT | Parallel agent forking |
| BRIDGE_MODE | Remote control / cloud sync |
| EXTRACT_MEMORIES | Background memory extraction |
| TEAMMEM | Team memory |
| BG_SESSIONS | Background sessions (ps/logs/attach) |
| DAEMON | Daemon worker mode |
| VOICE_MODE | Voice input |
| WEB_BROWSER_TOOL | WebView browser automation |

### Hardcoded Limits

| Limit | Value |
|-------|-------|
| Image max | 5MB base64 / 2000x2000px |
| PDF max | 20MB / 100 pages API / 20 pages per Read |
| Tool result max | 50K chars per tool / 200K chars per message |
| Media per request | 100 items |
| Bytes per token estimate | 4 |

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| Tools we use have no feature gates | Read, Edit, Bash, Agent, Skill — always available |
| COORDINATOR_MODE needs `ant` build | Public build cannot use coordinator mode |
| GrowthBook changes behavior between sessions | A/B tests can alter behavior unpredictably |
| Tool result budget: 50K chars per tool | Affects how much context our tools return |
| Prompt cache optimization is pervasive | CC avoids cache-busting; our context should be stable too |
| `ant` build has extra capabilities | Nested subagents, staging OAuth, internal betas |

**Confidence:** Alta

---

## Finding F16: Bootstrap (Configuration Spine)

**Question:** What is bootstrap? Why 218 exports with 0 imports?

**Files:** `bootstrap/state.ts` (1758 lines, single file)

### Not Configuration — Global Mutable State Singleton

Bootstrap is CC's **global state singleton**: a private `State` object with ~90 fields, accessed via 210 exported getter/setter functions. The "0 imports" in our dependency graph is architecturally correct — it only imports types and leaf utilities, enforced by a custom ESLint rule (`bootstrap-isolation`).

### State Categories (~90 fields)

| Category | Examples |
|----------|---------|
| Session identity | sessionId, parentSessionId, cwd, projectRoot |
| Cost/usage | totalCostUSD, modelUsage, token counts, API durations |
| Telemetry | OTel meter, logger, tracer, 8 named counters |
| UI flags | isInteractive, clientType, plan/auto mode |
| Auth tokens | sessionIngressToken, oauthTokenFromFd |
| Feature latches | 5 sticky-on beta header latches for prompt cache |
| Ephemeral | cron tasks, created teams, invoked skills |

### Design Decisions

- **Hand-written** (not generated) — detailed comments like "THINK THRICE BEFORE MODIFYING"
- **DAG leaf enforced by ESLint** — circular deps would cascade if bootstrap imported app modules
- **Getter/setter encapsulation** — enables `resetStateForTests()`
- **Sticky-on latches** for beta headers — once activated, never deactivate (prevents prompt cache busting)

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| Every module reads/writes bootstrap | Understanding any CC module requires knowing bootstrap state |
| DAG leaf constraint is architectural invariant | If violated, circular deps cascade everywhere |
| "0 imports" is by design, not a bug | Our analyzer correctly shows the architectural boundary |
| Sticky-on latches prevent cache busting | Important pattern for any prompt caching strategy |

**Confidence:** Alta

---

## Cross-Cutting: Memory & Context Architecture

```
┌─────────────────────────────────────────────────┐
│                 System Prompt                     │
│  Static zone (cached): instructions, tools       │
│  Dynamic zone: env info, memory prompt, MCP      │
│  System context: git status (snapshot)            │
├─────────────────────────────────────────────────┤
│           User Context (first message)            │
│  CLAUDE.md files (6 tiers, lowest→highest)        │
│  Current date                                     │
├─────────────────────────────────────────────────┤
│              Conversation                         │
│  User messages + assistant responses              │
│  Tool results (50K/tool, 200K/message)            │
│  <system-reminder> injections                     │
├─────────────────────────────────────────────────┤
│              Auto-Compact Zone                    │
│  Triggers at ~90% of context window              │
│  5-layer compaction (snip→micro→collapse→auto→rx) │
└─────────────────────────────────────────────────┘
```

Memory lifecycle:
```
Session start → load MEMORY.md index (always)
Per query    → Sonnet side-query selects ≤5 topic files
Per turn     → Main agent may write memories (prompt-driven)
Post turn    → Background extraction agent reviews transcript
Session end  → Memories persist for next session
```

---

*Generated by 4 parallel research agents analyzing Claude Code source.*
*Method: ADR-016 Phase 2 — Targeted Deep Dives.*
