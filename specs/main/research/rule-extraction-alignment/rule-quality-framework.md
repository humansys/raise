# Rule Quality Framework for raise.rules.generate

**Research ID**: RES-RULE-EXTRACT-ALIGN-001
**Date**: 2026-01-23
**Authors**: Claude Sonnet 4.5 (Research Agent)
**Word Count**: ~5,200 words
**Purpose**: Comprehensive quality framework for creating, validating, and maintaining high-quality code generation rules

---

## Executive Summary

This framework establishes **quality standards and processes** for RaiSE's `raise.rules.generate` command, ensuring rules are:
- **Evidence-Based**: Backed by 3-5 positive examples + 2 counter-examples
- **Actionable**: Clear, unambiguous specifications that agents can follow
- **Maintainable**: Versioned, documented, with clear ownership and review cycles
- **Effective**: Measured via adherence rates, false positive rates, code quality impact

The framework defines **3 quality gates**:
1. **Gate 1: Pre-Creation Validation** - Check before generating rule (duplicates, evidence)
2. **Gate 2: Post-Creation Quality** - Check after generating rule (schema, completeness, conflicts)
3. **Gate 3: Post-Deployment Effectiveness** - Check after 2-4 weeks of use (adherence, FP rate)

**Target Metrics** (aligned with industry benchmarks):
- **Adherence Rate**: >80% for P0 rules, >60% for P1 rules
- **False Positive Rate**: <10%
- **Developer Acceptance**: 70%+ approval rate for new rules (Amazon CodeGuru benchmark)
- **Rule Count**: 20-50 focused rules per project (Goldilocks zone)

---

## 1. Rule Inclusion Criteria

Before creating a rule, **ALL** of these criteria must be met:

### 1.1 Required Criteria (Must Pass)

- [ ] **Frequency**: Pattern appears in **3+ locations** in codebase
  - **Rationale**: Infrequent patterns don't justify rule overhead
  - **Exception**: Security vulnerabilities (even 1 occurrence warrants rule)
  - **Measurement**: Grep, AST analysis, or manual code review

- [ ] **Criticality**: Violation causes **bugs, security issues, or significant maintainability problems**
  - **Rationale**: Rules should prevent real problems, not enforce personal preferences
  - **Assessment**: High (causes bugs/security issues), Medium (maintainability), Low (style)
  - **Minimum**: Medium criticality for P1 rules, High criticality for P0 rules

- [ ] **Clarity**: Pattern can be described **unambiguously**
  - **Rationale**: Vague rules confuse agents and developers
  - **Test**: Can you write a "Do This" and "Don't Do This" example without ambiguity?
  - **Red Flag**: If rule requires 5+ paragraphs to explain, it may be too complex

- [ ] **Evidence**: **3-5 positive examples + 2 counter-examples** exist in codebase
  - **Rationale**: Evidence-Based Claims (RaiSE §3)
  - **Positive Examples**: Real code demonstrating correct pattern (with file paths)
  - **Counter-Examples**: Real code violating pattern or anti-pattern (with file paths)
  - **Synthetic Examples**: OK if codebase lacks counter-examples (explain why)

- [ ] **Enforcement**: Compliance can be checked **(manually or automatically)**
  - **Rationale**: Unenforceable rules are ignored
  - **Manual**: Human reviewer can verify (e.g., "Use Repository pattern")
  - **Automated**: Linter, AST check, or custom script (e.g., "No direct DB calls outside repos")

- [ ] **Scope**: Clear boundaries **(what's in scope, what's not)**
  - **Rationale**: Ambiguous scope causes confusion ("Does this apply to test files?")
  - **Specification**: Use glob patterns (e.g., `src/domain/**/*.ts`)
  - **Edge Cases**: Document exceptions explicitly

- [ ] **Non-Redundancy**: Not already covered by **existing rule**
  - **Rationale**: Duplicate rules cause confusion and maintenance burden
  - **Check**: Run duplicate detection script (REC-003)
  - **Alternative**: Update existing rule instead of creating new one

- [ ] **Stability**: Pattern has been **stable for 2+ months** (not experimental)
  - **Rationale**: Rules for experimental patterns churn frequently
  - **Check**: Git history, team consensus
  - **Exception**: Temporal rules for migrations (explicitly marked as temporary)

### 1.2 Recommended Criteria (Should Pass)

- [ ] **Observability**: Violations are **easily detectable** in code review
  - If violations are subtle, rule needs better examples or verification guidance

- [ ] **Team Consensus**: **2+ engineers** agree pattern is worth codifying
  - Avoid "one person's preference" rules

- [ ] **Actionable**: Agent can apply rule **without additional context**
  - Test: Show rule to someone unfamiliar with codebase - can they apply it?

- [ ] **Positive ROI**: Time saved (consistency, fewer bugs) > Time spent (writing, maintaining rule)
  - For low-impact rules (P2), this is critical

### 1.3 Exclusion Criteria (Do Not Create Rule If)

