---
story_id: "discover-validate-scaling"
title: "Scale discover-validate for brownfield projects"
epic_ref: "Standalone (E13 Discovery improvement)"
story_points: 8
complexity: "complex"
status: "draft"
version: "1.0"
created: "2026-02-07"
updated: "2026-02-07"
template: "lean-feature-spec-v2"
---

# Story: Scale discover-validate for brownfield projects

> **Epic**: Standalone — E13 Discovery improvement
> **Complexity**: complex | **SP**: 8

---

## 1. What & Why

**Problem**: The current `/discover-validate` skill presents 500+ symbols one-by-one for human review. On raise-cli (374 public components), this needed ~37 batches. On brownfield (50-200K lines), it'd need 200-500 batches. The process doesn't scale — and fatigue causes rubber-stamping after ~50 items, making it less reliable than upstream signal quality.

**Value**: A new deterministic CLI tool (`rai discover analyze`) computes confidence scores, auto-categorizes by path conventions, and groups components by module for parallel AI synthesis — reducing AI work by 60-70% and human decisions from O(components) to O(modules). The AI only synthesizes what's genuinely ambiguous. The human only reviews exceptions.

---

## 2. Approach

**How we'll solve it**: Build a deterministic `rai discover analyze` CLI command that takes raw scan output (`ScanResult`) and produces an `AnalysisResult` with confidence-scored, hierarchically-grouped, module-grouped components. Then rewrite the `/discover-scan` and `/discover-validate` skills to use this tool — the scan skill calls `analyze` after scanning, the validate skill processes module groups as parallel batches for AI synthesis with drill-down only on exceptions.

**Components affected**:

| Component | Change | Purpose |
|-----------|--------|---------|
| `src/rai_cli/discovery/analyzer.py` | **Create** | Confidence scoring, hierarchy build, path-based categorization, module grouping |
| `src/rai_cli/cli/commands/discover.py` | **Modify** | Add `rai discover analyze` subcommand |
| `src/rai_cli/output/formatters/discover.py` | **Modify** | Add `format_analyze_result()` formatter |
| `src/rai_cli/discovery/scanner.py` | No change | Existing `ScanResult` is the input |
| `.claude/skills/discover-scan/SKILL.md` | **Modify** | Call `rai discover analyze` after scan |
| `.claude/skills/discover-validate/SKILL.md` | **Rewrite** | Module-level parallel batches with confidence tiers |
| `tests/discovery/test_analyzer.py` | **Create** | Unit tests for analyzer logic |

---

## 3. Interface / Examples

### 3.1 CLI Usage

```bash
# Analyze scan output (pipe from scan)
rai discover scan src/rai_cli --language python --output json | rai discover analyze --output json

# Analyze from file (saved scan output)
rai discover analyze --input scan-result.json --output human

# Analyze with custom path-category mappings
rai discover analyze --input scan-result.json --category-map project-categories.yaml

# Just the summary statistics
rai discover analyze --input scan-result.json --output summary
```

### 3.2 Expected Output (human format)

```
Discovery Analysis
==================

Scanned: 82 files, 516 symbols (156 public, 360 internal)

Confidence Distribution:
  High   (auto-validate): 98 components (62.8%)
  Medium (batch review):  41 components (26.3%)
  Low    (needs review):  17 components (10.9%)

Category Breakdown:
  model:    34  |  service:  22  |  command:  15
  utility:  28  |  parser:   18  |  builder:  12
  schema:   14  |  handler:   8  |  test:      5

Module Groups: 13 modules (for parallel AI synthesis)
  cli/commands/discover.py    8 components (6 high, 2 medium)
  cli/commands/memory.py      5 components (4 high, 1 medium)
  discovery/scanner.py        7 components (5 high, 2 medium)
  discovery/drift.py          4 components (3 high, 1 low)
  context/builder.py          6 components (4 high, 2 medium)
  ...

Saved: work/discovery/analysis.json
```

