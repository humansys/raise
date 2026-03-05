# Evidence Catalog: Documentation Practices for CLI Frameworks

## Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|----------------|-------------|
| 1 | [Diataxis Framework](https://diataxis.fr/) | Primary | Very High | 4-type taxonomy (tutorials, how-to, reference, explanation) on 2x2 matrix (action/cognition x study/work). Adopted by Django, Canonical, NumPy, hundreds of projects. |
| 2 | [llms.txt Specification](https://llmstxt.org/) | Primary | High | Proposed standard for AI-readable site index. Markdown H1 + blockquote + H2 sections with URL lists. 844k+ sites adopted by Oct 2025. Used by Anthropic, Stripe, Cloudflare. |
| 3 | [Agent-Friendly Docs - Dachary Carey](https://dacharycarey.com/2026/02/18/agent-friendly-docs/) | Secondary | High | Practical field testing of agent doc consumption. Key: break pages into focused units (<5000 chars), serve .md versions, avoid JS-rendered docs, use llms.txt as index. |
| 4 | [uv Documentation (Astral)](https://docs.astral.sh/uv/) | Primary | Very High | Diataxis-aligned structure: Getting Started > Guides > Concepts > Reference. 50k+ GitHub stars. Gold standard for Python CLI tool docs. |
| 5 | [Mastra: Structuring Projects for AI Agents](https://mastra.ai/blog/how-to-structure-projects-for-ai-agents-and-llms) | Secondary | High | AGENTS.md/CLAUDE.md for persistent agent context, Skills spec, MCP docs server, frontmatter metadata for package mapping, Diataxis for structure. |
| 6 | [pyOpenSci Python Package Guide](https://www.pyopensci.org/python-package-guide/documentation/index.html) | Primary | Very High | Community standard for Python OSS docs. Required: README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE. User docs: install, getting started, API, tutorials. |
| 7 | [Mintlify: AI Documentation Trends 2025](https://www.mintlify.com/blog/ai-documentation-trends-whats-changing-in-2025) | Secondary | High | llms.txt rollout across thousands of doc sites. AI-first discovery model emerging. Content negotiation (Accept: text/markdown) as pattern. |
| 8 | [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) | Primary | Very High | De facto standard for Python project doc sites. Used by Typer, FastAPI, Pydantic. mkdocstrings for auto API docs from docstrings. |
| 9 | [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings) | Primary | High | Auto-generates API reference from Python docstrings. Google-style format, parameter tables, source code links. Integrates with MkDocs. |
| 10 | [Fern: API Docs for AI Agents](https://buildwithfern.com/post/optimizing-api-docs-ai-agents-llms-txt-guide) | Secondary | Medium | llms.txt + llms-full.txt pattern for API documentation. Token-efficient summaries vs full content split. |
| 11 | [GitBook: LLM-ready docs](https://gitbook.com/docs/publishing-documentation/llm-ready-docs) | Secondary | Medium | Auto-generated MCP server per published space. Structured retrieval without scraping. |
| 12 | [Real Python: MkDocs Guide](https://realpython.com/python-project-documentation-with-mkdocs/) | Tertiary | Medium | Step-by-step MkDocs setup with Material theme. docs/ directory convention, mkdocs.yml config, GitHub Pages deploy. |
| 13 | [Biel.ai: Optimizing Docs for AI Agents](https://biel.ai/blog/optimizing-docs-for-ai-agents-complete-guide) | Secondary | Medium | Self-contained pages, predictable heading hierarchies, reduce ambiguity to prevent hallucinations, concise content. |
| 14 | [pyOpenSci README Best Practices](https://www.pyopensci.org/python-package-guide/documentation/repository-files/readme-file-best-practices.html) | Primary | Very High | README must include: name, badges, 2-4 sentence description, quick-start example, doc links, citation info. |
| 15 | [Open Source Pre-Launch Checklist](https://github.com/libresource/open-source-checklist) | Secondary | Medium | README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, CHANGELOG, clean issue queue, no sensitive data in history. |
| 16 | [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) | Primary | High | SKILL.md pattern: YAML frontmatter + markdown instructions. Agent-readable by design. Persistent context file for extending agent capabilities. |
| 17 | [Agent Skills Specification](https://agentskills.io/specification) | Secondary | Medium | Emerging standard for agent skill folders. Referenced by Mastra as cross-agent pattern. |
| 18 | [Sequin: We fixed our docs with Diataxis](https://blog.sequinstream.com/we-fixed-our-documentation-with-the-diataxis-framework/) | Secondary | High | Real-world Diataxis migration case study. Before: mixed content types. After: clear separation improved discovery and maintenance. |

## Evidence Level Criteria

| Level | Criteria |
|-------|----------|
| Very High | Production-proven at scale, widely adopted standard, >10k stars/users |
| High | Expert practitioners, established companies, >1k stars/users |
| Medium | Community-validated, emerging consensus |
| Low | Single source, unvalidated |
