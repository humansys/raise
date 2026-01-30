# Deep Research Prompt: BMAD Brownfield Reverse Engineering & RaiSE SAR Evolution

**Research ID**: RES-BMAD-BFLD-001
**Date Created**: 2026-01-27
**Priority**: Critical
**Estimated Effort**: 6-8 hours of research + 4-5 hours of synthesis
**Target Outcome**: Strategic decision on SAR evolution: Adopt BMAD / Port BMAD / Create LLM-native SAR

---

## Research Objective

Perform **detailed reverse engineering** of BMAD Method's brownfield codebase analysis capabilities, then evaluate three strategic options for evolving RaiSE's SAR (System Analysis Report) process:

1. **ADOPT**: Take BMAD's `document-project` workflow as-is (or near as-is) and integrate into RaiSE
2. **PORT**: Adapt BMAD's brownfield architecture into RaiSE's governance-as-code paradigm, preserving BMAD's best patterns while adding RaiSE's enforcement layer
3. **INSPIRE**: Use BMAD as conceptual input to create a **completely LLM-native SAR process** that reimagines brownfield analysis from first principles under RaiSE's Lean/Jidoka/Governance-as-Code philosophy

**Core Question**: Given that BMAD produces *documentation that describes* and RaiSE needs *artifacts that govern* -- what is the optimal path to a world-class brownfield analysis capability?

---

## Context: What We Already Know

### RaiSE SAR (Current State)

The current SAR system is a **7-report archaeological analysis framework**:

| Report | Focus | Lens |
|--------|-------|------|
| 1. Resumen Repositorio | Executive summary, stack, entry point | Overview |
| 2. Descripcion General Arquitectura | Layers, patterns, Mermaid diagrams | Structure |
| 3. Analisis Codigo Limpio | Naming, functions, classes, smells | Clean Code |
| 4. Analisis Arquitectura Limpia | Dependency rules, independence | Clean Architecture |
| 5. Desglose Componentes | Modules, namespaces, deep dive | Components |
| 6. Mapa Dependencias | Internal dependency graph | Dependencies |
| 7. Recomendaciones Refactorizacion | Consolidated recommendations + business impact | Synthesis |

**Command**: `raise.1.analyze.code` (67 lines, 6-step outline)
**Templates**: `.raise-kit/templates/raise/sar/` (7 templates + README)
**Output**: `specs/main/analysis/`

**Known Gaps**:
- No handoffs (terminal node -- no next-step guidance)
- No incremental persistence (all 7 reports in one execution, loss risk on interruption)
- .NET/C# bias in templates (not polyglot)
- No partial execution (all-or-nothing, 30-60 min runtime)
- Missing layer-specific Katas (referenced but not created)
- No YAML frontmatter for AI consumption
- No `.cursorrules` generation from findings
- No differential/incremental re-analysis
- No project type detection/classification

### BMAD Brownfield (Known Architecture)

BMAD's brownfield capability centers on `document-project`:

| Component | Description |
|-----------|-------------|
| **Router** | `instructions.md` -- determines mode (initial scan, rescan, deep-dive) |
| **Full Scan** | 12-step workflow generating documentation artifacts |
| **Deep-Dive** | 7-step exhaustive analysis of specific areas |
| **Classification** | CSV-based 12 project types x 24 detection columns |
| **Scan Levels** | Quick (2-5 min), Deep (10-30 min), Exhaustive (30-120 min) |
| **State** | JSON state file with resumability + stale detection |
| **Context Management** | Write-as-you-go + context purging |
| **Validation** | 200+ item checklist |
| **Templates** | index, project-overview, source-tree, deep-dive |
| **Agent** | Mary (Analyst) owns the workflow |

**BMAD's Brownfield Gaps** (from our competitive analysis):
- NO rule/convention extraction (produces docs, not governance)
- NO architecture reverse-engineering (arch workflow is forward-only)
- NO code quality/health assessment (documents "what is", not "how good")
- NO enforceable guardrail generation
- NO incremental/differential analysis
- NO integration with static analysis tools (pure LLM file reading)
- Conversational convention suggestions, not deterministic enforcement

### RaiSE Brownfield Research (Existing)

Research ID RES-BFLD-AGENT-DOC-001 produced:
- Landscape report (~8,200 words) with 7 case studies
- Recommendations (~22,000 words) with 4 Quick Wins + 5 Strategic + 4 Experimental
- Key finding: Industry moving toward AI-consumable metadata (AGENTS.md, .cursorrules, YAML frontmatter)
- Key finding: AST-based chunking dominates RAG (cAST framework, 4.3-point Recall@5 improvement)
- Key finding: Continuous documentation regeneration emerging pattern

---

## Research Scope

### In Scope

1. **Complete BMAD brownfield reverse engineering**: Every step file, template, checklist, CSV, JSON schema -- full mechanical understanding
2. **Pattern extraction**: Identify BMAD's novel patterns worth preserving regardless of strategy chosen
3. **RaiSE SAR gap analysis**: What does SAR need that BMAD has? What does SAR have that BMAD lacks?
4. **Three-option evaluation**: Detailed analysis of Adopt vs. Port vs. Inspire with tradeoffs
5. **LLM-native SAR architecture design**: If "Inspire" is chosen, what does a from-scratch LLM-native SAR look like?
6. **Context window economics**: How does each approach manage the fundamental constraint of LLM context windows?
7. **Governance bridge**: How to connect brownfield documentation output to governance enforcement
8. **Industry best practices**: What does the state of the art look like in 2026 for AI-driven codebase analysis?

### Out of Scope

- BMAD's non-brownfield workflows (PRD, architecture creation, sprint planning)
- BMAD's agent personas beyond their brownfield-relevant capabilities
- Implementation of the chosen strategy (this prompt produces the decision, not the code)
- RaiSE's greenfield specification workflows
- Commercial analysis of BMAD

---

## Key Research Questions

### Category 1: BMAD Brownfield -- Deep Mechanical Understanding

