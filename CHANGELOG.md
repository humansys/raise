# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.4] - 2026-02-20

### Fixed
- `rai init`: Windows encoding crash (`UnicodeDecodeError: charmap cp1252`) when reading SKILL.md during workflow scaffolding — add `encoding="utf-8"` to `read_text()` call

## [2.0.3] - 2026-02-20

### Added
- Roo Code agent support: `.roo/skills` and `.roo/rules` generation, LiteLLM-compatible (RAISE-202)

### Fixed
- Discovery pipeline: C#, PHP, Dart language detection in `rai-discover-start`; exclude generated dirs (RAISE-224)
- Discovery pipeline: C#-aware confidence scorer with path and name suffix category mappings (RAISE-225)
- Discovery pipeline: normalize C# component IDs — strip namespace prefix, add `.cs`/`.dart` extensions (RAISE-226)
- Discovery pipeline: PHP namespace backslashes → dots, Windows path normalization, dedup warnings
- Discovery pipeline: C# namespace grouping and path escaping in `rai-discover-validate` (RAISE-229, RAISE-230)
- Discovery pipeline: C# and PHP branches in `rai-discover-document`; `constitution_reference` optional (RAISE-233, RAISE-234)
- `rai-discover-validate`: replace deprecated `rai discover build` with `rai memory build` (RAISE-231)
- `rai-discover-start`: avoid exit code 2 on missing optional directories
- `rai init --detect`: prompt user to confirm/extend detected agent selection (RAISE-221)
- `rai-project-onboard`: case-insensitive guardrails gate, 4-dimension coverage gate, doc discovery before conversational flow
- Guardrails template: remove hardcoded Python guardrail from base template
- `rai skill list`: 4 skills with non-standard `work_cycle` values now visible; defensive formatter fallback (RAISE-216)
- `AGENTS.md`: cross-IDE compatible session-start instruction (RAISE-217)
- `rai init`: warn when brownfield governance docs are empty after init (RAISE-220)## [2.0.2] - 2026-02-19

### Added
- Neurosymbolic Memory Density epic (RAISE-168): temporal decay scoring, Wilson confidence, pattern reinforcement via `rai memory reinforce`
- Task-relevant context bundle: two-phase context loading with `rai session context --sections` (RAISE-169)
- IDE Integration epic (RAISE-128): multi-IDE agent registry, `--ide` flag, Copilot/Cursor/Windsurf plugin support
- Problem-shape skill: `/rai-problem-shape` for guided problem definition at portfolio level (RAISE-200)
- Memory query `--format compact` for high-density Markdown-KV output (RAISE-166)
- Multi-IDE instruction generation: AgentConfig model with 5 built-in agent targets (RAISE-197)

### Fixed
- Session close race condition: three-layer defense with session-specific paths, session_id in state file, and coherence validation (RAISE-201)
- Pyright strict: explicit `last_sync_at=None` in SyncState constructor

## [2.0.1] - 2026-02-17

### Fixed
- SES-MIGRATED test fixture leakage across session tests
- Encoding fix for test `read_text()` calls on Windows

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

[Unreleased]: https://github.com/humansys-io/raise-commons/compare/v2.0.3...HEAD
[2.0.3]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a9...v2.0.3
[2.0.0a9]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a8...v2.0.0a9
[2.0.0a8]: https://github.com/humansys-io/raise-commons/compare/v2.0.0a6...v2.0.0a8
[2.0.0a6]: https://github.com/humansys-io/raise-commons/releases/tag/v2.0.0a6
