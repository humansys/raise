# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## Pre-Release (before first PyPI publish)

- [ ] **S-RENAME: Command entry point `rai` → `rai`, package `rai-cli` → `rai-cli`**
  - **Why now:** Zero installed users. After publish, this becomes a breaking change.
  - **Blast radius:** ~430 references across skills (123 in skills_base, 148 in .claude/skills), Python source (119), tests (42), README, CLAUDE.md, governance docs
  - **Nature:** Mechanical find-replace. No logic changes. Test suite catches breakage.
  - **Changes:** pyproject.toml (name + entry point), all `rai discover` → `rai discover`, `rai memory` → `rai memory`, `rai session` → `rai session`, `rai init` → `rai init`, etc.
  - **Rationale:** `rai` = the partner's name, 3 chars vs 5, no Python keyword collision, "I asked Rai to scan" is natural speech
  - **Size:** S (mechanical, ~30 min)
  - **Blocks:** PyPI publish

- [ ] **S-NAMESPACE: Skill namespace prefix `rai.` for all distributed skills**
  - **Why:** Without namespace, RaiSE skills mix with user-created skills in `.claude/skills/`
  - **Research needed:** Claude Code skill naming best practices, whether native namespacing is coming, dot vs dash separator, impact on `/skill-name` invocation
  - **Changes:** 17 skill directories renamed (both skills_base/ and .claude/skills/), DISTRIBUTABLE_SKILLS list, all cross-references between skills, methodology.yaml
  - **DX trade-off:** `/story-implement` → `/rai.story-implement` (longer to type)
  - **Alternative:** Wait for Claude Code to add native namespacing
  - **Size:** M (research + mechanical rename)
  - **Blocks:** PyPI publish (or not — could be done post-publish as non-breaking since skills are project-local)

---

## Urgent

- [x] **WorkLifecycle phase mismatch: CLI accepts phases the Pydantic model rejects** — (SES-131, SES-136) ✓ Fixed SES-136 — added `init` + `close` to Pydantic Literal
  - **Root cause:** Two validation layers disagree. CLI `valid_phases` list (memory.py:1396) includes `'init'` but `WorkLifecycle.phase` Pydantic Literal (schemas.py:267) only allows `['design', 'plan', 'implement', 'review']`. CLI pre-validation passes, Pydantic construction crashes.
  - **Missing phases:** `init` (needed by `/epic-start`, `/story-start`), `close` (needed by `/story-close`, `/epic-close`)
  - **Locations:**
    - Schema: `src/rai_cli/telemetry/schemas.py:267` — `phase: Literal["design", "plan", "implement", "review"]`
    - CLI validator: `src/rai_cli/cli/commands/memory.py:1396` — `valid_phases` list
  - **Fix:** Add `'init'` and `'close'` to the Pydantic Literal in `WorkLifecycle.phase`, and ensure CLI `valid_phases` matches exactly. Single source of truth: the Pydantic model should define valid phases, CLI should read from it.
  - **Workaround:** Use `--phase design` for init events, `--phase review` for close events
  - **Frequency:** Hits on every `/epic-start`, `/story-start`, `/story-close`, `/epic-close` — 4x per story cycle
  - **Priority:** Urgent — XS fix, high frequency

- [ ] **Domain stance layer — behavioral priming per project type** — (SES-134, 2026-02-10)
  - **Insight:** Identity (CLAUDE.md) shapes behavior deeply. Governance docs inform but don't prime as strongly. There's a missing middle layer: domain-specific thinking patterns that make Rai fluent, not just informed.
  - **Mechanism:** `domain-stance.md` loaded in system prompt (CLAUDE.md or CLAUDE.local.md). Same identity, different domain lens.
  - **Examples:** Lean Software Development stance (raise-commons), Lean Marketing stance (raise-gtm), Research stance
  - **Not:** A different Rai, a new feature, or the governance docs. It's the domain vocabulary and quality intuitions between identity (universal) and governance (project-specific).
  - **Next:** Prototype in raise-gtm CLAUDE.local.md, validate if alignment improves, then formalize pattern
  - **Priority:** Urgent — affects GTM work starting now, and Jumpstart client onboarding

