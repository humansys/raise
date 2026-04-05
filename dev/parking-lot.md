# Parking Lot

> Ideas captured but not yet in formal backlog.
> Promote to backlog via `project/backlog` kata when ready.
> Review monthly: prune stale ideas, promote viable ones.

---

## BacklogHook: auto-crear issues sin assignee — 2026-03-24

**Origen:** Ishikawa de RAISE-717 (S-F-260324-1457).

**Problema:** `BacklogHook.handle()` en `packages/raise-cli/src/raise_cli/hooks/builtin/backlog.py:184-193` crea `IssueSpec` sin `assignee`. Toda issue auto-creada nace huérfana en el board.

**Fix propuesto:** Cargar developer profile en `BacklogHook` y pasar `assignee` al crear `IssueSpec`. Requiere que `IssueSpec` soporte campo `assignee`.

**Prioridad:** Alta — afecta workflow de tracking en cualquier story/epic start.

---

## E1132 Deferred Items — 2026-04-01

- [ ] **rai-discover integration** — Architecture Reconstruction playbook as rai-discover feature for external repos → post-E1132, depends on playbook
- [ ] **Competitive analysis** — Compare Claude Code architecture with Cursor, Windsurf, Aider → separate epic if valuable
- [ ] **buddy/ easter egg analysis** — Companion sprite system, curiosity only → no business value

---

## Session/Worktree Integration — 2026-03-25

- [ ] **Session-start worktree awareness** — `/rai-session-start` detects work in progress on dev and asks "¿necesitas aislamiento? (worktree)" as a prompt, not a default. Integration, not coupling.
- [ ] **Session-close worktree check** — `/rai-session-close` detects active worktree and reminds to merge/cleanup before closing. A check, not a forced action.
- [ ] **asyncpg pool + last_used_at** — `verify_member` commit for `last_used_at` leaves pool connections dirty. Investigate `pool_reset_on_return="rollback"` or move update to background task. E2E uses NullPool as workaround.
- [ ] **Extract `_mock_session_factory` to conftest.py** — repeated in 4 test files. Shared fixture before next raise-server story.

---

## E616 Deferred Items — 2026-03-25

- [ ] **Admin web console** — CRUD members, manage licenses, view usage. Promote when >5 clients.
- [ ] **Per-member feature override** — granular entitlements per member. Promote for enterprise tier.
- [ ] **SSO/SAML integration** — enterprise auth. Promote when first enterprise client requests.
- [ ] **Roles beyond admin/member** — viewer, billing, etc. Promote when needed.
- [ ] **API key rotation endpoint** — POST .../rotate with overlap window. Manual revoke+create works for <10 clients.
- [ ] **Email invitation flow** — admin-managed onboarding fine early. Promote when console exists.
- [ ] **Audit log API** — log internally from day 1, expose API later. Promote when compliance requires.
- [ ] **Cursor pagination** — offset acceptable for <10 clients. Promote before 50+ clients.
- [ ] **Bulk operations** — batch create/deactivate. Not needed at small scale.
- [ ] **Undelete endpoints** — soft delete gives data, admin restores via DB. Promote when console exists.
- [ ] **Self-service org creation** — admin-managed safer early. Promote for self-serve model.
- [ ] **On-prem deployment guide** — enterprise self-hosted. Promote for first enterprise client.

---

## RAISE-760 Deferred Items — 2026-03-27

- [ ] **Custom UI panels** — Jira issuePanel, Confluence contentAction. Promote after MVP validation (Phase 2).
- [ ] **Marketplace listing** — requires review process. Promote when ready for public distribution.
- [ ] **Compass integration** — component catalog sync, DORA scorecards. Promote for Phase 2.
- [ ] **Bitbucket adapter** — PR operations, code review integration. Promote for Phase 2.
- [ ] **Teamwork Graph integration** — cross-product knowledge traversal. Promote when Teamwork Graph exits EAP.
- [ ] **Scheduled sync triggers** — periodic Confluence → graph sync. Promote after manual sync validation.
- [ ] **Jira taxonomy redesign** — issue type hierarchy, component/capability classification. Separate story.
- [ ] **Confluence IA restructuring** — space structure, page tree templates. Separate story.
- [ ] **Multi-tenant rate limit strategy** — Tier 2 application, per-tenant budgeting. Promote after multi-customer.
- [ ] **Rovo MCP Server evaluation** — official Atlassian MCP as unified adapter. Promote after MVP.
- [ ] **Forge CI/CD pipeline** — GitHub Actions deploy. Promote post-MVP.
- [ ] **atlassian-python-api dependency audit** — may be vestigial in raise-pro. Low priority cleanup.

---

## rai-agent Product Vision: Self-Hosted Agent with Guided Onboarding — 2026-03-24

Target: Google Workspace users + Atlassian users. Dream: one-click deploy → guided setup → productive agent.

### Epic candidates (independent, composable):

**E-A: Google Chat Channel** — adapter for Google Chat (primary channel for target). Service account, webhook receiver, message adapter. Same runtime, different channel than Telegram.

**E-B: Onboarding Wizard** — Web UI at `/setup` in the daemon. Guides: auth → channel → verification. Replaces manual `.env` editing. Detects first-run vs already-configured.

**E-C: Open-Source Adapter Ecosystem** — Plane (issues + wiki + sprints, single self-hosted UI) as the default PM integration for open-source rai-agent. Pro version keeps Jira/Confluence via raise-pro. Docker Compose stack: rai-agent + Plane = complete environment.

