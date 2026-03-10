---
id: S15.2
title: "Bounded Context and Layer Nodes"
epic: E15
size: S
sp: 3
status: design
depends_on: [S15.1]
adr: ADR-023
---

# S15.2: Bounded Context and Layer Nodes

## What & Why

**Problem:** The graph has module nodes but no structural grouping. There's no way to ask "which bounded context owns this module?" or "what layer is this module in?" — queries that S15.3 (constraints) and S15.5 (helpers) depend on.

**Value:** Domain boundaries and layer positions become navigable graph relationships. Foundation for constraint mapping (S15.3) and architectural context queries (S15.5).

## Approach

Add `bounded_context` and `layer` NodeTypes. Add `belongs_to` and `in_layer` EdgeTypes. Extract nodes and edges from the already-ingested `arch-domain-model` and `arch-design` node metadata (built by S15.1).

**Implementation strategy:** New `_extract_bounded_contexts()` and `_extract_layers()` methods in `UnifiedGraphBuilder`, called at the end of `load_architecture()` after arch nodes are built. These methods read from the in-memory arch node metadata — no re-parsing of files needed.

### Components Affected

| Component | Change | What |
|-----------|--------|------|
| `context/models.py` | **Modify** | Add `bounded_context`, `layer` to NodeType; add `belongs_to`, `in_layer` to EdgeType |
| `context/builder.py` | **Modify** | Add `_extract_bounded_contexts()`, `_extract_layers()` methods; call from `load_architecture()` |
| `tests/context/test_builder.py` | **Modify** | Add test class for BC/layer extraction |

## Data Sources (Validated)

### domain-model.md frontmatter (→ bounded_context + shared_kernel nodes)

```yaml
bounded_contexts:
  - name: governance
    modules: [governance]
  - name: discovery
    modules: [discovery]
  - name: ontology
    modules: [context, memory]
  - name: skills
    modules: [skills]
  - name: experience
    modules: [onboarding, output]
  - name: observability
    modules: [telemetry]
  - name: integrations         # status: planned, modules: []
    modules: []
shared_kernel:
  modules: [config, core, schemas]
application_layer:
  modules: [cli]
distribution:
  modules: [rai_base, skills_base]
```

### system-design.md frontmatter (→ layer nodes)

```yaml
layers:
  - name: leaf
    modules: [core, config, schemas]
  - name: domain
    modules: [governance, discovery, skills, telemetry]
  - name: integration
    modules: [context, memory, onboarding, output]
  - name: orchestration
    modules: [cli]
```

## Node ID Scheme

| Type | ID Pattern | Examples |
|------|-----------|----------|
| bounded_context | `bc-{name}` | `bc-governance`, `bc-ontology`, `bc-shared-kernel` |
| layer | `lyr-{name}` | `lyr-leaf`, `lyr-domain`, `lyr-integration`, `lyr-orchestration` |

**IMPORTANT:** shared_kernel, application_layer, and distribution are modeled as bounded_context nodes (they group modules). This keeps the query pattern uniform: every module has a `belongs_to` edge.

## Expected Nodes (12)

| ID | Type | Content |
|----|------|---------|
| `bc-governance` | bounded_context | "Extract structured knowledge from markdown governance documents" |
| `bc-discovery` | bounded_context | "Scan codebases to extract structural knowledge..." |
| `bc-ontology` | bounded_context | "Persist, integrate, and query accumulated knowledge..." |
| `bc-skills` | bounded_context | "Skill parsing, location, validation, and scaffolding..." |
| `bc-experience` | bounded_context | "First-run setup, developer profiles, and presentation" |
| `bc-observability` | bounded_context | "Local signal collection for process improvement" |
| `bc-integrations` | bounded_context | "External platform adapters..." |
| `bc-shared-kernel` | bounded_context | "Foundation utilities shared across all contexts" |
| `lyr-leaf` | layer | "Zero internal dependencies — foundation utilities" |
| `lyr-domain` | layer | "Independent domain logic — no cross-domain imports" |
| `lyr-integration` | layer | "Combines domains into unified capabilities" |
| `lyr-orchestration` | layer | "User-facing entry points — depends on everything..." |

## Expected Edges

### belongs_to (module → bounded_context): 14 edges

```
mod-governance    → bc-governance
mod-discovery     → bc-discovery
mod-context       → bc-ontology
mod-memory        → bc-ontology
mod-skills        → bc-skills
mod-onboarding    → bc-experience
mod-output        → bc-experience
mod-telemetry     → bc-observability
mod-config        → bc-shared-kernel
mod-core          → bc-shared-kernel
mod-schemas       → bc-shared-kernel
mod-cli           → bc-shared-kernel  (application_layer treated as BC node)
mod-rai_base      → bc-shared-kernel  (distribution treated as BC node)
mod-skills_base   → bc-shared-kernel  (distribution treated as BC node)
```

