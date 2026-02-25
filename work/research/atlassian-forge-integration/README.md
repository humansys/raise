# Research: Atlassian Forge Integration for Governance Copilot

**RAISE-273** | 2026-02-24

## Question
Can we build a governance copilot on Atlassian Forge that uses RaiSE's
neuro-symbolic knowledge graph for deterministic governance, with Confluence
as content store and Jira as process orchestrator?

## TL;DR
**YES.** Three-layer architecture:

1. **Confluence** = Content Store (documents, skills-as-pages, standards)
2. **RaiSE Backend** = Knowledge Layer (neuro-symbolic graph, deterministic)
3. **Forge App** = UI Layer (Rovo Agents — Rai Governance + Rai Dev)

Skills are Confluence pages — adding a governance process = creating a page.
No code, no deploy. The knowledge graph closes the governance → dev loop
deterministically. Teamwork Graph can't do this.

## Architecture

```
Confluence (content) → RaiSE Backend (knowledge, deterministic)
                              ↕
                    Rai Governance + Rai Dev (Rovo Agents)
```

## Key Decisions
1. Three layers, three responsibilities (UI / Content / Knowledge)
2. One contextual agent that executes skills from Confluence pages
3. Skills as Confluence pages (governance team edits, zero code)
4. Document state in Confluence (version history, properties, comments)
5. Knowledge state in RaiSE graph (relations, traceability, validation)
6. Deterministic validation via graph (not RAG, not probabilistic)
7. Two agents: Rai Governance + Rai Dev (shared actions)
8. Jira as orchestrator (Automation creates structure, Rai operates within)
9. Backend is the core differentiator (not an add-on)

## Files
- [Walking Skeleton Design](walking-skeleton-design.md) — full architecture, manifest, code, prompts, implementation plan
- [Viability Report](atlassian-forge-integration-report.md) — initial research, Forge capabilities
- [Evidence Catalog](sources/evidence-catalog.md) — 24 sources, triangulated claims

## FREE vs PRO
- **FREE:** local graph, local skills, one dev, one repo
- **PRO:** centralized graph, Confluence skills, governance→dev loop, deterministic, multi-team
