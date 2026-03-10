# Validation Scripts Specification

**Purpose**: Specifications for rule quality validation scripts
**Version**: 1.0.0
**Date**: 2026-01-23
**Related**: Rule Quality Framework, REC-003, REC-004

---

## Overview

This document specifies **5 validation scripts** for ensuring rule quality:

1. `validate-rule-candidate.sh` - Gate 1: Pre-creation validation
2. `validate-rule-quality.sh` - Gate 2: Post-creation quality
3. `measure-rule-effectiveness.sh` - Gate 3: Post-deployment effectiveness
4. `check-duplicate-rules.sh` - Duplicate detection (REC-003)
5. `detect-rule-conflicts.sh` - Conflict detection (REC-004)

All scripts follow consistent patterns:
- **Exit Codes**: 0 (pass), 1 (fail), 2 (warning)
- **Output Format**: Human-readable text + optional JSON (`--json` flag)
- **Location**: `.specify/scripts/bash/`

---

## Script 1: validate-rule-candidate.sh

### Purpose

Validate rule candidate **before** generating .mdc file (Gate 1).

### Usage

```bash
.specify/scripts/bash/validate-rule-candidate.sh \
  --pattern "repository-pattern" \
  --analysis-doc "specs/main/analysis/patterns/pattern-repository.md" \
  [--json]
```

### Parameters

- `--pattern` (required): Pattern name (kebab-case)
- `--analysis-doc` (required): Path to pattern analysis document
- `--json` (optional): Output JSON instead of text

### Validation Checks

#### Check 1: Sufficient Evidence

- **Requirement**: ≥3 positive examples + ≥2 counter-examples
- **How**: Parse analysis document, count code blocks in "Positive Examples" and "Counter-Examples" sections
- **Pass If**: `positive_count >= 3 AND counter_count >= 2`
- **Fail If**: Below threshold (unless justification provided)

#### Check 2: Frequency Threshold

- **Requirement**: Pattern appears ≥3 times in codebase
- **How**: Parse "Frequency Data" section of analysis document
- **Pass If**: `occurrences >= 3 OR criticality == "High" (security)`
- **Warning If**: `occurrences == 3` (barely meets threshold)

#### Check 3: No Duplicates

- **Requirement**: Similar rule doesn't exist
- **How**: Call `check-duplicate-rules.sh --pattern [pattern-name]`
- **Pass If**: No duplicates found
- **Warning If**: Potential duplicate (filename or content similarity)

#### Check 4: Scope Defined

- **Requirement**: Scope clearly specified (glob patterns or description)
- **How**: Check for "Scope" section in analysis document
- **Fail If**: Scope missing or ambiguous ("applies to some files")

#### Check 5: Criticality Assessed

- **Requirement**: Criticality rating (High/Medium/Low) with justification
- **How**: Check for "Criticality" section in analysis document
- **Fail If**: Criticality missing or unjustified

### Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed (do not generate rule)
- `2`: Warnings present (user decision required)

### Output Format

**Text Output**:
```
✓ Sufficient evidence (5 positive, 2 negative examples)
✓ Frequency threshold met (12 occurrences)
⚠ Potential duplicate found (check-duplicate-rules found similar pattern)
✓ Scope defined (src/data/repositories/**/*.ts)
✓ Criticality assessed (High: prevents tight coupling, enables testing)

WARNING: Manual review recommended before proceeding
```

**JSON Output** (`--json`):
```json
{
  "status": "warning",
  "exit_code": 2,
  "checks": [
    {
      "name": "sufficient_evidence",
      "status": "pass",
      "details": "5 positive, 2 negative examples"
    },
    {
      "name": "frequency_threshold",
      "status": "pass",
      "details": "12 occurrences"
    },
    {
      "name": "no_duplicates",
      "status": "warning",
      "details": "Potential duplicate: pattern-105-data-access"
    },
    {
      "name": "scope_defined",
      "status": "pass",
      "details": "src/data/repositories/**/*.ts"
    },
    {
      "name": "criticality_assessed",
      "status": "pass",
      "details": "High: prevents tight coupling, enables testing"
    }
  ]
}
```

---

## Script 2: validate-rule-quality.sh

### Purpose

Validate generated rule **after** creation (Gate 2).

