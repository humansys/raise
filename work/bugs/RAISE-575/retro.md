## Retrospective: RAISE-575

### Summary
- Root cause: PyJWT transitive dependency — authlib and mcp both pull pyjwt, neither pinned high enough for CVE-2026-32597
- Fix approach: uv constraint-dependencies to force pyjwt>=2.12.0 across all chains (commit 602d97d9)
- Classification: Configuration/S1-High/Environment/Incorrect

### Verification
- pyproject.toml: added `constraint-dependencies = ["pyjwt>=2.12.0"]` at workspace level
- Forces all workspace members to resolve pyjwt>=2.12.0 regardless of their own floor
- Correct use of uv's constraint mechanism for transitive pinning

### Process Improvement
**Prevention:** For security-critical transitive deps (jwt, crypto, tls), workspace-level constraint-dependencies is the right mechanism — individual package floors don't control transitives.
**Pattern:** Same class as RAISE-574 but worse: transitive deps are invisible. Direct deps you control; transitives need workspace constraints.

### Patterns
- Added: PAT-F-048 (see below)
- Reinforced: none evaluated
