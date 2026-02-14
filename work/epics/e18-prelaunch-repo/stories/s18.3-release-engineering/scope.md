## Story Scope: S18.3 — Release Engineering

**Size:** M
**Epic:** E18 (Pre-Launch Repo Readiness)
**GTM Ref:** S7.4
**Branch:** `story/s18.3/release-engineering`
**Research:** S18.4 security-quality-tooling synthesis (150+ sources)

**In Scope:**

L1 — Pre-commit (local dev):
- `.pre-commit-config.yaml` with ruff, detect-secrets, bandit, pyright (pre-push)
- `.secrets.baseline` for detect-secrets
- bandit config in pyproject.toml

L2 — CI Pipeline:
- GitHub Actions: test + lint + type check workflow
- GitHub Actions: CodeQL (security-extended queries)
- GitLab CI: SAST + dependency scanning + secret detection (3 template includes)
- Dependabot config (deps + GH Actions)

L3 — Release Pipeline:
- GitHub Actions: release workflow with Trusted Publishers (no token)
- PEP 740 attestations (automatic via pypa/gh-action-pypi-publish)
- GitHub public repo setup and mirror (GitLab → GitHub)
- TestPyPI → PyPI publish verification
- GitHub release tag (v2.0.0-alpha)

**Out of Scope:**
- zizmor (GH Actions audit) — post-launch
- CycloneDX SBOM generation — post-launch
- `actions/attest-build-provenance` — post-launch
- SonarCloud — revisit when team grows
- SLSA Level 3 — aspirational
- Automated mirror sync (manual push for alpha)
- PRO/Enterprise packaging

**Done Criteria:**
- [ ] Pre-commit hooks run <4s, pre-push <15s
- [ ] `pip install rai-cli` works from PyPI on clean environment
- [ ] GitHub public repo live with correct content
- [ ] GitHub release tag created
- [ ] CodeQL enabled on GitHub mirror
- [ ] GitLab CI security scanning active
- [ ] TestPyPI verification passed before production publish
- [ ] Retrospective complete

**Dependencies:** S18.1 (hard — repo must be clean), S18.2 (soft — README should be ready)

**Cross-repo:** Completion unblocks raise-gtm S7.6 (Soft Launch)
