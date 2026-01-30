# Rule Template v2.0 (Enhanced with REC-001 Metadata)

**Purpose**: Standard template for creating code generation rules in RaiSE
**Version**: 2.0.0
**Date**: 2026-01-23
**Changes from v1**: Enhanced frontmatter metadata schema, hierarchical organization support

---

## Usage

1. Copy this template to `.cursor/rules/[category]/[id].mdc`
2. Replace all `[placeholders]` with actual values
3. Delete optional sections if not applicable
4. Run validation: `.specify/scripts/bash/validate-rule-quality.sh --rule-file [path]`

---

## Template

```yaml
---
# ============================================================================
# REQUIRED FIELDS (validation fails if missing)
# ============================================================================
id: "[category]-[number]-[short-name]"
# Examples: "pattern-100-repository", "convention-200-naming"
# Format: category (8 types) + sequential number + kebab-case name

category: "[architecture|pattern|convention|domain|quality|security|meta]"
# architecture: Layer boundaries, system structure
# pattern: Design patterns (Repository, Factory, Observer)
# convention: Naming, file structure, imports
# domain: Business logic, domain rules
# quality: Testing, coverage, code quality
# security: Input validation, auth, encryption
# meta: Rules about rules (like this template)

priority: "[P0|P1|P2]"
# P0: Must follow (critical, causes bugs/security if violated)
# P1: Should follow (important, maintainability impact)
# P2: May follow (nice-to-have, style preference)

version: "1.0.0"
# Semantic versioning: MAJOR.MINOR.PATCH
# Increment: MAJOR (breaking), MINOR (new examples/scope), PATCH (typos)

# ============================================================================
# RECOMMENDED FIELDS (warning if missing, but not required)
# ============================================================================
scope: ["glob/pattern/**/*.ts"]
# File paths where this rule applies (glob patterns)
# Examples: ["src/domain/**/*.ts"], ["**/*.test.ts"], ["src/api/*.api.ts"]
# Use multiple patterns if rule applies to different areas

enforcement: "[cursor-ai|manual|automated-check]"
# cursor-ai: Cursor AI agent enforces (most common)
# manual: Human code review enforces
# automated-check: Linter/CI script enforces

created: "YYYY-MM-DD"
# Date rule was created

author: "[name or team]"
# Who created this rule (for questions/clarifications)
# Examples: "Architecture Team", "Jane Doe", "Backend Guild"

rationale_link: "[path to analysis doc]"
# Link to deeper rationale/analysis document
# Example: "specs/main/analysis/rules/analysis-for-[name].md"

examples: "[path to example files]"
# Link to code examples (real files in codebase)
# Example: "src/data/repositories/UserRepository.ts"

# ============================================================================
# OPTIONAL FIELDS (no warning, use if applicable)
# ============================================================================
deprecated: false
# Set to true when rule is obsolete

deprecated_by: "[rule-id]"
# If deprecated, which rule replaces this one

deprecated_date: "YYYY-MM-DD"
# When rule was deprecated

tags: ["tag1", "tag2", "tag3"]
# Searchable tags for discovery
# Examples: ["database", "testability"], ["security", "input-validation"]

related_rules: ["rule-id-1", "rule-id-2"]
# Other rules that are related (dependencies or complements)
# Example: ["architecture-001-clean-arch", "quality-300-testing"]

evidence_count: 5
# Number of positive examples found in codebase (from pattern analysis)

frequency: "high"
# Pattern frequency: high (>50% of code), medium (20-50%), low (<20%)

stability_months: 6
# How long pattern has existed in codebase (git history)

last_reviewed: "YYYY-MM-DD"
# Last time rule was audited/updated (for staleness detection)

hierarchy_level: "layer"
# Hierarchy level: global|layer|module|file-type|temporal
# global: Applies to entire codebase
# layer: Applies to architectural layer (domain, application, infrastructure)
# module: Applies to specific directory/module
# file-type: Applies by file extension (*.test.ts, *.api.ts)
# temporal: Temporary (migration periods)

hierarchy_path: "infrastructure"
# Subpath within hierarchy level
# Examples: "domain" (for layer), "api" (for module), "*.test.ts" (for file-type)
---

# Rule: [Short Descriptive Title]

**Example**: "Use Repository Pattern for Database Access"

## Purpose

[1-2 sentences: Why this rule exists, what problem it solves]

**Guidelines**:
- Focus on "why", not "how"
- Explain the benefit (testability, maintainability, performance, security)
- Keep concise (1-2 sentences max)

**Example**:
"Encapsulate database access logic in repository classes to enable testing, maintainability, and adherence to Clean Architecture principles."

---

## Context

[When/where this rule applies, scope boundaries, exceptions]

**Guidelines**:
- Define "Applies to" (which directories, file types)
- Define "Does NOT apply to" (exceptions)
- Clarify edge cases

**Template**:
```
**Applies to**:
- [Directory or file pattern where rule applies]
- [Another applicable area]

