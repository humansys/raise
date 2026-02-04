# Deep Research: Spec-Kit Product & Philosophy Critiques

**Research ID**: RES-SPECKIT-CRITIQUE-001-CONCISE
**Date**: 2026-01-23
**Estimated Effort**: 4-6 hours research + 3-4 hours synthesis
**Goal**: Identify differentiation opportunities for spec-kit RaiSE fork

---

## Core Question

**What are the fundamental limitations, complaints, and philosophical tensions in GitHub's spec-kit that could inform a superior RaiSE-enhanced fork?**

Specifically:
- Product gaps and pain points
- Philosophical assumptions that don't apply universally
- Missing features and workarounds
- Scalability limitations
- AI agent alignment effectiveness

---

## Research Scope

### In Scope
- Product critiques (usability, missing features, workflow friction)
- Philosophical critiques (methodology conflicts, assumptions)
- Scalability issues (team size, project complexity)
- Integration problems (Git, CI/CD, IDE)
- AI agent effectiveness (does spec-kit actually help AI?)
- User complaints (GitHub issues, blogs, social media)
- Alternative approaches (competing tools, forks)

### Out of Scope
- General PM tool comparisons (Jira, Linear, etc.)
- Non-specification GitHub features
- Theoretical criticisms without practical impact

---

## Key Research Questions

### 1. Product Limitations (What's Broken)

**Q1.1**: Most frequent user complaints?
- Workflow friction, command limitations, template rigidity
- Performance problems, error handling
- Validation gaps, handoff confusion

**Q1.2**: What features do users wish spec-kit had?
- Feature requests in GitHub Issues
- Workarounds users build (custom scripts)
- Integration requests (Slack, Notion, Linear)
- Export formats (PDF, HTML, Confluence)

**Q1.3**: What makes spec-kit difficult to adopt or scale?
- Onboarding challenges, documentation gaps
- Team size limits (works for 2-5, breaks at 20+?)
- Project complexity (multi-repo, microservices)
- Customization difficulty

**Look for**: GitHub Issues, "Why we stopped using spec-kit" posts, HN/Reddit complaints

---

### 2. Philosophical Critiques (What's Assumed)

**Q2.1**: Underlying assumptions in spec-kit?
- Linear workflow (spec → plan → tasks → implement)
- Single-author (solo/pair vs collaborative)
- Document-centric (Markdown vs wikis/Notion)
- AI-centric (optimized for agents vs humans)
- GitHub-centric (what about GitLab, Bitbucket?)
- Code generation focus (greenfield vs pure architecture)

**Q2.2**: How does spec-kit conflict with existing methodologies?
- **Agile/Scrum**: Too much upfront design? "Working software over docs"?
- **Lean/Kanban**: Too much ceremony? Continuous flow issues?
- **Shape Up**: 6-week cycles vs spec phases? Appetite vs estimation?
- **Continuous Discovery**: Assumes solution known, but discovery first?
- **JTBD**: Focus on features vs outcomes?

**Q2.3**: What does spec-kit get wrong?
- Assumption: Comprehensive specs before coding
  - Counter: Spike-first, learn-as-you-go, emergent design
- Assumption: Tasks are predictable and plannable
  - Counter: Unknown unknowns, emergent complexity
- Assumption: AI benefits from detailed specs
  - Counter: Over-specification constrains creativity?

**Look for**: Philosophical critiques in blogs, methodology debates, conference talks

---

### 3. Usability & Developer Experience

**Q3.1**: What makes spec-kit frustrating daily?
- Command verbosity, context switching
- Cognitive load, slow feedback loops
- IDE integration gaps, no GUI

**Q3.2**: How does spec-kit compare to alternatives?
- **RFC processes** (Rust RFC, Python PEP)
- **ADR systems** (MADR, ADR-tools)
- **Design Doc systems** (Google, Amazon PR/FAQ)
- **Issue-driven** (Linear, GitHub Issues → PRs)
- **Wiki-first** (Notion, Confluence)
- **Shape Up** (Pitch, Betting Table, Hill Charts)

**Q3.3**: What workarounds do teams build?
- Custom scripts, template modifications
- Integration hacks, parallel systems
- Selective adoption (only some commands)

**Look for**: Comparison posts, "spec-kit + X" hybrid approaches, GitHub repos with utils

---

### 4. Scalability & Team Dynamics

