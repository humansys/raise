---
story_id: "S15.5"
title: "Architectural Context Query Helpers"
epic_ref: "E15 Ontology Graph Refinement"
story_points: 3
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Feature: Architectural Context Query Helpers

> **Epic**: E15 - Ontology Graph Refinement
> **Complexity**: moderate | **SP**: 3

---

## 1. What & Why

**Problem**: Skills and CLI users need multiple separate queries to understand a module's architectural context — its domain, layer, constraints, and dependencies are scattered across different graph traversals.

**Value**: A single `get_architectural_context("memory")` call returns everything a design skill needs — bounded context, layer, applicable guardrails, and module dependencies. This is the enabler for S15.6 (ontology-guided design by default).

---

## 2. Approach

**How we'll solve it**: Add convenience methods to `UnifiedQueryEngine` that compose typed BFS traversals (using `edge_types` from S15.4) into single-call helpers. Expose via new CLI subcommands under `rai memory`.

**Components affected**:
- **`context/query.py`**: Add 4 helper methods + `ArchitecturalContext` model (modify)
- **`cli/commands/memory.py`**: Add `context` subcommand (modify)

---

## 3. Interface / Examples

### Python API

```python
from raise_cli.context.query import UnifiedQueryEngine, ArchitecturalContext

engine = UnifiedQueryEngine.from_file(Path(".raise/rai/memory/index.json"))

# Single-call: full architectural context
ctx: ArchitecturalContext = engine.get_architectural_context("mod-memory")
# ctx.module       → ConceptNode (mod-memory)
# ctx.domain       → ConceptNode (bc-ontology) | None
# ctx.layer        → ConceptNode (lyr-domain) | None
# ctx.constraints  → list[ConceptNode] (guardrails via constrained_by)
# ctx.dependencies → list[ConceptNode] (modules via depends_on)

# Individual helpers
domain = engine.find_domain_for("mod-memory")       # → ConceptNode | None
layer = engine.find_layer_for("mod-memory")          # → ConceptNode | None
constraints = engine.find_constraints_for("mod-memory")  # → list[ConceptNode]
```

### CLI Usage

```bash
# Full architectural context (primary command)
$ rai memory context mod-memory

# Output:
# Module: mod-memory — Manage Rai's persistent memory...
# Domain: bc-ontology — Persist, integrate, and query accumulated knowledge
# Layer: lyr-domain — Domain layer
# Constraints: 13 guardrails
#   MUST: guardrail-must-code-001, guardrail-must-code-002, ...
#   SHOULD: guardrail-should-code-002, ...
# Dependencies: mod-context, mod-telemetry
```

### Data Structures

```python
class ArchitecturalContext(BaseModel):
    """Full architectural context for a module."""

    module: ConceptNode
    domain: ConceptNode | None = None
    layer: ConceptNode | None = None
    constraints: list[ConceptNode] = Field(default_factory=list)
    dependencies: list[ConceptNode] = Field(default_factory=list)
```

**IMPORTANT**: The helpers use the module's `belongs_to` edge to find its bounded context, then follow `constrained_by` edges from that BC to find applicable guardrails. This is a two-hop traversal: module → BC → guardrails.

---

## 4. Acceptance Criteria

### Must Have

- [ ] `get_architectural_context(module_id)` returns `ArchitecturalContext` with domain, layer, constraints, dependencies
- [ ] `find_domain_for(module_id)` follows `belongs_to` edge to bounded context
- [ ] `find_layer_for(module_id)` follows `in_layer` edge to layer node
- [ ] `find_constraints_for(module_id)` follows `belongs_to` → BC → `constrained_by` → guardrails
- [ ] `rai memory context <module_id>` formats output via Rich console
- [ ] Returns empty/None gracefully when module has no domain, layer, or constraints
- [ ] Unit tests >90% coverage on new code

### Should Have

- [ ] `rai memory context` with `--format json` for machine consumption
- [ ] Helper methods handle non-existent module IDs gracefully (return None/empty)

### Must NOT

- [ ] Must NOT use keyword search for constraint discovery — typed BFS only (ADR-023)
- [ ] Must NOT duplicate graph traversal logic — reuse `get_neighbors(edge_types=...)` from S15.4

---

## References

**Related ADRs**:
- ADR-023: Ontology Graph Extension (typed queries as primary retrieval)
- ADR-019: Unified Context Graph Architecture

**Related Stories**:
- S15.3: Constraint Edges (creates `constrained_by` edges these helpers traverse)
- S15.4: Edge-Type Filtering (provides `edge_types` parameter these helpers use)
- S15.6: Skills Integration (consumes these helpers)

**Patterns**:
- PAT-175: Ontology-guided design by default
- PAT-186: Design is not optional

---

**Created**: 2026-02-08