**Does NOT apply to**:
- [Explicit exception 1]
- [Explicit exception 2]

**Edge Cases**:
- [Scenario that might be ambiguous]
```

**Example**:
```
**Applies to**:
- All code in `src/data/repositories/` that interacts with the database
- Infrastructure layer database access

**Does NOT apply to**:
- Test files (mock repositories allowed)
- Database migration scripts
- One-off admin scripts

**Edge Cases**:
- Read-only reporting queries may bypass repository if performance-critical (see exception below)
```

---

## Specification

### Do This

[Clear, actionable prescription with code example]

**Guidelines**:
- Show concrete code example (3-20 lines)
- Use real file paths if possible
- Annotate with comments explaining key points
- Use syntax highlighting (triple backticks with language)

**Template**:
```[language]
// [Brief description of what this demonstrates]
[code example showing correct pattern]

// [Annotation explaining why this is good]
```

**Example**:
```typescript
// Good: Repository encapsulates database access
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

// Service depends on interface, not implementation (testable)
class UserService {
  constructor(private userRepo: UserRepository) {}
}
```

### Don't Do This

[Clear prohibition with counter-example]

**Guidelines**:
- Show concrete code example of violation
- Use ❌ or "BAD" markers
- Explain why this is problematic

**Template**:
```[language]
// ❌ BAD: [Why this is wrong]
[code example showing anti-pattern]

// Problem: [Explanation of consequences]
```

**Example**:
```typescript
// ❌ BAD: Direct database call in service layer
class UserService {
  async getUserProfile(id: string) {
    // Problem: Tightly coupled to Prisma, impossible to test without real DB
    const user = await prisma.user.findUnique({ where: { id } })
    return user
  }
}
```

### Why This Matters

[Explanation of consequences if rule violated]

**Guidelines**:
- Explain impact: bugs, security, maintainability, performance
- Use "Without this rule" vs "With this rule" comparison
- Keep concise (2-3 sentences)

**Example**:
```
**Without this rule**:
- Services tightly coupled to Prisma (hard to test, hard to swap ORMs)
- Business logic mixed with database access (violates Single Responsibility)

**With this rule**:
- Services testable with mock repositories
- Database access centralized (easy to add caching, logging)
```

### Exception (Optional)

[Document any exceptions to the rule]

**Template**:
```
**Allowed**: [Exception description]

​```[language]
// ✓ Acceptable: [Why this exception is OK]
[code example of allowed exception]
​```

**Rationale**: [Why exception is necessary]
```

**Example**:
```
**Allowed**: Read-only queries (SELECT only) may bypass repository if performance-critical

​```typescript
// ✓ Acceptable: Complex read-only query for reporting
const stats = await prisma.$queryRaw`
  SELECT date_trunc('day', created_at) as day, COUNT(*) as count
  FROM users WHERE created_at > NOW() - INTERVAL '30 days'
  GROUP BY day
`
​```

**Rationale**: Reporting queries are often complex (JOINs, aggregations) and read-only (no mutation risk). Forcing through repository adds unnecessary indirection.
```

---

## Verification

[How to check if code follows this rule]

### Manual Check

[Step-by-step instructions for human reviewer]

**Template**:
```bash
# [Description of what this command checks]
[command to search for violations]

# Expected: [What success looks like]
```

**Example**:
```bash
# Search for direct Prisma calls outside repository directories
grep -r "prisma\." src/ --exclude-dir=repositories --exclude="*.test.ts"

# Expected: No results (exit code 1)
```

### Automated Check (Optional)

[If automated check exists (linter, script)]

**Template**:
```bash
# Run [tool name]
[command to run automated check]

# Expected: [Exit code, output]
```

**Example**:
```bash
# Run custom ESLint rule
npm run lint -- --rule no-direct-db-access

