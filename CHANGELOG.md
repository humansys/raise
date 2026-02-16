# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-02-16

### Added
- Developer Enablement: Starlight docs site (22 pages, EN+ES) at docs.raiseframework.ai
- Methodology article: core concepts, Lean principles, the Triad
- Jumpstart training materials for team onboarding
- Complete CLI reference for all core commands

## [2.0.0a9] - 2026-02-16

### Added
- Multi-agent session isolation: `--agent` and `--session` CLI flags for concurrent agent support (RAISE-127 pt1)
- Session token protocol with priority resolution (`RAI_SESSION_ID` env → `--session` flag → auto-generate)
- Per-session state directories with automatic migration from flat files
- CWD poka-yoke guard on session close to prevent shell death (PAT-204)
- `resolve_session_id()` and `resolve_session_id_optional()` helpers
- `--session` flag on telemetry emit commands (`emit-work`, `emit-calibration`, `emit-pattern`)
- JIRA OAuth 2.0 integration with PKCE flow and auto-refresh (PRO)
- Bidirectional JIRA sync: `rai backlog pull/push/status/auth` commands (PRO)

### Fixed
- PRO import guards: all `rai backlog` commands show clear "requires rai-pro" message instead of ImportError## [2.0.0a8] - 2026-02-14

### Added
- Session narrative for cross-session memory continuity (HF-1)
- Publish workflow: `rai publish check` and `rai publish release` commands (HF-2)
- `/rai-publish` skill for guided release workflow

### Fixed
- PEP 440 version compliance (`2.0.0a7` format)
- Version sync between pyproject.toml and __init__.py## [2.0.0a6] - 2026-02-12

### Added
- Initial public release of rai-cli
- 24 RaiSE skills for AI-assisted software engineering
- Codebase discovery with multi-language support (Python, TypeScript, JavaScript, PHP, Svelte)
- Knowledge graph for project context and memory
- Session lifecycle management with memory persistence
- Framework governance documents (constitution, guardrails, glossary)

### Note
- This is an alpha release. APIs and skill interfaces may change.

[Unreleased]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a9...HEAD
[2.0.0a9]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a8...v2.0.0a9
[2.0.0a8]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a6...v2.0.0a8
[2.0.0a6]: https://github.com/humansys-io/raise-commons/releases/tag/v2.0.0a6
