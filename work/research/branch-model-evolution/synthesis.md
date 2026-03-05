# Branch Model Evolution: Research Synthesis

> Date: 2026-03-03
> Sources: 2 evidence catalogs, 40+ sources
> Trigger: Cross-worktree artifact visibility problem during E353/E354 setup
> Status: Complete — ready for decision

---

## The Problem

Working on epic A in a worktree, we create research/artifacts. When we spin up
a worktree for epic B (from dev), those artifacts are invisible because they live
on epic A's uncommitted branch. The root cause: **epic branches are long-lived,
and artifacts don't reach dev until the entire epic merges.**

## What the Evidence Says

### DORA is unambiguous (Confidence: Very High)
- High-performing teams: 3 or fewer active branches, merge to trunk daily
- Branch lifetime: hours, not days or weeks
- AI agents make it WORSE: 21% more tasks but 7.2% less delivery stability
- Root cause: AI amplifies batch size → bigger changesets → more risk

### Agentic teams converge on story-level branches (Confidence: High)
- incident.io: worktree per task, PR against main, no intermediate branches
- Anthropic's 2026 report: "topic branches" and "stacked diffs" — story/task level
- Cursor 2.0: parallel agents in worktrees, one branch per agent
- Pattern: one agent session = one bounded change = one short-lived branch

### Epics are a planning concept, not a branching concept (Confidence: Very High)
- Linear, Shortcut, Jira: epics are tracking containers, not branches
- Google, Meta, Uber: trunk-based, no epic branches, feature flags for WIP
- Progress = aggregation of story completion in the tracker
- "Epic done" = all stories done in tracker, not a branch merge

### Feature flags replace epic branch isolation (Confidence: High)
- Flags provide runtime isolation that epic branches provide at source control level
- Lifecycle: create flag → stories merge behind flag → enable progressively → cleanup
- Trade-off: flag tech debt vs merge hell (flags win for most teams)
- For RaiSE: we're a CLI tool, not a web app — feature flags are less relevant,
  but the principle applies: stories should be independently mergeable

---

## Options for RaiSE

### Option A: Keep as-is
`main → dev → epic/eN/name → story/sN.M/name`

- Pro: familiar, epic isolation
- Con: artifacts invisible across epics, merge conflicts, DORA anti-pattern

### Option B: Drop epic branches (RECOMMENDED)
`main → dev → story/sN.M/name`

- Stories merge to dev directly
- Epic = label in Jira, not a branch
- Worktrees created from dev per story (or per session)
- Artifacts available immediately after story merge
- Epic close = verify all stories done in tracker, tag dev

### Option C: Drop epic AND dev (full trunk-based)
`main → story/sN.M/name`

- Maximum simplicity, full DORA alignment
- Requires: robust CI gates, feature flags for WIP
- More risk for a solo/small team project

### Option D: Hybrid
Default is B, but allow epic branches for exceptional cases
(massive refactors, breaking changes that can't be incrementally delivered)

---

## Recommended: Option B with gradual transition

**New branch model:**
```
main (stable, releases)
  └── dev (integration, CI must pass)
        └── story/sN.M/name (short-lived, hours/days, worktree-isolated)
```

**Epic lifecycle changes:**
- `rai-epic-start`: creates epic in tracker + `work/epics/eN/` directory, NO branch
- `rai-story-start`: creates branch from dev + worktree (optional)
- `rai-story-close`: merges to dev (not to epic branch)
- `rai-epic-close`: verifies all stories done, tags dev, writes retrospective

**Worktree model:**
- One worktree per active story (not per epic)
- Created from dev, always fresh
- Merge back to dev when story closes
- Cleanup after merge

**What this solves:**
- Cross-epic artifact visibility (everything on dev after story merge)
- Long-lived branch drift
- Worktree confusion (no more branch identity issues)
- Simpler mental model (2 levels instead of 3)

**What we lose:**
- Ability to revert an entire epic as one unit (mitigated by: revert individual stories)
- Epic branch as "staging area" for incomplete work (mitigated by: stories are independently complete)
- Visual grouping in git log (mitigated by: commit prefixes like `feat(e353):`)

---

## Impact on Skills

| Skill | Change needed |
|-------|--------------|
| `rai-epic-start` | Remove branch creation, keep tracker + directory |
| `rai-epic-close` | Remove merge, keep retrospective + tag |
| `rai-story-start` | Branch from dev (not epic), optional worktree |
| `rai-story-close` | Merge to dev (not epic) |
| `rai-story-run` | No change (orchestration is phase-level) |
| `rai-epic-run` | Simplify (no epic branch to manage) |
| CLAUDE.md | Update branch model section |

---

## Evidence Catalogs

- [Agentic Branching Patterns](agents output — 20+ sources on DORA, agentic workflows, worktrees)
- [Epics Without Epic Branches](epics-without-epic-branches.md — 24 sources)