### 3.3 Expected Output (JSON)

```json
{
  "scan_summary": {
    "files_scanned": 82,
    "total_symbols": 516,
    "public_symbols": 156,
    "internal_symbols": 360,
    "errors": []
  },
  "confidence_distribution": {
    "high": 98,
    "medium": 41,
    "low": 17
  },
  "categories": {
    "model": 34,
    "service": 22,
    "command": 15,
    "utility": 28,
    "parser": 18,
    "builder": 12,
    "schema": 14,
    "handler": 8,
    "test": 5
  },
  "components": [
    {
      "id": "comp-scanner-symbol",
      "name": "Symbol",
      "kind": "class",
      "file": "src/rai_cli/discovery/scanner.py",
      "line": 44,
      "signature": "class Symbol(BaseModel)",
      "module": "raise_cli.discovery.scanner",
      "confidence": {
        "score": 85,
        "tier": "high",
        "signals": {
          "has_docstring": true,
          "docstring_length": 156,
          "has_type_annotations": true,
          "path_matches_convention": true,
          "known_base_class": "BaseModel",
          "name_follows_convention": true
        }
      },
      "auto_category": "model",
      "auto_purpose": "A code symbol extracted from source.",
      "depends_on": ["BaseModel"],
      "internal": false,
      "methods": ["name", "kind", "file", "line", "signature", "docstring", "parent"]
    }
  ],
  "module_groups": {
    "src/rai_cli/discovery/scanner.py": [
      "comp-scanner-symbol",
      "comp-scanner-scanresult",
      "comp-scanner-extract_python_symbols",
      "comp-scanner-scan_directory",
      "comp-scanner-detect_language"
    ],
    "src/rai_cli/discovery/drift.py": [
      "comp-drift-driftwarning",
      "comp-drift-detect_drift"
    ]
  }
}
```

### 3.4 Data Structures

```python
# --- New models in src/rai_cli/discovery/analyzer.py ---

from pydantic import BaseModel, Field
from typing import Literal

ConfidenceTier = Literal["high", "medium", "low"]

class ConfidenceSignals(BaseModel):
    """Deterministic signals used to compute confidence score."""
    has_docstring: bool = False
    docstring_length: int = 0
    has_type_annotations: bool = False
    path_matches_convention: bool = False
    known_base_class: str | None = None
    name_follows_convention: bool = False
    parent_validated: bool = False

class ConfidenceResult(BaseModel):
    """Confidence assessment for a component."""
    score: int = Field(ge=0, le=100)  # 0-100
    tier: ConfidenceTier
    signals: ConfidenceSignals

class AnalyzedComponent(BaseModel):
    """A component enriched with deterministic analysis."""
    id: str
    name: str
    kind: str          # class, function, method, module
    file: str
    line: int
    signature: str
    module: str        # Python module path (dotted)
    confidence: ConfidenceResult
    auto_category: str   # Deterministic category from path/name conventions
    auto_purpose: str    # From docstring (first sentence) if available, else ""
    depends_on: list[str]
    internal: bool
    methods: list[str]   # Method names if kind=class (folded in)
    docstring: str | None

class AnalysisResult(BaseModel):
    """Complete analysis output — deterministic, no AI needed."""
    scan_summary: dict[str, int | list[str]]
    confidence_distribution: dict[str, int]  # tier -> count
    categories: dict[str, int]               # category -> count
    components: list[AnalyzedComponent]
    module_groups: dict[str, list[str]]      # module file path -> component IDs (for parallel AI batches)
```

### 3.5 Path-to-Category Convention Map

