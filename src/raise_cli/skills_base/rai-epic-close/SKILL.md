---
name: rai-epic-close
description: >
  Complete an epic with retrospective, metrics capture, and tracking update.
  No branch merge — epics are logical containers. Story branches merge
  directly to the development branch during story-close.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "9"
  raise.prerequisites: all stories complete
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - all_retrospectives: boolean, required, git
    - dev_branch: string, required, config
  raise.outputs: |
    - retrospective: file_path, file
    - tag: string, git
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

### Step 1: Verify Stories Complete

Check all stories are done in the epic scope document:

```bash
grep -E "^\s*-\s*\[ \]" "work/epics/e{N}-{name}/scope.md"
```

| Condition | Action |
|-----------|--------|
| All stories checked | Continue |
| Incomplete stories | Complete them first or explicitly descope |

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

### Step 4: Update Backlog & Context

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
| Backlog update | Tracker via `rai backlog` CLI |

## Quality Checklist

- [ ] All stories complete before closing (gate)
- [ ] Tests pass before closing
- [ ] Retrospective captures metrics, patterns, and process insights
- [ ] Epic milestone tagged on `{dev_branch}`
- [ ] Backlog updated via `rai backlog transition` CLI
- [ ] No epic branch to clean up — epics are logical containers
- [ ] NEVER close without retrospective — learnings compound across epics

## References

- Retrospective template: `templates/retrospective.md`
- Previous: All `/rai-story-close` completions
- Backlog: `rai backlog` CLI
- Next: `/rai-epic-design` for next epic
