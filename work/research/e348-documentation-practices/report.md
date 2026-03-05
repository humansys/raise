# Research Report: Documentation Practices for RaiSE v2.2

**Date:** 2026-03-05
**Depth:** Standard (18 sources)
**Decision:** E348 epic design — documentation architecture and story breakdown
**Researcher:** Rai + Emilio

---

## 1. Primary Question

What are the SOTA documentation practices for a Python CLI framework with plugin architecture, serving three audiences: **users**, **human developers/extensors**, and **AI agents**?

---

## 2. Key Findings

### 2.1 The Diataxis Framework is the Consensus Standard

**Confidence: HIGH** (Sources: 1, 4, 5, 13, 18 — 5 independent confirmations)

The industry has converged on the [Diataxis](https://diataxis.fr/) 4-type taxonomy:

| Type | Orientation | User Need | RaiSE Example |
|------|-------------|-----------|---------------|
| **Tutorial** | Learning + Action | "Show me how to get started" | First project setup with `rai init` |
| **How-to Guide** | Work + Action | "Help me solve this problem" | "How to create a custom adapter" |
| **Reference** | Work + Cognition | "Give me the facts" | CLI command reference, config schema |
| **Explanation** | Learning + Cognition | "Help me understand" | Architecture overview, design decisions |

**Exemplar:** uv (Astral) uses exactly this: Getting Started > Guides > Concepts > Reference. 50k+ stars, Python CLI, plugin-like architecture. This is our closest comparable.

**Contrary evidence:** Some practitioners (Source 3) note Diataxis can feel rigid for small projects. For pre-release, a pragmatic subset may suffice.

### 2.2 AI-Agent-Readable Documentation is an Emerging Must-Have

**Confidence: HIGH** (Sources: 2, 3, 5, 7, 10, 11, 13 — 7 confirmations)

Three layers of agent-readability have emerged:

#### Layer 1: llms.txt (table stakes)
- Markdown file at repo root with project overview + curated links
- 844k+ sites adopted. Anthropic, Stripe, Cloudflare use it
- Format: H1 title > blockquote summary > H2 sections with `[name](url): description` links
- Optional `llms-full.txt` for expanded content without URLs

#### Layer 2: Markdown-servable docs
- Every doc page should be readable as clean markdown (no JS rendering required)
- Agent tools truncate at ~5000 chars — pages must be focused and self-contained
- Heading hierarchies enable section-level retrieval

#### Layer 3: Agent context files
- `CLAUDE.md` — already exists in RaiSE (our own innovation)
- `AGENTS.md` — emerging cross-agent standard
- Skills folders (SKILL.md) — RaiSE already does this
- MCP docs server — GitBook, Mastra pattern for structured retrieval

**RaiSE advantage:** We already have CLAUDE.md and SKILL.md patterns. We're ahead of most projects on Layer 3. We need Layers 1 and 2.

### 2.3 Minimum Viable Documentation for Open Source Pre-Release

**Confidence: HIGH** (Sources: 6, 14, 15 — 3 confirmations)

The pyOpenSci community standard defines the minimum:

**Required files:**
- `README.md` — name, badges, description, quick-start, doc links
- `CONTRIBUTING.md` — how to contribute (code, docs, issues)
- `CODE_OF_CONDUCT.md` — community standards
- `LICENSE` — legal terms
- `CHANGELOG.md` — per-version changes

**Required user docs:**
- Installation guide
- Getting started / quickstart
- CLI command reference
- Configuration reference

**Nice to have for v1:**
- Tutorials (can come post-launch)
- Architecture explanation (aids contributors)
- Migration guide (if upgrading from prior version)

### 2.4 MkDocs + Material is the Toolchain Standard

**Confidence: HIGH** (Sources: 8, 9, 12 — 3 confirmations)

- Material for MkDocs is the de facto standard for Python project doc sites
- Used by Typer, FastAPI, Pydantic — our direct ecosystem peers
- `mkdocstrings` auto-generates API reference from docstrings
- Deploys to GitHub Pages with `mkdocs gh-deploy`
- Markdown source in `docs/` — docs-as-code, version controlled

**Trade-off:** Adding MkDocs is infrastructure work. For pre-release alpha, markdown docs in the repo may suffice. MkDocs can come as a follow-up story.

### 2.5 Plugin/Extension Documentation Patterns

**Confidence: MEDIUM** (Sources: 4, 5, 16 — 3 confirmations, but fewer direct comparables)

Successful plugin architectures document extension points with:
- **Protocol/interface reference** — what to implement
- **Step-by-step how-to** — "How to create a custom X"
- **Working example** — minimal but complete
- **Registration mechanism** — how the system discovers plugins

For RaiSE, this means documenting:
- Adapter protocol + how to create one
- MCP server registration + how to add one
- Skill creation + SKILL.md spec
- Hook protocol + how to wire one

---

## 3. Synthesis: Three-Audience Documentation Architecture

```
                    ┌─────────────────────────────┐
                    │        llms.txt              │  ← AI entry point
                    │   (index + summaries)        │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼───────────────────┐
          │                    │                    │
    ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼──────┐
    │   USER     │       │ DEVELOPER  │       │   AGENT    │
    │   DOCS     │       │   DOCS     │       │   DOCS     │
    ├────────────┤       ├────────────┤       ├────────────┤
    │ README     │       │ CONTRIB    │       │ CLAUDE.md  │
    │ Install    │       │ Arch Docs  │       │ AGENTS.md  │
    │ Quickstart │       │ Adapter    │       │ llms.txt   │
    │ CLI Ref    │       │ MCP Guide  │       │ SKILL.md   │
    │ Config Ref │       │ Skill Spec │       │ (per skill)│
    │ How-to     │       │ Hook Guide │       │            │
    │ Guides     │       │ API Ref    │       │            │
    └────────────┘       └────────────┘       └────────────┘
         │                     │                     │
         └─────────────────────┴─────────────────────┘
                          │
                   ┌──────▼──────┐
                   │  docs/      │  ← Markdown source
                   │  (Diataxis) │     MkDocs-ready
                   └─────────────┘
```

---

## 4. Recommendations

### R1: Adopt Diataxis as organizing framework
**Confidence: HIGH.** Structure docs/ as: tutorials/, guides/, reference/, explanation/. Even if we start with just reference + guides, the taxonomy prevents mixing content types.

### R2: Create llms.txt and AGENTS.md immediately
**Confidence: HIGH.** Low effort, high impact. llms.txt indexes our docs for AI consumption. AGENTS.md provides cross-agent context (CLAUDE.md is Claude-specific).

### R3: Start with markdown in docs/, defer MkDocs site
**Confidence: MEDIUM.** For alpha, in-repo markdown is sufficient. MkDocs + Material can be a follow-up story post-release. This avoids infrastructure scope creep.

### R4: Prioritize reference docs over tutorials
**Confidence: HIGH.** CLI reference and config reference serve all three audiences. Tutorials can follow — reference is the foundation.

### R5: Document extension points with protocol + how-to + example pattern
**Confidence: MEDIUM.** Each extension point (adapter, MCP, skill, hook) gets: protocol spec, step-by-step guide, working example.

### R6: Keep pages <5000 chars where possible
**Confidence: HIGH.** Agent tools truncate at varying thresholds. Self-contained, focused pages serve both humans and agents.

---

## 5. Proposed Story Mapping (for E348 design)

| # | Story | Diataxis Type | Audience | Priority |
|---|-------|---------------|----------|----------|
| 1 | Documentation audit + gap analysis | Meta | All | P0 |
| 2 | README refresh | — | All | P0 |
| 3 | llms.txt + AGENTS.md | — | Agent | P0 |
| 4 | CLI command reference | Reference | All | P0 |
| 5 | Configuration reference (.raise/, manifest) | Reference | All | P1 |
| 6 | Installation + quickstart guide | Tutorial | User | P0 |
| 7 | Extension guides (adapter, MCP, skill, hook) | How-to | Developer | P1 |
| 8 | Architecture overview | Explanation | Developer/Agent | P2 |
| 9 | MkDocs site setup | Infrastructure | All | P2 (post-release) |

---

## 6. Contrary Evidence & Risks

| Concern | Source | Mitigation |
|---------|--------|------------|
| Diataxis feels rigid for small projects | Carey (3) | Start with 2 types (reference + guides), expand later |
| llms.txt is "uncertain in execution" | Bluehost guide | Low cost to implement regardless of standard's future |
| MkDocs adds maintenance burden | — | Defer to post-release; markdown in repo is enough for alpha |
| Agent doc consumption is immature | Carey (3) | Focus on fundamentals (clean markdown) that work regardless |
| Extension docs require stable APIs | — | Document current protocols with "alpha — may change" notice |

---

## 7. References

- Evidence catalog: `work/research/e348-documentation-practices/sources/evidence-catalog.md`
- Diataxis framework: https://diataxis.fr/
- llms.txt spec: https://llmstxt.org/
- uv docs (exemplar): https://docs.astral.sh/uv/
- pyOpenSci guide: https://www.pyopensci.org/python-package-guide/documentation/index.html