# Expected: 0 errors
```

---

## Rationale

[Deeper explanation: architectural reasons, historical context, trade-offs]

**Guidelines**:
- Explain "why" in depth (this is for developers who want full context)
- Document benefits (with bullet list)
- Document trade-offs (be honest)
- Provide historical context if applicable (incidents, decisions)
- Link to analysis document for even more detail

**Template**:
```markdown
This rule enforces [pattern/principle] from [source].

**Benefits**:
1. [Benefit 1 with brief explanation]
2. [Benefit 2 with brief explanation]
3. [Benefit 3 with brief explanation]

**Trade-offs**:
- [Cost or downside]
- [Another consideration]
- **Judgment**: [Why trade-off is acceptable]

**Historical Context** (optional):
[Why team adopted this rule, any incidents that motivated it]

**Team Consensus**: [Approval process, validation]

**See full analysis**: [link to analysis document]
```

**Example**:
```markdown
This rule enforces the **Repository pattern** from Clean Architecture (Robert C. Martin, Chapter 22).

**Benefits**:
1. **Testability**: Services can be unit tested with mock repositories (no database needed)
2. **Maintainability**: Database access centralized (easy to add caching, logging)
3. **Flexibility**: Easy to swap ORMs without touching services
4. **Separation of Concerns**: Business logic separated from persistence

**Trade-offs**:
- Adds one layer of indirection (repository interface + implementation)
- More files to maintain
- **Judgment**: Acceptable cost for improved testability

**Historical Context**:
Adopted after Incident #42 (2024-03-15) where tightly coupled database calls made refactoring from MongoDB to PostgreSQL impossible.

**Team Consensus**: Approved by architecture team (2025-06-10), validated in Spike #87.

**See full analysis**: `specs/main/analysis/rules/analysis-for-repository-pattern.md`
```

---

## References

[Links to related resources]

**Guidelines**:
- ADRs (architecture decision records)
- Code examples (real files in codebase)
- External resources (books, articles, official docs)
- Related rules

**Template**:
```markdown
- **ADR**: [path to relevant ADR]
- **Code Examples**:
  - ✅ Good: [path to exemplary code]
  - ❌ Bad: [path to anti-pattern code] (commit hash, before refactor)
- **External Resources**:
  - [Book/Article title](URL)
  - [Another resource](URL)
- **Related Rules**:
  - `[rule-id]` ([brief description of relationship])
```

**Example**:
```markdown
- **ADR**: [ADR-007: Adopt Repository Pattern](docs/decisions/adr-007-repository-pattern.md)
- **Code Examples**:
  - ✅ Good: `src/data/repositories/UserRepository.ts`
  - ❌ Bad: `src/services/UserService.ts` (lines 42-55, commit abc123, before refactor)
- **External Resources**:
  - [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) (Uncle Bob)
  - [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) (Martin Fowler)
- **Related Rules**:
  - `architecture-001-clean-arch` (defines layers this rule operates within)
  - `quality-300-testing` (explains mock repositories in tests)
```

---

## Notes for Template Users

### Minimum Viable Rule

If creating a quick rule, you can omit:
- Optional frontmatter fields (tags, hierarchy, etc.)
- Exception section (if no exceptions)
- Automated check (if no automation exists)
- Historical context (if not applicable)

### Word Count Target

- **Minimum**: 200 words (less is too terse)
- **Target**: 400-600 words (sweet spot)
- **Maximum**: 1200 words (more is too verbose)

### Quality Checklist

Before submitting rule, verify:
- [ ] All required frontmatter fields present
- [ ] All required sections present (Purpose, Context, Specification, Verification, Rationale, References)
- [ ] "Do This" has code example
- [ ] "Don't Do This" has code example
- [ ] Examples use real language/framework from project
- [ ] Links resolve (analysis docs, ADRs, code examples)
- [ ] Word count: 200-1200 words
- [ ] Validation passes: `.specify/scripts/bash/validate-rule-quality.sh`

---

**Version History**:
- **v2.0.0** (2026-01-23): Enhanced metadata schema (REC-001), hierarchical organization support
- **v1.0.0** (2025-06-01): Initial template

**Maintained by**: RaiSE Framework Team
**Feedback**: [GitHub Issues](https://github.com/your-org/raise-commons/issues)
```