- [ ] **Marketing strategy** - ASAP, identify dependencies before Feb 15 launch
- [ ] **Rovo AI integration implementation** - Required for Mar 14 webinar (V3 scope)
- [ ] **V3: Rai as Commercial Offering** - Hosted Rai before Mar 14 webinar:
  - Rai = trained RaiSE agent (not generic Claude)
  - Value: accumulated judgment, calibration, collaborative intelligence
  - Integration: Jira, Confluence, Rovo Dev (Atlassian ecosystem)
  - Architecture: V2 decisions should enable V3 (session graph, memory persistence)
  - See: `.claude/rai/identity.md` for vision
  - **From OpenClaw research (RES-OPENCLAW-001):**
    - [ ] Gateway abstraction — single control plane for multi-interface (Jira, Rovo, CLI, MCP)
    - [ ] Typed kata execution — Lobster-inspired pipelines with approval gates + resume tokens
    - [ ] Token monitoring + self-managed context lifecycle — Rai detects context pressure (80% threshold), proactively runs /session-close to capture state, instructs user to open fresh conversation with /session-start. Infrastructure already exists (session-start/close, session-state.yaml). Missing piece: visibility into context usage (Claude Code feature request or heuristic). Makes context breaks a managed transition, not a loss. (SES-119, 2026-02-09)
    - [ ] Hybrid skills — markdown process + JSON schema + validation code

---

## Ideas

### Systemic Poka-Yoke — Design Principle (2026-02-10, PAT-242)

- [ ] **"As above, so below" — poka-yoke at every producer-consumer boundary** — (SES-134, BF-2)
  - **Insight:** BF-2 exposed the same failure shape at 5 layers (template, parser, graph, skill, process). Each layer silently trusted the previous. We add poka-yokes reactively after bugs, not systematically at design time.
  - **Action:** Audit existing boundaries for missing poka-yokes. Candidates:
    - Parser: log warning when `_parse_architecture_doc` returns None for a `.md` file
    - Scaffold: validate frontmatter exists after writing template
    - Graph build: completeness check (done in BF-2, but could be stronger)
    - Skill consumption: lint skills for factual claims about code behavior
    - Template distribution: contract test for all templates (done in BF-2)
  - **Principle candidate:** "Every boundary between producer and consumer must validate. Consumers check what they receive. Producers check what they emit." Consider adding to constitution or guardrails.
  - **Priority:** High strategic value — prevents a class of bugs, not just one instance
  - **Related:** PAT-242, Jidoka (constitution), BF-2 retrospective

### Discovery & Code Understanding

- [ ] **Publishable docs via MkDocs Material** — (SES-087, 2026-02-07)
  - **Context:** Architecture docs in `governance/architecture/` use Markdown + YAML frontmatter — already compatible with MkDocs, Docusaurus, Starlight, GitBook
  - **What:** Add `mkdocs.yml`, publish `framework/` + `governance/` as doc site
  - **Sizing:** S-sized story (config + CI only, no code changes)
  - **Priority:** Post-F&F, pre-public launch (Feb 15)
  - **Related:** `rai discover describe` generates the content; MkDocs publishes it

- [ ] **Formalize branchless epic pattern in branch model docs** — (SES-128, 2026-02-09)
  - **Context:** BF-1 validated that bugfix stories can branch directly off v2 without an epic branch. Epic serves as tracking label only.
  - **What:** Update branch model docs to distinguish feature epics (need branch isolation) from maintenance epics (tracking label, stories branch off v2 for fast propagation).
  - **Priority:** Low — pattern works, docs catch up later

### Framework Improvements

