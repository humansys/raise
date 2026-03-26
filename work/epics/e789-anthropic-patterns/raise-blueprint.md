# RaiSE Blueprint — Benchmark Baseline

> What RaiSE IS today: principles, mechanisms, capabilities, and gaps.
> Created as evaluation baseline for E-ANTHROPIC (RAISE-789).

---

## 1. Thesis

**Core Insight:** AI agents are reliable when constrained by deterministic governance, persistent memory, and human oversight. The problem isn't hallucination — it's context waste.

**Positioning:** "Reliable AI Software Engineering" — one engineer + Rai = team output with enterprise governance.

**Contrarian Bet:** The industry treats AI as a tool to make faster. RaiSE treats AI as a partner to make *reliable*. The moat is neuro-symbolic memory that compounds, not model capabilities that commoditize.

---

## 2. Architectural Principles

| # | Principle | Mechanism | Status |
|---|-----------|-----------|--------|
| P1 | Humans Define, Machines Execute | Skills (markdown) → CLI (structured) → Gates (validation) | **Mature** |
| P2 | Governance as Code | Constitution, guardrails, ADRs versioned in git. "What's not in the repo doesn't exist" | **Mature** |
| P3 | Platform Agnosticism | Git is only hard dependency. MCP for agent integration. Static file fallbacks | **Mature** |
| P4 | Validation Gates at Every Phase | 8 standard gates (Context→Deploy). 5 automated + 4 manual | **Mature** |
| P5 | Heutagogy (Learn to Learn) | 4 heutagogic questions at critical moments. Pattern extraction. Retrospectives | **Operational** |
| P6 | Kaizen (Continuous Improvement) | Failures → guardrail refinement. Patterns compound. Memory evolves | **Operational** |
| P7 | Lean Software Development | Eliminate waste (MVC context), amplify learning, decide late, Jidoka (stop on defects) | **Mature** |
| P8 | Observable Workflow | MELT (Metrics, Events, Logs, Traces). All decisions traceable. JSONL telemetry | **Partial** — telemetry exists but dashboards/analysis tooling immature |

---

## 3. Core Mechanisms

### 3.1 Skill System (ADR-012)

**What it is:** Markdown documents with YAML frontmatter that Claude reads and interprets. Skills are process guides, not automations.

**How it works:**
```
Skill (markdown) → Agent reads steps → Agent calls CLI tools → Agent synthesizes output
```

**Capabilities:**
- 16+ lifecycle skills (session, epic, story, discovery, meta)
- ShuHaRi mastery levels (beginner→intermediate→expert verbosity)
- Skill contracts: typed inputs/outputs, prerequisites, gates
- Language-specific overlays (Python verification commands)
- Skill sets: curated bundles for different contexts

