## Retrospective: RAISE-698

### Summary
- Root cause: S11.4 package migration split monolith into packages but lost 3 pyproject.toml configs from rai-agent: entry points, raise-cli dep, and telegram/scheduling deps.
- Fix approach: Restore missing configs in pyproject.toml (commit 0631e191). 8 insertions, 6 deletions.
- Classification: Configuration/S2-Medium/Integration/Missing

### Verification
- packages/rai-agent/pyproject.toml: entry points, raise-cli dep, and core deps restored
- Only bug in this batch with Origin=Integration — caused by migration between packages, not by code logic

### Process Improvement
**Prevention:** Package split migrations need a checklist: entry points, dependencies, optional deps, scripts, and CLI subcommands. Verify each package runs independently after split.
**Pattern:** Configuration + Integration + Missing → migration lost config. Package splits are high-risk for config loss because the original monolith pyproject.toml handled everything implicitly.

### Patterns
- Added: PAT-F-050 (see below)
- Reinforced: none evaluated
