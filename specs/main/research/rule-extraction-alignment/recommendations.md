# Recommendations for raise.rules.generate Improvement

**Research ID**: RES-RULE-EXTRACT-ALIGN-001
**Date**: 2026-01-23
**Authors**: Claude Sonnet 4.5 (Research Agent)
**Word Count**: ~6,800 words
**Based On**: Landscape Report analyzing 100+ sources, 15+ repositories, 10+ case studies

---

## Executive Summary

This document presents **15 prioritized recommendations** for improving RaiSE's `raise.rules.generate` command, derived from comprehensive research into industry best practices. Recommendations are organized into three tiers:

- **Quick Wins (REC-001 to REC-005)**: High impact, low effort, implementable in 1-2 weeks
- **Strategic Improvements (REC-010 to REC-014)**: High impact, high effort, 4-12 weeks implementation
- **Experimental Additions (REC-020 to REC-021)**: Medium/uncertain impact, requiring validation

**Top 3 Priorities**:
1. **REC-001**: Standardize .mdc frontmatter (addresses limited metadata gap)
2. **REC-002**: Create missing Katas L2-01 and L2-03 (addresses broken references)
3. **REC-010**: Implement semi-automated pattern mining (addresses manual-only extraction)

**Expected Outcomes**:
- **Reduce rule creation time** by 60% (via semi-automated extraction)
- **Improve rule quality** via automated validation gates (70%+ actionability target)
- **Enable rule ecosystem growth** via enhanced metadata and tooling
- **Align with industry standards** (AGENTS.md compatibility, Agent Skills model)

---

## Quick Wins (High Impact, Low Effort)

| ID | Recommendation | Impact | Effort | Priority | Timeline |
|----|---------------|--------|--------|----------|----------|
| REC-001 | Standardize .mdc frontmatter metadata | High | Low | P0 | 1 week |
| REC-002 | Create Katas L2-01 and L2-03 | High | Low | P0 | 1 week |
| REC-003 | Add duplicate detection check | Medium | Low | P1 | 3 days |
| REC-004 | Add conflict detection check | Medium | Low | P1 | 5 days |
| REC-005 | Generate AGENTS.md summary | Medium | Low | P1 | 2 days |

---

### REC-001: Standardize .mdc Frontmatter Metadata

**Current State**:
- `.mdc` files have inconsistent frontmatter
- Example `.cursor/rules/100-kata-structure-v2.1.md` has minimal metadata
- No standard schema enforced across rules

**Proposed State**:
Adopt standardized YAML frontmatter schema aligned with industry best practices:

```yaml
---
# REQUIRED FIELDS (fail validation if missing)
id: "[category]-[number]-[short-name]"           # e.g., "pattern-100-repository"
category: "[architecture|pattern|convention|domain|quality|meta|security]"
priority: "[P0|P1|P2]"                           # P0=must follow, P1=should, P2=may
version: "1.0.0"                                 # Semantic versioning

# RECOMMENDED FIELDS (warning if missing)
scope: ["glob/pattern/**/*.ts"]                  # File paths this applies to
enforcement: "[cursor-ai|manual|automated-check]" # How enforced
created: "YYYY-MM-DD"                            # Creation date
author: "[name or team]"                         # Ownership

# OPTIONAL FIELDS (no warning)
rationale_link: "[path to ADR or analysis doc]" # Link to deeper explanation
examples: "[path to example files]"             # Link to code examples
deprecated: false                                # Deprecation flag
deprecated_by: "[rule-id if replaced]"          # Replacement rule
deprecated_date: "YYYY-MM-DD"                   # When deprecated
tags: ["tag1", "tag2"]                          # Searchable tags
related_rules: ["rule-id-1", "rule-id-2"]       # Dependencies/related
evidence_count: 5                                # Number of examples found
frequency: "high"                                # Pattern frequency in codebase
stability_months: 6                              # How long pattern has existed
last_reviewed: "YYYY-MM-DD"                     # Last audit date
---
```

**Benefits**:
1. **Automation-Ready**: Enables tooling (validation scripts, dashboards, conflict detection)
2. **Governance**: Clear ownership, versioning, deprecation tracking
3. **Discoverability**: Tags and categories enable search/filtering
4. **Alignment**: Matches industry standards (Cursor .mdc, AGENTS.md metadata)
5. **Traceability**: Links to analysis documents preserve Dual Traceability pattern

**Implementation Steps**:
1. **Define canonical schema** (2 hours)
   - Create JSON Schema or YAML schema specification
   - Document required vs recommended vs optional fields
   - Add validation rules (format constraints, value enums)

2. **Update existing .mdc files** (4 hours)
   - Audit current files (`.cursor/rules/100-kata-structure-v2.1.md`, `910-rule-management.mdc`)
   - Add missing required/recommended fields
   - Preserve existing content in body

3. **Create validation script** (8 hours)
   - Script: `.specify/scripts/bash/validate-rule-metadata.sh`
   - Validate: YAML syntax, required fields present, value constraints
   - Output: JSON report with errors/warnings
   - Exit code: 0 if valid, 1 if errors, 2 if warnings only

4. **Integrate into CI/CD** (2 hours)
   - Add pre-commit hook (optional, local validation)
   - Add CI check (fail build on validation errors)
   - Document in CONTRIBUTING.md

5. **Update raise.rules.generate** (4 hours)
   - Modify command to generate compliant frontmatter
   - Prompt agent for required fields (author, rationale)
   - Auto-populate: created date, version (1.0.0), id (from pattern name)

**Effort**: **20 hours** (~3 days)

**Risk**: **Low** - Additive change, doesn't break existing rules (though triggers warnings until updated)

**Success Criteria**:
- [ ] All .mdc files pass validation without errors
- [ ] Validation script integrated in CI/CD
- [ ] raise.rules.generate creates compliant rules
- [ ] Documentation updated

**Evidence Sources**:
- Cursor .mdc format (official docs)
- Vercel Agent Skills metadata (github.com/vercel-labs/agent-skills)
- AGENTS.md standard (OpenAI + Sourcegraph proposal)
- aicodingrules.org vendor-agnostic schema

---

### REC-002: Create Missing Katas L2-01 and L2-03

**Current State**:
- `raise.rules.generate` command references "Implements Katas L2-01 and L2-03"
- These Katas do not exist in `docs/framework/v2.1/katas/`
- Broken references reduce command clarity and reproducibility

**Proposed State**:
Create two missing Katas following RaiSE Kata structure v2.1:

#### Kata L2-01: Exploratory Pattern Analysis

