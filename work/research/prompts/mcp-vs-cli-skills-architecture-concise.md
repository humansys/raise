# Deep Research: MCP vs CLI+Skills Architecture for AI Agents

**Research ID**: RES-MCP-CLI-SKILLS-001-CONCISE
**Date**: 2026-01-24
**Estimated Effort**: 5-7 hours research + 4-5 hours synthesis
**Goal**: Architectural decision for RaiSE context delivery

---

## Core Question

**Should RaiSE use MCP, CLI+Skills, or a Hybrid architecture for delivering context/rules to AI agents?**

**Strategic Context**: RaiSE invested in spec-kit fork (Markdown + CLI). Should we pivot, double-down, or hybrid?

**Key Claim to Validate**: Skills + CLI reduces token consumption by 70% vs MCP (from YouTube video)

---

## Research Scope

### In Scope
- MCP architecture (token consumption, scalability, pain points)
- Skills + CLI pattern (efficiency claims, MCPorter, real-world usage)
- Structured RAG (semantic compression, retrieval strategies)
- Hybrid approaches (multi-tier context systems)
- Performance metrics (tokens, latency, agent effectiveness)
- Strategic fit for RaiSE (differentiation, competitive advantage)

### Out of Scope
- General LLM context window theory (focus on practical patterns)
- Non-coding agents (focus on software development)
- Unvalidated claims (need empirical evidence)

---

## Key Research Questions

### 1. MCP Architecture (What's the Reality?)

**Q1.1**: How does MCP work?
- Protocol specification (Anthropic docs)
- Tool registration and schema loading
- Context injection mechanism
- When schemas enter agent context

**Q1.2**: What is actual token consumption?
- Baseline: Tokens per typical MCP server?
- Per-tool overhead
- Scaling: Linear with tool count?
- Real examples:
  - Browser automation (Playwright): X tokens?
  - File system MCP: X tokens?
  - GitHub MCP: X tokens?

**Q1.3**: What are the pain points?
- Context window exhaustion (real cases)
- Irrelevant tools loaded (waste)
- Performance issues
- Error handling problems

