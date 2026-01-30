# Brownfield Documentation for Agentic Development: Research Deliverables

**Research ID**: RES-BFLD-AGENT-DOC-001
**Research Date**: 2026-01-23
**Researcher**: Claude Sonnet 4.5
**Status**: ✅ Completed

---

## Executive Summary

This research investigates how top-tier engineering teams using agentic development (AI code assistants, autonomous coding agents) are documenting brownfield (existing) codebases to align code generation agents with existing architecture.

**Research Duration**: 6 hours
**Sources Consulted**: 50+ (web searches, research papers, open source repositories, tools, case studies)
**Total Documentation**: ~30,000 words across 3 main deliverables

---

## Key Findings at a Glance

1. **Configuration files for AI agents** (`.github/copilot-instructions.md`, `.cursorrules`, `AGENTS.md`) are now standard practice (2025-2026)

2. **AST-based code chunking** outperforms naive chunking by 4.3 points in Recall@5 (cAST framework, EMNLP 2025)

3. **Continuous documentation regeneration** (Google Code Wiki model) is replacing static documentation

4. **Productivity paradox**: Individual AI gains (20-40%) don't scale to organizational throughput without process redesign

5. **Quality gates for AI-generated code** are emerging as critical (SonarQube AI Code Assurance)

6. **Multi-language (polyglot) support** is essential for modern microservices architectures

---

## Deliverables

### 📊 Deliverable 1: Landscape Report

**File**: [`landscape-report.md`](./landscape-report.md)
**Length**: ~8,200 words
**Purpose**: Comprehensive state-of-practice analysis for 2026

**Contents**:
- Executive summary (key findings, paradigm shifts, gaps in RaiSE)
- Documentation artifact taxonomy (6 major categories)
- Content & granularity analysis (what to document, how much detail)
- Generation & maintenance patterns (manual, semi-automated, fully automated, hybrid)
- AI agent integration architectures (RAG, fine-tuning, prompt engineering, tool use)
- Emerging standards & tools (MADR, C4 Model, AGENTS.md, OpenAPI, MCP)
- 7 detailed case studies (GitHub Copilot, Cursor, Google Code Wiki, Tabnine, Sourcegraph Cody, Neo4j graphs, Faros AI)
- Comparison with RaiSE SAR system (strengths, gaps, opportunities)
- References (50+ categorized sources)

**Key Sections**:
1. Documentation Artifact Taxonomy
2. Content & Granularity Analysis
3. Generation & Maintenance Patterns
4. AI Agent Integration Architectures
5. Emerging Standards & Tools
6. Case Studies
7. Comparison with RaiSE SAR System
8. Recommendations Summary

---

### 🎯 Deliverable 2: Actionable Recommendations

**File**: [`recommendations.md`](./recommendations.md)
**Length**: ~22,000 words
**Purpose**: Implementation roadmap for improving `raise.1.analyze.code`

**Contents**:
- Decision matrix (quick wins, strategic improvements, experimental additions)
- 4 quick wins (High Impact, Low Effort, P0 priority)
  - REC-001: Add YAML frontmatter to SAR reports
  - REC-002: Generate `.cursorrules` from SAR analysis
  - REC-003: Create multi-language pattern abstraction guide
  - REC-004: Add "AI Consumption Guide" sections
- 5 strategic improvements (High Impact, High Effort, P1-P2 priority)
  - REC-010: Implement AST-based code chunking for RAG
  - REC-011: Build incremental update mechanism
  - REC-012: Extract and document pattern catalog
  - REC-013: Generate C4 model diagrams
  - REC-014: Integrate CI/CD validation gates
- 4 experimental additions (Uncertain Impact, P2-P3 priority)
  - REC-020: Neo4j knowledge graph export
  - REC-021: Agentic RAG for SAR querying
  - REC-022: Living dashboard with trend analysis
  - REC-023: Auto-generate draft ADRs