**Q1.1**: What is the exact execution flow of BMAD's `document-project` full scan?

**Investigate step-by-step with full detail**:

- **Step 0.5 (Load Requirements)**:
  - How is `documentation-requirements.csv` parsed by the LLM?
  - What happens if a project type is not in the CSV? Fallback behavior?
  - How reliable is CSV parsing by LLMs? Error rates?
  - What are the exact 24 columns and their purpose for each of the 12 project types?

- **Step 0.6 (Mode Detection)**:
  - How does the router decide between initial_scan, full_rescan, and deep_dive?
  - What triggers a rescan vs. a fresh scan?
  - How is stale state detected (>24 hours)? What happens to stale state?
  - What is the exact JSON schema of `project-scan-report.json`?

- **Step 1 (Structure Detection + Classification)**:
  - How are monolith vs. monorepo vs. multi-part distinguished?
  - What file patterns trigger each classification?
  - How accurate is LLM-based project type detection vs. deterministic detection?
  - Does user confirmation slow down the process? Is it skippable?

- **Step 4 (Conditional Analysis -- the critical step)**:
  - How does batching work? What constitutes a "batch"?
  - What is the write-as-you-go architecture in detail?
  - How does context purging work? What exactly is purged vs. retained?
  - What is the fidelity of summaries kept after purging?
  - How do boolean flags from CSV control scan behavior?

- **Step 10 (Master Index Generation)**:
  - What makes `index.md` the "primary AI retrieval source"?
  - How is it structured for optimal AI consumption?
  - What metadata does it contain?
  - Compare with RaiSE's approach to AI-consumable documentation

- **Step 11 (Validation)**:
  - What are the most important items in the 200+ item checklist?
  - How is "Brownfield PRD Readiness" determined?
  - What criteria? What thresholds?
  - How does this compare to RaiSE's Validation Gates?

**Sources**:
- Fetch full content of: `src/bmm/workflows/document-project/workflows/full-scan-instructions.md`
- Fetch full content of: `src/bmm/workflows/document-project/checklist.md`
- Fetch full content of: `src/bmm/workflows/document-project/documentation-requirements.csv`
- Fetch full content of: `src/bmm/workflows/document-project/templates/project-scan-report-schema.json`
- Fetch full content of: `src/bmm/workflows/document-project/instructions.md`

---

**Q1.2**: What is the exact execution flow of BMAD's deep-dive sub-workflow?

**Investigate**:

- **Step 13b (Exhaustive Scan)**:
  - "Read every line of every file in scope" -- how does this interact with context windows?
  - What per-file metadata is captured? (Purpose, exports, imports, dependents, patterns, etc.)
  - How is this structured for retention? In-memory? Written immediately?
  - What is the quality of dependency detection by LLM vs. AST tools?

- **Step 13c (Relationship & Data Flow Analysis)**:
  - How are dependency graphs constructed? Mermaid? Text? JSON?
  - Circular dependency detection -- how reliable without AST?
  - Data flow tracing -- how deep does the LLM trace?

- **Step 13d (Related Code Discovery)**:
  - "Searches OUTSIDE scanned area" -- how wide? How accurate?
  - How does this avoid false positives?
  - Useful for identifying cross-cutting concerns?

- **Step 13e (Documentation Generation)**:
  - What does the deep-dive template contain? (20+ sections)
  - How does the "contributor checklist" work?
  - What are "verification steps" in this context?

**Sources**:
- Fetch full content of: `src/bmm/workflows/document-project/workflows/deep-dive-instructions.md`
- Fetch full content of: `src/bmm/workflows/document-project/templates/deep-dive-template.md`

---

**Q1.3**: How does BMAD's brownfield output feed into downstream workflows?

**Investigate the critical handoff**:

- **`project-context.md` generation**: What exactly goes into this file?
  - Is it a summary of the full scan? A separate artifact?
  - What sections/structure?
  - How is it consumed by downstream agents (Barry, Amelia)?

- **PRD creation from brownfield**: Does `create-prd` behave differently when `project-context.md` exists?
  - Any brownfield-specific PRD steps?
  - How are existing constraints incorporated?
  - Compare with RaiSE's approach to brownfield specification

- **Architecture workflow from brownfield**: Does `create-architecture` use scan results?
  - Or is it always forward-looking?
  - Gap: No "document existing architecture" workflow?

- **Quick Flow brownfield path**: How does `quick-spec` use existing code analysis?
  - "Ask informed questions" pattern -- how well does this work?
  - Does it actually read code or just check for patterns?
  - Quality of brownfield-aware specifications?

- **Implementation from brownfield**: Does `dev-story` reference existing conventions?
  - How are existing patterns enforced?
  - Conversational vs. deterministic enforcement?

**Sources**:
- Fetch: Any PRD workflow steps that reference `project-context`
- Fetch: Quick spec step files that handle existing code
- Fetch: Dev story steps that reference conventions

---

### Category 2: Pattern Extraction -- What BMAD Does Uniquely Well

**Q2.1**: What novel patterns in BMAD's brownfield approach are worth preserving?

**Evaluate each pattern independently of strategy choice**:

- **Pattern 1: CSV-Based Project Classification**
  - 12 types x 24 detection columns
  - Deterministic? Or LLM-interpreted?
  - Extensibility: Can users add project types?
  - **RaiSE equivalent**: None. Worth adopting regardless?
  - **Lean audit**: Muda (waste in maintaining 24 columns for 12 types)?

- **Pattern 2: Scan Level Flexibility (Quick/Deep/Exhaustive)**
  - 3-tier time investment model
  - How does each tier differ in output quality?
  - **RaiSE equivalent**: All-or-nothing (1 level). This is a gap.
  - **Lean audit**: Mura (unevenness) -- current RaiSE SAR is always "exhaustive"

- **Pattern 3: Write-As-You-Go + Context Purging**
  - Generate artifact → write to disk → purge details → retain summary
  - Essential for large codebases
  - **RaiSE equivalent**: No persistence strategy. All in memory.
  - **Lean audit**: Eliminates Muda of context window waste