- [ ] **Drift detector calibration — reduce false positives** — (SES-118, 2026-02-08)
  - **Problem:** `rai discover drift` produces 383 warnings on raise-commons, nearly all false positives. Location drift flags correctly-placed files (`cli/commands/`, root-level `__main__.py`, `exceptions.py`). Naming drift suggests `emit_` prefix for standard functions (`main`, `start`, `close`).
  - **Evidence:** 367 warnings, 16 info — near-zero actionable. Signal-to-noise ratio makes the tool unusable for real drift detection.
  - **What:** Calibrate directory expectations to include standard Python patterns (root files, `cli/commands/`). Add allowlists or severity filtering. Consider making baseline patterns richer during `discover-validate`.
  - **Priority:** Post-F&F, medium — the concept is sound but needs tuning to be useful
  - **Related:** `rai doctor` (coherence audit), PAT-196 (architecture docs as map)

- [ ] **Remove "Unified" prefix from graph classes** — (SES-096, 2026-02-08)
  - **Problem:** `UnifiedGraph`, `UnifiedQueryEngine`, `UnifiedQuery`, etc. — 7 classes carry "Unified" prefix that distinguishes nothing. Vestige from when separate graphs existed.
  - **What:** Rename to `ContextGraph`, `QueryEngine`, `Query`, etc. Find-and-replace across `context/`, CLI, tests.
  - **Risk:** PAT-151 (renames have long tail) — do as dedicated story with proper verification
  - **Priority:** Post-F&F, low risk but real cognitive tax reduction

- [ ] **Governance doc frontmatter standardization** — (SES-094, 2026-02-08, PAT-184)
  - **Problem:** 5 of 8 governance docs use fragile regex parsing (guardrails, constitution, PRD, vision, glossary). 3 modern docs (architecture, modules, ADRs) use YAML frontmatter with deterministic extraction.
  - **What:** Migrate remaining 5 docs to YAML frontmatter.
  - **Docs to migrate:** constitution.md, prd.md, vision.md, glossary.md, backlog.md
  - **Priority:** Post-F&F, high compound value (every future graph rebuild benefits)
  - **Related:** PAT-184

- [ ] **Scope-refresh step after design deviations** — (SES-089, 2026-02-08, PAT-176)
  - **Problem:** Scope commits go stale when design deviates
  - **What:** Add scope-refresh to story-design skill. When design deviates, update scope.md automatically.
  - **Priority:** Post-F&F
  - **Pattern:** PAT-176

- [ ] **Move convention detection from onboarding to discovery** — (SES-089, 2026-02-08)
  - **What:** Move `detect_conventions()` to discovery module. Onboarding calls discovery for this.
  - **Priority:** Post-F&F refactoring

- [ ] **Stale terminology grep as rename gate** — (Ishikawa analysis, 2026-02-06)
  - S14.16 declared complete with 21 files still containing "feature" remnants (PAT-151)
  - **Countermeasure:** Add `grep -ri "<old_term>"` as mandatory final gate for rename stories
  - Consider: automated `rai lint terms` command that checks against glossary

- [ ] **Add graph-rebuild to /story-close when Pydantic models change** — (S14.16 retro, 2026-02-06)
  - Schema Literal changes invalidate cached unified graph (PAT-152)
  - **Note:** Partially addressed — story-close Step 1.75 runs `/docs-update` which rebuilds graph. But only triggers on source code changes, not model schema changes specifically.

- [ ] **System Open Ends Audit** — (Post-E14, 2026-02-05)
  - **Goal:** Systematic review to find "open ends" — things that accumulate without cleanup, fail silently, or assume state that may not exist.
  - **Priority:** Before V3 complexity increase

- [ ] **CLI integration test isolation (`--test-dir`)** — (SES-098, 2026-02-08)
  - **What:** Add `--test-dir` or `--dry-run` flag to session CLI commands for safe integration testing
  - **Priority:** Post-F&F, low — pytest tests already use tmp_path correctly