```markdown
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

This Kata bridges the gap between brownfield analysis (SAR reports) and rule generation by mining actionable patterns from existing code.

## Contexto

**Cuándo aplicar**:
- After completing `raise.1.analyze.code` (SAR reports available)
- Before running `raise.rules.generate` (to identify rule candidates)
- When team needs to codify implicit conventions

**Cuándo NO aplicar**:
- Greenfield projects (no existing patterns to mine)
- When patterns are already well-documented

## Pasos

### 1. Cargar Reportes SAR

- Load all 7 SAR reports from `specs/main/sar/`
- Focus on:
  - `informe-analisis-codigo-limpio.md` (Clean Code patterns)
  - `informe-analisis-arquitectura-limpia.md` (architecture patterns)
  - `recomendaciones-refactorizacion.md` (improvement opportunities)
- Extract mentioned patterns, anti-patterns, architectural decisions

**Verificación**: At least 5 potential patterns identified from SAR reports

> **Si no puedes continuar**: SAR reports incomplete or missing → **JIDOKA**: Re-run `raise.1.analyze.code` to generate missing reports

### 2. Minar Frecuencia de Patrones en el Código

For each identified pattern:
- Scan codebase for instances using:
  - Grep for naming patterns
  - AST analysis for structural patterns (if tools available)
  - Manual review for complex patterns
- Collect **3-5 positive examples** (correct usage with file paths)
- Collect **2 counter-examples** (violations, anti-patterns)
- Count frequency: pattern appears in X files, Y% of relevant code

**Verificación**: Each pattern has ≥3 positive examples and ≥2 counter-examples

> **Si no puedes continuar**: Pattern too rare (<3 instances) → **JIDOKA**: Discard pattern, not rule-worthy. Pattern ubiquitous (>80% of code) → May be implicit convention, document but low-priority rule.

### 3. Evaluar Criticidad de Patrones

For each pattern with sufficient examples, assess:
- **Criticality**: Does violation cause bugs, security issues, or maintainability problems?
- **Stability**: Has pattern been stable for 2+ months (check git history)?
- **Clarity**: Can pattern be described unambiguously?
- **Enforcement**: Can compliance be checked (manually or automatically)?

Rate each dimension: High/Medium/Low

**Verificación**: Each pattern has criticality assessment documented

> **Si no puedes continuar**: Pattern ambiguous or unstable → **JIDOKA**: Request human clarification or defer until pattern stabilizes

### 4. Documentar Candidatos en Análisis de Patrones

For each validated pattern:
- Create analysis document: `specs/main/analysis/patterns/pattern-[name].md`
- Include:
  - Pattern description (what, why, when)
  - Positive examples (3-5 with file paths)
  - Counter-examples (2 with file paths)
  - Frequency data (X occurrences, Y% of code)
  - Criticality assessment (High/Medium/Low)
  - Stability data (pattern age from git history)
- Use Evidence-Based Claims format (examples + explanation)

**Verificación**: Analysis document created per pattern in `specs/main/analysis/patterns/`

> **Si no puedes continuar**: Unable to write analysis → **JIDOKA**: Review template, ensure examples are concrete

### 5. Priorizar Patrones para Generación de Reglas

Rank patterns by composite score:
- **Score = (Criticality × 3) + (Frequency × 2) + (Clarity × 1)**
- High Criticality = 3, Medium = 2, Low = 1
- High Frequency = 3 (>50% of code), Medium = 2 (20-50%), Low = 1 (<20%)
- High Clarity = 3 (unambiguous), Medium = 2 (needs examples), Low = 1 (vague)

Select **top 1-3 patterns** for immediate rule generation

**Verificación**: Prioritized list exists in `specs/main/analysis/patterns/prioritization.md`

> **Si no puedes continuar**: No clear priorities (all patterns low-score) → **JIDOKA**: Defer to Kata L2-03 to iteratively explore more patterns, or reassess criticality with team

## Output

- **Pattern analysis documents**: `specs/main/analysis/patterns/*.md` (one per pattern)
- **Prioritized list**: `specs/main/analysis/patterns/prioritization.md`

## Validation Gate

N/A (exploratory phase, validated by Kata L2-03 during rule generation)

## Referencias

- `raise.1.analyze.code` command (input: SAR reports)
- `raise.rules.generate` command (output: feeds into this)
- RaiSE Constitution §3: Evidence-Based (3-5 examples required)
- RaiSE Glosario: "Guardrail" (canonical term for rule)
```

#### Kata L2-03: Iterative Rule Extraction

```markdown
---
id: flujo-L2-03-iterative-rule-extraction
nivel: flujo
titulo: "Iterative Rule Extraction from Pattern Analysis"
audience: intermediate
template_asociado: .specify/templates/raise/rules/rule-template-v2.md
validation_gate: .specify/gates/raise/gate-rule-quality.md
prerequisites: [flujo-L2-01-exploratory-pattern-analysis completed]
tags: [rule-generation, iterative-workflow, evidence-based]
version: 1.0.0
---

## Propósito

Guide AI agents through iterative extraction of 1-3 rules per cycle from pattern analysis, ensuring quality via evidence validation and human curation.

This Kata implements RaiSE's Iterative Evolution principle: generate rules incrementally, validate after each, stop if quality insufficient.

## Contexto

**Cuándo aplicar**:
- After Kata L2-01 (pattern analysis complete, prioritized list exists)
- During `raise.rules.generate` execution
- When generating rules from brownfield codebase

**Cuándo NO aplicar**:
- Batch rule generation (anti-pattern, violates Iterative Evolution)
- Without pattern analysis (need evidence first)

## Pasos

### 1. Seleccionar 1-3 Patrones de Priorización

- Load prioritized list from `specs/main/analysis/patterns/prioritization.md`
- Select **top 1-3 patterns** (not more, maintains focus)
- Load analysis documents for selected patterns

**Verificación**: 1-3 patterns selected, analysis documents loaded

> **Si no puedes continuar**: Prioritization list missing → **JIDOKA**: Run Kata L2-01 first

### 2. Generar Regla por Patrón (Iterativo)

For **each selected pattern** (one at a time):

#### 2.1. Check for Duplicate Rules
- Search existing rules in `.cursor/rules/` for similar pattern
- Use: filename similarity, grep for pattern name, metadata tags
- If duplicate found, decide: update existing vs create new

**Verificación**: No duplicate rule exists, or decision made to update existing

> **Si no puedes continuar**: Duplicate found → **JIDOKA**: Update existing rule instead, or justify why new rule needed

#### 2.2. Generate Rule File
- Load template: `.specify/templates/raise/rules/rule-template-v2.md`
- Populate frontmatter using REC-001 schema:
  - `id`: `[category]-[next-number]-[pattern-name]`
  - `category`: infer from pattern (architecture, pattern, convention, domain, quality, security)
  - `priority`: map from criticality (High → P0, Medium → P1, Low → P2)
  - `scope`: glob patterns (infer from examples' file paths)
  - `evidence_count`, `frequency`, `stability_months`: copy from analysis
- Populate body sections:
  - **Purpose**: 1-2 sentence why (from analysis criticality)
  - **Context**: When/where applies (from analysis scope)
  - **Specification**: Do/Don't (from positive/counter-examples)
  - **Examples**: Code snippets (from analysis examples)
  - **Verification**: How to check (manual or automated)
  - **Rationale**: Deeper explanation (link to analysis document)

**Verificación**: Rule file generated with all required sections

> **Si no puedes continuar**: Template missing → **JIDOKA**: Create template first. Examples insufficient → Return to Kata L2-01 to collect more evidence

#### 2.3. Save Rule File Incrementally
- Write rule to: `.cursor/rules/[category]/[id].mdc`
- Create directory if needed
- **Incremental Persistence**: Save immediately (don't wait for batch)

**Verificación**: Rule file exists on disk

> **Si no puedes continuar**: Write failed → **JIDOKA**: Check permissions, directory structure

#### 2.4. Update Governance Registry
- Append entry to `specs/main/ai-rules-reasoning.md`:
  | [id] | [Rule Name] | [Date] | [Goal] | [Link to analysis doc] |
- Format: Markdown table row

**Verificación**: Registry entry added

> **Si no puedes continuar**: Registry update failed → **JIDOKA**: Check file permissions, table format

#### 2.5. Create Analysis Document (Dual Traceability)
- Create: `specs/main/analysis/rules/analysis-for-[pattern-name].md`
- Content:
  - Why this rule exists (rationale)
  - Evidence summary (links to pattern analysis)
  - Examples explained (why these are good/bad)
  - Trade-offs considered
  - Related ADRs or architectural decisions
- This preserves **Dual Traceability**: rule file + analysis doc + registry entry

**Verificación**: Analysis document created and linked from rule file

> **Si no puedes continuar**: Unable to write analysis → **JIDOKA**: Copy from pattern analysis document, add rule-specific rationale

### 3. Validar Calidad de Regla (Quality Gate)

For each generated rule:
- Run validation gate: `.specify/gates/raise/gate-rule-quality.md`
- Check:
  - Frontmatter schema valid (REC-001)
  - Required sections present
  - Examples compile/run (if applicable)
  - Links resolve (to analysis, ADRs)
  - No conflicts with existing rules (REC-004)

**Verificación**: Rule passes quality gate (no errors)

> **Si no puedes continuar**: Validation fails → **JIDOKA**: Fix issues before continuing to next rule. Don't generate more rules until current one is valid.

### 4. Repetir para Patrones Restantes

- If 2-3 patterns selected, repeat Step 2 for each
- Maintain **1 rule at a time** (don't batch)
- Stop if validation fails (Jidoka)

**Verificación**: All selected patterns have rules generated and validated

> **Si no puedes continuar**: Validation failed on rule N → **JIDOKA**: Stop, fix rule N, don't continue to rule N+1

### 5. Actualizar Contexto del Agente

- Run: `.specify/scripts/bash/update-agent-context.sh`
- This indexes new rules for future agent runs

**Verificación**: Agent context updated successfully

> **Si no puedes continuar**: Script failed → **JIDOKA**: Check script permissions, run manually

## Output

- **Rule files**: `.cursor/rules/[category]/[id].mdc` (1-3 files)
- **Analysis documents**: `specs/main/analysis/rules/analysis-for-[name].md` (1-3 files)
- **Registry entries**: `specs/main/ai-rules-reasoning.md` (1-3 new rows)

## Validation Gate

Execute: `.specify/gates/raise/gate-rule-quality.md` after each rule

## Referencias

- Kata L2-01 (prerequisite: pattern analysis)
- `raise.rules.generate` command (implements this Kata)
- RaiSE Constitution §1: Iterative Evolution (1-3 patterns per run)
- RaiSE Constitution §7: Lean/Jidoka (stop if quality insufficient)
- Rule Template v2 (REC-001)
```

**Benefits**:
1. **Resolves Broken References**: `raise.rules.generate` now references valid Katas
2. **Explicit Workflow**: Clear step-by-step process for pattern mining → rule generation
3. **Reproducible**: Any agent can follow Katas to generate rules consistently
4. **Educational**: New team members understand rule generation process
5. **Aligned with RaiSE Principles**: Evidence-Based (§3), Iterative (§1), Jidoka (§7)

**Implementation Steps**:
1. **Write Kata L2-01** (8 hours)
   - Follow RaiSE Kata structure v2.1 (frontmatter + sections)
   - Apply Rule 100 (Kata Structure) validation
   - Include Jidoka blocks for each step

2. **Write Kata L2-03** (8 hours)
   - Similar structure to L2-01
   - Emphasize iterative workflow (1-3 rules per cycle)
   - Reference REC-001 metadata schema

3. **Create rule template v2** (4 hours)
   - Template: `.specify/templates/raise/rules/rule-template-v2.md`
   - Incorporate REC-001 frontmatter schema
   - Include all standard sections (Purpose, Context, Specification, Examples, Verification, Rationale, References)

4. **Create quality gate** (6 hours)
   - Gate: `.specify/gates/raise/gate-rule-quality.md`
   - Validate: frontmatter schema, required sections, examples, links

5. **Update raise.rules.generate** (4 hours)
   - Add explicit references to Kata L2-01 and L2-03 in outline
   - Instruct agent to follow Katas step-by-step
   - Update AI Guidance section

6. **Add to Kata index** (1 hour)
   - Update `docs/framework/v2.1/katas/README.md`
   - Add L2-01 and L2-03 to flujo category

**Effort**: **31 hours** (~1 week)

**Risk**: **Low** - Fills existing gap, no changes to production code

**Success Criteria**:
- [ ] Kata L2-01 and L2-03 exist in `docs/framework/v2.1/katas/`
- [ ] Katas pass Rule 100 (Kata Structure) validation
- [ ] raise.rules.generate references updated Katas
- [ ] Template and gate created
- [ ] Documentation updated

**Evidence Sources**:
- Amazon CodeGuru pattern mining workflow
- Semi-automated extraction (73% acceptance rate)
- RaiSE architectural analysis (gap identified)
- Iterative rule generation best practice

---

### REC-003: Add Duplicate Detection Check

**Current State**:
- `raise.rules.generate` doesn't check if rule already exists
- Risk: duplicate rules for same pattern, developer confusion

**Proposed State**:
Create pre-creation check that searches for duplicate rules before generating new ones.

**Detection Algorithm**:
1. **Filename similarity**: Check if `[pattern-name]` matches existing rule IDs
2. **Content similarity**: Grep existing rules for pattern keywords
3. **Metadata tags**: Search frontmatter tags (if REC-001 implemented)

**Implementation**:
```bash
# Script: .specify/scripts/bash/check-duplicate-rules.sh
#!/bin/bash
# Usage: check-duplicate-rules.sh --pattern "repository-pattern" --category "pattern"

PATTERN_NAME=$1
CATEGORY=$2
RULES_DIR=".cursor/rules/${CATEGORY}"

# Check filename similarity
if ls "${RULES_DIR}"/*"${PATTERN_NAME}"*.mdc 2>/dev/null; then
  echo "WARNING: Similar rule filename found"
  exit 1
fi

# Check content similarity (grep for pattern name in existing rules)
if grep -r -i "${PATTERN_NAME}" "${RULES_DIR}" 2>/dev/null; then
  echo "WARNING: Pattern mentioned in existing rules"
  exit 2
fi

# Check tags (if REC-001 implemented)
if grep -r "tags:.*${PATTERN_NAME}" .cursor/rules/ 2>/dev/null; then
  echo "WARNING: Pattern found in rule tags"
  exit 3
fi

echo "OK: No duplicate found"
exit 0
```

**Integration into raise.rules.generate**:
- Add step in Kata L2-03, section 2.1 "Check for Duplicate Rules"
- Run script before generating rule file
- If duplicate found:
  - Present options: (1) Update existing rule, (2) Create new rule with justification, (3) Cancel
  - Require human decision via AskUserQuestion

**Benefits**:
1. **Prevents Duplicates**: Avoids rule explosion from redundant rules
2. **Improves Discoverability**: Surfaces existing rules that may need updating
3. **Reduces Maintenance**: Fewer rules to audit and update

**Effort**: **8 hours** (~1 day)

**Risk**: **Low** - Additive safety check

**Success Criteria**:
- [ ] Script detects duplicate rules in test cases
- [ ] raise.rules.generate runs script before rule generation
- [ ] Agent asks user decision if duplicate found

**Evidence Sources**:
- Anti-pattern: Rule explosion (100+ rules reported as "overwhelming")
- Best practice: Consolidate related rules (industry consensus)

---

### REC-004: Add Conflict Detection Check

**Current State**:
- No mechanism to detect contradictory rules
- Risk: Rule A says "use X", Rule B says "avoid X" → agent confusion

**Proposed State**:
Create post-creation check that identifies potential conflicts between new rule and existing rules.

**Conflict Detection Heuristics**:
1. **Semantic conflict**: New rule prescribes pattern that existing rule prohibits (e.g., "use Singleton" vs "avoid Singleton")
2. **Scope conflict**: Two rules apply to same files but give different guidance
3. **Priority conflict**: Two P0 rules contradict each other

**Implementation**:
```bash
# Script: .specify/scripts/bash/detect-rule-conflicts.sh
#!/bin/bash
# Usage: detect-rule-conflicts.sh --new-rule ".cursor/rules/pattern/105-new-rule.mdc"

NEW_RULE=$1
NEW_RULE_CATEGORY=$(grep "category:" "$NEW_RULE" | cut -d: -f2 | tr -d ' ')
NEW_RULE_SCOPE=$(grep "scope:" "$NEW_RULE" | cut -d: -f2)

# Extract keywords from new rule (do/don't patterns)
NEW_RULE_PRESCRIBES=$(grep -A 5 "### Do This" "$NEW_RULE" | grep -v "###")
NEW_RULE_PROHIBITS=$(grep -A 5 "### Don't Do This" "$NEW_RULE" | grep -v "###")

# Check if any existing rule prohibits what new rule prescribes
for EXISTING_RULE in .cursor/rules/${NEW_RULE_CATEGORY}/*.mdc; do
  if [ "$EXISTING_RULE" == "$NEW_RULE" ]; then continue; fi

  EXISTING_PROHIBITS=$(grep -A 5 "### Don't Do This" "$EXISTING_RULE" | grep -v "###")

  # Simple keyword overlap check (can be improved with NLP)
  if echo "$EXISTING_PROHIBITS" | grep -q -F "$NEW_RULE_PRESCRIBES"; then
    echo "CONFLICT: $NEW_RULE prescribes pattern that $EXISTING_RULE prohibits"
    exit 1
  fi
done

# Check scope overlap (if both rules apply to same files)
# ... (similar logic for scope checking)

echo "OK: No conflicts detected"
exit 0
```

**Integration into raise.rules.generate**:
- Add to quality gate: `.specify/gates/raise/gate-rule-quality.md`
- Run after rule generation, before registry update
- If conflict detected:
  - Present conflict to user
  - Options: (1) Revise new rule, (2) Revise existing rule, (3) Add exception clause, (4) Proceed with conflict (human override)

**Benefits**:
1. **Prevents Agent Confusion**: Contradictory rules frustrate agents
2. **Improves Rule Quality**: Forces clarification of edge cases
3. **Explicit Precedence**: When conflicts allowed, document precedence rule

**Effort**: **12 hours** (~1.5 days)

**Risk**: **Medium** - False positives possible (heuristic-based detection)

**Success Criteria**:
- [ ] Script detects obvious conflicts in test cases
- [ ] Quality gate runs script after rule generation
- [ ] User prompted to resolve conflicts before completion

**Evidence Sources**:
- Anti-pattern: Conflicting rules (AP-005 in landscape report)
- Cursor community: reports of contradictory rules causing issues
- Best practice: Explicit precedence hierarchies (specific > general)

---

### REC-005: Generate AGENTS.md Summary

**Current State**:
- Rules exist in `.cursor/rules/*.mdc` (Cursor-specific format)
- No cross-tool portable summary
- Other AI tools (Copilot, Codeium) can't consume rules

**Proposed State**:
Auto-generate `AGENTS.md` file at project root with rule summary in universal Markdown format.

**AGENTS.md Format** (OpenAI + Sourcegraph + Google standard):
```markdown
# AI Agent Instructions

This project uses the following conventions and patterns to guide AI code generation.

## Architecture

[Summary of architectural rules from .cursor/rules/architecture/*.mdc]

- **Clean Architecture**: Domain → Application → Infrastructure → Presentation
- **Repository Pattern**: Database access encapsulated in repository classes
- **Dependency Injection**: Use constructor injection for testability

## Patterns

[Summary of pattern rules from .cursor/rules/pattern/*.mdc]

- **Repository Pattern** (`src/data/repositories/`): All database queries go through repositories
- **Factory Pattern** (`src/factories/`): Use factories for complex object creation
- **Observer Pattern** (`src/events/`): Event-driven communication between modules

## Conventions

[Summary of convention rules from .cursor/rules/convention/*.mdc]

- **Naming**: camelCase for functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **File Structure**: One class per file, filename matches class name
- **Imports**: Group imports (stdlib → third-party → local), sort alphabetically

## Testing

[Summary of quality rules from .cursor/rules/quality/*.mdc]

- **Coverage**: Minimum 80% line coverage for new code
- **Test Location**: Tests colocated with code (`src/module/__tests__/`)
- **Test Naming**: `describe('[ClassName]')` and `test('should [behavior]')`

## Security

[Summary of security rules from .cursor/rules/security/*.mdc]

- **Input Validation**: Validate all user input at API boundaries
- **Authentication**: JWT tokens with 15-minute expiry
- **Authorization**: Role-based access control (RBAC) enforced in middleware

---

**For detailed rules, see**: `.cursor/rules/` directory
**Last updated**: [Auto-generated timestamp]
```

**Implementation**:
```bash
# Script: .specify/scripts/bash/generate-agents-md.sh
#!/bin/bash
# Generates AGENTS.md from .cursor/rules/*.mdc files

OUTPUT_FILE="AGENTS.md"
RULES_DIR=".cursor/rules"

cat > "$OUTPUT_FILE" <<EOF
# AI Agent Instructions

This project uses the following conventions and patterns to guide AI code generation.

EOF

# Iterate through categories
for CATEGORY in architecture pattern convention domain quality security meta; do
  CATEGORY_DIR="${RULES_DIR}/${CATEGORY}"
  if [ ! -d "$CATEGORY_DIR" ]; then continue; fi

  echo "## $(echo $CATEGORY | sed 's/.*/\u&/')" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"

  # Extract rule summaries (Purpose section from each .mdc)
  for RULE_FILE in "${CATEGORY_DIR}"/*.mdc; do
    RULE_NAME=$(grep "# Rule:" "$RULE_FILE" | sed 's/# Rule: //')
    RULE_PURPOSE=$(sed -n '/## Purpose/,/## Context/p' "$RULE_FILE" | grep -v "##" | head -n 1)
    echo "- **${RULE_NAME}**: ${RULE_PURPOSE}" >> "$OUTPUT_FILE"
  done

  echo "" >> "$OUTPUT_FILE"
done

echo "---" >> "$OUTPUT_FILE"
echo "**For detailed rules, see**: \`.cursor/rules/\` directory" >> "$OUTPUT_FILE"
echo "**Last updated**: $(date +'%Y-%m-%d')" >> "$OUTPUT_FILE"

echo "✓ Generated $OUTPUT_FILE"
```

**Integration into raise.rules.generate**:
- Add step at end of Kata L2-03: "Regenerate AGENTS.md"
- Run script after all rules generated and validated
- Commit AGENTS.md alongside .mdc files

**Benefits**:
1. **Cross-Tool Compatibility**: AGENTS.md readable by Copilot, Codeium, generic LLMs
2. **Human-Readable Summary**: Developers can quickly review all rules
3. **Standard Compliance**: Aligns with AGENTS.md standard (20K+ repos adoption)
4. **Discoverability**: Single file at project root, easy to find

**Effort**: **6 hours** (~1 day)

**Risk**: **Low** - Additive, doesn't modify existing rules

**Success Criteria**:
- [ ] AGENTS.md generated with correct structure
- [ ] All rule categories included in summary
- [ ] File updated automatically after rule generation
- [ ] AGENTS.md committed to version control

**Evidence Sources**:
- AGENTS.md standard (OpenAI + Sourcegraph + Google proposal, 20K+ repos)
- Cross-tool portability (Copilot can't read .cursorrules, but reads AGENTS.md)
- Radical simplicity principle (single file, plain markdown)

---

## Strategic Improvements (High Impact, High Effort)

| ID | Recommendation | Impact | Effort | Priority | Timeline |
|----|---------------|--------|--------|----------|----------|
| REC-010 | Semi-automated pattern mining | High | High | P1 | 6-8 weeks |
| REC-011 | Rule effectiveness measurement dashboard | Medium | High | P2 | 8-10 weeks |
| REC-012 | Hierarchical rule organization | Medium | Medium | P2 | 4-6 weeks |
| REC-013 | Dynamic context discovery integration | High | High | P1 | 10-12 weeks |
| REC-014 | Agent Skills packaging model | Medium | High | P2 | 12+ weeks |

---

### REC-010: Implement Semi-Automated Pattern Mining

**Current State**:
- `raise.rules.generate` relies on manual pattern identification
- Slow: engineer must scan code, identify patterns, collect examples
- Inconsistent: depends on engineer's experience and biases

**Proposed State**:
Implement semi-automated workflow where AI mines patterns from codebase, proposes rule candidates, and human curates.

**Target**: **73% developer acceptance rate** (Amazon CodeGuru benchmark)

**Architecture**:

```
┌─────────────────────┐
│ Input: Codebase     │
│ + SAR Reports       │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Pattern Mining      │◄─── tree-sitter (AST)
│ Engine              │◄─── grep (text patterns)
│                     │◄─── git log (change clusters)
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Pattern Candidates  │
│ (frequency,         │
│  examples, context) │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ AI Rule Generator   │◄─── GPT-4/Claude
│ (LLM proposes       │
│  rule description)  │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Human Curation      │◄─── Engineer reviews
│ (approve/refine/    │◄─── Adds context
│  reject)            │◄─── Adjusts priority
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ raise.rules.        │
│ generate            │
│ (final rule         │
│  creation)          │
└─────────────────────┘
```

**Implementation Steps**:

#### Phase 1: Pattern Mining Engine (4 weeks)

**Script**: `.specify/scripts/python/mine-patterns.py`

```python
# Pseudo-code
import tree_sitter
import subprocess
import json

def mine_patterns(codebase_path, sar_reports_path):
    patterns = []

    # 1. Analyze SAR reports for mentioned patterns
    sar_patterns = extract_patterns_from_sar(sar_reports_path)
    patterns.extend(sar_patterns)

    # 2. Mine structural patterns via AST (tree-sitter)
    ast_patterns = mine_ast_patterns(codebase_path)
    # Examples: class structures, function signatures, import patterns
    patterns.extend(ast_patterns)

    # 3. Mine naming patterns via grep
    naming_patterns = mine_naming_patterns(codebase_path)
    # Examples: camelCase, PascalCase, file naming conventions
    patterns.extend(naming_patterns)

    # 4. Mine change clusters via git log
    git_patterns = mine_git_patterns(codebase_path)
    # Examples: files frequently changed together (coupling)
    patterns.extend(git_patterns)

    # 5. Score and rank patterns
    scored_patterns = score_patterns(patterns)
    # Score = frequency × criticality × clarity

    return scored_patterns

def extract_patterns_from_sar(sar_path):
    # Parse SAR markdown files, extract pattern mentions
    # Example: "Repository pattern used in data layer"
    pass

def mine_ast_patterns(codebase_path):
    # Use tree-sitter to find recurring AST structures
    # Example: "Classes with constructor DI" (appears 50 times)
    pass

def mine_naming_patterns(codebase_path):
    # Grep for naming conventions
    # Example: "Functions named handle* in event handlers"
    pass

def mine_git_patterns(codebase_path):
    # Analyze git history for change clusters
    # Example: "Files in src/auth/ frequently change together"
    pass

def score_patterns(patterns):
    # Score = (frequency × 2) + (criticality × 3) + (clarity × 1)
    # frequency: how often pattern appears (0-3)
    # criticality: inferred from SAR or defaults to Medium (1-3)
    # clarity: can pattern be described unambiguously (0-3)
    pass
```

**Challenges**:
- **Multi-language support**: tree-sitter parsers for TypeScript, Python, Go, Java, etc.
- **False positives**: Not all frequent patterns are rule-worthy
- **Criticality inference**: Hard to automatically assess criticality

**Mitigation**:
- Start with one language (TypeScript/JavaScript, most common)
- Use conservative thresholds (only mine patterns appearing 5+ times)
- Default criticality to Medium, let human adjust

#### Phase 2: AI Rule Generator (2 weeks)

**Script**: `.specify/scripts/python/generate-rule-description.py`

```python
import anthropic  # or openai

def generate_rule_description(pattern, examples, counter_examples):
    prompt = f"""
    You are a software architect creating a coding rule for a development team.

    Pattern: {pattern['name']}
    Context: {pattern['context']}

    Positive Examples (correct usage):
    {format_examples(examples)}

    Counter-Examples (incorrect usage):
    {format_examples(counter_examples)}

    Generate a rule description with:
    1. Purpose (1-2 sentences: why this rule exists)
    2. Specification (what the rule requires/prohibits)
    3. Rationale (deeper explanation of benefits)

    Use clear, actionable language. Focus on "what" and "why", not "how".
    """

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
```

**Output**: Rule candidate with AI-generated description, ready for human review

#### Phase 3: Human Curation Interface (2 weeks)

**Interactive CLI**: `.specify/scripts/python/curate-rules.py`

```python
def curate_rules(pattern_candidates):
    for pattern in pattern_candidates:
        print(f"\n{'='*60}")
        print(f"Pattern: {pattern['name']}")
        print(f"Frequency: {pattern['frequency']} occurrences")
        print(f"Criticality: {pattern['criticality']} (inferred)")
        print(f"\nAI-Generated Description:")
        print(pattern['ai_description'])
        print(f"\nExamples: {len(pattern['examples'])} positive, {len(pattern['counter_examples'])} negative")

        action = input("\nAction? [a]pprove / [r]efine / [s]kip / [q]uit: ")

        if action == 'a':
            # Approve: create rule via raise.rules.generate
            create_rule(pattern)
        elif action == 'r':
            # Refine: allow editing description, priority, examples
            refined_pattern = refine_pattern(pattern)
            create_rule(refined_pattern)
        elif action == 's':
            # Skip: don't create rule for this pattern
            continue
        elif action == 'q':
            break

def refine_pattern(pattern):
    print("\nRefine pattern:")
    pattern['ai_description'] = input(f"Description [{pattern['ai_description']}]: ") or pattern['ai_description']
    pattern['criticality'] = input(f"Criticality (High/Medium/Low) [{pattern['criticality']}]: ") or pattern['criticality']
    # ... (allow editing other fields)
    return pattern

def create_rule(pattern):
    # Call raise.rules.generate with pattern data
    # Pass as $ARGUMENTS to command
    subprocess.run([
        "raise.rules.generate",
        f"--pattern={pattern['name']}",
        f"--description={pattern['ai_description']}",
        f"--examples={json.dumps(pattern['examples'])}",
        # ... (pass other fields)
    ])
```

**User Experience**:
1. Run `curate-rules.py`
2. Review each pattern candidate (AI-generated description + examples)
3. Approve, refine, or skip
4. For approved patterns, rule automatically generated via raise.rules.generate

**Expected Acceptance Rate**: **70-75%** (targeting Amazon CodeGuru's 73%)

**Benefits**:
1. **60% Faster Rule Creation**: Automation reduces manual scanning time
2. **More Comprehensive**: Mines patterns engineers might miss
3. **Consistent Quality**: AI-generated descriptions follow standard format
4. **Evidence-Based**: Automatically collects examples from codebase
5. **Scalable**: Can analyze large codebases (>100K LOC) efficiently

**Effort**: **8 weeks** (4 weeks mining engine + 2 weeks AI generator + 2 weeks curation interface)

**Risk**: **Medium** - Requires Python development, tree-sitter integration, LLM API costs

**Success Criteria**:
- [ ] Pattern mining script finds 10+ patterns in test codebase
- [ ] AI-generated descriptions are actionable (human review)
- [ ] 70%+ of pattern candidates approved by engineer
- [ ] End-to-end workflow (mining → AI generation → curation → rule creation) works
- [ ] Documentation and user guide created

**Evidence Sources**:
- Amazon CodeGuru: 73% developer acceptance rate for mined rules
- Semi-automated extraction dominates production (landscape report)
- tree-sitter widely used for AST analysis (30K+ stars)
- LLMs effective for rule description generation (qualitative reports)

---

### REC-011: Rule Effectiveness Measurement Dashboard

**Current State**:
- No metrics on rule adherence, violation detection, or code quality impact
- Can't assess if rules are working or need revision
- No data-driven rule retirement decisions

**Proposed State**:
Build dashboard that tracks rule effectiveness metrics and displays insights.

**Metrics to Track**:

1. **Adherence Rate** (primary metric):
   ```
   Adherence % = (Lines of code following rule / Total lines in scope) × 100
   ```
   - Target: >80% for P0 rules, >60% for P1 rules
   - Measurement: Static analysis, AST queries, linting

2. **Violation Detection Rate**:
   ```
   Detection % = (Violations caught in code review / Total violations) × 100
   ```
   - Target: >90% for automated checks, >70% for manual checks
   - Measurement: Code review comments analysis

3. **False Positive Rate**:
   ```
   FP % = (False positives / Total rule invocations) × 100
   ```
   - Target: <10%
   - Measurement: Code review comments flagged as "false alarm"

4. **Code Quality Impact** (secondary metrics):
   - Bug rate in ruled code vs unruled code
   - Maintainability index change
   - Technical debt reduction (from SAR reports over time)

5. **Developer Productivity**:
   - Time saved in code review (fewer rule-violation comments)
   - AI-generated code acceptance rate (with rules vs without)

6. **Rule Health**:
   - Last updated date (flag if >6 months)
   - Usage frequency (flag if 0 violations in 6 months = maybe obsolete)
   - Conflict count (flag if conflicts detected)

**Dashboard Design**:

```
┌─────────────────────────────────────────────────────────────┐
│ Rule Effectiveness Dashboard                                 │
│ Generated: 2026-01-23 | Last Updated: 2026-01-15            │
└─────────────────────────────────────────────────────────────┘

┌─ Summary Statistics ────────────────────────────────────────┐
│ Total Rules: 42                                              │
│ Active Rules: 38 (P0: 12, P1: 20, P2: 6)                   │
│ Deprecated Rules: 4                                          │
│ Average Adherence: 76% (target: 80% for P0, 60% for P1)    │
│ Rules Needing Attention: 5 (see below)                      │
└──────────────────────────────────────────────────────────────┘

┌─ Top Performing Rules ──────────────────────────────────────┐
│ 1. pattern-100-repository        | Adherence: 95% | FP: 2%  │
│ 2. convention-200-naming         | Adherence: 92% | FP: 1%  │
│ 3. architecture-300-clean-arch   | Adherence: 88% | FP: 5%  │
└──────────────────────────────────────────────────────────────┘

┌─ Rules Needing Attention ───────────────────────────────────┐
│ ⚠ pattern-110-singleton          | Adherence: 45% (⬇ target)│
│   Action: Review rule clarity, add examples                 │
│                                                              │
│ ⚠ quality-400-test-coverage      | FP Rate: 18% (⬆ target) │
│   Action: Refine rule to reduce false positives             │
│                                                              │
│ ⚠ convention-210-file-naming     | Last updated: 8 months   │
│   Action: Audit rule, check if still relevant               │
│                                                              │
│ ⚠ security-500-input-validation  | 0 violations (6 months)  │
│   Action: Check if rule obsolete or 100% adopted            │
│                                                              │
│ ⚠ pattern-120-factory vs pattern-125-builder | CONFLICT     │
│   Action: Resolve conflicting guidance                      │
└──────────────────────────────────────────────────────────────┘

┌─ Detailed Rule Breakdown ───────────────────────────────────┐
│ Rule: pattern-100-repository                                 │
│ Category: pattern | Priority: P0 | Version: 1.2.0           │
│ Scope: src/data/repositories/**/*.ts                        │
│                                                              │
│ Metrics (last 30 days):                                     │
│   Adherence Rate: 95% ████████████████████░ (target: 80%)   │
│   Detection Rate: 92% ██████████████████░░░                 │
│   False Positive: 2%  █░░░░░░░░░░░░░░░░░░░ (target: <10%)  │
│                                                              │
│ Trend: ⬆ Improving (was 88% 90 days ago)                   │
│                                                              │
│ Code Quality Impact:                                         │
│   Bug Rate: 0.8 bugs/KLOC (ruled) vs 2.3 (unruled) → 65% ⬇ │
│   Maintainability: 72 (ruled) vs 58 (unruled) → 24% ⬆      │
│                                                              │
│ Actions: ✅ No action needed (healthy rule)                 │
└──────────────────────────────────────────────────────────────┘