```python
# Default conventions (Python projects)
DEFAULT_CATEGORY_MAP: dict[str, str] = {
    "cli/commands/":   "command",
    "cli/":            "utility",      # CLI utilities (non-command)
    "schemas/":        "schema",
    "models/":         "model",
    "output/":         "formatter",
    "governance/":     "parser",
    "context/":        "builder",
    "discovery/":      "service",
    "memory/":         "service",
    "onboarding/":     "service",
    "config/":         "utility",
    "core/":           "utility",
    "telemetry/":      "service",
}

# Name-based category overrides (applied after path match)
NAME_CATEGORY_OVERRIDES: dict[str, str] = {
    "Error":    "exception",   # Classes ending with "Error"
    "Warning":  "exception",   # Classes ending with "Warning"
    "Settings": "config",      # Classes ending with "Settings"
    "Config":   "config",
    "Test":     "test",        # Classes starting with "Test"
    "test_":    "test",        # Functions starting with "test_"
}

# Base class detection for category assignment
BASE_CLASS_CATEGORIES: dict[str, str] = {
    "BaseModel":  "model",
    "Exception":  "exception",
    "BaseSettings": "config",
    "TypedDict":  "schema",
}
```

### 3.6 Confidence Scoring Algorithm

```python
def compute_confidence(symbol: Symbol, path_category: str | None) -> ConfidenceResult:
    """Deterministic confidence scoring. No AI, no heuristics — only facts."""
    score = 0
    signals = ConfidenceSignals()

    # Signal 1: Has docstring (+30)
    if symbol.docstring:
        signals.has_docstring = True
        signals.docstring_length = len(symbol.docstring)
        score += 30
        # Bonus for substantial docstring (+10)
        if len(symbol.docstring) > 20:
            score += 10

    # Signal 2: Has type annotations in signature (+10)
    if "->" in symbol.signature or ": " in symbol.signature:
        signals.has_type_annotations = True
        score += 10

    # Signal 3: Path matches a known convention (+20)
    if path_category:
        signals.path_matches_convention = True
        score += 20

    # Signal 4: Known base class in signature (+10)
    for base_class in BASE_CLASS_CATEGORIES:
        if base_class in symbol.signature:
            signals.known_base_class = base_class
            score += 10
            break

    # Signal 5: Name follows convention (+5)
    if symbol.kind == "class" and symbol.name[0].isupper():
        signals.name_follows_convention = True
        score += 5
    elif symbol.kind in ("function", "method") and symbol.name.islower():
        signals.name_follows_convention = True
        score += 5

    # Signal 6: Parent class context (+15) — methods inherit parent confidence
    if symbol.parent:
        signals.parent_validated = True
        score += 15

    # Tier assignment
    tier: ConfidenceTier
    if score >= 70:
        tier = "high"
    elif score >= 40:
        tier = "medium"
    else:
        tier = "low"

    return ConfidenceResult(score=score, tier=tier, signals=signals)
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `rai discover analyze` command accepts JSON scan output (stdin or `--input`)
- [ ] Confidence scoring produces deterministic results (same input = same output)
- [ ] Components scored into three tiers: high (>=70), medium (40-69), low (<40)
- [ ] Path-based auto-categorization maps file paths to categories
- [ ] Hierarchical folding: methods grouped under parent class as single unit
- [ ] Module grouping: components grouped by source file for parallel AI synthesis batches
- [ ] Output formats: `human`, `json`, `summary` (consistent with other discover commands)
- [ ] `/discover-scan` skill updated to call `rai discover analyze` after scanning
- [ ] `/discover-validate` skill rewritten with module-level parallel batches and confidence tiers
- [ ] All new code has >90% test coverage
- [ ] Validated on raise-cli's own codebase (human decisions reduced by >70% vs total components)

### Should Have

- [ ] Custom category map via `--category-map` YAML file
- [ ] Auto-purpose extraction (first sentence of docstring) for high-confidence components

### Must NOT

- [ ] **MUST NOT** require AI inference for confidence scoring — all signals are deterministic
- [ ] **MUST NOT** change `ScanResult` or `Symbol` models — analyzer consumes existing output
- [ ] **MUST NOT** break existing `rai discover scan`, `build`, or `drift` commands

---

<details>
<summary><h2>5. Detailed Scenarios</h2></summary>

### Scenario 1: High-confidence component (auto-validate)

```gherkin
Given a scanned class "Symbol" with a docstring, type annotations, and file path "discovery/scanner.py"
When the analyzer scores it
Then confidence score is >= 70 (tier: "high")
And auto_category is "model" (from BaseModel in signature)
And auto_purpose is "A code symbol extracted from source." (first sentence of docstring)
And this component can be auto-validated without AI synthesis
```

### Scenario 2: Low-confidence component (needs human)

```gherkin
Given a scanned function "helper" with no docstring, no type annotations, in "core/utils.py"
When the analyzer scores it
Then confidence score is < 40 (tier: "low")
And auto_category is "utility" (from path convention)
And auto_purpose is "" (no docstring)
And this component is flagged for individual human review
```

### Scenario 3: Method folding into parent class

```gherkin
Given a class "UnifiedGraph" with 12 methods extracted as separate symbols
When the analyzer builds the hierarchy
Then the class and its methods become 1 unit (not 13)
And the unit's methods list contains all 12 method names
And the unit's confidence score accounts for the full class
```

### Scenario 4: Module grouping for parallel AI synthesis

```gherkin
Given 28 symbols from 3 files in the "discovery/" directory
When the analyzer groups components by module
Then module_groups contains 3 entries (one per file)
And each entry maps the file path to its component IDs
And the skill can process each module group as a parallel AI batch
```

### Scenario 5: Pipe from scan command

```gherkin
Given the user runs "raise discover scan src/ -l python -o json | rai discover analyze"
When the analyzer receives JSON on stdin
Then it parses the ScanResult JSON correctly
And produces the full AnalysisResult
And writes to work/discovery/analysis.json by default
```

</details>

---

<details>
<summary><h2>6. Algorithm / Logic</h2></summary>

### Analysis Pipeline

```python
def analyze(scan_result: ScanResult, category_map: dict[str, str] | None = None) -> AnalysisResult:
    """
    Deterministic analysis pipeline. No AI, no network calls.
    Input: ScanResult from rai discover scan
    Output: AnalysisResult with confidence, categories, hierarchy, module groups
    """
    categories = category_map or DEFAULT_CATEGORY_MAP

    # Step 1: Separate public vs internal
    public = [s for s in scan_result.symbols if not s.name.startswith("_")]
    internal = [s for s in scan_result.symbols if s.name.startswith("_")]

    # Step 2: Hierarchical folding — group methods under parent classes
    units = build_hierarchy(public)
    # Result: list of AnalyzedComponent where kind="class" includes methods list

    # Step 3: Confidence scoring — deterministic per unit
    for unit in units:
        path_category = match_path_category(unit.file, categories)
        unit.confidence = compute_confidence(unit, path_category)
        unit.auto_category = determine_category(unit, path_category)
        unit.auto_purpose = extract_first_sentence(unit.docstring)

    # Step 4: Group by module file (for parallel AI synthesis batches)
    module_groups = group_by_module(units)

    # Step 5: Aggregate statistics
    return AnalysisResult(
        scan_summary={...},
        confidence_distribution=count_by_tier(units),
        categories=count_by_category(units),
        components=units,
        module_groups=module_groups,
    )
