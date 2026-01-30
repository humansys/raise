# Deep Research Prompt: Spec-Kit Product & Philosophy Critiques

**Research ID**: RES-SPECKIT-CRITIQUE-001
**Date Created**: 2026-01-23
**Priority**: High
**Estimated Effort**: 4-6 hours of research + 3-4 hours of synthesis
**Target Outcome**: Actionable insights for spec-kit RaiSE fork differentiation

---

## Research Objective

Investigate critical perspectives, limitations, and complaints about GitHub's spec-kit system (both as a **product** and as a **philosophy**) to:

1. **Identify product gaps and pain points** that practitioners experience
2. **Understand philosophical assumptions** that may not apply universally
3. **Discover missing features** frequently requested or implemented as workarounds
4. **Analyze scalability limitations** for different team sizes and project types
5. **Evaluate methodology constraints** that conflict with other frameworks (Agile, Lean, etc.)
6. **Extract differentiation opportunities** for a RaiSE-enhanced fork

**Core Question**: What are the fundamental limitations, complaints, and philosophical tensions in spec-kit that could inform a superior RaiSE-enhanced alternative?

---

## Research Scope

### In Scope

1. **Product critiques**: Usability issues, missing features, bugs, workflow friction
2. **Philosophical critiques**: Underlying assumptions, methodology conflicts, paradigm limitations
3. **Scalability issues**: Team size constraints, project complexity limits
4. **Integration problems**: Git workflows, CI/CD, IDE integration, tooling gaps
5. **Adoption barriers**: Learning curve, documentation gaps, migration costs
6. **Alternative approaches**: Competing tools, community forks, custom implementations
7. **User complaints**: GitHub issues, discussions, blog posts, social media
8. **Anti-patterns**: Known misuses, workarounds, hacks

### Out of Scope

- General project management tool comparisons (Jira, Linear, etc.)
- Non-specification-related GitHub features
- Theoretical criticisms without practical impact
- Deprecated features no longer in spec-kit

---

## Key Research Questions

### Category 1: Product Limitations

**Q1.1**: What are the most frequent user complaints about spec-kit?

**Investigate**:
- **Workflow friction**: Steps that feel unnecessary or tedious
- **Command limitations**: Missing capabilities in existing commands
- **Template rigidity**: Can't customize templates enough
- **Output format issues**: Markdown limitations, lack of export options
- **Performance problems**: Slow commands, long execution times
- **Error handling**: Poor error messages, unclear failure modes
- **Validation gaps**: Important checks that gates don't catch
- **Handoff confusion**: Unclear next steps, broken chains

**Look for**:
- GitHub Issues on spec-kit repo (open and closed)
- Discussions on GitHub Community
- Blog posts titled "spec-kit pain points" or similar
- Reddit/HN threads about spec-kit frustrations
- Stack Overflow questions revealing confusion

---

**Q1.2**: What features do users wish spec-kit had?

**Investigate**:
- **Feature requests** in GitHub Issues
- **Workarounds** that users build (custom scripts, extensions)
- **Integration requests** (Slack, Notion, Linear, Jira)
- **Export formats** (PDF, HTML, Confluence)
- **Collaboration features** (multi-user editing, conflict resolution)
- **Version control** for specs (diffing, rollback)
- **Analytics** (spec health, task completion rates)
- **Custom command creation** (extension system)

**Look for**:
- GitHub Issues with "enhancement" or "feature request" labels
- Community discussions about "if only spec-kit had..."
- Custom tools built on top of spec-kit
- Forks that add missing features

---

**Q1.3**: What makes spec-kit difficult to adopt or scale?

**Investigate**:
- **Onboarding challenges**: Steep learning curve, unclear starting point
- **Documentation gaps**: Missing examples, unclear best practices
- **Team size limits**: Works for small teams (2-5) but not large (20+)?
- **Project complexity**: Breaks down for multi-repo, microservices?
- **Cross-team coordination**: Hard to sync specs across teams?
- **Legacy system integration**: Difficult to adopt mid-project?
- **Customization difficulty**: Hard to adapt to org-specific needs?

