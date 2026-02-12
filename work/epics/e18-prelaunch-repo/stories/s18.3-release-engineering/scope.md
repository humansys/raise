## Story Scope: S18.3 — Release Engineering

**Size:** M
**Epic:** E18 (Pre-Launch Repo Readiness)
**GTM Ref:** S7.4
**Branch:** TBD (via `/rai-story-start`)

**In Scope:**
- pyproject.toml review and cleanup for public release
- GitHub public repo creation and mirror setup (GitLab → GitHub)
- TestPyPI publish and install verification on clean environment
- PyPI publish (production)
- GitHub release tag (v2.0.0-alpha)
- Verify `pip install rai-cli` works end-to-end on fresh env

**Out of Scope:**
- CI/CD pipeline (post-launch)
- Automated mirror sync (manual push for alpha)
- PRO/Enterprise packaging

**Done Criteria:**
- [ ] `pip install rai-cli` works from PyPI on 3 clean environments
- [ ] GitHub public repo live with correct content
- [ ] GitHub release tag created
- [ ] TestPyPI verification passed before production publish
- [ ] Retrospective complete

**Dependencies:** S18.1 (hard — repo must be clean), S18.2 (soft — README should be ready)

**Cross-repo:** Completion unblocks raise-gtm S7.6 (Soft Launch)
