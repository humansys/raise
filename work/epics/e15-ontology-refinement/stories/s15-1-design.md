---
story_id: S15.1
title: Ingest All Architecture Docs into Graph
epic: E15 Ontology Graph Refinement
size: S
sp: 3
status: design
components_affected: 3
---

# Design: S15.1 — Ingest All Architecture Docs

## What & Why

**Problem:** Architecture docs (system-context.md, system-design.md, domain-model.md) contain structured knowledge about tech stack, layers, bounded contexts, and governance references — but none of it is in the graph. `load_architecture()` only scans `modules/*.md` and hard-filters `type != "module"`.

**Value:** All architecture knowledge becomes queryable. Foundation for S15.2 (bounded context/layer nodes) and S15.3 (constraint edges). "What's our tech stack?" or "What bounded contexts exist?" become graph queries instead of file reads.

## Approach

Extend `load_architecture()` to scan both `governance/architecture/modules/*.md` (existing) and `governance/architecture/*.md` (new). Add type-dispatch in `_parse_architecture_doc()` that routes by frontmatter `type` field instead of hard-filtering for `module` only.

**Components affected:**

| File | Change |
|------|--------|
| `src/raise_cli/context/models.py` | Add `"architecture"` to NodeType Literal |
| `src/raise_cli/context/builder.py` | Extend `load_architecture()` + refactor `_parse_architecture_doc()` |
| `tests/context/test_builder.py` | Add tests for each new doc type handler |

## Design Decisions

**D1: New `architecture` NodeType** — These docs are not modules, decisions, or guardrails. They're architecture documentation that describes system structure at different C4 levels. Adding `architecture` as a NodeType is semantically accurate and avoids polluting existing type queries. S15.2 will add `bounded_context` and `layer` as additional types that get extracted *from* these architecture nodes.

**D2: Scan parent directory, not just modules/** — Architecture docs live in `governance/architecture/` alongside the `modules/` subdirectory. The method should scan `*.md` in the parent dir (excluding `modules/` subdirectory files, which are already handled).

**D3: Content synthesis from frontmatter** — Each doc type gets a descriptive content string built from its structured data, not just a single `purpose` field:
- `architecture_context` → tech stack + external deps summary
- `architecture_design` → layers with module lists
- `architecture_domain_model` → bounded contexts with module lists
- `architecture_index` → skip (it's a generated summary of modules/, already covered by module nodes)

**D4: ID scheme** — `arch-{type_suffix}` where suffix is derived from frontmatter type:
- `arch-context` for system-context.md
- `arch-design` for system-design.md
- `arch-domain-model` for domain-model.md

**D5: Store full structured data in metadata** — All frontmatter fields (layers, bounded_contexts, tech_stack, etc.) go into node metadata. This is critical for S15.2, which will extract bounded_context and layer nodes from this metadata without re-parsing files.

## Examples

### New node for system-design.md:

```python
ConceptNode(
    id="arch-design",
    type="architecture",
    content="System design: 4 layers (leaf, domain, integration, orchestration). "
            "Leaf: core, config, schemas. Domain: governance, discovery, skills, telemetry. "
            "Integration: context, memory, onboarding, output. Orchestration: cli.",
    source_file="governance/architecture/system-design.md",
    created="2026-02-08T...",
    metadata={
        "arch_type": "architecture_design",
        "layers": [
            {"name": "leaf", "modules": ["core", "config", "schemas"], "description": "..."},
            {"name": "domain", "modules": ["governance", "discovery", "skills", "telemetry"], "description": "..."},
            ...
        ],
        "architectural_decisions": ["ADR-012: ...", "ADR-019: ...", ...],
        "guardrails_reference": "governance/guardrails.md",
    },
)
```

### New node for domain-model.md:

```python
ConceptNode(
    id="arch-domain-model",
    type="architecture",
    content="Domain model: 7 bounded contexts — governance, discovery, ontology, "
            "skills, experience, observability, integrations (planned). "
            "Shared kernel: config, core, schemas.",
    source_file="governance/architecture/domain-model.md",
    created="2026-02-08T...",
    metadata={
        "arch_type": "architecture_domain_model",
        "bounded_contexts": [
            {"name": "governance", "modules": ["governance"], "description": "..."},
            {"name": "ontology", "modules": ["context", "memory"], "description": "..."},
            ...
        ],
        "shared_kernel": {"modules": ["config", "core", "schemas"], "description": "..."},
        "application_layer": {"modules": ["cli"], "description": "..."},
    },
)
```

### CLI verification:

```bash
# After graph rebuild:
raise memory query "architecture" --types architecture
# Should return: arch-context, arch-design, arch-domain-model

raise memory query "bounded context ontology" --types architecture
# Should return: arch-domain-model (content mentions bounded contexts)
```

## Acceptance Criteria

**MUST:**
- [ ] `architecture` added to NodeType Literal
- [ ] `load_architecture()` scans both `modules/*.md` and parent `*.md`
- [ ] `_parse_architecture_doc()` dispatches by `type` field (module, architecture_context, architecture_design, architecture_domain_model)
- [ ] Each non-module doc type produces a ConceptNode with synthesized content and full frontmatter in metadata
- [ ] `architecture_index` type is skipped (no value as separate node)
- [ ] Existing module doc parsing unchanged (backward compatible)
- [ ] Tests for each new doc type handler + edge cases

**MUST NOT:**
- [ ] Break existing module node ingestion
- [ ] Add bounded_context or layer NodeTypes (that's S15.2)
- [ ] Modify the query engine

---

*Created: 2026-02-07*