- ❌ **Personal Preference**: Rule is stylistic without measurable impact (e.g., "I prefer X over Y")
- ❌ **Too Specific**: Rule applies to 1-2 files only (document in comments instead)
- ❌ **Too General**: Rule is common knowledge (e.g., "Write clean code")
- ❌ **Tool Overlap**: Rule is already enforced by linter/compiler (e.g., ESLint, TypeScript)
- ❌ **Unstable Pattern**: Pattern is experimental or frequently changes
- ❌ **Low Criticality + Low Frequency**: Pattern appears rarely and violations don't matter

---

## 2. Rule Structure Template

All rules **MUST** follow this structure for consistency and agent comprehension.

### 2.1 Frontmatter (YAML)

**Required Fields**:
```yaml
---
id: "[category]-[number]-[short-name]"           # e.g., "pattern-100-repository"
category: "[architecture|pattern|convention|domain|quality|security|meta]"
priority: "[P0|P1|P2]"                           # P0=must, P1=should, P2=may
version: "1.0.0"                                 # Semantic versioning (MAJOR.MINOR.PATCH)
---
```

**Recommended Fields**:
```yaml
scope: ["glob/pattern/**/*.ts"]                  # File paths this applies to
enforcement: "[cursor-ai|manual|automated-check]" # How enforced
created: "YYYY-MM-DD"                            # Creation date
author: "[name or team]"                         # Ownership
rationale_link: "[path to analysis doc]"         # Link to deeper explanation
examples: "[path to example files]"              # Link to code examples
```

**Optional Fields**:
```yaml
deprecated: false                                # Deprecation flag
deprecated_by: "[rule-id if replaced]"          # Replacement rule
deprecated_date: "YYYY-MM-DD"                   # When deprecated
tags: ["tag1", "tag2"]                          # Searchable tags
related_rules: ["rule-id-1", "rule-id-2"]       # Dependencies/related
evidence_count: 5                                # Number of examples found
frequency: "high"                                # Pattern frequency (high|medium|low)
stability_months: 6                              # How long pattern has existed
last_reviewed: "YYYY-MM-DD"                     # Last audit date
hierarchy_level: "layer"                        # global|layer|module|file-type|temporal
hierarchy_path: "infrastructure"                # Subpath within hierarchy level
```

### 2.2 Body Sections (Markdown)

**Required Sections**:

#### Section 1: Title
```markdown
# Rule: [Short Descriptive Title]

Example: "Use Repository Pattern for Database Access"
```

#### Section 2: Purpose
```markdown
## Purpose

[1-2 sentences: Why this rule exists, what problem it solves]

Example:
"Encapsulate database access logic in repository classes to enable testing, maintainability, and adherence to Clean Architecture principles."
```

#### Section 3: Context
```markdown
## Context

[When/where this rule applies, scope boundaries, exceptions]

Example:
"Applies to all code in `src/data/repositories/` that interacts with the database.

Does NOT apply to:
- Test files (mock repositories allowed)
- Database migration scripts
- One-off admin scripts"
```

#### Section 4: Specification

```markdown
## Specification

### Do This

[Clear, actionable prescription with example]

​```typescript
// Example of correct pattern
interface UserRepository {
  findById(id: string): Promise<User | null>
  create(data: CreateUserInput): Promise<User>
}

class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string) {
    return this.prisma.user.findUnique({ where: { id } })
  }
}
​```

### Don't Do This

[Clear prohibition with counter-example]

​```typescript
// BAD: Direct Prisma call in service layer
async function getUserProfile(id: string) {
  const user = await prisma.user.findUnique({ where: { id } })
  return user
}
​```

### Why This Matters

[Explanation of consequences if rule violated]

Example:
"Direct database calls in service layer tightly couple business logic to Prisma, making it impossible to test without a real database and difficult to switch ORMs later."
```

#### Section 5: Verification
```markdown
## Verification

[How to check if code follows this rule]

**Manual Check**:
- Search for `prisma.` calls outside `src/data/repositories/`
- Verify all services inject repositories via constructor

**Automated Check** (optional):
​```bash
# Grep for direct Prisma usage outside repositories
grep -r "prisma\." src/ --exclude-dir=repositories --exclude="*.test.ts"
​```

**Expected**: No results (exit code 1)
```

#### Section 6: Rationale
```markdown
## Rationale

[Deeper explanation: architectural reasons, historical context, trade-offs]

Example:
"This rule enforces the Repository pattern from Clean Architecture. Benefits:
1. **Testability**: Service layer can be tested with mock repositories
2. **Maintainability**: Database access logic centralized in one place
3. **Flexibility**: Easy to swap Prisma for another ORM

Trade-off: Adds one layer of indirection. Acceptable cost for improved testability and maintainability.

Historical Context: Adopted after incident #42 where tightly coupled database calls made refactoring impossible."

**See analysis document**: `specs/main/analysis/rules/analysis-for-repository-pattern.md`
```