### Usage

```bash
.specify/scripts/bash/validate-rule-quality.sh \
  --rule-file ".cursor/rules/pattern/100-repository.mdc" \
  [--json]
```

### Parameters

- `--rule-file` (required): Path to .mdc rule file
- `--json` (optional): Output JSON

### Validation Checks

#### Check 1: Frontmatter Schema Valid

- **Requirement**: All required fields present, correct format
- **Required Fields**: `id`, `category`, `priority`, `version`
- **How**: Parse YAML, validate against schema
- **Fail If**: Missing required field, invalid format, wrong enum value

#### Check 2: Required Sections Present

- **Requirement**: Purpose, Context, Specification, Verification, Rationale, References
- **How**: Parse Markdown, check for H2 headers
- **Fail If**: Any required section missing

#### Check 3: Examples Include Code Snippets

- **Requirement**: "Do This" and "Don't Do This" have code blocks
- **How**: Check for triple-backtick code fences in Specification section
- **Fail If**: Missing code examples in either subsection

#### Check 4: Links Resolve

- **Requirement**: Referenced files exist
- **How**: Extract links from Rationale and References sections, check file existence
- **Warning If**: Link broken (file doesn't exist)

#### Check 5: No Conflicts

- **Requirement**: New rule doesn't contradict existing rules
- **How**: Call `detect-rule-conflicts.sh --new-rule [rule-file]`
- **Fail If**: Semantic or scope conflict detected

#### Check 6: Word Count Reasonable

- **Requirement**: 200-1200 words
- **How**: Count words in body sections (exclude frontmatter)
- **Warning If**: <200 (too terse) or >1200 (too verbose)

#### Check 7: Priority Consistent

- **Requirement**: Priority matches criticality (P0 for High, P1 for Medium, P2 for Low)
- **How**: Check frontmatter `priority` vs linked analysis document `criticality`
- **Warning If**: Mismatch (e.g., P0 but Medium criticality)

### Exit Codes

- `0`: All checks passed
- `1`: Critical failures (do not proceed)
- `2`: Warnings (review recommended)

### Output Format

**Text Output**:
```
✓ Frontmatter schema valid (all required fields present)
✓ Required sections present (7/7)
✓ Examples include code snippets (Do This: 1, Don't Do This: 1)
⚠ Link broken: specs/main/analysis/rules/analysis-for-repository-pattern.md (file not found)
✓ No conflicts detected
✓ Word count: 652 words (within 200-1200 range)
✓ Priority (P0) consistent with criticality (High)

WARNING: Fix broken link before proceeding
```

---

## Script 3: measure-rule-effectiveness.sh

### Purpose

Measure rule effectiveness **after deployment** (Gate 3).

### Usage

```bash
.specify/scripts/bash/measure-rule-effectiveness.sh \
  --rule-id "pattern-100-repository" \
  --since "2025-12-01" \
  [--json]
```

### Parameters

- `--rule-id` (required): Rule ID
- `--since` (required): Start date for measurement (YYYY-MM-DD)
- `--json` (optional): Output JSON

### Metrics Collected

#### Metric 1: Adherence Rate

- **Definition**: % of code following rule
- **How**: AST analysis, linting, or manual sampling
- **Target**: >80% (P0), >60% (P1), >40% (P2)
- **Implementation**: Language-specific (e.g., tree-sitter for TypeScript)

#### Metric 2: Detection Rate

- **Definition**: % of violations caught in code review
- **How**: Analyze PR comments mentioning rule ID
- **Target**: >90% (automated), >70% (manual)
- **Implementation**: Parse PR comments via GitHub/GitLab API

#### Metric 3: False Positive Rate

- **Definition**: % of false alarms
- **How**: Count PR comments with "false positive", "doesn't apply", "exception"
- **Target**: <10%
- **Implementation**: Grep PR comments for keywords

#### Metric 4: Developer Feedback (Optional)

- **Definition**: Qualitative assessment
- **How**: Survey responses, retrospective notes
- **Output**: Average rating (1-5 stars), comment themes

#### Metric 5: Code Quality Impact (Optional)

- **Definition**: Bug rate, maintainability index
- **How**: Compare ruled code vs unruled code
- **Output**: Delta (% improvement/degradation)

### Exit Codes

- `0`: Rule is effective (all targets met)
- `1`: Rule is ineffective (retire or refine)
- `2`: Mixed results (review recommended)

### Output Format

**Text Output**:
```
Rule Effectiveness Report: pattern-100-repository
Period: 2025-12-01 to 2026-01-23 (54 days)

Adherence Rate: 88% ████████████████████░░ (target: 80%) ✓
Detection Rate: 85% ██████████████████░░░░ (target: 70%) ✓
False Positive: 5%  ███░░░░░░░░░░░░░░░░░░ (target: <10%) ✓

Developer Feedback: 4.2/5 stars (12 responses)
- Positive: "Caught 2 bugs in PR reviews"
- Negative: "Exception needed for admin scripts"

Code Quality Impact:
- Bug Rate: 0.9 bugs/KLOC (ruled) vs 2.1 (unruled) → 57% ⬇
- Maintainability: 75 (ruled) vs 62 (unruled) → 21% ⬆

PASS: Rule is effective, no action needed
```

**JSON Output** (`--json`):
```json
{
  "rule_id": "pattern-100-repository",
  "period": {"start": "2025-12-01", "end": "2026-01-23", "days": 54},
  "adherence_rate": {"value": 88, "target": 80, "status": "pass"},
  "detection_rate": {"value": 85, "target": 70, "status": "pass"},
  "false_positive_rate": {"value": 5, "target": 10, "status": "pass"},
  "developer_feedback": {
    "rating": 4.2,
    "responses": 12,
    "comments": ["Caught 2 bugs", "Exception needed for admin scripts"]
  },
  "code_quality_impact": {
    "bug_rate": {"ruled": 0.9, "unruled": 2.1, "delta_pct": -57},
    "maintainability": {"ruled": 75, "unruled": 62, "delta_pct": 21}
  },
  "status": "pass",
  "recommendation": "No action needed"
}
```

---

## Script 4: check-duplicate-rules.sh

### Purpose

Detect duplicate rules before creation (REC-003).

### Usage

```bash
.specify/scripts/bash/check-duplicate-rules.sh \
  --pattern "repository-pattern" \
  --category "pattern" \
  [--json]
```

### Parameters

- `--pattern` (required): Pattern name (kebab-case)
- `--category` (required): Rule category (architecture, pattern, convention, etc.)
- `--json` (optional): Output JSON

### Detection Algorithm

#### Detection 1: Filename Similarity

- **How**: Check if `[pattern-name]` matches existing rule IDs in `.cursor/rules/[category]/`
- **Match**: Exact substring match (e.g., "repository" matches "100-repository.mdc")

#### Detection 2: Content Similarity

- **How**: Grep existing rules for pattern keywords
- **Keywords**: Extract from pattern name (split on `-`), search in rule bodies

#### Detection 3: Tag Similarity (If REC-001 Implemented)

- **How**: Parse frontmatter `tags` field, check for overlap
- **Match**: ≥50% tag overlap

### Exit Codes

- `0`: No duplicates found
- `1`: Duplicate found (exact filename match)
- `2`: Potential duplicate (content or tag similarity)

### Output Format

**Text Output**:
```
Checking for duplicates of pattern "repository-pattern" in category "pattern"...

✓ No exact filename match
⚠ Content similarity found in:
  - pattern-105-data-access.mdc (mentions "repository" 3 times)
  - pattern-110-database-access.mdc (mentions "database access" 2 times)

WARNING: Review existing rules before creating new one
```

---

## Script 5: detect-rule-conflicts.sh

### Purpose

Detect conflicting rules (REC-004).

### Usage

```bash
.specify/scripts/bash/detect-rule-conflicts.sh \
  --new-rule ".cursor/rules/pattern/105-new-rule.mdc" \
  [--json]
```

### Parameters

- `--new-rule` (required): Path to new rule file
- `--json` (optional): Output JSON

### Conflict Detection Heuristics

#### Conflict Type 1: Semantic Conflict

- **Definition**: New rule prescribes pattern that existing rule prohibits
- **How**:
  1. Extract keywords from "Do This" section of new rule
  2. Search existing rules for those keywords in "Don't Do This" sections
  3. Flag if overlap found

#### Conflict Type 2: Scope Conflict

- **Definition**: Two rules apply to same files but give different guidance
- **How**:
  1. Parse `scope` globs from new rule and existing rules
  2. Check for overlap (e.g., both apply to `src/**/*.ts`)
  3. If overlap AND different priorities, flag as potential conflict

#### Conflict Type 3: Priority Conflict

- **Definition**: Two P0 rules contradict each other
- **How**: Semantic conflict + both rules have `priority: P0`

### Exit Codes

- `0`: No conflicts detected
- `1`: Critical conflict (P0 rules contradict)
- `2`: Potential conflict (review recommended)

### Output Format

**Text Output**:
```
Checking new rule: pattern-105-singleton

⚠ Semantic conflict detected:
  - New rule prescribes: "Use Singleton for database connection"
  - Existing rule pattern-110-testability prohibits: "Avoid Singleton (hard to test)"

⚠ Scope overlap:
  - Both rules apply to: src/**/*.ts

CONFLICT: Manual review required before proceeding
```

---

## Implementation Notes

### Dependencies

All scripts require:
- Bash 4.0+
- Standard Unix tools: `grep`, `awk`, `sed`
- YAML parser: `yq` (https://github.com/mikefarah/yq)
- JSON parser: `jq` (https://stedolan.github.io/jq/)

Optional:
- `tree-sitter` (for AST analysis in measure-rule-effectiveness.sh)
- GitHub CLI `gh` or GitLab CLI `glab` (for PR comment analysis)

### Error Handling

All scripts must:
- Validate input parameters (exit 1 if invalid)
- Handle missing files gracefully (exit 1 with clear error message)
- Provide actionable error messages ("File not found: X" instead of generic "Error")

### Testing

Each script should have:
- Unit tests for individual checks (using `bats` or similar)
- Integration tests with sample rules
- Golden output tests (compare actual vs expected output)

### Performance

Scripts should complete in:
- `validate-rule-candidate.sh`: <5 seconds
- `validate-rule-quality.sh`: <5 seconds
- `check-duplicate-rules.sh`: <10 seconds (scales with rule count)
- `detect-rule-conflicts.sh`: <10 seconds (scales with rule count)
- `measure-rule-effectiveness.sh`: <60 seconds (depends on codebase size, PR count)

---

## Integration with raise.rules.generate

### Workflow Integration

1. **Kata L2-01 (Pattern Analysis)**: Output feeds into `validate-rule-candidate.sh`
2. **Kata L2-03 Step 2.1**: Call `check-duplicate-rules.sh` before generating rule
3. **Kata L2-03 Step 2.5**: Call `validate-rule-quality.sh` after generating rule
4. **Kata L2-03 Step 2.5**: Call `detect-rule-conflicts.sh` as part of quality gate
5. **Quarterly Audit**: Run `measure-rule-effectiveness.sh` for all rules

### CI/CD Integration

**Pre-commit Hook** (optional):
```bash
#!/bin/bash
# .git/hooks/pre-commit

for rule in $(git diff --cached --name-only --diff-filter=A | grep '.cursor/rules/.*\.mdc'); do
  .specify/scripts/bash/validate-rule-quality.sh --rule-file "$rule"
  if [ $? -ne 0 ]; then
    echo "Rule validation failed for $rule"
    exit 1
  fi
done
```

**CI Check** (GitHub Actions / GitLab CI):
```yaml
rule-validation:
  script:
    - for rule in .cursor/rules/**/*.mdc; do
        .specify/scripts/bash/validate-rule-quality.sh --rule-file "$rule" --json
      done
```

---

## Future Enhancements

### V2 Improvements

- **Machine Learning**: Use ML to detect semantic conflicts (NLP-based, not keyword-based)
- **Rule Dependency Graph**: Visualize rule relationships (Neo4j or similar)
- **Automated Repair**: Suggest fixes for validation failures
- **IDE Integration**: VS Code extension showing validation results inline

### Performance Optimization

- **Caching**: Cache parsed rules to avoid re-parsing on every check
- **Parallelization**: Run conflict detection in parallel for large rule sets
- **Incremental Validation**: Only validate changed rules, not entire rule set

---

**Maintained by**: RaiSE Framework Team
**Version**: 1.0.0
**Last Updated**: 2026-01-23
