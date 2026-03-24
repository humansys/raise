# Retrospective: RAISE-634

## Summary
- Root cause: RAISE-514 symlink migration nested docs content one level deeper; body links were not updated and Starlight does not rewrite `.md` hrefs in body content
- Fix approach: Replace all 58 relative `.md` links across 25 MDX files with absolute `/docs/...` paths

## Heutagogical Checkpoint
1. Learned: Starlight only resolves sidebar slug config — body links are passed through as-is to the browser. Symlink depth matters for relative links but not for absolute paths.
2. Process change: Write the regression test script before estimating scope — the build audit revealed 62 broken hrefs vs. my initial estimate of 8 files.
3. Framework improvement: Add `check-links.mjs` to the site CI pipeline (npm script + CI step) to prevent regressions on future structural changes.
4. Capability gained: Clear mental model of how Starlight handles (and doesn't handle) internal links — useful for any future docs architecture changes.

## Patterns
- Added: PAT-F-046 (Starlight body link behavior)
- Reinforced: none evaluated