- [ ] **Parallel task execution in /story-implement** — (F7.7 discussion, 2026-02-05)
  - When tasks have no dependencies, allow spawning subagents in parallel
  - Combined HITL checkpoint after parallel tasks complete

- [ ] **Separation of Builder and Verifier (Lean Quality)** — (F7.2 discussion, 2026-02-05)
  - **Problem:** Self-review checklists in skills have builder verifying own work = muda
  - **Possible approaches:** Quality gate subagent, poka-yoke in skills, human gates, automated checks
  - **Potential skill:** `/quality-review`

- [ ] **Research output extraction** — Extract `work/research/*/` into unified graph (deferred from E12, complex format variance)
- [ ] **Component catalog extraction** — Extract `dev/components.md` into graph (deferred from E12, nice-to-have)
- [ ] **Feature pre-verification in /story-start** - Check if feature already implemented before starting work
- [ ] **Memory system improvements** (E12 retrospective, 2026-02-04):
  - Semantic search for queries (keyword brittleness)
  - Pattern deduplication (content similarity check before add)
  - Pattern pruning/archival when noise overwhelms signal
- [ ] **HITL approval before completion signals** - Telemetry "complete" events should only emit AFTER user approval
- [ ] **Pre-design research phase in lifecycle** - Formalize optional research phase before `/epic-design`

- [ ] **Documentation debt from early retros** — Minor additions deferred since early February:
  - Document Pyright + Pydantic `Field(default_factory=list)` exception in guardrails
  - Add Python naming best practices to guardrails ("clear names over acronyms")
  - Create ADR template for inference rule decisions
  - Document "compose, don't duplicate" architecture pattern
  - Add "Simple First" concrete examples to constitution
  - Document test fixture YAML frontmatter pattern (`dedent` gotcha)

### E7 Onboarding — Deferred (Post-F&F)

> Items explicitly deferred from E7 scope (ADR-021).

- [ ] **Team memory** — V3 scope, see E10 Collective Intelligence
- [ ] **`rai doctor` command** — Cognitive architecture coherence audit
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
- [x] **Multi-language support** — ~~Start with Python, expand based on need~~ → E17 Multi-Language Discovery

### E17 Multi-Language Discovery — Deferred (2026-02-09)

- [ ] **Blade template extraction** (`.blade.php`) — Template markup, not structured code. Revisit if customers need template-level discovery.
- [ ] **Vue SFC support** — No current customer need. Add when a Vue project needs discovery.
- [ ] **Cross-language dependency analysis** — Import/require tracking across languages. Future scope.
- [ ] **Svelte template/markup extraction** — Currently only script block symbols. Template bindings could be useful for component relationship mapping.

### Graph Health & Context Caring — Parking Lot (2026-02-10)

- [ ] **Lifecycle-aware graph health contract** — (SES-134, 2026-02-10)
  - **Context:** BF-2 exposed that graph completeness is invisible. `rai memory validate` checks structural integrity but not semantic completeness. Neither user nor Rai can detect absent node types.
  - **Vision:** Declarative invariants per lifecycle phase (post-init, post-onboard, post-discovery). Dedicated `rai memory health` command. Session-start integration so Rai sees gaps.
  - **Scope:** Full lifecycle-phase schema, not just the minimal check in BF-2's F5
  - **Related:** BF-2 (F5 is the seed), `rai doctor` (E7 deferred)

- [ ] **Tools for human to understand and care for Rai's memory state** — (SES-134, 2026-02-10)
  - **Context:** Emilio's insight — the graph is invisible to both Rai and the user. The user needs tools to understand what Rai knows and doesn't know, and to be more intentional about maintaining context quality.
  - **Questions:** What would a "memory dashboard" look like? Is it CLI? Is it a doc? Is it part of session-start? What metrics matter?
  - **Priority:** Post-BF-2, high value for Jumpstart client experience