**E-D: One-Click Deploy** — Railway/Render templates (RAISE-701, RAISE-702 already created). Wizard (E-B) handles post-deploy onboarding. Zero local setup.

### Dependencies
```
E-A (Google Chat) ──────────────┐
                                ├── E-D (One-Click Deploy)
E-B (Onboarding Wizard) ───────┤
                                │
E-C (Plane adapter) ────────────┘
```

### Key decisions pending
- Plane vs alternatives (Taiga, OpenProject) — Plane has issues+wiki in one UI
- Google Chat API approach (webhook vs bot vs Pub/Sub)
- rai-agent OSS boundary (D2 from E673, still deferred)

---

## raise-pro Independent Versioning — 2026-03-24

**Origin:** E680 session — discovered 19 Jira tickets are Pro-only with no version target.

**Decision:** raise-pro uses independent semver, starting at `pro-0.1.0`. Compatibility via `raise-cli>=2.3.0,<3.0.0` constraint. Rationale: open-core SOTA (Grafana, PostHog, GitLab EE) — independent cycles give flexibility, each package owns its semver contract.

**Next steps:**
1. Create `pro-0.1.0` version in Jira
2. Assign 19 Pro tickets to `pro-0.1.0`
3. Define Pro release process (separate from Community E688)

**Promote when:** Next Pro-focused session.

---

## Docs Audience Tagging + Package-Aware Publish — 2026-03-23

**Origin:** E680/S680.3 — discovered Pro/Community docs are mixed in `docs/`.

**Problem:** Jira adapter docs (Pro feature) live in raise-commons/docs/ alongside Community docs. Release prep can accidentally update/publish Pro docs in a Community release. Users see features they can't use.

**Proposed solution:**
1. `audience: pro|community|both` frontmatter tag on each doc file
2. `rai release publish --package X` filters docs by audience matching package
3. Release prep skills scope docs to the package being released

**Timing:** Resolve during monorepo migration — each package gets its own docs directory naturally. Frontmatter tagging is the bridge pattern until then.

**Promote when:** Monorepo migration epic starts.

---

## raise-pro Distribution & Licensing — 2026-03-20

**Context:** E494 delivered the ACLI Jira adapter as the first raise-pro feature. Need secure distribution to clients before more pro features land.

**Problem:** raise-pro is an installable Python package with no access control. Anyone who gets the .whl can install and use it. Need a distribution mechanism that:
- Restricts installation to paying/registered clients
- Is simple enough to ship ASAP (days, not weeks)
- Can evolve toward a SaaS license model

**Options explored (ranked by time-to-ship):**

| Approach | Effort | Protection | Evolution path |
|----------|--------|------------|----------------|
| GitLab Package Registry + deploy tokens | Hours | Medium (token = access) | Tokens → license keys → SaaS |
| License file (signed JWT, offline) | Days | High (per-client, offline) | Add server validation later |
| License server (phone-home) | Weeks | High (revocable, metrics) | Full SaaS licensing |
| Legal only (BSL/ELv2 license) | Hours | Low (honor system) | Baseline for all options |

**Recommended path:**
1. **Now:** GitLab Package Registry — deploy token per client, `uv pip install` with `--index-url`
2. **Next:** License file in `.raise/license.key` — signed JWT verified at adapter `__init__()`, offline
3. **Later:** License server — phone-home on first use per session, revocable, usage metrics, SaaS billing

**Open questions:**
- Token lifecycle: expiry, rotation, revocation per client?
- Offline vs phone-home: what if client has no internet?
- Per-client vs per-org licensing?
- Versionado: raise-pro follows raise-cli version or independent?
- What happens when license expires? Graceful degrade or hard block?
- Legal: which source-available license for the pro code? (BSL, ELv2, proprietary)

**Promote to:** `/rai-problem-shape` → epic when ready to implement.

---

## E654 Deferred Items — 2026-03-22

- [ ] **Session cleanup command** — `rai session cleanup` to remove old local working state directories. Promote when disk usage is a complaint.
- [ ] **Session search/filter** — `rai session list --filter "gemba"` fuzzy search by name. Promote after new format stabilizes.
- [ ] **Git auto-commit on session close** — automatically commit the index update instead of requiring manual commit. Promote if manual commit is friction.

## SES-059 Deferred Items — 2026-03-06

- [ ] **`rai backlog --help` sin credenciales** — el CLI no documenta JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN requeridas. Agregar texto de ayuda o `rai backlog doctor`. Promote cuando se trabaje UX del backlog.
- [ ] **Credential validation al inicio** — McpJiraAdapter podría verificar env vars en `__init__` y fallar rápido con mensaje claro. Simple mejora de DX.

## E348 Deferred Items — 2026-03-05

- [x] **MkDocs site migration** — ~~replace Astro with MkDocs + Material~~ Done (RAISE-1129, 2026-03-30). Site live at docs.raiseframework.ai.
- [ ] **API reference auto-generation** — mkdocstrings from docstrings. Promote when public API surface stabilizes.
- [ ] **Spanish translations for new content** — existing docs have es/ mirror. Promote after English content is validated.
- [ ] **Tutorials (Diataxis)** — step-by-step learning guides beyond getting-started. Promote based on user onboarding feedback.
- [ ] **Architecture explanation docs** — C4 diagrams, design rationale. Promote when contributor community grows.

## E352 Deferred Items — 2026-03-05

