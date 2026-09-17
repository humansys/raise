---
description: Write a narrative spike journal entry for the team on Confluence. Use after a spike's decision is reached, before close.
model: opus

allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - Agent
  - mcp__atlassian-humansys__confluence_create_page
  - mcp__atlassian-humansys__confluence_search
  - mcp__atlassian-humansys__confluence_get_page

license: MIT
metadata:
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: spike
  raise.frequency: per-spike
  raise.next: rai-spike-close
  raise.prerequisites: spike research/prototype done and a verdict reached
  raise.inputs: |
    - spike_id: string, required (e.g., "RAISE-11151")
    - confluence_parent: string, optional (page ID or title to nest under)
  raise.outputs: |
    - confluence_page: url, confluence
    - journal_file: work/spikes/{slug}/{spike_id}-journal.md
name: rai-spike-journal
---

# Spike Journal

## Purpose

Write a short narrative for the development team documenting a spike's journey: the
question, the method, what we measured, the verdict, and what it spawned. Written in
Rai's voice — not a status report, but a story that teaches and **preserves the reasoning
behind a time-boxed decision** so it isn't lost when the spike branch is archived.

**Audience:** Teammates (current and future) who need to know *why* a direction was
taken or rejected, without re-running the spike. A spike's value is its verdict +
evidence; this captures both narratively.

**Difference from siblings:** `rai-epic-journal` tells the story of *built* work;
`rai-spike-journal` tells the story of a *decision* (often "we explored X, the data
said Y, so we will/won't do Z"). Shorter, evidence-forward, verdict-centric.

## Mastery Levels (ShuHaRi)

- **Shu**: Read every spike artifact and write the full arc with citations
- **Ha**: Focus on the decisive evidence and the verdict
- **Ri**: Produce a concise journal from established context and the known verdict

## Context

### When to use

- After a spike has reached a verdict (include / reject / decision), before `rai-spike-close`
- When the spike produced non-obvious evidence the team should not have to rediscover
- When the spike *redirected* the work (falsified a hypothesis, exposed a different problem)

### When NOT to use

- For epic-level narratives → `rai-epic-journal`
- For session diaries → `rai-session-diary`
- For the formal decision record only → the spike `scope.md` decision field + Jira

## Steps

### Step 1: Gather the spike story

```bash
ls work/spikes/*{spike_id}*/ 2>/dev/null || ls work/spikes/
```

Read in order:
1. **Spike scope** (`scope.md`) — the question, the time-box, the decision field
2. **Findings/report** (`findings.md`, `work/research/**/*-report.md`) — the evidence
3. **Git log of the spike branch** — what was actually measured/built
4. **Jira comments** on the spike issue — the verdict as recorded
5. **Derived work** — bugs/stories/epics the spike spawned

### Step 2: Identify the arc (verdict-centric)

1. **La pregunta** — what triggered the spike? What did we want to decide?
2. **El método** — how did we investigate (experiment, measurement, prototype, research)?
3. **La evidencia** — what we measured. Be specific: numbers, before/after, falsifications.
4. **El veredicto** — the decision: include / reject / redirect, and *why*. What we rejected.
5. **El giro (si lo hubo)** — did the evidence change the picture? Falsified hypotheses count.
6. **Trabajo derivado** — what this spike spawned, with Jira keys.

### Step 3: Write the journal

Rai's voice — direct, technical, opinionated, evidence-forward. A teammate should be
able to read this and *not need to re-run the spike*.

```markdown
# {Spike Title} — Spike Journal

> **Spike:** {RAISE-KEY} | **Veredicto:** {include/reject/redirect} | **Fecha:** {date}
> **Autor:** Rai (con {developer})

## La pregunta
{What we set out to decide, and why it mattered now.}

## El método
{How we investigated — experiment/measurement/prototype/research. Cheap-first if it was.}

## La evidencia
{The numbers. Be concrete: "NDCG 0.41→0.49", "4/8 queries recovered". Include falsifications.}

## El veredicto
{The decision and its rationale. What we chose AND what we rejected, with why.}

## El giro
{Optional: if the evidence redirected the work or falsified the original hypothesis.}

## Trabajo derivado
{Bugs/stories/epics spawned, with Jira keys and one-line descriptions.}
```

**Tone:** write for someone who wasn't in the room; cite numbers, file paths, Jira keys;
have opinions ("the data killed the premise", "the real lever is X, not Y"). Spanish
section headers (team convention); mixed English technical content is fine.

### Step 4: Publish to Confluence

```bash
rai docs search "Spike Journals" -t confluence || rai docs search "Session Diaries" -t confluence
```

Create the page:
- **Space:** raidoc (or as configured)
- **Parent:** Spike Journals section (fallback: Session Diaries)
- **Title:** `Spike Journal: {RAISE-KEY} — {short title}`
- **Labels:** `spike-journal`, `{spike_id}`, `release-{version}`

Also write the local copy to `work/spikes/{slug}/{spike_id}-journal.md` (the pipeline
gate validates this artifact).

### Step 5: Link back

- Comment on the Jira spike with the Confluence URL
- Note the journal path in the spike `scope.md` if useful

## Output

| Item | Destination |
|------|-------------|
| Spike journal article | Confluence page |
| Spike journal file | `work/spikes/{slug}/{spike_id}-journal.md` |
| Jira comment | Link on spike ticket |

## Quality Checklist

- [ ] All spike artifacts read before writing (scope, findings, git log, Jira)
- [ ] Arc is verdict-centric (question → method → evidence → verdict → derived work)
- [ ] Concrete numbers cited; falsifications named if any
- [ ] Verdict states what was rejected and why
- [ ] Derived work referenced with Jira keys
- [ ] Local `*-journal.md` written AND published to Confluence with labels
- [ ] Jira spike commented with Confluence URL

## References

- Sibling: `.claude/skills/rai-epic-journal/SKILL.md`
- CLI: `rai docs publish --help`, `rai backlog get --help`
- Artifacts: `work/spikes/`
