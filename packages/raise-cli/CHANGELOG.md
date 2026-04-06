# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Integration test: comment test now uses ephemeral issues instead of accumulating on shared fixtures

## [2.3.0] - 2026-03-30

See root CHANGELOG.md for prior releases.

[Unreleased]: https://github.com/humansys/raise/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/humansys/raise/releases/tag/v2.3.0
