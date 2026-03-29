# Evidence Catalog — Confluence Documentation Standards

**Research:** confluence-documentation-standards
**Date:** 2026-03-28
**Sources collected:** 22

---

## Sources

### S1: Atlassian — Organizing Confluence: Building an Information Architecture
- **Type:** Primary (vendor official)
- **Evidence Level:** Very High
- **URL:** https://www.atlassian.com/enterprise/data-center/confluence/organizing-confluence-information-architecture
- **Key Finding:** Five-level hierarchy model (org > dept > team > project > personal). Recommends "Space Gardener" role, systematic labeling, space templates, and regular auditing. Emphasizes the building-metaphor: analyze → design → execute → migrate → maintain.
- **Relevance:** Direct vendor authority on Confluence IA

### S2: Atlassian — Confluence Best Practices
- **Type:** Primary (vendor official)
- **Evidence Level:** Very High
- **URL:** https://www.atlassian.com/software/confluence/resources/guides/get-started/best-practices
- **Key Finding:** Spaces of the same type should follow similar structure and naming so contributors learn one pattern and apply everywhere. Labels are the cross-cutting discovery mechanism.
- **Relevance:** Official Atlassian guidance

### S3: K15t — Using Labels in Confluence: Order Is Half the Battle
- **Type:** Secondary (Atlassian partner, enterprise focus)
- **Evidence Level:** High
- **URL:** https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/using-labels-in-confluence-order-is-half-the-battle
- **Key Finding:** Singular form only. Use prefixes (kb-, how-to-). Hyphens as separators. Designate a label manager. Use Label List macro for audit, Popular Labels macro for heatmap. Content by Label macro for cross-space discovery.
- **Relevance:** Detailed, actionable label taxonomy guidance

### S4: K15t — Page Naming Conventions for Better Searchability
- **Type:** Secondary (Atlassian partner)
- **Evidence Level:** High
- **URL:** https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/building-confluence-for-scale/page-naming-conventions-for-better-searchability-in-confluence
- **Key Finding:** Keyword-first titles. YYMM prefix for time-bound content. 3-4 letter product codes. Short titles in deep hierarchies. "Space Gardener" role. _Archive parent pages before full archival.
- **Relevance:** Specific naming patterns with examples

### S5: K15t — How to Structure Confluence Content for Long Term Success
- **Type:** Secondary (Atlassian partner)
- **Evidence Level:** High
- **URL:** https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/how-to-structure-confluence-content-for-long-term-success
- **Key Finding:** Governance, page templates, and periodic review cycles as the three pillars of long-term Confluence health. Without them, spaces degrade into "digital landfills."
- **Relevance:** Long-term maintenance strategies

### S6: Diátaxis Framework (Daniele Procida)
- **Type:** Primary (framework creator)
- **Evidence Level:** Very High
- **URL:** https://diataxis.fr/
- **Key Finding:** Four documentation types on a 2×2 matrix: Tutorials (learning, doing), How-to Guides (goals, doing), Reference (information, cognition), Explanation (understanding, cognition). Must be kept separate — mixing types creates confusion. Adopted by Canonical, Django, Cloudflare, many OSS projects.
- **Relevance:** The dominant modern framework for documentation classification

### S7: DITA (Darwin Information Typing Architecture) — OASIS Standard
- **Type:** Primary (international standard)
- **Evidence Level:** Very High
- **URL:** https://www.oasis-open.org/committees/dita/faq.php
- **Key Finding:** Three core topic types: Concept, Task, Reference. Self-contained topics. Subject schemes for controlled taxonomies. Separation of content from presentation. Reuse via conref/keyref. CCMS for governance. 20+ years of production use at IBM, SAP, etc.
- **Relevance:** The most battle-tested documentation architecture standard (since 2005)

### S8: NASA Systems Engineering Handbook (SP-2016-6105 Rev 2)
- **Type:** Primary (government standard)
- **Evidence Level:** Very High
- **URL:** https://www.nasa.gov/reference/systems-engineering-handbook/
- **Key Finding:** Technical documentation organized by lifecycle phase. Every artifact has a defined type, owner, review gate, and retention policy. NPR 7123.1C defines 17 SE processes, each producing specific artifact types. Technical Authority governance model ensures documentation quality.
- **Relevance:** 60+ years of documentation governance at the highest reliability level

### S9: INCOSE Systems Engineering Handbook v5.0 (2023)
- **Type:** Primary (professional body standard)
- **Evidence Level:** Very High
- **URL:** https://www.incose.org/resources-publications/se-handbook/
- **Key Finding:** Artifact taxonomy aligned to ISO/IEC/IEEE 15288:2023. Documentation types: ConOps, Requirements Spec, Architecture Description, Interface Control Doc, Verification Plan, Test Report, etc. Each tied to a lifecycle process.
- **Relevance:** The SE community's canonical artifact taxonomy

### S10: ISO 15489:2016 — Records Management
- **Type:** Primary (international standard)
- **Evidence Level:** Very High
- **URL:** https://www.iso.org/standard/62542.html
- **Key Finding:** Four characteristics of reliable records: authenticity, reliability, usability, integrity. Lifecycle: create → capture → manage → retain/dispose. Requires assigned responsibilities, metadata schema, retention schedules, and disposition authority.
- **Relevance:** The foundational standard for document lifecycle management

### S11: IEEE/ISO/IEC 26511:2018 — Management of User Documentation
- **Type:** Primary (international standard)
- **Evidence Level:** Very High
- **URL:** https://www.iso.org/standard/70879.html
- **Key Finding:** Defines documentation management processes: planning, production, review, maintenance, retirement. Emphasizes documentation as a managed deliverable with quality criteria, not an afterthought.
- **Relevance:** Standard for documentation lifecycle management

