# Deep Research Prompt: Rule Definition & Extraction for IDE-Based Code Generation Alignment

**Research ID**: RES-RULE-EXTRACT-ALIGN-001
**Date Created**: 2026-01-23
**Priority**: High
**Estimated Effort**: 3-5 hours of research + 3-4 hours of synthesis
**Target Outcome**: Actionable recommendations for improving `raise.rules.generate`

---

## Research Objective

Investigate how top-tier engineering teams using AI-powered IDEs (Cursor, GitHub Copilot, Codeium, etc.) are **defining, extracting, structuring, and maintaining code generation rules** to:

1. **Align AI code generation** with project-specific patterns, conventions, and architecture
2. **Optimize rule quantity and granularity** (avoiding both under-specification and rule overload)
3. **Structure rules for maximum IDE/agent comprehension** (format, metadata, organization)
4. **Automate rule extraction** from existing codebases (pattern mining, static analysis)
5. **Maintain rule quality over time** (validation, evolution, conflict resolution)
6. **Measure rule effectiveness** (adherence metrics, code quality impact)

**Core Question**: What is the optimal approach to defining and extracting code generation rules that maximally improve AI agent alignment without overwhelming developers or agents?

---

## Research Scope

### In Scope

1. **Rule definition methodologies** used by high-performing teams
2. **Rule extraction techniques** (manual, semi-automated, fully automated)
3. **Rule formats and structures** (.cursorrules, .mdc, JSON schemas, custom DSLs)
4. **Quantity and granularity heuristics** (how many rules? how specific?)
5. **Categorization and taxonomy** (types of rules, prioritization schemes)
6. **IDE/agent integration patterns** (Cursor, VS Code, JetBrains, etc.)
7. **Maintenance and evolution strategies** (updates, deprecation, conflict resolution)
8. **Validation and quality assurance** (how to ensure rules are effective)
9. **Empirical studies** with measurable outcomes (adherence rates, code quality, velocity)

### Out of Scope

- General code style guides without AI agent context
- Linter configurations (ESLint, Pylint) unless explicitly used for agent alignment
- Model fine-tuning or prompt engineering (focus on rule-based guidance)
- Rules for non-code generation (deployment, security policies, etc.)

---

## Key Research Questions

### Category 1: Rule Definition Methodology

**Q1.1**: What types of rules are teams defining for AI code generation?

**Investigate**:

- **Prohibitive rules** ("Never use X pattern")
- **Prescriptive rules** ("Always use Y pattern for Z scenario")
- **Informative rules** ("This codebase uses architecture A")
- **Contextual rules** ("In module M, follow pattern P")
- **Quality rules** ("Ensure test coverage >80%")
- **Architecture rules** ("Respect layer boundaries")
- **Convention rules** ("Naming: use camelCase for functions")
- **Domain rules** ("Business logic: discounts in OrderService")
- **Anti-pattern rules** ("Avoid God classes, flag if >500 LOC")
- **Migration rules** ("We're moving from REST to GraphQL")

**Look for**:
- Real examples from public repos (`.cursorrules`, `.cursor/rules/`, `.github/copilot-instructions.md`)
- Categorization schemes used in practice
- Ratio of prohibitive vs prescriptive rules

---

**Q1.2**: How are teams determining what to include in rules vs what to omit?

**Investigate**:

- **Signal-to-noise optimization**: What's the threshold for "rule-worthy" vs "documented elsewhere"?
- **Frequency heuristics**: Only codify patterns used in 3+ places?
- **Criticality thresholds**: Only rules that prevent breaking changes or security issues?
- **Agent confusion signals**: Rules created reactively when AI generates off-pattern code?
- **Prioritization frameworks**: P0 (must follow) vs P1 (should follow) vs P2 (nice to have)

**Key questions**:
- How do teams avoid rule explosion (too many rules)?
- How do teams avoid under-specification (too few rules)?
- What's the "Goldilocks zone" for rule quantity?

**Look for**:
- Blog posts about rule curation processes
- Decision frameworks for rule inclusion
- Examples of "too many rules" problems

---

**Q1.3**: What granularity levels are effective for rules?

**Investigate spectrum**:

- **Project-wide rules** (apply to entire codebase)
- **Module/package rules** (apply to specific directories)
- **Layer rules** (apply to domain/application/infrastructure layers)
- **File-type rules** (apply to .ts vs .tsx vs .test.ts)
- **Temporal rules** (apply during migration periods only)

**Key questions**:
- Do teams use hierarchical rule systems (general → specific)?
- How do specificity conflicts get resolved?
- What's the cognitive load on developers maintaining rules at multiple levels?

**Look for**:
- Examples of hierarchical rule systems
- Conflict resolution mechanisms
- IDE support for scoped rules

---

### Category 2: Rule Extraction Techniques

**Q2.1**: How are teams extracting rules from existing codebases?

**Investigate approaches**:

1. **Manual extraction**:
   - Senior developers documenting patterns
   - Architecture review sessions → rule formalization
   - Code review feedback → rule creation

2. **Semi-automated extraction**:
   - AI analyzes codebase, proposes rules, human curates
   - Static analysis identifies patterns, human validates
   - Pattern mining tools suggest candidates

3. **Fully automated extraction**:
   - AST analysis for pattern detection
   - Frequency analysis (if pattern appears 5+ times, suggest rule)
   - Machine learning on code review comments
   - Diff analysis (what changes get rejected in PRs → rules)

**Tools to research**:
- Pattern mining tools (PMD, SonarQube custom rules)
- AI-powered rule generators (GPT-4 + codebase analysis)
- Custom scripts using tree-sitter, Roslyn, etc.
- Commercial solutions (Codiga, Moderne, etc.)

**Look for**:
- Open source tools with GitHub repos
- Custom in-house solutions (conference talks, blog posts)
- Hybrid workflows (AI + human curation)

---

