## Retrospective: RAISE-574

### Summary
- Root cause: Dependency pinned to old minimum (authlib>=1.3.0) — never reviewed for CVEs until Snyk flagged it
- Fix approach: Bump floor to >=1.6.9, regenerate lock (commit a38f558d)
- Classification: Configuration/S1-High/Environment/Incorrect

### Verification
- pyproject.toml: authlib>=1.3.0 → >=1.6.9. Lock updated. 3 CVEs resolved.
- No code changes — pure dependency bump.

### Process Improvement
**Prevention:** Automated dependency scanning (Snyk/Dependabot) in CI catches CVEs reactively. Proactive: periodic review of security-critical deps (auth, crypto) even without alerts.
**Pattern:** Configuration + Environment + Incorrect → dependency floor too low, vulnerable transitive. Fix is always mechanical (bump + lock). The cost is in detection latency — critical CVEs sat in prod until scanner caught them.

### Patterns
- Added: none (dependency hygiene is well-understood)
- Reinforced: none evaluated