```

### Hierarchy Build

```python
def build_hierarchy(symbols: list[Symbol]) -> list[AnalyzedComponent]:
    """
    Fold methods into their parent classes.
    Classes become units with methods list.
    Standalone functions remain individual units.
    """
    classes: dict[str, list[Symbol]] = {}   # class_name -> methods
    class_symbols: dict[str, Symbol] = {}   # class_name -> class symbol

    for s in symbols:
        if s.kind == "class":
            class_symbols[s.name] = s
            classes.setdefault(s.name, [])
        elif s.kind == "method" and s.parent:
            classes.setdefault(s.parent, []).append(s)

    units = []
    seen_methods = set()

    # Create class units (with methods folded in)
    for class_name, class_sym in class_symbols.items():
        methods = classes.get(class_name, [])
        unit = AnalyzedComponent(
            ...class_sym fields...,
            methods=[m.name for m in methods],
        )
        units.append(unit)
        seen_methods.update(m.name for m in methods)

    # Add standalone functions and modules
    for s in symbols:
        if s.kind in ("function", "module"):
            units.append(AnalyzedComponent(...s fields..., methods=[]))

    return units
```

### Module Grouping

```python
def group_by_module(units: list[AnalyzedComponent]) -> dict[str, list[str]]:
    """
    Group component IDs by their source module file.
    Each module group = one batch for parallel AI synthesis.
    """
    groups: dict[str, list[str]] = {}
    for unit in units:
        groups.setdefault(unit.file, []).append(unit.id)
    return groups