**Look for**:
- "Getting started" complaints
- "Doesn't scale" anecdotes
- Companies that tried and abandoned spec-kit
- Blog posts: "Why we stopped using spec-kit"

---

### Category 2: Philosophical Critiques

**Q2.1**: What are the underlying assumptions in spec-kit's philosophy?

**Investigate**:
- **Linear workflow assumption**: spec → plan → tasks → implement
  - Does this assume waterfall? What about iterative/agile?
- **Single-author assumption**: Designed for solo developer or pair?
  - What about collaborative spec writing?
- **Document-centric assumption**: Markdown files as source of truth
  - What about teams using wikis, Notion, Confluence?
- **AI-centric assumption**: Optimized for AI agents
  - What about human-only workflows?
- **GitHub-centric assumption**: Tight coupling to GitHub
  - What about GitLab, Bitbucket, self-hosted Git?
- **English-centric assumption**: Commands and templates in English
  - What about non-English teams?
- **Code generation focus**: Assumes greenfield or refactoring
  - What about pure architecture work, research, documentation projects?

**Look for**:
- Philosophical critiques in blog posts
- Debates in GitHub Discussions
- Comments about "spec-kit assumes X but we need Y"
- Comparisons with other methodologies (Shape Up, Basecamp, etc.)

---

**Q2.2**: How does spec-kit conflict with existing methodologies?

**Investigate**:

- **Agile/Scrum conflicts**:
  - Spec-kit feels "too much upfront design"?
  - Conflicts with "working software over documentation"?
  - Sprint planning incompatibility?

- **Lean/Kanban conflicts**:
  - Too much ceremony?
  - Doesn't support continuous flow?
  - WIP limits hard to enforce?

- **Shape Up conflicts** (Basecamp methodology):
  - 6-week cycles vs spec-kit phases?
  - Appetite vs estimation?
  - Pitch vs spec?

- **Continuous Discovery conflicts** (Teresa Torres):
  - Spec-kit assumes solution known
  - What about opportunity solution trees?
  - Discovery != specification?

- **Jobs To Be Done conflicts**:
  - Spec-kit focuses on features
  - JTBD focuses on outcomes
  - Mismatch?

**Look for**:
- Blog posts comparing methodologies
- Teams that hybrid spec-kit + X
- Methodology practitioners critiquing spec-kit
- Conference talks about methodology integration

---

**Q2.3**: What does spec-kit get wrong about software development?

**Investigate controversial assumptions**:

- **Assumption**: Specs should be comprehensive before coding
  - **Counter**: Spike-first, learn-as-you-go, emergent design

- **Assumption**: One spec → one implementation
  - **Counter**: Prototypes, experiments, parallel implementations

- **Assumption**: Tasks are predictable and plannable
  - **Counter**: Unknown unknowns, emergent complexity

- **Assumption**: AI agents benefit from detailed specs
  - **Counter**: Over-specification constrains agent creativity?

- **Assumption**: Documentation lives with code (Git)
  - **Counter**: Living docs in wikis, Notion, etc.

- **Assumption**: Linear dependency chains
  - **Counter**: Circular dependencies, emergent architecture

**Look for**:
- Thought leaders critiquing spec-kit assumptions
- Research papers on specification practices
- Industry surveys on software practices
- Debates on "specification theater"

---

### Category 3: Usability and Developer Experience

**Q3.1**: What makes spec-kit frustrating to use daily?

**Investigate**:
- **Command verbosity**: Too many steps? Too much typing?
- **Context switching**: Constantly switching between CLI, editor, browser?
- **Cognitive load**: Hard to remember command sequences?
- **Feedback loops**: Too slow to see results?
- **Error recovery**: Hard to fix mistakes?
- **Discoverability**: Hard to find the right command?
- **IDE integration**: Lack of VS Code/JetBrains plugins?
- **Visual tools**: No GUI, only CLI?

