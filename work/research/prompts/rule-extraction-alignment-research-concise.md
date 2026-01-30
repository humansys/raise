# Deep Research: Rule Definition & Extraction for AI Code Generation Alignment

**Research ID**: RES-RULE-EXTRACT-ALIGN-001-CONCISE
**Date**: 2026-01-23
**Estimated Effort**: 3-5 hours research + 2-3 hours synthesis
**Goal**: Improve `raise.rules.generate` with industry best practices

---

## Core Question

**How do top engineering teams define, extract, structure, and maintain code generation rules to align AI agents (Cursor, Copilot, Codeium) with their codebases?**

Specifically:
- What quantity and granularity of rules is optimal?
- What formats and structures work best?
- How to extract rules from existing code?
- How to validate and measure effectiveness?

---

## Research Scope

### In Scope
- Rule definition methodologies (types, granularity, prioritization)
- Extraction techniques (manual, semi-automated, automated)
- Formats (.cursorrules, .mdc, JSON, YAML)
- IDE integration (Cursor, Copilot, Codeium, VS Code)
- Maintenance strategies (updates, validation, conflict resolution)
- Effectiveness metrics (adherence, quality impact)
- Real case studies with measurable outcomes

### Out of Scope
- General style guides without AI context
- Linter configs unless used for agent alignment
- Model fine-tuning or prompt engineering
- Non-code generation rules

---

## Key Research Questions

### 1. Rule Definition (What & How Much)

**Q1.1**: What types of rules are teams creating?
- Prohibitive ("never use X")
- Prescriptive ("always use Y for Z")
- Contextual ("in module M, use pattern P")
- Architecture, conventions, domain, anti-patterns

**Q1.2**: How do teams decide what becomes a rule?
- Frequency thresholds (appears 3+ times?)
- Criticality (prevents bugs/security issues?)
- Agent confusion signals (AI generates wrong patterns?)

**Q1.3**: What's the "Goldilocks zone"?
- Optimal rule count per codebase size
- Optimal granularity (project-wide vs module-specific)
- Optimal detail level per rule

**Look for**: Real examples, decision frameworks, blog posts about "too many rules"

---

### 2. Rule Extraction (Where Rules Come From)

**Q2.1**: How are teams extracting rules?
- Manual (developers document patterns)
- Semi-automated (AI proposes, humans curate)
- Fully automated (AST analysis, pattern mining)

**Q2.2**: What evidence validates a rule?
- Number of positive examples needed (RaiSE uses 3-5)
- Number of counter-examples (RaiSE uses 2)
- Quantitative thresholds (frequency in codebase)

**Q2.3**: What tools exist for rule extraction?
- AI-powered generators (GPT-4 + codebase)
- Static analysis tools (SonarQube, PMD)
- Pattern miners (custom scripts, tree-sitter)

**Look for**: Open source tools, custom solutions, hybrid workflows

---

### 3. Rule Format & Structure (How Rules Look)

**Q3.1**: What file formats are popular?
- Markdown (`.cursorrules`, `.mdc`)
- Structured (JSON, YAML)
- Hybrid (Markdown + YAML frontmatter)

**Q3.2**: What metadata do rules contain?
- Required: ID, category, priority, version
- Optional: scope (glob patterns), rationale links, evidence paths, created date
- Agent hints: LLM-specific guidance