#### Section 7: References
```markdown
## References

- **ADR**: `docs/decisions/adr-007-repository-pattern.md`
- **Code Examples**:
  - Good: `src/data/repositories/UserRepository.ts`
  - Bad: `src/services/UserService.ts` (lines 42-55, before refactor)
- **External Resources**:
  - Clean Architecture by Robert C. Martin (Chapter 22)
  - [Repository Pattern Explained](https://martinfowler.com/eaaCatalog/repository.html)
```

### 2.3 Example: Complete Rule

**See Appendix A** for a fully annotated example rule following all best practices.

---

## 3. Quality Gates

Rules pass through **3 quality gates** to ensure high standards.

### Gate 1: Pre-Creation Validation

**When**: Before generating .mdc file
**Script**: `.specify/scripts/bash/validate-rule-candidate.sh`
**Purpose**: Prevent bad rules from being created

**Checks**:

- [ ] **Sufficient Evidence**: 3-5 positive examples + 2 counter-examples provided
  - **How**: Parse pattern analysis document, count examples
  - **Fail If**: <3 positive or <2 counter-examples (unless justified)

- [ ] **Frequency Threshold**: Pattern appears 3+ times in codebase
  - **How**: Grep, AST query, or manual count
  - **Fail If**: <3 occurrences (unless security issue)

- [ ] **No Duplicates**: Similar rule doesn't already exist
  - **How**: Run duplicate detection script (REC-003)
  - **Fail If**: Filename similarity, keyword overlap in existing rules
  - **Action**: Prompt user to update existing rule or justify new rule

- [ ] **Scope Defined**: Glob pattern or scope description provided
  - **How**: Check pattern analysis document
  - **Fail If**: Scope missing or ambiguous ("applies to some files")

- [ ] **Criticality Assessed**: High/Medium/Low rating with justification
  - **How**: Check pattern analysis document
  - **Fail If**: Criticality missing or unjustified

**Exit Codes**:
- `0`: Pass (proceed to rule generation)
- `1`: Fail (do not generate rule, fix issues)
- `2`: Warning (user decision required)

**Usage**:
```bash
.specify/scripts/bash/validate-rule-candidate.sh \
  --pattern "repository-pattern" \
  --analysis-doc "specs/main/analysis/patterns/pattern-repository.md"

# Output:
✓ Sufficient evidence (5 positive, 2 negative examples)
✓ Frequency threshold met (12 occurrences)
✓ No duplicates found
✓ Scope defined (src/data/repositories/**/*.ts)
✓ Criticality assessed (High)
PASS: Rule candidate is valid
```

---

### Gate 2: Post-Creation Quality

**When**: After generating .mdc file, before registry update
**Script**: `.specify/scripts/bash/validate-rule-quality.sh`
**Purpose**: Ensure generated rule meets structural and content standards

**Checks**:

- [ ] **Frontmatter Schema Valid**: All required fields present, correct format
  - **Required**: id, category, priority, version
  - **Recommended**: scope, enforcement, created, author, rationale_link
  - **How**: Parse YAML, validate against JSON Schema

- [ ] **Required Sections Present**: Purpose, Context, Specification, Verification, Rationale, References
  - **How**: Parse Markdown, check for H2 headers

- [ ] **Examples Include Code Snippets**: "Do This" and "Don't Do This" have code blocks
  - **How**: Check for triple-backtick code fences in Specification section

- [ ] **Links Resolve**: Analysis doc, ADRs, code examples exist
  - **How**: Check file existence for all referenced paths

- [ ] **No Conflicts**: New rule doesn't contradict existing rules
  - **How**: Run conflict detection script (REC-004)
  - **Fail If**: Semantic conflict, scope overlap with different guidance

- [ ] **Word Count Reasonable**: 200-800 words (Goldilocks zone)
  - **How**: Count words in body sections
  - **Warning If**: <200 (too terse) or >1200 (too verbose)

- [ ] **Priority Consistent with Criticality**: P0 for High, P1 for Medium, P2 for Low
  - **How**: Check frontmatter priority vs analysis doc criticality

**Exit Codes**:
- `0`: Pass (proceed to registry update)
- `1`: Fail (fix issues before continuing)
- `2`: Warning (user review recommended but not required)

**Usage**:
```bash
.specify/scripts/bash/validate-rule-quality.sh \
  --rule-file ".cursor/rules/pattern/100-repository.mdc"

# Output:
✓ Frontmatter schema valid
✓ Required sections present
✓ Examples include code snippets
✓ Links resolve (analysis-for-repository-pattern.md, adr-007-repository-pattern.md)
✓ No conflicts detected
✓ Word count: 652 words (within range)
✓ Priority (P0) consistent with criticality (High)
PASS: Rule quality is acceptable
```

---

### Gate 3: Post-Deployment Effectiveness

**When**: 2-4 weeks after rule deployment
**Script**: `.specify/scripts/bash/measure-rule-effectiveness.sh`
**Purpose**: Validate rule is effective in practice, not just theory

**Checks**:

