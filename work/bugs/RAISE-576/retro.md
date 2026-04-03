## Retrospective: RAISE-576

### Summary
- Root cause: 9 CVEs across docs site JS deps — astro, cloudflare adapter, undici, svgo, h3. npm ecosystem churn.
- Fix approach: Direct upgrades + npm overrides for transitives (commit ab1e6962)
- Classification: Configuration/S2-Medium/Environment/Incorrect

### Verification
- site/package.json: direct version bumps + overrides section for transitives
- 956 lines changed in package-lock.json — cascading lock resolution
- Medium severity (not S1) because docs site is not auth/data-critical

### Process Improvement
**Prevention:** npm overrides are the JS equivalent of uv constraint-dependencies — needed for transitive CVEs. The docs site is a separate attack surface from the CLI; severity should reflect that.
**Pattern:** Same class as 574/575 but in JS ecosystem. npm overrides needed because npm has no workspace-level constraint mechanism as clean as uv's.

### Patterns
- Added: none (same class as RAISE-574/575)
- Reinforced: none evaluated
