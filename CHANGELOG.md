# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Windows brownfield onboarding — C# + T-SQL discovery preview** (RAISE-17095) — regex-based T-SQL extractor covering 6 object types (tables, views, procedures, functions, triggers, user-defined types), GO-batch splitting, and encoding chain (utf-8-sig → utf-16 with CRLF normalization). `tree-sitter-c-sharp` declared as default dependency. `GrammarNotAvailableError` for fail-fast when a tree-sitter grammar is not installed.
- **Discovery scan honesty counters** (RAISE-17096) — `ScanResult.files_found` and `skipped_by_extension` surface in `rai discover scan` JSON/summary/human output and round-trip through `discover analyze`, so a directory of files with no registered extractor is no longer indistinguishable from an empty one.
- **IoT Smart Grid reference corpus** (RAISE-17099) — a synthetic mixed C#+SQL fixture covering all six T-SQL object kinds, the C# `Program`-class collision pair, and three encoding variants (UTF-8 BOM, UTF-16LE BOM, CRLF), plus a corpus-qualification suite bound to `expected.json`.
- **Support & lifecycle policy** (RAISE-17074) — `docs/support-policy.md` with EOL dates, Sentry release tagging via `SENTRY_RELEASE` env var, and 72-hour post-release watch window procedure.
- **Multi-release-line support** (RAISE-17066) — `branches.release_lines[]` in `.raise/manifest.yaml` with `status: active | bugfix-only | sunset`; deterministic target resolution via `rai worktree resolve-base`; `pipeline_start` integration with env override.
- **Forward-merge propagation** (RAISE-17076) — `rai forward-merge` command for deterministic oldest→newest propagation chain with conflict HITL.
- **CI parameterization** (RAISE-17082) — `DEPLOY_RELEASE_LINE` variable replaces 48 hardcoded `release/3.1.0` literals in `.gitlab-ci.yml`; parity test ensures CI matches manifest.
- **Channel guards for GitHub Actions** (RAISE-17079) — `check-tag-provenance.sh` verifies orphan commit, `Source:` trailer, and version parity on every tag push; `prerelease` output propagated to both `release.yml` and `build.yml`.
- **Post-publish verification** (RAISE-17080) — `verify-published.sh` confirms PyPI wheel+sdist availability and GitHub Release asset completeness (17 assets) within the same CI run.
- **Pre-release binary validation** (RAISE-16952) — `check-release-binaries.sh` dispatches an ephemeral filtered snapshot to the GitHub mirror, runs the binary build workflow, and cleans up — catches build failures before the permanent sync.
- **Windows binary CI parity** (RAISE-16975) — Windows runner in GitLab CI builds and publishes binaries to R2, matching the GitHub Actions matrix.
- **Workflow model from backlog.yaml** (RAISE-16981) — workflow states and transitions declaratively defined in `.raise/backlog.yaml` instead of hardcoded in adapter logic.
- **Engine-owned state** (E16982) — pipeline motor as sole state writer; standalone skills governed by the engine.

### Changed

- **`tree-sitter-c-sharp` is now a default dependency** (RAISE-17096) — declared explicitly in raise-cli and raise-core's `scanning` group instead of relying on it being installed transitively via `tree-sitter-language-pack`; the `csharp` extra is now an empty backwards-compat alias.
- **`rai discover scan` exits 1 when files were found but none could be processed** (RAISE-17096) — previously always exited 0, even when every candidate file had no extractor or failed to parse. Partial per-file errors and empty directories still exit 0.
- **Installer defaults to stable channel** (RAISE-15670) — `install.sh` and `install.ps1` now default to the stable PyPI channel instead of the beta GitLab registry.
- **QA pipeline triggered by tags** (RAISE-17009) — CI QA trigger migrated from branch push to `test-*` tag pattern.

### Fixed

