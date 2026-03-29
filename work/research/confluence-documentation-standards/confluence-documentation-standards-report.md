# Research Report: Documentation Information Architecture for Confluence

**Date:** 2026-03-28
**Depth:** Standard (22 sources)
**Decision this informs:** Creation of a "Documentation Guide" for the RaiSE1 Confluence space
**Confidence:** HIGH (strong convergence across standards, vendors, and practitioners)

---

## TL;DR

Documentation information architecture is a solved problem across multiple domains. Four independent traditions — DITA (IBM/OASIS, 20+ years), Diátaxis (modern OSS), NASA/INCOSE (systems engineering, 60+ years), and ISO 15489 (records management, 25+ years) — converge on the same core principles: **type your documents**, **enforce lifecycle**, **assign ownership**, and **use controlled vocabularies**. Confluence-specific guidance from Atlassian and partners adds practical implementation: **Space Gardener role**, **label taxonomies with prefixes**, **keyword-first page titles**, and **template-driven consistency**. For AI agent consumption, the evidence adds: **semantic headings**, **self-contained sections**, **explicit metadata**, and **no visual-only information**.

---

## Research Questions

1. What taxonomies/classification schemes do mature organizations use for technical documentation?
2. What governance processes keep documentation organized over time?
3. What IA principles apply specifically to AI agent consumption?
4. What Confluence-specific patterns have proven effective at scale?

---

## Key Findings

### Finding 1: Document Type Systems — Four Convergent Traditions

Every mature documentation practice classifies documents by **type**, not just topic. Four traditions have independently converged on similar typologies:

| Tradition | Types | Evidence Level |
|-----------|-------|----------------|
| **DITA** (OASIS, 2005) | Concept, Task, Reference | Very High — 20 years production use at IBM, SAP, etc. [S7] |
| **Diátaxis** (Procida, 2017) | Tutorial, How-to, Reference, Explanation | Very High — adopted by Django, Canonical, Cloudflare [S6] |
| **NASA/INCOSE** (1960s–present) | ConOps, Requirements, Architecture, Interface, Verification, Test Report | Very High — 60 years, highest reliability [S8, S9] |
| **ISO 15489** (2001) | Record lifecycle: create, capture, manage, retain/dispose | Very High — 50+ countries, records management foundation [S10] |

**Convergence point:** All four insist that mixing types creates confusion. DITA: "one topic, one type." Diátaxis: "keep the four quadrants separate." NASA: "each artifact has a defined type." The separation is the architecture.

**Mapped to RaiSE context:**

| Diátaxis | DITA | RaiSE Artifact | Example |
|----------|------|----------------|---------|
| Tutorial | Task | Setup Guide, Happy Path | "Dev Environment Setup" |
| How-to | Task | SOP, Runbook | "SOP: SonarQube Analysis" |
| Reference | Reference | ADR, API Ref, CLI Ref | "ADR-033: Release Branch Model" |
| Explanation | Concept | Research Report, Tech Note, Design Doc | "Research: Shared Memory Architecture" |

**Confidence:** HIGH — four independent traditions converging is strong evidence.

**Contrary evidence:** Some practitioners argue that strict type separation increases overhead for small teams (S19 community discussion). However, even critics acknowledge that types improve findability — they disagree on enforcement strictness, not on the principle.

---

### Finding 2: Governance = Ownership + Lifecycle + Review Gates

Every mature standard defines documentation governance as three interacting systems:

#### 2a. Ownership Model

| Standard | Approach | Evidence Level |
|----------|----------|----------------|
| NASA NPR 7123.1C | Technical Authority delegates ownership per artifact type [S8] | Very High |
| ISO 15489 | Assigned responsibilities per record class [S10] | Very High |
| Atlassian | "Space Gardener" role per space [S1, S4] | High |
| Guru/KM | Content owner + SME verifier + knowledge manager [S16] | Medium |

**Convergence:** Every system assigns a named owner. No "everyone owns it" — that means no one does.

#### 2b. Content Lifecycle

All standards define a lifecycle with explicit transitions:

```
CREATE → REVIEW → PUBLISH → MAINTAIN → ARCHIVE → DISPOSE
```

Key lifecycle practices:
- **ISO 15489:** Retention schedules with disposition authority [S10]
- **NASA:** Artifacts tied to lifecycle phases — each phase produces/consumes specific document types [S8]
- **ADR pattern:** Immutable once accepted — supersede, don't edit [S13]
- **K15t:** Archive to `_Archive` parent page, then to archive space [S4]
- **Guru:** Lifecycle alerts when content exceeds staleness threshold [S16]

#### 2c. Review Gates

