# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## Urgent

- [x] **F&F Readiness (Feb 9)** — See `governance/projects/raise-cli/backlog.md` §4
  - [x] README update (v2 structure) — Done 2026-02-02
  - [x] Installation guide — In README
  - [x] Getting started guide — In README
  - **Validation method:** Dogfooding invertido — simulate F&F user on fresh clone
- [ ] **Marketing strategy** - ASAP, identify dependencies before Feb 15 launch
- [x] ~~**Rovo AI integration research**~~ **RESOLVED** — See `work/research/rovo-atlassian-integration/` (RES-ROVO-001)
  - Integration strategy draft created
  - MCP is primary integration mechanism
  - E8 design informed by Teamwork Graph compatibility
- [ ] **Rovo AI integration implementation** - Required for Mar 14 webinar (V3 scope)
- [ ] **V3: Rai as Commercial Offering** - Hosted Rai before Mar 14 webinar:
  - Rai = trained RaiSE agent (not generic Claude)
  - Value: accumulated judgment, calibration, collaborative intelligence
  - Integration: Jira, Confluence, Rovo Dev (Atlassian ecosystem)
  - Architecture: V2 decisions should enable V3 (session graph, memory persistence)
  - See: `.claude/rai/identity.md` for vision
  - **From OpenClaw research (RES-OPENCLAW-001):**
    - [x] ~~Pre-compaction memory flush~~ **→ E3** (F3.5 /session-close flush)
    - [ ] Gateway abstraction — single control plane for multi-interface (Jira, Rovo, CLI, MCP)
    - [ ] Typed kata execution — Lobster-inspired pipelines with approval gates + resume tokens
    - [ ] Token monitoring — track session context usage, trigger flush at soft threshold
    - [ ] Hybrid skills — markdown process + JSON schema + validation code

---

## Ideas

### Framework Improvements

- [ ] **Research output extraction** — Extract `work/research/*/` into unified graph (deferred from E12, complex format variance)
- [ ] **Component catalog extraction** — Extract `dev/components.md` into graph (deferred from E12, nice-to-have)
- [ ] **Session-aware context loading** — Skip redundant queries in same session (deferred from E12, optimization — re-querying is <1ms)
- [ ] **Post-Session Alignment Skill** (`/align-docs`) - After strategic sessions, auto-update docs:
  - Generate ADRs from decisions made
  - Update vision/architecture docs
  - Sync CLAUDE.md with new patterns
  - Could be triggered by `/session-close` for ideation/research sessions
  - Note: Doing manually now (2026-02-01) for quality; automate later
- [x] ~~**Identity Core Implementation**~~ **→ PROMOTED to E3** - See `dev/epic-e3-scope.md`
  - `.rai/` with identity/, memory/, relationships/, growth/
  - JSONL + Graph for memory (MVC pattern from E2)
  - ADR-013, ADR-014, ADR-015 define architecture
- [x] ~~**Session Graph Enabler Epic**~~ **→ ADDRESSED by E3** - Memory Graph (F3.3)
  - Same pattern: extract→graph→query for memory
  - JSONL storage + concept graph + BFS traversal
  - Reuses E2 infrastructure
- [ ] Translate all katas to English (currently some in Spanish)
- [ ] Apply Lean Spec Principles to katas (after research)
- [ ] Session management for Claude Code (`raise session start/wrap`) - standardize human-AI collaboration patterns
- [x] ~~**Session Start Skill** (`/session-start`)~~ **RESOLVED** — Already exists at `.claude/skills/session-start/`
  - Loads memory, analyzes progress, proposes session goal
  - Used at start of this session
