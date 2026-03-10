# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Docs site install commands corrected from `rai-cli` to `raise-cli` in EN and ES pages (RAISE-511)

## [2.2.2] - 2026-03-09

### Added
- Auto-sync skills on `rai session start` when CLI version is newer than deployed skills (RAISE-509)

### Fixed
- Session counter reset when `index.jsonl` lost — `get_next_id` now scans sibling directories as fallback (RAISE-502)
- Duplicate pattern IDs in `patterns_captured` — now collects real IDs from `append_pattern` results (RAISE-506)
- Orphan session directory from flat-to-per-session migration — migration now targets `last_session.id` (RAISE-505)
- Journal entry types documented in CLI quick reference — prevents agent from guessing invalid types (RAISE-485)
- Invalid `--type behavioral` in bugfix/debug skill docs — replaced with valid `--type process` (RAISE-508)
- MCP health check errors in session-start skill reported as "not connected" instead of tracebacks (RAISE-508)
- Duplicate node IDs in `rai graph build` now raise error instead of silent overwrite (RAISE-510)
- `sync-skills.py` path fixed for `raise_cli` rename; `twine` gate uses system install (RAISE-508)## [2.2.0] - 2026-03-05

### Added
- Complete CLI reference documentation: 17 command group pages covering 72 subcommands (E348)
- Developer extension guides: adapters, skills, MCP servers, lifecycle hooks (E348)
- `llms.txt` and `llms-full.txt` for AI agent documentation discovery (E348)
- AGENTS.md rewritten with comprehensive agent instructions (E348)
- `/rai-doctor` skill: conversational wrapper for CLI diagnostics (E352)
- `/rai-story-run` and `/rai-epic-run`: orchestrator skills for full lifecycle automation
- `/rai-bugfix`: formal 6-phase bug fix lifecycle with traceability
- `/rai-mcp-add`, `/rai-mcp-remove`, `/rai-mcp-status`: MCP server management skills
- `/rai-skill-create`, `/rai-skillset-manage`: skill authoring and set management
- 9 missing skills added to `DISTRIBUTABLE_SKILLS` registry
- `ArtifactNode` graph node type for work artifacts
- Doctor report generation and email via mailto (E352)
- Doctor `--fix` auto-remediation with backup (E352)

### Fixed
- README: version v2.2.0, branch model (no epic branches), GitHub URLs, 37 skills count
- CONTRIBUTING: branch reference `v2` → `dev`
- Install docs: Python 3.12-3.13 requirement, pipx recommended, macOS system Python warning
- All doc site pages updated from deprecated `rai memory` to current `rai graph`/`rai pattern`/`rai signal` commands
- Pyright errors in artifacts module (Pydantic/pyright compatibility)
- Consolidated story-design skill output from 3 locations to 2 (removed `work/docs/` redundancy)

### Changed
- Documentation site restructured: multi-file CLI reference with workflow ordering
- Docs deployed to docs.raiseframework.ai via Cloudflare Pages

## [2.1.0] - 2026-02-24

### Added
- Skill Excellence (E250): 27 ADR-040 compliant skills, ~65% line reduction across all skill definitions
- `/rai-debug` v2.1.0: triage tier (quick/standard/deep) for proportionate root cause analysis
- `/rai-architecture-review`: evaluate design proportionality and necessity using Beck's four rules
- `/rai-quality-review`: critical code review with external auditor perspective
- `/rai-problem-shape`: guided problem definition at portfolio level (RAISE-200)
- `/rai-framework-sync`: sync framework files across locations after architectural decisions
- `/rai-publish`: structured release workflow with quality gates
- Contract Chain restored (RAISE-266): typed artifact handoff between lifecycle skills — `brief.md`, `story.md`, `design.md` templates with producer/consumer references across 5 skills

### Fixed
- `iter_concepts`: graceful degradation on unknown `NodeType` — graph queries no longer crash on unrecognized node types (RAISE-136)
- CI: `uv sync --extra dev` ensures `pytest` is installed in pipeline (RAISE-256)

### Breaking Changes
- `rai memory generate` removed — functionality integrated into `rai graph build`
- `rai memory add-calibration` removed — use `rai signal emit-calibration`
- `rai memory add-session` removed — use `rai signal emit-session`
- All 27 skills updated (E250): re-run `rai init` in existing projects to get updated skill definitions

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
- `rai init`: warn when brownfield governance docs are empty after init (RAISE-220)

## [2.0.2] - 2026-02-19

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
- PRO import guards: all `rai backlog` commands show clear "requires rai-pro" message instead of ImportError

## [2.0.0a8] - 2026-02-14

### Added
- Session narrative for cross-session memory continuity (HF-1)
- Publish workflow: `rai publish check` and `rai publish release` commands (HF-2)
- `/rai-publish` skill for guided release workflow

### Fixed
- PEP 440 version compliance (`2.0.0a7` format)
- Version sync between pyproject.toml and __init__.py

## [2.0.0a6] - 2026-02-12

### Added
- Initial public release of raise-cli
- 24 RaiSE skills for AI-assisted software engineering
- Codebase discovery with multi-language support (Python, TypeScript, JavaScript, PHP, Svelte)
- Knowledge graph for project context and memory
- Session lifecycle management with memory persistence
- Framework governance documents (constitution, guardrails, glossary)

### Note
- This is an alpha release. APIs and skill interfaces may change.

[Unreleased]: https://github.com/humansys/raise/compare/v2.2.2...HEAD
[2.2.2]: https://github.com/humansys/raise/compare/v2.2.0...v2.2.2
[2.2.0]: https://github.com/humansys/raise/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/humansys/raise/compare/v2.0.4...v2.1.0
[2.0.4]: https://github.com/humansys/raise/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/humansys/raise/compare/v2.0.0a9...v2.0.3
[2.0.0a9]: https://github.com/humansys/raise/compare/v2.0.0a8...v2.0.0a9
[2.0.0a8]: https://github.com/humansys/raise/compare/v2.0.0a6...v2.0.0a8
[2.0.0a6]: https://github.com/humansys/raise/releases/tag/v2.0.0a6
