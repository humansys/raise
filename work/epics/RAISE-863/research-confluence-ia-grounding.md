# S863.0: Confluence IA Grounding Research

**Epic:** RAISE-863
**Story:** RAISE-865 (Spike)
**Date:** 2026-03-27
**Status:** Complete
**Duration:** ~25 min
**Sources:** 12 (8 primary, 4 secondary)

---

## Research Questions

1. How should software development teams structure their Confluence page tree?
2. When should we use Confluence folders vs parent pages?
3. How does Rovo consume Confluence content — does structure matter?

---

## Q1: Confluence Page Tree Best Practices for Dev Teams

### Evidence

| # | Source | Type | Key Claim |
|---|--------|------|-----------|
| E1 | [Atlassian Community: Page Tree Structure for Software Team](https://community.atlassian.com/forums/Confluence-questions/Confluence-Page-Tree-Structure-for-a-Software-Team-and-Jira/qaq-p/2992551) | Community (primary) | 6-8 top-level pages optimal for scalability |
| E2 | [Atlassian Blog: IA Strategy for Confluence](https://www.atlassian.com/blog/confluence/how-to-build-an-information-architecture-strategy-for-confluence) | Vendor (primary) | Five-level content framework: org → dept → team → project → personal |
| E3 | [Vectors: 10 Tips for Page Tree](https://covectors.io/blog/10-tips-to-better-structure-your-confluence-page-tree/) | Practitioner (primary) | Max 3-4 levels depth; beyond that, use separate spaces |
| E4 | [Atlassian: Organizing Confluence IA](https://www.atlassian.com/enterprise/data-center/confluence/organizing-confluence-information-architecture) | Vendor (primary) | Page tree within space to organize; labels for cross-cutting |
| E5 | [Refined: Confluence Documentation Best Practices](https://www.refined.com/blog/confluence-documentation-best-practices) | Practitioner (secondary) | Consistent naming, labels, landing pages per section |

### Findings

**Convergent advice across sources:**

1. **6-8 top-level sections** is the sweet spot (E1, E3). More than 10 becomes noisy.
2. **Max 3-4 levels of nesting** (E3, explicit). Beyond that, navigation becomes
   frustrating. If you need more depth, consider separate spaces.
3. **Labels for cross-cutting concerns, tree for hierarchy** (E4, E5). This is
   exactly what S760.4 already proposes.
4. **Consistent naming conventions** are universally recommended (E1, E3, E5).
   Include team/project prefix, dates where applicable.
5. **Landing pages per section** with links to key areas (E1, E5). Not blank
   parent pages — pages with actual orientation content.
6. **Assign page tree managers** to maintain structure (E3). Without ownership,
   structure decays.

### Impact on S760.4

S760.4 proposes **12 top-level sections**. Community consensus is 6-8. Several of
S760.4's sections are aspirational (Skills, Patterns, Glossary, Sessions,
Templates) with no current content. **Recommendation: reduce to 7-9 sections for
content that exists today. Create aspirational sections only when first content
arrives.**

S760.4's epic subtree design (Epic > Scope/Design/Plan/Retro/Research/Stories)
could reach 4 levels. This is at the recommended maximum. **Recommendation: keep
epic subtrees shallow — epic page with children, not grandchildren. Research and
stories are direct children of the epic, not nested under sub-sections.**

---

## Q2: Confluence Folders vs Parent Pages

### Evidence

| # | Source | Type | Key Claim |
|---|--------|------|-----------|
| E6 | [Atlassian Support: Use Folders](https://support.atlassian.com/confluence-cloud/docs/use-folders-to-organize-your-work/) | Vendor (primary) | Folders are simple containers; parent pages are containers with context |
| E7 | [K15t: Why Folders Are a Big Deal](https://www.k15t.com/rock-the-docs/news/2024/11/48-why-folders-in-confluence-are-a-big-deal) | Practitioner (primary) | Folders stand out visually; don't appear in search results |
| E8 | [Atlassian CQL Docs](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/) | Vendor (primary) | CQL supports `type=folder` and `ancestor` queries on folders |

### Findings

**Folders:**
- Simple containers with no content of their own
- Do NOT appear in search results (E7) — invisible to text search
- DO support CQL queries: `type=folder`, `ancestor={folder_id}` (E8)
- No version history (E6)
- Stand out visually in the page tree (E7)
- Deleting a folder moves children up a level (E6)
- Can only be created from the content tree sidebar, not global create (E6)
- Space-level feature toggle (E6)

**Parent pages:**
- Have their own content — can serve as landing/index pages
- Appear in search results
- Have version history
- Familiar to all users

**Decision matrix:**

| Use case | Folder | Parent Page |
|----------|--------|-------------|
| Section needs an index/overview | | **Yes** |
| Pure grouping, no context needed | **Yes** | |
| Content must be searchable | | **Yes** |
| CQL `ancestor` queries needed | Both work | Both work |
| Rovo needs to find the section | | **Yes** (folders invisible to search) |

### Impact on S760.4

S760.4 assumes all sections are parent pages. Given our needs (index pages per
section, Rovo discoverability, CQL queries), **parent pages are the right choice
for top-level sections**. Folders would make sections invisible to search and
Rovo.

**Recommendation: use parent pages for all sections. Do NOT use folders.**
Folders are useful for ad-hoc personal organization, not for an IA that needs
to be discoverable by agents and CQL.

---

## Q3: Rovo Indexing & Content Structure

### Evidence

| # | Source | Type | Key Claim |
|---|--------|------|-----------|
| E9 | [Atlassian: Rovo Knowledge Sources](https://support.atlassian.com/rovo/docs/knowledge-sources-for-agents/) | Vendor (primary) | Knowledge scoped by space, parent+children, or individual pages |
| E10 | [K15t: Getting Most Out of Rovo](https://www.k15t.com/rock-the-docs/confluence-cloud-best-practices/getting-the-most-out-of-atlassian-rovo) | Practitioner (primary) | "Rovo agents are only as good as the information you provide them" |
| E11 | [Atlassian: Rovo Agents](https://support.atlassian.com/rovo/docs/agents/) | Vendor (primary) | Agents use CQL (`searchConfluenceUsingCql`) to retrieve content |
| E12 | [Atlassian: Rovo Features](https://www.atlassian.com/software/rovo/features) | Vendor (secondary) | Rovo indexes Confluence, Jira, and third-party sources |

### Findings

**How Rovo consumes Confluence:**

1. **Scoping by parent + children** is supported (E9). You can point a Rovo agent
   at a parent page and it includes all descendants. This means our page tree
   structure directly enables Rovo scoping.

2. **Agents use CQL** for retrieval (E11). This means labels and page tree
   structure both matter — CQL can query by `ancestor`, `label`, `space`, and
   `text`.

3. **Content quality > structure** (E10). Rovo produces poor answers from poorly
   written or contradictory content. Structure helps discoverability, but content
   quality is the primary factor.

4. **No evidence that labels are used for Rovo scoping** at agent configuration
   level. Rovo scopes by space or by parent+children, not by label. However,
   Rovo agents using CQL actions CAN query by label at retrieval time.

5. **Folders are invisible to search** (E7), which likely means Rovo search
   doesn't surface them. Content INSIDE folders is still searchable, but the
   folder itself provides no signal.

### Impact on S760.4

S760.4's design is well-aligned with Rovo:
- Parent pages as sections → enables "parent + children" scoping
- Labels → enables CQL-based retrieval at agent query time
- Clean content → more important than perfect structure

**Recommendation: no changes needed for Rovo. The parent-page-per-section model
is the right approach. Invest in content quality (clear titles, structured
headings, no contradictions) over structural perfection.**

---

## Consolidated Recommendations for RAISE-863

### Validate (S760.4 is correct)

1. **Labels for cross-cutting, tree for hierarchy** — universally recommended
2. **One space per project** — aligned with Atlassian guidance
3. **Consistent naming conventions** — universally recommended
4. **Parent pages as sections** (not folders) — essential for search + Rovo

### Adjust (S760.4 needs modification)

1. **Reduce from 12 to 7-9 top-level sections** — only create sections with
   existing content. Community consensus is 6-8 max.
   - **Keep:** Epics, Architecture, Product, Developer Docs, Operations, Releases
   - **Keep (with content):** Sales & Delivery (Inter report exists)
   - **Defer:** Skills, Patterns, Glossary, Sessions, Templates (no content yet)
   - Governance: evaluate — do we have governance docs in Confluence? If not, defer.

2. **Limit depth to 3 levels max** — Epic > child pages (flat). Do NOT create
   Research/ and Stories/ sub-sections under each epic. Research pages and story
   pages are direct children of the epic page.

3. **Section pages must have content** — not blank parent pages. Each section
   page gets an index table + brief description. This makes sections useful as
   landing pages and improves Rovo indexing.

### Reject (S760.4 proposed, evidence contradicts)

1. **Deep epic subtrees** (Epic > Research > R1, R2...) — too many levels. Flatten.

---

## Confidence Assessment

| Question | Confidence | Basis |
|----------|-----------|-------|
| Page tree depth (max 3-4) | **High** | 3 independent sources converge |
| 6-8 top-level sections | **High** | Community consensus + Atlassian guidance |
| Parent pages over folders | **High** | Technical evidence (search, CQL, Rovo) |
| Rovo prefers parent+children scoping | **Medium** | Official docs confirm, but limited detail |
| Labels don't affect Rovo scoping | **Medium** | Absence of evidence, not evidence of absence |
| Content quality > structure for Rovo | **Medium** | Practitioner source, reasonable claim |