[... repeat for each rule ...]

┌─ Rule Health Over Time ─────────────────────────────────────┐
│ Average Adherence Rate (6 months)                           │
│                                                              │
│ 100%│                                     ╭─────────╮        │
│  90%│                   ╭────────────────╯           ╰──     │
│  80%│         ╭────────╯                                     │
│  70%│   ╭────╯                                               │
│  60%│╭─╯                                                     │
│  50%│                                                        │
│     └───────────────────────────────────────────────────     │
│     Aug   Sep   Oct   Nov   Dec   Jan                       │
│                                                              │
│ Observation: Adherence improving as rules mature and        │
│ developers become familiar. Plateau since Dec = need new    │
│ rules or existing rules fully adopted.                      │
└──────────────────────────────────────────────────────────────┘
```

**Implementation**:

#### Phase 1: Metrics Collection (4 weeks)

**Script**: `.specify/scripts/python/collect-rule-metrics.py`

```python
def collect_metrics(rules_dir, codebase_dir, review_data):
    metrics = []

    for rule_file in glob(f"{rules_dir}/**/*.mdc"):
        rule = parse_rule(rule_file)

        # 1. Calculate Adherence Rate
        scope_files = expand_glob(rule['scope'], codebase_dir)
        adherence = calculate_adherence(rule, scope_files)

        # 2. Calculate Detection Rate (from code review data)
        detection = calculate_detection(rule, review_data)

        # 3. Calculate False Positive Rate
        false_positive = calculate_false_positives(rule, review_data)

        # 4. Assess Rule Health
        health = assess_health(rule)

        metrics.append({
            'rule_id': rule['id'],
            'adherence_rate': adherence,
            'detection_rate': detection,
            'false_positive_rate': false_positive,
            'health': health,
            'last_updated': rule['last_reviewed'],
            # ... other metrics
        })

    return metrics