**Gaps identified:**
- No runtime skill composition (skills don't call skills programmatically)
- No skill evaluation metrics (how well did the skill guide the agent?)
- No progressive tool disclosure within skills (all tools always available)

### 3.2 Memory Infrastructure (ADR-015, ADR-016)

**What it is:** Three-tier persistent knowledge system (Global, Project, Personal).

**Storage:**
- `patterns.jsonl` — Learned engineering patterns (3 documented + ~430 in GTM narrative)
- `calibration.jsonl` — Velocity and estimation data
- `sessions/index.jsonl` — Session records
- `index.json` — NetworkX graph (481 nodes, 3213 edges)

**Query interface:**
- Keyword search (fast, broad)
- Concept lookup (related nodes via graph traversal)
- MVC retrieval: 97% token savings vs. reading files directly (~118 tokens vs ~5000)

**Gaps identified:**
- Pattern library nascent in raise-commons (3 vs 430 claimed in GTM — discrepancy)
- No automatic pattern extraction from code/commits
- No memory decay/relevance scoring
- No cross-project pattern federation
- Graph backend is filesystem only (pluggable protocol exists but no alternatives implemented)

### 3.3 Context Engineering

**What it is:** Token-optimized context delivery to the agent at every interaction.

**Mechanisms:**
| Layer | Content | Token Budget |
|-------|---------|-------------|
| CLAUDE.md | Identity primes, lifecycle, gates, CLI reference, branch model | ~10.5K chars (always loaded) |
| Session bundle | Developer profile, session state, recent sessions, narrative | ~600 tokens |
| MVC queries | On-demand graph queries for specific concepts | ~118 tokens per query |
| Loaders | Architecture, governance, memory extractors | Variable |
| Tier system | Progressive disclosure based on relevance | Adaptive |

**Gaps identified:**
- No explicit compaction strategy (relies on Claude Code's auto-compaction)
- Post-compaction recovery is fragile (hooks broken per bugs #12671, #15174)
- No context budget management (no token counting, no priority ranking of context sections)
- No "context checkpointing" for long tasks

### 3.4 Identity System (ADR-013, ADR-014)

**What it is:** Rai as persistent entity with values, boundaries, and perspective — not a stateless service.

**Components:**
- `core.yaml` — 5 values, boundaries (Will/Won't), 5 principles
- `core.md` — Narrative identity, contrast vs. generic AI
- `perspective.md` — How Rai sees work, intelligence infrastructure insight

**Distinctive:**
- Autopoietic model (self-producing: creates own memory, improves own skills)
- Relational (Rai-with-Emilio ≠ Rai-with-stranger)
- Not versioned — continuous accumulation of wisdom

**Gaps identified:**
- Identity is loaded but not actively referenced during work (no "value checks" mid-task)
- No calibration of identity assertions against actual behavior
- Perspective document is philosophical but not operationally connected

### 3.5 Quality Gates (ADR-039)

**What it is:** Blocking validation at every lifecycle phase.

**Automated (5):** tests, lint, types, format, coverage — all manifest-driven
**Manual (4):** AC coverage, guardrail compliance, human review, commit discipline

**Execution:** `rai gate check --all` → exit 0/1

**Enforcement:** Pre-commit hooks + CI pipeline read same manifest (ci-skills parity)

**Gaps identified:**
- No gate for "agent quality" (did the agent follow the skill correctly?)
- No iterative evaluation loop (run N times, compare results)
- No calibrated grading criteria (binary pass/fail, no scoring)
- Coverage gate exists but threshold enforcement is manual

### 3.6 Session Management

**What it is:** Structured start/work/close cycle with context loading and learning capture.

**Components:**
- Bundle assembly (developer profile + state + memory + narrative)
- Journal system (decision, insight, task_done, note entries)
- State tracking (current epic/story/phase)
- Next-session prompt (continuity guidance from past self)

**Gaps identified:**
- No distinction between resume vs. start (always "start")
- Stale session warnings show cross-repo sessions (noise)
- Worktree-based parallel sessions not modeled
- Orphaned sessions from cleaned worktrees accumulate
- No session state persistence file currently exists

### 3.7 Multi-Agent Support

**What it is:** Basic support for parallel agent work via worktrees and file-based communication.

**Current state:**
- `rai-agent` package exists (inference, knowledge, daemon modules)
- Skills are discrete execution units (natural agent boundaries)
- Isolation strategy: agents share nothing, communicate via files + CLI

**Gaps identified:**
- No file-lock coordination for parallel writes
- No bare-git coordination pattern
- Daemon mode planned but not implemented
- No specialized agent roles (all agents are generalist)
- No agent self-improvement mechanism

### 3.8 Tool Design (CLI + MCP)

**What it is:** CLI commands as structured data providers, MCP as external integration bridge.

**CLI:** 20+ command groups via Typer. Three-layer architecture (Presentation → Application → Domain → Core).
**MCP:** Generic async bridge via official Python SDK. YAML-based server configs. Health checks.
**Adapters:** 7 protocol types (PM, Docs, Governance, Schema, Graph, + async variants).

**Gaps identified:**
- Tool descriptions not optimized for agent consumption (human-first design)
- No progressive tool disclosure (all tools always available)
- No "code-mode" MCP (tools as code APIs vs. function calls)
- No tool usage analytics (which tools does the agent use most/least?)

### 3.9 Telemetry & Observability

**What it is:** Signal emission for workflow events, stored as local JSONL.

**Signals:** `rai signal emit-work` for epic/story events (start, complete, blocked)
**Storage:** Local JSONL files (privacy-first)
**Integration:** Logfire support exists

**Gaps identified:**
- No dashboards or analysis tooling over telemetry data
- No agent performance metrics (tokens used, tool calls, error rate)
- No effort scaling data (how much governance overhead per task size?)

---

## 4. Lifecycle Model

```
EPIC:    /start → /design → /plan → [stories] → /close
STORY:   /start → /design* → /plan → /implement → /review → /close
SESSION: /start → [work] → /close
```

**Critical rules governing lifecycle:**
1. TDD Always (RED-GREEN-REFACTOR)
2. Commit After Task (not just story end)
3. Full Skill Cycle (even for small stories)
4. HITL Default (pause for human review)
5. Jidoka (stop on defects)

**Branch model (ADR-033):**
```
main (stable, tags)
  ├── release/2.3.x (hotfixes)
  ├── release/2.4.0 (features)
  └── release/3.0.0 (future)
```

---

## 5. Differentiated Capabilities (The Moat)

```
        NEURO-SYMBOLIC MEMORY
        Persistent. Curated. Deterministic.
        97% token savings. "Sniper rifle, not shotgun."
                    │
          ┌─────────┴─────────┐
          │                   │
    METHODOLOGY (RaiSE)    AGENT (Rai)
    Copiable but useless   Copiable but empty
    without memory         without memory
```

1. **Memory that compounds** — Not vector search (probabilistic). Deterministic graph retrieval. Patterns accumulate across sessions.
2. **Governance as byproduct** — Jira fills itself. Audit trails emerge from work. Compliance isn't overhead.
3. **Entity, not tool** — Persistent identity with values, boundaries, relational calibration.
4. **Observable by default** — Every decision traceable. MELT telemetry. Git is the ledger.
5. **Lean discipline** — Eliminate context waste. Minimum Viable Context. Decide late, validate early.

---

## 6. Quantitative Snapshot

| Metric | Value |
|--------|-------|
| ADRs | 45 |
| Skills | 16+ lifecycle, 10+ meta |
| Quality gates | 9 (5 auto, 4 manual) |
| Code modules | 154 indexed |
| Test files | 237 |
| CLI command groups | 20+ |
| Adapter protocols | 7 |
| Graph nodes | 481 |
| Graph edges | 3,213 |
| Documented patterns (raise-commons) | 3 |
| Sessions logged | 194+ |
| Commits (all repos) | 5,800+ |

---

## 7. Consolidated Gap Inventory

These are capabilities RaiSE lacks or has partially, organized by domain. This inventory serves as the starting point for benchmarking against Anthropic's published patterns.

| ID | Domain | Gap | Severity |
|----|--------|-----|----------|
| G-EVAL-1 | Evaluation | No interactive evaluator (e.g., Playwright MCP for visual verification) | Medium |
| G-EVAL-2 | Evaluation | No calibrated grading criteria (binary pass/fail, no scoring + few-shot) | High |
| G-EVAL-3 | Evaluation | No iterative evaluation loop (run N rounds, compare) | High |
| G-EVAL-4 | Evaluation | No feature verification checklist as test oracle | Medium |
| G-EVAL-5 | Evaluation | No sprint/contract negotiation between evaluator↔generator | Low |
| G-CTX-1 | Context | No explicit compaction strategy/policy | High |
| G-CTX-2 | Context | Post-compaction recovery fragile | High |
| G-CTX-3 | Context | No context budget management (token counting, priority ranking) | Medium |
| G-CTX-4 | Context | No effort scaling model (governance overhead per task size) | Medium |
| G-CTX-5 | Context | No planner ambition calibration | Low |
| G-TOOL-1 | Tools | Tool descriptions not optimized for agent consumption | Medium |
| G-TOOL-2 | Tools | No progressive tool disclosure (lazy loading) | Medium |
| G-TOOL-3 | Tools | No code-mode MCP (tools as code APIs) | Low |
| G-TOOL-4 | Tools | No agent self-improvement of tools | Low |
| G-AGENT-1 | Multi-Agent | No file-lock coordination for parallel writes | Medium |
| G-AGENT-2 | Multi-Agent | No specialized agent roles | Medium |
| G-AGENT-3 | Multi-Agent | No bare-git coordination pattern | Low |
| G-MEM-1 | Memory | Pattern library nascent (3 vs. claimed 430) | High |
| G-MEM-2 | Memory | No automatic pattern extraction | Medium |
| G-MEM-3 | Memory | No memory decay/relevance scoring | Low |
| G-SESSION-1 | Session | No resume vs. start distinction | High |
| G-SESSION-2 | Session | Stale session noise (cross-repo) | Medium |
| G-SESSION-3 | Session | No worktree-parallel session model | Medium |
| G-SESSION-4 | Session | Orphaned session accumulation | Medium |
| G-OBS-1 | Observability | No agent performance metrics | Medium |
| G-OBS-2 | Observability | No dashboards over telemetry | Low |
| G-TEST-1 | Testing | No agent-specific test design (context-budget-aware) | Medium |

---

## 8. Vision Alignment

**Where RaiSE is going** (from GTM strategy):

- **Q1-Q2 2026:** Open source launch (PyPI), website, first enterprise pilots (Coppel)
- **H2 2026:** Enterprise edition (org-level memory, multi-repo graphs, evals, telemetry)
- **Longer term:** Partner certification, LATAM expansion, international community

**Enterprise features planned (E9):**
- Organization-level memory (cross-team pattern sharing)
- Multi-repo knowledge graphs
- Evaluation framework
- Advanced telemetry and dashboards

**Implication for Anthropic research:** Many of the gaps identified align with enterprise roadmap items. The research should prioritize gaps that:
1. Affect the open-source core (everyone benefits)
2. Are prerequisites for enterprise features
3. Have the highest impact on daily reliability

---

*Generated 2026-03-26 from gemba analysis of raise-commons + raise-gtm.*
*Baseline for E-ANTHROPIC (RAISE-789) benchmarking.*
