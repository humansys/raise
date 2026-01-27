# Deterministic Code Scan Process for LLM Rule Design

**Document Type**: Process Specification
**Date**: 2026-01-24
**Status**: DRAFT
**Goal**: Define a reproducible, deterministic code scan that provides structured data for LLM rule generation

---

## Core Principle

> **Separate deterministic extraction from non-deterministic interpretation.**
>
> - Phase 1: CLI tools extract facts (deterministic)
> - Phase 2: LLM interprets facts and proposes rules (non-deterministic but constrained)
> - Phase 3: Human validates LLM proposals against deterministic evidence

---

## Why BMAD Doesn't Achieve This

| Aspect | BMAD | Deterministic Scan |
|--------|------|-------------------|
| **Extraction** | LLM-powered | CLI tools (ast-grep, ripgrep) |
| **Reproducibility** | Run twice → may differ | Run twice → identical output |
| **Evidence** | Prose descriptions | Structured JSON with counts, locations |
| **Auditability** | "LLM said so" | "12 files match pattern X at lines Y" |
| **Governance** | Medium trust | High trust (verifiable) |

**BMAD's Value**: Great for initial understanding and documentation generation.
**BMAD's Limitation**: Not suitable for governance-grade rule extraction where reproducibility matters.

---

## The Deterministic Scan Pipeline

### Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC SCAN PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT: Brownfield Codebase (no git required)                       │
│                                                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │
│  │ SCAN 1:     │   │ SCAN 2:     │   │ SCAN 3:     │               │
│  │ Structure   │   │ Patterns    │   │ Conventions │               │
│  │ (tree, find)│   │ (ast-grep)  │   │ (ripgrep)   │               │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘               │
│         │                 │                 │                       │
│         ▼                 ▼                 ▼                       │
│  structure.json    patterns.json    conventions.json                │
│                                                                     │
│  ───────────────────────────────────────────────────────────────── │
│                                                                     │
│  AGGREGATION: Merge into scan-report.json                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ scan-report.json                                            │   │
│  │ ├── metadata (timestamp, tool versions, codebase hash)      │   │
│  │ ├── structure (directories, file counts, tech stack)        │   │
│  │ ├── patterns (AST patterns with evidence)                   │   │
│  │ └── conventions (text patterns with evidence)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  OUTPUT: Deterministic, reproducible JSON report                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Scan 1: Structure Analysis

**Purpose**: Understand codebase layout, technology stack, module boundaries.

**Tools**: `tree`, `find`, `wc`, `file`

**Commands**:

```bash
# 1.1 Directory structure (deterministic)
tree -J -L 3 --noreport src/ > structure-tree.json

# 1.2 File type distribution (deterministic)
find src/ -type f -name "*.ts" | wc -l > counts.txt
find src/ -type f -name "*.js" | wc -l >> counts.txt
find src/ -type f -name "*.py" | wc -l >> counts.txt

# 1.3 Module identification (deterministic)
find src/ -maxdepth 2 -type d | sort > modules.txt

# 1.4 Configuration files (deterministic)
find . -maxdepth 2 -name "*.config.*" -o -name "*.json" -o -name "*.yaml" | sort > configs.txt
```

**Output Schema** (`structure.json`):

```json
{
  "scan_type": "structure",
  "timestamp": "2026-01-24T10:30:00Z",
  "tool_versions": {
    "tree": "2.1.0",
    "find": "GNU findutils 4.9.0"
  },
  "codebase_root": "/path/to/codebase",
  "total_files": 342,
  "total_lines": 45230,
  "tech_stack": {
    "primary_language": "typescript",
    "file_distribution": {
      "typescript": 245,
      "javascript": 47,
      "json": 32,
      "yaml": 18
    }
  },
  "modules": [
    {"path": "src/domain", "file_count": 45},
    {"path": "src/infrastructure", "file_count": 67},
    {"path": "src/application", "file_count": 38}
  ],
  "config_files": [
    "tsconfig.json",
    "package.json",
    ".eslintrc.json"
  ]
}
```

**Determinism Guarantee**: Same files → same output (sorted, no timestamps in content).

---

## Scan 2: AST Pattern Analysis

**Purpose**: Extract structural code patterns using AST matching.

**Tool**: `ast-grep (sg)`

**Pattern Categories**:

| Category | Pattern Examples |
|----------|------------------|
| Naming | Class names, function names, variable prefixes |
| Structure | Class inheritance, interface implementation |
| Imports | Import organization, dependency patterns |
| Error Handling | Try-catch patterns, error types |
| Async | Promise patterns, async/await usage |

**Commands**:

```bash
# 2.1 Class naming patterns
sg --pattern 'class $NAME' --json src/ | jq -s '.' > classes.json

# 2.2 Function patterns
sg --pattern 'function $NAME($$$PARAMS) { $$$BODY }' --json src/ > functions.json
sg --pattern 'async function $NAME($$$PARAMS) { $$$BODY }' --json src/ > async-functions.json

# 2.3 Error handling patterns
sg --pattern 'try { $$$TRY } catch ($ERR) { $$$CATCH }' --json src/ > try-catch.json

# 2.4 Import patterns
sg --pattern 'import { $$$IMPORTS } from "$MODULE"' --json src/ > imports.json

# 2.5 Interface/Type patterns (TypeScript)
sg --pattern 'interface $NAME { $$$BODY }' --json src/ > interfaces.json
sg --pattern 'type $NAME = $TYPE' --json src/ > type-aliases.json
```

**Aggregation Script**:

```bash
#!/bin/bash
# aggregate-patterns.sh

echo '{"scan_type": "patterns", "categories": {' > patterns.json

# Class patterns
echo '"classes": {' >> patterns.json
echo '"total":' $(jq 'length' classes.json) ',' >> patterns.json
echo '"by_suffix": {' >> patterns.json
# Count classes ending with common suffixes
for suffix in Repository Service Controller Handler Factory; do
  count=$(jq "[.[] | select(.text | test(\"${suffix}$\"))] | length" classes.json)
  echo "\"$suffix\": $count," >> patterns.json
done
echo '}},' >> patterns.json

# ... repeat for other categories
echo '}}' >> patterns.json
```

**Output Schema** (`patterns.json`):

```json
{
  "scan_type": "patterns",
  "timestamp": "2026-01-24T10:31:00Z",
  "tool_versions": {
    "ast-grep": "0.32.3"
  },
  "categories": {
    "classes": {
      "total": 87,
      "by_suffix": {
        "Repository": 12,
        "Service": 23,
        "Controller": 8,
        "Handler": 15,
        "Factory": 5,
        "Other": 24
      },
      "evidence": [
        {
          "pattern": "class $NAME",
          "matches": 87,
          "sample_files": [
            {"path": "src/domain/UserRepository.ts", "line": 5},
            {"path": "src/domain/OrderService.ts", "line": 3}
          ]
        }
      ]
    },
    "error_handling": {
      "try_catch_count": 45,
      "error_types_used": ["Error", "CustomError", "ValidationError"],
      "patterns": [
        {
          "description": "catch with error logging",
          "count": 38,
          "query": "try { $$$TRY } catch ($ERR) { console.error($$$) }"
        }
      ]
    },
    "async_patterns": {
      "async_functions": 67,
      "await_usage": 234,
      "promise_then_usage": 12
    }
  }
}
```

**Determinism Guarantee**: ast-grep produces identical JSON for identical AST. Sorted output ensures reproducibility.

---

## Scan 3: Convention Analysis

**Purpose**: Extract text-based patterns (naming, comments, documentation).

**Tool**: `ripgrep (rg)`

**Pattern Categories**:

| Category | Pattern Examples |
|----------|------------------|
| Naming Conventions | camelCase, PascalCase, SCREAMING_CASE |
| Comment Patterns | TODO, FIXME, @param, @returns |
| Documentation | JSDoc, inline comments |
| Magic Strings | Hardcoded values, configuration |

**Commands**:

```bash
# 3.1 TODO/FIXME patterns
rg --json 'TODO|FIXME|HACK|XXX' src/ | jq -s '.' > todos.json

# 3.2 Documentation patterns (JSDoc)
rg --json '@param|@returns|@throws|@deprecated' src/ | jq -s '.' > jsdoc.json

# 3.3 Naming convention detection
# camelCase function names
rg --json 'function [a-z][a-zA-Z0-9]*\(' src/ | jq -s '.' > camel-functions.json

# PascalCase class names
rg --json 'class [A-Z][a-zA-Z0-9]*' src/ | jq -s '.' > pascal-classes.json

# SCREAMING_CASE constants
rg --json 'const [A-Z][A-Z0-9_]+ =' src/ | jq -s '.' > screaming-constants.json

# 3.4 Import organization
rg --json "^import .* from ['\"]@/" src/ | jq -s '.' > alias-imports.json
rg --json "^import .* from ['\"]\.\./" src/ | jq -s '.' > relative-imports.json
```

**Output Schema** (`conventions.json`):

