# Retrospective: S18.3 — Release Engineering

## Summary
- **Story:** S18.3
- **Epic:** E18 (Pre-Launch Repo Readiness)
- **Started:** 2026-02-13
- **Completed:** 2026-02-13
- **Estimated:** M (~2-3 hours)
- **Actual:** ~2 hours (T1-T6 fast, T7 reduced scope)
- **Velocity:** ~1.5x (scope reduced on T7, but fixes added)

## What Was Delivered

### T1-T6: Config Files (Complete)
- `.pre-commit-config.yaml` — ruff, detect-secrets, bandit, pyright (pre-push)
- `.secrets.baseline` — generated baseline for detect-secrets
- `.github/workflows/ci.yml` — test + lint + typecheck matrix
- `.github/workflows/codeql.yml` — security-extended queries
- `.github/workflows/release.yml` — Trusted Publishers + PEP 740 attestations
- `.gitlab-ci.yml` — SAST, dependency scanning, secret detection
- `.github/dependabot.yml` — weekly pip + GH Actions updates
- `pyproject.toml` — bandit config section

### T7: Sync (Partial — public flip deferred)
- GitHub mirror synced with filtered content
- `.gitlab-ci.yml` excluded from GitHub mirror
- Sync script rewritten to use git plumbing (no working tree changes)

### Unplanned Fixes
- `NodeType` literal missing `release` — broke `rai session start`
- `sync-github.sh` working tree modification — destroyed Claude Code skills

## What Went Well
- T1-T6 executed rapidly — pure config files with S18.4 research as input
- Clean separation: all tasks independent, no source code changes
- Research investment (S18.4) paid off — no decision fatigue during implementation

## What Could Improve
- T7 scope was ambitious (sync + public + Trusted Publisher + tag + verify) — should have been split into separate tasks
- The sync script bug was a latent defect from S18.5 that only surfaced in this session when skills were checked

## Heutagogical Checkpoint

### What did you learn?
- Git plumbing (`GIT_INDEX_FILE` + `read-tree`/`write-tree`/`commit-tree`) is the correct approach for building filtered commits without touching the working tree
- Schema Literal types (PAT-152) continue to be a source of runtime errors when new node types are added to data but not the model
- "Go public" is a business decision, not an engineering task — it should be a separate story or at least a separate task with explicit HITL gate

### What would you change about the process?
- Split T7 into: T7a (sync infrastructure), T7b (public flip + Trusted Publisher), T7c (tag + release). Each is independently valuable and has different HITL requirements.
- Test sync script's side effects on the development environment (not just its output)

### Are there improvements for the framework?
- Scripts that modify git state (checkout, branch, rm) should use plumbing when running inside Claude Code sessions
- NodeType model should have a test that validates against actual graph data

### What are you more capable of now?
- Git plumbing for filtered mirrors — reusable pattern for any multi-remote filtered sync
- Understanding that Claude Code watches the filesystem — any tool that temporarily removes `.claude/` will break skills

## Improvements Applied
- `sync-github.sh` rewritten to use git plumbing (permanent fix)
- `NodeType` literal updated to include `release`

## Deferred to Future
- [ ] Public flip + Trusted Publisher config (separate story or epic close activity)
- [ ] Version bump + tag (after public flip)
- [ ] Test that NodeType literal covers all graph node types
- [ ] zizmor, CycloneDX SBOM, SLSA Level 3 (post-launch backlog)
