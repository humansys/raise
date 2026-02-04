# Brownfield Governance Bridge: From Facts to Enforcement

**Research ID**: RES-BMAD-BFLD-001-D3
**Date**: 2026-01-27 (Updated -- aligned with SAR v2 Facts-First architecture)
**Status**: Updated
**Supersedes**: Original governance bridge spec (Clean Code/Architecture-based)

---

## Executive Summary

The Governance Bridge transforms **deterministic facts** extracted by tools (ast-grep, ripgrep) and **synthesized understanding** produced by LLM into **enforceable governance artifacts**. This is RaiSE's unique value proposition -- neither BMAD nor any current brownfield analysis tool produces governance-grade output from reproducible evidence.

**Key paradigm shift**: The bridge no longer operates on opinionated SAR reports (Clean Code/Architecture evaluation). It operates on:
- **Layer 1**: `scan-report.json` -- deterministic tool output (ast-grep imports, ripgrep pattern counts)
- **Layer 2**: SAR v2 reports -- LLM-synthesized facts (`conventions-discovered.md`, `consistency-report.md`, `architecture-as-found.md`)
- **Layer 3**: Governance artifacts -- rules, constraints, guardrails extracted from Layers 1-2

**Bridge Purpose**: Convert observed codebase facts into four types of enforceable artifacts:
1. **Conventions → Rules**: Naming patterns, code style, error handling → `.cursorrules`, guardrail files
2. **Architecture → Constraints**: Discovered structure, boundaries, dependency direction → fitness functions
3. **Patterns → Guardrails**: Recurring implementation patterns → enforcement rules with evidence
4. **Inconsistencies → Action Items**: Internal deviations from the codebase's own norms → prioritized remediation

**Key Design Decision**: Confidence-based enforcement. Only findings with >= 80% internal consistency become enforceable rules. Lower-confidence findings become advisory documentation. This prevents false governance -- enforcing rules the codebase itself does not follow.

**What Changed**: The bridge no longer evaluates against external standards (Clean Code, Clean Architecture, SOLID). It extracts the codebase's own conventions and measures internal consistency. "Your codebase says 95% camelCase" is a fact. "Your codebase violates Clean Architecture" is an opinion.

---

## 1. Governance Output Taxonomy

### 1.1 Tier 1: Always Generated

Produced in every SAR v2 analysis.

**1.1.1 project-profile.yaml**

Machine-readable project classification. Generated deterministically by Phase 0 (Detect).

```yaml
# project-profile.yaml
version: "1.0"
generated_date: "2026-01-27T10:30:00Z"
analyzer_version: "raise-sar-v2.0"
scan_method: "deterministic"  # tools, not LLM file reading

project:
  name: "example-api"
  type: "backend"
  structure: "monolith"
  primary_language: "typescript"
  languages:
    typescript: 78%
    javascript: 12%
    yaml: 7%
    other: 3%
  framework: "express"
  runtime: "node-20"

architecture:
  style_observed: "layered"  # what IS, not what should be
  layers_found: ["routes", "controllers", "services", "repositories", "models"]
  entry_points: ["src/index.ts", "src/app.ts"]
  test_framework: "jest"
  orm: "prisma"

metrics:
  files: 234
  loc: 45678
  modules_detected: 12

scan:
  tools_used: ["ast-grep-0.32.3", "ripgrep-15.1"]
  duration_seconds: 187
  deterministic: true  # identical output on repeated runs
```

**Source**: Phase 0 scripts (`phase0-detect.sh`). No LLM interpretation -- pure tool output.

**1.1.2 conventions-discovered.md**

Discovered coding conventions with evidence counts and confidence scores.

