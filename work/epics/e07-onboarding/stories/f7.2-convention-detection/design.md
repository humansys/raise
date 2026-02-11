---
story_id: "F7.2"
title: "Convention Detection"
epic_ref: "E7 Onboarding"
story_points: 3
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-05"
updated: "2026-02-05"
template: "lean-feature-spec-v2"
---

# Feature: Convention Detection

> **Epic**: E7 - Onboarding
> **Complexity**: moderate | **SP**: 3

---

## 1. What & Why

**Problem**: When Rai works in a brownfield codebase, it doesn't know the team's conventions. Without this knowledge, AI-generated code introduces inconsistencies — wrong indentation, different naming styles, files in wrong places. This breaks trust immediately.

**Value**: Convention detection enables Rai to respect existing patterns. The detected conventions flow into guardrails.md (F7.3), creating a contract: "I'll follow YOUR conventions." Trust through consistency.

---

## 2. Approach

**How we'll solve it**:

Scan Python source files and infer conventions through majority voting. For each convention category (style, naming, structure), analyze samples and report what's consistent with a confidence score. When the codebase is inconsistent, say so honestly (LOW confidence).

**Scoped for F&F** — detect the obvious stuff well:
- Code style: indentation (spaces/tabs, width)
- Naming: function/class/constant patterns
- Structure: project layout (src/, tests/, common patterns)

**Key design decisions**:
1. **Majority voting** — If 90% of files use 4-space indent, that's the convention
2. **Confidence tiers** — HIGH (>90%), MEDIUM (70-90%), LOW (<70%)
3. **Sample-size awareness** — 3 files = LOW confidence regardless of consistency
4. **Python first** — TypeScript/JS deferred to post-F&F

**Components affected**:
- **`src/rai_cli/onboarding/conventions.py`**: Create — detection logic
- **`src/rai_cli/schemas/conventions.py`**: Create — Pydantic models
- **`tests/onboarding/test_conventions.py`**: Create — unit tests

---

## 3. Interface / Examples

### API Usage

```python
from pathlib import Path
from raise_cli.onboarding.conventions import detect_conventions, ConventionResult

# Detect conventions in a project
result: ConventionResult = detect_conventions(Path("/path/to/project"))

# Access detected conventions
print(result.style.indentation)      # IndentationConvention
print(result.naming.functions)       # NamingConvention
print(result.structure.source_dir)   # str | None
print(result.overall_confidence)     # Confidence.HIGH | MEDIUM | LOW
```

### Expected Output

```python
ConventionResult(
    style=StyleConventions(
        indentation=IndentationConvention(
            style="spaces",
            width=4,
            confidence=Confidence.HIGH,
            sample_count=47,
            consistent_count=45,
        ),
        line_length=LineLengthConvention(
            max_length=88,
            confidence=Confidence.MEDIUM,
            sample_count=47,
        ),
        quote_style=QuoteConvention(
            style="double",
            confidence=Confidence.HIGH,
            sample_count=47,
            consistent_count=44,
        ),
    ),
    naming=NamingConventions(
        functions=NamingConvention(
            pattern="snake_case",
            confidence=Confidence.HIGH,
            sample_count=156,
            consistent_count=152,
        ),
        classes=NamingConvention(
            pattern="PascalCase",
            confidence=Confidence.HIGH,
            sample_count=23,
            consistent_count=23,
        ),
        constants=NamingConvention(
            pattern="UPPER_SNAKE_CASE",
            confidence=Confidence.MEDIUM,
            sample_count=8,
            consistent_count=6,
        ),
    ),
    structure=StructureConventions(
        source_dir="src/rai_cli",
        test_dir="tests",
        has_src_layout=True,
        common_patterns=["schemas/", "cli/commands/"],
    ),
    overall_confidence=Confidence.HIGH,
    files_analyzed=47,
    analysis_time_ms=234,
)
```

### Data Structures