**Look for**:
- User experience studies (if any)
- Usability complaints in issues
- Feature requests for "easier" versions of commands
- Tools built to wrap/simplify spec-kit

---

**Q3.2**: How does spec-kit compare to alternatives?

**Research competing/related tools**:

1. **RFC-style processes**:
   - Rust RFC
   - Python PEP
   - IETF RFC
   - How do they differ?

2. **ADR (Architecture Decision Records)**:
   - MADR format
   - ADR-tools
   - How complementary/overlapping with spec-kit?

3. **Design Doc systems**:
   - Google Design Docs
   - Amazon PR/FAQ
   - How do these compare philosophically?

4. **Issue-driven development**:
   - Linear approach
   - GitHub Issues → PRs
   - When is this better?

5. **Notion/Confluence workflows**:
   - Wiki-first approaches
   - How do teams use these for specs?

6. **Shape Up (Basecamp)**:
   - Pitch format
   - Betting table
   - Hill charts
   - Philosophical differences?

**Look for**:
- Comparison blog posts
- "Why we chose X over spec-kit"
- "We use spec-kit + Y together"
- Hybrid approaches

---

**Q3.3**: What workarounds do teams build?

**Investigate**:
- **Custom scripts** on top of spec-kit
- **Template modifications** that deviate from defaults
- **Integration hacks** (Slack bots, GitHub Actions)
- **Parallel systems** (using spec-kit + another tool)
- **Selective adoption** (only using some commands)
- **Format conversions** (Markdown → other formats)

**Look for**:
- GitHub repos with "spec-kit-utils" or similar
- Scripts in `.specify/scripts/` that extend spec-kit
- Blog posts about "how we adapted spec-kit"
- Forks with significant modifications

---

### Category 4: Scalability and Team Dynamics

**Q4.1**: At what team size does spec-kit break down?

**Investigate**:
- **Solo developers**: Overkill? Too much ceremony?
- **Pairs (2-3)**: Sweet spot?
- **Small teams (4-10)**: Still manageable?
- **Medium teams (11-30)**: Coordination challenges?
- **Large teams (31+)**: Unworkable?

**Specifically**:
- **Collaboration issues**: Multiple people editing specs
- **Review bottlenecks**: Spec approval delays
- **Coordination overhead**: Keeping specs in sync
- **Merge conflicts**: Markdown merge issues
- **Notification fatigue**: Too many spec updates

**Look for**:
- Team size mentioned in adoption stories
- "Doesn't scale beyond N people" complaints
- Large organizations' experiences
- Open source projects using spec-kit (team sizes)

---

**Q4.2**: At what project complexity does spec-kit struggle?

**Investigate**:
- **Single repo, single service**: Works well?
- **Mono-repo, multiple services**: Coordination issues?
- **Multi-repo, microservices**: How to sync specs?
- **Platform/infrastructure projects**: Spec-kit fit?
- **Research/exploration projects**: Spec-kit too rigid?
- **Legacy modernization**: How to integrate?

**Look for**:
- Complaints about multi-repo support
- Microservices coordination patterns
- Projects that outgrew spec-kit
- Use cases where spec-kit doesn't fit

---

**Q4.3**: How does spec-kit handle distributed teams?

**Investigate**:
- **Timezone issues**: Async spec collaboration?
- **Language barriers**: Non-English teams?
- **Cultural differences**: Spec-kit assumes US/Western norms?
- **Tooling access**: Requires GitHub, CLI, etc.
- **Communication overhead**: Specs vs. real-time discussion?

**Look for**:
- Distributed team experiences
- Non-US/Europe adoption stories
- Localization requests
- Async-first workflow adaptations

---

### Category 5: Integration and Ecosystem

**Q5.1**: What integrations are missing or broken?

**Investigate**:

- **Project management tools**:
  - Jira (import specs → issues?)
  - Linear (sync tasks?)
  - Asana, Monday, ClickUp

- **Documentation platforms**:
  - Notion (export specs?)
  - Confluence (sync?)
  - GitBook, Docusaurus