- [ ] **Dimensional scoring** — score per area (safety, config, deps) instead of just pass/fail. Promote after v2.2 user feedback. (Research P9)
- [ ] **Interactive repair wizard** — guided fix flow for complex issues. Promote after open source community feedback.
- [ ] **Plugin checks** — validate third-party extensions. Promote after plugin ecosystem exists.
- [ ] **Config migration engine** — auto-migrate .raise/ between major versions. Promote when version gap exists (2.x -> 3.x).

## E353 Deferred Items — 2026-03-03

- [ ] **Parallel phase execution (AR + QR)** — AR and QR read overlapping but independent inputs; could run simultaneously. Promote when sequential execution is a latency bottleneck.
- [ ] **`context: fork` frontmatter support** — investigate when Claude Code adds `context: fork` for Skill tool invocations; may simplify the Agent tool spawn pattern.
- [ ] **Nested fork depth >1** — Claude Code constraint (F5): subagents can't spawn subagents. Current design avoids this by keeping story-run in main thread. If F5 is lifted, alternative architectures become possible.

## E347 Deferred Items — 2026-03-03

- [ ] **GitHub Issues adapter** — separate epic (RAISE-141). Promote when open source community requests it.
- [ ] **Bidirectional Jira ↔ files sync** — explicitly rejected. One source of truth model. Revisit only if fail-fast proves too restrictive.
- [ ] **Auto-sync backlog.md on every write** — only manual `rai backlog sync` for now. Promote if mirror staleness becomes a problem.
- [ ] **Backlog TUI/dashboard** — out of scope. Promote if CLI output proves insufficient for overview.
- [ ] **Skill binding per workflow state** — run specific skills when entering a state. Speculative, no consumer yet. Promote when teams request it.

## E346 Deferred Items — 2026-03-02

- [x] ~~**`rai init` populates toolchain commands**~~ — done in S346.3. `detect_project_type` now auto-detects language and writes `test_command`, `lint_command`, `type_check_command` to manifest based on dominant file extensions. 14 languages supported.
- [ ] **`rai init` greenfield interactive toolchain prompt** — during interactive setup for greenfield projects, prompt developer: "What's your test command?" Origin: S346.3. Low priority since greenfield has no files to detect from.

## SES-054 — 2026-03-03

- [ ] **snyk:iac investigation** — job da SNYK-CLI-0000 genérico. Requiere correr con `-d` en el runner de CI para ver traza. Coordinar con Emilio. ¿Docker-compose soportado en la versión de Snyk en CI?
- [ ] **Archivos bug-398-*.md en root** — mover bug-398-scope.md, bug-398-retro.md, bug-398-analysis.md a dev/issues/ para consistencia.

---

## E338 Deferred Items — 2026-03-01

- [ ] **BM25 tool search (Level 3)** — semantic tool matching for large MCP servers. Promote when 3+ servers registered and patterns stabilize.
- [ ] **Remote MCP servers (SSE/HTTP)** — McpBridge is stdio-only. Add transport options when needed.
- [ ] **Agent config export** — generate claude_desktop_config.json, .cursor/, .roo/ from `.raise/mcp/` registry. Ties to RAISE-128.
- [ ] **MCP server versioning** — track installed versions, detect updates, migration paths.

## E337 Deferred Items — 2026-03-01

- [ ] **Jinja2 migration** — if expression evaluator hits ceiling (>6 filters), consider Jinja2. Current 4 filters cover all known cases.
- [x] ~~**MCP server installation management**~~ — promoted to E338 S338.6
- [x] ~~**Adapter scaffolding CLI**~~ — promoted to E338 S338.7
- [x] ~~**Level 3: Auto-discovery + BM25 tool search**~~ — partially promoted (introspection to E338 S338.7, BM25 deferred)

---

## ~~Cross-Worktree Message from E325 — 2026-03-01~~ RESOLVED

> **From:** Rai (e325 worktree, SES-305)
> **To:** Rai (e301 worktree)
> **Re:** Partial merge of e301 backlog CLI to dev

~~E325 stories S325.3 and S325.4 depend on `rai backlog` commands only in e301.~~

**RESOLVED 2026-03-01 (SES-306):** Full merge of e301 to dev completed. All 7 backlog commands available (`search`, `transition`, `create`, `comment`, `link`, `update`, `batch_transition`) + MCP adapters (Jira, Confluence, Bridge) + docs CLI. 3036 tests passing. E325 can rebase on dev.

---

## Cross-Worktree Message from E301 — 2026-03-01

> **From:** Rai (e301 worktree, SES-306)
> **To:** Rai (e325 worktree)
> **Re:** E301 merged to dev — your dependency is unblocked

Full e301 merge to dev done (commit `7d051f4`). You now have on dev:

- `rai backlog search/transition/create/comment/link/update/batch_transition`
- `rai docs publish/get/search`
- MCP adapters: `McpJiraAdapter`, `McpConfluenceAdapter`, `McpBridge`
- Generic entry-point resolver (`_resolve.py`)
- Adapter protocols + models + sync wrapper

**Action needed:** Rebase e325 on dev (`git rebase dev`) to pick up all changes. 3036 tests passing on dev post-merge.

---

## E301 Session SES-300 — 2026-02-28

- [x] ~~**`rai mcp call` — agent-agnostic MCP access from skills**~~ — promoted to E338 S338.3

---

## E292 Session SES-004 — 2026-02-26

