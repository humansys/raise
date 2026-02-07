# Evidence Catalog: Architecture Knowledge Layer

> RES-ARCH-KNOWLEDGE-001 | 2026-02-07

---

## Prior Art (19 entries)

### AI-Aware Code Documentation Tools

**Source**: [Aider Repository Map](https://aider.chat/docs/repomap.html) + [Tree-sitter implementation](https://aider.chat/2023/10/22/repomap.html)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: Graph-ranked, token-budgeted code map using tree-sitter AST parsing and PageRank. Default 1K token budget. Signatures only, not full code.
- **Format**: Plain text (file → symbol signatures with `⋮...` ellipsis)
- **Dual-purpose?**: AI-primary. Human-readable as side effect.
- **Sync**: Regenerated on every chat interaction.

**Source**: [Cursor Codebase Indexing](https://docs.cursor.com/context/codebase-indexing) + [How Cursor Indexes](https://towardsdatascience.com/how-cursor-actually-indexes-your-codebase/)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: Semantic chunking + vector embeddings. No human-readable artifact produced.
- **Format**: Internal vector database (Turbopuffer). Tree-sitter for chunk boundaries.
- **Dual-purpose?**: No. Purely machine-consumed.
- **Sync**: Merkle tree change detection. Incremental re-indexing.

**Source**: [Cursor Project Rules](https://cursor.com/docs/context/rules)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: `.cursor/rules/*.mdc` — MDC format with metadata + markdown. Scoped by path, `alwaysApply`, or relevance.
- **Dual-purpose?**: Yes. Human-authored markdown, machine-consumed contextually.

**Source**: [Claude Code CLAUDE.md](https://www.builder.io/blog/claude-md-guide)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: Freeform markdown, loaded into system prompt. Hierarchical: global → project → subdirectory. No schema, no frontmatter.
- **Dual-purpose?**: Yes, by design. "Keep it concise and human-readable."

**Source**: [Continue.dev Rules](https://docs.continue.dev/guides/codebase-documentation-awareness)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: `.continue/rules/*.md` + embeddings-based retrieval. `@tree` context for directory structure.
- **Dual-purpose?**: Rules = yes. Embeddings = machine-only.

**Source**: [GitHub Copilot Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: `.github/copilot-instructions.md` + `applyTo` frontmatter for file-type scoping.
- **Dual-purpose?**: Yes. Markdown + optional YAML frontmatter.

### Established Architecture Documentation Methods

**Source**: [C4 Model](https://c4model.com/) + [Structurizr DSL](https://docs.structurizr.com/dsl)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: Four hierarchical levels (Context > Container > Component > Code). Structurizr DSL is machine-parseable AND human-readable. Diagrams generated from model.
- **Dual-purpose?**: Yes, when using Structurizr DSL. Single source of truth.

**Source**: [arc42 Template](https://arc42.org/overview)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: 12 standardized sections. All optional. Building Block View (§5) closest to what AI needs.
- **Dual-purpose?**: Human-primary. Machine-parseable only if strict heading structure maintained.

**Source**: [ADRs - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: 4 fields: Title, Context, Decision, Consequences. Immutable. Most machine-friendly traditional architecture document.
- **Dual-purpose?**: Yes, inherently — fixed structure enables reliable parsing.

**Source**: [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: Goals/Non-goals pattern is powerful for AI — explicitly bounds scope. Alternatives Considered provides rationale code can't express.

**Source**: [Rust RFC Template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: Guide-Level Explanation (teach it) vs Reference-Level Explanation (implement it). Dual-tier maps to human vs AI consumption.

### Structured Documentation Formats

**Source**: [YAML Frontmatter (Hugo)](https://gohugo.io/content-management/front-matter/)
- **Type**: Primary | **Evidence Level**: Very High
- **Key Finding**: Universal dual-purpose pattern. YAML header = machine-parseable. Markdown body = human-readable. Every AI tool understands this.

**Source**: [DITA Standard](https://dita-lang.org/)
- **Type**: Secondary | **Evidence Level**: Medium
- **Key Finding**: Topic typing (Concept, Task, Reference) is valuable but XML format is too heavy. Typing achievable via YAML frontmatter `type:` field.

**Source**: [llms.txt Standard](https://gitbook.com/docs/publishing-documentation/llm-ready-docs)
- **Type**: Primary | **Evidence Level**: High
- **Key Finding**: Emerging standard. `llms.txt` = index. `llms-full.txt` = full content. 844K+ websites adopted. Auto-generated from docs.

**Source**: [Dual-Channel Documentation (InfoQ 2025)](https://www.infoq.com/articles/architects-ai-era/)
- **Type**: Secondary | **Evidence Level**: High
- **Key Finding**: "Models infer structure, not intent." Auto-generated structural layer + human-authored rationale layer.

---

## Developer Needs (17 entries)

**Source**: [From Expert to Novice (arXiv 2025)](https://arxiv.org/html/2503.08628v1)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: Existing docs fall short due to incompleteness, ambiguity, obsolescence. Developers rely on oral explanations.

**Source**: [DORA 2024 State of DevOps](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report)
- **Type**: Primary | **Evidence Level**: Very High
- **Finding**: Teams with high-quality docs are 2x+ likely to meet reliability targets. 25% AI adoption increase → 7.5% doc quality improvement.

**Source**: [vFunction 2025 Architecture Report](https://vfunction.com/resources/report-2025-architecture-in-software-development/)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: 93% report negative outcomes from architecture-documentation misalignment. 56% acknowledge docs don't reflect production.

**Source**: [Documentation Decay (Episteca)](https://episteca.ai/blog/documentation-decay/)
- **Type**: Secondary | **Evidence Level**: High
- **Finding**: 30-90 day half-life. 68% of enterprise content not updated in 6+ months.

**Source**: [DevEx: What Drives Productivity (ACM Queue)](https://queue.acm.org/detail.cfm?id=3595878)
- **Type**: Primary | **Evidence Level**: Very High
- **Finding**: Three DX dimensions: cognitive load, feedback loops, flow state. Docs must reduce cognitive load, not add to it.

**Source**: [CodeScene Code Health](https://codescene.com/product/code-health)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: Newcomers need 45-93% more time in low-quality code. Architecture docs should highlight hotspots and complexity zones.

**Source**: [Cortex 2024 Developer Productivity](https://www.cortex.io/report/the-2024-state-of-developer-productivity)
- **Type**: Primary | **Evidence Level**: Medium
- **Finding**: 1-3 months for first meaningful PRs. "Time to find project context" is top impediment.

**Source**: [Stack Overflow Blog: Documentation as Toil (Dec 2024)](https://stackoverflow.blog/2024/12/19/developers-hate-documentation-ai-generated-toil-work/)
- **Type**: Secondary | **Evidence Level**: High
- **Finding**: Meta-study (60+ papers): documentation shortens task duration, improves quality. AI-generated docs most valuable when eliminating toil.

**Source**: [Aider Repository Map](https://aider.chat/docs/repomap.html)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: Symbol-level map + dependency edges + graph ranking within token budget = state of the art for AI codebase awareness.

**Source**: [Effective Context Engineering (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: "Informative yet tight." Context rot — increasing window size doesn't help with irrelevant context.

**Source**: [Microsoft Onboarding Research](https://arxiv.org/pdf/2103.05055)
- **Type**: Primary | **Evidence Level**: High
- **Finding**: "Simple-Complex" strategy — progressive disclosure. Structured onboarding → 62% faster time-to-productivity.

**Source**: [GitHub Engineers: Learning New Codebases](https://github.blog/developer-skills/application-development/how-github-engineers-learn-new-codebases/)
- **Type**: Primary | **Evidence Level**: Medium
- **Finding**: Start with entry points, follow data flow, understand test structure, ask targeted questions.

**Source**: [Human-AI Code Comprehension (arXiv 2025)](https://arxiv.org/html/2504.04553v2)
- **Type**: Primary | **Evidence Level**: Medium
- **Finding**: Even experienced developers + LLMs struggle with unfamiliar codebases. Human-AI collaboration is most effective.

---

## Internal Analysis (Codebase)

**Source**: Memory graph analysis (`.raise/rai/memory/index.json`)
- **Type**: Primary (direct data) | **Evidence Level**: Very High
- **Finding**: 5,739 nodes, 4,739 edges. 300 components with ZERO `depends_on` edges. Graph knows WHAT exists but not HOW things relate.

**Source**: Session-start skill analysis
- **Type**: Primary (direct observation) | **Evidence Level**: Very High
- **Finding**: Rai re-discovers module dependencies, CLI mappings, data flows, parser protocols every session. Pre-computable but not pre-computed.

**Source**: Patterns.jsonl analysis (PAT-036, PAT-038, PAT-062)
- **Type**: Primary (historical data) | **Evidence Level**: High
- **Finding**: Multiple patterns record re-discovery of architectural knowledge that should be persistent.

---

*Total: 36 evidence entries across 50+ URLs*
*Confidence: High — strong convergence across independent sources*