- **`rai init` dry-run message now guides 2.x/3.0 upgraders** (RAISE-17159) — ⚠️ **Breaking change (3.1.0):** `rai init` is dry-run by default in 3.1.0; the "No files written" message now includes a pointer to `docs/guides/upgrading-to-3.1.0.md` so users upgrading from earlier versions are not left without guidance.
- **C# symbol id collisions across sibling project directories** (RAISE-17096) — `ConsoleClient/Program.cs` and `WinFormsClient/Program.cs` (and any `.cs`/`.sql` files sharing a name in different directories, including `src/`-anchored layouts) now mint distinct `sym-*` ids instead of silently colliding during graph dedup.
- **Symbol ID collision across namespaces** (RAISE-17098) — file discriminator includes parent directory for same-name files in sibling directories, preventing silent dedup drops.
- **Diagram `source_commit` merge conflicts** (RAISE-17084) — removed `source_commit` field from ground-truth manifests, eliminating guaranteed merge conflicts in stacked branches.
- **Long paths and unlistable directories no longer crash discovery** (RAISE-17099) — a file or directory whose path is at or beyond Windows `MAX_PATH` (260 chars) now produces a diagnostic naming `MAX_PATH` and the remedy in `ScanResult.errors` instead of a raw `[WinError 3]` traceback.
- **`install.ps1` unblocks downloaded archives after checksum verification** (RAISE-17099) — removes the Windows mark-of-the-web before extraction, so SmartScreen no longer blocks the installed binaries on first launch.
- **Backlog sync pagination** (RAISE-16899) — Cloud `enhanced_jql` pagination fixed; `isLast` default broke page-walk past the first page.
- **Backlog sync stage 3 silent failure** (RAISE-16996) — `remote_pm` passed correctly; `ValueError` now exits 1 instead of silently succeeding.
- **Story points surfaced in backlog** (RAISE-15072) — `rai backlog get/search` now includes story points in output.
- **httpx token leak in logs** (RAISE-15538) — httpx INFO logger suppressed to prevent bot token leakage.
- **ONNX model cache integrity** (RAISE-17047, RAISE-17052) — recall-gate CI job no longer `allow_failure`; model integrity validated on cache hit; download hardened.
- **SQLite write lock rollback** (RAISE-15442) — verification tests added for write-lock rollback scenarios.
- **Pipeline start stale cache** (RAISE-16965) — revalidates against remote when local cache would reject pipeline start.
- **Pipeline recovery hint** (RAISE-16999) — `pipeline start` prints `recovery_hint` from rejected guards.
- **Pipeline advance 422** (RAISE-17049) — sanitizes `project_id` and catches `HTTPStatusError` in pipeline stores.
- **Pipeline close persistence** (RAISE-16698) — `SqliteRunStore` regression guard for story close phase.
- **Parallel close integrity** (RAISE-17037) — drops stale pre-V72 unique indexes; guards `upsert_jira_mapping` against parallel `jira_key` conflicts.
- **Composite phase instruction** (RAISE-17006) — dispatches sub-pipeline correctly for composite phases.
- **Upsert batch abort** (RAISE-16997) — isolates upsert errors per item instead of aborting entire batch.
- **Gate preflight** (RAISE-17041) — detects missing executables before full-gate run.
- **Gate tests scope fallback** (RAISE-16928) — uses manifest `test_command` when scoped test path is unavailable.
- **Gate artifacts regex fail-open** (RAISE-16947) — `GovernanceArtifactsGate` now fails closed instead of silently passing on regex mismatch.
- **Gate coverage non-Python** (RAISE-16929) — skips `gate-coverage` on non-Python projects.
- **Governance trail scope range fallback** (RAISE-16748) — scopes to source branch name when commit range is unavailable.
- **Provenance block truncation** (RAISE-16904) — prepends governance block to survive CI log truncation.
- **Cartridge filesystem to DB** (RAISE-16901) — backlog cartridge state moved from filesystem to DB.
- **Unbounded cartridge embedding** (RAISE-14950) — `RAISE_CARTRIDGE_EMBED` kill-switch added to prevent runaway embedding.
- **Extractor YAML error swallow** (RAISE-16153) — raises `ExtractorConfigError` on YAML syntax errors instead of silently continuing.
- **`ar-skip-log.jsonl` merge conflicts** (RAISE-17026) — file removed; signal telemetry is the audit trail.
- **TUI MCP pipeline foreign venv** (RAISE-17027) — `shutil.which` results from foreign project venvs are skipped.
- **Auto-upgrade opt-out** (RAISE-16267) — `--no-auto-upgrade` flag added to `rai session start`.
- **Work item upsert divergence** (RAISE-16938, RAISE-16845) — converges `work_items` rows and completes backlog CRUD graph refresh; ghost rows handled in `WorkItemStore.create()`.
- **Node.js worktree deps** (RAISE-16717) — installs Node.js dependencies during worktree provisioning.
- **MR create gate order** (RAISE-16759) — adds STOP clause to bugfix-close on MR creation failure.
- **Fleet subagent MR bypass** (RAISE-16936) — MR-via-skill rule added to fleet subagent essential rules.
- 12 additional bug fixes across patterns migration (RAISE-16240), graph baseline bootstrap (RAISE-17040), epic parser tables (RAISE-17036), backlog mirror freshness (RAISE-16998), skill sync worktree (RAISE-16828), key-gen status category (RAISE-16968), onboard `--apply` (RAISE-16962), update-fields validation (RAISE-16949), filesystem adapter status (RAISE-16941), backlog create issue-type (RAISE-16893), pipeline session-id (RAISE-16892), and bugfix PIR bypass (RAISE-16615).

