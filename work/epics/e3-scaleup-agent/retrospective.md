# Epic E3 Retrospective — ScaleUp Knowledge Infrastructure

> Epic: E3 | Jira: LIFE-90
> Started: 2026-03-18 | Completed: 2026-03-22 (5 calendar days)
> Stories: 8 | Total effort: ~905 minutes (~15 hours)
> Tests: 369 passing (knowledge + scaleup modules)

---

## What Was Delivered

### Knowledge Pipeline (domain-agnostic infrastructure)
- **Extraction:** LLM-based chapter-by-chapter extraction with multi-strategy JSON parsing, retry, and reconciliation
- **Validation:** 4 CLI gates (validate, reconcile, coverage, graph) with GateResult model and exit codes
- **Discovery:** Zero-knowledge schema discovery from corpus using Claude Agent SDK
- **Pipeline skills:** 5 interactive Claude Code skills (/rai-knowledge-{discover,extract,validate,diff,run})

### ScaleUp Domain (first domain implementation)
- **447 ontology nodes** extracted from 35 chapters of Scaling Up corpus
- **6 node types** (decision, concept, tool, worksheet, stage, metric) with typed GraphNode subclasses
- **6 relationship types** mapped to RaiSE GraphEdge (belongs-to, requires, feeds-into, measured-by, prerequisite-of, implements)
- **HITL curation skill** (/rai-scaleup-curate) with session engine

### Retrieval & Query
- **Deterministic retrieval engine** — spreading activation + composite scoring (0.5×SA + 0.3×ATTR + 0.2×DOMAIN)
- **Pluggable domain resolution** — adapter, builder, prompting loaded dynamically from domain.yaml (SchemaRef pattern)
- **CLI:** `rai knowledge query scaleup "cash flow"` → ranked results with prompting context
- **3 output formats** (human, compact, json) consistent with `rai graph query`

## Metrics

| Metric | Value |
|---|---|
| Stories completed | 8/8 |
| Total tests | 369 |
| New tests (E3) | ~340 |
| Nodes extracted | 447 |
| Estimated time | ~600 min (original 6 stories) |
| Actual time | ~905 min (expanded to 8 stories) |
| Velocity | 0.66x (but scope grew 33% with S3.7/S3.8/S3.9) |
| Calendar time | 5 days |

## What Went Well

1. **Research grounding paid off** — 128 sources across 5 axes (R0-R4) informed every major decision. Pydantic+NetworkX over SHACL, extend raise-core over adopt Letta/Mem0, symbolic over vector RAG. Zero rework from wrong architectural bets.

2. **Walking skeleton first (S3.1→S3.4)** — validating schema and graph mapping with Eduardo's 10 existing nodes before building the pipeline caught mapping issues early. No late-stage integration surprises.

3. **Domain-agnostic from S3.7** — the decision to make CLI gates generic (not ScaleUp-specific) in S3.7 was the inflection point. Everything after that (S3.8 discovery, S3.6 query) built on pluggable infrastructure. This directly enabled the Domain Cartridges vision (RAISE-650).

4. **Real-world validation** — testing with Eduardo's actual ScaleUp questions proved the retrieval works and revealed the "knowledge without process is passive" insight that shaped the Domain Cartridges concept.

5. **TDD discipline held** — 369 tests across 8 stories. Every story committed tests before implementation. QR gate caught real bugs in S3.2, S3.3, S3.7, S3.8 (silent drops, resource leaks, format injection).

## What Didn't Go Well

1. **Estimation accuracy** — S3.9 was estimated at 105min, took 240min (2.3x over). LLM integration tax (format variance, retry logic, real vs mock testing) was consistently underestimated. S3.7 was sized as S but delivered M complexity.

2. **Worktree DX friction** — the S3.5-S3.9 worktree had path resolution issues with uv/pytest. Required `PYTHONPATH` hack. Discovered `EnterWorktree` only in S3.6 session — should have known earlier.

3. **Keyword-based retrieval gaps** — "hire A players" returns 0 results because the adapter does literal matching. The architecture is sound but the adapter is too rigid. Configurable synonyms or LLM-based interpretation needed.

## Patterns Learned

| ID | Pattern | Type |
|---|---|---|
| PAT-E-001 | Data flow trace in plans prevents wiring bugs | process |
| PAT-E-002 | Never .format() with corpus content — use .replace() | technical |
| PAT-E-003 | LLM output defense-in-depth is mandatory | technical |
| PAT-E-004 | Post-discovery refinement for autonomous gap-filling | technical |
| PAT-E-005 | Guard placement at lowest call level | technical |
| SchemaRef | Universal dynamic import pattern (module+class_name) | architecture |
| Comparison testing | Running with/without a tool reveals product value concretely | process |
| Domain cartridge | Knowledge + Process = complete methodology pack | architecture |

## Process Insights

1. **QR gate ROI is proven** — caught bugs in 4 of 8 stories (50%). Silent data drops (BASE-046), resource leaks, format injection, state machine corruption. Gate cost: ~15min per story. Bug cost if shipped: hours of debugging.

2. **Pre-implementation AR catches structural issues** — S3.5 had 2 wiring bugs; after adding AR + data flow trace, S3.8 had zero. The trace costs 5 minutes and saves 30+ minutes of debugging.

3. **LLM-calling stories need "real LLM test" task** — mock tests pass instantly but miss format variance. Add explicit task for real LLM calls in any story that wraps LLM output.

4. **`/rai-epic-docs` skill validated** — dogfood run on E3 produced comprehensive documentation (worked example, extension guide, invariants, failure modes). Should be standard before every epic close.

## What This Epic Spawned

- **RAISE-650:** Domain Cartridges — pluggable knowledge + process packs as raise-core foundational infrastructure
- **RAI-48:** E7: Skills Improvements — `/rai-epic-docs` skill for developer documentation
- **Confluence documentation:** 4 pages in RAI space + 2 pages in RaiSE1 space (requirements brief + dev docs)
- **Handoff to Eduardo:** ScaleUp knowledge pipeline ready for rai-agent development

## Unresolved / Parking Lot

- Eduardo curation sessions not yet done (skill exists, waiting for scheduling)
- Adapter synonym/NLP improvement (future: configurable in domain.yaml or LLM-based)
- Multi-domain graph (GTD, life areas as additional cartridges)
- Temporal validity in edges (research recommends, deferred to RAISE-650)
- Company data integration (CRM/ERP connection for personalized advice)