```json
{
  "scan_type": "conventions",
  "timestamp": "2026-01-24T10:32:00Z",
  "tool_versions": {
    "ripgrep": "15.0.0"
  },
  "categories": {
    "naming": {
      "functions": {
        "camelCase": {"count": 234, "percentage": 98.3},
        "snake_case": {"count": 4, "percentage": 1.7}
      },
      "classes": {
        "PascalCase": {"count": 87, "percentage": 100}
      },
      "constants": {
        "SCREAMING_CASE": {"count": 45, "percentage": 89},
        "camelCase": {"count": 6, "percentage": 11}
      }
    },
    "documentation": {
      "jsdoc_coverage": {
        "functions_with_jsdoc": 156,
        "total_functions": 234,
        "percentage": 66.7
      },
      "param_tags": 312,
      "returns_tags": 189,
      "throws_tags": 23
    },
    "code_quality_markers": {
      "TODO": {"count": 23, "files": 12},
      "FIXME": {"count": 8, "files": 5},
      "HACK": {"count": 2, "files": 2}
    },
    "import_style": {
      "alias_imports": {"count": 189, "pattern": "@/"},
      "relative_imports": {"count": 45, "pattern": "../"}
    }
  }
}
```

**Determinism Guarantee**: ripgrep with `--json` produces identical output for identical files. Results sorted by file path.

---

## Aggregated Scan Report

**Purpose**: Single JSON document combining all scans for LLM consumption.

**Schema** (`scan-report.json`):

```json
{
  "report_version": "1.0.0",
  "generated_at": "2026-01-24T10:35:00Z",
  "codebase_hash": "sha256:abc123...",  // Hash of all scanned files
  "tool_versions": {
    "ast-grep": "0.32.3",
    "ripgrep": "15.0.0",
    "tree": "2.1.0"
  },
  "scan_parameters": {
    "root_directory": "src/",
    "excluded_patterns": ["node_modules", "dist", "*.test.ts"],
    "languages": ["typescript", "javascript"]
  },
  "structure": { /* from structure.json */ },
  "patterns": { /* from patterns.json */ },
  "conventions": { /* from conventions.json */ },
  "summary": {
    "total_patterns_detected": 15,
    "high_confidence_patterns": 8,
    "medium_confidence_patterns": 5,
    "low_confidence_patterns": 2
  }
}
```

**Determinism Verification**:

```bash
# Run scan twice, compare hashes
./deterministic-scan.sh src/ > scan1.json
./deterministic-scan.sh src/ > scan2.json

# Must be identical
diff scan1.json scan2.json && echo "DETERMINISTIC: Scans match"
```

---

## LLM Rule Design Phase

**After** the deterministic scan, the LLM receives structured evidence:

### LLM Prompt Template

```markdown
# Rule Design Task

You are designing coding rules for a brownfield codebase.

## Deterministic Evidence

The following data was extracted using CLI tools (ast-grep, ripgrep).
This data is **factual and reproducible** - the same codebase will always
produce identical results.

### Structure Summary
- Primary language: TypeScript (245 files)
- Modules: domain (45), infrastructure (67), application (38)

### Pattern Evidence

**Class Naming**:
- 12 classes end with "Repository" (100% in src/domain/)
- 23 classes end with "Service" (87% in src/application/)
- 8 classes end with "Controller" (100% in src/infrastructure/)

**Error Handling**:
- 45 try-catch blocks detected
- 38 (84%) include console.error logging
- Error types: Error, CustomError, ValidationError

**Naming Conventions**:
- Functions: 98.3% camelCase
- Classes: 100% PascalCase
- Constants: 89% SCREAMING_CASE

## Your Task

Based on this **deterministic evidence**, propose rules that:
1. Codify observed patterns with high adoption (>80%)
2. Include specific examples from the evidence
3. Flag potential rule candidates for patterns with medium adoption (50-80%)
4. Note patterns that appear inconsistent (<50%) as anti-patterns to address

## Output Format

For each proposed rule, provide:
- Rule ID
- Description
- Evidence (cite specific numbers from scan)
- Confidence (HIGH/MEDIUM/LOW based on adoption percentage)
- Example code (from scan samples)
- Counter-example (if applicable)
```

### LLM Output Constraints

The LLM **cannot fabricate evidence** because:
1. All numbers come from the deterministic scan
2. All examples come from actual file paths in the scan
3. Human can verify any claim against `scan-report.json`

---

## Comparison: BMAD vs Deterministic Scan

| Aspect | BMAD document-project | Deterministic Scan |
|--------|----------------------|-------------------|
| **Extraction Method** | LLM reads code | CLI tools extract facts |
| **Reproducibility** | LOW (LLM variation) | HIGH (same input → same output) |
| **Evidence Quality** | Prose ("I observed...") | Quantified ("12 files match...") |
| **Auditability** | Difficult | Easy (re-run scan to verify) |
| **Speed** | Slow (full LLM analysis) | Fast (CLI tools) |
| **Token Usage** | High (entire codebase) | Low (structured JSON) |
| **Best For** | Initial understanding | Governance-grade rules |