### S12: IEEE/ISO/IEC 26512 — Acquirer/Supplier Documentation
- **Type:** Primary (international standard)
- **Evidence Level:** Very High
- **URL:** https://standards.ieee.org/ieee/26512/5160/
- **Key Finding:** Documentation as contractual deliverable with specification, acceptance criteria, and quality gates.
- **Relevance:** Documentation governance as formal process

### S13: ADR (Architecture Decision Records) — adr.github.io
- **Type:** Secondary (community standard, Martin Fowler endorsed)
- **Evidence Level:** High
- **URL:** https://adr.github.io/
- **Key Finding:** Lightweight records with status lifecycle (proposed → accepted → superseded). Store close to code (docs/adr/). Immutable once accepted — supersede, don't edit. Widely adopted (Google, AWS, Microsoft, GDS UK).
- **Relevance:** ADR lifecycle model applicable to all governance documents

### S14: kapa.ai — Writing Documentation for AI Best Practices
- **Type:** Secondary (AI documentation platform)
- **Evidence Level:** High
- **URL:** https://docs.kapa.ai/improving/writing-best-practices
- **Key Finding:** Semantic headings (proper H1-H6 hierarchy). No PDFs — Markdown/HTML only. Keep related info together (chunking-aware). State prerequisites explicitly. Text descriptions for all visuals. Self-contained sections. Quote exact error messages.
- **Relevance:** Direct evidence for AI-agent-consumable documentation

### S15: Alation — How to Write AI-Ready Documentation
- **Type:** Secondary (data governance platform)
- **Evidence Level:** High
- **URL:** https://www.alation.com/blog/how-to-write-ai-ready-documentation/
- **Key Finding:** Metadata as infrastructure: taxonomy tags, content type declarations, version tags, external metadata indices (llms.txt). Modular "chunkable" content. Rich metadata reduces hallucinations by narrowing search space.
- **Relevance:** Metadata-first approach to AI readability

### S16: Guru — Knowledge Management Governance
- **Type:** Secondary (KM platform vendor)
- **Evidence Level:** Medium
- **URL:** https://www.getguru.com/reference/knowledge-management-governance
- **Key Finding:** Governance framework with roles: content owners, SME verifiers, knowledge managers. Knowledge governance matrix maps who creates, reviews, approves. Lifecycle alerts for stale content.
- **Relevance:** Practical governance role definitions

### S17: Nick Milton (Knoco) — Curation vs Synthesis in KM
- **Type:** Secondary (KM practitioner, 30+ years)
- **Evidence Level:** High
- **URL:** http://www.nickmilton.com/2016/11/curation-v-synthesis-in-knowledge.html
- **Key Finding:** Curation (organizing existing artifacts for users) vs Synthesis (creating new content by combining/summarizing). Both needed. Curation scales better but synthesis captures tacit knowledge. Community-driven curation prevents single-point-of-failure.
- **Relevance:** Key distinction for documentation maintenance strategy

### S18: Taxonomies for Confluence (GitHub — cadmiumkitty)
- **Type:** Secondary (open source tool)
- **Evidence Level:** Medium
- **URL:** https://github.com/cadmiumkitty/taxonomies-for-confluence
- **Key Finding:** SKOS and RDFS controlled vocabularies can be applied to Confluence pages. Enables SPARQL queries, knowledge graph integration, and structured data capture alongside wiki content.
- **Relevance:** Technical evidence that formal taxonomies can be applied to Confluence

### S19: Atlassian Community — Confluence Page Tree for Software Teams
- **Type:** Tertiary (community discussion)
- **Evidence Level:** Medium
- **URL:** https://community.atlassian.com/forums/Confluence-questions/Confluence-Page-Tree-Structure-for-a-Software-Team-and-Jira/qaq-p/2992551
- **Key Finding:** Software teams commonly use: Architecture (ADRs, design docs), Engineering (runbooks, SOPs), Product (PRDs, roadmaps), Release Notes. Most successful teams mirror their work lifecycle in the page tree.
- **Relevance:** Real-world practitioner validation

### S20: arc42 — Architecture Decisions (Section 9)
- **Type:** Secondary (architecture documentation framework)
- **Evidence Level:** High
- **URL:** https://docs.arc42.org/section-9/
- **Key Finding:** Architecture documentation template with 12 standardized sections. Section 9 specifically for Architecture Decisions. Widely used in European enterprise (SAP, Deutsche Bank, etc.).
- **Relevance:** Complementary architecture documentation framework

### S21: Refined.com — Ultimate Guide to Confluence Wiki
- **Type:** Secondary (Confluence marketplace vendor)
- **Evidence Level:** Medium
- **URL:** https://www.refined.com/blog/ultimate-guide-creating-confluence-wiki
- **Key Finding:** Organize by function, not by team. Use templates for every repeating page type. Archive quarterly. Homepage as dashboard with macros.
- **Relevance:** Practical Confluence organization guidance

### S22: Document360 — Documentation for Humans and AI Agents
- **Type:** Secondary (documentation platform)
- **Evidence Level:** Medium
- **URL:** https://document360.com/blog/documentation-for-humans-and-ai-agents/
- **Key Finding:** Dual-audience documentation: structure for machines, write for humans. Consistent terminology. Semantic markup. Self-contained sections. (Page was blocked by JS, summary from search results.)
- **Relevance:** Dual-audience documentation design
