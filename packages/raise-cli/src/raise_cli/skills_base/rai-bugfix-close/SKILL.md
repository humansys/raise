---
name: rai-bugfix-close
description: Push branch, create MR, verify artifacts complete. Phase 7 of bugfix pipeline.

allowed-tools:
  - Read
  - "Bash(git:*)"
  - "Bash(glab:*)"

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

Push the bug branch, create a merge request targeting the development branch, and clean up the local branch. All artifacts must exist before closing.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify all 4 artifacts, create MR
- **Ha**: Streamline for batch closures
- **Ri**: Automated close with CI/CD integration

## Context

**When to use:** After `/rai-bugfix-review` has produced the retrospective artifact.

**When to skip:** Never — closing is how bug work becomes visible to the team.

**Inputs:** Bug ID, `{dev_branch}` from `.raise/manifest.yaml`.

**Expected state:** On bug branch. All artifacts exist (scope.md, analysis.md, plan.md, retro.md). Gates passed in fix phase.

## Steps

### Step 1: Verify Completeness & Clean Tree

Check all required artifacts exist and working tree is clean:

```bash
for f in scope.md analysis.md plan.md retro.md; do
  [ -f "work/bugs/RAISE-{N}/$f" ] && echo "✓ $f" || echo "ERROR: Missing $f"
done
git status --short
```

| Condition | Action |
|-----------|--------|
| All 4 artifacts + clean tree | Continue |
| Any artifact missing | **STOP** — run the missing phase skill first |
| Uncommitted changes | Commit them before push |

<verification>
All 4 artifacts verified. Working tree clean.
</verification>

### Step 2: Push & Create MR

**Never merge locally to `{dev_branch}`.**

```bash
git push origin bug/raise-{N}/{slug} -u

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

<if-blocked>
`glab` not available → provide push URL for manual MR creation.
</if-blocked>

### Step 3: Cleanup

```bash
git checkout {dev_branch}
git branch -D bug/raise-{N}/{slug}
```

<verification>
Local branch deleted.
</verification>

## Scope Constraints (CRITICAL)

Close is a **merge-request-only operation**:

- **NEVER edit source code, skill files, config, or governance docs**
- **NEVER create "fix" or "refactor" commits**
- **NEVER delete directories or files outside the bug branch**
- **NEVER revert or modify commits on `{dev_branch}`**

If something looks wrong, return it as a finding — do not act on it.

## Output

| Item | Destination |
|------|-------------|
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Next | — (pipeline complete) |

## Quality Checklist

- [ ] All 4 artifacts verified before closing
- [ ] Working tree clean before push
- [ ] MR created in GitLab targeting `{dev_branch}`
- [ ] Local branch deleted after MR creation
- [ ] No files modified outside scope constraints
- [ ] NEVER merge locally to `{dev_branch}` — always via MR

## References

- Previous: `/rai-bugfix-review`
- Complement: `/rai-bugfix-start`
- Branch model: `CLAUDE.md` § Branch Model
