# Deep Research: MVP Tooling Selection for Brownfield Rule Extraction

**Role**: Senior Software Architect applying KISS/DRY/YAGNI principles
**Objective**: Determine the minimal viable toolset for brownfield rule extraction that balances capability with simplicity, producing an implementable specification for RaiSE's `raise.rules.generate` command.

---

## Meta-Instructions for Reasoning

1. **KISS**: Simpler solutions are preferred; complexity must be justified by proportional value
2. **DRY**: Identify redundant capabilities; eliminate tools with overlapping functions
3. **YAGNI**: Exclude capabilities not needed for MVP; document as "Future Consideration"
4. **Pragmatism**: Favor battle-tested tools over cutting-edge; stability > features
5. **Implementation Focus**: Every recommendation must be immediately implementable

---

## Context: MVP Constraints

**Timeline**: 1 week implementation
**Team**: Single developer (AI agent + human orchestrator)
**Scope**: Brownfield rule extraction for single-repo projects
**Languages**: TypeScript/JavaScript (primary), Python (secondary)
**Output**: Rules in YAML frontmatter + Markdown format

**Non-Goals for MVP**:
- Multi-repo support
- Real-time extraction
- GUI/dashboard
- Language support beyond TS/JS/Python
- Semantic/ML-based pattern detection

---

## Research Questions

### 1. Core Tool Selection

**Primary Question**: What is the minimal set of tools needed for effective pattern extraction?

Evaluate against criteria:
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Capability | 30% | Can it extract the patterns we need? |
| Simplicity | 25% | Easy to install, configure, invoke? |
| Reliability | 20% | Deterministic, well-maintained? |
| Output Format | 15% | JSON/YAML output for parsing? |
| Cross-Platform | 10% | Works on Linux, macOS, Windows? |

Candidate tools to evaluate:
- **AST**: tree-sitter vs ast-grep vs semgrep
- **Text**: ripgrep vs grep vs ag
- **Git**: git log/diff vs gitinspector
- **Orchestration**: bash scripts vs Python scripts vs make

For each category, select ONE winner for MVP.

**Deliverable**: Single tool per category with justification.

### 2. Pattern Type Coverage

**Primary Question**: What pattern types must MVP support, and what tool handles each?

Pattern types for brownfield analysis:
1. **Naming conventions**: Class names, function names, file names
2. **Import patterns**: How dependencies are structured
3. **Architectural patterns**: Repository, Factory, Service layer detection
4. **Code structure**: Function signatures, class hierarchies
5. **Testing patterns**: Test file naming, assertion styles
6. **Configuration patterns**: Environment variables, config files

For each pattern type:
- Is it essential for MVP? (YES/NO)
- Which tool extracts it best?
- What's the extraction command?
- What's the output format?

**Deliverable**: Pattern → Tool mapping with CLI commands.

### 3. Workflow Integration

**Primary Question**: How do selected tools integrate into the raise.rules.generate workflow?

Current workflow stages:
1. **SAR Analysis Complete**: SAR reports exist in `specs/main/sar/`
2. **Pattern Mining**: Extract patterns from codebase
3. **Pattern Scoring**: Rank candidates by frequency, criticality
4. **Rule Generation**: Create .mdc files from top patterns
5. **Validation**: Check for duplicates, conflicts
6. **Graph Population**: Add rules to rules-graph.yaml

For each stage:
- What tool(s) are invoked?
- What are the inputs/outputs?
- What's the CLI command?
- How long does it take (order of magnitude)?

**Deliverable**: Stage → Tool → Command mapping.

### 4. Installation and Setup

**Primary Question**: What's the minimal installation footprint?

Evaluate:
- System dependencies (apt/brew packages)
- Language runtimes (Node.js, Python, Go)
- Package managers (npm, pip, cargo)
- Configuration files needed
- Environment variables

Produce:
- Single install script (`setup-rule-extraction.sh`)
- Prerequisites check script
- Version pinning strategy

**Deliverable**: Installation specification with exact versions.

### 5. Output Format Standardization

**Primary Question**: What intermediate format should tools produce?

Options:
- JSON (machine-readable, verbose)
- YAML (human-readable, structured)
- CSV (simple, limited structure)
- JSONL (streaming, line-delimited)
- Custom DSL (flexible, learning curve)

Evaluate for:
- Parseability by downstream tools
- Human readability for debugging
- Schema validation capability
- Streaming vs batch processing