- **Communication tools**:
  - Slack (notifications?)
  - Discord, Teams
  - Email digests

- **CI/CD**:
  - GitHub Actions templates?
  - GitLab CI integration?
  - Jenkins, CircleCI

- **IDEs**:
  - VS Code extension?
  - JetBrains plugin?
  - Neovim, Emacs

- **AI tools**:
  - Cursor integration status?
  - Copilot awareness of specs?
  - Claude, GPT-4 direct integration?

**Look for**:
- Feature requests for integrations
- Community-built integrations
- "Glue" tools that connect spec-kit to other systems
- Complaints about manual data entry

---

**Q5.2**: How does spec-kit fit into existing Git workflows?

**Investigate**:

- **Branch strategies**:
  - Git Flow compatibility?
  - Trunk-based development fit?
  - Feature branch per spec?

- **Pull request workflows**:
  - Spec in PR description?
  - Spec as separate PR?
  - Spec approval process?

- **Monorepo tools**:
  - Nx integration?
  - Turborepo, Bazel?
  - Specs per package?

- **Git history**:
  - Spec changes pollute history?
  - Squash specs?
  - Keep spec commits separate?

**Look for**:
- Best practices guides
- Workflow complaints
- Git history patterns in spec-kit repos
- Tooling to manage spec branches

---

### Category 6: AI Agent Alignment (Core Critique)

**Q6.1**: Does spec-kit actually improve AI code generation?

**Investigate**:

- **Empirical evidence**:
  - A/B tests: with spec vs without?
  - Code quality metrics?
  - Developer satisfaction?

- **Anecdotal evidence**:
  - "Specs helped AI generate better code"
  - "Specs didn't matter, AI ignored them"
  - "AI generates specs better than humans"

- **Theoretical critique**:
  - Is spec-first optimal for AI?
  - Or should AI generate specs iteratively?
  - Does LLM context window matter more than specs?

**Look for**:
- Studies on spec-driven AI coding
- User reports of AI + spec-kit effectiveness
- Comparisons: spec-kit vs .cursorrules vs prompts
- AI agent feedback on spec quality

---

**Q6.2**: Is the spec-kit template structure optimal for LLMs?

**Investigate**:

- **Format critique**:
  - Markdown vs JSON/YAML for LLMs?
  - Section structure intuitive for AI?
  - Too verbose vs too terse?

- **Content critique**:
  - User stories optimal for AI?
  - Acceptance criteria effective?
  - Technical constraints sufficient?

- **Context window usage**:
  - Specs too long for LLM context?
  - Progressive disclosure needed?
  - Embeddings vs direct inclusion?

**Look for**:
- Research on LLM-friendly documentation formats
- AI agent developers' opinions
- Experiments with alternative formats
- Context window optimization patterns

---

**Q6.3**: What do AI agent developers say about spec-kit?

**Investigate**:

- **Cursor team**: Public statements about spec-kit?
- **GitHub Copilot team**: Integration plans?
- **Anthropic (Claude)**: Opinions on spec-driven development?
- **Replit, Sourcegraph, Codeium**: Do they recommend spec-kit?
- **AI coding community**: General sentiment?

**Look for**:
- Conference talks by AI tool creators
- Blog posts from AI agent companies
- Recommendations (or lack thereof)
- Alternative approaches they advocate

---

### Category 7: Economic and Organizational Critiques

**Q7.1**: What is the ROI of spec-kit?

**Investigate**:

- **Time investment**:
  - Hours to write a good spec?
  - Hours to maintain specs?
  - Payoff in reduced coding time?

- **Quality impact**:
  - Fewer bugs with specs?
  - Better architecture?
  - Measurable improvements?

- **Velocity impact**:
  - Faster feature delivery?
  - Or slower due to spec overhead?
  - Break-even point?

**Look for**:
- Case studies with metrics
- Teams that measured before/after
- ROI calculations
- Abandoned spec-kit due to low ROI

---

**Q7.2**: What organizational barriers exist?