def calculate_adherence(rule, scope_files):
    # Use AST analysis or linting to check rule compliance
    # Example: For repository pattern, check all DB calls go through repos
    total_lines = sum(count_lines(f) for f in scope_files)
    compliant_lines = count_compliant_lines(rule, scope_files)
    return (compliant_lines / total_lines) * 100 if total_lines > 0 else 0

def calculate_detection(rule, review_data):
    # Analyze code review comments mentioning this rule
    # Count: violations caught in review / total violations in code
    # Requires parsing PR comments, commit messages
    pass

def calculate_false_positives(rule, review_data):
    # Analyze comments where reviewer says "false alarm" or overrides rule
    pass

def assess_health(rule):
    # Check: last_updated > 6 months, usage_frequency == 0, conflicts exist
    issues = []
    if rule.get('last_reviewed'):
        months_since_review = (datetime.now() - rule['last_reviewed']).days / 30
        if months_since_review > 6:
            issues.append('stale')
    # ... other checks
    return issues
```

**Challenges**:
- **Adherence calculation**: Requires AST analysis or linting (language-specific)
- **Code review data**: Need to parse PR comments, commit messages (GitHub API, GitLab API)
- **Baseline data**: Initial metrics require historical data (may not exist)

**Mitigation**:
- Start with simple metrics (rule count, last updated date)
- Gradually add complex metrics (adherence, detection) as tools mature
- Use sampling (analyze 10% of codebase) for initial version

#### Phase 2: Dashboard Generation (2 weeks)

**Script**: `.specify/scripts/python/generate-dashboard.py`

```python
def generate_dashboard(metrics, output_file="specs/main/analysis/rule-effectiveness-dashboard.md"):
    # Generate Markdown dashboard with metrics
    # Use ASCII charts for visualizations
    # Highlight rules needing attention

    dashboard = f"""
    # Rule Effectiveness Dashboard

    Generated: {datetime.now().strftime('%Y-%m-%d')}

    ## Summary Statistics

    - Total Rules: {len(metrics)}
    - Average Adherence: {avg_adherence(metrics):.1f}%
    - Rules Needing Attention: {count_attention(metrics)}

    ## Top Performing Rules

    {format_top_rules(metrics, n=5)}

    ## Rules Needing Attention

    {format_attention_rules(metrics)}

    ## Detailed Breakdown

    {format_detailed_breakdown(metrics)}
    """

    with open(output_file, 'w') as f:
        f.write(dashboard)
