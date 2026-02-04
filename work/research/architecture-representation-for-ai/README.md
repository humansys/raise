# Research: Architecture Representation for AI Understanding

## Research ID: RES-ARCH-REP-001
**Date**: 2026-02-04
**Status**: Complete
**Decision**: Informs Discovery Epic design

---

## Executive Summary

This research investigated how to represent software architecture at a level that enables fast AI understanding and consistent component reuse. Key findings:

1. **Aider's Repository Map** is the proven pattern: graph-ranked key identifiers within token budget
2. **C4 Model's 4 levels** (Context → Container → Component → Code) provide the right abstraction hierarchy
3. **Tree-sitter** is the modern standard for multi-language code structure extraction
4. **Component catalogs** (Backstage pattern) enable reuse discovery
5. **Hybrid extraction** (deterministic tools + LLM synthesis) is academically validated

**Recommended approach**: Build a multi-level component catalog using Tree-sitter extraction, stored in the unified graph, with human validation at each level.

---

## Navigation

| Document | Purpose |
|----------|---------|
| [This file](./README.md) | Overview and recommendations |
| [Evidence Catalog](./sources/evidence-catalog.md) | All sources with ratings |
| [Prompt](./prompt.md) | Research methodology |

---

## Key Findings

### 1. The "Repository Map" Pattern Works