```

**Rationale**: Module-based grouping is the natural semantic boundary. Each module group becomes a parallel AI synthesis batch in the `/discover-validate` skill. Confidence-based filtering reduces AI workload by 60-70%. Hierarchical folding reduces unit count by ~40%.

**Alternatives considered**:
- Token-estimated chunking with overflow splitting: Over-engineered — module boundaries are sufficient
- Import-graph clustering: Non-deterministic, complex, not needed
- Skills-only approach: No deterministic testing, no reproducibility

**Complexity**: O(n) for scoring and grouping, where n = number of symbols

</details>

---

<details>
<summary><h2>7. Constraints</h2></summary>

| Type | Constraint | Rationale |
|------|------------|-----------|
| **Determinism** | Same scan input must always produce same analysis output | Testable, reproducible — core RaiSE principle |
| **Performance** | Analysis of 2000 symbols must complete in <2 seconds | Instant feedback for developer |
| **Compatibility** | Consumes existing `ScanResult` JSON schema unchanged | No breaking changes to scan pipeline |
| **Python 3.12+** | Use modern type syntax (PEP 604 unions, etc.) | Aligned with project guardrails |

</details>

---

<details>
<summary><h2>8. Testing Approach</h2></summary>

| Test Type | What to Cover | Tooling |
|-----------|---------------|---------|
| **Unit** | `compute_confidence()` — all signal combinations, boundary scores (39/40/69/70) | pytest |
| **Unit** | `build_hierarchy()` — method folding, orphan methods, standalone functions | pytest |
| **Unit** | `match_path_category()` — all default mappings, custom map, no match | pytest |
| **Unit** | `group_by_module()` — single module, multi-module, empty list | pytest |
| **Unit** | `extract_first_sentence()` — docstrings with periods, multiline, None | pytest |
| **Integration** | Full pipeline: `ScanResult` → `AnalysisResult` with realistic data | pytest + fixtures |
| **Integration** | CLI command: stdin pipe, `--input` file, `--output` formats | pytest + typer.testing |
| **Dogfood** | Run on raise-cli's own codebase, verify confidence distribution matches expectations | Manual |

**Test fixtures**: Use raise-cli's actual scan output (516 symbols) as integration test data.

**Coverage target**: >90% for `analyzer.py`

</details>

---

## References

**Research**:
- RES-CHUNK-STRATEGY-001: Semantic chunking strategies (this session)
- Evidence from Aider (repo-map), Cursor (AST chunking), cAST (EMNLP 2025), Continue.dev, code-chunk

**Related**:
- Current architecture report: `work/stories/discover-validate-scaling/current-architecture.md`
- ADR-012: Skills + Toolkit Architecture
- E13 Discovery scope: `work/epics/e13-discovery/scope.md`

**Dependencies**:
- Existing `rai discover scan` command (no changes needed)
- `ScanResult` and `Symbol` Pydantic models (unchanged)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-07