**Investigate**:

- **Management resistance**:
  - "Just code, don't write docs"
  - "Too much process"
  - "Agile doesn't need specs"

- **Developer resistance**:
  - "Specs are outdated immediately"
  - "I know what to build, why write it down?"
  - "AI doesn't read my specs anyway"

- **Cultural mismatches**:
  - Move fast and break things vs spec-first?
  - Startup culture vs structured process?
  - Remote-first vs spec-heavy?

**Look for**:
- Adoption failure stories
- Change management challenges
- Cultural critiques
- "Why specs don't work in practice"

---

**Q7.3**: Is spec-kit a solution looking for a problem?

**Critical perspective**:

- **Problem statement**: What problem does spec-kit solve?
  - Unclear requirements → Spec clarifies
  - AI misalignment → Spec aligns
  - Poor planning → Spec enforces structure

- **Critique**: Are these real problems?
  - Or symptoms of deeper issues (unclear product vision, poor communication, wrong AI tool)?

- **Alternative hypothesis**:
  - Maybe specs aren't the solution
  - Maybe better tools (better AI, better PM, better communication)
  - Maybe simpler approaches work (Issues, RFCs, ADRs)

**Look for**:
- Philosophical critiques of specification culture
- "Specification theater" accusations
- Comparisons to "documentation for documentation's sake"
- Arguments for "working software over comprehensive documentation"

---

## Research Sources

### Primary Sources (Highest Value)

1. **GitHub spec-kit Repository**:
   - Issues (open and closed) - complaints, feature requests
   - Discussions - philosophical debates
   - PRs - rejected features reveal limitations
   - Forks - what did people change?
   - Stars/watchers - adoption signals

2. **GitHub Community Discussions**:
   - Search: "spec-kit" in discussions
   - Feedback on spec-kit usage
   - Support requests revealing pain points

3. **Blog Posts and Articles**:
   - Search: "spec-kit review", "spec-kit critique", "why we stopped using spec-kit"
   - Engineering blogs of companies
   - Personal blogs of practitioners

4. **Social Media**:
   - Hacker News: Search "spec-kit" (discussions)
   - Reddit: r/ExperiencedDevs, r/programming
   - Twitter/X: "spec-kit" sentiment analysis
   - Lobsters, Dev.to

5. **Competing Tools Documentation**:
   - Shape Up (Basecamp)
   - Linear Method
   - Amazon PR/FAQ
   - Google Design Docs
   - Compare philosophies and features

### Secondary Sources

6. **Academic Research**:
   - Papers on software specification practices
   - Studies on documentation effectiveness
   - Research on AI-driven development

7. **Podcasts and Videos**:
   - GitHub Universe talks mentioning spec-kit
   - Engineering podcasts discussing spec-kit
   - YouTube reviews/tutorials (comments reveal pain points)

8. **Internal Documentation** (if available):
   - GitHub's internal usage of spec-kit
   - Dogfooding experiences
   - Internal RFCs about spec-kit

9. **Community Tools**:
   - Awesome lists mentioning spec-kit
   - Tool comparisons
   - Integration repositories

---

## Analysis Framework

For each critique/limitation discovered, evaluate:

### Validity Assessment
- [ ] **Evidence Level**: Anecdotal / Single complaint / Multiple complaints / Systematic issue
- [ ] **Impact Severity**: Minor annoyance / Moderate limitation / Major blocker
- [ ] **Frequency**: Rare / Occasional / Common / Pervasive
- [ ] **User Segment**: Solo devs / Small teams / Large teams / Enterprise / All

### Root Cause Analysis
- [ ] **Type**: Product limitation / Philosophical assumption / Usability issue / Integration gap
- [ ] **Fixability**: Easy fix / Moderate effort / Fundamental redesign needed / Unfixable (paradigm clash)
- [ ] **Workarounds**: None / Hacky / Reasonable / Better alternative exists

