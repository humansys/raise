# Story Scope: S15.1 — Ingest All Architecture Docs

**Epic:** E15 Ontology Graph Refinement
**Size:** S (3 SP)
**Branch:** `epic/e15/ontology-refinement` (S-sized, no story branch)

---

## In Scope

- Extend `load_architecture()` to ingest all architecture doc types (not just modules)
- Add type-dispatch in `_parse_architecture_doc()` for:
  - `architecture_context` → system-context.md (tech stack, external deps)
  - `architecture_design` → system-design.md (layers, ADRs, guardrails ref)
  - `architecture_domain_model` → domain-model.md (bounded contexts, communication)
  - `architecture_index` → index.md (if present)
- Each doc type gets appropriate node ID scheme and content extraction
- Tests for new parsing paths

## Out of Scope

- Bounded context / layer nodes (S15.2)
- Constraint edges (S15.3)
- Query engine changes (S15.4-S15.6)
- Modifying existing module doc ingestion

## Done Criteria

- [ ] All architecture docs (system-context, system-design, domain-model) ingested as graph nodes
- [ ] Each doc type has its own NodeType-appropriate node with meaningful content
- [ ] `_parse_architecture_doc()` dispatches by `type` field from frontmatter
- [ ] Unit tests for each new doc type handler
- [ ] All quality checks pass (ruff, pyright, tests)
- [ ] Graph rebuild includes new nodes

---

*Created: 2026-02-07*