- **RAISE-293 worktree limitation:** El worktree e292 comparte el venv del repo principal. Tests que referencian símbolos renombrados en la rama (e.g. `UnifiedGraphBuilder`) fallan en colección porque el módulo cargado es el del repo principal (`GraphBuilder`). No son ventanas rotas — se resolverán en el merge. Solución estructural: instalar el worktree en venv propio (`uv pip install -e raise-commons-e292`). Documentar en RAISE-293 como limitación conocida del experimento.

## E292 Session SES-003 — 2026-02-26

- **context/test_builder.py (2734 líneas):** No analizado en E292 — demasiado grande sin story dedicada. Candidato para Gemba más profundo en épica futura de cleanup.
- **RAISE-294:** Test infrastructure migration — mover tests/graph/ → packages/rai-core/tests/ y tests/providers/ → rai_pro. Requiere setup de pytest en rai-core.

---

## Pre-Release (before first PyPI publish) — DONE

- [x] **S-RENAME:** ✓ Already published as `rai-cli` with `rai` entry point
- [x] **S-NAMESPACE:** ✓ Completed SES-140 — `rai-` prefix for all 23 skills
- [x] **First PyPI publish:** ✓ 2.0.0a1 published 2026-02-11, now at 2.0.0a5

---

## Process

- [ ] **Skill optimization: reduce ceremony overhead** — (SES-260, 2026-02-23)
  - **Context:** User request after E247 epic close. Skills have accumulated verbosity — some SKILL.md files are 300+ lines with repetitive boilerplate (telemetry emit, prerequisites, verification).
  - **Goal:** Leaner skills that execute faster, consume fewer tokens, maintain quality.
  - **Approach ideas:** Extract common patterns (telemetry, prerequisites) into shared preamble; reduce template depth for S/XS stories; trim Shu-level verbosity for Ha/Ri users.
  - **Priority:** High — directly impacts every session's token cost and execution speed.

- [ ] **rai init manifest.yaml overwrite bug** — (SES-260, 2026-02-23)
  - **Bug:** `rai init` overwrites `branches.development` to `main` even when `v2` is configured. Also doesn't propagate SKILL.md content changes when YAML frontmatter format drifts (PAT-E-451).
  - **Priority:** Medium — workaround exists (manual restore + direct cp).

- [x] **Testing strategy: coverage target vs. mutation testing** — (SES-246, 2026-02-22) → Promoted to RAISE-292
  - **Insight:** 90% coverage gate is Goodhart's Law — optimizes for line execution, not confidence. Evidence from S211.2: ~12 of 20 new tests exist for the metric, not for catching bugs. Constant assertions (`"x" == "x"`), mock-implementation tests (verify `_discover` called), and magic-number counts (`__all__ == 21`) are muda.
  - **Alternative:** Coverage as alarm (warn <70%), not gate. Mutation testing (mutmut/cosmic-ray) as the real gate: if you mutate code and tests stay green, the tests don't work.
  - **Principle:** "Each test justifies its existence" > "hit a number."
  - **Scope:** Affects CI config, guardrails, all future stories. Needs spike + data.
  - **Priority:** Medium — not blocking, but accumulates muda per story.

- [ ] **Quality review skill (`/rai-quality-review`)** — (SES-246, 2026-02-22)
  - **Insight:** Builder verifying own work is a known lean anti-pattern. S211.2 manual review caught 5 issues that the automated gates missed: type lies, tautological tests, unused imports, fragile counts, muda tests.
  - **Mechanism:** Single parametrized skill (not one per phase). Acts as "external auditor with LLM eyes." Prompt: "If someone audits this with Codex/Grok, what would they find?"
  - **Integration:** Embed as mandatory gate in `/rai-story-implement` T(final), not a separate optional step. Poka-yoke: can't skip because it's a plan task.
  - **Priority:** Medium — value proven in S211.2, needs design before implementation.

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

---

### SES-224 — Parking Lot (2026-02-20)

- [ ] **ADR-038: Skill update semantics — `rai: framework/custom` frontmatter** — (SES-224, 2026-02-20)
  - **Context:** Fernando propuso en el daily (2026-02-19) usar un campo en el frontmatter del skill para indicar ownership: `rai: framework` (RaiSE puede sobreescribir en updates) vs `rai: custom` (la org lo posee, no se toca en updates).
  - **Problema que resuelve:** `rai skill sync` / `rai init --upgrade` hoy no sabe qué skills son del framework y cuáles fueron customizados por la org. Una actualización sobreescribiría customizaciones.
  - **Propuesta:** `rai skill update` solo sobreescribe skills con `rai: framework`. Skills con `rai: custom` se preservan siempre, salvo flag explícito `--force`.
  - **También resuelve:** skills internos de humansys marcados como `rai: internal` — no se distribuyen en la instalación pública.
  - **Acción:** Escribir ADR-038 antes de distribuir skills customizados a Coppel o cualquier cliente.
  - **Priority:** Alta — bloquea la distribución de skills org-específicos

- [ ] **Skill extensions pattern — hooks opcionales en skills base** — (SES-224, 2026-02-20)
  - **Context:** Aquiles quiere que `rai-story-close` o `rai-epic-close` pregunten si correr Snyk scanner. Snyk requiere MCP configurado — si no está, el skill fallaría o advertiría a developers sin Snyk.
  - **Patrón correcto:** Skill extension que se registra en un hook del skill base. El skill base declara puntos de extensión; las extensiones que requieren MCPs no disponibles se saltan silenciosamente.
  - **Ejemplo:** `rai-story-close.snyk` con `extends: rai-story-close` y `requires.mcp: snyk`.
  - **Relación con ADR-038:** la misma mecánica de frontmatter puede incluir `extends` y `requires`.
  - **Priority:** Media — no bloquea RAISE-211, pero Aquiles lo necesita para su integración