**Q1.4**: Adoption and maturity?
- Official Anthropic support level
- Community adoption (# of MCP servers)
- Production readiness
- Tool vendor support

**Look for**: Anthropic MCP docs, GitHub MCP repos, token measurements, pain point reports

---

### 2. Skills + CLI Pattern (Is 70% Real?)

**Q2.1**: How does Skills + CLI work?
- skill.md format and structure
- Lazy loading mechanism
- CLI invocation from agent
- MCPorter bridge architecture

**Q2.2**: Validate 70% token reduction claim
- **CRITICAL**: Find YouTube video source
- Methodology of measurement
- Can it be reproduced?
- Independent benchmarks?
- Token cost breakdown: MCP vs Skills

**Q2.3**: What are the trade-offs?
- **Pros**: Token efficiency, CLI ecosystem, flexibility
- **Cons**: Maintenance burden, discoverability, platform issues

**Q2.4**: Who's using it?
- Real-world adoption examples
- MCPorter maturity and usage
- Success stories or failures

**Look for**: YouTube video, MCPorter GitHub, skill.md examples, benchmarks, practitioner reports

---

### 3. Structured RAG & Semantic Compression

**Q3.1**: How can RAG optimize guardrails delivery?
- Embedding strategies for rules
- Vector databases (ChromaDB, Pinecone, etc.)
- Retrieval mechanisms (semantic search, hybrid)
- Context window management

**Q3.2**: What formats maximize semantic density?
- **Markdown**: Human-readable, verbose for machines
- **JSON/YAML**: Structured, parseable, still verbose
- **Custom DSLs**: Optimized, but learning curve
- **Hybrid** (Markdown + YAML frontmatter): Best of both?

**Key question**: For LLMs, what format has highest information/token ratio?

**Q3.3**: Compression techniques?
- Summarization, embeddings, schema extraction
- Chunking strategies
- Metadata for filtering
- Deduplication

**Look for**: RAG for code generation, token efficiency comparisons, LLM-optimized formats

---

### 4. Hybrid Architectures

**Q4.1**: Can MCP and CLI coexist?
- MCPorter model (MCP via CLI)
- Selective MCP (critical tools only)
- Multi-tier approach:
  - Tier 1 (hot): Static files, always loaded
  - Tier 2 (warm): Skills + CLI, on-demand
  - Tier 3 (cold): RAG, semantic retrieval

**Q4.2**: RaiSE hybrid vision?
- **Machine layer**: JSON/YAML (compact, parseable)
- **Human layer**: Markdown (readable, maintainable)
- **RAG layer**: Embeddings (scalable retrieval)
- **Delivery router**: Intelligent context selection

**Q4.3**: Successful multi-tier examples?
- IDE systems (VS Code IntelliSense)
- Code search (Sourcegraph, GitHub)
- Documentation systems (Stripe, Twilio)

**Look for**: Multi-tier context patterns, hybrid architectures, best practices

---

### 5. Performance & Metrics

**Q5.1**: Quantitative comparison

| Metric | MCP | Skills+CLI | RAG Hybrid |
|--------|-----|------------|------------|
| Token overhead (10 tools) | ? | ? | ? |
| Token overhead (100 tools) | ? | ? | ? |
| Latency (tool call) | ? | ? | ? |
| Setup complexity | ? | ? | ? |
| Maintenance burden | ? | ? | ? |

**Q5.2**: What do real teams report?
- MCP users: pain points, scale limits
- Skills users: actual token savings, complexity
- RAG users: retrieval quality, latency

**Q5.3**: What do AI tool vendors say?
- **Anthropic**: MCP recommendations, internal usage
- **GitHub (Copilot)**: Context delivery approach
- **Cursor**: MCP vs .cursorrules guidance
- **Replit, Sourcegraph, Codeium**: Their approaches

**Look for**: Benchmarks, case studies, vendor recommendations, blog posts

---

### 6. Strategic Decision for RaiSE

**Q6.1**: What are the options?

**Option A: CLI + Static Files** (current spec-kit)
- Pros: Simple, Git-friendly, proven
- Cons: Token inefficient at scale
- Best for: <50 rules, small projects

**Option B: MCP-first**
- Pros: Official protocol, structured, type-safe
- Cons: Token overhead, vendor lock-in
- Best for: Rich tool integrations

**Option C: Skills + CLI**
- Pros: Token efficient (70%?), flexible
- Cons: Maintenance, discoverability
- Best for: Many integrations, token critical

**Option D: Hybrid (RaiSE differentiation?)**
- Pros: Best of all, unique, scalable
- Cons: Complexity, tooling investment
- Best for: Enterprise scale, competitive edge

**Q6.2**: Competitive advantage?
- If CLI + Static: Just "spec-kit with opinions"?
- If MCP: Everyone else does this too?
- If Skills: Token efficiency story?
- If Hybrid: **"Enterprise-scale AI governance without context exhaustion"**

**Q6.3**: Implementation complexity?
- MCP: Low effort, low customization
- Skills: Medium effort, high control
- Hybrid: High effort, very high payoff?

**Look for**: Differentiation strategies, competitive positioning, ROI analysis

---

## Primary Research Sources

### Critical Sources (Must Have)

1. **Anthropic MCP Documentation**
   - Official specification
   - Best practices
   - Example servers
   - Token consumption guidance

2. **YouTube Video (70% claim)**
   - Find original source
   - Validate methodology
   - Check creator credibility
   - Read comments for validation

3. **MCPorter GitHub**
   - How it works
   - Maturity signals
   - Usage examples
   - Issues/discussions

4. **Claude Code & Cursor Docs**
   - MCP implementation
   - Skills pattern (if documented)
   - Performance characteristics
   - Best practices

5. **Community Discussions**
   - Reddit: r/ClaudeAI, r/LocalLLaMA
   - Hacker News: "MCP", "Claude Code"
   - Discord: Anthropic, Cursor communities
   - GitHub Discussions

### Secondary Sources

6. **Research Papers**: RAG for code, semantic compression
7. **Open Source Examples**: MCP servers, Skills frameworks
8. **Blog Posts**: Token optimization, architecture decisions
9. **Tool Documentation**: LangChain, LlamaIndex, vector DBs

---

## Deliverables

### D1: Comparative Analysis Report (~8-10K words)

```markdown
# MCP vs CLI+Skills vs RAG Hybrid: Analysis

## Executive Summary
- Key findings
- Recommended architecture for RaiSE
- Critical decision factors

## 1. MCP Deep Dive
- How it works
- Token consumption (measured)
- Strengths/weaknesses
- Adoption and maturity

## 2. Skills + CLI Analysis
- How it works
- 70% claim validation (CRITICAL)
- Strengths/weaknesses
- Adoption and tooling

## 3. RAG & Semantic Compression
- RAG for guardrails
- Format comparison (Markdown vs JSON vs YAML)
- Compression techniques
- Hybrid approaches

## 4. Quantitative Comparison
- Performance benchmarks (table)
- Qualitative comparison

## 5. Strategic Analysis for RaiSE
- Alignment with principles
- Competitive differentiation
- Implementation roadmap

## 6. Recommendations
- Primary recommendation + rationale
- Fallback options
- Decision framework

## References
```

---

### D2: RaiSE Hybrid Architecture Spec (~5-7K words)

```markdown
# RaiSE Hybrid Context Delivery Architecture

## Vision
[What this enables]

## Three-Tier System

**Tier 1: Hot (Static Files)**
- Core rules, always loaded
- ~500-1000 tokens

**Tier 2: Warm (Skills + CLI)**
- On-demand tools
- 10-50 tokens per skill

**Tier 3: Cold (RAG)**
- Large rule sets, semantic retrieval
- Variable, optimized per query

## Machine-Optimized Layer
- JSON/YAML schemas
- Compact, parseable

## Human-Readable Layer
- Markdown docs (generated)
- Git-friendly, readable

## Context Delivery Router
- Intelligent tier selection
- Usage analytics
- Auto-optimization

## Implementation Plan
- Phase 1: Foundation (months 1-2)
- Phase 2: Skills (months 3-4)
- Phase 3: RAG (months 5-7)
- Phase 4: Optimization (months 8-9)
- Phase 5: Tooling (months 10-12)

## Success Metrics
- 60-80% token reduction vs MCP at 100 tools
- No degradation in agent effectiveness
- <1 hour to add new rule
- Support 1000+ rules without issues

## Risks & Mitigations
```

---

### D3: Decision Matrix (~3-4K words)

```markdown
# Architectural Decision for RaiSE

## Recommended Approach
[MCP / Skills+CLI / Hybrid / Other]

## Decision Matrix

| Criterion | Weight | MCP | Skills+CLI | Hybrid |
|-----------|--------|-----|------------|--------|
| Token Efficiency | 30% | 5 | 9 | 8 |
| Developer Experience | 25% | 8 | 6 | 7 |
| Differentiation | 20% | 4 | 6 | 9 |
| Maintainability | 15% | 7 | 5 | 6 |
| Ecosystem Fit | 10% | 9 | 7 | 8 |
| **Weighted Score** | | X.X | Y.Y | Z.Z |

## Rationale
[Why recommended approach?]

## Implementation Plan
- Immediate next steps
- POC (months 1-2)
- Production rollout (months 3-6)

## Decision Triggers for Reevaluation
[When to reconsider]
```

---

### D4: POC Specification (~3-4K words)

```markdown
# Proof of Concept: [Recommended Approach]

## Objective
Validate approach with minimal implementation

## Success Criteria
- [ ] Token usage <X
- [ ] Latency <Y ms
- [ ] Agent completes test tasks
- [ ] Developer can add rule in <Z min

## Test Scenarios
1. Agent retrieves relevant rule
2. Agent ignores irrelevant rules
3. Scalability (200 rules)

## Implementation Plan
- Week 1: Setup
- Week 2: Integration
- Week 3: Analysis

## Metrics Collection
- Token counts
- Latency measurements
- Task completion rates
- Developer experience survey

## Go/No-Go Decision
- After Week 2: Preliminary metrics
- After Week 3: Final decision
```

---

## Success Criteria

- [ ] **MCP token consumption measured** (empirical, not estimates)
- [ ] **70% claim validated** (is it real? methodology sound?)
- [ ] **RAG benchmarks** for rules delivery
- [ ] **≥3 independent sources** confirming findings
- [ ] **Quantitative comparison** across ≥8 dimensions
- [ ] **Clear recommendation** with rationale
- [ ] **Decision matrix** with weighted scoring
- [ ] **Implementation roadmap** (if hybrid)
- [ ] **POC specification** ready to execute

---

## Output Location

```
specs/main/research/mcp-vs-cli-skills/
├── comparative-analysis.md           # D1 (~8-10K words)
├── hybrid-architecture-spec.md       # D2 (~5-7K words, if recommended)
├── decision-matrix.md                # D3 (~3-4K words)
├── poc-specification.md              # D4 (~3-4K words)
└── sources/
    ├── mcp/
    │   ├── token-measurements.md
    │   └── pain-points.md
    ├── skills-cli/
    │   ├── 70-percent-claim-validation.md
    │   └── mcporter-analysis.md
    ├── rag/
    │   └── semantic-compression.md
    ├── benchmarks/
    │   └── performance-metrics.csv
    └── references/
        └── youtube-video-notes.md
```

---

## Execution Guidance

### For AI Agent

1. **Research phase** (4-5 hours):
   - MCP docs + token measurements (1.5 hours)
   - YouTube video + 70% claim validation (1 hour)
   - Skills + MCPorter analysis (1 hour)
   - RAG and hybrid patterns (1 hour)
   - Build evidence catalog

2. **Analysis phase** (1-2 hours):
   - Validate claims with measurements
   - Build comparison matrix
   - Calculate weighted scores

3. **Synthesis phase** (3-4 hours):
   - Write comparative analysis
   - Architecture spec (if hybrid)
   - Decision matrix
   - POC spec

4. **Validation**:
   - All measurements cited
   - 70% claim confirmed or debunked
   - Recommendation justified

### Critical: Empirical Validation

- **DO NOT** rely on estimates - MEASURE token counts
- **DO NOT** accept claims without validation - TEST them
- **DO NOT** assume - VERIFY with multiple sources

---

## RaiSE Context

**Current State**: RaiSE uses spec-kit (CLI + Markdown static files)

**Key Files**:
- Spec-kit analysis: `specs/main/analysis/architecture/speckit-design-patterns-synthesis.md`
- Current commands: `.raise-kit/commands/`
- Rules: `.cursor/rules/*.mdc`

**RaiSE Principles**:
- **§2. Governance as Code**: Context versionable, traceable
- **§3. Evidence-Based**: Measurements, not estimates
- **§7. Lean (Jidoka)**: Optimize efficiency
- **§8. Observable**: Transparent context delivery

**Strategic Question**: Is spec-kit the right foundation, or should RaiSE pivot?

**This is a CRITICAL fork-in-the-road architectural decision.**

---

**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed
**Researcher**: [Agent ID]
**Start**: [Date] | **End**: [Date]
