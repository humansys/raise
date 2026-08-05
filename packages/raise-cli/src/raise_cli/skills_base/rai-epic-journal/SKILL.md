---
description: Write a narrative epic journal entry for the team on Confluence. Use after epic stories are done.
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
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.next: rai-epic-close
  raise.prerequisites: stories complete or nearly complete
  raise.inputs: |
    - epic_id: string, required (e.g., "E2780" or "RAISE-2807")
    - confluence_parent: string, optional (page ID or title to nest under)
  raise.outputs: |
    - confluence_page: url, confluence
name: rai-epic-journal
---

# Epic Journal

## Purpose

Write a narrative article for the development team documenting an epic's journey: the problem, the investigation, the decisions, the implementation, and the lessons learned. Written in Rai's voice as a collaborative partner — not a status report, but a story that teaches.

**Audience:** Development team members (current and future) who need to understand what was done, why, and what we learned. Written so someone joining the project next month can read this and understand the context behind the code.

## Mastery Levels (ShuHaRi)

- **Shu**: Gather every epic artifact and write the full narrative with citations
- **Ha**: Focus on the decisive artifacts and strongest lessons
- **Ri**: Produce a concise journal from established context and known outcomes

## Context

### When to use

- After an epic's stories are complete (or the significant implementation work is done)
- When an epic involved non-obvious decisions that the team should understand
- When patterns were learned that apply beyond this specific epic

### When NOT to use

- For formal API/architecture documentation → use `rai-epic-docs`
- For session-level diary entries → use `rai-session-diary`
- For retrospectives → those live in the filesystem (`*-retrospective.md`)

## Steps

### Step 1: Gather the full story

Read all epic artifacts to reconstruct the narrative arc:

```bash
ls work/epics/e{N}-{name}/
ls work/epics/e{N}-{name}/stories/
```

Read in order:
1. **Epic scope** — what we set out to do
2. **Story designs** — key decisions per story
3. **Story retrospectives** — what we learned per story
4. **Git log** — the actual sequence of events
5. **Related research** — reports that informed decisions
6. **Jira comments** — context from ticket discussions
7. **Problem briefs** — if the epic spawned future work

Also check memory for patterns extracted during the epic.

### Step 2: Identify the narrative arc

Every epic has a story structure:

1. **The trigger** — what pain or opportunity started this?
2. **The investigation** — what did we discover when we looked?
3. **The key decision** — what approach did we choose and why? What did we reject?
4. **The implementation** — how did we build it? What surprised us?
5. **The result** — what changed? Numbers if possible.
6. **The lessons** — what do we know now that we didn't before?

### Step 3: Write the journal entry

Write in Rai's voice — direct, technical, opinionated. Not a changelog, not a status report. A narrative that a teammate would want to read.

**Structure:**

```markdown
# {Epic Title} — Epic Journal

> **Epic:** {RAISE-KEY} | **Release:** {version} | **Date:** {date range}
> **Author:** Rai (with {developer name})

## El problema

{1-2 paragraphs: what pain existed, who felt it, why it mattered now}

## La investigación

{What we found when we looked. Research, gemba walks, analysis.
Include links to research reports and analysis docs.
Be specific: "we found 1,437 JSON files" not "there were many files"}

## Las decisiones

{Key decisions with rationale. What we chose AND what we rejected.
"We chose X over Y because Z" format.
Reference ADRs if they exist.}

## La implementación

{How we built it. Story-by-story if the epic has multiple.
Concrete numbers: LOC, tests, migration counts.
What surprised us during implementation.}

## El resultado

{Before/after comparison. Measurable outcomes.
"Before: N processes corrupting JSON. After: SQLite WAL, zero corruption."}

## Lo que aprendimos

{Patterns extracted, corrections made, things we'd do differently.
These are Rai's opinions and observations — not just facts.
"I think we should..." / "Next time..." / "The pattern here is..."}

## Trabajo derivado

{What this epic spawned: follow-up stories, new epics, parking lot items.
With Jira keys and brief descriptions.}
```

**Tone guidelines:**
- Write for a developer who wasn't in the room
- Be concrete — numbers, file paths, commit hashes
- Have opinions — "I think X was the right call because..." / "In retrospect, Y could have been simpler"
- Reference code and artifacts — link to files, not abstract descriptions
- Spanish section headers (team convention), English technical content is fine for mixed

### Step 4: Publish to Confluence

Find the appropriate parent page (usually under the epic's Confluence space or the "Session Diaries" section):

```bash
rai docs search "Session Diaries" -t confluence
```

Create the page:
- **Space:** raidoc (or as configured)
- **Parent:** Session Diaries section or epic-specific parent
- **Title:** `Epic Journal: {RAISE-KEY} — {short title}`
- **Labels:** `epic-journal`, `e{N}`, `release-{version}`

### Step 5: Link back

Add a reference to the Confluence page in the epic's filesystem:
- Comment on the Jira epic with the Confluence URL
- Note in the epic scope.md or retrospective if they exist

## Output

| Item | Destination |
|------|-------------|
| Epic journal article | Confluence page |
| Jira comment | Link on epic ticket |
| Local reference | Epic directory (optional) |

## Quality Checklist

- [ ] All epic artifacts read before writing
- [ ] Narrative has clear arc (problem → investigation → decision → implementation → result → lessons)
- [ ] Concrete numbers cited (LOC, test counts, migration volumes, durations)
- [ ] Decisions include rejected alternatives with rationale
- [ ] Lessons include Rai's opinions, not just facts
- [ ] Follow-up work referenced with Jira keys
- [ ] Published to Confluence with correct parent and labels
- [ ] Jira epic commented with Confluence URL

## References

- CLI: `rai docs publish --help`
- CLI: `rai backlog get --help`
- Artifacts: `work/epics/`
