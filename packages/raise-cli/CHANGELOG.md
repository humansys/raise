# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- CLAUDE.local.md deprecated — git is authoritative via `rai session context` (RAISE-1434)
- MEMORY.md ownership — `memory-sync` hook disabled, Claude auto-memory respected (RAISE-1459)
- rai-epic-docs uses `rai docs publish` instead of direct MCP calls (RAISE-1298)
- Missing httpx dependency added (RAISE-1424)
- Heutagogia → Heutagogy spelling fix

### Deprecated

- `rai session journal add/show` — journal system deprecated, relies on broken CC hook injection (RAISE-1433)
- Pre-compact journal hook removed — output was discarded by Claude Code (RAISE-1433)
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

[Unreleased]: https://github.com/humansys/raise/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/humansys/raise/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/humansys/raise/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/humansys/raise/releases/tag/v2.2.3
