---
name: rai-bugfix-triage
description: Classify bug in 4 dimensions and set Jira custom fields. Phase 2 of bugfix pipeline.

allowed-tools:
  - Read
  - Edit
  - Write
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-bug
  raise.gate: hitl
  raise.next: bugfix-analyse
  raise.prerequisites: bugfix-start
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - triage_block: string, next_skill
---

# Bugfix Triage

## Purpose

Classify the bug in 4 orthogonal dimensions (ODC-inspired) and persist classification to both the scope artifact and Jira custom fields. This is the highest-leverage phase — misclassification cascades through all subsequent phases.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, classify all 4 dimensions, set all Jira fields
- **Ha**: Pre-classify from bug report patterns; adjust if uncertain
- **Ri**: Domain-specific triage taxonomies

## Context

**When to use:** After `/rai-bugfix-start` has produced `scope.md` with WHAT/WHEN/WHERE/EXPECTED.

**When to skip:** Never — triage is mandatory. Even trivial bugs need classification for queryable data.

**Inputs:** Bug ID, `work/bugs/RAISE-{N}/scope.md` without TRIAGE block.

**Expected state:** On bug branch. Scope artifact exists and bug reproduces.

## Steps

### Step 1: Classify in 4 Dimensions

Classify the bug **before any analysis** — classify what you see, not what you think caused it:

| Dimension | Values |
|-----------|--------|
| **Bug Type** | Functional, Interface, Data, Logic, Configuration, Regression |
| **Severity** | S0-Critical, S1-High, S2-Medium, S3-Low |
| **Origin** | Requirements, Design, Code, Integration, Environment |
| **Qualifier** | Missing, Incorrect, Extraneous |

Append to `work/bugs/RAISE-{N}/scope.md`:

```
TRIAGE:
  Bug Type:    [Functional|Interface|Data|Logic|Configuration|Regression]
  Severity:    [S0-Critical|S1-High|S2-Medium|S3-Low]
  Origin:      [Requirements|Design|Code|Integration|Environment]
  Qualifier:   [Missing|Incorrect|Extraneous]
```

<verification>
4 dimensions classified in scope artifact.
</verification>

### Step 2: Set Jira Custom Fields

Update Jira — set the 4 classification custom fields via MCP. Map Severity to Jira format (`S{N}-Label` → `Sev-{N}`) and Origin Environment → `Enviroment` (Jira typo):

```
mcp__atlassian__jira_update_issue(
  issue_key = "RAISE-{N}",
  additional_fields = '{"customfield_13267": {"value": "{Bug Type}"}, "customfield_12090": {"value": "Sev-{N}"}, "customfield_13269": {"value": "{Origin}"}, "customfield_13270": {"value": "{Qualifier}"}}'
)
```

> **Field IDs:** Bug Type = `customfield_13267`, Severity = `customfield_12090`, Origin = `customfield_13269`, Qualifier = `customfield_13270`.

Then transition:

```bash
rai backlog transition RAISE-{N} triaged -a jira
```

<verification>
Jira fields set. Issue transitioned to Triaged.
</verification>

### Step 3: Commit Classification

```bash
git add work/bugs/RAISE-{N}/scope.md
git commit -m "bug(RAISE-{N}): triage — {Bug Type}/{Severity}/{Origin}/{Qualifier}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Triage committed. All 4 dimensions in scope artifact AND Jira.
</verification>

## Triage Gate

**This gate is mandatory** — all 4 dimensions must be classified before advancing to Analyse. If uncertain about Origin, use your best hypothesis — it can be revised during Analyse.

When invoked via orchestrator (`/rai-bugfix-run`), the orchestrator presents classification for human active verification before proceeding.

## Output

| Item | Destination |
|------|-------------|
| TRIAGE block | Appended to `work/bugs/RAISE-{N}/scope.md` |
| Jira custom fields | 4 fields set via MCP |
| Jira transition | Triaged |
| Next | `/rai-bugfix-analyse` |

## Quality Checklist

- [ ] Classified BEFORE any analysis (avoid investigation bias)
- [ ] All 4 dimensions set in scope artifact
- [ ] All 4 Jira custom fields populated via MCP
- [ ] Jira transitioned to Triaged
- [ ] NEVER skip classification — it enables queryable bug data
- [ ] NEVER analyse before classifying — classification is independent of root cause

## References

- Previous: `/rai-bugfix-start`
- Next: `/rai-bugfix-analyse`
- Jira field IDs: `customfield_13267` (Bug Type), `customfield_12090` (Severity), `customfield_13269` (Origin), `customfield_13270` (Qualifier)