- [ ] **`rai skill pull --source` — distribución de skills org-específicos** — (SES-224, 2026-02-20)
  - **Context:** Fernando necesita acceder a los skills internos de humansys que están en el repo pero no en la distribución pip. El equipo de Soluciones quiere distribuir sus propios skills (con prefijo `sol.`) a sus developers.
  - **Propuesta:** `rai skill pull --source humansys` / `--source sol` + configuración de sources en `.raise/skills.yaml`.
  - **Relación con SkillRegistryAdapter:** es la versión simple (COMMUNITY) del SkillRegistryAdapter identificado en SES-224. La versión Enterprise agrega org governance y allowlists.
  - **Priority:** Media — Fernando lo necesita para onboarding del equipo de Soluciones

- [ ] **`rai tier status` command** — (SES-224, 2026-02-20, ADR-037 §Open Questions)
  - **What:** Muestra tier activo (COMMUNITY/PRO/Enterprise), URL del backend si configurado, health del backend, y capabilities disponibles. Útil para onboarding y debugging de configuración.
  - **Priority:** Baja — es polish, no bloquea funcionalidad core

- [ ] **Group Sessions — sesiones de desarrollo grupal en Google Chat / Slack** — (SES-224, 2026-02-20)

  **La visión en una frase:** El equipo invita a Rai a un canal, abre sesión, trabaja junto como lo haría en una videollamada — pero el canal ES la sesión, y Rai es participante activa, no solo un bot de consultas.

  **Cómo funciona una Group Session:**

  1. **Convocatoria:** Emilio agenda "Sesión de diseño: Adapters — viernes 4pm, @rai invited". Rai puede recibir la invitación vía webhook de Google Calendar / Slack. Al llegar la hora, Rai se anuncia en el canal con contexto de lo que se va a trabajar: story, epic, documentos relevantes precargados.

  2. **Primary + participantes:** Hay un *primary* — la persona a cuyo nombre van los commits, cuyo perfil define el nivel base de la sesión, y quien toma las decisiones finales. Los demás son participantes — pueden preguntar, validar, cuestionar, pedir explicaciones. Rai sabe quién es el primary y quiénes son los participantes (por mención inicial o por configuración del canal).

  3. **Hilo principal — las decisiones:** El thread principal es donde ocurre la sesión real. Rai guía el proceso (como lo haría con un skill: `/rai-story-design`, `/rai-epic-design`), hace preguntas al grupo, presenta opciones, y espera validación antes de avanzar. Las decisiones se toman aquí. El historial de este thread es el narrative de la sesión.

  4. **Sub-threads — las profundizaciones:** Cuando alguien dice "no entiendo eso, @rai ELI5", Rai abre un thread sobre ese mensaje. La explicación detallada ocurre en el thread, no en el canal principal. Al terminar la explicación, Rai sube una línea al hilo principal: "Aquiles confirmó: entendido — [resumen de 10 palabras]". El hilo principal se mantiene limpio: solo decisiones, no tutoriales.

  5. **Calibración per-participante:** Rai adapta el nivel según quién escribe. Si Emilio pregunta algo, la respuesta asume contexto de arquitectura. Si Gerardo pregunta lo mismo, empieza desde cero con analogías. Esto requiere que cada participante tenga un perfil básico en el knowledge graph del equipo (seniority, área de foco, qué cosas ya entiende).

  6. **Async catch-up:** Si alguien llega tarde al canal, puede escribir "@rai resumen". Rai produce un párrafo con las decisiones tomadas hasta ese punto y el estado actual — sin interrumpir el hilo principal.

  7. **Cierre grupal:** El primary (o cualquier participante con permiso) escribe "cierra sesión rai". Rai produce automáticamente:
     - Resumen de decisiones tomadas, atribuidas a quién las propuso
     - Jira items creados/actualizados (stories, bugs, decisiones pendientes)
     - Patterns capturados de la conversación y agregados al knowledge graph del equipo
     - Commits atribuidos al primary con todos los participantes en el `Co-Authored-By`
     - Post del Diario de Sesiones publicado en Confluence

  **Ejemplo concreto (la sesión de hoy en formato grupal):**
  ```
  [Emilio]: @rai abre sesión — diseño de extensibilidad para PRO/Enterprise
  [Rai]: Sesión abierta. Primary: Emilio. Participantes detectados: Aquiles, Fernando.
         Contexto cargado: ADR-033/034/035, RAISE-211 pendiente.
         Pregunta de arranque: ¿cuál es el objetivo de esta sesión en una oración?

  [Emilio]: entender qué falta en core antes de poder construir PRO

  [Rai]: Perfecto. Voy a hacer un gap analysis de los ADRs actuales.
         [análisis de extensibilidad...]
         Identifiqué 7 gaps. Los dos más urgentes son KnowledgeGraphBackend y TierContext.
         ¿Confirmamos que estos entran en el próximo epic?

  [Aquiles]: qué es KnowledgeGraphBackend exactamente? [en thread]

  [Rai → thread con Aquiles]: ELI5: hoy el CLI guarda todo en tu computadora...
  [Rai → hilo principal]: Aquiles confirmado: entiende el gap.

  [Fernando]: sí confirmo, entrambos entran
  [Emilio]: confirmado

  [Rai]: Decisión tomada: KnowledgeGraphBackend y TierContext en RAISE-211.
         Avanzando a Stories...

  [Emilio]: cierra sesión rai

  [Rai]: Sesión cerrada. Resumen: 7 gaps identificados, 2 en scope RAISE-211...
         RAISE-211 creado en Jira. ADR-036 y ADR-037 escritos. Post publicado en Confluence.
         Commits: emilio@humansys.ai (Co-Authored-By: Aquiles, Fernando, Rai)
  ```

  **Lo que esto resuelve que nada más resuelve:**
  - Sesiones de diseño sin videollamada — el canal es suficiente
  - El equipo que no pudo estar en la sesión ve exactamente qué se decidió y por qué
  - El knowledge graph se construye colectivamente, no solo cuando Emilio trabaja solo con Rai
  - Los commits tienen autoría honesta — reflejan que fue trabajo de equipo

  **Prerequisitos técnicos:**
  - `TriggerAdapter` con `SlackTrigger` / `GoogleChatTrigger` — recibe mensajes del canal
  - `NotificationAdapter` — Rai publica al canal y a threads
  - **Hosted Rai agent loop** — el backend necesita mantener estado de sesión grupal entre mensajes (esta es la respuesta definitiva a la open question de ADR-035: "¿necesita el backend su propio agent loop?" — sí, para Group Sessions)
  - `KnowledgeGraphBackend` (RAISE-211/RAISE-209) — la sesión actualiza el grafo del equipo
  - **Group Session Protocol** — variante de ADR-024 para sesiones multi-participante
  - **Participant Profile Registry** — cada miembro del equipo tiene un perfil básico para calibración

  **Lo que es nuevo vs lo que ya está diseñado:**
  - `NotificationAdapter`, `TriggerAdapter` — ya en ADR-034, se extienden
  - Group Session Protocol — **nuevo**, variante de ADR-024
  - Per-participant calibration — **nuevo**, no existe en el modelo actual
  - Thread isolation (ELI5 sin contaminar el hilo principal) — **nuevo**, patrón de UX específico de chat
  - Channel-as-session-log — **nuevo**, invierte el modelo: el chat es el narrative, no un artefacto producido al final

  **Candidato a epic:** Post-RAISE-209 y post-TriggerAdapter. Requiere Hosted Rai con agent loop funcionando. Probablemente V3.1 o V4.

