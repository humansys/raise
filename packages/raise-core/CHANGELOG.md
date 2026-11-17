## [Unreleased]

## [3.1.8] - 2026-11-17

### Added

- Pipeline `entry_gate` for HITL-gated phases: `PhaseDefinition.entry_gate`, evaluated on `pipeline advance`, and the engine fails closed when the gate is not approved; applied to mirror-sync, pypi-publish and binary-publish (RAISE-19799)

### Fixed

- Deterministic entry/exit gates are evaluated during `pipeline advance` (RAISE-20110)

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