- **Pattern 4: JSON State File with Resumability**
  - `project-scan-report.json` tracks step completion, timestamps, config
  - Enables resume-from-step on interruption
  - Stale detection (>24 hours) with auto-archive
  - **RaiSE equivalent**: No state tracking. Total loss on interruption.
  - **Lean audit**: Eliminates Muda of rework

- **Pattern 5: Master Index as AI Retrieval Source**
  - `index.md` designed specifically for AI consumption
  - Structured metadata, links, summaries
  - Acts as "table of contents" for RAG-like access
  - **RaiSE equivalent**: No AI-optimized index. Reports are human-oriented.
  - **Lean audit**: Supports flow of information to AI consumers

- **Pattern 6: Conditional Analysis via Boolean Flags**
  - CSV flags control which analyses run per project type
  - Avoids unnecessary scans (e.g., no UI scan for CLI tools)
  - **RaiSE equivalent**: All reports always generated regardless of type
  - **Lean audit**: Eliminates Muda of irrelevant analysis

- **Pattern 7: 200+ Item Validation Checklist**
  - Comprehensive but... how many items are actually checked?
  - Is this proportionate or checkbox theater?
  - **RaiSE equivalent**: Simple completeness checklist (7 reports exist)
  - **Lean audit**: Muri (overburden) if items aren't meaningfully checked

- **Pattern 8: Monolith/Monorepo/Multi-Part Detection**
  - Structural classification before analysis begins
  - Adapts analysis strategy to project structure
  - **RaiSE equivalent**: No structural classification
  - **Lean audit**: Enables right-sized analysis

**For each pattern, determine**: Adopt as-is / Adapt to RaiSE / Reject (with rationale)

---

**Q2.2**: What are BMAD's brownfield anti-patterns to avoid?

**Identify patterns that would harm RaiSE if adopted**:

- **Anti-Pattern 1: Documentation Without Governance**
  - BMAD generates excellent docs but no enforceable rules
  - Is this a feature (flexibility) or a bug (no enforcement)?
  - How often do teams actually read and follow the docs?
  - Evidence from community about doc-only brownfield approaches?

- **Anti-Pattern 2: LLM-Only File Reading (No Static Analysis)**
  - BMAD reads files line-by-line via LLM, no AST, no linters
  - What does the LLM miss vs. what AST/linting catches?
  - Performance comparison: LLM file reading vs. tree-sitter parsing
  - Error rates in dependency detection: LLM vs. import graph tools
  - What about binary files, minified code, generated code?

- **Anti-Pattern 3: Persona-Dependent Brownfield (Mary the Analyst)**
  - Brownfield analysis locked to one agent persona
  - What if the persona's prompt drifts? What if it's updated?
  - Is the persona adding value or just cosmetic wrapping?
  - Would a persona-less command produce the same quality?

- **Anti-Pattern 4: 200+ Item Checklist as Validation**
  - Can an LLM honestly evaluate 200+ items?
  - What's the false confidence rate?
  - Compare with RaiSE's focused, criteria-specific gates
  - Evidence of checklist fatigue in LLM contexts?

- **Anti-Pattern 5: No Quality Assessment in Documentation**
  - BMAD documents "what is" without evaluating "how good"
  - Technical debt detection is template placeholder, not active analysis
  - Missing: code smell density, coupling metrics, cohesion analysis
  - Compare with RaiSE SAR reports 3-4 (Clean Code + Clean Architecture analysis)

---

### Category 3: RaiSE SAR Gap Analysis

**Q3.1**: What does SAR need from BMAD?

**Map BMAD capabilities against SAR gaps**:

| SAR Gap | BMAD Capability | Transferable? | Adaptation Needed? |
|---------|-----------------|---------------|-------------------|
| No project type detection | CSV-based 12-type classification | Yes | Adapt to RaiSE context |
| All-or-nothing execution | Quick/Deep/Exhaustive scan levels | Yes | Map to SAR report subsets |
| No persistence/resume | JSON state file + stale detection | Yes | Integrate with SAR reports |
| No AI-consumable index | `index.md` as retrieval source | Yes | Add YAML frontmatter |
| .NET bias | 12 project types, polyglot | Partial | Need RaiSE-specific types |
| No context management | Write-as-you-go + purging | Yes | Critical for large codebases |
| No conditional analysis | Boolean flag-driven scans | Yes | Adapt to SAR report flags |
| No structural classification | Monolith/Monorepo/Multi-Part | Yes | Straightforward adoption |
| No handoffs | Next-step guidance to PRD | Yes | Map to RaiSE workflow |
| No deep-dive mode | 7-step exhaustive area analysis | Partial | Adapt to SAR layer Katas |
| No incremental update | (BMAD also lacks this) | No | Novel design needed |
| No rule extraction | (BMAD lacks this too) | No | RaiSE's unique opportunity |

**For each row**: Is BMAD's approach the best available, or are there better alternatives?

---

**Q3.2**: What does SAR have that BMAD lacks?

**Identify RaiSE's existing brownfield advantages**:

- **Clean Code + Clean Architecture dual lens**: BMAD has no quality evaluation framework
- **Evidence-based claims requirement**: BMAD's docs may contain unverified assertions
- **Business impact translation**: SAR Report 7 maps technical findings to business value
- **Mermaid diagram generation**: SAR generates architectural diagrams
- **Refactoring recommendations with prioritization**: BMAD doesn't generate actionable recommendations
- **Layer-by-layer analysis methodology**: Domain → Application → Infrastructure → Presentation
- **Rule extraction pipeline**: `raise.rules.generate` converts analysis into enforceable rules

**For each advantage**: How critical is it? Would losing it in a migration be acceptable?

---

**Q3.3**: What does neither SAR nor BMAD have that both need?

**Investigate state-of-the-art brownfield analysis**:

- **AST-based analysis**: tree-sitter, ast-grep, semgrep
  - What can AST tools detect that LLM file reading cannot?
  - Integration strategies: Run AST tools → feed results to LLM
  - Performance and accuracy data

