# E1248: Git-First Session State

> **Status:** in-progress
> **Target:** v2.4.0
> **Branch:** release/2.4.0
> **Created:** 2026-04-03
> **Jira:** RAISE-1248

## Objective

Eliminate session state unreliability by deriving work context from git (the only reliable source) instead of mutable YAML files. Design protocol interfaces that the server (3.0) extends, implementing git-only backends for community (2.4).

## Value

- Sessions start with correct context every time, including in worktrees
- Zero manual state tracking — Rai derives, not stores
- 2.4 community work becomes the fallback backend for 3.0, not throwaway
- 7 observed failure modes resolved

## Failure Modes (Gemba Evidence)

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

**Server-first design, community retrofit.**

Three session protocols (ADR-038):
- **StateDeriver** — derives current work context (branch, epic, story, phase)
- **SessionRegistry** — tracks active sessions, lifecycle, garbage collection
- **WorkstreamMonitor** — analyzes session patterns, suggests improvements

Each has a git-only community backend (2.4) and a server backend (3.0, RAISE-1229).

## Scope

**In (MUST):**
- Session protocols definition (StateDeriver, SessionRegistry, WorkstreamMonitor)
- Git-only StateDeriver implementation (branch parsing, scope.md, git log)
- SessionRegistry with zombie gc and retention policy
- Worktree-aware personal dir resolution
- Bundle assembly consuming protocols instead of YAML files
- Migration from current model (backward compatible)

**In (SHOULD):**
- WorkstreamMonitor basic implementation (journal + git heuristics)
- Kill CLAUDE.local.md (superseded by derived state)

**Out:**
- Server-backed implementations (RAISE-1229, v3.0)
- New session features (beyond reliability)
- Changes to session ID format or prefix registry

## Stories

| ID | Name | Size | Dependencies | FMs Addressed |
|----|------|------|-------------|---------------|
| S1248.1 | Session protocols + GitStateDeriver | M | — | FM-7, FM-6, FM-1 | ✓ |
| S1248.2 | SessionRegistry + lifecycle gc | M | S1248.1 | FM-2, FM-3, FM-4 | ✓ |
| S1248.3 | Bundle integration + CLAUDE.local.md kill | M | S1248.1 | FM-5, FM-7 | ✓ |
| S1248.4 | WorkstreamMonitor basics | S | S1248.2 | — (kaizen) | ✓ |
| S1248.5 | Session Doctor — safe operationalization | M | S1248.1-S1248.4 | All (operationalization) | ✓ |

### S1248.1: Session Protocols + GitStateDeriver

Define the three Protocol contracts in `session/protocols.py`. Implement `GitStateDeriver` in `session/derive.py` with:
- Branch parsing (release, story extraction)
- scope.md frontmatter grep for active epics
- git log recent activity extraction
- Phase inference from commit patterns
- Worktree-aware path resolution via `git rev-parse --git-common-dir`

Entry point registration in pyproject.toml.

### S1248.2: SessionRegistry + Lifecycle GC

Implement `LocalSessionRegistry` in `session/registry.py`:
- register/close/active operations (wraps existing index.py + active-session logic)
- gc() method: zombie reaping (>48h), session dir retention (20 dirs / 30 days), stale output cleanup
- Integrate gc() into session start flow
- Entry point registration

### S1248.3: Bundle Integration + CLAUDE.local.md Kill

Modify `bundle.py` to consume StateDeriver for current_work instead of YAML:
- StateDeriver.current_work() → replaces session-state.yaml read for work context
- YAML remains as fallback for non-derivable fields (narrative, pending, next_session_prompt)
- Remove CLAUDE.local.md references across codebase
- Close RAISE-821 as superseded

### S1248.4: WorkstreamMonitor Basics

Implement `LocalWorkstreamMonitor` in `session/monitor.py`:
- analyze_session(): commit velocity, TDD compliance (test commits vs code commits), revert ratio
- suggest_improvements(): heuristics from last N sessions
- Integrated into session close flow (optional analysis)

### S1248.5: Dogfood + Stabilize

Use the new protocols in real sessions for 3-5 days:
- Verify git derivation accuracy across worktrees
- Validate gc() cleans without destroying needed state
- Confirm bundle produces correct context
- Fix edge cases discovered during use

## Done Criteria

- [ ] All 7 failure modes have verified resolutions
- [ ] Bundle assembly works correctly in worktrees (manual verification)
- [ ] Session start derives correct current_work from git in >90% of cases
- [ ] Zombie sessions cleaned automatically on start
- [ ] Session directory count stabilizes (retention policy active)
- [ ] No regression in session start latency (git queries < 500ms)
- [ ] Protocol interfaces documented for 3.0 server implementation
- [ ] Architecture docs updated (ADR-038)
- [ ] Retrospective completed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Git derivation inaccurate for edge cases (detached HEAD, no scope.md) | Medium | Medium | Fallback to YAML, log derivation confidence |
| Protocol abstraction too heavy for 2 backends | Low | Medium | Start with StateDeriver only, validate before extending (ADR-038 mitigation) |
| Packages restructure (ongoing) conflicts with session module changes | Medium | Low | Coordinate with E1136, rebase frequently |

