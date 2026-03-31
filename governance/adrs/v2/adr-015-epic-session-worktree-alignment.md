---
id: "ADR-015"
title: "Epic–Session–Worktree Alignment: Parallelizable Value Delivery"
date: "2026-03-31"
status: "Draft"
related_to: ["ADR-033", "ADR-013"]
supersedes: []
story: null
research: null
---

# ADR-015: Epic–Session–Worktree Alignment

## Context

### Problem

RaiSE epics vary wildly in scope — from 3-story quick wins to 20-story marathons
spanning weeks. Large epics cause three compounding problems:

1. **Context decay.** An AI agent session loses coherence as conversation context
   grows. Multi-session epics require expensive context restoration (journal
   replay, artifact re-reading), and each restoration is lossy.

2. **Sequential bottleneck.** When epics are large and monolithic, even
   independent work streams block on a single branch. Two developers (or two
   agent instances) cannot work on the same epic safely without merge conflicts.

3. **Late integration.** A 15-story epic that merges once at the end carries
   high integration risk. Smaller, complete units that merge independently are
   safer and provide earlier feedback.

### Observation

E1051 (Confluence Adapter v2) delivered 7 stories in a single session,
producing a complete, mergeable capability. Three stories were deferred —
not because of failure, but because they belonged to a different capability
(self-service configuration). The natural unit of delivery was not "all 10
stories" but "the transport capability" (7 stories).

This pattern repeated: E494 (ACLI Jira Adapter, 7 stories), E337 (Declarative
MCP Adapter, 5 stories), RAISE-829 (Jira Taxonomy, 7 stories). Each was
effectively one session, one capability, one merge.

### Principle at Stake

**Simplicity over Completeness** (RaiSE constitution): the smallest unit that
delivers a complete capability is the right size. Epics should not be larger
than necessary to produce a coherent, independently valuable result.

## Decision

### Align Epic scope to Session scope, isolated by Worktree

Adopt three constraints that together enable safe parallelism:

### C1: One Epic ≈ One Session

An epic SHOULD be scoped to complete within a single RaiSE session
(one developer + one agent instance, typically 2–8 hours of focused work,
5–9 stories).

**Sizing heuristic:** If an epic has more than ~9 stories or requires more
than one session to complete, it is likely two epics. Split along capability
boundaries, not arbitrary size limits.

**Exception:** Research epics and design epics may span sessions because their
output is documents, not code. The constraint applies to implementation epics.

### C2: One Epic = One Worktree

Each implementation epic executes in its own git worktree, branching from
the release branch. The worktree provides:

- **Isolation** — changes don't interfere with other concurrent work
- **Atomicity** — the epic either merges completely or not at all
- **Parallelism** — multiple worktrees run simultaneously on the same machine

```text
release/2.4.0  (base)
  ├── worktree: e1052-jira-adapter-v2/     (session A)
  ├── worktree: e1060-confluence-selfserv/  (session B, if independent)
  └── worktree: e1061-jira-selfserv/        (session C, if independent)
```

Story branches within the worktree follow the existing model
(story/s{N}.{M}/{name}), merging locally to the epic's worktree branch,
which then merges to the release branch.

### C3: Roadmap = Dependency Graph for Parallelism

Epic planning (via `/rai-epic-plan`) produces a dependency graph where:

- **Edges** represent data or API dependencies between epics
- **Independent epics** (no edges between them) CAN run in parallel worktrees
- **Dependent epics** MUST run sequentially — the predecessor merges before the
  successor starts

The roadmap is not just a priority list — it is a **parallelization schedule**.
The goal of sequencing is to minimize the critical path by maximizing the
number of epics that can run concurrently.

```text
Example: Adapter v2 Roadmap

Ronda 1 (sequential — transport dependency):
  └── E-1052: Jira Adapter v2              [worktree A]

Ronda 2 (parallel — independent self-service):
  ├── E-xxxx: Confluence Self-Service       [worktree B]
  └── E-yyyy: Jira Self-Service             [worktree C]  ← parallel

Ronda 3 (sequential — depends on doctor from Ronda 2):
  └── E-zzzz: Adapter Reliability           [worktree D]
```