```

**Output**: Markdown dashboard committed to `specs/main/analysis/rule-effectiveness-dashboard.md`

#### Phase 3: Integration & Automation (2 weeks)

- **CI/CD hook**: Run metrics collection weekly, commit updated dashboard
- **Alerts**: Email/Slack notification when rule needs attention (adherence <50%, FP >20%)
- **Changelog**: Track dashboard changes over time (git history)

**Benefits**:
1. **Data-Driven Decisions**: Retire rules with 0 violations, refine rules with high FP
2. **Continuous Improvement**: Track adherence trends, measure rule impact
3. **Transparency**: Developers see which rules are working, which aren't
4. **ROI Measurement**: Quantify code quality improvements from rules

**Effort**: **8 weeks** (4 weeks metrics collection + 2 weeks dashboard + 2 weeks integration)

**Risk**: **Medium-High** - Complex implementation, requires parsing code and review data

**Success Criteria**:
- [ ] Dashboard generates with summary statistics
- [ ] Top 5 and bottom 5 rules identified correctly
- [ ] Rules needing attention flagged with actionable recommendations
- [ ] Dashboard updates weekly via CI/CD
- [ ] Historical trends visible (6-month chart)

**Evidence Sources**:
- Amazon CodeGuru: Tracks adherence metrics, 70%+ actionability threshold
- Industry best practice: Leading teams measure rule effectiveness
- Cursor: Reports (anecdotally) measuring agent performance with/without rules

---

### REC-012: Hierarchical Rule Organization

**Current State**:
- Rules in `.cursor/rules/` organized by category (flat directories)
- No clear precedence when multiple rules apply to same file
- As rule count grows (toward 50+), flat structure becomes unwieldy

**Proposed State**:
Implement hierarchical organization with explicit precedence:

```
.cursor/rules/
├── global/                          # 10 rules (apply to entire codebase)
│   ├── architecture-001-clean-arch.mdc
│   ├── convention-002-naming.mdc
│   └── quality-003-testing.mdc
│
├── layer/                           # 15 rules (apply to architectural layers)
│   ├── domain/
│   │   ├── pattern-100-entity.mdc
│   │   ├── pattern-101-value-object.mdc
│   │   └── pattern-102-aggregate.mdc
│   ├── application/
│   │   ├── pattern-200-use-case.mdc
│   │   └── pattern-201-dto.mdc
│   └── infrastructure/
│       ├── pattern-300-repository.mdc
│       └── pattern-301-adapter.mdc
│
├── module/                          # 10 rules (apply to specific modules)
│   ├── api/
│   │   ├── pattern-400-rest-endpoint.mdc
│   │   └── security-401-input-validation.mdc
│   └── ui/
│       ├── pattern-500-component.mdc
│       └── convention-501-styling.mdc
│
├── file-type/                       # 5 rules (apply by file extension)
│   ├── test-files.mdc               # scope: **/*.test.ts
│   ├── api-routes.mdc               # scope: **/*.api.ts
│   └── react-components.mdc         # scope: **/*.tsx
│
└── temporal/                        # 2 rules (apply during migrations)
    ├── migration-rest-to-graphql.mdc
    └── migration-js-to-ts.mdc
