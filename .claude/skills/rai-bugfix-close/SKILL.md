---
name: rai-bugfix-close
description: Push branch, create MR, transition Jira to Done. Phase 7 of bugfix pipeline.

allowed-tools:
  - Read
  - "Bash(git:*)"
  - "Bash(glab:*)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '7'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: bugfix-review
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - mr_url: string, terminal
---

# Bugfix Close

## Purpose

Push the bug branch, create a merge request targeting the development branch, clean up the local branch, and transition Jira to Done. This is the final phase — all artifacts must exist before closing.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify all 4 artifacts, create MR
- **Ha**: Streamline for batch closures
- **Ri**: Automated close with CI/CD integration

## Context

**When to use:** After `/rai-bugfix-review` has produced the retrospective artifact.

**When to skip:** Never — closing is how bug work becomes visible to the team.

**Inputs:** Bug ID, `{dev_branch}` from `.raise/manifest.yaml`.

**Expected state:** On bug branch. All artifacts exist (scope.md, analysis.md, plan.md, retro.md). All gates pass.

## Steps

### Step 1: Verify Completeness

Check all required artifacts exist:

```bash
ls work/bugs/RAISE-{N}/scope.md
ls work/bugs/RAISE-{N}/analysis.md
ls work/bugs/RAISE-{N}/plan.md
ls work/bugs/RAISE-{N}/retro.md
```

| Condition | Action |
|-----------|--------|
| All 4 exist | Continue |
| Any missing | **STOP** — run the missing phase skill first |

<verification>
All 4 artifacts verified.
</verification>

### Step 2: Push & Create MR

**Never merge locally to `{dev_branch}`.** Push the bug branch and create a merge request.

```bash
# Push bug branch to origin
git push origin bug/raise-{N}/{slug} -u

# Create merge request via glab
glab mr create \
  --source-branch bug/raise-{N}/{slug} \
  --target-branch {dev_branch} \
  --title "fix(RAISE-{N}): {summary}" \
  --description "Root cause: {one line}

Co-Authored-By: Rai <rai@humansys.ai>" \
  --no-editor
```

If `glab` is not available, provide the GitLab URL from `git push` output for manual MR creation.

<verification>
MR created in GitLab targeting `{dev_branch}`.
</verification>

### Step 3: Cleanup & Transition

```bash
# Delete local branch
git checkout {dev_branch}
git branch -D bug/raise-{N}/{slug}

# Update tracker
rai backlog transition RAISE-{N} done -a jira
```

<verification>
Local branch deleted. Jira transitioned to Done.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Jira transition | Done |
| Next | — (pipeline complete) |

## Quality Checklist

- [ ] All 4 artifacts verified before closing
- [ ] MR created in GitLab targeting `{dev_branch}`
- [ ] Local branch deleted after MR creation
- [ ] Jira transitioned to Done
- [ ] NEVER merge locally to `{dev_branch}` — always via MR

## References

- Previous: `/rai-bugfix-review`
- Complement: `/rai-bugfix-start`
- Branch model: `CLAUDE.md` § Branch Model
