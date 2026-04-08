---
description: Generate architecture docs and publish to Confluence. Use before epic close.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '8.5'
  raise.frequency: per-epic
  raise.gate: ''
  raise.inputs: '- epic_scope: file_path, required

    - story_retrospectives: file_path[], required

    - confluence_space: string, required

    '
  raise.next: rai-epic-close
  raise.outputs: '- confluence_pages: url[], confluence

    '
  raise.prerequisites: all stories complete
  raise.version: 1.0.0
  raise.visibility: public
  raise.work_cycle: epic
name: rai-epic-docs
---

# Epic Documentation

## Purpose

Generate comprehensive developer and user-facing documentation for a completed epic. This skill ensures that every epic leaves behind documentation that maximizes reliability — not just "what was built" but "how it works, how to extend it, what can break, and how to diagnose it."

**This skill runs before `/rai-epic-close` as a documentation gate.**

## Mastery Levels (ShuHaRi)

- **Shu**: Generate all 5 sections, publish to Confluence, get HITL review
- **Ha**: Adjust section depth by epic size (S=1 page, M=1 page with detail, L=multi-page)
- **Ri**: Auto-detect which sections need the most depth based on code complexity metrics

## Context

**When to use:** After all stories are complete and merged, before `/rai-epic-close`.

**When to skip:** Never — documentation is a gate. Even XS epics get a minimal version.

**Inputs:** Epic scope document, story design/plan/retrospective artifacts, source code, existing Confluence space.

## Steps

### Step 1: Load Epic Context

Gather all artifacts from the epic:

```bash
ls work/epics/e{N}-{name}/
ls work/epics/e{N}-{name}/stories/
```

Read:
1. Epic scope (`scope.md`) — stories, milestones, done criteria
2. Story designs (`s{N}.{M}-design.md`) — decisions, integration points
3. Story retrospectives (`s{N}.{M}-retrospective.md`) — learnings, patterns
4. Source code modules touched (from git log)

```bash
git log --oneline --name-only main..HEAD -- src/ | grep "\.py$" | sort -u
```

**Determine epic size for documentation depth:**

| Epic Size | Stories | Documentation |
|-----------|:-------:|---------------|
| S (1-3 stories) | 1-3 | 1 Confluence page, sections can be brief |
| M (4-6 stories) | 4-6 | 1 Confluence page, full detail on all sections |
| L (7+ stories) | 7+ | 1 index page + child pages per subsystem |

<verification>
All epic artifacts loaded. Documentation depth determined.
</verification>

### Step 2: Generate Section 1 — Worked Example

**Purpose:** A developer understands the system by tracing one real operation end-to-end with concrete values.

Pick the most representative use case of the epic and trace it through every component with actual values:

- Input → transformation 1 → intermediate value → transformation 2 → ... → output
- Show actual data at each step (not pseudocode, not placeholders)
- Include scores, IDs, field values — everything a dev needs to verify their understanding
- If the epic has a CLI, show the exact command and its output

**Format:**
```
## Worked Example: "{use case description}"

### Input
{concrete input with real values}

### Step 1: {component name}
{what happens, with actual intermediate values}

### Step 2: {component name}
{transformation, with actual values}

...

### Output
{final result with real values}
```

**Diagram:** Include an ASCII or Mermaid sequence diagram showing the component interactions.

<verification>
A developer can follow the example and predict correct outputs for similar inputs.
</verification>

### Step 3: Generate Section 2 — Extension Guide

**Purpose:** A developer can add new functionality (new domain, new adapter, new node type) by following steps mechanically.

Document the extension point(s) this epic created:

1. **What can be extended** (new domains, new adapters, new node types, etc.)
2. **Step-by-step instructions** with file paths and code snippets
3. **What to test** after extending
4. **What NOT to do** (common mistakes)

**Format:**
```
## Extension Guide: How to Add a {extensible thing}

### Prerequisites
{what you need before starting}

### Step 1: {action}
File: `{path}`
{code snippet or config snippet}

### Step 2: {action}
...

### Verification
{commands to run to verify the extension works}

### Common Mistakes
- {mistake 1} → {consequence} → {fix}
```

<verification>
A developer unfamiliar with the codebase can follow the guide and successfully extend the system.
</verification>

### Step 4: Generate Section 3 — Data Flow Diagram

**Purpose:** A developer can see at a glance where each transformation lives and which module to edit for a given change.

Create an end-to-end data flow showing:

- Every pipeline/flow the epic implemented
- The Python module responsible for each transformation
- Input/output types at each boundary
- Which parts are deterministic vs non-deterministic (if applicable)