**Q2.2**: What evidence are teams requiring to validate a rule?

**Investigate**:

- **Positive examples**: How many? (RaiSE uses 3-5)
- **Negative examples (anti-patterns)**: How many? (RaiSE uses 2)
- **Quantitative thresholds**: Pattern must appear in X% of codebase?
- **Qualitative validation**: Architect approval required?
- **Historical validation**: Pattern survived for Y months without issues?

**Look for**:
- Documentation of "rule approval gates"
- Examples of rejected rule proposals
- Templates showing evidence requirements

---

**Q2.3**: How are teams representing patterns for rule extraction?

**Investigate**:

- **Code snippets** (literal examples)
- **AST patterns** (structural templates)
- **Regex patterns** (syntactic patterns)
- **Semantic descriptions** (natural language → AI interprets)
- **Formal specifications** (Z notation, TLA+, etc.)

**Key questions**:
- What level of formality is practical?
- Do AI agents prefer code examples or semantic descriptions?
- How do teams balance precision vs flexibility?

---

### Category 3: Rule Format and Structure

**Q3.1**: What file formats are teams using for rules?

**Investigate**:

1. **Markdown-based**:
   - `.cursorrules` (Cursor's format)
   - `.cursor/rules/*.mdc` (RaiSE's approach)
   - `.github/copilot-instructions.md` (GitHub Copilot)
   - Plain markdown with conventions

2. **Structured formats**:
   - JSON schemas
   - YAML configurations
   - TOML files
   - Custom DSLs

3. **Hybrid formats**:
   - Markdown with YAML frontmatter (RaiSE's .mdc approach)
   - JSON with embedded markdown descriptions

**Look for**:
- Adoption signals (which formats are most common)
- IDE/agent support (which formats are natively understood)
- Extensibility (can metadata be added)

---

**Q3.2**: What metadata are teams embedding in rules?

**Investigate presence of**:

- **Identification**: ID, name, version
- **Categorization**: Type, category, tags
- **Scope**: Glob patterns (which files this applies to)
- **Priority**: P0/P1/P2, severity levels
- **Lifecycle**: Created date, author, deprecated flag
- **Rationale**: Why this rule exists (link to ADR, incident, etc.)
- **Evidence**: Links to examples, counter-examples
- **Enforcement**: Manual check vs automated validation
- **Agent hints**: LLM-specific guidance (e.g., "always explain reasoning")

**Example** (from RaiSE .mdc):
```yaml
---
id: 910-rule-management
category: meta
scope: [".cursor/rules/**/*.mdc"]
priority: P0
enforcement: cursor-ai
version: 1.0.0
---
```

**Look for**:
- Metadata schemas in the wild
- Which fields are most common
- Which fields correlate with rule effectiveness

---

**Q3.3**: How are teams structuring rule content?

**Investigate section patterns**:

1. **Purpose/Rationale**: Why this rule exists
2. **Scope**: When/where it applies
3. **Specification**: What the rule requires/prohibits
4. **Examples**: Positive examples (do this)
5. **Anti-Examples**: Negative examples (don't do this)
6. **Verification**: How to check compliance
7. **Exceptions**: When it's okay to break this rule
8. **References**: Links to ADRs, docs, code

**Key questions**:
- Which sections are mandatory vs optional?
- What's the optimal length per rule? (100 words? 500 words? 2000 words?)
- Do agents perform better with terse rules or detailed rules?

**Look for**:
- Templates used by teams
- Rule length distributions
- Agent performance correlation studies

---

### Category 4: Rule Organization and Taxonomy

**Q4.1**: How are teams organizing large rule sets?

**Investigate**:

1. **Flat structure**: All rules in one file (`.cursorrules`)
2. **Directory-based**: Rules organized by category (`.cursor/rules/architecture/`, `/patterns/`, `/conventions/`)
3. **Hierarchical**: Parent rules → child rules (inheritance)
4. **Tag-based**: Rules tagged, tools filter by tag
5. **Context-based**: Rules activated by file path or git branch

**Look for**:
- Examples of repos with 50+ rules (how organized?)
- IDE support for rule directories
- Performance implications (loading time for agents)

---

**Q4.2**: What categorization schemes are effective?

**Investigate taxonomies**:

1. **By type**:
   - Architecture rules
   - Pattern rules
   - Convention rules
   - Domain rules
   - Quality rules

2. **By layer** (Clean Architecture):
   - Domain layer rules
   - Application layer rules
   - Infrastructure layer rules
   - Presentation layer rules

3. **By severity**:
   - Must follow (breaking changes)
   - Should follow (strong preference)
   - May follow (suggestions)

4. **By lifecycle**:
   - Permanent rules
   - Migration rules (temporary)
   - Experimental rules (trial period)

5. **By technology**:
   - TypeScript rules
   - React rules
   - Database rules
   - API rules

**Look for**:
- Most common taxonomies in practice
- Multi-dimensional categorization (e.g., type + severity)
- Impact on rule discoverability

---

**Q4.3**: How are teams handling rule conflicts and precedence?

**Investigate**:

- **Precedence rules**: Specific overrides general? File-level overrides project-level?
- **Conflict detection**: Tools that flag contradictory rules?
- **Resolution mechanisms**: Last-defined wins? Priority-based? Human decision?
- **Deprecation strategies**: How to phase out old rules?

**Look for**:
- Examples of conflicting rules
- Conflict resolution algorithms
- IDE warnings for conflicts

---

### Category 5: IDE and Agent Integration

**Q5.1**: How are different IDEs/agents consuming rules?

**Investigate**:

1. **Cursor**:
   - `.cursorrules` (single file, plain text)
   - `.cursor/rules/*.mdc` (multiple files, markdown)
   - Context window management
   - Rule prioritization

2. **GitHub Copilot**:
   - `.github/copilot-instructions.md`
   - Comments-based hints
   - Workspace context

3. **Codeium**:
   - `.codeium/` directory
   - JSON configurations
   - Team knowledge learning

4. **VS Code + extensions**:
   - `.vscode/settings.json` (prompt snippets)
   - Custom prompts
   - Inline hints

5. **JetBrains AI Assistant**:
   - `.idea/` configurations
   - Context actions

**Look for**:
- Official documentation of rule formats
- Undocumented capabilities (community discoveries)
- Feature support matrices
- Performance characteristics (rule count limits)

---

**Q5.2**: What are the context window limitations and strategies?

**Investigate**:

- **Context window sizes**: Cursor (200K), Copilot (?), others
- **Rule compression techniques**: Summaries, embeddings
- **Selective rule loading**: Only load relevant rules per file/context
- **Rule caching**: How agents cache rules to avoid reloading

**Key questions**:
- At what rule count does performance degrade?
- Do teams use RAG (Retrieval-Augmented Generation) for rules?
- How do teams prioritize which rules to include in context?

**Look for**:
- Performance benchmarks
- Best practices from tool vendors
- Community discussions on limits

---

**Q5.3**: How are teams measuring agent comprehension of rules?

**Investigate metrics**:

1. **Adherence rate**: % of AI-generated code following rules
2. **Violation detection**: Automated checks post-generation
3. **Code review rejection rate**: AI code rejected for rule violations
4. **A/B testing**: Code quality with rules vs without
5. **Agent explanations**: Can agent explain why it followed a rule?

**Look for**:
- Tools that measure rule adherence
- Case studies with before/after metrics
- Correlation between rule characteristics and adherence

---

### Category 6: Maintenance and Evolution

**Q6.1**: How are teams keeping rules current as codebases evolve?

**Investigate**:

- **CI/CD integration**: Validate rules on every commit
- **Periodic audits**: Quarterly review of all rules
- **Event-driven updates**: New architecture pattern → new rule
- **Feedback loops**: Code review comments → rule refinements
- **Automated staleness detection**: Flag rules with no violations in 6 months (maybe obsolete)

**Look for**:
- Automation scripts for rule validation
- Processes for rule deprecation
- Tools that detect rule "drift" (rule says X, codebase does Y)

---

**Q6.2**: What governance processes exist for rule changes?

**Investigate**:

- **Ownership**: Who can create/modify/delete rules? (architects, tech leads, anyone)
- **Approval processes**: PR review for rules? Architecture review board?
- **Change impact analysis**: How to assess impact of rule changes?
- **Version control**: Git for rules? Semantic versioning?
- **Communication**: How to announce new/changed rules to team?

**Look for**:
- CODEOWNERS for rule files
- ADRs about rule governance
- Changelogs for rule sets

---

**Q6.3**: How are teams handling rule retirement?

**Investigate**:

- **Deprecation markers**: Metadata flag + sunset date
- **Migration guides**: "Old rule X is now rule Y"
- **Grace periods**: Warning period before enforcement
- **Archival**: Where do retired rules go? (for historical context)

**Look for**:
- Examples of deprecated rules
- Processes for safe rule removal
- Tools that detect unused rules

---

### Category 7: Validation and Quality Assurance

**Q7.1**: How are teams validating rule quality before deployment?

**Investigate**:

1. **Automated validation**:
   - Schema validation (YAML/JSON correctness)
   - Example code validation (do examples compile/run?)
   - Conflict detection (contradicts existing rule?)
   - Coverage analysis (does rule apply to any code?)

2. **Human validation**:
   - Peer review process
   - Architecture board approval
   - Trial period with subset of team
   - A/B testing (rule vs no rule)

3. **Agent testing**:
   - Synthetic tasks for agent (follow this rule)
   - Measure agent performance with/without rule
   - Check for confusion (does rule make agent worse?)

**Look for**:
- Validation scripts in public repos
- Quality gates for rules
- Testing frameworks for rules

---

**Q7.2**: What anti-patterns are teams avoiding?

**Investigate**:

- **Over-specification**: Rules too detailed, agent has no flexibility
- **Under-specification**: Rules too vague, agent confused
- **Conflicting rules**: Rule A contradicts Rule B
- **Obsolete rules**: Rule describes old architecture
- **Unmaintained rules**: Rules bitrot, never updated
- **Copy-paste rules**: Rules copied from another project without adaptation
- **Optimization-only rules**: Rules for micro-optimizations, ignored
- **Inconsistent formatting**: Rules in different styles, hard to parse

**Look for**:
- Blog posts about "rule mistakes we made"
- Discussions on Reddit/HN about rule problems
- Examples of bad rules (with explanations)

---

**Q7.3**: How are teams measuring rule effectiveness?

**Investigate metrics**:

1. **Direct metrics**:
   - Rule adherence rate (% of code following rule)
   - Violation detection rate (how often rule catches issues)
   - False positive rate (rule flags correct code)

2. **Indirect metrics**:
   - Code quality improvements (fewer bugs, better maintainability)
   - Developer productivity (faster feature delivery)
   - Onboarding time (new devs + AI agents)
   - Code review cycle time (less back-and-forth)

3. **Agent-specific metrics**:
   - AI-generated code acceptance rate
   - Reduction in "off-pattern" code generation
   - Developer satisfaction with AI outputs

**Look for**:
- Case studies with quantitative results
- Metrics dashboards (screenshots, demos)
- Correlation studies (rule count vs code quality)

---

### Category 8: Emerging Patterns and Tools

**Q8.1**: Are there emerging standards for rule definition?

**Investigate**:

- **OpenAI ".openai-rules"**: Any standardization efforts?
- **YAML schemas**: Common schema for cross-tool compatibility?
- **Rule interchange formats**: Can rules be shared across IDEs?
- **Rule marketplaces**: Repositories of common rules (like ESLint configs)?

**Look for**:
- Standards body initiatives (W3C, OASIS, etc.)
- Open source "awesome" lists (awesome-cursor-rules)
- Tool vendor collaborations

---

**Q8.2**: What tools are leading teams using?

**Research tool categories**:

1. **Rule generators**:
   - AI-powered (GPT-4 + codebase → rules)
   - Static analysis based (SonarQube → rules)
   - Pattern miners (custom AST analyzers)

2. **Rule validators**:
   - Schema validators (YAML linters)
   - Conflict detectors (rule contradiction checkers)
   - Coverage analyzers (which code is ruled vs unruled)

3. **Rule managers**:
   - Version control integrations
   - Dashboards (rule usage, effectiveness)
   - Deprecation trackers

4. **IDE integrations**:
   - Cursor (native .cursorrules support)
   - VS Code extensions (copilot-instructions)
   - JetBrains plugins

**Look for**:
- Open source tools on GitHub
- Commercial solutions with free tiers
- Custom in-house tools (conference talks)

---

**Q8.3**: What novel approaches are emerging?

**Investigate**:

1. **Knowledge graphs**: Rules as nodes, relationships as edges
2. **Embedding-based retrieval**: Find relevant rules via semantic search
3. **Active learning**: Agent proposes rules based on patterns it finds
4. **Federated rules**: Rules shared across projects/teams
5. **Dynamic rules**: Rules that adapt based on context (file type, git branch)
6. **Multi-agent systems**: Specialist agents for different rule categories

**Look for**:
- Research papers (arXiv, ACM)
- Experimental projects on GitHub
- Vendor roadmaps (future features)

---

### Category 9: Company-Specific Case Studies

**Q9.1**: What are specific companies doing?

**Companies to research** (if public information available):

- **GitHub** (Copilot instructions format)
- **Cursor** (Anysphere team's own .cursorrules)
- **Anthropic** (internal code generation guidelines)
- **OpenAI** (GPT-4 code interpreter rules)
- **Vercel** (Next.js codebase rules for AI)
- **Supabase** (open source project with AI guidelines)
- **Linear** (engineering excellence + AI tools)
- **Replit** (Ghostwriter AI rules)
- **Sourcegraph** (Cody AI rules)
- **HashiCorp** (Terraform + AI generation)

**Look for**:
- Public repositories with rule files
- Engineering blog posts about rule adoption
- Conference talks from engineering teams
- Open source projects "dogfooding" their own tools

---

**Q9.2**: What are startups/scale-ups reporting?

**Look for**:
- Y Combinator companies using Cursor/Copilot
- Indie hackers blogging about AI coding workflows
- DevOps/Platform engineering communities (practitionerX, Platformers)
- Reddit (r/Cursor, r/ExperiencedDevs, r/MachineLearning)
- Hacker News discussions ("Ask HN: How do you manage .cursorrules?")
- Twitter/X threads from practitioners (cursor-rules hashtag)

**Key signals**:
- Real-world pain points and solutions
- Tools abandoned vs adopted
- Evolution of practices over time (what worked, what didn't)

---

## Research Sources

### Primary Sources (Highest Value)

1. **Public Repositories with Rule Files**:
   - GitHub search: `filename:.cursorrules OR path:.cursor/rules`
   - GitHub search: `filename:copilot-instructions.md`
   - Look for: Large projects (1000+ stars) with active AI usage

2. **Tool Documentation**:
   - Cursor official docs
   - GitHub Copilot docs
   - Codeium docs
   - VS Code Copilot extension docs
   - JetBrains AI Assistant docs

3. **Company Engineering Blogs**:
   - github.blog/engineering, cursor.com/blog, vercel.com/blog
   - Search for: "AI coding", "code generation", "developer productivity"

4. **Conference Talks (2024-2026)**:
   - GitHub Universe, Cursor meetups, QCon, GOTO
   - YouTube/InfoQ search: "cursor rules", "copilot instructions", "AI coding workflow"

5. **Developer Communities**:
   - Reddit: r/Cursor, r/ExperiencedDevs, r/CodingWithAI
   - Discord: Cursor community, Copilot users
   - Hacker News: "cursorrules", "AI coding"

### Secondary Sources

6. **Research Papers (arXiv, ACM, IEEE)**:
   - Keywords: "code generation rules", "LLM guardrails", "coding assistant alignment"
   - Focus on: empirical studies with metrics

7. **Podcasts/Interviews**:
   - Software Engineering Daily, Changelog, Lex Fridman (AI coding episodes)
   - Interviews with Cursor founders, Copilot team, etc.

8. **Books (Recent)**:
   - "AI-Assisted Programming" (if published)
   - "Engineering with AI" chapters on code generation

9. **Open Source Rule Collections**:
   - GitHub topics: "cursorrules", "copilot-instructions"
   - "awesome-cursor-rules" lists (if they exist)

---

## Analysis Framework

For each practice/tool/pattern discovered, evaluate:

### Adoption Signals
- [ ] **Evidence Level**: Anecdotal / Single case study / Multiple case studies / Industry standard
- [ ] **Maturity**: Experimental / Production use / Widely adopted
- [ ] **Tool Support**: Cursor only / Multiple IDEs / IDE-agnostic
- [ ] **Integration Complexity**: Trivial / Moderate / Significant

### Effectiveness Indicators
- [ ] **Quantitative Results**: Metrics reported (adherence rate, quality improvement, etc.)
- [ ] **Qualitative Feedback**: Developer satisfaction, agent accuracy, maintenance burden
- [ ] **Sustainability**: How maintained over time (stale rules a problem?)
- [ ] **Scalability**: Works for rule sets of what size (10 rules? 100? 1000?)

### RaiSE Applicability
- [ ] **Alignment with raise.rules.generate**: High / Medium / Low
- [ ] **Effort to Adopt**: Low / Medium / High
- [ ] **Value Proposition**: Clear improvement over current approach
- [ ] **Multi-Stack Support**: Language/framework agnostic or specific

---

## Synthesis Requirements

### Deliverable 1: Landscape Report

**Format**: Markdown document (~6-10K words)

**Structure**:
```markdown
# Code Generation Rules: State of Practice 2026

## Executive Summary
- Key findings (3-5 bullets)
- Paradigm shifts observed
- Gaps in current RaiSE approach

## 1. Rule Definition Methodologies
- Types of rules (with examples)
- Inclusion/exclusion criteria
- Granularity spectrum
- Real-world examples from top teams

## 2. Rule Extraction Techniques
- Manual curation approaches
- Semi-automated approaches (tools + examples)
- Fully automated approaches (tools + examples)
- Evidence requirements observed

## 3. Rule Format and Structure
- File formats in use (Markdown, JSON, YAML, etc.)
- Metadata schemas (with examples)
- Content structure patterns
- Length and complexity analysis

## 4. Rule Organization and Taxonomy
- Organization strategies (flat, hierarchical, tag-based)
- Categorization schemes
- Conflict resolution mechanisms
- Precedence rules

## 5. IDE and Agent Integration
- Per-IDE consumption patterns
- Context window strategies
- Agent comprehension measurement
- Performance characteristics

## 6. Maintenance and Evolution
- Update strategies
- Governance processes
- Retirement/deprecation approaches
- Observed failure modes

## 7. Validation and Quality Assurance
- Validation approaches (automated + human)
- Anti-patterns to avoid (with examples)
- Effectiveness metrics
- A/B testing results

## 8. Emerging Patterns and Tools
- Novel approaches (knowledge graphs, embeddings, etc.)
- Tool landscape (generators, validators, managers)
- Standards initiatives
- Future directions

## 9. Case Studies
- Company A: [Approach + Results + Lessons]
- Company B: [Approach + Results + Lessons]
- Open Source Project C: [Approach + Results + Lessons]
- ...

## 10. Comparison with RaiSE raise.rules.generate
- Current strengths to preserve
- Gaps identified (e.g., missing Katas L2-01, L2-03)
- Opportunities for improvement
- Alignment with RaiSE principles

## 11. The "Goldilocks Zone" for Rules
- Optimal quantity (how many rules is "just right"?)
- Optimal granularity (how specific should rules be?)
- Optimal length (how detailed per rule?)
- Optimal structure (what sections are essential?)

## References
[Categorized by source type]
```

---

### Deliverable 2: Actionable Recommendations

**Format**: Markdown document with decision matrix

**Structure**:
```markdown
# Recommendations for raise.rules.generate Improvement

## Quick Wins (High Impact, Low Effort)

| Recommendation | Impact | Effort | Priority | Source |
|----------------|--------|--------|----------|--------|
| [REC-001] Standardize .mdc frontmatter metadata | High | Low | P0 | [Multiple sources] |
| [REC-002] Create Kata L2-01 (Exploratory Pattern Analysis) | High | Low | P0 | [Gap identified] |
| [REC-003] Add duplicate detection before rule creation | Medium | Low | P1 | [Best practice] |
| ... | | | | |

## Strategic Improvements (High Impact, High Effort)

| Recommendation | Impact | Effort | Priority | Timeline |
|----------------|--------|--------|----------|----------|
| [REC-010] Implement automated pattern mining from codebase | High | High | P1 | Q2 2026 |
| [REC-011] Build rule effectiveness dashboard | Medium | High | P2 | Q3 2026 |
| ... | | | | |

## Experimental Additions (Uncertain Impact, Low-Medium Effort)

| Recommendation | Potential Impact | Effort | Priority | Validation Needed |
|----------------|------------------|--------|----------|-------------------|
| [REC-020] Explore knowledge graph for rule relationships | Medium | Medium | P2 | Pilot study |
| [REC-021] Test embedding-based rule retrieval | Medium | Low | P2 | A/B test |
| ... | | | | |

---

## Per Recommendation Detail

### REC-001: Standardize .mdc Frontmatter Metadata

**Current State**: `.mdc` files have inconsistent frontmatter.

**Proposed State**: Standardized schema with required + optional fields:

​```yaml
---
# Required fields
id: "[category]-[number]-[short-name]"
category: "[architecture|pattern|convention|domain|quality|meta]"
priority: "[P0|P1|P2]"
version: "1.0.0"

# Optional but recommended
scope: ["glob/pattern/**/*.ts"]
enforcement: "[cursor-ai|manual|automated-check]"
created: "YYYY-MM-DD"
author: "[name or team]"
rationale_link: "[path to ADR or analysis doc]"
examples: "[path to example files]"
deprecated: false
deprecated_by: "[rule-id if replaced]"
tags: ["tag1", "tag2"]
---
​```

**Benefit**:
- Enables automated rule management tools
- Facilitates rule discovery and filtering
- Supports governance (ownership, versioning)
- Improves agent parsing

**Implementation**:
1. Define canonical schema (JSON Schema or similar)
2. Update existing .mdc files to match schema
3. Create validation script for CI/CD
4. Update raise.rules.generate to generate compliant frontmatter

**Risk**: Low - additive change, improves existing

**Evidence Source**: [Cursor community best practices, Vercel rules, etc.]

---

### REC-002: Create Kata L2-01 (Exploratory Pattern Analysis)

**Current State**: `raise.rules.generate` references "Kata L2-01" but it doesn't exist.

**Proposed State**: Create missing Kata with structure:

​```markdown
---
id: flujo-L2-01-exploratory-pattern-analysis
nivel: flujo
titulo: "Exploratory Pattern Analysis for Rule Extraction"
audience: intermediate
template_asociado: null
validation_gate: null
prerequisites: [raise.1.analyze.code completed]
tags: [pattern-mining, rule-generation, brownfield]
version: 1.0.0
---

## Propósito
Guide AI agents through systematic exploration of a codebase to identify recurring patterns suitable for rule formalization.

## Pasos

### 1. Analyze SAR Reports
- Load all SAR reports from raise.1.analyze.code
- Identify patterns mentioned in:
  - informe-analisis-codigo-limpio.md (Clean Code patterns)
  - informe-analisis-arquitectura-limpia.md (architecture patterns)
- **Verificación**: At least 3 patterns identified
- > **Si no puedes continuar**: SAR reports incomplete → Re-run raise.1.analyze.code

### 2. Mine Codebase for Pattern Frequency
- For each identified pattern, scan codebase for instances
- Collect 3-5 positive examples (correct usage)
- Collect 2 counter-examples (violations or anti-patterns)
- **Verificación**: Each pattern has sufficient examples
- > **Si no puedes continuar**: Pattern too rare (<3 instances) → Discard, not rule-worthy

### 3. Document Pattern Candidates
- For each pattern, create analysis document in specs/main/analysis/patterns/
- Include: description, examples, frequency, criticality assessment
- **Verificación**: Analysis document generated per pattern
- > **Si no puedes continuar**: Ambiguous pattern → Request human clarification

### 4. Prioritize Patterns for Rule Creation
- Rank patterns by: frequency, criticality, clarity
- Select top 1-3 patterns for immediate rule generation
- **Verificación**: Prioritized list exists
- > **Si no puedes continuar**: No clear priorities → Defer to Kata L2-03

## Output
- Pattern analysis documents (specs/main/analysis/patterns/*.md)
- Prioritized list of patterns for rule generation

## Validation Gate
N/A (exploratory phase)

## Referencias
- raise.rules.generate command
- RaiSE glosario: "Guardrail"
​```

**Benefit**:
- Resolves broken reference in raise.rules.generate
- Provides explicit workflow for pattern mining
- Improves reproducibility

**Implementation**:
1. Write Kata L2-01 following RaiSE Kata structure v2.1
2. Write Kata L2-03 (Iterative Rule Extraction) similarly
3. Update raise.rules.generate to reference new Katas
4. Add Katas to docs/framework/v2.1/katas/

**Risk**: Low - fills existing gap

**Evidence Source**: RaiSE architectural analysis, gap identification

---

[... repeat for each recommendation]
```

---

### Deliverable 3: Rule Quality Framework

**Format**: Markdown document with checklists and templates

**Structure**:
```markdown
# Rule Quality Framework for raise.rules.generate

## Rule Inclusion Criteria (Checklist)

Before creating a rule, verify:

- [ ] **Frequency**: Pattern appears in 3+ locations in codebase
- [ ] **Criticality**: Violation causes bugs, security issues, or significant maintainability problems
- [ ] **Clarity**: Pattern can be described unambiguously
- [ ] **Evidence**: 3-5 positive examples + 2 counter-examples exist
- [ ] **Enforcement**: Can be checked (manually or automatically)
- [ ] **Scope**: Clear boundaries (what's in scope, what's not)
- [ ] **Non-Redundancy**: Not already covered by existing rule
- [ ] **Stability**: Pattern stable for 2+ months (not experimental)

## Rule Structure Template

​```yaml
---
id: "[category]-[number]-[short-name]"
category: "[architecture|pattern|convention|domain|quality|meta]"
priority: "[P0|P1|P2]"
version: "1.0.0"
scope: ["glob/pattern/**/*.ext"]
enforcement: "[cursor-ai|manual|automated-check]"
created: "YYYY-MM-DD"
rationale_link: "specs/main/analysis/rules/analysis-for-[name].md"
examples: "src/examples/[category]/[name]/"
---

# Rule: [Short Descriptive Title]

## Purpose

[1-2 sentences: Why this rule exists, what problem it solves]

## Context

[When this rule applies, scope boundaries, exceptions]

## Specification

### Do This

[Clear, actionable prescription with example]

​```typescript
// Example of correct pattern
[code snippet]
​```

### Don't Do This

[Clear prohibition with counter-example]

​```typescript
// Example of anti-pattern
[code snippet]
​```

## Verification

[How to check if code follows this rule]

## Rationale

[Deeper explanation: architectural reasons, historical context, trade-offs]

See analysis document: [link to specs/main/analysis/rules/analysis-for-[name].md]

## References

- ADR: [if applicable]
- Code examples: [file paths]
- External docs: [if applicable]
​```

## Rule Quality Gates

### Gate 1: Validation (Pre-Creation)

Run before generating .mdc file:

​```bash
.specify/scripts/bash/validate-rule-candidate.sh \
  --pattern "repository-pattern" \
  --examples "src/repos/UserRepository.ts, src/repos/OrderRepository.ts" \
  --counter-examples "src/services/UserService.ts (direct DB access)"
​```

Checks:
- [ ] Sufficient examples exist
- [ ] Pattern frequency > threshold
- [ ] No duplicate rule exists
- [ ] Scope clearly defined

### Gate 2: Quality (Post-Creation)

Run after generating .mdc file:

​```bash
.specify/scripts/bash/validate-rule-quality.sh \
  --rule-file ".cursor/rules/100-repository-pattern.mdc"
​```

Checks:
- [ ] Frontmatter schema valid
- [ ] Required sections present
- [ ] Examples compile/run (if applicable)
- [ ] Links resolve (to analysis doc, ADRs)
- [ ] No conflicts with existing rules

### Gate 3: Effectiveness (Post-Deployment)

After 2 weeks of use:

​```bash
.specify/scripts/bash/measure-rule-effectiveness.sh \
  --rule-id "100-repository-pattern" \
  --since "2026-01-01"
​```

Measures:
- [ ] Adherence rate (% of new code following rule)
- [ ] Violation detection (how many caught in code review)
- [ ] False positives (rule flagged correct code)
- [ ] Developer feedback (survey or comments)

If adherence < 60% or false positives > 20%, trigger rule review.

---

## Rule Maintenance Procedures

### Quarterly Audit

Every 3 months:

1. **Staleness Detection**:
   ​```bash
   .specify/scripts/bash/detect-stale-rules.sh
   ​```
   Flags rules with:
   - Zero violations in 6 months (maybe obsolete)
   - Outdated examples (files moved/deleted)
   - Broken links

2. **Conflict Detection**:
   ​```bash
   .specify/scripts/bash/detect-rule-conflicts.sh
   ​```
   Flags rules with:
   - Contradictory specifications
   - Overlapping scopes with different guidance

3. **Coverage Analysis**:
   ​```bash
   .specify/scripts/bash/analyze-rule-coverage.sh
   ​```
   Reports:
   - % of codebase covered by rules
   - Uncovered areas (new patterns emerging?)
   - Over-covered areas (too many rules?)

### Rule Deprecation Process

When deprecating a rule:

1. Update frontmatter:
   ​```yaml
   deprecated: true
   deprecated_date: "YYYY-MM-DD"
   deprecated_reason: "[Brief explanation]"
   deprecated_by: "[replacement-rule-id or null]"
   ​```

2. Add deprecation notice to rule body:
   ​```markdown
   > **⚠️ DEPRECATED**: This rule is deprecated as of YYYY-MM-DD.
   > Reason: [explanation]
   > Replacement: See rule [ID] for updated guidance.
   ​```

3. Move to `.cursor/rules/deprecated/` after 1 month grace period

4. Update governance registry (specs/main/ai-rules-reasoning.md)

---

## Anti-Patterns to Avoid

### AP-001: Rule Explosion

**Symptom**: 100+ rules, developers overwhelmed, agents confused.

**Prevention**:
- Set hard limit (e.g., 50 rules max for project <100K LOC)
- Consolidate related rules
- Remove low-value rules (those with <60% adherence and low criticality)

### AP-002: Over-Specification

**Symptom**: Rules dictate exact implementation, agent has no flexibility.

**Example**:
​```markdown
# BAD: Too prescriptive
All functions must be exactly 10-15 lines.
Variable names must follow pattern: [type][PascalCase][Suffix].
​```

**Prevention**:
- Focus on "what" and "why", not "how" (unless critical)
- Allow agent judgment on implementation details

### AP-003: Under-Specification

**Symptom**: Rules too vague, agent interprets differently each time.

**Example**:
​```markdown
# BAD: Too vague
Code should be clean.
Follow SOLID principles.
​```

**Prevention**:
- Always include concrete examples
- Specify clear boundaries

### AP-004: Stale Rules

**Symptom**: Rules describe old architecture, agent generates outdated code.

**Prevention**:
- Version rules (use semver)
- Automated staleness detection
- Quarterly audits

### AP-005: Conflicting Rules

**Symptom**: Rule A says "do X", Rule B says "don't do X", agent confused.

**Prevention**:
- Conflict detection in CI/CD
- Clear precedence hierarchy (specific > general)
- Explicit exceptions in rules

---

## Rule Effectiveness Metrics

### Primary Metrics

1. **Adherence Rate**:
   ```
   Adherence % = (Lines of code following rule / Total lines in scope) × 100
   ```
   Target: >80% for P0 rules, >60% for P1 rules

2. **Violation Detection Rate**:
   ```
   Detection % = (Violations caught / Total violations) × 100
   ```
   Target: >90% for automated checks, >70% for manual checks

3. **False Positive Rate**:
   ```
   FP % = (False positives / Total rule invocations) × 100
   ```
   Target: <10%

### Secondary Metrics

4. **Code Quality Impact**:
   - Bug rate in ruled code vs unruled code
   - Maintainability index change
   - Technical debt reduction

5. **Developer Productivity**:
   - Time saved in code review (fewer rule-violation comments)
   - Onboarding time for new developers
   - AI-generated code acceptance rate

6. **Agent Performance**:
   - % of AI code passing code review
   - Reduction in off-pattern code generation
   - Developer satisfaction with AI outputs (survey)

---

## Example Rule (Fully Annotated)

[Include a complete, exemplary rule following all best practices]

---

## References

- RaiSE Constitution § [relevant sections]
- RaiSE Glosario: "Guardrail"
- Industry research: [links to case studies]
- Tool documentation: [Cursor, Copilot, etc.]
```

---

### Deliverable 4: Prototype Artifacts (Optional)

If particularly promising patterns are found, create:

1. **Enhanced .mdc Template**:
   - Incorporating all recommended metadata
   - With structured sections
   - Example: `.raise-kit/templates/raise/rules/rule-template-v2.md`

2. **Validation Scripts**:
   - `validate-rule-candidate.sh` (pre-creation checks)
   - `validate-rule-quality.sh` (post-creation checks)
   - `detect-stale-rules.sh` (maintenance)
   - `detect-rule-conflicts.sh` (quality assurance)
   - `measure-rule-effectiveness.sh` (metrics)

3. **Pattern Mining Tool** (if feasible):
   - Script using tree-sitter or similar
   - Scans codebase for recurring patterns
   - Outputs pattern candidates for human review

4. **Rule Dashboard** (if feasible):
   - Simple HTML page showing:
     - Total rules by category
     - Rule effectiveness metrics
     - Stale rules needing review
     - Recent rule changes

---

## Success Criteria

This research will be successful if it produces:

1. **Evidence-Based Insights**:
   - [ ] At least 5 real-world case studies with measurable outcomes
   - [ ] At least 10 public repositories with rule files analyzed
   - [ ] At least 15 distinct tools/approaches catalogued

2. **Actionable Recommendations**:
   - [ ] At least 3 "quick win" recommendations (high impact, low effort)
   - [ ] At least 2 "strategic" recommendations (high impact, high effort, clear ROI)
   - [ ] At least 1 recommendation addressing missing Katas (L2-01, L2-03)
   - [ ] Clear prioritization with effort estimates

3. **Novel Insights**:
   - [ ] At least 1 pattern/practice not currently in RaiSE
   - [ ] At least 1 anti-pattern to avoid (validated by practitioners)
   - [ ] Quantitative heuristics (e.g., "optimal rule count is 20-50 for 100K LOC codebases")

4. **RaiSE Alignment**:
   - [ ] Clear mapping to raise.rules.generate improvement opportunities
   - [ ] Compatibility with RaiSE ontology (Guardrails, not Rules)
   - [ ] Integration with Dual Traceability pattern (rule + analysis + registry)
   - [ ] Feasible within .raise-kit architecture

5. **Practical Deliverables**:
   - [ ] Updated .mdc template
   - [ ] Rule quality framework (checklists, gates)
   - [ ] At least 2 validation scripts (prototypes or specs)

---

## Timeline

**Week 1**:
- Days 1-2: Tool documentation research (Cursor, Copilot, Codeium, etc.)
- Day 3: Public repository analysis (search for .cursorrules, .cursor/rules/)
- Day 4: Company blog posts and conference talks
- Day 5: Initial synthesis

**Week 2**:
- Days 1-2: Deep dive on most promising approaches
- Day 3: Case study documentation
- Day 4: Recommendations formulation
- Day 5: Rule quality framework creation

**Week 3**:
- Days 1-2: Prototype artifacts (templates, scripts)
- Day 3: Report writing (landscape report)
- Day 4: Report writing (recommendations)
- Day 5: Final review and delivery

**Total**: ~12-15 working days for thorough research + synthesis + prototyping

---

## Output Location

**Deliverables saved to**:
```
specs/main/research/rule-extraction-alignment/
├── landscape-report.md              # Deliverable 1 (~6-10K words)
├── recommendations.md               # Deliverable 2 (~5-8K words)
├── rule-quality-framework.md        # Deliverable 3 (~4-6K words)
├── prototypes/                      # Deliverable 4 (optional)
│   ├── templates/
│   │   └── rule-template-v2.md
│   ├── scripts/
│   │   ├── validate-rule-candidate.sh
│   │   ├── validate-rule-quality.sh
│   │   ├── detect-stale-rules.sh
│   │   ├── detect-rule-conflicts.sh
│   │   └── measure-rule-effectiveness.sh
│   ├── examples/
│   │   └── exemplary-rule.mdc
│   └── dashboards/
│       └── rule-metrics.html
└── sources/
    ├── case-studies/                # Detailed notes per company
    ├── tools-reviewed/              # Notes per tool
    ├── repositories-analyzed/       # List of repos + findings
    └── papers-analyzed/             # Academic papers
```

---

## Meta: How to Use This Prompt

### For AI Research Agent

If executing this research with an AI agent:

1. **Read this prompt completely**
2. **Execute research questions sequentially** (Q1 → Q2 → ... → Q9)
3. **Document sources as you go** (save URLs, quotes, examples)
4. **Build evidence catalog** before synthesizing (don't synthesize prematurely)
5. **Apply analysis framework** to each finding (adoption, effectiveness, applicability)
6. **Generate deliverables** according to templates above
7. **Validate** against success criteria
8. **Iterate** if success criteria not met

### For Human Researcher

If executing manually:

1. **Allocate 2-3 hour blocks** for focused research
2. **Use parallel tabs** for broad initial sweep (open 10-20 promising sources)
3. **Take structured notes** (use analysis framework as template)
4. **Clone repos** with interesting rule files for local analysis
5. **Set time limits** on rabbit holes (30 min max per thread)
6. **Synthesize daily** (don't just accumulate sources without processing)
7. **Pair with practitioner** if possible (validate findings with someone using Cursor/Copilot daily)
8. **Use AI assistance** for synthesis (GPT-4/Claude to summarize findings, identify patterns)

---

## Related RaiSE Context

**Current system being improved**: `raise.rules.generate`

- Command: `.agent/workflows/01-onboarding/raise.rules.generate.md`
- Example rules: `.cursor/rules/100-kata-structure-v2.1.md`, `910-rule-management.mdc`
- Governance registry: `specs/main/ai-rules-reasoning.md`
- Architecture analysis: `specs/main/analysis/architecture/raise.rules.generate-architecture.md`

**Key Patterns to Preserve**:
- **Dual Traceability**: Rule + analysis document + registry entry
- **Iterative Generation**: 1-3 patterns per run (not batch)
- **Evidence-Based**: 3-5 positive examples + 2 counter-examples
- **Incremental Persistence**: Save after each rule (not batch at end)

**Known Gaps to Address**:
- **Missing Katas**: L2-01 (Exploratory Pattern Analysis) and L2-03 (Iterative Rule Extraction) referenced but don't exist
- **No Duplicate Detection**: No check if rule already exists before creation
- **No Registry Validation**: No check if registry entry successfully added
- **No Conflict Detection**: No check if new rule conflicts with existing rules
- **Limited Metadata**: Current .mdc files have minimal frontmatter

**RaiSE Principles to Honor**:
- **§2. Governance as Code**: Rules are versioned, traceable, auditable
- **§3. Evidence-Based**: Rules backed by real patterns in codebase
- **§4. Validation Gates**: Rules pass quality gates before deployment
- **§7. Lean (Jidoka)**: Stop if rule quality insufficient, correct before proceeding
- **§8. Observable Workflow**: Rule creation process is transparent and verifiable

**Adjacent RaiSE Commands**:
- `raise.1.analyze.code` (SAR generation) - input for pattern mining
- `raise.rules.edit` (rule modification) - lifecycle management
- `speckit.5.analyze` (quality gate) - could validate rules

---

**Research Start Date**: [YYYY-MM-DD]
**Research End Date**: [YYYY-MM-DD]
**Researcher**: [Name/Agent ID]
**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed

---

*This research prompt is part of the RaiSE Framework evolution (Feature 012: Raise Commands Research), aimed at improving rule generation and code generation alignment capabilities.*
