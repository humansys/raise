# Epic Retrospective: E18 Pre-Launch Repo Readiness

**Completed:** 2026-02-13
**Duration:** 2 days (started 2026-02-12)
**Stories:** 5 delivered (4M + 1S)

---

## Summary

Prepared raise-commons for public release: security audit, community files, README rewrite, 3-layer DevSecOps pipeline, GitHub org setup with filtered mirror, and release workflow. All infrastructure is in place — the repo is launch-ready pending the business decision to flip public and tag a release.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 5 | S18.1-S18.5 |
| Calendar Days | 2 | Feb 12-13 |
| Tests | 1718 passing | 92.73% coverage |
| Commits | 45 | On epic branch |

### Story Breakdown

| Story | Size | Velocity | Key Learning |
|-------|:----:|:--------:|--------------|
| S18.1 Repo Readiness | M | — | Community files pattern reusable for future projects |
| S18.2 README | M | — | FastAPI/Ruff pattern is remarkably consistent for OSS READMEs |
| S18.3 Release Engineering | M | 1.25x | Git plumbing for filtered mirrors; separate business decisions from engineering tasks |
| S18.4 Security Spike | S | — | Research spike — 150+ sources synthesized into 3-layer DevSecOps toolchain |
| S18.5 GitHub Org Setup | M | 1.58x | gh CLI API for org administration; orphan commits for filtered mirrors |

---

## What Went Well

- **Research-first paid off** — S18.4 spike (150+ sources) made S18.3 implementation decisions instant. No deliberation during execution.
- **Epic design decisions held** — D2 (fresh start), D4 (FastAPI/Ruff README), D8 (session transcript) all proved correct. No pivots needed.
- **Rapid execution** — 5 stories in 2 calendar days. Stories S18.1 and S18.2 each completed in a single session.
- **Iterative improvement on sync script** — Started with orphan-checkout approach (S18.5), discovered it broke Claude Code skills, rewrote to git plumbing (S18.3). Each iteration was a real improvement.

## What Could Be Improved

- **T7 scope bundled too many concerns** — "sync + flip public + Trusted Publisher + tag + verify" should have been separate tasks. The business decision (go public) was mixed with engineering tasks (sync, tag).
- **Sync script tested too late** — Side effects on working tree weren't caught until it broke Claude Code skills in production use. Should have tested the script's behavior in the development environment, not just its output.
- **Design docs drifted** — S18.5 exclusion list evolved 3 times but design.md wasn't updated. Same issue as PAT-196 (architecture docs are the map).

---

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-E-275 | Git scripts in Claude Code sessions must use plumbing (GIT_INDEX_FILE + read-tree/write-tree/commit-tree) to avoid destroying working tree | git, sync, claude-code |
| (from S18.5) | `git rm --ignore-unmatch` is the correct flag for defensive removals | git, scripts |
| (from S18.2) | FastAPI/Ruff README pattern: hero → why → features → install → how → community | documentation, OSS |

## Process Insights

- **Research spikes before implementation epics are high-leverage** — S18.4 eliminated all toolchain decisions from S18.3. The implementation was pure execution.
- **Business decisions should be explicit HITL gates, not task steps** — "flip public" is not an engineering task. It's a business decision that should be a separate story or handled outside the engineering workflow.
- **Sync infrastructure needed 3 iterations** — v1 (orphan checkout, S18.5), v1.1 (--ignore-unmatch fix), v2 (git plumbing, S18.3). Infrastructure that touches git state is inherently iterative.

---

## Artifacts

- **Scope:** `work/epics/e18-prelaunch-repo/scope.md`
- **Stories:** `work/epics/e18-prelaunch-repo/stories/` (5 stories, 4 with retrospectives)
- **ADRs:** ADR-026 (filtered GitHub mirror)
- **Config files:** `.pre-commit-config.yaml`, `.github/workflows/{ci,codeql,release}.yml`, `.gitlab-ci.yml`, `.github/dependabot.yml`

---

## Deferred Items

- [ ] Flip repo public (business decision, not engineering)
- [ ] Configure Trusted Publisher on PyPI (requires public repo)
- [ ] Enable branch protection on main (requires public or paid plan)
- [ ] Version bump + tag v2.0.0-alpha.7
- [ ] Validate README session transcript against real CLI output
- [ ] Add `--dry-run` flag to sync-github.sh

---

## Next Steps

- Epic close merges to v2
- Public flip + release becomes a separate activity (not an epic — it's a deployment decision)
- raise-gtm S7.6 (Soft Launch) unblocked once public

---

*Epic retrospective completed: 2026-02-13*