- [ ] **Adherence Rate**: % of code following rule
  - **Target**: >80% for P0, >60% for P1, >40% for P2
  - **How**: AST analysis, linting, or manual sampling
  - **Fail If**: Below target after 4 weeks

- [ ] **Detection Rate**: % of violations caught in code review
  - **Target**: >90% for automated checks, >70% for manual checks
  - **How**: Analyze code review comments mentioning rule
  - **Fail If**: <60% detection (rule unclear or unenforced)

- [ ] **False Positive Rate**: % of false alarms
  - **Target**: <10%
  - **How**: Analyze code review comments flagging "false positive"
  - **Fail If**: >20% (rule too strict or unclear)

- [ ] **Developer Feedback**: Qualitative assessment
  - **How**: Survey, retrospective, or async feedback
  - **Positive Signals**: "This rule caught a bug", "Clearer code", "Good reminder"
  - **Negative Signals**: "Too strict", "Unclear when to apply", "False positives"

- [ ] **Code Quality Impact** (optional): Bug rate, maintainability index
  - **How**: Compare metrics in ruled code vs unruled code
  - **Positive**: Bug rate lower, maintainability index higher

**Outcomes**:
- **Pass (✅)**: Rule is effective, no action needed
- **Refine (⚠️)**: Rule needs improvement (update examples, clarify scope, adjust priority)
- **Retire (❌)**: Rule is ineffective (0 violations = obsolete, or >20% FP = too strict)

**Usage**:
```bash
.specify/scripts/bash/measure-rule-effectiveness.sh \
  --rule-id "pattern-100-repository" \
  --since "2025-12-01"

# Output:
Adherence Rate: 88% ████████████████████░░ (target: 80%) ✓
Detection Rate: 85% ██████████████████░░░░ (target: 70%) ✓
False Positive: 5%  ███░░░░░░░░░░░░░░░░░░ (target: <10%) ✓
Developer Feedback: 4.2/5 stars (12 responses)

Code Quality Impact:
- Bug Rate: 0.9 bugs/KLOC (ruled) vs 2.1 (unruled) → 57% ⬇
- Maintainability: 75 (ruled) vs 62 (unruled) → 21% ⬆

PASS: Rule is effective, no action needed
```

---

## 4. Anti-Patterns Catalog

Avoid these common mistakes when creating rules.

### AP-001: Rule Explosion (Too Many Rules)

**Symptom**: 100+ rules, developers overwhelmed, agents confused

**Example**: Team creates separate rule for every class, function naming convention

**Prevention**:
- Set hard limit: **50 rules max** for projects <100K LOC
- Consolidate related rules (e.g., combine "camelCase for functions" + "PascalCase for classes" into "Naming Conventions")
- Remove low-value rules (P2 rules with <60% adherence)

**Refactoring**: Merge related rules, archive obsolete rules

---

### AP-002: Over-Specification (Too Detailed)

**Symptom**: Rules dictate exact implementation, agent has no flexibility

**Example**:
```markdown
# BAD: Too prescriptive
All functions must be exactly 10-15 lines.
Variable names must follow pattern: [type][PascalCase][Suffix].
Always use Option<T> for nullable values, never null.
```

**Why Bad**: Stifles agent creativity, doesn't account for edge cases

**Prevention**:
- Focus on "what" and "why", not "how" (unless critical)
- Allow agent judgment: "Prefer X, but Y is acceptable if [condition]"
- Use "should" instead of "must" for non-critical rules

**Example Fixed**:
```markdown
# GOOD: Prescriptive but flexible
Functions should be concise (typically 10-20 lines).
If a function exceeds 30 lines, consider extracting sub-functions.

Exception: Integration tests may be longer (50-100 lines) to improve readability.
```

---

### AP-003: Under-Specification (Too Vague)

**Symptom**: Rules too vague, agent interprets differently each time

**Example**:
```markdown
# BAD: Too vague
Code should be clean and maintainable.
Follow SOLID principles.
Use appropriate design patterns.
```

**Why Bad**: No actionable guidance, agent guesses intent

