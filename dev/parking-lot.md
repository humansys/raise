# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## Urgent

- [x] ~~**E14: Rai Distribution**~~ **PROMOTED TO ACTIVE EPIC** (2026-02-05)
  - **Scope:** `dev/epic-e14-scope.md`
  - **Branch:** `epic/e14/rai-distribution`
  - **Research:** `work/research/rai-distribution/` (complete)
  - **ADR:** ADR-022 (distribution architecture)

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

### Discovery & Code Understanding

- [x] ~~**`/discover-describe` skill**~~ **PROMOTED TO ACTIVE STORY** (2026-02-07)
  - **Story:** `work/stories/discover-document/`
  - **Research:** `work/research/architecture-knowledge-layer/` (RES-ARCH-KNOWLEDGE-001)
  - **Design:** `work/stories/discover-document/design.md`
  - **Branch:** `story/discover-document`
- [ ] **Publishable docs via MkDocs Material** — (SES-087, 2026-02-07)
  - **Context:** Architecture docs in `governance/architecture/` use Markdown + YAML frontmatter — already compatible with MkDocs, Docusaurus, Starlight, GitBook
  - **What:** Add `mkdocs.yml`, publish `framework/` + `governance/` as doc site
  - **Sizing:** S-sized story (config + CI only, no code changes)
  - **Priority:** Post-F&F, pre-public launch (Feb 15)
  - **Related:** `raise discover describe` generates the content; MkDocs publishes it

### Framework Improvements

- [ ] **Remove "Unified" prefix from graph classes** — (SES-096, 2026-02-08)
  - **Problem:** `UnifiedGraph`, `UnifiedQueryEngine`, `UnifiedQuery`, etc. — 7 classes carry "Unified" prefix that distinguishes nothing. Vestige from when separate graphs existed.
  - **What:** Rename to `ContextGraph`, `QueryEngine`, `Query`, etc. Find-and-replace across `context/`, CLI, tests.
  - **Risk:** PAT-151 (renames have long tail) — do as dedicated story with proper verification
  - **Priority:** Post-F&F, low risk but real cognitive tax reduction

- [x] ~~**Foundational pattern surfacing in session-start**~~ **RESOLVED by S15.7** (2026-02-08)
  - 10 patterns tagged `foundational: true` in patterns.jsonl
  - Context bundle assembler surfaces them as behavioral primes
  - `raise session start --context` outputs primes automatically

- [ ] **Governance doc frontmatter standardization** — (SES-094, 2026-02-08, PAT-184)
  - **Problem:** 5 of 8 governance docs use fragile regex parsing (guardrails, constitution, PRD, vision, glossary). 3 modern docs (architecture, modules, ADRs) use YAML frontmatter with deterministic extraction.
  - **Evidence:** SES-094 audit — regex parsers lose metadata, truncate content at 500 chars, use approximate line numbers, have 3+ version patterns for glossary alone.
  - **What:** Migrate remaining 5 docs to YAML frontmatter. S15.3 does guardrails.md first; remaining 4 follow same pattern.
  - **Docs to migrate:** constitution.md, prd.md, vision.md, glossary.md, backlog.md
  - **Pattern:** Each doc gets frontmatter template + parser reads frontmatter + body parsed as before for backward compat
  - **Priority:** Post-F&F, high compound value (every future graph rebuild benefits)
  - **Related:** PAT-184, S15.3 (guardrails.md is the first)

- [ ] **Ontology-guided design step for design skills** — (SES-089, 2026-02-08, PAT-175)
  - **Problem:** Design skills read governance files directly. The graph already has extracted, structured, related this information.
  - **What:** Create reusable "load architectural context" skill step. Design skills query `raise memory query` for relevant modules, guardrails, principles, domain boundaries before designing.
  - **Value:** Progressive disclosure of high-density context. Ontology-guided design by default, not by discipline. Works on any RaiSE project.
  - **Priority:** Post-F&F, high impact
  - **Pattern:** PAT-175

- [ ] **Scope-refresh step after design deviations** — (SES-089, 2026-02-08, PAT-176)
  - **Problem:** Scope commits go stale when design deviates (discover-describe: scope said CLI+Jinja2, actual was skill-only)
  - **What:** Add scope-refresh to story-design skill. When design deviates, update scope.md automatically.
  - **Priority:** Post-F&F
  - **Pattern:** PAT-176

