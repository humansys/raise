# Changelog

All notable changes to `raise-core` are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0a2] — 2026-04-17

### Added

- `DocumentNode` + ADR path compatibility for discovery v1/v2 layouts (S1700.5).

### Changed

- First PyPI release of the 3.0 line (previous 3.0.0a1 was tagged locally but never published).

## [3.0.0a1] — 2026-04-XX

Initial pre-release under the 3.0.0 line.

- Pipeline run persistence via `PipelineRunStore` Protocol (ADR-053): `JsonRunStore` for stdio, extension point for `PostgresRunStore` in `raise-server`.
- Knowledge graph read backend Protocol (`GraphReadBackend`) with `FilesystemGraphBackend` for stdio.
- Patterns backend Protocol + Filesystem/Postgres implementations.
- Session context backend Protocol.
- Workflow models: `PipelineRun`, `PhaseExecution`, `HitlDecision`, `PhaseResult`, `PipelineDefinition`, `RunStatus`.
- Runtime abstractions: `RaiAgentRuntime`, `RunConfig`.

## [2.2.1] — earlier

Previous stable line under the 2.x series. See git history for details.
