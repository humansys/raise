# Research: Epics Without Epic Branches

> **Date:** 2026-03-03
> **Type:** research
> **Goal:** How modern teams handle epic-level grouping without long-lived epic branches

---

## Executive Summary

The industry consensus is clear: **long-lived epic branches are an anti-pattern**. High-performing teams (Google, Meta, Uber, Netflix, Amazon) use trunk-based development where stories merge directly to trunk/main. Epic coherence is maintained through a combination of: (1) epics as tracking labels in project tools, (2) feature flags for incomplete work, (3) branch by abstraction for large replacements, and (4) stacked PRs for related change sequences. Release control uses release branches or feature flags, never epic branches.

**Confidence: High** -- This is well-documented across DORA research, Google's monorepo papers, and industry practice.

---

## Evidence Catalog

### 1. Epics as Labels, Not Branches

**Finding:** Modern project tools (Jira, Linear, Shortcut) model epics as *tracking containers*, not branch structures. Stories within an epic are independently deployable.

**Key Evidence:**

| Claim | Source | Confidence |
|-------|--------|------------|
| Epics are large bodies of work broken into smaller stories; they are organizational, not branch-level constructs | [Atlassian: Epics, Stories, Initiatives](https://www.atlassian.com/agile/project-management/epics-stories-themes) | Very High |
| Linear uses "Projects" (time-bound deliverables) and "Initiatives" (cross-project goals) -- neither maps to a branch | [Linear Docs: Concepts](https://linear.app/docs/conceptual-model), [Linear Docs: Projects](https://linear.app/docs/projects) | Very High |
| Linear's git integration links issues to branches per-story, auto-updating status as PRs move through lifecycle | [Linear Docs: Concepts](https://linear.app/docs/conceptual-model) | Very High |
| Shortcut defines Epics as collections of Stories spanning multiple Workflows and Teams -- purely organizational | [Shortcut Help: What is an Epic](https://help.shortcut.com/hc/en-us/articles/360017524632-What-is-an-Epic) | Very High |
| Linear Initiatives can nest up to 5 levels deep for enterprise hierarchy (OKRs, workstreams, goals) | [Linear Changelog: Sub-initiatives](https://linear.app/changelog/2025-07-10-sub-initiatives) | High |

**How they maintain coherence:**
- Epic/Project dashboards show aggregate progress across stories
- Labels, milestones, and parent-child relationships in the tracker
- Each story is CIT: Complete, Independent, Testable
- Stories are ordered by dependency in the backlog; each delivers incremental value

**How they handle partial epic delivery:**
- Feature flags hide incomplete user-facing functionality
- Stories deliver backend/infrastructure work that is inert without the flag
- Release notes group by epic label, not by branch
- "Epic done" = all stories done in tracker, not a branch merge

**Pattern:** Epic is a *planning* and *tracking* concept. The branch model is story-level only.

---

### 2. Stacked PRs / Graphite / ghstack

**Finding:** Stacked PRs are a tactical tool for breaking large *stories* into reviewable chunks. They complement trunk-based development but do not replace epic-level organization.

**Key Evidence:**

| Claim | Source | Confidence |
|-------|--------|------------|
| Stacked diffs: series of small, dependent changes atop one another, reviewed and merged independently | [Graphite: Stacked Diffs Guide](https://graphite.com/guides/stacked-diffs) | Very High |
| Tools: Graphite, ghstack, git-town, Sapling (Meta), spr | [Awesome Code Reviews: Stacked PRs Guide](https://www.awesomecodereviews.com/best-practices/stacked-prs/) | High |
| Asana engineers save up to 7 hours/week on code reviews with Graphite stacking | [Graphite Blog: Stacked PRs](https://graphite.com/blog/stacked-prs) | High |
| Semgrep uses Graphite to separate refactors from feature work within a single logical change | [Graphite: Semgrep Case Study](https://graphite.com/customer/semgrep) | High |
| When feedback arrives late on a base PR, everything above must be rebased -- cascading overhead | [Qodo Blog: Graphite Alternatives](https://www.qodo.ai/blog/graphite-alternatives/) | Medium |

**Relationship to epics:**
- Stacked PRs group related changes *within a single story or task*
- They solve the "1000-line PR" problem, not the "multi-story epic" problem
- A stack typically lives 1-3 days, not weeks
- Multiple stacks from different stories may contribute to the same epic, but the epic grouping is in the tracker, not in the stack

**Trade-offs:**
- (+) Faster reviews, unblocked development, parallel review
- (+) Natural ordering of changes (refactor -> implement -> test)
- (-) Cascade rebases when base PR changes
- (-) Team must learn new tooling and mental model
- (-) Not a replacement for epic-level coordination

---

### 3. Feature Flags vs Feature Branches

**Finding:** Feature flags are the primary mechanism that enables trunk-based development for multi-story work. They replace the *isolation* that epic branches provide.

**Key Evidence:**

| Claim | Source | Confidence |
|-------|--------|------------|
| Feature flags allow deploying new features incrementally, controlling exposure without long-lived branches | [Statsig: Feature Flags vs Feature Branches](https://www.statsig.com/perspectives/feature-flags-vs-feature-branches) | Very High |
| Feature flags wrap incomplete work so trunk is always deployable; the application behaves as if code hasn't been merged | [trunkbaseddevelopment.com: Feature Flags](https://trunkbaseddevelopment.com/feature-flags/) | Very High |
| Feature flags are intended to be temporary/short-lived; long-lived flags create technical debt | [Dave Farley: Feature Flags](https://www.davefarley.net/?p=255) | Very High |
| Flag cleanup strategies: monthly reviews, "Flag Cleanup Days", auto-failing builds for old flags | [LaunchDarkly: Technical Debt](https://launchdarkly.com/docs/guides/flags/technical-debt), [DevCycle: Tech Debt](https://docs.devcycle.com/best-practices/tech-debt/) | High |
| Combined approach: short-lived branches + feature flags for features that can't be atomically delivered | [Harness: Feature Flags vs Feature Branches](https://www.harness.io/blog/feature-flags-vs-feature-branches) | High |

**Feature flag lifecycle for epic-sized work:**

```
1. Create flag (e.g., `enable-new-checkout-flow`)
2. Stories merge to trunk behind flag (flag OFF in production)
3. Each story is independently testable with flag ON in dev/staging
4. When all stories complete -> enable flag progressively (canary -> % rollout -> 100%)
5. When stable -> remove flag and dead code (cleanup sprint/day)
```

**Branch by Abstraction** (for infrastructure/library replacements):

```
1. Introduce abstraction layer over existing code
2. Redirect all clients to use abstraction (multiple commits, all safe)
3. Build new implementation behind abstraction (turned off)
4. Switch to new implementation
5. Remove old implementation + abstraction
```

Source: [trunkbaseddevelopment.com: Branch by Abstraction](https://trunkbaseddevelopment.com/branch-by-abstraction/), [Martin Fowler: Branch By Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)

**Trade-offs:**

| Feature Flags | Epic Branches |
|--------------|---------------|
| (+) Trunk always deployable | (-) Merge hell on long-lived branch |
| (+) Incremental delivery possible | (-) All-or-nothing delivery |
| (+) Runtime control (canary, rollback) | (-) Rollback = revert merge |
| (-) Flag tech debt accumulates | (+) No flag cleanup needed |
| (-) Requires flag infrastructure | (+) No additional tooling |
| (-) Code complexity (conditionals) | (+) Cleaner code on branch |

---

### 4. Linear, Shortcut, and Modern Project Tools

**Finding:** Modern project tools explicitly decouple work organization from branching. None of them encourage epic branches.

**Key Evidence:**

| Tool | Work Hierarchy | Git Model | Source |
|------|---------------|-----------|--------|
| **Linear** | Initiative > Project > Issue | Branch per issue, auto-linked via integration | [Linear Docs](https://linear.app/docs/conceptual-model) |
| **Shortcut** | Epic > Story > Task | Branch per story | [Shortcut Help](https://help.shortcut.com/hc/en-us/articles/360017524632-What-is-an-Epic) |
| **Jira** | Initiative > Epic > Story > Subtask | No built-in branch model (integration-dependent) | [Atlassian](https://www.atlassian.com/agile/project-management/epics) |
| **GitHub** | Milestone > Issue | Branch per issue/PR | GitHub docs |

**Key insight:** These tools use *progress aggregation* (% complete, burn-down, status boards) to give epic-level visibility. The branch is irrelevant to the epic -- what matters is whether all stories are Done.

---

### 5. Monorepo Teams (Google, Meta, Uber)

**Finding:** Large-scale trunk-based teams use atomic commits, feature flags, and code ownership -- never long-lived feature branches.

**Key Evidence:**

| Claim | Source | Confidence |
|-------|--------|------------|
| Google, Meta, Netflix, Amazon, Shopify all use trunk-based development | [DORA: Trunk-Based Development](https://dora.dev/capabilities/trunk-based-development/) | Very High |
| Google's monorepo uses atomic commits across multiple modules in a single trunk | [ACM: Why Google Stores Billions of Lines of Code in a Single Repository](https://m-cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext) | Very High |
| Meta developed Sapling (stacked commits tool) for their monorepo workflow | [Awesome Code Reviews: Stacked PRs](https://www.awesomecodereviews.com/best-practices/stacked-prs/) | High |
| Branches must last no more than a couple of days; longer risks becoming a long-lived branch | [trunkbaseddevelopment.com: Short-Lived Feature Branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/) | Very High |
| Break work into multiple PRs sharing the same story association but different branch names | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) | High |

**How monorepo teams group multi-story work:**

1. **Tracking layer**: Jira/internal tool tracks epic progress across stories
2. **Code ownership**: OWNERS/CODEOWNERS files ensure reviews from domain experts
3. **Feature flags**: Gating new functionality behind runtime flags
4. **Atomic commits**: Cross-module changes land atomically in trunk
5. **Build system**: Hermetic builds ensure each commit is independently buildable
6. **No integration branch**: There is no "develop" or "epic" branch. Trunk IS the integration point.

---

### 6. Release Trains and Epic Delivery

**Finding:** If stories merge to trunk independently, release control happens at the *release* layer, not the *epic* layer.

**Key Evidence:**

| Claim | Source | Confidence |
|-------|--------|------------|
| Release branches cut from trunk at a point-in-time for stabilization | [trunkbaseddevelopment.com: Styles and Trade-offs](https://trunkbaseddevelopment.com/styles/) | Very High |
| Feature flags allow partial epic delivery: done stories are live, WIP stories are hidden | [Unleash: Trunk-Based Development](https://docs.getunleash.io/guides/trunk-based-development) | High |
| DORA research shows trunk-based development correlates with higher deployment frequency and lower change failure rate | [DORA](https://dora.dev/capabilities/trunk-based-development/) | Very High |

**Release patterns without epic branches:**

```
Pattern A: Feature Flag Gating
- All stories merge to trunk behind flag
- Flag controls release independently of deployment
- Release = "turn on the flag" (not "merge the branch")

Pattern B: Release Branch
- Cut release branch from trunk when ready
- Only bug fixes cherry-picked to release branch
- Epic "done" = all stories in trunk before cut point

Pattern C: Release Train
- Fixed cadence (e.g., every 2 weeks)
- Whatever is in trunk and flag-enabled ships
- Incomplete epics ship what's done; rest waits for next train
- No code freeze needed if flags gate incomplete work
```

---

## Synthesis: The Modern Model

```
                    PLANNING LAYER (Jira/Linear/Shortcut)
                    ====================================
                    Initiative
                        |
                    Epic (label/container)
                       / | \
                  Story  Story  Story    <-- each independently deliverable
                    |      |      |

                    GIT LAYER (trunk-based)
                    =======================
                    main/trunk
                      ^  ^  ^
                      |  |  |
                    PR-1 PR-2 PR-3       <-- short-lived branches (hours/days)
                    (may use stacked PRs within a story)

                    RUNTIME LAYER (feature flags)
                    ============================
                    flag: enable-new-checkout
                      OFF in prod until epic complete
                      ON in staging for testing
                      Gradual rollout when ready
```

**Key principles:**
1. **Epics are a planning concern**, not a branching concern
2. **Each story merges to trunk independently** via short-lived branch + PR
3. **Feature flags provide the isolation** that epic branches used to provide
4. **Release control is orthogonal** to epic completion
5. **Branch by abstraction** handles large infrastructure replacements
6. **Stacked PRs** handle large stories, not large epics

---

## Implications for RaiSE

Current model: `main -> dev -> epic/eN/name -> story/sN.M/name`

The evidence strongly suggests the epic branch layer adds friction without proportional value. Options to consider:

| Option | Model | Trade-off |
|--------|-------|-----------|
| **A: Keep as-is** | epic branches isolate epic work | Merge conflicts, stale branches, integration debt |
| **B: Drop epic branches** | `main -> dev -> story/sN.M/name` | Stories merge to dev directly; epic is label-only in backlog |
| **C: Drop epic AND dev** | `main -> story/sN.M/name` | Full trunk-based; requires feature flags for WIP |
| **D: Hybrid** | Epic branches only for high-risk/multi-week work; default is B | Pragmatic but inconsistent |

**Recommendation:** Option B is the lowest-risk improvement. It preserves the dev branch as an integration safety net while eliminating the epic branch layer. Epic tracking moves entirely to the backlog tool. Feature flags can be adopted incrementally for cases where partial delivery is visible to users.

---

## Sources

1. [Atlassian: Epics, Stories, and Initiatives](https://www.atlassian.com/agile/project-management/epics-stories-themes)
2. [Linear Docs: Conceptual Model](https://linear.app/docs/conceptual-model)
3. [Linear Docs: Projects](https://linear.app/docs/projects)
4. [Linear Changelog: Sub-initiatives](https://linear.app/changelog/2025-07-10-sub-initiatives)
5. [Shortcut Help: What is an Epic](https://help.shortcut.com/hc/en-us/articles/360017524632-What-is-an-Epic)
6. [Graphite: Stacked Diffs Guide](https://graphite.com/guides/stacked-diffs)
7. [Graphite Blog: Stacked PRs](https://graphite.com/blog/stacked-prs)
8. [Graphite: Semgrep Case Study](https://graphite.com/customer/semgrep)
9. [Awesome Code Reviews: Stacked PRs](https://www.awesomecodereviews.com/best-practices/stacked-prs/)
10. [trunkbaseddevelopment.com: Feature Flags](https://trunkbaseddevelopment.com/feature-flags/)
11. [trunkbaseddevelopment.com: Branch by Abstraction](https://trunkbaseddevelopment.com/branch-by-abstraction/)
12. [trunkbaseddevelopment.com: Short-Lived Feature Branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/)
13. [Martin Fowler: Branch By Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)
14. [Dave Farley: Feature Flags](https://www.davefarley.net/?p=255)
15. [DORA: Trunk-Based Development](https://dora.dev/capabilities/trunk-based-development/)
16. [ACM: Why Google Stores Billions of Lines of Code in a Single Repository](https://m-cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
17. [Statsig: Feature Flags vs Feature Branches](https://www.statsig.com/perspectives/feature-flags-vs-feature-branches)
18. [Harness: Feature Flags vs Feature Branches](https://www.harness.io/blog/feature-flags-vs-feature-branches)
19. [LaunchDarkly: Technical Debt from Feature Flags](https://launchdarkly.com/docs/guides/flags/technical-debt)
20. [DevCycle: Managing Tech Debt](https://docs.devcycle.com/best-practices/tech-debt/)
21. [Trisha Gee: Why I Prefer Trunk-Based Development](https://trishagee.com/2023/05/29/why-i-prefer-trunk-based-development/)
22. [Unleash: Trunk-Based Development Guide](https://docs.getunleash.io/guides/trunk-based-development)
23. [stacking.dev: The Stacking Workflow](https://www.stacking.dev/)
24. [Qodo Blog: Graphite Alternatives](https://www.qodo.ai/blog/graphite-alternatives/)
