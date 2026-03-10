# ADR-001: Three-Layer Architecture

**Date:** 2026-01-30
**Status:** Accepted
**Deciders:** Emilio Osorio, Rai

---

## Context

raise-cli needs to:
- Serve multiple interfaces (CLI, MCP server, web UI, direct Python imports)
- Keep business logic testable and reusable
- Allow layers to evolve independently
- Support multiple output formats (human, json, table)

Traditional flat CLI architectures (commands directly calling business logic) create tight coupling between presentation and domain logic.

---

## Decision

Use **three-layer architecture** (ports and adapters pattern):

```
Presentation (CLI) → Application (Handlers) → Domain (Engines)
                                                     ↓
                                              Core (Schemas, Config)
```

**Layers:**
1. **Presentation (CLI):** User interface, output formatting, error presentation
2. **Application (Handlers):** Orchestration, use cases, state/metrics management
3. **Domain (Engines):** Pure business logic, no I/O awareness
4. **Core:** Shared schemas, configuration, utilities

**Dependency rule:** Layers only depend downward. Engines never import from CLI or handlers.

---

## Alternatives Considered

### Alternative 1: Direct CLI → Engine
**Rejected because:**
- Engine becomes aware of CLI concerns (formatting, state)
- Can't reuse in MCP server or web UI
- Hard to test business logic in isolation
- Violates single responsibility principle

### Alternative 2: Microservices
**Rejected because:**
- Overkill for v2.0 scope
- Adds network complexity
- Harder to deploy (not just `pip install`)
- Can move to this later if needed (handlers become API)

### Alternative 3: Two layers (CLI + Engine)
**Rejected because:**
- Orchestration logic (state, metrics, validation) has to go somewhere
- Either CLI gets bloated or engine becomes impure
- Handler layer provides clean separation

---

## Consequences

### Positive
- Engines reusable across interfaces (CLI, MCP, web, Python)
- Easy to test each layer independently
- Clear separation of concerns
- Can swap CLI for web UI without touching engines
- Follows industry best practices (Poetry, HTTPie, Black)

### Negative
- More files and indirection (3 files for one feature)
- Need discipline to not violate dependency rules
- Handlers can become "anemic" if not careful

### Mitigations
- **More files:** Accept as cost of maintainability
- **Dependency violations:** Enforce with pyright imports checking
- **Anemic handlers:** Handlers coordinate and manage side effects (state, metrics), engines do computation

---

## References

- Research: `work/research/outputs/python-cli-architecture-analysis.md`
- Design: `governance/projects/raise-cli/design.md` (Section 2.2)
- Examples: Poetry, HTTPie, Black (all use similar patterns)

---

*ADR-001 - Three-layer architecture*
