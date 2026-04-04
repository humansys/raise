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
  raise.output_type: bug-triage
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - triage_block: string, next_skill
    - triage_yaml: file_path, .raise/artifacts/
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.triage
    context_source: scope doc
    affected_modules: []
    max_tier1_queries: 2
    max_jit_queries: 3
    tier1_queries:
      - "bug classification patterns for {affected_modules}"
      - "prior triage decisions for similar bugs"
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

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read bugfix-start's learning record at `.raise/rai/learnings/rai-bugfix-start/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Classify in 4 Dimensions

> **JIT**: Before classifying, query graph for classification patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

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

<if-blocked>
MCP not available → set fields manually in Jira UI. Log gap in LEARN record.
</if-blocked>

### Step 3: Produce Typed Artifact & Commit

Write typed artifact to `.raise/artifacts/RAISE-{N}-triage.yaml`:

```yaml
artifact_type: bug-triage
version: 1
skill: rai-bugfix-triage
created: '{ISO 8601 timestamp}'
bug: 'RAISE-{N}'
content:
  bug_type: '{Bug Type}'
  severity: '{S0-Critical|S1-High|S2-Medium|S3-Low}'
  origin: '{Origin}'
  qualifier: '{Qualifier}'
refs:
  scope: 'work/bugs/RAISE-{N}/scope.md'
  jira: 'RAISE-{N}'
metadata: {}
```

Commit classification:

```bash
git add work/bugs/RAISE-{N}/scope.md .raise/artifacts/RAISE-{N}-triage.yaml
git commit -m "bug(RAISE-{N}): triage — {Bug Type}/{Severity}/{Origin}/{Qualifier}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Triage committed. All 4 dimensions in scope artifact, typed artifact, AND Jira.
</verification>

## Triage Gate

**This gate is mandatory** — all 4 dimensions must be classified before advancing to Analyse. If uncertain about Origin, use your best hypothesis — it can be revised during Analyse.

When invoked via orchestrator (`/rai-bugfix-run`), the orchestrator presents classification for human active verification before proceeding.

## Output

| Item | Destination |
|------|-------------|
| TRIAGE block | Appended to `work/bugs/RAISE-{N}/scope.md` |
| Typed artifact | `.raise/artifacts/RAISE-{N}-triage.yaml` |
| Jira custom fields | 4 fields set via MCP |
| Jira transition | Triaged |
| Next | `/rai-bugfix-analyse` |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-triage/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-triage
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

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain. Enrich bugfix-start's record with `downstream: {reproduction_clear: bool, scope_complete: bool}`.

## Quality Checklist

- [ ] Classified BEFORE any analysis (avoid investigation bias)
- [ ] All 4 dimensions set in scope artifact
- [ ] All 4 Jira custom fields populated via MCP
- [ ] Typed artifact written to `.raise/artifacts/`
- [ ] Jira transitioned to Triaged
- [ ] NEVER skip classification — it enables queryable bug data
- [ ] NEVER analyse before classifying — classification is independent of root cause
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-triage/{work_id}/record.yaml`

## References

- Previous: `/rai-bugfix-start`
- Next: `/rai-bugfix-analyse`
- Jira field IDs: `customfield_13267` (Bug Type), `customfield_12090` (Severity), `customfield_13269` (Origin), `customfield_13270` (Qualifier)
