# BF-2 Design: Architecture Graph Gap

> **Story:** BF-2 | **Size:** L | **Phase:** Design
> **Modules affected:** mod-memory (validate), rai_base (templates), skills (project-onboard, project-create)

---

## Problem

After full onboarding + discovery on a brownfield project, the graph produces 0 architecture nodes and 0 module nodes. 144 component nodes are structurally orphaned. The system reports no error.

## Value

Without architecture and module nodes, Rai has no structural context — no layers, no bounded contexts, no module groupings. The Jumpstart client would get a flat bag of components with no navigable architecture. The graph silently looks "fine" but is semantically empty.

---

## Architectural Context

**Primary modules:**
- `mod-memory` (bc-ontology, lyr-integration) — validate command extension
- `rai_base` (distributed templates) — template frontmatter fix

**Skills affected:**
- `/project-onboard` — frontmatter in templates, module doc generation, graph gate
- `/project-create` — same frontmatter gap

**Parser (read-only, no changes):**
- `context/builder.py::_parse_architecture_doc` — correctly dispatches on `type:` frontmatter field. The parser is right; the templates are wrong.

---

## Approach

Five fixes, ordered by dependency:

### F1: Fix rai_base templates

Add YAML frontmatter to scaffolded architecture templates so the parser can find them.

**Files:**
- `src/raise_cli/rai_base/governance/architecture/system-context.md` — add `type: architecture_context` frontmatter
- `src/raise_cli/rai_base/governance/architecture/system-design.md` — add `type: architecture_design` frontmatter
- Create `src/raise_cli/rai_base/governance/architecture/domain-model.md` — add `type: architecture_domain_model` frontmatter

**Frontmatter contract** (matches what `_parse_architecture_doc` expects):

```yaml
# system-context.md
---
type: architecture_context
project: "{project_name}"
status: draft
tech_stack: {}
external_dependencies: []
users: []
governed_by: []
---
```

```yaml
# system-design.md
---
type: architecture_design
project: "{project_name}"
status: draft
layers: []
---
```

```yaml
# domain-model.md
---
type: architecture_domain_model
project: "{project_name}"
status: draft
bounded_contexts: []
shared_kernel: {}
---
```

**IMPORTANT:** Templates use `{project_name}` placeholder — the existing `raise init` scaffold replaces this. Verify the placeholder substitution still works after adding frontmatter.

### F2: Fix /project-onboard skill

Update skill templates to include YAML frontmatter and add missing generation steps.

**Changes:**
1. Step 6e (system-context.md): Add frontmatter block with `type: architecture_context`, `tech_stack`, `external_dependencies`, `users`
2. Step 6f (system-design.md): Add frontmatter block with `type: architecture_design`, `layers` structure populated from discovery modules
3. Add Step 6g: Generate `domain-model.md` with `type: architecture_domain_model`, `bounded_contexts` inferred from discovered module groupings
4. Correct line ~413: Remove false statement "Architecture docs don't produce individual nodes" → replace with "Architecture docs produce graph nodes (arch-context, arch-design, arch-domain-model)"
5. Add Step 6h: Generate `governance/architecture/modules/*.md` — one per discovered module, with `type: module` frontmatter

**Module doc template** (matches `_parse_module_doc` expectations):

```yaml
---
type: module
name: "{module_name}"
purpose: "{synthesized_purpose}"
status: draft
depends_on: [{detected_dependencies}]
depended_by: []
entry_points: []
public_api: []
components: {component_count}
---

# Module: {module_name}

> {purpose}

## Responsibility

{What this module does — synthesized from discovery scan + user conversation}

## Components

{List of components discovered in this module}
```

6. Update Step 7 verification: After `raise memory build`, check for architecture node types — not just governance node count

### F3: Fix /project-create skill

Same frontmatter gap. Apply identical changes to Steps 6e, 6f, add 6g (domain-model). Module doc generation is N/A for greenfield (no discovery data yet).

### F4: Graph completeness postcondition

Extend `raise memory validate` with a completeness check.

**Implementation in `src/raise_cli/cli/commands/memory.py`:**

