---
name: rai-bugfix-start
description: Initialize bug branch, reproduce, and create scope artifact. Phase 1 of bugfix pipeline.

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
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-triage
  raise.prerequisites: ''
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument (e.g. RAISE-251)
    - dev_branch: string, required, config
  raise.outputs: |
    - bug_branch: string, next_skill
    - scope_md: file_path, next_skill
---

# Bugfix Start

## Purpose

Create a bug branch from the development branch, reproduce the bug, and write the scope artifact that defines what the bug is and when it's fixed.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, reproduce bug, create scope with all 5 fields
- **Ha**: Streamline scope for well-understood bugs
- **Ri**: Custom initialization patterns for specific domains

## Context

**When to use:** A tracked bug (Jira issue) needs formal resolution with branch, artifacts, and traceability.

**When to skip:** Trivial fix (typo, obvious one-liner) — commit directly. Already started (scope.md exists).

**Inputs:** Bug ID (e.g., RAISE-251), problem statement or reproduction steps.

**Expected state:** On `{dev_branch}`, up to date with remote. No `work/bugs/RAISE-{N}/` directory yet.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`.

## Steps

### Step 1: Create Bug Branch

```bash
git checkout {dev_branch} && git pull origin {dev_branch}
git checkout -b bug/raise-{N}/{bug-slug}
```

Update the tracker immediately — assign to yourself and move to In Progress:

```bash
rai backlog update RAISE-{N} --assignee "{developer-email}" -a jira
rai backlog transition RAISE-{N} in-progress -a jira
```

Use the developer's Jira email from memory or session context. If not known, ask before proceeding.

<verification>
On `bug/raise-{N}/{slug}` branch. Jira issue assigned and In Progress.
</verification>

### Step 2: Reproduce & Write Scope

Reproduce the bug — confirm it is observable. Write `work/bugs/RAISE-{N}/scope.md`:

```
WHAT:      [behavior observed]
WHEN:      [conditions / triggers]
WHERE:     [file:line or component]
EXPECTED:  [correct behavior]
Done when: [specific observable outcome]
```

Commit the scope artifact:

```bash
git add work/bugs/RAISE-{N}/scope.md
git commit -m "bug(RAISE-{N}): initialize scope

WHAT: {summary}
Done when: {criteria}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Bug reproduces. Scope artifact committed on bug branch.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Bug branch | `bug/raise-{N}/{slug}` from `{dev_branch}` |
| Scope artifact | `work/bugs/RAISE-{N}/scope.md` |
| Backlog update | Jira assigned + In Progress |
| Next | `/rai-bugfix-triage` |

## Quality Checklist

- [ ] Bug branch created from `{dev_branch}`
- [ ] Jira issue assigned and transitioned to In Progress
- [ ] Bug reproduces before any investigation
- [ ] Scope artifact committed with WHAT/WHEN/WHERE/EXPECTED/Done-when
- [ ] NEVER investigate before reproducing

## References

- Next: `/rai-bugfix-triage`
- Complement: `/rai-bugfix-close`
- Branch model: `CLAUDE.md` § Branch Model
