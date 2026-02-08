---
type: module
name: schemas
purpose: "Shared Pydantic models for cross-module data structures"
status: current
depends_on: []
depended_by: [context, discovery, governance, memory, output]
entry_points: []
public_api: []
components: 0
constraints:
  - "No internal dependencies — leaf module"
  - "Currently minimal — most models live in their owning modules"
---

## Purpose

The schemas module is a placeholder for shared Pydantic models that need to be imported by multiple modules without creating circular dependencies. In practice, most data models currently live in their owning modules (e.g., `discovery.scanner.Symbol`, `memory.models.MemoryConcept`), so this module is intentionally minimal.

As the codebase grows and cross-module data contracts emerge, shared types will migrate here to keep the dependency graph clean.

## Key Files

- **`__init__.py`** — Module stub. Currently exports nothing.

## Dependencies

None — leaf module by design.

## Conventions

- Only types needed by 3+ modules should live here
- Module-specific types stay in their owning module
- Follow progressive directory structure (PAT-158): start minimal, grow when needed