### E17 / SES-135 — Parking Lot (2026-02-10)

- [ ] **`rai story` CLI subcommands** — Reduce inference overhead by tooling ceremony: `rai story context`, `rai story transition`, `rai story scaffold`, `rai story close --actual`, `rai gate check`. Estimated 30-40% token savings per story cycle. (Rai proposal, SES-135)
- [ ] **Skill compression for Ri level** — Current skills are Shu-verbose even at Ri. Ri-mode skills should be 20-30 lines of "what to decide" + CLI commands, not 200 lines of step-by-step. (SES-135)
- [ ] **Rename `discover-describe` to `discover-document`** — Better reflects output (documents, not descriptions). Avoids confusion with `docs-update`. (SES-135)
- [ ] **Scanner `--exclude` flag** — PAT-247: vendor/node_modules exclusion for PHP/JS projects. Full-repo scans hit noise and duplicate IDs.

### E16 Incremental Coherence — Parking Lot (2026-02-09)

- [x] **Multi-platform code analyzers** — ✅ E17 delivered TS/TSX, PHP, Svelte extractors (2026-02-10)
- [ ] **Add dataset enumeration step to /story-design for ID format changes** — (PAT-220)
- [ ] **Rename "discovery" namespace to "discover"** — Harmonize verb form across skills. Cosmetic.
- [ ] **Absorb `/discover-complete` into `/discover-validate`** — Export is a mechanical final step, not a separate concern.

### Research Needed

- [ ] **Graph memory effectiveness in design sessions** — (SES-131, 2026-02-09)
  - **Observation:** E17 epic-design loaded 3 graph queries (memory query, module context). None materially influenced design decisions. Design was driven by reading actual code (gemba).
  - **Questions:** Is this a query relevance problem? A graph content depth problem? Or expected for new-territory work? Need data across multiple design sessions before deciding what to measure.
  - **Possible outcomes:** Better query strategies in skills, graph content enrichment, effectiveness telemetry signal, or "working as intended for novel domains."
  - **Priority:** Medium — significant infrastructure investment deserves ROI analysis

- [ ] **Lean Spec Principles** — How do they apply to governance artifacts? (Previous research attempt stale — needs fresh start if still wanted)

### Governance Content Improvements (E2)

- [ ] **Refine relationship inference rules** - Based on real governance patterns discovered in F2.2
- [ ] **Add §N references to requirements in PRD** - Enable `governed_by` edges in concept graph
- [ ] **Add explicit outcome keywords to requirements** - Enable `implements` edges in concept graph
- [ ] **Consider "mentions" relationship type** - Lower confidence than `related_to` for broader semantic links

### E9 Telemetry — Deferred (Post-F&F)

> Phase 2 and 3 deferred to post-F&F. Phase 1 is F&F scope.

**Phase 2 (Local Insights):**
- [ ] F9.6 Signal Analyzer — Analyze signals.jsonl for patterns
- [ ] F9.7 Insight Generator — Epistemologically-grounded insights
- [ ] F9.8 Session Start Integration — Surface insights in /session-start
- [ ] F9.9 Calibration Updater — Auto-update calibration from actuals

**Phase 3 (Telemetry CLI):**
- [ ] F9.10 Telemetry Commands — `rai telemetry velocity`, `drift`, `insights`
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

**Growth layer (deferred entirely):**
- [ ] `growth/evolution.md` — Track how Rai evolves over time
- [ ] `growth/questions.md` — Open questions Rai is exploring

### Future Scope (Deferred)

- [ ] MCP server for raise-cli (v2.x consideration)
- [ ] Skill audit feature for ecosystem governance (v3.0 consideration)

---

*Created: 2026-01-31*
*Last reviewed: 2026-02-09*
*Last updated: 2026-02-09 (pruned 31 resolved/stale items, consolidated documentation debt)*
