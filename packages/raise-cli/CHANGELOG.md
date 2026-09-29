# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.1.3] - 2026-09-29

### Added

- **Epic bugfix-pipeline reclassification** (RAISE-17655) — epics carrying the `rai-bugfix-epic` label are automatically classified as bugfix pipelines; no manual override needed. [docs-debt: docs/cli/ pipeline classification by label not yet documented]
- **Epic pipeline branch resolution** (RAISE-17944) — `pipeline_start` resolves epic pipeline via `epic/{id}/pipeline` branch pattern when no explicit pipeline is configured.
- **`revert-scope` advisory gate** (RAISE-17599) — new gate wired into `rai mr create` admission checks that flags MRs reverting more than their declared scope. Gate is advisory (non-blocking). [docs-debt: docs/cli/gate.md#revert-scope pending]
- **`env-bash-sandbox` doctor check** (RAISE-17962) — `rai doctor` now checks whether the bash sandbox is correctly configured; includes AppArmor runbook for hardened environments. [docs-debt: docs/cli/doctor.md check list update pending]
- **MCP credential-exposure guardian** (RAISE-17965) — standalone guardian check closes false-negative gaps in MCP cleartext credential detection.
- **BC node id helpers** (RAISE-17980) — `bc_node_id`, `is_bc_node_id`, and `bc_name_from_node_id` helpers added to `raise-core` for consistent bounded-context node addressing.
- **DDD tactical prompts: global neighbor index** (RAISE-17982) — tactical prompts now include a global neighbor index and bounded-context context, improving classification accuracy.
- **Epic parent guard in `pipeline_start`** (RAISE-18076) — `pipeline_start` validates that a story's epic parent exists and is active before allowing pipeline execution.

### Fixed

- **Gate range base resolution** (RAISE-18328) — stale `merge_target` in worktree registry falls back to manifest; star-import guard catches any stale reference.
- **`rai doctor` zombie reconciliation** (RAISE-17631, RAISE-17629) — closed zombie sessions reconciled on startup; run list filtered by project to prevent cross-project contamination.
- **`rai doctor` MCP server check** (RAISE-17628) — MCP availability check uses process probe instead of port scan, eliminating false negatives on non-standard ports.
- **`rai doctor` lint corrections** (RAISE-17335) — C901 complexity and SIM102 nested-if violations resolved in doctor runner.
- **`rai ledger show` cross-session fallback** (RAISE-13750) — ledger entries from prior sessions surfaced when current session has no entries.
- **`rai release publish --dry-run`** (RAISE-17630) — dry-run correctly short-circuits TTY validation for `--force`, preventing false blocking in CI.
- **Public mirror dependabot guard** (RAISE-18334) — dependabot pip branches capped to prevent mirror churn; `dependabot/*` refs only synced when author-verified.
- **`rai gate types` vacuous scope** (RAISE-18295) — `--scope ""` now fails loud with a clear error instead of silently passing; test scopes routed to advisory profile.
- **`governance-trail-ci` gate base resolution** (RAISE-18299) — base SHA resolved via worktree registry first, then manifest default; TARGET_REF pinned to synced value in `rai mr create`.
- **Backlog cartridge `items.json` untracked** (RAISE-18276) — regenerable `items.json` removed from git tracking to prevent spurious hygiene failures.
- **`close-sync` merge target resolution** (RAISE-18300) — close-sync gate resolves target from worktree registry before falling back to manifest.
- **Graph backfill timeout** (RAISE-18255) — `changed_paths` batched into a single subprocess call per backfill run, eliminating subprocess-per-file timeout.
- **Graph fixture HOME isolation** (RAISE-18284) — `_local_repo_graph` fixture uses its own isolated `HOME`/`RAI_HOME`; plain helper dispatch avoids `__wrapped__` recursion.
- **Strict-drift CI baseline** (RAISE-16490) — CAND-10 drift baseline fingerprint stabilized; 5 justified violations baselined to stop recurring false failures.
- **CI `main` ref fetch** (RAISE-17569) — `test:xdist-safety-full` uses forced refspec `refs/heads/main:refs/remotes/origin/main` instead of bare fetch, ensuring `origin/main` is up-to-date.
- **Pipeline `evaluate_when` fail-open** (RAISE-18252) — `evaluate_when` now fails loud on evaluation errors instead of fail-open; sub-pipeline rejection path covered.
- **API key leak in error tracebacks** (RAISE-18038) — unhandled exceptions caught safely before they reach the error output stream; API key no longer visible in tracebacks.
- **`pytest-timeout` in CI** (RAISE-17792) — timeout guard backported to `test:raise-cli-full` CI job to prevent hung runners.
- **`Path.home()` isolation in tests** (RAISE-17974) — `Path.home()` and `HOME` env var globally isolated in all pytest tests; HOME propagated correctly to subprocesses.
- **Backlog node resolution** (RAISE-17986) — `get_node_by_id` resolves nodes by bare Jira key; falls back to `jira_key` metadata for pre-rename cartridges; `repo_id` validated at schema level.
- **Hook script path validation** (RAISE-17964) — hook script paths validated on disk at startup; `$VAR`/`~` path conventions honored without false `ERROR` logs.
- **Bash-sandbox doctor check** (RAISE-17962) — R1–R5 QR findings fixed; accepted posture and AppArmor runbook documented.
- **Forward-merge branch discovery in CI** (RAISE-18004) — resumed forward-merge branch materialized via remote-tracking ref; works in ephemeral CI runners without a local branch.
- **Hook command POSIX path on Windows** (RAISE-18085) — `_HOOK_COMMAND_WINDOWS` now uses POSIX paths, fixing hook execution on Windows.
- **`backlog update -F` string coercion** (RAISE-17094) — bare string values for `fixVersions` and `labels` coerced to list when passed via `-F`.
- **`WorkflowConfig` YAML serialization** (RAISE-17375) — models serialized to plain dicts before `yaml.dump`; bind-site crash on missing key fixed.
- **Worktree refresh branch assertion** (RAISE-15572) — branch checked before ff-only merge in `maybe_refresh_dev_worktree` to prevent silent wrong-branch merges.
- **External repo worktree error message** (RAISE-17148) — specific, actionable message when referenced worktree is missing in an external repo context.
- **`create_branch` base honesty** (RAISE-18075) — `create_branch` reports the real `base_ref` and `base_sha` used, not a default placeholder.
- **`rai docs write` companion file** (RAISE-17804) — `.md` companion derived and written automatically alongside the primary artifact.
- **`rai docs write` format validation** (RAISE-17888) — `--format` flag validated; HTML companion clobber guarded.
- **Pre-review prompt framing** (RAISE-17751) — pre-review prompt now includes reviewer framing to improve adversarial review quality.
- **Self-update on Windows** (RAISE-17814) — `.zip` bundles supported; archive filename derived from artifact URL; swap hardened with grace period and retry loop.
- **Skills catalog stale** (RAISE-17793) — skills catalog regenerated to reflect current skill set.
- **Missing backlog items human-readable error** (RAISE-17781) — missing backlog items produce a clear, human-readable error instead of a raw `KeyError`.
- **Spanish CLI docs mirror** (RAISE-17803) — `docs/es/cli/scm/pre-review.md` added; page declared in `not_in_nav` to prevent broken nav links.
- **Batch graph cartridge GLOB** (RAISE-17924) — `GLOB` used instead of `LIKE` in cartridge node deletion; lowercase `bc-*` nodes no longer deleted accidentally.
- **Spike journal docs adapter** (RAISE-17916) — `rai-spike-journal` publishes via the docs adapter instead of direct MCP tool calls.
- **Manifest `fix_versions` tied to publish** (RAISE-17925) — `fix_versions` in manifest updated atomically with `rai release publish`.
- **Workflow point resolution aliases** (RAISE-17917) — `status_mapping` role-key aliases now honored in workflow point resolution.
- **`resolve_dev_branch` manifest result** (RAISE-18074) — migrated to `ManifestLoadResult`; fail-open when `origin` is not configured.
- **`backlog update --fix-version ""`** (RAISE-18033) — empty string treated as clear operation (removes all fix versions) instead of no-op.
- **Graph node hash docstring** (RAISE-17980) — truthful docstring; hook timeout corrected to 180 s.

## [3.1.0rc5] - 2026-08-24

### Added

- **raise-admin project portal** (RAISE-16479) — vertical-slice project portal with project
  overview (stats, recent pipelines, activity), pipelines tab, activity tab, and navigation
  hardening with sub-nav and per-route error boundaries.
- **Server project-scoped queries** (RAISE-16475) — `project_id` added to pipeline runs schema
  (migration), project stats endpoint, and activity-feed project filter.

### Changed

- **CLI layer model: hook_bus to foundation tier** (RAISE-16455) — `hook_bus` package extracted
  from `hooks` (T2) to T5 foundation; 3 enrollment waivers removed. `MAX_WAIVERS` ratchet: 20→17.
- **CLI layer model: embeddings to foundation tier** (RAISE-16457) — `OnnxEmbeddingProvider`
  relocated from `cartridges` (T3) to new `embeddings` (T5); graph→cartridges import eliminated.
  `MAX_WAIVERS` ratchet: 21→20.
- **CLI layer model: 3 XS cross-layer waivers removed** (RAISE-16509) — `MAX_WAIVERS` ratchet:
  17→14. `rai-admin` frontend migrated to TanStack Query (RAISE-16476); `projectsBus` removed.
- **DDD ontological alignment** (RAISE-16484) — spike documenting domain-driven design concept
  mapping to the RaiSE governance model; drift prevention via ontological coherence.

### Fixed

- **Cockpit worktree delete safety** (RAISE-16521) — `_check_delete_safety`
  passed `--not=<ref>` as a single argv token, which git rejects; the non-zero
  exit was swallowed so `unmerged_commits` always reported 0 silently. The TUI
  `x` (delete worktree) gate could show SAFE/RISKY incorrectly. Fix: split into
  `["--not", ref]` two-token form. Regression test added.

## [3.1.0rc5] - 2026-08-23

### Added

- **Developer portal** (RAISE-16382) — static HTML portal generated from the repo: design system
  with CSS tokens and stamped navigation; 184 ADRs rendered as navigable decision pages; patterns
  how-to guide and curated showcase; 5 evergreen onboarding pages; full-text search index with
  CI freshness gate.

### Changed

- `story` backlog item type reclassified to `work_item` at T2 in the pipeline
  (RAISE-16462). `resolve_dev_branch` extracted to `project_config` for reuse.
- Mermaid diagram generator now sanitizes reserved keywords in node IDs to prevent
  parse failures in diagram fidelity gates (RAISE-16419, RAISE-16462).

### Fixed

- **httpx2 migration** (RAISE-16391) — `raise-server` tests migrated from the deprecated
  `client.cookies` assignment API to per-request cookie dicts, eliminating `DeprecationWarning`
  noise in the test output.
- **AsyncMock coroutine warnings** (RAISE-16390) — `raise-server` test suite no longer emits
  `RuntimeWarning: coroutine 'X' was never awaited` from improperly mocked async methods.
- **SQLAlchemy 2.0 row API** (RAISE-16392) — replaced deprecated `tuple(row)` with
  `row.tuple()` for SQLAlchemy 2.x compatibility.
- **Windows: `pid_alive()` broadcast signal** (RAISE-16347) — `os.kill(pid, 0)` on Windows
  sends CTRL_C to the entire process group; replaced with `OpenProcess` check.
- **CI diagram fidelity gate** (RAISE-16419) — `gate-diagram-fidelity-admin` restored after
  Mermaid reserved-keyword failures broke the gate for `rai-agent` diagrams.

## [3.1.0rc2] - 2026-08-05

### Fixed

- `rai init --force` no longer destroys cartridge content. It cleared each
  cartridge directory before copying, but the bundle ships only
  `CARTRIDGE.yaml` and `instances/` — so hand-curated `corpus/`, evaluation
  `eval/` qrels and `extractors/` configs were deleted permanently, without a
  backup or a prompt. `--force` now overwrites what the bundle owns and leaves
  everything else in place (RAISE-15655).

## [3.1.0b2] - 2026-07-30

### Fixed

- Windows: bare `rai` no longer crashes on startup. The cockpit imported the
  Unix-only `termios` and `tty` at module scope, so the command died with
  `ModuleNotFoundError` before printing anything. It now detects the missing
  raw-input support and prints the available commands instead (RAISE-15650).
- Windows: `rai gate check` no longer crashes before running a single gate.
  The worker-budget ledger imported the Unix-only `fcntl` at module scope; it
  now selects a locking backend at runtime and uses `msvcrt` on Windows, so
  gate checking works rather than merely starting (RAISE-15653).
- `rai cartridge` reports live node counts and honours checkout-wins
  visibility, instead of counting only one provenance (RAISE-15615).
- The published install scripts can now actually install a beta: they pass the
  GitLab pre-release index, keep a project's existing `.venv` untouched by
  installing into `.raise-venv`, and document that `curl | bash` needs
  `bash -s --` (and `irm | iex` cannot receive flags at all) for the version
  flag to survive (RAISE-15651, RAISE-15642).

## [3.1.0b1] - 2026-07-30

### Added

- Codex plugin distribution for initialized and upgraded projects, including a
  local marketplace manifest, the `raise-governance` plugin surface, and its
  RaiSE skills.
- Stateless workspace MCP execution with explicit project/worktree context and
  coherent harness configuration.

### Changed

- Release governance now enforces prerequisite ordering, bounded suppression
  growth, and post-retry stop conditions.
- Session post-destillation records outcomes and preserves interrupted work
  without leaking stale session state between tests or consumers.

### Fixed

- Dry-run workflows remain read-only, and consumer test discovery supports the
  installed package layouts used outside this monorepo.
- CI image recovery, session fixture isolation, PIR prerequisite restoration,
  and worktree mismatch handling for the alpha16 release line.
- Pre-publish checks accept alpha development candidates, resolve repository
  documentation artifacts from package roots, and run non-mutating quality
  gates with release-CI-compatible timeouts.## [3.0.0a4] — 2026-04-17

### Fixed

- Pin `httpx<1.0` to avoid pip resolving to `httpx-1.0.dev3` under `--pre` flag. The dev release removes `TransportError` which breaks MCP SSE client at import time (`AttributeError: module 'httpx' has no attribute 'TransportError'`).

## [3.0.0a3] — 2026-04-17

### Fixed

- `markdown` library promoted from optional `confluence` extra to core dependency (same pattern as RAISE-2049 did for `mcp`). `confluence_markdown.py` imports it at module top, which triggers on every CLI invocation — declaring it as optional caused `ModuleNotFoundError` on fresh `pip install raise-cli==3.0.0a2`.

**Note:** 3.0.0a3 has the `httpx-1.0.dev3` transitive pre-release bug. Use 3.0.0a4.

## [3.0.0a2] — 2026-04-17

Second pre-release of the 3.0 line. Accumulated work since 3.0.0a1.

### Added

- **MCP as core dependency** (RAISE-2049) — `mcp` is now a required dependency, not an optional extra. Install simplifies to `pip install raise-cli`.
- **Auto-scaffold `.mcp.json`** on `rai init` and `rai upgrade` (RAISE-1664) — new projects get rai-workspace MCP server pre-registered for Claude Code.
- **Project-mcp-json doctor check** (RAISE-1664) — `rai doctor` validates `.mcp.json` presence and rai-workspace entry.
- `raise_pattern_reinforce` MCP tool async backend (S1962.10) — Protocol + Postgres + Filesystem.
- `raise_pattern_add` + `raise_session_context` HTTP backend + Protocol extension (S1962.9).
- Port-based CC session discovery via `CLAUDE_CODE_SSE_PORT` (RAISE-1986).
- Per-session namespaced context file (RAISE-1982) — prevents cross-attribution between concurrent CC sessions in same worktree.
- Relative `--project` paths resolved at CLI boundary (RAISE-2048).

### Changed

- Session context binding: skills write to `.raise/rai/sessions/<cc_session_id>/context.env` (namespaced per CC session).
- Ruff + format drift fixes across `raise-cli/` (RAISE-1858).

### Fixed

- `git add` path duplication in monorepo release flow (RAISE-1599).
- `test_mcp_server` consumer tests out of sync with S1962.8 async migration (RAISE-1835).

**Known issue (fixed in 3.0.0a3):** missing core `markdown` dependency breaks `rai` command on fresh install. Upgrade to 3.0.0a3.

## [3.0.0a1] - 2026-04-08

### Added

- **Pipeline engine** — YAML-driven pipeline orchestration with phase definitions, context specs, and review modes (EP1)
- **Dev lifecycle pipelines** — story, epic, bugfix, and session lifecycles migrated to declarative YAML pipelines (EP2)
- **MCP skill runtime** — workspace-aware MCP server for pipeline execution with tool discovery (E1305)

### Fixed

- `sync-skills.py` bracket-matching bug that duplicated DISTRIBUTABLE_SKILLS on each run
- Added Bugfix lifecycle, Discovery, and MCP categories to sync-skills.py

### Changed

- Merged v2.4.0 changes (bugfix skills, docs, adapter migration) into v3.0 branch
- Version bump to 3.0.0a1 across raise-cli, raise-core, and skills_base


## [2.4.0] - 2026-04-06

### Added

- **7 atomic bugfix skills** — rai-bugfix-start, triage, analyse, plan, fix, review, close. Decomposed from monolithic /rai-bugfix with 100% artifact completeness vs 38% baseline (E1286)
- **rai-bugfix-run orchestrator** — 3 fixed HITL gates, inline execution, signal-driven analysis method selection (E1286)
- **Confluence adapter v2** — discovery, config generation, suggest_routing(), multi-instance support (E1051)
- **rai-adapter-setup skill** — interactive adapter configuration for Jira and Confluence (S1051.6)
- **Session doctor** — diagnose/classify/execute session health issues, wired into session-start (E1248)
- **Workstream monitor** — session analysis from git history, insights at session close (E1248)
- **`rai graph build --strict`** — fail on duplicate node IDs instead of warn+skip (RAISE-648)
- **`rai docs publish --parent`** — parent page ID support for Confluence publishing (RAISE-605)
- **Local persistence adapter** — filesystem-backed backlog for offline/OSS use (E1040)

### Changed

- Removed LEARN records, emit-work, and emit-calibration from 12 lifecycle skills — write-only telemetry replaced by pipeline infrastructure in v3 (E1286 D5/D7, RAISE-1303)
- Jira config generation now produces per-project workflow states and issue types instead of global merge (RAISE-1300)

### Fixed

- 20+ bugs resolved including: epic ID collisions (RAISE-1199, RAISE-1128), graph index unavailable in worktrees (RAISE-1276), LEARN record casing (RAISE-1278), Jira update_issue REST envelope (RAISE-1274), Confluence mixed-case space keys (RAISE-1187), suggest_routing substring matching (RAISE-1272), daemon CPU leak (RAISE-1008), docs publish parent_id (RAISE-605), stale imports (RAISE-1063), MCP env KEY=VALUE parsing (RAISE-539), session state overwrites (RAISE-697)
- Integration test: comment test now uses ephemeral issues instead of accumulating on shared fixtures## [2.3.0] - 2026-03-30

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
- **Adapter plugin system**: extensible via entry points (filesystem, Jira, Confluence built-in)
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

### Adapter Architecture (E478)

- **Adapter plugin system** via entry points — filesystem, Jira, Confluence built-in
- **Clean entry points**: adapters register via `rai.adapters.pm` and `rai.docs.targets`
- **Gitignored adapter configs** (.raise/jira.yaml, .raise/confluence.yaml) to prevent PII leaks

[Unreleased]: https://github.com/humansys/raise/compare/v3.1.0rc5...HEAD
[3.1.0rc5]: https://github.com/humansys/raise/compare/v3.1.0rc2...v3.1.0rc5
[3.1.0rc2]: https://github.com/humansys/raise/compare/v3.1.0b2...v3.1.0rc2
[3.1.0b2]: https://github.com/humansys/raise/compare/v3.1.0b1...v3.1.0b2
[3.1.0b1]: https://github.com/humansys/raise/compare/v3.0.0a1...v3.1.0b1
[3.0.0a1]: https://github.com/humansys/raise/compare/v2.4.0...v3.0.0a1
[2.4.0]: https://github.com/humansys/raise/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/humansys/raise/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/humansys/raise/releases/tag/v2.2.3