Add a new check after existing structural validation:

```python
# Check 4: Completeness — expected node types present
EXPECTED_ARCHITECTURE_TYPES = {
    "architecture": 1,        # ≥1 arch-* node (context, design, or domain model)
    "module": 1,              # ≥1 mod-* node
}

type_counts: dict[str, int] = {}
for node in graph.iter_concepts():
    type_counts[node.type] = type_counts.get(node.type, 0) + 1

missing = []
for node_type, min_count in EXPECTED_ARCHITECTURE_TYPES.items():
    actual = type_counts.get(node_type, 0)
    if actual < min_count:
        missing.append((node_type, min_count, actual))

if missing:
    console.print("  [yellow]⚠[/yellow]  Completeness gaps:")
    for node_type, expected, actual in missing:
        console.print(f"    {node_type}: expected ≥{expected}, found {actual}")
else:
    console.print("  ✓ Graph completeness check passed")
```

**Key decisions:**
- Warning, not error — a graph without architecture nodes is structurally valid, just incomplete
- Minimal expectations — just "has architecture" and "has modules". Not lifecycle-phase-aware (that's a future story)
- Same command — extend existing `validate`, don't create new command
- No new CLI flags needed — completeness check always runs as part of validation

### F5: Update /project-onboard graph gate

In Step 7, after `raise memory build`, run `raise memory validate`. If completeness warnings appear, the skill should report them to the user rather than silently continuing.

---

## Examples

### After fix: `raise init --detect` scaffold

```
governance/
  architecture/
    system-context.md    ← has type: architecture_context frontmatter
    system-design.md     ← has type: architecture_design frontmatter
    domain-model.md      ← NEW, has type: architecture_domain_model frontmatter
  guardrails.md          ← already has frontmatter (no change)
  vision.md
  prd.md
  backlog.md
```

### After fix: `/project-onboard` on zambezi-concierge

```bash
$ raise memory validate
Memory Index Validation
  ✓ 168 concepts loaded
  ✓ All relationships valid
  ✓ No cycles detected
  ✓ Graph completeness check passed    ← NEW
  ✓ 168/168 concepts reachable

$ raise memory query --types architecture
arch-context    System Context: zambezi-concierge
arch-design     System Design: zambezi-concierge
arch-domain-model  Domain Model: zambezi-concierge

$ raise memory query --types module
mod-api         Express API server
mod-frontend    Svelte SPA frontend
mod-shared      Shared utilities and types
```

### Completeness warning (when gap exists)

```bash
$ raise memory validate
Memory Index Validation
  ✓ 144 concepts loaded
  ✓ All relationships valid
  ✓ No cycles detected
  ⚠  Completeness gaps:
    architecture: expected ≥1, found 0
    module: expected ≥1, found 0
  ✓ 144/144 concepts reachable
```

---

## Acceptance Criteria

**MUST:**
1. All `rai_base/governance/architecture/*.md` templates have valid YAML frontmatter with `type:` field
2. `_parse_architecture_doc()` produces nodes from scaffolded templates (template contract test)
3. `/project-onboard` skill generates architecture docs with frontmatter + module docs
4. `raise memory validate` warns when architecture/module nodes are missing
5. Tests pass, types pass, lint passes

**SHOULD:**
1. `/project-create` skill has same frontmatter fix
2. Module docs include `depends_on` from discovery analysis

**MUST NOT:**
- Change `_parse_architecture_doc` or `builder.py` — the parser is correct
- Make completeness check a hard failure (warning only)
- Generate module docs without user context available (module purpose needs inference)

---

## Testing Approach

1. **Template contract test:** All `rai_base/governance/architecture/*.md` files parse successfully through `_parse_architecture_doc` → produce non-None nodes
2. **Completeness validation test:** Graph with 0 architecture nodes → warning. Graph with ≥1 → pass.
3. **Module doc frontmatter test:** Generated module doc frontmatter matches `_parse_module_doc` expected fields
4. **Integration test (if time):** scaffold → parse → build → validate → assert architecture + module nodes > 0
