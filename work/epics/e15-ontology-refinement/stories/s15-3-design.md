---
id: S15.3
title: "Constraint Edges"
epic: E15
size: S
sp: 3
status: design
depends_on: [S15.2]
adr: ADR-023
---

# S15.3: Constraint Edges

## What & Why

**Problem:** The graph has bounded contexts and layers (S15.2) but no way to ask "what constraints apply to this bounded context?" Guardrail nodes exist (22 total) but are disconnected from the structural nodes. Worse, the scope mapping (which guardrails apply where) lives in ADR-023 prose — the builder would have to hardcode it.

**Value:** `constrained_by` edges make constraints navigable. A typed BFS from any module → its BC → applicable guardrails gives reliable constraint discovery. By moving the scope mapping into `guardrails.md` frontmatter, the mapping becomes **governance data, not code** — editable by humans, extractable by machines.

## Approach

Two changes working together:

1. **Data layer:** Add YAML frontmatter to `guardrails.md` with `constraint_scopes` — the mapping of guardrail categories to bounded contexts/layers
2. **Graph layer:** Add `constrained_by` to EdgeType, builder reads scope from guardrail metadata

**Design principle:** The builder doesn't decide which guardrails apply where. The guardrails document declares it. The builder just reads and connects. **Poka-yoke: if scope isn't declared, the edge can't be created.**

### Components Affected

| Component | Change | What |
|-----------|--------|------|
| `governance/guardrails.md` | **Modify** | Add YAML frontmatter with `constraint_scopes` mapping |
| `governance/parsers/guardrails.py` | **Modify** | Parse frontmatter, propagate `scope` to each guardrail's metadata |
| `context/models.py` | **Modify** | Add `constrained_by` to EdgeType |
| `context/builder.py` | **Modify** | Add `_extract_constraints()` — reads scope from guardrail metadata |
| `tests/` | **Modify** | Tests for parser frontmatter + constraint edges |

## Guardrails Frontmatter Design

Add YAML frontmatter to `governance/guardrails.md`:

```yaml
---
type: guardrails
version: "2.0.0"
constraint_scopes:
  # Default: guardrails apply to all bounded contexts
  default: all_bounded_contexts
  # Overrides: specific categories with narrower scope
  # Key format: {level}-{category} extracted from guardrail ID
  overrides:
    must-arch: [bc-ontology, bc-skills]
    should-cli: [lyr-orchestration]
---
```

**Why this shape:**
- `default` covers 19 of 22 guardrails — no repetition
- `overrides` only lists exceptions (2 entries) — minimal, maintainable
- Key is `{level}-{category}` — deterministic extraction from guardrail ID
- Values are node IDs — directly usable by the builder, no interpretation needed

**Scope resolution for a guardrail:**
1. Extract prefix: `guardrail-must-arch-001` → strip `guardrail-`, strip last `-NNN` → `must-arch`
2. Check `overrides[must-arch]` → found: `[bc-ontology, bc-skills]`
3. If not found → use `default` (all_bounded_contexts)

## Parser Changes

`extract_guardrails()` currently:
1. Reads full file content
2. Finds `###` sections with tables
3. Parses table rows into Concepts

**Add:** Parse frontmatter before section finding. Propagate resolved scope to each guardrail's metadata.

```python
def extract_guardrails(file_path, project_root=None):
    content = file_path.read_text()

    # NEW: Parse frontmatter if present
    frontmatter = _parse_frontmatter(content)
    body = _strip_frontmatter(content)
    scopes = frontmatter.get("constraint_scopes", {})

    # Existing: find sections and parse tables from body
    section_tables = _find_section_tables(body)

    for section_name, table_text in section_tables:
        for guardrail in _parse_guardrail_table(table_text, section_name):
            # NEW: Resolve scope for this guardrail
            prefix = _extract_prefix(guardrail["id"])  # "MUST-ARCH-001" → "must-arch"
            scope = scopes.get("overrides", {}).get(prefix, scopes.get("default", "all_bounded_contexts"))

            concept = Concept(
                id=f"guardrail-{guardrail['id'].lower()}",
                # ... existing fields ...
                metadata={
                    # ... existing metadata ...
                    "constraint_scope": scope,  # NEW: scope for builder
                },
            )
```

