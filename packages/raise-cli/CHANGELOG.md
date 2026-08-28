# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/humansys/raise/compare/v3.1.0rc2...HEAD
[3.1.0rc2]: https://github.com/humansys/raise/compare/v3.1.0b2...v3.1.0rc2
[3.1.0b2]: https://github.com/humansys/raise/compare/v3.1.0b1...v3.1.0b2
[3.1.0b1]: https://github.com/humansys/raise/compare/v3.0.0a1...v3.1.0b1
[3.0.0a1]: https://github.com/humansys/raise/compare/v2.4.0...v3.0.0a1
[2.4.0]: https://github.com/humansys/raise/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/humansys/raise/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/humansys/raise/releases/tag/v2.2.3