**Deliverable**: Standard output schema for pattern candidates.

### 6. Error Handling and Recovery

**Primary Question**: How should the MVP handle tool failures?

Scenarios:
- Tool not installed → [Action]
- Tool times out on large file → [Action]
- Tool produces malformed output → [Action]
- Tool finds zero patterns → [Action]
- Tool finds too many patterns (>100) → [Action]

Design:
- Fail-fast vs graceful degradation
- Logging and diagnostics
- Human intervention triggers (Jidoka)

**Deliverable**: Error handling specification with recovery actions.

---

## Required Output Structure

### Section 1: MVP Tool Stack (~1,500 words)

Final selection:
| Category | Tool | Version | Justification |
|----------|------|---------|---------------|
| AST Parsing | [X] | [v.X.Y] | [Why this over alternatives] |
| Text Search | [X] | [v.X.Y] | [Why this over alternatives] |
| Git Analysis | [X] | [v.X.Y] | [Why this over alternatives] |
| Orchestration | [X] | [v.X.Y] | [Why this over alternatives] |

Include:
- What was excluded and why (YAGNI justification)
- Upgrade path to more capable tools (Future Consideration)

### Section 2: Pattern Extraction Commands (~2,000 words)

For each MVP pattern type:
```bash
# Pattern: [Name]
# Purpose: [What it detects]
# Tool: [Selected tool]

[CLI command with actual syntax]

# Expected output:
[Sample output in standard format]
```

Include at least 8 pattern extraction commands.

### Section 3: Workflow Specification (~1,500 words)

```
┌─────────────────┐
│ Stage 1: [Name] │
│ Tool: [X]       │
│ Input: [...]    │
│ Output: [...]   │
│ Command: [...]  │
└────────┬────────┘
         │
         ▼
         ...
```

With timing estimates and dependencies.

### Section 4: Installation Script (~500 words + code)

```bash
#!/bin/bash
# setup-rule-extraction.sh
# MVP tooling installation for RaiSE rule extraction

# Prerequisites check
...

# Tool installation
...

# Version verification
...

# Configuration
...
```

Full, runnable script.

### Section 5: Output Schema (~1,000 words)

```yaml
# pattern-candidates.yaml schema
version: "1.0"
extraction_date: "ISO-8601"
codebase_commit: "git-sha"
patterns:
  - id: "pattern-001"
    type: "naming_convention"
    name: "Repository suffix pattern"
    evidence:
      frequency: 12
      files:
        - path: "src/repos/UserRepository.ts"
          line: 1
          snippet: "class UserRepository..."
        - ...
    score: 0.87
    recommended_priority: "P1"
```

Full schema with field descriptions.

### Section 6: Error Handling Matrix (~1,000 words)

| Error Condition | Detection | Action | Jidoka Trigger? |
|-----------------|-----------|--------|-----------------|
| Tool not found | which/command -v | Install prompt | YES |
| Timeout | exit code 124 | Increase limit or skip file | NO (log warning) |
| ... | ... | ... | ... |

---

## Quality Criteria

- [ ] Exactly ONE tool selected per category (no redundancy)
- [ ] All tools are open source and actively maintained
- [ ] Installation script is complete and runnable
- [ ] At least 8 pattern extraction commands provided
- [ ] Output schema is formally specified
- [ ] Error handling covers at least 10 scenarios
- [ ] Total tool count ≤ 5 (KISS)
- [ ] YAGNI justification for every exclusion

---

## Constraints

- **1-Week Timeline**: Must be implementable by single developer in 5 days
- **Minimal Dependencies**: Prefer tools with few transitive dependencies
- **Offline Capable**: No cloud services required for core functionality
- **Deterministic**: Selected tools must produce reproducible output
- **Agent-Friendly**: All tools invocable via CLI with structured output

---

## Anti-Patterns to Avoid

1. **Tool Sprawl**: Selecting 10 tools when 4 would suffice
2. **Over-Configuration**: Complex config files for simple tasks
3. **Feature Creep**: Including ML-based detection in MVP
4. **Premature Optimization**: Building for 1M LOC when 100K is the target
5. **Framework Lock-in**: Choosing tools that require specific frameworks

---

**Target Length**: 7,500-8,500 words
**Confidence Level Required**: HIGH for all MVP selections (no "maybes")
**Output Location**: `specs/main/research/deterministic-rule-extraction/mvp-tooling-selection.md`