- **NASA:** Technical review at each lifecycle phase — documentation is a gate criterion [S8]
- **IEEE 26511:** Documentation quality criteria: accuracy, completeness, consistency, usability [S11]
- **ADR:** Status transitions require explicit decision (proposed → accepted) [S13]

**Confidence:** HIGH — universal across all traditions.

---

### Finding 3: Confluence-Specific IA Patterns

#### 3a. Space Structure

Atlassian recommends a **five-level hierarchy**: org > dept > team > project > personal [S1]. For a single-project space like RaiSE1, this flattens to **section-level hierarchy** within one space.

**Best practice pattern (converged from S1, S2, S4, S5, S19, S21):**

```
Space Root
├── [Section pages organized by artifact lifecycle]
├── Labels handle cross-cutting concerns
├── Templates enforce structure per page type
└── Archive section for completed/obsolete content
```

#### 3b. Page Naming Conventions

Converged from K15t [S4], Atlassian community [S19], and Refined [S21]:

| Pattern | When | Example |
|---------|------|---------|
| `{Context} — {Artifact Type}` | Most pages | `E494: ACLI Jira Adapter — Developer Documentation` |
| `{Prefix}: {Title}` | Typed artifacts | `ADR-033: Release Branch Model` |
| `YYMM, {Title}` | Time-bound content | `2603, Release Notes v2.3.0` |
| `{Product} — {Topic}` | Product-scoped | `rai-agent — Product Vision` |

**Rules:**
- Keyword-first: search terms in the first 3-5 words [S4]
- Short titles in deep hierarchies (truncation) [S4]
- No generic titles ("Notes", "Stuff", "Docs") [S4, S14]
- Consistent prefix within a section [S4]

#### 3c. Label Taxonomy

Converged from K15t [S3], Atlassian [S2], and Taxonomies for Confluence [S18]:

| Principle | Detail |
|-----------|--------|
| **Singular form** | `adr` not `adrs` [S3] |
| **Hyphen separators** | `how-to` not `how_to` or `howto` [S3] |
| **Prefixed categories** | `type:adr`, `epic:RAISE-760`, `status:accepted` [S3] |
| **Max 5 per page** | Too many dilutes meaning [S3] |
| **Base type always present** | Every page has at least one type label [S3] |
| **Label Manager role** | Someone monitors compliance [S3] |
| **Audit with macros** | Label List (alphabetical audit), Popular Labels (heatmap) [S3] |

#### 3d. Templates

Every source emphasizes templates as the primary quality control mechanism [S1, S4, S5, S7]:
- One template per document type
- Template defines required sections (contract for `rai docs publish` and Rovo)
- Template includes label suggestions
- New pages should always start from a template

**Confidence:** HIGH — vendor + partner + community consensus.

---

### Finding 4: AI-Agent-Consumable Documentation

A newer body of evidence (2024-2026) addresses how documentation should be structured for AI agent retrieval [S14, S15, S22]:

| Principle | Detail | Source |
|-----------|--------|--------|
| **Semantic headings** | Proper H1 → H6 hierarchy, never skip levels | S14 |
| **Self-contained sections** | Each section actionable in isolation — front-load context | S14 |
| **No visual-only information** | Text descriptions for all diagrams, tables over images | S14 |
| **Consistent terminology** | Same concept = same word everywhere | S14 |
| **Explicit metadata** | Taxonomy tags, content type, version tags, deprecation flags | S15 |
| **Markdown over PDF** | Markdown/HTML chunks better than PDF for retrieval | S14 |
| **Modular chunks** | One topic per page/section for precise retrieval | S15 |
| **Quote exact messages** | Error messages verbatim for direct matching | S14 |
| **llms.txt pattern** | External index file guiding LLMs to important pages | S15 |

**Key insight from S15:** "Rich metadata reduces hallucinations by narrowing the search space." Metadata is not overhead — it's retrieval infrastructure.

**Convergence with DITA:** DITA's "one topic, one type, self-contained" principle (2005) is exactly what AI retrieval needs (2025). The structured authoring community solved this 20 years ago.

**Confidence:** HIGH — convergence between traditional structured authoring and modern AI retrieval.

---

### Finding 5: Content Entropy Prevention

Wiki entropy — the tendency of documentation spaces to degrade into unstructured dumps — is well-documented [S5, S16, S17]:

| Mechanism | How It Prevents Entropy | Source |
|-----------|------------------------|--------|
| **Space Gardener** | Named person audits structure, enforces naming, archives stale pages | S1, S4 |
| **Quarterly review** | Scheduled audit of content freshness, broken links, orphan pages | S5, S16 |
| **Lifecycle alerts** | Automated flags when pages exceed staleness threshold | S16 |
| **Template enforcement** | New pages must use a template — prevents freeform dumps | S1, S5 |
| **Archive-before-delete** | Move to _Archive first, then to archive space after 6 months | S4 |
| **Curation as role** | Distinguish curating (organizing) from synthesizing (creating) [S17] — both needed, different skills |