## [3.1.0] - 2026-09-01

### Added

- **Graph staleness visibility in session open** (RAISE-16049, E15983) — `rai session open` now reports graph age and commits-since-build; manifest thresholds drive warn/stale status. Doctor graph checks delegate to shared freshness core.
- **Multi-provider agent routing** (E16110) — `provider_map` + `provider_models.yaml` define available LLM providers. KimiRuntime and CodexRuntime adapters join ClaudeRuntime. `RAISE_AGENT_RUNTIME` env var selects runtime at startup.
- **Pattern embedding extension** (RAISE-16087) — graph nodes embedded at build time; ADR ingestion via `graph.document_sources` manifest key; scorer discovery fuses graph-node embeddings.
- **Cartridge pipeline completeness** (E15985) — `cartridge extract --emit-work` incremental mode; content-keyed work orders prevent positional mispairing; relationship schema validation fails loud on malformation.
- **Worktree lifecycle** (`rai worktree register/list/close`) — multi-worktree development with session isolation and propagation. New in 3.1 (E14697).
- **Full cross-harness parity** — Codex CLI and Kimi now expose the same 36 MCP tools as Claude Code. Codex gains PostToolUse staleness detection (RAISE-14908).
- **Mechanical scope guard** (RAISE-15618) — `rai discover scan` output is now scoped to the current checkout; cross-worktree symbol leakage is closed.
- **Admin UX redesign** (RAISE-16479 epic + story cluster RAISE-16780–16784, RAISE-16886, RAISE-16598.x, RAISE-16902.1, RAISE-16868, RAISE-16869, RAISE-16763) — project overview foundation, sidebar reorganization, project-selector context switch, artifacts project portal, breadcrumbs wayfinding, governance tab redesign, cost-tab per-project/per-story-point views, graph HUD tab, KPI card tooltips, pipelines load-more, and pipeline date-format filter.
- **Cockpit TUI redesign** (RAISE-16700) — Workspace-First Cockpit with a new "Copper & Patina" terminal design system.
- **DDD tactical-modeling suite** (RAISE-16526 epic + s16730-s16738, s16760-s16761, s16787-s16791, s16799-s16804, s16850-s16851, s16915-s16918) — bounded-context assignment, `rai ddd discover/refine/assign-bcs` and `rai ddd type` CLI commands, tactical type-schema heuristics, domain-model ratification gate, and confidence recalibration.
- **Graph structured filters** (RAISE-16887, RAISE-16940) — `--filter` predicates and `--depth` edge expansion on `rai graph query`.
- **Graph lifecycle GC** (RAISE-16879) — stale graph node/edge garbage collection.
- **Backlog knowledge-graph initiative** (RAISE-16394) — backlog items surface as first-class nodes in the knowledge graph.
- **GitLab tester distribution** (RAISE-16536 epic, RAISE-16632) — ONNX tester binary packaged and distributed via GitLab.
- **HTML artifact publishing platform** (RAISE-16616, RAISE-16657, RAISE-16660, RAISE-16870) — `rai docs publish` gains a dual Markdown/HTML `DocsTarget`, idempotent republish, and publish-from-fresh-connect.
- **Container agent orchestration** (RAISE-16568) — gate API and admin UI for running agents in containers.

