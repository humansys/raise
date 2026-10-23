---
name: rai-bugfix-triage
description: Classify bug in 4 dimensions and set Jira custom fields. Phase 2 of bugfix pipeline.
model: sonnet

allowed-tools:
  - Read
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
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - triage_block: string, next_skill
---

# Bugfix Triage

## Purpose

Classify the bug in 4 orthogonal dimensions (ODC-inspired) and persist classification to scope artifact and Jira custom fields. This is the highest-leverage phase — misclassification cascades through all subsequent phases.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, classify all 4 dimensions, set all Jira fields
- **Ha**: Pre-classify from bug report patterns; adjust if uncertain
- **Ri**: Domain-specific triage taxonomies

## Context

**When to use:** After `/rai-bugfix-start` has produced `scope.md` with WHAT/WHEN/WHERE/EXPECTED.

**When to skip:** Never — triage is mandatory. Even trivial bugs need classification for queryable data.

**Inputs:** Bug ID, `work/bugs/{issue_key}/scope.md` without TRIAGE block.

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

Append the TRIAGE block to `work/bugs/{issue_key}/scope.md` via CLI (preserves existing content + publishes to Confluence):

Use `raise_docs_write` MCP tool with doc_type="bugfix-scope", title="{issue_key}: scope+triage", content="existing work/bugs/{issue_key}/scope.md contents plus TRIAGE block with Bug Type, Severity, Origin, and Qualifier fields", output_path="work/bugs/{issue_key}/scope.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write bugfix-scope \
  --title "{issue_key}: scope+triage" \
  --stdin \
  --output-path work/bugs/{issue_key}/scope.md << EOF
$(cat work/bugs/{issue_key}/scope.md)

TRIAGE:
  Bug Type:    {Functional|Interface|Data|Logic|Configuration|Regression}
  Severity:    {S0-Critical|S1-High|S2-Medium|S3-Low}
  Origin:      {Requirements|Design|Code|Integration|Environment}
  Qualifier:   {Missing|Incorrect|Extraneous}
EOF
```

Note: unquoted heredoc so `$(cat ...)` expands the existing file content.

<verification>
4 dimensions classified in scope artifact.
</verification>

### Step 2: Resolve and Set Jira Custom Fields

#### 2a — Resolve field IDs from config

```bash
rai backlog fields list --format agent
```

Output format: `name|id|issue_type|context_name|is_global|values` (one line per field context).

Determine `bug.issue_type`: read `Issue Type:` field from `work/bugs/{issue_key}/scope.md`,
or run `rai backlog get {issue_key}` and read the issue type from the output.

Parse the output: filter lines where the third column matches `{bug.issue_type}`, deduplicate by name, build a map:
`{ "Bug Type": "<id>", "Severity": "<id>", "Origin": "<id>", "Qualifier": "<id>" }`

**If no pipe-delimited lines match `{bug.issue_type}`** (`custom_fields.{bug.issue_type}` not configured):
- Skip step 2b entirely
- Append to TRIAGE block: `Jira fields: not set — run rai-backlog-setup and add custom_fields.{bug.issue_type}`
- Continue to Step 3

#### 2b — Set fields via CLI (only when configured)

Apply value mappings (Jira quirks):
- Severity: `S0-Critical → Sev-0`, `S1-High → Sev-1`, `S2-Medium → Sev-2`, `S3-Low → Sev-3`
- Origin: `Environment → Enviroment` (Jira typo — one `n`)
- Fields absent from config output: skip silently

Use the `raise_backlog_update` MCP tool with issue_key="{issue_key}", custom_fields='{"bug_type_id": "{Bug Type}", "severity_id": "Sev-{N}", "origin_id": "{Origin}", "qualifier_id": "{Qualifier}"}'.
If MCP tools are not available, fall back to:
```bash
rai backlog update {issue_key} \
  --field {bug_type_id}="{Bug Type}" \
  --field {severity_id}="Sev-{N}" \
  --field {origin_id}="{Origin}" \
  --field {qualifier_id}="{Qualifier}"
```

Select fields are auto-wrapped by the CLI — no need to pass `{"value": "..."}` manually.

> **Field names looked up:** `"Bug Type"`, `"Severity"`, `"Origin"`, `"Qualifier"` (issue type: `{bug.issue_type}`).
> Field IDs are resolved at runtime from `backlog.yaml` via `rai backlog fields list` — never hardcoded.

<verification>
Jira fields set using IDs from config, or step skipped with note if not configured.
</verification>

<if-blocked>
Adapter not configured or update fails → log warning and continue. Field classification is best-effort.
</if-blocked>

### Step 3: Commit Classification

```bash
git add work/bugs/{issue_key}/scope.md
git commit -m "bug({issue_key}): triage — {Bug Type}/{Severity}/{Origin}/{Qualifier}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Triage committed. All 4 dimensions in scope artifact AND Jira.
</verification>

## Triage Gate

**This gate is mandatory** — all 4 dimensions must be classified before advancing to Analyse. If uncertain about Origin, use your best hypothesis — it can be revised during Analyse.

Present classification for human active verification before proceeding to Analyse.

## Output

| Item | Destination |
|------|-------------|
| TRIAGE block | Appended to `work/bugs/{issue_key}/scope.md` |
| Jira custom fields | 4 fields set via MCP |
| Next | `/rai-bugfix-analyse` |

## Quality Checklist

- [ ] Classified BEFORE any analysis (avoid investigation bias)
- [ ] All 4 dimensions set in scope artifact
- [ ] All 4 Jira custom fields populated via MCP
- [ ] NEVER skip classification — it enables queryable bug data
- [ ] NEVER analyse before classifying — classification is independent of root cause

## References

- Previous: `/rai-bugfix-start`
- Next: `/rai-bugfix-analyse`
- Field IDs: resolved at runtime from `rai backlog fields list --format agent`
- Field names looked up: `"Bug Type"`, `"Severity"`, `"Origin"`, `"Qualifier"` (context: `bug`)