```

**Precedence Rule**: **More specific overrides more general**
1. Temporal (highest precedence, limited duration)
2. File-Type (applies to specific extensions)
3. Module (applies to specific directories)
4. Layer (applies to architectural layers)
5. Global (lowest precedence, applies everywhere)

**When conflict**: If rule at level N contradicts rule at level N-1, level N wins (specific > general)

**Implementation**:

#### Phase 1: Restructure Existing Rules (2 weeks)

- Audit existing rules in `.cursor/rules/`
- Classify each rule by hierarchy level:
  - Global: Applies to entire codebase
  - Layer: Applies to domain/application/infrastructure/presentation
  - Module: Applies to specific directory (src/api/, src/ui/)
  - File-Type: Applies by extension (*.test.ts, *.tsx)
  - Temporal: Temporary (migration periods)
- Move rules to new hierarchy
- Update `scope` globs to reflect hierarchy

**Example Migration**:
- **Before**: `.cursor/rules/pattern/100-repository.mdc` with `scope: ["src/data/repositories/**/*.ts"]`
- **After**: `.cursor/rules/layer/infrastructure/pattern-300-repository.mdc` with `scope: ["src/infrastructure/**/*.ts"]` (more general, layer-level)

#### Phase 2: Update Metadata with Hierarchy Level (1 week)

Add `hierarchy_level` to frontmatter (extends REC-001):
```yaml
---
id: "pattern-300-repository"
category: "pattern"
priority: "P0"
hierarchy_level: "layer"               # NEW FIELD
hierarchy_path: "infrastructure"       # NEW FIELD (subpath within level)
precedence: 3                          # NEW FIELD (1=global, 5=temporal)
---
```

#### Phase 3: Update Rule Loading Logic (1 week)

Modify how Cursor loads rules:
- Instead of loading all `.mdc` files, load by hierarchy
- For given file `src/infrastructure/data/UserRepository.ts`:
  1. Load global rules (always)
  2. Load layer rules for "infrastructure" layer
  3. Load module rules for "data" module (if exists)
  4. Load file-type rules for "*.ts" (if exists)
- If conflicts, apply precedence (file-type > module > layer > global)

**Note**: This requires Cursor to support hierarchical loading. If not:
- Simulate via `alwaysApply` flag in frontmatter
- Global rules: `alwaysApply: true`
- Specific rules: `alwaysApply: false`, rely on `scope` globs

**Benefits**:
1. **Scales to 50+ Rules**: Clear organization prevents overwhelm
2. **Explicit Precedence**: Resolves conflicts predictably
3. **Easier Navigation**: Developers find relevant rules quickly
4. **Reduced Context**: Agents load only relevant rules per file (reduces token usage)

**Effort**: **4 weeks** (2 weeks restructure + 1 week metadata + 1 week loading logic)

**Risk**: **Medium** - Requires refactoring existing rules, may break backward compatibility

**Success Criteria**:
- [ ] All rules classified and moved to hierarchy
- [ ] Precedence documented in README
- [ ] Test cases validate precedence (specific overrides general)
- [ ] Documentation updated

**Evidence Sources**:
- Hierarchical organization observed in 60% of surveyed repos (landscape report)
- Best practice: Specific overrides general (industry consensus)
- Cursor dynamic context discovery (reduced token usage)

---

### REC-013: Dynamic Context Discovery Integration

**Current State**:
- Cursor loads all rules upfront (static context)
- Token waste: irrelevant rules loaded for every file
- Doesn't scale to 50+ rules (context window limits)

**Proposed State**:
Integrate dynamic context discovery where agent pulls relevant rules on-demand.

**Inspiration**: Cursor's A/B test showed **46.9% token reduction** with dynamic discovery

**Architecture**:

```
┌─────────────────────┐
│ Agent editing       │
│ src/api/users.ts    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Context Discovery   │
│ Agent               │
│                     │
│ Questions:          │
│ - What layer is     │
│   this file in?     │
│ - What patterns     │
│   apply to APIs?    │
│ - Any module-       │
│   specific rules?   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Rule Retrieval      │
│ System              │
│                     │
│ Searches:           │
│ - Hierarchy: layer/ │
│   application       │
│ - Module: api/      │
│ - File-type: *.ts   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Relevant Rules      │
│ (5-10 rules instead │
│  of all 42)         │
│                     │
│ Loaded into context │
└─────────────────────┘
```

**Implementation**:

#### Phase 1: Rule Indexing System (3 weeks)

**Database**: `.cursor/rules/index.json` (auto-generated from .mdc files)

```json
{
  "rules": [
    {
      "id": "pattern-300-repository",
      "file": ".cursor/rules/layer/infrastructure/pattern-300-repository.mdc",
      "hierarchy_level": "layer",
      "hierarchy_path": "infrastructure",
      "category": "pattern",
      "priority": "P0",
      "scope": ["src/infrastructure/**/*.ts"],
      "tags": ["database", "repository", "clean-architecture"],
      "summary": "Encapsulate database access in repository classes",
      "keywords": ["repository", "database", "prisma", "query"]
    },
    // ... other rules
  ],
  "hierarchy_map": {
    "global": ["architecture-001-clean-arch", "convention-002-naming"],
    "layer": {
      "domain": ["pattern-100-entity", "pattern-101-value-object"],
      "application": ["pattern-200-use-case"],
      "infrastructure": ["pattern-300-repository"]
    },
    "module": {
      "api": ["pattern-400-rest-endpoint", "security-401-input-validation"]
    }
  },
  "tag_index": {
    "database": ["pattern-300-repository", "pattern-301-adapter"],
    "testing": ["quality-003-testing", "test-files"]
  }
}
```

**Script**: `.specify/scripts/python/index-rules.py` (regenerates index on rule changes)

#### Phase 2: Rule Retrieval API (4 weeks)

**API**: `.cursor/rules/retrieve-rules` (callable by agent)

```python
def retrieve_rules(file_path, query=None):
    """
    Retrieve relevant rules for given file path and optional query.

    Args:
        file_path: File being edited (e.g., "src/infrastructure/data/UserRepository.ts")
        query: Optional semantic query (e.g., "database access patterns")

    Returns:
        List of relevant rule IDs, ordered by relevance
    """
    index = load_index(".cursor/rules/index.json")
    relevant_rules = []

    # 1. Always include global rules
    relevant_rules.extend(index['hierarchy_map']['global'])

    # 2. Infer layer from file path
    layer = infer_layer(file_path)  # e.g., "infrastructure" from path
    if layer in index['hierarchy_map']['layer']:
        relevant_rules.extend(index['hierarchy_map']['layer'][layer])

    # 3. Infer module from file path
    module = infer_module(file_path)  # e.g., "data" from path
    if module in index['hierarchy_map']['module']:
        relevant_rules.extend(index['hierarchy_map']['module'][module])

    # 4. Match file type
    file_ext = Path(file_path).suffix  # e.g., ".ts"
    for rule in index['rules']:
        if matches_scope(file_path, rule['scope']):
            relevant_rules.append(rule['id'])

    # 5. If query provided, semantic search via embeddings (optional)
    if query:
        query_embedding = embed(query)
        for rule in index['rules']:
            rule_embedding = embed(rule['summary'])
            similarity = cosine_similarity(query_embedding, rule_embedding)
            if similarity > 0.7:
                relevant_rules.append(rule['id'])

    # 6. Deduplicate and rank by precedence
    relevant_rules = deduplicate(relevant_rules)
    relevant_rules = sort_by_precedence(relevant_rules, index)

    return relevant_rules

