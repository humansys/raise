---
type: module
name: governance
purpose: "Extract semantic concepts from governance markdown files into structured data for the context graph"
status: current
depends_on: [core]
depended_by: [cli, context]
entry_points:
  - "raise context build (via builder)"
public_api:
  - "Concept"
  - "ConceptType"
  - "ExtractionResult"
  - "GovernanceExtractor"
components: 32
constraints:
  - "Independent of discovery module — no cross-imports"
  - "All extraction is deterministic — pattern matching on markdown structure"
  - "Parsers are format-specific, not content-aware"
---

## Purpose

The governance module reads markdown governance files (Constitution, PRD, Vision, Guardrails, Backlog, Glossary, ADRs) and extracts structured `Concept` objects from them. These concepts become nodes in the unified context graph, making governance artifacts queryable via `raise memory query`.

This is what makes RaiSE's "Governance as Code" principle concrete — the governance files aren't just documentation, they're **machine-readable data** that constrains and informs AI behavior.

## Architecture

The module uses a **parser-per-format** architecture. Each governance file type has its own parser because the markdown structure differs (PRD uses tables, Constitution uses numbered sections, Glossary uses definition lists). The `GovernanceExtractor` orchestrates all parsers and returns a unified `ExtractionResult`.

```
governance/*.md → GovernanceExtractor → [Concept, ...] → context graph
```

## Key Files

- **`extractor.py`** — `GovernanceExtractor` class. Discovers governance files in `governance/` and `framework/reference/`, runs appropriate parsers, returns `ExtractionResult`.
- **`models.py`** — `Concept` and `ConceptType` Pydantic models. Every extracted concept has an id, type, content, source file, section, and line range.
- **`parsers/`** — Individual parsers:
  - `constitution.py` — Parses `§N` numbered principles
  - `prd.py` — Parses requirement tables (`RF-*`)
  - `vision.py` — Parses outcome sections (`OUT-*`)
  - `guardrails.py` — Parses code standards (`GR-*`)
  - `backlog.py` — Parses epic entries (`E*`)
  - `epic.py` — Parses story entries from epic scope files (`F*.*`)
  - `glossary.py` — Parses term definitions (`TERM-*`)
  - `adr.py` — Parses ADR files (`ADR-*`)

## Dependencies

| Depends On | Why |
|-----------|-----|
| `core` | File reading utilities |

## Conventions

- Each parser is a standalone function that takes a file path and returns `list[Concept]`
- Concept IDs follow the pattern from the source format (e.g., `§2`, `RF-06.1`, `ADR-019`)
- Parsers use regex and string matching, not AI inference
- New governance file types require a new parser in `parsers/`
