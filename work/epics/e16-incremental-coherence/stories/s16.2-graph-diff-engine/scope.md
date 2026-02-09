# S16.2: Graph Diff Engine

> **Status:** In Progress
> **Size:** M
> **Epic:** E16 Incremental Coherence
> **Branch:** `story/s16.2/graph-diff-engine`
> **Depends on:** S16.1 (Code-Aware Graph), S16.5 (Component ID Uniqueness)

---

## In Scope

- `diff_graphs(old, new)` pure function comparing two unified graphs
- `NodeChange` and `EdgeChange` Pydantic models for structured diff output
- `GraphDiff` model with impact classification (none/frontmatter/structural/architectural)
- `affected_modules` derivation from change set
- `raise memory build --diff` CLI flag: build new graph, diff against previous, persist diff
- Diff persistence as JSON artifact alongside unified graph
- Conservative change detection to minimize false positives

## Out of Scope

- AI-generated summaries (deferred to S16.3 `/docs-update`)
- Doc updates from diff (S16.3)
- Lifecycle wiring (S16.4)
- Watch mode / real-time detection
- Cross-project diffing

## Done Criteria

- [ ] `diff_graphs()` correctly detects added, removed, and modified nodes
- [ ] `diff_graphs()` correctly detects added, removed, and modified edges
- [ ] Impact classification works (none → frontmatter → structural → architectural)
- [ ] `affected_modules` correctly derived from changes
- [ ] `raise memory build --diff` CLI integration works end-to-end
- [ ] Diff persisted as JSON artifact
- [ ] Tests pass with >90% coverage on new code
- [ ] Tested against real raise-commons graph snapshots
- [ ] All quality gates pass (ruff, pyright, bandit)
- [ ] Retrospective complete