### Changed

- **Schema: CLI SQLite V31→V79** — migrations run automatically the first time any command opens the database. Back up `~/.rai/raise.db` before upgrading; the migration is forward-only.
- **Session continuity is now scoped to worktree + agent** (E15456, ADR-2026-07-27) — a session only inherits continuity from the last session closed in the *same worktree* (main checkout donates only to main), with the agent session id as a tie-breaker within the worktree. The previous project-wide "last closed session" fallback was **removed** from the donor chain, `rai session context`, and `rai session measure`; history, ledger auto-surface, and recent-sessions reads default to the caller's scope.
- **Behavior change for main-checkout users:** session history written before schema V67 carries no worktree/agent attribution and is now excluded from continuity. Worst case is a clean start (no inherited context) instead of inheriting the last project-wide session.
- Session ids gain an entropy suffix to prevent minute-collision between concurrent sessions (RAISE-15482).
- `sentence-transformers` declared as explicit dependency; missing-embeddings now surfaced as user-visible warning with `KEYWORD_SEARCH_FORCED` fallback (RAISE-15987).
- **Transactional upgrade/migration recovery** (RAISE-15659) — schema migrations recover transactionally instead of leaving the database in a partially-migrated state.
- **Brownfield onboarding** (RAISE-15707) — `rai init` hardened for adoption on existing, non-greenfield codebases.
- **Storage reliability prerequisites** (RAISE-16633) — storage-layer hardening ahead of further reliability work.
- **Mirror-push security guards now fail closed** (RAISE-16589, RAISE-16590, RAISE-16591, RAISE-16664) — public-mirror publication sanitizes Windows paths, enforces the agent-governance mirror invariant, and treats a missing or failing gitleaks scan as a hard failure instead of warn-and-continue.
- **MR governance hardened** (RAISE-16770, RAISE-16826, RAISE-16936) — pre-MR admission and `rai mr create` gating reject thin/incomplete admission evidence.

### Fixed

- **Doc-loader node_id and truncation** (E15983) — 5 MRs merged fixing document_sources, graph staleness, and node-id generation across the doc-loader subsystem.
- **Pattern reachability** (E15984) — semantic search reachability restored; empty-project-id guard; module-id off-by-one for TS/JS flat layout (RAISE-16027); package-qualified module ids prevent cross-package collision (RAISE-16033).
- **Cartridge pipeline** (E15985) — 5 bugfixes across sidecar denylist reconciliation, work-order cleanup glob, relationship schema validation, and content-key deduplication.
- **SQLite WAL write-lock** (RAISE-15605) — orphaned `BEGIN` transactions from failed schema migrations blocked all writers for the life of the process. Fixed with `with conn:` in `create_all()` and 8 write paths hardened.
- **Graph scoped by checkout** (RAISE-15607) — KG queries no longer return symbols from other worktrees. `checkout_root` + `validate_asserted_root()` enforce per-checkout isolation.
- **Tier display false evidence** (RAISE-15610) — `rai` no longer prints a tier that contradicts ADR-082.
- **3 CI drift guards** (RAISE-15608) — architectural drift now fails CI instead of warning-and-continue.
- **Windows: bare `rai` no longer crashes** (RAISE-15650) — the cockpit imported the Unix-only `termios`/`tty` at module scope; it now detects the missing raw-input support and prints the available commands instead.
- **Windows: `rai gate check` no longer crashes on startup** (RAISE-15653) — the worker-budget ledger imported the Unix-only `fcntl` at module scope; it now selects a locking backend at runtime (`msvcrt` on Windows).
- **Install scripts can actually install the beta** (RAISE-15651, RAISE-15670) — the published installers default to the GitLab pre-release registry, keep a project's existing `.venv` untouched, and document how flags survive `curl | bash`.
- **`rai cartridge` reports live node counts** (RAISE-15615) — honours checkout-wins visibility instead of counting only one provenance.
- **`rai init --force` no longer wipes cartridge content** (RAISE-15655) — it overwrites only what the bundle owns and leaves hand-curated corpus/eval/extractor content in place.
- **deploy:docs actually deploys** (RAISE-15654) — the CI job now runs the deploy with Node 22 and a pinned wrangler.
- **`rai self-update` no longer destroys the local install** (RAISE-16741).
- **Pipeline and session resume no longer lose state** (RAISE-16907, RAISE-16908) — `rai session open` and story-open resume paths preserve tokens and progress across interrupted runs.
- 111 additional bugs resolved since 3.1.0rc2 across doc-loader, pattern query, cartridge pipeline, agent routing, admin UX, DDD tooling, graph tooling, and CI/governance subsystems — unique issue keys on `bug/`/`bugfix/` branches in the first-parent history of `release/3.1.0` since `v3.1.0rc2`, counted at the cut (git-derived; replaces a previously unreproducible count). Recompute at the GA merge if further bug branches land.

