# RAISE-760: Retrospective

**Epic:** RAISE-760 — RaiSE Project Management Model
**Date:** 2026-03-27
**Duration:** Single session (~7 hours)
**Type:** Design epic (no code changes)

---

## Metrics

| Metric | Value |
|--------|-------|
| Stories planned | 8 |
| Stories delivered | 8 (100%) |
| Research tracks | 4 (85 sources, all High confidence) |
| Design documents | 6 |
| ADRs created | 4 (ADR-034 to ADR-037) |
| Confluence pages | 15 (13 RaiSE1 + 2 Ventas) |
| Jira issues created | 8 (RAISE-819 + 6 implementation epics + VE-87) |
| Gaps identified | 30 (13 P1, 11 P2, 6 P3) |
| Implementation epics | 6 (RAISE-829 to RAISE-834) |
| Strategic recommendations | 10 |
| Open questions | 5 |

## What Went Well

### 1. Parallel research was highly effective

Running R1-R4 as parallel subagents produced 85 sources of evidence in ~20 minutes
wall time. Each track was independent, properly scoped, and produced a
self-contained report. This pattern should be reused for future research epics.

### 2. The "each product does what it was designed for" principle emerged organically

The key insight — Capabilities belong in Compass, not Jira — came from
applying the principle consistently. We didn't start with this conclusion; it
emerged from rigorous mapping of RaiSE concepts to Atlassian products. ADR-037
was the most impactful decision in the epic.

### 3. Design documents produced actionable implementation artifacts

Every design document (S760.2-S760.6) identified specific gaps with IDs, priorities,
and effort estimates. The gap analysis (S760.7) consolidated 30 gaps into 6
implementation epics. Zero knowledge was left as "we'll figure it out later."

### 4. Sales opportunity emerged from technical research

The VE-87 deal (Inter capacity planning) came from applying R4 (Forge Deep-Dive)
knowledge to a real client need during the same session. The research produced
direct business value, not just technical documentation.

### 5. Product vision document bridges technical and business audiences

Writing the vision as a PM communication (not a technical spec) produced a document
that ventas, delivery, developers, and agents can all use. This should become
standard practice for epics with cross-team impact.

## What Could Be Better

### 1. Initial scope confusion (design vs construction)

The first design attempt produced an implementation scope (Forge app stories)
instead of the actual objective (integration model design). This was caught
and corrected, but cost ~30 minutes of rework. The correction itself was
valuable — it clarified that RAISE-760 is a design epic and RAISE-819 is
the construction epic.

**Pattern:** When an epic objective is ambiguous between "design X" and
"build X," clarify before writing the first story.

### 2. Subagent design documents need review pass

S760.4, S760.5, S760.6 were produced by subagents. While comprehensive, they
weren't individually reviewed before consolidation. A quick review pass after
each subagent completes would catch inconsistencies earlier.

### 3. Confluence page formatting is imperfect

Markdown → Confluence conversion loses some formatting (code blocks show as
"Defaultnone", heading anchors add noise). The content is correct but the
presentation could be better. Consider using storage format for critical
pages.

### 4. The 5 open questions remain unresolved

Compass plan availability, Jira Automation tier, and 3 other questions were
identified but not answered in this session. These should be resolved before
starting RAISE-831 (Compass Adapter) and RAISE-829 (Backlog Adapter v2).

## Patterns Captured

### PAT-E-599: Parallel research subagents with shared evidence base

Run independent research tracks as parallel subagents, each producing a
self-contained report. Consolidate findings in a summary document with
cross-references. Each report has its own evidence catalog with confidence
levels. ~85 sources in ~20 minutes.

### PAT-E-600: Product Responsibility Matrix as design anchor

When integrating with a multi-product platform, start by mapping "each concept
belongs to exactly ONE primary product." This prevents the natural tendency
to over-load one product (usually Jira) and produces cleaner architecture.
The matrix then drives all subsequent design decisions.

### PAT-E-601: Gap analysis → implementation epic pipeline

Design documents should identify specific gaps (ID, description, priority,
effort). The gap analysis story consolidates them and groups into implementation
epics. This creates a clean handoff: design epic produces the blueprint,
implementation epics consume it.

### PAT-E-602: Research → Sales pipeline

Technical research (API landscape, platform capabilities) directly informs
sales strategy. When a client need matches research findings, the analysis
time drops from days to minutes. The VE-87 case (transcript → strategy in
~30 minutes) demonstrates this.

## Process Insights

1. **Design epics don't need code tests.** The "tests pass" gate doesn't apply
   to epics that produce only documents. The gate should be "all documents
   published and cross-referenced."

2. **Confluence publishing should happen incrementally.** Publishing each document
   as it's completed (not all at the end) enables review in parallel.

3. **The epic close process should check for downstream artifacts** (implementation
   epics, sales opportunities, vision docs) — not just the planned stories.

4. **Single-session design epics are viable** when the research is parallel and
   the designer has deep domain context. 7 hours for 8 design stories + 4
   research tracks + 4 ADRs + vision document is efficient.

## Next Actions

1. Resolve 5 open questions (Compass plan, Automation tier, etc.)
2. Begin RAISE-819 (Forge MVP) — deadline Apr 16
3. Prioritize RAISE-829 and RAISE-830 (P1 adapter gaps)
4. Present vision document to full team
5. Follow up VE-87 (Inter) — Gerardo to review pricing
