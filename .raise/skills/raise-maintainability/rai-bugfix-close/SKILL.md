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
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.close
    context_source: all bug artifacts
    affected_modules: []
    max_tier1_queries: 1
    max_jit_queries: 1
    tier1_queries:
      - "close patterns and common merge issues"
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

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read bugfix-review's learning record at `.raise/rai/learnings/rai-bugfix-review/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Verify Completeness

Check all required artifacts exist:

```bash
SCOPE="work/bugs/RAISE-{N}/scope.md"
ANALYSIS="work/bugs/RAISE-{N}/analysis.md"
PLAN="work/bugs/RAISE-{N}/plan.md"
RETRO="work/bugs/RAISE-{N}/retro.md"
for f in "$SCOPE" "$ANALYSIS" "$PLAN" "$RETRO"; do
  [ -f "$f" ] && echo "✓ $f" || echo "ERROR: Missing $f"
done
```

| Condition | Action |
|-----------|--------|
| All 4 exist | Continue |
| Any missing | **STOP** — run the missing phase skill first |

<verification>
All 4 artifacts verified.
</verification>

### Step 2: Verify Clean Working Tree & Gates

Run **all four gates** before pushing. Resolve commands from `.raise/manifest.yaml` or use defaults (see `/rai-bugfix-fix` Step 1 for the full table):

1. **Tests** — `project.test_command` or language default
2. **Lint** — `project.lint_command` or language default
3. **Format** — `project.format_command` or language default
4. **Type check** — `project.type_check_command` or language default

```bash
git status --short
```

| Condition | Action |
|-----------|--------|
| Working tree clean + all gates green | Continue |
| Uncommitted changes from this bug | **Commit them** before push — artifacts must not be orphaned |
| Unrelated changes | Stash or commit separately with `chore:` prefix |
| Any gate failing | Fix before push — CI will reject the same errors |

**NEVER push with uncommitted bug artifacts.** Files created during the pipeline that aren't committed will be silently lost.

<verification>
Working tree clean. All four gates pass.
</verification>

### Step 3: Push & Create MR

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

<if-blocked>
`glab` not available → provide push URL for manual MR creation.
</if-blocked>

### Step 4: Cleanup & Transition

```bash
# Delete local branch
git checkout {dev_branch}
git branch -D bug/raise-{N}/{slug}

# Update tracker
rai backlog transition RAISE-{N} done -a jira

# Emit telemetry
rai signal emit-work bug RAISE-{N} --event complete
```

| Condition | Action |
|-----------|--------|
| Transition succeeds | Continue |
| Transition fails | Log warning and continue — backlog errors are **non-blocking** for lifecycle |

<verification>
Local branch deleted. Jira transitioned to Done. Telemetry emitted.
</verification>

<if-blocked>
Adapter not configured or transition fails → log and continue. Backlog sync is best-effort; it must never block bug close.
</if-blocked>

## Scope Constraints (CRITICAL)

Close is a **merge-request-only operation**. The following are explicitly forbidden:

- **NEVER edit source code, skill files, config, or governance docs** — close does not "fix" things
- **NEVER create "fix" or "refactor" commits** — if something looks wrong, report it; do not repair it
- **NEVER delete directories, worktrees, or files outside the bug branch** — close only deletes the merged bug branch
- **NEVER revert or modify commits already on `{dev_branch}`** — prior work is settled
- **NEVER rationalize unauthorized changes** — "this field looks wrong" is not a close concern

**Allowed writes during close (exhaustive list):**
1. Merge request (via `glab mr create`)
2. Signal/backlog CLI calls (side-effect only)
3. LEARN record

Anything not on this list is out of scope. If you believe something needs fixing, return it as a finding — do not act on it.

## Output

| Item | Destination |
|------|-------------|
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Jira transition | Done |
| Telemetry | Via `rai signal emit-work` |
| Next | — (pipeline complete) |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-close/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-close
work_id: {work_id}
version: "2.4.0"
timestamp: {ISO 8601 UTC}
primed_patterns: [{list of pattern IDs from PRIME}]
tier1_queries: {count}
tier1_results: {count}
jit_queries: {count}
pattern_votes:
  {PATTERN_ID}: {vote: 1|0|-1, why: "reason"}
gaps:
  - "description of missing knowledge"
artifacts: [{list of files produced}]
commit: {current commit hash or null}
branch: {current branch}
downstream: {}
```

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain.

## Quality Checklist

- [ ] All 4 artifacts verified before closing
- [ ] Working tree clean before push — no orphaned artifacts
- [ ] All four gates pass (test, lint, format, types)
- [ ] MR created in GitLab targeting `{dev_branch}`
- [ ] Local branch deleted after MR creation
- [ ] Jira transitioned to Done
- [ ] Telemetry emitted via `rai signal emit-work`
- [ ] No files modified outside scope constraints
- [ ] NEVER merge locally to `{dev_branch}` — always via MR
- [ ] NEVER edit source/skill/config files during close — MR only
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-close/{work_id}/record.yaml`

## References

- Previous: `/rai-bugfix-review`
- Complement: `/rai-bugfix-start`
- Branch model: `CLAUDE.md` § Branch Model