**Q4.1**: At what team size does spec-kit break?
- Solo (overkill?), Pairs (sweet spot?), Small teams (4-10)
- Medium (11-30), Large (31+)
- Collaboration issues, merge conflicts, review bottlenecks

**Q4.2**: At what project complexity does it struggle?
- Single repo ✓, Mono-repo ?, Multi-repo microservices ?
- Platform/infrastructure fit?
- Legacy modernization?

**Q4.3**: Distributed teams?
- Timezone issues, language barriers
- Cultural differences, async workflows

**Look for**: Team size mentions, microservices complaints, distributed team stories

---

### 5. Integration & Ecosystem

**Q5.1**: What integrations are missing?
- **PM tools**: Jira, Linear, Asana
- **Docs platforms**: Notion, Confluence, GitBook
- **Communication**: Slack, Discord, Teams
- **CI/CD**: GitHub Actions, GitLab CI
- **IDEs**: VS Code extension, JetBrains plugin
- **AI tools**: Cursor status, Copilot awareness

**Q5.2**: Git workflow fit?
- Branch strategies (Git Flow, trunk-based)
- PR workflows, monorepo tools (Nx, Turborepo)
- Spec history pollution?

**Look for**: Integration feature requests, glue tools, workflow complaints

---

### 6. AI Agent Alignment (Critical)

**Q6.1**: Does spec-kit actually improve AI code generation?
- **Empirical**: A/B tests, code quality metrics
- **Anecdotal**: "Specs helped" vs "AI ignored specs"
- **Theoretical**: Is spec-first optimal for AI?

**Q6.2**: Is template structure optimal for LLMs?
- Markdown vs JSON/YAML for LLMs?
- Section structure intuitive?
- Too verbose vs too terse?
- Context window usage

**Q6.3**: What do AI tool creators say?
- Cursor team, GitHub Copilot team, Anthropic
- Replit, Sourcegraph, Codeium
- Do they recommend spec-kit?

**Look for**: Studies on spec-driven AI, AI developer opinions, alternative formats

---

### 7. Economic & Organizational

**Q7.1**: What is the ROI?
- Time investment (hours to write/maintain)
- Quality impact (fewer bugs?)
- Velocity impact (faster or slower?)

**Q7.2**: Organizational barriers?
- Management: "Just code, don't write docs"
- Developers: "Specs outdated immediately"
- Cultural: Move fast vs spec-first?

**Q7.3**: Solution looking for a problem?
- What problem does spec-kit solve?
- Are these real problems or symptoms?
- Maybe simpler approaches work?

**Look for**: ROI case studies, adoption failures, "specification theater" debates

---

## Primary Research Sources

### High Priority
1. **GitHub spec-kit repo**: Issues, Discussions, PRs, Forks (analyze differences)
2. **Blog posts**: "spec-kit review", "why we stopped using", engineering blogs
3. **Social media**: HN, Reddit (r/ExperiencedDevs), Twitter/X
4. **Competing tools**: Shape Up, Linear, ADRs, RFC processes
5. **AI tool docs**: Cursor, Copilot, Claude recommendations

### Medium Priority
6. **Conference talks**: GitHub Universe, QCon
7. **Community tools**: Extensions, integrations, forks
8. **Research papers**: Specification practices, documentation effectiveness
9. **Podcasts**: Engineering podcasts mentioning spec-kit

---

## Deliverables

### D1: Critique Taxonomy (~5-7K words)

Structure:
```markdown
# Spec-Kit Critiques: Systematic Analysis

## Executive Summary
- Top 5 product limitations
- Top 3 philosophical tensions
- Top 3 RaiSE differentiation opportunities

## 1. Product Critiques
- Workflow friction
- Missing features (ranked by demand)
- Usability issues
- Scalability limits
- Integration gaps

## 2. Philosophical Critiques
- Underlying assumptions + validity
- Methodology conflicts (Agile, Lean, Shape Up, JTBD)
- Paradigm limitations

## 3. Comparative Analysis
- Spec-kit vs alternatives (matrix)
- Hybrid approaches (spec-kit + X)

## 4. AI Agent Alignment Critique
- Effectiveness evidence
- Format optimality
- AI developer opinions

## 5. Economic & Organizational
- ROI analysis
- Adoption barriers
- "Solution looking for problem?" perspective

## 6. Workarounds & Hacks
- Common patterns
- Community extensions

## References
```

---

### D2: RaiSE Fork Differentiation Strategy (~4-6K words)

