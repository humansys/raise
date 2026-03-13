# E479 Design: ISO 27001 Audit Report Generator

## Gemba (Current State)

Teams preparing for ISO 27001 audits manually collect evidence from:
- Git logs → copy-paste into spreadsheets
- Test results → screenshots or manual summaries
- Decisions → search through docs and chat history

This takes days per audit cycle. RaiSE already produces structured artifacts (commits, gates, sessions, ADRs) that map to ISO controls — but no tool connects them.

## Target Architecture

```
┌─────────────────┐
│  Control Map     │  ← YAML: control → evidence sources
│  (A.8 subset)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Git    │ │ Gate   │ │Session │  ← Evidence Extractors
│Extractor│ │Extractor│ │Extractor│
└────┬───┘ └────┬───┘ └────┬───┘
     │          │          │
     ▼          ▼          ▼
┌─────────────────────────────┐
│     Evidence Collection      │  ← Pydantic models
│  List[EvidenceItem]          │
└────────────┬────────────────┘
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
┌────────┐┌──────┐┌─────┐
│Markdown││ PDF  ││ CSV │  ← Report Renderers
└────────┘└──────┘└─────┘
```

## Key Contracts

### EvidenceItem (Pydantic)
- control_id: str (e.g. "A.8.32")
- control_name: str
- evidence_type: Literal["git", "gate", "session"]
- title: str
- description: str
- timestamp: datetime
- source_ref: str (commit hash, file path, etc.)
- url: str | None

### ControlMapping (YAML → Pydantic)
- control_id: str
- control_name: str
- description: str
- evidence_sources: list[EvidenceSourceConfig]

## Key Decisions

- **No ADR needed**: Architecture is straightforward extract-transform-render pipeline
- **Pydantic models** for all data structures (project standard)
- **YAML config** for control mapping (auditor-customizable without code changes)
- **Markdown as intermediate** format — PDF and CSV derive from the same evidence collection
- **Git-only** for v1 — no Jira/Confluence extractors yet