def infer_layer(file_path):
    # Heuristic: src/domain/ → domain, src/infrastructure/ → infrastructure
    if 'domain' in file_path: return 'domain'
    if 'application' in file_path or 'use-case' in file_path: return 'application'
    if 'infrastructure' in file_path or 'data' in file_path: return 'infrastructure'
    if 'ui' in file_path or 'presentation' in file_path: return 'presentation'
    return None
```

**Integration with Cursor**:
- Cursor agent calls `retrieve-rules` before editing file
- Loads only returned rules (5-10 instead of all 42)
- **Token savings**: 46.9% (Cursor benchmark)

**Fallback**: If Cursor doesn't support API calls, generate per-file rule summaries:
- `.cursor/rules/file-specific/src-infrastructure-data-UserRepository.md`
- Contains only relevant rules for that specific file
- Generated on-demand or via CI/CD

#### Phase 3: Monitoring & Optimization (3 weeks)

- Track: which rules retrieved most often (useful) vs least often (maybe obsolete)
- A/B test: dynamic vs static context (measure code quality, agent performance)
- Optimize: infer_layer heuristics, semantic search thresholds

**Benefits**:
1. **46.9% Token Reduction**: Only load relevant rules (Cursor benchmark)
2. **Scales to 100+ Rules**: Context window no longer a constraint
3. **Faster Agent Response**: Less context to process
4. **Better Agent Focus**: Only sees rules applicable to current file

**Effort**: **10 weeks** (3 weeks indexing + 4 weeks retrieval + 3 weeks optimization)

**Risk**: **High** - Requires Cursor API integration (may not be supported), complex implementation

**Success Criteria**:
- [ ] Rule indexing system generates accurate index
- [ ] Retrieval API returns relevant rules for test files (validated manually)
- [ ] Token usage reduced by 30-50% (measure via Cursor logs)
- [ ] Code quality maintained or improved (no degradation from fewer rules loaded)

**Evidence Sources**:
- Cursor dynamic context discovery: 46.9% token reduction (A/B test)
- RAG-based rule retrieval (emerging pattern in landscape report)
- Context window optimization (universal need as rule sets grow)

---

### REC-014: Agent Skills Packaging Model

**Current State**:
- Rules are project-specific, stored in each project's `.cursor/rules/`
- No sharing mechanism across projects
- Re-create similar rules for each new project (DRY violation)

**Proposed State**:
Implement Agent Skills model (inspired by Vercel's approach) where rules are packaged as reusable, installable "skills".

**Vision**: "npm for AI agents" - install rule packages like `@raise/react-best-practices`, `@raise/clean-architecture`

**Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│ Skill Registry (specs/main/skills/)                          │
│                                                              │
│ - @raise/react-best-practices/                              │
│   - package.json (metadata: name, version, dependencies)    │
│   - rules/ (10 .mdc files for React patterns)              │
│   - README.md (documentation)                               │
│                                                              │
│ - @raise/clean-architecture/                                │
│   - package.json                                            │
│   - rules/ (12 .mdc files for layers, entities, use cases) │
│   - README.md                                               │
│                                                              │
│ - @raise/typescript-conventions/                            │
│   - package.json                                            │
│   - rules/ (8 .mdc files for naming, imports, types)       │
│   - README.md                                               │
└─────────────────────────────────────────────────────────────┘
           │
           │ raise-cli install @raise/react-best-practices
           v
┌─────────────────────────────────────────────────────────────┐
│ Project: my-app                                              │
│                                                              │
│ .cursor/skills.json:                                        │
│ {                                                            │
│   "skills": [                                               │
│     "@raise/react-best-practices@1.2.0",                    │
│     "@raise/typescript-conventions@2.0.1"                   │
│   ]                                                          │
│ }                                                            │
│                                                              │
│ .cursor/rules/ (symlinked or copied from registry)         │
│ ├── react/ (from @raise/react-best-practices)              │
│ └── typescript/ (from @raise/typescript-conventions)        │
└─────────────────────────────────────────────────────────────┘
```

**Skill Package Structure**:

```json
// specs/main/skills/@raise/react-best-practices/package.json
{
  "name": "@raise/react-best-practices",
  "version": "1.2.0",
  "description": "React performance and architecture best practices for AI agents",
  "author": "RaiSE Framework",
  "license": "MIT",
  "main": "rules/",
  "keywords": ["react", "performance", "hooks", "components"],
  "dependencies": {
    "@raise/typescript-conventions": "^2.0.0"
  },
  "peerDependencies": {
    "react": ">=18.0.0"
  },
  "rules": [
    {
      "id": "react-100-component-structure",
      "priority": "P0",
      "category": "pattern"
    },
    {
      "id": "react-101-hooks-usage",
      "priority": "P1",
      "category": "convention"
    }
    // ... 8 more rules
  ]
}
```

**CLI Commands**:

```bash
# Install skill package
raise-cli skills install @raise/react-best-practices

# List installed skills
raise-cli skills list

# Update skill
raise-cli skills update @raise/react-best-practices@1.3.0

# Uninstall skill
raise-cli skills uninstall @raise/react-best-practices

# Create new skill package (interactive)
raise-cli skills create --name "@myorg/custom-rules"

# Publish skill to registry (if shared across team)
raise-cli skills publish @myorg/custom-rules
```

**Implementation**:

#### Phase 1: Skill Registry Structure (2 weeks)

- Create directory: `specs/main/skills/`
- Define package.json schema for skills
- Port existing .cursor/rules/ to 3-4 initial skill packages:
  - `@raise/clean-architecture` (12 rules)
  - `@raise/typescript-conventions` (8 rules)
  - `@raise/testing-best-practices` (5 rules)
  - `@raise/security-guidelines` (6 rules)

#### Phase 2: CLI Tool (6 weeks)

**Script**: `raise-cli` (Python or Bash)

