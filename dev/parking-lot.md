# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## Pre-Release (before first PyPI publish) — DONE

- [x] **S-RENAME:** ✓ Already published as `rai-cli` with `rai` entry point
- [x] **S-NAMESPACE:** ✓ Completed SES-140 — `rai-` prefix for all 23 skills
- [x] **First PyPI publish:** ✓ 2.0.0a1 published 2026-02-11, now at 2.0.0a5

---

## Urgent

- [x] **WorkLifecycle phase mismatch** — ✓ Fixed SES-136

- [ ] **Domain stance layer — behavioral priming per project type** — (SES-134, 2026-02-10)
  - **Insight:** Identity (CLAUDE.md) shapes behavior deeply. Governance docs inform but don't prime as strongly. There's a missing middle layer: domain-specific thinking patterns that make Rai fluent, not just informed.
  - **Mechanism:** `domain-stance.md` loaded in system prompt (CLAUDE.md or CLAUDE.local.md). Same identity, different domain lens.
  - **Examples:** Lean Software Development stance (raise-commons), Lean Marketing stance (raise-gtm), Research stance
  - **Not:** A different Rai, a new feature, or the governance docs. It's the domain vocabulary and quality intuitions between identity (universal) and governance (project-specific).
  - **Next:** Prototype in raise-gtm CLAUDE.local.md, validate if alignment improves, then formalize pattern
  - **Priority:** Urgent — affects GTM work starting now, and Jumpstart client onboarding

- [ ] **Marketing strategy** - ASAP, identify dependencies before Feb 15 launch
- [ ] **E-NEXT: Backlog Abstraction Layer (RaiSE PRO)** — (SES-148, 2026-02-13)
  - **Epic candidate.** Platform-agnostic backlog interface: `rai backlog` commands that work against any backend.
  - **Architecture:** Port/Adapter pattern. `BacklogProvider` interface → `JiraAdapter`, `GitLabAdapter`, `OdooAdapter`, `LocalAdapter` (current `work/epics/` = implicit LocalAdapter).
  - **Source of truth is configurable per project:** Local→JIRA (indie/small team), JIRA→Local (enterprise/Coppel), bidirectional sync.
  - **Token economy:** CLI wrapper over `atlassian-python-api` returns compact output (~200 tokens vs ~8,000 from MCP raw JSON per operation). MCP as fallback only.
  - **Strategic context:**
    - Humansys = Atlassian Gold Partner. All devs + Rai using JIRA/Confluence daily = organic demo refinement.
    - Coppel (new client) uses JIRA — direct customer need.
    - March 14 Atlassian webinar — 4 weeks of real usage produces polished demo.
    - Extends to Confluence: `rai docs publish` → Confluence page from design.md, architecture docs.
  - **Includes:** JIRA read/write, Confluence read/write, Compass catalog (when enabled), search (JQL/CQL abstracted).
  - **Validated in PoC:** MCP integration works (SES-148). PRAISE-59 created, Confluence page created, full read/write confirmed.
  - **Priority:** High — enables PRO tier, Atlassian partnership demo, customer delivery.
  - **Depends on:** E18 complete (repo public, CI/CD live).

- [x] **E-NEXT: Multi-IDE Portability** — ✓ Promoted to RAISE-128 (epic/raise-128/ide-integration). Antigravity focus first, Gemini CLI deferred.
  - **Deferred to future story:** Gemini CLI support (`--ide gemini`, `.gemini/skills/`, `GEMINI.md`, `.gemini/commands/*.toml`)
  - **Deferred to future epic:** Other IDEs (Cursor, Windsurf, Continue, Amazon Q, Codex CLI)
  - **Deferred to parking lot:** `rai migrate --ide` for existing projects (convert `.claude/` → `.agent/` in-place)

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
    - [ ] Token monitoring + self-managed context lifecycle — Rai detects context pressure (80% threshold), proactively runs /session-close to capture state, instructs user to open fresh conversation with /session-start. Infrastructure already exists (session-start/close, session-state.yaml). Makes context breaks a managed transition, not a loss. (SES-119, 2026-02-09)
      - **Research update (SES-204, 2026-02-18):** Claude Code hooks no exponen % de contexto a scripts externos — barra de contexto está hardwired al modelo, no hay API. Detección programática está descartada.
      - **Heurístico viable:** 200K para trabajo iterativo diario. Activar `/model sonnet[1m]` para sesiones de onboarding brownfield o análisis masivo de codebase (Sonnet 4.6: mismo precio hasta 200K, triple sobre 200K). Señal manual: cuando la conversación se siente larga → `/rai-session-close` consciente + nuevo thread con `/rai-session-start`.
      - **Lost-in-the-middle:** calidad se degrada con contexto acumulado largo — argumento adicional para breaks frecuentes como práctica, no solo como emergencia.
    - [ ] Hybrid skills — markdown process + JSON schema + validation code

