# E1248 Retrospective: Git-First Session State

**Epic:** E1248 — Git-First Session State
**Dates:** 2026-04-03 (single day, multiple sessions)
**Stories:** 5/5 complete (3M + 1S + 1M)
**Branch:** release/2.4.0
**Jira:** RAISE-1248

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 5 (S1248.1-S1248.5) |
| Commits | 40 |
| Files changed | 35 |
| Lines added | ~5,300 |
| Lines removed | ~100 |
| Tests added | ~100 new tests |
| Full suite | 4,151 passed, 0 failed |
| Failure modes resolved | 7/7 |

## Deliverables

1. **Three session protocols** (ADR-038): StateDeriver, SessionRegistry, WorkstreamMonitor
2. **GitStateDeriver** — derives CurrentWork from branch, scope.md, git log
3. **LocalSessionRegistry** — session lifecycle with gc() (now deprecated)
4. **LocalWorkstreamMonitor** — commit velocity, TDD compliance, revert ratio
5. **Bundle integration** — assemble_orientation() uses git-derived state
6. **CLAUDE.local.md killed** — references removed from 6 docs
7. **Session Doctor** — consent-based cleanup replacing silent gc()
8. **`rai session doctor`** — standalone diagnostic subcommand
9. **Session close insights** — commit stats shown on close
10. **Entry points** — 3 protocol backends discoverable via importlib

## Failure Modes Resolution

| FM | Description | Resolution |
|----|-------------|-----------|
| FM-1 | Session state lost between sessions | GitStateDeriver derives from git — no file to lose |
| FM-2 | Stale session-output.yaml | Doctor detects and auto-cleans (>24h) |
| FM-3 | Zombie sessions in profile | Doctor detects (>48h), cleans with consent |
| FM-4 | No session directory cleanup | Doctor + retention policy (20 dirs) |
| FM-5 | CLAUDE.local.md dead | Killed — references removed from codebase |
| FM-6 | Worktree invisibility | GitStateDeriver uses git rev-parse --git-common-dir |
| FM-7 | Git not used as primary state | Bundle now calls GitStateDeriver first, YAML fallback |

## What Went Well

- **Walking skeleton strategy paid off.** S1248.1 proved the protocol pattern; S1248.2-S1248.5 followed the same shape. Pattern repetition (protocol → implementation → entry point → test) took ~15 minutes per story by S1248.4.
- **TDD caught real bugs.** The classify() routing bug (S1248.5 QR) was caught before merge. Defense-in-depth for derive_current_work() was added after a mock test revealed the gap.
- **Data safety principle emerged naturally.** "Never destroy user data without informed consent" wasn't in the original design — it emerged from gemba observation during S1248.5 scope design.
- **Parallel story execution worked.** S1248.2 and S1248.3 touched different files, merged without conflict.

## What to Improve

- **LEARN records inconsistent.** Only 7/25 possible records were created. Autonomous implementation mode drops them. Need a checkpoint or automation.
- **Epic scope lagged implementation.** S1248.5 was redesigned from "Dogfood + stabilize" (S) to "Session Doctor" (M) mid-epic. The scope.md in the worktree diverged from the main repo copy.
- **Pattern ID conflicts on merge.** PAT-E-713/714 had to be renumbered to 717/718 due to parallel work in E1051. patterns.jsonl needs an auto-increment or UUID strategy.

## Patterns Discovered

| ID | Pattern | Type |
|----|---------|------|
| PAT-E-709 | Instance methods as test seams for subprocess wrappers | technical |
| PAT-E-710 | Entry points require reinstall for test discovery | process |
| PAT-E-717 | Consent-based CLI cleanup: diagnose → classify → execute | process |
| PAT-E-718 | Deprecation via warnings.warn + docstring | process |

## Architecture Decisions

- **ADR-038 accepted** — Session protocols with derived state. Validated by S1248.1, updated with backend selection strategy for 3.0.
- **gc() deprecated** — Replaced by SessionDoctor consent model. Method stays in protocol for server backend compatibility.
- **info_only bucket questionable** — ActionPlan.info_only may not be needed. All findings have actions; classify() now routes everything to auto_clean or needs_consent.

## What This Enables

- **v3.0 server backend** (RAISE-1229): Protocol contracts ready. Server implementations register via entry points — zero-config upgrade for community users.
- **Epic close** (E1248): All 7 failure modes resolved. Sessions start with correct context in worktrees.
- **Session Doctor** as a pattern: diagnose → classify → execute with consent is reusable for migration tools, cleanup wizards, and health checks.

## Learning Chain Summary

| Skill | Records Found | Records Missing |
|-------|:------------:|:--------------:|
| epic-design | 0 | 1 |
| epic-plan | 0 | 1 |
| story-plan | 2 | 3 |
| story-implement | 2 | 3 |
| story-review | 3 | 2 |
| **Total** | **7** | **10** |

Gap: 58% record loss, primarily from sessions before LEARN discipline was established and from autonomous mode in S1248.3-S1248.5.