```python
from enum import Enum
from pydantic import BaseModel

class Confidence(str, Enum):
    """Confidence level for a detected convention."""
    HIGH = "high"      # >90% consistency AND >10 samples
    MEDIUM = "medium"  # 70-90% consistency OR 5-10 samples
    LOW = "low"        # <70% consistency OR <5 samples


class IndentationConvention(BaseModel):
    """Detected indentation convention."""
    style: Literal["spaces", "tabs", "mixed"]
    width: int | None  # None if tabs or mixed
    confidence: Confidence
    sample_count: int
    consistent_count: int


class NamingConvention(BaseModel):
    """Detected naming pattern for a symbol type."""
    pattern: Literal["snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"]
    confidence: Confidence
    sample_count: int
    consistent_count: int


class QuoteConvention(BaseModel):
    """Detected string quote style."""
    style: Literal["single", "double", "mixed"]
    confidence: Confidence
    sample_count: int
    consistent_count: int


class LineLengthConvention(BaseModel):
    """Detected line length convention."""
    max_length: int  # 80th percentile of line lengths
    confidence: Confidence
    sample_count: int


class StyleConventions(BaseModel):
    """Code style conventions."""
    indentation: IndentationConvention
    line_length: LineLengthConvention
    quote_style: QuoteConvention


class NamingConventions(BaseModel):
    """Naming conventions by symbol type."""
    functions: NamingConvention
    classes: NamingConvention
    constants: NamingConvention


class StructureConventions(BaseModel):
    """Project structure conventions."""
    source_dir: str | None  # Detected source root (e.g., "src/mypackage")
    test_dir: str | None    # Detected test directory (e.g., "tests")
    has_src_layout: bool    # Whether using src/ layout pattern
    common_patterns: list[str]  # Recurring directory patterns


class ConventionResult(BaseModel):
    """Complete result of convention detection."""
    style: StyleConventions
    naming: NamingConventions
    structure: StructureConventions
    overall_confidence: Confidence
    files_analyzed: int
    analysis_time_ms: int
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `detect_conventions(path)` returns typed `ConventionResult`
- [ ] Detects indentation style (spaces/tabs) and width with confidence
- [ ] Detects naming patterns (snake_case, PascalCase, etc.) for functions, classes, constants
- [ ] Detects project structure (source_dir, test_dir, has_src_layout)
- [ ] Confidence scoring: HIGH (>90% + >10 samples), MEDIUM (70-90% or 5-10), LOW (<70% or <5)
- [ ] >90% test coverage
- [ ] Works correctly on raise-commons (our test case)

### Should Have

- [ ] Quote style detection (single vs double)
- [ ] Line length detection (80th percentile)
- [ ] `common_patterns` identifies recurring directory structures

### Must NOT

- [ ] Must NOT import AST parsing for detection (use regex/file reading — keep it simple)
- [ ] Must NOT auto-correct or suggest fixes (detection only)
- [ ] Must NOT claim HIGH confidence with <5 samples

---

## 5. Algorithm / Logic

### Confidence Calculation

```python
def calculate_confidence(consistent: int, total: int) -> Confidence:
    """
    Calculate confidence based on consistency ratio and sample size.

    Rules:
    1. <5 samples → always LOW (insufficient data)
    2. 5-10 samples → cap at MEDIUM (small sample)
    3. >10 samples → ratio determines:
       - >90% consistent → HIGH
       - 70-90% consistent → MEDIUM
       - <70% consistent → LOW
    """
    if total < 5:
        return Confidence.LOW

    ratio = consistent / total

    if total <= 10:
        # Small sample: cap at MEDIUM even if 100% consistent
        return Confidence.MEDIUM if ratio >= 0.7 else Confidence.LOW

    # Large sample: ratio determines confidence
    if ratio > 0.9:
        return Confidence.HIGH
    elif ratio >= 0.7:
        return Confidence.MEDIUM
    else:
        return Confidence.LOW
```

### Naming Pattern Detection

```python
import re

def classify_name(name: str) -> str:
    """Classify a name into its naming pattern."""
    if re.match(r'^[A-Z][A-Z0-9_]*$', name):
        return "UPPER_SNAKE_CASE"  # CONSTANT_NAME
    if re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
        return "PascalCase"  # ClassName
    if re.match(r'^[a-z][a-z0-9_]*$', name):
        return "snake_case"  # function_name
    if re.match(r'^[a-z][a-zA-Z0-9]*$', name):
        return "camelCase"  # variableName
    return "mixed"
```

### Symbol Extraction (Lightweight)

**IMPORTANT**: Use regex, not AST parsing. We want fast, simple detection.

```python
# Extract function names
FUNCTION_PATTERN = re.compile(r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)

# Extract class names
CLASS_PATTERN = re.compile(r'^class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]', re.MULTILINE)

# Extract module-level constants (UPPER_CASE assignments)
CONSTANT_PATTERN = re.compile(r'^([A-Z][A-Z0-9_]*)\s*[=:]', re.MULTILINE)
```

### Overall Confidence

```python
def calculate_overall_confidence(result: ConventionResult) -> Confidence:
    """
    Overall confidence is the LOWEST of the key conventions.
    If indentation is LOW, overall is LOW (can't trust the detection).
    """
    key_confidences = [
        result.style.indentation.confidence,
        result.naming.functions.confidence,
    ]

    if Confidence.LOW in key_confidences:
        return Confidence.LOW
    if Confidence.MEDIUM in key_confidences:
        return Confidence.MEDIUM
    return Confidence.HIGH
```

---

## 6. Testing Approach

| Test Type | What to Cover |
|-----------|---------------|
| **Unit** | Each detection function independently, confidence calculation edge cases |
| **Integration** | `detect_conventions()` on fixture projects (consistent, inconsistent, minimal) |
| **Real-world** | Run on raise-commons, verify results match known conventions |

**Test Fixtures**:

```
tests/fixtures/conventions/
├── consistent_python/      # Clean project, HIGH confidence expected
│   ├── src/
│   │   └── module.py      # 4-space indent, snake_case, double quotes
│   └── tests/
│       └── test_module.py
├── inconsistent_python/    # Mixed styles, LOW confidence expected
│   └── mixed.py           # 2-space and 4-space, mixed naming
├── minimal_python/         # <5 files, LOW confidence expected
│   └── tiny.py
└── empty_project/          # No Python files
```

**Coverage Target**: >90%

---

## References

**Related ADRs**:
- ADR-001: SAR Pipeline Phases (inspiration for DETECT → SCAN flow)
- ADR-021: Brownfield-First Onboarding

**Related Features**:
- F7.1: `rai init` (creates manifest, calls detection in future)
- F7.3: Governance Generation (consumes conventions to generate guardrails.md)

**Dependencies**:
- F7.1 complete (provides project detection infrastructure)

---

*Design created: 2026-02-05*
*Next: `/story-plan` to decompose into tasks*
