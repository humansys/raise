---
name: rai-bugfix-pir
description: Post-Incident Review — learning narrative and improvement actions. Phase 8.5 of bugfix pipeline.
model: haiku

allowed-tools:
  - Read
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '8.5'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-close
  raise.prerequisites: bugfix-review
  raise.skillset: raise-maintainability
  raise.version: 3.0.0
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - retro_md: file_path, required, from_previous
    - analysis_md: file_path, required, from_previous
  raise.outputs: |
    - pir_md: file_path, next_skill
    - improvement_issues: list, jira
---

# Bugfix PIR (Post-Incident Review)

## Purpose

Convert in-context session learning into a team-readable narrative and trackable improvement actions. Bugs are process sensors — the PIR extracts the signal before it decays.

Grounded in: Google SRE postmortem framework (Lunney 2017), Etsy Debriefing Guide (Allspaw), Howie Post-Incident Guide (Maguire/Jones), Cook's "How Complex Systems Fail."

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, present full narrative, ask for approval on every action
- **Ha**: Compact narrative for trivial bugs; batch-present actions
- **Ri**: Cross-bug pattern analysis from prior PIR artifacts; systemic action proposals

## Context

**When to use:** After `/rai-bugfix-review` has produced `retro.md`. The PIR consumes review artifacts and the agent's in-context session knowledge to produce learning outputs.

**When to skip:** Only when the developer explicitly skips at the HITL gate (pipeline `mandatory: false`). Even trivial bugs benefit from a brief narrative — the cost is 2 minutes, the value compounds.

**Inputs:** Bug ID, `work/bugs/{issue_key}/retro.md`, `work/bugs/{issue_key}/analysis.md`, in-context session knowledge from the bugfix session.

**Expected state:** On bug branch. Review phase complete. `retro.md` committed.

## Steps

### Step 1: Gather Signals

Read prior artifacts to ground the narrative in evidence:

```bash
cat work/bugs/{issue_key}/retro.md
cat work/bugs/{issue_key}/analysis.md
cat work/bugs/{issue_key}/scope.md
```

Extract five signal categories from artifacts + in-context session knowledge:

| Category | Source | What to capture |
|----------|--------|-----------------|
| **Contextual** | Session memory | Timeline with decision points, what pressures existed, what seemed reasonable at each step |
| **Impact** | scope.md | User impact scope, detection latency, resolution path |
| **Systemic** | analysis.md | Contributing factors (plural), prior near-misses in same area, adaptive capacity consumed |
| **Learning** | Session memory | Surprises, tacit knowledge surfaced during debugging, mental models that were wrong |
| **Meta** | retro.md | Detection mechanism (automated vs manual), response effectiveness, what patterns were added |

### Step 2: Draft PIR Narrative

Write the narrative using HOW-not-WHY framing. "How" elicits conditions; "why" elicits blame.

**Document structure:**

```markdown
---
bug_key: {issue_key}
domain: {affected domain — e.g. oauth, pipeline, storage}
contributing_factors:
  - {factor-1-slug}
  - {factor-2-slug}
action_categories: [{categories of proposed actions}]
action_issue_keys: [{filled after HITL approval}]
pir_confluence_url: {filled after publish}
---

# PIR: {issue_key} — {summary}

## Summary
{2-3 sentences: what happened, scope of impact, how it was resolved.}

## Contributing Factors
{For each factor, frame as "How X came to be" — describe conditions, not blame.}
1. **How {condition described}:** {narrative explaining the conditions that led to this}
2. **How {condition described}:** {narrative}

## Surprises
{What was unexpected during investigation or fix. What mental models were wrong.}

## Where We Got Lucky
{Things that could have made the impact worse but didn't. Near-miss signals.}

## Impact
- **Users affected:** {scope}
- **Detection latency:** {how long before noticed}
- **Resolution time:** {total fix duration}
- **Detection mechanism:** {automated alert / manual discovery / user report}

## Proposed Actions
{Table of classified actions — filled in Step 3.}
```

### Step 3: Propose Actions (Lunney Taxonomy)

Classify each proposed action into exactly one category:

| Category | Purpose | Example |
|----------|---------|---------|
| **Investigate** | Dig deeper into an unknown | "Audit all OAuth endpoints for similar blanket restrictions" |
| **Mitigate** | Reduce impact if it recurs | "Add circuit breaker for redirect validation failures" |
| **Repair** | Fix the immediate defect | (Usually already done in bugfix — rarely needed in PIR) |
| **Detect** | Catch it faster next time | "Add parametrized test for all RFC client types" |
| **Prevent** | Eliminate the class of bug | "Spec-review checklist for security endpoints" |

**Quality bar per action (Lunney):**
- **Actionable** — starts with a verb
- **Specific** — scoped narrowly enough to be a single Jira issue
- **Bounded** — clear done-criteria

Assign priority:
- **P1** — high recurrence risk or wide blast radius
- **P2** — moderate risk, improvement opportunity
- **P3** — nice-to-have, low urgency