## [3.1.0a1] - 2026-05-28

### Added

- Multi-dev foundation: team model, `rai connect` device auth, governance sync, pattern promotion lifecycle, activity feed (E5477, E5593, E5596, E5604, E5708)
- Zero-friction onboarding: `rai init --server`, `rai repo register`, `rai connect <org>`, journey-aligned checklist with auto-detection (E6030, E6097, E6098)
- Knowledge Graph auto-update on story/epic close with staleness detection in `rai doctor` (E6173, ADR-085/086)
- KG server sync: `DualWriteBackend`, federated cross-repo queries via `rai graph query --cross-repo` (E6174)
- Domain Cartridges: `rai cartridge init/validate/pack/install/uninstall` with JSON Schema spec (E5875, ADR-083)
- Console HUD (`rai hud`): TUI with Missions/Sessions/Pipeline/Events/Insights tabs (E2724, E3128)
- Rai for Rovo: 5 Forge Actions connecting Rovo to raise-server (E5399)
- MCP-primary: 100% skill migration to MCP-first, 3 new tools (E6003, ADR-084)
- Drift prevention system: 8 CI guards, mandatory architecture-review gate (E2100, E2313)
- Auto-upgrade on session start: syncs skills, patterns (55→60 BASE), methodology (v1→v2) on version mismatch (E6100/S6100.5)
- Backlog attachments: `rai backlog attach` and `rai backlog get-attachments` (S2503.7)
- `rai project create/link-repo/list` CLI commands (RAISE-6178, RAISE-6179)
- `/rai-onboard-repo` skill for guided repository onboarding (RAISE-6219)

### Changed

- SQLite is canonical graph backend; Kuzu optional at runtime (E5664)
- Graph session context: 3.8s → ~200ms via recursive CTEs and lazy loading (E4513)
- Environment variable prefix: `RAI_*` → `RAISE_*` (**breaking**)
- `atlassian-python-api` and `kuzu` promoted to default dependencies
- Jira REST API upgraded to v3 Cloud standard (E2503)
- Branch model: development branch → `release/3.1.0` (E6100/S6100.1)
- Product line canonicalized: one product, OSS/Community/Pro tiers (ADR-082)
- Schema: CLI SQLite V1→V31, Server Alembic 011→027

### Fixed

- 86 bugs resolved across 13 subsystems (10 S1-High, 67 S2-Medium, 10 S3-Low)
- See `work/release/3.1.0a1-alpha-notes.md` for complete bug list

## [3.0.0] - 2026-05-04

### Changed

- Pre-release 3.0.0a3: git-first config cascade (RAISE-2025), MCP bridge foundation (E1962)

