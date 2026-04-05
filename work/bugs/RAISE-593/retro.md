# Retrospective: RAISE-593

## Summary
- Root cause: Generic `except Exception` in `resolve_entrypoint` renders raw FileNotFoundError with no guidance on how to create the missing config
- Fix approach: Catch `FileNotFoundError` separately, show what's missing + suggest `rai adapter-setup`
- Classification: UX/S3-Low/Code/Missing

## Process Improvement
**Prevention:** Every `except Exception` that renders to the user should distinguish recoverable errors (missing config → guided setup) from unrecoverable ones (connection refused → raw message). Generic catch-all is a UX smell.
**Pattern:** UX + Code + Missing → generic error handler masking actionable recovery path.

## Heutagogical Checkpoint
1. Learned: `resolve_entrypoint` is the single instantiation point for all adapters — fixing it here benefits Jira, Confluence, and any future adapter.
2. Process change: When adding adapter constructors that throw on missing config, the error message should include the fix command.
3. Framework improvement: The `rai adapter-setup` skill already exists — the error message now points to it, completing the guided loop.
4. Capability gained: Understanding of the full adapter resolution chain: entry points + YAML discovery → resolve → instantiate → wrap.

## Patterns
- Added: none (fix is self-documenting — 9 lines)
- Reinforced: none evaluated
