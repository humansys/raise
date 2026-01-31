# Component Catalog

> **Purpose:** Single source of truth for all raise-cli components
> **Audience:** Contributors, GraphRAG, future maintainers
> **Update:** Per feature as components are added
> **Status:** Living document

---

## How to Use This Catalog

**For contributors:** Find what exists, understand dependencies, avoid duplication
**For GraphRAG:** Query "What does X do?", "What uses Y?", "Where is Z?"
**For reviewers:** Verify new components are documented

---

## Engines (Domain Layer)

> Pure business logic - no I/O awareness

### [No engines yet - E2 will add KataEngine, E3 will add GateEngine]

---

## Handlers (Application Layer)

> Orchestration and use case coordination

### [No handlers yet - E2 will add KataHandler, E3 will add GateHandler]

---

## CLI Commands (Presentation Layer)

> User-facing commands

### Global Options (F1.2)
- **Location:** `src/raise_cli/cli/main.py`
- **Purpose:** Global options for all commands (format, verbosity, quiet)
- **Added:** F1.2 (Epic E1)
- **API:**
  - `--format/-f` (human|json|table)
  - `--verbose/-v` (count, up to -vvv)
  - `--quiet/-q` (suppress non-error output)
- **Storage:** `ctx.obj["format"]`, `ctx.obj["verbosity"]`, `ctx.obj["quiet"]`

---

## Schemas (Data Models)

> Pydantic models for type-safe data structures

### [No schemas yet - will be added as engines are built]

---

## Configuration (Core Layer)

### [No config yet - F1.3 will add RaiseSettings]

---

## Output Formatters (Core Layer)

### [No formatters yet - F1.5 will add human/json/table formatters]

---

## Utilities (Core Layer)

### [No utilities yet - F1.6 will add subprocess wrappers]

---

## Metadata

- **Started:** 2026-01-31 (E1 foundation)
- **Last Updated:** 2026-01-31 (F1.2 complete)
- **Components:** 1 (Global Options)
- **Next:** F1.3 Configuration System

---

*Component catalog - updated per feature completion*