- **Dependency graph extraction**: madge, dependency-cruiser, deptry
  - Deterministic import graph construction vs. LLM inference
  - Visualization tools (D3, Graphviz, Mermaid)
  - Integration with brownfield documentation

- **Complexity metrics**: cyclomatic complexity, cognitive complexity, LOC
  - Sonar-like metrics without Sonar
  - LLM-computed complexity vs. tool-computed
  - How to translate metrics into actionable recommendations

- **Git history analysis** (where available):
  - Hotspot analysis (frequently changed files)
  - Churn metrics (code instability)
  - Coupling analysis (files that change together)
  - Author analysis (bus factor, knowledge silos)
  - Tools: git-of-theseus, code-maat, git-fame

- **Architecture fitness functions**:
  - Automated architecture compliance checks
  - Dependency rule verification
  - Module boundary enforcement
  - Tools: ArchUnit, Fitness Functions, custom

- **AI-consumable codebase metadata**:
  - AGENTS.md (emerging standard)
  - .cursorrules generation from analysis
  - YAML frontmatter for every artifact
  - Structured JSON/YAML summaries

---

### Category 4: Three-Option Deep Evaluation

**Q4.1**: Option A -- ADOPT BMAD's brownfield approach

**What this means**:
- Take `document-project` workflow as-is (or minor modifications)
- Install BMAD's brownfield module into RaiSE's pipeline
- Use BMAD's templates, CSV classification, step files
- Add RaiSE governance layer on top (gates, rules extraction)

**Evaluate**:

- **Compatibility**:
  - Can BMAD's step-file architecture run inside RaiSE's command model?
  - Do BMAD's YAML/CSV/JSON formats conflict with RaiSE's conventions?
  - Can BMAD's persona-driven approach coexist with RaiSE's functional agents?
  - What about language? BMAD is English; RaiSE SAR is Spanish content

- **Completeness**:
  - Does BMAD cover everything SAR currently covers? (No -- missing Clean Code/Architecture analysis)
  - What RaiSE features would be lost? (Quality evaluation, refactoring recommendations)
  - What RaiSE features would be gained? (Classification, scan levels, persistence, context management)

- **Maintenance burden**:
  - BMAD is MIT licensed -- legal compatibility with RaiSE?
  - Dependency on BMAD's evolution -- what if they change direction?
  - Need to track BMAD updates and merge/rebase?
  - Fork risk: Divergence over time

- **Integration cost**:
  - How much adapter code is needed?
  - Can the governance layer (rules extraction) be added cleanly?
  - How does this interact with existing `raise.1.analyze.code`?
  - Migration path for existing SAR users?

- **Verdict criteria**:
  - [ ] BMAD covers ≥80% of SAR's brownfield needs
  - [ ] Integration cost is ≤ 2 weeks
  - [ ] No critical RaiSE features are lost
  - [ ] Maintenance burden is acceptable
  - [ ] BMAD's evolution trajectory aligns with RaiSE goals

---

**Q4.2**: Option B -- PORT BMAD's brownfield architecture to RaiSE

**What this means**:
- Extract BMAD's best patterns and reimplement in RaiSE's paradigm
- Use RaiSE's command structure, templates, gates
- Preserve: Classification, scan levels, persistence, context management
- Add: Quality analysis, governance extraction, Lean principles
- Discard: Personas, step-file architecture, CSV format, BMAD-specific templates

**Evaluate**:

- **What to port**:
  - Project classification system → RaiSE YAML format (not CSV)
  - Scan level flexibility → Map to SAR report subsets
  - Write-as-you-go + context purging → Integrate into SAR command
  - JSON state tracking → Adapt to RaiSE's approach
  - Master index generation → AI-consumable SAR index
  - Conditional analysis flags → Boolean gates per project type
  - Monolith/Monorepo/Multi-Part detection → Structural classification step
  - Deep-dive sub-workflow → Layer-specific Kata activation

