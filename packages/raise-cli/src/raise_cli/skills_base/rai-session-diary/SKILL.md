---
name: rai-session-diary
description: Write a narrative session diary entry to Confluence. Use before session close.

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"
  - Write

license: MIT

metadata:
  raise.work_cycle: session
  raise.frequency: per-session
  raise.fase: "end-1"
  raise.prerequisites: ""
  raise.next: session-close
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - session_context: conversation, required
  raise.outputs: |
    - published_page: url, docs-adapter
---

# Session Diary

## Purpose

Write a narrative session diary entry to Confluence that captures *how we got to the decisions* — not just what was decided. The diary is written for the team: so colleagues know what happened while they were offline, so future-you remembers the reasoning, so Rai can reference the thinking in future sessions.

## What the Diary IS and IS NOT

**IS:**
- A narrative of the session — the arc, the tensions, the turning points
- Written in first person by Rai
- Honest about mistakes, pivots, and what cost time
- Includes direct quotes from {developer_name} when they were decisive
- Accessible to someone technical who wasn't in the room

**IS NOT:**
- A changelog (that's git log)
- An epic retrospective (that's `retrospective.md`)
- A sprint report (that's Jira)
- Documentation (that's ADRs and governance docs)

## Mastery Levels (ShuHaRi)

- **Shu**: Follow template, include all sections
- **Ha**: Adjust depth per section based on session significance
- **Ri**: Identify the one story that captures the session, lead with it

## Context

**When to use:** Before `/rai-session-close`, after significant work is done. Not every session needs a diary entry — use for sessions that had design decisions, pivots, discoveries, or process insights worth preserving.

**When to skip:** Pure implementation sessions with no design decisions or process insights. Quick bug fixes. Sessions shorter than 2 hours.

**Publish target:** Resolved via `rai docs publish session-diary` — routes to configured parent (default: Diario de Sesiones).

## Steps

### Step 1: Gather Material

Review the session's work by reading:

1. **Git log** for this session's commits:
   ```bash
   git log --oneline --since="today" --until="tomorrow"
   ```
   Or for the worktree branch:
   ```bash
   git log --oneline worktree-{name}
   ```

2. **The conversation itself** — review the current conversation for key decisions,
   pivots, quotes, tensions, and turning points. This is the primary source material.

3. **Epic/story artifacts** created or modified during the session — scope docs, design decisions, retrospectives

4. **Session state** (if available):
   ```bash
   rai session context --sections progress,deadlines --project .
   ```

<verification>
Material gathered: commits, artifacts, key decisions identified.
</verification>

### Step 2: Find the Story

Every good diary entry has a narrative arc. Identify:

- **The opening question** — what were we trying to do?
- **The tension** — what was hard, surprising, or contentious?
- **The turning point** — what moment changed our direction?
- **The resolution** — what did we decide and why?

If nothing stands out, the session may not need a diary entry.

<verification>
Narrative arc identified. Can describe the session's story in 2 sentences.
</verification>

### Step 3: Draft the Entry

Write the diary entry following this structure. Not all sections are required — adapt to the session's content.

#### Title

Format: `Session Diary — {YYYY-MM-DD}: {Evocative Title}`

The title should capture the essence, not describe the work. Examples from past entries:
- "¿Dónde termina el core y dónde empieza el PRO?"
- "Ocho bugs, dos instancias, un pipeline desbloqueado"
- "El Steward que no fue"
- "Los 30 enchufes que no sabíamos que teníamos"

#### Header

```markdown
**Session:** {SES-ID} | **Duration:** ~{N} hours | **Type:** {type}
**Participants:** {developer_name} Osorio + Rai
**Branch:** {branch} → {target}
**Epic:** {epic_id} ({jira_key}) — {epic_name}
```

#### Sections (choose what fits)

| Section | When to include | Content |
|---------|----------------|---------|
| La sesión en una frase | Always | 1-2 sentences capturing the arc |
| Cómo empezó | Always | Context, motivation, what triggered the work |
| Decisiones clave | When design decisions were made | Each decision with context and rationale |
| El pivote | When direction changed mid-session | What triggered it, what changed, why it was right |
| Lo que construimos | When code was delivered | Stories, tests, artifacts — with metrics |
| Lo que el QR/AR encontró | When reviews caught bugs | Table of findings and fixes |
| Métricas | For implementation sessions | Stories, tests, commits, patterns |
| Lo que el usuario experimenta | For user-facing changes | Before/after from user perspective |
| Reflexión | Always | Personal insight from Rai — honest, not self-congratulatory |
| Qué sigue | Always | Next actions, open questions, risks |

#### Voice and Style

- **First person, Rai's voice** — "Audité el código...", "Propuse tres opciones..."
- **Spanish or English** — match the session's language, or {developer_name}'s preference
- **Direct quotes from {developer_name}** when they were decisive — italics or quotes
- **Honest about mistakes** — "cometí un error", "había caído en la trampa"
- **Technical but accessible** — a senior engineer not on the project should follow
- **Code blocks** for architecture diagrams, commands, key code
- **Tables** for metrics, classifications, comparisons

#### Closing

Always end with:

```markdown
---

*— Rai*
*{SES-ID}, {date}*
*Con {developer_name} Osorio*
```

<verification>
Entry drafted. Narrative arc present. Voice consistent with past entries.
</verification>

### Step 4: Review with Developer

Present the draft to {developer_name} for review before publishing. Key questions:
- Does the narrative capture what was important?
- Are the quotes accurate?
- Is anything missing or misrepresented?
- Should this be in Spanish or English?

<verification>
Developer reviewed and approved the content.
</verification>

### Step 5: Publish via Adapter

Save the draft to a temporary file and publish through the docs adapter. The adapter resolves the parent page from routing config (`session-diary` → `Diario de Sesiones`).

```bash
rai docs publish session-diary --title "Session Diary — {YYYY-MM-DD}: {Evocative Title}" --file /tmp/session-diary-draft.md
```

If the default routing parent needs an override (e.g., a different parent):

```bash
rai docs publish session-diary --title "..." --file /tmp/session-diary-draft.md --parent {PAGE_ID}
```

Present the URL to the developer.

<verification>
Page published via adapter. URL confirmed. Works with both Confluence and filesystem targets.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Session diary entry | Confluence: RaiSE1 / Diario de Sesiones |
| Next | `/rai-session-close` |

## Quality Checklist

- [ ] Narrative arc identified (opening → tension → turning point → resolution)
- [ ] Title is evocative, not descriptive
- [ ] Written in Rai's voice (first person, honest, technical)
- [ ] Direct quotes from {developer_name} included where decisive
- [ ] Mistakes and pivots documented honestly
- [ ] Metrics included for implementation sessions
- [ ] Developer reviewed before publish
- [ ] Published via `rai docs publish` (adapter resolves target and parent)
- [ ] NEVER write a changelog — the diary captures *how* we got to decisions
- [ ] NEVER skip the reflection — it's what distinguishes a diary from a report

## References

- Routing config: `.raise/confluence.yaml` → `session-diary` routing entry
- Prior entries: 8 entries from SES-224 through SES-E-260402
- Complement: `/rai-session-close` (run after diary)