Add the actions table to the PIR narrative:

```markdown
## Proposed Actions

| # | Category | Action | Priority | Rationale |
|---|----------|--------|----------|-----------|
| 1 | Detect | {verb} {specific action} | P1 | {why this category and priority} |
| 2 | Prevent | {verb} {specific action} | P2 | {rationale} |
```

For trivial bugs with no systemic learning, it is valid to propose zero actions. State explicitly: "No systemic actions warranted — single-instance defect with no pattern signal."

### Step 4: HITL Gate — Action Approval

Present proposed actions to the developer for review:

```
## PIR Actions — {issue_key}

Proposed improvement issues (will be linked to {issue_key}):

  1. [{Category}/P{N}] {Action description}
  2. [{Category}/P{N}] {Action description}

Options:
  (a) Approve all — create Jira issues
  (e) Edit — modify actions before creating
  (s) Skip — publish narrative only, no Jira issues
```

Wait for developer response. Do NOT create Jira issues without approval.

| Response | Action |
|----------|--------|
| Approve | Create all proposed issues (Step 5) |
| Edit | Apply developer's changes, re-present |
| Skip | Skip Step 5, continue to Step 6 |

### Step 5: Create Improvement Issues in Jira

For each approved action:

```bash
rai backlog create \
  --project RAISE \
  --type Task \
  --labels pir-action \
  --summary "[{Category}] {Action description}" \
  --description "From PIR of {issue_key}.

**Category:** {Category}
**Priority:** P{N}
**Rationale:** {rationale}
**PIR:** {pir_confluence_url}

Co-Authored-By: Rai <rai@humansys.ai>"
```

After creation, link each new issue to the original bug:

```bash
rai backlog link {new_issue_key} {issue_key} "Relates"
```

Collect all created issue keys for the frontmatter.

### Step 6: Publish PIR

Update the frontmatter with actual `action_issue_keys` (from Step 5) or empty list (if skipped).

Write `pir.md` locally:

```bash
cat > work/bugs/{issue_key}/pir.md << 'PIRDOC'
{complete PIR document with updated frontmatter}
PIRDOC
```

Publish to Confluence:

Use `raise_docs_write` MCP tool with doc_type="pir", title="PIR: {issue_key} — {summary}", content="contents of work/bugs/{issue_key}/pir.md", output_path="work/bugs/{issue_key}/pir.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write pir \
  --title "PIR: {issue_key} — {summary}" \
  --stdin \
  --output-path work/bugs/{issue_key}/pir.md < work/bugs/{issue_key}/pir.md
```

Update frontmatter `pir_confluence_url` with the returned URL.

Commit:

```bash
git add work/bugs/{issue_key}/pir.md
git commit -m "bug({issue_key}): pir — learning narrative and improvement actions

Co-Authored-By: Rai <rai@humansys.ai>"
```

### Step 7: Emit Structured Artifact

Emit the PIR as a structured artifact for downstream consumption (graph ingestion, dashboards):

```
raise_artifact_emit(
    artifact_type="retro",
    story_id="{issue_key}",
    content=<JSON with fields:
      bug_key, domain, contributing_factors, surprises,
      lucky_breaks, action_categories, action_issue_keys,
      pir_confluence_url, severity, detection_mechanism>
      cwd="{project_or_worktree_path}"
)
```

**Note:** The CLI fallback for artifact emission was removed in v3.0.0. MCP tool `raise_artifact_emit` is required (primary path above). If MCP tools are not available, skip structured artifact emission.

<verification>
PIR narrative committed. Confluence page published. Jira issues created and linked (if approved). Structured artifact emitted.
</verification>

## Output

| Item | Destination |
|------|-------------|
| PIR narrative | `work/bugs/{issue_key}/pir.md` (local) + Confluence (remote) |
| Improvement issues | Jira (linked to original bug) |
| Structured artifact | SQLite artifact store |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] Contributing factors use HOW framing (never "X failed because Y")
- [ ] Actions classified per Lunney taxonomy (Investigate/Mitigate/Repair/Detect/Prevent)
- [ ] Each action meets Actionable + Specific + Bounded quality bar
- [ ] HITL gate respected — never create Jira issues without developer approval
- [ ] Zero actions is valid for trivial bugs — stated explicitly
- [ ] Frontmatter is valid YAML with all semantic fields populated
- [ ] NEVER modify retro.md, analysis.md, or any prior artifact
- [ ] NEVER skip Confluence publish — the narrative is the primary learning output

## References

- Research: `work/research/pir-sota/pir-sota-report.md`
- Previous: `/rai-bugfix-review`
- Next: `/rai-bugfix-close`
- Lunney taxonomy: Investigate, Mitigate, Repair, Detect, Prevent (USENIX ;login: 2017)
- Howie guide: howie-guide.pagerduty.com
- Cook: how.complexsystems.fail