### RaiSE Opportunity Analysis
- [ ] **Differentiation Potential**: Low / Medium / High
- [ ] **Alignment with RaiSE Principles**: Contradicts / Neutral / Supports
- [ ] **Implementation Feasibility**: Hard / Moderate / Easy
- [ ] **Strategic Value**: Nice-to-have / Important / Critical

---

## Synthesis Requirements

### Deliverable 1: Critique Taxonomy

**Format**: Markdown document (~5-7K words)

**Structure**:
```markdown
# Spec-Kit Critiques: A Systematic Analysis

## Executive Summary
- Top 5 product limitations
- Top 3 philosophical tensions
- Top 3 differentiation opportunities for RaiSE

## 1. Product Critiques

### 1.1 Workflow Friction
- [List of friction points with evidence]
- Severity: High/Medium/Low
- Frequency: Common/Occasional/Rare

### 1.2 Missing Features
- [Ranked list of requested features]
- Demand signals (# of requests, upvotes, workarounds)

### 1.3 Usability Issues
- [UX problems with specific examples]

### 1.4 Scalability Limits
- Team size breakpoints
- Project complexity ceilings

### 1.5 Integration Gaps
- Missing tool integrations
- Broken workflows

## 2. Philosophical Critiques

### 2.1 Underlying Assumptions
- [List assumptions + validity assessment]

### 2.2 Methodology Conflicts
- Agile/Scrum tensions
- Lean/Kanban incompatibilities
- Shape Up differences
- Continuous Discovery gaps

### 2.3 Paradigm Limitations
- What spec-kit assumes about software development
- What reality shows
- Mismatches

## 3. Comparative Analysis

### 3.1 Spec-Kit vs Alternatives
- [Tool comparison matrix]
- When to use spec-kit
- When to use alternatives

### 3.2 Hybrid Approaches
- Teams using spec-kit + X
- Integration patterns
- Best practices

## 4. AI Agent Alignment Critique

### 4.1 Effectiveness Evidence
- Does spec-kit actually help AI?
- Empirical data
- Anecdotal reports

### 4.2 Format Optimality
- Is Markdown + spec structure ideal for LLMs?
- Alternative formats
- Context window considerations

## 5. Economic and Organizational Critiques

### 5.1 ROI Analysis
- Time investment vs payoff
- Measurable outcomes
- Break-even scenarios

### 5.2 Adoption Barriers
- Management resistance
- Developer resistance
- Cultural mismatches

## 6. Workarounds and Hacks

### 6.1 Common Workarounds
- [Patterns teams use to overcome limitations]

### 6.2 Community Extensions
- Tools built on spec-kit
- Forks with modifications

## References
[Categorized by source type]
```

---

### Deliverable 2: RaiSE Fork Differentiation Strategy

**Format**: Markdown document (~4-6K words)