- [ ] **Session duration tracking** — (SES-011 raise-gtm, 2026-02-16)
  - **Problem:** `rai session start/close` only records date, not timestamps. No way to measure actual session duration. Calibration data (estimated vs actual minutes) is manually estimated from commit timestamps, not measured.
  - **What:** Record ISO timestamps on session start and close in `sessions/index.jsonl`. Calculate and display duration on close. Enable velocity analysis across sessions.
  - **Priority:** Medium — low effort, high compound value for calibration accuracy

---

## Process Debt

- [ ] **Deterministic backlog sync via CLI** — (SES-150, 2026-02-13, S-RELEASE-ONTOLOGY)
  - **Problem:** Epic lifecycle skills (start/close) rely on inference to update `governance/backlog.md`. E18-E22 existed but weren't in the backlog — zero release→epic edges in graph. Strategy sessions that define future epics also bypass the backlog.
  - **Skill fix (done):** Added Step 5 to `/rai-epic-start` requiring backlog row registration. `/rai-epic-close` already had Step 6.
  - **CLI fix (needed):** `rai epic register E{N} --name "..." --status "In Progress"` — deterministic command that adds/updates the backlog row. Removes inference from the loop. Same pattern as `rai memory emit-work`.
  - **Also needed:** `rai epic update-status E{N} --status complete` for close, and backlog sync during planning sessions when future epics are defined.
  - **Priority:** High — backlog is the authoritative epic index; if it drifts, the ontology graph is incomplete.
  - **Related:** PAT-194 (infrastructure without wiring), PAT-196 (stale docs → wrong paths)

- [ ] **Skill sync on upgrade — `rai skill sync`** — (SES-007, 2026-02-17)
  - **Problem:** `scaffold_skills()` is idempotent — skips existing `SKILL.md` files. When user upgrades rai-cli via pip, project skills stay at the version from first `rai init`. No mechanism to detect stale skills or pull updates.
  - **What:** `rai skill sync` command that compares bundled skills (in `skills_base/`) against project skills (`.claude/skills/`), detects version drift, and updates with user confirmation.
  - **Considerations:** Needs version tracking per skill (frontmatter `version` field already exists). Diff display before overwrite. Backup of customized skills.
  - **Priority:** Medium — affects every project that upgrades rai-cli
  - **Related:** RAISE-144 (Engineering Health)

---

## Ideas

### Local Rai Runtime — Daemon con AOP para telemetría y tracking (SES-223, 2026-02-19)