## [2.3.0] - 2026-03-30

### Added

- Session identity model — deterministic session IDs per developer+repo using timestamp-based format `S-{prefix}-{YYMMDD}-{HHMM}`, Pydantic prefix registry with collision detection, per-project active pointer (E654, RAISE-654)
- CLI extension mechanism via entry points — `ExtensionInfo` discovery, collision and duplicate protection, wired into main CLI (RAISE-594)
- `rai doctor` adapter availability diagnostics (RAISE-614, S613.1)

### Changed

- Session data moved from global `~/.rai/` tracking to per-project `.raise/rai/personal/` directory (E654) — **breaking** for tools that read `developer.yaml` active session fields
- Pattern add default scope changed from `personal` to `project` (RAISE-608)

### Fixed

- CLAUDE.local.md references removed from skills_base close skills (RAISE-635)
- Session-start context loss — load session state before migration so previous state is preserved (RAISE-566)
- `promote_unreleased` fails when Unreleased is last section in changelog — add `\Z` to regex (RAISE-547)
- Unicode symbols crash on Windows CP1252 terminals — add symbols module with fallbacks (RAISE-554)
- C# scanner not extracting constructor dependencies — pass `depends_on` through `build_hierarchy` (RAISE-227)
- `rai init` ide.type not syncing with `agents.types[0]` (RAISE-218)
- CI container missing git — add to `apt-get install` (RAISE-570)
- Regex precedence/grouping fixes in ADR and changelog parsers (RAISE-589)
- Story-plan skill enforces project-wide verification scope (RAISE-572)
- Doctor callback cognitive complexity reduced from 47 to ~7 via extract refactoring (RAISE-598)
- SonarQube code smells resolved: S1192, S6019, S1172, S7503, S5713, S7632, S125, S5754 (RAISE-541)

### Security

- authlib 1.6.8 → 1.6.9 — 3 CVEs patched (RAISE-574)
- PyJWT ≥ 2.12.0 — critical `crit` header bypass, CVE-2026-32597 (RAISE-575)
- astro/cloudflare/undici dependencies upgraded — 9 Snyk CVEs in docs site (RAISE-576)

## [2.2.3] - 2026-03-11

Initial open-source release. RaiSE Framework v2 — a lean methodology and deterministic
toolkit for reliable AI-assisted software engineering.

### Highlights

- **37 skills** covering the full SDLC: epic, story, discovery, implementation, review, debug, research
- **Knowledge graph** for project context, patterns, and cross-session memory
- **Multi-language discovery**: Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte
- **Governance as code**: constitution, guardrails, ADRs, gates — all versioned in Git
- **Adapter plugin system**: extensible via entry points (filesystem built-in, Jira/Confluence via raise-pro)
- **Doctor diagnostics**: `rai doctor` with `--fix` auto-remediation
- **Documentation site**: docs.raiseframework.ai (EN + ES)

### CLI Commands

72 subcommands across 17 groups: `init`, `session`, `graph`, `pattern`, `signal`,
`backlog`, `skill`, `discover`, `adapter`, `mcp`, `gate`, `doctor`, `docs`,
`artifact`, `release`, `info`, `profile`.

### Framework

- 5 work cycles: solution, project, feature, setup, improve
- 3-layer architecture: Context (wisdom), Kata (practice), Skill (action)
- Jidoka (stop-and-fix) verification at every step
- Skill sets: distributable, customizable skill collections per team

### Pro/Community Boundary (E478)

- **Separated pro adapters** into `packages/raise-pro/` workspace package
- **Removed 6 pro-only dependencies** from community install (atlassian-python-api, authlib, cryptography, requests, urllib3, certifi)
- **Clean entry points**: Jira/Confluence adapters register only when raise-pro is installed
- **Removed hardcoded Jira CLI logic** from community package (-207 lines)
- **Gitignored adapter configs** (.raise/jira.yaml, .raise/confluence.yaml) to prevent PII leaks

[Unreleased]: https://github.com/humansys/raise/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/humansys/raise/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/humansys/raise/releases/tag/v2.2.3