## Consequences

### Positive

- **Predictable delivery.** Each epic is scoped to one session. No multi-week
  epics with uncertain completion dates.
- **Safe parallelism.** Worktrees provide git-level isolation. Two agent
  instances working concurrently cannot corrupt each other's state.
- **Earlier feedback.** Each epic merges independently. A capability is
  available to the rest of the system as soon as its epic completes, not when
  the entire roadmap finishes.
- **Context coherence.** The agent never needs to "pick up where it left off"
  across sessions for the same epic. The full epic context fits in one session.
- **Natural scope control.** The session constraint forces honest sizing. If it
  doesn't fit in a session, the epic is too big — split it.

### Negative

- **More epics.** What was one large epic becomes 2–4 smaller epics. More
  tracker entries, more scope documents, more retrospectives.
  **Mitigation:** The overhead per epic is small (~15 min for scope + retro).
  The alternative — multi-session epics with lossy context — is more expensive.

- **Dependency management overhead.** Parallel execution requires explicit
  dependency tracking. Implicit "it's all one epic" coordination goes away.
  **Mitigation:** `/rai-epic-plan` already produces dependency graphs. Making
  them inter-epic instead of intra-epic is a presentation change, not a
  conceptual one.

- **Merge ordering matters.** If epic B depends on epic A, B cannot start
  until A merges. A slow review on A blocks B.
  **Mitigation:** Keep epics small (one session) so review turnaround is fast.
  The merge-to-release gate already exists (ADR-033 branch model).

### Neutral

- **Worktree lifecycle.** Worktrees are created at epic start and cleaned up
  after merge. This is mechanical — `git worktree add` / `git worktree remove`.
  Claude Code's `--worktree` flag already supports this.

## Sizing Guide

| Stories | Sessions | Verdict |
|:-------:|:--------:|---------|
| 1–3     | < 1      | Fine — might be a story, not an epic |
| 4–9     | 1        | Ideal epic size |
| 10–12   | 1–2      | Acceptable if tightly coupled; consider split |
| 13+     | 2+       | Split required — find the capability boundary |

The split criterion is **capability boundary**, not arbitrary count:

- Can capability A be merged and used without capability B?
- Does capability B have a different consumer or different test strategy?
- Would a different developer/agent benefit from working on B independently?

If yes to any → split into separate epics.

## Relationship to Existing Process

| Concept | Before | After |
|---------|--------|-------|
| Epic scope | Variable (3–20 stories) | Bounded (~5–9 stories, one session) |
| Epic execution | Single branch, may span sessions | One worktree, one session |
| Roadmap | Priority-ordered list | Dependency graph enabling parallelism |
| Parallelism | Not formalized | Explicit: independent epics → concurrent worktrees |
| Story branches | From release branch | From worktree branch (merge locally, then to release) |

This ADR does NOT change:
- Story lifecycle (`/rai-story-start` through `/rai-story-close`)
- Branch model (ADR-033 — release branches, story branches)
- Gate requirements (tests, types, lint before commit)
- Epic artifacts (scope, design, plan, retrospective)
- Session lifecycle (`/rai-session-start`, `/rai-session-close`)

## Open Questions

1. **Worktree branch naming.** Should worktree branches follow a convention
   (e.g., `epic/e1052/jira-adapter-v2`) or reuse the release branch directly?
   Current branch model (ADR-033) says epics are logical containers, not
   branches. This ADR may need to revisit that.

2. **Cross-worktree dependencies at story level.** What if story S3 in epic B
   needs a utility introduced in epic A, but A hasn't merged yet? Options:
   cherry-pick, shared library extract, or simply wait. Needs dogfood data.

3. **Session duration variance.** "One session" is not a fixed time unit.
   A 4-hour focused session and an 8-hour exploratory session are both "one
   session." The constraint is cognitive (one context window), not temporal.

4. **Multiple agents per epic.** This ADR assumes one agent per worktree. Could
   two agents share a worktree for different stories within the same epic?
   Likely not safe without file-level locking. Defer to experience.