## Related

- RAISE-1229: Server-Backed State Management (v3.0) — this epic produces the local model that 1229 extends
- RAISE-822: Session state should derive from git (absorbed as S1248.1/S1248.3)
- RAISE-821: epic/story close skips CLAUDE.local.md update (absorbed as S1248.3 — kill)
- RAISE-1232: S1229.1 SAR report (completed, informed this epic)
- ADR-038: Session Protocols with Derived State

---

## Implementation Plan

### Sequencing Strategy: Walking Skeleton + Risk-First

S1248.1 proves the protocol architecture (highest risk, everything depends on it). Then S1248.2 and S1248.3 run in parallel — different codebase areas, no mutual dependency. S1248.4 and S1248.5 close out.

### Story Sequence

| # | Story | Size | Depends On | Rationale | Enables |
|---|-------|------|-----------|-----------|---------|
| 1 | S1248.1: Protocols + GitStateDeriver | M | — | Walking skeleton: proves protocol pattern, defines contracts, implements core derivation | S1248.2, S1248.3 |
| 2a | S1248.2: SessionRegistry + gc | M | S1248.1 | Parallel track A: lifecycle management, zombie cleanup | S1248.4 |
| 2b | S1248.3: Bundle integration + kill CLAUDE.local | M | S1248.1 | Parallel track B: wire protocols into actual bundle, user-visible change | S1248.5 |
| 3 | S1248.4: WorkstreamMonitor basics | S | S1248.2 | Kaizen: session analysis heuristics, lowest risk | — |
| 4 | S1248.5: Dogfood + stabilize | S | S1248.3 | Validation: real usage across worktrees, edge case fixing | Epic close |

### Critical Path

```
S1248.1 ──► S1248.3 ──► S1248.5 ──► Epic Close
              │
S1248.1 ──► S1248.2 ──► S1248.4
```

Critical path: S1248.1 → S1248.3 → S1248.5 (protocol → bundle → validation).
S1248.2 → S1248.4 is the parallel track (registry → monitor).

### Milestones

#### M1: Architecture Proven (after S1248.1) ✓

- [x] Protocol contracts defined in `session/protocols.py`
- [x] GitStateDeriver returns correct CurrentWork for: release branch, story branch, worktree
- [x] Entry points registered and discoverable
- [x] Unit tests pass for all derivation cases (including edge: detached HEAD, no scope.md)

**Demo:** `GitStateDeriver().current_work(Path("."))` returns accurate state in this worktree.

#### M2: Core Reliable (after S1248.2 + S1248.3)

- [ ] Bundle assembly uses StateDeriver (not YAML) for current_work
- [ ] SessionRegistry gc() cleans zombies on session start
- [ ] CLAUDE.local.md references removed
- [ ] Session start works correctly in worktrees
- [ ] All 7 failure modes addressed

**Demo:** `/rai-session-start` in a worktree shows correct epic/story/branch context.

#### M3: Epic Complete (after S1248.4 + S1248.5)

- [ ] WorkstreamMonitor provides basic session insights
- [ ] 3-5 days of real usage validates reliability
- [ ] Done criteria met
- [ ] Retrospective completed

**Demo:** Session close optionally shows "this session: N commits, TDD compliance X%".

### Parallel Opportunities

S1248.2 and S1248.3 touch different areas:
- S1248.2: `session/registry.py` (new), `session/index.py` (refactor), `cli/commands/session.py` (gc integration)
- S1248.3: `session/bundle.py` (modify), `session/bundle_data.py` (modify), CLAUDE.local.md references (delete)

No file overlap → safe to parallelize in separate sessions/worktrees.

### Progress Tracking

| Story | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| S1248.1 | pending | — | — | |
| S1248.2 | pending | — | — | |
| S1248.3 | pending | — | — | |
| S1248.4 | pending | — | — | |
| S1248.5 | pending | — | — | |

### Sequencing Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| S1248.1 protocol pattern doesn't fit session domain | Blocks everything | ADR-038 mitigation: start with StateDeriver only, validate before extending |
| Parallel S1248.2/S1248.3 causes merge conflicts | Low delay | Different files, rebase frequently |
| Dogfood (S1248.5) reveals fundamental issues | Rework | PAT-E-592: budget 50% time buffer for dogfood stories |

## References

- Design: `work/epics/e1248-git-first-session-state/design.md`
- Gemba findings: `work/epics/e1248-git-first-session-state/gemba-findings.md`
- SAR report: `work/epics/e1229-server-state-management/s1229.1-sar-report.md`
- Existing protocols: `packages/raise-cli/src/raise_cli/adapters/protocols.py`