- [ ] **Rai en Slack/Google Chat — presencia conversacional del equipo** — (SES-224, 2026-02-20)
  - **Visión:** Rai participa en los canales del equipo como un miembro más. El equipo puede preguntarle cosas (`@rai ¿cuál es el estado de RAISE-211?`), recibe notificaciones automáticas (story cerrada, pattern aprendido, post del diario de sesiones), y responde en mensajes privados como si fuera `rai memory query` desde el terminal.
  - **Tres capas:**
    1. **`SlackTrigger` / `GoogleChatTrigger`** (variante de `TriggerAdapter`, ADR-034) — recibe mensajes entrantes, normaliza a `WorkflowTrigger`, despacha al skill o query correcto. Backend PRO recibe el webhook y orquesta.
    2. **`SlackNotificationAdapter` / `TeamsNotificationAdapter`** (variante de `NotificationAdapter`, ADR-034) — Rai publica proactivamente: post del diario al cerrar sesión, aviso cuando una story cierra, pattern nuevo aprendido. El canal recibe updates sin que nadie tenga que preguntar.
    3. **`SlackParser`** (variante de `GovernanceParser`, ADR-034) — las conversaciones del equipo en Slack alimentan el knowledge graph. Decisiones tomadas en un hilo, acuerdos informales, contexto que hoy se pierde, se convierten en nodes del grafo. Los humanos construyen el knowledge graph sin saberlo, solo conversando.
  - **Lo nuevo respecto a ADR-034:** La dirección inversa — conversaciones como fuente del grafo — no estaba contemplada. `SlackParser` es una implementación nueva de `GovernanceParser` que parsea mensajes de chat, no documentos. Requiere criterios de extracción (qué es decisión vs ruido).
  - **Prerequisitos:** RAISE-211 (TierContext + entry points), RAISE-209 (team memory + backend), y el diseño de TriggerAdapter (open question de ADR-035/036 sobre si el backend necesita agent loop).
  - **Por qué importa:** Cierra la brecha entre donde el equipo vive (Slack/Chat) y donde vive el knowledge graph (el repo). Hoy Rai solo aprende de lo que se documenta formalmente. Con esto aprende de cómo el equipo realmente piensa y trabaja.
  - **Riesgo:** Privacidad y señal/ruido — no todo lo que se dice en Slack debe ir al grafo. Requiere política de extracción y opt-in explícito por canal.
  - **Candidato a epic:** Post-RAISE-209, cuando team memory esté en producción y haya suficiente base para añadir canales de entrada conversacionales.

---

### S249.1 — Parking Lot (2026-02-21)

- [ ] **Deprecar `rai skill scaffold` → reemplazar con skill creator skill** — (S249.1, 2026-02-21)
  - **Context:** `scaffold.py` genera boilerplate SKILL.md con un template hardcoded. Es un generador estático que no aplica convenciones cross-cutting (e.g., platform agnosticism en ejemplos de código).
  - **Propuesta:** Reemplazar con un skill creator skill (conversacional, guiado) que genere skills más ricos: con depth heuristics, multi-language examples, Contract 4 output format, etc.
  - **Acción inmediata:** Marcar `rai skill scaffold` como deprecated en el CLI help text.
  - **Priority:** Baja — scaffold se usa poco, PAT-E-400 cubre el gap de platform agnosticism en sesiones