**Nick Milton's insight [S17]:** "Curation scales better than synthesis, but synthesis captures tacit knowledge." For a documentation guide, define both roles explicitly.

**Confidence:** HIGH — universal agreement that unmanaged wikis degrade.

---

## Triangulation Summary

| Claim | Sources | Confidence |
|-------|---------|------------|
| Documents must be typed (not just topical) | S6, S7, S8, S9, S10 | HIGH |
| Type separation prevents confusion | S6, S7, S14 | HIGH |
| Named ownership prevents entropy | S1, S4, S8, S10, S16 | HIGH |
| Lifecycle with explicit transitions required | S8, S10, S11, S13 | HIGH |
| Labels: singular, prefixed, governed | S2, S3, S18 | HIGH |
| Page titles: keyword-first, short | S4, S14, S19 | HIGH |
| Templates are the primary quality mechanism | S1, S4, S5, S7 | HIGH |
| AI agents need semantic structure + metadata | S14, S15, S22 | HIGH |
| Quarterly review prevents wiki entropy | S4, S5, S16, S17 | HIGH |
| Space Gardener role is effective | S1, S4, S5 | HIGH |

---

## Recommendation

**Create a "Documentation Guide" page at the root of the RaiSE1 space** that codifies:

1. **Document Type System** — Map RaiSE artifact types to Diátaxis quadrants. Every page must declare its type via label. The four types: Tutorial/Guide, How-to/SOP, Reference (ADR, API, CLI), Explanation (Research, Tech Note, Design Doc).

2. **Page Naming Convention** — `{Context} — {Artifact Type}` as default pattern. Keyword-first. No generic titles.

3. **Label Taxonomy** — Codify the prefix system already in confluence-ia-design.md. Add governance: label manager, quarterly audit, Label List macro on guide page.

4. **Content Lifecycle** — Define states: Draft → Published → Under Review → Archived → Deleted. Retention rules per type.

5. **Space Gardener Role** — Assign explicitly. Monthly audit checklist.

6. **Template Library** — One template per document type. Template defines required sections and suggested labels. All new pages start from template.

7. **AI-Readability Rules** — Semantic headings, self-contained sections, no visual-only info, consistent terminology.

8. **Quarterly Health Check** — Scheduled review: orphan pages, stale content, naming violations, label compliance.

**Implementation path:** This guide should be the first page under a "Governance" section, and referenced from the space homepage. It applies to both human authors and the `rai docs publish` skill.

**Trade-offs:**
- (+) Strong evidence from multiple traditions — not inventing anything new
- (+) Builds on existing confluence-ia-design.md — extends, not replaces
- (+) AI-readability rules are free — they also improve human readability
- (-) Requires Space Gardener time commitment (~2h/month)
- (-) Template enforcement adds friction to quick notes (mitigate: allow "scratch" section for unstructured content)

---

## Governance Linkage

- **ADR:** Not needed — this is a process guide, not an architecture decision
- **Backlog:** Create story to write the Documentation Guide page in Confluence
- **Existing artifact:** Extends `work/epics/RAISE-760/confluence-ia-design.md` (S760.4)

---

## References

See [Evidence Catalog](sources/evidence-catalog.md) for full source details.

### Key Sources (by evidence level)

**Very High:**
- [Atlassian — Organizing Confluence IA](https://www.atlassian.com/enterprise/data-center/confluence/organizing-confluence-information-architecture)
- [Diátaxis Framework](https://diataxis.fr/)
- [DITA — OASIS Standard](https://www.oasis-open.org/committees/dita/faq.php)
- [NASA SE Handbook](https://www.nasa.gov/reference/systems-engineering-handbook/)
- [INCOSE SE Handbook v5.0](https://www.incose.org/resources-publications/se-handbook/)
- [ISO 15489:2016 Records Management](https://www.iso.org/standard/62542.html)
- [IEEE 26511:2018 Documentation Management](https://www.iso.org/standard/70879.html)

**High:**
- [K15t — Labels in Confluence](https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/using-labels-in-confluence-order-is-half-the-battle)
- [K15t — Page Naming Conventions](https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/building-confluence-for-scale/page-naming-conventions-for-better-searchability-in-confluence)
- [ADR — adr.github.io](https://adr.github.io/)
- [kapa.ai — Writing Docs for AI](https://docs.kapa.ai/improving/writing-best-practices)
- [Alation — AI-Ready Documentation](https://www.alation.com/blog/how-to-write-ai-ready-documentation/)
- [Nick Milton — Curation vs Synthesis](http://www.nickmilton.com/2016/11/curation-v-synthesis-in-knowledge.html)