- [ ] **Local Rai Runtime — daemon de background para telemetría como aspecto** — (SES-223, 2026-02-19)
  - **Insight:** La telemetría y el session tracking hoy viven *dentro* de las skills (emit-work calls, session start/close en el contenido). Esto es frágil (RAISE-201 fue un síntoma), limita la riqueza de datos, y añade complejidad a las skills. Un daemon local convierte estos cross-cutting concerns en aspectos de la infraestructura, no del contenido.
  - **Mecanismo central:**
    1. **CLI middleware** — un solo interceptor en `app.callback()` (no en cada comando). Cada `rai` invocation emite un `CliEvent` tipado al daemon. Graceful degradation: si el daemon no corre, timeout 50ms, CLI continúa sin error.
    2. **Unix socket** — `~/.rai/daemon.sock`. IPC local, sin red, sin latencia perceptible. Inspirado en OpenClaw Gateway (`ws://127.0.0.1:18789`) pero más simple y tipado.
    3. **Correlación por env var** — el agente (Claude Code) setea `RAI_SKILL_CONTEXT=<skill>:<story-id>` antes de ejecutar una skill. CLI lo lee e incluye en el evento. Skills no hacen ninguna llamada de tracking. Agente setea el var una vez.
    4. **Filesystem watcher** — cubre cambios a `.raise/` fuera del CLI (edits manuales, agente escribiendo archivos directamente). También detecta sesiones huérfanas (RAISE-201 estructuralmente).
  - **Lo que captura que hoy no tenemos:**
    - Duración real por skill (no estimada)
    - Pasos re-ejecutados dentro de una skill
    - Correcciones: `add-pattern` inmediatamente post-error
    - Tiempo entre skills (cadencia real de trabajo)
    - CLI calls sin contexto de skill (work ad-hoc)
    - Cache hits vs misses en memory query
  - **Puerta de entrada a inference local (COMMUNITY):** daemon puramente determinista en v1. Si hay modelo local configurado (Ollama, LM Studio), el mismo daemon puede añadir inference opcional: "llevas 40 min en story-plan sin avanzar de fase de diseño — ¿quieres ayuda?". Sin backend requerido.
  - **Relación con ADR-035:** el backend PRO/Enterprise tiene su propio agent loop (Hosted Rai). Este daemon es el equivalente COMMUNITY — mismo patrón, distinto alcance.
  - **Impacto en skills:** skills existentes se simplifican. Sin llamadas `rai memory emit-work`. Sin `rai session start/close` explícitos en el contenido. El daemon maneja todo.
  - **Riesgo:** proceso permanente en máquina del developer → consumo de recursos, crashes, conflictos con otros procesos. Diseño debe ser ultra-ligero. `rai daemon start|stop|status` como interfaz explícita.
  - **Prioridad:** Media-Alta — resuelve problemas estructurales (RAISE-201 class), habilita telemetría rica, y es prerequisito para inference local. Candidato a epic post-V3.
  - **Referencias:** OpenClaw Gateway pattern, AOP (Aspect-Oriented Programming), ADR-034 §TriggerAdapter, ADR-035 §Hosted Rai Agent Loop

---

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

- [ ] **`rai init` generates CLAUDE.md from .raise/ canonical source** — (SES-209, 2026-02-18, ADR-012)
  - **Context:** RAISE-165 established CLAUDE.md as a projection from `.raise/` canonical source. Currently hand-written. `rai init --ide claude-code` should deterministically generate it.
  - **Scope:** Read identity files + process rules + CLI introspection → generate CLAUDE.md. Also `rai init --ide cursor` for `.cursorrules`.
  - **Priority:** Medium — closes the loop on ADR-012's deterministic update principle

- [ ] **`rai cli reference --compact` auto-generation** — (SES-200, 2026-02-17)
  - **Context:** RAISE-163 solved CLI fumbling by regenerating cli-reference.md manually from `--help` output. But it drifts when commands change.
  - **What:** CLI command that generates compact reference from argparse/click introspection. Run during session-start or as pre-commit hook.
  - **Priority:** Low — manual regeneration works, automation is polish

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

- [x] **CLI integration test isolation (`--test-dir`)** — (SES-098, 2026-02-08) ✓ Solved via `conftest.py` autouse fixture (2026-02-16)
  - **What:** Prevented test leakage into `~/.rai/developer.yaml` via global `_isolate_rai_home` fixture
  - **Resolution:** `tests/conftest.py` redirects `get_rai_home` to `tmp_path` for all tests. No `--test-dir` flag needed.

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
- [x] **Research gate for UX-facing stories** — ✓ S-RESEARCH-GATE (SES-142)

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
- [x] **Multi-language support** — ✓ E17 Multi-Language Discovery

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

- [x] **Multi-platform code analyzers** — ✓ E17 (2026-02-10)
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

### RAISE-197 Session — Parking Lot (2026-02-18)

- [ ] **RaiSE Hub — curated skill marketplace** — (SES-213, 2026-02-18, OpenClaw research)
  - **Context:** OpenClaw's ClawHub hit 5,000+ skills in weeks via network effects, but also attracted malicious skills (Cisco found exfiltration, prompt injection). VirusTotal scanning added reactively.
  - **RaiSE differentiator:** Process-embedded skills (TDD, gates, retrospectives) vs generic "teach AI a tool" skills. Governance-aware curation = enterprise trust advantage.
  - **What:** Curated marketplace where teams publish process skills with verification + governance metadata.
  - **Priority:** Strategic — post-RAISE-197, depends on plugin architecture being validated
  - **Related:** AgentSkills standard convergence, F&F user wanting "connectors"