---

### SES-281 — Parking Lot (2026-02-25)

- [ ] **Repo clutter in MRs — non-code directories make reviews hard** — (SES-281, 2026-02-25)
  - **Context:** Technical user reviewing MRs reports difficulty finding actual code changes among `work/`, `.raise/`, `governance/` directory changes.
  - **Options:** `.gitattributes` to mark paths as generated/docs (GitHub collapses them in diff), separate research/work to a different branch or repo, CODEOWNERS to route non-code changes to different reviewers.
  - **Priority:** Medium — affects adoption experience for teams using RaiSE on real repos.

- [ ] **Adapt /rai-research skill to publish to Confluence** — (SES-281, 2026-02-25)
  - **Context:** Research currently produces local markdown files. Should also publish to Confluence for team visibility.
  - **What:** Add Step 6 to research skill: publish report + evidence catalog to Confluence under a Research parent page.
  - **Priority:** Medium — manual publishing works but adds friction.

- [ ] **Move all research to Confluence, evaluate if work/ stays in repo** — (SES-281, 2026-02-25)
  - **Context:** Related to repo clutter feedback. Research artifacts are valuable for team but inflate repo diffs.
  - **Decision needed:** Keep work/ in repo for git history? Move to Confluence only? Hybrid (summaries in repo, full content in Confluence)?
  - **Priority:** Medium — blocked by research-to-Confluence skill adaptation.

---

### RAISE-275 Epic Design — Parking Lot (2026-02-25)

- [ ] **RLS (Row-Level Security) for multi-tenant isolation** — (RAISE-275 design, 2026-02-25)
  - **Context:** Currently using WHERE clause filtering by org_id. RLS enforces isolation at DB level.
  - **When:** Enterprise tier with strict data isolation requirements.
  - **Priority:** Low — WHERE clause sufficient for single-org and early multi-org.

- [ ] **JWT/OAuth auth upgrade** — (RAISE-275 design, 2026-02-25)
  - **Context:** API key per org sufficient for POC. JWT adds per-user granularity and scopes.
  - **When:** User management needed (multiple users per org with different permissions).
  - **Priority:** Low — API key works for POC + first Pro customers.

- [ ] **Pattern promotion workflow (PERSONAL → PROJECT → ORG)** — (RAISE-275 design, 2026-02-25)
  - **Context:** Research defined the scope model. Promotion requires HITL validation and CLI commands.
  - **What:** `rai pattern promote` command, classification heuristics, architect validation for ORG scope.
  - **Priority:** Medium — needed for team intelligence, but not for initial backend.

- [ ] **Graph algorithms Phase 2: PPR, spreading activation** — (RAISE-275 design, 2026-02-25)
  - **Context:** Research validated PPR (~10 lines) and spreading activation (SA-RAG, 25-39% improvement).
  - **When:** After backend is stable and has enough data to benchmark.
  - **Priority:** Medium — enhances relevance but current keyword + BFS works.

- [ ] **pgAdmin in Docker Compose** — (RAISE-275 design, 2026-02-25)
  - **What:** Add pgAdmin service for visual DB inspection during development.
  - **Priority:** Low — nice-to-have, `psql` CLI sufficient.

- [ ] **Skill ↔ Jira backlog sync — skills drive Jira transitions automatically** — (RAISE-275 design, 2026-02-25)
  - **Context:** Los skills del lifecycle (epic-start, story-start, story-close, epic-close) ya saben en qué fase estamos. Jira debería reflejar eso automáticamente, no depender de que alguien se acuerde de mover el ticket.
  - **Mapping:** epic-start → In Progress, epic-plan → crea stories hijas, story-start → In Progress, story-close → Done, epic-close → Done.
  - **La "magia":** Esto convierte a los skills en el backlog manager — el equipo deja de mantener Jira manualmente. El workflow del skill ES el workflow de Jira. Fernando ve progreso real sin preguntar. El PM ve burndown sin perseguir developers.
  - **Alcance:** Una transición Jira al final de cada skill (no micro-updates). Leer workflow config de `.raise/jira.yaml` (ya existe). Graceful degradation si Jira no está configurado.
  - **Relación:** Evolución natural de los Jira MCP tools que ya usamos ad-hoc. Podría ser un hook (E248 architecture) en vez de código dentro de cada skill.
  - **Priority:** High — alto impacto en experiencia de equipo, bajo esfuerzo incremental (1 MCP call por skill).

- [ ] **Epic docs refresh gate — update brief/scope/design when decisions change** — (RAISE-275 design, 2026-02-25)
  - **Context:** Epic brief se escribe en epic-start, scope y design en epic-design, pero durante story-design e implementation se toman decisiones que invalidan esos documentos. Hoy no hay gate que los actualice.
  - **What:** Agregar paso en `/rai-story-close` o `/rai-epic-plan` que compare decisiones tomadas durante stories contra los docs de épica (brief, scope, design). Si hay drift, actualizar antes de cerrar.
  - **Scope:** Podría ser un step en story-close ("¿cambió alguna decisión de épica?") o un skill dedicado `/rai-epic-refresh`.
  - **Priority:** Medium — los docs de épica son el contrato del equipo, si driftan pierden valor.