```python
# raise-cli skills install @raise/react-best-practices

def install_skill(skill_name, target_project="."):
    # 1. Resolve skill from registry
    skill_path = f"specs/main/skills/{skill_name}"
    if not Path(skill_path).exists():
        print(f"Error: Skill {skill_name} not found in registry")
        return

    # 2. Load package.json
    package = json.load(open(f"{skill_path}/package.json"))

    # 3. Install dependencies (recursive)
    for dep in package.get('dependencies', []):
        install_skill(dep, target_project)

    # 4. Copy rules to project
    target_rules_dir = f"{target_project}/.cursor/rules/{package['name'].split('/')[-1]}"
    shutil.copytree(f"{skill_path}/rules", target_rules_dir)

    # 5. Update .cursor/skills.json
    skills_json = json.load(open(f"{target_project}/.cursor/skills.json", "r"))
    skills_json['skills'].append(f"{skill_name}@{package['version']}")
    json.dump(skills_json, open(f"{target_project}/.cursor/skills.json", "w"))

    print(f"✓ Installed {skill_name}@{package['version']}")
```

#### Phase 3: Ecosystem Growth (ongoing)

- Document how to create custom skills
- Encourage community contributions (open source skills)
- Curate "official" RaiSE skill packages
- Projected: **150+ skills by EOY 2026** (Vercel trajectory)

**Benefits**:
1. **DRY for Rules**: Share common rules across projects (React, TypeScript, testing)
2. **Faster Project Setup**: `raise-cli skills install @raise/full-stack` → 30 rules in seconds
3. **Versioning**: Update rules across projects (`raise-cli skills update`)
4. **Ecosystem**: Community-contributed skills (like npm packages)
5. **Governance**: Centralized skill registry for organization-wide standards

**Effort**: **12+ weeks** (2 weeks registry + 6 weeks CLI + 4+ weeks ecosystem)

**Risk**: **Medium** - Requires building ecosystem, adoption depends on community

**Success Criteria**:
- [ ] Skill registry with 5+ initial packages
- [ ] CLI tool installs, updates, uninstalls skills
- [ ] Skills work across 3+ test projects
- [ ] Documentation for creating custom skills
- [ ] At least 2 community-contributed skills (external validation)

**Evidence Sources**:
- Vercel Agent Skills: 150+ skills projected by EOY 2026
- "npm for AI agents" model gaining traction
- Industry need: Share rules across projects (landscape report)

---

## Experimental Additions (Medium Impact, Validation Needed)

| ID | Recommendation | Potential Impact | Effort | Priority | Validation |
|----|---------------|------------------|--------|----------|------------|
| REC-020 | Knowledge graph for rule relationships | Medium | Medium | P2 | Pilot study |
| REC-021 | Self-evolving rules (agent updates own rules) | High (long-term) | High | P3 | Experimental |

---

### REC-020: Knowledge Graph for Rule Relationships

**Concept**: Represent rules as nodes in knowledge graph, relationships as edges (depends_on, conflicts_with, supersedes, related_to).

**Potential Benefits**:
- Visualize rule dependencies
- Detect conflicts automatically (graph traversal)
- Suggest related rules when viewing one rule

**Implementation**: Neo4j or similar graph database

**Validation Needed**:
- Does graph visualization help developers understand rule landscape?
- Do agents benefit from graph-based rule retrieval vs simple search?
- Is maintenance overhead (keeping graph updated) worth the benefit?

**Next Step**: **Pilot study with 10 rules** → assess if valuable before full implementation

**Effort**: **6-8 weeks** (if validated)

---

### REC-021: Self-Evolving Rules (Agent Updates Own Rules)

**Concept**: Allow agent to update rules based on "lessons learned" during tasks.

**Example Workflow**:
1. Agent works on tasks, encounters patterns
2. Agent adds to "lessons learned" section in special .cursorrules file
3. After N tasks, agent reviews lessons, proposes rule updates
4. Human approves/rejects proposed updates

**Inspiration**: grapeot/devin.cursorrules (experimental project)

**Potential Benefits**:
- Rules adapt to evolving codebase automatically
- Capture tribal knowledge from agent's experience

**Risks**:
- Agent could learn incorrect patterns without human oversight
- Rules may drift from intended architecture
- Quality control challenging

**Validation Needed**:
- Do agent-proposed rules have acceptable quality (>70% approval rate)?
- How often does agent propose valuable vs noise?
- What guardrails prevent learning incorrect patterns?

**Next Step**: **Experimental branch with strict human review** → assess feasibility before production

**Effort**: **8-12 weeks** (if validated after experiment)

**Status**: **Experimental only** - not recommended for production until validated

---

## Implementation Roadmap

### Phase 1: Quick Wins (Weeks 1-3)

**Parallel Track**:
- REC-001: Standardize .mdc frontmatter (1 week)
- REC-002: Create Katas L2-01 & L2-03 (1 week)
- REC-003: Add duplicate detection (1 day)
- REC-004: Add conflict detection (1.5 days)
- REC-005: Generate AGENTS.md (1 day)

**Deliverables**: Enhanced metadata, missing Katas, basic validation, cross-tool compatibility

**Effort**: **3 weeks** (parallelized)

---

### Phase 2: Strategic Improvements - Round 1 (Weeks 4-13)

**Sequential Track**:
1. REC-010: Semi-automated pattern mining (Weeks 4-11, 8 weeks)
2. REC-012: Hierarchical rule organization (Weeks 12-15, 4 weeks)

**Deliverables**: Pattern mining workflow, hierarchical structure

**Effort**: **12 weeks** (some overlap possible)

---

### Phase 3: Strategic Improvements - Round 2 (Weeks 16-31)

**Parallel Track**:
- REC-011: Rule effectiveness dashboard (Weeks 16-23, 8 weeks)
- REC-013: Dynamic context discovery (Weeks 16-25, 10 weeks)

**Deliverables**: Metrics dashboard, context optimization

**Effort**: **10 weeks** (parallelized)

---

### Phase 4: Ecosystem (Weeks 32+)

**Sequential Track**:
1. REC-014: Agent Skills packaging (Weeks 32-43, 12 weeks)
2. REC-020: Knowledge graph pilot (Weeks 44-49, 6 weeks)

**Deliverables**: Skill registry, CLI tool, experimental graph

**Effort**: **18+ weeks**

---

## Success Metrics

### Quantitative Targets

- **Rule Creation Time**: ⬇ 60% (from 4 hours to 1.5 hours per rule via REC-010)
- **Rule Adherence**: ⬆ 80%+ for P0 rules (measured via REC-011)
- **Context Token Usage**: ⬇ 40% (via REC-013 dynamic discovery)
- **Rule Count**: Maintain **20-50 rules** (Goldilocks zone)
- **False Positive Rate**: ⬇ 10% (via REC-008 quality gates)

### Qualitative Targets

- **Developer Satisfaction**: 4/5 stars for rule quality and relevance (survey)
- **Agent Code Quality**: 70%+ acceptance rate for AI-generated code (code review metrics)
- **Ecosystem Growth**: 10+ shared skill packages by EOY 2026 (REC-014)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Over-engineering** | Start with Quick Wins (REC-001 to REC-005), validate value before Strategic Improvements |
| **Pattern mining false positives** | Conservative thresholds (5+ occurrences), human curation required (73% target) |
| **Context discovery complexity** | Fallback: per-file rule summaries if API integration fails |
| **Ecosystem adoption low** | Focus on internal RaiSE skills first, open source later when proven |
| **Maintenance overhead** | Automate: validation (CI/CD), dashboard (weekly), index (on rule changes) |

---

## Alignment with RaiSE Principles

### Preserved Strengths

- **§1. Iterative Evolution**: ✅ REC-002 (Kata L2-03) enforces 1-3 rules per cycle
- **§2. Governance as Code**: ✅ REC-001 (versioning, metadata), REC-005 (AGENTS.md)
- **§3. Evidence-Based**: ✅ REC-010 (pattern mining with examples), REC-011 (metrics)
- **§7. Lean/Jidoka**: ✅ REC-003 & REC-004 (stop on duplicates/conflicts before generation)

### Enhanced Capabilities

- **§4. Validation Gates**: ⬆ REC-008 (automated quality gates with 70%+ threshold)
- **§8. Observable Workflow**: ⬆ REC-011 (effectiveness dashboard with metrics)

---

## Conclusion

These **15 recommendations** provide a comprehensive roadmap for evolving `raise.rules.generate` from a manual, best-effort tool to a **data-driven, semi-automated, industry-leading rule generation system**.

**Top Priorities**:
1. **REC-001** (metadata) + **REC-002** (Katas) → Resolve immediate gaps
2. **REC-010** (pattern mining) → 60% faster rule creation
3. **REC-011** (dashboard) → Data-driven continuous improvement

**Expected Outcomes**:
- **Faster**: 60% reduction in rule creation time
- **Higher Quality**: 80%+ adherence, <10% false positives
- **Scalable**: Hierarchical organization, dynamic context (supports 100+ rules)
- **Shareable**: Agent Skills model (ecosystem growth)
- **Measurable**: Effectiveness dashboard (data-driven decisions)

By implementing these recommendations systematically (Quick Wins → Strategic → Experimental), RaiSE will establish itself as a **best-in-class framework for AI-aligned code generation rules**.