Structure:
```markdown
# Spec-Kit RaiSE Fork: Differentiation Strategy

## Executive Summary
- Core thesis: Why fork?
- Top 5 differentiators
- Target audience

## 1. Critical Gaps to Fill

| Gap | Spec-kit Limitation | RaiSE Solution | Evidence | Effort | Impact | Priority |
|-----|---------------------|----------------|----------|--------|--------|----------|
| 1 | [Name] | [Fix] | [Sources] | L/M/H | L/M/H | P0/P1/P2 |

## 2. Philosophical Repositioning

| Philosophy | Spec-kit Assumes | RaiSE Fork Position | Implications |
|------------|------------------|---------------------|--------------|

## 3. Feature Additions

| Feature | Demand | Effort | Impact | Priority |
|---------|--------|--------|--------|----------|

## 4. Integration Strategy
- Prioritized integrations
- Ecosystem positioning

## 5. Migration Path
- For existing spec-kit users
- For new users (why choose RaiSE?)

## 6. Positioning & Messaging
- Target segments
- Key messages

## 7. Success Criteria
- Adoption metrics
- Satisfaction metrics
- Impact metrics

## 8. Risks & Mitigations

## 9. Roadmap
- Phase 1: Foundation (months 1-3)
- Phase 2: Differentiation (months 4-6)
- Phase 3: Ecosystem (months 7-12)
```

---

### D3: Feature Specifications

Individual spec files for top differentiation features:
```markdown
# Feature: [Name]

## Context
- Spec-kit limitation
- User complaints (evidence)
- Opportunity

## User Stories
[US1, US2, US3 with acceptance criteria]

## Functional Requirements
[FR-001, FR-002...]

## Technical Approach
[Architecture, integration, data model]

## Implementation Plan
[Phased rollout]

## Success Metrics
[Measurement strategy]
```

---

## Success Criteria

- [ ] **≥20 product limitations** identified
- [ ] **≥10 philosophical tensions** documented
- [ ] **≥30 user complaints** analyzed
- [ ] **≥5 competing tools** compared
- [ ] **Top 5 differentiators** prioritized (effort/impact matrix)
- [ ] **≥3 "quick wins"** (low effort, high impact)
- [ ] **≥2 "strategic bets"** (high effort, transformative)
- [ ] **Clear positioning**: "RaiSE fork vs spec-kit"
- [ ] **Evidence-backed** (all claims cited)

---

## Output Location

```
specs/main/research/speckit-critiques/
├── critique-taxonomy.md              # D1 (~5-7K words)
├── differentiation-strategy.md       # D2 (~4-6K words)
├── features/                         # D3
│   ├── feature-001-[name].md
│   ├── feature-002-[name].md
│   └── ...
└── sources/
    ├── github-issues/
    ├── blog-posts/
    ├── social-media/
    ├── competing-tools/
    └── user-complaints/
```

---

## Execution Guidance

### For AI Agent

1. **Research phase** (3-4 hours):
   - GitHub spec-kit repo (issues, discussions, forks) - 1.5 hours
   - Blog posts and social media - 1 hour
   - Competing tools - 1 hour
   - Build evidence catalog with quotes and links

2. **Analysis phase** (1 hour):
   - Identify patterns across sources
   - Validate critiques (multiple sources = more valid)
   - Extract quantitative findings

3. **Synthesis phase** (2-3 hours):
   - Write critique taxonomy
   - Formulate differentiation strategy
   - Create feature specs for top opportunities

4. **Validation**:
   - Check against success criteria
   - Ensure all deliverables complete
   - Verify evidence citations

---

## RaiSE Context

**Current state**: RaiSE has integrated spec-kit as base system

**Key files**:
- Spec-kit analysis: `specs/main/analysis/architecture/speckit-design-patterns-synthesis.md`
- RaiSE adaptation: `.raise-kit/README.md`

**RaiSE Principles**:
- **§2. Governance as Code**: Specs versionable, traceable
- **§3. Evidence-Based**: Every differentiation backed by evidence
- **§7. Lean (Jidoka)**: Stop at defects, don't cargo-cult
- **§8. Observable**: Transparent decision-making

**Key Questions**:
- Where does spec-kit align with RaiSE?
- Where do tensions exist?
- How can RaiSE fork improve?
- What to keep vs change vs add?

---

**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed
**Researcher**: [Agent ID]
**Start**: [Date] | **End**: [Date]