- [ ] **Move convention detection from onboarding to discovery** — (SES-089, 2026-02-08, domain model decision #4)
  - **Problem:** Convention detection is codebase analysis but lives in onboarding (Experience context). Domain model says it belongs in Discovery.
  - **What:** Move `detect_conventions()` to discovery module. Onboarding calls discovery for this.
  - **Priority:** Post-F&F refactoring

- [ ] **Stale terminology grep as rename gate** — (Ishikawa analysis, 2026-02-06)
  - S14.16 declared complete with 21 files still containing "feature" remnants (PAT-151)
  - Root cause: verification was behavioral (tests pass) not lexical (no stale terms)
  - **Countermeasure:** Add `grep -ri "<old_term>"` as mandatory final gate for rename stories
  - Consider: automated `raise lint terms` command that checks against glossary
  - Priority: Add to rename story template now; automated linter post-F&F

- [ ] **Add graph-rebuild to /story-close when Pydantic models change** — (S14.16 retro, 2026-02-06)
  - Schema Literal changes invalidate cached unified graph (PAT-152)
  - Stale `unified.json` breaks `raise memory query` with ValidationError
  - Consider: auto-detect model changes via git diff, or add optional flag to /story-close

- [x] ~~**Session-start continuity improvement**~~ **RESOLVED by S15.7** (2026-02-08)
  - Context bundle includes last session summary, current work, and pending next actions
  - `session-state.yaml` carries state between sessions (overwritten each close)
  - No dependency on CLAUDE.local.md for continuity

- [ ] **System Open Ends Audit** — (Post-E14, 2026-02-05)
  - **Trigger:** Found 22 stale branches because no cleanup in lifecycle skills
  - **Goal:** Systematic review to find similar "open ends" in RaiSE system
  - **Method:** Walk through each lifecycle skill, each process rule, each integration point
  - **Questions to ask:**
    - What accumulates without cleanup? (branches, files, cache, telemetry)
    - What can fail silently? (git -d vs -D, missing hooks)
    - What requires manual memory that Rai should enforce?
    - Where do skills assume state that may not exist?
  - **Output:** List of gaps → prioritize → fix or add to backlog
  - **Priority:** Post-E14, before V3 complexity increase
  - **Pattern:** PAT-096 — Periodic system hygiene audits catch drift before accumulation

- [ ] **CLI integration test isolation (`--test-dir`)** — (SES-098, 2026-02-08)
  - **Problem:** Manual integration tests (Task 8 in S15.7) write to real memory paths (patterns.jsonl, sessions/index.jsonl). Requires manual cleanup after testing.
  - **What:** Add `--test-dir` or `--dry-run` flag to session CLI commands for safe integration testing
  - **Priority:** Post-F&F, low — pytest tests already use tmp_path correctly
  - **Related:** S15.7 retrospective action item

- [ ] **Parallel task execution in /story-implement** — (F7.7 discussion, 2026-02-05)
  - When tasks have no dependencies, allow spawning subagents in parallel
  - Combined HITL checkpoint after parallel tasks complete
  - Pattern: identify independent tasks in plan → spawn parallel → converge → continue sequential

- [ ] **Separation of Builder and Verifier (Lean Quality)** — (F7.2 discussion, 2026-02-05)
  - **Problem:** Self-review checklists in skills (e.g., /story-design Step 8) have builder verifying own work = muda
  - **Lean principle:** TPS separates production from quality inspection. Jidoka catches defects, but verification is external.
  - **Possible approaches:**
    1. **Quality Gate Subagent** — Different Rai prompt focused on critical review, not building
    2. **Poka-yoke in skills** — Design process so defects can't happen (structured templates, required fields)
    3. **Human gate** — Explicit approval before phase transition (friction vs. quality tradeoff)
    4. **Automated checks** — Deterministic validation where possible (schema validation, coverage gates)
  - **Research needed:** How do lean masters handle creative/judgment work quality? Six Thinking Hats? Devil's Advocate pattern?
  - **Potential skill:** `/quality-review` — invoke reviewer-Rai before proceeding to next phase

- [ ] **Research output extraction** — Extract `work/research/*/` into unified graph (deferred from E12, complex format variance)
- [ ] **Component catalog extraction** — Extract `dev/components.md` into graph (deferred from E12, nice-to-have)
- [ ] **Session-aware context loading** — Skip redundant queries in same session (deferred from E12, optimization — re-querying is <1ms)
- [x] ~~**Epic-close skill** (`/epic-close`)~~ **DONE** — Implemented 2026-02-05, v1.0.0. Includes retrospective, metrics, branch cleanup.
- [ ] **Feature pre-verification in /story-start** - Check if feature already implemented before starting work. (F12.6 was already done, 2026-02-04)
- [ ] **Memory system improvements** (E12 retrospective, 2026-02-04):
  - Semantic search for queries (keyword brittleness — "testing" misses "type hints")
  - Better calibration query patterns or dedicated report command
  - Pattern deduplication (content similarity check before add)
  - Pattern pruning/archival when noise overwhelms signal
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
- [ ] **Add "test with real data" checkpoint to story-plan kata** - After design validation, verify patterns/rules against real project data (F2.2 retro)
- [ ] **Add "commit after task" to /story-implement skill** - Good discipline, enables recovery (F3.3 retro)
- [ ] **`/story-start` skill** - Lightweight skill to create story branch from epic branch with scope commit. Replaces ad-hoc branch creation. (E8 retro, E11 discussion 2026-02-03)
- [ ] **Branch verification in merge workflow** - Add checklist to /story-review: verify target branch per CLAUDE.md, check epic branch exists, enforce feature→epic→dev flow. Prevents merging to wrong branch. (E11 F11.3/F11.4 retro, 2026-02-03)
- [ ] **Epic implement skill (`/epic-implement`)** - Do we need one? Current thinking: probably not, epic implementation IS feature implementation. Alternatives: fold progress tracking into `/story-review`, add `raise epic status` CLI command, keep `/session-start` as "where am I?" mechanism. (E11 discussion, 2026-02-03)
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
- [ ] **Pre-design research phase in lifecycle** - Before `/epic-design`, sometimes need targeted research (e.g., reverse engineering prior art like Aider's repo map). Consider formalizing as optional phase in epic lifecycle. (E13 discussion, 2026-02-04)

- [x] ~~**CurrentWork model: allow empty state**~~ **FIXED** (SES-116) — Fields default to `""`, `None` coerced via `field_validator`

- [x] ~~**Skill stop hooks: missing `log-skill-complete.sh` in target projects**~~ **FIXED** (SES-116) — Scripts now scaffolded by `raise init`

- [x] ~~**Remove duplicate bash hook telemetry — use CLI telemetry only**~~ **DONE** (SES-117) — Story `hooks-cleanup`, merged to v2
  - **Problem:** Two parallel systems write to `signals.jsonl`: bash Stop hooks (`.raise/scripts/log-*.sh`) and CLI telemetry (`raise memory emit-work` / `telemetry/writer.py`). CLI version is strictly better (Pydantic schemas, file locking, proper error handling). Bash hooks are a vestige from E9 Phase 1.
  - **What:** Strip `hooks:` sections from all 21 distributable skills. Remove bash scripts from `rai_base/scripts/` and bootstrap. Keep CLI `emit-work` calls in skill steps (they already cover the same events).
  - **Files:** `src/raise_cli/skills_base/*/SKILL.md` (remove hooks), `src/raise_cli/rai_base/scripts/` (delete), `src/raise_cli/onboarding/bootstrap.py` (remove `_copy_scripts`)
  - **Size:** S — mechanical removal across skills + bootstrap cleanup
  - **Priority:** Medium — working but redundant, slight noise reduction

### E7 Onboarding — Deferred (Post-F&F)

> Items explicitly deferred from E7 scope (ADR-021).

- [ ] **Team memory** — V3 scope, see E10 Collective Intelligence
- [ ] **`raise doctor` command** — Cognitive architecture coherence audit. Detect: graph primes duplicated in CLAUDE.md, MEMORY.md grown beyond boot pointer, session state referencing nonexistent stories, identity node drift from canonical source, always_on patterns missing from bundle, orphaned sessions, stale parking lot items. Not just "are files right" but "is the whole system coherent." (SES-005, 2026-02-08)
- [ ] **Full ~/.rai/ expansion** — YAGNI for F&F, start with developer.yaml only
- [ ] **Multi-language convention detection** — Python first, TypeScript/JS later
- [ ] **Auto-progress Shu→Ha→Ri** — Experience level progression (manual for now)
- [ ] **Communication style preferences** — Full customization (minimal for F&F)

### E14 Rai Distribution — Deferred (V3/Future)

> Items explicitly deferred from E14 scope.

- [ ] **Team/org shared patterns** — Multi-tenant complexity, defer to E10 Collective Intelligence
- [ ] **Pattern marketplace** — Community feature, future consideration
- [ ] **Cross-project pattern sync** — Complex state management
- [ ] **AI-generated base pattern updates** — Keep human-curated for trust/quality
- [ ] **Progressive reveal intro** — Nice-to-have polish, post-F&F

### E13 Discovery — Deferred (Post-F&F)

> Items explicitly deferred from E13 MVP scope.

- [ ] **Function-level granularity** — Too noisy for MVP; component level sufficient for reuse discovery
- [ ] **Call graphs / data flow analysis** — Complex; not needed for component catalog
- [ ] **Git history integration** — Nice-to-have for evolution tracking
- [ ] **CI/CD drift blocking** — Start with warnings, add blocking after validation
- [ ] **PageRank ranking** — Simpler heuristics (public/exported) sufficient for MVP
- [ ] **Multi-language support** — Start with Python, expand based on need

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
- [ ] F9.11 Retro Integration — /story-review queries telemetry

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
*Last updated: 2026-02-04 (E7 design complete, deferred items added)*