- **What to enhance during port**:
  - Add Clean Code + Clean Architecture analysis (RaiSE's unique value)
  - Add rule extraction step (SAR findings → `.cursorrules` / guardrails)
  - Add YAML frontmatter to all outputs
  - Add ADR generation for discovered architectural decisions
  - Add business impact translation (SAR Report 7's strength)
  - Add AST integration hooks (future: tree-sitter, ast-grep)
  - Add incremental re-analysis capability (diff-based)

- **What to discard**:
  - BMAD persona system (Mary the Analyst)
  - Step-file micro-architecture (use RaiSE's command structure)
  - CSV format (use YAML for project type definitions)
  - BMAD-specific templates (redesign for RaiSE)
  - 200+ item checklist (replace with focused Validation Gates)
  - BMAD's YOLO mode (conflicts with Jidoka principle)

- **Implementation estimate**:
  - Phase 1 (Core SAR v2): Classification + Scan Levels + Persistence + Context Management
  - Phase 2 (Enhanced SAR): Quality Analysis + Governance Bridge + Rule Extraction
  - Phase 3 (Advanced SAR): AST Integration + Incremental Analysis + C4 Diagrams
  - Effort per phase?

- **Verdict criteria**:
  - [ ] Preserves all valuable BMAD patterns
  - [ ] Maintains all RaiSE SAR strengths
  - [ ] Adds governance bridge (docs → rules)
  - [ ] Total effort is ≤ 4-6 weeks
  - [ ] Result is demonstrably better than either source

---

**Q4.3**: Option C -- INSPIRE: Create LLM-native SAR from first principles

**What this means**:
- Use BMAD and current SAR as conceptual inputs only
- Redesign brownfield analysis from scratch using RaiSE's philosophy
- Native LLM architecture: progressive context building, tool integration, governance output
- Not constrained by either BMAD's or current SAR's structure

**Evaluate a from-scratch design**:

- **Architecture question**: What is the ideal brownfield analysis workflow for an LLM?
  - Not "how do we document a codebase" (BMAD's question)
  - Not "how do we evaluate clean code/architecture" (current SAR's question)
  - Instead: "How do we extract governance-grade understanding from a codebase?"

- **Design principles for LLM-native SAR**:
  1. **Progressive Context Building**: Build understanding layer by layer, never overload context
  2. **Tool-Augmented Analysis**: LLM orchestrates tools (AST, git, linters) -- doesn't read raw files
  3. **Governance-First Output**: Every finding maps to an enforceable artifact (rule, gate, constraint)
  4. **Right-Sized Analysis**: Lean principle -- only analyze what produces value for the project's context
  5. **Resumable by Design**: State machine architecture, checkpoint after every phase
  6. **Evidence-Chained**: Every claim links to file:line evidence, traceable through the entire chain
  7. **Incrementally Refinable**: First pass is fast (5 min); each subsequent pass adds depth
  8. **AI-Native Output**: Artifacts designed for AI consumption first, human readability second

- **Proposed Architecture** (evaluate this sketch):

  ```
  Phase 0: Detect (1-2 min)
  ├── Run deterministic tools: file tree, package manifests, git stats
  ├── Classify: project type, structure (mono/multi/monorepo), stack
  ├── Output: project-profile.yaml (machine-readable classification)
  └── Gate: User confirms classification

  Phase 1: Surface (5-10 min)
  ├── Entry point identification (deterministic: main, index, etc.)
  ├── Top-level dependency graph (AST or import parsing)
  ├── Module boundary detection (directories, namespaces)
  ├── Output: surface-map.md (overview) + surface-data.yaml (structured)
  ├── State checkpoint: phase-1-complete
  └── Gate: User validates high-level understanding

  Phase 2: Analyze (15-30 min, optional, by area)
  ├── For each module/component (user-selected or auto-priority):
  │   ├── LLM reads key files (not ALL files -- tool-guided selection)
  │   ├── Pattern detection: architecture, code quality, conventions
  │   ├── Convention extraction: naming, error handling, testing, logging
  │   ├── Technical debt identification with severity
  │   ├── Output: per-module analysis + extracted conventions
  │   ├── Write-to-disk + context purge after each module
  │   └── State checkpoint: module-X-complete
  ├── Cross-cutting analysis: shared patterns, inconsistencies
  └── Gate: Gate-Coherencia (cross-module consistency check)

  Phase 3: Synthesize (5-10 min)
  ├── Consolidate findings into governance artifacts:
  │   ├── Extracted conventions → .cursorrules / guardrails
  │   ├── Discovered architecture → architectural fitness constraints
  │   ├── Identified patterns → pattern catalog with evidence
  │   ├── Technical debt → prioritized refactoring roadmap + business impact
  │   └── Project understanding → AI-consumable index (AGENTS.md format)
  ├── Output: SAR index + governance artifacts + recommendations
  ├── State checkpoint: synthesis-complete
  └── Gate: Gate-Trazabilidad (evidence chain verification)

  Phase 4: Bridge (2-5 min)
  ├── Generate handoff artifacts:
  │   ├── For specification: brownfield constraints document
  │   ├── For architecture: existing architecture baseline + ADRs
  │   ├── For development: coding conventions + patterns + anti-patterns
  │   └── For testing: test architecture baseline + gaps
  ├── Output: handoff package for downstream RaiSE commands
  └── Handoff: → raise.1.discovery or raise.2.vision
  ```

- **How this differs from BMAD**:
  - Tool-augmented (not LLM-only file reading)
  - Governance-output (rules, not just documentation)
  - Phase-gated (Validation Gates, not checklists)
  - Right-sized (Lean: only analyze what produces value)
  - Incrementally refinable (not all-or-nothing)
  - Evidence-chained (Jidoka: stop if evidence is insufficient)

- **How this differs from current SAR**:
  - Not 7 monolithic reports (modular, per-area outputs)
  - Not Clean Code/Architecture specific (multi-lens, configurable)
  - Not all-at-once (phased, resumable, incremental)
  - Not .NET-biased (polyglot by design)
  - Not documentation-only (governance artifacts output)
  - Includes handoffs (not a terminal node)

- **Risks**:
  - Higher design effort (from-scratch vs. adapting existing work)
  - No proven track record (novel architecture)
  - May over-engineer (violate Lean/YAGNI)
  - Tool integration complexity (AST, git, linters)

- **Verdict criteria**:
  - [ ] Demonstrably superior to both BMAD and current SAR
  - [ ] Achievable in ≤ 8-10 weeks for Phase 1-2
  - [ ] Aligns with RaiSE constitution (all 8 principles)
  - [ ] Produces governance artifacts (not just documentation)
  - [ ] Manageable complexity (YAGNI applied rigorously)

---

### Category 5: Context Window Economics

**Q5.1**: How do context windows constrain brownfield analysis?

**Investigate the fundamental constraint**:

- **File reading capacity**: How many source files can an LLM read in one session?
  - Claude Opus 4.5: ~200K tokens context, ~150K usable after system prompt + instructions
  - Average source file: 200-500 lines, 1,500-4,000 tokens
  - Effective capacity: ~37-100 source files per session
  - Typical brownfield project: 100-10,000+ source files
  - **Implication**: LLM CANNOT read an entire non-trivial codebase

- **BMAD's solution**: Write-as-you-go + context purge + scan levels
  - Effectiveness: Good for medium projects, unclear for large ones
  - Risk: Summary quality degrades over many purge cycles?

- **Current SAR's approach**: Read everything in one session
  - Only works for small-medium codebases
  - No strategy for large projects

- **Optimal approaches** (research):
  - Tool-first analysis (AST, static analysis) → LLM reads tool output (compact)
  - Multi-session with persistent state (checkpoint/resume)
  - Hierarchical analysis (overview → drill-down)
  - RAG-augmented (embed codebase, retrieve relevant chunks)
  - Hybrid: deterministic extraction (graph, metrics) + LLM synthesis (patterns, insights)

- **For each approach**: Token economics, quality tradeoffs, implementation complexity

---

**Q5.2**: What is the optimal analysis strategy per codebase size?

**Build a size-aware strategy matrix**:

| Codebase Size | Files | Tokens | Strategy | Time Estimate |
|--------------|-------|--------|----------|---------------|
| Tiny (<20 files) | <20 | <30K | Full LLM read | 5-10 min |
| Small (20-100 files) | 20-100 | 30K-150K | Selective LLM read | 15-30 min |
| Medium (100-500 files) | 100-500 | 150K-750K | Tool-assisted + LLM synthesis | 30-60 min |
| Large (500-2000 files) | 500-2K | 750K-3M | Multi-session tool-first | 1-3 hours |
| Very Large (2000+ files) | 2K+ | 3M+ | RAG + tool-first + hierarchical | 3+ hours |

**For each size tier**: What's the optimal tool mix? What does the LLM focus on?

---

### Category 6: Governance Bridge Design

**Q6.1**: How do you go from "brownfield documentation" to "enforceable governance"?

**This is RaiSE's unique value proposition. Investigate**:

- **Convention → Rule**: When analysis finds "all services use `camelCase` naming"
  - How to codify this as an enforceable rule?
  - What format? `.cursorrules`? YAML? Custom?
  - How to handle exceptions? (Legacy modules that don't follow the convention)
  - Confidence levels: "100% consistent" vs. "80% consistent" vs. "inconsistent"

- **Architecture → Constraint**: When analysis finds "clean architecture with 4 layers"
  - How to codify layer dependency rules?
  - What format for architectural fitness functions?
  - How to detect violations in future code?

- **Pattern → Guardrail**: When analysis finds "all API endpoints validate input via middleware"
  - How to ensure new endpoints follow this pattern?
  - Integration with AI coding tools (Cursor, Claude Code)
  - Auto-generation of validation rules

- **Debt → Recommendation**: When analysis finds technical debt
  - How to prioritize: business impact, effort, risk?
  - How to track remediation over time?
  - Integration with project management workflows

- **RaiSE-specific bridge outputs**:
  - `.cursorrules` generation from discovered conventions
  - Guardrail files for RaiSE's validation gate system
  - ADR templates pre-populated from architectural discoveries
  - Constitution seed documents for new projects based on existing patterns

---

**Q6.2**: What governance artifacts should a brownfield analysis produce?

**Design the output taxonomy**:

- **Tier 1 (Always generated)**:
  - `project-profile.yaml`: Machine-readable project classification
  - `conventions-extracted.md`: Discovered coding conventions with evidence
  - `architecture-baseline.md`: Current architecture description + diagrams
  - `analysis-index.md`: AI-consumable navigation index

- **Tier 2 (Generated on request / for deep analysis)**:
  - `.cursorrules` or guardrail files per convention
  - `technical-debt-roadmap.md`: Prioritized debt with business impact
  - `architecture-fitness.yaml`: Testable architectural constraints
  - `pattern-catalog.md`: Discovered patterns with examples + anti-examples

- **Tier 3 (Generated for governance-mature teams)**:
  - ADR drafts for discovered architectural decisions
  - Test architecture baseline (gaps, coverage, strategy)
  - Dependency health report (outdated, vulnerable, unused)
  - Brownfield constitution (seed for project governance)

**For each artifact**: Format, content, AI-consumability, effort to generate, value to team

---

### Category 7: Industry State of the Art (2026)

**Q7.1**: What are the best brownfield analysis tools and approaches in 2026?

**Survey the landscape**:

- **AI-powered codebase analysis**:
  - Sourcegraph Cody: How does it analyze codebases?
  - GitHub Copilot Workspace: Codebase understanding features?
  - Cursor's codebase indexing: How does it work?
  - Augment Code: Codebase understanding approach?
  - Any new entrants since 2025?

- **Static analysis + AI hybrid**:
  - SonarQube AI Code Assurance: How does it combine static + AI?
  - Codacy, CodeClimate: AI features?
  - Semgrep rules + AI generation: State of the art?

- **Architecture reverse engineering**:
  - Lattix, Structure101, NDepend: Still relevant?
  - AI-powered architecture discovery: Any new tools?
  - C4 model generators from code: Options?

- **Emerging standards**:
  - AGENTS.md: Current adoption and format
  - `.github/copilot-instructions.md`: Structure and effectiveness
  - `.cursorrules`: Community patterns and best practices
  - Structured project metadata: What's becoming standard?

**Sources**: Web searches for "AI codebase analysis 2026", "brownfield analysis tools", "code architecture discovery AI", "AGENTS.md standard"

---

**Q7.2**: What academic research informs LLM-based codebase analysis?

**Survey recent research**:

- **Code understanding**: Papers on LLM code comprehension accuracy
- **Architecture recovery**: ML/AI approaches to architecture reverse engineering
- **Technical debt detection**: AI-powered debt identification
- **Convention mining**: Extracting coding conventions from codebases
- **Code summarization**: State-of-the-art code summary quality
- **RAG for code**: Retrieval-augmented generation for code analysis
- **AST + LLM**: Hybrid approaches combining syntax analysis with LLM reasoning

---

## Analysis Framework

For each aspect of BMAD's brownfield approach, evaluate:

### Pattern Quality Assessment
- [ ] **Novelty**: Is this pattern original to BMAD or industry-standard?
- [ ] **Effectiveness**: Does this pattern produce measurably better outcomes?
- [ ] **Reliability**: Does this pattern work consistently across LLM providers/versions?
- [ ] **Simplicity**: Is this pattern the simplest solution to the problem? (YAGNI)
- [ ] **Composability**: Does this pattern compose well with RaiSE's architecture?

### Strategic Fit Assessment
- [ ] **RaiSE Constitution Alignment**: Does this support or contradict RaiSE's 8 principles?
- [ ] **Governance-as-Code Compatibility**: Can this produce governance artifacts (not just docs)?
- [ ] **Lean Principle Compliance**: Does this eliminate waste or create it?
- [ ] **Jidoka Compatibility**: Does this support stop-at-defects behavior?
- [ ] **Heutagogy Support**: Does this empower the Orquestador's self-directed learning?

### Three-Option Decision Matrix (per pattern)
- [ ] **Adopt?**: Take as-is -- effort, risk, benefit
- [ ] **Port?**: Transform for RaiSE -- effort, risk, benefit
- [ ] **Inspire?**: Use concept only, redesign from scratch -- effort, risk, benefit
- [ ] **Verdict**: Which option wins for this specific pattern?

---

## Synthesis Requirements

### Deliverable 1: BMAD Brownfield Reverse Engineering Report

**Format**: Markdown document (~8-10K words)

**Structure**:
```markdown
# BMAD Brownfield: Complete Reverse Engineering

## Executive Summary
- BMAD's brownfield philosophy in one paragraph
- Core architecture (workflow, steps, classification, state)
- Key strengths (with evidence)
- Key weaknesses (with evidence)
- Novel patterns worth preserving

## 1. Full Scan Workflow -- Step-by-Step Mechanical Analysis
### 1.1 Mode Detection and Routing
### 1.2 Project Classification System (CSV deep dive)
### 1.3 Structure Detection (Mono/Multi/Monorepo)
### 1.4 Conditional Analysis Engine
### 1.5 Context Management (Write-as-you-go + Purge)
### 1.6 Master Index Generation
### 1.7 Validation Checklist Analysis

## 2. Deep-Dive Sub-Workflow -- Step-by-Step Analysis
### 2.1 Target Selection
### 2.2 Exhaustive Scan Mechanics
### 2.3 Relationship and Data Flow Analysis
### 2.4 Related Code Discovery
### 2.5 Documentation Generation

## 3. Downstream Integration
### 3.1 project-context.md as Handoff Artifact
### 3.2 PRD Workflow Brownfield Adaptations
### 3.3 Quick Flow Brownfield Detection
### 3.4 Implementation Workflow Convention Awareness

## 4. Novel Patterns Catalog
### 4.1 [Pattern Name] -- Description, Evidence, RaiSE Applicability
[Repeat for each pattern]

## 5. Anti-Pattern Catalog
### 5.1 [Anti-Pattern Name] -- Description, Evidence, RaiSE Implication
[Repeat for each anti-pattern]

## 6. Context Window Economics
### 6.1 BMAD's Approach vs. Theoretical Optimal
### 6.2 Token Budget Analysis per Codebase Size

## References
[Full file list with GitHub URLs]
```

---

### Deliverable 2: Three-Option Strategic Decision Report

**Format**: Markdown document (~6-8K words)

**Structure**:
```markdown
# SAR Evolution: Adopt vs. Port vs. Inspire

## Executive Summary
- Recommended option: [A/B/C]
- Rationale in 3 sentences
- Key tradeoffs

## 1. Decision Context
### 1.1 Current SAR Capabilities and Gaps
### 1.2 BMAD Capabilities and Gaps
### 1.3 Industry State of the Art (2026)
### 1.4 RaiSE Constitution Constraints

## 2. Option A: ADOPT BMAD
### 2.1 What Would Be Adopted
### 2.2 Compatibility Analysis
### 2.3 What Would Be Lost from SAR
### 2.4 What Would Be Gained
### 2.5 Implementation Effort
### 2.6 Maintenance Burden
### 2.7 Risk Assessment
### 2.8 Verdict: [Recommended / Not Recommended / Conditional]

## 3. Option B: PORT BMAD Patterns to RaiSE
### 3.1 What Would Be Ported
### 3.2 What Would Be Enhanced
### 3.3 What Would Be Discarded
### 3.4 Implementation Phases
### 3.5 Implementation Effort per Phase
### 3.6 Risk Assessment
### 3.7 Verdict: [Recommended / Not Recommended / Conditional]

## 4. Option C: INSPIRE -- LLM-Native SAR from First Principles
### 4.1 Design Philosophy
### 4.2 Proposed Architecture (Phase 0-4)
### 4.3 Governance Bridge Design
### 4.4 Tool Integration Strategy
### 4.5 Implementation Effort
### 4.6 Risk Assessment
### 4.7 Verdict: [Recommended / Not Recommended / Conditional]

## 5. Comparative Analysis
### 5.1 Feature Coverage Matrix
| Capability | Adopt | Port | Inspire | Current SAR |
|-----------|-------|------|---------|-------------|
| ... | ... | ... | ... | ... |

### 5.2 Effort Comparison
### 5.3 Risk Comparison
### 5.4 Strategic Value Comparison
### 5.5 RaiSE Constitution Alignment Comparison

## 6. Per-Pattern Decision Matrix
| Pattern | Adopt | Port | Inspire | Verdict |
|---------|-------|------|---------|---------|
| CSV Classification | ... | ... | ... | ... |
| Scan Levels | ... | ... | ... | ... |
| Write-As-You-Go | ... | ... | ... | ... |
[All patterns from Q2.1]

## 7. Recommendation
### 7.1 Primary Recommendation
### 7.2 Hybrid Option (if applicable)
### 7.3 Implementation Roadmap
### 7.4 Success Criteria
### 7.5 Open Questions

## References
```

---

### Deliverable 3: Governance Bridge Specification

**Format**: Markdown document (~4-5K words)

**Structure**:
```markdown
# Brownfield Governance Bridge: From Analysis to Enforcement

## Executive Summary
- Bridge purpose and philosophy
- Input: brownfield analysis findings
- Output: governance artifacts (rules, gates, constraints)
- Key design decisions

## 1. Governance Output Taxonomy
### 1.1 Tier 1: Always Generated
### 1.2 Tier 2: On-Request
### 1.3 Tier 3: Governance-Mature Teams

## 2. Convention → Rule Pipeline
### 2.1 Convention Detection
### 2.2 Confidence Scoring
### 2.3 Rule Codification Format
### 2.4 Exception Handling
### 2.5 Integration with AI Coding Tools

## 3. Architecture → Constraint Pipeline
### 3.1 Architecture Discovery
### 3.2 Constraint Formalization
### 3.3 Fitness Function Design
### 3.4 Violation Detection

## 4. Pattern → Guardrail Pipeline
### 4.1 Pattern Mining
### 4.2 Guardrail Generation
### 4.3 Evidence Linking
### 4.4 Evolution Over Time

## 5. Debt → Recommendation Pipeline
### 5.1 Debt Identification
### 5.2 Business Impact Assessment
### 5.3 Prioritization Framework
### 5.4 Tracking Mechanism

## 6. Integration with RaiSE Ecosystem
### 6.1 → raise.rules.generate
### 6.2 → raise.1.discovery
### 6.3 → raise.2.vision
### 6.4 → Validation Gates

## References
```

---

## Success Criteria

This research will be successful if it produces:

1. **Complete Mechanical Understanding**:
   - [ ] Every step of BMAD's brownfield workflows documented
   - [ ] All templates, schemas, and checklists analyzed
   - [ ] Downstream integration paths mapped
   - [ ] Context window economics quantified

2. **Honest Pattern Assessment**:
   - [ ] At least 8 BMAD patterns evaluated
   - [ ] At least 3 anti-patterns identified
   - [ ] Each pattern has Adopt/Port/Inspire verdict
   - [ ] Evidence-based (not opinion-based) assessments

3. **Clear Three-Option Decision**:
   - [ ] Each option fully evaluated with effort, risk, benefit
   - [ ] Feature coverage matrix comparing all 3 options
   - [ ] Per-pattern decision matrix
   - [ ] One recommended option with clear rationale
   - [ ] Hybrid option considered if applicable

4. **Governance Bridge Design**:
   - [ ] Output taxonomy (3 tiers) defined
   - [ ] Convention → Rule pipeline designed
   - [ ] Architecture → Constraint pipeline designed
   - [ ] Integration with RaiSE ecosystem mapped

5. **Actionable Output**:
   - [ ] Implementation roadmap for chosen option
   - [ ] Phase definitions with effort estimates
   - [ ] Success criteria for Phase 1
   - [ ] Open questions for future research

---

## Output Location

**Deliverables saved to**:
```
specs/main/research/bmad-brownfield-analysis/
├── reverse-engineering-report.md         # Deliverable 1 (~8-10K words)
├── strategic-decision-report.md          # Deliverable 2 (~6-8K words)
├── governance-bridge-spec.md             # Deliverable 3 (~4-5K words)
└── sources/
    ├── bmad-source-files/                # Key BMAD files analyzed
    ├── industry-landscape/               # State-of-art tools and practices
    ├── context-window-analysis/          # Token economics data
    └── pattern-evidence/                 # Per-pattern evidence
```

---

## Meta: How to Use This Prompt

### For AI Research Agent

1. **Read this prompt completely** including all context sections
2. **Fetch BMAD brownfield source files** -- every file in `src/bmm/workflows/document-project/`
3. **Read RaiSE SAR templates** -- all files in `.raise-kit/templates/raise/sar/`
4. **Read RaiSE SAR command** -- `.raise-kit/commands/01-onboarding/raise.1.analyze.code.md`
5. **Read RaiSE brownfield research** -- `specs/main/research/brownfield-agent-docs/`
6. **Fetch industry state of the art** -- web search for tools, papers, standards
7. **Build comparison matrix** -- BMAD vs. SAR feature by feature
8. **Evaluate all 3 options** -- with explicit criteria and evidence
9. **Design governance bridge** -- the unique RaiSE value proposition
10. **Generate all 3 deliverables** -- following templates exactly
11. **Validate** against success criteria

### For Human Researcher

1. **Install BMAD** and run `document-project` on a real brownfield codebase
2. **Run RaiSE SAR** on the same codebase
3. **Compare outputs** side by side (quality, coverage, actionability)
4. **Try the governance bridge** -- manually extract rules from BMAD output
5. **Measure time** -- how long does each approach take?
6. **Note friction points** -- where does each approach struggle?
7. **Talk to users** who have tried both approaches
8. **Document your experience** for the decision report

---

## Related RaiSE Context

**Key Documents**:
- **SAR Templates**: `.raise-kit/templates/raise/sar/` (7 templates + README)
- **SAR Command**: `.raise-kit/commands/01-onboarding/raise.1.analyze.code.md`
- **SAR Architecture**: `specs/main/analysis/architecture/raise.1.analyze-code-architecture.md`
- **Brownfield Research**: `specs/main/research/brownfield-agent-docs/`
- **Rule Generation**: `.raise-kit/commands/01-onboarding/raise.rules.generate.md`
- **BMAD Competitive Analysis**: `specs/main/research/bmad-competitive-analysis/`
- **Spec-Kit Differentiation**: `specs/main/research/speckit-critiques/differentiation-strategy.md`
- **Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`

**RaiSE Principles to Apply**:
- **§2. Governance as Code**: Output must be governance artifacts, not just documentation
- **§3. Evidence-Based**: Every finding cites file:line evidence
- **§4. Validation Gates**: Phase-gated analysis with specific criteria
- **§5. Heutagogy**: Empower the Orquestador, don't prescribe
- **§7. Lean (Jidoka)**: Stop at defects; eliminate waste; right-size analysis
- **§8. Observable Workflow**: Every step's output is inspectable and traceable

---

**Research Start Date**: [YYYY-MM-DD]
**Research End Date**: [YYYY-MM-DD]
**Researcher**: [Name/Agent ID]
**Status**: [ ] Not Started / [ ] In Progress / [ ] Completed

---

*This research prompt is part of the RaiSE Framework evolution (Feature 012: Raise Commands Research). It addresses a critical strategic decision: how to evolve RaiSE's brownfield analysis capability in light of BMAD Method's approach, with the goal of creating a governance-grade brownfield analysis system that is demonstrably superior to both the current SAR process and BMAD's documentation-only approach.*
