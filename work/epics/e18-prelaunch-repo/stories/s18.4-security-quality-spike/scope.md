## Story Scope: S18.4 — Security & Quality Tooling Spike

**Size:** S (research only, no implementation)
**Type:** Spike / Research
**Epic:** E18 (Pre-Launch Repo Readiness)
**Branch:** story/s18.1/repo-readiness (no separate branch — research artifact only)

**Motivation:** We want to show technical excellence from day one. Starting from modern best practices — not retrofitting later. We have GitLab Premium and budget for quality tooling.

**In Scope:**
- Research GitLab Premium security features for Python CLI (SAST, dependency scanning, secret detection, license compliance)
- Evaluate SonarCloud vs GitLab built-in SAST — complementary or redundant?
- Python-specific release quality tooling (pip-audit, Sigstore signing, SBOM generation, detect-secrets pre-commit, Trusted Publishers)
- Survey what best-in-class Python CLI projects use (FastAPI, Ruff, uv, Pydantic, Typer)
- Recommend a concrete toolchain with effort estimates

**Out of Scope:**
- Implementation (that goes into S18.3 or post-launch stories)
- CI/CD pipeline setup (post-launch)
- Non-Python tooling

**Done Criteria:**
- [ ] Evidence catalog with triangulated claims
- [ ] Concrete recommendation: which tools, why, effort estimate
- [ ] Decision on what to include in S18.3 vs post-launch
- [ ] Retrospective complete

**Deliverable:** Research synthesis in `work/epics/e18-prelaunch-repo/research/security-quality-tooling.md`
