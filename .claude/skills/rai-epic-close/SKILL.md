---
name: rai-epic-close
description: Close epic with retrospective, push, and merge request. Use after all stories done.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "9"
  raise.prerequisites: all stories complete
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.1.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - all_retrospectives: boolean, required, git
    - dev_branch: string, required, config
  raise.outputs: |
    - retrospective: file_path, file
    - tag: string, git
  raise.aspects: introspection
  raise.introspection:
    phase: epic.close
    context_source: all epic artifacts
    affected_modules: []
    max_tier1_queries: 2
    max_jit_queries: 3
    tier1_queries:
      - "retrospective patterns for {domain} epics"
      - "process improvement patterns from similar epics"
---

# Epic Close

## Purpose

Complete an epic by conducting a retrospective, tagging the milestone, and updating tracking. No branch merge needed — stories already merged to the development branch during story-close.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, complete full retrospective template
- **Ha**: Adjust retrospective depth based on epic complexity
- **Ri**: Integrate with release workflows, automate metrics extraction

## Context

**When to use:** All stories complete and merged to `{dev_branch}`. Ready to close the epic lifecycle.

**When to skip:** Epic abandoned (document why, update backlog as "Abandoned").

**Inputs:** Epic scope document, all story retrospectives, passing test suite.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

> **PRIME**: Before Step 1, follow PRIME protocol in `aspects/introspection.md`.
> Chain read: read ALL learning records from this epic's skills (epic-design, epic-plan, and all story records).
> This provides the aggregate view for the retrospective.

### Step 1: Verify Stories Complete

Check all stories are done in the epic scope document:

```bash
grep -E "^\s*-\s*\[ \]" "work/epics/e{N}-{name}/scope.md"
```

| Condition | Action |
|-----------|--------|
| All stories checked | Continue |
| Incomplete stories | Complete them first or explicitly descope |

> **JIT**: Before descoping decisions, query graph for completion patterns and prior descoping outcomes
> → `aspects/introspection.md § JIT Protocol`

<verification>
All stories marked complete in epic scope.
</verification>

### Step 2: Run Tests & Write Retrospective

Determine which test command to run using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command` — if set, use it directly (configuration over convention)
2. **Detect language** from `project.project_type` in manifest, or scan file extensions of changed files (`git diff --name-only`)
3. **Map language to default** using the table below

| Language | Extensions | Default Test Command |
|----------|-----------|----------------------|
| Python | `.py`, `.pyi` | `uv run pytest --tb=short` |
| TypeScript | `.ts`, `.tsx` | `npx vitest run` or `npm test` |
| JavaScript | `.js`, `.jsx` | `npx vitest run` or `npm test` |
| C# | `.cs` | `dotnet test --verbosity quiet` |
| Go | `.go` | `go test ./...` |
| PHP | `.php` | `vendor/bin/phpunit` |
| Dart | `.dart` | `flutter test` |
| Unknown | — | Ask developer |

The table is a **fallback** — `project.test_command` always wins when present.

> **JIT**: Before writing retrospective, query graph for process improvement patterns from similar epics
> → `aspects/introspection.md § JIT Protocol`

Create retrospective at `work/epics/e{N}-{name}/retrospective.md` using `templates/retrospective.md`. Fill from story retrospectives and git history.

<verification>
Tests green. Retrospective created with metrics, patterns, and process insights.
</verification>

<if-blocked>
Tests failing → fix before closing.
</if-blocked>

### Step 3: Tag Epic Milestone

Tag the current `{dev_branch}` HEAD to mark epic completion:

```bash
git tag -a "epic/e{N}-complete" -m "Epic E{N}: {Epic Name} complete

Delivered: [key deliverables]
Stories: N stories

Co-Authored-By: Rai <rai@humansys.ai>"
```

Commit retrospective and any final artifacts:

```bash
git add -A
git commit -m "epic(e{N}): close with retrospective

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Tag created. Retrospective committed.
</verification>

### Step 4: Push and Create Merge Request

Push `{dev_branch}` to origin and create a merge request. This is the single MR for the entire epic — all stories were merged locally during `/rai-story-close`.

```bash
# Push dev with all epic commits
git push origin {dev_branch}

# Create merge request via glab (dev → main for releases, or just push dev)
glab mr create \
  --source-branch {dev_branch} \
  --target-branch {main_branch} \
  --title "epic(e{N}): {Epic Name}" \
  --description "## Epic E{N}: {Epic Name}

### Stories delivered
- S{N}.1: {name}
- S{N}.2: {name}
- ...

### Key changes
- {summary of deliverables}

### Retrospective
- {top learnings}

Co-Authored-By: Rai <rai@humansys.ai>" \
  --no-editor
```

Present the MR URL to the developer for review.

| Condition | Action |
|-----------|--------|
| MR to main needed | Create MR as above |
| No release planned | Push dev only, skip MR to main |
| `glab` not available | Provide the GitLab URL from `git push` output for manual MR creation |
| Push rejected | `git pull --rebase origin {dev_branch}`, resolve conflicts, push again |

<verification>
Dev pushed to origin. MR created if targeting main. MR URL presented to developer.
</verification>

### Step 5: Update Backlog & Context

1. Mark epic complete via CLI:
   - **If Jira issue exists:** `rai backlog transition {JIRA_KEY} "Done" -a jira`
   - **If no Jira key:** `rai backlog search "summary ~ '{epic name}'" -a jira` to find it, then transition
2. Emit telemetry:

```bash
rai signal emit-work epic E{N} --event complete
```

<verification>
Backlog reflects completion. Local context updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/epics/e{N}-{name}/retrospective.md` |
| Tag | `epic/e{N}-complete` on `{dev_branch}` |
| Push | `{dev_branch}` pushed to origin |
| Merge request | GitLab MR: `{dev_branch}` → `{main_branch}` (if release) |
| Backlog update | Tracker via `rai backlog` CLI |

> **LEARN**: After completing Step 5, follow LEARN protocol in `aspects/introspection.md`.
> Record path: `.raise/rai/learnings/rai-epic-close/{work_id}/record.yaml`
> This is the final record in the epic chain — include aggregate learning summary.

## Quality Checklist

- [ ] All stories complete before closing (gate)
- [ ] Tests pass before closing
- [ ] Retrospective captures metrics, patterns, and process insights
- [ ] Epic milestone tagged on `{dev_branch}`
- [ ] Dev pushed to origin with all epic commits
- [ ] Merge request created if targeting main (epic-level MR, not per story)
- [ ] Backlog updated via `rai backlog transition` CLI
- [ ] No epic branch to clean up — epics are logical containers
- [ ] NEVER close without retrospective — learnings compound across epics
- [ ] NEVER create per-story MRs — one MR per epic at close time

## References

- Retrospective template: `templates/retrospective.md`
- Previous: All `/rai-story-close` completions
- Backlog: `rai backlog` CLI
- Next: `/rai-epic-design` for next epic
