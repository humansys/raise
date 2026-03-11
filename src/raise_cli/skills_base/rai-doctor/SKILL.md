---
name: rai-doctor
description: >
  Run RaiSE self-diagnostics, explain results conversationally, and guide
  the user through fixes. The CLI does the checking; the skill does the
  interpreting and helping.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.2.0"
  raise.visibility: public
---

# Doctor

## Purpose

Diagnose RaiSE setup health, explain issues in plain language, and guide the user through resolution. The user never touches the CLI directly — Rai runs the diagnostics and translates results into actionable conversation.

## Context

**When to use:** User reports something isn't working, after `rai init`, after upgrading raise-cli, or proactively at session start when setup feels off.

**When to skip:** The issue is clearly in user code, not RaiSE configuration.

## Steps

### Step 1: Run diagnostics

```bash
rai doctor --json
```

Parse the JSON output. Categorize results by severity.

### Step 2: Report to user

**If all checks pass:**
> Your RaiSE setup is healthy. All checks passed.

**If there are warnings or errors**, explain each one conversationally:

- Translate technical check IDs into human language
- Group by category (environment, project, adapters, skills, MCP)
- For each issue: what it means, why it matters, and what to do

Example:
> I found 2 issues with your setup:
>
> 1. **Graph is outdated** — your knowledge graph hasn't been rebuilt since governance files changed. This means my context queries may return stale data. I can rebuild it now if you'd like.
>
> 2. **MCP server 'jira' is unreachable** — the Jira integration can't connect. Check that JIRA_URL and JIRA_API_TOKEN are set in your environment.

### Step 3: Offer fixes

For auto-fixable issues (those with `fix_id` in the JSON):

> I can fix issue #1 automatically. Should I run `rai doctor --fix`?

Wait for user confirmation before running fixes.

```bash
rai doctor --fix
```

Report the outcome of each fix.

### Step 4: Guide manual fixes

For issues that can't be auto-fixed, guide step by step:

- Missing env vars → tell the user exactly which vars to set and where
- Missing optional extras → provide the exact pip install command
- Stale skills → offer to run `rai skill sync`
- Invalid manifest → explain what's wrong and how to fix it

### Step 5: Bug report (if unresolvable)

If issues persist after fixes:

> This looks like a bug in RaiSE itself. I can generate a diagnostic report for the team. It only includes non-sensitive data (versions, check results, file names — never secrets or code). Want me to prepare it?

If the user agrees:

```bash
rai doctor report
```

Show the user the saved report path so they can review it. Then:

> The report is saved at {path}. Review it, and when ready I can open your email client to send it:

```bash
rai doctor report --send
```

## Output

| Artifact | When |
|----------|------|
| Diagnostic summary | Always (conversational) |
| Auto-fixes applied | When user approves --fix |
| Report file | When user requests bug report |
| Email draft | When user approves --send |

## Quality Checklist

- [ ] Never run `--fix` without user confirmation
- [ ] Explain issues in plain language, not technical jargon
- [ ] Never expose secrets, tokens, or file contents in conversation
- [ ] Offer bug report only after fix attempts fail
- [ ] Always show the report path so user can review before sending