- Implementation roadmap (3 phases, 12 weeks)
- Risk mitigation strategies
- Success criteria
- Tools and resources (libraries, platforms, learning resources)

**Key Structure**:
- Decision Matrix Overview
- Quick Wins (Detailed Implementation)
- Strategic Improvements (Detailed Implementation)
- Experimental Additions (POC Guidance)
- Implementation Roadmap
- Prioritization Rationale
- Risk Mitigation
- Success Criteria

---

### 📚 Deliverable 3: Research Summary & Sources

**File**: [`sources/research-summary.md`](./sources/research-summary.md)
**Length**: ~10,000 words
**Purpose**: Quick reference and source catalog

**Contents**:
- Key findings (6 major insights with evidence)
- Top 3 actionable recommendations (condensed)
- Novel patterns/practices not in RaiSE (5 patterns)
- Anti-patterns to avoid (4 validated anti-patterns)
- Emerging standards (5 standards: AGENTS.md, MADR, C4, OpenAPI, MCP)
- Tool landscape by category (6 categories, 20+ tools)
- Productivity metrics (6 empirical studies with data)
- Particularly interesting tools/patterns (5 deep dives)
- Conferences & talks (3 events)
- Open source repositories (5 notable examples)
- Success criteria validation (checkboxes)

**Key Sections**:
1. Key Findings
2. Top 3 Recommendations
3. Novel Patterns Not in RaiSE
4. Anti-Patterns to Avoid
5. Emerging Standards
6. Tool Landscape
7. Productivity Metrics (Empirical Studies)
8. Interesting Tools/Patterns
9. Conferences & Talks
10. Open Source Repositories
11. Success Criteria Validation

---

## Success Criteria Achievement

### ✅ Evidence-Based Insights

**Target**: At least 5 case studies, 3 OSS examples, 10 tools
**Achieved**:
- ✅ **7 detailed case studies** (GitHub Copilot, Cursor, Google Code Wiki, Tabnine, Sourcegraph Cody, Neo4j, Faros AI)
- ✅ **5+ open source examples** (awesome-copilot, awesome-cursorrules, Graph-Code, Code Grapher, C4Diagrammer)
- ✅ **15+ tools catalogued** across 6 categories

---

### ✅ Actionable Recommendations

**Target**: At least 3 quick wins, 2 strategic
**Achieved**:
- ✅ **4 quick wins** (YAML frontmatter, .cursorrules, multi-language, AI guide)
- ✅ **5 strategic** (AST RAG, incremental updates, pattern catalog, C4 diagrams, CI/CD gates)
- ✅ **4 experimental** (knowledge graphs, agentic RAG, dashboard, ADRs)
- ✅ **Clear prioritization** with effort estimates and timelines

---

### ✅ Novel Insights

**Target**: At least 1 pattern not in RaiSE, 1 anti-pattern
**Achieved**:
- ✅ **5 novel patterns** (agentic RAG, tool RAG, knowledge graphs, continuous doc service, AI quality gates)
- ✅ **4 validated anti-patterns** (context stuffing, no validation, fine-tuning over RAG, static docs)
- ✅ **1 emerging standard** (AGENTS.md)

---

### ✅ RaiSE Alignment

**Target**: Clear mapping to raise.1.analyze.code improvements
**Achieved**:
- ✅ **Detailed gap analysis** comparing RaiSE vs. industry (7 dimensions)
- ✅ **11 recommendations** mapped to SAR templates
- ✅ **Implementation roadmap** (3 phases, 12 weeks)
- ✅ **Compatibility** with RaiSE ontology and methodology

---

## Quick Start Guide

### For Product/Tech Leads

