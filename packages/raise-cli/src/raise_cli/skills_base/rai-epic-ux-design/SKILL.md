---
name: rai-epic-ux-design
description: Define workflows, surfaces, and trust boundaries for user-facing epics before planning. Use after epic design when interaction design matters.
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "3.5"
  raise.prerequisites: epic-design
  raise.next: epic-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - design: file_path, optional, previous_skill
    - brief: file_path, optional, previous_skill
  raise.outputs: |
    - ux_design: file_path, primary
  raise.aspects: introspection
  raise.introspection:
    phase: epic.ux_design
    context_source: epic scope and design docs
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "workflow patterns for {user_surface}"
      - "trust and review patterns for {domain}"
      - "prior user-facing epic designs with similar scope"
raise.mastery:
  shu: "Follow all steps and produce a complete low-fi UX artifact"
  ha: "Adjust depth to epic risk while keeping the output lightweight"
  ri: "Collapse to the smallest artifact that still improves planning"
---

# Epic UX Design
## Purpose
Define the minimum viable user-facing workflow before epic planning starts.
## Mastery Levels (ShuHaRi)
See `raise.mastery` in frontmatter.
## Context
**When to use:** After `/rai-epic-design` for epics that introduce screens, workflows, prompts, dashboards, review surfaces, or trust-heavy interactions.
**When to skip:** Backend-only infrastructure, migrations, adapters, CI, or refactors with no meaningful interaction change.
**Inputs:** `scope.md`, `design.md` if present, and optional problem brief.
## Steps
### PRIME (mandatory — do not skip)
1. Run tier-1 graph queries from frontmatter. If MCP is unavailable, fall back to:
   ```bash
   rai graph query
   ```
   Zero results is valid.
2. Read `scope.md` first, then `design.md` if it exists.
### Step 1: Confirm the Phase Is Needed
State in one sentence why this epic does or does not qualify for UX design.
If it does not qualify, stop and hand back to `/rai-epic-plan`.
### Step 2: Define Users and Jobs
List:
- primary user
- secondary user if relevant
- top 2-4 jobs to be done in v1
Prefer operational clarity over personas.
### Step 3: Map the Core Workflow
Write the minimum viable happy path from entry to value.
Also mark:
- review or approval steps
- points where trust can fail
- steps that must stay human-controlled in v1
### Step 4: Define Surfaces and Information Shape
Enumerate the v1 surfaces:
- screen, panel, report, queue, prompt surface, or conversational entrypoint
- what the user must see there
- what the user can decide or do there
Low-fi is enough. Wireframes are optional; surface inventory is mandatory.
### Step 4a: Map Screens to Stories (Coverage Map)
Immediately after enumerating surfaces, produce a **screen-to-story coverage table** that maps every screen or view to the story that delivers it plus a coverage status. Use these statuses:
- ✅ cubierta en prototipo — screen has a named story and is included in the current prototype
- ⚠ parcial — screen exists in a story but scope is incomplete or uncertain
- ❌ falta — screen is enumerated but no story currently covers it

**Example coverage map** (per ADR-125 — ambiguity-killer; adapt column names to your epic):

| Pantalla / Vista | Historia que la entrega | Estado |
|---|---|---|
| Dashboard de revisión | S4478.4 — Review Dashboard | ✅ cubierta |
| Panel de acción masiva | — | ❌ falta |
| Configuración de umbrales | S4478.6 — Threshold Config | ⚠ parcial |

A ❌ in any row is a **planning gap** — either add a story or explicitly defer the screen to a later epic before handing off to `/rai-epic-plan`. Do not silently accept gaps.
### Step 5: Draw the V1 Boundary
Split the epic into:
- **v1 must-have**
- **defer**
If an item does not change planning, it does not belong here.
### Step 6: Write the Artifact
Create `work/epics/e{N}-{name}/ux-design.md` with:
- users
- jobs to be done
- workflow
- surface inventory
- screen-to-story coverage map (from Step 4a)
- trust boundaries
- v1/deferred split
- planning implications
Recommended CLI:
Use `raise_docs_write` MCP tool with doc_type="epic-design", title="E{N}: {epic-name} UX design", content="[ux design content]", output_path="work/epics/e{N}-{name}/ux-design.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write epic-design \
  --title "E{N}: {epic-name} UX design" \
  --stdin \
  --output-path work/epics/e{N}-{name}/ux-design.md << 'EOF'
[ux design content]
EOF
```
### Step 7: Hand Off to Planning
End with 3-7 concrete planning implications:
- stories that must exist
- stories that can be cut
- sequencing constraints created by the workflow
Then emit completion:
<verification>
User-facing workflow is explicit. Trust boundaries are named. V1 cut is clear. `ux-design.md` exists and is useful input to `/rai-epic-plan`.
</verification>
## Output
Primary artifact: `work/epics/e{N}-{name}/ux-design.md`
Next: `/rai-epic-plan`
## Quality Checklist
- [ ] Explicit trigger or skip decision made
- [ ] Primary user and top jobs identified
- [ ] Workflow includes review/trust boundaries
- [ ] Surfaces are concrete, not abstract
- [ ] V1 cut is explicit
- [ ] Planning implications are actionable
## References
- Previous: `/rai-epic-design`
- Next: `/rai-epic-plan`
