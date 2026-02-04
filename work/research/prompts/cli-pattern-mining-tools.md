# Deep Research: CLI Pattern Mining Tools for Deterministic Rule Extraction

**Role**: Senior DevTools Engineer specializing in Static Analysis and Code Intelligence
**Objective**: Produce a comprehensive comparative analysis of CLI tools for extracting code patterns from brownfield codebases, with selection criteria for RaiSE framework integration.

---

## Meta-Instructions for Reasoning

1. **Evidence Hierarchy**: Prioritize empirical benchmarks > documented case studies > expert opinion > theoretical claims
2. **Falsifiability**: For each tool recommendation, state conditions under which it would be wrong
3. **Trade-off Transparency**: Every tool has downsides—document them explicitly
4. **Reproducibility Focus**: Favor tools that produce deterministic, reproducible outputs
5. **CLI-First**: We need tools that can be invoked from command line by AI agents, not GUI-based tools

---

## Research Questions

### 1. AST-Based Pattern Mining Tools

**Primary Question**: What CLI tools use Abstract Syntax Trees for reliable pattern extraction?

Investigate:
- **tree-sitter**: Capabilities, language support, query syntax, performance benchmarks
- **ast-grep (sg)**: Pattern matching syntax, comparison to tree-sitter, use cases
- **semgrep**: Rule-based pattern matching, accuracy metrics, false positive rates
- **comby**: Structural code search, language support, reliability
- **srcML**: XML-based AST representation, tooling ecosystem

For each tool, document:
- Installation and setup complexity
- Query/pattern syntax (with examples)
- Language support breadth
- Output format (JSON, YAML, custom)
- Performance on large codebases (>100K LOC)
- Determinism guarantees (same input → same output?)
- Maintenance status and community health

**Deliverable**: Comparison matrix with quantitative metrics where available.

### 2. Text-Based Pattern Mining Tools

**Primary Question**: What text-based CLI tools are effective for pattern discovery?

Investigate:
- **ripgrep (rg)**: Regex capabilities, performance, structured output (--json)
- **grep/egrep**: POSIX compatibility, limitations
- **ack**: Code-aware searching, language filters
- **ag (The Silver Searcher)**: Performance characteristics
- **ugrep**: Modern features, structured output

For pattern discovery specifically:
- Naming convention detection (PascalCase, snake_case patterns)
- Import/dependency pattern extraction
- Comment/documentation pattern analysis
- Configuration file pattern matching

**Deliverable**: Use case matrix showing which tool excels at which pattern type.

### 3. Git History Analysis Tools

**Primary Question**: What tools extract patterns from version control history?

Investigate:
- **git log** with custom formatting
- **git diff** for change pattern analysis
- **gitinspector**: Code contribution analysis
- **git-quick-stats**: Repository statistics
- **hercules/labours**: ML-based git analysis
- **git-of-theseus**: Codebase evolution visualization

Focus on:
- Identifying frequently co-changed files (coupling patterns)
- Finding stable vs volatile code regions
- Extracting commit message patterns (conventions)
- Detecting refactoring patterns in history

**Deliverable**: Workflow examples showing git-based pattern extraction.

### 4. Static Analysis Tools with CLI Interface

**Primary Question**: Which static analysis tools provide CLI-accessible pattern data?

Investigate:
- **ESLint** (JavaScript/TypeScript): Custom rule creation, pattern detection
- **Pylint/flake8** (Python): Plugin architecture, custom checkers
- **golangci-lint** (Go): Linter aggregation, custom linters
- **RuboCop** (Ruby): Pattern-based cops
- **PMD**: Multi-language, ruleset customization
- **SonarQube CLI (sonar-scanner)**: Quality gate integration

For each:
- Can it detect custom patterns (not just violations)?
- What's the output format?
- Can patterns be exported as rules?
- Integration with CI/CD pipelines

**Deliverable**: Assessment of pattern detection vs violation detection capabilities.

### 5. Specialized Code Intelligence Tools

**Primary Question**: What emerging tools offer advanced pattern mining?

Investigate:
- **Sourcegraph CLI (src)**: Code search at scale, structural search
- **GitHub Code Search**: API capabilities, pattern queries
- **OpenGrok**: Cross-reference and search
- **Kythe**: Language-agnostic code indexing
- **Language Server Protocol (LSP) tools**: Extracting semantic information

**Deliverable**: Evaluation of suitability for brownfield analysis.

---

## Required Output Structure

### Section 1: Tool Inventory (~2,000 words)

For each tool category, provide:
- Tool name, maintainer, license
- Primary use case
- CLI invocation examples
- Output format samples
- Strengths and limitations

### Section 2: Comparative Analysis (~1,500 words)

| Tool | Type | Languages | Determinism | Output Format | Learning Curve | Maintenance |
|------|------|-----------|-------------|---------------|----------------|-------------|
| ... | ... | ... | ... | ... | ... | ... |

Include:
- Head-to-head comparisons for overlapping capabilities
- Performance benchmarks where available
- Community adoption metrics (GitHub stars, npm downloads, etc.)

### Section 3: Pattern Type → Tool Mapping (~1,000 words)

| Pattern Type | Best Tool | Alternative | Rationale |
|--------------|-----------|-------------|-----------|
| Function signatures | ast-grep | tree-sitter | ... |
| Naming conventions | ripgrep | ast-grep | ... |
| Import patterns | semgrep | tree-sitter | ... |
| Change clusters | git log | hercules | ... |
| ... | ... | ... | ... |

### Section 4: RaiSE Integration Recommendations (~1,500 words)

Based on analysis, recommend:
1. **Must-Have Tools** (MVP): Minimal set for brownfield rule extraction
2. **Should-Have Tools** (Phase 2): Enhanced capabilities
3. **Nice-to-Have Tools** (Future): Advanced features

For each recommendation:
- Installation command
- Basic usage pattern
- Integration with raise.rules.generate workflow
- Expected output format

### Section 5: Tool Chain Architecture (~1,000 words)

Propose a cohesive tool chain:
```
[Input: Codebase] → [Tool 1] → [Intermediate Format] → [Tool 2] → [Pattern Candidates]
```

Include:
- Data flow diagram
- Intermediate artifact schemas
- Error handling between tools

---

## Quality Criteria

- [ ] At least 15 tools evaluated
- [ ] At least 5 tools have hands-on CLI examples
- [ ] Determinism explicitly assessed for each tool
- [ ] Output formats documented with samples
- [ ] Performance data included where available
- [ ] Trade-offs clearly articulated
- [ ] Recommendations falsifiable (state when they'd be wrong)

---

## Constraints

- **CLI-Only**: Exclude GUI-based tools unless they have robust CLI interface
- **Open Source Preferred**: Prioritize open source; note commercial tools separately
- **Cross-Platform**: Tools must work on Linux (primary), macOS, Windows (nice-to-have)
- **Agent-Invocable**: Tools must be scriptable (no interactive prompts required)

---

**Target Length**: 7,000-8,000 words
**Confidence Level Required**: State HIGH/MEDIUM/LOW for each recommendation
**Output Location**: `specs/main/research/deterministic-rule-extraction/cli-pattern-mining-tools.md`
