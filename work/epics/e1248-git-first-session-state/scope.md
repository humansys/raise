# E1248: Git-First Session State

> **Status:** in-progress
> **Target:** v2.4.0
> **Branch:** release/2.4.0
> **Created:** 2026-04-03
> **Jira:** RAISE-1248

## Problem

Gemba analysis identified 7 failure modes in session state management. Root cause: mutable YAML files serve as source of truth instead of git.

## Failure Modes

| FM | Description | Severity | Observed Evidence |
|----|------------|----------|-------------------|
| FM-1 | Session state lost between sessions | High | `session-state.yaml` missing entirely |
| FM-2 | Stale session-output.yaml treated as truth | Medium | 2-day-old output still present |
| FM-3 | Zombie sessions in developer profile | Low | 5-day stale session in active_sessions |
| FM-4 | No session directory cleanup | Low | 53 dirs, unbounded growth |
| FM-5 | CLAUDE.local.md dead/never implemented | Medium | File empty/absent |
| FM-6 | Worktree invisibility | High | Worktree sessions have no state context |
| FM-7 | Git not used as primary state source | High | scope.md and git log reliable but unused |

## Design Principle

**Git-first, derived, not stored.**

- Session start derives state from git (branch, scope.md frontmatter, git log)
- YAML state files become regenerable cache, not source of truth
- Automatic cleanup of stale sessions and zombie pointers
- Worktree-aware state resolution

## Scope

**In:**
- State derivation from git at session start
- Zombie session cleanup (profile.active_sessions)
- Session directory retention policy
- Worktree-aware state path resolution
- Kill or replace CLAUDE.local.md with derived generation
- Migration path from current model

**Out:**
- Server-backed state (RAISE-1229, v3.0)
- New session features
- Changes to session ID format or prefix registry

## Stories

*To be designed via `/rai-epic-design`*

## Related

- RAISE-1229: Server-Backed State Management (v3.0) — this epic produces the local model that 1229 extends
- RAISE-822: Session state should derive from git (absorbed into this epic)
- RAISE-821: epic/story close skips CLAUDE.local.md update (absorbed into this epic)
- RAISE-1232: S1229.1 SAR report (completed, informed this epic)

## References

- SAR report: `work/epics/e1229-server-state-management/s1229.1-sar-report.md`
- Gemba session: 2026-04-03, reliability-2.4 worktree