- [ ] **Add "test with real data" checkpoint to feature-plan kata** - After design validation, verify patterns/rules against real project data (F2.2 retro)
- [ ] **Add "commit after task" to /feature-implement skill** - Good discipline, enables recovery (F3.3 retro)
- [ ] **`/feature-start` skill** - Lightweight skill to create feature branch from epic branch with scope commit. Replaces ad-hoc branch creation. (E8 retro, E11 discussion 2026-02-03)
- [ ] **Branch verification in merge workflow** - Add checklist to /feature-review: verify target branch per CLAUDE.md, check epic branch exists, enforce feature→epic→dev flow. Prevents merging to wrong branch. (E11 F11.3/F11.4 retro, 2026-02-03)
- [ ] **Epic implement skill (`/epic-implement`)** - Do we need one? Current thinking: probably not, epic implementation IS feature implementation. Alternatives: fold progress tracking into `/feature-review`, add `raise epic status` CLI command, keep `/session-start` as "where am I?" mechanism. (E11 discussion, 2026-02-03)
- [ ] **Design revision process** - What happens when a design needs to be updated after initial creation? Should we emit `design revision` signals? How does this affect downstream phases? (F11.1 discussion, 2026-02-03)
- [ ] **HITL approval before completion signals** - Telemetry "complete" events should only emit AFTER user approval, not when Rai finishes drafting. Update skills to require explicit sign-off before completion telemetry. (F11.1 discussion, 2026-02-03)
- [ ] **Fix test path convention in plan template** - Plan says `tests/cli/test_*.py` but actual is `tests/cli/commands/test_*.py` (F3.3 retro)
- [ ] **Document Pyright + Pydantic exception in guardrails.md** - `Field(default_factory=list)` false positives acceptable when Ruff passes (F2.2 retro)
- [ ] **Create ADR template for inference rule decisions** - When to be conservative vs aggressive in pattern matching (F2.2 retro)
- [ ] **Add kata-optimized estimation multiplier to planning guidance** - Apply 0.5x to estimates when using full kata cycle (F2.3 retro: 3 features at 2-3x velocity)
- [ ] **Add Python naming best practices to guardrails** - "Prefer clear names over acronyms unless universally understood" (F2.3 retro: MVCQuery→ContextQuery)
- [ ] **Document "compose, don't duplicate" architecture pattern** - Create ADR or concept doc with F2.2→F2.3 BFS reuse example (F2.3 retro)
- [ ] **Add "Simple First" concrete examples to constitution** - Keyword matching (no NLP), token heuristics; elevate from value to principle (F2.3 retro)
- [ ] **Document test fixture YAML frontmatter pattern** - Use `dedent("""\---` not `dedent("""\n---` to avoid leading newline breaking `^---` regex (F11.2 retro)
- [ ] **Add `get_all_*` aliases to UnifiedGraph** - `iter_concepts()` is efficient but `get_all_concepts()` is more discoverable for CLI integration (F11.2 retro, low priority)

### Research Needed

- [ ] What are the Lean Spec Principles? How do they apply to governance artifacts? **← In progress (subagent researching for /epic-design skill)**
- [x] ~~Are agent personas really needed for katas?~~ **RESOLVED** — No. See `work/research/agent-personas/` (RES-PERSONA-001)
- [x] ~~OpenClaw/Moltbot architecture patterns for V3~~ **RESOLVED** — See `work/research/openclaw-architecture/` (RES-OPENCLAW-001)
- [x] ~~Rovo AI / Atlassian Teamwork Graph research~~ **RESOLVED** — See `work/research/rovo-atlassian-integration/` (RES-ROVO-001)

### Governance Content Improvements (E2)

- [ ] **Refine relationship inference rules** - Based on real governance patterns discovered in F2.2 (F2.2 retro)
- [ ] **Add §N references to requirements in PRD** - Enable `governed_by` edges in concept graph (F2.2 retro)
- [ ] **Add explicit outcome keywords to requirements** - Enable `implements` edges in concept graph (F2.2 retro)
- [ ] **Consider "mentions" relationship type** - Lower confidence than `related_to` for broader semantic links (F2.2 retro)

### E9 Telemetry — Deferred (Post-F&F)

> Phase 2 and 3 deferred to post-F&F. Phase 1 is F&F scope.

**Phase 2 (Local Insights):**
- [ ] F9.6 Signal Analyzer — Analyze signals.jsonl for patterns
- [ ] F9.7 Insight Generator — Epistemologically-grounded insights
- [ ] F9.8 Session Start Integration — Surface insights in /session-start
- [ ] F9.9 Calibration Updater — Auto-update calibration from actuals

**Phase 3 (Telemetry CLI):**
- [ ] F9.10 Telemetry Commands — `raise telemetry velocity`, `drift`, `insights`
- [ ] F9.11 Retro Integration — /feature-review queries telemetry

**Also deferred:**
- [ ] Signal rotation/archival — Handle unbounded growth
- [ ] OTLP export — Enterprise observability integration
- [ ] Dashboard visualization — Beyond CLI

### E3 Identity Core — Deferred (YAGNI)

> Lean MVP decision (2026-02-02): Start with 7 files, grow when needed.

**Identity layer (deferred splits):**
- [ ] `identity/voice.md` — Extract from core.md when communication patterns grow
- [ ] `identity/boundaries.md` — Extract from core.md when limits need detail

**Memory layer (deferred files):**
- [ ] `memory/insights.jsonl` — Add when patterns.jsonl isn't sufficient
- [ ] `memory/decisions.jsonl` — Add when we need queryable decision history
- [x] ~~`memory/graph.json`~~ **RESOLVED** — Implemented in F3.3 Memory Graph

**Growth layer (deferred entirely):**
- [ ] `growth/evolution.md` — Track how Rai evolves over time
- [ ] `growth/questions.md` — Open questions Rai is exploring

**Rationale:** These add value but aren't needed for MVP session continuity and calibrated collaboration. Add when we hit limits.

### Future Scope (Deferred)

- [ ] MCP server for raise-cli (v2.x consideration)
- [ ] Skill audit feature for ecosystem governance (v3.0 consideration)

---

*Created: 2026-01-31*
*Last reviewed: 2026-02-02*
*Last updated: 2026-02-02 (RES-ROVO-001 complete, E8 design informed)*