**Prevention**:
- Always include concrete examples (Do This / Don't Do This)
- Specify clear boundaries (what's in scope, what's not)
- Use specific verbs: "Use Repository pattern" (not "Use appropriate data access pattern")

**Example Fixed**:
```markdown
# GOOD: Specific and actionable
Use Repository pattern for database access.

Do This:
​```typescript
class UserRepository {
  findById(id: string): Promise<User | null>
}
​```

Don't Do This:
​```typescript
// BAD: Direct DB call in service
await prisma.user.findUnique({ where: { id } })
​```
```

---

### AP-004: Stale Rules (Obsolete Patterns)

**Symptom**: Rules describe old architecture, agent generates outdated code

**Example**: Rule says "Use REST" but team migrated to GraphQL 6 months ago

**Prevention**:
- Quarterly audits: Review all rules, flag if last_reviewed >6 months
- Automated staleness detection: Flag rules with 0 violations in 6 months (maybe 100% adopted or obsolete)
- Deprecation workflow: Mark rule as deprecated, add sunset date, provide migration guide

**Refactoring**:
```yaml
---
deprecated: true
deprecated_date: "2026-01-15"
deprecated_reason: "Migrated to GraphQL, REST endpoints no longer used"
deprecated_by: "pattern-401-graphql-resolver"
---
```

---

### AP-005: Conflicting Rules (Contradictions)

**Symptom**: Rule A says "do X", Rule B says "avoid X", agent confused

**Example**:
- Rule 100: "Use Singleton for database connection"
- Rule 105: "Avoid Singleton pattern (hard to test)"

**Prevention**:
- Conflict detection script (REC-004) catches contradictions
- Explicit precedence hierarchy: Specific > General, File-Type > Module > Layer > Global
- Exception clauses: "Avoid Singleton, except for [specific case]"

**Refactoring**:
- Merge conflicting rules with exception clauses
- Document precedence explicitly in rule body

---

### AP-006: Tool Overlap (Redundant with Linter)

**Symptom**: Rule enforces something already checked by ESLint, TypeScript compiler, etc.

**Example**:
```markdown
# REDUNDANT: TypeScript already enforces this
All variables must have explicit types.
Never use `any` type.
```

**Prevention**:
- Before creating rule, check: Is this enforced by existing tooling?
- If yes, document in README ("We use ESLint for style, rules for architecture")
- Focus rules on architecture, patterns, domain logic (not syntax)

**Exception**: If linter rule exists but needs explanation for AI agents, create rule with "Rationale" section pointing to linter

---

### AP-007: Personal Preference Disguised as Rule

**Symptom**: Rule is one developer's preference without measurable benefit

**Example**:
```markdown
# PERSONAL PREFERENCE: No objective benefit
Always use single quotes for strings, never double quotes.
Prefer `forEach` over `for` loops.
```

**Prevention**:
- Require justification: "Why does this matter? What problem does it solve?"
- Require 2+ engineers to approve rule (team consensus)
- Challenge: "Would violating this rule cause a bug or maintainability issue?"

**Exception**: Team-wide style preferences are OK if consistently applied and documented in README ("Our stylistic choices")

---

## 5. Maintenance Procedures

### 5.1 Quarterly Audit (Every 3 Months)

**Owner**: Technical Lead or Architecture Team

**Process**:

1. **Run Staleness Detection**:
   ```bash
   .specify/scripts/bash/detect-stale-rules.sh
   ```
   Flags rules with:
   - Last reviewed >6 months ago
   - 0 violations in past 6 months (maybe obsolete)
   - Broken links (analysis docs, ADRs deleted)

2. **Run Conflict Detection**:
   ```bash
   .specify/scripts/bash/detect-rule-conflicts.sh
   ```
   Flags rules with:
   - Contradictory specifications
   - Overlapping scopes with different guidance

3. **Run Coverage Analysis**:
   ```bash
   .specify/scripts/bash/analyze-rule-coverage.sh
   ```
   Reports:
   - % of codebase covered by rules (by directory)
   - Uncovered areas (new patterns emerging?)
   - Over-covered areas (too many rules for one area?)

4. **Review Flagged Rules**:
   - For each flagged rule, decide: **Update**, **Deprecate**, or **Keep**
   - Update: Refresh examples, clarify scope, adjust priority
   - Deprecate: Mark as deprecated, set sunset date, provide replacement
   - Keep: Add review date, justify why still relevant despite 0 violations

5. **Generate Report**:
   - Document: `specs/main/analysis/rule-audit-YYYY-MM-DD.md`
   - Summary: Rules reviewed, actions taken, trends observed

**Timeline**: 1-2 days per audit

---

### 5.2 Rule Deprecation Process

**Trigger**: Rule is obsolete, ineffective, or superseded

**Steps**:

1. **Update Frontmatter**:
   ```yaml
   ---
   deprecated: true
   deprecated_date: "YYYY-MM-DD"
   deprecated_reason: "[Brief explanation, 1 sentence]"
   deprecated_by: "[replacement-rule-id or null]"
   ---
   ```

2. **Add Deprecation Notice to Body**:
   ```markdown
   > **⚠️ DEPRECATED** (as of YYYY-MM-DD)
   >
   > **Reason**: [Explanation]
   >
   > **Replacement**: See rule [ID] for updated guidance.
   >
   > **Sunset Date**: This rule will be archived on [YYYY-MM-DD] (1 month grace period).
   ```

3. **Communicate to Team**:
   - Announce in Slack/email: "Rule [ID] deprecated, use [replacement] instead"
   - Update CHANGELOG.md in .cursor/rules/

4. **Grace Period** (1 month):
   - Keep deprecated rule in .cursor/rules/ (marked deprecated)
   - Monitor: Any violations flagged? (indicates rule still needed)

5. **Archive**:
   - After grace period, move to `.cursor/rules/deprecated/[ID].mdc`
   - Update registry: Mark as archived
   - Remove from AGENTS.md summary

**Rationale**: Gradual deprecation prevents breaking changes, allows team to adjust

---

### 5.3 Rule Update Process

**Trigger**: Rule needs refinement (examples unclear, scope ambiguous, priority wrong)

**Steps**:

1. **Create Update Branch**:
   ```bash
   git checkout -b update-rule-[ID]
   ```

2. **Update Rule File**:
   - Modify .mdc file (frontmatter or body)
   - Increment version:
     - Patch (1.0.0 → 1.0.1): Typo fix, example clarification
     - Minor (1.0.0 → 1.1.0): Scope change, new examples
     - Major (1.0.0 → 2.0.0): Specification change (breaking)
   - Update `last_reviewed` date

3. **Update Analysis Document**:
   - Modify `specs/main/analysis/rules/analysis-for-[name].md`
   - Document rationale for change

4. **Re-Run Quality Gate**:
   ```bash
   .specify/scripts/bash/validate-rule-quality.sh --rule-file ".cursor/rules/[category]/[ID].mdc"
   ```

5. **Code Review**:
   - PR review by 2+ engineers
   - Check: Is change justified? Does it improve clarity?

6. **Merge and Communicate**:
   - Merge to main branch
   - Announce in Slack/email if major change
   - Update CHANGELOG.md

**Timeline**: 1-2 hours for minor updates, 4-8 hours for major updates

---

## 6. Effectiveness Metrics

### 6.1 Primary Metrics

**Adherence Rate**:
```
Adherence % = (Lines of code following rule / Total lines in scope) × 100
```

**Target**:
- P0 rules: >80%
- P1 rules: >60%
- P2 rules: >40%

**Measurement**:
- Manual sampling (review 10% of codebase)
- AST analysis (automated, language-specific)
- Linting (if custom linter rule created)

**Interpretation**:
- >80%: Excellent (rule well-adopted)
- 60-80%: Good (room for improvement, add examples or training)
- 40-60%: Fair (rule unclear or too strict, needs refinement)
- <40%: Poor (rule ineffective, consider deprecating)

---

**Detection Rate**:
```
Detection % = (Violations caught in code review / Total violations in code) × 100
```

**Target**:
- Automated checks: >90%
- Manual checks: >70%

**Measurement**:
- Code review comments: Count comments mentioning rule
- Compare: Violations caught vs violations found later (bugs, audits)

**Interpretation**:
- >90%: Excellent (rule is catching issues proactively)
- 70-90%: Good (acceptable for manual checks)
- <70%: Poor (rule not being enforced, or violations too subtle)

---

**False Positive Rate**:
```
FP % = (False positives / Total rule invocations) × 100
```

**Target**: <10%

**Measurement**:
- Code review comments: Count "false alarm", "doesn't apply here", "exception needed"

**Interpretation**:
- <10%: Excellent (rule is precise)
- 10-20%: Acceptable (some edge cases, document exceptions)
- >20%: Poor (rule too strict, needs refinement)

---

### 6.2 Secondary Metrics

**Code Quality Impact**:
- **Bug Rate**: Bugs per KLOC (ruled code vs unruled code)
- **Maintainability Index**: CodeClimate, SonarQube score
- **Technical Debt**: SAR report changes over time

**Developer Productivity**:
- **Code Review Time**: Reduced if fewer rule violations
- **Onboarding Time**: New developers faster with clear rules
- **AI Code Acceptance**: % of AI-generated code passing review (with rules vs without)

**Rule Health**:
- **Rule Age**: Last updated date (flag if >6 months)
- **Usage Frequency**: Violations per month (flag if 0 for 6 months)
- **Conflict Count**: Number of conflicts detected with other rules

---

### 6.3 Dashboard Visualization

**Example** (from REC-011):

```
┌─ Rule: pattern-100-repository ──────────────────────────────┐
│ Priority: P0 | Version: 1.2.0 | Last Reviewed: 2025-12-15  │
│                                                              │
│ Metrics (last 30 days):                                     │
│   Adherence Rate: 88% ████████████████████░░ (target: 80%)  │
│   Detection Rate: 85% ██████████████████░░░░ (target: 70%)  │
│   False Positive: 5%  ███░░░░░░░░░░░░░░░░░░ (target: <10%) │
│                                                              │
│ Trend: ⬆ Improving (was 78% 90 days ago)                   │
│                                                              │
│ Code Quality Impact:                                         │
│   Bug Rate: 0.8 bugs/KLOC (ruled) vs 2.3 (unruled) → 65% ⬇ │
│   Maintainability: 72 (ruled) vs 58 (unruled) → 24% ⬆      │
│                                                              │
│ Action: ✅ No action needed (healthy rule)                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Continuous Improvement Process

### 7.1 Feedback Loop

```
┌────────────────┐
│ Create Rule    │
│ (raise.rules.  │
│  generate)     │
└───────┬────────┘
        │
        v
┌────────────────┐
│ Deploy Rule    │
│ (commit to     │
│  .cursor/rules)│
└───────┬────────┘
        │
        v
┌────────────────┐
│ Monitor        │
│ (adherence,    │
│  FP rate)      │
└───────┬────────┘
        │
        v
┌────────────────┐
│ Collect        │
│ Feedback       │
│ (code review   │
│  comments)     │
└───────┬────────┘
        │
        v
┌────────────────┐
│ Analyze        │
│ (quarterly     │
│  audit)        │
└───────┬────────┘
        │
        v
┌────────────────┐
│ Decide Action  │
│ (keep, update, │
│  deprecate)    │
└───────┬────────┘
        │
        v
┌────────────────┐
│ Implement      │
│ (update rule   │
│  or retire)    │
└───────┬────────┘
        │
        └─────────► (back to Monitor)
```

**Cycle Time**: 3 months (quarterly audits)

**Goal**: Continuously improve rule quality based on real-world usage

---

### 7.2 Lessons Learned Repository

**Document**: `specs/main/analysis/rules/lessons-learned.md`

**Format**:
```markdown
# Lessons Learned: Rule Quality

## [YYYY-MM-DD] Rule 100-repository: High False Positives

**Problem**: 18% FP rate (target: <10%)

**Root Cause**: Rule didn't account for read-only queries (reporting)

**Solution**: Added exception clause: "Read-only queries (SELECT only) may bypass repository if performance-critical"

**Result**: FP rate dropped to 6%

**Takeaway**: Always document exceptions explicitly, especially for performance trade-offs

---

## [YYYY-MM-DD] Rule 200-naming: Low Adherence

**Problem**: 52% adherence (target: >60%)

**Root Cause**: Examples only showed TypeScript, team also uses Python

**Solution**: Added Python examples, updated scope to include *.py files

**Result**: Adherence increased to 71%

**Takeaway**: Multi-language projects need examples for each language

---
```

**Usage**: Review before creating new rules to avoid repeating mistakes

---

## 8. Appendix A: Example Exemplary Rule

**File**: `.cursor/rules/pattern/100-repository.mdc`

```yaml
---
# REQUIRED FIELDS
id: "pattern-100-repository"
category: "pattern"
priority: "P0"
version: "1.2.0"

# RECOMMENDED FIELDS
scope: ["src/data/repositories/**/*.ts", "src/infrastructure/**/*.ts"]
enforcement: "manual"
created: "2025-06-15"
author: "Architecture Team"
rationale_link: "specs/main/analysis/rules/analysis-for-repository-pattern.md"
examples: "src/data/repositories/UserRepository.ts"

# OPTIONAL FIELDS
deprecated: false
tags: ["clean-architecture", "database", "testability"]
related_rules: ["architecture-001-clean-arch", "quality-300-testing"]
evidence_count: 12
frequency: "high"
stability_months: 18
last_reviewed: "2025-12-15"
hierarchy_level: "layer"
hierarchy_path: "infrastructure"
---

# Rule: Use Repository Pattern for Database Access

## Purpose

Encapsulate database access logic in repository classes to enable testing, maintainability, and adherence to Clean Architecture principles (Dependency Inversion).

## Context

**Applies to**:
- All code in `src/data/repositories/` or `src/infrastructure/` that interacts with the database

**Does NOT apply to**:
- Test files (mock repositories allowed)
- Database migration scripts (`migrations/`)
- One-off admin scripts (`scripts/admin/`)
- Read-only reporting queries (see exception below)

## Specification

### Do This

Create a repository class for each domain entity, implementing an interface:

​```typescript
// src/domain/interfaces/UserRepository.ts
export interface UserRepository {
  findById(id: string): Promise<User | null>
  create(data: CreateUserInput): Promise<User>
  update(id: string, data: UpdateUserInput): Promise<User>
  delete(id: string): Promise<void>
}

// src/data/repositories/PrismaUserRepository.ts
import { UserRepository } from '@/domain/interfaces/UserRepository'
import { PrismaClient } from '@prisma/client'

export class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    const user = await this.prisma.user.findUnique({ where: { id } })
    return user ? toDomainUser(user) : null
  }

  // ... other methods
}

// src/services/UserService.ts (depends on interface, not implementation)
export class UserService {
  constructor(private userRepo: UserRepository) {}

  async getUserProfile(id: string): Promise<UserProfile> {
    const user = await this.userRepo.findById(id)
    if (!user) throw new NotFoundError('User not found')
    return toUserProfile(user)
  }
}
​```

### Don't Do This

**BAD**: Direct database calls in service layer:

​```typescript
// src/services/UserService.ts
import { prisma } from '@/lib/prisma'

export class UserService {
  async getUserProfile(id: string): Promise<UserProfile> {
    // ❌ Direct Prisma call - tightly couples service to Prisma
    const user = await prisma.user.findUnique({ where: { id } })
    if (!user) throw new NotFoundError('User not found')
    return toUserProfile(user)
  }
}
​```

**BAD**: Bypassing repository in controller:

​```typescript
// src/api/users.controller.ts
import { prisma } from '@/lib/prisma'

export async function getUser(req, res) {
  // ❌ Controller directly accesses database - skips business logic layer
  const user = await prisma.user.findUnique({ where: { id: req.params.id } })
  res.json(user)
}
​```

### Why This Matters

**Without Repository Pattern**:
- Services are tightly coupled to Prisma (hard to test, hard to swap ORMs)
- Business logic mixed with database access (violates Single Responsibility)
- Impossible to unit test without real database

**With Repository Pattern**:
- Services depend on interface (testable with mocks)
- Database access centralized (easy to add caching, logging)
- Can swap Prisma for another ORM with minimal changes

### Exception: Read-Only Reporting Queries

**Allowed**: Read-only queries (SELECT only) may bypass repository if performance-critical:

​```typescript
// src/reports/UserActivityReport.ts
// ✓ Acceptable: Complex read-only query for reporting
const stats = await prisma.$queryRaw`
  SELECT date_trunc('day', created_at) as day, COUNT(*) as count
  FROM users
  WHERE created_at > NOW() - INTERVAL '30 days'
  GROUP BY day
`
​```

**Rationale**: Reporting queries are often complex (JOINs, aggregations) and read-only (no data mutation risk). Forcing through repository adds unnecessary indirection.

## Verification

### Manual Check

Search for `prisma.` calls outside repository directories:

​```bash
# Should return no results (exit code 1)
grep -r "prisma\." src/ \
  --exclude-dir=repositories \
  --exclude-dir=data \
  --exclude="*.test.ts" \
  --exclude-dir=reports
​```

Check services inject repositories via constructor:

​```bash
# Should find constructor injections
grep -r "constructor.*Repository" src/services/
​```

### Automated Check (Optional)

Create ESLint custom rule to flag `prisma.` calls outside allowed directories.

## Rationale

This rule enforces the **Repository pattern** from Clean Architecture (Robert C. Martin, Chapter 22).

**Benefits**:
1. **Testability**: Service layer can be unit tested with mock repositories (no database needed)
2. **Maintainability**: Database access logic centralized in one place (easy to add caching, logging)
3. **Flexibility**: Easy to swap Prisma for another ORM (or raw SQL) without touching services
4. **Separation of Concerns**: Business logic (services) separated from persistence (repositories)

**Trade-offs**:
- Adds one layer of indirection (repository interface + implementation)
- More files to maintain
- **Judgment**: Acceptable cost for improved testability and maintainability

**Historical Context**:
Adopted after Incident #42 (2024-03-15) where tightly coupled database calls made refactoring from MongoDB to PostgreSQL impossible without rewriting 50+ service methods. Repository pattern would have isolated changes to repository layer only.

**Team Consensus**: Approved by architecture team (2025-06-10), validated in Spike #87.

**See full analysis**: `specs/main/analysis/rules/analysis-for-repository-pattern.md`

## References

- **ADR**: [ADR-007: Adopt Repository Pattern](docs/decisions/adr-007-repository-pattern.md)
- **Code Examples**:
  - ✅ Good: `src/data/repositories/UserRepository.ts` (full implementation)
  - ❌ Bad: `src/services/UserService.ts` (lines 42-55, before refactor, commit abc123)
- **External Resources**:
  - [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) (Uncle Bob)
  - [Repository Pattern Explained](https://martinfowler.com/eaaCatalog/repository.html) (Martin Fowler)
  - [Testing with Repositories](https://khalilstemmler.com/articles/typescript-domain-driven-design/repository-dto-mapper/) (Khalil Stemmler)
- **Related Rules**:
  - `architecture-001-clean-arch` (parent rule, defines layers)
  - `quality-300-testing` (explains mock repositories in tests)
```

**Why This is Exemplary**:
- ✅ Complete frontmatter (all recommended fields)
- ✅ All required sections present
- ✅ Clear examples (Do This / Don't Do This with code)
- ✅ Exception documented explicitly
- ✅ Verification (manual + automated)
- ✅ Rationale (benefits, trade-offs, historical context)
- ✅ References (ADRs, code, external resources)
- ✅ Word count: 652 words (within 200-800 range)

---

## 9. Conclusion

This Rule Quality Framework provides **comprehensive guidance** for creating, validating, and maintaining high-quality code generation rules in RaiSE.

**Key Takeaways**:
1. **Evidence-Based**: Always require 3-5 positive + 2 counter-examples
2. **3 Quality Gates**: Pre-creation (prevent bad rules), Post-creation (validate structure), Post-deployment (measure effectiveness)
3. **Target Metrics**: 80%+ adherence (P0), <10% false positives, 70%+ developer acceptance
4. **Avoid Anti-Patterns**: Rule explosion, over/under-specification, staleness, conflicts
5. **Continuous Improvement**: Quarterly audits, feedback loops, lessons learned

By following this framework, RaiSE will maintain a **high-quality, effective rule ecosystem** that truly improves AI code generation alignment.