**Prefix extraction:** `MUST-ARCH-001` → lowercase → `must-arch-001` → rsplit `-` once from right → `must-arch`

## Builder Changes

`_extract_constraints()` reads scope from guardrail node metadata — no hardcoded mapping:

```python
def _extract_constraints(self, all_nodes, node_by_id):
    edges = []
    bc_nodes = [n for n in node_by_id.values() if n.type == "bounded_context"]
    bc_ids = [n.id for n in bc_nodes]

    for node in all_nodes:
        if node.type != "guardrail":
            continue

        scope = node.metadata.get("constraint_scope", "all_bounded_contexts")

        if scope == "all_bounded_contexts":
            targets = bc_ids
        elif isinstance(scope, list):
            targets = [t for t in scope if t in node_by_id]
        else:
            continue

        for target_id in targets:
            edges.append(ConceptEdge(
                source=target_id, target=node.id,
                type="constrained_by", weight=1.0,
            ))

    return edges
```

**Key:** Builder is dumb — it reads `constraint_scope` and connects. All intelligence is in the governance data.

## build() Integration

```python
# In build(), after structural nodes added:
node_by_id.update({n.id: n for n in structural_nodes})

constraint_edges = self._extract_constraints(all_nodes, node_by_id)
structural_edges.extend(constraint_edges)
```

## Expected Edge Count

| Prefix | Scope | Targets | Count |
|--------|-------|---------|-------|
| `must-code` | default (ALL BCs) | 10 × 3 | 30 |
| `must-test` | default (ALL BCs) | 10 × 2 | 20 |
| `must-sec` | default (ALL BCs) | 10 × 2 | 20 |
| `must-dev` | default (ALL BCs) | 10 × 2 | 20 |
| `must-arch` | override: [bc-ontology, bc-skills] | 2 × 2 | 4 |
| `should-cli` | override: [lyr-orchestration] | 1 × 1 | 1 |
| `should-*` (rest) | default (ALL BCs) | 10 × 10 | 100 |
| **Total** | | | **195** |

## Examples

### API Usage

```python
graph = builder.build()

# What constrains the ontology bounded context?
constraints = graph.get_neighbors("bc-ontology", edge_types=["constrained_by"])
# → 21 guardrails (19 universal + 2 arch-specific)

# What constrains the orchestration layer?
constraints = graph.get_neighbors("lyr-orchestration", edge_types=["constrained_by"])
# → 1 guardrail (should-cli-001)

# Two-hop: module → BC → constraints
bc = graph.get_neighbors("mod-memory", edge_types=["belongs_to"])
# → [bc-ontology]
constraints = graph.get_neighbors("bc-ontology", edge_types=["constrained_by"])
# → 21 guardrails
```

### CLI Usage

```bash
raise memory build
raise memory query "bc-ontology" --strategy concept_lookup
# → bc-ontology + constrained_by neighbors
```

## Acceptance Criteria

### MUST

- [ ] `guardrails.md` has YAML frontmatter with `constraint_scopes` (default + overrides)
- [ ] Guardrails parser reads frontmatter and propagates `constraint_scope` to metadata
- [ ] `constrained_by` added to EdgeType Literal
- [ ] `_extract_constraints()` reads scope from guardrail metadata (no hardcoded mapping)
- [ ] 195 `constrained_by` edges created
- [ ] All quality gates pass (ruff, pyright --strict, pytest >90%)

### SHOULD

- [ ] Graceful degradation: no frontmatter → no constraint edges (not crash)
- [ ] Graceful degradation: no BC/layer nodes → no constraint edges
- [ ] Edge weight = 1.0 (explicit structural relationship)

### MUST NOT

- [ ] Hardcode scope mapping in the builder — scope comes from guardrails.md data
- [ ] Create edges to nodes that don't exist in the graph
- [ ] Break existing guardrail extraction (tables still parsed as before)
- [ ] Break existing belongs_to/in_layer edges (S15.2)