**Q3.3**: What sections do rules have?
- Purpose, scope, specification (do/don't), examples, verification, rationale
- Typical length: 200-1000 words per rule

**Look for**: Real .cursorrules files, .mdc examples, metadata schemas

---

### 4. Organization & Taxonomy (How Rules Are Organized)

**Q4.1**: How are large rule sets organized?
- Flat (one file) vs directory-based (by category)
- Hierarchical (parent→child) vs tag-based

**Q4.2**: How are rules categorized?
- By type (architecture, pattern, convention)
- By layer (domain, application, infrastructure)
- By severity (must/should/may follow)

**Q4.3**: How are conflicts resolved?
- Precedence rules (specific > general)
- Conflict detection tools
- Deprecation strategies

**Look for**: Repos with 50+ rules, categorization schemes

---

### 5. IDE Integration (How Agents Use Rules)

**Q5.1**: How do IDEs consume rules?
- Cursor: `.cursorrules` or `.cursor/rules/*.mdc`
- GitHub Copilot: `.github/copilot-instructions.md`
- Codeium: `.codeium/` directory
- Context window limitations and strategies

**Q5.2**: How is agent comprehension measured?
- Adherence rate (% code following rules)
- Code review rejection rate
- A/B testing (with/without rules)

**Look for**: Tool documentation, performance benchmarks, community discussions

---

### 6. Maintenance & Validation (Keeping Rules Current)

**Q6.1**: How are rules kept current?
- CI/CD validation
- Periodic audits (quarterly)
- Automated staleness detection
- Feedback loops from code reviews

**Q6.2**: What validates rule quality?
- Automated: schema validation, conflict detection, example compilation
- Human: peer review, trial periods
- Agent testing: synthetic tasks, performance measurement

**Q6.3**: What anti-patterns should be avoided?
- Rule explosion (too many)
- Over-specification (too detailed)
- Under-specification (too vague)
- Stale rules (obsolete patterns)
- Conflicting rules

**Look for**: Validation scripts, quality gates, "lessons learned" posts

---

## Primary Research Sources

### High Priority
1. **Public repos with rule files**: GitHub search for `.cursorrules`, `.cursor/rules/`, `copilot-instructions.md` (analyze 10+ repos with 1000+ stars)
2. **Tool docs**: Cursor, GitHub Copilot, Codeium official documentation
3. **Company blogs**: github.blog, cursor.com/blog, vercel.com/blog (search "AI coding", "rules")
4. **Communities**: r/Cursor, r/ExperiencedDevs, Hacker News ("cursorrules", "AI coding")

### Medium Priority
5. **Conference talks**: GitHub Universe, Cursor meetups, QCon (YouTube/InfoQ)
6. **Case studies**: Companies using Cursor/Copilot at scale
7. **Open source projects**: Vercel, Supabase with AI guidelines
8. **Research papers**: arXiv/ACM (empirical studies only)

---

## Deliverables

### D1: Landscape Report (~4-6K words)

Structure:
```markdown
# Code Generation Rules: State of Practice 2026

## Executive Summary (3-5 bullets)

## 1. Rule Definition Practices
- Types and granularity observed
- Decision frameworks for rule inclusion
- "Goldilocks zone" findings (optimal quantity/detail)

## 2. Extraction Techniques & Tools
- Manual/semi-automated/automated approaches
- Evidence requirements
- Tool landscape (with examples)

## 3. Format, Structure & Organization
- Popular formats and metadata schemas
- Content structure patterns
- Organization strategies for large rule sets

## 4. IDE Integration & Effectiveness
- Per-IDE consumption patterns
- Measured outcomes (adherence rates, quality metrics)
- Context window strategies

## 5. Maintenance & Quality Assurance
- Update strategies and governance
- Validation approaches
- Anti-patterns to avoid

## 6. Case Studies (3-5 companies/projects)
- Company/Project: [Approach + Results + Lessons]

## 7. Comparison with RaiSE raise.rules.generate
- Strengths to preserve
- Gaps (missing Katas L2-01/L2-03)
- Improvement opportunities

## References (categorized)
```

---

### D2: Actionable Recommendations (~3-4K words)

Structure:
```markdown
# Recommendations for raise.rules.generate

## Quick Wins (High Impact, Low Effort)

| ID | Recommendation | Impact | Effort | Priority | Source |
|----|---------------|--------|--------|----------|--------|
| REC-001 | Standardize .mdc frontmatter | High | Low | P0 | [Multiple] |
| REC-002 | Create Kata L2-01 (Pattern Analysis) | High | Low | P0 | [Gap] |
| REC-003 | Add duplicate detection | Medium | Low | P1 | [Best practice] |

## Strategic Improvements (High Impact, High Effort)

| ID | Recommendation | Impact | Effort | Priority | Timeline |
|----|---------------|--------|--------|----------|----------|
| REC-010 | Automated pattern mining | High | High | P1 | Q2 2026 |
| REC-011 | Rule effectiveness dashboard | Medium | High | P2 | Q3 2026 |

## Detailed Recommendations

### REC-001: Standardize .mdc Frontmatter
**Current**: Inconsistent metadata
**Proposed**: Standard schema with required fields (id, category, priority, version) + optional (scope, enforcement, rationale_link)
**Benefit**: Enables automation, improves governance
**Implementation**: Define schema → update files → create validator
**Evidence**: [Sources]

### REC-002: Create Missing Kata L2-01
**Current**: raise.rules.generate references non-existent Kata
**Proposed**: Create "Exploratory Pattern Analysis" Kata with steps: analyze SAR → mine patterns → collect examples → prioritize
**Benefit**: Resolves broken reference, provides explicit workflow
**Implementation**: Write Kata following v2.1 structure → update command
**Evidence**: Architectural analysis gap

[... continue for each recommendation]
```

---

### D3: Rule Quality Framework (~2-3K words)

Structure:
```markdown
# Rule Quality Framework

## Rule Inclusion Checklist
- [ ] Frequency: Pattern in 3+ locations
- [ ] Criticality: Violation causes bugs/security/maintainability issues
- [ ] Clarity: Unambiguous description
- [ ] Evidence: 3-5 positive + 2 negative examples
- [ ] Scope: Clear boundaries
- [ ] Non-redundant: Not covered by existing rule
- [ ] Stable: Pattern established 2+ months

## Rule Template
[Standard structure with frontmatter + sections]

## Quality Gates
1. **Pre-creation**: Validate candidate (frequency, examples, no duplicates)
2. **Post-creation**: Validate quality (schema, sections, examples compile, no conflicts)
3. **Post-deployment**: Measure effectiveness (adherence >60%, false positives <20%)

## Effectiveness Metrics
- Adherence Rate: (Code following rule / Total in scope) × 100
- Detection Rate: (Violations caught / Total violations) × 100
- False Positive Rate: (FP / Total invocations) × 100

## Anti-Patterns
- AP-001: Rule explosion (100+ rules)
- AP-002: Over-specification (no agent flexibility)
- AP-003: Under-specification (too vague)
- AP-004: Stale rules (obsolete patterns)
- AP-005: Conflicting rules (contradictions)

## Maintenance Procedures
- Quarterly audit: staleness, conflicts, coverage
- Deprecation: flag in frontmatter → grace period → archive
```

---

### D4: Prototype Artifacts (Optional)

If time permits:
- Enhanced .mdc template with recommended metadata
- Validation script spec (validate-rule-candidate.sh)
- Example of exemplary rule following all best practices

---

## Success Criteria

- [ ] **5+ case studies** with measurable outcomes
- [ ] **10+ repos** analyzed for rule patterns
- [ ] **15+ tools** catalogued (generators, validators, managers)
- [ ] **3+ quick wins** identified
- [ ] **2+ strategic improvements** proposed
- [ ] **1+ novel insight** not in current RaiSE
- [ ] **Quantitative heuristics** (e.g., "20-50 rules optimal for 100K LOC")
- [ ] **Address Katas L2-01/L2-03** gap

---

## Output Location

```
specs/main/research/rule-extraction-alignment/
├── landscape-report.md           # D1
├── recommendations.md            # D2
├── rule-quality-framework.md     # D3
├── prototypes/                   # D4 (optional)
│   ├── rule-template-v2.md
│   └── exemplary-rule.mdc
└── sources/
    ├── case-studies/
    ├── repositories-analyzed/
    └── tools-reviewed/
```

---

## Execution Guidance

### For AI Agent

1. **Research phase** (2-3 hours):
   - Search GitHub for repos with `.cursorrules` (10+ repos, 1000+ stars)
   - Read tool documentation (Cursor, Copilot, Codeium)
   - Search company blogs and HN/Reddit for case studies
   - Build evidence catalog with URLs and quotes

2. **Analysis phase** (1 hour):
   - Identify patterns across sources
   - Extract quantitative findings (rule counts, metrics)
   - Note novel practices not in RaiSE

3. **Synthesis phase** (2-3 hours):
   - Write landscape report
   - Formulate recommendations (prioritize quick wins)
   - Create quality framework
   - Generate prototypes if feasible

4. **Validation**:
   - Check against success criteria
   - Ensure all deliverables created
   - Verify evidence citations

---

## RaiSE Context

**Improving**: `raise.rules.generate` command
**Current patterns**: Dual Traceability (rule + analysis + registry), Iterative Generation (1-3 patterns/run), Evidence-Based (3-5 positive + 2 negative examples)
**Known gaps**: Missing Katas L2-01/L2-03, no duplicate detection, limited metadata, no conflict detection
**Principles**: Governance as Code (§2), Evidence-Based (§3), Validation Gates (§4), Lean/Jidoka (§7)

---

**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed
**Researcher**: [Agent ID]
**Start**: [Date] | **End**: [Date]
