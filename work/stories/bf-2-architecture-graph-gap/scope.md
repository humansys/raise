# BF-2: Architecture Graph Gap — Templates + Skills Don't Produce Graph Nodes

> **Type:** Bugfix (systemic)
> **Priority:** P1 — blocks demo-ready onboarding for external projects
> **Found:** 2026-02-09, dry-run of discovery on zambezi-concierge
> **Size:** M (templates + 2 skills + tests)

---

## Defect

After running the full onboarding + discovery cycle on a brownfield project, the graph produces **0 architecture nodes** and **0 module nodes**. The 144 discovered component nodes are structurally orphaned — not grouped into modules, not placed in bounded contexts, no design narrative.

## Root Cause (Ishikawa)

Three gaps identified via 5-Whys analysis:

### G1: Templates lack YAML frontmatter

`rai_base/governance/architecture/system-context.md` and `system-design.md` are scaffolded as plain Markdown. The graph builder's `_parse_architecture_doc()` requires YAML frontmatter with `type:` field to dispatch parsing:

- `type: architecture_context` → system-context node
- `type: architecture_design` → system-design node
- `type: architecture_domain_model` → domain-model node
- `type: module` → module node

Without frontmatter, the parser silently returns `None` and skips the file.

### G2: `/project-onboard` skill has wrong contract

- Step 6e/6f templates for system-context.md and system-design.md lack YAML frontmatter
- Line 413 states "Architecture docs don't produce individual nodes but enrich the graph context" — this is **false**. The builder code (`load_architecture()`) clearly produces nodes for each type.
- No step generates `domain-model.md` or `modules/` directory

### G3: No skill generates per-module architecture docs

`governance/architecture/modules/*.md` files are what produce `type: module` nodes in the graph. These are the structural backbone — they link components to modules, modules to layers, modules to bounded contexts.

No skill in the current toolkit generates these:
- `/discover-complete` stops at `components-validated.json`
- `/project-onboard` only covers the 6 governance templates
- `/docs-update` updates existing module docs but doesn't create them from scratch

Raise-commons got its module docs through manual creation during story development, then maintained via `/docs-update`.

## Reproduction

```bash
raise init --detect          # scaffolds templates WITHOUT frontmatter
/project-onboard             # fills templates WITHOUT frontmatter
/discover-start → scan → validate → complete  # produces components only
raise discover build         # loads components into graph
raise memory build           # builds full index
raise memory query "architecture"  # → 0 results
```

## Fix Scope

### F1: Fix templates in `rai_base` (G1)

Add YAML frontmatter to scaffolded architecture templates:

- `rai_base/governance/architecture/system-context.md` — add `type: architecture_context` frontmatter
- `rai_base/governance/architecture/system-design.md` — add `type: architecture_design` frontmatter
- Add new template: `rai_base/governance/architecture/domain-model.md` with `type: architecture_domain_model` frontmatter

### F2: Fix `/project-onboard` skill (G2)

- Step 6e: Add YAML frontmatter to system-context.md template
- Step 6f: Add YAML frontmatter to system-design.md template with `layers:` structure
- Add Step 6g: Generate `domain-model.md` with bounded contexts inferred from discovery modules
- Correct line 413: Architecture docs DO produce graph nodes
- Add verification in Step 7: Check for architecture node types, not just governance nodes

### F3: Add module doc generation (G3)

Option A: Extend `/discover-complete` with a "generate module docs" step after JSON export
Option B: Create a new step in `/project-onboard` that generates `modules/*.md` from discovery analysis
Option C: Create a dedicated `/discover-describe` skill

**Recommended:** Option B (extend `/project-onboard`) — this is where the full context (discovery + conversation) is available. The module docs need both structural data (from scan) and intent data (from user).

### F4: Fix `/project-create` skill (if same gap exists)

Check if `/project-create` has the same frontmatter gap in its architecture templates. Likely yes — fix in parallel.

## Acceptance Criteria

1. After `raise init --detect` + `/project-onboard` on a brownfield project:
   - `raise memory query "architecture"` returns architecture nodes (context, design, domain model)
   - `raise memory query --types module` returns module nodes
   - Module nodes have `depends_on` edges
   - Component nodes are reachable from module nodes

2. Templates in `rai_base/governance/architecture/` have YAML frontmatter

3. `/project-onboard` skill templates include frontmatter and generate:
   - system-context.md (with `type: architecture_context`)
   - system-design.md (with `type: architecture_design`, `layers:`)
   - domain-model.md (with `type: architecture_domain_model`, `bounded_contexts:`)
   - modules/*.md (with `type: module`, one per discovered module)

4. Graph gate in `/project-onboard` Step 7 verifies architecture + module nodes exist

## Test Plan

- Integration test: scaffold → onboard → build graph → assert architecture nodes > 0
- Integration test: assert module nodes match discovered modules
- Unit test: `_parse_architecture_doc()` with new templates produces correct node types
- Template contract test: all `rai_base/governance/architecture/*.md` files have valid YAML frontmatter with `type:` field

## Related

- **PAT-194:** Infrastructure without wiring is invisible debt
- **PAT-202/203:** Templates-as-contract — template files ARE the contract
- **E15:** Ontology Graph Refinement (added `load_architecture()` to builder)
- **E13:** Discovery (added `load_components()` to builder)
- **BF-1:** Previous bugfix (flaky tests)