**Format:** ASCII diagram in the document + Mermaid diagram if Confluence supports it.

```
## Data Flow

### Pipeline: {pipeline name}

{source} ({type})
    ↓ module.function()
{intermediate} ({type})
    ↓ module.function()
{output} ({type})
```

<verification>
Every module mentioned in the diagram exists. Every type mentioned is a real class/model.
</verification>

### Step 5: Generate Section 4 — Invariants & Contracts

**Purpose:** A developer knows what MUST remain true for the system to work correctly. Violations of these invariants cause silent failures or bugs that manifest far from the source.

Read the source code and identify:

1. **Data invariants** — structural rules about data (e.g., "every node must have at least one relationship")
2. **Protocol contracts** — interface requirements (e.g., "adapters must never modify the graph")
3. **Value ranges** — numeric bounds (e.g., "scores are always in [0.0, 1.0]")
4. **Configuration contracts** — what domain.yaml/config must contain
5. **Ordering invariants** — sequence requirements (e.g., "validation must run before extraction")

**Format:**
```
## Invariants & Contracts

### Data Invariants
- **INV-1:** {invariant description}
  - Violated when: {scenario}
  - Symptom: {what happens}
  - Check: {how to verify}

### Protocol Contracts
- **CON-1:** {contract description}
  ...

### Value Ranges
- **RNG-1:** {range description}
  ...
```

**Source:** Derive these from:
- Pydantic model validators and field constraints
- Function preconditions and postconditions
- Test assertions (tests ARE invariant documentation)
- Design decisions from story design docs

<verification>
Each invariant is verifiable — a developer can write a test for it.
</verification>

### Step 6: Generate Section 5 — Failure Mode Catalog

**Purpose:** A developer encountering unexpected behavior can diagnose the root cause in minutes, not hours.

Document every known failure mode:

1. **Symptom** — what the developer observes
2. **Root cause** — why it happens
3. **Diagnosis** — how to confirm this is the issue
4. **Fix** — how to resolve it

**Sources for failure modes:**
- Story retrospectives (learnings from implementation)
- Known limitations documented in designs
- Edge cases discovered during testing
- Common mistakes from the extension guide

**Format:**
```
## Failure Mode Catalog

### FM-1: {symptom in developer's words}
- **Cause:** {root cause}
- **Diagnosis:** {command or check to confirm}
- **Fix:** {resolution steps}

### FM-2: {symptom}
...
```

**Minimum failure modes to document:**
- At least 1 per major component/module
- All limitations mentioned in story retrospectives
- All "known limitation" sections from design docs

<verification>
Each failure mode has a concrete diagnosis step — not just "check the logs."
</verification>

### Step 7: Publish to Confluence

Determine the page structure based on epic size:

**S/M epic (1 page):**
Create a single page with all 5 sections under the epic's Confluence parent.

**L epic (multi-page):**
Create an index page linking to child pages per subsystem.

**Page title convention:** `E{N}: {Epic Name} — Developer Documentation`

**Parent page:** Find the epic's Confluence space/parent. If none exists, use the governance section.

Publish via `rai docs publish` CLI command (routes to configured documentation target).

<verification>
Page(s) created in Confluence. URLs captured.
</verification>

### Step 8: HITL Review

Present the documentation to the human for review:

1. Show Confluence URL(s)
2. Summarize what each section covers
3. Ask: "Is there anything missing or unclear for a developer new to this code?"

| Condition | Action |
|-----------|--------|
| Human approves | Continue to epic-close |
| Human requests changes | Update and re-publish |
| Human identifies missing failure modes | Add them — these are the most valuable |

<verification>
Human approved documentation. Ready for /rai-epic-close.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Developer documentation | Confluence page(s) |
| Next | `/rai-epic-close` |

## Quality Checklist

- [ ] All 5 sections present (worked example, extension guide, data flow, invariants, failure modes)
- [ ] Worked example uses REAL values, not placeholders
- [ ] Extension guide is step-by-step reproducible
- [ ] Data flow diagram references real modules and types
- [ ] Every invariant is verifiable (can write a test for it)
- [ ] Every failure mode has a concrete diagnosis step
- [ ] Documentation depth matches epic size (S=brief, M=full, L=multi-page)
- [ ] Published to Confluence before epic-close
- [ ] HITL review completed
- [ ] NEVER skip this skill — undocumented epics create knowledge silos
- [ ] NEVER use placeholder values in worked examples — concrete data or nothing

## References

- Next: `/rai-epic-close`
- Previous: All `/rai-story-close` completions
- Epic artifacts: `work/epics/e{N}-{name}/`