**Claim**: A graph-ranked map of key identifiers is sufficient for AI codebase understanding.
**Confidence**: HIGH
**Evidence**:
- [Aider](https://aider.chat/docs/repomap.html): Uses graph ranking on file dependency graph, sends "most important identifiers" within token budget (~1k tokens)
- [Sourcegraph Cody](https://sourcegraph.com/blog/copilot-vs-cody-why-context-matters-for-code-ai): 82% accuracy vs Copilot's 68% due to "broader project structure" understanding
- [Continue.dev](https://docs.continue.dev/customize/custom-providers): Adopted Aider's repo map pattern

**Implication**: We don't need full codebase mapping. A ranked subset of key symbols is sufficient.

---

### 2. Four Abstraction Levels Are Enough

**Claim**: C4's four levels (System Context → Container → Component → Code) provide adequate granularity.
**Confidence**: HIGH
**Evidence**:
- [C4 Model](https://c4model.com/): 20+ years of industry adoption
- [C4Diagrammer MCP](https://github.com/jonverrier/C4Diagrammer): Creates per-directory summaries because "repos too large for context"
- [Granularity research](https://nadermedhatthoughts.medium.com/granularity-in-software-architecture-bec7c432d6d3): Fine-grained = flexible but hard to maintain

**Implication for RaiSE**:

| C4 Level | RaiSE Equivalent | What We Store |
|----------|------------------|---------------|
| Context | System | External dependencies, integrations |
| Container | Module | Top-level packages/directories |
| Component | Component | Classes, key functions, services |
| Code | (Skip for MVP) | Individual functions (too granular) |

---

### 3. Tree-sitter Is the Extraction Standard

**Claim**: Tree-sitter is the modern tool for multi-language code structure extraction.
**Confidence**: VERY HIGH
**Evidence**:
- [Symflower](https://symflower.com/en/company/blog/2023/parsing-code-with-tree-sitter/): 36x speedup over JavaParser
- [Dropstone](https://www.dropstone.io/blog/ast-parsing-tree-sitter-40-languages): 40+ language support
- [Aider](https://aider.chat/docs/ctags.html): Migrated from ctags to Tree-sitter
- [MCP Server](https://github.com/wrale/mcp-server-tree-sitter): Existing MCP implementation

**Implication**: Use Tree-sitter (via ast-grep or direct bindings) for extraction.

---

### 4. Component Catalogs Enable Reuse

**Claim**: A searchable catalog of components with metadata enables reuse discovery.
**Confidence**: HIGH
**Evidence**:
- [Backstage](https://backstage.io/docs/features/software-catalog/): Spotify's production-proven catalog; teams maintain via Git
- [Atlassian Compass](https://support.atlassian.com/compass/docs/search-the-component-catalog/): Enterprise component discovery
- [Discover](https://technology.discover.com/posts/reuse-basics): "Reusable components need documentation so target audience can consume with little assistance"

**Implication**: Not just a graph — needs searchable metadata: name, purpose, how to use, dependencies.

---

### 5. Hybrid Extraction Is Validated

**Claim**: Deterministic extraction + LLM synthesis produces better results than pure LLM or pure tools.
**Confidence**: HIGH
**Evidence**:
- [arXiv paper](https://arxiv.org/html/2511.05165v1): Reverse engineering extracts class diagram, LLM filters "architecturally significant elements"
- [Spec-Grounded Modernization](https://medium.com/kairi-ai/spec-grounded-modernization-leveraging-ai-specification-kits-for-brownfield-software-systems-e69bdaf04e32): Static analysis → JSON model → LLM enrichment
- Our own ADR-001: DETECT (deterministic) → SCAN (deterministic) → DESCRIBE (LLM) → GOVERN (LLM)

**Implication**: Keep the 4-phase pipeline from prior research; it's academically validated.

---

### 6. Minimum Viable Context Is Key

**Claim**: The smallest high-signal token set outperforms larger unfocused context.
**Confidence**: VERY HIGH
**Evidence**:
- [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): "Finding the smallest possible set of high-signal tokens"
- [IntuitionLabs](https://intuitionlabs.ai/articles/what-is-context-engineering): "Mid-tier LLM with proper context outperforms advanced model without it"
- [DigitalOcean](https://docs.digitalocean.com/products/gradient-ai-platform/concepts/context-management/): Insufficient → hallucination; Overflow → unfocused

**Implication**: Our MVC approach is correct. Quality over quantity.

---

## Synthesis: What Rai Needs to Understand a Codebase

Based on the evidence, Rai needs:

### Level 1: System Overview (Context)
- What is this system?
- What external systems does it integrate with?
- What's the tech stack?

### Level 2: Module Map (Container)
- Top-level directory structure
- What each major module/package does
- Dependencies between modules

### Level 3: Component Catalog (Component)
- Key classes, services, functions
- What each does (purpose)
- How to use it (interface/signature)
- What it depends on

### Level 4: Patterns & Conventions
- Naming conventions observed
- Architectural patterns used
- Error handling approaches
- Testing patterns

---

## Recommendation

### Approach: Progressive Component Catalog

Build a **component catalog** in the unified graph that Rai can query for reuse discovery.

```
┌─────────────────────────────────────────────────────────────┐
│                 DISCOVERY OUTPUT                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  System Node (1)                                             │
│  ├── name, description, tech_stack                          │
│  ├── external_dependencies                                   │
│  └── entry_points                                            │
│                                                              │
│  Module Nodes (N)                                            │
│  ├── name, path, purpose                                     │
│  ├── responsibilities                                        │
│  └── depends_on (other modules)                              │
│                                                              │
│  Component Nodes (M)                                         │
│  ├── name, type (class/function/service)                     │
│  ├── purpose (what it does)                                  │
│  ├── interface (how to use it)                               │
│  ├── location (file:line)                                    │
│  └── depends_on, used_by                                     │
│                                                              │
│  Pattern Nodes (P)                                           │
│  ├── name, description                                       │
│  ├── examples (file:line references)                         │
│  └── adoption_rate                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Node Types for Unified Graph

Extend the unified graph schema with:

```python
NodeType = Literal[
    # Existing
    "pattern", "calibration", "session", "term", "decision",
    "guardrail", "requirement", "feature",
    # New (Discovery)
    "system",      # Top-level system description
    "module",      # Package/directory level
    "component",   # Class/service/function level
    "convention",  # Observed coding convention
]
```

### Extraction Approach

| Phase | Tool | Output |
|-------|------|--------|
| Structure | Tree-sitter / ast-grep | File tree, symbols, dependencies |
| Patterns | ripgrep + heuristics | Naming patterns, code patterns |
| Synthesis | LLM (Rai) | Human-readable descriptions |
| Validation | Human review | Approved nodes for graph |

### MVP Scope for F&F

**What to include**:
1. System overview (1 node)
2. Module map (top-level directories)
3. Key components (classes/services with public interfaces)
4. Basic patterns (naming conventions)

**What to defer**:
- Function-level granularity
- Call graphs
- Data flow analysis
- Git history integration

---

## Drift Detection Strategy

The component catalog enables drift detection:

```python
# On new code (PR/commit):
1. Extract components from changed files
2. Compare against catalog:
   - New component? → Flag for catalog addition
   - Modified interface? → Flag for catalog update
   - Violates pattern? → Flag for review
3. Human decides: update catalog or reject change
```

This is simpler than full architectural drift detection but covers the main use case: "does this new code fit the established patterns?"

---

## Trade-offs Accepted

| Decision | Trade-off | Rationale |
|----------|-----------|-----------|
| Skip function-level | Miss some reuse opportunities | Too granular; component level sufficient for MVP |
| Tree-sitter over LSP | Less semantic info | Faster, simpler, multi-language |
| Human validation required | Slower than full automation | Quality over speed; prevents bad data in graph |
| NetworkX over Neo4j | Limited query capability | Sufficient for our scale; no external dependency |

---

## References

- [Evidence Catalog](./sources/evidence-catalog.md) - 34 sources reviewed
- [ADR-001 - SAR Pipeline](../../dev/decisions/v2/adr-001-sar-pipeline-phases.md) - Prior decision on phases
- [ADR-019 - Unified Graph](../../dev/decisions/adr-019-unified-context-graph.md) - Graph architecture
- [Solution Vision SAR](../sar-component/solution-vision-sar.md) - Prior research

---

## Next Steps

1. Design Discovery epic with human-sequenced phases
2. Define node schemas for system/module/component/convention
3. Implement extraction tools (Tree-sitter based)
4. Create `/discover-*` skills for each phase

---

*Research completed: 2026-02-04*
*Decision: Proceed with Discovery epic design*