**WAIT — design decision needed.** Application layer (cli) and distribution (rai_base, skills_base) are NOT shared kernel. They are separate groupings in the domain model. Options:

1. Model `application_layer` and `distribution` as separate BC nodes → 10 BC nodes, clean mapping
2. Lump cli/rai_base/skills_base into shared kernel → loses domain model fidelity
3. Only create `belongs_to` edges for modules that appear in `bounded_contexts[]` or `shared_kernel` → 11 modules mapped, 3 unmapped

**Decision: Option 1.** Model all groupings as bounded_context nodes. This matches the source data exactly and gives every module a `belongs_to` edge. The `metadata.bc_type` field distinguishes true bounded contexts from structural groupings.

### Revised: 10 bounded_context nodes

| ID | bc_type | Source |
|----|---------|--------|
| `bc-governance` through `bc-integrations` | `bounded_context` | `bounded_contexts[]` |
| `bc-shared-kernel` | `shared_kernel` | `shared_kernel` |
| `bc-application-layer` | `application_layer` | `application_layer` |
| `bc-distribution` | `distribution` | `distribution` |

### Revised belongs_to edges: 16

Every module maps to exactly one grouping:
- 7 BC modules (governance, discovery, context, memory, skills, onboarding+output, telemetry)
- 3 shared kernel (config, core, schemas)
- 1 application layer (cli)
- 2 distribution (rai_base, skills_base)
- integrations has 0 modules (planned)

**Total:** 13 modules with edges (integrations BC has no modules yet)

### in_layer (module → layer): 12 edges

```
mod-core          → lyr-leaf
mod-config        → lyr-leaf
mod-schemas       → lyr-leaf
mod-governance    → lyr-domain
mod-discovery     → lyr-domain
mod-skills        → lyr-domain
mod-telemetry     → lyr-domain
mod-context       → lyr-integration
mod-memory        → lyr-integration
mod-onboarding    → lyr-integration
mod-output        → lyr-integration
mod-cli           → lyr-orchestration
```

**Note:** rai_base and skills_base are NOT in any layer (they're distribution packages, not runtime modules). No `in_layer` edge for them.

## Examples

### API Usage

```python
# After build(), the graph contains:
graph = builder.build()

# Query bounded contexts
bcs = graph.get_concepts_by_type("bounded_context")
assert len(bcs) == 10  # 7 BCs + shared_kernel + app_layer + distribution

# Query layers
layers = graph.get_concepts_by_type("layer")
assert len(layers) == 4

# Navigate: which BC owns the memory module?
neighbors = graph.get_neighbors("mod-memory", edge_types=["belongs_to"])
# → [ConceptNode(id="bc-ontology", type="bounded_context", ...)]

# Navigate: what layer is the memory module in?
neighbors = graph.get_neighbors("mod-memory", edge_types=["in_layer"])
# → [ConceptNode(id="lyr-integration", type="layer", ...)]
```

### CLI Usage

```bash
# After graph rebuild:
rai memory build

# Query bounded contexts
rai memory query "ontology" --types bounded_context
# → bc-ontology: Persist, integrate, and query accumulated knowledge...

# Query layers
rai memory query "leaf" --types layer
# → lyr-leaf: Zero internal dependencies — foundation utilities
```

## Acceptance Criteria

### MUST

- [ ] `bounded_context` and `layer` added to NodeType Literal
- [ ] `belongs_to` and `in_layer` added to EdgeType Literal
- [ ] 10 bounded_context nodes created from domain-model.md metadata
- [ ] 4 layer nodes created from system-design.md metadata
- [ ] 13 `belongs_to` edges (module → BC) created
- [ ] 12 `in_layer` edges (module → layer) created
- [ ] All quality gates pass (ruff, pyright --strict, pytest >90%)

### SHOULD

- [ ] `metadata.bc_type` distinguishes bounded_context vs shared_kernel vs application_layer vs distribution
- [ ] Graceful degradation if arch-domain-model or arch-design nodes not found

### MUST NOT

- [ ] Re-parse YAML files — use already-built arch node metadata
- [ ] Break existing module or architecture node parsing
- [ ] Create edges to module nodes that don't exist in the graph

## Implementation Notes

**Extraction approach:** `_extract_bounded_contexts()` iterates the nodes list for the `arch-domain-model` node, reads `metadata.bounded_contexts`, `metadata.shared_kernel`, `metadata.application_layer`, `metadata.distribution`, creates BC nodes and `belongs_to` edges. Similarly `_extract_layers()` reads from `arch-design` node's `metadata.layers`.

**Edge safety:** Only create `belongs_to`/`in_layer` edges when the target module node (`mod-{name}`) exists in the nodes list. This prevents dangling edges if a module doc is missing.

**Return type:** Both methods return `tuple[list[ConceptNode], list[ConceptEdge]]` — nodes AND edges, since these are structural relationships, not inferred heuristics. The edges have `weight=1.0` (explicit, not inferred).