```markdown
# Discovered Conventions

## Naming Conventions

### NC-001: Service Classes use PascalCase + "Service" Suffix
- **Confidence**: 95% (38/40 service classes follow pattern)
- **Source**: ast-grep pattern match on `class $NAME { $$$ }` in `src/services/`
- **Evidence**: `scan-report.json` → `patterns.classes` (38 matches)
- **Exceptions**: `src/legacy/auth_handler.ts` (legacy module, snake_case)
- **Governance**: ENFORCE -- high confidence, clear pattern

### NC-002: Database Models use PascalCase Singular
- **Confidence**: 100% (15/15 models follow pattern)
- **Source**: ast-grep pattern match on `class $NAME { $$$ }` in `src/models/`
- **Evidence**: `scan-report.json` → `patterns.classes` (15 matches)
- **Governance**: ENFORCE -- unanimous convention

### NC-003: API Routes use kebab-case
- **Confidence**: 82% (28/34 routes follow pattern)
- **Source**: ripgrep pattern `router\.(get|post|put|delete)\(["']/` across route files
- **Evidence**: `scan-report.json` → `conventions.routing` (28/34)
- **Exceptions**: 6 legacy endpoints using camelCase
- **Governance**: ENFORCE with exceptions noted
```

**Source**: Phase 1 (`scan-report.json` pattern counts) + Phase 2 (LLM synthesizes patterns into named conventions with confidence scoring).

**1.1.3 architecture-as-found.md**

What the architecture IS. No compliance evaluation. No opinions.

Content: Observed architectural style, discovered layers/modules, dependency direction (from ast-grep import analysis), communication patterns found, entry points, key abstractions. Includes Mermaid diagrams generated from dependency-map data.

**What this is NOT**: This is not "how well does this match Clean Architecture." It's "this codebase has 5 layers; dependencies flow inward from routes to models; there are 3 circular dependencies between services."

**Source**: Phase 1 (`scan-report.json` → import graph) + Phase 2 (LLM interprets structure into architectural description).

**1.1.4 sar-index.md**

AI-consumable navigation index.

```markdown
---
name: "Example API"
description: "Backend REST API for order management"
scan_method: "deterministic"
conventions: "./conventions-discovered.md"
architecture: "./architecture-as-found.md"
profile: "./project-profile.yaml"
scan_data: "./scan-report.json"
governance:
  cursorrules: "./.cursorrules"
  guardrails: "./guardrails.yaml"
  inconsistencies: "./inconsistencies.md"
---

# SAR v2 Analysis Index

## Quick Reference
- **Type**: Backend / Express / TypeScript / Monolith
- **Architecture**: Layered (Routes → Controllers → Services → Repositories → Models)
- **Key Convention**: PascalCase services, kebab-case routes
- **Internal Consistency**: 87% (naming: 95%, error handling: 72%, logging: 91%)
- **Top Inconsistency**: Error handling pattern varies across services (72% adoption)

## Navigation
[Links to all generated reports with 1-line summaries]
```

**Source**: Aggregation of metadata from all other artifacts.

### 1.2 Tier 2: On-Request

Generated when user requests governance output (Phase 3 of SAR v2 pipeline).

**1.2.1 .cursorrules / Guardrail Files**

Auto-generated rule files for AI coding assistants. Only contains rules at >= 80% confidence.

```markdown
# Project Rules (Auto-generated from RaiSE SAR v2 Analysis)
# Source: scan-report.json + conventions-discovered.md
# Generated: 2026-01-27 | Deterministic evidence base

## Architecture Rules (from dependency-map.md)
- All database access MUST go through repository classes in `src/repositories/`
- Controllers MUST NOT directly import models or database clients
- Services MUST NOT import Express request/response types

## Naming Rules (from conventions-discovered.md, >= 80% confidence)
- Service classes: PascalCase + "Service" suffix (95% adoption, 38/40)
- Models: PascalCase singular (100% adoption, 15/15)
- Routes: kebab-case (82% adoption, 28/34)

## Pattern Rules (from conventions-discovered.md, >= 80% confidence)
- Error handling: Use custom AppError class with error codes (87% adoption)
- Validation: Use Zod schemas in `src/schemas/` directory (91% adoption)
- Authentication: JWT middleware at router level (100% adoption)

## Known Inconsistencies (DO NOT enforce -- below 80% threshold)
- Logging approach varies: console.log (45%) vs logger (55%) -- no dominant convention
```

**Generation Logic**: Filter `conventions-discovered.md` for confidence >= 80%. Format for target AI tool. Include evidence counts. Explicitly mark what is NOT enforced.

**1.2.2 guardrails.yaml**

Machine-readable constraints for programmatic consumption.

```yaml
version: "1.0"
source: "scan-report.json"
generated: "2026-01-27"

rules:
  - id: "NC-001"
    type: "naming"
    description: "Service classes use PascalCase + Service suffix"
    pattern: "^[A-Z][a-zA-Z]+Service$"
    scope: "src/services/**/*.ts"
    confidence: 0.95
    evidence_count: 38
    total_applicable: 40
    exceptions: ["src/legacy/auth_handler.ts"]
    enforcement: "error"

  - id: "ARCH-001"
    type: "dependency"
    description: "Controllers must not import models directly"
    source_glob: "src/controllers/**"
    forbidden_imports: ["src/models/**", "prisma"]
    confidence: 0.92
    evidence: "dependency-map.md#controller-imports"
    enforcement: "warning"
```

**1.2.3 inconsistencies.md**

Internal deviations -- where the codebase contradicts its own patterns. These are **facts**, not opinions.

```markdown
# Internal Inconsistencies

## INC-001: Error Handling (72% consistency)
- **Dominant pattern**: AppError with error codes (22/30 service methods)
- **Deviation**: 8 methods throw raw errors or don't handle errors
- **Files**: `src/services/PaymentService.ts:45`, `src/services/LegacyAuth.ts:12`, ...
- **Evidence**: `scan-report.json` → `conventions.error_handling`
- **Impact**: Inconsistent error responses to clients; harder onboarding
- **Action**: Align deviating methods to dominant pattern

## INC-002: Logging Approach (55% / 45% split)
- **No dominant pattern**: console.log (55%) vs structured logger (45%)
- **Assessment**: No convention exists. Team should decide.
- **Action**: Team decision needed -- not an inconsistency to fix, but a convention to establish
```

**Key distinction from legacy SAR katas** (which inherited Clean Architecture evaluation from the C# project where they originated): These are not "refactoring recommendations based on Clean Code principles." They are factual observations about where the codebase disagrees with itself. No external standard imposed.

**1.2.4 project-context.md**

Handoff artifact for downstream RaiSE commands.

Contains: Project classification, key architectural facts, discovered conventions, known inconsistencies, and constraints that downstream commands must respect. Designed to be loaded by `raise.1.discovery`, `raise.2.vision`, or any implementation command.

### 1.3 Tier 3: Governance-Mature Teams

Generated on explicit request for teams with established governance practices.

**1.3.1 architecture-fitness.yaml**

Testable constraints extracted from observed architecture.

```yaml
constraints:
  - id: "AF-001"
    name: "Layer Dependency Direction"
    description: "Dependencies flow: Routes → Controllers → Services → Repositories → Models"
    type: "dependency_direction"
    source: "architecture-as-found.md"
    evidence: "dependency-map.md + scan-report.json imports"
    severity: "error"
    note: "Extracted from observed dependency graph, not prescribed"

  - id: "AF-002"
    name: "No Circular Dependencies"
    type: "circular_dependency"
    scope: "all"
    evidence: "scan-report.json → patterns.imports (circular detection)"
    severity: "warning"
    current_violations: 3
    violation_details: "dependency-map.md#circular-deps"
```

**Important**: These constraints are extracted from what the architecture IS, not from what Clean Architecture says it should be. If the codebase has no clear layer structure, this file says so -- it doesn't impose one.

**1.3.2 Brownfield Constitution Seed**

Template constitution pre-populated from analysis findings. Contains project-specific principles, discovered conventions as governance rules, architectural constraints, and quality thresholds derived from the codebase's own norms.

---

## 2. Convention → Rule Pipeline

### 2.1 Convention Detection

**Input Sources (SAR v2)**:
- `scan-report.json` → `patterns` section (ast-grep: imports, exports, classes, functions)
- `scan-report.json` → `conventions` section (ripgrep: naming, error handling, logging, TODOs)
- `conventions-discovered.md` (LLM-synthesized named conventions with evidence)
- `consistency-report.md` (deviations from dominant patterns)

**Detection Algorithm**:
1. Phase 1 tools extract raw pattern counts (deterministic)
2. LLM groups related counts into named conventions
3. For each convention, calculate: `adoption_rate = matches / applicable_locations`
4. Identify exceptions (files/modules that deviate)
5. Record evidence chain: `scan-report.json` line → convention → rule

**What's different from old spec**: Detection no longer sources from "Clean Code Analysis" or "Clean Architecture Analysis." It sources from deterministic tool output (ast-grep import counts, ripgrep pattern matches) interpreted by LLM into named conventions.

### 2.2 Confidence Scoring

Unchanged from original -- this was already aligned with facts-first philosophy.

| Confidence Level | Adoption Rate | Action |
|-----------------|---------------|--------|
| **Unanimous** | 100% | ENFORCE -- hard rule, no exceptions |
| **Strong** | 90-99% | ENFORCE with noted exceptions |
| **Moderate** | 80-89% | ENFORCE with exception list |
| **Weak** | 60-79% | RECOMMEND -- advisory only |
| **Inconsistent** | < 60% | DOCUMENT -- note as area needing team decision |

**Key Principle**: Never enforce a rule the codebase itself does not follow consistently.

### 2.3 Rule Codification Format

Dual format, unchanged from original:

**Human-Readable** (`.cursorrules` / `CLAUDE.md`):
```markdown
## Rule: Service Class Naming [NC-001]
- **Pattern**: PascalCase + "Service" suffix
- **Scope**: All files in `src/services/`
- **Confidence**: 95% (38/40)
- **Source**: scan-report.json → patterns.classes (deterministic)
- **Exceptions**: `src/legacy/auth_handler.ts`
```

**Machine-Readable** (`guardrails.yaml`):
```yaml
- id: "NC-001"
  type: "naming"
  pattern: "^[A-Z][a-zA-Z]+Service$"
  scope: "src/services/**/*.ts"
  confidence: 0.95
  source: "scan-report.json"
  deterministic_evidence: true
```

### 2.4 Exception Handling

Unchanged -- exception types (Legacy, Intentional, Evolving, Third-Party) remain valid and framework-agnostic.

### 2.5 Integration with AI Coding Tools

| Tool | Integration File | Format |
|------|-----------------|--------|
| Cursor | `.cursorrules` | Markdown with sections |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown |
| Claude Code | `CLAUDE.md` | Markdown |
| Generic | `guardrails.yaml` | Machine-readable YAML |

Pipeline generates all applicable formats from `conventions-discovered.md`. Single source of truth.

---

## 3. Architecture → Constraint Pipeline

### 3.1 Architecture Discovery

**Input Sources (SAR v2)**:
- `scan-report.json` → `patterns.imports` (ast-grep: full import/export graph)
- `architecture-as-found.md` (LLM-synthesized architectural description)
- `dependency-map.md` (visualized dependency relationships)

**Discovery Dimensions** (unchanged but reframed):
- **Layers found**: What logical layers exist? (not "do the right layers exist?")
- **Boundaries observed**: What module boundaries are maintained? (not "are they Clean Architecture boundaries?")
- **Communication found**: How do layers/modules communicate? (observed fact)
- **Patterns in use**: What architectural patterns are present? (not "are they the right patterns?")
- **Dependency direction**: Which way do dependencies flow? (graph fact from ast-grep)

### 3.2 Constraint Formalization

Discovered architecture formalized as testable constraints. Unchanged structure, but constraints are extracted from observed facts, not from Clean Architecture compliance:

| Type | Description | Source |
|------|-------------|--------|
| `dependency_direction` | A depends on B but not vice versa | ast-grep import graph |
| `import_restriction` | Module A never imports from Module B | ast-grep negative evidence |
| `circular_dependency` | Circular import chains detected | ast-grep graph analysis |
| `boundary_enforcement` | Access patterns through public API only | ast-grep import paths |
| `pattern_consistency` | All entities of type X follow pattern Y | ripgrep + ast-grep counts |

### 3.3 Fitness Function Design

Unchanged structure. Key reframing: fitness functions test the codebase's own rules, not external standards.

### 3.4 Violation Detection

**MVP (Phase 3 of SAR v2)**: LLM identifies violations from `scan-report.json` data.
**Future**: Tool-based continuous detection (dependency-cruiser, eslint, CI/CD).

---

## 4. Pattern → Guardrail Pipeline

### 4.1 Pattern Mining

**Input Sources (SAR v2)**:
- `scan-report.json` → all pattern sections (deterministic counts)
- `conventions-discovered.md` (LLM-grouped patterns)
- `consistency-report.md` (patterns with low adoption flagged)

**Mining Process**:
1. Phase 1 tools extract pattern counts across the codebase (deterministic)
2. LLM classifies patterns by type: structural, behavioral, integration, testing
3. For each pattern, extract canonical example (highest-confidence instance)
4. Extract counter-example (deviation from pattern)
5. Calculate adoption rate from tool counts

**What changed**: Patterns are mined from deterministic tool output, not from Clean Code/Architecture evaluation. A pattern is "how the codebase does X" not "how Clean Code says to do X."

### 4.2 Guardrail Generation

Each pattern with adoption rate >= 70% becomes a guardrail. Structure unchanged, but evidence chain now traces to `scan-report.json`:

```markdown
# Guardrail: Error Handling Pattern [PT-003]

## Pattern Description
All service methods that can fail wrap errors in AppError with error code.

## Evidence
- **Source**: ripgrep count of `new AppError` in `src/services/` = 26
- **Source**: ripgrep count of `catch` blocks in `src/services/` = 30
- **Adoption**: 87% (26/30)
- **Deterministic**: Yes -- rerun `phase1-scan.sh` to verify

## Canonical Example
[code snippet from highest-adoption module]

## Counter-Example (Deviation)
[code snippet from deviating module]
```

### 4.3 Evidence Linking

Evidence chain now starts from deterministic tool output:

```
Guardrail PT-003
  → scan-report.json line 456 (ripgrep: 26 AppError matches in services/)
  → scan-report.json line 460 (ripgrep: 30 catch blocks in services/)
  → conventions-discovered.md → PT-003 (LLM: 87% adoption, named "AppError Convention")
  → guardrails.yaml → PT-003 (machine-readable rule)
  → .cursorrules → Error Handling section (AI-consumable enforcement)
```

**Audit trail**: Any auditor can rerun `phase1-scan.sh` and verify the counts. The LLM interpretation layer is traceable but the foundation is deterministic.

### 4.4 Evolution Over Time

Unchanged -- guardrails are living artifacts recalculated on each SAR v2 run.

---

## 5. Inconsistency → Action Item Pipeline

**Renamed from "Debt → Recommendation"** to reflect the facts-first philosophy. We don't detect "debt" (which implies a standard being violated). We detect **inconsistencies** (where the codebase contradicts its own patterns).

### 5.1 Inconsistency Detection

**Input Sources (SAR v2)**:
- `scan-report.json` → pattern counts with low adoption (< 80%)
- `consistency-report.md` → named inconsistencies with evidence
- `conventions-discovered.md` → conventions at WEAK or INCONSISTENT confidence

**Inconsistency Categories**:

| Category | Detection Method | Example |
|----------|-----------------|---------|
| Naming inconsistency | ripgrep: multiple naming patterns for same entity type | Services: 38 PascalCase, 2 snake_case |
| Error handling variance | ripgrep: mixed error patterns | 22 AppError, 8 raw throws |
| Import pattern divergence | ast-grep: inconsistent import structure | 80% barrel imports, 20% direct |
| Structural inconsistency | ast-grep: mixed module organization | Some modules have index.ts, others don't |
| Configuration drift | ripgrep: different config approaches | .env in some services, hardcoded in others |
| Test pattern variance | ast-grep + ripgrep: mixed test styles | describe/it in some, test() in others |

### 5.2 Impact Assessment

Each inconsistency is assessed on factual impact dimensions -- no opinions about "code quality":

- **Developer friction**: Does this inconsistency slow down developers? (e.g., "must check which pattern to use each time")
- **Onboarding cost**: Does this confuse new team members? (e.g., "two error handling patterns in same codebase")
- **AI tool confusion**: Does this cause AI coding assistants to generate inconsistent code? (e.g., "Cursor might use either pattern")
- **Merge conflict risk**: Does this cause unnecessary conflicts? (e.g., "different formatting conventions")

### 5.3 Prioritization

Simple priority based on factual signals:

```
Priority = Adoption Gap × Scope
```

Where:
- **Adoption Gap**: Distance from dominant pattern (e.g., 72% = gap of 28%)
- **Scope**: Number of files affected

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 | Gap > 30% AND scope > 20 files | Team decision needed now |
| P1 | Gap > 20% AND scope > 10 files | Address when touching affected code |
| P2 | Gap > 10% OR scope > 5 files | Document for awareness |
| P3 | Small gap or scope | Monitor on next SAR run |

**What's NOT here**: No "business impact" scoring (too subjective for MVP), no urgency ratings, no risk scores. KISS -- adoption gap and scope are measurable facts.

### 5.4 Tracking

On each SAR v2 re-run:
1. Recalculate adoption rates from fresh `scan-report.json`
2. Compare with previous run: improving, stable, or degrading?
3. Resolved inconsistencies move to "aligned" (convention now consistent)
4. New inconsistencies flagged

---

## 6. Integration with RaiSE Ecosystem

### 6.1 → raise.rules.generate

**Input**: `conventions-discovered.md` + `guardrails.yaml`
**Process**: Rule generation command reads extracted conventions, applies RaiSE guardrail format
**Output**: `.raise-kit/rules/` directory with per-convention rule files
**Handoff**: "Convention analysis complete. Run `/raise.rules.generate` to create enforceable rules from 23 detected conventions."

### 6.2 → raise.1.discovery

**Input**: `project-profile.yaml` + `architecture-as-found.md` + `inconsistencies.md`
**Process**: Discovery loads existing project context. PRD creation incorporates existing constraints and known inconsistencies.
**Output**: Brownfield-aware PRD that respects existing architecture.

### 6.3 → raise.2.vision

**Input**: `architecture-as-found.md` + `conventions-discovered.md`
**Process**: Vision considers existing architecture as baseline. Evolution strategy respects current patterns.
**Output**: Brownfield-aware Solution Vision with explicit delta from current state.

### 6.4 → Validation Gates

SAR v2 governance artifacts become gate criteria:

**Gate: Convention Compliance**
- Check: New code follows conventions at >= 80% confidence
- Source: `conventions-discovered.md` + `guardrails.yaml`
- Evidence: Pattern matching on changed files

**Gate: Architecture Consistency**
- Check: New code respects observed dependency direction
- Source: `architecture-as-found.md` + `dependency-map.md`
- Evidence: Import analysis of changed files

**Gate: Inconsistency Prevention**
- Check: New code does not introduce new inconsistencies
- Source: `conventions-discovered.md` (follow dominant pattern)
- Evidence: Pattern matching on new files

---

## References

### RaiSE Framework
- Constitution: `docs/framework/v2.1/model/00-constitution-v2.md`
- Glossary: `docs/framework/v2.1/model/20-glossary-v2.1.md`
- Rule Generation: `.raise-kit/commands/01-onboarding/raise.rules.generate.md`

### SAR v2 Pipeline
- Strategic Decision: `specs/main/research/bmad-brownfield-analysis/strategic-decision-report.md`
- Deterministic Scan Process: `specs/main/research/deterministic-rule-extraction/deterministic-scan-process.md`
- MVP Tooling Selection: `specs/main/research/deterministic-rule-extraction/mvp-tooling-selection.md`

### Industry Standards
- .cursorrules: github.com/PatrickJS/awesome-cursorrules
- dependency-cruiser: github.com/sverweij/dependency-cruiser
- ast-grep: ast-grep.github.io
- ripgrep: github.com/BurntSushi/ripgrep
