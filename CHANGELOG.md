# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.0] - 2026-03-30

### Added

- ACLI Jira adapter with multi-instance support — replaces MCP adapter with subprocess-based ACLI bridge, site resolution, and telemetry (E494, RAISE-579)
- Session identity model — deterministic session IDs per developer+repo using timestamp-based format `S-{prefix}-{YYMMDD}-{HHMM}`, Pydantic prefix registry with collision detection, per-project active pointer (E654, RAISE-654)
- CLI extension mechanism via entry points — `ExtensionInfo` discovery, collision and duplicate protection, wired into main CLI (RAISE-594)
- ISO 27001 audit report generator — Pydantic control mapping models, YAML config loader, git evidence extractor for commits, tags, and branches (E479 partial, S479.1–S479.2)
- `rai doctor` ACLI availability and authentication check (RAISE-614, S613.1)

### Changed

- MCP Jira adapter replaced by ACLI adapter (E494) — **breaking** for users who extended `McpJiraAdapter`; deleted in S494.5, entry point migrated to `AcliJiraAdapter`
- Session data moved from global `~/.rai/` tracking to per-project `.raise/rai/personal/` directory (E654) — **breaking** for tools that read `developer.yaml` active session fields
- Pattern add default scope changed from `personal` to `project` (RAISE-608)

### Fixed

- ADF description parsing — replace `str()` with `_adf_to_text()` in `_parse_issue_detail`, remove 500-char hard-cap on description display (RAISE-663)
- CLAUDE.local.md references removed from skills_base close skills (RAISE-635)
- Session-start context loss — load session state before migration so previous state is preserved (RAISE-566)
- Backlog command error handling — wrap adapter calls with consistent error messages (RAISE-553)
- Backlog search smart JQL wrapping — normalize plain-text queries to JQL in adapter (RAISE-552)
- `promote_unreleased` fails when Unreleased is last section in changelog — add `\Z` to regex (RAISE-547)
- Unicode symbols crash on Windows CP1252 terminals — add symbols module with fallbacks (RAISE-554)
- C# scanner not extracting constructor dependencies — pass `depends_on` through `build_hierarchy` (RAISE-227)
- `rai init` ide.type not syncing with `agents.types[0]` (RAISE-218)
- CI container missing git — add to `apt-get install` (RAISE-570)
- Quote project values in JQL to avoid reserved word errors (S494.4)
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