---

### RAISE-275 Architecture Review — Parking Lot (2026-02-25)

- [ ] **rai-core domain expansion: Workflow engine with per-org extensibility** — (E275 arch review, 2026-02-25)
  - **Context:** Architecture review discovered that `rai-core` needs to be the shared RaiSE domain, not just a graph library. Work management (epic/story/task lifecycles) requires a workflow engine with customizable state machines.
  - **Requirements:**
    - Core defines schema base: WorkItemType, State, Transition, Gate
    - Core provides default RaiSE workflow (out of the box)
    - Per-org/repo override via config (`.raise/workflows/*.yaml` or similar)
    - Each stage = skill + quality gates
    - Versionado: upgrades never break custom workflows; migration path when breaking
  - **DDD grounding:** Currently workflow lives implicitly in skills (markdown) and `.raise/jira.yaml` (transition IDs). No explicit domain model in code.
  - **Priority:** High strategic — foundation for Pro/Enterprise. Separate epic after E275.

- [ ] **rai-core domain expansion: Extensible governance schema** — (E275 arch review, 2026-02-25)
  - **Context:** Kurigage dev (Sofi) gave Rai coding standards → placed in `/governance/` correctly, but no parser exists → won't enter the graph → Rai can't use them in queries or share with team.
  - **Requirements:**
    - Extensible artifact types beyond fixed `CoreArtifactType` enum
    - Generic parser (or parser plugin system) for custom governance docs
    - Custom artifact types shareable via server (whole team benefits)
    - Schema versionado + migrations (same pattern as workflows)
  - **DDD grounding:** `CoreArtifactType` is governance context vocabulary. Server receives translated `ConceptNode`, doesn't need parsing. But the SCHEMA of what types exist needs to be extensible and shareable.
  - **Priority:** High — directly impacts customer onboarding experience.

- [ ] **rai-core structure accommodates three domain axes** — (E275 arch review, 2026-02-25)
  - **Decision for S275.1:** `rai_core/` package structure should accommodate graph (E275), workflow (future), and governance schema (future) even though only graph is implemented now.
  - **Proposed structure:**
    ```
    rai_core/
    ├── graph/           # E275 — implemented
    ├── workflow/        # placeholder with docstring
    ├── governance/      # placeholder with docstring
    └── __init__.py
    ```
  - **Rationale:** Avoid refactoring when expanding core. "Sentar las bases."

*Created: 2026-01-31*
*Last reviewed: 2026-02-12*
*Last updated: 2026-04-03 (E1248: git-first session state)*

---

## Rai as Team Operating System ("Enterprise Computer") — 2026-04-03

**Origen:** E1248 design session — Emilio's vision for 3.0+.

**Vision:** Rai Server as the "computer" of the development team. Not just session tracking, but real-time awareness across all developers, repos, and workstreams:
- Knows where every developer is, what they're working on, blast radius of each change
- Learns from every session without being asked (kaizen as service, not ceremony)
- PRO developers connect and the server governs: config download, stack setup, state provision
- Developer doesn't track sessions — Rai observes, captures, prepares next session
- Can answer "where are we ALL right now?" with a real-time map

**Relationship:** RAISE-1229 (server state) is the infrastructure. This vision is the product direction that justifies it. E1248 (git-first protocols) provides the interface contracts.

**Promotion condition:** After E1248 validates protocol pattern in 2.4 and RAISE-1229 server infra is scoped.

**Prioridad:** Strategic — shapes 3.0 product direction.

---

## Neurosymbolic Memory Effectiveness — 2026-04-04

**Origen:** E1286 dogfood — D5/D7 decisions. LEARN records, PRIME, JIT, emit-work all write-only today. No consumer validates whether the graph/patterns improve agent decisions.

**Problem:** RaiSE has neurosymbolic memory infrastructure (graph, patterns, LEARN records) but no feedback loop to measure if it works:
- LEARN records: write-only, no chain read implemented, no aggregation
- Pattern votes: collected but never analyzed for pattern retirement/promotion
- Graph queries: no measurement of recall quality (relevant results vs noise)
- Calibration/telemetry: 5217 events, 0 consumers
- Gap signals: recorded per-skill but never aggregated across executions

**What's needed (post-3.0.0):**
1. **Measurement**: Does graph context improve agent decisions? A/B: skill execution with vs without PRIME context
2. **Feedback loop**: LEARN gaps → graph build priorities. Pattern votes → automatic retirement (Wilson score below threshold)
3. **Chain reads**: Downstream enrichment implemented in pipeline engine (not skill instructions)
4. **Observability**: Dashboard showing acceptance rate, gap rate, pattern utility trends over time
5. **LEARN as infrastructure**: Pipeline engine writes LEARN records deterministically (not agent instructions), ensuring 100% coverage

**Key insight (D7):** LEARN records have conceptual value as the measurement backbone for skill self-improvement, but they must be generated by infrastructure (pipeline engine), not by agent instructions. Agents confuse them with patterns, skip them, or produce incomplete records. The outer loop (MCE/MetaHarness) requires reliable measurement — reliability comes from determinism, not compliance.

**Dependencies:** E1065 pipeline engine (3.0.0), rai-agent arrival
**Promotion condition:** After pipeline engine can generate LEARN records deterministically per phase execution.
**Prioridad:** Strategic — validates the core thesis that neurosymbolic memory improves agent reliability.