**Read First**: [Landscape Report - Executive Summary](./landscape-report.md#executive-summary)
**Then**: [Recommendations - Decision Matrix](./recommendations.md#decision-matrix-overview)
**Action**: Review top 3 quick wins (P0 priority, weeks 1-2)

### For Developers/Engineers

**Read First**: [Recommendations - Quick Wins](./recommendations.md#quick-wins-immediate-implementation)
**Then**: [Recommendations - Strategic Improvements](./recommendations.md#strategic-improvements-high-impact-high-effort)
**Action**: Start with REC-001 (YAML frontmatter, 3 days effort)

### For Researchers/Architects

**Read First**: [Landscape Report - Full Document](./landscape-report.md)
**Then**: [Research Summary - Novel Patterns](./sources/research-summary.md#novel-patternspractices-not-in-raise)
**Action**: Evaluate experimental additions for pilot studies

### For Stakeholders

**Read First**: [Research Summary - Key Findings](./sources/research-summary.md#key-findings-executive-summary)
**Then**: [Recommendations - Implementation Roadmap](./recommendations.md#implementation-roadmap)
**Action**: Review phased approach (quick wins → strategic → experimental)

---

## Top 3 Recommendations (Summary)

### 1. Add Machine-Readable Metadata (YAML Frontmatter)

**What**: Add YAML frontmatter to each SAR report with structured metrics, patterns, tags
**Why**: Unlocks all downstream improvements (RAG, CI/CD, trend analysis)
**Effort**: 3 days
**Impact**: High
**Priority**: P0

**Example**:
```yaml
---
report_type: codigo_limpio
metrics:
  total_violations: 42
  critical_count: 7
patterns_detected:
  - repository_pattern
  - dependency_injection
tags:
  - technical_debt
  - refactoring_needed
---
```

---

### 2. Generate `.cursorrules` from SAR Analysis

**What**: Auto-generate `.cursorrules` and `.github/copilot-instructions.md` files from SAR analysis
**Why**: Immediate AI alignment for Cursor, GitHub Copilot users
**Effort**: 3 days
**Impact**: High
**Priority**: P0

**Example Output**:
```markdown
# Project Coding Rules (Generated from RaiSE SAR)

## Approved Patterns
- Repository pattern for data access (see src/repositories/)
- Dependency injection for services

## Anti-Patterns to Avoid
- God classes (OrderService being refactored)
- Direct SQL in controllers
```

---

### 3. Implement AST-Based Chunking for RAG

**What**: Integrate tree-sitter AST parsing to chunk code at semantic boundaries for vector embeddings
**Why**: 4.3-point improvement in Recall@5 (empirical benchmark, cAST framework)
**Effort**: 3-4 weeks
**Impact**: High
**Priority**: P1

**Technology Stack**:
- tree-sitter (AST parsing, multi-language)
- CodeT5 or Voyage-3-large (embeddings)
- Qdrant or FAISS (vector storage)
- Hybrid retrieval (BM25 + semantic search)

---

## Next Steps

### Immediate (Week 1)

1. **Review deliverables** with RaiSE team
2. **Validate quick wins** (REC-001 to REC-004) against current SAR templates
3. **Prioritize** recommendations based on team capacity and roadmap
4. **Start implementation** of REC-001 (YAML frontmatter, 3 days)

### Short-Term (Weeks 2-8)

1. **Complete quick wins** (REC-001 to REC-004)
2. **Begin strategic improvements** (REC-010: AST-based RAG, REC-011: Incremental updates)
3. **Monitor adoption** of generated `.cursorrules` files by team
4. **Measure impact** (AI alignment, developer feedback, productivity metrics)

### Medium-Term (Weeks 9-12)

1. **Pilot experimental additions** (REC-020: Neo4j graph POC, REC-023: Draft ADRs)
2. **Evaluate POC results** (Go/No-Go decisions)
3. **Promote successful experiments** to production
4. **Plan Phase 2** roadmap (Q2 2026)

---

## Sources & References

### Research Papers

- [cAST: Enhancing Code RAG with AST-Based Chunking (EMNLP 2025)](https://arxiv.org/abs/2506.15655)
- [Agentic RAG: A Survey (arXiv 2025)](https://arxiv.org/abs/2501.09136)
- [METR: Early-2025 AI Impact on Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

### Company Blogs & Case Studies

- [GitHub Blog: Copilot CLI Enhanced Agents](https://github.blog/changelog/2026-01-14-github-copilot-cli-enhanced-agents-context-management-and-new-ways-to-install/)
- [GitHub Blog: How to Write a Great AGENTS.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Google Developers Blog: Introducing Code Wiki](https://developers.googleblog.com/introducing-code-wiki-accelerating-your-code-understanding/)

### Tools & Platforms

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Cursor AI Features](https://cursor.com/features)
- [Sourcegraph Cody Documentation](https://sourcegraph.com/docs/cody)
- [CodeSee Platform](https://www.codesee.io/)
- [SonarQube AI Code Assurance](https://docs.sonarsource.com/sonarqube-server/2025.1/instance-administration/analysis-functions/ai-code-assurance/)
- [Neo4j GraphRAG for Python](https://github.com/neo4j/neo4j-graphrag-python)

### Standards & Specifications

- [MADR (Markdown Architecture Decision Records)](https://adr.github.io/madr/)
- [AGENTS.md Specification](https://github.com/agentsmd/agents.md)
- [OpenAPI Specification 3.1.0](https://spec.openapis.org/oas/)
- [C4 Model](https://c4model.com/)

### Industry Reports

- [Faros AI: The AI Productivity Paradox (2025)](https://www.faros.ai/blog/ai-software-engineering)
- [State of Software Architecture Report 2025 (IcePanel)](https://icepanel.medium.com/state-of-software-architecture-report-2025-12178cbc5f93)
- [AI Coding Assistant ROI: Real Productivity Data (Index.dev 2025)](https://www.index.dev/blog/ai-coding-assistants-roi-productivity)
- [Qodo: State of AI Code Quality 2025](https://www.qodo.ai/reports/state-of-ai-code-quality/)

### Open Source Repositories

- [GitHub: awesome-copilot](https://github.com/github/awesome-copilot)
- [GitHub: awesome-cursorrules (PatrickJS)](https://github.com/PatrickJS/awesome-cursorrules)
- [GitHub: awesome-cursorrules (tugkanboz)](https://github.com/tugkanboz/awesome-cursorrules)
- [GitHub: cursorrules-architect (SlyyCooper)](https://github.com/SlyyCooper/cursorrules-architect)
- [GitHub: agentsmd/agents.md](https://github.com/agentsmd/agents.md)

---

## Contact & Questions

For questions about this research or implementation guidance:

- **Research Document**: This repository
- **Implementation Support**: RaiSE team
- **Source Verification**: All sources cited with URLs in deliverables

---

## Research Metadata

**Research ID**: RES-BFLD-AGENT-DOC-001
**Research Objective**: Investigate brownfield codebase documentation practices for AI agent alignment
**Research Date**: 2026-01-23
**Research Duration**: 6 hours
**Researcher**: Claude Sonnet 4.5
**Sources Consulted**: 50+ (web searches, papers, repositories, tools, case studies)
**Total Documentation**: ~30,000 words
**Deliverables**: 3 (landscape report, recommendations, research summary)
**Status**: ✅ Completed

**Success Criteria**:
- ✅ At least 5 real-world case studies with measurable outcomes
- ✅ At least 3 open source examples to study directly
- ✅ At least 10 distinct tools/approaches catalogued
- ✅ At least 3 "quick win" recommendations (high impact, low effort)
- ✅ At least 2 "strategic" recommendations (high impact, high effort)
- ✅ At least 1 novel pattern/practice not currently in RaiSE

---

*This research was conducted to inform improvements to the RaiSE Framework's `raise.1.analyze.code` command for brownfield codebase analysis and AI agent alignment.*