---

## Hybrid Approach: BMAD + Deterministic Scan

For best results, combine both:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      HYBRID WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: BMAD-Style Discovery (LLM-powered)                        │
│  ──────────────────────────────────────────                         │
│  - Run BMAD document-project for initial understanding              │
│  - Generate architecture overview, identify areas of interest       │
│  - Output: Prose documentation, pattern hypotheses                  │
│                                                                     │
│  PHASE 2: Hypothesis → Query Translation                            │
│  ─────────────────────────────────────────                          │
│  - Take BMAD's prose hypotheses                                     │
│  - Translate to ast-grep/ripgrep queries                            │
│  - Example: "Repository pattern observed" →                         │
│             sg --pattern 'class $NAMERepository' --json             │
│                                                                     │
│  PHASE 3: Deterministic Validation (CLI-powered)                    │
│  ──────────────────────────────────────────────                     │
│  - Run queries to get quantified evidence                           │
│  - Confirm or refute BMAD's hypotheses with numbers                 │
│  - Output: scan-report.json with hard evidence                      │
│                                                                     │
│  PHASE 4: Rule Generation (LLM with evidence)                       │
│  ────────────────────────────────────────────                       │
│  - LLM receives deterministic scan data                             │
│  - Proposes rules grounded in verifiable evidence                   │
│  - Human validates against scan-report.json                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## MVP Implementation

### Script: `deterministic-scan.sh`

```bash
#!/bin/bash
# deterministic-scan.sh - Reproducible codebase pattern extraction
# Usage: ./deterministic-scan.sh <codebase_root> [output_dir]

set -euo pipefail

CODEBASE_ROOT="${1:-.}"
OUTPUT_DIR="${2:-./scan-output}"

mkdir -p "$OUTPUT_DIR"

echo "Starting deterministic scan of $CODEBASE_ROOT..."

# Scan 1: Structure
echo "  [1/3] Analyzing structure..."
./scan-structure.sh "$CODEBASE_ROOT" > "$OUTPUT_DIR/structure.json"

# Scan 2: AST Patterns
echo "  [2/3] Extracting AST patterns..."
./scan-patterns.sh "$CODEBASE_ROOT" > "$OUTPUT_DIR/patterns.json"

# Scan 3: Conventions
echo "  [3/3] Detecting conventions..."
./scan-conventions.sh "$CODEBASE_ROOT" > "$OUTPUT_DIR/conventions.json"

# Aggregate
echo "  Aggregating results..."
./aggregate-scans.sh "$OUTPUT_DIR" > "$OUTPUT_DIR/scan-report.json"

# Compute hash for verification
HASH=$(cat "$OUTPUT_DIR/scan-report.json" | sha256sum | cut -d' ' -f1)
echo "  Scan complete. Hash: $HASH"

# Verify determinism
echo "  Verifying determinism (re-running scan)..."
./scan-structure.sh "$CODEBASE_ROOT" > "$OUTPUT_DIR/verify-structure.json"
if diff -q "$OUTPUT_DIR/structure.json" "$OUTPUT_DIR/verify-structure.json" > /dev/null; then
  echo "  ✓ Determinism verified"
  rm "$OUTPUT_DIR/verify-structure.json"
else
  echo "  ✗ WARNING: Non-deterministic output detected!"
  exit 1
fi

echo ""
echo "Output: $OUTPUT_DIR/scan-report.json"
```

---

## Summary

| Question | Answer |
|----------|--------|
| Does BMAD achieve deterministic extraction? | **No** - it uses LLM analysis |
| What does BMAD provide? | Initial understanding, prose documentation |
| What do we need for governance? | CLI-based deterministic extraction |
| Can we combine them? | **Yes** - BMAD for discovery, CLI for validation |
| What's the output? | `scan-report.json` with quantified evidence |
| How does LLM use it? | Receives evidence, proposes rules, human verifies |

---

## Next Steps

1. **Implement `deterministic-scan.sh`** with the three sub-scans
2. **Create pattern query library** for common patterns (naming, error handling, etc.)
3. **Design LLM prompt template** that constrains rule generation to evidence
4. **Build verification workflow** to confirm LLM proposals against scan data

---

**Document Status**: DRAFT
**Dependencies**: ast-grep 0.32.x, ripgrep 15.x, jq 1.7+, bash 5.x
