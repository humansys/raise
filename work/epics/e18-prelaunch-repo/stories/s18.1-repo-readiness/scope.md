## Story Scope: S18.1 — Repo Readiness

**Size:** M
**Epic:** E18 (Pre-Launch Repo Readiness)
**GTM Ref:** S7.1
**Branch:** TBD (via `/rai-story-start`)

**In Scope:**
- Security audit of git history (secrets, API keys, tokens)
- Fix license in pyproject.toml (MIT → Apache 2.0 to match LICENSE file)
- Create NOTICE file (Apache 2.0 attribution)
- Update CONTRIBUTING.md for GitHub open core (GitLab refs, CLI name, PR terminology)
- Create CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- Create CHANGELOG.md (Keep a Changelog format, v2.0.0-alpha entry)
- Create GitHub issue templates (bug, feature request, first session)
- Dependency vulnerability check

**Out of Scope:**
- README rewrite (S18.2)
- pyproject.toml packaging changes (S18.3)
- CI/CD pipeline setup

**Done Criteria:**
- [ ] No secrets found in git history (or remediation complete)
- [ ] License consistent across LICENSE file, pyproject.toml, and classifiers
- [ ] NOTICE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG files present
- [ ] Issue templates valid YAML
- [ ] No critical dependency vulnerabilities
- [ ] All existing tests still pass
- [ ] Retrospective complete

**Plan:** Adopt from raise-gtm `work/epics/e07-prelaunch-open-core/stories/s7.1-repo-readiness/plan.md`