**Structure**:
```markdown
# Spec-Kit RaiSE Fork: Differentiation Strategy

## Executive Summary
- Core thesis: Why fork spec-kit?
- Top 5 differentiators
- Target audience

## 1. Critical Gaps to Fill

### Gap 1: [Name]
**Critique**: [Spec-kit limitation]
**RaiSE Solution**: [How RaiSE fork addresses it]
**Evidence**: [User complaints, feature requests]
**Implementation**: [Technical approach]
**Effort**: [L/M/H]
**Impact**: [L/M/H]
**Priority**: P0/P1/P2

[Repeat for each gap]

## 2. Philosophical Repositioning

### Philosophy 1: [Name]
**Spec-kit assumes**: [Assumption]
**RaiSE fork position**: [Alternative philosophy]
**Rationale**: [Why this is better]
**Implications**: [What changes in commands/templates]

[Repeat for each philosophical difference]

## 3. Feature Additions

| Feature | Demand | Effort | Impact | Priority |
|---------|--------|--------|--------|----------|
| [Feature 1] | High | Low | High | P0 |
| [Feature 2] | Medium | Medium | High | P1 |
| ... | | | | |

### Per Feature Detail

#### Feature 1: [Name]
**User Story**: As a [user], I want [capability] so that [benefit]
**Current State**: Spec-kit doesn't support this; users work around via [workaround]
**Proposed State**: RaiSE fork provides [solution]
**Implementation Plan**: [Technical approach]
**Success Metrics**: [How to measure success]

## 4. Integration Strategy

### Integrations to Build
- [List prioritized integrations]
- Per integration: target tool, use case, technical approach

### Ecosystem Positioning
- How RaiSE fork fits into broader tooling landscape
- Partnerships/collaborations
- Open source strategy

## 5. Migration Path

### For Existing Spec-Kit Users
- Compatibility strategy
- Migration tooling
- Upgrade path

### For New Users
- Why choose RaiSE fork over spec-kit?
- Unique value propositions
- Getting started experience

## 6. Positioning and Messaging

### Target Segments
- Primary: [User segment]
- Secondary: [User segment]
- Tertiary: [User segment]

### Key Messages
- For spec-kit users: "Everything you love, plus [X, Y, Z]"
- For new users: "Spec-kit, but [differentiation]"
- For skeptics: "We addressed [concern A, B, C]"

## 7. Success Criteria

### Adoption Metrics
- Target: X users in Y months
- Target: Z% of spec-kit users try RaiSE fork

### Satisfaction Metrics
- NPS target
- Feature satisfaction scores
- Retention rate

### Impact Metrics
- Measurable improvements in [X, Y, Z]
- ROI calculations
- Case studies

## 8. Risks and Mitigations

### Risk 1: [Name]
**Description**: [Risk]
**Probability**: L/M/H
**Impact**: L/M/H
**Mitigation**: [Strategy]

[Repeat for each risk]

## 9. Roadmap

### Phase 1: Foundation (Months 1-3)
- [Deliverables]

### Phase 2: Differentiation (Months 4-6)
- [Deliverables]

### Phase 3: Ecosystem (Months 7-12)
- [Deliverables]

## References
- Spec-kit critique analysis
- User research
- Competitive analysis
```

---

### Deliverable 3: Feature Specifications

**Format**: Individual spec files per major feature

**Structure**:
```markdown
# Feature: [Name]

## Context
**Spec-kit limitation**: [What's missing/broken]
**User complaints**: [Evidence]
**Opportunity**: [How this differentiates RaiSE fork]

## User Stories

### US1: [Primary use case]
As a [user],
I want [capability],
So that [benefit].

**Acceptance Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

[Repeat for US2, US3...]

## Functional Requirements

FR-001: [Requirement]
FR-002: [Requirement]

## Technical Approach

### Architecture
[High-level design]

### Integration Points
[With existing spec-kit components]

### Data Model
[If applicable]

## Implementation Plan

### Phase 1: MVP
- [Tasks]

### Phase 2: Enhancement
- [Tasks]

## Success Metrics
- [How to measure if this feature solves the problem]

## References
- [Links to spec-kit issues, user requests, etc.]
```

---

## Success Criteria

This research will be successful if it produces:

1. **Comprehensive Critique Catalog**:
   - [ ] At least 20 distinct product limitations identified
   - [ ] At least 10 philosophical tensions documented
   - [ ] At least 30 user complaints analyzed
   - [ ] At least 5 competing tool comparisons

2. **Validated Insights**:
   - [ ] Each critique supported by multiple sources
   - [ ] Severity and frequency assessed
   - [ ] Root causes identified
   - [ ] Workarounds documented

3. **Actionable Differentiation**:
   - [ ] At least 10 differentiation opportunities identified
   - [ ] Top 5 prioritized with effort/impact analysis
   - [ ] At least 3 "quick wins" (low effort, high impact)
   - [ ] At least 2 "strategic bets" (high effort, transformative impact)

4. **Strategic Clarity**:
   - [ ] Clear positioning: "RaiSE fork vs spec-kit"
   - [ ] Target audience identified
   - [ ] Value propositions articulated
   - [ ] Roadmap outlined