- [ ] **Skills as MCP servers — portable process execution** — (SES-213, 2026-02-18)
  - **Context:** OpenClaw validates two-layer model: Skills (tight integration) + MCP (portable). RaiSE already uses MCP for external tools (Jira).
  - **What:** Expose RaiSE skills as MCP servers consumable by OpenClaw, Claude Code, Cursor, any MCP-compatible agent. Our process becomes portable to any agent.
  - **Priority:** Medium-term — after plugin architecture stabilizes

- [ ] **`rai migrate --agent` for existing projects** — (SES-213, 2026-02-18)
  - **What:** Convert existing IDE-specific files in-place (e.g., `.claude/` → `.cursor/` + `.windsurf/`). Inverse of `rai init --detect`.
  - **Previously:** Listed as `rai migrate --ide` in E14 deferred items. Updated scope with agent terminology.

---

### RAISE-169 Session — Parking Lot (2026-02-18)

- [ ] **`rai session context --all` shortcut** — Load all priming sections at once instead of listing each name. Observe over 3-5 sessions whether full loading is common enough to warrant a shortcut.
- [ ] **Two-phase context loading friction monitoring** — RAISE-169 introduced lean bundle + `rai session context --sections`. Monitor if the extra step feels natural or adds friction. If friction: consider auto-loading a default set. If natural: leave as-is.

---

### RAISE-170 Session — Parking Lot (2026-02-19)

- [ ] **Curación de patrones: análisis AI-driven para identificar foundational + duplicados** — (SES-217, 2026-02-19)
  - **Idea:** Con 378 patrones de peso uniforme, hay candidatos a `foundational: true` que no están marcados como tales, patrones redundantes, y posibles contradicciones.
  - **Qué haría:** Leer todos los patrones del JSONL, analizar cada uno con inferencia: ¿debería ser foundational? ¿es redundante con otro? ¿contradice otro?
  - **Output:** Reporte de candidatos a foundational, pares de duplicados potenciales, sugerencias de re-rank inicial.
  - **Encaje natural:** Podría ser el núcleo de `rai memory health` (ya en parking lot como deferred de RAISE-171) o historia separada de curaduría.
  - **Trigger para promover:** Cuando RAISE-170 esté completo y el scoring real revele patrones que suben/bajan significativamente — ahí el análisis de curación será más informado.

---

### SES-218 — Parking Lot (2026-02-19)

- [ ] **Documentar que bugs siguen el story lifecycle** — (SES-218, 2026-02-19)
  - **Gap:** CLAUDE.md (generado por `rai init`) documenta `STORY:` lifecycle pero no dice explícitamente que Bugs siguen el mismo ciclo (start → design → plan → implement → review → close).
  - **Fix:** Agregar regla en el source canónico de `.raise/` que genera CLAUDE.md. 2-liner.
  - **Priority:** Low — regla clara, no necesita research.

---

---

### SES-222 — Parking Lot (2026-02-19)

- [ ] **Invitar a Gustavo a construir raise-azuredevops-adapter** — (SES-222, 2026-02-19)
  - **Context:** Gustavo (desarrollador, conocido de Emilio) quiere construir un adaptador de RaiSE para Azure DevOps.
  - **Timing:** Esperar a que RAISE-204 (contratos ADR-033) esté implementado y publicado. Sin contratos estables, el adaptador no tiene base.
  - **Acción:** Una vez que `rai-cli` incluya `ProjectManagementAdapter` Protocol + `rai.adapters.pm` entry point, compartir el ADR-033 con Gustavo como punto de partida.

- [ ] **PAT-E-354 desactualizado — "4 of 5 IDEs"** — (SES-222, 2026-02-19)
  - **Context:** El patrón dice "4 of 5 IDEs" pero Roo Code ya es el 6to IDE soportado (RAISE-202). Texto desactualizado.
  - **Fix:** Actualizar el texto del patrón para reflejar el estado actual.
  - **Priority:** Low — cosmético, no bloquea nada.

---

*Created: 2026-01-31*
*Last reviewed: 2026-02-12*
*Last updated: 2026-02-19 (SES-222: Gustavo/Azure DevOps adapter, PAT-E-354 stale)*