5. **Evidence-Based**:
   - [ ] All claims supported by citations
   - [ ] Counterarguments considered
   - [ ] Bias and assumptions acknowledged
   - [ ] Alternative perspectives included

---

## Timeline

**Week 1**:
- Days 1-2: GitHub spec-kit repo deep dive (issues, discussions, PRs, forks)
- Day 3: Blog posts and social media sentiment analysis
- Day 4: Competing tools research
- Day 5: Initial synthesis

**Week 2**:
- Days 1-2: Deep dive on top critiques (validate, find more evidence)
- Day 3: AI agent alignment critique
- Day 4: Economic and organizational critique
- Day 5: Workarounds and community extensions

**Week 3**:
- Days 1-2: Differentiation strategy formulation
- Day 3: Feature specification for top opportunities
- Days 4-5: Report writing + deliverables

**Total**: ~12-15 working days for thorough research + synthesis + strategy

---

## Output Location

**Deliverables saved to**:
```
specs/main/research/speckit-critiques/
├── critique-taxonomy.md              # Deliverable 1 (~5-7K words)
├── differentiation-strategy.md       # Deliverable 2 (~4-6K words)
├── features/                         # Deliverable 3
│   ├── feature-001-[name].md
│   ├── feature-002-[name].md
│   └── ...
└── sources/
    ├── github-issues/                # Extracted issues
    ├── blog-posts/                   # Summaries with links
    ├── social-media/                 # Sentiment analysis
    ├── competing-tools/              # Comparison notes
    └── user-complaints/              # Categorized complaints
```

---

## Meta: How to Use This Prompt

### For AI Research Agent

If executing this research with an AI agent:

1. **Read this prompt completely**
2. **Start with GitHub repo** (issues, discussions, forks)
3. **Collect evidence systematically** (save quotes, links, examples)
4. **Look for patterns** across sources (recurring complaints)
5. **Validate critiques** (multiple sources = more valid)
6. **Apply analysis framework** to each finding
7. **Synthesize incrementally** (don't wait until end)
8. **Generate deliverables** according to templates
9. **Validate** against success criteria
10. **Iterate** if gaps remain

### For Human Researcher

If executing manually:

1. **Allocate 2-3 hour blocks** for focused research
2. **Start with GitHub Issues** (sort by comments, reactions)
3. **Use advanced search** ("spec-kit" AND "limitation" OR "problem")
4. **Take structured notes** (use analysis framework as template)
5. **Interview users** if possible (Reddit, Discord, direct outreach)
6. **Compare with alternatives** side-by-side
7. **Synthesize daily** (capture insights while fresh)
8. **Maintain skepticism** (not all critiques are valid)
9. **Seek counterarguments** (spec-kit defenders)
10. **Document assumptions** (your own biases)

---

## Related RaiSE Context

**Current state**: RaiSE has integrated spec-kit as base system

**Key Documents**:
- **Spec-kit analysis**: `specs/main/analysis/architecture/speckit-design-patterns-synthesis.md`
- **RaiSE adaptation**: `.raise-kit/README.md`
- **Command standardization**: `specs/main/migration/command-standardization-roadmap.md`
- **Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`

**RaiSE Principles to Apply**:
- **§2. Governance as Code**: Specs are versionable, traceable
- **§3. Evidence-Based**: Every differentiation backed by evidence
- **§7. Lean (Jidoka)**: Stop at defects, don't cargo-cult spec-kit
- **§8. Observable Workflow**: Transparent decision-making

**Key Questions for RaiSE**:
- Where does spec-kit align with RaiSE principles?
- Where do tensions exist?
- How can RaiSE fork improve on spec-kit foundation?
- What should RaiSE keep vs change vs add?

---

**Research Start Date**: [YYYY-MM-DD]
**Research End Date**: [YYYY-MM-DD]
**Researcher**: [Name/Agent ID]
**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed

---

*This research prompt is part of the RaiSE Framework evolution (Feature 012: Raise Commands Research), aimed at identifying differentiation opportunities for a spec-kit RaiSE fork that better serves agentic development and structured software engineering.*
